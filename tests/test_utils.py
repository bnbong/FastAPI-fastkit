# --------------------------------------------------------------------------
# Testcases of utils modules.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from pathlib import Path
from unittest.mock import MagicMock, patch

from fastapi_fastkit.core.settings import FastkitConfig
from fastapi_fastkit.utils.logging import setup_logging
from fastapi_fastkit.utils.main import (
    handle_exception,
    print_error,
    print_info,
    print_success,
    print_warning,
)


class TestUtilsMain:
    """Test cases for utils/main.py functions."""

    def test_handle_exception(self) -> None:
        """Test handle_exception function."""
        # given
        test_exception = ValueError("Test error")
        error_message = "Test error occurred"

        # when & then
        with patch("fastapi_fastkit.utils.main.print_error") as mock_print_error:
            handle_exception(test_exception, error_message)
            mock_print_error.assert_called_once()

    def test_print_functions(self) -> None:
        """Test print utility functions."""
        # given
        test_message = "Test message"

        # when & then
        with patch("fastapi_fastkit.utils.main.console.print") as mock_console_print:
            print_error(test_message)
            print_info(test_message)
            print_success(test_message)
            print_warning(test_message)

            # Should have been called 4 times
            assert mock_console_print.call_count == 4

    def test_print_error_formatting(self) -> None:
        """Test print_error formatting."""
        # given
        error_message = "Critical error occurred"

        # when
        with patch("fastapi_fastkit.utils.main.console.print") as mock_console_print:
            print_error(error_message)

            # then
            mock_console_print.assert_called_once()
            # Check that a Panel object was passed
            args, kwargs = mock_console_print.call_args
            assert len(args) > 0

    def test_print_success_formatting(self) -> None:
        """Test print_success formatting."""
        # given
        success_message = "Operation completed successfully"

        # when
        with patch("fastapi_fastkit.utils.main.console.print") as mock_console_print:
            print_success(success_message)

            # then
            mock_console_print.assert_called_once()
            # Check that a Panel object was passed
            args, kwargs = mock_console_print.call_args
            assert len(args) > 0

    def test_print_warning_formatting(self) -> None:
        """Test print_warning formatting."""
        # given
        warning_message = "This is a warning"

        # when
        with patch("fastapi_fastkit.utils.main.console.print") as mock_console_print:
            print_warning(warning_message)

            # then
            mock_console_print.assert_called_once()
            # Check that a Panel object was passed
            args, kwargs = mock_console_print.call_args
            assert len(args) > 0

    def test_print_info_formatting(self) -> None:
        """Test print_info formatting."""
        # given
        info_message = "Information message"

        # when
        with patch("fastapi_fastkit.utils.main.console.print") as mock_console_print:
            print_info(info_message)

            # then
            mock_console_print.assert_called_once()
            # Check that a Panel object was passed
            args, kwargs = mock_console_print.call_args
            assert len(args) > 0


class TestUtilsLogging:
    """Test cases for utils/logging.py functions."""

    def test_setup_logging(self) -> None:
        """Test setup_logging function."""
        # given
        test_config = FastkitConfig()
        test_config.LOGGING_LEVEL = "INFO"

        # when
        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            setup_logging(test_config)

            # then
            mock_get_logger.assert_called_once_with("fastapi-fastkit")
            mock_logger.setLevel.assert_called_once_with("INFO")

    def test_setup_logging_with_terminal_width(self) -> None:
        """Test setup_logging with custom terminal width."""
        # given
        test_config = FastkitConfig()
        test_config.LOGGING_LEVEL = "DEBUG"
        terminal_width = 120

        # when
        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            setup_logging(test_config, terminal_width)

            # then
            # Just check that logging was configured
            mock_get_logger.assert_called()
            mock_logger.setLevel.assert_called_once_with("DEBUG")

    def test_is_fastkit_project_function_with_setup_py(self, temp_dir: str) -> None:
        """Test is_fastkit_project function with setup.py containing fastkit metadata."""
        # given
        from fastapi_fastkit.utils.main import is_fastkit_project

        project_path = Path(temp_dir) / "fastkit-project"
        project_path.mkdir()
        setup_py = project_path / "setup.py"
        setup_py.write_text("""
from setuptools import setup
setup(
    name="test-project",
    description="Created with FastAPI-fastkit"
)
""")

        # when & then
        assert is_fastkit_project(str(project_path)) is True

    def test_is_fastkit_project_function_invalid_path(self) -> None:
        """Test is_fastkit_project function with invalid path."""
        # given
        from fastapi_fastkit.utils.main import is_fastkit_project

        nonexistent_path = "/nonexistent/path"

        # when & then
        assert is_fastkit_project(nonexistent_path) is False

    def test_is_fastkit_project_pyproject_tool_section(self, temp_dir: str) -> None:
        """Pyproject with [tool.fastapi-fastkit].managed = true is detected."""
        from fastapi_fastkit.utils.main import is_fastkit_project

        project_path = Path(temp_dir) / "pyproject-tool-project"
        project_path.mkdir()
        (project_path / "pyproject.toml").write_text(
            '[project]\nname = "demo"\nversion = "0.1.0"\n'
            'description = "an unrelated description"\n\n'
            "[tool.fastapi-fastkit]\nmanaged = true\n"
        )

        assert is_fastkit_project(str(project_path)) is True

    def test_is_fastkit_project_pyproject_description_marker_only(
        self, temp_dir: str
    ) -> None:
        """Pyproject with only the description marker (no tool section) is detected."""
        from fastapi_fastkit.utils.main import is_fastkit_project

        project_path = Path(temp_dir) / "pyproject-desc-project"
        project_path.mkdir()
        # Lowercase marker confirms case-insensitive matching.
        (project_path / "pyproject.toml").write_text(
            '[project]\nname = "demo"\nversion = "0.1.0"\n'
            'description = "[fastapi-fastkit templated] demo"\n'
        )

        assert is_fastkit_project(str(project_path)) is True

    def test_is_fastkit_project_legacy_setup_py_only(self, temp_dir: str) -> None:
        """Project with only a legacy setup.py marker is still detected."""
        from fastapi_fastkit.utils.main import is_fastkit_project

        project_path = Path(temp_dir) / "legacy-setup-project"
        project_path.mkdir()
        # Mixed-case marker exercises case-insensitive setup.py scan.
        (project_path / "setup.py").write_text(
            "from setuptools import setup\n"
            'setup(name="legacy", description="[FASTAPI-FASTKIT templated] legacy")\n'
        )

        assert is_fastkit_project(str(project_path)) is True

    def test_is_fastkit_project_unrelated_fastapi_project(self, temp_dir: str) -> None:
        """An unrelated FastAPI project with neither marker is NOT detected."""
        from fastapi_fastkit.utils.main import is_fastkit_project

        project_path = Path(temp_dir) / "unrelated-fastapi"
        project_path.mkdir()
        (project_path / "pyproject.toml").write_text(
            '[project]\nname = "unrelated"\nversion = "0.1.0"\n'
            'description = "A regular FastAPI app"\n'
            'dependencies = ["fastapi>=0.115"]\n'
        )

        assert is_fastkit_project(str(project_path)) is False

    def test_is_fastkit_project_pyproject_precedence_over_setup_py(
        self, temp_dir: str
    ) -> None:
        """Pyproject marker alone is sufficient even without a setup.py."""
        from fastapi_fastkit.utils.main import is_fastkit_project

        project_path = Path(temp_dir) / "pyproject-only-detection"
        project_path.mkdir()
        (project_path / "pyproject.toml").write_text(
            '[project]\nname = "demo"\nversion = "0.1.0"\n'
            'description = "demo"\n\n'
            "[tool.fastapi-fastkit]\nmanaged = true\n"
        )

        assert is_fastkit_project(str(project_path)) is True

    def test_is_fastkit_project_malformed_pyproject_falls_back(
        self, temp_dir: str
    ) -> None:
        """A malformed pyproject still detects the marker via plain-text scan."""
        from fastapi_fastkit.utils.main import is_fastkit_project

        project_path = Path(temp_dir) / "broken-pyproject"
        project_path.mkdir()
        # Invalid TOML (unterminated string) but the marker text is present.
        (project_path / "pyproject.toml").write_text(
            '[project\nname = "broken\n'
            'description = "[FastAPI-fastkit templated] broken"\n'
        )

        assert is_fastkit_project(str(project_path)) is True

    def test_is_fastkit_project_malformed_pyproject_tool_section_text(
        self, temp_dir: str
    ) -> None:
        """Malformed pyproject with a [tool.fastapi-fastkit] header is still detected."""
        from fastapi_fastkit.utils.main import is_fastkit_project

        project_path = Path(temp_dir) / "broken-with-tool"
        project_path.mkdir()
        # Unterminated string makes tomllib fail, but the text-fallback spots
        # the [tool.fastapi-fastkit] header.
        (project_path / "pyproject.toml").write_text(
            '[project\nname = "broken\n\n[tool.fastapi-fastkit]\nmanaged = true\n'
        )

        assert is_fastkit_project(str(project_path)) is True

    def test_is_fastkit_project_malformed_pyproject_no_markers(
        self, temp_dir: str
    ) -> None:
        """Malformed pyproject with neither marker falls through to False."""
        from fastapi_fastkit.utils.main import is_fastkit_project

        project_path = Path(temp_dir) / "broken-unmarked"
        project_path.mkdir()
        (project_path / "pyproject.toml").write_text(
            '[project\nname = "broken\ndescription = "nothing here"\n'
        )

        assert is_fastkit_project(str(project_path)) is False

    def test_is_fastkit_project_setup_py_read_error(self, temp_dir: str) -> None:
        """OSError while reading setup.py does not crash detection; returns False."""
        from fastapi_fastkit.utils.main import is_fastkit_project

        project_path = Path(temp_dir) / "setup-read-err"
        project_path.mkdir()
        (project_path / "setup.py").write_text(
            'from setuptools import setup\nsetup(name="demo")\n'
        )

        with patch("builtins.open", side_effect=OSError("Permission denied")):
            assert is_fastkit_project(str(project_path)) is False

    def test_pyproject_text_marks_fastkit_read_error(self, temp_dir: str) -> None:
        """Text fallback swallows OSError and returns False cleanly."""
        from fastapi_fastkit.utils.main import _pyproject_text_marks_fastkit

        project_path = Path(temp_dir) / "text-fallback-err"
        project_path.mkdir()
        pyproject = project_path / "pyproject.toml"
        pyproject.write_text("whatever")

        with patch("builtins.open", side_effect=OSError("Permission denied")):
            assert _pyproject_text_marks_fastkit(str(pyproject)) is False

    def test_print_error_with_traceback(self) -> None:
        """Test print_error function with traceback enabled."""
        # given
        import io

        from rich.console import Console

        from fastapi_fastkit.core.settings import settings
        from fastapi_fastkit.utils.main import print_error

        # Setup console to capture output
        string_io = io.StringIO()
        test_console = Console(file=string_io, force_terminal=True, width=80)
        original_debug = settings.DEBUG_MODE

        try:
            settings.set_debug_mode(True)

            # when
            print_error("Test error message", console=test_console, show_traceback=True)

            # then
            output = string_io.getvalue()
            assert "Test error message" in output

        finally:
            settings.set_debug_mode(original_debug)

    def test_print_success_function(self) -> None:
        """Test print_success function."""
        # given
        import io

        from rich.console import Console

        from fastapi_fastkit.utils.main import print_success

        # Setup console to capture output
        string_io = io.StringIO()
        test_console = Console(file=string_io, force_terminal=True, width=80)

        # when
        print_success("Test success message", console=test_console)

        # then
        output = string_io.getvalue()
        assert "Test success message" in output

    def test_print_warning_function(self) -> None:
        """Test print_warning function."""
        # given
        import io

        from rich.console import Console

        from fastapi_fastkit.utils.main import print_warning

        # Setup console to capture output
        string_io = io.StringIO()
        test_console = Console(file=string_io, force_terminal=True, width=80)

        # when
        print_warning("Test warning message", console=test_console)

        # then
        output = string_io.getvalue()
        assert "Test warning message" in output

    def test_print_info_function(self) -> None:
        """Test print_info function."""
        # given
        import io

        from rich.console import Console

        from fastapi_fastkit.utils.main import print_info

        # Setup console to capture output
        string_io = io.StringIO()
        test_console = Console(file=string_io, force_terminal=True, width=80)

        # when
        print_info("Test info message", console=test_console)

        # then
        output = string_io.getvalue()
        assert "Test info message" in output

    def test_handle_exception_function(self) -> None:
        """Test handle_exception function."""
        # given
        from fastapi_fastkit.utils.main import handle_exception

        # when & then
        # Should not raise exception
        handle_exception(ValueError("Test exception"), "Custom error message")

    def test_handle_exception_function_no_message(self) -> None:
        """Test handle_exception function without custom message."""
        # given
        from fastapi_fastkit.utils.main import handle_exception

        # when & then
        # Should not raise exception
        handle_exception(ValueError("Test exception"))

    def test_create_info_table_function(self) -> None:
        """Test create_info_table function."""
        # given
        from fastapi_fastkit.utils.main import create_info_table

        # when
        table = create_info_table(
            "Test Information",
            {
                "Key 1": "Value 1",
                "Key 2": "Value 2",
            },
        )

        # then
        assert table.title == "Test Information"

    def test_create_info_table_function_empty_data(self) -> None:
        """Test create_info_table function with empty data."""
        # given
        from fastapi_fastkit.utils.main import create_info_table

        # when
        table = create_info_table("Empty Table", {})

        # then
        assert table.title == "Empty Table"
