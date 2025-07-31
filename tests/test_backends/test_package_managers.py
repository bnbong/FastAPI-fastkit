# --------------------------------------------------------------------------
# Test Package Managers Module
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import shutil
import tempfile
from pathlib import Path
from typing import List
from unittest.mock import Mock, patch

import pytest

from fastapi_fastkit.backend.package_managers import (
    BasePackageManager,
    PackageManagerFactory,
    PdmManager,
    PipManager,
    PoetryManager,
    UvManager,
)
from fastapi_fastkit.core.exceptions import BackendExceptions


class TestBasePackageManager:
    """Test BasePackageManager abstract class."""

    def test_cannot_instantiate_abstract_class(self) -> None:
        """Test that BasePackageManager cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BasePackageManager("/test/path")  # type: ignore[abstract]

    def test_get_executable_path_windows(self) -> None:
        """Test executable path generation for Windows."""

        class TestManager(BasePackageManager):
            def is_available(self) -> bool:
                return True

            def get_dependency_file_name(self) -> str:
                return "test.txt"

            def create_virtual_environment(self) -> str:
                return "/test/venv"

            def install_dependencies(self, venv_path: str) -> None:
                pass

            def generate_dependency_file(self, deps: List[str]) -> None:
                pass

            def add_dependency(self, dep: str, dev: bool = False) -> None:
                pass

        manager = TestManager("/test")

        with patch("os.name", "nt"):
            path = manager.get_executable_path("pip", "/test/venv")
            assert path == "/test/venv/Scripts/pip.exe"

    def test_get_executable_path_unix(self) -> None:
        """Test executable path generation for Unix systems."""

        class TestManager(BasePackageManager):
            def is_available(self) -> bool:
                return True

            def get_dependency_file_name(self) -> str:
                return "test.txt"

            def create_virtual_environment(self) -> str:
                return "/test/venv"

            def install_dependencies(self, venv_path: str) -> None:
                pass

            def generate_dependency_file(self, deps: List[str]) -> None:
                pass

            def add_dependency(self, dep: str, dev: bool = False) -> None:
                pass

        manager = TestManager("/test")

        with patch("os.name", "posix"):
            path = manager.get_executable_path("pip", "/test/venv")
            assert path == "/test/venv/bin/pip"

    def test_get_dependency_file_path(self) -> None:
        """Test dependency file path generation."""

        class TestManager(BasePackageManager):
            def is_available(self) -> bool:
                return True

            def get_dependency_file_name(self) -> str:
                return "requirements.txt"

            def create_virtual_environment(self) -> str:
                return "/test/venv"

            def install_dependencies(self, venv_path: str) -> None:
                pass

            def generate_dependency_file(self, deps: List[str]) -> None:
                pass

            def add_dependency(self, dep: str, dev: bool = False) -> None:
                pass

        manager = TestManager("/test/project")
        file_path = manager.get_dependency_file_path()
        assert str(file_path) == "/test/project/requirements.txt"


class TestPackageManagerFactory:
    """Test PackageManagerFactory."""

    def test_get_supported_managers(self) -> None:
        """Test getting list of supported managers."""
        supported = PackageManagerFactory.get_supported_managers()
        expected = ["pip", "pdm", "uv", "poetry"]
        assert set(supported) == set(expected)

    @patch(
        "fastapi_fastkit.backend.package_managers.pip_manager.PipManager.is_available"
    )
    def test_create_pip_manager(self, mock_is_available: Mock) -> None:
        """Test creating PIP manager."""
        mock_is_available.return_value = True
        manager = PackageManagerFactory.create_manager("pip", "/test")
        assert isinstance(manager, PipManager)
        assert manager.get_dependency_file_name() == "requirements.txt"

    @patch(
        "fastapi_fastkit.backend.package_managers.pdm_manager.PdmManager.is_available"
    )
    def test_create_pdm_manager(self, mock_is_available: Mock) -> None:
        """Test creating PDM manager."""
        mock_is_available.return_value = True
        manager = PackageManagerFactory.create_manager("pdm", "/test")
        assert isinstance(manager, PdmManager)
        assert manager.get_dependency_file_name() == "pyproject.toml"

    @patch("fastapi_fastkit.backend.package_managers.uv_manager.UvManager.is_available")
    def test_create_uv_manager(self, mock_is_available: Mock) -> None:
        """Test creating UV manager."""
        mock_is_available.return_value = True
        manager = PackageManagerFactory.create_manager("uv", "/test")
        assert isinstance(manager, UvManager)
        assert manager.get_dependency_file_name() == "pyproject.toml"

    @patch(
        "fastapi_fastkit.backend.package_managers.poetry_manager.PoetryManager.is_available"
    )
    def test_create_poetry_manager(self, mock_is_available: Mock) -> None:
        """Test creating Poetry manager."""
        mock_is_available.return_value = True
        manager = PackageManagerFactory.create_manager("poetry", "/test")
        assert isinstance(manager, PoetryManager)
        assert manager.get_dependency_file_name() == "pyproject.toml"

    def test_create_unsupported_manager(self) -> None:
        """Test creating unsupported manager raises exception."""
        with pytest.raises(BackendExceptions) as exc_info:
            PackageManagerFactory.create_manager("unsupported", "/test")
        assert "Unsupported package manager" in str(exc_info.value)

    @patch(
        "fastapi_fastkit.backend.package_managers.pip_manager.PipManager.is_available"
    )
    def test_create_manager_case_insensitive(self, mock_is_available: Mock) -> None:
        """Test that manager creation is case insensitive."""
        mock_is_available.return_value = True
        manager = PackageManagerFactory.create_manager("PIP", "/test")
        assert isinstance(manager, PipManager)

    @patch(
        "fastapi_fastkit.backend.package_managers.pip_manager.PipManager.is_available"
    )
    def test_create_manager_not_available_no_auto_detect(
        self, mock_is_available: Mock
    ) -> None:
        """Test creating manager when not available and auto_detect=False."""
        mock_is_available.return_value = False

        with pytest.raises(BackendExceptions) as exc_info:
            PackageManagerFactory.create_manager("pip", "/test", auto_detect=False)
        assert "not available on the system" in str(exc_info.value)

    def test_get_available_managers(self) -> None:
        """Test getting available managers on system."""
        available = PackageManagerFactory.get_available_managers()
        assert isinstance(available, list)
        # At least pip should be available in most environments
        # assert "pip" in available

    def test_register_manager(self) -> None:
        """Test registering a new manager type."""

        class CustomManager(BasePackageManager):
            def is_available(self) -> bool:
                return True

            def get_dependency_file_name(self) -> str:
                return "custom.txt"

            def create_virtual_environment(self) -> str:
                return "/test/venv"

            def install_dependencies(self, venv_path: str) -> None:
                pass

            def generate_dependency_file(self, deps: List[str]) -> None:
                pass

            def add_dependency(self, dep: str, dev: bool = False) -> None:
                pass

        PackageManagerFactory.register_manager("custom", CustomManager)

        # Test that we can create the custom manager
        manager = PackageManagerFactory.create_manager("custom", "/test")
        assert isinstance(manager, CustomManager)

        # Cleanup
        del PackageManagerFactory._managers["custom"]

    def test_register_invalid_manager(self) -> None:
        """Test registering invalid manager class raises error."""

        class InvalidManager:
            pass

        with pytest.raises(ValueError) as exc_info:
            PackageManagerFactory.register_manager("invalid", InvalidManager)  # type: ignore[arg-type]
        assert "must inherit from BasePackageManager" in str(exc_info.value)


class TestPipManager:
    """Test PipManager implementation."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = PipManager(self.temp_dir)

    def teardown_method(self) -> None:
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("subprocess.run")
    def test_is_available_true(self, mock_run: Mock) -> None:
        """Test is_available returns True when pip is available."""
        mock_run.return_value.returncode = 0
        assert self.manager.is_available() is True

    @patch("subprocess.run")
    def test_is_available_false(self, mock_run: Mock) -> None:
        """Test is_available returns False when pip is not available."""
        mock_run.side_effect = FileNotFoundError()
        assert self.manager.is_available() is False

    def test_get_dependency_file_name(self) -> None:
        """Test dependency file name for pip."""
        assert self.manager.get_dependency_file_name() == "requirements.txt"

    def test_generate_dependency_file(self) -> None:
        """Test generating requirements.txt file."""
        dependencies = ["fastapi==0.104.1", "uvicorn==0.24.0"]
        self.manager.generate_dependency_file(dependencies)

        req_file = Path(self.temp_dir) / "requirements.txt"
        assert req_file.exists()

        content = req_file.read_text()
        assert "fastapi==0.104.1" in content
        assert "uvicorn==0.24.0" in content

    def test_add_dependency_new(self) -> None:
        """Test adding new dependency to requirements.txt."""
        # Create initial requirements.txt
        req_file = Path(self.temp_dir) / "requirements.txt"
        req_file.write_text("fastapi==0.104.1\n")

        self.manager.add_dependency("uvicorn==0.24.0")

        content = req_file.read_text()
        assert "fastapi==0.104.1" in content
        assert "uvicorn==0.24.0" in content

    def test_add_dependency_existing(self) -> None:
        """Test adding existing dependency doesn't duplicate."""
        # Create initial requirements.txt
        req_file = Path(self.temp_dir) / "requirements.txt"
        req_file.write_text("fastapi==0.104.1\n")

        self.manager.add_dependency("fastapi==0.104.1")

        content = req_file.read_text()
        # Should only appear once
        assert content.count("fastapi==0.104.1") == 1


class TestPdmManager:
    """Test PdmManager implementation."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = PdmManager(self.temp_dir)

    def teardown_method(self) -> None:
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("subprocess.run")
    def test_is_available_true(self, mock_run: Mock) -> None:
        """Test is_available returns True when PDM is available."""
        mock_run.return_value.returncode = 0
        assert self.manager.is_available() is True

    @patch("subprocess.run")
    def test_is_available_false(self, mock_run: Mock) -> None:
        """Test is_available returns False when PDM is not available."""
        mock_run.side_effect = FileNotFoundError()
        assert self.manager.is_available() is False

    def test_get_dependency_file_name(self) -> None:
        """Test dependency file name for PDM."""
        assert self.manager.get_dependency_file_name() == "pyproject.toml"

    def test_generate_dependency_file(self) -> None:
        """Test generating pyproject.toml file for PDM."""
        dependencies = ["fastapi", "uvicorn"]
        self.manager.generate_dependency_file(dependencies)

        toml_file = Path(self.temp_dir) / "pyproject.toml"
        assert toml_file.exists()

        content = toml_file.read_text()
        assert "[project]" in content
        assert '"fastapi"' in content
        assert '"uvicorn"' in content
        assert "[build-system]" in content
        assert "pdm-backend" in content

    def test_initialize_project(self) -> None:
        """Test PDM project initialization."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0

            self.manager.initialize_project(
                "test-project", "Test Author", "test@example.com", "Test description"
            )

            # Check if pyproject.toml was created with correct content
            toml_file = Path(self.temp_dir) / "pyproject.toml"
            assert toml_file.exists()

            content = toml_file.read_text()
            assert 'name = "test-project"' in content
            assert 'name = "Test Author"' in content
            assert 'email = "test@example.com"' in content
            assert 'description = "Test description"' in content


class TestIntegration:
    """Integration tests for package managers."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self) -> None:
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch(
        "fastapi_fastkit.backend.package_managers.pip_manager.PipManager.is_available"
    )
    @patch(
        "fastapi_fastkit.backend.package_managers.pdm_manager.PdmManager.is_available"
    )
    @patch("fastapi_fastkit.backend.package_managers.uv_manager.UvManager.is_available")
    @patch(
        "fastapi_fastkit.backend.package_managers.poetry_manager.PoetryManager.is_available"
    )
    def test_factory_creates_all_managers(
        self, mock_poetry: Mock, mock_uv: Mock, mock_pdm: Mock, mock_pip: Mock
    ) -> None:
        """Test that factory can create all supported managers."""
        # Mock all managers as available
        mock_pip.return_value = True
        mock_pdm.return_value = True
        mock_uv.return_value = True
        mock_poetry.return_value = True

        factory = PackageManagerFactory()

        for manager_type in factory.get_supported_managers():
            manager = factory.create_manager(manager_type, self.temp_dir)
            assert manager is not None
            assert hasattr(manager, "is_available")
            assert hasattr(manager, "get_dependency_file_name")
            assert hasattr(manager, "create_virtual_environment")
            assert hasattr(manager, "install_dependencies")
            assert hasattr(manager, "generate_dependency_file")
            assert hasattr(manager, "add_dependency")

    @patch(
        "fastapi_fastkit.backend.package_managers.pip_manager.PipManager.is_available"
    )
    @patch(
        "fastapi_fastkit.backend.package_managers.pdm_manager.PdmManager.is_available"
    )
    @patch("fastapi_fastkit.backend.package_managers.uv_manager.UvManager.is_available")
    @patch(
        "fastapi_fastkit.backend.package_managers.poetry_manager.PoetryManager.is_available"
    )
    def test_all_managers_implement_interface(
        self, mock_poetry: Mock, mock_uv: Mock, mock_pdm: Mock, mock_pip: Mock
    ) -> None:
        """Test that all managers properly implement the interface."""
        # Mock all managers as available
        mock_pip.return_value = True
        mock_pdm.return_value = True
        mock_uv.return_value = True
        mock_poetry.return_value = True

        factory = PackageManagerFactory()

        for manager_type in factory.get_supported_managers():
            manager = factory.create_manager(manager_type, self.temp_dir)

            # Test that all required methods exist and are callable
            assert callable(manager.is_available)
            assert callable(manager.get_dependency_file_name)
            assert callable(manager.create_virtual_environment)
            assert callable(manager.install_dependencies)
            assert callable(manager.generate_dependency_file)
            assert callable(manager.add_dependency)

            # Test basic method calls don't raise unexpected errors
            file_name = manager.get_dependency_file_name()
            assert isinstance(file_name, str)
            assert len(file_name) > 0

    @patch("fastapi_fastkit.backend.package_managers.pip_manager.subprocess.run")
    def test_pip_manager_dependency_workflow(self, mock_run: Mock) -> None:
        """Test complete dependency management workflow with PIP."""
        mock_run.return_value.returncode = 0

        manager = PipManager(self.temp_dir)

        # Generate dependency file
        deps = ["fastapi==0.104.1", "uvicorn==0.24.0"]
        manager.generate_dependency_file(deps)

        # Check file was created
        req_file = Path(self.temp_dir) / "requirements.txt"
        assert req_file.exists()

        # Add new dependency
        manager.add_dependency("pytest==7.4.0")

        # Check it was added
        content = req_file.read_text()
        assert "pytest==7.4.0" in content
