# 应该选择哪个 starter？

FastAPI-fastkit 提供了多种项目起步方式。本页是一份**面向新手的选型指南**：先在这里决定路线,再跳转到 [快速上手](quick-start.md) 实际创建项目。

如果您拿不定主意,最简短的建议是：

> **从 `fastkit init --interactive` 开始,并选择 `domain-starter` 预设。** 它是现代 API 项目的推荐默认选项。

下面会进一步解释为什么这样推荐,以及在哪些情况下更适合选择其他方案。

## TL;DR —— 按用户类型选择

| 您的情况 | 起点 |
|---|---|
| 刚接触 FastAPI,想要引导式上手 | `fastkit init --interactive`(预设:**`domain-starter`**) |
| 想要一个可运行的 CRUD 示例来阅读与修改 | `fastkit startdemo fastapi-default` |
| 想要尽可能小的骨架 | `fastkit init --interactive`(预设:**`minimal`**) |
| 编写快速原型 / 单文件脚本 | `fastkit init --interactive`(预设:**`single-module`**) |
| 需要真实的数据库(PostgreSQL + SQLAlchemy + Alembic) | `fastkit startdemo fastapi-psql-orm` |
| 想要面向中型 API 的生产风格领域布局 | `fastkit init --interactive`(预设:**`domain-starter`**) |

## `startdemo` 与 `init --interactive` —— 有什么区别?

这是两个主要入口,分别面向不同的使用需求。

### `fastkit startdemo <template>`

它会基于内置模板(`fastapi-default`、`fastapi-async-crud`、`fastapi-psql-orm`、`fastapi-domain-starter` 等)直接生成一个**完整、可运行的示例项目**。模板源码会原样复制,并自动填充 `<project_name>` 等元数据占位符。

- ✅ 这是拿到可运行 demo 的最快方式。
- ✅ 代码完整可读,非常适合通过示例学习。
- ❌ 模板的技术栈与结构是固定的;您无法在生成过程中只保留 CORS、去掉认证等组件。

```console
$ fastkit list-templates              # 查看可用模板
$ fastkit startdemo fastapi-default   # 基于某个模板生成项目
```

### `fastkit init --interactive`

它会通过一个 **引导式向导** 带您依次完成：项目元数据 → 架构预设 → 功能选择(数据库、认证、测试、部署等)→ 包管理器 → 最终确认。生成器会根据预设挑选合适的基础模板,再叠加您选中的功能。

- ✅ 您可以组合出更贴近自身需求的技术栈。
- ✅ 架构预设会直接决定项目布局(单文件、分层、领域驱动等)。
- ❌ 对于保留自带 `main.py` 的较完整预设(`classic-layered`、`domain-starter`),工具会生成配置模块,但仍需要您手动接入到已有路由中。具体契约请参阅 [架构预设矩阵](../reference/preset-feature-matrix.md)。

```console
$ fastkit init --interactive
```

## 四种架构预设

它们会在 `fastkit init --interactive` 收集完项目信息后出现。请根据本节决定选哪一个。

### `minimal` —— 从最简单开始,后续再扩展

最小可行的 FastAPI 应用。空骨架 + 一个根据您的功能开关重新生成的 `src/main.py`。若您选择了 CORS、限流、Prometheus 监控,会自动接入到 `main.py`。

- 👤 **适合谁**:希望自己在项目成长过程中逐步加入结构的人,或者想在不预设布局观念的情况下探索 FastAPI 的人。
- 📦 **基础模板**:`fastapi-empty`。
- 🧠 **心智模型**：“先给我一个能跑起来的 FastAPI 文件,其余部分我自己来决定。”

### `single-module` —— 脚本风格的原型

一切都放在一个模块里。`main.py` 的重新生成方式与 `minimal` 相同。

- 👤 **适合谁**:编写一个粘合脚本、一个小型 webhook 或一天就能写完的原型,不需要包级别的划分。
- 📦 **基础模板**:`fastapi-single-module`。
- 🧠 **心智模型**：“我想要一个坐下来就能跑、也能一次读完的 Python 文件。”

### `classic-layered` —— 分层布局(api / crud / schemas / core)

这是一种带有 “Django 风味” 的布局 —— 按关注点横向拆分：所有路由放在 `api/`,所有 CRUD 逻辑放在 `crud/`,所有 Pydantic 模式放在 `schemas/`,所有配置放在 `core/`。自带的 `main.py` 会**保留**(其中已经接入了 CORS);生成的数据库 / 认证配置会写入 `src/core/`。

- 👤 **适合谁**:熟悉 Django/Rails 风格布局的团队,或者拥有大量小型端点、共享 CRUD 底座的项目。
- 📦 **基础模板**:`fastapi-default`。
- 🧠 **心智模型**：“按代码 _是什么_ 来拆分。”

### `domain-starter` —— 领域驱动(推荐默认)

代码按 **业务概念** 纵向切分:每个领域在 `src/app/domains/<concept>/` 下拥有自己的路由、service、repository 与 schemas。自带一个 `/health` 端点,以及一个 `items` 示例领域,您可以复制并重命名以创建新的概念。自带的 `main.py`(位于 `src/app/`)会保留;生成的配置落在 `src/app/core/`。

- 👤 **适合谁**：适用于包含多个独立业务概念(users、orders、billing 等)的中型 API。也是当前推荐的现代默认选项。
- 📦 **基础模板**:`fastapi-domain-starter`。
- 🧠 **心智模型**：“按代码 _为业务做什么_ 来拆分。”

## 对比矩阵

下面是一眼就能看明白的并列对比。

| | `minimal` | `single-module` | `classic-layered` | `domain-starter` |
|---|---|---|---|---|
| 基础模板 | `fastapi-empty` | `fastapi-single-module` | `fastapi-default` | `fastapi-domain-starter` |
| 项目入口 | `src/main.py` | `src/main.py` | `src/main.py` | `src/app/main.py` |
| 路由位置 | (您自行添加) | (在 `main.py` 内) | `src/api/routes/` | `src/app/domains/<concept>/router.py` |
| 每领域文件夹 | ❌ | ❌ | ❌ | ✅ |
| 内置 `/health` 端点 | ✅ | ✅ | ❌ | ✅ |
| 根据功能重新生成 `main.py` | ✅ | ✅ | ❌ | ❌ |
| `main.py` 中已接入 CORS | 选中后自动加入 | 选中后自动加入 | 是(由环境变量驱动) | 是(由环境变量驱动) |
| pyproject-first | 可选 | 可选 | 可选 | ✅ |
| 最适合 | “结构由我后续添加” | “单文件原型” | “按关注点切分” | “按业务概念切分” |

要查看每个功能的完整契约(数据库 / 认证配置会生成到哪里、哪些选择需要手动接入、哪些会触发警告),请参阅 [架构预设矩阵](../reference/preset-feature-matrix.md)。

## 选择 `startdemo` 模板

如果您更想要一个**完整、可运行的示例项目**,而不是一步步引导式拼装,那 `fastkit startdemo <template>` 会更适合。大多数模板都大致对应上面的四种预设之一,但还额外附带了示例代码(如基于 mock 存储的 CRUD 端点、自定义响应处理、Docker 配置等)。

| 模板 | 最接近的预设 | 何时选择 |
|---|---|---|
| `fastapi-default` | `classic-layered` | 带分层布局的可运行 CRUD 示例。一个不错的起点。 |
| `fastapi-empty` | `minimal` | 裸骨架;与 `minimal` 落地后的形态相同。 |
| `fastapi-single-module` | `single-module` | 单文件示例。 |
| `fastapi-domain-starter` | `domain-starter` | 推荐的现代默认选项;自带 items 示例领域。 |
| `fastapi-async-crud` | `classic-layered` | `fastapi-default` 的异步版本。 |
| `fastapi-custom-response` | `classic-layered` | 演示自定义响应包装 / 格式化。 |
| `fastapi-dockerized` | `classic-layered` | 在默认布局之上加入生产级 Dockerfile。 |
| `fastapi-psql-orm` | (无直接对应预设) | PostgreSQL + SQLAlchemy + Alembic。需要真实数据库时选它。 |
| `fastapi-mcp` | (无直接对应预设) | Model Context Protocol 集成。 |

`fastkit list-templates` 会显示当前可用模板及其一行说明。

## 常见问题

**Q. 是否需要在一开始就选定预设 / 模板?**
不用 —— 之后您仍然可以手动重组生成的代码。预设只是起点,并不是硬性约束,不必过度纠结。

**Q. 哪个是“现代”选项?**
`domain-starter`。它采用 pyproject-first 结构,自带 `/health` 端点,布局也更贴近许多成熟的中型 FastAPI 项目。

**Q. 之后能从 `classic-layered` 切换到 `domain-starter` 吗?**
可以,但这属于手动重构 —— 目前没有自动迁移命令。如果您预计项目后续会发展到需要按领域分目录,建议一开始就选它。

**Q. 我只是想学习 FastAPI 怎么办?**
可以从 `fastkit startdemo fastapi-default` 开始 —— 先阅读代码、运行测试、改几个端点。熟悉之后,再过渡到 `fastkit init --interactive` + `domain-starter` 会很自然。

**Q. 在哪里能看到每个预设生成的精确文件?**
[架构预设矩阵](../reference/preset-feature-matrix.md) 是这方面的参考页面。

## 下一步

- [快速上手](quick-start.md) —— 真正动手创建您的第一个项目。
- [创建项目](creating-projects.md) —— 更深入地了解 CLI 参数。
- [领域驱动项目教程](../tutorial/domain-starter.md) —— 如果您选择了 `domain-starter`,这是从生成的目录树、内置 `items` 示例,到如何添加下一个领域的完整演练。
- [架构预设矩阵](../reference/preset-feature-matrix.md) —— 每个预设 / 功能的完整契约。
