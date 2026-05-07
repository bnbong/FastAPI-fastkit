# 기본 API 서버 구축

FastAPI-fastkit으로 간단한 REST API 서버를 빠르게 만드는 방법을 배웁니다. 이 튜토리얼은 FastAPI 입문자에게 적합하며, 기본 CRUD API를 직접 만들어 보는 과정을 다룹니다.

## 이 튜토리얼에서 배우는 내용

- `fastkit startdemo` 명령으로 기본 API 서버 만들기
- FastAPI 프로젝트 구조 이해
- 기본 CRUD 엔드포인트 사용
- API 테스트와 문서화
- 프로젝트 확장 방법

## 사전 요구 사항

- Python 3.12 이상 설치
- FastAPI-fastkit 설치 (`pip install fastapi-fastkit`)
- Python 기초 지식

## 1단계: 기본 API 프로젝트 생성

`fastapi-default` 템플릿으로 기본 API 서버를 만들어 봅시다.

<div class="termy">

```console
$ fastkit startdemo fastapi-default
Enter the project name: my-first-api
Enter the author name: Developer Kim
Enter the author email: developer@example.com
Enter the project description: My first FastAPI server
Deploying FastAPI project using 'fastapi-default' template

           Project Information
┌──────────────┬────────────────────────────┐
│ Project Name │ my-first-api               │
│ Author       │ Developer Kim              │
│ Author Email │ developer@example.com      │
│ Description  │ My first FastAPI server    │
└──────────────┴────────────────────────────┘

       Template Dependencies
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ pydantic          │
│ Dependency 4 │ pydantic-settings │
│ Dependency 5 │ python-dotenv     │
└──────────────┴───────────────────┘

Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y

✨ FastAPI project 'my-first-api' from 'fastapi-default' has been created successfully!
```

</div>

## 2단계: 생성된 프로젝트 구조 이해

생성된 프로젝트 구조를 살펴봅시다:

```
my-first-api/
├── README.md                 # 프로젝트 문서
├── requirements.txt          # 의존성 패키지 목록
├── setup.py                  # 패키지 구성
├── scripts/
│   └── run-server.sh        # 서버 실행 스크립트
├── src/                     # 메인 소스 코드
│   ├── main.py              # FastAPI 애플리케이션 진입점
│   ├── core/
│   │   └── config.py        # 설정 관리
│   ├── api/
│   │   ├── api.py           # API 라우터 모음
│   │   └── routes/
│   │       └── items.py     # item 관련 엔드포인트
│   ├── schemas/
│   │   └── items.py         # 데이터 모델 정의
│   ├── crud/
│   │   └── items.py         # 데이터 처리 로직
│   └── mocks/
│       └── mock_items.json  # 테스트 데이터
└── tests/                   # 테스트 코드
    ├── __init__.py
    ├── conftest.py
    └── test_items.py
```

### 주요 파일 설명

- **`src/main.py`**: FastAPI 애플리케이션 진입점
- **`src/api/routes/items.py`**: item 관련 API 엔드포인트 정의
- **`src/schemas/items.py`**: 요청 / 응답 데이터 구조 정의
- **`src/crud/items.py`**: 데이터베이스 작업 로직
- **`src/mocks/mock_items.json`**: 개발용 샘플 데이터

## 3단계: 서버 실행

생성된 프로젝트 디렉터리로 이동해 서버를 실행합니다.

<div class="termy">

```console
$ cd my-first-api
$ fastkit runserver
Starting FastAPI server at 127.0.0.1:8000...

INFO:     Will watch for changes in these directories: ['/path/to/my-first-api']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

</div>

서버가 정상적으로 실행되면 브라우저에서 다음 URL 들에 접속할 수 있습니다:

- **API 서버**: http://127.0.0.1:8000
- **Swagger UI 문서**: http://127.0.0.1:8000/docs
- **ReDoc 문서**: http://127.0.0.1:8000/redoc

## 4단계: API 엔드포인트 살펴보기

생성된 API는 기본적으로 다음 엔드포인트를 제공합니다:

| 메서드 | 엔드포인트 | 설명 |
|--------|----------|-------------|
| GET | `/items/` | 모든 item 조회 |
| GET | `/items/{item_id}` | 특정 item 조회 |
| POST | `/items/` | 새 item 생성 |
| PUT | `/items/{item_id}` | item 갱신 |
| DELETE | `/items/{item_id}` | item 삭제 |

### API 테스트

**1. 모든 item 조회**

<div class="termy">

```console
$ curl -X GET "http://127.0.0.1:8000/items/"
[
  {
    "id": 1,
    "name": "Laptop",
    "description": "High-performance laptop",
    "price": 999.99,
    "tax": 99.99
  },
  {
    "id": 2,
    "name": "Mouse",
    "description": "Wireless mouse",
    "price": 29.99,
    "tax": 2.99
  }
]
```

</div>

**2. 새 item 생성**

<div class="termy">

```console
$ curl -X POST "http://127.0.0.1:8000/items/" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Keyboard",
       "description": "Mechanical keyboard",
       "price": 150.00,
       "tax": 15.00
     }'

{
  "id": 3,
  "name": "Keyboard",
  "description": "Mechanical keyboard",
  "price": 150.0,
  "tax": 15.0
}
```

</div>

**3. 특정 item 조회**

<div class="termy">

```console
$ curl -X GET "http://127.0.0.1:8000/items/1"
{
  "id": 1,
  "name": "Laptop",
  "description": "High-performance laptop",
  "price": 999.99,
  "tax": 99.99
}
```

</div>

## 5단계: Swagger UI 로 API 테스트

브라우저에서 http://127.0.0.1:8000/docs 로 이동하면 자동 생성된 API 문서를 볼 수 있습니다.

Swagger UI 로 할 수 있는 일:

1. **API 엔드포인트 보기**: 사용 가능한 모든 엔드포인트를 시각적으로 확인
2. **요청 / 응답 스키마 확인**: 각 엔드포인트의 입출력 형식 확인
3. **API 직접 테스트**: "Try it out" 버튼으로 실제 API 호출 수행
4. **예시 데이터 보기**: 각 엔드포인트의 예시 요청 / 응답 데이터 확인

### Swagger UI 사용 방법

1. `/items/` GET 엔드포인트 클릭
2. "Try it out" 버튼 클릭
3. "Execute" 버튼 클릭
4. 서버 응답 확인

## 6단계: 코드 구조 이해

### 메인 애플리케이션 (`src/main.py`)

```python
from fastapi import FastAPI
from src.api.api import api_router
from src.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
)

app.include_router(api_router)

@app.get("/")
def read_root():
    return {"message": "Hello World"}
```

### Item 스키마 (`src/schemas/items.py`)

```python
from pydantic import BaseModel
from typing import Optional

class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    name: Optional[str] = None
    price: Optional[float] = None

class Item(ItemBase):
    id: int

    class Config:
        from_attributes = True
```

### CRUD 로직 (`src/crud/items.py`)

```python
from typing import List, Optional
from src.schemas.items import Item, ItemCreate, ItemUpdate

class ItemCRUD:
    def __init__(self):
        self.items: List[Item] = []
        self.next_id = 1

    def create_item(self, item: ItemCreate) -> Item:
        new_item = Item(id=self.next_id, **item.dict())
        self.items.append(new_item)
        self.next_id += 1
        return new_item

    def get_items(self) -> List[Item]:
        return self.items

    def get_item(self, item_id: int) -> Optional[Item]:
        return next((item for item in self.items if item.id == item_id), None)
```

## 7단계: 프로젝트 확장

### 새 라우트 추가

`fastkit addroute` 명령으로 새 엔드포인트를 추가할 수 있습니다:

<div class="termy">

```console
$ fastkit addroute user
                       Adding New Route
┌──────────────────┬──────────────────────────────────────────┐
│ Project          │ my-first-api                             │
│ Route Name       │ user                                     │
│ Target Directory │ /path/to/my-first-api                   │
└──────────────────┴──────────────────────────────────────────┘

Do you want to add route 'user' to the current project? [Y/n]: y

✨ Successfully added new route 'user' to the current project!
```

</div>

이 명령은 다음 파일들을 만듭니다:

- `src/api/routes/user.py` - 사용자 관련 엔드포인트
- `src/schemas/user.py` - 사용자 데이터 모델
- `src/crud/user.py` - 사용자 데이터 처리 로직

### 환경 설정 커스터마이즈

`src/core/config.py` 를 수정해 프로젝트 설정을 변경할 수 있습니다:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "My First API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "My first FastAPI server"
    API_V1_STR: str = "/api/v1"

    class Config:
        env_file = ".env"

settings = Settings()
```

## 8단계: 테스트 실행

프로젝트에는 기본 테스트가 포함돼 있습니다:

<div class="termy">

```console
$ pytest tests/ -v
======================== test session starts ========================
collected 4 items

tests/test_items.py::test_create_item PASSED                   [ 25%]
tests/test_items.py::test_read_items PASSED                    [ 50%]
tests/test_items.py::test_read_item PASSED                     [ 75%]
tests/test_items.py::test_update_item PASSED                   [100%]

======================== 4 passed in 0.15s ========================
```

</div>

## 다음 단계

기본 API 서버 구축을 마쳤습니다! 다음으로 시도해 볼 만한 것들:

1. **[비동기 CRUD API 구축](async-crud-api.md)** — 더 복잡한 비동기 처리 학습
2. **[데이터베이스 통합](database-integration.md)** — PostgreSQL과 SQLAlchemy 사용
3. **[Docker 컨테이너화](docker-deployment.md)** — 프로덕션 배포 준비
4. **[커스텀 응답 처리](custom-response-handling.md)** — 고급 응답 형식 구성

## 문제 해결

### 자주 마주치는 문제

**Q: 서버가 시작되지 않습니다**
A: 가상 환경이 활성화돼 있고 의존성이 제대로 설치됐는지 확인하세요.

**Q: API 엔드포인트에 접속이 안 됩니다**
A: 서버가 정상 동작 중이고 포트 번호 (기본값: 8000) 가 맞는지 확인하세요.

**Q: Swagger UI에 API가 보이지 않습니다**
A: 라우터가 `src/main.py` 에 제대로 포함됐는지 확인하세요.

## 요약

이 튜토리얼에서는 FastAPI-fastkit으로 다음 작업을 진행했습니다:

- ✅ 기본 FastAPI 프로젝트 생성
- ✅ 프로젝트 구조 이해
- ✅ CRUD API 엔드포인트 사용
- ✅ API 문서화 및 테스트
- ✅ 프로젝트 확장 방법

이제 FastAPI의 기본을 익혔으니, 더 복잡한 프로젝트에도 도전해 보세요!
