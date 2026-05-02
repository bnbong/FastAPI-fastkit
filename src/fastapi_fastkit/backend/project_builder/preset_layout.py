# --------------------------------------------------------------------------
# Architecture-preset layout strategy for interactive project generation.
#
# Maps each architecture preset (issue #44) to the actual generation
# decisions interactive ``init`` makes:
#
#   - which template ships as the base scaffold,
#   - whether the dynamic ``main.py`` overlay should overwrite the shipped one,
#   - where database / auth config files should land so they sit next to the
#     template's existing structure rather than in a parallel ``src/config``,
#   - and which feature combinations need a "you must wire this up manually"
#     warning because the dynamic ``main.py`` overlay isn't applied.
#
# Keeping every preset's layout knowledge in one place lets the CLI flow stay
# linear ("ask the strategist where to write the file") instead of growing a
# branching maze of preset-specific if/else blocks.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Canonical preset id used when a caller doesn't supply one. Picked to
# preserve pre-#45 behaviour: interactive ``init`` historically deployed
# ``fastapi-empty`` and regenerated ``src/main.py`` from feature flags.
_FALLBACK_PRESET_ID: str = "minimal"


@dataclass(frozen=True)
class PresetProfile:
    """Per-preset generation decisions. Treat as a value object."""

    preset_id: str
    base_template: str
    regenerate_main: bool
    main_py_relpath: str
    db_config_relpath: str
    auth_config_relpath: str
    # Hint shown when ``regenerate_main`` is False and the user picked a
    # feature whose dynamic main.py overlay won't run. Empty string means
    # "no special note for this preset".
    manual_wiring_note: str = ""
    extra_warning_targets: Tuple[str, ...] = field(default_factory=tuple)


_PRESET_PROFILES: Dict[str, PresetProfile] = {
    "minimal": PresetProfile(
        preset_id="minimal",
        base_template="fastapi-empty",
        regenerate_main=True,
        main_py_relpath="src/main.py",
        db_config_relpath="src/config/database.py",
        auth_config_relpath="src/config/auth.py",
    ),
    "single-module": PresetProfile(
        preset_id="single-module",
        base_template="fastapi-single-module",
        regenerate_main=True,
        main_py_relpath="src/main.py",
        db_config_relpath="src/config/database.py",
        auth_config_relpath="src/config/auth.py",
    ),
    "classic-layered": PresetProfile(
        preset_id="classic-layered",
        base_template="fastapi-default",
        regenerate_main=False,
        main_py_relpath="src/main.py",
        db_config_relpath="src/core/database.py",
        auth_config_relpath="src/core/auth.py",
        # CORS is intentionally NOT in this list: fastapi-default's shipped
        # main.py already imports CORSMiddleware and adds it conditionally
        # on settings.all_cors_origins, so the user only has to populate
        # BACKEND_CORS_ORIGINS in .env — no code edits needed.
        manual_wiring_note=(
            "fastapi-default's shipped src/main.py is preserved. The "
            "selections below need manual wiring there (CORS is already "
            "wired — set BACKEND_CORS_ORIGINS in .env to activate it)."
        ),
        extra_warning_targets=("Rate-Limiting", "Prometheus"),
    ),
    "domain-starter": PresetProfile(
        preset_id="domain-starter",
        base_template="fastapi-domain-starter",
        regenerate_main=False,
        main_py_relpath="src/app/main.py",
        db_config_relpath="src/app/core/database.py",
        auth_config_relpath="src/app/core/auth.py",
        manual_wiring_note=(
            "fastapi-domain-starter's shipped src/app/main.py is preserved. "
            "The selections below need manual wiring there (CORS is already "
            "wired — set BACKEND_CORS_ORIGINS in .env to activate it)."
        ),
        extra_warning_targets=("Rate-Limiting", "Prometheus"),
    ),
}


class PresetLayoutStrategist:
    """Single source of truth for preset → generation-layout decisions."""

    def __init__(self, preset_id: str | None) -> None:
        # Empty / None / unknown ids fall back to ``minimal`` so older callers
        # that pre-date the architecture-preset prompt keep working.
        canonical = (preset_id or _FALLBACK_PRESET_ID).strip()
        self.profile: PresetProfile = _PRESET_PROFILES.get(
            canonical, _PRESET_PROFILES[_FALLBACK_PRESET_ID]
        )

    @classmethod
    def supported_presets(cls) -> List[str]:
        """Return the ordered list of preset ids the strategist understands."""
        return list(_PRESET_PROFILES.keys())

    @property
    def preset_id(self) -> str:
        return self.profile.preset_id

    @property
    def base_template(self) -> str:
        return self.profile.base_template

    @property
    def should_regenerate_main(self) -> bool:
        return self.profile.regenerate_main

    def main_py_target(self, project_dir: str) -> Path:
        """Absolute path where the dynamic main.py overlay should land."""
        return Path(project_dir) / self.profile.main_py_relpath

    @property
    def app_module(self) -> str:
        """Return the ``module:attr`` string uvicorn / Docker should target.

        Derived from ``main_py_relpath`` so docker generation, runserver,
        and any future container-orchestration code all agree on the
        entrypoint a given preset produces.
        """
        # Strip the trailing ``.py`` and convert path separators to dots.
        relpath = self.profile.main_py_relpath
        if relpath.endswith(".py"):
            relpath = relpath[: -len(".py")]
        module_part = relpath.replace("/", ".").replace("\\", ".")
        return f"{module_part}:app"

    def db_config_target(self, project_dir: str) -> Path:
        """Absolute path for the generated database config module."""
        return Path(project_dir) / self.profile.db_config_relpath

    def auth_config_target(self, project_dir: str) -> Path:
        """Absolute path for the generated authentication config module."""
        return Path(project_dir) / self.profile.auth_config_relpath

    def compatibility_warnings(self, config: Dict[str, Any]) -> List[str]:
        """Return user-facing warnings for unsupported preset/feature mixes.

        The dynamic ``main.py`` overlay (CORS middleware wiring, Prometheus
        instrumentation, rate-limit hookup) only runs for presets that
        regenerate ``main.py``. For the other presets we keep the
        template-shipped ``main.py`` intact and surface a single warning
        listing the affected features so users know to wire them up
        themselves rather than assuming the package install was enough.
        """
        if self.profile.regenerate_main:
            return []

        affected = self._affected_overlay_targets(config)
        if not affected:
            return []

        warnings: List[str] = []
        if self.profile.manual_wiring_note:
            warnings.append(self.profile.manual_wiring_note)
        warnings.append(
            "Affected selections (packages installed, but no dynamic main.py "
            "edits applied for the '"
            + self.profile.preset_id
            + "' preset): "
            + ", ".join(affected)
        )
        return warnings

    def _affected_overlay_targets(self, config: Dict[str, Any]) -> List[str]:
        """Detect which of the user's selections rely on main.py overlay."""
        triggered: List[str] = []
        utilities = set(config.get("utilities") or [])

        for target in self.profile.extra_warning_targets:
            if target in {"CORS", "Rate-Limiting"}:
                if target in utilities:
                    triggered.append(target)
            elif target == "Prometheus":
                if config.get("monitoring") == "Prometheus":
                    triggered.append(target)
        return triggered


__all__ = [
    "PresetLayoutStrategist",
    "PresetProfile",
]
