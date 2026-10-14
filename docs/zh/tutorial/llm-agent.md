# 使用 `fastapi-llm-agent` 构建流式 LLM 智能体

构建一个聊天后端:它能在令牌生成时将其流式输出,并且能真正*做*事情 —— 调用工具、读取工具结果并继续推进。本教程会走完 `fastapi-llm-agent` 模板:SSE 事件协议、工具调用循环及其迭代上限、隐藏在接口之后的对话记忆,以及一个从不访问网络的测试套件。

## 您将学到的内容

- 使用 `fastkit startdemo fastapi-llm-agent` 生成项目
- 客户端必须处理的 SSE 事件类型,以及每种事件的含义
- 工具调用循环的一轮是如何逐步进行的
- 添加您自己的工具
- 将进程内对话存储替换为真正的存储
- 为什么测试是确定性的,并且运行时不产生费用

## 前置条件

- Python 3.12+
- 已安装 FastAPI-fastkit(`pip install fastapi-fastkit`)
- 一个 Anthropic API 密钥 —— 仅在与真实模型对话时需要。生成的测试套件无需密钥即可运行。
- 熟悉 `async`/`await` 以及异步生成器

## 第 1 步:生成并配置

```console
$ fastkit startdemo fastapi-llm-agent
Enter the project name: support-agent
Enter the author name: Developer Kim
Enter the author email: developer@example.com
Enter the project description: Streaming support assistant
Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y
```

首次运行前,请将密钥写入 `.env`:

```bash
ANTHROPIC_API_KEY=sk-ant-...
LLM_MODEL=claude-sonnet-5
LLM_MAX_TOKENS=4096
MAX_TOOL_ITERATIONS=5
```

密钥由 pydantic-settings 读取,并在构造客户端时传入。它从不写入源代码,也从不打包进 Docker 镜像。

```console
$ cd support-agent
$ bash scripts/run-server.sh
$ bash scripts/chat.sh "What is 12 * 34?"
```

!!! tip "使用网关代替 Anthropic API"
    设置 `LLM_BASE_URL`(如果网关使用 Bearer 认证,还需设置 `LLM_AUTH_TOKEN`),使其指向 LiteLLM、内部代理或本地服务器。传输格式仍然是 Anthropic Messages API;为其他提供商做转换是网关的职责,而不是应用的职责。

## 第 2 步:生成的目录树

```
support-agent/
├── pyproject.toml              # PEP 621 metadata + [tool.fastapi-fastkit]
├── requirements.txt
├── Dockerfile
├── .env
├── scripts/
│   ├── chat.sh                 # send one message to a running server
│   ├── format.sh  lint.sh  run-server.sh  test.sh
├── src/
│   └── app/
│       ├── main.py             # FastAPI app + lifespan
│       ├── core/config.py      # pydantic-settings (API key lives here)
│       ├── llm/
│       │   ├── client.py       # AsyncAnthropic factory
│       │   ├── tools.py        # tool schemas + handlers
│       │   └── agent.py        # streaming agent + tool loop
│       ├── memory/
│       │   ├── base.py         # ConversationStore interface
│       │   └── in_memory.py    # process-local implementation
│       ├── schemas/chat.py     # request bodies + SSE event envelope
│       └── api/
│           ├── router.py       # aggregates health + chat
│           ├── deps.py         # store / agent dependencies
│           ├── health.py       # GET /health
│           └── chat.py         # POST /chat (SSE), conversation history
└── tests/
    ├── conftest.py             # scripted fake Anthropic client
    ├── test_health.py  test_chat.py  test_tools.py  test_memory.py
```

有三条边界值得一开始就注意:**客户端**由工厂创建(因此测试可以替换它),**记忆**是一个带有简单实现的接口(因此生产环境可以替换它),**工具**是一个模式列表加一个处理器字典(因此添加工具只需修改一个文件)。

## 第 3 步:端点

| 方法 | 端点                         | 说明                    |
|--------|------------------------------|-------------------------|
| GET    | `/api/v1/health`             | 存活探针                |
| POST   | `/api/v1/chat`               | 以 SSE 流式返回回复     |
| GET    | `/api/v1/conversations/{id}` | 读取已存储的历史        |
| DELETE | `/api/v1/conversations/{id}` | 删除一段对话            |

`POST /api/v1/chat` 接收 `{"message": "...", "conversation_id": "..."}`。省略 `conversation_id` 即可开始新的对话,并从最后的 `done` 事件中读取分配的 id。

## 第 4 步:流协议

每条 SSE 消息在 `event:` 字段中携带其类型,在 `data:` 中携带一个 JSON 封装。客户端必须处理其中五种事件以及错误:

| 事件          | 字段                            | 含义                           |
|---------------|---------------------------------|--------------------------------|
| `token`       | `text`                          | 助手回复的一个片段             |
| `tool_use`    | `tool_name`, `tool_input`       | Claude 请求调用工具            |
| `tool_result` | `tool_name`, `tool_output`      | 工具已执行                     |
| `usage`       | `input_tokens`, `output_tokens` | 每轮的令牌消耗                 |
| `done`        | `conversation_id`               | 本轮结束                       |
| `error`       | `detail`                        | 流式传输中途出错               |

`tool_use` 和 `tool_result` 并不是装饰 —— 正是它们让 UI 能在工具运行时显示 "searching…",而不是一段无法解释的停顿。

每一轮的令牌用量也会写入 `app.agent` 日志记录器,因此无需在客户端埋点即可在服务器日志中看到消耗情况。

## 第 5 步:循环的一轮

`src/app/llm/agent.py` 中的 `ChatAgent.stream` 就是整个引擎。一轮的过程如下:

1. 从存储中加载对话历史。
2. 携带历史、新的用户消息和工具模式发起一个流式请求。
3. 每收到一个文本片段,就立即以 `token` 事件产出。
4. 流结束后读取最终消息;产出 `usage` 事件并记录令牌数量。
5. **如果 `stop_reason != "tool_use"`,**说明助手已经完成:持久化本轮,产出 `done`,然后返回。
6. **否则,**对每个 `tool_use` 块:产出 `tool_use`,运行处理器,产出 `tool_result`,并收集输出。
7. 将所有工具结果作为一条 `user` 消息发回 —— 这是 Messages API 的要求 —— 然后从第 2 步开始循环。

循环受 `MAX_TOOL_ITERATIONS`(默认 5)限制。如果 Claude 在超过上限后仍持续请求工具,本轮会被持久化、记录一条警告并产出 `error` 事件,而不是让服务器空转:

```python
yield AgentEvent(
    type="error",
    detail=(
        "The assistant exceeded the tool-call limit of "
        f"{self._max_tool_iterations} iterations."
    ),
)
```

在智能体循环中,这样的上限并不是可有可无的。没有它,一个误解了工具结果的模型可能会无限期地向您计费。

## 第 6 步:自带的工具

| 工具           | 用途                                                     |
|----------------|----------------------------------------------------------|
| `calculator`   | 算术运算,解析为 AST 并进行白名单检查 —— 不使用 `eval`  |
| `current_time` | 某个 IANA 时区的当前时间                                 |

`calculator` 值得再看一眼。它使用 `ast` 解析表达式,并且只遍历白名单中的节点类型,因此来自模型的工具参数无法执行任意 Python 代码。任何接受模型生成输入的工具都需要同样的纪律:**模型输出是不可信的输入。**

### 添加工具

所有内容都在 `src/app/llm/tools.py` 中:

1. 向 `TOOL_SCHEMAS` 追加一个模式 —— `name`、`description` 以及一个 JSON Schema 格式的 `input_schema`。
2. 在 `TOOL_HANDLERS` 中以相同名称注册处理器。

有两件事需要做对:

- **描述是 Claude 关于何时使用该工具所得到的全部指令。**它是提示词工程,而不是文档 —— 含糊的描述会让工具要么从不被调用,要么被不停地调用。
- **处理器应返回字符串,并把自身的失败转换为可读的消息,**而不是抛出异常。循环会把这段文本直接反馈给模型,因此 "no city named X was found" 能让模型自行恢复,而异常则会终止本轮。

## 第 7 步:对话记忆

`ConversationStore`(`src/app/memory/base.py`)是接口;自带的 `in_memory.py` 用一个字典实现了它。这对单个进程来说没问题,对其他任何情况来说都是错误的 —— 重启会忘记一切,两个 worker 对历史的认知也会不一致。

要让它可用于实际环境:针对 Redis 或数据库实现同一接口,并在 `src/app/api/deps.py` 的 `get_store()` 中返回它。智能体和路由都无需改动,因为它们都从不引用具体的类。

## 第 8 步:测试

```console
$ bash scripts/test.sh    # or: pytest
```

`tests/conftest.py` 通过一个模仿 `AsyncAnthropic.messages.stream` 的假客户端回放预先编排好的对话轮次。因此测试套件是确定性的、可离线运行、不产生任何费用,同时仍然覆盖了重要的路径:流式路径和完整的工具循环,包括调用了工具、随后模型给出回答的一轮。

在扩展智能体时请保持这一模式。针对真实模型测试 LLM 集成,会得到一个缓慢、不稳定且昂贵的测试套件,而且仍然无法断言模型会说什么。针对编排好的客户端测试*循环*,断言的恰恰是您所编写的东西。

## 第 9 步:扩展点

- **持久化历史** —— 针对 Redis 或数据库实现 `ConversationStore`(第 7 步)。
- **RAG** —— 模板刻意没有包含检索功能。最自然的接入点是 `ChatAgent.stream`:在第一次请求前获取上下文并将其添加到系统提示词开头,或者把您的索引作为另一个工具暴露出来,让模型决定何时搜索。
- **认证与限流** —— 按出厂状态,`POST /chat` 没有认证。在公开暴露之前,请为路由器加上依赖;[JWT 认证教程](auth-jwt.md) 提供了可以复用的守卫。

## 回顾

- **生成**:`fastkit startdemo fastapi-llm-agent`,设置 `ANTHROPIC_API_KEY`,`bash scripts/run-server.sh`。
- **流式传输**:SSE,包含 `token` / `tool_use` / `tool_result` / `usage` / `done` / `error` 事件。
- **循环**:流式输出 → 工具调用 → 结果作为一条用户消息发回 → 重复,受 `MAX_TOOL_ITERATIONS` 限制。
- **工具**:`TOOL_SCHEMAS` 中的一个模式加上 `TOOL_HANDLERS` 中的一个处理器;将工具输入视为不可信。
- **记忆**:`ConversationStore` 接口,字典实现,在 `get_store()` 中替换。
- **测试**:编排好的假客户端,因此测试套件可离线运行且具有确定性。

## 接下来去哪里

- [MCP 集成](mcp-integration.md) —— 如果您需要的是 MCP 服务器而不是聊天智能体。
- [JWT 认证](auth-jwt.md) —— 在聊天端点之前加上账户体系。
- [应该选择哪个 starter?](../user-guide/choosing-a-starter.md)
