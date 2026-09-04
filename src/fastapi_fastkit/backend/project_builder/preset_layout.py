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

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Sequence, Tuple

from fastapi_fastkit.core.settings import (
    NONE_CHOICE,
    AsyncTaskChoice,
    AuthChoice,
    CachingChoice,
    FeatureAxis,
    LoggingChoice,
    MonitoringChoice,
    UtilityChoice,
)

# Canonical preset id used when a caller doesn't supply one. Picked to
# preserve pre-#45 behaviour: interactive ``init`` historically deployed
# ``fastapi-empty`` and regenerated ``src/main.py`` from feature flags.
_FALLBACK_PRESET_ID: str = "minimal"


def _utility_selected(config: Dict[str, Any], utility: str) -> bool:
    """Whether a multi-select ``utilities`` entry was picked."""
    return utility in set(config.get(FeatureAxis.UTILITIES) or [])


def _axis_is(config: Dict[str, Any], axis: str, choice: str) -> bool:
    """Whether a single-select axis holds exactly ``choice``."""
    return config.get(axis) == choice


@dataclass(frozen=True)
class OverlayTarget:
    """One feature whose wiring normally lives in the dynamic main.py overlay.

    ``label`` is what the user sees in the warning, ``applies`` decides
    whether their configuration actually triggered it, and ``wiring`` (when
    present) is the import / statement pair that can be spliced into a
    template-shipped ``main.py`` through its ``# fastkit:`` anchors instead
    of only being warned about.
    """

    label: str
    applies: Callable[[Dict[str, Any]], bool]
    #: ``(import lines, statement lines)`` rendered with ``{pkg}``.
    wiring: Tuple[Tuple[str, ...], Tuple[str, ...]] = ((), ())

    @property
    def is_wirable(self) -> bool:
        return bool(self.wiring[0] or self.wiring[1])


#: Every feature the dynamic ``main.py`` overlay is responsible for. Presets
#: that preserve their template's ``main.py`` name the subset they care about
#: in ``PresetProfile.extra_warning_targets``.
OVERLAY_TARGETS: Tuple[OverlayTarget, ...] = (
    OverlayTarget(
        label="CORS",
        applies=lambda c: _utility_selected(c, UtilityChoice.CORS),
    ),
    OverlayTarget(
        label="Rate-Limiting",
        applies=lambda c: _utility_selected(c, UtilityChoice.RATE_LIMITING),
    ),
    OverlayTarget(
        label="WebSocket",
        applies=lambda c: _utility_selected(c, UtilityChoice.WEBSOCKET),
        wiring=(
            ("from {pkg}.features.websocket import router as websocket_router",),
            ("app.include_router(websocket_router)",),
        ),
    ),
    OverlayTarget(
        label="Pagination",
        applies=lambda c: _utility_selected(c, UtilityChoice.PAGINATION),
        wiring=(
            (
                "from fastapi_pagination import add_pagination",
                "from {pkg}.features.pagination import router as pagination_router",
            ),
            ("app.include_router(pagination_router)", "add_pagination(app)"),
        ),
    ),
    OverlayTarget(
        label="Background tasks",
        applies=lambda c: c.get(FeatureAxis.ASYNC_TASKS, NONE_CHOICE)
        in (AsyncTaskChoice.CELERY, AsyncTaskChoice.DRAMATIQ),
        wiring=(
            ("from {pkg}.features.tasks import router as tasks_router",),
            ("app.include_router(tasks_router)",),
        ),
    ),
    # Caching is deliberately warn-only: mounting ``cache_router`` without the
    # ``FastAPICache.init`` lifespan hook would ship endpoints that raise at
    # request time, which is worse than an unmounted module plus a warning.
    OverlayTarget(
        label="Caching (Redis)",
        applies=lambda c: _axis_is(c, FeatureAxis.CACHING, CachingChoice.REDIS),
    ),
    OverlayTarget(
        label="Prometheus",
        applies=lambda c: _axis_is(
            c, FeatureAxis.MONITORING, MonitoringChoice.PROMETHEUS
        ),
    ),
    OverlayTarget(
        label="OpenTelemetry",
        applies=lambda c: _axis_is(
            c, FeatureAxis.MONITORING, MonitoringChoice.OPENTELEMETRY
        ),
    ),
    OverlayTarget(
        label="OAuth2 session middleware",
        applies=lambda c: _axis_is(c, FeatureAxis.AUTHENTICATION, AuthChoice.OAUTH2),
    ),
    OverlayTarget(
        label="Session-based auth middleware",
        applies=lambda c: _axis_is(c, FeatureAxis.AUTHENTICATION, AuthChoice.SESSION),
    ),
    OverlayTarget(
        label="Structured logging",
        applies=lambda c: _axis_is(c, FeatureAxis.LOGGING, LoggingChoice.STRUCTURED),
    ),
)

_TARGETS_BY_LABEL: Dict[str, OverlayTarget] = {
    target.label: target for target in OVERLAY_TARGETS
}

#: Every overlay target except CORS, which template-shipped ``main.py`` files
#: already wire from ``settings.all_cors_origins``.
_NON_CORS_TARGETS: Tuple[str, ...] = tuple(
    target.label for target in OVERLAY_TARGETS if target.label != "CORS"
)


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
        extra_warning_targets=_NON_CORS_TARGETS,
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
        extra_warning_targets=_NON_CORS_TARGETS,
    ),
}


def _package_root(main_py_relpath: str) -> str:
    """Dotted package the generated feature modules live in.

    ``src/main.py`` -> ``src``; ``src/app/main.py`` -> ``src.app``. Mirrors
    ``DynamicConfigGenerator.pkg`` so the import lines spliced into a
    preserved ``main.py`` match where the generator actually wrote them.
    """
    normalized = main_py_relpath.replace("\\", "/").strip("/")
    parent = normalized.rsplit("/", 1)[0] if "/" in normalized else "src"
    return parent.replace("/", ".")


def app_module_from_relpath(relpath: str) -> str:
    """Convert a project-relative ``main.py`` path into ``module:attr``.

    Single source of truth shared by the preset profiles (which know the
    layout up-front) and by ``runserver`` (which discovers ``main.py`` on
    disk). Both used to derive the dotted path independently, and the two
    implementations drifted for the ``src/app/main.py`` layout.
    """
    normalized = relpath.replace("\\", "/").strip("/")
    if normalized.endswith(".py"):
        normalized = normalized[: -len(".py")]
    module_part = normalized.replace("/", ".")
    return f"{module_part}:app"


def app_module_from_main_path(project_dir: str, main_path: str) -> str:
    """Convert an absolute ``main.py`` location into ``module:attr``."""
    return app_module_from_relpath(os.path.relpath(main_path, project_dir))


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

        Derived from ``main_py_relpath`` through :func:`app_module_from_relpath`
        so docker generation, ``runserver`` and any future
        container-orchestration code all agree on the entrypoint a given
        preset produces.
        """
        return app_module_from_relpath(self.profile.main_py_relpath)

    def db_config_target(self, project_dir: str) -> Path:
        """Absolute path for the generated database config module."""
        return Path(project_dir) / self.profile.db_config_relpath

    def auth_config_target(self, project_dir: str) -> Path:
        """Absolute path for the generated authentication config module."""
        return Path(project_dir) / self.profile.auth_config_relpath

    def compatibility_warnings(
        self, config: Dict[str, Any], wired: Sequence[str] = ()
    ) -> List[str]:
        """Return user-facing warnings for unsupported preset/feature mixes.

        The dynamic ``main.py`` overlay (middleware wiring, Prometheus
        instrumentation, feature router mounting) only runs for presets that
        regenerate ``main.py``. For the other presets we keep the
        template-shipped ``main.py`` intact and surface a single warning
        listing the affected features so users know to wire them up
        themselves rather than assuming the package install was enough.

        Args:
            config: Interactive project configuration
            wired: Labels already spliced into ``main.py`` by
                :meth:`wire_generated_routers`, which therefore need no warning

        Returns:
            Warning strings, empty when nothing needs manual attention
        """
        if self.profile.regenerate_main:
            return []

        already_wired = set(wired)
        affected = [
            label
            for label in self._affected_overlay_targets(config)
            if label not in already_wired
        ]
        if not affected:
            return []

        warnings: List[str] = []
        if self.profile.manual_wiring_note:
            warnings.append(self.profile.manual_wiring_note)
        warnings.append(
            "Affected selections (modules and packages generated, but you must "
            "register them yourself in "
            + self.profile.main_py_relpath
            + " for the '"
            + self.profile.preset_id
            + "' preset): "
            + ", ".join(affected)
        )
        return warnings

    def _affected_overlay_targets(self, config: Dict[str, Any]) -> List[str]:
        """Detect which of the user's selections rely on main.py overlay."""
        return [
            label
            for label in self.profile.extra_warning_targets
            if label in _TARGETS_BY_LABEL and _TARGETS_BY_LABEL[label].applies(config)
        ]

    def wire_generated_routers(
        self, project_dir: str, config: Dict[str, Any]
    ) -> List[str]:
        """Splice generated feature routers into a preserved ``main.py``.

        Presets that keep their template's ``main.py`` used to leave every
        generated router (background tasks, WebSocket, pagination) sitting on
        disk unmounted. Templates ship ``# fastkit:imports`` /
        ``# fastkit:routes`` anchors precisely so generated code can be added
        without rewriting the file, so we use them here and fall back to a
        warning for anything not safely wirable.

        Args:
            project_dir: Absolute path of the generated project
            config: Interactive project configuration

        Returns:
            Labels of the features actually wired (empty when the preset
            regenerates ``main.py``, or when ``main.py`` is missing)
        """
        if self.profile.regenerate_main:
            return []

        # Imported lazily: ``backend.main`` imports this module at load time.
        from fastapi_fastkit.backend.main import (
            insert_import_line,
            insert_statement_line,
        )

        main_path = self.main_py_target(project_dir)
        if not main_path.is_file():
            return []

        pkg = _package_root(self.profile.main_py_relpath)
        content = original = main_path.read_text(encoding="utf-8")
        wired: List[str] = []

        for label in self.profile.extra_warning_targets:
            target = _TARGETS_BY_LABEL.get(label)
            if target is None or not target.is_wirable:
                continue
            if not target.applies(config):
                continue

            imports, statements = target.wiring
            for line in imports:
                content = insert_import_line(content, line.format(pkg=pkg))
            for line in statements:
                content = insert_statement_line(content, line.format(pkg=pkg))
            wired.append(label)

        if content != original:
            main_path.write_text(content, encoding="utf-8")

        return wired


__all__ = [
    "OVERLAY_TARGETS",
    "OverlayTarget",
    "PresetLayoutStrategist",
    "PresetProfile",
    "app_module_from_main_path",
    "app_module_from_relpath",
]
