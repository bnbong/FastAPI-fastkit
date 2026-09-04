# Which starter should I choose?

FastAPI-fastkit ships several ways to bootstrap a project. This page is a
**decision aid** for newcomers: pick a path here, then jump to
[Quick Start](quick-start.md) to actually create the project.

If you're not sure, the short answer is:

> **Start with `fastkit init --interactive` and pick the
> `domain-starter` preset.** It's the recommended default for modern API
> projects.

The rest of this page explains why, and when to pick something else.

## TL;DR — pick by user type

| You are... | Start with |
|---|---|
| New to FastAPI, want a guided walkthrough | `fastkit init --interactive` (preset: **`domain-starter`**) |
| Want a working CRUD demo to read and modify | `fastkit startdemo fastapi-default` |
| Want the smallest possible scaffold | `fastkit init --interactive` (preset: **`minimal`**) |
| Writing a quick prototype / single-file script | `fastkit init --interactive` (preset: **`single-module`**) |
| Need a real database (PostgreSQL + SQLAlchemy + Alembic) | `fastkit startdemo fastapi-psql-orm` |
| Want async persistence with migrations and generic CRUD | `fastkit startdemo fastapi-sqlmodel` |
| Need user accounts, login and protected routes on day one | `fastkit startdemo fastapi-auth-jwt` |
| Building an LLM chat backend with streaming and tools | `fastkit startdemo fastapi-llm-agent` |
| Want production-style domain layout for a medium-sized API | `fastkit init --interactive` (preset: **`domain-starter`**) |

## `startdemo` vs `init --interactive` — what's the difference?

These are the two main entry points. They serve different needs.

### `fastkit startdemo <template>`

Drops a **complete, working example** project onto disk based on one of the
shipped templates (`fastapi-default`, `fastapi-async-crud`,
`fastapi-psql-orm`, `fastapi-domain-starter`, ...). The template's source
code is pasted as-is, with metadata placeholders (`<project_name>`, etc.)
filled in.

- ✅ Fastest path to a runnable demo.
- ✅ All code is real and readable — great for learning by example.
- ❌ The template's stack and structure are fixed; you can't pick CORS but
  drop authentication on the way in.

```console
$ fastkit list-templates              # show what's available
$ fastkit startdemo fastapi-default   # generate a project from one
```

### `fastkit init --interactive`

Walks you through a **guided wizard**: project metadata → architecture
preset → feature selections (database, auth, testing, deployment, ...) →
package manager → confirmation. The generator picks an appropriate base
template per preset and overlays the features you chose.

- ✅ You assemble the stack you actually want.
- ✅ The architecture preset shapes the project layout (single-file, layered,
  domain-oriented, ...).
- ❌ The richer preserve-main presets (`classic-layered`, `domain-starter`)
  generate config modules but expect you to wire them into the shipped
  routers yourself. See the
  [Architecture Preset Matrix](../reference/preset-feature-matrix.md) for
  the per-preset / per-feature contract.

```console
$ fastkit init --interactive
```

## The four architecture presets

These appear inside `fastkit init --interactive` after the project info
prompts. Use this section to decide which one to pick.

### `minimal` — start simplest, grow later

Smallest viable FastAPI app. Empty scaffold + a single
`src/main.py` regenerated from your feature flags. CORS, rate limiting,
and Prometheus instrumentation are auto-wired into `main.py` if selected.

- 👤 **Who**: people who want to add structure themselves as the project
  grows, or are exploring FastAPI without preconceived layout opinions.
- 📦 **Base template**: `fastapi-empty`.
- 🧠 **Mental model**: "give me one file with FastAPI imported and let me
  figure out the rest."

### `single-module` — script-style prototype

Everything lives in one module. Same regenerate-`main.py` overlay as
`minimal`.

- 👤 **Who**: writing a glue script, a small webhook, or a one-day
  prototype that doesn't need package boundaries.
- 📦 **Base template**: `fastapi-single-module`.
- 🧠 **Mental model**: "I want one Python file I can run and read in one
  sitting."

### `classic-layered` — layered split (api / crud / schemas / core)

The "Django-flavoured" layout — code is split horizontally by concern:
all routers in `api/`, all CRUD logic in `crud/`, all pydantic schemas in
`schemas/`, all configuration in `core/`. The shipped `main.py` is
**preserved** (it already wires CORS for you); generated database/auth
configs land under `src/core/`.

- 👤 **Who**: teams familiar with Django/Rails-style layouts, projects
  with many small endpoints sharing common CRUD plumbing.
- 📦 **Base template**: `fastapi-default`.
- 🧠 **Mental model**: "split code by what it _is_."

### `domain-starter` — domain-oriented (recommended default)

Code is split vertically by **business concept**: each domain owns its
own router, service, repository, and schemas under
`src/app/domains/<concept>/`. Comes with a `/health` endpoint and an
`items` example domain that you copy and rename for each new concept.
The shipped `main.py` (under `src/app/`) is preserved; generated configs
land under `src/app/core/`.

- 👤 **Who**: medium-sized APIs that will grow several distinct concepts
  (users, orders, billing, ...). The recommended modern default.
- 📦 **Base template**: `fastapi-domain-starter`.
- 🧠 **Mental model**: "split code by what it _does_ for the business."

## Comparison matrix

A side-by-side at a glance.

| | `minimal` | `single-module` | `classic-layered` | `domain-starter` |
|---|---|---|---|---|
| Base template | `fastapi-empty` | `fastapi-single-module` | `fastapi-default` | `fastapi-domain-starter` |
| Project entry | `src/main.py` | `src/main.py` | `src/main.py` | `src/app/main.py` |
| Routers location | (you add) | (inside `main.py`) | `src/api/routes/` | `src/app/domains/<concept>/router.py` |
| Per-domain folders | ❌ | ❌ | ❌ | ✅ |
| Built-in `/health` endpoint | ✅ | ✅ | ❌ | ✅ |
| `main.py` regenerated from features | ✅ | ✅ | ❌ | ❌ |
| CORS pre-wired in `main.py` | added when selected | added when selected | yes (env-driven) | yes (env-driven) |
| pyproject-first | optional | optional | optional | ✅ |
| Best for | "I'll grow my own structure" | "one-file prototype" | "split by concern" | "split by business concept" |

For the full per-feature contract (database / auth config target paths,
which selections need manual wiring vs auto-wiring, when warnings fire),
see the [Architecture Preset Matrix](../reference/preset-feature-matrix.md).

## Picking a `startdemo` template

`fastkit startdemo <template>` is best when you want a **complete,
runnable example** rather than a guided assembly. Most templates roughly
correspond to one of the four presets above, but they ship with extra
example code (CRUD endpoints over a mock store, custom response handling,
Docker tooling, etc.).

| Template | Closest preset | When to pick it |
|---|---|---|
| `fastapi-default` | `classic-layered` | Working CRUD demo with the layered layout. Good first stop. |
| `fastapi-empty` | `minimal` | Bare scaffold; same shape `minimal` lands on. |
| `fastapi-single-module` | `single-module` | Single-file demo. |
| `fastapi-domain-starter` | `domain-starter` | Recommended modern default; ships with an items domain example. |
| `fastapi-auth-jwt` | `domain-starter` | Your API needs accounts. Access/refresh tokens, argon2id hashing, roles and scopes, Alembic migrations. |
| `fastapi-sqlmodel` | `domain-starter` | Async persistence first: SQLModel + async SQLAlchemy, migrations, a generic CRUD base and paginated lists. |
| `fastapi-llm-agent` | `domain-starter` | A streaming Claude chat backend with a real tool-call loop and offline tests. |
| `fastapi-custom-response` | `classic-layered` | Demonstrates custom response envelopes / formatting. |
| `fastapi-psql-orm` | (no direct preset) | PostgreSQL + SQLAlchemy + Alembic, synchronous. Pick this when you want a Compose stack around a real database. |
| `fastapi-mcp` | (no direct preset) | Model Context Protocol integration. |
| `fastapi-async-crud` | `classic-layered` | ⚠️ **Deprecated.** Async-flavoured equivalent of `fastapi-default`; prefer `fastapi-sqlmodel`. |
| `fastapi-dockerized` | `classic-layered` | ⚠️ **Deprecated.** Adds a Dockerfile to the default layout; every current template ships one. |

### The three newer starters

Added in v1.4.0, all three follow the `domain-starter` shape (`src/app/`
with per-concept folders) so they compose with what you already know from
that preset.

**`fastapi-auth-jwt` — authentication that survives contact with production.**
Access tokens are short-lived; refresh tokens rotate on every use and are
tracked by their `jti` in the database, so a replayed token is rejected
rather than silently accepted. Passwords are hashed with argon2id via
`pwdlib`. Logout is real: revoke one session or every session of a user.
Guards ship as dependencies — `get_current_user`,
`get_current_active_superuser`, and a `require_scopes(...)` factory. It runs
on SQLite with no external services and moves to PostgreSQL by setting
`DATABASE_URL`. Walkthrough: [JWT Authentication](../tutorial/auth-jwt.md).

**`fastapi-sqlmodel` — one model definition per concept.**
A SQLModel class is both the SQLAlchemy table and the pydantic schema, so a
new column is declared once and every request/response schema inherits it.
Async all the way down, async Alembic migrations, a `CRUDBase` that supplies
create / read / list / count / update / delete so each domain only writes
what is specific to it, and list endpoints wrapped in a page envelope.
Walkthrough: [SQLModel Persistence](../tutorial/sqlmodel.md).

**`fastapi-llm-agent` — a chat backend, not a `POST /completion` wrapper.**
Tokens stream to the client over SSE, and a tool-call loop runs until the
model is done or the iteration cap fires. Conversation history sits behind a
`ConversationStore` interface, so moving from the bundled dict to Redis is
one implementation. The test suite replaces the Anthropic client with a
scripted fake — deterministic, offline, no API key.
Walkthrough: [LLM Agent](../tutorial/llm-agent.md).

### About the deprecated templates

`fastapi-async-crud` and `fastapi-dockerized` are still shipped and still
generate working projects — nothing breaks if you use them. They are marked
deprecated because the reason to pick them has gone away:

- `fastapi-dockerized` existed to add a Dockerfile. Every current template
  ships one, and interactive deployment selection generates Docker files for
  any preset.
- `fastapi-async-crud` demonstrated async endpoints over a mock store.
  `fastapi-sqlmodel` does the same thing against a real async database, with
  migrations.

Existing projects generated from either template need no action.

`fastkit list-templates` shows the live list with one-line descriptions.

## Common questions

**Q. Do I have to pick a preset / template up front?**
No — you can always reorganize the generated code by hand later. The
presets are starting points, not contracts. Don't over-think the choice.

**Q. Which is the "modern" choice?**
`domain-starter`. It's pyproject-first, ships with a `/health` endpoint,
and uses the layout most well-run mid-sized FastAPI projects converge on.

**Q. Can I switch from `classic-layered` to `domain-starter` later?**
Yes, but it's a manual refactor — there's no migration command. If you
think your project will grow enough to need domain folders, start there.

**Q. What if I just want to learn FastAPI?**
Start with `fastkit startdemo fastapi-default` — read the code, run the
tests, change a few endpoints. Once you're comfortable, `fastkit init
--interactive` with the `domain-starter` preset is the natural next step.

**Q. Where do I see the exact files each preset generates?**
The [Architecture Preset Matrix](../reference/preset-feature-matrix.md)
is the reference page for that.

## Next steps

- [Quick Start](quick-start.md) — actually create your first project.
- [Creating Projects](creating-projects.md) — deeper walkthrough of the
  CLI flags.
- [JWT Authentication tutorial](../tutorial/auth-jwt.md),
  [SQLModel Persistence tutorial](../tutorial/sqlmodel.md), and
  [LLM Agent tutorial](../tutorial/llm-agent.md) — end-to-end walkthroughs
  of the three starters added in v1.4.0.
- [Domain-oriented Project tutorial](../tutorial/domain-starter.md) —
  if you picked `domain-starter`, this is the end-to-end walkthrough of
  the generated tree, the bundled `items` example, and how to add your
  next domain.
- [Architecture Preset Matrix](../reference/preset-feature-matrix.md) —
  the full per-preset / per-feature contract.
