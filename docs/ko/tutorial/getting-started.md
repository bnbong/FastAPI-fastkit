# 시작하기

FastAPI-fastkit으로 시작하는 종합 단계별 튜토리얼입니다. 이 가이드는 설치부터 첫 API 실행까지 약 15분 안에 차근차근 안내합니다.

## 사전 요구 사항

시작하기 전에 다음을 갖춰 두세요:

- 시스템에 설치된 **Python 3.12 이상**
- **Python 기초 지식** (변수, 함수, 클래스)
- **터미널 / 커맨드라인** 사용 가능
- **텍스트 에디터 또는 IDE** (VS Code, PyCharm 등)

## 1단계: 설치

먼저 FastAPI-fastkit을 설치합니다. 프로젝트를 분리해서 관리할 수 있도록 가상 환경 사용을 권장합니다.

### 방법 A: pip 사용 (전통적)

<div class="termy">

```console
$ pip install fastapi-fastkit
---> 100%
Successfully installed fastapi-fastkit
```

</div>

### 방법 B: UV 사용 (권장 — 더 빠름)

UV는 빠른 Python 패키지 매니저입니다. 아직 설치하지 않았다면 다음과 같이 진행하세요:

<div class="termy">

```console
# 먼저 UV 설치
$ curl -LsSf https://astral.sh/uv/install.sh | sh

# 이어서 FastAPI-fastkit 설치
$ uv pip install fastapi-fastkit
---> 100%
Successfully installed fastapi-fastkit
```

</div>

### 방법 C: 가상 환경 사용

<div class="termy">

```console
$ python -m venv fastapi-env
$ source fastapi-env/bin/activate  # Windows: fastapi-env\Scripts\activate
$ pip install fastapi-fastkit
```

</div>

### 설치 확인

FastAPI-fastkit이 올바르게 설치됐는지 확인합니다:

<div class="termy">

```console
$ fastkit --version
FastAPI-fastkit version 1.0.0
```

</div>

## 2단계: 첫 프로젝트 생성

이제 대화형 `init` 명령으로 첫 FastAPI 프로젝트를 만듭니다:

<div class="termy">

```console
$ fastkit init
Enter the project name: my-first-api
Enter the author name: Your Name
Enter the author email: your.email@example.com
Enter the project description: My first FastAPI project

           Project Information
┌──────────────┬─────────────────────────┐
│ Project Name │ my-first-api            │
│ Author       │ Your Name               │
│ Author Email │ your.email@example.com  │
│ Description  │ My first FastAPI project│
└──────────────┴─────────────────────────┘

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

Creating virtual environment...
Installing dependencies...
✨ FastAPI project 'my-first-api' has been created successfully!
```

</div>

!!! note "스택 선택"
    이 튜토리얼에서는 단순함을 위해 **MINIMAL** 을 골랐습니다. 실제 프로젝트에서는 **STANDARD** (데이터베이스 지원 포함) 또는 **FULL** (백그라운드 작업 포함) 을 고려하세요.

## 3단계: 프로젝트로 이동

방금 생성한 프로젝트 디렉터리로 이동합니다:

<div class="termy">

```console
$ cd my-first-api
$ ls -la
total 32
drwxr-xr-x  8 user user  256 Dec  7 10:30 .
drwxr-xr-x  3 user user   96 Dec  7 10:30 ..
drwxr-xr-x  5 user user  160 Dec  7 10:30 .venv
-rw-r--r--  1 user user  156 Dec  7 10:30 README.md
-rw-r--r--  1 user user  243 Dec  7 10:30 requirements.txt
drwxr-xr-x  3 user user   96 Dec  7 10:30 scripts
-rw-r--r--  1 user user 1245 Dec  7 10:30 setup.py
drwxr-xr-x  8 user user  256 Dec  7 10:30 src
drwxr-xr-x  3 user user   96 Dec  7 10:30 tests
```

</div>

## 4단계: 가상 환경 활성화

프로젝트에는 미리 구성된 가상 환경이 함께 옵니다. 활성화해 봅시다:

<div class="termy">

```console
$ source .venv/bin/activate  # Windows: .venv\Scripts\activate
(my-first-api) $
```

</div>

이제 터미널 프롬프트가 `(my-first-api)` 로 표시되며, 가상 환경이 활성화됐음을 알려 줍니다.

## 5단계: 개발 서버 시작

이제 FastAPI 서버를 실행해 봅시다:

<div class="termy">

```console
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [28720] using StatReload
INFO:     Started server process [28722]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

</div>

🎉 **축하합니다!** FastAPI 서버가 동작 중입니다.

## 6단계: API 테스트

여러 방법으로 API를 테스트해 봅시다:

### 방법 1: 브라우저

웹 브라우저에서 다음 주소를 열어 보세요:

- **메인 API 엔드포인트**: [http://127.0.0.1:8000](http://127.0.0.1:8000)

다음과 같이 보일 것입니다:
```json
{"message": "Hello World"}
```

### 방법 2: 인터랙티브 API 문서

자동 생성된 API 문서를 열어 봅니다:

- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

특히 Swagger UI 가 유용합니다. 다음을 할 수 있습니다:

- 사용 가능한 모든 엔드포인트 보기  
- 브라우저에서 직접 엔드포인트 테스트  
- 요청 / 응답 스키마 확인  
- OpenAPI 명세 다운로드  

### 방법 3: 커맨드라인

새 터미널을 열고 (서버를 실행하는 터미널은 그대로 두세요) curl 로 테스트합니다:

<div class="termy">

```console
$ curl http://127.0.0.1:8000
{"message":"Hello World"}

$ curl http://127.0.0.1:8000/api/v1/items/
[]

$ curl -X POST "http://127.0.0.1:8000/api/v1/items/" \
     -H "Content-Type: application/json" \
     -d '{"title": "My First Item", "description": "This is a test item"}'
{
  "id": 1,
  "title": "My First Item",
  "description": "This is a test item"
}
```

</div>

## 7단계: 프로젝트 구조 이해

FastAPI-fastkit이 무엇을 생성했는지 살펴봅시다:

<div class="termy">

```console
$ tree src
src/
├── __init__.py
├── main.py                 # FastAPI 애플리케이션 진입점
├── core/
│   ├── __init__.py
│   └── config.py          # 애플리케이션 설정
├── api/
│   ├── __init__.py
│   ├── api.py             # 메인 API 라우터
│   └── routes/
│       ├── __init__.py
│       └── items.py       # Items API 엔드포인트
├── crud/
│   ├── __init__.py
│   └── items.py           # items 의 비즈니스 로직
├── schemas/
│   ├── __init__.py
│   └── items.py           # 데이터 검증 스키마
└── mocks/
    ├── __init__.py
    └── mock_items.json    # 샘플 데이터
```

</div>

### 주요 파일 설명

**`src/main.py`** — 애플리케이션의 핵심:
```python
from fastapi import FastAPI
from src.api.api import api_router
from src.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"message": "Hello World"}
```

**`src/core/config.py`** — 애플리케이션 설정:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "my-first-api"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    class Config:
        env_file = ".env"

settings = Settings()
```

**`src/api/routes/items.py`** — API 엔드포인트:
```python
from typing import List
from fastapi import APIRouter, HTTPException
from src.schemas.items import Item, ItemCreate, ItemUpdate
from src.crud.items import items_crud

router = APIRouter()

@router.get("/", response_model=List[Item])
def read_items():
    """Get all items"""
    return items_crud.get_all()

@router.post("/", response_model=Item)
def create_item(item: ItemCreate):
    """Create a new item"""
    return items_crud.create(item)
```

## 8단계: 첫 커스텀 라우트 추가

배운 내용을 연습할 겸 새 API 라우트를 추가해 봅시다:

<div class="termy">

```console
$ fastkit addroute users my-first-api
                       Adding New Route
┌──────────────────┬──────────────────────────────────────────┐
│ Project          │ my-first-api                             │
│ Route Name       │ users                                    │
│ Target Directory │ ~/my-first-api                           │
└──────────────────┴──────────────────────────────────────────┘

Do you want to add route 'users' to project 'my-first-api'? [Y/n]: y

✨ Successfully added new route 'users' to project 'my-first-api'
```

</div>

서버는 자동으로 재시작되고, 이제 새 엔드포인트들이 생깁니다:

- `GET /api/v1/users/` — 모든 사용자 조회  
- `POST /api/v1/users/` — 새 사용자 생성  
- `GET /api/v1/users/{user_id}` — 특정 사용자 조회  
- 그 외 다수...  

### 새 라우트 테스트

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

$ curl http://127.0.0.1:8000/api/v1/users/
[
  {
    "id": 1,
    "title": "John Doe",
    "description": "Software Developer"
  }
]
```

</div>

## 9단계: 코드 살펴보고 수정하기

코드가 어떻게 동작하는지 이해하기 위해 작은 수정을 해 봅니다.

### 환영 메시지 수정

텍스트 에디터에서 `src/main.py` 를 열고 루트 엔드포인트를 변경합니다:

```python
@app.get("/")
def read_root():
    return {"message": "Welcome to my first FastAPI application!"}
```

파일을 저장합니다. 자동 리로드 덕분에 서버가 자동으로 재시작됩니다.

### 변경 사항 테스트

<div class="termy">

```console
$ curl http://127.0.0.1:8000
{"message":"Welcome to my first FastAPI application!"}
```

</div>

### 새 엔드포인트 추가

`src/main.py` 에 단순한 엔드포인트를 추가해 봅시다:

```python
@app.get("/hello/{name}")
def say_hello(name: str):
    return {"message": f"Hello, {name}!"}
```

### 새 엔드포인트 테스트

<div class="termy">

```console
$ curl http://127.0.0.1:8000/hello/World
{"message":"Hello, World!"}

$ curl http://127.0.0.1:8000/hello/FastAPI
{"message":"Hello, FastAPI!"}
```

</div>

## 10단계: 테스트 실행

프로젝트에는 미리 구성된 테스트가 함께 옵니다. 실행해 봅시다:

<div class="termy">

```console
$ python -m pytest
======================== test session starts ========================
collected 5 items

tests/test_items.py::test_create_item PASSED
tests/test_items.py::test_read_items PASSED
tests/test_items.py::test_read_item PASSED
tests/test_items.py::test_update_item PASSED
tests/test_items.py::test_delete_item PASSED

======================== 5 passed in 0.45s ========================
```

</div>

## 핵심 개념 이해

### 1. FastAPI 애플리케이션 구조

FastAPI-fastkit은 **모듈형 아키텍처**를 따릅니다:

- **`main.py`**: 애플리케이션 진입점과 전역 엔드포인트
- **`api/`**: API 라우트 구성
- **`core/`**: 애플리케이션 구성 및 설정
- **`crud/`**: 비즈니스 로직과 데이터 작업
- **`schemas/`**: 데이터 검증 및 직렬화
- **`tests/`**: 자동화된 테스트

### 2. 의존성 관리

프로젝트는 현대적인 Python 의존성 관리 방식을 사용합니다:

- **가상 환경**: 격리된 Python 환경
- **requirements.txt**: 모든 의존성을 나열
- **자동 설치**: 프로젝트 생성 시 의존성을 자동 설치

### 3. 개발 서버

FastAPI-fastkit은 ASGI 서버로 **Uvicorn**을 사용합니다:

- **자동 리로드**: 코드 변경 시 자동 재시작
- **빠른 시작**: 빠른 개발 반복
- **프로덕션 대비**: 프로덕션에서도 같은 서버 사용

### 4. API 문서화

FastAPI는 자동으로 다음 항목을 생성합니다:

- **OpenAPI 명세**: 업계 표준 API 문서
- **Swagger UI**: 인터랙티브 테스트 인터페이스
- **ReDoc**: 대안 문서 뷰

## 다음 단계

축하합니다! 다음을 성공적으로 마쳤습니다:

✅ FastAPI-fastkit 설치  
✅ 첫 프로젝트 생성  
✅ 개발 서버 시작  
✅ API 엔드포인트 테스트  
✅ 새 라우트 추가  
✅ 기존 코드 수정  
✅ 테스트 실행  

### 학습 이어가기

1. **[첫 프로젝트 만들기](first-project.md)**: 고급 기능을 갖춘 완전한 블로그 API 구축
2. **[라우트 추가](../user-guide/adding-routes.md)**: 복잡한 API 엔드포인트 만드는 법 학습
3. **[템플릿 사용하기](../user-guide/using-templates.md)**: 사전 구축 프로젝트 템플릿 살펴보기

### 더 실험해 보기

다음 도전 과제를 시도해 보세요:

1. **검증 추가**: 스키마를 수정해 데이터 검증 규칙을 추가해 보세요
2. **커스텀 응답**: 라우트의 응답 형식을 바꿔 보세요
3. **환경 변수**: 설정에 `.env` 파일을 사용해 보세요
4. **미들웨어 추가**: CORS 또는 인증을 구현해 보세요
5. **데이터베이스 통합**: 데이터베이스 지원을 위해 STANDARD 스택으로 업그레이드하세요

### 자주 마주치는 문제와 해결

**서버가 시작되지 않을 때:**

- 프로젝트 디렉터리에 있는지 확인  
- 가상 환경이 활성화돼 있는지 확인  
- 코드에 문법 오류가 없는지 검증  

**Import 오류:**

- 모든 `__init__.py` 파일이 존재하는지 확인  
- import 경로가 올바른지 확인  
- 가상 환경을 사용하고 있는지 확인  

**포트가 이미 사용 중일 때:**
```console
$ fastkit runserver --port 8080
```

## 여기서 배운 모범 사례

1. **가상 환경**: 항상 격리된 환경 사용
2. **프로젝트 구조**: 잘 정리된 모듈형 아키텍처 따르기
3. **자동 리로드**: 빠른 반복을 위해 개발 서버 사용
4. **API 문서화**: 자동 문서 생성 활용
5. **테스트**: 개발 중에도 정기적으로 테스트 실행

!!! tip "개발 팁"
    - 코딩 중에는 개발 서버를 켜 두세요
    - API 테스트에는 인터랙티브 문서 (`/docs`) 를 활용하세요
    - 도움이 되는 에러 메시지가 있는지 터미널을 확인하세요
    - 코드를 정기적으로 버전 관리에 커밋하세요

이제 FastAPI-fastkit으로 멋진 API를 만들 준비가 됐습니다! 🚀
