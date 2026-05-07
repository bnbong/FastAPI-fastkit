# 프로젝트 생성

FastAPI-fastkit으로 다양한 유형의 FastAPI 프로젝트를 만드는 방법을 자세히 안내합니다.

## 기본 프로젝트 생성

### 1. 대화형 모드 프로젝트 생성

가장 기본적인 대화형 프로젝트 생성 방법은 다음과 같습니다:

<div class="termy">

```console
$ fastkit init
Enter the project name: my-awesome-api
Enter the author name: John Doe
Enter the author email: john@example.com
Enter the project description: Awesome FastAPI project

           Project Information
┌──────────────┬─────────────────────────┐
│ Project Name │ my-awesome-api          │
│ Author       │ John Doe                │
│ Author Email │ john@example.com        │
│ Description  │ Awesome FastAPI project │
└──────────────┴─────────────────────────┘
```

</div>

### 2. 스택 선택

프로젝트에 포함할 의존성 스택을 선택합니다:

#### MINIMAL 스택 (기본값)

가장 기본적인 FastAPI 프로젝트:

- `fastapi` - FastAPI 프레임워크
- `uvicorn` - ASGI 서버
- `pydantic` - 데이터 검증
- `pydantic-settings` - 설정 관리

**적합한 경우:**

- FastAPI 학습
- 간단한 API
- 프로토타입
- 마이크로서비스

#### STANDARD 스택

데이터베이스 지원과 테스트를 포함:

- 모든 MINIMAL 의존성
- `sqlalchemy` - 데이터베이스 작업용 ORM
- `alembic` - 데이터베이스 마이그레이션
- `pytest` - 테스트 프레임워크

**적합한 경우:**

- 대부분의 웹 애플리케이션
- 데이터베이스 저장이 필요한 API
- 프로덕션 수준의 애플리케이션
- 팀 프로젝트

#### FULL 스택

완전한 개발 환경:

- 모든 STANDARD 의존성
- `redis` - 캐싱 및 세션 저장
- `celery` - 백그라운드 작업 처리

**적합한 경우:**

- 대규모 애플리케이션
- 고성능 요구 사항
- 복잡한 비즈니스 로직
- 엔터프라이즈 애플리케이션

## 고급 프로젝트 옵션

### 커스텀 프로젝트 설정

생성 시 프로젝트를 커스터마이즈할 수 있습니다:

<div class="termy">

```console
$ fastkit init
Enter the project name: advanced-api
Enter the author name: Development Team
Enter the author email: dev@company.com
Enter the project description: Advanced FastAPI application with custom features

# 데이터베이스 지원을 위해 STANDARD 스택 선택
Select stack (minimal, standard, full): standard
Do you want to proceed with project creation? [y/N]: y
```

</div>

### 프로젝트 구조 설명

프로젝트를 생성하면 FastAPI-fastkit이 다음과 같은 구조를 만들어 줍니다:

```
my-awesome-api/
├── .venv/                      # 가상 환경
├── src/                        # 소스 코드
│   ├── __init__.py
│   ├── main.py                # 애플리케이션 진입점
│   ├── core/                  # 핵심 설정
│   │   ├── __init__.py
│   │   └── config.py         # 설정과 구성
│   ├── api/                   # API 계층
│   │   ├── __init__.py
│   │   ├── api.py            # 메인 API 라우터
│   │   └── routes/           # 개별 라우트 모듈
│   │       ├── __init__.py
│   │       └── items.py      # 예제 items 엔드포인트
│   ├── crud/                  # 데이터베이스 작업
│   │   ├── __init__.py
│   │   └── items.py          # items용 CRUD 작업
│   ├── schemas/               # Pydantic 모델
│   │   ├── __init__.py
│   │   └── items.py          # 데이터 검증 스키마
│   └── mocks/                 # 테스트 데이터
│       ├── __init__.py
│       └── mock_items.json   # 개발용 샘플 데이터
├── tests/                     # 테스트 스위트
│   ├── __init__.py
│   ├── conftest.py           # 테스트 설정
│   └── test_items.py         # 예제 테스트
├── scripts/                   # 유틸리티 스크립트
│   ├── test.sh               # 테스트 실행
│   ├── coverage.sh           # 테스트 커버리지
│   └── lint.sh               # 코드 린팅
├── requirements.txt           # Python 의존성
├── setup.py                  # 패키지 설정
└── README.md                 # 프로젝트 문서
```

### 3. 패키지 매니저 선택

FastAPI-fastkit은 여러 Python 패키지 매니저를 지원합니다. 지금 사용하는 개발 워크플로에 가장 잘 맞는 것을 선택하세요:

#### 사용 가능한 패키지 매니저

<div class="termy">

```console
Available Package Managers:
                   Package Managers
┌────────┬────────────────────────────────────────────┐
│ PIP    │ Standard Python package manager            │
│ UV     │ Fast Python package manager                │
│ PDM    │ Modern Python dependency management        │
│ POETRY │ Python dependency management and packaging │
└────────┴────────────────────────────────────────────┘

Select package manager (pip, uv, pdm, poetry) [uv]: uv
```

</div>

각 패키지 매니저는 자신만의 강점을 가집니다:

#### UV (기본값 — 권장)

**Rust 기반의 빠른 패키지 매니저**

- ⚡ **초고속**: pip보다 10~100배 빠름
- 🔧 **드롭인 대체**: pip 워크플로와 호환
- 📦 **모던**: 완전한 PEP 621 지원
- 🛠️ **신뢰성**: 결정론적 의존성 해석

**생성되는 파일:**

- `pyproject.toml` (PEP 621 형식)
- `uv.lock` (lock 파일)

**생성 후 사용법:**
```console
cd my-project
uv sync              # 의존성 설치
uv add requests      # 새 의존성 추가
uv run pytest       # 테스트 실행
```

#### PDM

**현대적인 Python 의존성 관리**

- 🚀 **현대적**: PEP 582와 PEP 621 지원
- 🧠 **스마트**: 고급 의존성 해석
- 💼 **프로페셔널**: 워크스페이스 및 멀티 프로젝트 지원
- 📊 **분석**: 의존성 분석 도구

**생성되는 파일:**

- `pyproject.toml` (PEP 621 형식)
- `pdm.lock` (lock 파일)

**생성 후 사용법:**
```console
cd my-project
pdm install          # 의존성 설치
pdm add requests     # 새 의존성 추가
pdm run pytest      # 테스트 실행
```

#### Poetry

**성숙한 의존성 관리 및 패키징**

- ✅ **검증됨**: 성숙하고 널리 사용됨
- 📦 **통합**: 빌드 및 배포 지원
- 🔒 **재현 가능**: poetry.lock 으로 정확한 버전 고정
- 🏗️ **완전함**: 전체 프로젝트 라이프사이클 관리

**생성되는 파일:**

- `pyproject.toml` (Poetry 형식)
- `poetry.lock` (lock 파일)

**생성 후 사용법:**
```console
cd my-project
poetry install       # 의존성 설치
poetry add requests  # 새 의존성 추가
poetry run pytest   # 테스트 실행
```

#### PIP

**표준 Python 패키지 매니저**

- 🏠 **내장**: Python에 기본 포함
- 🌍 **범용성**: 어디서나 무리 없이 사용 가능
- 📚 **친숙함**: 대부분의 개발자가 알고 있음
- 🔧 **단순함**: 직관적인 워크플로

**생성되는 파일:**

- `requirements.txt`

**생성 후 사용법:**
```console
cd my-project
source .venv/bin/activate    # Linux/macOS
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
pip install requests
pytest
```

#### 패키지 매니저 지정

선호하는 패키지 매니저를 지정할 수 있습니다:

**대화형 선택 (기본):**
```console
$ fastkit init
# ... 패키지 매니저 선택 프롬프트 표시
```

**명령줄 옵션:**
```console
$ fastkit init --package-manager poetry
$ fastkit init --package-manager pdm
$ fastkit init --package-manager uv
$ fastkit init --package-manager pip
```

### 각 디렉터리의 의미

#### `src/` 디렉터리

Python 패키징 모범 사례인 **src layout** 패턴을 따라 모든 애플리케이션 소스 코드를 담습니다.

#### `core/` 모듈

- **config.py**: 애플리케이션 설정, 환경 변수, 그리고 구성
- 모든 설정 관리를 한곳에 집중
- `.env` 파일을 통해 환경별 설정을 지원

#### `api/` 모듈

- **api.py**: 모든 하위 라우터를 포함하는 메인 API 라우터
- **routes/**: 리소스별 개별 라우트 모듈
- API 엔드포인트별 깔끔한 관심사 분리

#### `crud/` 모듈

- 데이터베이스 작업과 비즈니스 로직
- **C**reate, **R**ead, **U**pdate, **D**elete 작업
- API 라우트와 데이터 저장 사이의 추상화 계층

#### `schemas/` 모듈

- 데이터 검증을 위한 Pydantic 모델
- 요청 / 응답 스키마
- 타입 정의와 데이터 모델

#### `tests/` 디렉터리

- 애플리케이션의 완전한 테스트 스위트
- 단위 테스트 및 통합 테스트 포함
- pytest 기반으로 사전 구성

## 스택 비교

| 기능 | MINIMAL | STANDARD | FULL |
|---|---|---|---|
| FastAPI & Uvicorn | ✅ | ✅ | ✅ |
| 데이터 검증 | ✅ | ✅ | ✅ |
| 데이터베이스 지원 | ❌ | ✅ | ✅ |
| 마이그레이션 | ❌ | ✅ | ✅ |
| 테스트 프레임워크 | ❌ | ✅ | ✅ |
| 캐싱 (Redis) | ❌ | ❌ | ✅ |
| 백그라운드 작업 | ❌ | ❌ | ✅ |
| **적합한 경우** | 학습, 단순 API | 대부분의 애플리케이션 | 엔터프라이즈, 복잡한 앱 |

## 프로젝트 생성 예시

### 예시 1: 학습용 프로젝트

<div class="termy">

```console
$ fastkit init
Enter the project name: fastapi-learning
Enter the author name: Student
Enter the author email: student@example.com
Enter the project description: Learning FastAPI basics

Select stack (minimal, standard, full): minimal
Do you want to proceed with project creation? [y/N]: y
```

</div>

### 예시 2: 이커머스 API

<div class="termy">

```console
$ fastkit init
Enter the project name: ecommerce-api
Enter the author name: E-commerce Team
Enter the author email: team@ecommerce.com
Enter the project description: E-commerce platform API

Select stack (minimal, standard, full): standard
Do you want to proceed with project creation? [y/N]: y
```

</div>

### 예시 3: 고성능 애플리케이션

<div class="termy">

```console
$ fastkit init
Enter the project name: enterprise-api
Enter the author name: Enterprise Team
Enter the author email: enterprise@company.com
Enter the project description: High-performance enterprise API

Select stack (minimal, standard, full): full
Do you want to proceed with project creation? [y/N]: y
```

</div>

## 프로젝트 생성 이후

### 1. 가상 환경 활성화

<div class="termy">

```console
$ cd my-awesome-api
$ source .venv/bin/activate  # Linux/macOS
$ .venv\Scripts\activate     # Windows
```

</div>

### 2. 설치 확인

<div class="termy">

```console
$ pip list
Package         Version
fastapi         0.104.1
uvicorn         0.24.0
pydantic        2.5.0
...
```

</div>

### 3. 개발 시작

<div class="termy">

```console
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000
```

</div>

## 설정 관리

### 환경 변수

프로젝트는 `.env` 파일을 통한 환경 기반 설정을 지원합니다:

프로젝트 루트에 `.env` 파일을 만드세요:

```env
# .env
APP_NAME=My Awesome API
APP_VERSION=1.0.0
DEBUG=True
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your-secret-key-here
```

### 코드에서 설정

생성된 `src/core/config.py` 가 이 변수들을 자동으로 로드합니다:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "FastAPI Application"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    DATABASE_URL: str = "sqlite:///./app.db"
    SECRET_KEY: str = "dev-secret-key"

    class Config:
        env_file = ".env"

settings = Settings()
```

## 커스터마이즈 옵션

### 커스텀 의존성 추가

프로젝트 생성 후에도 의존성을 추가할 수 있습니다:

<div class="termy">

```console
$ pip install requests httpx python-jose
$ pip freeze > requirements.txt
```

</div>

### 프로젝트 구조 수정

생성된 구조는 모범 사례를 따르지만, 자유롭게 수정할 수 있습니다:

- `src/` 에 새 모듈 추가
- `api/routes/` 에 추가 라우트 파일 생성
- `crud/` 에서 CRUD 작업 확장
- `schemas/` 에 더 많은 스키마 추가

## 모범 사례

### 1. 가상 환경

프로젝트 의존성 격리를 위해 항상 가상 환경을 사용하세요:

```bash
# 가상 환경과 함께 프로젝트 생성
$ fastkit init  # .venv/ 자동 생성

# 작업 시 활성화
$ source .venv/bin/activate
```

### 2. 버전 관리

프로젝트 생성 후 git 저장소를 초기화하세요:

<div class="termy">

```console
$ cd my-awesome-api
$ git init
$ git add .
$ git commit -m "Initial commit - FastAPI project setup"
```

</div>

### 3. 환경 설정

- 로컬 개발에는 `.env` 파일 사용
- 프로덕션에는 환경 변수 사용
- 민감한 데이터는 절대 버전 관리에 커밋하지 마세요

### 4. 테스트

내장된 테스트 프레임워크를 활용하세요:

<div class="termy">

```console
$ python -m pytest
$ bash scripts/test.sh
```

</div>

## 다음 단계

프로젝트를 만들었다면:

1. **[라우트 추가](adding-routes.md)**: 새 API 엔드포인트 추가 방법 학습
2. **[CLI 레퍼런스](cli-reference.md)**: 모든 명령어 익히기
3. **[첫 프로젝트 만들기 튜토리얼](../tutorial/first-project.md)**: 완전한 애플리케이션 구축

!!! tip "프로젝트 생성 팁"
    - 프로젝트 요구 사항에 맞는 스택을 선택하세요
    - 학습용은 MINIMAL, 대부분의 프로젝트는 STANDARD 로 시작하세요
    - 프로젝트 구조는 확장성과 유지보수성을 고려해 설계되어 있습니다
    - 생성된 모든 코드는 FastAPI 모범 사례를 따릅니다
