"""
Test cases for backend/transducer.py module.
"""

import os
import tempfile
from pathlib import Path

import pytest

from fastapi_fastkit.backend.transducer import copy_and_convert_template


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
