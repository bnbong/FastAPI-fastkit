# Streaming LLM agent with `fastapi-llm-agent`

Build a chat backend that streams tokens as they are generated and can
actually *do* things — call tools, read their results, and keep going.
This tutorial walks through the `fastapi-llm-agent` template: the SSE
event protocol, the tool-call loop and its iteration cap, conversation
memory behind an interface, and a test suite that never touches the
network.

## What you'll learn

- Generating a project with `fastkit startdemo fastapi-llm-agent`
- The SSE event types a client has to handle, and what each one means
- How one turn of the tool-call loop works, step by step
- Adding your own tool
- Swapping the in-process conversation store for a real one
- Why the tests are deterministic and free to run

## Prerequisites

- Python 3.12+
- FastAPI-fastkit installed (`pip install fastapi-fastkit`)
- An Anthropic API key — only to talk to a real model. The generated test
  suite runs without one.
- Familiarity with `async`/`await` and async generators

## Step 1: Generate and configure

```console
$ fastkit startdemo fastapi-llm-agent
Enter the project name: support-agent
Enter the author name: Developer Kim
Enter the author email: developer@example.com
Enter the project description: Streaming support assistant
Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y
```

Put your key in `.env` before the first run:

```bash
ANTHROPIC_API_KEY=sk-ant-...
LLM_MODEL=claude-sonnet-5
LLM_MAX_TOKENS=4096
MAX_TOOL_ITERATIONS=5
```

The key is read by pydantic-settings and handed to the client at
construction. It is never written into source and never baked into the
Docker image.

```console
$ cd support-agent
$ bash scripts/run-server.sh
$ bash scripts/chat.sh "What is 12 * 34?"
```

!!! tip "Using a gateway instead of the Anthropic API"
    Set `LLM_BASE_URL` (and `LLM_AUTH_TOKEN` if the gateway uses bearer
    auth) to point at LiteLLM, an internal proxy, or a local server. The
    wire format stays the Anthropic Messages API; translating for other
    providers is the gateway's job, not the app's.

## Step 2: The generated tree

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

Three boundaries are worth noticing up front: the **client** is created
by a factory (so tests can substitute one), **memory** is an interface
with a trivial implementation (so production can substitute one), and
**tools** are a schema list plus a handler dict (so adding one touches
one file).

## Step 3: The endpoints

| Method | Endpoint                     | Description             |
|--------|------------------------------|-------------------------|
| GET    | `/api/v1/health`             | Liveness probe          |
| POST   | `/api/v1/chat`               | Stream a reply as SSE   |
| GET    | `/api/v1/conversations/{id}` | Read stored history     |
| DELETE | `/api/v1/conversations/{id}` | Forget a conversation   |

`POST /api/v1/chat` takes `{"message": "...", "conversation_id": "..."}`.
Omit `conversation_id` to start a new conversation and read the assigned
id back from the final `done` event.

## Step 4: The stream protocol

Each SSE message carries its type in the `event:` field and a JSON
envelope in `data:`. A client has to handle five of them plus errors:

| Event         | Fields                          | Meaning                        |
|---------------|---------------------------------|--------------------------------|
| `token`       | `text`                          | A chunk of the assistant reply |
| `tool_use`    | `tool_name`, `tool_input`       | Claude requested a tool        |
| `tool_result` | `tool_name`, `tool_output`      | The tool ran                   |
| `usage`       | `input_tokens`, `output_tokens` | Per-turn token spend           |
| `done`        | `conversation_id`               | The turn finished              |
| `error`       | `detail`                        | Something failed mid-stream    |

`tool_use` and `tool_result` are not decoration — they are what lets a UI
show "searching…" instead of an unexplained pause while a tool runs.

Token usage is also written to the `app.agent` logger on every turn, so
spend is visible in server logs without instrumenting a client.

## Step 5: One turn of the loop

`ChatAgent.stream` in `src/app/llm/agent.py` is the whole engine. A turn
goes:

1. Load the conversation history from the store.
2. Open a streaming request with the history, the new user message, and
   the tool schemas.
3. Yield every text chunk as a `token` event as it arrives.
4. When the stream ends, read the final message; emit a `usage` event and
   log the token counts.
5. **If `stop_reason != "tool_use"`,** the assistant is finished: persist
   the turn, emit `done`, return.
6. **Otherwise,** for each `tool_use` block: emit `tool_use`, run the
   handler, emit `tool_result`, and collect the output.
7. Send every tool result back as a single `user` message — that is what
   the Messages API requires — and loop from step 2.

The loop is bounded by `MAX_TOOL_ITERATIONS` (5 by default). If Claude
keeps asking for tools past the cap, the turn is persisted, a warning is
logged, and an `error` event is emitted rather than the server spinning:

```python
yield AgentEvent(
    type="error",
    detail=(
        "The assistant exceeded the tool-call limit of "
        f"{self._max_tool_iterations} iterations."
    ),
)
```

A cap like this is not optional in an agent loop. Without it a model that
misunderstands a tool result can bill you indefinitely.

## Step 6: The bundled tools

| Tool           | Purpose                                                  |
|----------------|----------------------------------------------------------|
| `calculator`   | Arithmetic, parsed to an AST and whitelisted — not `eval` |
| `current_time` | Current time in an IANA timezone                          |

The `calculator` deserves a second look. It parses the expression with
`ast` and walks only whitelisted node types, so a tool argument coming
from a model cannot execute arbitrary Python. Any tool that accepts
model-generated input needs the same discipline: **model output is
untrusted input.**

### Adding a tool

Everything lives in `src/app/llm/tools.py`:

1. Append a schema to `TOOL_SCHEMAS` — `name`, `description`, and a JSON
   Schema `input_schema`.
2. Register the handler in `TOOL_HANDLERS` under the same name.

Two things to get right:

- **The description is the entire instruction Claude gets** about when to
  reach for the tool. It is prompt engineering, not documentation —
  vague descriptions produce tools that are never called, or called
  constantly.
- **Handlers should return a string and turn their own failures into a
  readable message** rather than raising. The loop feeds that text
  straight back to the model, so "no city named X was found" lets the
  model recover, while an exception ends the turn.

## Step 7: Conversation memory

`ConversationStore` (`src/app/memory/base.py`) is the interface; the
bundled `in_memory.py` implements it with a dict. That is fine for a
single process and wrong for anything else — a restart forgets
everything, and two workers disagree about history.

To make it real: implement the same interface against Redis or a
database, and return it from `get_store()` in `src/app/api/deps.py`.
Nothing in the agent or the routers changes, because neither ever names
the concrete class.

## Step 8: The tests

```console
$ bash scripts/test.sh    # or: pytest
```

`tests/conftest.py` replays scripted turns through a fake that mimics
`AsyncAnthropic.messages.stream`. So the suite is deterministic, runs
offline, costs nothing, and still covers the paths that matter: the
streaming path and the full tool loop, including a turn where a tool is
called and the model then answers.

This is the pattern to keep as you extend the agent. Testing an LLM
integration against the live model gives you a slow, flaky, expensive
suite that still cannot assert what the model will say. Testing the
*loop* against a scripted client asserts exactly the thing you wrote.

## Step 9: Extension points

- **Persistent history** — implement `ConversationStore` against Redis or
  a database (Step 7).
- **RAG** — retrieval is deliberately out of scope in the template. The
  natural seam is `ChatAgent.stream`: fetch context before the first
  request and prepend it to the system prompt, or expose your index as
  one more tool and let the model decide when to search.
- **Auth and rate limiting** — `POST /chat` is unauthenticated as
  shipped. Put a dependency on the router before exposing it publicly;
  the [JWT Authentication tutorial](auth-jwt.md) has the guards you
  would reuse.

## Recap

- **Generation**: `fastkit startdemo fastapi-llm-agent`, set
  `ANTHROPIC_API_KEY`, `bash scripts/run-server.sh`.
- **Streaming**: SSE with `token` / `tool_use` / `tool_result` / `usage`
  / `done` / `error` events.
- **Loop**: stream → tool calls → results back as one user message →
  repeat, bounded by `MAX_TOOL_ITERATIONS`.
- **Tools**: a schema in `TOOL_SCHEMAS` and a handler in
  `TOOL_HANDLERS`; treat tool input as untrusted.
- **Memory**: `ConversationStore` interface, dict implementation, swap
  it in `get_store()`.
- **Tests**: a scripted fake client, so the suite is offline and
  deterministic.

## Where to go next

- [Integrating with MCP](mcp-integration.md) — if you need an MCP server
  rather than a chat agent.
- [JWT Authentication](auth-jwt.md) — putting accounts in front of the
  chat endpoint.
- [Which starter should I choose?](../user-guide/choosing-a-starter.md)
