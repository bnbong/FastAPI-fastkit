# --------------------------------------------------------------------------
# Project configuration file (de)serialization for non-interactive ``init``.
#
# ``fastkit init --interactive`` builds a plain configuration dict; this
# module lets that same dict travel through a file so a project can be
# reproduced without answering a single prompt (``--config``), and so an
# interactive session can be captured for later reuse (``--save-config``).
#
# Supported formats are picked from the file extension: JSON and TOML are
# always available (both ship with the stdlib on Python 3.12), YAML only
# when PyYAML happens to be installed — fastkit deliberately does not add it
# as a runtime dependency.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import importlib
import json
import os
import tomllib
from typing import Any, Dict, List, Tuple

from fastapi_fastkit.backend.interactive.validators import (
    validate_email_format,
    validate_project_name,
)
from fastapi_fastkit.backend.project_builder.config_schema import (
    ConfigSchemaError,
    normalize_project_config,
    validate_project_config_schema,
)

JSON_EXTENSIONS: Tuple[str, ...] = (".json",)
TOML_EXTENSIONS: Tuple[str, ...] = (".toml",)
YAML_EXTENSIONS: Tuple[str, ...] = (".yaml", ".yml")

SUPPORTED_EXTENSIONS: Tuple[str, ...] = (
    JSON_EXTENSIONS + TOML_EXTENSIONS + YAML_EXTENSIONS
)

# Keys the scaffolder needs; everything else in the file is passed through
# untouched so feature blocks stay forward-compatible.
REQUIRED_KEYS: Tuple[str, ...] = ("project_name", "author", "author_email")


class ConfigFileError(Exception):
    """Raised when a project config file cannot be read, parsed or trusted."""


def _yaml_module() -> Any:
    """Return the optional PyYAML module, or None when it isn't installed."""
    try:
        # Imported dynamically: PyYAML is optional, so a static import would
        # make it look like a hard dependency to type checkers and readers.
        return importlib.import_module("yaml")
    except ImportError:
        return None


def load_project_config(path: str) -> Dict[str, Any]:
    """
    Load a project configuration dict from a JSON / TOML / YAML file.

    :param path: Path to the configuration file
    :return: Configuration dictionary equivalent to the interactive builder's
    :raises ConfigFileError: If the file is missing, of an unsupported format,
        unparsable, or does not describe a mapping.
    """
    if not os.path.exists(path):
        raise ConfigFileError(f"Config file not found: {path}")

    extension = os.path.splitext(path)[1].lower()

    if extension in JSON_EXTENSIONS:
        raw = _load_json(path)
    elif extension in TOML_EXTENSIONS:
        raw = _load_toml(path)
    elif extension in YAML_EXTENSIONS:
        raw = _load_yaml(path)
    else:
        raise ConfigFileError(
            f"Unsupported config file extension '{extension or path}'. "
            f"Supported extensions: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    if not isinstance(raw, dict):
        raise ConfigFileError(
            f"Config file '{path}' must contain a mapping at its top level."
        )

    return raw


def _load_json(path: str) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as e:
        raise ConfigFileError(f"Could not parse JSON config '{path}': {e}")


def _load_toml(path: str) -> Any:
    try:
        with open(path, "rb") as f:
            return tomllib.load(f)
    except (OSError, tomllib.TOMLDecodeError) as e:
        raise ConfigFileError(f"Could not parse TOML config '{path}': {e}")


def _load_yaml(path: str) -> Any:
    yaml = _yaml_module()
    if yaml is None:
        raise ConfigFileError(
            "YAML config files need PyYAML, which is not installed. "
            "Install it (pip install pyyaml) or use a .json / .toml config file instead."
        )
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        # PyYAML raises its own YAMLError hierarchy; catching broadly keeps
        # this import-optional module free of a yaml type import.
        raise ConfigFileError(f"Could not parse YAML config '{path}': {e}")


def validate_project_config(config: Dict[str, Any]) -> List[str]:
    """
    Validate a loaded configuration against the interactive-mode rules.

    Reuses ``interactive.validators`` so a file-driven run is held to exactly
    the same standard as an answered prompt.

    :param config: Configuration dictionary
    :return: List of human-readable error messages (empty when the config is valid)
    """
    errors: List[str] = []

    for key in REQUIRED_KEYS:
        if not config.get(key):
            errors.append(f"Missing required config key: '{key}'")

    project_name = config.get("project_name")
    if isinstance(project_name, str) and project_name:
        is_valid, message = validate_project_name(project_name)
        if not is_valid and message:
            errors.append(message)

    author_email = config.get("author_email")
    if isinstance(author_email, str) and author_email:
        if not validate_email_format(author_email):
            errors.append(f"Invalid author email format: '{author_email}'")

    # Feature selections are held to the catalog: an axis spelled in a shape
    # the pipeline cannot read used to reach generation and produce a project
    # whose ``main.py`` imported modules nobody wrote.
    errors.extend(validate_project_config_schema(config))

    return errors


def load_normalized_project_config(path: str) -> Dict[str, Any]:
    """
    Load a config file and return it in the canonical pipeline shape.

    ``load_project_config`` deliberately hands back exactly what the file
    said (so ``--save-config`` round-trips byte for byte); this wrapper is
    what the generation pipeline consumes, because every consumer of a
    configuration must see the same normalised selections.

    :param path: Path to the configuration file
    :return: Normalised configuration dictionary
    :raises ConfigFileError: If the file cannot be read, parsed or trusted
    """
    raw = load_project_config(path)
    try:
        return normalize_project_config(raw)
    except ConfigSchemaError as e:
        raise ConfigFileError(f"Invalid project config '{path}': {e}")


def save_project_config(config: Dict[str, Any], path: str) -> None:
    """
    Write a configuration dict to a JSON / TOML / YAML file.

    :param config: Configuration dictionary produced by the interactive builder
    :param path: Destination path; the extension selects the format
    :raises ConfigFileError: If the format is unsupported or the write fails
    """
    extension = os.path.splitext(path)[1].lower()

    if extension in JSON_EXTENSIONS:
        content = (
            json.dumps(config, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
        )
    elif extension in TOML_EXTENSIONS:
        content = _dump_toml(config)
    elif extension in YAML_EXTENSIONS:
        yaml = _yaml_module()
        if yaml is None:
            raise ConfigFileError(
                "Saving YAML config files needs PyYAML, which is not installed. "
                "Use a .json / .toml path instead."
            )
        content = str(yaml.safe_dump(config, sort_keys=True, allow_unicode=True))
    else:
        raise ConfigFileError(
            f"Unsupported config file extension '{extension or path}'. "
            f"Supported extensions: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    try:
        parent = os.path.dirname(os.path.abspath(path))
        os.makedirs(parent, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    except OSError as e:
        raise ConfigFileError(f"Could not write config file '{path}': {e}")


def _dump_toml(config: Dict[str, Any]) -> str:
    """
    Serialize a configuration dict to TOML.

    Python 3.12 ships a TOML reader but no writer, and fastkit may not add a
    runtime dependency for one. The interactive config only ever holds
    strings, booleans, numbers, string lists and one level of nested tables
    (``database``), which this covers.
    """
    scalars: List[str] = []
    tables: List[str] = []

    for key in sorted(config):
        value = config[key]
        if isinstance(value, dict):
            table_lines = [f"[{key}]"]
            for sub_key in sorted(value):
                table_lines.append(f"{sub_key} = {format_toml_value(value[sub_key])}")
            tables.append("\n".join(table_lines))
        else:
            scalars.append(f"{key} = {format_toml_value(value)}")

    sections = ["\n".join(scalars)] if scalars else []
    sections.extend(tables)
    return "\n\n".join(section for section in sections if section) + "\n"


def format_toml_value(value: Any) -> str:
    """
    Render a Python value as a TOML literal.

    Shared with pyproject metadata injection so both writers escape and
    quote values identically.

    :param value: Value to render (bool / int / float / list / str)
    :return: TOML literal string
    """
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(format_toml_value(item) for item in value) + "]"
    escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'
