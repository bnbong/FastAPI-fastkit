# --------------------------------------------------------------------------
# Project scaffolding service.
#
# ``init`` and ``startdemo`` used to carry the whole generation pipeline
# inline: template lookup, copy, metadata injection, dependency files,
# dynamic config generation, virtualenv creation, install, and the rollback
# for every failure mode in between. That left the CLI functions unable to
# be reused or tested apart from Click, and the two commands drifted.
#
# ``ProjectScaffolder`` owns that pipeline. The CLI is left with argument
# parsing, prompting and reporting.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
import shutil
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import click
from rich.tree import Tree

from fastapi_fastkit.backend.main import (
    create_venv_with_manager,
    deploy_template_files,
    generate_dependency_file_with_manager,
    inject_project_metadata,
    install_dependencies_with_manager,
    read_template_stack,
    update_setup_py_dependencies,
    write_fastkit_metadata,
)
from fastapi_fastkit.backend.project_builder import (
    DependencyCollector,
    DynamicConfigGenerator,
    PresetLayoutStrategist,
    app_module_from_relpath,
)
from fastapi_fastkit.backend.project_builder.config_schema import (
    normalize_project_config,
)
from fastapi_fastkit.core.exceptions import BackendExceptions
from fastapi_fastkit.core.settings import FeatureAxis
from fastapi_fastkit.utils.logging import debug_log
from fastapi_fastkit.utils.main import (
    console,
    print_info,
    print_success,
    print_warning,
)

from .. import __version__


def cleanup_failed_project(
    project_dir: str,
    user_workspace: str,
    create_project_folder: bool,
    project_dir_pre_existed: bool = False,
) -> None:
    """
    Clean up a partially created project after an error.

    Only deletes a project folder this run created. Two directories must never
    be removed: the user's workspace itself (which is what ``project_dir`` is
    when the template was deployed in place), and a directory that already
    existed before scaffolding started - rolling back into it would delete the
    user's own files along with the half-written project.

    :param project_dir: Directory the failed run was writing into
    :param user_workspace: The workspace scaffolding was launched from
    :param create_project_folder: Whether the run was told to create a folder
    :param project_dir_pre_existed: Whether ``project_dir`` was already on disk
        before the run started
    """
    if not create_project_folder:
        return
    if project_dir_pre_existed:
        debug_log(
            f"Not rolling back {project_dir}: the directory existed before this run",
            "warning",
        )
        return
    if not project_dir or not os.path.exists(project_dir):
        return
    if os.path.abspath(project_dir) == os.path.abspath(user_workspace):
        return
    shutil.rmtree(project_dir, ignore_errors=True)


@dataclass
class ScaffoldOptions:
    """Everything the scaffolder needs to generate one project."""

    project_name: str
    author: str
    author_email: str
    description: str
    package_manager: str
    template: str
    preset_id: Optional[str] = None
    # ``None`` means "keep whatever dependency file the template ships"
    # (``startdemo``); a list replaces it (``init``).
    dependencies: Optional[List[str]] = None
    # Interactive / ``--config`` selections. When present the dynamic
    # config generator runs over the deployed template.
    config: Optional[Dict[str, Any]] = None
    create_project_folder: bool = True
    dry_run: bool = False
    # Skip the "this will overwrite existing files" confirmation. Set by the
    # CLI's ``--yes`` flag; also implied when there is no terminal to ask.
    assume_yes: bool = False
    with_venv: bool = True
    with_install: bool = True


@dataclass
class ScaffoldResult:
    """What a completed (or previewed) scaffold produced."""

    project_dir: str
    template: str
    app_module: str
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    venv_path: str = ""
    dry_run: bool = False


class ProjectScaffolder:
    """Runs the full project generation pipeline for one set of options."""

    def __init__(self, settings: Any, options: ScaffoldOptions) -> None:
        self.settings = settings
        self.options = options
        if options.config is not None:
            # Second normalisation point (the first is ``--config`` load).
            # Whatever route a config took to get here, the dependency
            # collector, the dynamic config generator and the feature
            # metadata below all read one canonical shape.
            self.options.config = normalize_project_config(options.config, settings)
        self.strategist = PresetLayoutStrategist(options.preset_id)
        self.template_dir = os.path.join(
            settings.FASTKIT_TEMPLATE_ROOT, options.template
        )

    # ----------------------------------------------------------------
    # Public API
    # ----------------------------------------------------------------

    @property
    def project_dir(self) -> str:
        """Where the project lands, given the folder-creation choice."""
        if self.options.create_project_folder:
            return os.path.join(self.settings.USER_WORKSPACE, self.options.project_name)
        return str(self.settings.USER_WORKSPACE)

    @property
    def app_module(self) -> str:
        """The uvicorn entrypoint the generated layout will expose.

        Discovered from the template's own ``main.py-tpl`` location so
        ``startdemo`` on any template (not just the preset-backed ones)
        records a correct entrypoint; the preset profile is the fallback.
        """
        template_main = self._template_main_relpath()
        if template_main:
            return app_module_from_relpath(template_main)
        return self.strategist.app_module

    def _template_main_relpath(self) -> str:
        """Project-relative ``main.py`` path shipped by the template."""
        for root, _dirs, files in os.walk(self.template_dir):
            for file_name in files:
                if file_name.removesuffix("-tpl") != "main.py":
                    continue
                relative = os.path.relpath(
                    os.path.join(root, "main.py"), self.template_dir
                )
                return relative.replace(os.sep, "/")
        return ""

    def resolve_dependencies(self) -> List[str]:
        """Return the dependency list that will end up in the project.

        Feature selections are always re-derived from the catalog and merged
        in. Callers assemble ``options.dependencies`` themselves, and an
        axis they forget to walk would otherwise ship a project whose
        generated code imports a package nobody installed.
        """
        if self.options.dependencies is None:
            return read_template_stack(self.template_dir)

        dependencies = set(self.options.dependencies)
        if self.options.config:
            collector = DependencyCollector(self.settings)
            dependencies.update(collector.collect_from_config(self.options.config))
        return sorted(dependencies)

    def build_metadata(self) -> Dict[str, Any]:
        """
        Build the ``[tool.fastapi-fastkit]`` mapping for this project.

        This is the contract other fastkit commands read back: ``runserver``
        takes ``app_module`` from it, ``addroute`` locates the entrypoint
        through it, and ``preset`` / ``features`` document how the project
        was produced.
        """
        metadata: Dict[str, Any] = {
            "managed": True,
            "version": __version__,
            "template": self.options.template,
            "package_manager": self.options.package_manager,
            "app_module": self.app_module,
            "features": self._collect_features(),
        }
        if self.options.preset_id:
            metadata["preset"] = self.options.preset_id
        return metadata

    def preview(self) -> ScaffoldResult:
        """
        Print what a run would create, writing nothing (``--dry-run``).

        :return: The result the real run would have produced, flagged dry.
        """
        self._require_template()

        dependencies = self.resolve_dependencies()
        metadata = self.build_metadata()

        tree = Tree(f"[bold]{self.project_dir}[/bold]")
        for relative_path in self._planned_files():
            _add_tree_path(tree, relative_path)
        console.print("\n[bold]Files that would be created:[/bold]")
        console.print(tree)

        packages_tree = Tree("[bold]Packages[/bold]")
        if dependencies:
            for dependency in dependencies:
                packages_tree.add(dependency)
        else:
            packages_tree.add("[dim](none — template ships no dependency list)[/dim]")
        console.print(
            f"\n[bold]Packages that would be installed "
            f"(via {self.options.package_manager}):[/bold]"
        )
        console.print(packages_tree)

        if not self.options.with_venv:
            print_info("--no-venv: no virtual environment would be created.")
        if not self.options.with_install:
            print_info("--no-install: dependencies would not be installed.")

        print_info("Dry run complete — no files were written.")

        return ScaffoldResult(
            project_dir=self.project_dir,
            template=self.options.template,
            app_module=self.app_module,
            dependencies=dependencies,
            metadata=metadata,
            dry_run=True,
        )

    def run(self) -> ScaffoldResult:
        """
        Generate the project.

        Any failure aborts immediately and rolls back the partially created
        project (never the user's workspace itself).

        :return: Details of the generated project
        :raises BackendExceptions: If any generation step fails
        """
        self._require_template()

        if self.options.dry_run:
            return self.preview()

        if not self._confirm_overwrites():
            raise BackendExceptions("Project creation aborted by user.")

        pre_existed = os.path.isdir(self.project_dir)
        project_dir = ""
        try:
            project_dir, _, copied_files = deploy_template_files(
                self.template_dir,
                self.settings.USER_WORKSPACE,
                self.options.project_name,
                self.options.create_project_folder,
            )

            inject_project_metadata(
                project_dir,
                self.options.project_name,
                self.options.author,
                self.options.author_email,
                self.options.description,
                files=copied_files,
            )

            dependencies = self.resolve_dependencies()
            if self.options.dependencies is not None:
                self._write_dependency_files(project_dir, dependencies)

            if self.options.config:
                self._generate_dynamic_config(project_dir, self.options.config)

            metadata = self.build_metadata()
            write_fastkit_metadata(project_dir, metadata)

            venv_path = self._setup_environment(project_dir)

            return ScaffoldResult(
                project_dir=project_dir,
                template=self.options.template,
                app_module=self.app_module,
                dependencies=dependencies,
                metadata=metadata,
                venv_path=venv_path,
            )

        except Exception as e:
            debug_log(f"Scaffolding failed, rolling back: {e}", "error")
            cleanup_failed_project(
                project_dir,
                self.settings.USER_WORKSPACE,
                self.options.create_project_folder,
                project_dir_pre_existed=pre_existed,
            )
            raise

    # ----------------------------------------------------------------
    # Pipeline steps
    # ----------------------------------------------------------------

    def existing_targets(self) -> List[str]:
        """Project-relative files that a run would overwrite.

        Only meaningful for an in-place deployment: the target directory is
        the user's own workspace, so files planned by the template may
        collide with work that is already there.
        """
        project_dir = self.project_dir
        return [
            relative_path
            for relative_path in self._planned_files()
            if os.path.isfile(os.path.join(project_dir, *relative_path.split("/")))
        ]

    def _confirm_overwrites(self) -> bool:
        """Ask before overwriting files that are already in the target directory.

        Returns True when the run may proceed. Non-interactive sessions and
        ``--yes`` skip the prompt rather than hanging on a dead stdin.
        """
        if self.options.create_project_folder:
            return True

        clashes = self.existing_targets()
        if not clashes:
            return True

        print_warning(
            f"Deploying in place will overwrite {len(clashes)} existing "
            f"file(s) in '{self.project_dir}':"
        )
        for relative_path in clashes:
            console.print(f"  [yellow]{relative_path}[/yellow]")

        if self.options.assume_yes or not sys.stdin.isatty():
            print_warning("Proceeding without confirmation (--yes / non-interactive).")
            return True

        return bool(click.confirm("Overwrite these files?", default=False))

    def _require_template(self) -> None:
        if not os.path.exists(self.template_dir):
            raise BackendExceptions(
                f"Template '{self.options.template}' does not exist in "
                f"'{self.settings.FASTKIT_TEMPLATE_ROOT}'."
            )

    def _write_dependency_files(
        self, project_dir: str, dependencies: List[str]
    ) -> None:
        generate_dependency_file_with_manager(
            project_dir,
            dependencies,
            self.options.package_manager,
            self.options.project_name,
            self.options.author,
            self.options.author_email,
            self.options.description,
        )
        update_setup_py_dependencies(project_dir, dependencies)
        print_success(f"Generated dependency file with {len(dependencies)} packages")

    def _config_generator(self, project_dir: str) -> DynamicConfigGenerator:
        """Build a generator that knows this preset's file layout."""
        return DynamicConfigGenerator(
            self.options.config or {},
            project_dir,
            app_module=self.app_module,
            main_py_relpath=self.strategist.profile.main_py_relpath,
            db_config_relpath=self.strategist.profile.db_config_relpath,
            auth_config_relpath=self.strategist.profile.auth_config_relpath,
        )

    def _generate_dynamic_config(
        self, project_dir: str, config: Dict[str, Any]
    ) -> None:
        """Write the feature-driven modules on top of the deployed template.

        The generator owns the full artifact list; the only preset decision
        left here is whether the dynamic ``main.py`` overlay replaces the
        template-shipped entrypoint. For richer presets (classic-layered,
        domain-starter) we keep the template's router-aware main.py intact.
        """
        generator = self._config_generator(project_dir)
        include_main = self.strategist.should_regenerate_main

        if not include_main:
            print_info(
                f"Preserving template-shipped main.py for preset "
                f"'{self.strategist.preset_id}'."
            )

        written = generator.generate_all_files(include_main=include_main)

        if "Dockerfile" in written or "docker-compose.yml" in written:
            print_success("Generated Docker deployment files")

        # Presets that preserve their template's main.py still get the
        # generated feature routers mounted through the file's
        # ``# fastkit:`` anchors; whatever can't be spliced in safely is
        # reported instead so the user knows to wire it up themselves.
        wired = self.strategist.wire_generated_routers(project_dir, config)
        if wired:
            print_success(
                f"Registered generated routers in "
                f"{self.strategist.profile.main_py_relpath}: {', '.join(wired)}"
            )

        # Surface preset-specific warnings (e.g. "you picked a preset whose
        # shipped main.py we kept; Prometheus must be wired manually").
        for warning in self.strategist.compatibility_warnings(config, wired=wired):
            print_warning(warning, title="Preset compatibility")

        print_success(
            f"Generated {len(written)} configuration files for selected stack"
        )

    def _setup_environment(self, project_dir: str) -> str:
        """Create the virtualenv and install dependencies, honouring opt-outs."""
        if not self.options.with_venv:
            print_info("Skipping virtual environment creation (--no-venv).")
            if self.options.with_install:
                print_warning(
                    "Dependencies are not installed without a virtual environment."
                )
            return ""

        venv_path = create_venv_with_manager(project_dir, self.options.package_manager)

        if not self.options.with_install:
            print_info("Skipping dependency installation (--no-install).")
            return venv_path

        install_dependencies_with_manager(
            project_dir, venv_path, self.options.package_manager
        )
        return venv_path

    # ----------------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------------

    def _collect_features(self) -> List[str]:
        """
        Flatten the selected features into ``"<category>:<choice>"`` entries.

        Recorded in project metadata so a later ``fastkit`` run (or a human)
        can tell what the project was generated with.
        """
        config = self.options.config or {}
        features: List[str] = []

        db_info = config.get("database", {})
        if isinstance(db_info, dict) and db_info.get("type", "None") != "None":
            features.append(f"database:{db_info['type']}")

        for category in (
            FeatureAxis.AUTHENTICATION,
            FeatureAxis.ASYNC_TASKS,
            FeatureAxis.TESTING,
            FeatureAxis.CACHING,
            FeatureAxis.MONITORING,
            FeatureAxis.MIGRATIONS,
            FeatureAxis.LOGGING,
        ):
            choice = config.get(category, "None")
            if isinstance(choice, str) and choice != "None":
                features.append(f"{category}:{choice}")

        for axis in (FeatureAxis.UTILITIES, FeatureAxis.TOOLING):
            for choice in config.get(axis, []) or []:
                if choice != "None":
                    features.append(f"{axis}:{choice}")

        for target in config.get("deployment", []) or []:
            if target != "None":
                features.append(f"deployment:{target}")

        return features

    def _planned_files(self) -> List[str]:
        """
        List the project-relative files a real run would create.

        Template files are reported under their converted names (the ``-tpl``
        marker is stripped on copy), plus the extra modules the dynamic
        config generator writes for the selected features.
        """
        planned: List[str] = []

        for root, _dirs, files in os.walk(self.template_dir):
            for file_name in files:
                relative_dir = os.path.relpath(root, self.template_dir)
                converted = file_name.removesuffix("-tpl")
                if relative_dir == ".":
                    planned.append(converted)
                else:
                    planned.append(os.path.join(relative_dir, converted))

        config = self.options.config or {}
        if config:
            planned.extend(
                self._config_generator(self.project_dir).planned_files(
                    include_main=self.strategist.should_regenerate_main
                )
            )
            deployment = config.get("deployment", [])
            if deployment and deployment != ["None"]:
                planned.append(".dockerignore")

        if self.options.dependencies is not None:
            planned.append(
                self.settings.PACKAGE_MANAGER_CONFIG[self.options.package_manager][
                    "dependency_file"
                ]
            )

        return sorted(set(path.replace(os.sep, "/") for path in planned))


def _add_tree_path(tree: Tree, relative_path: str) -> None:
    """Add a ``a/b/c.py`` path to a rich tree, reusing existing branches."""
    node = tree
    parts = relative_path.split("/")
    for part in parts[:-1]:
        existing = None
        for child in node.children:
            if str(child.label) == f"[bold]{part}/[/bold]":
                existing = child
                break
        node = existing if existing is not None else node.add(f"[bold]{part}/[/bold]")
    node.add(parts[-1])


__all__ = [
    "ProjectScaffolder",
    "ScaffoldOptions",
    "ScaffoldResult",
    "cleanup_failed_project",
]
