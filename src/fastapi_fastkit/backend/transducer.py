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
from typing import Dict, List, Optional

from fastapi_fastkit.core.exceptions import TemplateExceptions
from fastapi_fastkit.utils.logging import debug_log, get_logger

logger = get_logger(__name__)

#: Template-only metadata files that must never land in a generated project.
#: ``template-config.yml`` drives the template inspector (test strategy, smoke
#: test entrypoint); it is meaningless to a user's project, so it is filtered
#: out during the copy instead of being deleted afterwards. The names listed
#: here are the *converted* names (the ``-tpl`` marker already stripped).
TEMPLATE_ONLY_FILES = frozenset({"template-config.yml"})

#: Extensions of files that are known to be text and therefore safe to rewrite
#: with Unix line endings. Anything outside this list is copied byte for byte,
#: so an image or an archive shipped inside a template survives untouched.
TEXT_FILE_EXTENSIONS = frozenset(
    {
        ".bash",
        ".cfg",
        ".css",
        ".env",
        ".html",
        ".ini",
        ".js",
        ".json",
        ".mako",
        ".md",
        ".py",
        ".rst",
        ".sh",
        ".sql",
        ".toml",
        ".ts",
        ".txt",
        ".yaml",
        ".yml",
    }
)

#: Extension-less file names that are text as well.
TEXT_FILE_NAMES = frozenset(
    {
        ".dockerignore",
        ".env",
        ".gitignore",
        "CHANGELOG",
        "Dockerfile",
        "LICENSE",
        "Makefile",
        "Procfile",
        "README",
    }
)

#: How much of a file is sampled when looking for a NUL byte. A NUL in the
#: first chunk is the same heuristic Git uses to call a blob binary.
BINARY_SNIFF_BYTES = 8192


def _looks_like_text_file(file_path: str, file_name: str) -> bool:
    """
    Decide whether a copied file may have its line endings normalised.

    The check is deliberately conservative: the name has to be on the text
    whitelist *and* the content must carry no NUL byte, so a mislabelled
    binary is left alone rather than corrupted.

    :param file_path: Path of the file to inspect
    :param file_name: File name used for the extension/name whitelist
    :return: True when the file is safe to rewrite as text
    """
    _, extension = os.path.splitext(file_name)
    if (
        extension.lower() not in TEXT_FILE_EXTENSIONS
        and file_name not in TEXT_FILE_NAMES
    ):
        return False

    try:
        with open(file_path, "rb") as f:
            return b"\x00" not in f.read(BINARY_SNIFF_BYTES)
    except OSError as e:
        debug_log(f"Could not sniff {file_path} for binary content: {e}", "warning")
        return False


def _normalize_line_endings(file_path: str, file_name: str) -> None:
    """
    Rewrite a copied text file with Unix line endings.

    Templates checked out on Windows (or with ``core.autocrlf=true``) carry
    CRLF, which makes a generated project's shell scripts unusable inside a
    Linux container: ``env: 'bash\r': No such file or directory``. The rewrite
    happens in place through :func:`fix_script_line_endings`, which truncates
    rather than recreates the file and therefore keeps the executable bit
    ``shutil.copy2`` just carried over.

    :param file_path: Path of the copied file
    :param file_name: File name used for the text/binary decision
    """
    if not _looks_like_text_file(file_path, file_name):
        return

    # Imported lazily: ``fastapi_fastkit.backend.inspection`` pulls in the
    # scaffolder, which imports this module, so a top-level import would be
    # circular.
    from fastapi_fastkit.backend.inspection.fsutils import fix_script_line_endings

    fix_script_line_endings(file_path)


def copy_and_convert_template(
    template_dir: str, target_dir: str, project_name: str = ""
) -> List[str]:
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
    :return: Absolute paths of the files this copy actually wrote. Callers use
        the list to keep every later rewriting pass (placeholder substitution,
        metadata injection) scoped to the deployed files, which matters when
        the template is deployed in place into a directory that already holds
        unrelated user files.
    """
    # If project_name is provided, create a subdirectory
    # Otherwise, copy directly to target_dir
    target_path = os.path.join(target_dir, project_name) if project_name else target_dir

    try:
        os.makedirs(target_path, exist_ok=True)
    except OSError as e:
        debug_log(f"Failed to create target directory {target_path}: {e}", "error")
        raise

    return _process_directory_tree(template_dir, target_path)


def _process_directory_tree(template_dir: str, target_path: str) -> List[str]:
    """
    Process directory tree and copy files with template conversion.

    :param template_dir: Source template directory
    :param target_path: Target directory path
    :return: Absolute paths of the written files
    """
    copied: List[str] = []
    for root, dirs, files in os.walk(template_dir):
        relative_path = os.path.relpath(root, template_dir)

        # Handle the root directory case
        destination_dir = (
            target_path
            if relative_path == "."
            else os.path.join(target_path, relative_path)
        )

        _ensure_directory_exists(destination_dir)

        # Process files in current directory
        for file in files:
            src_file = os.path.join(root, file)
            dst_file = _copy_template_file(src_file, destination_dir, file)
            if dst_file:
                copied.append(dst_file)

    return copied


def _ensure_directory_exists(directory_path: str) -> None:
    """
    Ensure directory exists, create if it doesn't.

    A failure here leaves the target tree half-written, so it is raised to the
    caller instead of being swallowed - the caller is responsible for rollback.

    :param directory_path: Path to directory
    :raises TemplateExceptions: If the directory cannot be created
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
    except OSError as e:
        debug_log(f"Failed to create directory {directory_path}: {e}", "error")
        raise TemplateExceptions(
            f"Failed to create directory {directory_path}: {e}"
        ) from e


def _copy_template_file(
    src_file: str, destination_dir: str, file_name: str
) -> Optional[str]:
    """
    Copy a single template file with appropriate name conversion.

    :param src_file: Source file path
    :param destination_dir: Destination directory
    :param file_name: Original file name
    :return: Absolute path of the written file, or None when the file was
        skipped as template-only metadata
    :raises TemplateExceptions: If the file cannot be copied
    """
    # Convert -tpl extension. ``removesuffix`` only strips the trailing marker,
    # so a name such as "run-tpl-helper.py-tpl" keeps its inner "-tpl".
    dst_file_name = file_name.removesuffix("-tpl")
    if dst_file_name in TEMPLATE_ONLY_FILES:
        debug_log(f"Skipping template-only file {src_file}", "debug")
        return None

    dst_file = os.path.join(destination_dir, dst_file_name)

    try:
        shutil.copy2(src_file, dst_file)
        _normalize_line_endings(dst_file, dst_file_name)
        debug_log(f"Copied {src_file} to {dst_file}", "debug")
        return dst_file

    except (OSError, PermissionError) as e:
        debug_log(f"Failed to copy file {src_file} to {dst_file}: {e}", "error")
        raise TemplateExceptions(
            f"Failed to copy file {src_file} to {dst_file}: {e}"
        ) from e


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

        with open(target_file, "w", encoding="utf-8", newline="\n") as f:
            f.write(content.replace("\r\n", "\n").replace("\r", "\n"))

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
