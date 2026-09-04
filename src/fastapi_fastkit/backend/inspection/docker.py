# --------------------------------------------------------------------------
# Docker Compose orchestration for templates that declare requires_docker.
#
# ``DockerCompose`` owns every ``docker``/``docker-compose`` invocation so the
# test strategies stay free of process plumbing.
#
# @author bnbong
# --------------------------------------------------------------------------
import json
import subprocess
import time
from typing import Any, Dict, List, Optional, Sequence

from fastapi_fastkit.utils.logging import debug_log

COMPOSE_COMMAND = "docker-compose"
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

    def _compose(
        self, args: Sequence[str], timeout: int
    ) -> Optional[subprocess.CompletedProcess[str]]:
        """Run a docker-compose subcommand against the configured compose file."""
        return self._run(
            [COMPOSE_COMMAND, "-f", self.compose_file, *args], timeout=timeout
        )

    @staticmethod
    def is_available() -> bool:
        """Check that both docker and docker-compose respond."""
        for command in (["docker", "--version"], [COMPOSE_COMMAND, "--version"]):
            try:
                result = subprocess.run(
                    command, capture_output=True, text=True, timeout=SHORT_TIMEOUT
                )
            except (subprocess.TimeoutExpired, OSError):
                return False
            if result.returncode != 0:
                return False
        return True

    def _services(self, timeout: int) -> List[Dict[str, Any]]:
        """Return the parsed ``docker-compose ps --format json`` entries."""
        result = self._compose(["ps", "--format", "json"], timeout=timeout)
        if result is None or result.returncode != 0:
            return []

        services: List[Dict[str, Any]] = []
        for line in result.stdout.strip().split("\n"):
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
            raise subprocess.TimeoutExpired(COMPOSE_COMMAND, timeout)
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

    def exec_tests(
        self, use_test_script: bool
    ) -> Optional[subprocess.CompletedProcess[str]]:
        """Run the template's tests inside the app container."""
        if use_test_script:
            command = ["exec", "-T", "app", "bash", "scripts/test.sh"]
        else:
            command = ["exec", "-T", "app", "python", "-m", "pytest", "tests/", "-v"]
        return self._compose(command, timeout=TEST_TIMEOUT)

    def cleanup(self) -> None:
        """Tear down services and volumes, ignoring any failure."""
        debug_log("Cleaning up Docker services", "info")
        self._run(
            [COMPOSE_COMMAND, "down", "-v", "--remove-orphans"], timeout=CLEANUP_TIMEOUT
        )
        self._run(["docker", "system", "prune", "-f"], timeout=STATUS_TIMEOUT)
