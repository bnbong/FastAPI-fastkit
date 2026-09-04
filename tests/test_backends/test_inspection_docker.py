# --------------------------------------------------------------------------
# Testcases for the DockerCompose wrapper used by the docker inspection
# strategy. All subprocess invocations are mocked - no real docker/
# docker-compose binary is ever invoked.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import subprocess
from typing import Any, List, Optional
from unittest.mock import patch

import pytest

from fastapi_fastkit.backend.inspection.docker import COMPOSE_COMMAND, DockerCompose


def completed(
    returncode: int = 0, stdout: str = "", stderr: str = ""
) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(
        args=["x"], returncode=returncode, stdout=stdout, stderr=stderr
    )


class TestRun:
    """The low-level ``_run`` helper swallows timeout / OSError into None."""

    def test_returns_completed_process(self) -> None:
        # given
        compose = DockerCompose("/tmp/project")

        # when
        with patch("subprocess.run", return_value=completed()) as mock_run:
            result = compose._run(["docker", "--version"], timeout=5)

        # then
        assert result is not None
        mock_run.assert_called_once()

    def test_returns_none_on_timeout(self) -> None:
        # given
        compose = DockerCompose("/tmp/project")

        # when
        with patch(
            "subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="docker", timeout=5),
        ):
            result = compose._run(["docker", "--version"], timeout=5)

        # then
        assert result is None

    def test_returns_none_on_oserror(self) -> None:
        # given
        compose = DockerCompose("/tmp/project")

        # when
        with patch("subprocess.run", side_effect=OSError("no docker")):
            result = compose._run(["docker", "--version"], timeout=5)

        # then
        assert result is None


class TestIsAvailable:
    """Both docker and docker-compose must respond successfully."""

    def test_true_when_both_commands_succeed(self) -> None:
        with patch("subprocess.run", return_value=completed(returncode=0)):
            assert DockerCompose.is_available() is True

    def test_false_when_docker_missing(self) -> None:
        with patch("subprocess.run", side_effect=OSError("not found")):
            assert DockerCompose.is_available() is False

    def test_false_when_a_command_fails(self) -> None:
        with patch("subprocess.run", return_value=completed(returncode=1)):
            assert DockerCompose.is_available() is False

    def test_false_on_timeout(self) -> None:
        with patch(
            "subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="docker", timeout=5),
        ):
            assert DockerCompose.is_available() is False


class TestServices:
    """``_services`` parses docker-compose ps --format json output."""

    def test_returns_empty_list_when_command_fails(self) -> None:
        compose = DockerCompose("/tmp/project")
        with patch.object(compose, "_compose", return_value=None):
            assert compose._services(timeout=5) == []

    def test_returns_empty_list_on_nonzero_returncode(self) -> None:
        compose = DockerCompose("/tmp/project")
        with patch.object(compose, "_compose", return_value=completed(returncode=1)):
            assert compose._services(timeout=5) == []

    def test_parses_json_lines_and_skips_malformed(self) -> None:
        compose = DockerCompose("/tmp/project")
        stdout = (
            '{"Name": "app", "State": "running"}\n'
            "not-json\n"
            "\n"
            '["not", "a", "dict"]\n'
            '{"Name": "db", "State": "exited"}'
        )
        with patch.object(compose, "_compose", return_value=completed(stdout=stdout)):
            services = compose._services(timeout=5)

        assert services == [
            {"Name": "app", "State": "running"},
            {"Name": "db", "State": "exited"},
        ]


class TestContainersRunning:
    """Every container in the project must report ``true`` for Running."""

    def test_false_when_ps_fails(self) -> None:
        compose = DockerCompose("/tmp/project")
        with patch.object(compose, "_compose", return_value=None):
            assert compose.containers_running() is False

    def test_false_when_no_containers(self) -> None:
        compose = DockerCompose("/tmp/project")
        with patch.object(compose, "_compose", return_value=completed(stdout="\n")):
            assert compose.containers_running() is False

    def test_true_when_all_containers_running(self) -> None:
        compose = DockerCompose("/tmp/project")
        with patch.object(
            compose, "_compose", return_value=completed(stdout="abc123\ndef456\n")
        ):
            with patch.object(compose, "_run", return_value=completed(stdout="true\n")):
                assert compose.containers_running() is True

    def test_false_when_inspect_fails(self) -> None:
        compose = DockerCompose("/tmp/project")
        with patch.object(
            compose, "_compose", return_value=completed(stdout="abc123\n")
        ):
            with patch.object(compose, "_run", return_value=None):
                assert compose.containers_running() is False

    def test_false_when_a_container_is_not_running(self) -> None:
        compose = DockerCompose("/tmp/project")
        with patch.object(
            compose, "_compose", return_value=completed(stdout="abc123\n")
        ):
            with patch.object(
                compose, "_run", return_value=completed(stdout="false\n")
            ):
                assert compose.containers_running() is False


class TestUp:
    """``up`` raises TimeoutExpired when the underlying command errors out."""

    def test_returns_result_on_success(self) -> None:
        compose = DockerCompose("/tmp/project")
        with patch.object(compose, "_compose", return_value=completed()):
            result = compose.up(timeout=30)
        assert result.returncode == 0

    def test_raises_timeout_when_command_fails(self) -> None:
        compose = DockerCompose("/tmp/project")
        with patch.object(compose, "_compose", return_value=None):
            with pytest.raises(subprocess.TimeoutExpired):
                compose.up(timeout=30)


class TestWaitUntilHealthy:
    """Polls until all services report running, or the deadline passes."""

    def test_returns_once_services_running(self) -> None:
        compose = DockerCompose("/tmp/project")
        with patch.object(compose, "_services", return_value=[{"State": "running"}]):
            with patch("time.sleep"):
                compose.wait_until_healthy(timeout=5)

    def test_times_out_when_never_healthy(self) -> None:
        compose = DockerCompose("/tmp/project")
        times = iter([0, 100])
        with patch.object(compose, "_services", return_value=[]):
            with patch("time.sleep"):
                with patch("time.time", side_effect=lambda: next(times, 100)):
                    compose.wait_until_healthy(timeout=1)


class TestVerifyServicesRunning:
    """DB and app services must both be reported as running."""

    def test_error_when_no_services(self) -> None:
        compose = DockerCompose("/tmp/project")
        with patch.object(compose, "_services", return_value=[]):
            assert compose.verify_services_running() == "Failed to check service status"

    def test_error_when_db_not_running(self) -> None:
        compose = DockerCompose("/tmp/project")
        services = [{"Name": "proj-app-1", "State": "running"}]
        with patch.object(compose, "_services", return_value=services):
            assert (
                compose.verify_services_running() == "Database service is not running"
            )

    def test_error_with_logs_when_app_not_running(self) -> None:
        compose = DockerCompose("/tmp/project")
        services = [{"Name": "proj-db-1", "State": "running"}]
        logs = completed(stdout="boot failure")
        with patch.object(compose, "_services", return_value=services):
            with patch.object(compose, "_compose", return_value=logs):
                message = compose.verify_services_running()
        assert message is not None
        assert "Application service is not running" in message
        assert "boot failure" in message

    def test_error_without_logs_when_logs_command_fails(self) -> None:
        compose = DockerCompose("/tmp/project")
        services = [{"Name": "proj-db-1", "State": "running"}]
        with patch.object(compose, "_services", return_value=services):
            with patch.object(compose, "_compose", return_value=None):
                message = compose.verify_services_running()
        assert message == "Application service is not running"

    def test_none_when_both_running(self) -> None:
        compose = DockerCompose("/tmp/project")
        services = [
            {"Name": "proj-db-1", "State": "running"},
            {"Name": "proj-app-1", "State": "running"},
        ]
        with patch.object(compose, "_services", return_value=services):
            assert compose.verify_services_running() is None


class TestExecTests:
    """The test invocation switches between scripts/test.sh and pytest."""

    def test_uses_test_script_when_requested(self) -> None:
        compose = DockerCompose("/tmp/project")
        with patch.object(compose, "_compose", return_value=completed()) as mock:
            compose.exec_tests(use_test_script=True)
        args = mock.call_args.args[0]
        assert "scripts/test.sh" in args

    def test_uses_pytest_by_default(self) -> None:
        compose = DockerCompose("/tmp/project")
        with patch.object(compose, "_compose", return_value=completed()) as mock:
            compose.exec_tests(use_test_script=False)
        args = mock.call_args.args[0]
        assert "pytest" in args


class TestCleanup:
    """Cleanup tears down compose services and prunes docker, ignoring errors."""

    def test_runs_down_and_prune(self) -> None:
        compose = DockerCompose("/tmp/project")
        with patch.object(compose, "_run", return_value=completed()) as mock_run:
            compose.cleanup()
        assert mock_run.call_count == 2
        first_args = mock_run.call_args_list[0].args[0]
        assert first_args[0] == COMPOSE_COMMAND
        second_args = mock_run.call_args_list[1].args[0]
        assert second_args == ["docker", "system", "prune", "-f"]
