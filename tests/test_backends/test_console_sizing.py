# --------------------------------------------------------------------------
# Tests for console sizing functionality in FastAPI-fastkit CLI.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console

from fastapi_fastkit.utils.main import (
    create_adaptive_console,
    create_info_table,
    get_optimal_console_size,
    print_error,
    print_info,
    print_success,
    print_warning,
)


class TestConsoleSizing:
    """Test cases for console sizing functionality."""

    def test_get_optimal_console_size_normal_terminal(self) -> None:
        """Test optimal console size calculation with normal terminal dimensions."""
        with patch("os.get_terminal_size") as mock_get_size:
            # Mock terminal size: 100 columns, 30 lines
            mock_get_size.return_value = os.terminal_size((100, 30))

            width, height = get_optimal_console_size()

            # Width should be 80% of terminal width (80), but within constraints
            assert width == 80  # min(120, max(80, int(100 * 0.8)))
            # Height should be terminal height minus buffer (25)
            assert height == 25  # max(24, 30 - 5)

    def test_get_optimal_console_size_large_terminal(self) -> None:
        """Test optimal console size calculation with large terminal dimensions."""
        with patch("os.get_terminal_size") as mock_get_size:
            # Mock large terminal: 200 columns, 50 lines
            mock_get_size.return_value = os.terminal_size((200, 50))

            width, height = get_optimal_console_size()

            # Width should be capped at max_width (120)
            assert width == 120  # min(120, max(80, int(200 * 0.8)))
            # Height should be terminal height minus buffer (45)
            assert height == 45  # max(24, 50 - 5)

    def test_get_optimal_console_size_small_terminal(self) -> None:
        """Test optimal console size calculation with small terminal dimensions."""
        with patch("os.get_terminal_size") as mock_get_size:
            # Mock small terminal: 60 columns, 20 lines
            mock_get_size.return_value = os.terminal_size((60, 20))

            width, height = get_optimal_console_size()

            # Width should be minimum width (80)
            assert width == 80  # min(120, max(80, int(60 * 0.8)))
            # Height should be minimum height (24)
            assert height == 24  # max(24, 20 - 5)

    def test_get_optimal_console_size_fallback(self) -> None:
        """Test fallback behavior when terminal size detection fails."""
        with patch("os.get_terminal_size") as mock_get_size:
            # Mock OSError (terminal size detection failure)
            mock_get_size.side_effect = OSError("Terminal size not available")

            width, height = get_optimal_console_size()

            # Should fallback to default size
            assert width == 80
            assert height == 24

    def test_create_adaptive_console_normal(self) -> None:
        """Test adaptive console creation in normal environment."""
        with patch("os.get_terminal_size") as mock_get_size:
            mock_get_size.return_value = os.terminal_size((100, 30))

            console = create_adaptive_console()

            assert isinstance(console, Console)
            # Console should have adaptive sizing
            assert console.width == 80
            # Rich Console may use different height handling
            assert console.height >= 25 or console.height == 30

    def test_create_adaptive_console_pytest_env(self) -> None:
        """Test adaptive console creation in pytest environment."""
        with patch.dict(
            os.environ, {"PYTEST_CURRENT_TEST": "test_module::test_function"}
        ):
            console = create_adaptive_console()

            assert isinstance(console, Console)
            # Should create no_color console for testing
            assert console._color_system is None or console._force_terminal is False

    def test_create_info_table_adaptive_sizing(self) -> None:
        """Test that create_info_table uses adaptive sizing."""
        with patch("os.get_terminal_size") as mock_get_size:
            mock_get_size.return_value = os.terminal_size((100, 30))

            data = {
                "Project Name": "test-project",
                "Author": "Test Author",
                "Description": "A test project description",
            }

            table = create_info_table("Test Table", data)

            # Table should have columns with proper width settings
            assert len(table.columns) == 2
            assert (
                table.columns[0].width is not None and table.columns[0].width >= 14
            )  # Length of "Project Name" + 2
            assert (
                table.columns[1].width is not None and table.columns[1].width >= 27
            )  # Length of "A test project description" + 2

    def test_create_info_table_long_content(self) -> None:
        """Test table creation with long content that needs scaling."""
        with patch("os.get_terminal_size") as mock_get_size:
            mock_get_size.return_value = os.terminal_size((80, 30))  # Small terminal

            data = {
                "Very Long Project Name Field": "This is a very long project description that might exceed normal terminal width",
                "Another Long Field Name": "Another very long value that should be handled properly",
            }

            table = create_info_table("Test Table", data)

            # Table should have appropriate column widths based on content
            assert len(table.columns) == 2
            assert (
                table.columns[0].width is not None
                and table.columns[0].width >= len("Very Long Project Name Field") + 2
            )
            assert (
                table.columns[1].width is not None
                and table.columns[1].width
                >= len(
                    "This is a very long project description that might exceed normal terminal width"
                )
                + 2
            )

    @patch("fastapi_fastkit.utils.main.console")
    def test_print_functions_use_adaptive_sizing(self, mock_console: MagicMock) -> None:
        """Test that print functions use adaptive panel sizing."""
        with patch("os.get_terminal_size") as mock_get_size:
            mock_get_size.return_value = os.terminal_size((100, 30))

            test_message = "Test message"

            # Test each print function
            print_error(test_message, console=mock_console)
            print_success(test_message, console=mock_console)
            print_warning(test_message, console=mock_console)
            print_info(test_message, console=mock_console)

            # Each function should have been called once
            assert mock_console.print.call_count == 4

            # Check that panels were created with width parameter
            for call in mock_console.print.call_args_list:
                panel = call[0][0]  # First positional argument should be the Panel
                assert hasattr(panel, "width")
                assert panel.width is not None

    def test_empty_data_table_creation(self) -> None:
        """Test table creation with empty data."""
        with patch("os.get_terminal_size") as mock_get_size:
            mock_get_size.return_value = os.terminal_size((100, 30))

            table = create_info_table("Empty Table")

            # Should create table with default column setup
            assert len(table.columns) == 2
            assert table.columns[0].width == 15  # Default field width
            assert table.columns[1].width == 30  # Default value width

    def test_console_sizing_edge_cases(self) -> None:
        """Test edge cases in console sizing."""
        with patch("os.get_terminal_size") as mock_get_size:
            # Test with zero dimensions
            mock_get_size.return_value = os.terminal_size((0, 0))

            width, height = get_optimal_console_size()

            # Should use minimum constraints
            assert width == 80
            assert height == 24


if __name__ == "__main__":
    pytest.main([__file__])
