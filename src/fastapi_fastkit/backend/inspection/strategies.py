# --------------------------------------------------------------------------
# Test strategies for template inspection.
#
# All strategies share one base: prepare an environment, pick between the
# template's own ``scripts/test.sh`` and a direct pytest invocation, then turn
# a non-zero return code into an inspection error. The concrete strategies
# only supply what actually differs - the environment and the command.
#
# @author bnbong
# --------------------------------------------------------------------------
import os
import subprocess
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from fastapi_fastkit.backend.main import create_venv, install_dependencies_with_manager
from fastapi_fastkit.utils.logging import debug_log

from . import smoke
from .context import InspectionContext
from .docker import DockerCompose
from .fsutils import fix_all_script_line_endings, fix_script_line_endings

TEST_TIMEOUT = 300
DEFAULT_TEST_COMMAND = "pytest tests/ -v"


def detect_package_manager(project_dir: str) -> str:
    """Pick the package manager that fits the project's dependency files."""
    if os.path.exists(os.path.join(project_dir, "pyproject.toml")):
        return "uv"
    return "pip"


def prepare_environment(ctx: InspectionContext) -> bool:
    """Create the inspection venv and install the project's dependencies.

    Idempotent: a context that already carries a ``venv_path`` is left alone,
    so the smoke test can reuse whatever a test strategy already built.
    """
    if ctx.venv_path:
        return True

    try:
        venv_path = create_venv(ctx.temp_dir)
    except Exception as e:
        ctx.add_error(f"Failed to create virtual environment: {e}")
        return False

    package_manager = detect_package_manager(ctx.temp_dir)
    debug_log(f"Using package manager: {package_manager}", "info")

    try:
        install_dependencies_with_manager(ctx.temp_dir, venv_path, package_manager)
    except Exception as e:
        ctx.add_error(f"Failed to install dependencies: {str(e)}")
        return False

    ctx.venv_path = venv_path
    return True


class TestStrategy(ABC):
    """Base class for the ways a template's test suite can be executed."""

    name = "base"

    def __init__(self, ctx: InspectionContext):
        self.ctx = ctx

    @property
    def config(self) -> Dict[str, Any]:
        """The template's configuration mapping (empty when absent)."""
        return self.ctx.template_config or {}

    @abstractmethod
    def run(self) -> bool:
        """Execute the template's tests, recording errors on the context."""

    def _report_failure(self, result: subprocess.CompletedProcess[str]) -> None:
        """Turn a failed test process into a single descriptive error entry."""
        message = f"{self.name} tests failed with return code {result.returncode}\n"
        if result.stderr:
            message += f"STDERR:\n{result.stderr}\n"
        if result.stdout:
            message += f"STDOUT:\n{result.stdout}\n"
        self.ctx.add_error(message)


class LocalVenvStrategy(TestStrategy):
    """Run the tests in a virtual environment created next to the project."""

    name = "Standard"

    def environment(self) -> Dict[str, str]:
        """Environment variables for the test process."""
        return os.environ.copy()

    def test_command(self) -> List[str]:
        """The pytest invocation used when the template ships no test script."""
        return DEFAULT_TEST_COMMAND.split()

    def on_success(self) -> None:
        """Hook for strategies that want to annotate a successful run."""

    def run(self) -> bool:
        if not prepare_environment(self.ctx):
            return False

        venv_path = self.ctx.venv_path
        assert venv_path is not None  # prepare_environment guarantees this

        env = self.environment()
        bin_dir = "Scripts" if os.name == "nt" else "bin"
        separator = ";" if os.name == "nt" else ":"
        env["PATH"] = (
            f"{os.path.join(venv_path, bin_dir)}{separator}{env.get('PATH', '')}"
        )

        test_script_path = self.ctx.temp_path("scripts", "test.sh")
        try:
            if os.path.exists(test_script_path):
                debug_log("Found scripts/test.sh, using template test script", "info")
                result = self._run_test_script(test_script_path, env)
            else:
                debug_log("No scripts/test.sh found, running pytest directly", "info")
                result = self._run_pytest(env)
        except subprocess.TimeoutExpired:
            self.ctx.add_error(f"{self.name} tests timed out after 5 minutes")
            return False
        except OSError as e:
            self.ctx.add_error(f"Error running {self.name.lower()} tests: {e}")
            return False

        if result.returncode != 0:
            self._report_failure(result)
            return False

        debug_log(f"{self.name} tests passed successfully", "info")
        self.on_success()
        return True

    def _run_test_script(
        self, test_script_path: str, env: Dict[str, str]
    ) -> subprocess.CompletedProcess[str]:
        """Run the template's own test script."""
        fix_script_line_endings(test_script_path)
        os.chmod(test_script_path, 0o755)
        return subprocess.run(
            [test_script_path],
            cwd=self.ctx.temp_dir,
            capture_output=True,
            text=True,
            env=env,
            timeout=TEST_TIMEOUT,
        )

    def _run_pytest(self, env: Dict[str, str]) -> subprocess.CompletedProcess[str]:
        """Run pytest with the strategy's command inside the inspection venv."""
        python_executable = self.ctx.python_executable()
        assert python_executable is not None
        return subprocess.run(
            [python_executable, "-m", *self.test_command()],
            cwd=self.ctx.temp_dir,
            capture_output=True,
            text=True,
            env=env,
            timeout=TEST_TIMEOUT,
        )


class StandardStrategy(LocalVenvStrategy):
    """Plain virtual environment run - the default for most templates."""

    name = "Standard"


class FallbackStrategy(LocalVenvStrategy):
    """Docker-free substitute run (e.g. SQLite in place of PostgreSQL)."""

    name = "Fallback"

    @property
    def fallback_config(self) -> Dict[str, Any]:
        """The ``fallback_testing`` block of the template configuration."""
        block = self.config.get("fallback_testing", {})
        return block if isinstance(block, dict) else {}

    def environment(self) -> Dict[str, str]:
        env = os.environ.copy()
        database_url = self.fallback_config.get("database_url", "sqlite:///:memory:")
        env["DATABASE_URL"] = database_url
        env["SQLALCHEMY_DATABASE_URI"] = database_url
        return env

    def test_command(self) -> List[str]:
        command = self.fallback_config.get("test_command", DEFAULT_TEST_COMMAND)
        return str(command).split()

    def on_success(self) -> None:
        self.ctx.add_warning(
            "Tests passed using fallback strategy (SQLite instead of PostgreSQL)"
        )


class DockerStrategy(TestStrategy):
    """Run the tests inside the template's own Docker Compose stack."""

    name = "Docker"

    def _testing_config(self) -> Dict[str, Any]:
        block = self.config.get("testing", {})
        return block if isinstance(block, dict) else {}

    def _setup_test_environment(self) -> None:
        """Materialise a .env file from ``test_env_defaults`` and fix scripts."""
        env_defaults = self.config.get("test_env_defaults", {})
        env_file_path = self.ctx.temp_path(".env")

        existing_vars: Dict[str, str] = {}
        if os.path.exists(env_file_path):
            debug_log(f".env file already exists at {env_file_path}", "info")
            try:
                with open(env_file_path, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and "=" in line and not line.startswith("#"):
                            key, value = line.split("=", 1)
                            existing_vars[key] = value
            except (OSError, UnicodeDecodeError) as e:
                debug_log(f"Error reading existing .env file: {e}", "warning")

        final_vars = {**env_defaults, **existing_vars}
        with open(env_file_path, "w", encoding="utf-8") as f:
            for key, value in final_vars.items():
                f.write(f"{key}={value}\n")

        debug_log(
            f"Set up environment file: {env_file_path} "
            f"with variables: {list(final_vars.keys())}",
            "info",
        )
        fix_all_script_line_endings(self.ctx.temp_dir)

    def run(self) -> bool:
        if not DockerCompose.is_available():
            debug_log("Docker not available, trying fallback strategy", "warning")
            self.ctx.add_warning(
                "Docker not available, using fallback testing strategy"
            )
            return select_fallback_strategy(self.ctx).run()

        testing_config = self._testing_config()
        compose = DockerCompose(
            self.ctx.temp_dir,
            str(testing_config.get("compose_file", "docker-compose.yml")),
        )
        timeout = int(testing_config.get("health_check_timeout", 120))

        try:
            self._setup_test_environment()

            if not compose.containers_running():
                debug_log("Starting Docker Compose services for testing", "info")
                result = compose.up(timeout)
                if result.returncode != 0:
                    self.ctx.add_error(
                        f"Failed to start Docker services: {result.stderr}"
                    )
                    return False
                compose.wait_until_healthy(timeout)
            else:
                debug_log(
                    "Docker Compose services already running, skipping startup", "info"
                )

            verification_error = compose.verify_services_running()
            if verification_error is not None:
                self.ctx.add_error(verification_error)
                return False

            if not self._run_tests(compose):
                return False

            # The application is running right here, in a container with a
            # published port: probing that is the only way a Docker-only
            # template gets a smoke test, since no host venv is ever built for
            # it. Done before the ``finally`` below tears the stack down.
            self._run_smoke_test(compose)
            return True
        except subprocess.TimeoutExpired:
            self.ctx.add_error("Docker Compose setup timed out")
            return False
        except OSError as e:
            self.ctx.add_error(f"Unexpected error during Docker testing: {e}")
            return False
        finally:
            compose.cleanup()

    def _run_tests(self, compose: DockerCompose) -> bool:
        """Execute the suite inside the app container and grade the result."""
        test_script_path = self.ctx.temp_path("scripts", "test.sh")
        use_test_script = os.path.exists(test_script_path)
        if use_test_script:
            fix_script_line_endings(test_script_path)

        result = compose.exec_tests(use_test_script)
        if result is None:
            self.ctx.add_error("Docker tests timed out")
            return False

        if result.returncode != 0:
            self._report_failure(result)
            return False

        debug_log("Docker tests passed successfully", "info")
        return True

    def _run_smoke_test(self, compose: DockerCompose) -> None:
        """Probe the running container's HTTP surface and record the verdict.

        The result lands on the context so the pipeline's Smoke Test step
        reuses it instead of trying (and failing) to boot the project from a
        virtual environment that a Docker run never creates.
        """
        if not self.ctx.options.run_smoke_test:
            return

        port = compose.published_port()
        if port is None:
            self.ctx.add_warning(
                "smoke test skipped: Docker template without published port"
            )
            self.ctx.smoke_result = True
            return

        self.ctx.smoke_result = smoke.run_http_smoke(
            self.ctx, f"http://127.0.0.1:{port}"
        )


def select_fallback_strategy(ctx: InspectionContext) -> TestStrategy:
    """Pick the fallback strategy, or the standard one when none is configured."""
    config = ctx.template_config or {}
    if "fallback_testing" not in config:
        debug_log("No fallback strategy configured, using standard strategy", "info")
        return StandardStrategy(ctx)
    return FallbackStrategy(ctx)


def select_strategy(ctx: InspectionContext) -> TestStrategy:
    """Pick the strategy the template's configuration asks for."""
    config = ctx.template_config or {}
    if config.get("requires_docker", False):
        return DockerStrategy(ctx)
    return StandardStrategy(ctx)


def run_template_tests(ctx: InspectionContext) -> bool:
    """Run the template's test suite with the appropriate strategy."""
    if not ctx.options.run_template_tests:
        debug_log("Template test execution disabled", "info")
        return prepare_environment(ctx)

    strategy = select_strategy(ctx)
    debug_log(f"Running tests with {strategy.name} strategy", "info")
    return strategy.run()
