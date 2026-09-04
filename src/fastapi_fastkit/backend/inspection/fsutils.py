# --------------------------------------------------------------------------
# Filesystem helpers shared by the inspection pipeline: shell script line
# ending normalisation and best-effort removal of temporary directories that
# Docker or a test run may have left behind with awkward permissions.
#
# @author bnbong
# --------------------------------------------------------------------------
import os
import shutil
import stat
import subprocess
import time

from fastapi_fastkit.utils.logging import debug_log

CLEANUP_MAX_RETRIES = 5


def fix_script_line_endings(script_path: str) -> None:
    """Convert Windows line endings in a script to Unix ones."""
    try:
        with open(script_path, "rb") as f:
            content = f.read()

        content = content.replace(b"\r\n", b"\n").replace(b"\r", b"\n")

        with open(script_path, "wb") as f:
            f.write(content)

        debug_log(f"Fixed line endings in {script_path}", "debug")
    except OSError as e:
        debug_log(f"Failed to fix line endings in {script_path}: {e}", "warning")


def fix_all_script_line_endings(directory: str) -> None:
    """Normalise line endings for every shell script below ``directory``."""
    for root, _dirs, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith((".sh", ".bash")):
                fix_script_line_endings(os.path.join(root, file_name))

    debug_log("Fixed line endings for all shell scripts", "info")


def _fix_permissions(path: str) -> None:
    """Grant full permissions to ``path``, ignoring failures."""
    try:
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    except OSError:
        pass


def fix_directory_permissions(directory_path: str) -> None:
    """Make a directory tree writable so it can be removed."""
    _fix_permissions(directory_path)
    for root, dirs, files in os.walk(directory_path):
        _fix_permissions(root)
        for name in dirs + files:
            _fix_permissions(os.path.join(root, name))


def remove_directory_contents(directory_path: str) -> None:
    """Remove a directory's contents entry by entry, ignoring failures."""
    for root, dirs, files in os.walk(directory_path, topdown=False):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            _fix_permissions(file_path)
            try:
                os.remove(file_path)
            except OSError:
                pass

        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            _fix_permissions(dir_path)
            try:
                os.rmdir(dir_path)
            except OSError:
                pass


def force_cleanup_directory(directory_path: str) -> None:
    """Remove ``directory_path`` using progressively more forceful strategies."""
    for attempt in range(CLEANUP_MAX_RETRIES):
        try:
            shutil.rmtree(directory_path)
            debug_log(
                f"Successfully cleaned up temp directory: {directory_path}", "info"
            )
            return
        except (OSError, PermissionError) as e:
            if attempt == CLEANUP_MAX_RETRIES - 1:
                break
            debug_log(
                f"Attempt {attempt + 1} failed to cleanup {directory_path}: {e}",
                "warning",
            )

            try:
                fix_directory_permissions(directory_path)
                shutil.rmtree(directory_path)
                debug_log(
                    "Successfully cleaned up temp directory after permission fix: "
                    f"{directory_path}",
                    "info",
                )
                return
            except OSError:
                pass

            try:
                remove_directory_contents(directory_path)
                os.rmdir(directory_path)
                debug_log(
                    "Successfully cleaned up temp directory by removing contents: "
                    f"{directory_path}",
                    "info",
                )
                return
            except OSError:
                pass

            time.sleep(2)

    debug_log(
        f"Failed to cleanup temp directory after {CLEANUP_MAX_RETRIES} attempts: "
        f"{directory_path}",
        "warning",
    )
    try:
        if os.name == "nt":  # pragma: no cover - Windows-only branch
            subprocess.run(
                ["rmdir", "/s", "/q", directory_path], check=False, shell=True
            )
        else:
            subprocess.run(["rm", "-rf", directory_path], check=False)
        debug_log(f"Force cleanup completed for: {directory_path}", "info")
    except OSError:
        debug_log(f"All cleanup attempts failed for: {directory_path}", "warning")
