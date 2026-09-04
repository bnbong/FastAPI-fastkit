# --------------------------------------------------------------------------
# Canonical shape of an interactive / ``--config`` project configuration.
#
# Three modules read the same configuration dict and each used to interpret
# it their own way: ``DependencyCollector`` looked axis values up in the
# package catalog, ``DynamicConfigGenerator`` compared them against the
# ``"None"`` sentinel, and ``ProjectScaffolder`` recorded them as
# ``"<axis>:<choice>"`` metadata. A hand-written config file that spelled an
# axis differently than the interactive builder does (say ``async_tasks`` as
# ``{"type": "Celery"}`` instead of ``"Celery"``) made the three disagree:
# the collector saw a value that was not in the catalog and installed
# nothing, while the generator saw a non-``None`` value and emitted an import
# for a feature module it never wrote — a project that fails at import time.
#
# This module is the single normalisation point. Every entry into the
# generation pipeline (``fastkit init --config`` right after load, and
# ``ProjectScaffolder`` on construction) runs the config through
# :func:`normalize_project_config`, so the three consumers can only ever see
# one shape:
#
#   ================  ==========================================
#   Key               Canonical value
#   ================  ==========================================
#   database          ``{"type": <choice>, "packages": [<pkg>]}``
#   single-select     ``"<choice>"`` (``"None"`` when unset)
#   multi-select      ``["<choice>", ...]`` (``[]`` when unset)
#   deployment        ``["Docker", "docker-compose"]`` subset
#   ================  ==========================================
#
# Anything the catalog does not know about is rejected with the offending
# key and the list of allowed values, instead of being silently dropped.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from typing import Any, Dict, List, Optional, Tuple

from fastapi_fastkit.core.settings import (
    MULTI_SELECT_AXES,
    NONE_CHOICE,
    FastkitConfig,
    FeatureAxis,
)

#: Deployment targets ``prompt_deployment_options`` can produce.
DEPLOYMENT_CHOICES: Tuple[str, ...] = ("Docker", "docker-compose", NONE_CHOICE)

#: Non-axis keys the interactive builder writes. Anything outside this set
#: (and outside :class:`FeatureAxis`) is a typo rather than a feature block.
KNOWN_METADATA_KEYS: Tuple[str, ...] = (
    "project_name",
    "author",
    "author_email",
    "description",
    "version",
    "base_template",
    "architecture_preset",
    "architecture_preset_description",
    "preset",
    "package_manager",
    "deployment",
    "custom_packages",
    "all_dependencies",
)

#: Alias accepted for ``architecture_preset`` — it is the key the generated
#: project's own ``[tool.fastapi-fastkit]`` metadata uses, so a config
#: written from a previous project's metadata still loads.
_PRESET_ALIAS = "preset"


class ConfigSchemaError(Exception):
    """Raised when a configuration cannot be normalised into canonical form."""


def normalize_project_config(
    config: Dict[str, Any], settings: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Return ``config`` in the canonical shape, or raise on anything unknown.

    The operation is idempotent: normalising an already-canonical config
    (including one written by ``--save-config``) returns an equal mapping.

    :param config: Configuration mapping (interactive builder shape, or any
        of the accepted spellings described in this module's header)
    :param settings: ``FastkitConfig`` instance; a default one is used when
        omitted (the catalog it carries is class-level data)
    :return: A new mapping with every known key in canonical form
    :raises ConfigSchemaError: If a key, a choice or a value type is unknown
    """
    normalized, errors = _normalize(config, settings)
    if errors:
        raise ConfigSchemaError("; ".join(errors))
    return normalized


def validate_project_config_schema(
    config: Dict[str, Any], settings: Optional[Any] = None
) -> List[str]:
    """
    Collect the schema problems of ``config`` without raising.

    :param config: Configuration mapping
    :param settings: ``FastkitConfig`` instance (optional)
    :return: Human-readable error messages, empty when the config is valid
    """
    _, errors = _normalize(config, settings)
    return errors


def _normalize(
    config: Dict[str, Any], settings: Optional[Any]
) -> Tuple[Dict[str, Any], List[str]]:
    """Normalise ``config`` and report every problem found along the way."""
    if not isinstance(config, dict):
        return {}, ["Project configuration must be a mapping."]

    active_settings = settings if settings is not None else FastkitConfig()
    catalog: Dict[str, Dict[str, List[str]]] = active_settings.PACKAGE_CATALOG

    errors: List[str] = []
    normalized: Dict[str, Any] = {}

    axis_keys = {str(axis) for axis in FeatureAxis}
    known_keys = set(KNOWN_METADATA_KEYS) | axis_keys
    for key in config:
        if key not in known_keys:
            errors.append(
                f"Unknown config key '{key}'. Allowed keys: "
                f"{', '.join(sorted(known_keys))}"
            )

    # Pass through everything that is not an axis; the axis keys below
    # overwrite their raw counterparts with the canonical form.
    for key, value in config.items():
        if key in known_keys and key not in axis_keys:
            normalized[key] = value

    for axis in FeatureAxis:
        key = str(axis)
        choices = catalog.get(axis, {})
        raw = config.get(key)
        axis_errors: List[str]
        if axis in MULTI_SELECT_AXES:
            normalized[key], axis_errors = _normalize_multi(key, raw, choices)
        elif axis == FeatureAxis.DATABASE:
            normalized[key], axis_errors = _normalize_database(raw, choices)
        else:
            normalized[key], axis_errors = _normalize_single(key, raw, choices)
        errors.extend(axis_errors)

    errors.extend(_normalize_preset(config, normalized, active_settings))
    errors.extend(_normalize_package_manager(config, normalized, active_settings))
    errors.extend(_normalize_deployment(config, normalized))
    errors.extend(_normalize_string_list(config, normalized, "custom_packages"))
    errors.extend(_normalize_string_list(config, normalized, "all_dependencies"))

    return normalized, errors


def _scalar_choice(axis: str, raw: Any) -> Tuple[Optional[str], List[str]]:
    """
    Reduce one axis' raw value to a single choice name.

    Accepts a bare string and the ``{"type": ...}`` mapping spelling that a
    hand-written config file may use for any axis (the interactive builder
    only produces it for ``database``).
    """
    if isinstance(raw, dict):
        unknown = sorted(set(raw) - {"type", "packages"})
        if unknown:
            return None, [
                f"Config key '{axis}' mapping may only hold 'type' and 'packages'; "
                f"got unexpected {', '.join(unknown)}"
            ]
        raw = raw.get("type", NONE_CHOICE)

    if raw is None:
        return NONE_CHOICE, []
    if isinstance(raw, str):
        return raw, []
    return None, [
        f"Config key '{axis}' must be a string or a {{'type': ...}} mapping, "
        f"got {type(raw).__name__}"
    ]


def _unknown_choice_error(axis: str, choice: str, choices: Dict[str, Any]) -> str:
    """Build the "that option does not exist" message for one axis."""
    return (
        f"Unknown '{axis}' option '{choice}'. Allowed values: "
        f"{', '.join(sorted(choices))}"
    )


def _normalize_single(
    axis: str, raw: Any, choices: Dict[str, Any]
) -> Tuple[str, List[str]]:
    """Canonicalise a single-select axis into a bare choice string."""
    if isinstance(raw, (list, tuple)):
        return NONE_CHOICE, [
            f"Config key '{axis}' takes a single choice, not a list. "
            f"Allowed values: {', '.join(sorted(choices))}"
        ]

    choice, errors = _scalar_choice(axis, raw)
    if choice is None:
        return NONE_CHOICE, errors
    if choice not in choices:
        return NONE_CHOICE, [_unknown_choice_error(axis, choice, choices)]
    return choice, []


def _normalize_multi(
    axis: str, raw: Any, choices: Dict[str, Any]
) -> Tuple[List[str], List[str]]:
    """Canonicalise a multi-select axis into a deduplicated choice list."""
    if raw is None:
        return [], []
    if isinstance(raw, str):
        raw = [raw]
    if isinstance(raw, dict):
        choice, scalar_errors = _scalar_choice(axis, raw)
        if choice is None:
            return [], scalar_errors
        raw = [choice]
    if not isinstance(raw, (list, tuple)):
        return [], [
            f"Config key '{axis}' must be a list of choices, "
            f"got {type(raw).__name__}"
        ]

    errors: List[str] = []
    selected: List[str] = []
    for item in raw:
        if not isinstance(item, str):
            errors.append(
                f"Config key '{axis}' may only contain strings, "
                f"got {type(item).__name__}"
            )
            continue
        if item == NONE_CHOICE:
            continue
        if item not in choices:
            errors.append(_unknown_choice_error(axis, item, choices))
            continue
        if item not in selected:
            selected.append(item)

    return selected, errors


def _normalize_database(
    raw: Any, choices: Dict[str, Any]
) -> Tuple[Dict[str, Any], List[str]]:
    """Canonicalise the ``database`` axis into ``{"type", "packages"}``."""
    axis = str(FeatureAxis.DATABASE)
    if isinstance(raw, (list, tuple)):
        return {"type": NONE_CHOICE, "packages": []}, [
            f"Config key '{axis}' takes a single choice, not a list. "
            f"Allowed values: {', '.join(sorted(choices))}"
        ]

    choice, errors = _scalar_choice(axis, raw)
    if choice is None:
        return {"type": NONE_CHOICE, "packages": []}, errors
    if choice not in choices:
        return {"type": NONE_CHOICE, "packages": []}, [
            _unknown_choice_error(axis, choice, choices)
        ]

    # ``packages`` is a cache of the catalog entry; it is always rebuilt so a
    # stale or hand-edited list can never contradict the selected type.
    return {"type": choice, "packages": list(choices[choice])}, []


def _normalize_preset(
    config: Dict[str, Any], normalized: Dict[str, Any], settings: Any
) -> List[str]:
    """Fold the ``preset`` alias into ``architecture_preset`` and validate it."""
    presets: Dict[str, str] = settings.ARCHITECTURE_PRESETS
    canonical = config.get("architecture_preset")
    alias = config.get(_PRESET_ALIAS)

    if canonical is not None and alias is not None and canonical != alias:
        return [
            f"Conflicting presets: 'architecture_preset' is '{canonical}' but "
            f"'preset' is '{alias}'. Use one of them."
        ]

    preset = canonical if canonical is not None else alias
    normalized.pop(_PRESET_ALIAS, None)
    if preset is None:
        normalized.pop("architecture_preset", None)
        return []

    if not isinstance(preset, str) or preset not in presets:
        normalized.pop("architecture_preset", None)
        return [
            f"Unknown architecture preset '{preset}'. Allowed values: "
            f"{', '.join(sorted(presets))}"
        ]

    normalized["architecture_preset"] = preset
    return []


def _normalize_package_manager(
    config: Dict[str, Any], normalized: Dict[str, Any], settings: Any
) -> List[str]:
    """Validate ``package_manager`` against the supported managers."""
    manager = config.get("package_manager")
    if manager is None:
        normalized.pop("package_manager", None)
        return []

    supported: List[str] = settings.SUPPORTED_PACKAGE_MANAGERS
    if not isinstance(manager, str) or manager not in supported:
        normalized.pop("package_manager", None)
        return [
            f"Unknown package manager '{manager}'. Allowed values: "
            f"{', '.join(sorted(supported))}"
        ]

    normalized["package_manager"] = manager
    return []


def _normalize_deployment(
    config: Dict[str, Any], normalized: Dict[str, Any]
) -> List[str]:
    """Canonicalise ``deployment`` into an ordered Docker target list."""
    raw = config.get("deployment")
    if raw is None:
        normalized["deployment"] = []
        return []
    if isinstance(raw, str):
        raw = [raw]
    if not isinstance(raw, (list, tuple)):
        normalized["deployment"] = []
        return [
            f"Config key 'deployment' must be a list of targets, "
            f"got {type(raw).__name__}"
        ]

    errors: List[str] = []
    selected: List[str] = []
    for item in raw:
        if not isinstance(item, str) or item not in DEPLOYMENT_CHOICES:
            errors.append(
                f"Unknown 'deployment' target '{item}'. Allowed values: "
                f"{', '.join(sorted(DEPLOYMENT_CHOICES))}"
            )
            continue
        if item == NONE_CHOICE:
            continue
        if item not in selected:
            selected.append(item)

    # ``docker-compose.yml`` builds the image the Dockerfile describes, so
    # picking compose implies Docker — the interactive prompt does the same.
    if "docker-compose" in selected and "Docker" not in selected:
        selected.insert(0, "Docker")

    normalized["deployment"] = selected
    return errors


def _normalize_string_list(
    config: Dict[str, Any], normalized: Dict[str, Any], key: str
) -> List[str]:
    """Validate one of the free-form string list keys, dropping it when absent."""
    raw = config.get(key)
    if raw is None:
        normalized.pop(key, None)
        return []
    if not isinstance(raw, (list, tuple)) or not all(
        isinstance(item, str) for item in raw
    ):
        normalized.pop(key, None)
        return [f"Config key '{key}' must be a list of strings"]

    normalized[key] = list(raw)
    return []
