# --------------------------------------------------------------------------
# The Module defines backend operations for FastAPI-fastkit CLI.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import ast
import io
import json
import os
import re
import tokenize
import tomllib
from typing import Any, Dict, Iterable, List, Optional

import click

from fastapi_fastkit.backend.package_managers import PackageManagerFactory
from fastapi_fastkit.backend.project_builder.preset_layout import (
    app_module_from_main_path,
)
from fastapi_fastkit.backend.transducer import (
    copy_and_convert_template,
    copy_and_convert_template_file,
)
from fastapi_fastkit.core.exceptions import BackendExceptions
from fastapi_fastkit.core.settings import settings
from fastapi_fastkit.utils.config_file import format_toml_value
from fastapi_fastkit.utils.logging import debug_log, get_logger
from fastapi_fastkit.utils.main import (
    FASTKIT_DESCRIPTION_MARKER,
    FASTKIT_TOOL_SECTION,
    handle_exception,
    print_info,
    print_success,
    print_warning,
    read_fastkit_metadata,
)

# Explicit insertion points templates may declare so ``addroute`` never has
# to guess where generated code belongs. See the route anchor contract in
# the project docs.
IMPORT_ANCHOR = "# fastkit:imports"
ROUTES_ANCHOR = "# fastkit:routes"

logger = get_logger(__name__)


# ------------------------------------------------------------
# Template Discovery Functions
# ------------------------------------------------------------


def find_template_core_modules(project_dir: str) -> Dict[str, str]:
    """
    Find core module files in the template project structure.
    Returns a dictionary with paths to main.py, setup.py, pyproject.toml and config files.

    :param project_dir: Path to the project directory
    :return: Dictionary with paths to core modules
    """
    core_modules = {"main": "", "setup": "", "pyproject": "", "config": ""}
    template_paths = settings.TEMPLATE_PATHS

    # Find main.py
    for main_path in template_paths["main"]:
        full_path = os.path.join(project_dir, main_path)
        if os.path.exists(full_path):
            core_modules["main"] = full_path
            break

    # Find setup.py
    for setup_path in template_paths["setup"]:
        full_path = os.path.join(project_dir, setup_path)
        if os.path.exists(full_path):
            core_modules["setup"] = full_path
            break

    # Find pyproject.toml
    for pyproject_path in template_paths["pyproject"]:
        full_path = os.path.join(project_dir, pyproject_path)
        if os.path.exists(full_path):
            core_modules["pyproject"] = full_path
            break

    # Find config file
    config_info = template_paths["config"]
    if isinstance(config_info, dict):
        for config_path in config_info["paths"]:
            for config_file in config_info["files"]:
                full_path = os.path.join(project_dir, config_path, config_file)
                if os.path.exists(full_path):
                    core_modules["config"] = full_path
                    break
            if core_modules["config"]:
                break

    return core_modules


def read_template_stack(template_path: str) -> List[str]:
    """
    Read dependencies from a template's metadata files.

    Lookup order preserves legacy behaviour for templates that still ship
    ``requirements.txt-tpl`` while allowing modern pyproject-first templates
    to resolve their stack from ``pyproject.toml-tpl``:

    1. ``requirements.txt-tpl`` (legacy, highest precedence)
    2. ``pyproject.toml-tpl`` ``[project].dependencies``
    3. ``setup.py-tpl`` ``install_requires``

    :param template_path: Path to the template directory
    :return: List of PEP 508 requirement strings
    """
    req_file = os.path.join(template_path, "requirements.txt-tpl")
    if os.path.exists(req_file):
        try:
            with open(req_file, "r", encoding="utf-8") as f:
                deps = [dep.strip() for dep in f.readlines() if dep.strip()]
                return deps
        except (OSError, UnicodeDecodeError) as e:
            debug_log(
                f"Error reading template dependencies from {req_file}: {e}", "error"
            )
            return []

    pyproject_file = os.path.join(template_path, "pyproject.toml-tpl")
    if os.path.exists(pyproject_file):
        deps = _parse_pyproject_dependencies(pyproject_file)
        if deps:
            return deps

    setup_file = os.path.join(template_path, "setup.py-tpl")
    if os.path.exists(setup_file):
        try:
            with open(setup_file, "r", encoding="utf-8") as f:
                content = f.read()
                return _parse_setup_dependencies(content)
        except (OSError, UnicodeDecodeError) as e:
            debug_log(f"Error reading setup.py template: {e}", "error")

    return []


def _parse_setup_dependencies(content: str) -> List[str]:
    """
    Parse dependencies from setup.py content.

    :param content: setup.py file content
    :return: List of dependencies
    """
    # First try to find install_requires with list[str] type annotation (new format)
    list_match = re.search(
        r"install_requires:\s*list\[str\]\s*=\s*\[(.*?)\]",
        content,
        re.DOTALL,
    )
    if list_match:
        deps_str = list_match.group(1)
        # Split by lines and commas, clean up quotes
        deps = []
        for line in deps_str.split("\n"):
            line = line.strip()
            if line and not line.startswith("#"):
                # Remove quotes and trailing commas
                line = line.strip(" \",'")
                if line:
                    deps.append(line)
        return [dep for dep in deps if dep]  # Remove empty strings

    # Fallback to original install_requires parsing
    match = re.search(r"install_requires\s*=\s*\[(.*?)\]", content, re.DOTALL)
    if match:
        deps_str = match.group(1).replace("\n", "").replace(" ", "")
        deps = [
            dep.strip().strip("'").strip('"')
            for dep in deps_str.split(",")
            if dep.strip() and not dep.isspace()
        ]
        return [dep for dep in deps if dep]  # Remove empty strings

    return []


def _parse_pyproject_dependencies(pyproject_path: str) -> List[str]:
    """
    Parse dependencies from a ``pyproject.toml-tpl`` file.

    Returns the list of PEP 508 requirement strings from
    ``[project].dependencies``. Returns an empty list on parse errors so
    callers can fall through to the next metadata source.
    """
    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
    except (OSError, tomllib.TOMLDecodeError, UnicodeDecodeError) as e:
        debug_log(f"Error reading pyproject.toml template: {e}", "error")
        return []

    project = data.get("project", {})
    raw_deps = project.get("dependencies", []) or []
    if not isinstance(raw_deps, list):
        return []
    return [dep.strip() for dep in raw_deps if isinstance(dep, str) and dep.strip()]


# ------------------------------------------------------------
# Project Setup Functions
# ------------------------------------------------------------


# Placeholder tokens a template may declare anywhere in its files. Every one
# of them is substituted project-wide during generation, so a template author
# can use them in a README, a .env, a conftest.py - not just in the handful of
# "core" modules the injector used to know about.
PROJECT_PLACEHOLDERS = (
    "<project_name>",
    "<author>",
    "<author_email>",
    "<description>",
)

# Suffixes that are safe to rewrite as UTF-8 text. Anything else (images,
# fonts, compiled artifacts) is skipped without being read. Extension-less
# files (Dockerfile, Makefile, .env, .gitignore) are read too - they are the
# ones templates most often put placeholders in.
_TEXT_FILE_SUFFIXES = frozenset(
    {
        "",
        ".cfg",
        ".conf",
        ".env",
        ".example",
        ".html",
        ".in",
        ".ini",
        ".j2",
        ".json",
        ".mako",
        ".md",
        ".po",
        ".py",
        ".rst",
        ".sh",
        ".sql",
        ".toml",
        ".txt",
        ".yaml",
        ".yml",
    }
)

# Directories never worth walking: virtualenvs and caches are not part of the
# template output, and rewriting them would be both slow and wrong.
_SKIPPED_SCAN_DIRS = frozenset(
    {
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "__pycache__",
        "venv",
    }
)

# Guard against rewriting an accidentally huge file (a checked-in fixture,
# a lockfile dump). 2 MiB is far above any real template source file.
_MAX_SUBSTITUTION_FILE_BYTES = 2 * 1024 * 1024


#: File suffixes whose placeholder values must be escaped as TOML basic
#: string bodies, and those needing Python/JSON string escaping. A raw
#: substitution of a value containing a quote or a backslash would otherwise
#: produce a pyproject.toml or a config.py that no longer parses.
_TOML_SUFFIXES = frozenset({".toml"})
_PY_STRING_SUFFIXES = frozenset({".py", ".json"})


def escape_placeholder_value(value: str, file_path: str) -> str:
    """
    Escape a metadata value for safe substitution inside ``file_path``.

    Placeholder tokens sit *inside* a quoted literal in the template
    (``name = "<project_name>"``), so what is needed is the escaped *body*
    of a string, not a fully quoted literal.

    :param value: Raw metadata value entered by the user
    :param file_path: Destination file the value is substituted into
    :return: The value escaped for that file type (unchanged for plain text)
    """
    suffix = os.path.splitext(file_path)[1].lower()
    if suffix in _TOML_SUFFIXES:
        return format_toml_value(value)[1:-1]
    if suffix in _PY_STRING_SUFFIXES:
        return json.dumps(value, ensure_ascii=False)[1:-1]
    return value


def _escaped_replacements(
    replacements: Dict[str, str], file_path: str
) -> Dict[str, str]:
    """Escape every replacement value for the target file's syntax."""
    return {
        placeholder: escape_placeholder_value(value, file_path)
        for placeholder, value in replacements.items()
    }


def _apply_escaped_replacements(
    content: str, replacements: Dict[str, str], file_path: str
) -> str:
    """Substitute ``replacements`` into ``content``, escaping per file type."""
    for placeholder, value in _escaped_replacements(replacements, file_path).items():
        content = content.replace(placeholder, value)
    return content


def _is_substitutable_file(file_path: str) -> bool:
    """Return True when a file should be scanned for placeholder tokens.

    :param file_path: Absolute path to the candidate file
    :return: True for reasonably sized text files
    """
    if os.path.islink(file_path):
        return False
    if os.path.splitext(file_path)[1].lower() not in _TEXT_FILE_SUFFIXES:
        return False
    try:
        return os.path.getsize(file_path) <= _MAX_SUBSTITUTION_FILE_BYTES
    except OSError:
        return False


def _iter_project_text_files(project_dir: str) -> List[str]:
    """List every text file in a generated project, skipping caches and venvs.

    :param project_dir: Path to the generated project
    :return: Absolute paths of candidate text files
    """
    candidates: List[str] = []
    for root, dirs, files in os.walk(project_dir):
        dirs[:] = [d for d in dirs if d not in _SKIPPED_SCAN_DIRS]
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if _is_substitutable_file(file_path):
                candidates.append(file_path)
    return candidates


def _substitution_targets(
    project_dir: str, files: Optional[Iterable[str]] = None
) -> List[str]:
    """Resolve which files a rewriting pass may touch.

    ``files`` is the list of paths the template deployment actually wrote.
    Scoping to it is what keeps an in-place deployment (``project_dir`` is
    the user's own workspace) from rewriting unrelated files that happened
    to be sitting there. Only when a caller supplies nothing do we fall back
    to walking the whole project.
    """
    if files is None:
        return _iter_project_text_files(project_dir)
    return [path for path in dict.fromkeys(files) if _is_substitutable_file(path)]


def replace_placeholders_in_project(
    project_dir: str,
    replacements: Dict[str, str],
    files: Optional[Iterable[str]] = None,
) -> List[str]:
    """
    Substitute placeholder tokens across every text file of a project.

    Files that cannot be decoded as UTF-8 are left untouched rather than
    corrupted, and a file is only rewritten when it actually changed.

    :param project_dir: Path to the generated project
    :param replacements: Mapping of placeholder token to replacement value
    :param files: Absolute paths written by the template deployment. When
        given, only these files are considered; otherwise the whole project
        tree is walked.
    :return: Project-relative paths of the files that were rewritten
    """
    rewritten: List[str] = []

    for file_path in _substitution_targets(project_dir, files):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except (OSError, UnicodeDecodeError) as e:
            debug_log(f"Skipping {file_path} during substitution: {e}", "debug")
            continue

        updated = _apply_escaped_replacements(content, replacements, file_path)

        if updated == content:
            continue

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(updated)
        except OSError as e:
            debug_log(f"Failed to write substituted file {file_path}: {e}", "error")
            raise BackendExceptions(f"Failed to substitute placeholders: {e}")

        rewritten.append(os.path.relpath(file_path, project_dir))

    return rewritten


def find_unsubstituted_placeholders(
    project_dir: str, files: Optional[Iterable[str]] = None
) -> Dict[str, List[str]]:
    """
    Report placeholder tokens that survived project generation.

    A surviving token means the template declares a variable the generator
    does not know how to fill - a bug in the template, and a broken file in
    the user's brand new project. Callers surface it instead of failing hard
    so the project is still usable.

    :param project_dir: Path to the generated project
    :param files: Absolute paths written by the template deployment; when
        given the scan is limited to them
    :return: Mapping of project-relative file path to the tokens found in it
    """
    residue: Dict[str, List[str]] = {}

    for file_path in _substitution_targets(project_dir, files):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except (OSError, UnicodeDecodeError):
            continue

        hits = [token for token in PROJECT_PLACEHOLDERS if token in content]
        if hits:
            residue[os.path.relpath(file_path, project_dir)] = hits

    return residue


def inject_project_metadata(
    target_dir: str,
    project_name: str,
    author: str,
    author_email: str,
    description: str,
    files: Optional[Iterable[str]] = None,
) -> None:
    """
    Inject project metadata into template files after template conversion.

    The core metadata files (setup.py, pyproject.toml, the settings module and
    main.py) are handled first because they need more than a text replacement -
    pyproject also gets the ``[tool.fastapi-fastkit]`` marker block. Every
    remaining text file in the project is then swept for the same placeholder
    tokens, so README.md, .env, tests/conftest.py and friends are covered too.

    ``files`` scopes that sweep to the paths the template deployment wrote.
    An in-place deployment targets the user's own workspace, and walking the
    whole tree there would rewrite unrelated files.
    """
    try:
        core_modules = find_template_core_modules(target_dir)
        _process_setup_file(
            core_modules.get("setup", ""),
            project_name,
            author,
            author_email,
            description,
        )
        _process_pyproject_file(
            core_modules.get("pyproject", ""),
            project_name,
            author,
            author_email,
            description,
        )
        _process_config_file(core_modules.get("config", ""), project_name)
        _process_main_file(core_modules.get("main", ""), project_name)

        replacements = dict(
            zip(
                PROJECT_PLACEHOLDERS,
                (project_name, author, author_email, description),
            )
        )
        rewritten = replace_placeholders_in_project(target_dir, replacements, files)
        if rewritten:
            debug_log(
                f"Substituted placeholders in {len(rewritten)} additional files",
                "info",
            )

        residue = find_unsubstituted_placeholders(target_dir, files)
        if residue:
            for relative_path, tokens in sorted(residue.items()):
                print_warning(
                    f"{relative_path}: {', '.join(tokens)}",
                    title="Unsubstituted placeholder",
                )

        print_success("Project metadata injected successfully")

    except BackendExceptions:
        raise
    except Exception as e:
        debug_log(f"Failed to inject project metadata: {e}", "error")
        handle_exception(e, "Failed to inject project metadata")
        raise BackendExceptions("Failed to inject project metadata")


def _process_setup_file(
    setup_py: str, project_name: str, author: str, author_email: str, description: str
) -> None:
    """
    Process setup.py file and inject metadata.

    :param setup_py: Path to setup.py file
    :param project_name: Project name
    :param author: Author name
    :param author_email: Author email
    :param description: Project description
    """
    if not setup_py or not os.path.exists(setup_py):
        return

    try:
        with open(setup_py, "r", encoding="utf-8") as f:
            content = f.read()

        # Replace placeholders
        replacements = {
            "<project_name>": project_name,
            "<author>": author,
            "<author_email>": author_email,
            "<description>": description,
        }

        content = _apply_escaped_replacements(content, replacements, setup_py)

        with open(setup_py, "w", encoding="utf-8") as f:
            f.write(content)

        debug_log("Injected metadata into setup.py", "info")
        print_info("Injected metadata into setup.py")

    except (OSError, UnicodeDecodeError) as e:
        debug_log(f"Error processing setup.py: {e}", "error")
        raise BackendExceptions(f"Failed to process setup.py: {e}")


def _process_main_file(main_py: str, project_name: str) -> None:
    """
    Replace project name placeholders in the template main.py file.

    Some templates (e.g. fastapi-single-module) inline the project name directly
    in main.py rather than reading it from a settings module, so the placeholder
    must be substituted here as well.

    :param main_py: Path to main.py file
    :param project_name: Project name
    """
    if not main_py or not os.path.exists(main_py):
        return

    try:
        with open(main_py, "r", encoding="utf-8") as f:
            content = f.read()

        if "<project_name>" not in content:
            return

        content = content.replace(
            "<project_name>", escape_placeholder_value(project_name, main_py)
        )

        with open(main_py, "w", encoding="utf-8") as f:
            f.write(content)

        debug_log("Injected project name into main.py", "info")
        print_info("Injected project name into main.py")

    except (OSError, UnicodeDecodeError) as e:
        debug_log(f"Error processing main.py: {e}", "error")
        raise BackendExceptions(f"Failed to process main.py: {e}")


def _process_config_file(config_py: str, project_name: str) -> None:
    """
    Process config file and inject project name.

    :param config_py: Path to config file
    :param project_name: Project name
    """
    if not config_py or not os.path.exists(config_py):
        return

    try:
        with open(config_py, "r", encoding="utf-8") as f:
            content = f.read()

        # Replace project name placeholder
        content = content.replace(
            "<project_name>", escape_placeholder_value(project_name, config_py)
        )

        with open(config_py, "w", encoding="utf-8") as f:
            f.write(content)

        debug_log("Injected project name into config file", "info")
        print_info("Injected project name into config file")

    except (OSError, UnicodeDecodeError) as e:
        debug_log(f"Error processing config file: {e}", "error")
        raise BackendExceptions(f"Failed to process config file: {e}")


def _process_pyproject_file(
    pyproject_toml: str,
    project_name: str,
    author: str,
    author_email: str,
    description: str,
) -> None:
    """
    Process pyproject.toml file and inject metadata.

    :param pyproject_toml: Path to pyproject.toml file
    :param project_name: Project name
    :param author: Author name
    :param author_email: Author email
    :param description: Project description
    """
    if not pyproject_toml or not os.path.exists(pyproject_toml):
        return

    try:
        with open(pyproject_toml, "r", encoding="utf-8") as f:
            content = f.read()

        # Replace placeholders
        replacements = {
            "<project_name>": project_name,
            "<author>": author,
            "<author_email>": author_email,
            "<description>": description,
        }

        content = _apply_escaped_replacements(content, replacements, pyproject_toml)

        content = _ensure_pyproject_fastkit_markers(content)

        with open(pyproject_toml, "w", encoding="utf-8") as f:
            f.write(content)

        debug_log("Injected metadata into pyproject.toml", "info")
        print_info("Injected metadata into pyproject.toml")

    except (OSError, UnicodeDecodeError) as e:
        debug_log(f"Error processing pyproject.toml: {e}", "error")
        raise BackendExceptions(f"Failed to process pyproject.toml: {e}")


_DESCRIPTION_LINE_PATTERN = re.compile(
    r'^(?P<prefix>description\s*=\s*)"(?P<value>.*?)"(?P<suffix>\s*)$',
    re.MULTILINE,
)


# The ``[tool.fastapi-fastkit]`` table body cannot be matched with a regex: a
# ``features = [...]`` array contains ``[`` characters, so an "everything up to
# the next bracket" pattern stops in the middle of the table and leaves half of
# it behind. The extent of the table is found line by line instead, using the
# two patterns below (see ``_replace_fastkit_section``).
_FASTKIT_SECTION_HEADER_PATTERN = re.compile(
    r"^\[tool\." + re.escape(FASTKIT_TOOL_SECTION) + r"\]\s*(?:#.*)?$"
)

#: A TOML table / array-of-tables header line, used as the section terminator.
_TOML_TABLE_HEADER_PATTERN = re.compile(r"^\[\[?[^\[\]]+\]\]?\s*(?:#.*)?$")


def _replace_fastkit_section(content: str, block: str) -> str:
    """
    Replace an existing ``[tool.fastapi-fastkit]`` table with ``block``.

    The table runs from its header up to (but excluding) the next line that
    starts a new TOML table, so a multi-line ``features`` array inside it is
    replaced together with the rest of the table instead of being orphaned.

    :param content: Full pyproject.toml text
    :param block: Rendered replacement table, newline-terminated
    :return: Updated content (unchanged when no section is present)
    """
    lines = content.splitlines(keepends=True)

    start = next(
        (
            index
            for index, line in enumerate(lines)
            if _FASTKIT_SECTION_HEADER_PATTERN.match(line.strip())
        ),
        None,
    )
    if start is None:
        return content

    end = len(lines)
    for index in range(start + 1, len(lines)):
        if _TOML_TABLE_HEADER_PATTERN.match(lines[index].strip()):
            end = index
            break

    # Blank lines between this table and the next one belong to the file's
    # formatting, not to the table, so leave them in place.
    while end - 1 > start and not lines[end - 1].strip():
        end -= 1

    return "".join(lines[:start]) + block + "".join(lines[end:])


# Order the ``[tool.fastapi-fastkit]`` keys are emitted in. Stable ordering
# keeps generated pyproject diffs readable and matches the documented
# metadata contract.
_FASTKIT_METADATA_KEY_ORDER = (
    "managed",
    "version",
    "template",
    "preset",
    "package_manager",
    "app_module",
    "features",
)


def build_fastkit_metadata_block(metadata: Dict[str, Any]) -> str:
    """
    Render a ``[tool.fastapi-fastkit]`` TOML table from a metadata mapping.

    ``managed = true`` is always emitted so project detection keeps working
    even when a caller passes a partial mapping. Keys with a ``None`` value
    are omitted (that is how optional entries such as ``preset`` disappear
    for non-preset templates).

    :param metadata: Metadata mapping (see the project metadata contract)
    :return: TOML table text, newline-terminated
    """
    values: Dict[str, Any] = {"managed": True}
    values.update({k: v for k, v in metadata.items() if v is not None})

    ordered_keys = [k for k in _FASTKIT_METADATA_KEY_ORDER if k in values]
    ordered_keys += [k for k in values if k not in _FASTKIT_METADATA_KEY_ORDER]

    lines = [f"[tool.{FASTKIT_TOOL_SECTION}]"]
    lines += [f"{key} = {format_toml_value(values[key])}" for key in ordered_keys]
    return "\n".join(lines) + "\n"


def _ensure_pyproject_fastkit_markers(
    content: str, metadata: Optional[Dict[str, Any]] = None
) -> str:
    """Idempotently ensure pyproject content carries FastAPI-fastkit markers.

    Adds the canonical description marker if the ``description`` field does
    not already include it (case-insensitive check), and writes the
    ``[tool.fastapi-fastkit]`` section. Without ``metadata`` the section is
    only created when missing (``managed = true``); with ``metadata`` any
    existing section is replaced so re-running generation refreshes the
    recorded template / preset / app module rather than duplicating it.
    """
    marker = FASTKIT_DESCRIPTION_MARKER
    match = _DESCRIPTION_LINE_PATTERN.search(content)
    if match and marker.lower() not in match.group("value").lower():
        existing = match.group("value")
        new_value = f"{marker} {existing}".strip() if existing else marker
        content = (
            content[: match.start()]
            + f'{match.group("prefix")}"{new_value}"{match.group("suffix")}'
            + content[match.end() :]
        )

    tool_header = f"[tool.{FASTKIT_TOOL_SECTION}]"
    has_section = tool_header in content

    if metadata is None:
        if not has_section:
            if not content.endswith("\n"):
                content += "\n"
            content += f"\n{tool_header}\nmanaged = true\n"
        return content

    block = build_fastkit_metadata_block(metadata)

    if has_section:
        return _replace_fastkit_section(content, block)

    if not content.endswith("\n"):
        content += "\n"
    return content + "\n" + block


def write_fastkit_metadata(project_dir: str, metadata: Dict[str, Any]) -> None:
    """
    Write the ``[tool.fastapi-fastkit]`` block into a project's pyproject.toml.

    Called at the very end of scaffolding: package managers regenerate
    ``pyproject.toml`` while resolving dependencies, so the metadata block
    has to be (re)stamped after that step rather than during the initial
    placeholder substitution.

    :param project_dir: Path to the generated project directory
    :param metadata: Metadata mapping (see the project metadata contract)
    """
    pyproject_path = find_template_core_modules(project_dir).get("pyproject", "")
    if not pyproject_path:
        pyproject_path = os.path.join(project_dir, "pyproject.toml")

    if not os.path.exists(pyproject_path):
        debug_log("No pyproject.toml found; skipping fastkit metadata write", "warning")
        return

    try:
        with open(pyproject_path, "r", encoding="utf-8") as f:
            content = f.read()

        content = _ensure_pyproject_fastkit_markers(content, metadata)

        with open(pyproject_path, "w", encoding="utf-8") as f:
            f.write(content)

        debug_log("Wrote FastAPI-fastkit metadata into pyproject.toml", "info")

    except (OSError, UnicodeDecodeError) as e:
        debug_log(f"Error writing fastkit metadata: {e}", "error")
        print_warning(f"Could not write fastkit metadata: {e}")


def _render_dependency_array(dependencies: List[str]) -> str:
    """Render a PEP 621 ``dependencies`` array as multi-line TOML."""
    if not dependencies:
        return "[]"
    body = "\n".join(f'    "{dep}",' for dep in dependencies)
    return f"[\n{body}\n]"


def _update_pyproject_dependencies(
    pyproject_path: str, dependencies: List[str]
) -> bool:
    """
    Replace ``[project].dependencies`` in a pyproject.toml file.

    The array is located by bracket matching rather than a lazy regex so
    requirement strings carrying extras (``redis[hiredis]``) don't truncate
    the match.

    :param pyproject_path: Path to the project's pyproject.toml
    :param dependencies: Dependency specifications to write
    :return: True when the file was rewritten, False when no array was found
    """
    try:
        with open(pyproject_path, "r", encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError) as e:
        debug_log(f"Error reading pyproject.toml dependencies: {e}", "error")
        return False

    project_match = re.search(r"^\[project\]\s*$", content, re.MULTILINE)
    if not project_match:
        return False

    section_start = project_match.end()
    next_table = re.search(r"^\[", content[section_start:], re.MULTILINE)
    section_end = section_start + next_table.start() if next_table else len(content)
    section = content[section_start:section_end]

    deps_match = re.search(r"^dependencies\s*=\s*\[", section, re.MULTILINE)
    if not deps_match:
        return False

    array_start = section.rindex("[", deps_match.start(), deps_match.end())
    depth = 0
    array_end = -1
    for index in range(array_start, len(section)):
        char = section[index]
        if char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                array_end = index + 1
                break
    if array_end == -1:
        return False

    new_section = (
        section[: deps_match.start()]
        + f"dependencies = {_render_dependency_array(dependencies)}"
        + section[array_end:]
    )
    new_content = content[:section_start] + new_section + content[section_end:]

    try:
        with open(pyproject_path, "w", encoding="utf-8") as f:
            f.write(new_content)
    except OSError as e:
        debug_log(f"Error writing pyproject.toml dependencies: {e}", "error")
        return False

    return True


def update_setup_py_dependencies(project_dir: str, dependencies: List[str]) -> None:
    """
    Update the project's declared dependencies with the selected packages.

    ``pyproject.toml``'s ``[project].dependencies`` is the primary target —
    every current template ships one, and it is what every supported package
    manager installs from. ``setup.py`` is still updated when a template
    happens to ship one, purely as a legacy path.

    The function name is kept for backwards compatibility with existing
    callers and tests.

    :param project_dir: Path to the project directory
    :param dependencies: List of dependency specifications
    """
    updated_any = False

    pyproject_path = find_template_core_modules(project_dir).get("pyproject", "")
    if pyproject_path and os.path.exists(pyproject_path):
        if _update_pyproject_dependencies(pyproject_path, dependencies):
            updated_any = True
            print_info(f"Updated pyproject.toml with {len(dependencies)} dependencies")
        else:
            debug_log(
                "Could not find [project].dependencies in pyproject.toml", "warning"
            )

    setup_py_path = os.path.join(project_dir, "setup.py")
    if not os.path.exists(setup_py_path):
        if not updated_any:
            debug_log(
                "No pyproject.toml/setup.py dependency table found, skipping update",
                "info",
            )
        return

    try:
        with open(setup_py_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Build the new install_requires list
        deps_str = ",\n    ".join(f'"{dep}"' for dep in dependencies)

        # Try to replace existing install_requires first (with type annotation)
        pattern = r"install_requires:\s*list\[str\]\s*=\s*\[(.*?)\]"
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(
                pattern,
                f"install_requires: list[str] = [\n    {deps_str},\n]",
                content,
                flags=re.DOTALL,
            )
            debug_log(
                "Updated install_requires with type annotation in setup.py", "info"
            )
        else:
            # Fallback: try without type annotation
            pattern_old = r"install_requires\s*=\s*\[(.*?)\]"
            if re.search(pattern_old, content, re.DOTALL):
                content = re.sub(
                    pattern_old,
                    f"install_requires = [\n    {deps_str},\n]",
                    content,
                    flags=re.DOTALL,
                )
                debug_log("Updated install_requires in setup.py", "info")
            else:
                debug_log("Could not find install_requires in setup.py", "warning")
                return

        # Write updated content
        with open(setup_py_path, "w", encoding="utf-8") as f:
            f.write(content)

        print_info(f"Updated setup.py with {len(dependencies)} dependencies")

    except (OSError, UnicodeDecodeError) as e:
        debug_log(f"Error updating setup.py dependencies: {e}", "error")
        print_warning(f"Could not update setup.py: {e}")


def create_venv_with_manager(project_dir: str, manager_type: str = "pip") -> str:
    """
    Create a virtual environment using the specified package manager.

    :param project_dir: Path to the project directory
    :param manager_type: Type of package manager to use
    :return: Path to the virtual environment
    :raises: BackendExceptions if virtual environment creation fails
    """
    try:
        package_manager = PackageManagerFactory.create_manager(
            manager_type, project_dir, auto_detect=True
        )
        return package_manager.create_virtual_environment()
    except Exception as e:
        debug_log(
            f"Error creating virtual environment with {manager_type}: {e}", "error"
        )
        raise BackendExceptions(f"Failed to create virtual environment: {str(e)}")


def create_venv(project_dir: str) -> str:
    """
    Create a Python virtual environment in the project directory.

    This is a backward compatibility wrapper that uses pip by default.

    :param project_dir: Path to the project directory
    :return: Path to the virtual environment
    """
    return create_venv_with_manager(project_dir, "pip")


def install_dependencies_with_manager(
    project_dir: str, venv_path: str, manager_type: str = "pip"
) -> None:
    """
    Install dependencies using the specified package manager.

    :param project_dir: Path to the project directory
    :param venv_path: Path to the virtual environment
    :param manager_type: Type of package manager to use
    :return: None
    :raises: BackendExceptions if dependency installation fails
    """
    try:
        package_manager = PackageManagerFactory.create_manager(
            manager_type, project_dir, auto_detect=True
        )
        package_manager.install_dependencies(venv_path)
    except Exception as e:
        debug_log(f"Error installing dependencies with {manager_type}: {e}", "error")
        raise BackendExceptions(f"Failed to install dependencies: {str(e)}")


def install_dependencies(project_dir: str, venv_path: str) -> None:
    """
    Install dependencies in the virtual environment.

    This is a backward compatibility wrapper that uses pip by default.

    :param project_dir: Path to the project directory
    :param venv_path: Path to the virtual environment
    :return: None
    """
    install_dependencies_with_manager(project_dir, venv_path, "pip")


def generate_dependency_file_with_manager(
    project_dir: str,
    dependencies: List[str],
    manager_type: str = "pip",
    project_name: str = "",
    author: str = "",
    author_email: str = "",
    description: str = "",
) -> None:
    """
    Generate a dependency file using the specified package manager.

    :param project_dir: Path to the project directory
    :param dependencies: List of dependency specifications
    :param manager_type: Type of package manager to use
    :param project_name: Name of the project
    :param author: Author name
    :param author_email: Author email
    :param description: Project description
    :return: None
    :raises: BackendExceptions if dependency file generation fails
    """
    try:
        package_manager = PackageManagerFactory.create_manager(
            manager_type, project_dir, auto_detect=True
        )
        package_manager.generate_dependency_file(
            dependencies, project_name, author, author_email, description
        )

        # Also generate requirements.txt for pip compatibility (if not using pip)
        if manager_type != "pip":
            from pathlib import Path

            requirements_path = Path(project_dir) / "requirements.txt"
            try:
                with open(requirements_path, "w", encoding="utf-8") as f:
                    for dep in dependencies:
                        f.write(f"{dep}\n")
                debug_log("Generated requirements.txt for pip compatibility", "info")
            except (OSError, UnicodeEncodeError) as e:
                debug_log(
                    f"Warning: Could not generate requirements.txt: {e}", "warning"
                )

    except Exception as e:
        debug_log(f"Error generating dependency file with {manager_type}: {e}", "error")
        raise BackendExceptions(f"Failed to generate dependency file: {str(e)}")


# ------------------------------------------------------------
# Add Route Functions
# ------------------------------------------------------------


def resolve_project_layout(project_dir: str) -> Dict[str, str]:
    """
    Resolve where a generated project keeps its entrypoint and API router.

    Replaces the old ``src/main.py`` assumption. Resolution order:

    1. ``[tool.fastapi-fastkit].app_module`` in ``pyproject.toml`` — written
       at generation time, so it is authoritative for every fastkit project.
    2. On-disk discovery via :func:`find_template_core_modules`.
    3. A ``src/`` fallback so hand-made projects behave as they used to.

    :param project_dir: Path to the project directory
    :return: Mapping with ``main``, ``app_module``, ``package_dir``,
        ``package_module``, ``api_dir``, ``api_router_file`` and
        ``api_router_module`` entries (``main`` is empty when no entrypoint
        could be found).
    """
    metadata = read_fastkit_metadata(project_dir)

    main_path = ""
    recorded_module = metadata.get("app_module")
    if isinstance(recorded_module, str) and recorded_module:
        module_path = recorded_module.split(":")[0].replace(".", os.sep)
        candidate = os.path.join(project_dir, f"{module_path}.py")
        if os.path.exists(candidate):
            main_path = candidate

    if not main_path:
        main_path = find_template_core_modules(project_dir).get("main", "")

    if main_path:
        package_dir = os.path.dirname(main_path)
        app_module = app_module_from_main_path(project_dir, main_path)
    else:
        # Nothing discovered — keep the historical ``src/`` assumption so the
        # caller still gets a usable structure to create files in.
        package_dir = os.path.join(project_dir, "src")
        app_module = "src.main:app"

    package_module = _dotted_module(project_dir, package_dir)
    api_dir = os.path.join(package_dir, "api")
    api_router_file = _find_api_router_file(api_dir)
    stem = os.path.splitext(os.path.basename(api_router_file))[0]
    api_router_module = (
        f"{package_module}.api"
        if stem == "__init__"
        else f"{package_module}.api.{stem}"
    )

    return {
        "main": main_path,
        "app_module": app_module,
        "package_dir": package_dir,
        "package_module": package_module,
        "api_dir": api_dir,
        "api_router_file": api_router_file,
        "api_router_module": api_router_module,
    }


def _dotted_module(project_dir: str, path: str) -> str:
    """Convert a path inside the project into a dotted module prefix."""
    relative = os.path.relpath(path, project_dir)
    if relative in (".", ""):
        return ""
    return relative.replace(os.sep, ".")


# Router module filenames templates use, in precedence order. ``api.py`` is
# the classic-layered name, ``router.py`` the domain-starter one.
_API_ROUTER_FILENAMES = ("api.py", "router.py", "__init__.py")


def _find_api_router_file(api_dir: str) -> str:
    """
    Pick the file inside ``api/`` that declares ``api_router``.

    Falls back to ``api.py`` (the file ``addroute`` creates from the module
    template) when the package has no router file yet.
    """
    for filename in _API_ROUTER_FILENAMES:
        candidate = os.path.join(api_dir, filename)
        if not os.path.exists(candidate):
            continue
        try:
            with open(candidate, "r", encoding="utf-8") as f:
                content = f.read()
        except (OSError, UnicodeDecodeError):
            continue
        if "api_router" in content:
            return candidate

    return os.path.join(api_dir, "api.py")


def insert_import_line(content: str, import_line: str) -> str:
    """
    Insert an import statement using the ``# fastkit:imports`` anchor.

    Templates declare the anchor to say exactly where generated imports
    belong. Without one the insertion point is computed from the module's
    AST (right after the last top-level import), which is precise where the
    previous line-prefix scan was merely approximate.

    :param content: Source of the module being edited
    :param import_line: Import statement to add
    :return: Updated source (unchanged if the import is already present)
    """
    if import_line in content:
        return content

    anchored = _insert_after_anchor(content, IMPORT_ANCHOR, import_line)
    if anchored is not None:
        return anchored

    lines = content.split("\n")
    insert_at = _last_import_line(content)
    lines.insert(insert_at, import_line)
    return "\n".join(lines)


def insert_statement_line(
    content: str, statement: str, anchor: str = ROUTES_ANCHOR
) -> str:
    """
    Insert a statement at the ``# fastkit:routes`` anchor, else append it.

    :param content: Source of the module being edited
    :param statement: Statement to add
    :param anchor: Anchor comment to look for
    :return: Updated source (unchanged if the statement is already present)
    """
    if statement in content:
        return content

    anchored = _insert_after_anchor(content, anchor, statement)
    if anchored is not None:
        return anchored

    if content and not content.endswith("\n"):
        content += "\n"
    return f"{content}{statement}\n"


def _anchor_line_numbers(content: str, anchor: str) -> List[int]:
    """Return the 1-based line numbers carrying ``anchor`` as a real comment.

    Tokenising is what separates an anchor from a string that merely *looks*
    like one: a docstring or a ``"# fastkit:routes"`` literal must not be
    treated as an insertion point, because inserting a router registration
    inside a string silently produces a module that no longer registers it.
    Unparsable sources fall back to a plain scan so a template with a syntax
    error still behaves as it did before.
    """
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(content).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return [
            index
            for index, line in enumerate(content.split("\n"), start=1)
            if line.strip().startswith(anchor)
        ]

    return [
        token.start[0]
        for token in tokens
        if token.type == tokenize.COMMENT and token.string.strip().startswith(anchor)
    ]


def _insert_after_anchor(content: str, anchor: str, line: str) -> Optional[str]:
    """Insert ``line`` right below ``anchor``, preserving the anchor's indent.

    When a module declares the same anchor more than once the first one wins
    and the duplicates are reported: silently picking one of several
    insertion points makes generated code land somewhere the template author
    did not intend.

    Returns None when the anchor isn't present so callers can fall back.
    """
    anchor_lines = _anchor_line_numbers(content, anchor)
    if not anchor_lines:
        return None

    if len(anchor_lines) > 1:
        print_warning(
            f"Found {len(anchor_lines)} '{anchor}' anchors "
            f"(lines {', '.join(str(n) for n in anchor_lines)}); "
            "inserting at the first one.",
            title="Duplicate anchor",
        )

    lines = content.split("\n")
    index = anchor_lines[0] - 1
    existing = lines[index]
    indent = existing[: len(existing) - len(existing.lstrip())]
    lines.insert(index + 1, f"{indent}{line}")
    return "\n".join(lines)


def _last_import_line(content: str) -> int:
    """
    Return the 0-based line index just after the last top-level import.

    Uses ``ast`` so multi-line ``from x import (a, b)`` statements and
    imports appearing inside strings or functions are handled correctly.

    A module with no imports at all still has places an import may not go:
    a new import inserted at line 0 would land above the module docstring
    (demoting it to a plain expression) or above a ``from __future__``
    statement (which must stay first). So the fallback point is just after
    the docstring and any ``__future__`` imports.
    """
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return 0

    last_line = 0
    prelude_line = 0
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "__future__":
            prelude_line = max(prelude_line, node.end_lineno or node.lineno)
            last_line = max(last_line, node.end_lineno or node.lineno)
            continue
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            last_line = max(last_line, node.end_lineno or node.lineno)

    if last_line:
        return last_line

    docstring_node = tree.body[0] if tree.body else None
    if (
        isinstance(docstring_node, ast.Expr)
        and isinstance(docstring_node.value, ast.Constant)
        and isinstance(docstring_node.value.value, str)
    ):
        prelude_line = max(
            prelude_line, docstring_node.end_lineno or docstring_node.lineno
        )

    return prelude_line


def _ensure_project_structure(src_dir: str) -> Dict[str, str]:
    """
    Ensure the project structure exists for adding a new route.
    Creates necessary directories if they don't exist.

    :param src_dir: Source directory of the project
    :return: Dictionary with paths to target directories
    """
    if not os.path.exists(src_dir):
        raise BackendExceptions(f"Source directory not found at {src_dir}")

    # Define target directories
    target_dirs = {
        "api": os.path.join(src_dir, "api"),
        "api_routes": os.path.join(src_dir, "api", "routes"),
        "crud": os.path.join(src_dir, "crud"),
        "schemas": os.path.join(src_dir, "schemas"),
    }

    # Create directories and __init__.py files if needed
    for dir_name, dir_path in target_dirs.items():
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

            # Create __init__.py if it doesn't exist
            init_file = os.path.join(dir_path, "__init__.py")
            if not os.path.exists(init_file):
                with open(init_file, "w"):
                    pass

    return target_dirs


def _create_route_files(
    modules_dir: str, target_dirs: Dict[str, str], route_name: str
) -> None:
    """
    Create route files from templates.

    :param modules_dir: Path to the modules directory
    :param target_dirs: Dictionary with paths to target directories
    :param route_name: Name of the route to create
    """
    replacements = {"<new_route>": route_name}
    module_types = ["api/routes", "crud", "schemas"]

    for module_type in module_types:
        # Source template
        source = os.path.join(modules_dir, module_type, "new_route.py-tpl")

        # Target directory
        if module_type == "api/routes":
            target_dir = target_dirs["api_routes"]
        else:
            target_dir = target_dirs[module_type.split("/")[-1]]

        # Target file
        target = os.path.join(target_dir, f"{route_name}.py")

        if os.path.exists(target):
            print_warning(f"File {target} already exists, skipping...")
            continue

        if not copy_and_convert_template_file(source, target, replacements):
            print_warning(f"Failed to copy template file {source} to {target}")


def _handle_api_router_file(
    target_dirs: Dict[str, str],
    modules_dir: str,
    route_name: str,
    api_router_file: str = "",
) -> None:
    """
    Handle API router file creation or update.

    :param target_dirs: Dictionary with paths to target directories
    :param modules_dir: Path to the modules directory
    :param route_name: Name of the route
    :param api_router_file: Router file resolved from the project layout.
        Defaults to ``<api dir>/api.py`` for callers that don't resolve one.
    """
    api_dir = target_dirs["api"]
    if not api_router_file:
        api_router_file = os.path.join(api_dir, "api.py")

    if not os.path.exists(api_router_file):
        # Create the router module if it doesn't exist
        api_source = os.path.join(modules_dir, "api", "__init__.py-tpl")
        if os.path.exists(api_source):
            copy_and_convert_template_file(api_source, api_router_file)

    # Update API router to include new route
    if os.path.exists(api_router_file):
        _update_api_router(api_router_file, route_name)


def _update_api_router(api_router_file: str, route_name: str) -> None:
    """
    Update API router file to include new route.

    Insertion points come from the ``# fastkit:imports`` /
    ``# fastkit:routes`` anchors when the template declares them, and from
    the module's AST otherwise.

    :param api_router_file: Path to API router file
    :param route_name: Name of the route
    """
    try:
        with open(api_router_file, "r", encoding="utf-8") as f:
            content = f.read()

        route_import = f"from .routes import {route_name}"
        route_include = (
            f"api_router.include_router({route_name}.router, "
            f'prefix="/{route_name}", tags=["{route_name}"])'
        )

        if (
            route_import in content
            and f"api_router.include_router({route_name}.router" in content
        ):
            return  # Already included

        content = insert_import_line(content, route_import)
        content = insert_statement_line(content, route_include)

        with open(api_router_file, "w", encoding="utf-8") as f:
            f.write(content)

        debug_log(f"Updated API router to include {route_name}", "info")

    except (OSError, UnicodeDecodeError) as e:
        debug_log(f"Error updating API router: {e}", "error")


def _process_init_files(
    modules_dir: str, target_dirs: Dict[str, str], module_types: List[str]
) -> None:
    """
    Process __init__.py files if they don't exist.

    :param modules_dir: Path to the modules directory
    :param target_dirs: Dictionary with paths to target directories
    :param module_types: List of module types to process
    """
    for module_type in module_types:
        module_base = module_type.split("/")[0]
        init_source = os.path.join(modules_dir, module_base, "__init__.py-tpl")

        if os.path.exists(init_source):
            init_target_dir = target_dirs.get(module_base, None) or target_dirs.get(
                f"{module_base}_routes"
            )
            if init_target_dir:
                init_target = os.path.join(init_target_dir, "__init__.py")
                if not os.path.exists(init_target):
                    copy_and_convert_template_file(init_source, init_target)


def _update_main_app(
    src_dir: str,
    route_name: str,
    router_module: str = "",
    main_py_path: str = "",
) -> None:
    """
    Update the main application file to include the API router.

    :param src_dir: Package directory holding ``main.py`` (``src`` or
        ``src/app`` depending on the template layout)
    :param route_name: Name of the route to add
    :param router_module: Dotted module exposing ``api_router``. Derived from
        ``src_dir`` when omitted, preserving the classic ``src.api.api``.
    :param main_py_path: Explicit entrypoint path; defaults to
        ``<src_dir>/main.py``.
    """
    if not main_py_path:
        main_py_path = os.path.join(src_dir, "main.py")
    if not router_module:
        router_module = f"{os.path.basename(src_dir)}.api.api"

    if not os.path.exists(main_py_path):
        print_warning("main.py not found. Please manually add the API router.")
        return

    try:
        with open(main_py_path, "r", encoding="utf-8") as f:
            main_content = f.read()

        # Check if router is already imported or included
        router_import = f"from {router_module} import api_router"
        router_include = "app.include_router(api_router"

        if router_import in main_content and router_include in main_content:
            # Router already fully configured, nothing to do
            return

        # Check if FastAPI app is defined
        if "app = FastAPI" not in main_content:
            print_warning(
                "FastAPI app instance not found in main.py. Please manually add router."
            )
            return

        main_content = insert_import_line(main_content, router_import)

        if router_include not in main_content:
            main_content = insert_statement_line(
                main_content, "app.include_router(api_router)"
            )

        with open(main_py_path, "w", encoding="utf-8") as f:
            f.write(main_content)

        debug_log(f"Updated main.py to include router for {route_name}", "info")

    except (OSError, UnicodeDecodeError) as e:
        debug_log(f"Error updating main.py: {e}", "error")
        print_warning(f"Failed to update main.py: {e}")


def add_new_route(project_dir: str, route_name: str) -> None:
    """
    Add a new API route to an existing FastAPI project.

    The target locations come from :func:`resolve_project_layout`, so the
    command works for both the classic ``src/main.py`` layout and the
    domain-starter's ``src/app/main.py``.

    :param project_dir: Path to the project directory
    :param route_name: Name of the new route to add
    :raises BackendExceptions: If route addition fails
    """
    try:
        # Setup paths
        modules_dir = os.path.join(settings.FASTKIT_TEMPLATE_ROOT, "modules")
        layout = resolve_project_layout(project_dir)
        src_dir = layout["package_dir"]

        # Ensure project structure exists
        target_dirs = _ensure_project_structure(src_dir)

        # Create route files
        _create_route_files(modules_dir, target_dirs, route_name)

        # Handle API router file
        _handle_api_router_file(
            target_dirs, modules_dir, route_name, layout["api_router_file"]
        )

        # Process init files
        module_types = ["api/routes", "crud", "schemas"]
        _process_init_files(modules_dir, target_dirs, module_types)

        # Update main application
        _update_main_app(
            src_dir,
            route_name,
            router_module=layout["api_router_module"],
            main_py_path=layout["main"],
        )

        debug_log(f"Successfully added new route: {route_name}", "info")
        print_success(f"Route '{route_name}' has been added successfully!")

    except (OSError, PermissionError) as e:
        debug_log(f"File system error while adding route {route_name}: {e}", "error")
        handle_exception(e, f"Error adding new route: {str(e)}")
        raise BackendExceptions(f"Failed to add new route: {str(e)}")
    except BackendExceptions:
        # Re-raise our own exceptions
        raise
    except Exception as e:
        debug_log(f"Unexpected error while adding route {route_name}: {e}", "error")
        handle_exception(e, f"Error adding new route: {str(e)}")
        raise BackendExceptions(f"Failed to add new route: {str(e)}")


# ------------------------------------------------------------
# Create Project Folder Functions
# ------------------------------------------------------------


def ask_create_project_folder(project_name: str) -> bool:
    """
    Ask user whether to create a new project folder.

    :param project_name: Name of the project
    :return: True if user wants to create a folder, False otherwise
    """
    return click.confirm(
        f"\nCreate a new project folder named '{project_name}'?\n"
        f"Yes: Templates will be placed in './{project_name}/'\n"
        f"No: Templates will be placed in current directory",
        default=True,
    )


def deploy_template_files(
    target_template: str, user_local: str, project_name: str, create_folder: bool
) -> tuple[str, str, List[str]]:
    """
    Deploy template based on folder creation option.

    :param target_template: Path to template directory
    :param user_local: User's workspace directory
    :param project_name: Name of the project
    :param create_folder: Whether to create a new folder
    :return: Tuple of (project_dir, deployment_message, copied file paths). The
        file list lets callers keep later rewriting passes scoped to what this
        deployment actually wrote.
    """
    if create_folder:
        project_dir = os.path.join(user_local, project_name)
        deployment_message = f"FastAPI template project will deploy at '{user_local}' in folder '{project_name}'"
        copied = copy_and_convert_template(target_template, user_local, project_name)
    else:
        project_dir = user_local
        deployment_message = (
            f"FastAPI template project will deploy directly at '{user_local}'"
        )
        copied = copy_and_convert_template(target_template, user_local, "")

    click.echo(deployment_message)
    return project_dir, deployment_message, copied


def deploy_template_with_folder_option(
    target_template: str, user_local: str, project_name: str, create_folder: bool
) -> tuple[str, str]:
    """
    Deploy template based on folder creation option.

    Thin wrapper over :func:`deploy_template_files` kept for callers that do
    not need the list of copied files.

    :param target_template: Path to template directory
    :param user_local: User's workspace directory
    :param project_name: Name of the project
    :param create_folder: Whether to create a new folder
    :return: Tuple of (project_dir, deployment_message)
    """
    project_dir, deployment_message, _ = deploy_template_files(
        target_template, user_local, project_name, create_folder
    )
    return project_dir, deployment_message


def get_deployment_success_message(
    template: str, project_name: str, user_local: str, create_folder: bool
) -> str:
    """
    Get appropriate success message based on deployment option.

    :param template: Template name used
    :param project_name: Name of the project
    :param user_local: User's workspace directory
    :param create_folder: Whether folder was created
    :return: Success message string
    """
    if create_folder:
        return f"FastAPI project '{project_name}' from '{template}' has been created and saved to {user_local}!"
    else:
        return f"FastAPI project '{project_name}' from '{template}' has been deployed directly to {user_local}!"
