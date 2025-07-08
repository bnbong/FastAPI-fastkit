# --------------------------------------------------------------------------
# Testcases of transducer module.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
import tempfile
from pathlib import Path
from typing import Dict
from unittest.mock import patch

import pytest

from fastapi_fastkit.backend.transducer import (
    _apply_replacements,
    _copy_template_file,
    _ensure_directory_exists,
    _process_directory_tree,
    _read_template_content,
    _write_target_file,
    copy_and_convert_template,
    copy_and_convert_template_file,
)


class TestTransducer:
    """Test cases for transducer module."""

    def setup_method(self) -> None:
        """Setup method for each test."""
        self.temp_source_dir = tempfile.mkdtemp()
        self.temp_dest_dir = tempfile.mkdtemp()
        self.source_path = Path(self.temp_source_dir)
        self.dest_path = Path(self.temp_dest_dir)

    def teardown_method(self) -> None:
        """Cleanup method for each test."""
        import shutil

        if os.path.exists(self.temp_source_dir):
            shutil.rmtree(self.temp_source_dir)
        if os.path.exists(self.temp_dest_dir):
            shutil.rmtree(self.temp_dest_dir)

    def test_copy_and_convert_template(self) -> None:
        """Test copy_and_convert_template function."""
        # given
        # Create template files
        template_file = self.source_path / "main.py-tpl"
        template_file.write_text("from fastapi import FastAPI\napp = FastAPI()")

        config_file = self.source_path / "config.py-tpl"
        config_file.write_text("PROJECT_NAME = 'test'")

        # Create subdirectory with template
        subdir = self.source_path / "api"
        subdir.mkdir()
        api_file = subdir / "routes.py-tpl"
        api_file.write_text("# API routes")

        # Create non-template file
        readme_file = self.source_path / "README.md-tpl"
        readme_file.write_text("# README")

        # when
        copy_and_convert_template(str(self.source_path), str(self.dest_path))

        # then
        # Check converted files
        assert (self.dest_path / "main.py").exists()
        assert (self.dest_path / "config.py").exists()
        assert (self.dest_path / "api" / "routes.py").exists()
        assert (self.dest_path / "README.md").exists()

        # Check content is preserved
        assert (
            self.dest_path / "main.py"
        ).read_text() == "from fastapi import FastAPI\napp = FastAPI()"
        assert (self.dest_path / "config.py").read_text() == "PROJECT_NAME = 'test'"
        assert (self.dest_path / "api" / "routes.py").read_text() == "# API routes"
        assert (self.dest_path / "README.md").read_text() == "# README"

    def test_copy_and_convert_template_empty_source(self) -> None:
        """Test copy_and_convert_template with empty source directory."""
        # given
        # Empty source directory

        # when
        copy_and_convert_template(str(self.source_path), str(self.dest_path))

        # then
        # Should not raise an error and dest should remain empty
        assert list(self.dest_path.iterdir()) == []

    def test_copy_and_convert_template_mixed_files(self) -> None:
        """Test copy_and_convert_template with mixed template and regular files."""
        # given
        # Template file
        template_py = self.source_path / "app.py-tpl"
        template_py.write_text("# Template Python file")

        # Regular file (should be copied as-is but without -tpl)
        regular_txt = self.source_path / "notes.txt-tpl"
        regular_txt.write_text("Regular text file")

        # Non-template file
        regular_file = self.source_path / "actual.txt"
        regular_file.write_text("Actual regular file")

        # when
        copy_and_convert_template(str(self.source_path), str(self.dest_path))

        # then
        assert (self.dest_path / "app.py").exists()
        assert (self.dest_path / "notes.txt").exists()
        assert (self.dest_path / "actual.txt").exists()

        # Check content
        assert (self.dest_path / "app.py").read_text() == "# Template Python file"
        assert (self.dest_path / "notes.txt").read_text() == "Regular text file"
        assert (self.dest_path / "actual.txt").read_text() == "Actual regular file"

    def test_copy_and_convert_template_nested_directories(self) -> None:
        """Test copy_and_convert_template with nested directory structure."""
        # given
        # Create nested structure
        deep_dir = self.source_path / "level1" / "level2" / "level3"
        deep_dir.mkdir(parents=True)

        deep_file = deep_dir / "deep.py-tpl"
        deep_file.write_text("# Deep nested file")

        # when
        copy_and_convert_template(str(self.source_path), str(self.dest_path))

        # then
        expected_file = self.dest_path / "level1" / "level2" / "level3" / "deep.py"
        assert expected_file.exists()
        assert expected_file.read_text() == "# Deep nested file"

    # Tests for new functions added to transducer.py

    def test_copy_and_convert_template_file_success(self) -> None:
        """Test copy_and_convert_template_file with successful operation."""
        # given
        source_file = self.source_path / "test.py-tpl"
        target_file = self.dest_path / "test.py"
        content = "from fastapi import FastAPI\napp = FastAPI(title='{{PROJECT_NAME}}')"
        source_file.write_text(content)

        replacements: Dict[str, str] = {"{{PROJECT_NAME}}": "MyProject"}

        # when
        result = copy_and_convert_template_file(
            str(source_file), str(target_file), replacements
        )

        # then
        assert result is True
        assert target_file.exists()
        expected_content = (
            "from fastapi import FastAPI\napp = FastAPI(title='MyProject')"
        )
        assert target_file.read_text() == expected_content

    def test_copy_and_convert_template_file_no_replacements(self) -> None:
        """Test copy_and_convert_template_file without replacements."""
        # given
        source_file = self.source_path / "simple.py-tpl"
        target_file = self.dest_path / "simple.py"
        content = "# Simple Python file"
        source_file.write_text(content)

        # when
        result = copy_and_convert_template_file(str(source_file), str(target_file))

        # then
        assert result is True
        assert target_file.exists()
        assert target_file.read_text() == content

    def test_copy_and_convert_template_file_source_not_found(self) -> None:
        """Test copy_and_convert_template_file with non-existent source."""
        # given
        source_file = self.source_path / "nonexistent.py-tpl"
        target_file = self.dest_path / "target.py"

        # when
        result = copy_and_convert_template_file(str(source_file), str(target_file))

        # then
        assert result is False
        assert not target_file.exists()

    def test_copy_and_convert_template_file_target_dir_creation(self) -> None:
        """Test copy_and_convert_template_file creates target directory."""
        # given
        source_file = self.source_path / "test.py-tpl"
        target_file = self.dest_path / "deep" / "nested" / "test.py"
        content = "# Test content"
        source_file.write_text(content)

        # when
        result = copy_and_convert_template_file(str(source_file), str(target_file))

        # then
        assert result is True
        assert target_file.exists()
        assert target_file.read_text() == content

    def test_read_template_content_success(self) -> None:
        """Test _read_template_content with valid file."""
        # given
        test_file = self.source_path / "test.txt"
        content = "Test content with unicode: ñáéíóú"
        test_file.write_text(content, encoding="utf-8")

        # when
        result = _read_template_content(str(test_file))

        # then
        assert result == content

    def test_read_template_content_file_not_found(self) -> None:
        """Test _read_template_content with non-existent file."""
        # given
        non_existent_file = self.source_path / "nonexistent.txt"

        # when
        result = _read_template_content(str(non_existent_file))

        # then
        assert result is None

    def test_read_template_content_permission_error(self) -> None:
        """Test _read_template_content with permission error."""
        # given
        test_file = self.source_path / "test.txt"
        test_file.write_text("content")

        # when
        with patch("builtins.open", side_effect=PermissionError("Access denied")):
            result = _read_template_content(str(test_file))

        # then
        assert result is None

    def test_read_template_content_unicode_error(self) -> None:
        """Test _read_template_content with unicode decode error."""
        # given
        test_file = self.source_path / "test.txt"
        test_file.write_text("content")

        # when
        with patch(
            "builtins.open", side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "error")
        ):
            result = _read_template_content(str(test_file))

        # then
        assert result is None

    def test_apply_replacements_multiple(self) -> None:
        """Test _apply_replacements with multiple replacements."""
        # given
        content = "Hello {{NAME}}, your project is {{PROJECT}} in {{LANGUAGE}}"
        replacements: Dict[str, str] = {
            "{{NAME}}": "John",
            "{{PROJECT}}": "FastAPI App",
            "{{LANGUAGE}}": "Python",
        }

        # when
        result = _apply_replacements(content, replacements)

        # then
        expected = "Hello John, your project is FastAPI App in Python"
        assert result == expected

    def test_apply_replacements_no_matches(self) -> None:
        """Test _apply_replacements with no matching placeholders."""
        # given
        content = "Static content without placeholders"
        replacements: Dict[str, str] = {"{{NAME}}": "John"}

        # when
        result = _apply_replacements(content, replacements)

        # then
        assert result == content

    def test_apply_replacements_empty_dict(self) -> None:
        """Test _apply_replacements with empty replacements dict."""
        # given
        content = "Content with {{PLACEHOLDER}}"
        replacements: Dict[str, str] = {}

        # when
        result = _apply_replacements(content, replacements)

        # then
        assert result == content

    def test_write_target_file_success(self) -> None:
        """Test _write_target_file with successful write."""
        # given
        target_file = self.dest_path / "output.txt"
        content = "Test content to write"
        source_file = "source.txt"

        # when
        result = _write_target_file(str(target_file), content, source_file)

        # then
        assert result is True
        assert target_file.exists()
        assert target_file.read_text() == content

    def test_write_target_file_create_directory(self) -> None:
        """Test _write_target_file creates parent directories."""
        # given
        target_file = self.dest_path / "deep" / "nested" / "output.txt"
        content = "Test content"
        source_file = "source.txt"

        # when
        result = _write_target_file(str(target_file), content, source_file)

        # then
        assert result is True
        assert target_file.exists()
        assert target_file.read_text() == content

    def test_write_target_file_permission_error(self) -> None:
        """Test _write_target_file with permission error."""
        # given
        target_file = self.dest_path / "output.txt"
        content = "Test content"
        source_file = "source.txt"

        # when
        with patch("builtins.open", side_effect=PermissionError("Access denied")):
            result = _write_target_file(str(target_file), content, source_file)

        # then
        assert result is False

    def test_ensure_directory_exists_new_directory(self) -> None:
        """Test _ensure_directory_exists creates new directory."""
        # given
        new_dir = self.dest_path / "new_directory"

        # when
        result = _ensure_directory_exists(str(new_dir))

        # then
        assert result is True
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_ensure_directory_exists_existing_directory(self) -> None:
        """Test _ensure_directory_exists with existing directory."""
        # given
        existing_dir = self.dest_path / "existing"
        existing_dir.mkdir()

        # when
        result = _ensure_directory_exists(str(existing_dir))

        # then
        assert result is True
        assert existing_dir.exists()

    def test_ensure_directory_exists_permission_error(self) -> None:
        """Test _ensure_directory_exists with permission error."""
        # given
        new_dir = "/invalid/path/that/cannot/be/created"

        # when
        result = _ensure_directory_exists(new_dir)

        # then
        assert result is False

    def test_copy_template_file_success(self) -> None:
        """Test _copy_template_file with successful copy."""
        # given
        source_file = self.source_path / "test.py-tpl"
        dest_dir = self.dest_path
        content = "# Test content"
        source_file.write_text(content)

        # when
        _copy_template_file(str(source_file), str(dest_dir), "test.py-tpl")

        # then
        target_file = dest_dir / "test.py"  # -tpl should be removed
        assert target_file.exists()
        assert target_file.read_text() == content

    def test_copy_template_file_no_tpl_extension(self) -> None:
        """Test _copy_template_file with file without -tpl extension."""
        # given
        source_file = self.source_path / "regular.txt"
        dest_dir = self.dest_path
        content = "Regular file content"
        source_file.write_text(content)

        # when
        _copy_template_file(str(source_file), str(dest_dir), "regular.txt")

        # then
        target_file = dest_dir / "regular.txt"  # Should keep original name
        assert target_file.exists()
        assert target_file.read_text() == content

    def test_copy_template_file_permission_error(self) -> None:
        """Test _copy_template_file with permission error."""
        # given
        source_file = self.source_path / "test.py-tpl"
        dest_dir = self.dest_path
        source_file.write_text("content")

        # when
        with patch("shutil.copy2", side_effect=PermissionError("Access denied")):
            # Should not raise exception
            _copy_template_file(str(source_file), str(dest_dir), "test.py-tpl")

        # then
        # No exception should be raised, error is logged

    def test_process_directory_tree_success(self) -> None:
        """Test _process_directory_tree with successful processing."""
        # given
        # Create a source structure
        (self.source_path / "subdir").mkdir()
        (self.source_path / "file1.py-tpl").write_text("# File 1")
        (self.source_path / "subdir" / "file2.txt-tpl").write_text("File 2 content")

        # when
        _process_directory_tree(str(self.source_path), str(self.dest_path))

        # then
        assert (self.dest_path / "file1.py").exists()
        assert (self.dest_path / "subdir" / "file2.txt").exists()
        assert (self.dest_path / "file1.py").read_text() == "# File 1"
        assert (self.dest_path / "subdir" / "file2.txt").read_text() == "File 2 content"

    def test_process_directory_tree_directory_creation_failure(self) -> None:
        """Test _process_directory_tree when directory creation fails."""
        # given
        (self.source_path / "file.txt-tpl").write_text("content")

        # when
        with patch(
            "fastapi_fastkit.backend.transducer._ensure_directory_exists",
            return_value=False,
        ):
            # Should handle gracefully
            _process_directory_tree(str(self.source_path), str(self.dest_path))

        # then
        # Should not raise exception, just skip the problematic directory

    def test_copy_and_convert_template_with_project_name(self) -> None:
        """Test copy_and_convert_template with project name parameter."""
        # given
        template_file = self.source_path / "main.py-tpl"
        template_file.write_text("from fastapi import FastAPI\napp = FastAPI()")
        project_name = "my_project"

        # when
        copy_and_convert_template(
            str(self.source_path), str(self.dest_path), project_name
        )

        # then
        project_dir = self.dest_path / project_name
        assert project_dir.exists()
        assert (project_dir / "main.py").exists()
        assert (
            project_dir / "main.py"
        ).read_text() == "from fastapi import FastAPI\napp = FastAPI()"

    def test_copy_and_convert_template_target_creation_error(self) -> None:
        """Test copy_and_convert_template when target directory creation fails."""
        # given
        template_file = self.source_path / "main.py-tpl"
        template_file.write_text("content")

        # when & then
        with patch("os.makedirs", side_effect=OSError("Permission denied")):
            with pytest.raises(OSError):
                copy_and_convert_template(
                    str(self.source_path), "/invalid/path", "project"
                )
