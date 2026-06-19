# 架构预设 / 功能矩阵

交互式的 `fastkit init --interactive` 在收集功能选择之前,会先询问一个 **架构预设**([issue #44](https://github.com/bnbong/FastAPI-fastkit/issues/44))。预设决定了生成项目的整体布局 —— 不同的预设会使用不同的基础模板,并把生成的配置文件落到不同位置,使其与已有结构相邻,而不是放进平行的 `src/config/` 子树中。

本页是关于「每个预设的作用、文件落地位置、哪些功能组合需要手动接入」的权威说明。

## 预设 → 基础模板

| 预设 | 基础模板 | 描述 |
|---|---|---|
| `minimal` | `fastapi-empty` | 最小可运行的 FastAPI 应用 —— 占位的 `main.py` 会根据您的功能选择重新生成。 |
| `single-module` | `fastapi-single-module` | 单文件 FastAPI 应用 —— `main.py` 会被重新生成。 |
| `classic-layered` | `fastapi-default` | 分层布局(`api/routes`、`crud`、`schemas`、`core`)。自带的 `main.py` 会被保留。 |
| `domain-starter` | `fastapi-domain-starter` | 领域驱动布局(`src/app/domains/<concept>/`)。自带的 `main.py` 会被保留。**推荐默认选项。** |

## 生成文件的落地位置

| 预设 | `main.py` 覆盖策略 | 数据库配置落点 | 认证配置落点 |
|---|---|---|---|
| `minimal` | 在 `src/main.py` 处重新生成 | `src/config/database.py` | `src/config/auth.py` |
| `single-module` | 在 `src/main.py` 处重新生成 | `src/config/database.py` | `src/config/auth.py` |
| `classic-layered` | 保留(模板自带) | `src/core/database.py` | `src/core/auth.py` |
| `domain-starter` | 保留(模板自带) | `src/app/core/database.py` | `src/app/core/auth.py` |

## 各预设对数据库 / 认证功能的支持

下列功能在**所有**预设中都支持 —— 包安装都会成功;差别只在于动态的 `main.py` 覆盖是否会自动接入它们。

| 功能 | `minimal` / `single-module` | `classic-layered` / `domain-starter` |
|---|---|---|
| **数据库**(PostgreSQL、MySQL、SQLite、MongoDB) | 生成配置模块,**并且**在重新生成的 `main.py` 中插入 `await init_db()` 调用。 | 在预设对应路径生成配置模块。自带的 `main.py` 会**保留**,因此需要手动把 `get_db()` 接入路由器。 |
| **认证**(JWT、FastAPI-Users、OAuth2、基于会话) | 生成认证配置模块。JWT 还会在重新生成的 `main.py` 中导入 `HTTPBearer`。 | 在预设对应路径生成认证配置模块。不会向 `main.py` 添加 import —— 需要手动接入依赖。 |
| **后台任务**(Celery、Dramatiq) | 安装相应包;目前没有 main.py 覆盖。 | 同上。 |
| **缓存**(Redis) | 安装相应包;目前没有 main.py 覆盖。 | 同上。 |
| **CORS**(工具类) | 在重新生成的 `main.py` 中加入 `CORSMiddleware`,`allow_origins=['*']`。 | 自带的 `main.py` 中**已接入**(以 `settings.all_cors_origins` 作为条件)。只需在 `.env` 中设置 `BACKEND_CORS_ORIGINS` 即可启用 —— 无需修改代码。 |
| **测试**(基础 / 覆盖率 / 进阶) | 在项目根生成 `pytest.ini`。 | 同上。 |
| **部署**(Docker、docker-compose) | 在项目根写入 `Dockerfile` 和/或 `docker-compose.yml`。 | 同上。 |

## 何时会出现「Preset compatibility」警告

对于**保留自带 `main.py`** 的预设(`classic-layered`、`domain-starter`),某些功能选择不会被自动接入到应用。CLI 会在生成结束时一次性给出警告,列出哪些选择需要手动接入:

| 选择的功能 | 在 `classic-layered` / `domain-starter` 下是否触发警告? |
|---|---|
| `CORS`(工具类) | ❌ —— 自带的 `main.py` 已接入。只需在 `.env` 中填好 `BACKEND_CORS_ORIGINS`。 |
| `Rate-Limiting`(工具类) | ✅ —— 不会加入 `slowapi` 限流器的初始化 |
| `Prometheus`(监控) | ✅ —— 不会调用 `Instrumentator().instrument(app)` |
| 任意数据库 / 认证选择 | ⚠️ —— 配置文件已生成,但需要您手动在路由器中通过 `Depends()` 接入 |

对 `minimal` 与 `single-module` 预设,动态的 `main.py` 覆盖会自动处理 CORS、限流与 Prometheus 监控,因此不会触发警告。

## 不支持的组合(安全起见)

策略设计者**刻意不会**尝试把生成的代码拼接进模板自带的 `main.py`。这样做有可能产生坏掉的 import 或重复的路由器。整体契约是:

- 所选的包总是会被安装(这样 `pip freeze` 与用户意图匹配)。
- 生成的配置模块总是落到对应预设的路径。
- 对于保留 main 的预设,会告知用户哪些选择仍需手动接入,而不是产出悄无声息坏掉的代码。

如果您需要对所有功能都进行自动接入,请选择 `minimal` 或 `single-module` —— 它们会基于功能开关重新生成 `main.py`。
