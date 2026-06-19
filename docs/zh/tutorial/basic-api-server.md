# 构建一个基础 API 服务器

学习如何使用 FastAPI-fastkit 快速构建一个简单的 REST API 服务器。本教程面向 FastAPI 初学者,覆盖基础 CRUD API 的创建。

## 您将学到的内容

- 使用 `fastkit startdemo` 命令创建基础 API 服务器
- 理解 FastAPI 项目结构
- 使用基础的 CRUD 端点
- API 测试与文档
- 项目的扩展方式

## 前置条件

- 已安装 Python 3.12 及以上
- 已安装 FastAPI-fastkit(`pip install fastapi-fastkit`)
- 具备 Python 基础知识

## 第 1 步:创建基础 API 项目

使用 `fastapi-default` 模板创建基础 API 服务器。

<div class="termy">

```console
$ fastkit startdemo fastapi-default
Enter the project name: my-first-api
Enter the author name: Developer Kim
Enter the author email: developer@example.com
Enter the project description: My first FastAPI server
Deploying FastAPI project using 'fastapi-default' template

           Project Information
┌──────────────┬────────────────────────────┐
│ Project Name │ my-first-api               │
│ Author       │ Developer Kim              │
│ Author Email │ developer@example.com      │
│ Description  │ My first FastAPI server    │
└──────────────┴────────────────────────────┘

       Template Dependencies
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ pydantic          │
│ Dependency 4 │ pydantic-settings │
│ Dependency 5 │ python-dotenv     │
└──────────────┴───────────────────┘

Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y

✨ FastAPI project 'my-first-api' from 'fastapi-default' has been created successfully!
```

</div>

## 第 2 步:理解生成的项目结构

先来看看生成后的项目结构：

```
my-first-api/
├── README.md                 # 项目文档
├── requirements.txt          # 依赖列表
├── setup.py                  # 包配置
├── scripts/
│   └── run-server.sh        # 启动服务器脚本
├── src/                     # Main source code
│   ├── main.py              # FastAPI 应用入口
│   ├── core/
│   │   └── config.py        # 配置管理
│   ├── api/
│   │   ├── api.py           # API 路由汇总
│   │   └── routes/
│   │       └── items.py     # items 相关端点
│   ├── schemas/
│   │   └── items.py         # 数据模型定义
│   ├── crud/
│   │   └── items.py         # 数据处理逻辑
│   └── mocks/
│       └── mock_items.json  # 测试数据
└── tests/                   # 测试代码
    ├── __init__.py
    ├── conftest.py
    └── test_items.py
```

### 关键文件说明

- **`src/main.py`**:FastAPI 应用入口
- **`src/api/routes/items.py`**:item 相关的 API 端点定义
- **`src/schemas/items.py`**:请求 / 响应数据结构定义
- **`src/crud/items.py`**:数据库操作逻辑
- **`src/mocks/mock_items.json`**:开发用的示例数据

## 第 3 步:运行服务器

进入生成的项目目录,运行服务器。

<div class="termy">

```console
$ cd my-first-api
$ fastkit runserver
Starting FastAPI server at 127.0.0.1:8000...

INFO:     Will watch for changes in these directories: ['/path/to/my-first-api']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

</div>

服务器成功运行后,您可以在浏览器中访问:

- **API 服务器**:http://127.0.0.1:8000
- **Swagger UI 文档**:http://127.0.0.1:8000/docs
- **ReDoc 文档**:http://127.0.0.1:8000/redoc

## 第 4 步:探索 API 端点

生成的 API 默认提供以下端点:

| 方法 | 端点 | 描述 |
|--------|----------|-------------|
| GET | `/items/` | 获取所有 item |
| GET | `/items/{item_id}` | 获取指定 item |
| POST | `/items/` | 创建新 item |
| PUT | `/items/{item_id}` | 更新 item |
| DELETE | `/items/{item_id}` | 删除 item |

### 测试 API

**1. 获取所有 item**

<div class="termy">

```console
$ curl -X GET "http://127.0.0.1:8000/items/"
[
  {
    "id": 1,
    "name": "Laptop",
    "description": "High-performance laptop",
    "price": 999.99,
    "tax": 99.99
  },
  {
    "id": 2,
    "name": "Mouse",
    "description": "Wireless mouse",
    "price": 29.99,
    "tax": 2.99
  }
]
```

</div>

**2. 创建新 item**

<div class="termy">

```console
$ curl -X POST "http://127.0.0.1:8000/items/" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Keyboard",
       "description": "Mechanical keyboard",
       "price": 150.00,
       "tax": 15.00
     }'

{
  "id": 3,
  "name": "Keyboard",
  "description": "Mechanical keyboard",
  "price": 150.0,
  "tax": 15.0
}
```

</div>

**3. 获取指定 item**

<div class="termy">

```console
$ curl -X GET "http://127.0.0.1:8000/items/1"
{
  "id": 1,
  "name": "Laptop",
  "description": "High-performance laptop",
  "price": 999.99,
  "tax": 99.99
}
```

</div>

## 第 5 步:用 Swagger UI 测试 API

在浏览器中访问 http://127.0.0.1:8000/docs,查看自动生成的 API 文档。

借助 Swagger UI 您可以:

1. **查看 API 端点**:以可视化方式查看所有可用端点
2. **核对请求 / 响应模式**:查看每个端点的输入输出格式
3. **直接测试 API**:点击「Try it out」实际调用 API
4. **查看示例数据**:浏览各端点的请求 / 响应示例

### 如何使用 Swagger UI

1. 点击 `/items/` GET 端点
2. 点击「Try it out」按钮
3. 点击「Execute」按钮
4. 查看服务器响应

## 第 6 步:理解代码结构

### 主应用(`src/main.py`)

```python
from fastapi import FastAPI
from src.api.api import api_router
from src.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
)

app.include_router(api_router)

@app.get("/")
def read_root():
    return {"message": "Hello World"}
```

### Item 模式(`src/schemas/items.py`)

```python
from pydantic import BaseModel
from typing import Optional

class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    name: Optional[str] = None
    price: Optional[float] = None

class Item(ItemBase):
    id: int

    class Config:
        from_attributes = True
```

### CRUD 逻辑(`src/crud/items.py`)

```python
from typing import List, Optional
from src.schemas.items import Item, ItemCreate, ItemUpdate

class ItemCRUD:
    def __init__(self):
        self.items: List[Item] = []
        self.next_id = 1

    def create_item(self, item: ItemCreate) -> Item:
        new_item = Item(id=self.next_id, **item.dict())
        self.items.append(new_item)
        self.next_id += 1
        return new_item

    def get_items(self) -> List[Item]:
        return self.items

    def get_item(self, item_id: int) -> Optional[Item]:
        return next((item for item in self.items if item.id == item_id), None)
```

## 第 7 步:扩展项目

### 添加新路由

可以使用 `fastkit addroute` 命令添加新端点:

<div class="termy">

```console
$ fastkit addroute user
                       Adding New Route
┌──────────────────┬──────────────────────────────────────────┐
│ Project          │ my-first-api                             │
│ Route Name       │ user                                     │
│ Target Directory │ /path/to/my-first-api                   │
└──────────────────┴──────────────────────────────────────────┘

Do you want to add route 'user' to the current project? [Y/n]: y

✨ Successfully added new route 'user' to the current project!
```

</div>

该命令会创建以下文件:

- `src/api/routes/user.py` —— 用户相关端点
- `src/schemas/user.py` —— 用户数据模型
- `src/crud/user.py` —— 用户数据处理逻辑

### 自定义环境配置

可以修改 `src/core/config.py` 文件来调整项目设置:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "My First API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "My first FastAPI server"
    API_V1_STR: str = "/api/v1"

    class Config:
        env_file = ".env"

settings = Settings()
```

## 第 8 步:运行测试

项目自带基础测试:

<div class="termy">

```console
$ pytest tests/ -v
======================== test session starts ========================
collected 4 items

tests/test_items.py::test_create_item PASSED                   [ 25%]
tests/test_items.py::test_read_items PASSED                    [ 50%]
tests/test_items.py::test_read_item PASSED                     [ 75%]
tests/test_items.py::test_update_item PASSED                   [100%]

======================== 4 passed in 0.15s ========================
```

</div>

## 下一步

恭喜您完成了基础 API 服务器的构建!接下来可以尝试:

1. **[构建异步 CRUD API](async-crud-api.md)** —— 学习更复杂的异步处理
2. **[数据库集成](database-integration.md)** —— 使用 PostgreSQL 与 SQLAlchemy
3. **[Docker 容器化](docker-deployment.md)** —— 为生产部署做准备
4. **[自定义响应处理](custom-response-handling.md)** —— 进阶的响应格式配置

## 故障排查

### 常见问题

**问:服务器无法启动**
答:确认虚拟环境已激活,依赖已正确安装。

**问:无法访问 API 端点**
答:确认服务器在正常运行,端口号(默认 8000)正确。

**问:API 没有出现在 Swagger UI 中**
答:确认路由器已正确包含在 `src/main.py` 中。

## 小结

在本教程中,您使用 FastAPI-fastkit 完成了:

- ✅ 创建基础 FastAPI 项目
- ✅ 理解项目结构
- ✅ 使用 CRUD API 端点
- ✅ API 文档与测试
- ✅ 项目扩展方式

既然您已经掌握了 FastAPI 的基础,不妨挑战更复杂的项目!
