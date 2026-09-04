# JWT Authentication with `fastapi-auth-jwt`

Build an API that has real accounts from the first commit. This tutorial
walks through the `fastapi-auth-jwt` template end-to-end: how token pairs
are issued and rotated, why a replayed refresh token is rejected, how the
role and scope guards are wired, and what changes when you move off SQLite.

## What you'll learn

- Generating a project with `fastkit startdemo fastapi-auth-jwt`
- The difference between the access token and the refresh token, and why
  rotation matters
- How `get_current_user`, `get_current_active_superuser` and
  `require_scopes(...)` protect a route
- Where password hashing happens and why it is argon2id
- Moving from the bundled SQLite file to PostgreSQL with Alembic

## Prerequisites

- Python 3.12+
- FastAPI-fastkit installed (`pip install fastapi-fastkit`)
- Comfort with FastAPI dependencies and pydantic schemas

If you have never built a FastAPI app before, start with
[Building a Basic API Server](basic-api-server.md) and come back — this
template assumes the basics.

## Step 1: Generate the project

```console
$ fastkit startdemo fastapi-auth-jwt
Enter the project name: accounts-api
Enter the author name: Developer Kim
Enter the author email: developer@example.com
Enter the project description: Accounts and sessions service
Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y
```

Then run it:

```console
$ cd accounts-api
$ bash scripts/run-server.sh    # or: uvicorn src.app.main:app --reload
```

The app starts on SQLite (`sqlite:///./app.db`) and creates its tables on
startup, so there is nothing to install or configure first. Docs are at
<http://127.0.0.1:8000/docs>.

!!! tip "Preview before you commit"
    `fastkit startdemo fastapi-auth-jwt --dry-run` prints the file tree and
    the package list without writing anything — handy for seeing what you
    are about to get.

## Step 2: The generated tree

```
accounts-api/
├── pyproject.toml              # PEP 621 metadata + [tool.fastapi-fastkit]
├── requirements.txt
├── alembic.ini
├── Dockerfile
├── .env                        # SECRET_KEY, DATABASE_URL, token lifetimes
├── scripts/
│   ├── format.sh  lint.sh  run-server.sh  test.sh
├── src/
│   └── app/
│       ├── main.py             # FastAPI() + lifespan + CORS + api_router
│       ├── core/
│       │   ├── config.py       # pydantic-settings
│       │   └── security.py     # argon2 hashing + JWT encode/decode
│       ├── db/session.py       # engine + get_session dependency
│       ├── api/
│       │   ├── router.py       # aggregates health + every domain router
│       │   ├── health.py       # GET /health
│       │   └── deps.py         # session, current user, role/scope guards
│       ├── domains/
│       │   ├── auth/           # login, refresh rotation, logout
│       │   └── users/          # registration and profiles
│       └── alembic/            # migration environment + versions/
└── tests/
    ├── conftest.py  test_health.py  test_auth.py  test_users.py
```

The layout is the `domain-starter` shape: each domain owns its
`router.py` (transport), `service.py` (business logic), `repository.py`
(data access), `models.py` (tables) and `schemas.py` (API I/O). Auth
concerns live in `auth/`, account concerns in `users/`, and neither
reaches into the other's internals.

## Step 3: Register, log in, call a protected route

```console
# 1. register
$ curl -X POST http://127.0.0.1:8000/api/v1/auth/register \
    -H 'Content-Type: application/json' \
    -d '{"email": "alice@example.com", "password": "s3cret-password"}'

# 2. log in — note the form encoding: this is the OAuth2 password flow
$ curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
    -d 'username=alice@example.com&password=s3cret-password'
{"access_token": "...", "refresh_token": "...", "token_type": "bearer"}

# 3. call a protected route
$ curl http://127.0.0.1:8000/api/v1/users/me \
    -H "Authorization: Bearer $ACCESS_TOKEN"
```

The Swagger "Authorize" button drives the same flow, so you can exercise
protected routes from `/docs` without leaving the browser.

The full surface:

| Method | Endpoint                    | Auth        | Description                       |
|--------|-----------------------------|-------------|-----------------------------------|
| GET    | `/api/v1/health`            | —           | Liveness probe                    |
| POST   | `/api/v1/auth/register`     | —           | Create an account                 |
| POST   | `/api/v1/auth/login`        | —           | OAuth2 password form → token pair  |
| POST   | `/api/v1/auth/refresh`      | refresh tok | Rotate into a fresh token pair    |
| POST   | `/api/v1/auth/logout`       | refresh tok | Revoke one refresh token          |
| POST   | `/api/v1/auth/logout-all`   | access tok  | Revoke every session of the user  |
| GET    | `/api/v1/users/me`          | access tok  | Current user's profile            |
| PATCH  | `/api/v1/users/me`          | access tok  | Update the current user's profile |
| GET    | `/api/v1/users/me/scopes`   | scope `me`  | Scope-gated example route         |
| GET    | `/api/v1/users`             | superuser   | Role-gated user listing           |

## Step 4: Two tokens, and why

A login returns a **pair**:

- The **access token** is short-lived (`ACCESS_TOKEN_EXPIRE_MINUTES`,
  30 by default) and travels on every request. Because it is short-lived,
  a leaked one stops working quickly.
- The **refresh token** is long-lived (`REFRESH_TOKEN_EXPIRE_DAYS`, 14 by
  default) and is used for exactly one thing: getting a new pair.

Nothing above is unusual. What makes this template different from the
average JWT snippet is that refresh tokens are **tracked and rotated**.
Every issued refresh token gets a `jti` claim, and that `jti` is written
into the database:

```python
def issue_token_pair(self, user: User) -> TokenPair:
    scopes = user.scope_list
    access_token, _, _ = create_access_token(str(user.id), scopes)
    refresh_token, jti, expires_at = create_refresh_token(str(user.id), scopes)
    self.refresh_tokens.add(jti, user.id or 0, expires_at)
    return TokenPair(access_token=access_token, refresh_token=refresh_token)
```

On refresh, the presented token is revoked **before** the new pair is
issued:

```python
def rotate(self, refresh_token: str) -> TokenPair:
    payload = decode_token(refresh_token, REFRESH_TOKEN_TYPE)
    record = self.refresh_tokens.get_by_jti(str(payload.get("jti")))
    if record is None or record.revoked:
        raise TokenError("refresh token is no longer valid")
    ...
    self.refresh_tokens.revoke(record)
    return self.issue_token_pair(user)
```

Try it: refresh once, then send the *old* refresh token again.

```console
$ curl -X POST http://127.0.0.1:8000/api/v1/auth/refresh \
    -H 'Content-Type: application/json' \
    -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}"
# → new pair

$ curl -X POST http://127.0.0.1:8000/api/v1/auth/refresh \
    -H 'Content-Type: application/json' \
    -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}"
# → 401: the token died the moment it was used
```

That single property is what turns a stolen refresh token from a
permanent backdoor into a detectable, single-use failure.

Logout works the same way, which is the other thing plain JWT setups
usually cannot do: `POST /auth/logout` revokes one token,
`POST /auth/logout-all` revokes every refresh token belonging to the user.

## Step 5: Passwords

Hashing lives in `src/app/core/security.py` and goes through `pwdlib`
with **argon2id** — the current recommended default, not a legacy bcrypt
configuration. Nothing in the routers or services ever sees a plaintext
password beyond the moment it is verified, and `hashed_password` is never
part of a response schema.

You do not need to configure anything here. The one thing you *must*
configure is the signing key.

## Step 6: Roles and scopes

Three guards ship as FastAPI dependencies:

```python
CurrentUser = Annotated[User, Depends(get_current_user)]
```

- **`get_current_user`** decodes the bearer access token, loads the user,
  and rejects inactive accounts with `403`. Anything malformed, expired,
  or pointing at a deleted user comes back as `401`.
- **`get_current_active_superuser`** layers an `is_superuser` check on
  top. `GET /api/v1/users` uses it.
- **`require_scopes(...)`** builds a dependency demanding specific
  scopes:

```python
from fastapi import Depends
from src.app.api.deps import require_scopes

@router.get("/reports", dependencies=[Depends(require_scopes("reports"))])
def read_reports() -> list[str]:
    ...
```

Scopes live on the user row as a comma-separated string (`scopes: str`,
read back through the `scope_list` property) and are copied into every
issued token. That is deliberately the simplest thing that works for a
starter; when your permission model outgrows a string, replace the column
with a roles table and keep the dependency signatures unchanged — nothing
in the routers has to move.

## Step 7: Adding a protected domain

To add, say, an `orders` domain that only logged-in users can reach:

1. Create `src/app/domains/orders/` mirroring `users/`
   (`models.py`, `schemas.py`, `repository.py`, `service.py`, `router.py`).
2. Take `CurrentUser` as a parameter in the routes that need an account,
   or attach `Depends(require_scopes("orders"))` to the router.
3. Register the router in `src/app/api/router.py`, above the
   `# fastkit:routes` anchor. `fastkit addroute` writes into those same
   anchors, so hand-written and generated routes stay in one place.
4. Generate a migration: `alembic revision --autogenerate -m "add orders"`.
5. Mirror `tests/test_users.py` for the new endpoints.

## Step 8: SQLite now, PostgreSQL later

The default `DATABASE_URL` is a local SQLite file and the app calls
`create_db_and_tables()` on startup, which is why `pytest` and `uvicorn`
both work with zero setup. For anything beyond local development, let
Alembic own the schema instead:

```console
$ export DATABASE_URL='postgresql+psycopg://postgres:postgres@localhost:5432/app_db'
$ alembic upgrade head
```

After a model change:

```console
$ alembic revision --autogenerate -m "add profile fields"
```

## Step 9: Before you deploy

Two settings in `.env` decide whether this is a demo or a real service:

- **`SECRET_KEY`** signs every token. Leave it unset and a random key is
  generated per process — which logs everyone out on every restart, and
  makes multiple workers disagree about which tokens are valid. Generate
  one and pin it:

  ```console
  $ python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```

- **`DATABASE_URL`** selects the database. The SQLite default is not a
  production store.

Optionally set `FIRST_SUPERUSER_EMAIL` and `FIRST_SUPERUSER_PASSWORD` to
have a superuser seeded on startup, and `BACKEND_CORS_ORIGINS` to a
comma-separated list of front-end origins.

## Step 10: The tests

```console
$ bash scripts/test.sh    # or: pytest
```

The suite runs `httpx.AsyncClient` against an in-memory SQLite database
and covers the whole happy path — register → login → me → refresh →
logout — plus the rejection paths that actually matter: wrong password,
malformed token, expired token, and the replayed refresh token from
Step 4. When you extend the auth rules, extend those rejection tests
first; they are the ones that catch a broken guard.

## Recap

- **Generation**: `fastkit startdemo fastapi-auth-jwt` →
  `bash scripts/run-server.sh` → docs at `/docs`.
- **Tokens**: short-lived access token for requests, rotating refresh
  token tracked by `jti` so replays fail and logout is real.
- **Guards**: `get_current_user`, `get_current_active_superuser`, and
  `require_scopes(...)` as plain dependencies.
- **Storage**: SQLite for free, PostgreSQL by setting `DATABASE_URL` and
  running `alembic upgrade head`.
- **Before deploying**: pin `SECRET_KEY`, point `DATABASE_URL` at a real
  database.

## Where to go next

- [SQLModel Persistence](sqlmodel.md) — the same domain layout focused on
  async data access, migrations and generic CRUD.
- [Domain-oriented Project](domain-starter.md) — the layout this template
  builds on, without the auth machinery.
- [Which starter should I choose?](../user-guide/choosing-a-starter.md) —
  how this template compares with the rest.
