# --------------------------------------------------------------------------
# Testcases of inspector module.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from fastapi_fastkit.backend.inspector import (
    TemplateInspector,
    inspect_fastapi_template,
)


class TestTemplateInspector:
    """Test cases for TemplateInspector class."""

    def setup_method(self) -> None:
        """Setup method for each test."""
        self.temp_template_dir = tempfile.mkdtemp()
        self.template_path = Path(self.temp_template_dir)

    def teardown_method(self) -> None:
        """Cleanup method for each test."""
        # Clean up temp directories
        import shutil

        if os.path.exists(self.temp_template_dir):
            shutil.rmtree(self.temp_template_dir)

    def create_valid_template_structure(self) -> None:
        """Create a valid template structure for testing."""
        # Create required directories
        (self.template_path / "tests").mkdir(exist_ok=True)
        (self.template_path / "src").mkdir(exist_ok=True)

        # Create required files
        (self.template_path / "requirements.txt-tpl").write_text(
            "fastapi==0.104.1\nuvicorn==0.24.0"
        )
        (self.template_path / "setup.py-tpl").write_text(
            "from setuptools import setup\nsetup(name='test')"
        )
        (self.template_path / "README.md-tpl").write_text("# Test Template")

        # Create main.py-tpl with FastAPI app
        main_content = """
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
"""
        (self.template_path / "src" / "main.py-tpl").write_text(main_content)

        # Create test file
        test_content = """
def test_example():
    assert True
"""
        (self.template_path / "tests" / "test_example.py-tpl").write_text(test_content)

    def test_init(self) -> None:
        """Test TemplateInspector initialization."""
        # given
        self.create_valid_template_structure()

        # when
        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

        # then
        assert inspector.template_path == self.template_path
        assert inspector.errors == []
        assert inspector.warnings == []
        assert inspector.temp_dir.endswith("temp")

    def test_check_file_structure_valid(self) -> None:
        """Test _check_file_structure with valid structure."""
        # given
        self.create_valid_template_structure()

        # when
        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))
            result = inspector._check_file_structure()

        # then
        assert result is True
        assert inspector.errors == []

    def test_check_file_structure_missing_files(self) -> None:
        """Test _check_file_structure with missing files."""
        # given
        # Don't create the required structure

        # when
        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))
            result = inspector._check_file_structure()

        # then
        assert result is False
        assert len(inspector.errors) > 0
        assert any("Missing required path:" in error for error in inspector.errors)

    def test_check_file_extensions_valid(self) -> None:
        """Test _check_file_extensions with valid extensions."""
        # given
        self.create_valid_template_structure()

        # when
        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))
            result = inspector._check_file_extensions()

        # then
        assert result is True
        assert inspector.errors == []

    def test_check_file_extensions_invalid(self) -> None:
        """Test _check_file_extensions with invalid .py files."""
        # given
        self.create_valid_template_structure()
        # Create an invalid .py file (should be .py-tpl)
        (self.template_path / "invalid.py").write_text("# Invalid file")

        # when
        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))
            result = inspector._check_file_extensions()

        # then
        assert result is False
        assert len(inspector.errors) > 0
        assert any(
            "Found .py file instead of .py-tpl:" in error for error in inspector.errors
        )

    def test_check_dependencies_valid(self) -> None:
        """Test _check_dependencies with valid dependencies."""
        # given
        self.create_valid_template_structure()

        # when
        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))
            result = inspector._check_dependencies()

        # then
        assert result is True
        assert inspector.errors == []

    def test_check_dependencies_missing_fastapi(self) -> None:
        """Test _check_dependencies without FastAPI dependency."""
        # given
        (self.template_path / "tests").mkdir(exist_ok=True)
        (self.template_path / "requirements.txt-tpl").write_text("uvicorn==0.24.0")
        (self.template_path / "setup.py-tpl").write_text("from setuptools import setup")
        (self.template_path / "README.md-tpl").write_text("# Test")

        # when
        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))
            result = inspector._check_dependencies()

        # then
        assert result is False
        assert any(
            "FastAPI dependency not found" in error for error in inspector.errors
        )

    @patch("fastapi_fastkit.backend.inspector.find_template_core_modules")
    def test_check_fastapi_implementation_valid(
        self, mock_find_modules: MagicMock
    ) -> None:
        """Test _check_fastapi_implementation with valid FastAPI implementation."""
        # given
        self.create_valid_template_structure()
        mock_find_modules.return_value = {
            "main": str(self.template_path / "src" / "main.py")
        }

        # Create main.py with FastAPI content
        main_py = self.template_path / "src" / "main.py"
        main_py.write_text("from fastapi import FastAPI\napp = FastAPI()")

        # when
        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))
            result = inspector._check_fastapi_implementation()

        # then
        assert result is True
        assert inspector.errors == []

    @patch("fastapi_fastkit.backend.inspector.find_template_core_modules")
    def test_check_fastapi_implementation_no_main(
        self, mock_find_modules: MagicMock
    ) -> None:
        """Test _check_fastapi_implementation without main.py."""
        # given
        mock_find_modules.return_value = {"main": None}

        # when
        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))
            result = inspector._check_fastapi_implementation()

        # then
        assert result is False
        assert any("main.py not found" in error for error in inspector.errors)

    @patch("fastapi_fastkit.backend.inspector.create_venv")
    @patch("fastapi_fastkit.backend.inspector.install_dependencies")
    @patch("subprocess.run")
    def test_test_template_success(
        self,
        mock_subprocess: MagicMock,
        mock_install: MagicMock,
        mock_create_venv: MagicMock,
    ) -> None:
        """Test _test_template with successful tests."""
        # given
        self.create_valid_template_structure()
        mock_create_venv.return_value = "/fake/venv"
        mock_subprocess.return_value.returncode = 0

        # when
        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))
            # Create tests directory in temp_dir
            os.makedirs(os.path.join(inspector.temp_dir, "tests"), exist_ok=True)
            result = inspector._test_template()

        # then
        assert result is True
        assert inspector.errors == []

    def test_inspect_template_function(self) -> None:
        """Test the inspect_template function."""
        # given
        self.create_valid_template_structure()

        # when
        with patch.object(TemplateInspector, "inspect_template", return_value=True):
            with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
                result = inspect_fastapi_template(str(self.template_path))

        # then
        assert "is_valid" in result
        assert "errors" in result
        assert "warnings" in result

    def test_context_manager_enter_exit(self) -> None:
        """Test context manager enter and exit functionality."""
        # given
        self.create_valid_template_structure()

        # when & then
        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            with TemplateInspector(str(self.template_path)) as inspector:
                # Should be properly initialized
                assert inspector.template_path == self.template_path
                assert inspector._cleanup_needed is True
                assert os.path.exists(inspector.temp_dir)

        # After exiting, cleanup should have been called
        # Note: In test environment, temp_dir might still exist due to mocking

    def test_context_manager_exception_handling(self) -> None:
        """Test context manager cleanup on exception."""
        # given
        self.create_valid_template_structure()

        # Mock os.makedirs to raise an exception
        with patch("os.makedirs", side_effect=OSError("Permission denied")):
            # when & then
            with pytest.raises(OSError, match="Permission denied"):
                with TemplateInspector(str(self.template_path)) as inspector:
                    pass  # Exception should be raised during __enter__

    def test_cleanup_method(self) -> None:
        """Test _cleanup method functionality."""
        # given
        self.create_valid_template_structure()

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))
            # Simulate entering context
            inspector._cleanup_needed = True

            # Create mock temp directory
            import tempfile

            mock_temp_dir = tempfile.mkdtemp()
            inspector.temp_dir = mock_temp_dir

        # when
        inspector._cleanup()

        # then
        assert inspector._cleanup_needed is False
        assert not os.path.exists(mock_temp_dir)

    def test_cleanup_method_no_cleanup_needed(self) -> None:
        """Test _cleanup method when cleanup is not needed."""
        # given
        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))
            inspector._cleanup_needed = False

            import tempfile

            mock_temp_dir = tempfile.mkdtemp()
            inspector.temp_dir = mock_temp_dir

        # when
        inspector._cleanup()

        # then
        # Directory should still exist since cleanup wasn't needed
        assert os.path.exists(mock_temp_dir)

        # Manual cleanup for test
        import shutil

        shutil.rmtree(mock_temp_dir)

    def test_cleanup_method_permission_error(self) -> None:
        """Test _cleanup method handling permission errors."""
        # given
        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))
            inspector._cleanup_needed = True
            # Create an actual temp directory first
            import tempfile

            mock_temp_dir = tempfile.mkdtemp()
            inspector.temp_dir = mock_temp_dir

        # Mock shutil.rmtree to raise OSError
        with patch("shutil.rmtree", side_effect=OSError("Permission denied")):
            # when & then (should not raise exception)
            inspector._cleanup()

        # Cleanup should still set _cleanup_needed to False even on error
        assert inspector._cleanup_needed is False

    def test_get_report_method(self) -> None:
        """Test get_report method functionality."""
        # given
        self.create_valid_template_structure()

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

            # Add some test data
            inspector.errors = ["Error 1", "Error 2"]
            inspector.warnings = ["Warning 1"]

        # when
        report = inspector.get_report()

        # then
        assert report["template_path"] == str(self.template_path)
        assert report["errors"] == ["Error 1", "Error 2"]
        assert report["warnings"] == ["Warning 1"]
        assert report["is_valid"] is False  # Should be False due to errors

    def test_get_report_method_valid_template(self) -> None:
        """Test get_report method with valid template (no errors)."""
        # given
        self.create_valid_template_structure()

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

            # No errors or warnings
            inspector.errors = []
            inspector.warnings = []

        # when
        report = inspector.get_report()

        # then
        assert report["template_path"] == str(self.template_path)
        assert report["errors"] == []
        assert report["warnings"] == []
        assert report["is_valid"] is True  # Should be True with no errors

    def test_inspect_template_with_all_checks_passing(self) -> None:
        """Test inspect_template method with all checks passing."""
        # given
        self.create_valid_template_structure()

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

        # Mock all check methods to return True
        with (
            patch.object(inspector, "_check_file_structure", return_value=True),
            patch.object(inspector, "_check_file_extensions", return_value=True),
            patch.object(inspector, "_check_dependencies", return_value=True),
            patch.object(inspector, "_check_fastapi_implementation", return_value=True),
            patch.object(inspector, "_test_template", return_value=True),
        ):

            # when
            result = inspector.inspect_template()

            # then
            assert result is True

    def test_inspect_template_with_failing_check(self) -> None:
        """Test inspect_template method with one check failing."""
        # given
        self.create_valid_template_structure()

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

        # Mock one check to fail
        with (
            patch.object(inspector, "_check_file_structure", return_value=False),
            patch.object(inspector, "_check_file_extensions", return_value=True),
            patch.object(inspector, "_check_dependencies", return_value=True),
            patch.object(inspector, "_check_fastapi_implementation", return_value=True),
            patch.object(inspector, "_test_template", return_value=True),
        ):

            # when
            result = inspector.inspect_template()

            # then
            assert result is False

    def test_check_dependencies_missing_requirements_file(self) -> None:
        """Test _check_dependencies when requirements.txt-tpl is missing."""
        # given
        # Create structure without requirements.txt-tpl
        (self.template_path / "tests").mkdir(exist_ok=True)
        (self.template_path / "setup.py-tpl").write_text("from setuptools import setup")
        (self.template_path / "README.md-tpl").write_text("# Test")

        # when
        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))
            result = inspector._check_dependencies()

        # then
        assert result is False
        assert any(
            "requirements.txt-tpl not found" in error for error in inspector.errors
        )

    def test_check_dependencies_missing_setup_file(self) -> None:
        """Test _check_dependencies when setup.py-tpl is missing."""
        # given
        # Create structure without setup.py-tpl
        (self.template_path / "tests").mkdir(exist_ok=True)
        (self.template_path / "requirements.txt-tpl").write_text("fastapi==0.104.1")
        (self.template_path / "README.md-tpl").write_text("# Test")

        # when
        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))
            result = inspector._check_dependencies()

        # then
        assert result is False
        assert any("setup.py-tpl not found" in error for error in inspector.errors)

    def test_check_dependencies_file_read_error(self) -> None:
        """Test _check_dependencies with file read error."""
        # given
        self.create_valid_template_structure()

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

        # Mock open to raise an exception
        with patch("builtins.open", side_effect=OSError("Permission denied")):
            # when
            result = inspector._check_dependencies()

            # then
            assert result is False
            assert any(
                "Error reading requirements.txt-tpl" in error
                for error in inspector.errors
            )

    # ===== NEW TESTS FOR ADDED FEATURES =====

    def test_load_template_config_no_file(self) -> None:
        """Test _load_template_config when template-config.yml doesn't exist."""
        # given
        self.create_valid_template_structure()

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

        # when
        config = inspector._load_template_config()

        # then
        assert config is None

    def test_load_template_config_valid_file(self) -> None:
        """Test _load_template_config with valid template-config.yml."""
        # given
        self.create_valid_template_structure()
        config_content = """
name: fastapi-psql-orm
description: FastAPI template with PostgreSQL
testing:
  strategy: docker
  compose_file: docker-compose.yml
  health_check_timeout: 180
fallback_testing:
  strategy: sqlite
  env_vars:
    DATABASE_URL: sqlite:///./test.db
"""
        (self.template_path / "template-config.yml-tpl").write_text(config_content)

        with patch(
            "fastapi_fastkit.backend.transducer.copy_and_convert_template"
        ) as mock_copy:
            # Mock that config file exists in temp dir
            temp_config_path = os.path.join("temp_dir", "template-config.yml")
            mock_copy.return_value = None

            inspector = TemplateInspector(str(self.template_path))

            # Mock the temp dir to have the config file
            with (
                patch("os.path.exists", return_value=True),
                patch("builtins.open", mock_open(read_data=config_content)),
            ):
                # when
                config = inspector._load_template_config()

        # then
        assert config is not None
        assert config["name"] == "fastapi-psql-orm"
        assert config["testing"]["strategy"] == "docker"

    def test_load_template_config_invalid_yaml(self) -> None:
        """Test _load_template_config with invalid YAML."""
        # given
        self.create_valid_template_structure()

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

            with (
                patch("os.path.exists", return_value=True),
                patch(
                    "builtins.open", mock_open(read_data="invalid: yaml: content: [")
                ),
            ):
                # when
                config = inspector._load_template_config()

        # then
        assert config is None

    def test_check_docker_available_success(self) -> None:
        """Test _check_docker_available when Docker is available."""
        # given
        self.create_valid_template_structure()

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

        # Mock subprocess.run for Docker commands
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                MagicMock(
                    returncode=0, stdout="Docker version 20.10.0"
                ),  # docker --version
                MagicMock(
                    returncode=0, stdout="Docker Compose version 2.0.0"
                ),  # docker-compose --version
            ]

            # when
            result = inspector._check_docker_available()

        # then
        assert result is True

    def test_check_docker_available_docker_not_found(self) -> None:
        """Test _check_docker_available when Docker is not installed."""
        # given
        self.create_valid_template_structure()

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

        # Mock subprocess.run to raise FileNotFoundError
        with patch("subprocess.run", side_effect=FileNotFoundError()):
            # when
            result = inspector._check_docker_available()

        # then
        assert result is False

    def test_check_docker_available_docker_compose_not_found(self) -> None:
        """Test _check_docker_available when Docker is available but Docker Compose is not."""
        # given
        self.create_valid_template_structure()

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

        # Mock subprocess.run
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                MagicMock(
                    returncode=0, stdout="Docker version 20.10.0"
                ),  # docker --version
                MagicMock(
                    returncode=1, stderr="docker-compose: command not found"
                ),  # docker-compose --version
            ]

            # when
            result = inspector._check_docker_available()

        # then
        assert result is False

    def test_check_containers_running_no_containers(self) -> None:
        """Test _check_containers_running when no containers are running."""
        # given
        self.create_valid_template_structure()

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

        # Mock subprocess.run to return no containers
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="")

            # when
            result = inspector._check_containers_running("docker-compose.yml")

        # then
        assert result is False

    def test_check_containers_running_containers_exist(self) -> None:
        """Test _check_containers_running when containers are running."""
        # given
        self.create_valid_template_structure()

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

        # Mock subprocess.run
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                MagicMock(
                    returncode=0, stdout="container1\ncontainer2"
                ),  # docker-compose ps -q
                MagicMock(returncode=0, stdout="true"),  # docker inspect container1
                MagicMock(returncode=0, stdout="true"),  # docker inspect container2
            ]

            # when
            result = inspector._check_containers_running("docker-compose.yml")

        # then
        assert result is True

    def test_fix_script_line_endings(self) -> None:
        """Test _fix_script_line_endings method."""
        # given
        self.create_valid_template_structure()

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

        # Create a test script with Windows line endings
        test_script = self.template_path / "test_script.sh"
        test_script.write_bytes(b"#!/bin/bash\r\necho 'Hello'\r\necho 'World'\r\n")

        # when
        inspector._fix_script_line_endings(str(test_script))

        # then
        content = test_script.read_bytes()
        assert b"\r\n" not in content
        assert b"#!/bin/bash\necho 'Hello'\necho 'World'\n" == content

    def test_fix_all_script_line_endings(self) -> None:
        """Test _fix_all_script_line_endings method."""
        # given
        self.create_valid_template_structure()

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

        # Create test scripts with Windows line endings
        scripts_dir = self.template_path / "scripts"
        scripts_dir.mkdir(exist_ok=True)

        script1 = scripts_dir / "test1.sh"
        script2 = scripts_dir / "test2.bash"
        script1.write_bytes(b"#!/bin/bash\r\necho 'test1'\r\n")
        script2.write_bytes(b"#!/bin/bash\r\necho 'test2'\r\n")

        # Mock temp_dir to point to our test directory
        inspector.temp_dir = str(self.template_path)

        # when
        inspector._fix_all_script_line_endings()

        # then
        assert b"\r\n" not in script1.read_bytes()
        assert b"\r\n" not in script2.read_bytes()

    @patch("subprocess.run")
    def test_run_test_script_success(self, mock_run: MagicMock) -> None:
        """Test _run_test_script with successful execution."""
        # given
        self.create_valid_template_structure()

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

        # Create test script
        test_script = self.template_path / "test.sh"
        test_script.write_text("#!/bin/bash\necho 'test passed'\n")
        test_script.chmod(0o755)

        mock_run.return_value = MagicMock(returncode=0, stdout="test passed", stderr="")

        # when
        result = inspector._run_test_script(str(test_script), "/fake/venv")

        # then
        assert result.returncode == 0
        assert "test passed" in result.stdout

    @patch("subprocess.run")
    def test_run_test_script_with_env_success(self, mock_run: MagicMock) -> None:
        """Test _run_test_script_with_env with successful execution."""
        # given
        self.create_valid_template_structure()

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

        test_script = self.template_path / "test.sh"
        test_script.write_text("#!/bin/bash\necho $TEST_VAR\n")
        test_script.chmod(0o755)

        mock_run.return_value = MagicMock(returncode=0, stdout="test_value", stderr="")

        env_vars = {"TEST_VAR": "test_value"}

        # when
        result = inspector._run_test_script_with_env(
            str(test_script), "/fake/venv", env_vars
        )

        # then
        assert result.returncode == 0
        assert "test_value" in result.stdout

    def test_setup_test_environment(self) -> None:
        """Test _setup_test_environment method."""
        # given
        self.create_valid_template_structure()

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

        inspector.temp_dir = str(self.template_path)
        # Set template config with test environment defaults
        inspector.template_config = {
            "test_env_defaults": {
                "DATABASE_URL": "sqlite:///./test.db",
                "DEBUG": "true",
            }
        }

        # when
        inspector._setup_test_environment()

        # then
        env_file = self.template_path / ".env"
        assert env_file.exists()

        content = env_file.read_text()
        assert "DATABASE_URL=sqlite:///./test.db" in content
        assert "DEBUG=true" in content

    def test_setup_test_environment_existing_env_file(self) -> None:
        """Test _setup_test_environment with existing .env file."""
        # given
        self.create_valid_template_structure()

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

        inspector.temp_dir = str(self.template_path)

        # Create existing .env file
        env_file = self.template_path / ".env"
        env_file.write_text("EXISTING_VAR=existing_value\n")

        # Set template config with test environment defaults
        inspector.template_config = {
            "test_env_defaults": {"DATABASE_URL": "sqlite:///./test.db"}
        }

        # when
        inspector._setup_test_environment()

        # then
        content = env_file.read_text()
        assert "EXISTING_VAR=existing_value" in content
        assert "DATABASE_URL=sqlite:///./test.db" in content

    @patch("subprocess.run")
    def test_verify_services_running_success(self, mock_run: MagicMock) -> None:
        """Test _verify_services_running with all services running."""
        # given
        self.create_valid_template_structure()

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

        # Mock docker-compose ps output
        mock_services = [
            {"Name": "test_db_1", "State": "running"},
            {"Name": "test_app_1", "State": "running"},
        ]

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="\n".join([json.dumps(service) for service in mock_services]),
        )

        # when
        result = inspector._verify_services_running("docker-compose.yml")

        # then
        assert result is True

    @patch("subprocess.run")
    def test_verify_services_running_app_not_running(self, mock_run: MagicMock) -> None:
        """Test _verify_services_running when app service is not running."""
        # given
        self.create_valid_template_structure()

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

        # Mock docker-compose ps output with app not running
        mock_services = [
            {"Name": "test_db_1", "State": "running"},
            {"Name": "test_app_1", "State": "exited"},
        ]

        mock_run.side_effect = [
            MagicMock(
                returncode=0,
                stdout="\n".join([json.dumps(service) for service in mock_services]),
            ),
            MagicMock(
                returncode=0, stdout="App service logs..."
            ),  # docker-compose logs
        ]

        # when
        result = inspector._verify_services_running("docker-compose.yml")

        # then
        assert result is False

    @patch("subprocess.run")
    @patch("time.sleep")
    def test_wait_for_services_healthy_success(
        self, mock_sleep: MagicMock, mock_run: MagicMock
    ) -> None:
        """Test _wait_for_services_healthy with services becoming healthy."""
        # given
        self.create_valid_template_structure()

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

        # Mock first call returns not running, second call returns running
        mock_services_not_ready = [
            {"Name": "test_db_1", "State": "starting"},
            {"Name": "test_app_1", "State": "starting"},
        ]
        mock_services_ready = [
            {"Name": "test_db_1", "State": "running"},
            {"Name": "test_app_1", "State": "running"},
        ]

        mock_run.side_effect = [
            MagicMock(
                returncode=0,
                stdout="\n".join(
                    [json.dumps(service) for service in mock_services_not_ready]
                ),
            ),
            MagicMock(
                returncode=0,
                stdout="\n".join(
                    [json.dumps(service) for service in mock_services_ready]
                ),
            ),
        ]

        # when
        inspector._wait_for_services_healthy("docker-compose.yml", 30)

        # then
        assert mock_run.call_count == 2
        mock_sleep.assert_called()

    @patch("subprocess.run")
    def test_test_with_docker_strategy_no_docker(self, mock_run: MagicMock) -> None:
        """Test _test_with_docker_strategy when Docker is not available."""
        # given
        self.create_valid_template_structure()

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

        # Mock Docker not available
        with (
            patch.object(inspector, "_check_docker_available", return_value=False),
            patch.object(
                inspector, "_test_with_fallback_strategy", return_value=True
            ) as mock_fallback,
        ):

            # when
            result = inspector._test_with_docker_strategy()

            # then
            assert result is True
            mock_fallback.assert_called_once()

    @patch("subprocess.run")
    def test_test_with_fallback_strategy_success(self, mock_run: MagicMock) -> None:
        """Test _test_with_fallback_strategy with successful execution."""
        # given
        self.create_valid_template_structure()

        # Create template config with fallback testing
        config_content = {
            "fallback_testing": {
                "env_vars": {"DATABASE_URL": "sqlite:///./test.db"},
                "timeout": 180,
            }
        }

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

        inspector.template_config = config_content

        # Mock virtual environment and dependencies
        with (
            patch("fastapi_fastkit.backend.inspector.create_venv") as mock_create_venv,
            patch(
                "fastapi_fastkit.backend.inspector.install_dependencies"
            ) as mock_install,
            patch.object(inspector, "_run_test_script_with_env") as mock_run_script,
        ):

            mock_create_venv.return_value = "/fake/venv"
            mock_install.return_value = True
            mock_run_script.return_value = MagicMock(
                returncode=0, stdout="All tests passed"
            )

            # Create test script
            scripts_dir = self.template_path / "scripts"
            scripts_dir.mkdir(exist_ok=True)
            test_script = scripts_dir / "test.sh"
            test_script.write_text("#!/bin/bash\necho 'test passed'\n")

            inspector.temp_dir = str(self.template_path)

            # when
            result = inspector._test_with_fallback_strategy()

            # then
            assert result is True

    def test_test_with_fallback_strategy_no_config(self) -> None:
        """Test _test_with_fallback_strategy when no fallback config is available."""
        # given
        self.create_valid_template_structure()

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

        inspector.template_config = None

        # Mock standard strategy
        with patch.object(
            inspector, "_test_with_standard_strategy", return_value=True
        ) as mock_standard:
            # when
            result = inspector._test_with_fallback_strategy()

            # then
            assert result is True
            mock_standard.assert_called_once()

    # ===== ADDITIONAL TESTS FOR BETTER COVERAGE =====

    @patch("fastapi_fastkit.backend.inspector.create_venv")
    @patch("fastapi_fastkit.backend.inspector.install_dependencies")
    def test_test_with_standard_strategy_success(
        self, mock_install: MagicMock, mock_create_venv: MagicMock
    ) -> None:
        """Test _test_with_standard_strategy with successful execution."""
        # given
        self.create_valid_template_structure()

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

        # Create test script
        scripts_dir = self.template_path / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        test_script = scripts_dir / "test.sh"
        test_script.write_text("#!/bin/bash\necho 'test passed'\n")

        inspector.temp_dir = str(self.template_path)

        # Mock dependencies
        mock_create_venv.return_value = "/fake/venv"
        mock_install.return_value = True

        # Mock test script execution
        with patch.object(inspector, "_run_test_script") as mock_run_script:
            mock_run_script.return_value = MagicMock(
                returncode=0, stdout="All tests passed"
            )

            # when
            result = inspector._test_with_standard_strategy()

            # then
            assert result is True
            mock_create_venv.assert_called_once()
            mock_install.assert_called_once()
            mock_run_script.assert_called_once()

    @patch("fastapi_fastkit.backend.inspector.create_venv")
    @patch("fastapi_fastkit.backend.inspector.install_dependencies")
    def test_test_with_standard_strategy_no_test_script(
        self, mock_install: MagicMock, mock_create_venv: MagicMock
    ) -> None:
        """Test _test_with_standard_strategy when no test script exists."""
        # given
        self.create_valid_template_structure()

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

        inspector.temp_dir = str(self.template_path)

        # Mock dependencies
        mock_create_venv.return_value = "/fake/venv"
        mock_install.return_value = True

        # Mock pytest execution
        with patch.object(inspector, "_run_pytest_directly") as mock_pytest:
            mock_pytest.return_value = MagicMock(
                returncode=0, stdout="All tests passed"
            )

            # when
            result = inspector._test_with_standard_strategy()

            # then
            assert result is True
            mock_pytest.assert_called_once()

    @patch("fastapi_fastkit.backend.inspector.create_venv")
    def test_test_with_standard_strategy_venv_creation_failed(
        self, mock_create_venv: MagicMock
    ) -> None:
        """Test _test_with_standard_strategy when virtual environment creation fails."""
        # given
        self.create_valid_template_structure()

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

        # Mock venv creation failure
        mock_create_venv.return_value = None

        # when
        result = inspector._test_with_standard_strategy()

        # then
        assert result is False
        assert len(inspector.errors) > 0

    @patch("fastapi_fastkit.backend.inspector.create_venv")
    @patch("fastapi_fastkit.backend.inspector.install_dependencies")
    def test_test_with_standard_strategy_dependency_installation_failed(
        self, mock_install: MagicMock, mock_create_venv: MagicMock
    ) -> None:
        """Test _test_with_standard_strategy when dependency installation fails."""
        # given
        self.create_valid_template_structure()

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

        # Mock dependencies
        mock_create_venv.return_value = "/fake/venv"
        mock_install.return_value = False

        # when
        result = inspector._test_with_standard_strategy()

        # then
        assert result is False
        assert len(inspector.errors) > 0

    @patch("subprocess.run")
    def test_run_pytest_directly_success(self, mock_run: MagicMock) -> None:
        """Test _run_pytest_directly with successful execution."""
        # given
        self.create_valid_template_structure()

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

        mock_run.return_value = MagicMock(
            returncode=0, stdout="All tests passed", stderr=""
        )

        # when
        result = inspector._run_pytest_directly("/fake/venv")

        # then
        assert result.returncode == 0
        assert "All tests passed" in result.stdout

    def test_check_fastapi_implementation_no_fastapi_import(self) -> None:
        """Test _check_fastapi_implementation when FastAPI is not imported."""
        # given
        self.create_valid_template_structure()

        # Create main.py without FastAPI
        main_content = """
def hello():
    return "Hello World"
"""
        (self.template_path / "src" / "main.py").write_text(main_content)

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

        with patch(
            "fastapi_fastkit.backend.inspector.find_template_core_modules"
        ) as mock_find:
            mock_find.return_value = {
                "main": str(self.template_path / "src" / "main.py")
            }

            # when
            result = inspector._check_fastapi_implementation()

            # then
            assert result is False
            assert any(
                "FastAPI app creation not found" in error for error in inspector.errors
            )

    def test_check_fastapi_implementation_no_app_instance(self) -> None:
        """Test _check_fastapi_implementation when no FastAPI app instance is found."""
        # given
        self.create_valid_template_structure()

        # Create main.py with FastAPI import but without 'app' variable
        main_content = """
from fastapi import FastAPI

def create_fastapi():
    return FastAPI()
"""
        (self.template_path / "src" / "main.py").write_text(main_content)

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

        with patch(
            "fastapi_fastkit.backend.inspector.find_template_core_modules"
        ) as mock_find:
            mock_find.return_value = {
                "main": str(self.template_path / "src" / "main.py")
            }

            # when
            result = inspector._check_fastapi_implementation()

            # then
            assert result is False
            assert any(
                "FastAPI app creation not found" in error for error in inspector.errors
            )

    def test_check_fastapi_implementation_file_read_error(self) -> None:
        """Test _check_fastapi_implementation when file cannot be read."""
        # given
        self.create_valid_template_structure()

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

        with (
            patch(
                "fastapi_fastkit.backend.inspector.find_template_core_modules"
            ) as mock_find,
            patch("builtins.open", side_effect=OSError("Permission denied")),
        ):
            mock_find.return_value = {
                "main": str(self.template_path / "src" / "main.py")
            }

            # when
            result = inspector._check_fastapi_implementation()

            # then
            assert result is False
            assert any(
                "Error checking FastAPI implementation" in error
                for error in inspector.errors
            )

    def test_setup_test_environment_no_config(self) -> None:
        """Test _setup_test_environment when no template config exists."""
        # given
        self.create_valid_template_structure()

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

        inspector.temp_dir = str(self.template_path)
        inspector.template_config = None

        # when
        inspector._setup_test_environment()

        # then
        env_file = self.template_path / ".env"
        assert not env_file.exists()

    def test_setup_test_environment_env_file_read_error(self) -> None:
        """Test _setup_test_environment when existing .env file cannot be read."""
        # given
        self.create_valid_template_structure()

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

        inspector.temp_dir = str(self.template_path)
        inspector.template_config = {"test_env_defaults": {"TEST_VAR": "test_value"}}

        # Create existing .env file
        env_file = self.template_path / ".env"
        env_file.write_text("EXISTING_VAR=existing_value\n")

        # Mock file reading to raise exception for reading, but allow writing
        read_mock = mock_open()
        read_mock.side_effect = OSError("Permission denied")
        write_mock = mock_open()

        with patch("builtins.open") as mock_file:
            # First call (reading) raises exception, second call (writing) succeeds
            mock_file.side_effect = [
                OSError("Permission denied"),
                write_mock.return_value,
            ]

            # when
            inspector._setup_test_environment()

            # then
            # Should complete without crashing and write defaults
            assert mock_file.call_count == 2

    @patch("subprocess.run")
    def test_verify_services_running_command_failure(self, mock_run: MagicMock) -> None:
        """Test _verify_services_running when docker-compose command fails."""
        # given
        self.create_valid_template_structure()

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

        mock_run.return_value = MagicMock(
            returncode=1, stderr="Docker compose command failed"
        )

        # when
        result = inspector._verify_services_running("docker-compose.yml")

        # then
        assert result is False

    @patch("subprocess.run")
    def test_verify_services_running_invalid_json(self, mock_run: MagicMock) -> None:
        """Test _verify_services_running when docker-compose returns invalid JSON."""
        # given
        self.create_valid_template_structure()

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

        mock_run.return_value = MagicMock(returncode=0, stdout="invalid json output")

        # when
        result = inspector._verify_services_running("docker-compose.yml")

        # then
        assert result is False

    @patch("subprocess.run")
    def test_run_docker_exec_tests_success(self, mock_run: MagicMock) -> None:
        """Test _run_docker_exec_tests with successful execution."""
        # given
        self.create_valid_template_structure()

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

        # Create test script
        scripts_dir = self.template_path / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        test_script = scripts_dir / "test.sh"
        test_script.write_text("#!/bin/bash\necho 'test passed'\n")

        inspector.temp_dir = str(self.template_path)

        mock_run.return_value = MagicMock(
            returncode=0, stdout="All tests passed", stderr=""
        )

        # when
        result = inspector._run_docker_exec_tests("docker-compose.yml")

        # then
        assert result is True

    @patch("subprocess.run")
    def test_run_docker_exec_tests_failure(self, mock_run: MagicMock) -> None:
        """Test _run_docker_exec_tests when tests fail."""
        # given
        self.create_valid_template_structure()

        with patch("fastapi_fastkit.backend.transducer.copy_and_convert_template"):
            inspector = TemplateInspector(str(self.template_path))

        inspector.temp_dir = str(self.template_path)

        mock_run.return_value = MagicMock(
            returncode=1, stdout="", stderr="Tests failed"
        )

        # when
        result = inspector._run_docker_exec_tests("docker-compose.yml")

        # then
        assert result is False
