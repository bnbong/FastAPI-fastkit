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
from fastapi_fastkit.utils.logging import get_logger


def _convert_tpl_to_real_extension(file_path: str) -> str:
    """
    Converts a file ending in `.*-tpl` to its respective file extension by removing the `-tpl` suffix.

    :param file_path: The full path of the `.*-tpl` file.
    :type file_path: str
    :return: The new path of the file with the `-tpl` suffix removed.
    """
    # Remove the '-tpl' suffix from any file extension
    if file_path.endswith("-tpl"):
        new_file_path = file_path.replace("-tpl", "")
        try:
            os.rename(file_path, new_file_path)
            return new_file_path
        except OSError as e:
            if settings.DEBUG_MODE:
                logger = get_logger(__name__)
                logger.error(
                    f"Failed to rename file {file_path} to {new_file_path}: {e}"
                )
            return file_path
    return file_path


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
    if project_name:
        target_path = os.path.join(target_dir, project_name)
    else:
        target_path = target_dir

    try:
        os.makedirs(target_path, exist_ok=True)
    except OSError as e:
        if settings.DEBUG_MODE:
            logger = get_logger(__name__)
            logger.error(f"Failed to create target directory {target_path}: {e}")
        raise

    for root, dirs, files in os.walk(template_dir):
        relative_path = os.path.relpath(root, template_dir)

        # Handle the root directory case
        if relative_path == ".":
            destination_dir = target_path
        else:
            destination_dir = os.path.join(target_path, relative_path)

        try:
            if not os.path.exists(destination_dir):
                os.makedirs(destination_dir)
        except OSError as e:
            if settings.DEBUG_MODE:
                logger = get_logger(__name__)
                logger.error(f"Failed to create directory {destination_dir}: {e}")
            continue

        for file in files:
            src_file = os.path.join(root, file)

            try:
                if file.endswith("-tpl"):
                    dst_file = os.path.join(destination_dir, file.replace("-tpl", ""))
                    shutil.copy2(src_file, dst_file)
                else:
                    dst_file = os.path.join(destination_dir, file)
                    shutil.copy2(src_file, dst_file)
            except (OSError, PermissionError) as e:
                if settings.DEBUG_MODE:
                    logger = get_logger(__name__)
                    logger.error(f"Failed to copy file {src_file} to {dst_file}: {e}")
                continue


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
    try:
        if not os.path.exists(source_file):
            if settings.DEBUG_MODE:
                logger = get_logger(__name__)
                logger.warning(f"Source template file not found: {source_file}")
            return False

        # Read a single source content (with .py-tpl extension)
        with open(source_file, "r", encoding="utf-8") as src_file:
            content = src_file.read()

        if replacements and isinstance(replacements, dict):
            for placeholder, value in replacements.items():
                content = content.replace(placeholder, value)

        target_dir = os.path.dirname(target_file)
        os.makedirs(target_dir, exist_ok=True)

        with open(target_file, "w", encoding="utf-8") as tgt_file:
            tgt_file.write(content)

        if settings.DEBUG_MODE:
            logger = get_logger(__name__)
            logger.debug(
                f"Successfully copied template file from {source_file} to {target_file}"
            )
        return True

    except (OSError, PermissionError) as e:
        if settings.DEBUG_MODE:
            logger = get_logger(__name__)
            logger.error(
                f"Error copying template file from {source_file} to {target_file}: {e}"
            )
        return False
    except UnicodeDecodeError as e:
        if settings.DEBUG_MODE:
            logger = get_logger(__name__)
            logger.error(
                f"Error reading template file {source_file} (encoding issue): {e}"
            )
        return False


# Note: _convert_real_extension_to_tpl function was removed as it was not implemented
# and not used in the current codebase. If needed in the future for debugging
# operations, it can be re-implemented in the inspector module.
