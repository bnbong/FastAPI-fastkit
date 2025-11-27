# --------------------------------------------------------------------------
# Test cases for backend/interactive/selectors.py
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from unittest.mock import MagicMock, patch

import pytest

from fastapi_fastkit.backend.interactive.selectors import (
    confirm_selections,
    display_feature_catalog,
    multi_select_prompt,
    render_feature_options,
    render_selection_table,
)
from fastapi_fastkit.core.settings import FastkitConfig


class TestRenderSelectionTable:
    """Test cases for render_selection_table function."""

    @patch("fastapi_fastkit.backend.interactive.selectors.console.print")
    def test_render_selection_table_with_numbers(self, mock_print) -> None:
        """Test rendering selection table with numbers."""
        # given
        title = "Test Options"
        options = {"option1": "Description 1", "option2": "Description 2"}

        # when
        render_selection_table(title, options, show_numbers=True)

        # then
        assert mock_print.called

    @patch("fastapi_fastkit.backend.interactive.selectors.console.print")
    def test_render_selection_table_without_numbers(self, mock_print) -> None:
        """Test rendering selection table without numbers."""
        # given
        title = "Test Options"
        options = {"option1": "Description 1"}

        # when
        render_selection_table(title, options, show_numbers=False)

        # then
        assert mock_print.called


class TestRenderFeatureOptions:
    """Test cases for render_feature_options function."""

    @patch("fastapi_fastkit.backend.interactive.selectors.console.print")
    def test_render_feature_options(self, mock_print) -> None:
        """Test rendering feature options."""
        # given
        category = "Database"
        options = ["PostgreSQL", "MySQL", "MongoDB"]
        descriptions = {
            "PostgreSQL": "PostgreSQL database",
            "MySQL": "MySQL database",
            "MongoDB": "MongoDB NoSQL",
        }

        # when
        render_feature_options(category, options, descriptions)

        # then
        assert (
            mock_print.call_count >= 3
        )  # Category + instruction + at least one option


class TestMultiSelectPrompt:
    """Test cases for multi_select_prompt function."""

    @patch("fastapi_fastkit.backend.interactive.selectors.console.input")
    @patch("fastapi_fastkit.backend.interactive.selectors.console.print")
    def test_multi_select_prompt_single_selection(self, mock_print, mock_input) -> None:
        """Test multi-select with single selection."""
        # given
        title = "Select utilities"
        options = ["CORS", "Rate-Limiting", "Pagination"]
        descriptions = {}
        mock_input.return_value = "1"

        # when
        result = multi_select_prompt(title, options, descriptions)

        # then
        assert result == [0]  # 0-based index

    @patch("fastapi_fastkit.backend.interactive.selectors.console.input")
    @patch("fastapi_fastkit.backend.interactive.selectors.console.print")
    def test_multi_select_prompt_multiple_selections(
        self, mock_print, mock_input
    ) -> None:
        """Test multi-select with multiple selections."""
        # given
        title = "Select utilities"
        options = ["CORS", "Rate-Limiting", "Pagination"]
        descriptions = {}
        mock_input.return_value = "1,3"

        # when
        result = multi_select_prompt(title, options, descriptions)

        # then
        assert 0 in result
        assert 2 in result

    @patch("fastapi_fastkit.backend.interactive.selectors.console.input")
    @patch("fastapi_fastkit.backend.interactive.selectors.console.print")
    def test_multi_select_prompt_skip(self, mock_print, mock_input) -> None:
        """Test multi-select with skip (empty input)."""
        # given
        title = "Select utilities"
        options = ["CORS", "Rate-Limiting"]
        descriptions = {}
        mock_input.return_value = ""

        # when
        result = multi_select_prompt(title, options, descriptions)

        # then
        assert result == []

    @patch("fastapi_fastkit.backend.interactive.selectors.console.input")
    @patch("fastapi_fastkit.backend.interactive.selectors.console.print")
    def test_multi_select_prompt_invalid_then_valid(
        self, mock_print, mock_input
    ) -> None:
        """Test multi-select with invalid input followed by valid input."""
        # given
        title = "Select utilities"
        options = ["CORS", "Rate-Limiting"]
        descriptions = {}
        mock_input.side_effect = ["invalid", "1"]

        # when
        result = multi_select_prompt(title, options, descriptions)

        # then
        assert result == [0]


class TestConfirmSelections:
    """Test cases for confirm_selections function."""

    @patch("fastapi_fastkit.backend.interactive.selectors.console.input")
    @patch("fastapi_fastkit.backend.interactive.selectors.console.print")
    def test_confirm_selections_yes(self, mock_print, mock_input) -> None:
        """Test confirming selections with 'y'."""
        # given
        config = {
            "project_name": "test-project",
            "author": "Test Author",
            "author_email": "test@example.com",
            "description": "Test",
            "database": {"type": "PostgreSQL"},
            "authentication": "JWT",
            "package_manager": "uv",
            "all_dependencies": ["fastapi", "uvicorn"],
        }
        mock_input.return_value = "y"

        # when
        result = confirm_selections(config)

        # then
        assert result is True

    @patch("fastapi_fastkit.backend.interactive.selectors.console.input")
    @patch("fastapi_fastkit.backend.interactive.selectors.console.print")
    def test_confirm_selections_empty_yes(self, mock_print, mock_input) -> None:
        """Test confirming selections with empty input (default yes)."""
        # given
        config = {
            "project_name": "test-project",
            "database": {"type": "None"},
            "authentication": "None",
            "package_manager": "uv",
            "all_dependencies": [],
        }
        mock_input.return_value = ""

        # when
        result = confirm_selections(config)

        # then
        assert result is True

    @patch("fastapi_fastkit.backend.interactive.selectors.console.input")
    @patch("fastapi_fastkit.backend.interactive.selectors.console.print")
    def test_confirm_selections_no(self, mock_print, mock_input) -> None:
        """Test rejecting selections with 'n'."""
        # given
        config = {
            "project_name": "test-project",
            "database": {"type": "None"},
            "authentication": "None",
            "package_manager": "uv",
            "all_dependencies": [],
        }
        mock_input.return_value = "n"

        # when
        result = confirm_selections(config)

        # then
        assert result is False


class TestDisplayFeatureCatalog:
    """Test cases for display_feature_catalog function."""

    @patch("fastapi_fastkit.backend.interactive.selectors.console.print")
    def test_display_feature_catalog(self, mock_print) -> None:
        """Test displaying feature catalog."""
        # given
        settings = FastkitConfig()
        catalog = settings.PACKAGE_CATALOG
        descriptions = settings.FEATURE_DESCRIPTIONS

        # when
        display_feature_catalog(catalog, descriptions)

        # then
        # Should print tables for each category
        assert mock_print.called
        assert mock_print.call_count > 5  # Multiple categories
