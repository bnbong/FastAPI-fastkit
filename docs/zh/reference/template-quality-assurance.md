# 模板质量保障

FastAPI-fastkit 提供了完善的自动化模板校验,确保所有模板在不同环境与包管理器下都保持高质量且可正常工作。

## 多层质量保障

FastAPI-fastkit 同时使用**两套互补的质量保障系统**:

### 1. 静态模板检查
**对模板结构与语法的每周自动校验**

### 2. 动态模板测试
**包含真实项目创建的完整端到端测试**

## 自动化的每周检查

每周三午夜(UTC),我们的 GitHub Actions 工作流会自动检查所有 FastAPI 模板,确保它们达到质量标准:

- ✅ **文件结构校验** —— 确保所有必备文件与目录都存在
- ✅ **文件扩展名核对** —— 确认模板文件使用正确的 `.py-tpl` 扩展名
- ✅ **依赖检查** —— 确认 FastAPI 及必要依赖被正确声明
- ✅ **FastAPI 实现** —— 确认模板包含合规的 FastAPI 应用初始化
- ✅ **测试执行** —— 运行模板的测试以确认功能正常

## 自动化模板测试系统

FastAPI-fastkit 自带一套**革新性的自动化测试系统**,对每个模板进行完整校验:

### 动态模板发现

测试系统会**自动发现所有模板**,无需手动配置:

```console
# Test all templates automatically
$ pytest tests/test_templates/test_all_templates.py -v

# Results show all discovered templates
PASSED tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[fastapi-default]
PASSED tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[fastapi-async-crud]
PASSED tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[fastapi-dockerized]
PASSED tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[fastapi-psql-orm]
```

### 全面的测试覆盖

每个模板都会经历**完整的端到端测试**:

#### ✅ 项目创建过程
- 模板复制与文件转换
- 项目元数据注入(名称、作者、描述)
- 文件结构校验

#### ✅ 包管理器兼容性
- **UV**(默认):基于 Rust 的高速包管理器
- **PDM**:现代 Python 依赖管理工具
- **Poetry**:成熟的依赖管理工具
- **PIP**:传统的 Python 包管理器

#### ✅ 虚拟环境管理
- 为每种包管理器创建对应环境
- 校验依赖安装
- 处理包管理器特有的工作流

#### ✅ 依赖解析
- 生成 `pyproject.toml`(UV、PDM、Poetry)
- 生成 `requirements.txt`(PIP)
- 元数据合规(PEP 621)
- 构建系统配置

#### ✅ 项目结构校验
- FastAPI 项目识别
- 必备文件存在性
- 目录结构核对

### 测试执行示例

**运行全部模板测试:**
```console
$ pytest tests/test_templates/test_all_templates.py -v
```

**测试指定模板:**
```console
$ pytest tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[fastapi-default] -v
```

**在 PDM 环境中运行测试:**
```console
$ pdm run pytest tests/test_templates/test_all_templates.py -v
```

### 持续集成

自动化测试系统在 **CI/CD 流水线**中运行:

- ✅ **Pull Request 校验**:每个 PR 都会测试受影响的模板
- ✅ **每日夜间测试**:对完整模板套件进行校验
- ✅ **包管理器测试**:覆盖所有包管理器的交叉校验
- ✅ **环境测试**:覆盖多个 Python 版本与平台

### 对贡献者的好处

**零配置测试:**

- 🚀 添加新模板 → 自动测试
- ⚡ 无需手动创建测试文件
- 🛡️ 一致的质量标准

**全面覆盖:**

- 🔍 端到端项目创建测试
- 📦 多包管理器校验
- 🏗️ 完整的依赖解析测试
- ✅ 模拟真实使用场景

**开发体验:**

- 🎯 **专注模板内容**:测试由系统自动完成
- 🔄 **即时反馈**:测试执行迅速
- 📊 **结果清晰**:报告信息详尽
- 🚫 **零样板代码**:无需任何测试配置

## 手动模板检查

为开发与调试之便,您可以通过本地检查脚本或 Makefile 命令手动检查模板:

### 直接使用检查脚本

```console
# Inspect all templates
$ python scripts/inspect-templates.py

# Inspect specific templates
$ python scripts/inspect-templates.py --templates fastapi-default,fastapi-async-crud

# Verbose output with detailed information
$ python scripts/inspect-templates.py --verbose

# Save results to custom file
$ python scripts/inspect-templates.py --output my_results.json
```

### 使用 Makefile 命令

```console
# Inspect all templates
$ make inspect-templates

# Inspect with verbose output
$ make inspect-templates-verbose

# Inspect specific templates
$ make inspect-template TEMPLATES="fastapi-default,fastapi-async-crud"
```

## 检查结果

- **成功的检查**会被记录在工作流输出与产物中
- **失败的检查**会自动创建 GitHub issue,附带详细的错误报告
- **检查历史**在 GitHub Actions 产物中保留 30 天

## 理解检查输出

运行模板检查时,您会看到类似输出:

```console
📋 Found 6 templates to inspect: fastapi-async-crud, fastapi-custom-response, fastapi-default, fastapi-dockerized, fastapi-empty, fastapi-psql-orm
============================================================
🔍 Inspecting template: fastapi-async-crud
   Path: /path/to/src/fastapi_fastkit/fastapi_project_template/fastapi-async-crud
✅ fastapi-async-crud: PASSED
----------------------------------------
🔍 Inspecting template: fastapi-custom-response
   Path: /path/to/src/fastapi_fastkit/fastapi_project_template/fastapi-custom-response
✅ fastapi-custom-response: PASSED
----------------------------------------
...
============================================================
📊 INSPECTION SUMMARY
   Total templates: 6
   ✅ Passed: 6
   ❌ Failed: 0
🎉 All templates passed inspection!
📄 Results saved to: template_inspection_results.json
```

## 模板要求

要让模板通过检查,必须满足以下要求:

### 文件结构
- 必须包含一个带 Python 源文件的 `src/` 目录
- Python 文件必须使用 `.py-tpl` 扩展名
- 必须包含 `tests/` 目录与 `README.md-tpl` 文件
- 必须至少包含**一份**元数据文件:
    - `pyproject.toml-tpl`(推荐,PEP 621),或
    - `setup.py-tpl`(遗留,仍可接受)
- 当 `pyproject.toml-tpl` 已声明 `[project].dependencies` 时,`requirements.txt-tpl` 为可选

### FastAPI 要求
- 必须包含 FastAPI 应用初始化
- 必须在以下至少一个位置把 `fastapi` 声明为依赖:`pyproject.toml-tpl` 的 `[project].dependencies`、`requirements.txt-tpl`,或 `setup.py-tpl` 的 `install_requires`
- 所有模板文件必须具有有效的 Python 语法

### 身份标识

模板应携带 FastAPI-fastkit 的身份标识,这样生成的项目在用户工作区中可以与无关的 FastAPI 项目区分开:

- `pyproject.toml-tpl` —— 在 `description` 中带 `[FastAPI-fastkit templated]` 前缀,并提供带 `managed = true` 的 `[tool.fastapi-fastkit]` 表。
- `setup.py-tpl` —— 在 `setup()` 的 `description` 参数中带 `[FastAPI-fastkit templated]` 前缀。

`is_fastkit_project()` 接受其中任一标识(pyproject 优先,setup.py 是遗留回退;匹配不区分大小写)。即使模板遗漏了它们,元数据注入也能确保生成的项目带上这些标识。

### 质量标准
- 所有模板文件必须语法正确
- 依赖必须正确声明
- 模板结构必须遵循 FastAPI-fastkit 的约定

这套自动化的质量保障可以让所有模板保持可靠,并随时可用于生产。
