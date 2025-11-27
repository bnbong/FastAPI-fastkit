# --------------------------------------------------------------------------
# Project Builder module for FastAPI-fastkit
#
# Provides project building functionality including:
# - Dependency collection and management
# - Dynamic configuration file generation
# - Template merging
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from .config_generator import DynamicConfigGenerator
from .dependency_collector import DependencyCollector

__all__ = [
    "DependencyCollector",
    "DynamicConfigGenerator",
]
