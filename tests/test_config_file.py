# --------------------------------------------------------------------------
# Testcases for project configuration file (de)serialization.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from pathlib import Path
from unittest.mock import patch

import pytest

from fastapi_fastkit.utils.config_file import (
    ConfigFileError,
    format_toml_value,
    load_normalized_project_config,
    load_project_config,
    save_project_config,
    validate_project_config,
)

VALID_CONFIG = {
    "project_name": "demo-project",
    "author": "bnbong",
    "author_email": "bbbong9@gmail.com",
    "description": "demo",
}


class TestLoadProjectConfig:
    """``load_project_config`` reads JSON / TOML / YAML files by extension."""

    def test_raises_when_file_missing(self, tmp_path: Path) -> None:
        # given
        missing = tmp_path / "missing.json"

        # when / then
        with pytest.raises(ConfigFileError, match="not found"):
            load_project_config(str(missing))

    def test_loads_json_file(self, tmp_path: Path) -> None:
        # given
        path = tmp_path / "config.json"
        path.write_text('{"project_name": "demo"}')

        # when
        result = load_project_config(str(path))

        # then
        assert result == {"project_name": "demo"}

    def test_raises_on_invalid_json(self, tmp_path: Path) -> None:
        # given
        path = tmp_path / "config.json"
        path.write_text("{not valid json")

        # when / then
        with pytest.raises(ConfigFileError, match="Could not parse JSON"):
            load_project_config(str(path))

    def test_loads_toml_file(self, tmp_path: Path) -> None:
        # given
        path = tmp_path / "config.toml"
        path.write_text('project_name = "demo"\n')

        # when
        result = load_project_config(str(path))

        # then
        assert result == {"project_name": "demo"}

    def test_raises_on_invalid_toml(self, tmp_path: Path) -> None:
        # given
        path = tmp_path / "config.toml"
        path.write_text("not = valid = toml")

        # when / then
        with pytest.raises(ConfigFileError, match="Could not parse TOML"):
            load_project_config(str(path))

    def test_loads_yaml_file(self, tmp_path: Path) -> None:
        # given
        yaml = pytest.importorskip("yaml")
        path = tmp_path / "config.yaml"
        path.write_text("project_name: demo\n")

        # when
        result = load_project_config(str(path))

        # then
        assert result == {"project_name": "demo"}

    def test_raises_when_yaml_module_missing(self, tmp_path: Path) -> None:
        # given
        path = tmp_path / "config.yaml"
        path.write_text("project_name: demo\n")

        # when / then
        with patch("fastapi_fastkit.utils.config_file._yaml_module", return_value=None):
            with pytest.raises(ConfigFileError, match="PyYAML"):
                load_project_config(str(path))

    def test_raises_on_invalid_yaml(self, tmp_path: Path) -> None:
        # given
        pytest.importorskip("yaml")
        path = tmp_path / "config.yaml"
        path.write_text("key: [unclosed\n")

        # when / then
        with pytest.raises(ConfigFileError, match="Could not parse YAML"):
            load_project_config(str(path))

    def test_raises_on_unsupported_extension(self, tmp_path: Path) -> None:
        # given
        path = tmp_path / "config.ini"
        path.write_text("project_name = demo")

        # when / then
        with pytest.raises(ConfigFileError, match="Unsupported config file extension"):
            load_project_config(str(path))

    def test_raises_when_top_level_is_not_a_mapping(self, tmp_path: Path) -> None:
        # given
        path = tmp_path / "config.json"
        path.write_text("[1, 2, 3]")

        # when / then
        with pytest.raises(ConfigFileError, match="must contain a mapping"):
            load_project_config(str(path))


class TestValidateProjectConfig:
    """Validation mirrors the interactive-mode rules."""

    def test_valid_config_has_no_errors(self) -> None:
        # given / when
        errors = validate_project_config(dict(VALID_CONFIG))

        # then
        assert errors == []

    def test_reports_missing_required_keys(self) -> None:
        # given
        config: dict = {}

        # when
        errors = validate_project_config(config)

        # then
        assert any("project_name" in e for e in errors)
        assert any("author" in e for e in errors)
        assert any("author_email" in e for e in errors)

    def test_reports_invalid_project_name(self) -> None:
        # given
        config = dict(VALID_CONFIG)
        config["project_name"] = "1 invalid name!"

        # when
        errors = validate_project_config(config)

        # then
        assert len(errors) > 0

    def test_reports_invalid_email(self) -> None:
        # given
        config = dict(VALID_CONFIG)
        config["author_email"] = "not-an-email"

        # when
        errors = validate_project_config(config)

        # then
        assert any("Invalid author email format" in e for e in errors)


class TestLoadNormalizedProjectConfig:
    """The normalised loader wraps schema errors into ConfigFileError."""

    def test_loads_and_normalizes(self, tmp_path: Path) -> None:
        # given
        path = tmp_path / "config.json"
        path.write_text(
            '{"project_name": "demo", "author": "bnbong", '
            '"author_email": "bbbong9@gmail.com"}'
        )

        # when
        result = load_normalized_project_config(str(path))

        # then
        assert result["project_name"] == "demo"

    def test_raises_config_file_error_on_schema_error(self, tmp_path: Path) -> None:
        # given
        path = tmp_path / "config.json"
        path.write_text('{"project_name": "demo", "database": "not-a-mapping"}')

        # when / then
        with pytest.raises(ConfigFileError, match="Invalid project config"):
            load_normalized_project_config(str(path))


class TestSaveProjectConfig:
    """Serialization round-trips through JSON / TOML / YAML."""

    def test_saves_json(self, tmp_path: Path) -> None:
        # given
        path = tmp_path / "out.json"

        # when
        save_project_config(dict(VALID_CONFIG), str(path))

        # then
        assert '"project_name": "demo-project"' in path.read_text()

    def test_saves_toml(self, tmp_path: Path) -> None:
        # given
        path = tmp_path / "out.toml"
        config = dict(VALID_CONFIG)
        config["database"] = {"engine": "postgresql", "port": 5432}
        config["features"] = ["docker", "auth"]

        # when
        save_project_config(config, str(path))

        # then
        content = path.read_text()
        assert 'project_name = "demo-project"' in content
        assert "[database]" in content
        assert 'engine = "postgresql"' in content
        assert "port = 5432" in content
        assert 'features = ["docker", "auth"]' in content

    def test_saves_yaml(self, tmp_path: Path) -> None:
        # given
        pytest.importorskip("yaml")
        path = tmp_path / "out.yaml"

        # when
        save_project_config(dict(VALID_CONFIG), str(path))

        # then
        assert "project_name" in path.read_text()

    def test_raises_when_yaml_module_missing_on_save(self, tmp_path: Path) -> None:
        # given
        path = tmp_path / "out.yaml"

        # when / then
        with patch("fastapi_fastkit.utils.config_file._yaml_module", return_value=None):
            with pytest.raises(ConfigFileError, match="PyYAML"):
                save_project_config(dict(VALID_CONFIG), str(path))

    def test_raises_on_unsupported_extension(self, tmp_path: Path) -> None:
        # given
        path = tmp_path / "out.ini"

        # when / then
        with pytest.raises(ConfigFileError, match="Unsupported config file extension"):
            save_project_config(dict(VALID_CONFIG), str(path))

    def test_raises_on_write_failure(self, tmp_path: Path) -> None:
        # given
        path = tmp_path / "out.json"

        # when / then
        with patch("builtins.open", side_effect=OSError("disk full")):
            with pytest.raises(ConfigFileError, match="Could not write config file"):
                save_project_config(dict(VALID_CONFIG), str(path))

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        # given
        path = tmp_path / "nested" / "dir" / "out.json"

        # when
        save_project_config(dict(VALID_CONFIG), str(path))

        # then
        assert path.exists()


class TestFormatTomlValue:
    """TOML literal rendering for the scalar types the config dict carries."""

    def test_bool(self) -> None:
        assert format_toml_value(True) == "true"
        assert format_toml_value(False) == "false"

    def test_numbers(self) -> None:
        assert format_toml_value(5) == "5"
        assert format_toml_value(1.5) == "1.5"

    def test_list(self) -> None:
        assert format_toml_value(["a", "b"]) == '["a", "b"]'

    def test_string_escaping(self) -> None:
        assert format_toml_value('say "hi"\\') == '"say \\"hi\\"\\\\"'
