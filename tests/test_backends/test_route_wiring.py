"""Tests for router registration."""

from pathlib import Path
from unittest.mock import patch

import pytest

from fastapi_fastkit.backend.route_wiring import register_router, router_alias


@pytest.mark.parametrize("keyword", [False, True])
@pytest.mark.parametrize("custom", [False, True])
def test_existing_registration(tmp_path: Path, keyword: bool, custom: bool) -> None:
    target = tmp_path / "api.py"
    argument = "router=users.router" if keyword else "users.router"
    prefix = "/custom" if custom else "/users"
    source = f'from .routes import users\napi_router.include_router({argument}, prefix="{prefix}", tags=["users"])\n'
    target.write_text(source)
    with patch("fastapi_fastkit.backend.route_wiring.print_info") as info:
        register_router(
            {"api_dir": str(tmp_path), "api_router_file": str(target)},
            "from .routes import users",
            'api_router.include_router(users.router, prefix="/users", tags=["users"])',
        )
    assert target.read_text() == source
    assert info.call_count == int(custom)


def test_syntax_error_falls_back_to_text_insertion(tmp_path: Path) -> None:
    target = tmp_path / "api.py"
    source = "from .routes import users\n# fastkit:imports\napi_router = APIRouter(\n# fastkit:routes\n"
    target.write_text(source)
    assert router_alias(str(target), "routes", "users", "users") == "users"
    register_router(
        {"api_dir": str(tmp_path), "api_router_file": str(target)},
        "from .routes import groups",
        'api_router.include_router(groups.router, prefix="/groups")',
    )
    result = target.read_text()
    assert "api_router = APIRouter(" in result
    assert result.count("from .routes import groups") == 1
    assert result.count("include_router(groups.router") == 1


def test_alias_avoids_all_top_level_bindings(tmp_path: Path) -> None:
    target = tmp_path / "api.py"
    target.write_text(
        "import package as users\nfrom package import module as users_2\nusers_3 = None\nusers_4: int = 1\ndef users_5(): pass\nclass users_6: pass\n"
    )
    assert router_alias(str(target), "routes", "users", "users") == "users_7"
