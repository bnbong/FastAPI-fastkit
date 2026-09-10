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

from fastapi_fastkit.backend.inspection import docker as docker_module
from fastapi_fastkit.backend.inspection.docker import (
    COMPOSE_COMMAND,
    COMPOSE_PLUGIN_COMMAND,
    RECLAIM_IMAGE,
    DockerCompose,
)


@pytest.fixture(autouse=True)
def reset_compose_prefix() -> Any:
    """Keep the module-level compose prefix from leaking between testcases."""
    original = docker_module._compose_prefix
    yield
    docker_module._compose_prefix = original


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

    def test_keeps_docker_compose_command_by_default(self) -> None:
        with patch("subprocess.run", return_value=completed(returncode=0)):
            assert DockerCompose.is_available() is True
        assert DockerCompose.compose_command() == [COMPOSE_COMMAND]

    def test_falls_back_to_compose_plugin(self) -> None:
        # given - only ``docker --version`` and ``docker compose version`` work
        def fake_run(
            command: List[str], **kwargs: Any
        ) -> subprocess.CompletedProcess[str]:
            if command[0] == COMPOSE_COMMAND:
                raise OSError("not found")
            return completed(returncode=0)

        # when
        with patch("subprocess.run", side_effect=fake_run):
            available = DockerCompose.is_available()

        # then
        assert available is True
        assert DockerCompose.compose_command() == list(COMPOSE_PLUGIN_COMMAND)

    def test_false_when_no_compose_implementation(self) -> None:
        # given
        def fake_run(
            command: List[str], **kwargs: Any
        ) -> subprocess.CompletedProcess[str]:
            if command[:1] == ["docker"] and command[1:] == ["--version"]:
                return completed(returncode=0)
            return completed(returncode=1)

        # when / then
        with patch("subprocess.run", side_effect=fake_run):
            assert DockerCompose.is_available() is False

    def test_plugin_fallback_is_used_by_compose_invocations(self) -> None:
        # given
        compose = DockerCompose("/tmp/project")
        docker_module._compose_prefix = list(COMPOSE_PLUGIN_COMMAND)

        # when
        with patch.object(compose, "_run", return_value=completed()) as mock_run:
            compose._compose(["ps"], timeout=5)

        # then
        assert mock_run.call_args.args[0][:2] == ["docker", "compose"]


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

    def test_returns_empty_list_on_empty_output(self) -> None:
        compose = DockerCompose("/tmp/project")
        with patch.object(compose, "_compose", return_value=completed(stdout="  \n")):
            assert compose._services(timeout=5) == []

    def test_parses_single_json_array(self) -> None:
        # given - compose v2.18 and older print one JSON array
        compose = DockerCompose("/tmp/project")
        stdout = (
            '[{"Name": "app", "State": "running"}, '
            '{"Name": "db", "State": "running"}]'
        )

        # when
        with patch.object(compose, "_compose", return_value=completed(stdout=stdout)):
            services = compose._services(timeout=5)

        # then
        assert services == [
            {"Name": "app", "State": "running"},
            {"Name": "db", "State": "running"},
        ]

    def test_parses_single_json_object(self) -> None:
        compose = DockerCompose("/tmp/project")
        stdout = '{"Name": "app", "State": "running"}'
        with patch.object(compose, "_compose", return_value=completed(stdout=stdout)):
            assert compose._services(timeout=5) == [{"Name": "app", "State": "running"}]

    def test_skips_non_dict_entries_of_a_json_array(self) -> None:
        compose = DockerCompose("/tmp/project")
        stdout = '["not-a-dict", {"Name": "db", "State": "running"}]'
        with patch.object(compose, "_compose", return_value=completed(stdout=stdout)):
            assert compose._services(timeout=5) == [{"Name": "db", "State": "running"}]

    def test_ignores_interleaved_warning_lines(self) -> None:
        # given - compose may mix its own logs into stdout
        compose = DockerCompose("/tmp/project")
        stdout = (
            'time="2024-01-01T00:00:00Z" level=warning msg="deprecated"\n'
            '{"Name": "app", "State": "running"}\n'
            '{"Name": "db", "State": "running"}\n'
        )

        # when
        with patch.object(compose, "_compose", return_value=completed(stdout=stdout)):
            services = compose._services(timeout=5)

        # then
        assert services == [
            {"Name": "app", "State": "running"},
            {"Name": "db", "State": "running"},
        ]

    def test_ignores_warning_lines_around_a_json_array(self) -> None:
        compose = DockerCompose("/tmp/project")
        stdout = (
            'time="2024-01-01T00:00:00Z" level=warning msg="deprecated"\n'
            '[{"Name": "app", "State": "running"}]\n'
        )
        with patch.object(compose, "_compose", return_value=completed(stdout=stdout)):
            assert compose._services(timeout=5) == [{"Name": "app", "State": "running"}]

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
            with (
                patch("os.getuid", return_value=1000, create=True),
                patch("os.getgid", return_value=1000, create=True),
            ):
                compose.cleanup()
        assert mock_run.call_count == 3
        reclaim_args = mock_run.call_args_list[0].args[0]
        assert reclaim_args[:3] == ["docker", "run", "--rm"]
        assert RECLAIM_IMAGE in reclaim_args
        assert reclaim_args[-4:] == ["chown", "-R", "1000:1000", "/mnt"]
        second_args = mock_run.call_args_list[1].args[0]
        assert second_args[0] == COMPOSE_COMMAND
        third_args = mock_run.call_args_list[2].args[0]
        assert third_args == ["docker", "system", "prune", "-f"]

    def test_ownership_reclaim_is_skipped_for_root(self) -> None:
        compose = DockerCompose("/tmp/project")
        with patch.object(compose, "_run", return_value=completed()) as mock_run:
            with patch("os.getuid", return_value=0, create=True):
                compose.reclaim_bind_mount_ownership()
        mock_run.assert_not_called()

    def test_ownership_reclaim_mounts_the_project_directory(self) -> None:
        compose = DockerCompose("/tmp/project")
        with patch.object(compose, "_run", return_value=completed()) as mock_run:
            with (
                patch("os.getuid", return_value=501, create=True),
                patch("os.getgid", return_value=20, create=True),
            ):
                compose.reclaim_bind_mount_ownership()
        args = mock_run.call_args.args[0]
        assert "/tmp/project:/mnt" in args
        assert "501:20" in args


class TestPublishedPort:
    """``published_port`` reads host-bound ports out of ``ps --format json``."""

    def _services(self, entries: List[Any]) -> Any:
        return patch.object(DockerCompose, "_services", return_value=entries)

    def test_prefers_the_app_service(self) -> None:
        # given
        compose = DockerCompose("/tmp/project")
        entries = [
            {
                "Service": "db",
                "Name": "proj-db-1",
                "Publishers": [{"PublishedPort": 5432, "TargetPort": 5432}],
            },
            {
                "Service": "app",
                "Name": "proj-app-1",
                "Publishers": [{"PublishedPort": 8000, "TargetPort": 8000}],
            },
        ]

        # when
        with self._services(entries):
            port = compose.published_port()

        # then
        assert port == 8000

    def test_ignores_unpublished_entries(self) -> None:
        # given
        compose = DockerCompose("/tmp/project")
        entries = [
            {
                "Service": "app",
                "Name": "proj-app-1",
                "Publishers": [
                    {"PublishedPort": 0, "TargetPort": 8000},
                    {"PublishedPort": "32770", "TargetPort": 8000},
                ],
            }
        ]

        # when
        with self._services(entries):
            port = compose.published_port()

        # then
        assert port == 32770

    def test_falls_back_to_any_service_with_a_published_port(self) -> None:
        # given: no service name matches the hint
        compose = DockerCompose("/tmp/project")
        entries = [
            {
                "Service": "web",
                "Name": "proj-web-1",
                "Publishers": [{"PublishedPort": 9000}],
            }
        ]

        # when
        with self._services(entries):
            port = compose.published_port()

        # then
        assert port == 9000

    def test_returns_none_without_publishers(self) -> None:
        # given
        compose = DockerCompose("/tmp/project")
        entries = [
            {"Service": "app", "Name": "proj-app-1", "Publishers": []},
            {"Service": "db", "Name": "proj-db-1"},
        ]

        # when
        with self._services(entries):
            port = compose.published_port()

        # then
        assert port is None

    def test_returns_none_when_ps_reports_nothing(self) -> None:
        # given
        compose = DockerCompose("/tmp/project")

        # when
        with self._services([]):
            port = compose.published_port()

        # then
        assert port is None

    def test_malformed_publisher_entries_are_skipped(self) -> None:
        # given
        compose = DockerCompose("/tmp/project")
        entries = [
            {
                "Service": "app",
                "Name": "proj-app-1",
                "Publishers": ["nonsense", {"PublishedPort": "not-a-number"}],
            }
        ]

        # when
        with self._services(entries):
            port = compose.published_port()

        # then
        assert port is None
