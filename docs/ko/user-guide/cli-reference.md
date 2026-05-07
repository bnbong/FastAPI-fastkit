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
| `--package-manager` | 사용할 패키지 매니저 (pip, uv, pdm, poetry) | uv |
| `--help` | 명령 도움말 표시 | - |

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
$ fastkit addroute PROJECT_NAME ROUTE_NAME [OPTIONS]
```

#### 인자

| 인자 | 설명 | 필수 |
|----------|-------------|----------|
| `PROJECT_NAME` | 기존 프로젝트의 이름 | 예 |
| `ROUTE_NAME` | 새 라우트의 이름 (복수형 권장) | 예 |

#### 옵션

| 옵션 | 설명 | 기본값 |
|--------|-------------|---------|
| `--help` | 명령 도움말 표시 | - |

#### 예시

<div class="termy">

```console
$ fastkit addroute my-api users
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

### `startdemo`

사전 구축된 템플릿으로부터 FastAPI 프로젝트를 생성합니다.

#### 문법

```console
$ fastkit startdemo [OPTIONS]
```

#### 옵션

| 옵션 | 설명 | 기본값 |
|--------|-------------|---------|
| `--package-manager` | 사용할 패키지 매니저 (pip, uv, pdm, poetry) | uv |
| `--help` | 명령 도움말 표시 | - |

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
| `fastapi-async-crud` | 비동기 item 관리 API | Async/await, 성능 |
| `fastapi-custom-response` | 맞춤형 응답 시스템 | 맞춤형 응답, 페이지네이션 |
| `fastapi-dockerized` | Docker 기반 FastAPI API | Docker, 프로덕션 준비 |
| `fastapi-psql-orm` | PostgreSQL용 FastAPI API | PostgreSQL, SQLAlchemy, Alembic |
| `fastapi-empty` | 최소 구성 FastAPI 프로젝트 | 최소 설정만 포함 |

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
- 프로젝트에 FastAPI 앱이 있는 `src/main.py` 가 있어야 합니다
- 가상 환경이 활성화되어 있어야 합니다

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

## 환경 변수

FastAPI-fastkit은 다음 환경 변수를 인식합니다:

| 변수 | 설명 | 기본값 |
|----------|-------------|---------|
| `FASTKIT_CONFIG_DIR` | 설정 디렉터리 | `~/.fastkit` |
| `FASTKIT_TEMPLATES_DIR` | 커스텀 템플릿 디렉터리 | 내장 템플릿 |
| `FASTKIT_LOG_LEVEL` | 로깅 레벨 | `INFO` |

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
# 여러 라우트 추가
$ fastkit addroute my-api users
$ fastkit addroute my-api products
$ fastkit addroute my-api orders

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
    fastkit addroute "$service-service" "$service"
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
