# --------------------------------------------------------------------------
# The Module transduces .*-tpl extension files to their respective file extensions
# and copies them to user's local directory.
#
# This will handle .py-tpl, .txt-tpl, .md-tpl, etc.
#
# @author bnbong
# --------------------------------------------------------------------------
import os
import shutil
from typing import Dict, Optional

from fastapi_fastkit.core.settings import settings
from fastapi_fastkit.utils.logging import debug_log, get_logger

logger = get_logger(__name__)


def copy_and_convert_template(
    template_dir: str, target_dir: str, project_name: str = ""
) -> None:
    """
    Copies all files from the template directory to the target directory,
    converting any files ending in `.*-tpl` during the copy process.

    :param project_name: name of new project user defined at CLI.
    :param template_dir: The source directory containing the template files.
    :type template_dir: str
    :param target_dir: The destination directory where files will be copied.
    :type target_dir: str
    :raises OSError: If directory operations fail
    :raises PermissionError: If file access is denied
    """
    # If project_name is provided, create a subdirectory
    # Otherwise, copy directly to target_dir
    target_path = os.path.join(target_dir, project_name) if project_name else target_dir

    try:
        os.makedirs(target_path, exist_ok=True)
    except OSError as e:
        debug_log(f"Failed to create target directory {target_path}: {e}", "error")
        raise

    _process_directory_tree(template_dir, target_path)


def _process_directory_tree(template_dir: str, target_path: str) -> None:
    """
    Process directory tree and copy files with template conversion.

    :param template_dir: Source template directory
    :param target_path: Target directory path
    """
    for root, dirs, files in os.walk(template_dir):
        relative_path = os.path.relpath(root, template_dir)

        # Handle the root directory case
        destination_dir = (
            target_path
            if relative_path == "."
            else os.path.join(target_path, relative_path)
        )

        if not _ensure_directory_exists(destination_dir):
            continue

        # Process files in current directory
        for file in files:
            src_file = os.path.join(root, file)
            _copy_template_file(src_file, destination_dir, file)


def _ensure_directory_exists(directory_path: str) -> bool:
    """
    Ensure directory exists, create if it doesn't.

    :param directory_path: Path to directory
    :return: True if directory exists or was created successfully, False otherwise
    """
    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
        return True
    except OSError as e:
        debug_log(f"Failed to create directory {directory_path}: {e}", "error")
        return False


def _copy_template_file(src_file: str, destination_dir: str, file_name: str) -> None:
    """
    Copy a single template file with appropriate name conversion.

    :param src_file: Source file path
    :param destination_dir: Destination directory
    :param file_name: Original file name
    """
    try:
        # Convert -tpl extension
        dst_file_name = (
            file_name.replace("-tpl", "") if file_name.endswith("-tpl") else file_name
        )
        dst_file = os.path.join(destination_dir, dst_file_name)

        shutil.copy2(src_file, dst_file)
        debug_log(f"Copied {src_file} to {dst_file}", "debug")

    except (OSError, PermissionError) as e:
        debug_log(f"Failed to copy file {src_file} to {dst_file}: {e}", "error")


def copy_and_convert_template_file(
    source_file: str, target_file: str, replacements: Optional[Dict[str, str]] = None
) -> bool:
    """
    Copies a single template file to the target location, converting it from .*-tpl
    to its proper extension and replacing any placeholders with provided values.

    :param source_file: Path to the source template file (with -tpl extension)
    :param target_file: Path to target destination file (without -tpl extension)
    :param replacements: Dictionary of placeholder replacements {placeholder: value}
    :return: True if successful, False otherwise
    """
    if not os.path.exists(source_file):
        debug_log(f"Source template file not found: {source_file}", "warning")
        return False

    try:
        # Read source content
        content = _read_template_content(source_file)
        if content is None:
            return False

        # Apply replacements if provided
        if replacements and isinstance(replacements, dict):
            content = _apply_replacements(content, replacements)

        # Write to target file
        return _write_target_file(target_file, content, source_file)

    except Exception as e:
        debug_log(
            f"Unexpected error processing template file {source_file}: {e}", "error"
        )
        return False


def _read_template_content(source_file: str) -> Optional[str]:
    """
    Read content from template file.

    :param source_file: Path to source file
    :return: File content or None if error occurred
    """
    try:
        with open(source_file, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError as e:
        debug_log(
            f"Error reading template file {source_file} (encoding issue): {e}", "error"
        )
        return None
    except (OSError, PermissionError) as e:
        debug_log(f"Error reading template file {source_file}: {e}", "error")
        return None


def _apply_replacements(content: str, replacements: Dict[str, str]) -> str:
    """
    Apply placeholder replacements to content.

    :param content: Original content
    :param replacements: Dictionary of replacements
    :return: Content with replacements applied
    """
    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)
    return content


def _write_target_file(target_file: str, content: str, source_file: str) -> bool:
    """
    Write content to target file.

    :param target_file: Target file path
    :param content: Content to write
    :param source_file: Source file path (for logging)
    :return: True if successful, False otherwise
    """
    try:
        # Ensure target directory exists
        target_dir = os.path.dirname(target_file)
        os.makedirs(target_dir, exist_ok=True)

        with open(target_file, "w", encoding="utf-8") as f:
            f.write(content)

        debug_log(
            f"Successfully copied template file from {source_file} to {target_file}",
            "debug",
        )
        return True

    except (OSError, PermissionError) as e:
        debug_log(f"Error writing to target file {target_file}: {e}", "error")
        return False


# Note: _convert_real_extension_to_tpl function was removed as it was not implemented
# and not used in the current codebase. If needed in the future for debugging
# operations, it can be re-implemented in the inspector module.
