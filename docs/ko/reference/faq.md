# 자주 묻는 질문

FastAPI-fastkit에 대해 자주 묻는 질문과 답변을 모아 둔 페이지입니다.

## 설치와 환경 설정

### Q: 어떤 Python 버전을 지원하나요?

**A:** FastAPI-fastkit은 **Python 3.12 이상**이 필요합니다. 가장 안정적으로 사용하려면 최신 안정 버전의 Python을 권장합니다.

<div class="termy">

```console
$ python --version
Python 3.12.1

$ pip install fastapi-fastkit
```

</div>

### Q: FastAPI-fastkit 은 어떻게 설치하나요?

**A:** `pip`으로 설치할 수 있습니다:

<div class="termy">

```console
# 최신 안정 버전
$ pip install fastapi-fastkit

# GitHub 개발 버전
$ pip install git+https://github.com/bnbong/FastAPI-fastkit.git

# 특정 버전
$ pip install fastapi-fastkit==1.0.0
```

</div>

### Q: 권한 오류로 설치가 실패합니다

**A:** 가상 환경에서 설치하거나 사용자 권한으로 설치해 보세요:

<div class="termy">

```console
# 가상 환경 생성
$ python -m venv fastapi-env
$ source fastapi-env/bin/activate  # Windows: fastapi-env\Scripts\activate

# 가상 환경에 설치
$ pip install fastapi-fastkit

# 또는 현재 사용자에게만 설치
$ pip install --user fastapi-fastkit
```

</div>

### Q: 설치 후 `fastkit` 명령을 찾을 수 없습니다

**A:** 보통 설치 디렉터리가 PATH 에 들어 있지 않아 발생합니다:

<div class="termy">

```console
# 설치됐는지 확인
$ pip show fastapi-fastkit

# 설치 위치 찾기
$ python -c "import fastapi_fastkit; print(fastapi_fastkit.__file__)"

# 직접 실행 시도
$ python -m fastapi_fastkit --version

# 또는 PATH 에 추가 (Linux/macOS)
$ export PATH="$HOME/.local/bin:$PATH"
```

</div>

## 프로젝트 생성

### Q: 어떤 의존성 스택이 있나요?

**A:** FastAPI-fastkit은 세 가지 의존성 스택을 제공합니다:

- **MINIMAL**: FastAPI, Uvicorn, Pydantic, Pydantic-Settings (기본 웹 API)
- **STANDARD**: SQLAlchemy, Alembic, pytest 추가 (데이터베이스 지원)
- **FULL**: Redis, Celery 추가 (백그라운드 작업)

!!! tip "기본 패키지 매니저"
    더 빠른 의존성 설치를 위해 기본 패키지 매니저는 `uv` 입니다. `pip`, `pdm`, `poetry` 도 선택할 수 있습니다.

<div class="termy">

```console
$ fastkit init
# 프로젝트 생성 중에 선호하는 스택을 선택하세요
```

</div>

### Q: 프로젝트 템플릿을 커스터마이즈할 수 있나요?

**A:** 가능합니다! 다음 중 선택할 수 있습니다:

1. **기존 템플릿 사용**: `fastkit startdemo`
2. **커스텀 템플릿 작성**: 기존 템플릿을 복사 후 수정
3. **점진적으로 라우트 추가**: `fastkit addroute`

<div class="termy">

```console
# 사전 구축 템플릿 사용
$ fastkit list-templates
$ fastkit startdemo

# 기존 프로젝트에 라우트 추가
$ fastkit addroute users .          # 현재 디렉터리에 'users' 라우트 추가
$ fastkit addroute users my-project # 'my-project' 에 'users' 라우트 추가
```

</div>

### Q: 특정 이름 형식으로 프로젝트를 어떻게 만드나요?

**A:** 프로젝트 이름은 유효한 Python 식별자여야 합니다:

- ✅ `my-api`, `blog_system`, `UserService`
- ❌ `my api`, `123project`, `project-name!`

<div class="termy">

```console
$ fastkit init
Enter the project name: my_awesome_api  # 유효
Enter the project name: my-awesome-api  # 유효 (하이픈은 언더스코어로 변환됨)
```

</div>

### Q: 프로젝트 생성이 "directory already exists" 로 실패합니다

**A:** 프로젝트 디렉터리가 이미 존재합니다. 다음 중 하나를 선택하세요:

1. **다른 이름 사용**
2. **기존 디렉터리 제거** (안전한 경우에만)
3. **다른 출력 위치 사용**

<div class="termy">

```console
# 디렉터리 존재 여부 확인
$ ls my-project

# 안전하다면 제거 (주의!)
$ rm -rf my-project

# 또는 다른 위치에 생성
$ mkdir projects
$ cd projects
$ fastkit init
```

</div>

### Q: 프로젝트 설정에 대화형 모드는 어떻게 사용하나요?

**A:** `fastkit init --interactive`를 사용하면 단계별로 질문에 답하면서 프로젝트를 구성할 수 있습니다:

<div class="termy">

```console
$ fastkit init --interactive
```

</div>

대화형 모드는 다음 단계를 순서대로 진행합니다:

1. **프로젝트 정보** — 이름, 작성자, 이메일, 설명.
2. **아키텍처 프리셋** — 프로젝트 레이아웃을 선택합니다. 권장 기본값은 `domain-starter`이며, Enter만 누르면 그대로 선택됩니다. 각 프리셋이 만드는 레이아웃과 어떤 기능 조합에서 수동 연결이 필요한지는 [프리셋 / 기능 매트릭스](preset-feature-matrix.md)를 참고하세요.
3. **기능 선택** — 데이터베이스, 인증, 백그라운드 작업, 캐싱, 모니터링, 테스트, 유틸리티, 배포.
4. **패키지 매니저와 추가 패키지** — pip / uv / pdm / poetry 가운데 하나를 고르고, 필요하면 고정 버전으로 추가 패키지를 넣을 수 있습니다.
5. **확인** — 프로젝트가 만들어지기 전에 아키텍처 프리셋을 포함한 모든 선택 사항이 요약 표로 표시됩니다.

대화형 모드에서는 아래 기능 목록에서 원하는 구성을 선택할 수 있습니다:

| 카테고리 | 사용 가능한 옵션 |
|----------|-------------------|
| **아키텍처** | minimal, single-module, classic-layered, **domain-starter** (권장 기본값) |
| **데이터베이스** | PostgreSQL, MySQL, MongoDB, Redis, SQLite |
| **인증** | JWT, OAuth2, FastAPI-Users, Session-based |
| **백그라운드 작업** | Celery, Dramatiq |
| **테스트** | Basic (pytest), Coverage, Advanced (faker, factory-boy 포함) |
| **캐싱** | fastapi-cache2 와 함께 Redis |
| **모니터링** | Loguru, OpenTelemetry, Prometheus |
| **유틸리티** | CORS, Rate-Limiting, Pagination, WebSocket |
| **배포** | Docker, docker-compose 와 자동 생성 설정 |

대화형 모드는 다음을 자동으로 생성합니다:

- 선택한 기능이 반영된 `main.py`
- 코드 생성을 지원하는 옵션을 골랐을 때의 데이터베이스 / 인증 설정 파일 (예: 데이터베이스의 PostgreSQL/MySQL/SQLite/MongoDB, 인증의 JWT/FastAPI-Users). 그 밖의 옵션은 필요한 패키지만 설치합니다
- 선택한 배포 옵션에 맞는 배포 파일 (`Docker` 선택 시 `Dockerfile`, `docker-compose` 선택 시 `docker-compose.yml`)
- 선택한 테스트 옵션에 맞는 테스트 설정 (커버리지 설정은 `Coverage` 또는 `Advanced` 를 선택했을 때만 포함)

### Q: 대화형 모드에서 사용 가능한 기능을 어떻게 볼 수 있나요?

**A:** `list-features` 명령으로 사용 가능한 모든 기능과 패키지를 표시할 수 있습니다:

<div class="termy">

```console
$ fastkit list-features
# 모든 사용 가능한 기능을 카테고리별로 표시
# 각 기능에 연결된 패키지와 함께
```

</div>

각 기능 선택에 따라 어떤 패키지가 설치되는지 파악하는 데 도움이 됩니다.

## 라우트 개발

### Q: 라우트에 인증을 어떻게 추가하나요?

**A:** 인증용 의존성을 만드세요:

```python
# src/api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

def get_current_user(token: str = Depends(security)):
    # Verify token and return user
    if not verify_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return get_user_from_token(token)

# src/api/routes/users.py
@router.get("/me")
def get_current_user_profile(user = Depends(get_current_user)):
    return user
```

### Q: 데이터베이스 모델은 어떻게 추가하나요?

**A:** STANDARD 또는 FULL 스택에서는 SQLAlchemy 모델을 만들 수 있습니다:

```python
# src/models/users.py
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
```

### Q: 요청 데이터 검증은 어떻게 추가하나요?

**A:** 스키마에서 Pydantic 모델을 사용하세요:

```python
# src/schemas/users.py
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

    @validator('username')
    def validate_username(cls, v):
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v
```

### Q: 파일 업로드는 어떻게 처리하나요?

**A:** FastAPI 의 `UploadFile` 을 사용하세요:

```python
from fastapi import UploadFile, File

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()

    # Save file
    with open(f"uploads/{file.filename}", "wb") as f:
        f.write(contents)

    return {"filename": file.filename, "size": len(contents)}
```

## 템플릿

### Q: 어떤 템플릿이 있나요?

**A:** FastAPI-fastkit 은 여러 사전 구축 템플릿을 포함합니다:

<div class="termy">

```console
$ fastkit list-templates
                      Available Templates
┌─────────────────────────┬───────────────────────────────────┐
│ fastapi-default         │ Simple FastAPI Project            │
│ fastapi-async-crud      │ Async Item Management API Server  │
│ fastapi-custom-response │ Custom Response System            │
│ fastapi-dockerized      │ Dockerized FastAPI API            │
│ fastapi-empty           │ Minimal FastAPI Project           │
│ fastapi-mcp             │ MCP (Model Context Protocol) API  │
│ fastapi-psql-orm        │ PostgreSQL FastAPI API            │
│ fastapi-single-module   │ Single-file FastAPI Project       │
└─────────────────────────┴───────────────────────────────────┘
```

</div>

### Q: 특정 템플릿은 어떻게 사용하나요?

**A:** `startdemo` 명령을 사용하세요:

<div class="termy">

```console
$ fastkit startdemo
Enter the project name: my-blog
Select template: fastapi-psql-orm
```

</div>

### Q: 직접 템플릿을 만들 수 있나요?

**A:** 가능합니다! 디렉터리 구조를 만들고 템플릿 변수를 사용하세요:

```
my-template/
├── src/
│   └── main.py-tpl
├── requirements.txt-tpl
└── template.yaml
```

```python
# main.py-tpl
from fastapi import FastAPI

app = FastAPI(title="{{PROJECT_NAME}}")

@app.get("/")
def read_root():
    return {"message": "Hello from {{PROJECT_NAME}}!"}
```

### Q: 기존 템플릿은 어떻게 수정하나요?

**A:** 템플릿은 `fastapi_project_template` 디렉터리에 있습니다. 다음과 같이 할 수 있습니다:

1. **저장소를 fork** 해서 템플릿 수정
2. 기존 템플릿을 기반으로 **커스텀 템플릿 작성**
3. 프로젝트 생성 후 **특정 파일만 덮어쓰기**

## 개발 서버

### Q: 개발 서버는 어떻게 시작하나요?

**A:** 프로젝트 디렉터리에서 `runserver` 명령을 사용하세요:

<div class="termy">

```console
$ cd my-project
$ source .venv/bin/activate  # 가상 환경 활성화
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000
```

</div>

### Q: 서버가 시작되지 않습니다 — "Address already in use"

**A:** 8000 번 포트가 사용 중입니다. 다른 포트를 쓰거나 기존 프로세스를 종료하세요:

<div class="termy">

```console
# 다른 포트 사용
$ fastkit runserver --port 8080

# 또는 기존 프로세스 찾아서 종료
$ lsof -ti:8000 | xargs kill -9

# Windows
$ netstat -ano | findstr :8000
$ taskkill /PID <PID> /F
```

</div>

### Q: 자동 리로드가 동작하지 않습니다

**A:** 프로젝트 디렉터리에 있고 가상 환경이 활성화돼 있는지 확인하세요:

<div class="termy">

```console
# 현재 디렉터리 확인
$ pwd
/path/to/my-project

# 가상 환경 확인
$ which python
/path/to/my-project/.venv/bin/python

# 명시적 reload 옵션으로 시작
$ fastkit runserver --reload
```

</div>

### Q: 프로덕션 환경에서는 서버를 어떻게 구성하나요?

**A:** 프로덕션에서는 개발 서버를 사용하지 마세요. 대신:

```python
# gunicorn 이나 비슷한 WSGI 서버 사용
$ pip install gunicorn
$ gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker

# 또는 fastapi-dockerized 템플릿으로 Docker 사용
$ fastkit startdemo  # fastapi-dockerized 선택
$ docker build -t my-app .
$ docker run -p 8000:8000 my-app
```

## 성능과 최적화

### Q: API 성능은 어떻게 개선하나요?

**A:** 다양한 최적화 전략이 있습니다:

1. I/O 작업에 **async/await 사용**
2. 비싼 작업에 **캐싱 추가**
3. **데이터베이스 쿼리 최적화**
4. 무거운 처리에 **백그라운드 작업 사용**

```python
# 비동기 엔드포인트
@router.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await users_service.get_user_async(user_id)
    return user

# 백그라운드 작업
from fastapi import BackgroundTasks

@router.post("/send-email")
def send_email(background_tasks: BackgroundTasks, email: str):
    background_tasks.add_task(send_notification_email, email)
    return {"message": "Email will be sent in background"}
```

### Q: 캐싱은 어떻게 추가하나요?

**A:** 캐싱에 Redis 를 사용하세요:

```python
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expiration: int = 300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"

            # 캐시에서 가져오기 시도
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # 함수 실행 및 결과 캐싱
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            return result
        return wrapper
    return decorator

@cache_result(expiration=600)
async def get_expensive_data():
    # 비싼 작업
    return complex_calculation()
```

### Q: 동시 요청이 많을 때는 어떻게 처리하나요?

**A:** 적절한 서버 설정을 사용하세요:

<div class="termy">

```console
# 개발
$ fastkit runserver --workers 1  # 개발용 단일 워커

# 프로덕션
$ gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker
$ uvicorn src.main:app --workers 4 --host 0.0.0.0 --port 8000
```

</div>

## 테스트

### Q: 테스트는 어떻게 실행하나요?

**A:** 프로젝트 디렉터리에서 pytest 를 사용하세요:

<div class="termy">

```console
$ cd my-project
$ source .venv/bin/activate
$ python -m pytest

# 커버리지 포함
$ python -m pytest --cov=src

# 특정 테스트 파일만
$ python -m pytest tests/test_users.py

# verbose 출력
$ python -m pytest -v
```

</div>

### Q: API 테스트는 어떻게 작성하나요?

**A:** FastAPI 의 테스트 클라이언트를 사용하세요:

```python
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_create_user():
    response = client.post(
        "/api/v1/users/",
        json={"email": "test@example.com", "username": "testuser"}
    )
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

def test_get_user():
    response = client.get("/api/v1/users/1")
    assert response.status_code == 200
```

### Q: 외부 의존성은 어떻게 모킹하나요?

**A:** pytest 픽스처와 mocking 을 사용하세요:

```python
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def mock_database():
    with patch('src.database.get_db') as mock_db:
        mock_db.return_value = Mock()
        yield mock_db

def test_user_creation_with_mock_db(mock_database):
    # 모킹된 데이터베이스로 테스트
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 201
```

## 기여

### Q: FastAPI-fastkit에는 어떻게 기여하나요?

**A:** 다음 단계를 따르세요:

1. GitHub에서 **저장소를 포크**
2. **개발 환경 설정**
3. **기능 브랜치 생성**
4. 테스트와 함께 **변경 사항 작성**
5. **Pull Request 제출**

<div class="termy">

```console
$ git clone https://github.com/yourusername/FastAPI-fastkit.git
$ cd FastAPI-fastkit
$ make dev-setup  # 개발 환경 설정
$ git checkout -b feature/my-feature
# 변경 사항 작성...
$ make dev-check  # 포맷, 린트, 테스트
$ git commit -m "feat: add new feature"
$ git push origin feature/my-feature
```

</div>

### Q: Pull Request에는 무엇을 포함해야 하나요?

**A:** 모든 Pull Request에는 다음 내용이 포함되어야 합니다:

- [ ] 변경 사항에 대한 **명확한 설명**
- [ ] 새 기능에 대한 **테스트**
- [ ] 필요하다면 **문서 업데이트**
- [ ] **코드 가이드라인 준수**
- [ ] **모든 검사 통과**

### Q: 버그는 어떻게 신고하나요?

**A:** GitHub에 아래 정보를 포함한 이슈를 작성하세요:

1. **버그 설명**과 기대 동작
2. **재현 단계**
3. **환경 정보** (OS, Python 버전 등)
4. **에러 메시지**나 로그
5. 가능하면 **최소 재현 예제**

### Q: 새 기능은 어떻게 요청하나요?

**A:** 다음 정보를 포함한 기능 요청 이슈를 여세요:

1. 기능에 대한 **명확한 설명**
2. **사용 사례**와 동기
3. **제안하는 구현 방식** (선택)
4. 비슷한 기능의 **예시**

## 문제 해결

### Q: import 오류가 발생합니다

**A:** Python 경로와 가상 환경을 확인하세요:

<div class="termy">

```console
# 가상 환경이 활성화됐는지 확인
$ which python
/path/to/project/.venv/bin/python

# Python 경로 확인
$ python -c "import sys; print(sys.path)"

# editable 모드로 재설치 (개발용)
$ pip install -e .
```

</div>

### Q: 데이터베이스 연결 문제

**A:** 데이터베이스 템플릿에서는 데이터베이스가 실행 중인지 확인하세요:

<div class="termy">

```console
# PostgreSQL 템플릿
$ docker-compose up -d postgres  # 데이터베이스 시작
$ alembic upgrade head            # 마이그레이션 실행

# 연결 확인
$ docker-compose logs postgres
```

</div>

### Q: 템플릿 파일을 찾을 수 없습니다

**A:** 보통 템플릿 경로 문제입니다:

<div class="termy">

```console
# 사용 가능한 템플릿 확인
$ fastkit list-templates

# 템플릿 디렉터리 확인
$ python -c "import fastapi_fastkit; print(fastapi_fastkit.__path__)"

# 템플릿이 없으면 재설치
$ pip uninstall fastapi-fastkit
$ pip install fastapi-fastkit
```

</div>

### Q: pre-commit 훅이 실패합니다

**A:** 훅을 설치하고 실행하세요:

<div class="termy">

```console
$ pip install pre-commit
$ pre-commit install
$ pre-commit run --all-files

# 포맷팅 문제 수정
$ black src/ tests/
$ isort src/ tests/
```

</div>

### Q: CI 에서는 테스트가 실패하지만 로컬에서는 통과합니다

**A:** 흔한 원인과 해결책:

1. **환경 차이**: Python 버전이 일치하는지 확인
2. **누락된 의존성**: 테스트 요구 사항이 설치됐는지 확인
3. **경로 문제**: 절대 경로 import 사용
4. **타이밍 문제**: 비동기 테스트에 적절한 대기 추가

<div class="termy">

```console
# CI와 같은 Python 버전으로 테스트
$ python3.12 -m pytest

# 누락된 의존성 확인
$ pip install -r requirements-dev.txt

# 격리된 환경에서 테스트 실행
$ tox
```

</div>

## 도움 받기

### Q: 도움은 어디서 받을 수 있나요?

**A:** 도움을 받을 수 있는 여러 경로가 있습니다:

- **GitHub Issues**: 버그와 기능 요청
- **GitHub Discussions**: 질문과 커뮤니티 지원
- **문서**: 사용 가이드와 튜토리얼
- **코드 예제**: 기존 템플릿과 테스트 참고

### Q: 업데이트 소식은 어떻게 받나요?

**A:** 프로젝트 업데이트를 따라가세요:

- GitHub에서 **저장소 watch**
- 새 기능 확인을 위해 **릴리스 확인**
- 호환성 깨짐 변경에 대해서는 **영문 changelog 확인**
- 문서의 **모범 사례 따르기**

!!! tip "Pro Tips"
    - Python 프로젝트에는 항상 가상 환경을 사용하세요
    - FastAPI-fastkit 설치를 최신으로 유지하세요
    - 사용 가능한 명령은 `fastkit --help` 로 확인하세요
    - 막히면 문서를 확인하세요
    - GitHub Discussions에서 자유롭게 질문하세요
