# --------------------------------------------------------------------------
# Build comprehensive project configuration from user selections
#
# Aggregates all user choices into a structured configuration dict
# that can be consumed by the project builder.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from typing import Any, Dict, List

from fastapi_fastkit.utils.main import console, print_warning

from ..project_builder.config_schema import normalize_project_config
from ..project_builder.dependency_collector import DependencyCollector
from .prompts import (
    prompt_additional_features,
    prompt_architecture_preset,
    prompt_basic_info,
    prompt_template_selection,
)
from .selectors import confirm_selections
from .validators import sanitize_custom_packages, validate_feature_compatibility


class InteractiveConfigBuilder:
    """
    Builds project configuration from interactive prompts.

    Orchestrates the entire interactive flow and aggregates all
    user selections into a cohesive configuration dictionary.
    """

    def __init__(self, settings: Any) -> None:
        """
        Initialize the config builder.

        Args:
            settings: FastkitConfig instance
        """
        self.settings = settings
        self.config: Dict[str, Any] = {}

    def run_interactive_flow(self) -> Dict[str, Any]:
        """
        Execute full interactive flow and return config.

        Returns:
            Complete project configuration dictionary
        """
        console.print(
            "\n[bold magenta]⚡ FastAPI-fastkit Interactive Project Setup ⚡[/bold magenta]\n"
        )

        # Step 1: Basic information
        self._collect_basic_info()

        # Step 2: Architecture preset — chosen early so downstream prompts
        # (and later, preset-specific scaffolding) can branch on the layout.
        self._collect_architecture_preset()

        # Step 3: Always use Empty template as base for interactive mode
        # (Feature selection will build the project incrementally)
        self.config["base_template"] = None  # None = Empty project

        # Step 4: Feature selections
        self._collect_feature_selections()

        # Step 4: Build final configuration
        final_config = self._build_final_config()

        # Step 5: Validate compatibility
        is_valid, warning = validate_feature_compatibility(final_config)
        if warning:
            print_warning(warning, title="Feature Compatibility")

        # Step 6: Confirm selections
        if confirm_selections(final_config):
            return final_config
        else:
            print_warning("Project creation cancelled by user.")
            return {}

    def _collect_basic_info(self) -> None:
        """Collect basic project information."""
        basic_info = prompt_basic_info()
        self.config.update(basic_info)

    def _collect_architecture_preset(self) -> None:
        """Collect the user's architecture preset choice.

        Persists the canonical id on the config under ``architecture_preset``
        (used by downstream code) plus the human-readable description under
        ``architecture_preset_description`` (used by the confirmation summary
        so users see what their choice means, not just the raw id).
        """
        preset = prompt_architecture_preset(self.settings)
        self.config["architecture_preset"] = preset
        self.config["architecture_preset_description"] = (
            self.settings.ARCHITECTURE_PRESETS.get(preset, "")
        )

    def _collect_template_selection(self) -> None:
        """Collect template selection."""
        template = prompt_template_selection(self.settings)
        self.config["base_template"] = template

    def _collect_feature_selections(self) -> None:
        """Collect all feature selections."""
        features = prompt_additional_features(self.settings)
        self.config.update(features)

    def build_config_from_mapping(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete a configuration that came from a file instead of prompts.

        ``fastkit init --config`` accepts a hand-written file that lists only
        feature selections; running them back through the same dependency
        collection the interactive flow uses keeps both entry points in
        agreement about which packages a selection implies.

        The mapping is normalised first, so a file that spells an axis
        differently than the prompts do (a ``{"type": ...}`` block for a
        single-select axis, say) still resolves to the catalog choice the
        rest of the pipeline reads.

        Args:
            config: Configuration mapping (interactive builder shape)

        Returns:
            The normalised mapping with ``all_dependencies`` filled in

        Raises:
            ConfigSchemaError: If the mapping holds an unknown key or choice
        """
        self.config = normalize_project_config(config, self.settings)
        return self._build_final_config()

    def _build_final_config(self) -> Dict[str, Any]:
        """
        Build and validate final configuration.

        Returns:
            Complete configuration dictionary with collected dependencies
        """
        # Normalise before anything reads the selections, so an interactive
        # session and a ``--config`` file hand the pipeline the same shape.
        self.config = normalize_project_config(self.config, self.settings)

        # Collect all dependencies
        all_deps = self._collect_all_dependencies()

        # Add to config
        self.config["all_dependencies"] = all_deps

        return self.config

    def _collect_all_dependencies(self) -> List[str]:
        """
        Collect all dependencies from selected features.

        Delegates to :class:`DependencyCollector`, which walks every axis in
        ``PACKAGE_CATALOG`` generically. Duplicating the walk here meant a
        newly added axis (logging, migrations, tooling) was silently skipped
        for interactive projects while ``fastkit init --config`` picked it up.

        Returns:
            Deduplicated list of all package dependencies
        """
        config = dict(self.config)

        # Custom packages are free-form user input, so they are sanitized
        # before the collector merges them with the catalog-derived set.
        custom_packages = config.get("custom_packages", [])
        if custom_packages:
            config["custom_packages"] = sanitize_custom_packages(custom_packages)

        collector = DependencyCollector(self.settings)
        return collector.collect_from_config(config)

    def get_config(self) -> Dict[str, Any]:
        """
        Get the current configuration.

        Returns:
            Current configuration dictionary
        """
        return self.config
