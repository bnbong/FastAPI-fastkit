# 开发环境配置

为参与 FastAPI-fastkit 贡献而准备开发环境的完整指南。

## 前置条件

开始之前,请确认您已具备:

- 已安装 **Python 3.12 及以上**
- 已安装并配置 **Git**
- 具备 **Python 与 FastAPI 的基础知识**
- 一个 **文本编辑器或 IDE**(VS Code、PyCharm 等)

## 借助 Makefile 快速配置

FastAPI-fastkit 提供了用于简化开发环境配置的 Makefile:

<div class="termy">

```console
$ git clone https://github.com/bnbong/FastAPI-fastkit.git
$ cd FastAPI-fastkit
$ make install-dev
Setting up development environment...
Creating virtual environment...
Installing dependencies...
Installing pre-commit hooks...
✅ Development environment ready!
```

</div>

这一条命令会:

- 以可编辑模式安装包及其开发依赖
- 安装 pre-commit 钩子
- 配置开发工具

!!! note

    在运行该命令前,建议先创建并激活虚拟环境。

## 手动配置

如果您倾向于手动配置,或 Makefile 在您的系统上无法正常工作:

### 1. 克隆仓库

<div class="termy">

```console
$ git clone https://github.com/bnbong/FastAPI-fastkit.git
$ cd FastAPI-fastkit
```

</div>

### 2. 创建虚拟环境

<div class="termy">

```console
$ python -m venv .venv
$ source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

</div>

### 3. 安装依赖

<div class="termy">

```console
# Install package in editable mode with development dependencies
$ pip install -e ".[dev]"

# Or install from requirements files
$ pip install -r requirements.txt
$ pip install -r requirements-dev.txt
```

</div>

### 4. 配置 pre-commit 钩子

<div class="termy">

```console
$ pre-commit install
pre-commit installed at .git/hooks/pre-commit
```

</div>

### 5. 验证安装

<div class="termy">

```console
$ fastkit --version
fastapi-fastkit, version 1.2.1

$ python -m pytest tests/
======================== test session starts ========================
collected 45 items
tests/test_cli.py::test_init_command PASSED
tests/test_templates.py::test_template_listing PASSED
...
======================== 45 passed in 2.34s ========================
```

</div>

## 开发工具

开发环境包含多种工具,用于维护代码质量:

### 一行命令

使用 Makefile:

```console
$ make format lint
Running isort...
Running black...
Running mypy...
✅ All checks passed!
```

使用项目自带脚本:

```console
$ ./scripts/format.sh
$ ./scripts/lint.sh
```

### 代码格式化

**Black** —— 代码格式化器:

<div class="termy">

```console
$ black src/ tests/
reformatted src/main.py
reformatted tests/test_cli.py
All done! ✨ 🍰 ✨
```

</div>

**isort** —— import 排序:

<div class="termy">

```console
$ isort src/ tests/
Fixing import order in src/main.py
```

</div>

### 代码静态检查

**mypy** —— 类型检查:

<div class="termy">

```console
$ mypy src/
Success: no issues found in 12 source files
```

</div>

## 可用的 Make 命令

项目的 Makefile 为常见的开发任务提供了便捷命令:

### 安装命令

| 命令 | 描述 |
|---------|-------------|
| `make install` | 以生产模式安装包 |
| `make install-dev` | 以包含开发依赖的方式安装包 |
| `make install-test` | 为测试用途安装包(卸载并重新安装) |
| `make uninstall` | 卸载包 |
| `make clean` | 清理构建产物与缓存文件 |

### 代码质量命令

| 命令 | 描述 |
|---------|-------------|
| `make format` | 使用 black 与 isort 格式化代码 |
| `make format-check` | 检查代码格式,但不做修改 |
| `make lint` | 运行所有静态检查(isort、black、mypy) |

### 测试命令

| 命令 | 描述 |
|---------|-------------|
| `make test` | 运行全部测试 |
| `make test-verbose` | 以详细模式运行测试 |
| `make test-coverage` | 运行测试并生成覆盖率报告 |
| `make coverage-report` | 生成详细的覆盖率报告(FORMAT=html/xml/json/all) |

### 模板检查命令

| 命令 | 描述 |
|---------|-------------|
| `make inspect-templates` | 对所有模板执行模板检查 |
| `make inspect-templates-verbose` | 以详细输出运行模板检查 |
| `make inspect-template` | 检查指定模板(TEMPLATES 参数) |

### 文档命令

| 命令 | 描述 |
|---------|-------------|
| `make serve-docs` | 在本地启动文档服务 |
| `make build-docs` | 构建文档 |

### 翻译命令

| 命令 | 描述 |
|---------|-----------|
| `make translate` | 翻译文档(LANG、PROVIDER、MODEL 参数) |

### 示例

<div class="termy">

```console
# Format code and run all checks
$ make format lint
Running isort...
Running black...
Running mypy...
✅ All checks passed!

# Run tests with coverage
$ make test-coverage
======================== test session starts ========================
collected 45 items
tests/test_cli.py::test_init_command PASSED
...
======================== 45 passed in 2.34s ========================

---------- coverage: platform darwin, python 3.12.1-final-0 ----------
Name                     Stmts   Miss  Cover
--------------------------------------------
src/main.py                 45      2    96%
src/cli.py                  89      5    94%
src/templates.py            67      3    96%
--------------------------------------------
TOTAL                      201     10    95%

# Generate HTML coverage report
$ make coverage-report FORMAT=html
🌐 Opening HTML coverage report in browser...

# Translate documentation to Korean
$ make translate LANG=ko PROVIDER=github MODEL=gpt-4o-mini
Starting translation...
Running: python scripts/translate.py --target-lang ko --api-provider github --model gpt-4o-mini
```

</div>

## 项目结构

理解项目结构对开发工作至关重要:

```bash
FastAPI-fastkit/
├── src/
│   ├── fastapi_fastkit/
│   │   ├── __main__.py                      # Entry point of the application
│   │   ├── backend/
│   │   │   ├── inspector.py                 # FastAPI-fastkit template inspector
│   │   │   ├── interactive/
│   │   │   │   ├── config_builder.py        # Configuration builder for interactive mode
│   │   │   │   ├── prompts.py               # Prompts for interactive mode
│   │   │   │   ├── selectors.py             # Selectors logic for interactive mode
│   │   │   │   └── validators.py            # User input validators for interactive mode
│   │   │   ├── main.py                      # Backend's logic entry point
│   │   │   ├── package_managers/
│   │   │   │   ├── base.py                  # Base class for package managers
│   │   │   │   ├── factory.py               # Factory for package managers
│   │   │   │   ├── pdm_manager.py           # PDM package manager
│   │   │   │   ├── pip_manager.py           # pip package manager
│   │   │   │   ├── poetry_manager.py        # Poetry package manager
│   │   │   │   └── uv_manager.py            # uv package manager
│   │   │   ├── project_builder/
│   │   │   │   ├── config_generator.py      # Configuration generator for project builder
│   │   │   │   └── dependency_collector.py  # Dependency collector for project builder
│   │   │   └── transducer.py                # Transducer for project builder
│   │   ├── cli.py                           # FastAPI-fastkit main CLI entry point
│   │   ├── core/
│   │   │   ├── exceptions.py                # Exception handling
│   │   │   └── settings.py                  # Settings configuration
│   │   ├── fastapi_project_template/
│   │   │   ├── PROJECT_README_TEMPLATE.md   # fastkit template project base README file
│   │   │   ├── README.md                    # fastkit template README
│   │   │   ├── fastapi-async-crud/
│   │   │   ├── fastapi-custom-response/
│   │   │   ├── fastapi-default/
│   │   │   ├── fastapi-dockerized/
│   │   │   ├── fastapi-empty/
│   │   │   ├── fastapi-mcp/
│   │   │   ├── fastapi-psql-orm/
│   │   │   ├── fastapi-single-module/
│   │   │   └── modules/
│   │   │       ├── api/
│   │   │       │   └── routes/
│   │   │       ├── crud/
│   │   │       └── schemas/
│   │   ├── py.typed
│   │   └── utils/
│   │       ├── logging.py                   # Logging configuration
│   │       └── main.py                      # FastAPI-fastkit main entry point
│   └── logs
├── tests
│   ├── conftest.py                          # pytest configuration
│   ├── test_backends/
│   ├── test_cli_operations/
│   ├── test_core.py
│   ├── test_rich/
│   ├── test_templates/
│   └── test_utils.py
├── uv.lock
├── docs/                                    # Documentation
├── scripts/                                 # Development scripts
├── mkdocs.yml
├── overrides/                               # mkdocs overrides
├── pdm.lock
├── pyproject.toml
├── requirements-docs.txt                    # requirements for documentation
├── requirements.txt                         # requirements for development
├── CHANGELOG.md
├── CITATION.cff
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE
├── MANIFEST.in
├── Makefile
├── README.md
├── SECURITY.md
└── env.example                              # environment example(configures translation AI model env vars)
```

### 关键目录

- **`src/fastapi_fastkit/`** —— 主包源码
    - **`cli.py`** —— 主 CLI 入口
    - **`backend/`** —— 核心后端逻辑
        - **`inspector.py`** —— 模板检查器
        - **`interactive/`** —— 交互模式相关组件(提示、选择器、校验器)
        - **`package_managers/`** —— 包管理器实现(pip、uv、pdm、poetry)
        - **`project_builder/`** —— 项目构建工具
        - **`transducer.py`** —— 模板 transducer
    - **`core/`** —— 核心配置与异常
    - **`fastapi_project_template/`** —— 项目模板(fastapi-default、fastapi-async-crud 等)
    - **`utils/`** —— 共享工具函数
- **`tests/`** —— 测试套件
    - **`test_backends/`** —— 针对后端的测试
    - **`test_cli_operations/`** —— CLI 操作的测试
    - **`test_templates/`** —— 模板系统的测试
- **`docs/`** —— 文档(MkDocs)
    - 用户指南、教程与 API 参考

## 开发工作流

### 1. 创建特性分支

<div class="termy">

```console
$ git checkout -b feature/add-new-template
Switched to a new branch 'feature/add-new-template'
```

</div>

### 2. 进行改动

编辑代码、添加特性、修复 bug……

### 3. 运行测试与检查

<div class="termy">

```console
$ make dev-check
Running all quality checks...
Running all tests...
✅ All tests passed!
```

</div>

### 4. 提交改动

pre-commit 钩子会自动运行:

<div class="termy">

```console
$ git add .
$ git commit -m "Add new FastAPI template with authentication"
format...................................................................Passed
isort-check..............................................................Passed
black-fix................................................................Passed
mypy.....................................................................Passed
[feature/add-new-template abc1234] Add new FastAPI template with authentication
```

</div>

### 5. 推送并创建 Pull Request

<div class="termy">

```console
$ git push origin feature/add-new-template
$ gh pr create --title "Add new FastAPI template with authentication"
```

</div>

## 测试

### 运行测试

**全部测试:**

<div class="termy">

```console
$ make test
# or
$ python -m pytest
```

</div>

**指定测试文件:**

<div class="termy">

```console
$ python -m pytest tests/test_cli.py -v
```

</div>

**带覆盖率:**

<div class="termy">

```console
$ make test-coverage
# or
$ python -m pytest --cov=src --cov-report=html
```

</div>

### 编写测试

新增特性时,务必同步编写测试:

```python
# tests/test_commands/test_new_feature.py
import pytest
from fastapi_fastkit.commands.new_feature import NewFeatureCommand

class TestNewFeatureCommand:
    def test_command_success(self):
        """Test successful command execution"""
        command = NewFeatureCommand()
        result = command.execute(valid_args)
        assert result.success is True
        assert result.message == "Feature executed successfully"

    def test_command_validation_error(self):
        """Test command with invalid arguments"""
        command = NewFeatureCommand()
        with pytest.raises(ValueError, match="Invalid argument"):
            command.execute(invalid_args)

    def test_command_edge_case(self):
        """Test edge case handling"""
        command = NewFeatureCommand()
        result = command.execute(edge_case_args)
        assert result.success is True
        assert "warning" in result.message.lower()
```

### 测试分类

**单元测试** —— 测试单个函数与类:

```python
def test_validate_project_name():
    assert validate_project_name("valid-name") is True
    assert validate_project_name("invalid name!") is False
```

**集成测试** —— 测试命令之间的交互:

```python
def test_init_command_creates_project(tmp_path):
    result = runner.invoke(cli, ['init'], input='test-project\n...')
    assert result.exit_code == 0
    assert (tmp_path / "test-project").exists()
```

**端到端测试** —— 测试完整的工作流:

```python
def test_full_project_creation_workflow(tmp_path):
    # Create project
    result = runner.invoke(cli, ['init'], input='...')
    assert result.exit_code == 0

    # Add route
    result = runner.invoke(cli, ['addroute', 'test-project', 'users'])
    assert result.exit_code == 0

    # Verify files exist
    assert (tmp_path / "test-project" / "src" / "api" / "routes" / "users.py").exists()
```

## 文档

### 在本地启动文档服务

<div class="termy">

```console
$ make serve-docs
INFO     -  Building documentation...
INFO     -  Cleaning site directory
INFO     -  Documentation built in 0.43 seconds
INFO     -  [14:30:00] Serving on http://127.0.0.1:8000/
```

</div>

### 构建文档

<div class="termy">

```console
$ make build-docs
INFO     -  Building documentation...
INFO     -  Documentation built in 0.43 seconds
```

</div>

### 编写文档

文档使用 Markdown 编写,由 MkDocs 构建。以下是示例结构:

**特性指南模板:**

````markdown
# New Feature Guide

This guide explains how to use the new feature.

## Prerequisites

- FastAPI-fastkit installed
- Basic Python knowledge

## Usage

<div class="termy">

```console
$ fastkit new-feature --option value
✅ Feature executed successfully!
```

</div>

!!! tip "Pro Tip"
    Use `--help` to see all available options.
````

要了解 `mkdocs-material` 的详细参考,请查看 [mkdocs-material 文档](https://squidfunk.github.io/mkdocs-material/reference/admonitions/)。

## 代码风格指南

### Python 代码风格

遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/),并附加以下具体约定:

- **行宽**:88 字符(Black 默认)
- **import**:由 isort 组织
- **类型注解**:所有公共函数都必须提供
- **docstring**:所有公共 API 使用 Google 风格

### 示例

```python
from typing import List, Optional
from pathlib import Path

def create_project_structure(
    project_name: str,
    template_path: Path,
    output_dir: Optional[Path] = None,
) -> List[Path]:
    """Create project structure from template.

    Args:
        project_name: Name of the project to create
        template_path: Path to the template directory
        output_dir: Output directory, defaults to current directory

    Returns:
        List of created file paths

    Raises:
        ValueError: If project_name is invalid
        FileNotFoundError: If template_path doesn't exist
    """
    if not project_name.isidentifier():
        raise ValueError(f"Invalid project name: {project_name}")

    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    # Implementation here...
    return created_files
```

## 环境变量

进行开发时,您可以设置以下环境变量:

| 变量 | 描述 | 默认值 |
|----------|-------------|---------|
| `FASTKIT_DEBUG` | 启用调试日志 | `False` |
| `FASTKIT_DEV_MODE` | 启用开发模式特性 | `False` |
| `FASTKIT_TEMPLATE_DIR` | 自定义模板目录 | 内置模板 |
| `FASTKIT_CONFIG_DIR` | 配置目录 | `~/.fastkit` |
| `TRANSLATION_API_KEY` | 翻译 API key(使用 [Github AI 模型提供方](https://github.com/marketplace/models/azure-openai) 时填写 Github PAT) | `None` |

<div class="termy">

```console
$ export FASTKIT_DEBUG=true
$ export FASTKIT_DEV_MODE=true
$ fastkit init
DEBUG: Loading configuration from /home/user/.fastkit/
DEBUG: Available templates: ['fastapi-default', ...]
```

</div>

其他环境变量设置请参阅 [@settings.py](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/core/settings.py) 模块。

## 故障排查

### 常见问题

**1. pre-commit 钩子失败:**

<div class="termy">

```console
$ git commit -m "Fix bug"
black....................................................................Failed
hookid: black

Files were modified by this hook. Additional output:

would reformat src/cli.py
```

</div>

**解决办法:** 运行格式化器后再次提交:

<div class="termy">

```console
$ make format
$ git add .
$ git commit -m "Fix bug"
```

</div>

**2. 在不同 Python 版本上测试失败:**

**解决办法:** 使用 tox 在多个 Python 版本上测试:

<div class="termy">

```console
$ pip install tox
$ tox
py38: commands succeeded
py39: commands succeeded
py310: commands succeeded
py311: commands succeeded
py312: commands succeeded
```

</div>

**3. 开发时出现 import 错误:**

**解决办法:** 以可编辑模式安装包:
<div class="termy">

```console
$ pip install -e .
```

</div>

### 获取帮助

- **[GitHub Issues](https://github.com/bnbong/FastAPI-fastkit/issues)**:报告 bug 与请求特性
- **[GitHub Discussions](https://github.com/bnbong/FastAPI-fastkit/discussions)**:提问与分享想法
- **文档**:查看 [用户指南](../user-guide/installation.md)

## 贡献指南

### 提交 PR 之前

1. **运行所有检查:** `make dev-check`
2. **必要时更新文档**
3. **为新特性增加测试**
4. **遵循提交信息规范**

### 提交信息格式

```
type(scope): brief description

Longer description if needed

Fixes #123
```

**类型(type):**

- `feat`:新特性
- `fix`:bug 修复
- `docs`:文档相关改动
- `style`:代码风格改动
- `refactor`:代码重构
- `test`:增加 / 调整测试
- `chore`:维护性任务

**示例:**

```
feat(cli): add new template command

Add support for creating projects from custom templates.
The command accepts a template path and creates a new
project with the specified configuration.

Fixes #45

fix(templates): handle missing template files gracefully

When a template file is missing, show a clear error message
instead of crashing with a stack trace.

Fixes #67
```

## 发布流程

对维护者而言,发布流程如下:

1. **更新版本号**(`setup.py` 与 `__init__.py`)
2. **更新 CHANGELOG.md**
3. **创建发布 PR**
4. **合并后打 tag**
5. **GitHub Actions** 自动构建并发布

<div class="termy">

```console
$ git tag v1.2.0
$ git push origin v1.2.0
```

</div>

## 下一步

开发环境已就绪后:

1. **[浏览代码库](https://github.com/bnbong/FastAPI-fastkit/tree/main/src/fastapi_fastkit)** —— 理解整体架构
2. **运行测试套件**,确认一切正常
3. **从 GitHub 上挑选一个 [issue](https://github.com/bnbong/FastAPI-fastkit/issues)** 着手开发
4. **加入 [discussions](https://github.com/bnbong/FastAPI-fastkit/discussions)**,与其他贡献者交流

祝您编码愉快!🚀

!!! tip "开发小贴士"
    - 提交前先运行 `make dev-check`
    - 优先编写测试(TDD 方式)
    - 让每次提交保持小而聚焦
    - 新特性同时更新文档
