# 템플릿 사용

FastAPI-fastkit은 다양한 기술 스택으로 빠르게 시작할 수 있도록 사전 구성된 프로젝트 템플릿을 제공합니다.

## 사용 가능한 템플릿

`list-templates` 명령으로 사용 가능한 템플릿을 확인하세요:

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

## 템플릿 설명

### 1. `fastapi-default`

**단순한 FastAPI 프로젝트**

- 핵심 기능을 갖춘 기본 FastAPI 셋업
- 목 데이터 기반 item 관리
- 학습용이나 간단한 API에 적합
- 기본 CRUD 작업 포함

**적합한 경우:**

- FastAPI 초보자
- 단순한 웹 API
- 학습 및 프로토타이핑

### 2. `fastapi-async-crud`

**비동기 item 관리용 API 서버**

- 완전 비동기 FastAPI 애플리케이션
- async/await 기반의 고급 CRUD 작업
- I/O 작업에서 더 좋은 성능
- 비동기 패턴의 목 데이터 저장

**적합한 경우:**

- 고성능 애플리케이션
- I/O 집약적 작업
- 모던 비동기 Python 개발

### 3. `fastapi-custom-response`

**맞춤형 응답 시스템을 갖춘 비동기 item 관리 API**

- 커스텀 응답 모델과 포매팅
- 고급 에러 처리
- 페이지네이션 지원
- 커스텀 HTTP 상태 코드와 응답

**적합한 경우:**

- 특정 응답 형식이 요구되는 API
- 고급 에러 처리가 필요한 경우
- 응답에 커스텀 비즈니스 로직이 필요한 경우

### 4. `fastapi-dockerized`

**Docker 기반 FastAPI item 관리 API**

- 완전한 Docker 컨테이너화
- 실서비스 배포에 가까운 구성
- 멀티 스테이지 Docker 빌드
- 환경 기반 설정

**적합한 경우:**

- 프로덕션 배포
- 컨테이너화된 환경
- DevOps 및 CI/CD 파이프라인

### 5. `fastapi-psql-orm`

**PostgreSQL을 사용하는 Docker 기반 FastAPI item 관리 API**

- PostgreSQL 데이터베이스 통합
- SQLAlchemy ORM 과 Alembic 마이그레이션
- 로컬 개발용 Docker Compose
- 완전한 데이터베이스 CRUD 작업

**적합한 경우:**

- 데이터베이스 기반 애플리케이션
- 프로덕션 수준의 데이터 저장
- 복잡한 데이터 관계

### 6. `fastapi-empty`

**최소 FastAPI 프로젝트**

- 최소한의 FastAPI 셋업
- 사전 구축된 기능 없음
- 커스텀 개발을 위한 빈 캔버스

**적합한 경우:**

- 처음부터 직접 시작하기
- 의존성을 최소화하고 싶을 때
- 커스텀 아키텍처 요구 사항

## 템플릿으로 프로젝트 생성

`startdemo` 명령으로 템플릿에서 프로젝트를 생성합니다:

<div class="termy">

```console
$ fastkit startdemo
Enter the project name: my-blog-api
Enter the author name: John Doe
Enter the author email: john@example.com
Enter the project description: Blog API with PostgreSQL

Available Templates:
           fastapi-default
┌─────────────┬──────────────────────┐
│ Description │ Simple FastAPI       │
│             │ Project              │
│ Stack       │ FastAPI, Uvicorn     │
│ Database    │ Mock Data            │
│ Features    │ Basic CRUD           │
└─────────────┴──────────────────────┘

           fastapi-psql-orm
┌─────────────┬──────────────────────┐
│ Description │ Dockerized FastAPI   │
│             │ Item Management API  │
│             │ with PostgreSQL      │
│ Stack       │ FastAPI, PostgreSQL, │
│             │ SQLAlchemy, Docker   │
│ Database    │ PostgreSQL           │
│ Features    │ Full ORM, Migrations │
└─────────────┴──────────────────────┘

Select template (fastapi-default, fastapi-async-crud, fastapi-custom-response, fastapi-dockerized, fastapi-psql-orm, fastapi-empty): fastapi-psql-orm

           Project Information
┌──────────────┬─────────────────────┐
│ Project Name │ my-blog-api         │
│ Author       │ John Doe            │
│ Author Email │ john@example.com    │
│ Description  │ Blog API with       │
│              │ PostgreSQL          │
└──────────────┴─────────────────────┘

       Template Dependencies
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ sqlalchemy        │
│ Dependency 4 │ alembic           │
│ Dependency 5 │ psycopg2-binary   │
│ Dependency 6 │ python-dotenv     │
│ Dependency 7 │ pytest            │
└──────────────┴───────────────────┘

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

✨ FastAPI project 'my-blog-api' from 'fastapi-psql-orm' has been created successfully!
```

</div>

## 템플릿 기능 비교

| 기능 | Default | Async CRUD | Custom Response | Dockerized | PostgreSQL ORM | Empty |
|---|---|---|---|---|---|---|
| **기본 FastAPI** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **목 데이터** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **비동기 지원** | 기본 | ✅ | ✅ | ✅ | ✅ | ❌ |
| **커스텀 응답** | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Docker** | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ |
| **데이터베이스** | Mock | Mock | Mock | Mock | PostgreSQL | None |
| **ORM** | ❌ | ❌ | ❌ | ❌ | SQLAlchemy | ❌ |
| **마이그레이션** | ❌ | ❌ | ❌ | ❌ | Alembic | ❌ |
| **테스트** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **적합한 경우** | 학습 | 성능 | 커스텀 API | 프로덕션 | DB 앱 | 커스텀 |

## 템플릿별 셋업

### `fastapi-psql-orm` 사용

이 템플릿은 완전한 PostgreSQL 셋업을 포함합니다. 생성 후:

1. **Docker로 PostgreSQL 시작:**

<div class="termy">

```console
$ cd my-blog-api
$ docker-compose up -d postgres
Starting my-blog-api_postgres_1 ... done
```

</div>

2. **데이터베이스 마이그레이션 실행:**

<div class="termy">

```console
$ source .venv/bin/activate
$ alembic upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade -> bedcdc35b64a, first alembic
```

</div>

3. **API 서버 시작:**

<div class="termy">

```console
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000
```

</div>

### `fastapi-dockerized` 사용

이 템플릿은 완전한 Docker 지원을 제공합니다:

1. **Docker 이미지 빌드:**

<div class="termy">

```console
$ cd my-dockerized-api
$ docker build -t my-dockerized-api .
Successfully built abc123def456
Successfully tagged my-dockerized-api:latest
```

</div>

2. **컨테이너 실행:**

<div class="termy">

```console
$ docker run -p 8000:8000 my-dockerized-api
INFO:     Uvicorn running on http://0.0.0.0:8000
```

</div>

### `fastapi-custom-response` 사용

이 템플릿은 고급 응답 처리를 포함합니다:

1. **커스텀 응답 모델:**

```python
from src.helper.pagination import PaginatedResponse
from src.schemas.base import StandardResponse

@router.get("/", response_model=PaginatedResponse[Item])
def read_items(skip: int = 0, limit: int = 10):
    items = items_crud.get_multi(skip=skip, limit=limit)
    total = items_crud.count()

    return PaginatedResponse(
        data=items,
        total=total,
        page=skip // limit + 1,
        pages=(total + limit - 1) // limit
    )

@router.post("/", response_model=StandardResponse[Item])
def create_item(item: ItemCreate):
    new_item = items_crud.create(item)
    return StandardResponse(
        data=new_item,
        message="Item created successfully",
        status_code=201
    )
```

2. **개선된 에러 처리:**

```python
from src.helper.exceptions import ItemNotFoundError, ValidationError

@router.get("/{item_id}", response_model=StandardResponse[Item])
def read_item(item_id: int):
    try:
        item = items_crud.get(item_id)
        return StandardResponse(data=item)
    except ItemNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Item with id {item_id} not found"
        )
```

## 템플릿 프로젝트 구조

각 템플릿은 일관되면서도 용도에 맞게 커스터마이즈된 구조를 따릅니다:

### `fastapi-default` 구조
```
my-project/
├── src/
│   ├── main.py
│   ├── core/config.py
│   ├── api/
│   │   ├── api.py
│   │   └── routes/items.py
│   ├── crud/items.py
│   ├── schemas/items.py
│   └── mocks/mock_items.json
├── tests/
├── scripts/
└── requirements.txt
```

### `fastapi-psql-orm` 구조
```
my-project/
├── src/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   └── db.py
│   ├── api/
│   │   ├── api.py
│   │   ├── deps.py
│   │   └── routes/items.py
│   ├── crud/items.py
│   ├── schemas/items.py
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   └── utils/
├── tests/
├── scripts/
├── docker-compose.yml
├── Dockerfile
├── alembic.ini
└── requirements.txt
```

## 템플릿 커스터마이즈

템플릿으로 프로젝트를 생성한 후, 자유롭게 커스터마이즈할 수 있습니다:

### 1. 새 라우트 추가

<div class="termy">

```console
$ fastkit addroute my-blog-api posts
$ fastkit addroute my-blog-api users
$ fastkit addroute my-blog-api comments
```

</div>

### 2. 설정 수정

`src/core/config.py` 를 필요에 맞게 수정하세요:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "My Blog API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # 데이터베이스 설정 (PostgreSQL 템플릿용)
    DATABASE_URL: str = "postgresql://user:password@localhost/dbname"

    # 보안 설정
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
```

### 3. 환경 변수 추가

프로젝트 루트에 `.env` 파일을 만드세요:

```env
# .env
PROJECT_NAME=My Blog API
VERSION=1.0.0
DEBUG=True

# 데이터베이스 (PostgreSQL 템플릿용)
DATABASE_URL=postgresql://user:password@localhost:5432/myblogdb
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=myblogdb

# 보안
SECRET_KEY=your-super-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 템플릿 테스트

각 템플릿은 사전 구성된 테스트와 함께 제공됩니다:

<div class="termy">

```console
$ cd my-blog-api
$ source .venv/bin/activate
$ python -m pytest

======================== test session starts ========================
tests/test_items.py::test_create_item PASSED
tests/test_items.py::test_read_items PASSED
tests/test_items.py::test_read_item PASSED
tests/test_items.py::test_update_item PASSED
tests/test_items.py::test_delete_item PASSED
======================== 5 passed in 0.23s ========================
```

</div>

## 템플릿 개발 워크플로

### 1. 적합한 템플릿 선택

- **학습 / 단순 API**: `fastapi-default`
- **고성능**: `fastapi-async-crud`
- **커스텀 응답 형식**: `fastapi-custom-response`
- **프로덕션 배포**: `fastapi-dockerized`
- **데이터베이스 애플리케이션**: `fastapi-psql-orm`
- **커스텀 아키텍처**: `fastapi-empty`

### 2. 생성 및 셋업

<div class="termy">

```console
$ fastkit startdemo
# 프롬프트를 따라 진행
$ cd your-project
$ source .venv/bin/activate
```

</div>

### 3. 개발

<div class="termy">

```console
# 개발 서버 시작
$ fastkit runserver

# 테스트 실행
$ python -m pytest

# 새 기능 추가
$ fastkit addroute your-project new-resource
```

</div>

### 4. 배포

프로덕션 템플릿(`fastapi-dockerized`, `fastapi-psql-orm`) 의 경우:

<div class="termy">

```console
# 프로덕션용 빌드
$ docker build -t your-app .

# Docker Compose 로 배포
$ docker-compose up -d
```

</div>

## 모범 사례

### 1. 템플릿을 신중히 선택

- 학습용으로는 더 간단한 템플릿부터 시작하세요
- 데이터 기반 앱에는 데이터베이스 템플릿을 사용하세요
- 프로덕션 배포에는 Docker 템플릿을 사용하세요

### 2. 환경 관리

- 설정에는 항상 `.env` 파일을 사용하세요
- 민감한 데이터를 버전 관리에 절대 커밋하지 마세요
- 개발/프로덕션 환경을 분리해서 사용하세요

### 3. 커스터마이즈 전략

- 새 라우트는 `fastkit addroute` 로 추가하세요
- 비즈니스 로직에 맞게 기존 코드를 수정하세요
- 프로젝트 구조를 정돈된 상태로 유지하세요

### 4. 테스트

- 개발 중에 정기적으로 테스트를 실행하세요
- 새로 추가한 기능에 대한 테스트도 작성하세요
- 제공된 테스트 구조를 가이드로 활용하세요

## 문제 해결

### 데이터베이스 연결 문제 (PostgreSQL 템플릿)

PostgreSQL에 연결할 수 없는 경우:

1. **Docker가 실행 중인지 확인:**

   <div class="termy">
   ```console
   $ docker ps
   ```
   </div>

2. **PostgreSQL 컨테이너 상태 확인:**

   <div class="termy">
   ```console
   $ docker-compose logs postgres
   ```
   </div>

3. **환경 변수 확인:**

   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/dbname
   ```

### Docker 빌드 실패

Docker 빌드가 실패하는 경우:

1. **Dockerfile 문법 확인**
2. **모든 파일이 존재하는지 확인**
3. **Docker 데몬이 실행 중인지 확인**

### 의존성 누락

import 오류가 발생하는 경우:

1. **가상 환경 활성화:**
   <div class="termy">
   ```console
   $ source .venv/bin/activate
   ```
   </div>

2. **의존성 설치:**
   <div class="termy">
   ```console
   $ pip install -r requirements.txt
   ```
   </div>

## 다음 단계

이제 템플릿을 이해했다면:

1. **[첫 프로젝트 만들기](../tutorial/first-project.md)**: 완전한 애플리케이션 구축
2. **[라우트 추가](adding-routes.md)**: 템플릿 기반 프로젝트 확장
3. **[CLI 레퍼런스](cli-reference.md)**: 모든 명령어 익히기

!!! tip "템플릿 팁"
    - 템플릿은 훌륭한 출발점이지 최종 솔루션이 아닙니다
    - 템플릿을 자신의 요구 사항에 맞게 커스터마이즈하세요
    - 템플릿 코드를 학습해 FastAPI 모범 사례를 익히세요
    - 커스터마이즈 내역을 추적할 수 있도록 버전 관리를 사용하세요
