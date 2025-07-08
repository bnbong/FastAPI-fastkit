# --------------------------------------------------------------------------
# Testcases of inspector module.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

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
