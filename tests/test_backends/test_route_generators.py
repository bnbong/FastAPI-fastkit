"""Tests for route generators."""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Optional
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from fastapi_fastkit.backend.main import add_new_route, write_fastkit_metadata
from fastapi_fastkit.backend.route_generators import resolve_route_layout
from fastapi_fastkit.backend.transducer import copy_and_convert_template
from fastapi_fastkit.cli import fastkit_cli
from fastapi_fastkit.core.exceptions import BackendExceptions
from fastapi_fastkit.core.settings import settings


def make_project(
    root: Path,
    nested: bool = True,
    preset: Optional[str] = "domain-starter",
    aggregator: bool = True,
    anchors: bool = True,
) -> Path:
    """Create a test project."""
    package = root / "src" / "app" if nested else root / "src"
    package.mkdir(parents=True)
    prefix = "src.app" if nested else "src"
    (root / "src" / "__init__.py").write_text("", encoding="utf-8")
    (package / "__init__.py").write_text("", encoding="utf-8")
    import_anchor = "# fastkit:imports\n" if anchors else ""
    route_anchor = "# fastkit:routes\n" if anchors else ""
    main = (
        f"from fastapi import FastAPI\n{import_anchor}\napp = FastAPI()\n{route_anchor}"
    )
    if aggregator:
        api = package / "api"
        api.mkdir()
        (api / "__init__.py").write_text("", encoding="utf-8")
        router_name = "router" if nested else "api"
        (api / f"{router_name}.py").write_text(
            f"from fastapi import APIRouter\n{import_anchor}\n"
            f"api_router = APIRouter()\n{route_anchor}",
            encoding="utf-8",
        )
        main = (
            "from fastapi import FastAPI\n"
            f"from {prefix}.api.{router_name} import api_router\n{import_anchor}\n"
            f"app = FastAPI()\n{route_anchor}"
            'app.include_router(api_router, prefix="/api/v1")\n'
        )
    (package / "main.py").write_text(main, encoding="utf-8")
    metadata = (
        '[project]\nname = "test-project"\nversion = "0.1.0"\n'
        "[tool.fastapi-fastkit]\nmanaged = true\n"
        f'app_module = "{prefix}.main:app"\n'
    )
    if preset is not None:
        metadata += f"preset = {json.dumps(preset)}\n"
    (root / "pyproject.toml").write_text(metadata, encoding="utf-8")
    return package


@pytest.mark.parametrize(
    "preset, expected",
    [
        ("domain-starter", "domain"),
        ("classic-layered", "classic-layer"),
        ("minimal", "classic-layer"),
        ("single-module", "classic-layer"),
        (None, "classic-layer"),
        ("", "classic-layer"),
    ],
)
def test_layout_from_preset(
    tmp_path: Path, preset: Optional[str], expected: str
) -> None:
    make_project(tmp_path, preset=preset)
    assert resolve_route_layout(str(tmp_path)) == expected


@pytest.mark.parametrize("layout", ["classic-layer", "domain"])
@pytest.mark.parametrize(
    "preset", ["domain-starter", "classic-layered", None, "unknown"]
)
def test_explicit_layout_overrides_preset(
    tmp_path: Path, layout: str, preset: Optional[str]
) -> None:
    make_project(tmp_path, preset=preset)
    with patch("fastapi_fastkit.backend.route_generators.print_warning") as warning:
        assert resolve_route_layout(str(tmp_path), layout) == layout
    warning.assert_not_called()


@pytest.mark.parametrize(
    "content", [None, "not valid [toml", "[project]\nname = 'legacy'\n"]
)
def test_missing_or_unreadable_metadata_falls_back(
    tmp_path: Path, content: Optional[str]
) -> None:
    if content is not None:
        (tmp_path / "pyproject.toml").write_text(content, encoding="utf-8")
    assert resolve_route_layout(str(tmp_path)) == "classic-layer"


def test_unknown_preset_warns(tmp_path: Path) -> None:
    make_project(tmp_path, preset="future-preset")
    with patch("fastapi_fastkit.backend.route_generators.print_warning") as warning:
        assert resolve_route_layout(str(tmp_path)) == "classic-layer"
    warning.assert_called_once()
    assert "future-preset" in warning.call_args.args[0]


def test_invalid_layout_does_not_write(tmp_path: Path) -> None:
    make_project(tmp_path)
    before = snapshot(tmp_path)
    with pytest.raises(BackendExceptions, match="Unknown route layout"):
        add_new_route(str(tmp_path), "users", layout="invalid")
    assert snapshot(tmp_path) == before


def snapshot(root: Path) -> dict[str, bytes]:
    """Read project files for comparison."""
    return {
        str(path.relative_to(root)): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }


def test_shipped_items_domain_is_preserved(tmp_path: Path) -> None:
    """Keep the starter items domain unchanged."""
    template = Path(settings.FASTKIT_TEMPLATE_ROOT) / "fastapi-domain-starter"
    copy_and_convert_template(str(template), str(tmp_path))
    write_fastkit_metadata(
        str(tmp_path),
        {"preset": "domain-starter", "app_module": "src.app.main:app"},
    )
    before = snapshot(tmp_path)
    add_new_route(str(tmp_path), "items")
    assert snapshot(tmp_path) == before
    add_new_route(str(tmp_path), "users")
    for name, content in before.items():
        if name != str(Path("src/app/api/router.py")):
            assert (tmp_path / name).read_bytes() == content
    router = (tmp_path / "src/app/api/router.py").read_text(encoding="utf-8")
    assert (
        router.count(
            'api_router.include_router(items_router.router, prefix="/items", tags=["items"])'
        )
        == 1
    )
    assert (
        router.count(
            'api_router.include_router(users_router.router, prefix="/users", tags=["users"])'
        )
        == 1
    )

    if all(importlib.util.find_spec(name) for name in ("fastapi", "httpx")):
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                """
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.app.api.router import api_router
app = FastAPI()
app.include_router(api_router, prefix="/api/v1")
client = TestClient(app)
assert client.get("/api/v1/items").status_code == 200
created = client.post("/api/v1/items", json={"name": "Mug", "price": 9.5})
assert created.status_code == 201
assert client.get("/api/v1/items/" + str(created.json()["id"])).status_code == 200
paths = app.openapi()["paths"]
assert paths["/api/v1/items"]["get"]["tags"] == ["items"]
assert "/api/v1/items/items" not in paths
""",
            ],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("nested", [False, True])
@pytest.mark.parametrize("layout", ["classic-layer", "domain"])
def test_generation_preserves_edits_and_restores_missing_files(
    tmp_path: Path, nested: bool, layout: str
) -> None:
    package = make_project(tmp_path, nested=nested)
    metadata = (tmp_path / "pyproject.toml").read_bytes()
    add_new_route(str(tmp_path), "users", layout=layout)
    if layout == "domain":
        edited = package / "domains/users/service.py"
        missing = package / "domains/users/schemas.py"
        assert not (package / "crud").exists()
        assert not (package / "schemas").exists()
        assert not (package / "api/routes").exists()
    else:
        edited = package / "crud/users.py"
        missing = package / "schemas/users.py"
        assert not (package / "domains").exists()
    edited.write_text("# User-edited implementation\n", encoding="utf-8")
    before = snapshot(tmp_path)
    add_new_route(str(tmp_path), "users", layout=layout)
    assert snapshot(tmp_path) == before
    missing.unlink()
    add_new_route(str(tmp_path), "users", layout=layout)
    assert snapshot(tmp_path) == before
    assert (tmp_path / "pyproject.toml").read_bytes() == metadata


@pytest.mark.parametrize(
    "first, second", [("domain", "classic-layer"), ("classic-layer", "domain")]
)
def test_same_name_layouts_can_coexist(tmp_path: Path, first: str, second: str) -> None:
    package = make_project(tmp_path)
    add_new_route(str(tmp_path), "users", layout=first)
    add_new_route(str(tmp_path), "users", layout=second)
    assert (package / "domains/users/router.py").exists()
    assert (package / "api/routes/users.py").exists()
    before = snapshot(tmp_path)
    add_new_route(str(tmp_path), "users", layout=first)
    add_new_route(str(tmp_path), "users", layout=second)
    assert snapshot(tmp_path) == before


@pytest.mark.parametrize("directory", ["api/routes", "crud", "schemas"])
def test_partial_classic_module_allows_domain(tmp_path: Path, directory: str) -> None:
    package = make_project(tmp_path)
    target = package / directory / "users.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("# Existing module\n", encoding="utf-8")
    add_new_route(str(tmp_path), "users", layout="domain")
    assert target.read_text() == "# Existing module\n"
    assert (package / "domains/users/router.py").exists()


@pytest.mark.parametrize(
    "name, class_name", [("checkups", "Checkups"), ("health_checks", "HealthChecks")]
)
def test_domain_uses_subject_names(tmp_path: Path, name: str, class_name: str) -> None:
    package = make_project(tmp_path)
    add_new_route(str(tmp_path), name)
    assert f"class {class_name}:" in (package / f"domains/{name}/models.py").read_text()
    assert (
        f"class {class_name}Create"
        in (package / f"domains/{name}/schemas.py").read_text()
    )
    assert (
        f"def get_{name}_service" in (package / f"domains/{name}/router.py").read_text()
    )


@pytest.mark.parametrize("nested", [False, True])
@pytest.mark.parametrize("anchors", [False, True])
@pytest.mark.parametrize("aggregator", [False, True])
def test_generated_domain_crud(
    tmp_path: Path, nested: bool, anchors: bool, aggregator: bool
) -> None:
    """Run CRUD checks in a separate process to avoid src import collisions."""
    if any(importlib.util.find_spec(name) is None for name in ("fastapi", "httpx")):
        pytest.skip("Generated application runtime requires fastapi and httpx")
    make_project(tmp_path, nested=nested, aggregator=aggregator, anchors=anchors)
    add_new_route(str(tmp_path), "users")
    add_new_route(str(tmp_path), "groups")
    add_new_route(str(tmp_path), "users")
    prefix = "src.app" if nested else "src"
    api_prefix = "/api/v1" if aggregator else ""
    script = f"PACKAGE = {prefix!r}\nAPI = {api_prefix!r}\n" + CRUD_CHECK
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr


CRUD_CHECK = """
import importlib
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient

app = importlib.import_module(PACKAGE + ".main").app
repository = importlib.import_module(PACKAGE + ".domains.users.repository")
service = importlib.import_module(PACKAGE + ".domains.users.service")
router = importlib.import_module(PACKAGE + ".domains.users.router")
client = TestClient(app)
users = API + "/users"
groups = API + "/groups"
assert client.get(users).json() == []
created = client.post(users, json={"name": "Alice"})
assert created.status_code == 201
assert created.json() == {"id": 1, "name": "Alice"}
assert client.get(users + "/1").json() == created.json()
assert client.get(users).json() == [created.json()]
for payload in ({}, {"name": ""}, {"name": "a" * 121}, {"name": None}):
    assert client.post(users, json=payload).status_code == 422
    assert client.put(users + "/1", json=payload).status_code == 422
assert client.post(users, json={"name": "a" * 120}).status_code == 201
assert client.post(users, json={"name": "a"}).json()["id"] == 3
updated = client.put(users + "/1", json={"name": "Bob"})
assert updated.status_code == 200
assert updated.json() == {"id": 1, "name": "Bob"}
assert client.get(users + "/1").json() == updated.json()
assert client.get(groups).json() == []
assert client.post(groups, json={"name": "Team"}).json() == {"id": 1, "name": "Team"}
deleted = client.delete(users + "/1")
assert deleted.status_code == 204 and deleted.content == b""
assert client.get(users + "/1").status_code == 404
assert client.get(users + "/999").status_code == 404
assert client.put(users + "/999", json={"name": "Missing"}).status_code == 404
assert client.delete(users + "/999").status_code == 404
assert client.delete(users + "/1").status_code == 404
assert client.get(groups + "/1").status_code == 200
assert client.post(users, json={"name": "Next"}).json()["id"] == 4
assert client.patch(users + "/2", json={"name": "No PATCH"}).status_code == 405
schema = client.get("/openapi.json").json()
assert set(schema["paths"][users]) == {"get", "post"}
assert set(schema["paths"][users + "/{entity_id}"]) == {"get", "put", "delete"}
operations = [op["operationId"] for path in schema["paths"].values() for op in path.values()]
assert len(set(operations)) == len(operations)
assert schema["paths"][users]["get"]["tags"] == ["users"]

isolated = repository.UsersRepository()
assert isolated.list_all() == []
assert isolated.add(name="Isolated").id == 1
assert repository.UsersRepository().list_all() == []
app.dependency_overrides[router.get_users_service] = lambda: service.UsersService(isolated)
assert client.get(users).json() == [{"id": 1, "name": "Isolated"}]
app.dependency_overrides.clear()
assert len(client.get(users).json()) == 3
parallel = repository.UsersRepository()
with ThreadPoolExecutor(max_workers=8) as pool:
    entities = list(pool.map(lambda i: parallel.add(name=str(i)), range(100)))
assert {entity.id for entity in entities} == set(range(1, 101))
assert len(parallel.list_all()) == 100
"""


@pytest.mark.parametrize("nested", [False, True])
def test_classic_without_aggregator_imports(tmp_path: Path, nested: bool) -> None:
    if importlib.util.find_spec("fastapi") is None:
        pytest.skip("Generated application runtime requires fastapi")
    make_project(tmp_path, nested=nested, preset="minimal", aggregator=False)
    add_new_route(str(tmp_path), "users")
    prefix = "src.app" if nested else "src"
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            f"from {prefix}.main import app; assert app.openapi()['paths']",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    "preset, option, expected",
    [
        ("domain-starter", [], "domain"),
        ("domain-starter", ["--layout=classic-layer"], "classic-layer"),
        ("minimal", ["--layout=domain"], "domain"),
        ("single-module", [], "classic-layer"),
    ],
)
def test_cli_selects_and_displays_layout(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    preset: str,
    option: list[str],
    expected: str,
) -> None:
    package = make_project(tmp_path, preset=preset)
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(
        fastkit_cli, ["addroute", "users", ".", *option], input="Y\n"
    )
    assert result.exit_code == 0, result.output
    assert "Layout" in result.output and expected in result.output
    assert (package / "domains/users/router.py").exists() == (expected == "domain")
    assert (package / "api/routes/users.py").exists() == (expected == "classic-layer")


def test_cli_invalid_layout_and_cancellation_do_not_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    make_project(tmp_path)
    monkeypatch.chdir(tmp_path)
    before = snapshot(tmp_path)
    runner = CliRunner()
    invalid = runner.invoke(fastkit_cli, ["addroute", "users", "--layout=invalid"])
    assert invalid.exit_code == 2 and "Invalid value" in invalid.output
    cancelled = runner.invoke(
        fastkit_cli, ["addroute", "users", "--layout=domain"], input="N\n"
    )
    assert "cancelled" in cancelled.output.lower()
    assert snapshot(tmp_path) == before


@pytest.mark.parametrize("domain_first", [False, True])
def test_router_alias_collisions(tmp_path: Path, domain_first: bool) -> None:
    make_project(tmp_path)
    routes = [("users", "domain"), ("users_router", "classic-layer")]
    if not domain_first:
        routes.reverse()
    for name, layout in routes:
        add_new_route(str(tmp_path), name, layout)
    before = snapshot(tmp_path)
    for name, layout in routes:
        add_new_route(str(tmp_path), name, layout)
    assert snapshot(tmp_path) == before
    if importlib.util.find_spec("fastapi") is None:
        pytest.skip("Generated application runtime requires fastapi")
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from src.app.main import app; paths = app.openapi()['paths']; assert '/api/v1/users' in paths; assert '/api/v1/users_router/' in paths",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("legacy", [False, True])
def test_existing_domain_registration_is_preserved(
    tmp_path: Path, legacy: bool
) -> None:
    package = make_project(tmp_path)
    add_new_route(str(tmp_path), "users")
    aggregator = package / "api/router.py"
    if legacy:
        router = package / "domains/users/router.py"
        router.write_text(
            router.read_text().replace(
                "router = APIRouter()",
                'router = APIRouter(prefix="/users", tags=["users"])',
            )
        )
        aggregator.write_text(
            aggregator.read_text().replace(
                'include_router(users_router.router, prefix="/users", tags=["users"])',
                "include_router(users_router.router)",
            )
        )
    else:
        aggregator.write_text(
            aggregator.read_text().replace(
                'prefix="/users", tags=["users"]',
                'prefix="/custom-users", tags=["custom"]',
            )
        )
    before = snapshot(tmp_path)
    add_new_route(str(tmp_path), "users")
    assert snapshot(tmp_path) == before
