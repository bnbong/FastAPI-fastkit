# CLI 레퍼런스

FastAPI-fastkit의 모든 커맨드라인 인터페이스 명령어를 한눈에 볼 수 있는 레퍼런스입니다.

## 전역 옵션

모든 명령은 다음의 전역 옵션을 지원합니다:

```console
$ fastkit [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS]
```

### 전역 옵션

| 옵션 | 설명 |
|--------|-------------|
| `--version` | FastAPI-fastkit 버전 표시 |
| `--help` | 도움말 표시 |

### 예시

<div class="termy">

```console
$ fastkit --version
FastAPI-fastkit version 1.0.0

$ fastkit --help
Usage: fastkit [OPTIONS] COMMAND [ARGS]...

  FastAPI-fastkit CLI

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  addroute       Add a new route to FastAPI project
  init           Create a new FastAPI project
  list-templates List available FastAPI templates
  runserver      Start FastAPI development server
  startdemo      Create FastAPI project from template
```

</div>

## 명령어

### `init`

대화형 설정으로 새 FastAPI 프로젝트를 생성합니다.

#### 문법

```console
$ fastkit init [OPTIONS]
```

#### 옵션

| 옵션 | 설명 | 기본값 |
|--------|-------------|---------|
| `--interactive` | 아키텍처 프리셋과 기능을 단계별로 고르는 가이드형 설정 | 꺼짐 |
| `--config <경로>` | 저장해 둔 설정 파일로 프롬프트 없이 프로젝트 생성 | - |
| `--save-config <경로>` | `--interactive` 와 함께 쓰면 답변한 설정을 이 경로에 저장 | - |
| `--project-name` | 프로젝트 이름 (생략하면 물어봄) | - |
| `--author` | 작성자 이름 (생략하면 물어봄) | - |
| `--author-email` | 작성자 이메일 (생략하면 물어봄) | - |
| `--description` | 프로젝트 설명 (생략하면 물어봄) | - |
| `--package-manager` | 사용할 패키지 매니저 (pip, uv, pdm, poetry) | uv |
| `--dry-run` | 무엇이 만들어질지만 보여주고 아무것도 쓰지 않음 | 꺼짐 |
| `--no-venv` | 가상환경 생성을 건너뜀 (`--no-install` 포함) | 꺼짐 |
| `--no-install` | 의존성 설치를 건너뜀 | 꺼짐 |
| `--yes` / `-y` | 프로젝트를 그 자리에(in-place) 배포할 때 기존 파일을 덮어쓰기 전에 확인을 묻지 않음 | 꺼짐 |
| `--help` | 명령 도움말 표시 | - |

#### 설정 파일 (`--config` / `--save-config`)

대화형 세션에서 고른 답변은 결국 평범한 매핑이고, 그 매핑은 파일에 담아
옮길 수 있습니다. 덕분에 프로젝트 생성을 커밋하고 리뷰하고 다시 실행할 수
있게 됩니다.

```console
# 대화형 세션의 선택을 기록
$ fastkit init --interactive --save-config fastkit.config.json

# 나중에 프롬프트 없이 그대로 재생성
$ fastkit init --config fastkit.config.json
```

`--save-config` 를 주지 않아도, 끝까지 진행한 대화형 실행은 선택을 저장할지
와 저장 위치를 물어봅니다. 이 질문은 사람이 터미널 앞에 있을 때만 나오며,
파이프로 입력을 받거나 CI에서 도는 실행은 조용히 넘어가고 대신 플래그로
저장을 요청합니다.

**지원 형식** 은 확장자로 결정됩니다.

| 확장자 | 사용 가능 여부 |
|---|---|
| `.json` | 항상 (표준 라이브러리) |
| `.toml` | 항상 (표준 라이브러리) |
| `.yaml` / `.yml` | PyYAML 이 설치돼 있을 때만 — fastkit 은 이를 런타임 의존성으로 추가하지 않습니다 |

불러올 파일은 최상위가 매핑이어야 하고 최소한 `project_name`, `author`,
`author_email` 을 담아야 합니다. 이후 대화형 프롬프트와 똑같은 규칙(프로젝트
이름 형식, 이메일 형식, `all_dependencies` 는 리스트)으로 검증하며, 문제가
있으면 아무것도 쓰기 전에 모두 알려 줍니다. `all_dependencies` 없이 기능
선택만 적힌 파일은 대화형 빌더를 통해 확장되므로, 직접 쓴 설정 파일과 마법사
세션이 동일한 패키지 집합으로 수렴합니다.

최소 예시:

```json
{
  "project_name": "orders-api",
  "author": "Developer Kim",
  "author_email": "developer@example.com",
  "description": "Domain-oriented orders service",
  "architecture_preset": "domain-starter",
  "package_manager": "uv"
}
```

#### 설정 파일 스키마

직접 쓴 파일이든 `--save-config` 로 저장한 파일이든, 모든 설정 파일은
생성기에 전달되기 전에 동일한 정규화 과정을 거칩니다
(`backend/project_builder/config_schema.py` 의 `normalize_project_config`).
알 수 없는 키, 알려진 축의 알 수 없는 선택지, 잘못된 타입의 값은 어떤 것이
문제인지와 실제로 허용되는 값 목록을 함께 알려 주며 거부됩니다.

| 키 | 형태 | 비고 |
|---|---|---|
| `project_name`, `author`, `author_email` | 문자열 | 필수 |
| `description` | 문자열 | 필수 |
| `architecture_preset` (별칭 `preset`) | `"minimal"` \| `"single-module"` \| `"classic-layered"` \| `"domain-starter"` | 둘 다 있으면 값이 일치해야 함 |
| `package_manager` | `"pip"` \| `"uv"` \| `"pdm"` \| `"poetry"` | |
| `database` | 문자열, 또는 `{"type": <선택지>}` | `PostgreSQL`, `MySQL`, `MongoDB`, `Redis`, `SQLite`, `None` |
| `authentication`, `async_tasks`, `testing`, `caching`, `monitoring`, `migrations`, `logging` | 문자열, 또는 `{"type": <선택지>}` | 단일 선택 축 — 각 축의 선택지는 위의 [기능 카탈로그](#-interactive) 참고 |
| `utilities`, `tooling` | 문자열 리스트 | 다중 선택 축 — 선택지는 동일한 카탈로그 참고 |
| `deployment` | 문자열 리스트 | `Docker`, `docker-compose` 의 부분집합; `docker-compose` 를 고르면 `Docker` 도 자동으로 함께 포함됨 |
| `custom_packages` | 문자열 리스트 | 그대로 설치할 추가 패키지 |

모든 축은 값을 그대로(`"authentication": "JWT"`) 받거나, `database` 와
프로젝트 자체의 `[tool.fastapi-fastkit]` 메타데이터가 쓰는
`{"type": ...}` 매핑 형태(`"authentication": {"type": "JWT"}`)로도 받을 수
있습니다 — 둘 다 동일한 정규 형태로 변환되며, `--save-config` 는 항상 정규
형태인 순수 문자열 형태로 저장합니다.

대부분의 축을 활용한 설정 예시:

```json
{
  "project_name": "orders-api",
  "author": "Developer Kim",
  "author_email": "developer@example.com",
  "description": "Domain-oriented orders service",
  "architecture_preset": "domain-starter",
  "package_manager": "uv",
  "database": "PostgreSQL",
  "authentication": "JWT",
  "async_tasks": "Celery",
  "caching": "Redis",
  "migrations": "Alembic",
  "tooling": ["ruff", "makefile"],
  "deployment": ["Docker"]
}
```

같은 설정을 TOML 로 쓰면:

```toml
project_name = "orders-api"
author = "Developer Kim"
author_email = "developer@example.com"
description = "Domain-oriented orders service"
architecture_preset = "domain-starter"
package_manager = "uv"
database = "PostgreSQL"
authentication = "JWT"
async_tasks = "Celery"
caching = "Redis"
migrations = "Alembic"
tooling = ["ruff", "makefile"]
deployment = ["Docker"]
```

#### 미리 보기와 단계 건너뛰기

`--dry-run` 은 만들어질 트리와 설치될 패키지를(그리고 어떤 패키지 매니저가
설치할지를) 출력한 뒤, 디스크는 건드리지 않고 종료합니다.

```console
$ fastkit init --config fastkit.config.json --dry-run
```

`--no-install` 은 가상환경까지만 만들고 멈추며, `--no-venv` 는 가상환경도
건너뜁니다(따라서 설치도 하지 않습니다). 컨테이너, CI, 그리고 환경을 fastkit
바깥에서 관리하는 모든 상황에서 유용합니다.

#### 그 자리 배포(in-place)와 덮어쓰기 확인 (`--yes` / `-y`)

프로젝트를 새 프로젝트 폴더가 아니라 지금 작업 중인 워크스페이스에 그
자리에서(in-place) 배포하면, fastkit 은 이미 존재하는 파일을 덮어쓰기 전에
"Overwrite these files?" 확인을 물어봅니다. `--yes`(또는 짧은 형태
`-y`)를 주면 이 확인을 건너뛰고 바로 덮어씁니다. 이는 별도의 "Do you want
to proceed with project creation?" 확인 프롬프트에는 영향을 주지 않으며, 그
질문은 그대로 나옵니다. 표준 입력이 TTY 가 아닌 비대화형 환경(CI 나 파이프
실행 등)에서는 `--yes` 없이도 이 덮어쓰기 확인이 자동으로 생략됩니다.

#### 대화형 프롬프트

`init` 명령은 다음을 묻습니다:

1. **프로젝트 이름**: 디렉터리 이름이자 패키지 이름
2. **작성자 이름**: 패키지 작성자 정보
3. **작성자 이메일**: 패키지 연락 이메일
4. **프로젝트 설명**: 프로젝트에 대한 짧은 설명
5. **스택 선택**: minimal, standard, full 중 선택
6. **패키지 매니저 선택**: pip, uv, pdm, poetry 중 선택 (`--package-manager` 로 지정한 경우는 제외)

#### 스택 옵션

**MINIMAL 스택:**

- `fastapi` - FastAPI 프레임워크
- `uvicorn` - ASGI 서버
- `pydantic` - 데이터 검증
- `pydantic-settings` - 설정 관리

**STANDARD 스택:**

- 모든 MINIMAL 스택 패키지
- `sqlalchemy` - SQL 툴킷 및 ORM
- `alembic` - 데이터베이스 마이그레이션 도구
- `pytest` - 테스트 프레임워크

**FULL 스택:**

- 모든 STANDARD 스택 패키지
- `redis` - 인메모리 데이터 저장소
- `celery` - 분산 작업 큐

#### 대화형 빌더 기능 카탈로그 (`--interactive`)

`fastkit init --interactive` 는 위의 minimal/standard/full 스택과는 별개로,
축(axis) 기반 카탈로그를 순서대로 물어봅니다 (근거: `core/settings.py` 의
`FastkitConfig.PACKAGE_CATALOG`, 그리고 각 선택지가 무엇을 생성하는지는
`DynamicConfigGenerator.build_artifacts()`). 모든 축은 기본값이 `None`(건너뛰기)
이며, `utilities` 와 `tooling` 은 다중 선택입니다.

이제 모든 선택지가 패키지 설치에 그치지 않고 실제 코드를 생성합니다.
`minimal` / `single-module` (main.py 재생성) 과 `classic-layered` /
`domain-starter` (main.py 보존 + 수동 연결 경고) 의 차이는
[아키텍처 프리셋 / 기능 매트릭스](../reference/preset-feature-matrix.md) 를
참고하세요.

| 축 | 선택지 | 설치되는 패키지 | 생성되는 파일 |
|---|---|---|---|
| `database` | PostgreSQL, MySQL, MongoDB, Redis, SQLite, None | PostgreSQL: `asyncpg`, `sqlalchemy` · MySQL: `aiomysql`, `sqlalchemy` · MongoDB: `motor` · Redis: `redis[hiredis]` · SQLite: `sqlalchemy`, `aiosqlite` | 프리셋 경로에 데이터베이스 설정 모듈 (예: `src/config/database.py`) |
| `authentication` | JWT, OAuth2, FastAPI-Users, Session-based, None | JWT: `python-jose[cryptography]`, `passlib[bcrypt]` · OAuth2: `authlib`, `itsdangerous`, `httpx` · FastAPI-Users: `fastapi-users[sqlalchemy]`, `python-jose[cryptography]`, `passlib[bcrypt]` · Session-based: `itsdangerous` | 프리셋 경로에 인증 설정 모듈 생성; OAuth2 · Session-based 는 `main.py` 미들웨어 설정도 추가 |
| `async_tasks` | Celery, Dramatiq, None | Celery: `celery[redis]`, `redis[hiredis]` · Dramatiq: `dramatiq[redis]`, `redis[hiredis]` | `<pkg>/worker.py`(백그라운드 워커) + `<pkg>/features/tasks.py`(작업 라우트) |
| `testing` | Basic, Coverage, Advanced, None | Basic: `pytest`, `pytest-asyncio`, `httpx` · Coverage: + `pytest-cov` · Advanced: + `faker`, `factory-boy` | `pytest.ini`; Advanced 는 `tests/factories.py`, `tests/test_factories.py` 도 추가 |
| `caching` | Redis, None | Redis: `redis[hiredis]`, `fastapi-cache2`, `jinja2` | `<pkg>/features/cache.py`(캐시된 엔드포인트) |
| `monitoring` | Loguru, OpenTelemetry, Prometheus, None | Loguru: `loguru` · OpenTelemetry: `opentelemetry-api`, `opentelemetry-sdk`, `opentelemetry-instrumentation-fastapi`, `opentelemetry-exporter-otlp-proto-http` · Prometheus: `prometheus-client`, `prometheus-fastapi-instrumentator` | 별도 파일 없음 — `main.py` 에 직접 연결(import / lifespan / setup) |
| `utilities` (다중 선택) | CORS, Rate-Limiting, Pagination, WebSocket, None | CORS: 없음(FastAPI 내장) · Rate-Limiting: `slowapi` · Pagination: `fastapi-pagination` · WebSocket: `websockets` | CORS · Rate-Limiting 은 `main.py` 에 직접 연결; Pagination 은 `<pkg>/features/pagination.py`, WebSocket 은 `<pkg>/features/websocket.py` 추가 |
| `migrations` | Alembic, None | Alembic: `alembic` | `alembic.ini`, `alembic/env.py`, `alembic/script.py.mako`, 베이스라인 `alembic/versions/<id>_initial.py`, `scripts/migrate.sh` — 데이터베이스 축이 SQL 데이터베이스일 때만 |
| `tooling` (다중 선택) | ruff, pre-commit, github-actions, devcontainer, makefile, None | ruff: `ruff` · pre-commit: `pre-commit` · github-actions / devcontainer / makefile: 없음 | ruff 는 `pyproject.toml` 에 `[tool.ruff]` 블록 병합(`pip` 프로젝트는 `ruff.toml` 생성); pre-commit 은 `.pre-commit-config.yaml`; github-actions 는 `.github/workflows/test.yml`; devcontainer 는 `.devcontainer/devcontainer.json`; makefile 은 `Makefile` |
| `logging` | structured, None | 없음(표준 라이브러리 `logging` + `json` 만 사용) | `<pkg>/logging_config.py`(구조화 JSON 로깅 + request-id 미들웨어), `main.py` 에 연결 |

선택과 무관하게 모든 생성 프로젝트는 `main.py` 에 `/health`, `/ready`
엔드포인트를 포함하며, `--dry-run` 은 실제로 작성되기 전에 이 파일 목록을
그대로 미리 보여줍니다.

#### 예시

<div class="termy">

```console
$ fastkit init
Enter the project name: my-api
Enter the author name: John Doe
Enter the author email: john@example.com
Enter the project description: My awesome API

Select stack (minimal, standard, full): standard
Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y

✨ FastAPI project 'my-api' has been created successfully!
```

</div>

#### 생성되는 구조

다음 구조의 프로젝트를 생성합니다:

```
my-api/
├── .venv/                    # 가상 환경
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI 애플리케이션
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py        # 설정
│   ├── api/
│   │   ├── __init__.py
│   │   ├── api.py          # API 라우터 모음
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── items.py     # 예제 라우트
│   ├── crud/
│   │   ├── __init__.py
│   │   └── items.py         # CRUD 작업
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── items.py         # Pydantic 스키마
│   └── mocks/
│       ├── __init__.py
│       └── mock_items.json  # 테스트 데이터
├── tests/
├── scripts/
├── requirements.txt
├── setup.py
└── README.md
```

### `addroute`

기존 FastAPI 프로젝트에 새 API 라우트를 추가합니다.

#### 문법

```console
$ fastkit addroute ROUTE_NAME [PROJECT_DIR] [OPTIONS]
```

#### 인자

| 인자 | 설명 | 필수 |
|----------|-------------|----------|
| `ROUTE_NAME` | 새 라우트의 이름 (복수형 권장) | 예 |
| `PROJECT_DIR` | 워크스페이스 내 프로젝트 디렉터리 (기본값 `.`, 즉 현재 디렉터리) | 아니오 |

#### 옵션

| 옵션 | 설명 | 기본값 |
|--------|-------------|---------|
| `--help` | 명령 도움말 표시 | - |

#### 예시

<div class="termy">

```console
$ cd my-api
$ fastkit addroute users
                       Adding New Route
┌──────────────────┬──────────────────────────────────────────┐
│ Project          │ my-api                                   │
│ Route Name       │ users                                    │
│ Target Directory │ ~/my-api                                 │
└──────────────────┴──────────────────────────────────────────┘

Do you want to add route 'users' to project 'my-api'? [Y/n]: y

✨ Successfully added new route 'users' to project 'my-api'
```

</div>

`cd` 하지 않고 워크스페이스 내 프로젝트 이름을 두 번째 인자로 넘겨도 됩니다:

<div class="termy">

```console
$ fastkit addroute users my-api
```

</div>

#### 생성되는 파일

프로젝트에 다음 파일들을 생성합니다:

- `src/api/routes/users.py` - 라우트 핸들러
- `src/crud/users.py` - CRUD 작업
- `src/schemas/users.py` - Pydantic 스키마

또한 `src/api/api.py` 가 갱신되어 새 라우터가 포함됩니다.

#### 생성되는 엔드포인트

전체 CRUD 엔드포인트가 만들어집니다:

| 메서드 | 엔드포인트 | 설명 |
|--------|----------|-------------|
| `GET` | `/api/v1/users/` | 모든 사용자 조회 |
| `POST` | `/api/v1/users/` | 새 사용자 생성 |
| `GET` | `/api/v1/users/{user_id}` | 특정 사용자 조회 |
| `PUT` | `/api/v1/users/{user_id}` | 사용자 갱신 |
| `DELETE` | `/api/v1/users/{user_id}` | 사용자 삭제 |

#### 코드가 삽입되는 위치

`addroute` 가 프로젝트에서 알아야 하는 것은 두 가지입니다. 새 import 를 어디에
넣을지, 그리고 라우터를 어디에 등록할지. 템플릿과 생성된 진입점은 두 지점을
앵커 주석으로 표시해 둡니다.

```python
# src/app/api/router.py
from src.app.api import health

# fastkit:imports

api_router = APIRouter()
api_router.include_router(health.router)

# fastkit:routes
```

이 파일을 직접 수정할 때도 주석은 그대로 두세요 — `addroute` 는
`# fastkit:imports` 와 `# fastkit:routes` 바로 위에 코드를 넣습니다. 주석을
잃어버린 프로젝트(또는 앵커가 생기기 전에 만들어진 프로젝트)도 동작합니다.
fastkit 이 AST 기반 삽입으로 되돌아가 import 블록과 라우터 등록부를 스스로
찾습니다. 앵커는 그 결과를 예측 가능하게 만들어 줄 뿐입니다.

`addroute` 는 진입점을 찾을 때도 프로젝트의 `[tool.fastapi-fastkit]` 블록을
읽으므로, 디스크 스캔만으로는 잘못 고를 수 있는 레이아웃에서도 정확히
동작합니다.

### `startdemo`

사전 구축된 템플릿으로부터 FastAPI 프로젝트를 생성합니다.

#### 문법

```console
$ fastkit startdemo [OPTIONS]
```

#### 옵션

| 옵션 | 설명 | 기본값 |
|--------|-------------|---------|
| `--project-name` | 프로젝트 이름 (생략하면 물어봄) | - |
| `--author` | 작성자 이름 (생략하면 물어봄) | - |
| `--author-email` | 작성자 이메일 (생략하면 물어봄) | - |
| `--description` | 프로젝트 설명 (생략하면 물어봄) | - |
| `--package-manager` | 사용할 패키지 매니저 (pip, uv, pdm, poetry) | uv |
| `--dry-run` | 무엇이 만들어질지만 보여주고 아무것도 쓰지 않음 | 꺼짐 |
| `--no-venv` | 가상환경 생성을 건너뜀 (`--no-install` 포함) | 꺼짐 |
| `--no-install` | 의존성 설치를 건너뜀 | 꺼짐 |
| `--yes` / `-y` | 프로젝트를 그 자리에(in-place) 배포할 때 기존 파일을 덮어쓰기 전에 확인을 묻지 않음 | 꺼짐 |
| `--help` | 명령 도움말 표시 | - |

`init` 과 마찬가지로 `startdemo` 도 대상 프로젝트 디렉터리가 이미 존재하면
실행을 거부합니다(`Error: Project '{name}' already exists.`). 예외는
`--dry-run` 입니다. 디스크에 아무것도 쓰지 않으므로, 이미 디렉터리가 있는
이름을 대상으로 지정해도 여전히 허용됩니다. 워크스페이스에 그 자리에서
배포할 때 `--yes` 가 하는 일은 위의
[그 자리 배포(in-place)와 덮어쓰기 확인](#in-place-yes-y)
절을 참고하세요.

#### 대화형 프롬프트

`startdemo` 명령은 다음을 묻습니다:

1. **프로젝트 이름**: 새 프로젝트의 디렉터리 이름
2. **작성자 이름**: 패키지 작성자 정보
3. **작성자 이메일**: 연락 이메일
4. **프로젝트 설명**: 짧은 설명
5. **패키지 매니저 선택**: pip, uv, pdm, poetry 중 선택 (`--package-manager` 로 지정한 경우는 제외)

#### 사용 가능한 템플릿

| 템플릿 | 설명 | 기능 |
|----------|-------------|----------|
| `fastapi-default` | 간단한 FastAPI 프로젝트 | 기본 CRUD, Mock 데이터 |
| `fastapi-domain-starter` | 도메인 지향 스타터 | 업무 개념별 폴더 분리, `/health` |
| `fastapi-auth-jwt` | JWT 인증 | 액세스/리프레시 회전, argon2id, 역할·스코프, Alembic |
| `fastapi-sqlmodel` | 비동기 SQLModel 영속성 | SQLModel + 비동기 SQLAlchemy, Alembic, 제네릭 CRUD, 페이지네이션 |
| `fastapi-llm-agent` | 스트리밍 Claude 에이전트 | SSE 스트리밍, 도구 호출 루프, 대화 기록 |
| `fastapi-custom-response` | 맞춤형 응답 시스템 | 맞춤형 응답, 페이지네이션 |
| `fastapi-psql-orm` | PostgreSQL용 FastAPI API | PostgreSQL, SQLAlchemy, Alembic |
| `fastapi-mcp` | Model Context Protocol 서버 | MCP 통합 |
| `fastapi-single-module` | 단일 파일 실습용 | 모듈 하나, 패키지 경계 없음 |
| `fastapi-empty` | 최소 구성 FastAPI 프로젝트 | 최소 설정만 포함 |
| `fastapi-async-crud` | *(deprecated)* 비동기 item 관리 API | `fastapi-sqlmodel` 로 대체 |
| `fastapi-dockerized` | *(deprecated)* Docker 기반 FastAPI API | Docker 구성은 이제 모든 최신 템플릿에 포함 |

deprecated 템플릿도 여전히 동작하는 프로젝트를 만들어 냅니다. 다만 새로
시작하는 프로젝트에는 더 이상 권장하지 않습니다.
[어떤 스타터를 고를까?](choosing-a-starter.md) 를 참고하세요.

#### 예시

<div class="termy">

```console
$ fastkit startdemo fastapi-psql-orm
Enter the project name: my-blog
Enter the author name: Jane Smith
Enter the author email: jane@example.com
Enter the project description: Blog API with PostgreSQL

Select package manager (pip, uv, pdm, poetry) [uv]: poetry
Do you want to proceed with project creation? [y/N]: y

✨ FastAPI project 'my-blog' from 'fastapi-psql-orm' has been created!
```

</div>

### `runserver`

FastAPI 개발 서버를 시작합니다.

#### 문법

```console
$ fastkit runserver [OPTIONS]
```

#### 옵션

| 옵션 | 단축 | 설명 | 기본값 |
|--------|-------|-------------|---------|
| `--host` | `-h` | 바인드할 호스트 | `127.0.0.1` |
| `--port` | `-p` | 바인드할 포트 | `8000` |
| `--reload` | `-r` | 자동 리로드 활성화 | `True` |
| `--workers` | `-w` | 워커 수 | `1` |
| `--help` | | 명령 도움말 표시 | - |

#### 예시

<div class="termy">

```console
# 기본 사용법 (기본 설정)
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000

# 커스텀 호스트와 포트
$ fastkit runserver --host 0.0.0.0 --port 8080
INFO:     Uvicorn running on http://0.0.0.0:8080

# 자동 리로드 비활성화
$ fastkit runserver --no-reload
INFO:     Uvicorn running on http://127.0.0.1:8000

# 다중 워커 (프로덕션)
$ fastkit runserver --workers 4
INFO:     Uvicorn running on http://127.0.0.1:8000
```

</div>

#### 요구 사항

- FastAPI 프로젝트 디렉터리 안에서 실행해야 합니다
- 프로젝트가 FastAPI 앱을 제공해야 합니다 — 기록된
  `[tool.fastapi-fastkit].app_module` 이 있으면 그 값을 쓰고, 없으면 트리를
  훑어 `main.py` 를 찾습니다
- 가상 환경이 활성화되어 있어야 합니다

기록된 진입점도 없고 스캔으로도 찾지 못하면 `runserver` 는 `main.py` 를 찾을
수 없다고 알리고 멈춥니다.

### `list-templates`

사용 가능한 모든 FastAPI 프로젝트 템플릿을 나열합니다.

#### 문법

```console
$ fastkit list-templates [OPTIONS]
```

#### 옵션

| 옵션 | 설명 | 기본값 |
|--------|-------------|---------|
| `--help` | 명령 도움말 표시 | - |

#### 예시

<div class="termy">

```console
$ fastkit list-templates
                      Available Templates
┌─────────────────────────┬───────────────────────────────────┐
│ fastapi-custom-response │ Async Item Management API with    │
│                         │ Custom Response System            │
│ fastapi-dockerized      │ Dockerized FastAPI Item           │
│                         │ Management API                    │
│ fastapi-empty           │ No description                    │
│ fastapi-async-crud      │ Async Item Management API Server  │
│ fastapi-psql-orm        │ Dockerized FastAPI Item           │
│                         │ Management API with PostgreSQL    │
│ fastapi-default         │ Simple FastAPI Project            │
└─────────────────────────┴───────────────────────────────────┘
```

</div>

## 프로젝트 메타데이터 (`[tool.fastapi-fastkit]`)

fastkit 이 만든 프로젝트는 자신이 어떻게 만들어졌는지를 스스로의
`pyproject.toml` 에 기록합니다.

```toml
[tool.fastapi-fastkit]
managed = true
version = "1.4.0"
template = "fastapi-domain-starter"
preset = "domain-starter"
package_manager = "uv"
app_module = "src.app.main:app"
features = ["database:PostgreSQL", "authentication:JWT"]
```

| 키 | 의미 |
|---|---|
| `managed` | 항상 `true`. fastkit 이 관리하는 프로젝트임을 표시 |
| `version` | 프로젝트를 생성한 fastkit 버전 |
| `template` | `startdemo` 템플릿, 또는 프리셋의 베이스 템플릿 |
| `preset` | `init --interactive` 아키텍처 프리셋 (그 외에는 생략) |
| `package_manager` | 환경을 구성할 때 사용한 패키지 매니저 |
| `app_module` | uvicorn 진입점 (`module:attr`) |
| `features` | 대화형 선택을 `"<범주>:<선택>"` 형태로 나열한 목록 |

이 블록은 프로젝트 진입점에 대한 단일 진실 원천입니다. `fastkit runserver`
는 디스크를 훑기 전에 여기서 `app_module` 을 읽고, `fastkit addroute` 는 이
값으로 애플리케이션 위치를 찾으며, 생성된 Dockerfile 도 같은 값을 `CMD` 에
씁니다.

블록은 생성 과정의 가장 마지막에 기록됩니다. 패키지 매니저가 의존성을
해결하면서 `pyproject.toml` 을 다시 쓰기 때문에, 그 뒤에 찍어야 하기
때문입니다. 이후 다시 생성해도 블록은 새로 추가되지 않고 교체됩니다. 직접
정리한 레이아웃을 fastkit 에 알려 주는 정식 방법은 `app_module` 값을 손으로
고치는 것입니다.

## 환경 변수

FastAPI-fastkit은 다음 환경 변수를 인식합니다:

| 변수 | 설명 | 기본값 |
|----------|-------------|---------|
| `FASTKIT_CONFIG_DIR` | 설정 디렉터리 | `~/.fastkit` |
| `FASTKIT_TEMPLATES_DIR` | 커스텀 템플릿 디렉터리 | 내장 템플릿 |
| `FASTKIT_LOG_LEVEL` | 로깅 레벨 | `INFO` |
| `FASTKIT_SUBPROCESS_TIMEOUT` | 패키지 매니저 서브프로세스 타임아웃을 초 단위로 일괄 지정 | 작업별 (30 / 120 / 900) |

패키지 매니저 호출은 각각 시간 제한을 두고 실행되므로, 멈춰 버린 자식
프로세스가 CLI 를 영원히 붙잡는 일은 없습니다. 설치 가능 여부 확인 30초,
가상환경 생성 120초, 의존성 설치 900초입니다.
`FASTKIT_SUBPROCESS_TIMEOUT` 은 이 셋을 하나의 값으로 덮어씁니다. 느린
네트워크에서 늘리거나 CI 에서 빨리 실패시키고 싶을 때 쓰면 됩니다. 양의
정수가 아닌 값은 무시합니다.

```console
$ export FASTKIT_SUBPROCESS_TIMEOUT=1800
$ fastkit startdemo fastapi-sqlmodel
```

### 예시

<div class="termy">

```console
# 커스텀 설정 디렉터리
$ export FASTKIT_CONFIG_DIR=~/my-fastkit-config
$ fastkit init

# 커스텀 템플릿 디렉터리
$ export FASTKIT_TEMPLATES_DIR=~/my-templates
$ fastkit list-templates

# 디버그 로깅
$ export FASTKIT_LOG_LEVEL=DEBUG
$ fastkit init
```

</div>

## 설정 파일

FastAPI-fastkit은 기본 설정값을 위한 설정 파일을 사용할 수 있습니다.

### 설정 파일 위치

1. `$FASTKIT_CONFIG_DIR/config.yaml` (`FASTKIT_CONFIG_DIR` 가 설정된 경우)
2. `~/.fastkit/config.yaml` (기본값)
3. `./fastkit.yaml` (프로젝트별)

### 설정 파일 형식

```yaml
# ~/.fastkit/config.yaml
default:
  author:
    name: "Your Name"
    email: "your.email@example.com"

  project:
    stack: "standard"
    create_venv: true
    install_deps: true

  server:
    host: "127.0.0.1"
    port: 8000
    reload: true

templates:
  custom_dir: "~/my-templates"

logging:
  level: "INFO"
  file: "~/.fastkit/logs/fastkit.log"
```

## 자주 쓰는 워크플로

### 1. 새 프로젝트 생성

<div class="termy">

```console
# 새 프로젝트 생성
$ fastkit init
# 프롬프트를 따라 진행...

# 프로젝트로 이동
$ cd my-awesome-api

# 가상 환경 활성화
$ source .venv/bin/activate

# 개발 서버 시작
$ fastkit runserver
```

</div>

### 2. 기존 프로젝트에 기능 추가

<div class="termy">

```console
# 여러 라우트 추가 (두 번째 인자로 워크스페이스 내 프로젝트 이름)
$ fastkit addroute users my-api
$ fastkit addroute products my-api
$ fastkit addroute orders my-api

# API 테스트
$ fastkit runserver
# http://127.0.0.1:8000/docs 접속
```

</div>

### 3. 복잡한 프로젝트에 템플릿 사용

<div class="termy">

```console
# 사용 가능한 템플릿 보기
$ fastkit list-templates

# 템플릿으로부터 생성
$ fastkit startdemo
# 데이터베이스 프로젝트라면 fastapi-psql-orm 선택

# 데이터베이스 설정 (PostgreSQL 템플릿용)
$ cd my-project
$ docker-compose up -d postgres
$ source .venv/bin/activate
$ alembic upgrade head
$ fastkit runserver
```

</div>

## 문제 해결

### 명령을 찾을 수 없을 때

`fastkit` 명령을 찾을 수 없다면:

1. **설치 확인:**
   <div class="termy">
   ```console
   $ pip show fastapi-fastkit
   ```
   </div>

2. **필요하면 재설치:**
   <div class="termy">
   ```console
   $ pip uninstall fastapi-fastkit
   $ pip install fastapi-fastkit
   ```
   </div>

3. **PATH 확인:**
   <div class="termy">
   ```console
   $ which fastkit
   ```
   </div>

### 가상 환경 문제

가상 환경 생성에 실패한다면:

1. **Python 버전 확인:**
   <div class="termy">
   ```console
   $ python --version  # 3.12+ 이어야 합니다
   ```
   </div>

2. **venv 모듈 확인:**
   <div class="termy">
   ```console
   $ python -m venv --help
   ```
   </div>

3. **수동 가상 환경 생성:**
   <div class="termy">
   ```console
   $ python -m venv .venv
   $ source .venv/bin/activate
   $ pip install -r requirements.txt
   ```
   </div>

### 서버가 시작되지 않을 때

`fastkit runserver` 가 실패한다면:

1. **프로젝트 디렉터리에 있는지 확인하세요**
2. **`src/main.py` 가 있는지 검증하세요**
3. **가상 환경을 활성화하세요:**
   <div class="termy">
   ```console
   $ source .venv/bin/activate
   ```
   </div>

4. **문법 오류 확인:**
   <div class="termy">
   ```console
   $ python -c "from src.main import app"
   ```
   </div>

### 포트가 이미 사용 중일 때

8000 번 포트가 사용 중이라면:

<div class="termy">

```console
# 다른 포트 사용
$ fastkit runserver --port 8080

# 또는 기존 프로세스 종료
$ lsof -ti:8000 | xargs kill -9
```

</div>

## 고급 사용법

### 커스텀 템플릿

다음과 같이 커스텀 템플릿을 만들 수 있습니다:

1. **템플릿 디렉터리 생성:**
   ```
   my-template/
   ├── src/
   │   └── main.py-tpl
   ├── requirements.txt-tpl
   └── setup.py-tpl
   ```

2. **환경 변수 설정:**
   <div class="termy">
   ```console
   $ export FASTKIT_TEMPLATES_DIR=~/my-templates
   ```
   </div>

3. **커스텀 템플릿 사용:**
   <div class="termy">
   ```console
   $ fastkit startdemo
   # 커스텀 템플릿이 목록에 나타납니다
   ```
   </div>

### 스크립트에서 FastAPI-fastkit 활용하기

FastAPI-fastkit을 스크립트 안에서 활용할 수도 있습니다:

```bash
#!/bin/bash
# create-microservices.sh

for service in users products orders; do
    echo "Creating $service service..."
    fastkit init <<EOF
$service-service
Company Team
team@company.com
$service microservice
minimal
y
EOF

    cd "$service-service"
    fastkit addroute "$service"
    cd ..
done
```

### CI/CD 통합

GitHub Actions 워크플로 예시:

```yaml
name: Test FastAPI-fastkit Project

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.12'

    - name: Install FastAPI-fastkit
      run: pip install fastapi-fastkit

    - name: Create test project
      run: |
        fastkit init <<EOF
        test-project
        CI
        ci@example.com
        Test project
        standard
        y
        EOF

    - name: Test project
      run: |
        cd test-project
        source .venv/bin/activate
        python -m pytest
```

## 패키지 매니저 지원

FastAPI-fastkit은 여러 Python 패키지 매니저를 지원하므로, 현재 워크플로에 가장 잘 맞는 것을 고를 수 있습니다.

### 지원하는 패키지 매니저

| 매니저 | 설명 | 의존성 파일 | 적합한 경우 |
|---------|-------------|----------------|----------|
| **UV** (기본값) | 빠른 Python 패키지 매니저 | `pyproject.toml` | 속도와 성능 |
| **PDM** | 현대적인 Python 의존성 관리 | `pyproject.toml` | 고급 의존성 해석 |
| **Poetry** | Python 의존성 관리 및 패키징 | `pyproject.toml` | Poetry 기반 워크플로 |
| **PIP** | 표준 Python 패키지 매니저 | `requirements.txt` | 전통적인 Python 개발 |

### 패키지 매니저 지정

#### 전역 설정

모든 프로젝트에 대해 선호 패키지 매니저를 설정할 수 있습니다:

```console
# 커맨드라인 옵션 사용
$ fastkit init --package-manager poetry
$ fastkit startdemo --package-manager pdm
```

#### 프로젝트별 선택

각 프로젝트가 서로 다른 패키지 매니저를 사용할 수 있습니다. 선택은 프로젝트 생성 시점에 이뤄지며 다음에 영향을 줍니다:

- **의존성 파일 형식**: 매니저별로 적절한 파일을 만듭니다
- **가상 환경 관리**: 활성화 방식이 다릅니다
- **의존성 설치**: 매니저별 명령이 다릅니다

### 패키지 매니저 기능

#### UV (기본값)
- **빠름**: Rust 기반, 매우 빠른 의존성 해석
- **호환**: pip 및 pip-tools의 드롭인 대체
- **현대적**: PEP 621 프로젝트 메타데이터 지원

<div class="termy">

```console
$ fastkit init --package-manager uv
# UV 설정이 적용된 pyproject.toml 생성
```

</div>

#### PDM
- **현대적**: PEP 582와 PEP 621 지원
- **고급**: 정교한 의존성 해석
- **유연**: 다양한 프로젝트 레이아웃

<div class="termy">

```console
$ fastkit init --package-manager pdm
# PDM 설정이 적용된 pyproject.toml 생성
```

</div>

#### Poetry
- **검증됨**: 성숙하고 널리 사용됨
- **통합**: 빌드 및 게시 지원
- **Lockfile**: 재현 가능한 빌드를 위한 poetry.lock

<div class="termy">

```console
$ fastkit init --package-manager poetry
# Poetry 설정이 적용된 pyproject.toml 생성
```

</div>

#### PIP
- **표준**: Python에 기본 포함
- **호환**: 어디서나 동작
- **단순**: 직관적인 의존성 관리

<div class="termy">

```console
$ fastkit init --package-manager pip
# requirements.txt 생성
```

</div>

### 프로젝트 작업

특정 패키지 매니저로 프로젝트를 만든 뒤:

#### UV 프로젝트
```console
cd my-project
uv sync          # 의존성 설치
uv add requests  # 새 의존성 추가
uv run pytest   # 환경에서 명령 실행
```

#### PDM 프로젝트
```console
cd my-project
pdm install      # 의존성 설치
pdm add requests # 새 의존성 추가
pdm run pytest  # 환경에서 명령 실행
```

#### Poetry 프로젝트
```console
cd my-project
poetry install      # 의존성 설치
poetry add requests # 새 의존성 추가
poetry run pytest  # 환경에서 명령 실행
```

#### PIP 프로젝트
```console
cd my-project
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
pip install requests
pytest
```

## 다음 단계

이제 CLI를 이해했으니:

1. **[퀵 스타트](quick-start.md)**: 직접 명령들을 실행해 보기
2. **[첫 프로젝트 만들기](../tutorial/first-project.md)**: 완전한 애플리케이션 구축
3. **[기여 안내](../contributing/development-setup.md)**: FastAPI-fastkit에 기여하기

!!! tip "CLI 팁"
    - 어떤 명령에든 `--help` 를 붙이면 자세한 도움말을 볼 수 있습니다
    - 기본 설정값을 미리 구성하면 프로젝트 생성 속도가 빨라집니다
    - 복잡한 프로젝트 설정에는 템플릿을 사용하세요
    - 명령들을 조합하면 강력한 워크플로를 만들 수 있습니다
