# --------------------------------------------------------------------------
# Testcases for the filesystem helpers used by the inspection pipeline.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
import stat
import subprocess
from pathlib import Path
from unittest.mock import patch

from fastapi_fastkit.backend.inspection import fsutils


class TestFixScriptLineEndings:
    """Windows line endings are normalised in place."""

    def test_converts_crlf_and_cr_to_lf(self, tmp_path: Path) -> None:
        # given
        script = tmp_path / "script.sh"
        script.write_bytes(b"echo hi\r\necho bye\recho done\n")

        # when
        fsutils.fix_script_line_endings(str(script))

        # then
        assert script.read_bytes() == b"echo hi\necho bye\necho done\n"

    def test_logs_warning_on_read_failure(self, tmp_path: Path) -> None:
        # given
        missing = tmp_path / "missing.sh"

        # when / then - should not raise
        fsutils.fix_script_line_endings(str(missing))


class TestFixAllScriptLineEndings:
    """Every .sh/.bash file below a directory gets normalised."""

    def test_fixes_shell_scripts_recursively(self, tmp_path: Path) -> None:
        # given
        (tmp_path / "sub").mkdir()
        sh_file = tmp_path / "run.sh"
        bash_file = tmp_path / "sub" / "run.bash"
        other_file = tmp_path / "notes.txt"
        sh_file.write_bytes(b"echo hi\r\n")
        bash_file.write_bytes(b"echo bye\r\n")
        other_file.write_bytes(b"unchanged\r\n")

        # when
        fsutils.fix_all_script_line_endings(str(tmp_path))

        # then
        assert sh_file.read_bytes() == b"echo hi\n"
        assert bash_file.read_bytes() == b"echo bye\n"
        assert other_file.read_bytes() == b"unchanged\r\n"


class TestFixDirectoryPermissions:
    """Permission fixing ignores failures and is applied tree-wide."""

    def test_fix_permissions_ignores_oserror(self, tmp_path: Path) -> None:
        # given / when / then - should not raise even for a bogus path
        fsutils._fix_permissions(str(tmp_path / "does-not-exist"))

    def test_fix_directory_permissions_applies_to_tree(self, tmp_path: Path) -> None:
        # given
        (tmp_path / "sub").mkdir()
        file_path = tmp_path / "sub" / "file.txt"
        file_path.write_text("data")
        os.chmod(file_path, 0o000)

        # when
        fsutils.fix_directory_permissions(str(tmp_path))

        # then
        mode = stat.S_IMODE(os.stat(file_path).st_mode)
        assert mode == (stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)


class TestRemoveDirectoryContents:
    """Contents are removed entry by entry, tolerating failures."""

    def test_removes_all_files_and_subdirectories(self, tmp_path: Path) -> None:
        # given
        (tmp_path / "sub").mkdir()
        (tmp_path / "sub" / "file.txt").write_text("data")
        (tmp_path / "top.txt").write_text("data")

        # when
        fsutils.remove_directory_contents(str(tmp_path))

        # then
        assert list(tmp_path.iterdir()) == []

    def test_ignores_removal_failures(self, tmp_path: Path) -> None:
        # given
        (tmp_path / "file.txt").write_text("data")

        # when / then - patched removal raises but is swallowed
        with patch("os.remove", side_effect=OSError("boom")):
            fsutils.remove_directory_contents(str(tmp_path))

        with patch("os.rmdir", side_effect=OSError("boom")):
            fsutils.remove_directory_contents(str(tmp_path))


class TestForceCleanupDirectory:
    """Cleanup escalates through progressively more forceful strategies."""

    def test_succeeds_on_first_rmtree(self, tmp_path: Path) -> None:
        # given
        target = tmp_path / "victim"
        target.mkdir()
        (target / "file.txt").write_text("data")

        # when
        fsutils.force_cleanup_directory(str(target))

        # then
        assert not target.exists()

    def test_falls_back_to_permission_fix_then_rmtree(self, tmp_path: Path) -> None:
        # given
        target = tmp_path / "victim"
        target.mkdir()
        (target / "file.txt").write_text("data")

        calls = {"n": 0}
        real_rmtree = __import__("shutil").rmtree

        def flaky_rmtree(path: str, *a: object, **kw: object) -> None:
            calls["n"] += 1
            if calls["n"] == 1:
                raise OSError("locked")
            real_rmtree(path, *a, **kw)

        # when
        with patch("shutil.rmtree", side_effect=flaky_rmtree):
            fsutils.force_cleanup_directory(str(target))

        # then
        assert not target.exists()

    def test_falls_back_to_manual_removal(self, tmp_path: Path) -> None:
        # given
        target = tmp_path / "victim"
        target.mkdir()
        (target / "file.txt").write_text("data")

        # when - rmtree always fails, permission fix does nothing useful, so
        # the manual remove_directory_contents + rmdir path must finish it.
        with patch("shutil.rmtree", side_effect=OSError("locked")):
            with patch.object(fsutils, "fix_directory_permissions"):
                fsutils.force_cleanup_directory(str(target))

        # then
        assert not target.exists()

    def test_gives_up_and_shells_out_after_max_retries(self, tmp_path: Path) -> None:
        # given
        target = tmp_path / "victim"
        target.mkdir()

        # when - every strategy fails, forcing the final subprocess fallback
        with patch("shutil.rmtree", side_effect=OSError("locked")):
            with patch.object(fsutils, "fix_directory_permissions"):
                with patch.object(
                    fsutils,
                    "remove_directory_contents",
                    side_effect=OSError("locked"),
                ):
                    with patch("time.sleep"):
                        with patch("subprocess.run") as mock_run:
                            fsutils.force_cleanup_directory(str(target))

        # then
        mock_run.assert_called_once()
        assert mock_run.call_args.args[0] == ["rm", "-rf", str(target)]

    def test_subprocess_fallback_oserror_is_logged(self, tmp_path: Path) -> None:
        # given
        target = tmp_path / "victim"
        target.mkdir()

        # when
        with patch("shutil.rmtree", side_effect=OSError("locked")):
            with patch.object(fsutils, "fix_directory_permissions"):
                with patch.object(
                    fsutils,
                    "remove_directory_contents",
                    side_effect=OSError("locked"),
                ):
                    with patch("time.sleep"):
                        with patch("subprocess.run", side_effect=OSError("no rm")):
                            fsutils.force_cleanup_directory(str(target))

        # then - should not raise; failure is only logged
