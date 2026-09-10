# --------------------------------------------------------------------------
# HTTP smoke test for a generated project.
#
# Booting the application is the only honest way to prove a template works:
# a substring search for "FastAPI" in main.py cannot tell a working app from
# one that raises on import. The generated project is started with uvicorn in
# a subprocess on a free port; ``/docs`` must answer 200 and ``/health``, when
# the template exposes one, must answer 200 as well.
#
# @author bnbong
# --------------------------------------------------------------------------
import os
import signal
import socket
import subprocess
import tempfile
import time
import tomllib
import urllib.error
import urllib.request
from typing import IO, List, Optional, Tuple

from fastapi_fastkit.utils.logging import debug_log

from .context import InspectionContext

#: Probed in order when no explicit app_module is declared.
MAIN_MODULE_CANDIDATES = [
    ("src/app/main.py", "src.app.main"),
    ("src/main.py", "src.main"),
    ("app/main.py", "app.main"),
    ("main.py", "main"),
]
DEFAULT_APP_ATTRIBUTE = "app"
SHUTDOWN_TIMEOUT = 10

#: How many ports to try before giving up. ``find_free_port`` releases the
#: port before uvicorn binds it, so another process can win the race; on a
#: busy CI machine that is common enough to be worth retrying.
PORT_ATTEMPTS = 3

#: Bytes of captured server output attached to a failure report.
LOG_TAIL_BYTES = 4000


def find_free_port() -> int:
    """Reserve and release a port so uvicorn can bind it."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        port: int = sock.getsockname()[1]
    return port


def _app_module_from_pyproject(ctx: InspectionContext) -> Optional[str]:
    """Read ``[tool.fastapi-fastkit].app_module`` from the generated project."""
    pyproject_path = ctx.temp_path("pyproject.toml")
    if not os.path.exists(pyproject_path):
        return None
    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
    except (OSError, tomllib.TOMLDecodeError, UnicodeDecodeError) as e:
        debug_log(f"Could not read generated pyproject.toml: {e}", "warning")
        return None
    value = data.get("tool", {}).get("fastapi-fastkit", {}).get("app_module")
    return str(value) if value else None


def _app_module_from_template_config(ctx: InspectionContext) -> Optional[str]:
    """Read ``app_module`` from template-config.yml, if the template ships one."""
    if not ctx.template_config:
        return None
    value = ctx.template_config.get("app_module")
    return str(value) if value else None


def _app_module_from_layout(ctx: InspectionContext) -> Optional[str]:
    """Fall back to the conventional main module locations."""
    for relative_path, dotted in MAIN_MODULE_CANDIDATES:
        if os.path.exists(ctx.temp_path(*relative_path.split("/"))):
            return f"{dotted}:{DEFAULT_APP_ATTRIBUTE}"
    return None


def resolve_app_module(ctx: InspectionContext) -> Optional[str]:
    """Determine the ``module:attribute`` uvicorn target for the project.

    Resolution order: generated ``pyproject.toml`` metadata, then
    ``template-config.yml``, then the conventional file layout.
    """
    for resolver in (
        _app_module_from_pyproject,
        _app_module_from_template_config,
        _app_module_from_layout,
    ):
        value = resolver(ctx)
        if value:
            if ":" not in value:
                value = f"{value}:{DEFAULT_APP_ATTRIBUTE}"
            debug_log(f"Resolved app module: {value}", "info")
            return value
    return None


def _probe(url: str, timeout: int = 5) -> Optional[int]:
    """GET ``url`` and return its status code, or ``None`` when unreachable."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            status: int = response.status
            return status
    except urllib.error.HTTPError as e:
        return int(e.code)
    except (urllib.error.URLError, OSError, TimeoutError):
        return None


def _wait_for_server(
    process: Optional["subprocess.Popen[bytes]"], base_url: str, timeout: int
) -> Tuple[bool, str]:
    """Poll ``/docs`` until the server answers, the process dies or time runs out.

    ``process`` is ``None`` when the server is not ours to watch - a container
    started by the Docker strategy, for one - in which case only the timeout
    bounds the wait.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        if process is not None and process.poll() is not None:
            return False, "server process exited before becoming reachable"
        status = _probe(f"{base_url}/docs")
        if status is not None:
            if status == 200:
                return True, ""
            return False, f"/docs returned HTTP {status} (expected 200)"
        time.sleep(0.5)
    return False, f"server did not become reachable within {timeout}s"


def _signal_group(process: "subprocess.Popen[bytes]", sig: int) -> bool:
    """Signal the server's whole process group, if it has one of its own.

    uvicorn spawns reloader / worker children, and signalling only the
    parent leaves them holding the port. The process is started with
    ``start_new_session=True`` so the group id equals its pid.

    Only a group we created ourselves is ever signalled: the pid must be a
    real positive integer and must be its own group leader. Anything else --
    a mocked process object, a pid that has been reaped and rejoined another
    group, the init group, or the group this interpreter itself belongs to --
    falls back to signalling the single process, because signalling the wrong
    group would tear down unrelated processes (a CI runner, for one).

    :return: True when the group was signalled, False to fall back
    """
    if not hasattr(os, "killpg"):  # pragma: no cover - non-POSIX
        return False

    pid = process.pid
    if type(pid) is not int or pid <= 1:
        debug_log(f"Refusing to signal process group for pid {pid!r}", "debug")
        return False

    try:
        pgid = os.getpgid(pid)
    except OSError as e:
        debug_log(f"Could not read smoke test process group: {e}", "debug")
        return False

    # start_new_session=True makes the child its own group leader, so a pgid
    # that differs from the pid means the process is sharing someone else's
    # group -- never ours to signal.
    if pgid != pid or pgid <= 1 or pgid == os.getpgrp():
        debug_log(
            f"Smoke test process {pid} is not its own group leader "
            f"(pgid {pgid}); signalling the process only",
            "debug",
        )
        return False

    try:
        os.killpg(pgid, sig)
        return True
    except OSError as e:
        debug_log(f"Could not signal smoke test process group: {e}", "debug")
        return False


def _terminate(process: "subprocess.Popen[bytes]") -> None:
    """Stop the server process (and its group), escalating to SIGKILL."""
    if process.poll() is not None:
        return

    if not _signal_group(process, signal.SIGTERM):
        process.terminate()
    try:
        process.wait(timeout=SHUTDOWN_TIMEOUT)
        return
    except subprocess.TimeoutExpired:
        pass

    if not _signal_group(process, signal.SIGKILL):
        process.kill()
    try:
        process.wait(timeout=SHUTDOWN_TIMEOUT)
    except subprocess.TimeoutExpired:  # pragma: no cover - defensive
        debug_log("Smoke test server could not be killed", "warning")


#: Phrases uvicorn / asyncio emit when the chosen port was taken between
#: ``find_free_port`` releasing it and uvicorn binding it.
_PORT_CONFLICT_MARKERS = (
    "address already in use",
    "error while attempting to bind on address",
    "only one usage of each socket address",
)


def _is_port_conflict(output: str) -> bool:
    """Return True when captured server output shows a failed port bind."""
    lowered = output.lower()
    return any(marker in lowered for marker in _PORT_CONFLICT_MARKERS)


def _read_log_tail(log_file: IO[bytes]) -> str:
    """Return the tail of the captured server output."""
    try:
        log_file.flush()
        size = os.fstat(log_file.fileno()).st_size
        log_file.seek(max(0, size - LOG_TAIL_BYTES))
        return log_file.read().decode("utf-8", errors="replace").strip()
    except OSError as e:  # pragma: no cover - defensive
        debug_log(f"Could not read smoke test server log: {e}", "warning")
        return ""


def _check_health_endpoint(ctx: InspectionContext, base_url: str) -> Optional[str]:
    """Probe ``/health``; return a failure message, or ``None`` when acceptable.

    A template without a ``/health`` route answers 404, which is fine; an
    unreachable endpoint is only worth a warning, but a route that exists and
    answers with anything other than 200 is a real failure.
    """
    health_status = _probe(f"{base_url}/health")
    if health_status is None:
        ctx.add_warning("Smoke test: /health did not respond")
    elif health_status == 404:
        debug_log("Template exposes no /health endpoint, skipping", "info")
    elif health_status != 200:
        return (
            f"Smoke test failed: /health returned HTTP {health_status} (expected 200)"
        )
    return None


def run_http_smoke(ctx: InspectionContext, base_url: str) -> bool:
    """Verify the HTTP surface of a server someone else already started.

    Used by the Docker strategy, which has the real application running in a
    container: probing its published port is more honest than booting a second
    copy on the host, and templates that require Docker never get a host venv
    to boot one with in the first place.
    """
    debug_log(f"Running smoke test against {base_url}", "info")
    reachable, reason = _wait_for_server(None, base_url, ctx.options.smoke_timeout)
    if not reachable:
        ctx.add_error(f"Smoke test failed: {reason}")
        return False

    failure = _check_health_endpoint(ctx, base_url)
    if failure:
        ctx.add_error(failure)
        return False

    debug_log("Smoke test passed", "info")
    return True


def _requires_docker(ctx: InspectionContext) -> bool:
    """Whether the template declares that it can only run under Docker."""
    return bool((ctx.template_config or {}).get("requires_docker", False))


def check_smoke_test(ctx: InspectionContext) -> bool:
    """Boot the generated project and verify its HTTP surface."""
    if not ctx.options.run_smoke_test:
        debug_log("Smoke test disabled", "info")
        return True

    if ctx.smoke_result is not None:
        debug_log("Reusing the smoke test result recorded while testing", "info")
        return ctx.smoke_result

    python_executable = ctx.python_executable()
    if not python_executable or not os.path.exists(python_executable):
        if _requires_docker(ctx):
            ctx.add_warning(
                "smoke test skipped: Docker template without published port"
            )
            return True
        ctx.add_error(
            "Smoke test requires an installed environment, but no virtual "
            "environment was prepared for the generated project"
        )
        return False

    app_module = resolve_app_module(ctx)
    if not app_module:
        ctx.add_error(
            "Could not determine the ASGI app module: declare "
            "[tool.fastapi-fastkit].app_module or ship a conventional main.py"
        )
        return False

    env = os.environ.copy()
    env["PYTHONPATH"] = ctx.temp_dir + os.pathsep + env.get("PYTHONPATH", "")

    last_failure = ""
    for attempt in range(1, PORT_ATTEMPTS + 1):
        port = find_free_port()
        base_url = f"http://127.0.0.1:{port}"
        command: List[str] = [
            python_executable,
            "-m",
            "uvicorn",
            app_module,
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ]

        debug_log(f"Starting smoke test server: {' '.join(command)}", "info")

        # The server's output goes to a temp file rather than a pipe: uvicorn
        # keeps logging for as long as it runs, and a pipe nobody drains fills
        # its buffer and blocks the server mid-request.
        with tempfile.TemporaryFile() as log_file:
            try:
                process = subprocess.Popen(
                    command,
                    cwd=ctx.temp_dir,
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    env=env,
                    # Own process group, so terminating the server also stops
                    # any worker it spawned instead of orphaning it.
                    start_new_session=True,
                )
            except OSError as e:
                ctx.add_error(f"Failed to start the application server: {e}")
                return False

            try:
                reachable, reason = _wait_for_server(
                    process, base_url, ctx.options.smoke_timeout
                )
                if not reachable:
                    output = _read_log_tail(log_file)
                    last_failure = f"Smoke test failed: {reason}\n{output}".rstrip()
                    if _is_port_conflict(output) and attempt < PORT_ATTEMPTS:
                        debug_log(
                            f"Port {port} was taken before uvicorn bound it; "
                            f"retrying on another port ({attempt}/{PORT_ATTEMPTS})",
                            "warning",
                        )
                        continue
                    ctx.add_error(last_failure)
                    return False

                failure = _check_health_endpoint(ctx, base_url)
                if failure:
                    ctx.add_error(f"{failure}\n{_read_log_tail(log_file)}".rstrip())
                    return False
            finally:
                _terminate(process)

        debug_log("Smoke test passed", "info")
        return True

    ctx.add_error(last_failure or "Smoke test failed: no free port could be bound")
    return False
