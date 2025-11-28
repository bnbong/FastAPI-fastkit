# --------------------------------------------------------------------------
# Test Package Managers Module
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, List
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

            def generate_dependency_file(
                self,
                dependencies: List[str],
                project_name: str = "",
                author: str = "",
                author_email: str = "",
                description: str = "",
            ) -> None:
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

            def generate_dependency_file(
                self,
                dependencies: List[str],
                project_name: str = "",
                author: str = "",
                author_email: str = "",
                description: str = "",
            ) -> None:
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

            def generate_dependency_file(
                self,
                dependencies: List[str],
                project_name: str = "",
                author: str = "",
                author_email: str = "",
                description: str = "",
            ) -> None:
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

            def generate_dependency_file(
                self,
                dependencies: List[str],
                project_name: str = "",
                author: str = "",
                author_email: str = "",
                description: str = "",
            ) -> None:
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


# ============================================================================
# Extended Coverage Tests
# These tests run only during explicit coverage tests and CI
# ============================================================================


@pytest.mark.extended
class TestPipManagerExtended:
    """Extended coverage tests for PipManager."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = PipManager(self.temp_dir)

    def teardown_method(self) -> None:
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("subprocess.run")
    def test_create_virtual_environment_success(self, mock_run: Mock) -> None:
        """Test successful virtual environment creation."""
        mock_run.return_value.returncode = 0
        venv_path = self.manager.create_virtual_environment()
        assert venv_path == str(Path(self.temp_dir) / ".venv")
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_create_virtual_environment_failure(self, mock_run: Mock) -> None:
        """Test virtual environment creation failure."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "venv", stderr="Error")
        with pytest.raises(BackendExceptions):
            self.manager.create_virtual_environment()

    @patch("subprocess.run")
    def test_create_virtual_environment_os_error(self, mock_run: Mock) -> None:
        """Test virtual environment creation OS error."""
        mock_run.side_effect = OSError("Disk full")
        with pytest.raises(BackendExceptions):
            self.manager.create_virtual_environment()

    def test_install_dependencies_no_venv(self) -> None:
        """Test installing dependencies when venv doesn't exist."""
        with patch.object(
            self.manager, "create_virtual_environment"
        ) as mock_create_venv:
            mock_create_venv.return_value = None
            with pytest.raises(BackendExceptions):
                self.manager.install_dependencies("/nonexistent/venv")

    @patch("subprocess.run")
    def test_install_dependencies_no_requirements_file(self, mock_run: Mock) -> None:
        """Test installing dependencies when requirements.txt doesn't exist."""
        venv_path = str(Path(self.temp_dir) / ".venv")
        Path(venv_path).mkdir(parents=True)

        with pytest.raises(BackendExceptions) as exc_info:
            self.manager.install_dependencies(venv_path)
        assert "Requirements file not found" in str(exc_info.value)

    @patch("subprocess.run")
    def test_install_dependencies_success(self, mock_run: Mock) -> None:
        """Test successful dependency installation."""
        venv_path = str(Path(self.temp_dir) / ".venv")
        Path(venv_path).mkdir(parents=True)

        # Create requirements.txt
        req_file = Path(self.temp_dir) / "requirements.txt"
        req_file.write_text("fastapi==0.104.1\n")

        mock_run.return_value.returncode = 0
        self.manager.install_dependencies(venv_path)
        # Should call pip upgrade and install
        assert mock_run.call_count == 2

    @patch("subprocess.run")
    def test_install_dependencies_failure(self, mock_run: Mock) -> None:
        """Test dependency installation failure."""
        venv_path = str(Path(self.temp_dir) / ".venv")
        Path(venv_path).mkdir(parents=True)

        req_file = Path(self.temp_dir) / "requirements.txt"
        req_file.write_text("fastapi==0.104.1\n")

        mock_run.side_effect = subprocess.CalledProcessError(
            1, "pip", stderr="Installation failed"
        )
        with pytest.raises(BackendExceptions):
            self.manager.install_dependencies(venv_path)

    def test_generate_dependency_file_error(self) -> None:
        """Test dependency file generation with OS error."""
        with patch("builtins.open", side_effect=OSError("Permission denied")):
            with pytest.raises(BackendExceptions):
                self.manager.generate_dependency_file(["fastapi"])

    def test_add_dependency_unicode_error(self) -> None:
        """Test adding dependency with unicode decode error."""
        req_file = Path(self.temp_dir) / "requirements.txt"
        req_file.write_bytes(b"\xff\xfe")  # Invalid UTF-8

        with pytest.raises(BackendExceptions):
            self.manager.add_dependency("pytest")


@pytest.mark.extended
class TestPdmManagerExtended:
    """Extended coverage tests for PdmManager."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = PdmManager(self.temp_dir)

    def teardown_method(self) -> None:
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("subprocess.run")
    def test_create_virtual_environment_success(self, mock_run: Mock) -> None:
        """Test successful virtual environment creation with PDM."""
        mock_run.return_value.returncode = 0
        venv_path = self.manager.create_virtual_environment()
        assert venv_path == str(Path(self.temp_dir) / ".venv")

    @patch("subprocess.run")
    def test_create_virtual_environment_failure(self, mock_run: Mock) -> None:
        """Test virtual environment creation failure with PDM."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "pdm", stderr="PDM error"
        )
        with pytest.raises(BackendExceptions):
            self.manager.create_virtual_environment()

    @patch("subprocess.run")
    def test_create_virtual_environment_os_error(self, mock_run: Mock) -> None:
        """Test virtual environment creation OS error with PDM."""
        mock_run.side_effect = OSError("System error")
        with pytest.raises(BackendExceptions):
            self.manager.create_virtual_environment()

    def test_install_dependencies_no_venv(self) -> None:
        """Test installing dependencies when venv doesn't exist."""
        with patch.object(
            self.manager, "create_virtual_environment"
        ) as mock_create_venv:
            mock_create_venv.return_value = None
            with pytest.raises(BackendExceptions):
                self.manager.install_dependencies("/nonexistent/venv")

    @patch("subprocess.run")
    def test_install_dependencies_no_pyproject(self, mock_run: Mock) -> None:
        """Test installing dependencies when pyproject.toml doesn't exist."""
        venv_path = str(Path(self.temp_dir) / ".venv")
        Path(venv_path).mkdir(parents=True)

        with pytest.raises(BackendExceptions) as exc_info:
            self.manager.install_dependencies(venv_path)
        assert "pyproject.toml file not found" in str(exc_info.value)

    @patch("subprocess.run")
    def test_install_dependencies_success(self, mock_run: Mock) -> None:
        """Test successful dependency installation with PDM."""
        venv_path = str(Path(self.temp_dir) / ".venv")
        Path(venv_path).mkdir(parents=True)

        # Create pyproject.toml
        pyproject_file = Path(self.temp_dir) / "pyproject.toml"
        pyproject_file.write_text('[project]\nname = "test"\n')

        mock_run.return_value.returncode = 0
        self.manager.install_dependencies(venv_path)
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_install_dependencies_failure(self, mock_run: Mock) -> None:
        """Test dependency installation failure with PDM."""
        venv_path = str(Path(self.temp_dir) / ".venv")
        Path(venv_path).mkdir(parents=True)

        pyproject_file = Path(self.temp_dir) / "pyproject.toml"
        pyproject_file.write_text('[project]\nname = "test"\n')

        mock_run.side_effect = subprocess.CalledProcessError(
            1, "pdm", stderr="Installation failed"
        )
        with pytest.raises(BackendExceptions):
            self.manager.install_dependencies(venv_path)

    @patch("subprocess.run")
    def test_install_dependencies_os_error(self, mock_run: Mock) -> None:
        """Test dependency installation OS error with PDM."""
        venv_path = str(Path(self.temp_dir) / ".venv")
        Path(venv_path).mkdir(parents=True)

        pyproject_file = Path(self.temp_dir) / "pyproject.toml"
        pyproject_file.write_text('[project]\nname = "test"\n')

        mock_run.side_effect = OSError("System error")
        with pytest.raises(BackendExceptions):
            self.manager.install_dependencies(venv_path)

    def test_generate_dependency_file_with_metadata(self) -> None:
        """Test generating pyproject.toml with metadata."""
        deps = ["fastapi", "uvicorn"]
        self.manager.generate_dependency_file(
            deps,
            project_name="test-project",
            author="Test Author",
            author_email="test@example.com",
            description="Test description",
        )

        pyproject_file = Path(self.temp_dir) / "pyproject.toml"
        assert pyproject_file.exists()
        content = pyproject_file.read_text()
        assert 'name = "test-project"' in content
        assert 'name = "Test Author"' in content
        assert 'email = "test@example.com"' in content
        assert 'description = "Test description"' in content

    def test_generate_dependency_file_error(self) -> None:
        """Test pyproject.toml generation error."""
        with patch("builtins.open", side_effect=OSError("Permission denied")):
            with pytest.raises(BackendExceptions):
                self.manager.generate_dependency_file(["fastapi"])

    @patch("subprocess.run")
    def test_add_dependency_success(self, mock_run: Mock) -> None:
        """Test successful dependency addition with PDM."""
        mock_run.return_value.returncode = 0
        self.manager.add_dependency("fastapi")
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_add_dependency_dev(self, mock_run: Mock) -> None:
        """Test adding dev dependency with PDM."""
        mock_run.return_value.returncode = 0
        self.manager.add_dependency("pytest", dev=True)
        args = mock_run.call_args[0][0]
        assert "--dev" in args

    @patch("subprocess.run")
    def test_add_dependency_failure(self, mock_run: Mock) -> None:
        """Test dependency addition failure with PDM."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "pdm", stderr="Error")
        with pytest.raises(BackendExceptions):
            self.manager.add_dependency("fastapi")

    @patch("subprocess.run")
    def test_add_dependency_os_error(self, mock_run: Mock) -> None:
        """Test dependency addition OS error with PDM."""
        mock_run.side_effect = OSError("System error")
        with pytest.raises(BackendExceptions):
            self.manager.add_dependency("fastapi")

    @patch("subprocess.run")
    def test_initialize_project_success(self, mock_run: Mock) -> None:
        """Test successful project initialization with PDM."""
        mock_run.return_value.returncode = 0
        self.manager.initialize_project(
            "test-project", "Author", "author@example.com", "Description"
        )

        pyproject_file = Path(self.temp_dir) / "pyproject.toml"
        assert pyproject_file.exists()

    @patch("subprocess.run")
    def test_initialize_project_subprocess_error(self, mock_run: Mock) -> None:
        """Test project initialization subprocess error."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "pdm", stderr="Error")
        with pytest.raises(BackendExceptions):
            self.manager.initialize_project(
                "test-project", "Author", "author@example.com", "Description"
            )

    @patch("subprocess.run")
    def test_initialize_project_os_error(self, mock_run: Mock) -> None:
        """Test project initialization OS error."""
        mock_run.return_value.returncode = 0
        with patch("builtins.open", side_effect=OSError("Permission denied")):
            with pytest.raises(BackendExceptions):
                self.manager.initialize_project(
                    "test-project", "Author", "author@example.com", "Description"
                )


@pytest.mark.extended
class TestPoetryManagerExtended:
    """Extended coverage tests for PoetryManager."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = PoetryManager(self.temp_dir)

    def teardown_method(self) -> None:
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("subprocess.run")
    def test_create_virtual_environment_existing_venv(self, mock_run: Mock) -> None:
        """Test virtual environment creation when venv already exists."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "/path/to/venv"
        mock_run.return_value = mock_result

        venv_path = self.manager.create_virtual_environment()
        assert venv_path == "/path/to/venv"

    @patch("subprocess.run")
    def test_create_virtual_environment_create_new(self, mock_run: Mock) -> None:
        """Test creating new virtual environment with Poetry."""

        def run_side_effect(*args: Any, **kwargs: Any) -> Any:
            result = Mock()
            if "env" in args[0] and "info" in args[0]:
                if hasattr(run_side_effect, "called"):
                    result.returncode = 0
                    result.stdout = "/path/to/new/venv"
                else:
                    run_side_effect.called = True  # type: ignore[attr-defined]
                    result.returncode = 1
                    result.stdout = ""
            else:
                result.returncode = 0
                result.stdout = ""
            return result

        mock_run.side_effect = run_side_effect
        venv_path = self.manager.create_virtual_environment()
        assert venv_path == "/path/to/new/venv"

    @patch("subprocess.run")
    def test_create_virtual_environment_failure(self, mock_run: Mock) -> None:
        """Test virtual environment creation failure with Poetry."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "poetry", stderr="Error"
        )
        with pytest.raises(BackendExceptions):
            self.manager.create_virtual_environment()

    @patch("subprocess.run")
    def test_create_virtual_environment_os_error(self, mock_run: Mock) -> None:
        """Test virtual environment creation OS error with Poetry."""
        mock_run.side_effect = OSError("System error")
        with pytest.raises(BackendExceptions):
            self.manager.create_virtual_environment()

    @patch("subprocess.run")
    def test_install_dependencies_no_pyproject(self, mock_run: Mock) -> None:
        """Test installing dependencies when pyproject.toml doesn't exist."""
        with pytest.raises(BackendExceptions) as exc_info:
            self.manager.install_dependencies("/some/venv")
        assert "pyproject.toml file not found" in str(exc_info.value)

    @patch("subprocess.run")
    def test_install_dependencies_success(self, mock_run: Mock) -> None:
        """Test successful dependency installation with Poetry."""
        pyproject_file = Path(self.temp_dir) / "pyproject.toml"
        pyproject_file.write_text('[tool.poetry]\nname = "test"\n')

        mock_run.return_value.returncode = 0
        self.manager.install_dependencies("/some/venv")
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_install_dependencies_failure(self, mock_run: Mock) -> None:
        """Test dependency installation failure with Poetry."""
        pyproject_file = Path(self.temp_dir) / "pyproject.toml"
        pyproject_file.write_text('[tool.poetry]\nname = "test"\n')

        mock_run.side_effect = subprocess.CalledProcessError(
            1, "poetry", stderr="Installation failed"
        )
        with pytest.raises(BackendExceptions):
            self.manager.install_dependencies("/some/venv")

    @patch("subprocess.run")
    def test_install_dependencies_os_error(self, mock_run: Mock) -> None:
        """Test dependency installation OS error with Poetry."""
        pyproject_file = Path(self.temp_dir) / "pyproject.toml"
        pyproject_file.write_text('[tool.poetry]\nname = "test"\n')

        mock_run.side_effect = OSError("System error")
        with pytest.raises(BackendExceptions):
            self.manager.install_dependencies("/some/venv")

    def test_generate_dependency_file_with_metadata(self) -> None:
        """Test generating pyproject.toml with Poetry format."""
        deps = ["fastapi==0.104.1", "uvicorn"]
        self.manager.generate_dependency_file(
            deps,
            project_name="test-project",
            author="Test Author",
            author_email="test@example.com",
            description="Test description",
        )

        pyproject_file = Path(self.temp_dir) / "pyproject.toml"
        assert pyproject_file.exists()
        content = pyproject_file.read_text()
        assert "[tool.poetry]" in content
        assert 'name = "test-project"' in content
        assert 'fastapi = "0.104.1"' in content
        assert 'uvicorn = "*"' in content

    def test_generate_dependency_file_error(self) -> None:
        """Test pyproject.toml generation error with Poetry."""
        with patch("builtins.open", side_effect=OSError("Permission denied")):
            with pytest.raises(BackendExceptions):
                self.manager.generate_dependency_file(["fastapi"])

    @patch("subprocess.run")
    def test_add_dependency_success(self, mock_run: Mock) -> None:
        """Test successful dependency addition with Poetry."""
        mock_run.return_value.returncode = 0
        self.manager.add_dependency("fastapi")
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_add_dependency_dev(self, mock_run: Mock) -> None:
        """Test adding dev dependency with Poetry."""
        mock_run.return_value.returncode = 0
        self.manager.add_dependency("pytest", dev=True)
        args = mock_run.call_args[0][0]
        assert "--group=dev" in args

    @patch("subprocess.run")
    def test_add_dependency_failure(self, mock_run: Mock) -> None:
        """Test dependency addition failure with Poetry."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "poetry", stderr="Error"
        )
        with pytest.raises(BackendExceptions):
            self.manager.add_dependency("fastapi")

    @patch("subprocess.run")
    def test_add_dependency_os_error(self, mock_run: Mock) -> None:
        """Test dependency addition OS error with Poetry."""
        mock_run.side_effect = OSError("System error")
        with pytest.raises(BackendExceptions):
            self.manager.add_dependency("fastapi")

    @patch("subprocess.run")
    def test_initialize_project_success(self, mock_run: Mock) -> None:
        """Test successful project initialization with Poetry."""
        mock_run.return_value.returncode = 0
        self.manager.initialize_project(
            "test-project", "Author", "author@example.com", "Description"
        )
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_initialize_project_subprocess_error(self, mock_run: Mock) -> None:
        """Test project initialization subprocess error with Poetry."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "poetry", stderr="Error"
        )
        with pytest.raises(BackendExceptions):
            self.manager.initialize_project(
                "test-project", "Author", "author@example.com", "Description"
            )

    @patch("subprocess.run")
    def test_initialize_project_os_error(self, mock_run: Mock) -> None:
        """Test project initialization OS error with Poetry."""
        mock_run.side_effect = OSError("System error")
        with pytest.raises(BackendExceptions):
            self.manager.initialize_project(
                "test-project", "Author", "author@example.com", "Description"
            )

    @patch("subprocess.run")
    def test_lock_dependencies_success(self, mock_run: Mock) -> None:
        """Test successful lock file generation with Poetry."""
        mock_run.return_value.returncode = 0
        self.manager.lock_dependencies()
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_lock_dependencies_failure(self, mock_run: Mock) -> None:
        """Test lock file generation failure with Poetry."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "poetry", stderr="Lock error"
        )
        with pytest.raises(BackendExceptions):
            self.manager.lock_dependencies()

    @patch("subprocess.run")
    def test_lock_dependencies_os_error(self, mock_run: Mock) -> None:
        """Test lock file generation OS error with Poetry."""
        mock_run.side_effect = OSError("System error")
        with pytest.raises(BackendExceptions):
            self.manager.lock_dependencies()

    @patch("subprocess.run")
    def test_run_script_success(self, mock_run: Mock) -> None:
        """Test successful script execution with Poetry."""
        mock_run.return_value.returncode = 0
        self.manager.run_script("python test.py")
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_run_script_failure(self, mock_run: Mock) -> None:
        """Test script execution failure with Poetry."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "poetry", stderr="Script error"
        )
        with pytest.raises(BackendExceptions):
            self.manager.run_script("python test.py")

    @patch("subprocess.run")
    def test_run_script_os_error(self, mock_run: Mock) -> None:
        """Test script execution OS error with Poetry."""
        mock_run.side_effect = OSError("System error")
        with pytest.raises(BackendExceptions):
            self.manager.run_script("python test.py")

    @patch("subprocess.run")
    def test_show_dependencies_success(self, mock_run: Mock) -> None:
        """Test showing dependencies with Poetry."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "fastapi 0.104.1\nuvicorn 0.24.0"
        mock_run.return_value = mock_result

        output = self.manager.show_dependencies()
        assert "fastapi" in output
        assert "uvicorn" in output

    @patch("subprocess.run")
    def test_show_dependencies_failure(self, mock_run: Mock) -> None:
        """Test showing dependencies failure with Poetry."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "poetry", stderr="Show error"
        )
        with pytest.raises(BackendExceptions):
            self.manager.show_dependencies()

    @patch("subprocess.run")
    def test_show_dependencies_os_error(self, mock_run: Mock) -> None:
        """Test showing dependencies OS error with Poetry."""
        mock_run.side_effect = OSError("System error")
        with pytest.raises(BackendExceptions):
            self.manager.show_dependencies()


@pytest.mark.extended
class TestUvManagerExtended:
    """Extended coverage tests for UvManager."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = UvManager(self.temp_dir)

    def teardown_method(self) -> None:
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("subprocess.run")
    def test_create_virtual_environment_success(self, mock_run: Mock) -> None:
        """Test successful virtual environment creation with UV."""
        mock_run.return_value.returncode = 0
        venv_path = self.manager.create_virtual_environment()
        assert venv_path == str(Path(self.temp_dir) / ".venv")

    @patch("subprocess.run")
    def test_create_virtual_environment_failure(self, mock_run: Mock) -> None:
        """Test virtual environment creation failure with UV."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "uv", stderr="Error")
        with pytest.raises(BackendExceptions):
            self.manager.create_virtual_environment()

    @patch("subprocess.run")
    def test_create_virtual_environment_os_error(self, mock_run: Mock) -> None:
        """Test virtual environment creation OS error with UV."""
        mock_run.side_effect = OSError("System error")
        with pytest.raises(BackendExceptions):
            self.manager.create_virtual_environment()

    def test_install_dependencies_no_venv(self) -> None:
        """Test installing dependencies when venv doesn't exist."""
        with patch.object(
            self.manager, "create_virtual_environment"
        ) as mock_create_venv:
            mock_create_venv.return_value = None
            with pytest.raises(BackendExceptions):
                self.manager.install_dependencies("/nonexistent/venv")

    @patch("subprocess.run")
    def test_install_dependencies_no_pyproject(self, mock_run: Mock) -> None:
        """Test installing dependencies when pyproject.toml doesn't exist."""
        venv_path = str(Path(self.temp_dir) / ".venv")
        Path(venv_path).mkdir(parents=True)

        with pytest.raises(BackendExceptions) as exc_info:
            self.manager.install_dependencies(venv_path)
        assert "pyproject.toml file not found" in str(exc_info.value)

    @patch("subprocess.run")
    def test_install_dependencies_success(self, mock_run: Mock) -> None:
        """Test successful dependency installation with UV."""
        venv_path = str(Path(self.temp_dir) / ".venv")
        Path(venv_path).mkdir(parents=True)

        pyproject_file = Path(self.temp_dir) / "pyproject.toml"
        pyproject_file.write_text('[project]\nname = "test"\n')

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Installing dependencies..."
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        self.manager.install_dependencies(venv_path)
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_install_dependencies_failure(self, mock_run: Mock) -> None:
        """Test dependency installation failure with UV."""
        venv_path = str(Path(self.temp_dir) / ".venv")
        Path(venv_path).mkdir(parents=True)

        pyproject_file = Path(self.temp_dir) / "pyproject.toml"
        pyproject_file.write_text('[project]\nname = "test"\n')

        mock_run.side_effect = subprocess.CalledProcessError(
            1, "uv", stderr="Installation failed"
        )
        with pytest.raises(BackendExceptions):
            self.manager.install_dependencies(venv_path)

    @patch("subprocess.run")
    def test_install_dependencies_os_error(self, mock_run: Mock) -> None:
        """Test dependency installation OS error with UV."""
        venv_path = str(Path(self.temp_dir) / ".venv")
        Path(venv_path).mkdir(parents=True)

        pyproject_file = Path(self.temp_dir) / "pyproject.toml"
        pyproject_file.write_text('[project]\nname = "test"\n')

        mock_run.side_effect = OSError("System error")
        with pytest.raises(BackendExceptions):
            self.manager.install_dependencies(venv_path)

    def test_generate_dependency_file_with_metadata(self) -> None:
        """Test generating pyproject.toml with metadata for UV."""
        deps = ["fastapi", "uvicorn"]
        self.manager.generate_dependency_file(
            deps,
            project_name="test-project",
            author="Test Author",
            author_email="test@example.com",
            description="Test description",
        )

        pyproject_file = Path(self.temp_dir) / "pyproject.toml"
        assert pyproject_file.exists()
        content = pyproject_file.read_text()
        assert 'name = "test-project"' in content
        assert 'name = "Test Author"' in content
        assert 'email = "test@example.com"' in content
        assert 'description = "Test description"' in content
        assert "[tool.uv]" in content

    def test_generate_dependency_file_error(self) -> None:
        """Test pyproject.toml generation error with UV."""
        with patch("builtins.open", side_effect=OSError("Permission denied")):
            with pytest.raises(BackendExceptions):
                self.manager.generate_dependency_file(["fastapi"])

    @patch("subprocess.run")
    def test_add_dependency_success(self, mock_run: Mock) -> None:
        """Test successful dependency addition with UV."""
        mock_run.return_value.returncode = 0
        self.manager.add_dependency("fastapi")
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_add_dependency_dev(self, mock_run: Mock) -> None:
        """Test adding dev dependency with UV."""
        mock_run.return_value.returncode = 0
        self.manager.add_dependency("pytest", dev=True)
        args = mock_run.call_args[0][0]
        assert "--dev" in args

    @patch("subprocess.run")
    def test_add_dependency_failure(self, mock_run: Mock) -> None:
        """Test dependency addition failure with UV."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "uv", stderr="Error")
        with pytest.raises(BackendExceptions):
            self.manager.add_dependency("fastapi")

    @patch("subprocess.run")
    def test_add_dependency_os_error(self, mock_run: Mock) -> None:
        """Test dependency addition OS error with UV."""
        mock_run.side_effect = OSError("System error")
        with pytest.raises(BackendExceptions):
            self.manager.add_dependency("fastapi")

    @patch("subprocess.run")
    def test_initialize_project_success(self, mock_run: Mock) -> None:
        """Test successful project initialization with UV."""
        mock_run.return_value.returncode = 0
        self.manager.initialize_project(
            "test-project", "Author", "author@example.com", "Description"
        )

        pyproject_file = Path(self.temp_dir) / "pyproject.toml"
        assert pyproject_file.exists()

    @patch("subprocess.run")
    def test_initialize_project_subprocess_error(self, mock_run: Mock) -> None:
        """Test project initialization subprocess error with UV."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "uv", stderr="Error")
        with pytest.raises(BackendExceptions):
            self.manager.initialize_project(
                "test-project", "Author", "author@example.com", "Description"
            )

    @patch("subprocess.run")
    def test_initialize_project_os_error(self, mock_run: Mock) -> None:
        """Test project initialization OS error with UV."""
        mock_run.return_value.returncode = 0
        with patch("builtins.open", side_effect=OSError("Permission denied")):
            with pytest.raises(BackendExceptions):
                self.manager.initialize_project(
                    "test-project", "Author", "author@example.com", "Description"
                )

    @patch("subprocess.run")
    def test_lock_dependencies_success(self, mock_run: Mock) -> None:
        """Test successful lock file generation with UV."""
        mock_run.return_value.returncode = 0
        self.manager.lock_dependencies()
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_lock_dependencies_failure(self, mock_run: Mock) -> None:
        """Test lock file generation failure with UV."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "uv", stderr="Lock error"
        )
        with pytest.raises(BackendExceptions):
            self.manager.lock_dependencies()

    @patch("subprocess.run")
    def test_lock_dependencies_os_error(self, mock_run: Mock) -> None:
        """Test lock file generation OS error with UV."""
        mock_run.side_effect = OSError("System error")
        with pytest.raises(BackendExceptions):
            self.manager.lock_dependencies()

    @patch("subprocess.run")
    def test_run_script_success(self, mock_run: Mock) -> None:
        """Test successful script execution with UV."""
        mock_run.return_value.returncode = 0
        self.manager.run_script("python test.py")
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_run_script_failure(self, mock_run: Mock) -> None:
        """Test script execution failure with UV."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "uv", stderr="Script error"
        )
        with pytest.raises(BackendExceptions):
            self.manager.run_script("python test.py")

    @patch("subprocess.run")
    def test_run_script_os_error(self, mock_run: Mock) -> None:
        """Test script execution OS error with UV."""
        mock_run.side_effect = OSError("System error")
        with pytest.raises(BackendExceptions):
            self.manager.run_script("python test.py")
