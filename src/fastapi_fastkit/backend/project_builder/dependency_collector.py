# --------------------------------------------------------------------------
# Dependency collection and management
#
# Collects dependencies from:
# - Base template (if selected)
# - Database choice
# - Authentication method
# - Additional features
# - Custom packages
#
# Handles deduplication and version conflict detection.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from typing import Any, Dict, List, Set

from fastapi_fastkit.core.settings import (
    MULTI_SELECT_AXES,
    NONE_CHOICE,
    FeatureAxis,
)


class DependencyCollector:
    """
    Collects and manages project dependencies.

    This class is responsible for gathering all dependencies from
    various sources and ensuring they are properly deduplicated.
    """

    def __init__(self, settings: Any) -> None:
        """
        Initialize dependency collector.

        Args:
            settings: FastkitConfig instance
        """
        self.settings = settings
        self.dependencies: Set[str] = set()

    def collect_from_config(self, config: Dict[str, Any]) -> List[str]:
        """
        Collect all dependencies from configuration.

        Every axis in ``PACKAGE_CATALOG`` is walked generically through
        :class:`~fastapi_fastkit.core.settings.FeatureAxis`, so a new axis
        only has to be added to the catalog — there is no per-axis branch
        here to forget to update.

        Args:
            config: Project configuration dictionary

        Returns:
            Sorted list of all dependencies
        """
        # Reset dependencies
        self.dependencies = set()

        # Add base dependencies
        self.add_base_dependencies()

        for axis in FeatureAxis:
            for choice in self._selected_choices(config, axis):
                self.add_axis_dependencies(axis, choice)

        # Add custom packages
        custom = config.get("custom_packages", [])
        if custom:
            self.dependencies.update(custom)

        return self.get_final_dependencies()

    @staticmethod
    def _selected_choices(config: Dict[str, Any], axis: str) -> List[str]:
        """
        Normalise one axis' selection into a list of catalog keys.

        Handles the three shapes the interactive config uses: the database
        axis stores ``{"type": ..., "packages": [...]}``, multi-select axes
        store a list, and every other axis stores a bare string.

        Args:
            config: Project configuration dictionary
            axis: Axis key to read

        Returns:
            Selected choice names, with the ``None`` sentinel filtered out
        """
        raw = config.get(axis)

        if axis == FeatureAxis.DATABASE and isinstance(raw, dict):
            raw = raw.get("type", NONE_CHOICE)

        if raw is None:
            return []
        if axis in MULTI_SELECT_AXES or isinstance(raw, list):
            selected = [str(item) for item in raw]
        else:
            selected = [str(raw)]

        return [choice for choice in selected if choice != NONE_CHOICE]

    def add_axis_dependencies(self, axis: str, choice: str) -> None:
        """
        Add the packages one catalog choice implies.

        Args:
            axis: Catalog axis key (see :class:`FeatureAxis`)
            choice: Selected option within that axis
        """
        catalog = self.settings.PACKAGE_CATALOG.get(axis, {})
        self.dependencies.update(catalog.get(choice, []))

    def add_base_dependencies(self) -> None:
        """Add core FastAPI dependencies."""
        self.dependencies.update(
            [
                "fastapi",
                "uvicorn",
                "pydantic",
                "pydantic-settings",
            ]
        )

    def add_database_dependencies(self, db_type: str) -> None:
        """
        Add database-specific dependencies.

        Args:
            db_type: Database type name
        """
        self.add_axis_dependencies(FeatureAxis.DATABASE, db_type)

    def add_authentication_dependencies(self, auth_type: str) -> None:
        """
        Add authentication-specific dependencies.

        Args:
            auth_type: Authentication type name
        """
        self.add_axis_dependencies(FeatureAxis.AUTHENTICATION, auth_type)

    def add_async_tasks_dependencies(self, tasks_type: str) -> None:
        """
        Add async tasks-specific dependencies.

        Args:
            tasks_type: Task queue type name
        """
        self.add_axis_dependencies(FeatureAxis.ASYNC_TASKS, tasks_type)

    def add_caching_dependencies(self, cache_type: str) -> None:
        """
        Add caching-specific dependencies.

        Args:
            cache_type: Caching type name
        """
        self.add_axis_dependencies(FeatureAxis.CACHING, cache_type)

    def add_monitoring_dependencies(self, monitoring_type: str) -> None:
        """
        Add monitoring-specific dependencies.

        Args:
            monitoring_type: Monitoring type name
        """
        self.add_axis_dependencies(FeatureAxis.MONITORING, monitoring_type)

    def add_testing_dependencies(self, testing_type: str) -> None:
        """
        Add testing-specific dependencies.

        Args:
            testing_type: Testing framework type name
        """
        self.add_axis_dependencies(FeatureAxis.TESTING, testing_type)

    def add_utility_dependencies(self, utility: str) -> None:
        """
        Add utilities-specific dependencies.

        Args:
            utility: Utility name
        """
        self.add_axis_dependencies(FeatureAxis.UTILITIES, utility)

    def add_migrations_dependencies(self, migrations_type: str) -> None:
        """
        Add migrations-specific dependencies.

        Args:
            migrations_type: Migration tool name
        """
        self.add_axis_dependencies(FeatureAxis.MIGRATIONS, migrations_type)

    def add_tooling_dependencies(self, tooling: str) -> None:
        """
        Add tooling-specific dependencies.

        Args:
            tooling: Developer tooling option name
        """
        self.add_axis_dependencies(FeatureAxis.TOOLING, tooling)

    def add_logging_dependencies(self, logging_type: str) -> None:
        """
        Add logging-specific dependencies.

        Args:
            logging_type: Logging style name
        """
        self.add_axis_dependencies(FeatureAxis.LOGGING, logging_type)

    def add_feature_dependencies(self, features: List[str]) -> None:
        """
        Add dependencies for ``"<axis>:<choice>"`` feature strings.

        This is the shape project metadata records selections in, so a
        previously generated project's ``[tool.fastapi-fastkit] features``
        list can be replayed straight back into a dependency set.

        Args:
            features: List of ``"<axis>:<choice>"`` entries
        """
        for feature in features:
            axis, _, choice = feature.partition(":")
            if not choice or choice == NONE_CHOICE:
                continue
            self.add_axis_dependencies(axis, choice)

    def get_final_dependencies(self) -> List[str]:
        """
        Return deduplicated, sorted dependency list.

        Returns:
            Sorted list of all dependencies
        """
        return sorted(list(self.dependencies))

    def get_dependency_count(self) -> int:
        """
        Get the total number of dependencies.

        Returns:
            Count of unique dependencies
        """
        return len(self.dependencies)
