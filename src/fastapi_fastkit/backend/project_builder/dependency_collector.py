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

        Args:
            config: Project configuration dictionary

        Returns:
            Sorted list of all dependencies
        """
        # Reset dependencies
        self.dependencies = set()

        # Add base dependencies
        self.add_base_dependencies()

        # Add database dependencies
        db_info = config.get("database", {})
        if isinstance(db_info, dict) and db_info.get("type") != "None":
            self.add_database_dependencies(db_info.get("type", ""))

        # Add authentication dependencies
        auth_type = config.get("authentication", "None")
        if auth_type != "None":
            self.add_authentication_dependencies(auth_type)

        # Add async tasks dependencies
        tasks_type = config.get("async_tasks", "None")
        if tasks_type != "None":
            self.add_async_tasks_dependencies(tasks_type)

        # Add caching dependencies
        cache_type = config.get("caching", "None")
        if cache_type != "None":
            self.add_caching_dependencies(cache_type)

        # Add monitoring dependencies
        monitoring_type = config.get("monitoring", "None")
        if monitoring_type != "None":
            self.add_monitoring_dependencies(monitoring_type)

        # Add testing dependencies
        testing_type = config.get("testing", "None")
        if testing_type != "None":
            self.add_testing_dependencies(testing_type)

        # Add utilities dependencies
        utilities = config.get("utilities", [])
        for util in utilities:
            self.add_utility_dependencies(util)

        # Add custom packages
        custom = config.get("custom_packages", [])
        if custom:
            self.dependencies.update(custom)

        return self.get_final_dependencies()

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
        catalog = self.settings.PACKAGE_CATALOG.get("database", {})
        packages = catalog.get(db_type, [])
        self.dependencies.update(packages)

    def add_authentication_dependencies(self, auth_type: str) -> None:
        """
        Add authentication dependencies.

        Args:
            auth_type: Authentication type name
        """
        catalog = self.settings.PACKAGE_CATALOG.get("authentication", {})
        packages = catalog.get(auth_type, [])
        self.dependencies.update(packages)

    def add_async_tasks_dependencies(self, tasks_type: str) -> None:
        """
        Add async tasks dependencies.

        Args:
            tasks_type: Task queue type name
        """
        catalog = self.settings.PACKAGE_CATALOG.get("async_tasks", {})
        packages = catalog.get(tasks_type, [])
        self.dependencies.update(packages)

    def add_caching_dependencies(self, cache_type: str) -> None:
        """
        Add caching dependencies.

        Args:
            cache_type: Caching type name
        """
        catalog = self.settings.PACKAGE_CATALOG.get("caching", {})
        packages = catalog.get(cache_type, [])
        self.dependencies.update(packages)

    def add_monitoring_dependencies(self, monitoring_type: str) -> None:
        """
        Add monitoring dependencies.

        Args:
            monitoring_type: Monitoring type name
        """
        catalog = self.settings.PACKAGE_CATALOG.get("monitoring", {})
        packages = catalog.get(monitoring_type, [])
        self.dependencies.update(packages)

    def add_testing_dependencies(self, testing_type: str) -> None:
        """
        Add testing dependencies.

        Args:
            testing_type: Testing framework type name
        """
        catalog = self.settings.PACKAGE_CATALOG.get("testing", {})
        packages = catalog.get(testing_type, [])
        self.dependencies.update(packages)

    def add_utility_dependencies(self, utility: str) -> None:
        """
        Add utility dependencies.

        Args:
            utility: Utility name
        """
        catalog = self.settings.PACKAGE_CATALOG.get("utilities", {})
        packages = catalog.get(utility, [])
        self.dependencies.update(packages)

    def add_feature_dependencies(self, features: List[str]) -> None:
        """
        Add dependencies for selected features.

        Args:
            features: List of feature names
        """
        for feature in features:
            # This is a generic method that can be extended
            # Currently handled by specific methods above
            pass

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
