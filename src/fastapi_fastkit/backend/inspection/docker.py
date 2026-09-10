# --------------------------------------------------------------------------
# Docker Compose orchestration for templates that declare requires_docker.
#
# ``DockerCompose`` owns every ``docker``/``docker-compose`` invocation so the
# test strategies stay free of process plumbing.
#
# @author bnbong
# --------------------------------------------------------------------------
import json
import os
import subprocess
import time
from typing import Any, Dict, List, Optional, Sequence

from fastapi_fastkit.utils.logging import debug_log

COMPOSE_COMMAND = "docker-compose"
#: Fallback for hosts that only ship the ``docker compose`` CLI plugin.
COMPOSE_PLUGIN_COMMAND = ["docker", "compose"]
#: Resolved compose invocation, switched by :meth:`DockerCompose.is_available`.
_compose_prefix: List[str] = [COMPOSE_COMMAND]
#: Throwaway image used to give bind-mounted files back to the host user.
RECLAIM_IMAGE = "alpine:3.20"
SHORT_TIMEOUT = 10
STATUS_TIMEOUT = 30
CLEANUP_TIMEOUT = 60
TEST_TIMEOUT = 300


class DockerCompose:
    """Thin wrapper around the docker-compose CLI for one project directory."""

    def __init__(self, project_dir: str, compose_file: str = "docker-compose.yml"):
        self.project_dir = project_dir
        self.compose_file = compose_file

    def _run(
        self, args: Sequence[str], timeout: int
    ) -> Optional[subprocess.CompletedProcess[str]]:
        """Run a command in the project directory, returning ``None`` on failure."""
        try:
            return subprocess.run(
                list(args),
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except (subprocess.TimeoutExpired, OSError) as e:
            debug_log(f"Command {' '.join(args)} failed: {e}", "warning")
            return None

    @staticmethod
    def compose_command() -> List[str]:
        """Return the compose invocation resolved by :meth:`is_available`."""
        return list(_compose_prefix)

    def _compose(
        self, args: Sequence[str], timeout: int
    ) -> Optional[subprocess.CompletedProcess[str]]:
        """Run a docker-compose subcommand against the configured compose file."""
        return self._run(
            [*self.compose_command(), "-f", self.compose_file, *args], timeout=timeout
        )

    @staticmethod
    def _probe(command: Sequence[str]) -> bool:
        """Return whether ``command`` exits successfully."""
        try:
            result = subprocess.run(
                list(command), capture_output=True, text=True, timeout=SHORT_TIMEOUT
            )
        except (subprocess.TimeoutExpired, OSError):
            return False
        return result.returncode == 0

    @staticmethod
    def is_available() -> bool:
        """Check that docker responds and a compose implementation exists.

        ``docker-compose`` stays the preferred command; hosts that only ship
        the ``docker compose`` CLI plugin fall back to it.
        """
        global _compose_prefix

        if not DockerCompose._probe(["docker", "--version"]):
            return False
        if DockerCompose._probe([COMPOSE_COMMAND, "--version"]):
            _compose_prefix = [COMPOSE_COMMAND]
            return True
        if DockerCompose._probe([*COMPOSE_PLUGIN_COMMAND, "version"]):
            debug_log("Falling back to the 'docker compose' CLI plugin", "info")
            _compose_prefix = list(COMPOSE_PLUGIN_COMMAND)
            return True
        return False

    def _services(self, timeout: int) -> List[Dict[str, Any]]:
        """Return the parsed ``docker-compose ps --format json`` entries."""
        result = self._compose(["ps", "--format", "json"], timeout=timeout)
        if result is None or result.returncode != 0:
            return []

        # Compose sometimes interleaves ``time="..." level=warning`` log lines
        # with the JSON payload, so only JSON-looking lines are considered.
        payload = "\n".join(
            line
            for line in result.stdout.splitlines()
            if line.strip().startswith(("[", "{"))
        ).strip()
        if not payload:
            return []

        # Compose < v2.21 prints a single JSON array, newer versions print one
        # JSON object per line (NDJSON).
        try:
            document = json.loads(payload)
        except json.JSONDecodeError:
            return DockerCompose._parse_json_lines(payload)

        if isinstance(document, dict):
            return [document]
        if isinstance(document, list):
            return [entry for entry in document if isinstance(entry, dict)]
        return []

    @staticmethod
    def _parse_json_lines(payload: str) -> List[Dict[str, Any]]:
        """Parse NDJSON output, skipping malformed or non-object lines."""
        services: List[Dict[str, Any]] = []
        for line in payload.split("\n"):
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(entry, dict):
                services.append(entry)
        return services

    def containers_running(self) -> bool:
        """Check whether every container of the project is already up."""
        result = self._compose(["ps", "-q"], timeout=STATUS_TIMEOUT)
        if result is None or result.returncode != 0:
            return False

        container_ids = [line.strip() for line in result.stdout.strip().split("\n")]
        container_ids = [cid for cid in container_ids if cid]
        if not container_ids:
            return False

        for container_id in container_ids:
            status = self._run(
                ["docker", "inspect", "-f", "{{.State.Running}}", container_id],
                timeout=SHORT_TIMEOUT,
            )
            if status is None or status.returncode != 0:
                return False
            if status.stdout.strip() != "true":
                return False
        return True

    def up(self, timeout: int) -> subprocess.CompletedProcess[str]:
        """Build and start the compose services in the background."""
        result = self._compose(["up", "-d", "--build"], timeout=timeout)
        if result is None:
            raise subprocess.TimeoutExpired(" ".join(self.compose_command()), timeout)
        return result

    def wait_until_healthy(self, timeout: int) -> None:
        """Block until every service reports ``running`` or ``timeout`` elapses."""
        debug_log("Waiting for services to be healthy...", "info")
        deadline = time.time() + timeout

        while time.time() < deadline:
            services = self._services(timeout=SHORT_TIMEOUT)
            if services and all(
                service.get("State") == "running" for service in services
            ):
                debug_log("All services are running", "info")
                # Give the application a moment to finish booting.
                time.sleep(10)
                return

            debug_log("Services not ready yet, waiting...", "info")
            time.sleep(5)

        debug_log(
            f"Services did not become healthy within {timeout} seconds", "warning"
        )

    def verify_services_running(self) -> Optional[str]:
        """Return ``None`` when db and app are up, else a descriptive error."""
        services = self._services(timeout=STATUS_TIMEOUT)
        if not services:
            return "Failed to check service status"

        db_running = False
        app_running = False
        for service in services:
            name = str(service.get("Name", ""))
            state = str(service.get("State", ""))
            debug_log(f"Service {name}: {state}", "info")
            if "db" in name and state == "running":
                db_running = True
            elif "app" in name and state == "running":
                app_running = True

        if not db_running:
            return "Database service is not running"
        if not app_running:
            logs = self._compose(
                ["logs", "--tail", "50", "app"], timeout=STATUS_TIMEOUT
            )
            if logs is not None and logs.returncode == 0:
                return (
                    "Application service is not running. " f"Logs: {logs.stdout[-500:]}"
                )
            return "Application service is not running"

        debug_log("All required services are running", "info")
        return None

    def published_port(self, service_hint: str = "app") -> Optional[int]:
        """Return the host port the app container publishes, if any.

        ``docker-compose ps --format json`` reports a ``Publishers`` list per
        service; an entry with a non-zero ``PublishedPort`` is a port bound on
        the host, which is what a smoke test can reach. Services whose name
        contains ``service_hint`` are preferred, so a database that happens to
        publish a port is never mistaken for the application.
        """
        services = self._services(timeout=STATUS_TIMEOUT)
        if not services:
            return None

        def _matches(service: Dict[str, Any]) -> bool:
            name = f"{service.get('Service', '')} {service.get('Name', '')}"
            return service_hint in name

        for candidate in (
            [entry for entry in services if _matches(entry)],
            services,
        ):
            for service in candidate:
                port = self._first_published_port(service)
                if port is not None:
                    return port
        return None

    @staticmethod
    def _first_published_port(service: Dict[str, Any]) -> Optional[int]:
        """Extract the first host-bound port from one ``ps`` entry."""
        publishers = service.get("Publishers")
        if not isinstance(publishers, list):
            return None
        for publisher in publishers:
            if not isinstance(publisher, dict):
                continue
            try:
                port = int(publisher.get("PublishedPort", 0))
            except (TypeError, ValueError):
                continue
            if port > 0:
                return port
        return None

    def exec_tests(
        self, use_test_script: bool
    ) -> Optional[subprocess.CompletedProcess[str]]:
        """Run the template's tests inside the app container."""
        if use_test_script:
            command = ["exec", "-T", "app", "bash", "scripts/test.sh"]
        else:
            command = ["exec", "-T", "app", "python", "-m", "pytest", "tests/", "-v"]
        return self._compose(command, timeout=TEST_TIMEOUT)

    def reclaim_bind_mount_ownership(self) -> None:
        """Give the bind-mounted project directory back to the host user.

        Containers run as root, so a test run inside the stack leaves
        root-owned artefacts (``__pycache__``, ``.pytest_cache``, ...) in the
        mounted project. Later host-side steps and the temp directory cleanup
        cannot touch those and fail with a PermissionError, so the ownership
        is reset from inside a throwaway container. Best effort: a failure
        here is never worth failing an inspection over.
        """
        if not hasattr(os, "getuid"):  # pragma: no cover - Windows hosts
            return

        uid, gid = os.getuid(), os.getgid()
        if uid == 0:
            return

        debug_log("Reclaiming ownership of bind-mounted project files", "info")
        self._run(
            [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{self.project_dir}:/mnt",
                RECLAIM_IMAGE,
                "chown",
                "-R",
                f"{uid}:{gid}",
                "/mnt",
            ],
            timeout=CLEANUP_TIMEOUT,
        )

    def cleanup(self) -> None:
        """Tear down services and volumes, ignoring any failure."""
        debug_log("Cleaning up Docker services", "info")
        self.reclaim_bind_mount_ownership()
        self._run(
            [*self.compose_command(), "down", "-v", "--remove-orphans"],
            timeout=CLEANUP_TIMEOUT,
        )
        self._run(["docker", "system", "prune", "-f"], timeout=STATUS_TIMEOUT)
