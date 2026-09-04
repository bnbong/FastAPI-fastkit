# --------------------------------------------------------------------------
# Testcases of the project metadata contract and layout-aware route insertion.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
from pathlib import Path

from fastapi_fastkit.backend.main import (
    _ensure_pyproject_fastkit_markers,
    _update_api_router,
    _update_main_app,
    build_fastkit_metadata_block,
    insert_import_line,
    insert_statement_line,
    resolve_project_layout,
    update_setup_py_dependencies,
    write_fastkit_metadata,
)
from fastapi_fastkit.utils.main import is_fastkit_project, read_fastkit_metadata

BASE_PYPROJECT = """[project]
name = "demo"
description = "a demo project"
dependencies = [
    "fastapi",
]
"""


class TestFastkitMetadata:
    def test_block_renders_the_documented_keys_in_order(self) -> None:
        # given
        metadata = {
            "features": ["database:PostgreSQL"],
            "app_module": "src.app.main:app",
            "template": "fastapi-domain-starter",
            "version": "1.2.0",
            "preset": "domain-starter",
            "package_manager": "uv",
        }

        # when
        block = build_fastkit_metadata_block(metadata)

        # then
        assert block.splitlines() == [
            "[tool.fastapi-fastkit]",
            "managed = true",
            'version = "1.2.0"',
            'template = "fastapi-domain-starter"',
            'preset = "domain-starter"',
            'package_manager = "uv"',
            'app_module = "src.app.main:app"',
            'features = ["database:PostgreSQL"]',
        ]

    def test_write_then_read_round_trips(self, tmp_path: Path) -> None:
        # given
        (tmp_path / "pyproject.toml").write_text(BASE_PYPROJECT)
        metadata = {
            "version": "1.2.0",
            "template": "fastapi-default",
            "package_manager": "pip",
            "app_module": "src.main:app",
            "features": [],
        }

        # when
        write_fastkit_metadata(str(tmp_path), metadata)

        # then
        stored = read_fastkit_metadata(str(tmp_path))
        assert stored["managed"] is True
        assert stored["app_module"] == "src.main:app"
        assert stored["features"] == []
        assert is_fastkit_project(str(tmp_path))

    def test_rewriting_metadata_does_not_duplicate_the_section(
        self, tmp_path: Path
    ) -> None:
        # given
        (tmp_path / "pyproject.toml").write_text(BASE_PYPROJECT)
        write_fastkit_metadata(str(tmp_path), {"app_module": "src.main:app"})

        # when
        write_fastkit_metadata(str(tmp_path), {"app_module": "src.app.main:app"})

        # then
        content = (tmp_path / "pyproject.toml").read_text()
        assert content.count("[tool.fastapi-fastkit]") == 1
        assert read_fastkit_metadata(str(tmp_path))["app_module"] == "src.app.main:app"

    def test_marker_only_mode_is_still_supported(self) -> None:
        # when
        content = _ensure_pyproject_fastkit_markers(BASE_PYPROJECT)

        # then
        assert "[tool.fastapi-fastkit]\nmanaged = true" in content
        assert "[FastAPI-fastkit templated]" in content

    def test_read_returns_empty_for_unmanaged_projects(self, tmp_path: Path) -> None:
        # given
        (tmp_path / "pyproject.toml").write_text(BASE_PYPROJECT)

        # when & then
        assert read_fastkit_metadata(str(tmp_path)) == {}
        assert read_fastkit_metadata(str(tmp_path / "missing")) == {}


class TestDependencyUpdate:
    def test_pyproject_dependencies_are_replaced(self, tmp_path: Path) -> None:
        # given
        (tmp_path / "pyproject.toml").write_text(BASE_PYPROJECT)

        # when
        update_setup_py_dependencies(str(tmp_path), ["fastapi", "redis[hiredis]"])

        # then
        content = (tmp_path / "pyproject.toml").read_text()
        assert '"redis[hiredis]"' in content
        # The extras bracket must not truncate the array replacement.
        assert content.count("dependencies = [") == 1
        assert content.rstrip().endswith("]")

    def test_setup_py_is_updated_only_when_present(self, tmp_path: Path) -> None:
        # given
        (tmp_path / "pyproject.toml").write_text(BASE_PYPROJECT)
        (tmp_path / "setup.py").write_text(
            'install_requires: list[str] = [\n    "fastapi",\n]\n'
        )

        # when
        update_setup_py_dependencies(str(tmp_path), ["fastapi", "httpx"])

        # then
        assert '"httpx"' in (tmp_path / "setup.py").read_text()
        assert '"httpx"' in (tmp_path / "pyproject.toml").read_text()


class TestCodeInsertion:
    def test_anchor_wins_over_ast(self) -> None:
        # given
        source = (
            "from fastapi import APIRouter\n"
            "\n"
            "# fastkit:imports\n"
            "\n"
            "api_router = APIRouter()\n"
            "# fastkit:routes\n"
        )

        # when
        updated = insert_import_line(source, "from .routes import user")
        updated = insert_statement_line(
            updated, "api_router.include_router(user.router)"
        )

        # then
        lines = updated.splitlines()
        assert lines[lines.index("# fastkit:imports") + 1] == "from .routes import user"
        assert (
            lines[lines.index("# fastkit:routes") + 1]
            == "api_router.include_router(user.router)"
        )

    def test_ast_fallback_inserts_after_the_last_import(self) -> None:
        # given: a multi-line import the old line-prefix scan mishandled
        source = (
            "from fastapi import (\n"
            "    APIRouter,\n"
            "    Depends,\n"
            ")\n"
            "\n"
            "api_router = APIRouter()\n"
        )

        # when
        updated = insert_import_line(source, "from .routes import user")

        # then
        lines = updated.splitlines()
        assert lines[4] == "from .routes import user"

    def test_insertion_is_idempotent(self) -> None:
        # given
        source = "from .routes import user\n"

        # when
        updated = insert_import_line(source, "from .routes import user")

        # then
        assert updated == source

    def test_import_inside_a_string_is_not_mistaken_for_code(self) -> None:
        # given
        source = 'DOC = """\nimport os\n"""\n\napp = 1\n'

        # when
        updated = insert_import_line(source, "import sys")

        # then
        assert updated.splitlines()[0] == "import sys"


class TestProjectLayoutResolution:
    def _make_domain_project(self, root: Path) -> None:
        app_dir = root / "src" / "app"
        (app_dir / "api").mkdir(parents=True)
        (app_dir / "main.py").write_text(
            "from fastapi import FastAPI\n"
            "from src.app.api.router import api_router\n"
            "\n"
            "app = FastAPI()\n"
            "app.include_router(api_router)\n"
        )
        (app_dir / "api" / "router.py").write_text(
            "from fastapi import APIRouter\n\napi_router = APIRouter()\n"
        )
        (root / "pyproject.toml").write_text(BASE_PYPROJECT)
        write_fastkit_metadata(str(root), {"app_module": "src.app.main:app"})

    def test_metadata_app_module_drives_the_layout(self, tmp_path: Path) -> None:
        # given
        self._make_domain_project(tmp_path)

        # when
        layout = resolve_project_layout(str(tmp_path))

        # then
        assert layout["app_module"] == "src.app.main:app"
        assert layout["package_module"] == "src.app"
        assert layout["api_router_module"] == "src.app.api.router"
        assert layout["api_router_file"].endswith(os.path.join("api", "router.py"))

    def test_classic_layout_is_discovered_without_metadata(
        self, tmp_path: Path
    ) -> None:
        # given
        src_dir = tmp_path / "src"
        (src_dir / "api").mkdir(parents=True)
        (src_dir / "main.py").write_text(
            "from fastapi import FastAPI\napp = FastAPI()\n"
        )
        (src_dir / "api" / "api.py").write_text(
            "from fastapi import APIRouter\n\napi_router = APIRouter()\n"
        )

        # when
        layout = resolve_project_layout(str(tmp_path))

        # then
        assert layout["app_module"] == "src.main:app"
        assert layout["api_router_module"] == "src.api.api"

    def test_domain_starter_main_py_gets_the_right_router_import(
        self, tmp_path: Path
    ) -> None:
        # given
        self._make_domain_project(tmp_path)
        layout = resolve_project_layout(str(tmp_path))

        # when
        _update_api_router(layout["api_router_file"], "user")
        _update_main_app(
            layout["package_dir"],
            "user",
            router_module=layout["api_router_module"],
            main_py_path=layout["main"],
        )

        # then
        router_content = Path(layout["api_router_file"]).read_text()
        assert "from .routes import user" in router_content
        assert 'api_router.include_router(user.router, prefix="/user"' in router_content

        main_content = Path(layout["main"]).read_text()
        # src/main.py was never assumed, and the existing import is untouched
        assert main_content.count("from src.app.api.router import api_router") == 1
        assert main_content.count("app.include_router(api_router)") == 1
