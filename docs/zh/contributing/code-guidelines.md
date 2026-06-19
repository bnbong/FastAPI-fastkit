# 代码规范

为参与 FastAPI-fastkit 贡献而准备的完整编码标准与最佳实践。

## 总览

这些规范用于保证 FastAPI-fastkit 项目在代码质量、一致性与可维护性上的水准。遵循这些标准,可以让代码库更易于阅读、维护与扩展。

## Python 代码风格

### PEP 8 一致性

遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/),并按以下具体约定:

- **行宽**:88 字符(Black 默认)
- **缩进**:4 空格(不要使用 tab)
- **末尾逗号**:多行结构必须保留末尾逗号
- **字符串引号**:优先使用双引号

### 代码格式化

我们使用 **Black** 进行自动格式化:

```python
# Good ✅
def create_project(
    name: str,
    template: str,
    options: Dict[str, Any],
) -> ProjectResult:
    """Create a new FastAPI project."""
    return ProjectResult(name=name, template=template)

# Bad ❌
def create_project(name: str, template: str, options: Dict[str,Any])->ProjectResult:
    """Create a new FastAPI project."""
    return ProjectResult(name=name,template=template)
```

### Import 组织

使用 **isort** 组织 import:

```python
# Standard library imports
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union

# Third-party imports
import click
import pydantic
from fastapi import FastAPI

# Local imports
from fastapi_fastkit.commands import BaseCommand
from fastapi_fastkit.utils import validation
from fastapi_fastkit.templates.manager import TemplateManager
```

## 类型注解

### 必备的类型注解

所有公共函数与方法必须带有类型注解:

```python
# Good ✅
def validate_project_name(name: str) -> bool:
    """Validate project name format."""
    return name.isidentifier() and not name.startswith('_')

def create_files(
    files: List[Path],
    template_data: Dict[str, Any]
) -> List[Path]:
    """Create files from template data."""
    created_files = []
    for file_path in files:
        # Implementation...
        created_files.append(file_path)
    return created_files

# Bad ❌
def validate_project_name(name):
    return name.isidentifier() and not name.startswith('_')
```

### 复杂类型注解

对复杂结构使用合适的类型注解:

```python
from typing import Dict, List, Optional, Union, Tuple, Any
from pathlib import Path

# Type aliases for complex types
ProjectConfig = Dict[str, Union[str, bool, List[str]]]
FileMapping = Dict[Path, str]
ValidationResult = Tuple[bool, Optional[str]]

def process_template(
    template_path: Path,
    config: ProjectConfig,
    output_dir: Optional[Path] = None,
) -> ValidationResult:
    """Process template with configuration."""
    # Implementation...
    return True, None
```

## 命名约定

### 变量与函数

- 变量与函数使用 **snake_case**
- 名称应**有描述性**,清晰表达用途
- **避免缩写**,除非该缩写已被广泛接受

```python
# Good ✅
project_name = "my-api"
template_directory = Path("templates")
user_input_data = get_user_input()

def validate_email_address(email: str) -> bool:
    """Validate email address format."""
    return "@" in email and "." in email

# Bad ❌
proj_nm = "my-api"
temp_dir = Path("templates")
usr_data = get_input()

def validate_email(e):
    return "@" in e and "." in e
```

### 类

- 类名使用 **PascalCase**
- 名称要**具体且具描述性**

```python
# Good ✅
class SomeClass:
    """Represents example class of FastAPI-fastkit."""
    pass

class SomeClassValidationError(Exception):
    """Raised when example class validation fails."""
    pass

class UserInputHandler:
    """Handles user input validation and processing."""
    pass

# Bad ❌
class Class:
    pass

class Error(Exception):
    pass

class Handler:
    pass
```

### 常量

- 使用带下划线的 **UPPER_CASE**
- 仅在**模块级**定义常量

```python
# Good ✅
DEFAULT_TEMPLATE_NAME = "fastapi-default"
MAX_PROJECT_NAME_LENGTH = 50
SUPPORTED_PYTHON_VERSIONS = ["3.8", "3.9", "3.10", "3.11", "3.12"]

# Bad ❌
default_template = "fastapi-default"
maxLength = 50
versions = ["3.8", "3.9", "3.10", "3.11", "3.12"]
```

## 文档标准

### Docstring

所有公共 API 使用 **Google 风格 docstring**:

```python
def create_project_structure(
    project_name: str,
    template_path: Path,
    output_directory: Optional[Path] = None,
    overwrite: bool = False,
) -> List[Path]:
    """Create project structure from template.

    Creates a new FastAPI project structure by copying and processing
    template files. Supports variable substitution and file customization.

    Args:
        project_name: Name of the project to create. Must be a valid
            Python identifier.
        template_path: Path to the template directory containing
            source files and configuration.
        output_directory: Directory where project will be created.
            Defaults to current working directory.
        overwrite: Whether to overwrite existing files. If False,
            raises error when files exist.

    Returns:
        List of created file paths in order of creation.

    Raises:
        ValueError: If project_name is invalid or empty.
        FileExistsError: If output directory exists and overwrite is False.
        TemplateNotFoundError: If template_path doesn't exist.
        PermissionError: If insufficient permissions to create files.

    Example:
        ```python
        template_path = Path("templates/fastapi-default")
        created_files = create_project_structure(
            project_name="my-api",
            template_path=template_path,
            output_directory=Path("./projects"),
            overwrite=False
        )
        print(f"Created {len(created_files)} files")
        ```
    """
    # Implementation here...
    pass
```

### 注释

- **解释 WHY,而不是 WHAT**
- **节制使用** —— 代码本身应具有自解释性
- 代码改动后**同步更新注释**

```python
# Good ✅
def validate_dependencies(requirements: List[str]) -> bool:
    """Validate project dependencies."""
    # Skip validation in development mode to allow experimental packages
    if os.getenv("FASTKIT_DEV_MODE"):
        return True

    # Check each requirement against known security vulnerabilities
    for requirement in requirements:
        if is_vulnerable_package(requirement):
            return False

    return True

# Bad ❌
def validate_dependencies(requirements: List[str]) -> bool:
    """Validate project dependencies."""
    # Check if dev mode
    if os.getenv("FASTKIT_DEV_MODE"):
        return True

    # Loop through requirements
    for requirement in requirements:
        # Check if vulnerable
        if is_vulnerable_package(requirement):
            return False

    # Return true
    return True
```

## 错误处理

### 异常处理

- 尽量**捕获具体异常**
- **提供有意义的错误信息**
- **合理地记录错误日志**

```python
# Good ✅
def load_template_config(template_path: Path) -> Dict[str, Any]:
    """Load template configuration from file."""
    config_file = template_path / "template.yaml"

    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise TemplateNotFoundError(
            f"Template configuration not found: {config_file}"
        )
    except yaml.YAMLError as e:
        raise TemplateConfigError(
            f"Invalid YAML syntax in {config_file}: {e}"
        )
    except PermissionError:
        raise TemplateAccessError(
            f"Permission denied reading {config_file}"
        )

# Bad ❌
def load_template_config(template_path: Path) -> Dict[str, Any]:
    """Load template configuration from file."""
    config_file = template_path / "template.yaml"

    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise Exception(f"Error loading config: {e}")
```

### 自定义异常

为不同错误场景定义具体的异常类:

```python
class FastKitError(Exception):
    """Base exception for FastAPI-fastkit errors."""
    pass

class ProjectCreationError(FastKitError):
    """Raised when project creation fails."""
    pass

class TemplateNotFoundError(FastKitError):
    """Raised when template is not found."""
    pass

class ValidationError(FastKitError):
    """Raised when input validation fails."""

    def __init__(self, message: str, field: str = None):
        super().__init__(message)
        self.field = field
```

## 测试标准

### 测试结构

测试要有清晰的结构与命名:

```python
class TestProjectCreation:
    """Test project creation functionality."""

    def test_create_project_with_valid_name(self, tmp_path):
        """Test project creation with valid project name."""
        project_name = "test-project"
        result = create_project(project_name, template="minimal", output=tmp_path)

        assert result.success is True
        assert (tmp_path / project_name).exists()
        assert (tmp_path / project_name / "src" / "main.py").exists()

    def test_create_project_with_invalid_name(self):
        """Test project creation fails with invalid name."""
        with pytest.raises(ValueError, match="Invalid project name"):
            create_project("invalid-project-name!", template="minimal")

    def test_create_project_overwrites_existing(self, tmp_path):
        """Test project creation overwrites existing directory when forced."""
        project_name = "existing-project"
        project_dir = tmp_path / project_name
        project_dir.mkdir()

        result = create_project(
            project_name,
            template="minimal",
            output=tmp_path,
            overwrite=True
        )

        assert result.success is True
        assert project_dir.exists()
```

### 测试覆盖率

- 对新代码,**目标覆盖率 90% 以上**
- **覆盖边界情况**与异常路径
- 对外部依赖使用 **mock**

```python
def test_template_download_with_network_error(mock_requests):
    """Test template download handles network errors gracefully."""
    mock_requests.get.side_effect = requests.ConnectionError("Network unreachable")

    with pytest.raises(TemplateDownloadError, match="Network error"):
        download_template("https://example.com/template.zip")

def test_file_creation_with_permission_error(mock_open):
    """Test file creation handles permission errors."""
    mock_open.side_effect = PermissionError("Permission denied")

    with pytest.raises(FileCreationError, match="Permission denied"):
        create_file(Path("/restricted/file.py"), content="test")
```

## Import 规范

### Import 组织

!!! note

    `isort` 格式化器会自动组织 import,只需运行 `bash scripts/format.sh` 即可。

1. **标准库** import 在最前
2. **第三方** import 在中间
3. **本地应用** import 在最后
4. 每组之间用**空行**分隔

```python
# Standard library
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Third-party
import click
import pydantic
import yaml
from fastapi import FastAPI

# Local application
from fastapi_fastkit.commands.base import BaseCommand
from fastapi_fastkit.utils.validation import validate_project_name
from fastapi_fastkit.templates import TemplateManager
```

### Import 最佳实践

- **避免通配 import**(`from module import *`)
- 使用**绝对 import**,保持清晰
- 当需要导入许多项时,**优先导入模块本身**

```python
# Good ✅
from fastapi_fastkit.utils import validation, files, formatting

# Good ✅ (when importing few items)
from fastapi_fastkit.utils.validation import validate_email, validate_project_name

# Bad ❌
from fastapi_fastkit.utils.validation import *

# Bad ❌ (when importing many items)
from fastapi_fastkit.utils.validation import (
    validate_email, validate_project_name, validate_template_name,
    validate_dependencies, validate_python_version, validate_directory
)
```

## 安全规范

### 输入校验

始终对用户输入进行校验与净化:

```python
def validate_project_name(name: str) -> str:
    """Validate and sanitize project name."""
    if not name:
        raise ValueError("Project name cannot be empty")

    if not name.isidentifier():
        raise ValueError("Project name must be a valid Python identifier")

    if name.startswith('_'):
        raise ValueError("Project name cannot start with underscore")

    if len(name) > 50:
        raise ValueError("Project name too long (max 50 characters)")

    # Sanitize by removing dangerous characters
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '', name)

    return sanitized
```

### 文件操作

谨慎处理文件路径与文件操作:

```python
def create_file_safely(file_path: Path, content: str, base_dir: Path) -> None:
    """Create file safely within base directory."""
    # Resolve to prevent directory traversal attacks
    resolved_path = file_path.resolve()
    resolved_base = base_dir.resolve()

    # Ensure file is within base directory
    try:
        resolved_path.relative_to(resolved_base)
    except ValueError:
        raise SecurityError(f"File path outside base directory: {file_path}")

    # Create parent directories safely
    resolved_path.parent.mkdir(parents=True, exist_ok=True)

    # Write file with appropriate permissions
    resolved_path.write_text(content, encoding='utf-8')
    resolved_path.chmod(0o644)  # Read/write for owner, read for others
```

## 性能规范

### 高效的代码写法

- 对大数据集**使用生成器**
- **避免过早优化**
- **先剖析,再优化**

```python
# Good ✅ - Generator for memory efficiency
def process_large_template(template_files: List[Path]) -> Iterator[ProcessedFile]:
    """Process template files efficiently."""
    for file_path in template_files:
        content = file_path.read_text()
        processed_content = process_template_content(content)
        yield ProcessedFile(path=file_path, content=processed_content)

# Bad ❌ - Loads everything into memory
def process_large_template(template_files: List[Path]) -> List[ProcessedFile]:
    """Process template files."""
    results = []
    for file_path in template_files:
        content = file_path.read_text()
        processed_content = process_template_content(content)
        results.append(ProcessedFile(path=file_path, content=processed_content))
    return results
```

### 缓存

对开销大的操作使用缓存:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_template_metadata(template_path: Path) -> TemplateMetadata:
    """Get template metadata with caching."""
    config_file = template_path / "template.yaml"

    if not config_file.exists():
        return TemplateMetadata(name=template_path.name)

    config = yaml.safe_load(config_file.read_text())
    return TemplateMetadata.from_config(config)
```

## Git 提交规范

### 提交信息格式

使用约定式提交(Conventional Commits)格式:

```
type(scope): description

[optional body]

[optional footer]
```

### 提交类型

- **feat**:新特性
- **fix**:bug 修复
- **docs**:文档相关改动
- **style**:代码风格改动(格式化等)
- **refactor**:代码重构
- **test**:增加或调整测试
- **chore**:维护性任务

### 示例

```bash
# Good ✅
feat(cli): add template validation command

Add new command to validate template structure and configuration.
The command checks for required files, validates YAML syntax,
and ensures template follows conventions.

Closes #123

# Good ✅
fix(templates): handle missing dependency files gracefully

When a template references a requirements file that doesn't exist,
show a clear error message instead of crashing.

# Bad ❌
update stuff

# Bad ❌
Fixed bug
```

## 代码评审规范

### 对作者而言

提交评审前请确认:

1. **运行全部测试**,且全部通过
2. **核查测试覆盖率**未下滑
3. **必要时更新文档**
4. **遵循提交信息**规范
5. **保持 PR 聚焦且小**

### 对评审者而言

评审时请关注:

1. **功能是否正确** —— 行为是否符合预期?
2. **测试是否完善** —— 是否覆盖边界情况?
3. **文档是否同步** —— 描述是否清晰、最新?
4. **代码风格** —— 是否遵循项目约定?
5. **是否考虑安全** —— 是否存在潜在漏洞?

### 评审清单

- [ ] 代码符合风格规范
- [ ] 测试齐备且全部通过
- [ ] 文档已更新
- [ ] 无安全漏洞
- [ ] 已考虑性能问题
- [ ] 错误处理得当
- [ ] 提交信息符合规范

## 工具与自动化

### Pre-commit 钩子

我们使用 pre-commit 钩子来强制执行标准:

```yaml
# .pre-commit-config.yaml
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-toml

-   repo: local
    hooks:
    -   id: format
        name: format
        entry: black --config pyproject.toml --check .
        language: python
        types: [python]
        additional_dependencies: ['black>=24.10.0']
        pass_filenames: false

    -   id: isort-check
        name: isort check
        entry: isort --sp pyproject.toml --check-only --diff .
        language: python
        types: [python]
        additional_dependencies: ['isort>=5.13.2']
        pass_filenames: false

    -   id: isort-fix
        name: isort fix
        entry: isort --sp pyproject.toml .
        language: python
        types: [python]
        additional_dependencies: ['isort>=5.13.2']
        pass_filenames: false

    -   id: black-fix
        name: black fix
        entry: black --config pyproject.toml .
        language: python
        types: [python]
        additional_dependencies: ['black>=24.10.0']
        pass_filenames: false

    -   id: mypy
        name: mypy
        entry: mypy --config-file pyproject.toml src
        language: python
        types: [python]
        additional_dependencies:
          - mypy>=1.12.0
          - rich>=13.9.2
          - click>=8.1.7
          - pyyaml>=6.0.0
          - types-PyYAML>=6.0.12
        pass_filenames: false

ci:
    autofix_commit_msg: 🎨 [pre-commit.ci] Auto format from pre-commit.com hooks
    autoupdate_commit_msg: ⬆ [pre-commit.ci] pre-commit autoupdate
```

!!! note

    Pre-commit 钩子使用隔离的 Python 环境(`language: python`)。

### IDE 配置

推荐的 VS Code 设置:

```json
{
    "python.linting.enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.path": "isort",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

## 下一步

读完这些规范后:

1. **配置开发环境**,参见 [开发环境配置](development-setup.md)
2. **从小贡献开始练手**,熟悉流程
3. **在 GitHub Discussions 提问**,有不明之处随时问
4. **阅读已有代码**,看看这些规范在实践中的样子

!!! tip "速查"
    - 用 `make check-all` 验证您的代码是否满足全部规范
    - 配置 pre-commit 钩子,尽早发现问题
    - 拿不准时,看现有代码作为示例
    - 评审中遇到问题,不要犹豫,主动求助

遵循这些规范有助于让 FastAPI-fastkit 保持高水准的代码质量,并让所有人协作起来更轻松!🚀
