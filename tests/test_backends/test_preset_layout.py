# --------------------------------------------------------------------------
# Tests for project_builder.preset_layout.
#
# Covers each preset's static layout decisions plus the compatibility
# warnings surfaced when a preset preserves the template-shipped main.py.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from pathlib import Path

import pytest

from fastapi_fastkit.backend.project_builder.preset_layout import (
    PresetLayoutStrategist,
)


class TestSupportedPresets:
    """Sanity checks for the canonical preset list."""

    def test_all_four_presets_listed_in_order(self) -> None:
        assert PresetLayoutStrategist.supported_presets() == [
            "minimal",
            "single-module",
            "classic-layered",
            "domain-starter",
        ]


class TestBaseTemplateMapping:
    """Each preset must point at a real shipped template."""

    @pytest.mark.parametrize(
        "preset_id, expected_base",
        [
            ("minimal", "fastapi-empty"),
            ("single-module", "fastapi-single-module"),
            ("classic-layered", "fastapi-default"),
            ("domain-starter", "fastapi-domain-starter"),
        ],
    )
    def test_base_template_for_each_preset(
        self, preset_id: str, expected_base: str
    ) -> None:
        strategist = PresetLayoutStrategist(preset_id)
        assert strategist.base_template == expected_base

    def test_unknown_preset_falls_back_to_minimal(self) -> None:
        strategist = PresetLayoutStrategist("not-a-real-preset")
        assert strategist.preset_id == "minimal"
        assert strategist.base_template == "fastapi-empty"

    def test_none_preset_falls_back_to_minimal(self) -> None:
        strategist = PresetLayoutStrategist(None)
        assert strategist.preset_id == "minimal"

    def test_empty_string_preset_falls_back_to_minimal(self) -> None:
        strategist = PresetLayoutStrategist("")
        assert strategist.preset_id == "minimal"


class TestRegenerationPolicy:
    """Only minimal / single-module presets regenerate main.py."""

    @pytest.mark.parametrize(
        "preset_id, expected",
        [
            ("minimal", True),
            ("single-module", True),
            ("classic-layered", False),
            ("domain-starter", False),
        ],
    )
    def test_should_regenerate_main(self, preset_id: str, expected: bool) -> None:
        strategist = PresetLayoutStrategist(preset_id)
        assert strategist.should_regenerate_main is expected


class TestFileTargets:
    """Generated files land at preset-appropriate paths."""

    @pytest.mark.parametrize(
        "preset_id, expected_main, expected_db, expected_auth",
        [
            (
                "minimal",
                "src/main.py",
                "src/config/database.py",
                "src/config/auth.py",
            ),
            (
                "single-module",
                "src/main.py",
                "src/config/database.py",
                "src/config/auth.py",
            ),
            (
                "classic-layered",
                "src/main.py",
                "src/core/database.py",
                "src/core/auth.py",
            ),
            (
                "domain-starter",
                "src/app/main.py",
                "src/app/core/database.py",
                "src/app/core/auth.py",
            ),
        ],
    )
    def test_targets_match_documented_matrix(
        self,
        preset_id: str,
        expected_main: str,
        expected_db: str,
        expected_auth: str,
    ) -> None:
        strategist = PresetLayoutStrategist(preset_id)
        project = "/proj"

        assert strategist.main_py_target(project) == Path(project) / expected_main
        assert strategist.db_config_target(project) == Path(project) / expected_db
        assert strategist.auth_config_target(project) == Path(project) / expected_auth


class TestAppModule:
    """The ``app_module`` property must match each preset's main.py path."""

    @pytest.mark.parametrize(
        "preset_id, expected_app_module",
        [
            ("minimal", "src.main:app"),
            ("single-module", "src.main:app"),
            ("classic-layered", "src.main:app"),
            ("domain-starter", "src.app.main:app"),
        ],
    )
    def test_app_module_matches_main_py_path(
        self, preset_id: str, expected_app_module: str
    ) -> None:
        strategist = PresetLayoutStrategist(preset_id)
        assert strategist.app_module == expected_app_module


class TestCompatibilityWarnings:
    """Warnings only fire on presets that don't regenerate main.py."""

    def test_minimal_never_warns(self) -> None:
        strategist = PresetLayoutStrategist("minimal")
        config = {"utilities": ["CORS", "Rate-Limiting"], "monitoring": "Prometheus"}
        assert strategist.compatibility_warnings(config) == []

    def test_single_module_never_warns(self) -> None:
        strategist = PresetLayoutStrategist("single-module")
        config = {"utilities": ["CORS"], "monitoring": "Prometheus"}
        assert strategist.compatibility_warnings(config) == []

    def test_classic_layered_warns_on_rate_limiting(self) -> None:
        strategist = PresetLayoutStrategist("classic-layered")
        config = {"utilities": ["Rate-Limiting"], "monitoring": "None"}
        warnings = strategist.compatibility_warnings(config)
        # Two lines: the manual-wiring note and the affected-features list.
        assert len(warnings) == 2
        assert any("Rate-Limiting" in line for line in warnings)
        assert any("classic-layered" in line for line in warnings)

    def test_domain_starter_warns_on_prometheus(self) -> None:
        strategist = PresetLayoutStrategist("domain-starter")
        config = {"utilities": [], "monitoring": "Prometheus"}
        warnings = strategist.compatibility_warnings(config)
        assert any("Prometheus" in line for line in warnings)
        assert any("domain-starter" in line for line in warnings)

    def test_preserve_main_silent_for_cors_only(self) -> None:
        """CORS alone must NOT fire a warning on preserve-main presets.

        Both fastapi-default and fastapi-domain-starter already wire
        CORSMiddleware in their shipped main.py, conditional on
        ``settings.all_cors_origins`` — picking CORS in the wizard only
        means the user needs to populate BACKEND_CORS_ORIGINS in .env.
        """
        for preset_id in ("classic-layered", "domain-starter"):
            strategist = PresetLayoutStrategist(preset_id)
            config = {"utilities": ["CORS"], "monitoring": "None"}
            assert (
                strategist.compatibility_warnings(config) == []
            ), f"{preset_id} should not warn for CORS-only selection"

    def test_classic_layered_silent_when_no_overlay_features(self) -> None:
        strategist = PresetLayoutStrategist("classic-layered")
        # Database / auth only — these don't trigger main.py overlay
        # warnings (config files still get generated at the preset path).
        config = {
            "database": {"type": "PostgreSQL"},
            "authentication": "JWT",
            "utilities": [],
            "monitoring": "None",
        }
        assert strategist.compatibility_warnings(config) == []

    def test_domain_starter_collects_multiple_warnings(self) -> None:
        strategist = PresetLayoutStrategist("domain-starter")
        config = {
            # CORS is intentionally included here too: it must NOT show up
            # in the *affected-selections* line, since the shipped main.py
            # already wires it. (The leading manual-wiring note may still
            # mention CORS informationally — "CORS is already wired —
            # set BACKEND_CORS_ORIGINS in .env" — so we scope the strict
            # check to the affected-features line.)
            "utilities": ["CORS", "Rate-Limiting"],
            "monitoring": "Prometheus",
        }
        warnings = strategist.compatibility_warnings(config)
        affected_line = next(
            (line for line in warnings if line.startswith("Affected selections")),
            "",
        )
        assert affected_line, f"expected an 'Affected selections' line, got: {warnings}"
        assert "CORS" not in affected_line, (
            "CORS is pre-wired in the shipped main.py; affected-selections "
            "list must omit it"
        )
        assert "Rate-Limiting" in affected_line
        assert "Prometheus" in affected_line
