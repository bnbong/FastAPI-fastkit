# --------------------------------------------------------------------------
# Route generators for fastkit addroute.
# --------------------------------------------------------------------------
import keyword
import os
from pathlib import Path
from typing import Dict, Optional, Union

from fastapi_fastkit.backend import main as backend
from fastapi_fastkit.backend.route_wiring import register_router, router_alias
from fastapi_fastkit.backend.transducer import copy_and_convert_template_file
from fastapi_fastkit.core.exceptions import BackendExceptions
from fastapi_fastkit.core.settings import settings
from fastapi_fastkit.utils.main import print_warning, read_fastkit_metadata

ROUTE_LAYOUTS = ("classic-layer", "domain")


def resolve_route_layout(project_dir: str, layout: Optional[str] = None) -> str:
    """Resolve the route layout from the option or project preset."""
    if layout is not None:
        if layout not in ROUTE_LAYOUTS:
            raise BackendExceptions(f"Unknown route layout: {layout!r}")
        return layout

    preset = read_fastkit_metadata(project_dir).get("preset")
    if preset == "domain-starter":
        return "domain"
    if preset and preset not in ("classic-layered", "minimal", "single-module"):
        print_warning(f"Unknown preset {preset!r}; using classic-layer route layout.")
    return "classic-layer"


def _validate_route_name(route_name: str) -> None:
    """Validate the route module name."""
    if not route_name.isidentifier() or keyword.iskeyword(route_name):
        raise BackendExceptions(f"Route name {route_name!r} is not a Python identifier")


class ClassicLayeredRouteGenerator:
    """Generate api/routes, crud, and schemas modules."""

    def add_new_route(
        self, project_dir: str, route_name: str, project_layout: Dict[str, str]
    ) -> None:
        """Create route files and register the router."""
        src_dir = project_layout["package_dir"]
        _validate_route_name(route_name)
        modules_dir = os.path.join(settings.FASTKIT_TEMPLATE_ROOT, "modules")
        target_dirs = backend._ensure_project_structure(src_dir)
        backend._create_route_files(
            modules_dir, target_dirs, route_name, project_layout["package_module"]
        )
        backend._handle_api_router_file(
            target_dirs, modules_dir, route_name, project_layout["api_router_file"]
        )
        backend._process_init_files(
            modules_dir, target_dirs, ["api/routes", "crud", "schemas"]
        )
        backend._update_main_app(
            src_dir,
            route_name,
            router_module=project_layout["api_router_module"],
            main_py_path=project_layout["main"],
        )


class DomainRouteGenerator:
    """Generate a domain module."""

    def add_new_route(
        self, project_dir: str, route_name: str, project_layout: Dict[str, str]
    ) -> None:
        """Create domain files and register the router."""
        package = Path(project_layout["package_dir"])
        _validate_route_name(route_name)
        if not package.is_dir():
            raise BackendExceptions(f"Source directory not found at {package}")

        domain_module = _create_domain_files(package, route_name, project_layout)
        alias = router_alias(
            project_layout["api_router_file"],
            domain_module,
            "router",
            f"{route_name}_router",
        )
        register_router(
            project_layout,
            f"from {domain_module} import router as {alias}",
            f'api_router.include_router({alias}.router, prefix="/{route_name}", tags=["{route_name}"])',
        )
        backend._update_main_app(
            str(package),
            route_name,
            router_module=project_layout["api_router_module"],
            main_py_path=project_layout["main"],
        )


def _create_domain_files(
    package: Path, route_name: str, project_layout: Dict[str, str]
) -> str:
    templates = Path(settings.FASTKIT_TEMPLATE_ROOT) / "modules" / "domain"
    filenames = (
        "__init__.py",
        "models.py",
        "schemas.py",
        "repository.py",
        "service.py",
        "router.py",
    )
    for filename in filenames:
        if not (templates / f"{filename}-tpl").is_file():
            raise BackendExceptions(f"Missing domain template: {filename}-tpl")

    domain_dir = package / "domains" / route_name
    domain_dir.mkdir(parents=True, exist_ok=True)
    domains_init = domain_dir.parent / "__init__.py"
    if not domains_init.exists():
        domains_init.write_text("", encoding="utf-8")
    prefix = project_layout["package_module"]
    domain_module = (
        f"{prefix}.domains.{route_name}" if prefix else f"domains.{route_name}"
    )
    entity_class = (
        "".join(part[:1].upper() + part[1:] for part in route_name.split("_")) or "_"
    )
    if keyword.iskeyword(entity_class):
        entity_class += "Entity"
    replacements = {
        "<new_route>": route_name,
        "<domain_module>": domain_module,
        "<entity_class>": entity_class,
    }
    for filename in filenames:
        target = domain_dir / filename
        if target.exists():
            print_warning(f"File {target} already exists, skipping...")
            continue
        if not copy_and_convert_template_file(
            str(templates / f"{filename}-tpl"), str(target), replacements
        ):
            raise BackendExceptions(f"Failed to create domain file: {target}")

    return domain_module


def get_route_generator(
    route_layout: str,
) -> Union[ClassicLayeredRouteGenerator, DomainRouteGenerator]:
    """Return the generator for the selected layout."""
    if route_layout == "classic-layer":
        return ClassicLayeredRouteGenerator()
    if route_layout == "domain":
        return DomainRouteGenerator()
    raise BackendExceptions(f"Unknown route layout: {route_layout!r}")
