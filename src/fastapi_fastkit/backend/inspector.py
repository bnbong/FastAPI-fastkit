# --------------------------------------------------------------------------
# The Module defines FastAPI template inspector for template validation.
# This module will be used by maintainers of FastAPI-fastkit when anyone
#   makes a PR of adding new FastAPI template.
#
# First, check a FastAPI template is formed a valid template form with .py-tpl extension
#   & dependencies requirements.
# Second, check a FastAPI template has a proper FastAPI server implementation.
#   main.py module must have a FastAPI app creation. like `app = FastAPI()`
# Third, check a FastAPI template has passed all the tests.
#
# This module create temporary named 'temp' directory at src/fastapi_fastkit/backend
#   and copy a template to Funtional FastAPI application into the temp directory.
# After the inspection, it will be deleted.
#
# This module include virtual environment creation & installation of dependencies.
# Depending on the volume in which the template is implemented and the number of dependencies,
#   it may take some time to complete the inspection.
#
# @author bnbong
# --------------------------------------------------------------------------
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import yaml  # type: ignore

from fastapi_fastkit.backend.main import (
    create_venv,
    find_template_core_modules,
    install_dependencies,
)
from fastapi_fastkit.backend.transducer import copy_and_convert_template
from fastapi_fastkit.core.settings import settings
from fastapi_fastkit.utils.logging import debug_log, get_logger
from fastapi_fastkit.utils.main import print_error, print_success, print_warning

logger = get_logger(__name__)


class TemplateInspector:
    """
    Template inspector for validating FastAPI templates.

    Uses context manager protocol for proper resource cleanup.
    """

    def __init__(self, template_path: str):
        self.template_path = Path(template_path)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.temp_dir = os.path.join(os.path.dirname(__file__), "temp")
        self._cleanup_needed = False
        self.template_config: Optional[Dict[str, Any]] = None

    def __enter__(self) -> "TemplateInspector":
        """Enter context manager - create temp directory and copy template."""
        try:
            os.makedirs(self.temp_dir, exist_ok=True)
            copy_and_convert_template(str(self.template_path), self.temp_dir)
            self._cleanup_needed = True
            self.template_config = self._load_template_config()
            debug_log(f"Created temporary directory at {self.temp_dir}", "debug")
            return self
        except Exception as e:
            debug_log(f"Failed to setup template inspector: {e}", "error")
            self._cleanup()
            raise

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager - cleanup temp directory."""
        self._cleanup()

    def _cleanup(self) -> None:
        """Cleanup temp directory if it exists and cleanup is needed."""
        if self._cleanup_needed and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                debug_log(f"Cleaned up temp directory {self.temp_dir}", "debug")
            except OSError as e:
                debug_log(
                    f"Failed to cleanup temp directory {self.temp_dir}: {e}", "warning"
                )
            finally:
                self._cleanup_needed = False

    def _load_template_config(self) -> Optional[Dict[str, Any]]:
        """Load template configuration from template-config.yml if available."""
        config_file = os.path.join(self.temp_dir, "template-config.yml")
        if not os.path.exists(config_file):
            debug_log(
                "No template-config.yml found, using default testing strategy", "info"
            )
            return None

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                if isinstance(config, dict):
                    debug_log(
                        f"Loaded template configuration: {config.get('name', 'Unknown')}",
                        "info",
                    )
                    return config
                else:
                    debug_log("Invalid template configuration format", "warning")
                    return None
        except (yaml.YAMLError, OSError, UnicodeDecodeError) as e:
            debug_log(f"Failed to load template configuration: {e}", "warning")
            return None

    def _check_docker_available(self) -> bool:
        """Check if Docker and Docker Compose are available."""
        try:
            # Check Docker
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                return False

            # Check Docker Compose
            result = subprocess.run(
                ["docker-compose", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except (
            subprocess.CalledProcessError,
            subprocess.TimeoutExpired,
            FileNotFoundError,
        ):
            return False

    def _check_containers_running(self, compose_file: str) -> bool:
        """Check if Docker Compose containers are already running."""
        try:
            result = subprocess.run(
                ["docker-compose", "-f", compose_file, "ps", "-q"],
                cwd=self.temp_dir,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                return False

            # Check if any containers are running
            container_ids = result.stdout.strip().split("\n")
            if not container_ids or container_ids == [""]:
                return False

            # Check if containers are actually running (not just exist)
            for container_id in container_ids:
                if container_id.strip():
                    status_result = subprocess.run(
                        [
                            "docker",
                            "inspect",
                            "-f",
                            "{{.State.Running}}",
                            container_id.strip(),
                        ],
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                    if (
                        status_result.returncode != 0
                        or status_result.stdout.strip() != "true"
                    ):
                        return False

            return True
        except (
            subprocess.CalledProcessError,
            subprocess.TimeoutExpired,
            FileNotFoundError,
        ):
            return False

    def inspect_template(self) -> bool:
        """
        Inspect the template to validate it's a proper FastAPI application.

        :return: True if template is valid, False otherwise
        """
        checks: List[Tuple[str, Callable[[], bool]]] = [
            ("File Structure", self._check_file_structure),
            ("File Extensions", self._check_file_extensions),
            ("Dependencies", self._check_dependencies),
            ("FastAPI Implementation", self._check_fastapi_implementation),
            ("Template Tests", self._test_template),
        ]

        for check_name, check_func in checks:
            debug_log(f"Running check: {check_name}", "info")
            if not check_func():
                debug_log(f"Check failed: {check_name}", "error")
                return False
            debug_log(f"Check passed: {check_name}", "info")

        return True

    def _check_file_structure(self) -> bool:
        """Check the required file and directory structure."""
        required_paths = [
            "tests",
            "requirements.txt-tpl",
            "setup.py-tpl",
            "README.md-tpl",
        ]

        for path in required_paths:
            if not (self.template_path / path).exists():
                error_msg = f"Missing required path: {path}"
                self.errors.append(error_msg)
                debug_log(f"File structure check failed: {error_msg}", "error")
                return False

        debug_log("File structure check passed", "info")
        return True

    def _check_file_extensions(self) -> bool:
        """Check all Python files have .py-tpl extension."""
        for path in self.template_path.rglob("*"):
            if path.is_file() and path.suffix == ".py":
                error_msg = f"Found .py file instead of .py-tpl: {path}"
                self.errors.append(error_msg)
                debug_log(f"File extension check failed: {error_msg}", "error")
                return False

        debug_log("File extension check passed", "info")
        return True

    def _check_dependencies(self) -> bool:
        """Check the dependencies in both setup.py-tpl and requirements.txt-tpl."""
        req_path = self.template_path / "requirements.txt-tpl"
        setup_path = self.template_path / "setup.py-tpl"

        if not req_path.exists():
            error_msg = "requirements.txt-tpl not found"
            self.errors.append(error_msg)
            debug_log(f"Dependencies check failed: {error_msg}", "error")
            return False
        if not setup_path.exists():
            error_msg = "setup.py-tpl not found"
            self.errors.append(error_msg)
            debug_log(f"Dependencies check failed: {error_msg}", "error")
            return False

        try:
            with open(req_path, encoding="utf-8") as f:
                deps = f.read().splitlines()
                package_names = [dep.split("==")[0] for dep in deps if dep]
                debug_log(f"Found dependencies: {package_names}", "debug")
                if "fastapi" not in package_names:
                    error_msg = "FastAPI dependency not found in requirements.txt-tpl"
                    self.errors.append(error_msg)
                    debug_log(f"Dependencies check failed: {error_msg}", "error")
                    return False
        except (OSError, UnicodeDecodeError) as e:
            error_msg = f"Error reading requirements.txt-tpl: {e}"
            self.errors.append(error_msg)
            debug_log(f"Dependencies check failed: {error_msg}", "error")
            return False

        debug_log("Dependencies check passed", "info")
        return True

    def _check_fastapi_implementation(self) -> bool:
        """Check if the template has a proper FastAPI server implementation."""
        try:
            core_modules = find_template_core_modules(self.temp_dir)
            debug_log(f"Found core modules: {core_modules}", "debug")

            if not core_modules["main"]:
                error_msg = "main.py not found in template"
                self.errors.append(error_msg)
                debug_log(f"FastAPI implementation check failed: {error_msg}", "error")
                return False

            with open(core_modules["main"], encoding="utf-8") as f:
                content = f.read()
                if "FastAPI" not in content or "app" not in content:
                    error_msg = "FastAPI app creation not found in main.py"
                    self.errors.append(error_msg)
                    debug_log(
                        f"FastAPI implementation check failed: {error_msg}", "error"
                    )
                    debug_log(f"main.py content preview: {content[:200]}...", "debug")
                    return False
        except (OSError, UnicodeDecodeError) as e:
            error_msg = f"Error checking FastAPI implementation: {e}"
            self.errors.append(error_msg)
            debug_log(f"FastAPI implementation check failed: {error_msg}", "error")
            return False

        debug_log("FastAPI implementation check passed", "info")
        return True

    def _test_template(self) -> bool:
        """Run tests on the template using appropriate strategy based on configuration."""
        test_dir = os.path.join(self.temp_dir, "tests")
        if not os.path.exists(test_dir):
            warning_msg = "No tests directory found"
            self.warnings.append(warning_msg)
            debug_log(f"Template warning: {warning_msg}", "warning")
            return True

        # Determine test strategy based on template configuration
        if self.template_config and self.template_config.get("requires_docker", False):
            return self._test_with_docker_strategy()
        else:
            return self._test_with_standard_strategy()

    def _test_with_docker_strategy(self) -> bool:
        """Run tests using Docker Compose strategy."""
        docker_available = self._check_docker_available()

        if not docker_available:
            debug_log("Docker not available, trying fallback strategy", "warning")
            warning_msg = "Docker not available, using fallback testing strategy"
            self.warnings.append(warning_msg)
            debug_log(f"Template warning: {warning_msg}", "warning")
            return self._test_with_fallback_strategy()

        try:
            # Set up environment variables
            self._setup_test_environment()

            # Run Docker Compose based tests
            testing_config = (
                self.template_config.get("testing", {}) if self.template_config else {}
            )
            compose_file = testing_config.get("compose_file", "docker-compose.yml")
            timeout = testing_config.get("health_check_timeout", 120)

            # Check if containers are already running
            if not self._check_containers_running(compose_file):
                debug_log("Starting Docker Compose services for testing", "info")

                # Start services
                result = subprocess.run(
                    ["docker-compose", "-f", compose_file, "up", "-d", "--build"],
                    cwd=self.temp_dir,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )

                if result.returncode != 0:
                    self.errors.append(
                        f"Failed to start Docker services: {result.stderr}"
                    )
                    return False

                # Wait for services to be healthy
                self._wait_for_services_healthy(compose_file, timeout)
            else:
                debug_log(
                    "Docker Compose services already running, skipping startup", "info"
                )

            # Verify services are actually running before attempting tests
            if not self._verify_services_running(compose_file):
                self.errors.append("Services failed to start properly")
                return False

            # Run tests using docker exec
            test_result = self._run_docker_exec_tests(compose_file)

            return test_result

        except subprocess.TimeoutExpired:
            self.errors.append("Docker Compose setup timed out")
            return False
        except Exception as e:
            self.errors.append(f"Unexpected error during Docker testing: {e}")
            return False
        finally:
            # Clean up Docker services
            self._cleanup_docker_services()

    def _test_with_standard_strategy(self) -> bool:
        """Run tests using standard virtual environment strategy."""
        try:
            # Create virtual environment for testing
            venv_path = create_venv(self.temp_dir)
            install_dependencies(self.temp_dir, venv_path)

            # Check if scripts/test.sh exists
            test_script_path = os.path.join(self.temp_dir, "scripts", "test.sh")
            if os.path.exists(test_script_path):
                debug_log("Found scripts/test.sh, using template test script", "info")
                result = self._run_test_script(test_script_path, venv_path)
            else:
                debug_log("No scripts/test.sh found, running pytest directly", "info")
                result = self._run_pytest_directly(venv_path)

            if result.returncode != 0:
                error_msg = f"Tests failed with return code {result.returncode}\n"
                if result.stderr:
                    error_msg += f"STDERR:\n{result.stderr}\n"
                if result.stdout:
                    error_msg += f"STDOUT:\n{result.stdout}\n"
                self.errors.append(error_msg)
                debug_log(f"Standard strategy tests failed: {error_msg}", "error")
                return False

            debug_log("All tests passed successfully", "info")
            return True

        except subprocess.TimeoutExpired:
            self.errors.append("Tests timed out after 5 minutes")
            return False
        except subprocess.CalledProcessError as e:
            self.errors.append(f"Error running tests: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Unexpected error during testing: {e}")
            return False

    def _fix_script_line_endings(self, script_path: str) -> None:
        """Fix line endings in script file (convert Windows \r\n to Unix \n)."""
        try:
            with open(script_path, "rb") as f:
                content = f.read()

            # Convert Windows line endings to Unix
            content = content.replace(b"\r\n", b"\n")
            content = content.replace(b"\r", b"\n")

            with open(script_path, "wb") as f:
                f.write(content)

            debug_log(f"Fixed line endings in {script_path}", "debug")
        except Exception as e:
            debug_log(f"Failed to fix line endings in {script_path}: {e}", "warning")

    def _fix_all_script_line_endings(self) -> None:
        """Fix line endings in all shell scripts in the temp directory."""
        script_patterns = ["*.sh", "*.bash"]

        for pattern in script_patterns:
            for root, dirs, files in os.walk(self.temp_dir):
                for file in files:
                    if file.endswith((".sh", ".bash")):
                        script_path = os.path.join(root, file)
                        self._fix_script_line_endings(script_path)

        debug_log("Fixed line endings for all shell scripts", "info")

    def _run_test_script(
        self, test_script_path: str, venv_path: str
    ) -> subprocess.CompletedProcess[str]:
        """Run the template's test script."""
        # Fix line endings (convert Windows \r\n to Unix \n)
        self._fix_script_line_endings(test_script_path)

        # Make script executable
        os.chmod(test_script_path, 0o755)

        # Set up environment to use virtual environment
        env = os.environ.copy()
        if os.name == "nt":  # Windows
            env["PATH"] = f"{os.path.join(venv_path, 'Scripts')};{env.get('PATH', '')}"
        else:  # Unix-based
            env["PATH"] = f"{os.path.join(venv_path, 'bin')}:{env.get('PATH', '')}"

        # Run the test script
        return subprocess.run(
            [test_script_path],
            cwd=self.temp_dir,
            capture_output=True,
            text=True,
            env=env,
            timeout=300,  # 5 minutes timeout
        )

    def _run_pytest_directly(self, venv_path: str) -> subprocess.CompletedProcess[str]:
        """Run pytest directly using virtual environment."""
        if os.name == "nt":  # Windows
            python_executable = os.path.join(venv_path, "Scripts", "python")
        else:  # Unix-based
            python_executable = os.path.join(venv_path, "bin", "python")

        test_dir = os.path.join(self.temp_dir, "tests")
        return subprocess.run(
            [python_executable, "-m", "pytest", test_dir, "-v"],
            cwd=self.temp_dir,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes timeout
        )

    def _run_test_script_with_env(
        self, test_script_path: str, venv_path: str, env: Dict[str, str]
    ) -> subprocess.CompletedProcess[str]:
        """Run the template's test script with custom environment variables."""
        # Fix line endings (convert Windows \r\n to Unix \n)
        self._fix_script_line_endings(test_script_path)

        # Make script executable
        os.chmod(test_script_path, 0o755)

        # Set up environment to use virtual environment
        env = env.copy()
        if os.name == "nt":  # Windows
            env["PATH"] = f"{os.path.join(venv_path, 'Scripts')};{env.get('PATH', '')}"
        else:  # Unix-based
            env["PATH"] = f"{os.path.join(venv_path, 'bin')}:{env.get('PATH', '')}"

        # Run the test script
        return subprocess.run(
            [test_script_path],
            cwd=self.temp_dir,
            capture_output=True,
            text=True,
            env=env,
            timeout=300,  # 5 minutes timeout
        )

    def _run_pytest_with_env(
        self, venv_path: str, env: Dict[str, str], fallback_config: Dict[str, Any]
    ) -> subprocess.CompletedProcess[str]:
        """Run pytest directly with custom environment variables."""
        if os.name == "nt":  # Windows
            python_executable = os.path.join(venv_path, "Scripts", "python")
        else:  # Unix-based
            python_executable = os.path.join(venv_path, "bin", "python")

        test_command = fallback_config.get("test_command", "pytest tests/ -v").split()
        return subprocess.run(
            [python_executable, "-m"] + test_command,
            cwd=self.temp_dir,
            capture_output=True,
            text=True,
            env=env,
            timeout=300,
        )

    def _test_with_fallback_strategy(self) -> bool:
        """Run tests using fallback strategy (e.g., SQLite instead of PostgreSQL)."""
        if not self.template_config or "fallback_testing" not in self.template_config:
            debug_log(
                "No fallback strategy configured, using standard strategy", "info"
            )
            return self._test_with_standard_strategy()

        try:
            # Create virtual environment for testing
            venv_path = create_venv(self.temp_dir)
            install_dependencies(self.temp_dir, venv_path)

            # Set up fallback environment (e.g., SQLite database)
            fallback_config = self.template_config["fallback_testing"]
            database_url = fallback_config.get("database_url", "sqlite:///:memory:")

            # Set environment variable for fallback database
            env = os.environ.copy()
            env["DATABASE_URL"] = database_url
            env["SQLALCHEMY_DATABASE_URI"] = database_url

            # Check if scripts/test.sh exists
            test_script_path = os.path.join(self.temp_dir, "scripts", "test.sh")
            if os.path.exists(test_script_path):
                debug_log(
                    "Found scripts/test.sh, using template test script with fallback environment",
                    "info",
                )
                result = self._run_test_script_with_env(
                    test_script_path, venv_path, env
                )
            else:
                debug_log(
                    "No scripts/test.sh found, running pytest directly with fallback environment",
                    "info",
                )
                result = self._run_pytest_with_env(venv_path, env, fallback_config)

            if result.returncode != 0:
                error_msg = (
                    f"Fallback tests failed with return code {result.returncode}\n"
                )
                if result.stderr:
                    error_msg += f"STDERR:\n{result.stderr}\n"
                if result.stdout:
                    error_msg += f"STDOUT:\n{result.stdout}\n"
                self.errors.append(error_msg)
                debug_log(f"Fallback strategy tests failed: {error_msg}", "error")
                return False

            debug_log("Fallback tests passed successfully", "info")
            warning_msg = (
                "Tests passed using fallback strategy (SQLite instead of PostgreSQL)"
            )
            self.warnings.append(warning_msg)
            debug_log(f"Template warning: {warning_msg}", "warning")
            return True

        except Exception as e:
            self.errors.append(f"Unexpected error during fallback testing: {e}")
            return False

    def _setup_test_environment(self) -> None:
        """Set up environment variables for testing."""
        if not self.template_config:
            return

        env_defaults = self.template_config.get("test_env_defaults", {})
        env_file_path = os.path.join(self.temp_dir, ".env")

        # Check if .env file already exists
        if os.path.exists(env_file_path):
            debug_log(f".env file already exists at {env_file_path}", "info")
            # Read existing content and merge with defaults
            existing_vars = {}
            try:
                with open(env_file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and "=" in line and not line.startswith("#"):
                            key, value = line.split("=", 1)
                            existing_vars[key] = value
            except Exception as e:
                debug_log(f"Error reading existing .env file: {e}", "warning")
        else:
            existing_vars = {}

        # Merge defaults with existing variables (defaults take precedence for missing vars)
        final_vars = {**env_defaults, **existing_vars}

        # Create .env file with merged variables
        with open(env_file_path, "w", encoding="utf-8") as f:
            for key, value in final_vars.items():
                f.write(f"{key}={value}\n")

        debug_log(
            f"Set up environment file: {env_file_path} with variables: {list(final_vars.keys())}",
            "info",
        )

        # Fix line endings in all shell scripts
        self._fix_all_script_line_endings()

    def _wait_for_services_healthy(self, compose_file: str, timeout: int) -> None:
        """Wait for Docker Compose services to be healthy."""
        import time

        debug_log("Waiting for services to be healthy...", "info")
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                # Check if all services are running and healthy
                result = subprocess.run(
                    ["docker-compose", "-f", compose_file, "ps", "--format", "json"],
                    cwd=self.temp_dir,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode == 0:
                    import json

                    services = []
                    for line in result.stdout.strip().split("\n"):
                        if line.strip():
                            try:
                                service_info = json.loads(line)
                                services.append(service_info)
                            except json.JSONDecodeError:
                                continue

                    # Check if all services are running
                    all_running = True
                    for service in services:
                        if service.get("State") != "running":
                            all_running = False
                            debug_log(
                                f"Service {service.get('Name')} is {service.get('State')}",
                                "info",
                            )
                            break

                    if all_running and len(services) >= 2:  # db and app services
                        debug_log("All services are running", "info")
                        # Additional wait for app to be fully ready
                        time.sleep(10)
                        return

            except Exception as e:
                debug_log(f"Error checking service health: {e}", "warning")

            debug_log("Services not ready yet, waiting...", "info")
            time.sleep(5)

        debug_log(
            f"Services did not become healthy within {timeout} seconds", "warning"
        )

    def _verify_services_running(self, compose_file: str) -> bool:
        """Verify that all required services are running."""
        try:
            result = subprocess.run(
                ["docker-compose", "-f", compose_file, "ps", "--format", "json"],
                cwd=self.temp_dir,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                debug_log(f"Failed to check service status: {result.stderr}", "error")
                return False

            import json

            services = []
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    try:
                        service_info = json.loads(line)
                        services.append(service_info)
                    except json.JSONDecodeError:
                        continue

            # Check for required services (db and app)
            db_running = False
            app_running = False

            for service in services:
                service_name = service.get("Name", "")
                service_state = service.get("State", "")

                debug_log(f"Service {service_name}: {service_state}", "info")

                if "db" in service_name and service_state == "running":
                    db_running = True
                elif "app" in service_name and service_state == "running":
                    app_running = True

            if not db_running:
                self.errors.append("Database service is not running")
                return False

            if not app_running:
                # Get logs from failed app service for debugging
                try:
                    logs_result = subprocess.run(
                        [
                            "docker-compose",
                            "-f",
                            compose_file,
                            "logs",
                            "--tail",
                            "50",
                            "app",
                        ],
                        cwd=self.temp_dir,
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                    if logs_result.returncode == 0:
                        debug_log(f"App service logs: {logs_result.stdout}", "error")
                        self.errors.append(
                            f"Application service is not running. Logs: {logs_result.stdout[-500:]}"
                        )
                    else:
                        self.errors.append("Application service is not running")
                except Exception:
                    self.errors.append("Application service is not running")
                return False

            debug_log("All required services are running", "info")
            return True

        except Exception as e:
            debug_log(f"Error verifying services: {e}", "error")
            self.errors.append(f"Failed to verify service status: {e}")
            return False

    def _run_docker_tests(self, compose_file: str) -> bool:
        """Run tests in Docker environment."""
        try:
            # Check if scripts/test.sh exists in temp directory
            test_script_path = os.path.join(self.temp_dir, "scripts", "test.sh")
            if os.path.exists(test_script_path):
                debug_log(
                    "Found scripts/test.sh, using template test script in Docker",
                    "info",
                )
                # Fix line endings before running in Docker
                self._fix_script_line_endings(test_script_path)
                # Run the test script inside Docker container
                result = subprocess.run(
                    [
                        "docker-compose",
                        "-f",
                        compose_file,
                        "exec",
                        "-T",
                        "app",
                        "bash",
                        "-c",
                        "chmod +x ./scripts/test.sh && ./scripts/test.sh",
                    ],
                    cwd=self.temp_dir,
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
            else:
                debug_log(
                    "No scripts/test.sh found, running pytest directly in Docker",
                    "info",
                )
                # Run pytest directly using docker-compose exec
                result = subprocess.run(
                    [
                        "docker-compose",
                        "-f",
                        compose_file,
                        "exec",
                        "-T",
                        "app",
                        "python",
                        "-m",
                        "pytest",
                        "tests/",
                        "-v",
                    ],
                    cwd=self.temp_dir,
                    capture_output=True,
                    text=True,
                    timeout=300,
                )

            if result.returncode != 0:
                error_msg = (
                    f"Docker tests failed with return code {result.returncode}\n"
                )
                if result.stderr:
                    error_msg += f"STDERR:\n{result.stderr}\n"
                if result.stdout:
                    error_msg += f"STDOUT:\n{result.stdout}\n"
                self.errors.append(error_msg)
                debug_log(f"Docker strategy tests failed: {error_msg}", "error")
                return False

            debug_log("Docker tests passed successfully", "info")
            return True

        except subprocess.TimeoutExpired:
            self.errors.append("Docker tests timed out")
            return False
        except Exception as e:
            self.errors.append(f"Error running Docker tests: {e}")
            return False

    def _run_docker_exec_tests(self, compose_file: str) -> bool:
        """Run tests using docker-compose exec command."""
        try:
            # Check if scripts/test.sh exists in temp directory
            test_script_path = os.path.join(self.temp_dir, "scripts", "test.sh")
            if os.path.exists(test_script_path):
                debug_log(
                    "Found scripts/test.sh, using template test script with docker-compose exec",
                    "info",
                )
                # Fix line endings before running in Docker
                self._fix_script_line_endings(test_script_path)
                # Run the test script inside Docker container using docker-compose exec
                result = subprocess.run(
                    [
                        "docker-compose",
                        "-f",
                        compose_file,
                        "exec",
                        "-T",
                        "app",
                        "bash",
                        "scripts/test.sh",
                    ],
                    cwd=self.temp_dir,
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
            else:
                debug_log(
                    "No scripts/test.sh found, running pytest directly with docker-compose exec",
                    "info",
                )
                # Run pytest directly using docker-compose exec
                result = subprocess.run(
                    [
                        "docker-compose",
                        "-f",
                        compose_file,
                        "exec",
                        "-T",
                        "app",
                        "python",
                        "-m",
                        "pytest",
                        "tests/",
                        "-v",
                    ],
                    cwd=self.temp_dir,
                    capture_output=True,
                    text=True,
                    timeout=300,
                )

            if result.returncode != 0:
                error_msg = (
                    f"Docker exec tests failed with return code {result.returncode}\n"
                )
                if result.stderr:
                    error_msg += f"STDERR:\n{result.stderr}\n"
                if result.stdout:
                    error_msg += f"STDOUT:\n{result.stdout}\n"
                self.errors.append(error_msg)
                debug_log(f"Docker exec strategy tests failed: {error_msg}", "error")
                debug_log(f"Docker exec test stderr: {result.stderr}", "error")
                debug_log(f"Docker exec test stdout: {result.stdout}", "info")
                return False

            debug_log("Docker exec tests passed successfully", "info")
            debug_log(f"Docker exec test stdout: {result.stdout}", "info")
            return True

        except subprocess.TimeoutExpired:
            self.errors.append("Docker exec tests timed out")
            return False
        except Exception as e:
            self.errors.append(f"Error running Docker exec tests: {e}")
            return False

    def _cleanup_docker_services(self) -> None:
        """Clean up Docker Compose services."""
        try:
            debug_log("Cleaning up Docker services", "info")
            subprocess.run(
                ["docker-compose", "down", "-v"],
                cwd=self.temp_dir,
                capture_output=True,
                text=True,
                timeout=60,
            )
        except Exception as e:
            debug_log(f"Failed to cleanup Docker services: {e}", "warning")

    def get_report(self) -> Dict[str, Any]:
        """
        Get inspection report with errors and warnings.

        :return: Dictionary containing inspection results
        """
        is_valid = len(self.errors) == 0
        template_name = self.template_path.name

        # Log final inspection results
        if is_valid:
            debug_log(
                f"Template inspection completed successfully for {template_name}",
                "info",
            )
            if self.warnings:
                debug_log(
                    f"Template {template_name} has {len(self.warnings)} warnings: {self.warnings}",
                    "warning",
                )
        else:
            debug_log(
                f"Template inspection failed for {template_name} with {len(self.errors)} errors",
                "error",
            )
            for i, error in enumerate(self.errors, 1):
                debug_log(f"Error {i}: {error}", "error")
            if self.warnings:
                debug_log(
                    f"Template {template_name} also has {len(self.warnings)} warnings: {self.warnings}",
                    "warning",
                )

        return {
            "template_path": str(self.template_path),
            "errors": self.errors,
            "warnings": self.warnings,
            "is_valid": is_valid,
        }


def inspect_fastapi_template(template_path: str) -> Dict[str, Any]:
    """
    Convenience function to inspect a FastAPI template.

    :param template_path: Path to the template to inspect
    :return: Inspection report dictionary
    """
    template_name = Path(template_path).name
    debug_log(
        f"Starting template inspection for {template_name} at {template_path}", "info"
    )

    with TemplateInspector(template_path) as inspector:
        is_valid = inspector.inspect_template()
        report = inspector.get_report()

        if is_valid:
            print_success(f"Template {template_path} is valid!")
            debug_log(
                f"Template inspection completed successfully for {template_name}",
                "info",
            )
        else:
            print_error(f"Template {template_path} validation failed")
            debug_log(f"Template inspection failed for {template_name}", "error")
            for error in inspector.errors:
                print_error(f"  - {error}")

        if inspector.warnings:
            debug_log(
                f"Template inspection for {template_name} has warnings", "warning"
            )
            for warning in inspector.warnings:
                print_warning(f"  - {warning}")

    debug_log(
        f"Template inspection completed for {template_name}. Valid: {is_valid}, Errors: {len(inspector.errors)}, Warnings: {len(inspector.warnings)}",
        "info",
    )
    return report


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print_error("Usage: python inspector.py <template_dir>")
        sys.exit(1)

    template_dir = sys.argv[1]
    inspect_fastapi_template(template_dir)
