# --------------------------------------------------------------------------
# The TemplateInspector orchestrator.
#
# The inspector generates a real project from the template (copy + convert +
# metadata injection), runs every check against that generated project, and
# cleans the temporary directory up afterwards. Individual checks live in
# sibling modules; this class only sequences them and owns the lifecycle.
#
# @author bnbong
# --------------------------------------------------------------------------
import os
import shutil
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable, Dict, List, Optional, Tuple

from fastapi_fastkit.backend.scaffolder import ProjectScaffolder, ScaffoldOptions
from fastapi_fastkit.core.settings import settings
from fastapi_fastkit.utils.logging import debug_log

from . import checks, consistency, freshness, lint, smoke, strategies
from .context import InspectionContext, InspectionOptions
from .docker import DockerCompose
from .fsutils import force_cleanup_directory
from .report import build_report, print_report

#: Metadata used to generate the throwaway project that gets inspected.
DUMMY_METADATA = {
    "project_name": "test-template",
    "author": "Template Inspector",
    "author_email": "inspector@fastapi-fastkit.dev",
    "description": "Test project for template inspection",
}


class TemplateInspector:
    """Validate a FastAPI template by generating and exercising a project.

    Uses the context manager protocol so the temporary project directory is
    always removed, even when a check raises.
    """

    def __init__(
        self,
        template_path: str,
        temp_base_dir: Optional[str] = None,
        options: Optional[InspectionOptions] = None,
    ):
        template_name = Path(template_path).name
        base_dir = temp_base_dir or os.path.dirname(os.path.dirname(__file__))
        self.ctx = InspectionContext(
            template_path=Path(template_path),
            temp_dir=os.path.join(base_dir, f"temp_{template_name}"),
            options=options or InspectionOptions(),
        )
        self._cleanup_needed = False

    # -- state exposed for callers and tests -------------------------------
    @property
    def template_path(self) -> Path:
        """The on-disk template directory being inspected."""
        return self.ctx.template_path

    @property
    def temp_dir(self) -> str:
        """The generated project directory used for the inspection."""
        return self.ctx.temp_dir

    @property
    def errors(self) -> List[str]:
        """Fatal findings accumulated so far."""
        return self.ctx.errors

    @property
    def warnings(self) -> List[str]:
        """Non-fatal findings accumulated so far."""
        return self.ctx.warnings

    @property
    def template_config(self) -> Optional[Dict[str, Any]]:
        """Parsed ``template-config.yml`` contents, when the template ships one."""
        return self.ctx.template_config

    # -- lifecycle ---------------------------------------------------------
    def __enter__(self) -> "TemplateInspector":
        """Create the temporary directory and generate a project from the template."""
        try:
            if os.path.exists(self.ctx.temp_dir):
                debug_log(
                    f"Cleaning up existing temp directory: {self.ctx.temp_dir}", "info"
                )
                try:
                    shutil.rmtree(self.ctx.temp_dir)
                except OSError as e:
                    debug_log(
                        f"Failed to cleanup existing temp directory: {e}", "warning"
                    )

            os.makedirs(self.ctx.temp_dir, exist_ok=True)
            # Mark for cleanup immediately: a failure below must not leak the
            # directory that was just created.
            self._cleanup_needed = True
            self._generate_project()

            self.ctx.template_config = self._load_template_config()
            debug_log(f"Created temporary directory at {self.ctx.temp_dir}", "debug")
            return self
        except Exception as e:
            debug_log(f"Failed to setup template inspector: {e}", "error")
            self._cleanup()
            raise

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Remove the generated project directory."""
        self._cleanup()

    def _cleanup(self) -> None:
        """Tear down Docker services and delete the temporary directory."""
        if not (self._cleanup_needed and os.path.exists(self.ctx.temp_dir)):
            return

        try:
            if self._cleanup_docker_services():
                # Give the daemon a moment to release bind-mounted files.
                time.sleep(3)
            force_cleanup_directory(self.ctx.temp_dir)
        except Exception as e:
            debug_log(
                f"Warning: Unexpected error during cleanup of "
                f"{self.ctx.temp_dir}: {e}",
                "warning",
            )
            try:
                force_cleanup_directory(self.ctx.temp_dir)
            except Exception:
                pass
        finally:
            self._cleanup_needed = False

    def _cleanup_docker_services(self) -> bool:
        """Stop any Docker Compose stack started for this template.

        Returns ``True`` when a teardown was actually attempted - templates
        without a compose file skip the (slow) docker invocations entirely.
        """
        compose_files = [
            name
            for name in ("docker-compose.yml", "docker-compose.yaml", "compose.yml")
            if os.path.exists(self.ctx.temp_path(name))
        ]
        if not compose_files:
            return False

        try:
            DockerCompose(self.ctx.temp_dir, compose_files[0]).cleanup()
            return True
        except Exception as e:
            debug_log(f"Failed to cleanup Docker services: {e}", "warning")
            return False

    def _generate_project(self) -> None:
        """Produce the project to inspect through the real ``startdemo`` path.

        Running the actual ``ProjectScaffolder`` (rather than re-implementing
        copy + inject here) is the point: whatever generation does for a user
        - placeholder substitution, the ``[tool.fastapi-fastkit]`` metadata
        block, the template-only files it filters out - is exactly what the
        checks then see. Virtualenv creation and dependency installation are
        switched off, so no package manager is ever invoked.

        A generation failure is propagated: there is nothing meaningful to
        inspect when the template cannot even be deployed, and ``__enter__``
        already removes the half-written directory.
        """
        template_path = self.ctx.template_path.resolve()
        project_dir = Path(self.ctx.temp_dir).resolve()

        scaffold_settings = SimpleNamespace(
            FASTKIT_TEMPLATE_ROOT=str(template_path.parent),
            USER_WORKSPACE=str(project_dir.parent),
            PACKAGE_MANAGER_CONFIG=settings.PACKAGE_MANAGER_CONFIG,
        )
        options = ScaffoldOptions(
            project_name=project_dir.name,
            author=str(DUMMY_METADATA["author"]),
            author_email=str(DUMMY_METADATA["author_email"]),
            description=str(DUMMY_METADATA["description"]),
            package_manager="uv",
            template=template_path.name,
            create_project_folder=True,
            with_venv=False,
            with_install=False,
        )

        ProjectScaffolder(scaffold_settings, options).run()

    def _load_template_config(self) -> Optional[Dict[str, Any]]:
        """Load ``template-config.yml`` from the template, if it ships one.

        The file is read from the template directory rather than the generated
        project: it is inspector-only metadata and is deliberately not copied
        into a user's project by the transducer.
        """
        config_file = str(self.ctx.template_path / "template-config.yml-tpl")
        if not os.path.exists(config_file):
            # Legacy layout: some templates shipped the config without the
            # ``-tpl`` marker, in which case it still lands in the copy.
            config_file = self.ctx.temp_path("template-config.yml")
        if not os.path.exists(config_file):
            debug_log(
                "No template-config.yml found, using default testing strategy", "info"
            )
            return None

        try:
            import yaml
        except ImportError:  # pragma: no cover - PyYAML is an optional extra
            debug_log(
                "PyYAML is not installed; ignoring template-config.yml", "warning"
            )
            return None

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
        except (yaml.YAMLError, OSError, UnicodeDecodeError) as e:
            debug_log(f"Failed to load template configuration: {e}", "warning")
            return None

        if not isinstance(config, dict):
            debug_log("Invalid template configuration format", "warning")
            return None

        debug_log(
            f"Loaded template configuration: {config.get('name', 'Unknown')}", "info"
        )
        return config

    # -- checks ------------------------------------------------------------
    def inspect_template(self) -> bool:
        """Run every inspection step, stopping at the first failure.

        :return: True if template is valid, False otherwise
        """
        check_list: List[Tuple[str, Callable[[], bool]]] = [
            ("File Structure", self._check_file_structure),
            ("File Extensions", self._check_file_extensions),
            ("Test Suite Presence", self._check_tests_present),
            ("Junk Files", self._check_no_junk_files),
            ("Dependencies", self._check_dependencies),
            ("Configuration Consistency", self._check_configuration_consistency),
            ("FastAPI Implementation", self._check_fastapi_implementation),
            ("Placeholder Substitution", self._check_no_placeholder_residue),
            ("Template Tests", self._test_template),
            ("Compile Check", self._check_compileall),
            ("Type Check", self._check_mypy),
            ("Smoke Test", self._check_smoke_test),
            ("Dependency Freshness", self._check_dependency_freshness),
        ]

        for check_name, check_func in check_list:
            debug_log(f"Running check: {check_name}", "info")
            if not check_func():
                debug_log(f"Check failed: {check_name}", "error")
                return False
            debug_log(f"Check passed: {check_name}", "info")

        return True

    def _check_file_structure(self) -> bool:
        return checks.check_file_structure(self.ctx)

    def _check_file_extensions(self) -> bool:
        return checks.check_file_extensions(self.ctx)

    def _check_dependencies(self) -> bool:
        return checks.check_dependencies(self.ctx)

    def _check_fastapi_implementation(self) -> bool:
        return checks.check_fastapi_implementation(self.ctx)

    def _check_tests_present(self) -> bool:
        return checks.check_tests_present(self.ctx)

    def _check_no_junk_files(self) -> bool:
        return checks.check_no_junk_files(self.ctx)

    def _check_no_placeholder_residue(self) -> bool:
        return checks.check_no_placeholder_residue(self.ctx)

    def _check_configuration_consistency(self) -> bool:
        return consistency.check_configuration_consistency(self.ctx)

    def _check_compileall(self) -> bool:
        return lint.check_compileall(self.ctx)

    def _check_mypy(self) -> bool:
        return lint.check_mypy(self.ctx)

    def _check_smoke_test(self) -> bool:
        return smoke.check_smoke_test(self.ctx)

    def _check_dependency_freshness(self) -> bool:
        return freshness.check_dependency_freshness(self.ctx)

    def _test_template(self) -> bool:
        return strategies.run_template_tests(self.ctx)

    def get_report(self) -> Dict[str, Any]:
        """
        Get inspection report with errors and warnings.

        :return: Dictionary containing inspection results
        """
        return build_report(self.ctx)


def inspect_fastapi_template(
    template_path: str,
    temp_base_dir: Optional[str] = None,
    options: Optional[InspectionOptions] = None,
) -> Dict[str, Any]:
    """
    Convenience function to inspect a FastAPI template.

    :param template_path: Path to the template to inspect
    :param temp_base_dir: Base directory for temporary files (defaults to backend directory)
    :param options: Optional switches (offline mode, smoke test, mypy, ...)
    :return: Inspection report dictionary
    """
    template_name = Path(template_path).name
    debug_log(
        f"Starting template inspection for {template_name} at {template_path}", "info"
    )

    with TemplateInspector(template_path, temp_base_dir, options) as inspector:
        is_valid = inspector.inspect_template()
        report = inspector.get_report()
        print_report(inspector.ctx, is_valid)

    debug_log(
        f"Template inspection completed for {template_name}. Valid: {is_valid}, "
        f"Errors: {len(report['errors'])}, Warnings: {len(report['warnings'])}",
        "info",
    )
    return report
