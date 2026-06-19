# 快速上手

5 分钟内使用 FastAPI-fastkit 创建您的第一个 FastAPI 项目!

!!! tip "不确定该选哪个 starter？"
    请参阅 [**应该选择哪个 starter？**](choosing-a-starter.md)。其中对 `startdemo` 模板与交互式架构预设(`minimal` / `single-module` / `classic-layered` / `domain-starter`)做了面向新手的对比。简短结论是：**推荐使用 `fastkit init --interactive`，并选择 `domain-starter` 预设。**

## 1. 创建项目

使用 FastAPI-fastkit 的 `init` 命令创建一个新项目:

<div class="termy">

```console
$ fastkit init
Enter the project name: my-first-app
Enter the author name: Your Name
Enter the author email: your.email@example.com
Enter the project description: My first FastAPI application

           Project Information
┌──────────────┬─────────────────────────────┐
│ Project Name │ my-first-app                │
│ Author       │ Your Name                   │
│ Author Email │ your.email@example.com      │
│ Description  │ My first FastAPI application│
└──────────────┴─────────────────────────────┘

Available Stacks and Dependencies:
           MINIMAL Stack
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ pydantic          │
│ Dependency 4 │ pydantic-settings │
└──────────────┴───────────────────┘

           STANDARD Stack
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ sqlalchemy        │
│ Dependency 4 │ alembic           │
│ Dependency 5 │ pytest            │
│ Dependency 6 │ pydantic          │
│ Dependency 7 │ pydantic-settings │
└──────────────┴───────────────────┘

             FULL Stack
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ sqlalchemy        │
│ Dependency 4 │ alembic           │
│ Dependency 5 │ pytest            │
│ Dependency 6 │ redis             │
│ Dependency 7 │ celery            │
│ Dependency 8 │ pydantic          │
│ Dependency 9 │ pydantic-settings │
└──────────────┴───────────────────┘

Select stack (minimal, standard, full): minimal

Available Package Managers:
                   Package Managers
┌────────┬────────────────────────────────────────────┐
│ PIP    │ Standard Python package manager            │
│ UV     │ Fast Python package manager                │
│ PDM    │ Modern Python dependency management        │
│ POETRY │ Python dependency management and packaging │
└────────┴────────────────────────────────────────────┘

Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y

✨ FastAPI project 'my-first-app' has been created successfully!
```

</div>

## 2. 激活虚拟环境

进入项目目录并激活虚拟环境:

<div class="termy">

```console
$ cd my-first-app
$ source .venv/bin/activate  # Linux/macOS
$ .venv\Scripts\activate     # Windows
```

</div>

## 3. 启动开发服务器

启动 FastAPI 开发服务器:

<div class="termy">

```console
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [28720]
INFO:     Started server process [28722]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

</div>

!!! success "恭喜!"
    您的 FastAPI 服务器已经运行起来了！现在就可以打开浏览器查看。

## 4. 测试您的 API

打开浏览器,访问以下 URL:

### 主要端点

访问 [http://127.0.0.1:8000](http://127.0.0.1:8000)

您将看到:

```json
{"message": "Hello World"}
```

### 交互式 API 文档

访问 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

这是自动生成的 **Swagger UI** 文档,您可以在其中:

- 查看所有 API 端点
- 直接在浏览器中测试端点
- 查看请求/响应模式

### 备选文档

访问 [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

这是 **ReDoc** 文档界面,展示方式更偏文档化,阅读起来也更清晰。

## 5. 添加您的第一个路由

让我们为项目添加一个新的 API 路由:

<div class="termy">

```console
$ fastkit addroute users my-first-app
                       Adding New Route
┌──────────────────┬──────────────────────────────────────────┐
│ Project          │ my-first-app                             │
│ Route Name       │ users                                    │
│ Target Directory │ ~/my-first-app                           │
└──────────────────┴──────────────────────────────────────────┘

Do you want to add route 'users' to project 'my-first-app'? [Y/n]: y

╭──────────────────────── Info ────────────────────────╮
│ ℹ Updated main.py to include the API router          │
╰──────────────────────────────────────────────────────╯
╭─────────────────────── Success ───────────────────────╮
│ ✨ Successfully added new route 'users' to project    │
│ `my-first-app`                                        │
╰───────────────────────────────────────────────────────╯
```

</div>

服务器会自动重载,现在您拥有了新的端点:

- `GET /api/v1/users/` —— 获取所有用户
- `POST /api/v1/users/` —— 创建新用户
- `GET /api/v1/users/{user_id}` —— 获取指定用户
- `PUT /api/v1/users/{user_id}` —— 更新用户
- `DELETE /api/v1/users/{user_id}` —— 删除用户

## 6. 测试新增 API

### 使用 curl

**获取所有用户:**

<div class="termy">

```console
$ curl http://127.0.0.1:8000/api/v1/users/
[]
```

</div>

**创建新用户:**

<div class="termy">

```console
$ curl -X POST "http://127.0.0.1:8000/api/v1/users/" \
     -H "Content-Type: application/json" \
     -d '{"title": "John Doe", "description": "Software Developer"}'
{
  "id": 1,
  "title": "John Doe",
  "description": "Software Developer"
}
```

</div>

### 通过交互式文档

1. 访问 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
2. 展开 **“users”** 部分
3. 点击 **“POST /api/v1/users/”**
4. 点击 **“Try it out”**
5. 填写请求体:
   ```json
   {
     "title": "Jane Smith",
     "description": "Product Manager"
   }
   ```
6. 点击 **“Execute”**

## 7. 了解项目结构

生成的项目结构清晰、易于扩展：

```
my-first-app/
├── .venv/                    # 虚拟环境
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py        # 应用配置
│   ├── api/
│   │   ├── __init__.py
│   │   ├── api.py          # API 路由汇总
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── items.py     # 默认的 items 路由
│   │       └── users.py     # 新增的 users 路由
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── items.py         # items 相关的 CRUD 操作
│   │   └── users.py         # users 相关的 CRUD 操作
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── items.py         # items 的 Pydantic 模式
│   │   └── users.py         # users 的 Pydantic 模式
│   └── mocks/
│       ├── __init__.py
│       └── mock_items.json  # 测试数据
├── tests/                   # 测试文件
├── scripts/                 # 辅助脚本
├── requirements.txt         # Python 依赖
├── setup.py                # 包配置
└── README.md               # 项目文档
```

## 8. 包管理器选项

FastAPI-fastkit 支持多种 Python 包管理器以适应不同偏好:

### 可用的包管理器

| 管理器 | 描述 | 适用场景 |
|---------|-------------|----------|
| **UV** | 快速的 Python 包管理器(默认) | 追求速度与性能 |
| **PDM** | 现代化的 Python 依赖管理 | 需要更强的依赖解析 |
| **Poetry** | Python 依赖管理与打包 | 基于 Poetry 的工作流 |
| **PIP** | 标准 Python 包管理器 | 传统 Python 开发 |

### 指定包管理器

您可以通过多种方式指定偏好的包管理器:

#### 1. 交互式选择(默认)

运行 `fastkit init` 或 `fastkit startdemo` 时,系统会提示您选择:

<div class="termy">

```console
$ fastkit init
# ... after project details and stack selection ...

Available Package Managers:
                   Package Managers
┌────────┬────────────────────────────────────────────┐
│ PIP    │ Standard Python package manager            │
│ UV     │ Fast Python package manager                │
│ PDM    │ Modern Python dependency management        │
│ POETRY │ Python dependency management and packaging │
└────────┴────────────────────────────────────────────┘

Select package manager (pip, uv, pdm, poetry) [uv]: uv
```

</div>

#### 2. 命令行参数

直接通过参数指定包管理器,跳过交互选择:

<div class="termy">

```console
$ fastkit init --package-manager poetry
$ fastkit startdemo --package-manager pdm
```

</div>

### 生成的依赖文件

每种包管理器会生成相应的依赖文件:

- **UV/PDM**:`pyproject.toml`(PEP 621 格式)
- **Poetry**:`pyproject.toml`(Poetry 格式)
- **PIP**:`requirements.txt`

## 9. 接下来呢?

恭喜!您已经成功完成了以下任务:

✅ 创建了您的第一个 FastAPI 项目
✅ 启动了开发服务器
✅ 添加了新的 API 路由
✅ 测试了您的 API

### 继续学习

1. **[您的第一个项目](../tutorial/first-project.md)**:构建一个更完整的博客 API
2. **[创建项目](creating-projects.md)**:了解不同的技术栈与选项
3. **[添加路由](adding-routes.md)**:精通 API 开发
4. **[使用模板](using-templates.md)**:探索预构建的项目模板

### 多动手实践

您还可以试试下面这些命令,继续探索更多功能：

<div class="termy">

```console
# 列出可用模板
$ fastkit list-templates

# 基于模板创建项目
$ fastkit startdemo

# 继续添加更多路由（先写路由名,再写项目目录）
$ fastkit addroute products my-first-app
$ fastkit addroute orders my-first-app
```

</div>

!!! tip "开发小贴士"
    - 修改代码后,服务器会自动重载
    - 添加新功能时,记得查看交互式文档 `/docs`
    - 使用虚拟环境隔离项目依赖
    - 多阅读生成出来的代码,熟悉项目结构
