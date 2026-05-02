# Architecture preset / feature matrix

Interactive `fastkit init --interactive` asks for an **architecture preset**
([issue #44](https://github.com/bnbong/FastAPI-fastkit/issues/44)) before
collecting feature selections. The preset shapes the generated project's
layout — different presets ship a different base template and put generated
config files in different locations so they sit next to the existing
structure rather than in a parallel `src/config/` tree.

This page is the source of truth for what each preset does, where files
land, and which feature combinations require manual wiring.

## Preset → base template

| Preset | Base template | Description |
|---|---|---|
| `minimal` | `fastapi-empty` | Smallest viable FastAPI app — placeholder `main.py` is regenerated from your feature selections. |
| `single-module` | `fastapi-single-module` | Single-file FastAPI app — `main.py` is regenerated. |
| `classic-layered` | `fastapi-default` | Layered split (`api/routes`, `crud`, `schemas`, `core`). Shipped `main.py` is preserved. |
| `domain-starter` | `fastapi-domain-starter` | Domain-oriented (`src/app/domains/<concept>/`). Shipped `main.py` is preserved. **Recommended default.** |

## Generated file locations

| Preset | `main.py` overlay | Database config target | Auth config target |
|---|---|---|---|
| `minimal` | regenerated at `src/main.py` | `src/config/database.py` | `src/config/auth.py` |
| `single-module` | regenerated at `src/main.py` | `src/config/database.py` | `src/config/auth.py` |
| `classic-layered` | preserved (template-shipped) | `src/core/database.py` | `src/core/auth.py` |
| `domain-starter` | preserved (template-shipped) | `src/app/core/database.py` | `src/app/core/auth.py` |

## Database / auth feature support per preset

These features are supported across **every** preset — the package install
always succeeds; the difference is whether the dynamic `main.py` overlay
also wires them up automatically.

| Feature | `minimal` / `single-module` | `classic-layered` / `domain-starter` |
|---|---|---|
| **Database** (PostgreSQL, MySQL, SQLite, MongoDB) | Generates the config module **and** stubs `await init_db()` calls in the regenerated `main.py`. | Generates the config module at the preset's path. The shipped `main.py` is **preserved**, so wire `get_db()` into routers manually. |
| **Authentication** (JWT, FastAPI-Users, OAuth2, Session-based) | Generates the auth config module. JWT also imports `HTTPBearer` in the regenerated `main.py`. | Generates the auth config module at the preset's path. No imports added to `main.py` — wire dependencies manually. |
| **Background tasks** (Celery, Dramatiq) | Packages installed; no main.py overlay today. | Same. |
| **Caching** (Redis) | Packages installed; no main.py overlay today. | Same. |
| **CORS** (utility) | `CORSMiddleware` added to the regenerated `main.py` with `allow_origins=['*']`. | **Already wired** in the shipped `main.py` (conditional on `settings.all_cors_origins`). Activate by setting `BACKEND_CORS_ORIGINS` in `.env` — no code edits required. |
| **Testing** (Basic / Coverage / Advanced) | `pytest.ini` is generated at the project root. | Same. |
| **Deployment** (Docker, docker-compose) | `Dockerfile` and/or `docker-compose.yml` written at the project root. | Same. |

## When you'll see a "Preset compatibility" warning

For presets that **preserve the shipped `main.py`** (`classic-layered`,
`domain-starter`), some feature selections won't be auto-wired into the
app. The CLI surfaces a one-shot warning at the end of generation listing
which selections need manual wiring:

| Selected feature | Triggers a warning under `classic-layered` / `domain-starter`? |
|---|---|
| `CORS` (utility) | ❌ — already wired in the shipped `main.py`. Just populate `BACKEND_CORS_ORIGINS` in `.env`. |
| `Rate-Limiting` (utility) | ✅ — `slowapi` limiter setup is not added |
| `Prometheus` (monitoring) | ✅ — `Instrumentator().instrument(app)` is not called |
| Any database / auth selection | ⚠️ — config files are generated, but you must `Depends()` them into your routers |

For `minimal` and `single-module` presets the dynamic `main.py` overlay
handles CORS, rate-limiting, and Prometheus instrumentation automatically;
no warnings fire.

## Unsupported combinations (stay safe)

The strategist deliberately **does not** attempt to splice generated code
into a template-shipped `main.py`. Doing so would risk producing broken
imports or duplicating routers. The contract is:

- Selected packages are always installed (so `pip freeze` matches the
  user's intent).
- Generated config modules always land at the preset-appropriate path.
- For preserve-main presets, the user is told which selections still need
  manual wiring instead of getting silently broken code.

If you need full auto-wiring of every feature, pick `minimal` or
`single-module` — they regenerate `main.py` from feature flags.
