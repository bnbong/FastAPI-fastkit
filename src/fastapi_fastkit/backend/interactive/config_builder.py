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

from .prompts import (
    prompt_additional_features,
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

        # Step 2: Always use Empty template as base for interactive mode
        # (Feature selection will build the project incrementally)
        self.config["base_template"] = None  # None = Empty project

        # Step 3: Feature selections
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

    def _collect_template_selection(self) -> None:
        """Collect template selection."""
        template = prompt_template_selection(self.settings)
        self.config["base_template"] = template

    def _collect_feature_selections(self) -> None:
        """Collect all feature selections."""
        features = prompt_additional_features(self.settings)
        self.config.update(features)

    def _build_final_config(self) -> Dict[str, Any]:
        """
        Build and validate final configuration.

        Returns:
            Complete configuration dictionary with collected dependencies
        """
        # Collect all dependencies
        all_deps = self._collect_all_dependencies()

        # Add to config
        self.config["all_dependencies"] = all_deps

        return self.config

    def _collect_all_dependencies(self) -> List[str]:
        """
        Collect all dependencies from selected features.

        Returns:
            Deduplicated list of all package dependencies
        """
        dependencies = set()

        # Always add base FastAPI dependencies
        dependencies.update(["fastapi", "uvicorn", "pydantic", "pydantic-settings"])

        # Database dependencies
        db_info = self.config.get("database", {})
        if isinstance(db_info, dict) and db_info.get("packages"):
            dependencies.update(db_info["packages"])

        # Authentication dependencies
        auth_type = self.config.get("authentication", "None")
        if auth_type != "None":
            auth_packages = self.settings.PACKAGE_CATALOG["authentication"].get(
                auth_type, []
            )
            dependencies.update(auth_packages)

        # Async tasks dependencies
        tasks_type = self.config.get("async_tasks", "None")
        if tasks_type != "None":
            task_packages = self.settings.PACKAGE_CATALOG["async_tasks"].get(
                tasks_type, []
            )
            dependencies.update(task_packages)

        # Caching dependencies
        cache_type = self.config.get("caching", "None")
        if cache_type != "None":
            cache_packages = self.settings.PACKAGE_CATALOG["caching"].get(
                cache_type, []
            )
            dependencies.update(cache_packages)

        # Monitoring dependencies
        monitoring_type = self.config.get("monitoring", "None")
        if monitoring_type != "None":
            monitoring_packages = self.settings.PACKAGE_CATALOG["monitoring"].get(
                monitoring_type, []
            )
            dependencies.update(monitoring_packages)

        # Testing dependencies
        testing_type = self.config.get("testing", "None")
        if testing_type != "None":
            testing_packages = self.settings.PACKAGE_CATALOG["testing"].get(
                testing_type, []
            )
            dependencies.update(testing_packages)

        # Utilities dependencies
        utilities = self.config.get("utilities", [])
        for util in utilities:
            if util in self.settings.PACKAGE_CATALOG["utilities"]:
                util_packages = self.settings.PACKAGE_CATALOG["utilities"][util]
                dependencies.update(util_packages)

        # Custom packages
        custom_packages = self.config.get("custom_packages", [])
        if custom_packages:
            sanitized = sanitize_custom_packages(custom_packages)
            dependencies.update(sanitized)

        # Convert to sorted list
        return sorted(list(dependencies))

    def get_config(self) -> Dict[str, Any]:
        """
        Get the current configuration.

        Returns:
            Current configuration dictionary
        """
        return self.config
