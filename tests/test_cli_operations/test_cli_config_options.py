# NOTE: For panel outputs, assertions may not work properly due to ANSI output issues even when output strings are identical.
# --------------------------------------------------------------------------
# Testcases of the config-file / dry-run / environment CLI options.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import ast
import json
import os
from pathlib import Path
from typing import Any, Dict, List

import pytest
from click.testing import CliRunner

from fastapi_fastkit.backend.interactive import InteractiveConfigBuilder
from fastapi_fastkit.backend.project_builder.config_schema import (
    ConfigSchemaError,
    normalize_project_config,
    validate_project_config_schema,
)
from fastapi_fastkit.cli import fastkit_cli
from fastapi_fastkit.core.settings import FastkitConfig
from fastapi_fastkit.utils.config_file import (
    ConfigFileError,
    load_project_config,
    save_project_config,
    validate_project_config,
)
from fastapi_fastkit.utils.main import read_fastkit_metadata

MINIMAL_CONFIG: Dict[str, Any] = {
    "project_name": "config-driven",
    "author": "bnbong",
    "author_email": "bbbong9@gmail.com",
    "description": "created from a config file",
    "package_manager": "pip",
    "architecture_preset": "minimal",
    "database": {"type": "None", "packages": []},
    "authentication": "None",
    "async_tasks": "None",
    "caching": "None",
    "monitoring": "None",
    "testing": "None",
    "utilities": [],
    "all_dependencies": ["fastapi", "uvicorn"],
}


class TestConfigFileSerialization:
    def test_json_round_trip(self, tmp_path: Path) -> None:
        # given
        path = str(tmp_path / "fastkit.config.json")

        # when
        save_project_config(MINIMAL_CONFIG, path)
        loaded = load_project_config(path)

        # then
        assert loaded == MINIMAL_CONFIG

    def test_toml_round_trip(self, tmp_path: Path) -> None:
        # given
        path = str(tmp_path / "fastkit.config.toml")

        # when
        save_project_config(MINIMAL_CONFIG, path)
        loaded = load_project_config(path)

        # then
        assert loaded["project_name"] == "config-driven"
        assert loaded["all_dependencies"] == ["fastapi", "uvicorn"]
        assert loaded["database"] == {"type": "None", "packages": []}

    def test_unsupported_extension_is_rejected(self, tmp_path: Path) -> None:
        # given
        path = tmp_path / "fastkit.config.ini"
        path.write_text("nope")

        # when & then
        with pytest.raises(ConfigFileError, match="Unsupported config file extension"):
            load_project_config(str(path))

    def test_missing_file_is_rejected(self, tmp_path: Path) -> None:
        # when & then
        with pytest.raises(ConfigFileError, match="not found"):
            load_project_config(str(tmp_path / "absent.json"))

    def test_validation_reuses_interactive_rules(self) -> None:
        # given
        config = dict(MINIMAL_CONFIG, project_name="1bad", author_email="not-an-email")

        # when
        errors = validate_project_config(config)

        # then
        assert any("cannot start with a number" in error for error in errors)
        assert any("Invalid author email" in error for error in errors)

    def test_validation_requires_core_keys(self) -> None:
        # when
        errors = validate_project_config({})

        # then
        assert len(errors) == 3


class TestCLIConfigOptions:
    def setup_method(self) -> None:
        self.runner = CliRunner()
        self.current_workspace = os.getcwd()

    def teardown_method(self) -> None:
        os.chdir(self.current_workspace)

    def _write_config(self, tmp_path: Path, **overrides: Any) -> str:
        config = dict(MINIMAL_CONFIG)
        config.update(overrides)
        path = tmp_path / "fastkit.config.json"
        path.write_text(json.dumps(config))
        return str(path)

    def test_init_from_config_file_creates_project(self, tmp_path: Path) -> None:
        # given
        config_path = self._write_config(tmp_path)
        os.chdir(tmp_path)

        # when
        result = self.runner.invoke(
            fastkit_cli,
            ["init", "--config", config_path, "--no-venv"],
            input="Y\n",  # Create a new project folder
        )

        # then
        project_path = tmp_path / "config-driven"
        assert project_path.is_dir(), result.output
        metadata = read_fastkit_metadata(str(project_path))
        assert metadata["managed"] is True
        assert metadata["preset"] == "minimal"
        assert metadata["app_module"] == "src.main:app"
        assert metadata["package_manager"] == "pip"
        assert not (project_path / ".venv").exists()

    def test_init_from_config_reports_validation_errors(self, tmp_path: Path) -> None:
        # given
        config_path = self._write_config(tmp_path, author_email="broken")
        os.chdir(tmp_path)

        # when
        result = self.runner.invoke(
            fastkit_cli, ["init", "--config", config_path, "--no-venv"]
        )

        # then
        assert "Invalid author email" in result.output
        assert not (tmp_path / "config-driven").exists()

    def test_init_from_config_reports_missing_file(self, tmp_path: Path) -> None:
        # given
        os.chdir(tmp_path)

        # when
        result = self.runner.invoke(
            fastkit_cli, ["init", "--config", str(tmp_path / "absent.json")]
        )

        # then
        assert "not found" in result.output

    def test_init_dry_run_writes_nothing(self, tmp_path: Path) -> None:
        # given
        config_path = self._write_config(tmp_path)
        os.chdir(tmp_path)

        # when
        result = self.runner.invoke(
            fastkit_cli, ["init", "--config", config_path, "--dry-run"]
        )

        # then
        assert "Files that would be created" in result.output
        assert "Packages that would be installed" in result.output
        assert not (tmp_path / "config-driven").exists()
        assert os.listdir(tmp_path) == ["fastkit.config.json"]

    def test_startdemo_dry_run_writes_nothing(self, tmp_path: Path) -> None:
        # given
        os.chdir(tmp_path)

        # when
        result = self.runner.invoke(
            fastkit_cli,
            [
                "startdemo",
                "fastapi-default",
                "--project-name",
                "dry-demo",
                "--author",
                "bnbong",
                "--author-email",
                "bbbong9@gmail.com",
                "--description",
                "dry run demo",
                "--package-manager",
                "pip",
                "--dry-run",
            ],
            input="Y\n",  # Proceed with project creation
        )

        # then
        assert "Files that would be created" in result.output
        assert "Dry run complete" in result.output
        assert os.listdir(tmp_path) == []

    def test_init_no_install_still_creates_the_project(self, tmp_path: Path) -> None:
        # given
        config_path = self._write_config(tmp_path, project_name="no-install-project")
        os.chdir(tmp_path)

        # when
        result = self.runner.invoke(
            fastkit_cli,
            ["init", "--config", config_path, "--no-venv", "--no-install"],
            input="Y\n",
        )

        # then
        project_path = tmp_path / "no-install-project"
        assert project_path.is_dir(), result.output
        assert not (project_path / ".venv").exists()

    def test_init_config_without_dependencies_derives_them(
        self, tmp_path: Path
    ) -> None:
        # given: a hand-written config that only lists feature selections
        config = dict(MINIMAL_CONFIG)
        config.pop("all_dependencies")
        config["project_name"] = "derived-deps"
        config["database"] = {"type": "SQLite", "packages": ["sqlalchemy"]}
        path = tmp_path / "fastkit.config.json"
        path.write_text(json.dumps(config))
        os.chdir(tmp_path)

        # when
        result = self.runner.invoke(
            fastkit_cli,
            ["init", "--config", str(path), "--no-venv"],
            input="Y\n",
        )

        # then
        project_path = tmp_path / "derived-deps"
        assert project_path.is_dir(), result.output
        pyproject = (project_path / "pyproject.toml").read_text()
        assert "sqlalchemy" in pyproject
        assert "database:SQLite" in read_fastkit_metadata(str(project_path))["features"]


class TestLayoutAwareCommands:
    """addroute / runserver must follow the generated layout, not ``src/``."""

    def setup_method(self) -> None:
        self.runner = CliRunner()
        self.current_workspace = os.getcwd()

    def teardown_method(self) -> None:
        os.chdir(self.current_workspace)

    def _generate(self, tmp_path: Path, template: str, preset: str) -> Path:
        from fastapi_fastkit.backend.scaffolder import (
            ProjectScaffolder,
            ScaffoldOptions,
        )
        from fastapi_fastkit.core.settings import FastkitConfig

        settings = FastkitConfig()
        settings.USER_WORKSPACE = str(tmp_path)
        scaffolder = ProjectScaffolder(
            settings,
            ScaffoldOptions(
                project_name="layout-project",
                author="bnbong",
                author_email="bbbong9@gmail.com",
                description="layout testcase project",
                package_manager="pip",
                template=template,
                preset_id=preset,
                with_venv=False,
                with_install=False,
            ),
        )
        return Path(scaffolder.run().project_dir)

    def test_addroute_targets_the_domain_starter_layout(self, tmp_path: Path) -> None:
        # given
        project_path = self._generate(
            tmp_path, "fastapi-domain-starter", "domain-starter"
        )
        os.chdir(project_path)

        # when
        result = self.runner.invoke(fastkit_cli, ["addroute", "user", "."], input="Y\n")

        # then
        assert "Successfully added new route" in result.output, result.output
        assert (project_path / "src" / "app" / "api" / "routes" / "user.py").exists()
        # the classic layout must not be created alongside it
        assert not (project_path / "src" / "api").exists()

        router_content = (
            project_path / "src" / "app" / "api" / "router.py"
        ).read_text()
        assert "from .routes import user" in router_content

    def test_addroute_imports_resolve_for_the_domain_starter_layout(
        self, tmp_path: Path
    ) -> None:
        # given
        project_path = self._generate(
            tmp_path, "fastapi-domain-starter", "domain-starter"
        )
        os.chdir(project_path)

        # when
        result = self.runner.invoke(fastkit_cli, ["addroute", "user", "."], input="Y\n")

        # then
        assert "Successfully added new route" in result.output, result.output
        route_content = (
            project_path / "src" / "app" / "api" / "routes" / "user.py"
        ).read_text()
        assert "from src.app.crud.user import *" in route_content
        assert "from src.app.schemas.user import *" in route_content
        assert "<package_root>" not in route_content
        assert _unresolved_project_imports(project_path) == []

    def test_addroute_imports_resolve_for_the_classic_layout(
        self, tmp_path: Path
    ) -> None:
        # given
        project_path = self._generate(tmp_path, "fastapi-default", "classic-layered")
        os.chdir(project_path)

        # when
        result = self.runner.invoke(fastkit_cli, ["addroute", "user", "."], input="Y\n")

        # then
        assert "Successfully added new route" in result.output, result.output
        route_content = (
            project_path / "src" / "api" / "routes" / "user.py"
        ).read_text()
        assert "from src.crud.user import *" in route_content
        assert "from src.schemas.user import *" in route_content
        assert _unresolved_project_imports(project_path) == []

    def test_runserver_prefers_the_recorded_app_module(self, tmp_path: Path) -> None:
        # given
        from fastapi_fastkit.cli import _resolve_runserver_app_module

        project_path = self._generate(
            tmp_path, "fastapi-domain-starter", "domain-starter"
        )

        # when
        app_module = _resolve_runserver_app_module(str(project_path))

        # then
        assert app_module == "src.app.main:app"


#: A config written the way a user reaches for it rather than the way the
#: interactive builder emits it: every single-select axis as a
#: ``{"type": ...}`` block, the preset under its metadata alias.
DICT_SHAPED_CONFIG: Dict[str, Any] = {
    "project_name": "cfgapp",
    "author": "bnbong",
    "author_email": "bbbong9@gmail.com",
    "description": "cfg e2e",
    "package_manager": "pip",
    "preset": "minimal",
    "database": {"type": "PostgreSQL"},
    "authentication": {"type": "JWT"},
    "async_tasks": {"type": "Celery"},
    "caching": {"type": "Redis"},
    "migrations": {"type": "Alembic"},
    "tooling": ["ruff", "makefile"],
    "logging": {"type": "structured"},
    "deployment": ["Docker", "docker-compose"],
    "utilities": ["CORS", "WebSocket"],
}


def _unresolved_project_imports(project_path: Path) -> List[str]:
    """
    Return the ``from src.…`` imports of a generated project that lead nowhere.

    Standing in for ``python -c "import src.main"``: the generated project's
    third-party dependencies are deliberately not installed by these tests
    (``--no-venv``), so the modules are parsed instead and every intra-project
    import is resolved against the files on disk.
    """
    missing: List[str] = []

    for module_path in sorted(project_path.rglob("*.py")):
        tree = ast.parse(module_path.read_text(), filename=str(module_path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom) or not node.module:
                continue
            if node.module != "src" and not node.module.startswith("src."):
                continue
            relative = node.module.replace(".", os.sep)
            module_file = project_path / f"{relative}.py"
            package_file = project_path / relative / "__init__.py"
            if not module_file.exists() and not package_file.exists():
                missing.append(f"{module_path.name} -> {node.module}")

    return missing


class TestConfigSchemaNormalization:
    """A config file may spell an axis several ways; all resolve to one shape."""

    def test_dict_shaped_axes_are_normalized(self) -> None:
        # when
        normalized = normalize_project_config(DICT_SHAPED_CONFIG)

        # then
        assert normalized["database"] == {
            "type": "PostgreSQL",
            "packages": ["asyncpg", "sqlalchemy"],
        }
        assert normalized["authentication"] == "JWT"
        assert normalized["async_tasks"] == "Celery"
        assert normalized["caching"] == "Redis"
        assert normalized["migrations"] == "Alembic"
        assert normalized["logging"] == "structured"
        # The metadata alias folds into the canonical preset key.
        assert normalized["architecture_preset"] == "minimal"
        assert "preset" not in normalized
        # Unset axes get their sentinel, so every consumer reads the same keys.
        assert normalized["monitoring"] == "None"
        assert normalized["testing"] == "None"

    def test_normalization_is_idempotent(self) -> None:
        # when
        once = normalize_project_config(DICT_SHAPED_CONFIG)
        twice = normalize_project_config(once)

        # then
        assert once == twice

    def test_dependency_collector_sees_every_normalized_axis(self) -> None:
        # given
        settings = FastkitConfig()

        # when
        config = InteractiveConfigBuilder(settings).build_config_from_mapping(
            DICT_SHAPED_CONFIG
        )

        # then
        dependencies = config["all_dependencies"]
        for package in (
            "asyncpg",
            "python-jose[cryptography]",
            "celery[redis]",
            "fastapi-cache2",
            "alembic",
            "ruff",
            "websockets",
        ):
            assert package in dependencies

    def test_unknown_choice_is_rejected(self) -> None:
        # given
        config = dict(DICT_SHAPED_CONFIG, authentication="Kerberos")

        # when & then
        with pytest.raises(ConfigSchemaError, match="Unknown 'authentication' option"):
            normalize_project_config(config)

    def test_unknown_key_is_rejected(self) -> None:
        # given
        config = dict(DICT_SHAPED_CONFIG, databse={"type": "SQLite"})

        # when & then
        with pytest.raises(ConfigSchemaError, match="Unknown config key 'databse'"):
            normalize_project_config(config)

    def test_wrong_value_type_is_rejected(self) -> None:
        # given
        config = dict(DICT_SHAPED_CONFIG, caching=["Redis"], logging=3)

        # when
        errors = validate_project_config_schema(config)

        # then
        assert any("'caching' takes a single choice" in error for error in errors)
        assert any("'logging' must be a string" in error for error in errors)

    def test_unknown_preset_and_package_manager_are_rejected(self) -> None:
        # given
        config = dict(DICT_SHAPED_CONFIG, preset="hexagonal", package_manager="conda")

        # when
        errors = validate_project_config_schema(config)

        # then
        assert any("Unknown architecture preset" in error for error in errors)
        assert any("Unknown package manager" in error for error in errors)

    def test_compose_deployment_implies_docker(self) -> None:
        # given
        config = dict(DICT_SHAPED_CONFIG, deployment=["docker-compose"])

        # when
        normalized = normalize_project_config(config)

        # then
        assert normalized["deployment"] == ["Docker", "docker-compose"]

    def test_validation_reports_schema_errors(self) -> None:
        # given
        config = dict(DICT_SHAPED_CONFIG, utilities=["Telepathy"])

        # when
        errors = validate_project_config(config)

        # then
        assert any(
            "Unknown 'utilities' option 'Telepathy'" in error for error in errors
        )

    def test_saved_config_round_trips_through_normalization(
        self, tmp_path: Path
    ) -> None:
        # given: what --save-config would write for a file-driven run
        settings = FastkitConfig()
        saved = InteractiveConfigBuilder(settings).build_config_from_mapping(
            DICT_SHAPED_CONFIG
        )
        path = str(tmp_path / "fastkit.config.json")

        # when
        save_project_config(saved, path)
        reloaded = load_project_config(path)

        # then
        assert reloaded == saved
        assert not validate_project_config(reloaded)
        assert normalize_project_config(reloaded) == reloaded


class TestConfigSchemaRejectionCases:
    """Every rejection branch of ``_normalize`` and its axis helpers."""

    def test_non_dict_config_is_rejected(self) -> None:
        # when
        errors = validate_project_config_schema(["not", "a", "dict"])  # type: ignore[arg-type]

        # then
        assert errors == ["Project configuration must be a mapping."]

    def test_unknown_config_key_is_rejected(self) -> None:
        # given
        config = dict(DICT_SHAPED_CONFIG, bogus_key="oops")

        # when
        errors = validate_project_config_schema(config)

        # then
        assert any("Unknown config key 'bogus_key'" in error for error in errors)

    def test_scalar_choice_rejects_unknown_dict_fields(self) -> None:
        # given: a {"type": ...} mapping with an unexpected extra field
        config = dict(DICT_SHAPED_CONFIG, authentication={"type": "JWT", "level": "hi"})

        # when
        errors = validate_project_config_schema(config)

        # then
        assert any("may only hold 'type' and 'packages'" in error for error in errors)

    def test_scalar_choice_rejects_non_string_non_dict(self) -> None:
        # given
        config = dict(DICT_SHAPED_CONFIG, authentication=42)

        # when
        errors = validate_project_config_schema(config)

        # then
        assert any(
            "must be a string or a {'type': ...} mapping" in error for error in errors
        )

    def test_single_select_axis_rejects_list(self) -> None:
        # given
        config = dict(DICT_SHAPED_CONFIG, authentication=["JWT"])

        # when
        errors = validate_project_config_schema(config)

        # then
        assert any(
            "'authentication' takes a single choice, not a list" in error
            for error in errors
        )

    def test_multi_select_axis_rejects_non_list_non_string(self) -> None:
        # given
        config = dict(DICT_SHAPED_CONFIG, tooling=42)

        # when
        errors = validate_project_config_schema(config)

        # then
        assert any(
            "'tooling' must be a list of choices, got int" in error for error in errors
        )

    def test_multi_select_axis_rejects_non_string_items(self) -> None:
        # given
        config = dict(DICT_SHAPED_CONFIG, tooling=["ruff", 42])

        # when
        errors = validate_project_config_schema(config)

        # then
        assert any(
            "'tooling' may only contain strings, got int" in error for error in errors
        )

    def test_multi_select_axis_accepts_dict_shape(self) -> None:
        # given: a single {"type": ...} mapping for a multi-select axis
        config = dict(DICT_SHAPED_CONFIG, tooling={"type": "ruff"})

        # when
        normalized = normalize_project_config(config)

        # then
        assert normalized["tooling"] == ["ruff"]

    def test_database_axis_rejects_list(self) -> None:
        # given
        config = dict(DICT_SHAPED_CONFIG, database=["PostgreSQL"])

        # when
        errors = validate_project_config_schema(config)

        # then
        assert any(
            "'database' takes a single choice, not a list" in error for error in errors
        )

    def test_database_axis_rejects_unknown_choice(self) -> None:
        # given
        config = dict(DICT_SHAPED_CONFIG, database={"type": "Oracle"})

        # when
        errors = validate_project_config_schema(config)

        # then
        assert any("Unknown 'database' option 'Oracle'" in error for error in errors)

    def test_conflicting_preset_aliases_are_rejected(self) -> None:
        # given
        config = dict(
            DICT_SHAPED_CONFIG, preset="minimal", architecture_preset="classic-layered"
        )

        # when
        errors = validate_project_config_schema(config)

        # then
        assert any("Conflicting presets" in error for error in errors)

    def test_deployment_string_is_normalized_to_list(self) -> None:
        # given
        config = dict(DICT_SHAPED_CONFIG, deployment="Docker")

        # when
        normalized = normalize_project_config(config)

        # then
        assert normalized["deployment"] == ["Docker"]

    def test_deployment_rejects_non_list_non_string(self) -> None:
        # given
        config = dict(DICT_SHAPED_CONFIG, deployment=42)

        # when
        errors = validate_project_config_schema(config)

        # then
        assert any(
            "'deployment' must be a list of targets, got int" in error
            for error in errors
        )

    def test_deployment_rejects_unknown_target(self) -> None:
        # given
        config = dict(DICT_SHAPED_CONFIG, deployment=["Kubernetes"])

        # when
        errors = validate_project_config_schema(config)

        # then
        assert any(
            "Unknown 'deployment' target 'Kubernetes'" in error for error in errors
        )

    def test_custom_packages_must_be_a_string_list(self) -> None:
        # given
        config = dict(DICT_SHAPED_CONFIG, custom_packages="not-a-list")

        # when
        errors = validate_project_config_schema(config)

        # then
        assert any(
            "'custom_packages' must be a list of strings" in error for error in errors
        )


class TestConfigDrivenProjectIsImportable:
    def setup_method(self) -> None:
        self.runner = CliRunner()
        self.current_workspace = os.getcwd()

    def teardown_method(self) -> None:
        os.chdir(self.current_workspace)

    def test_dict_shaped_config_generates_an_importable_project(
        self, tmp_path: Path
    ) -> None:
        # given
        path = tmp_path / "fastkit.config.json"
        path.write_text(json.dumps(DICT_SHAPED_CONFIG))
        os.chdir(tmp_path)

        # when
        result = self.runner.invoke(
            fastkit_cli,
            ["init", "--config", str(path), "--no-venv"],
            input="Y\n",
        )

        # then
        project_path = tmp_path / "cfgapp"
        assert project_path.is_dir(), result.output

        features = read_fastkit_metadata(str(project_path))["features"]
        for feature in (
            "database:PostgreSQL",
            "authentication:JWT",
            "async_tasks:Celery",
            "caching:Redis",
            "migrations:Alembic",
            "logging:structured",
        ):
            assert feature in features

        # every ``from src.…`` the generated code emits must resolve on disk
        assert _unresolved_project_imports(project_path) == []
