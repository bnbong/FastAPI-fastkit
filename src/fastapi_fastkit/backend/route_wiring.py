"""Router registration helpers."""

import ast
from pathlib import Path
from typing import Dict

from fastapi_fastkit.utils.main import print_info


def _parse_module(content: str) -> ast.Module:
    try:
        return ast.parse(content)
    except SyntaxError:
        statements: list[ast.stmt] = []
        for line in content.splitlines():
            try:
                statements.extend(ast.parse(line.strip()).body)
            except SyntaxError:
                continue
        return ast.Module(body=statements, type_ignores=[])


def _router_argument(call: ast.Call) -> ast.expr | None:
    if call.args:
        return call.args[0]
    return next((item.value for item in call.keywords if item.arg == "router"), None)


def register_router(
    project_layout: Dict[str, str], import_line: str, statement: str
) -> None:
    """Register a router in the API router module."""

    from fastapi_fastkit.backend.main import insert_import_line, insert_statement_line

    api_dir = Path(project_layout["api_dir"])
    api_dir.mkdir(parents=True, exist_ok=True)
    init = api_dir / "__init__.py"
    if not init.exists():
        init.write_text("", encoding="utf-8")
    target = Path(project_layout["api_router_file"])
    content = target.read_text(encoding="utf-8") if target.exists() else ""
    if not content.strip():
        content = "from fastapi import APIRouter\n\napi_router = APIRouter()\n"
    registration = ast.parse(statement).body[0]
    existing = None
    if isinstance(registration, ast.Expr) and isinstance(registration.value, ast.Call):
        expected = registration.value
        expected_router = _router_argument(expected)
        existing = next(
            (
                node
                for node in ast.walk(_parse_module(content))
                if isinstance(node, ast.Call)
                and ast.dump(node.func) == ast.dump(expected.func)
                and (argument := _router_argument(node)) is not None
                and expected_router is not None
                and ast.dump(argument) == ast.dump(expected_router)
            ),
            None,
        )
        if existing is not None:
            current_options = {
                item.arg: ast.dump(item.value)
                for item in existing.keywords
                if item.arg != "router"
            }
            expected_options = {
                item.arg: ast.dump(item.value)
                for item in expected.keywords
                if item.arg != "router"
            }
            if (
                current_options != expected_options
                or existing.args[1:] != expected.args[1:]
            ):
                print_info(
                    f"Keeping existing router registration in {target} with its current prefix and options."
                )
    updated = insert_import_line(content, import_line)
    if existing is None:
        updated = insert_statement_line(updated, statement)
    if not target.exists() or updated != content:
        target.write_text(updated, encoding="utf-8")


def router_alias(file: str, module: str, name: str, preferred: str) -> str:
    """Reuse the router import alias or choose an unused name."""

    target = Path(file)
    if not target.exists():
        return preferred
    tree = _parse_module(target.read_text(encoding="utf-8"))
    occupied: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            for imported in node.names:
                if node.module == module and imported.name == name:
                    return imported.asname or name
                occupied.add(imported.asname or imported.name)
        elif isinstance(node, ast.Import):
            occupied.update(
                item.asname or item.name.split(".")[0] for item in node.names
            )
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            occupied.add(node.name)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            occupied.update(
                target.id for target in targets if isinstance(target, ast.Name)
            )
    alias = preferred
    counter = 2
    while alias in occupied:
        alias = f"{preferred}_{counter}"
        counter += 1
    return alias
