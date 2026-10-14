# FastAPI 템플릿 작성 가이드

FastAPI-fastkit에 새 FastAPI 프로젝트 템플릿을 추가하는 방법을 정리한 종합 가이드입니다.

## 🎯 개요

새 템플릿을 추가하는 작업은 5단계 프로세스로 진행됩니다:

1. **📋 계획과 설계** — 템플릿의 목적과 구조 정의
2. **🏗️ 템플릿 구현** — 필수 구조와 파일 생성
3. **🔍 로컬 검증** — inspector 로 템플릿 검증
4. **📚 문서화** — README 및 사용 가이드 작성
5. **🚀 제출과 검토** — PR 생성 및 커뮤니티 검토

## 📋 1단계: 계획과 설계

### 템플릿 목적 정의

새 템플릿을 만들기 전에 다음 질문에 답해 보세요:

- **이 템플릿이 제공하는 고유한 가치는 무엇인가?**
- **기존 템플릿들과 어떻게 차별화되는가?**
- **어떤 사용자 그룹이 대상 사용자인가?**
- **어떤 기술 스택을 포함할 것인가?**

### 템플릿 명명 규칙

```
fastapi-{purpose}-{stack}
```

예:

- `fastapi-microservice` (마이크로서비스 템플릿)
- `fastapi-graphql` (GraphQL 통합 템플릿)
- `fastapi-auth-jwt` (JWT 인증 템플릿)

### 기술 스택 계획

포함할 주요 기술을 미리 정의하세요:

```yaml
# 예시: fastapi-microservice 템플릿
core_dependencies:
  - fastapi
  - uvicorn
  - pydantic
  - pydantic-settings

additional_features:
  - sqlalchemy (ORM)
  - alembic (migrations)
  - redis (caching)
  - celery (background tasks)
  - pytest (testing)

development_tools:
  - black (code formatting)
  - isort (import sorting)
  - mypy (type checking)
  - pre-commit (Git hooks)
```

## 🏗️ 2단계: 템플릿 구현

### 필수 디렉터리 구조

```
fastapi-{template-name}/
├── src/                          # 애플리케이션 소스 코드
│   ├── main.py-tpl              # ✅ FastAPI 앱 진입점 (필수)
│   ├── __init__.py-tpl
│   ├── api/                     # API 라우터
│   │   ├── __init__.py-tpl
│   │   ├── api.py-tpl           # 메인 API 라우터
│   │   └── routes/              # 개별 라우트
│   │       ├── __init__.py-tpl
│   │       └── items.py-tpl     # 예제 라우트
│   ├── core/                    # 코어 설정
│   │   ├── __init__.py-tpl
│   │   └── config.py-tpl        # 설정 관리
│   ├── crud/                    # CRUD 로직
│   │   ├── __init__.py-tpl
│   │   └── items.py-tpl
│   ├── schemas/                 # Pydantic 모델
│   │   ├── __init__.py-tpl
│   │   └── items.py-tpl
│   └── utils/                   # 유틸리티 함수
│       ├── __init__.py-tpl
│       └── helpers.py-tpl
├── tests/                       # ✅ 테스트 (필수)
│   ├── __init__.py-tpl
│   ├── conftest.py-tpl         # pytest 설정
│   └── test_items.py-tpl       # 예제 테스트
├── scripts/                     # 스크립트
│   ├── format.sh-tpl           # 코드 포매팅
│   ├── lint.sh-tpl             # 린팅
│   ├── run-server.sh-tpl       # 서버 실행
│   └── test.sh-tpl             # 테스트 실행
├── pyproject.toml-tpl           # ✅ 주요 메타데이터 (PEP 621, 필수)
├── requirements.txt-tpl         # 🟡 pyproject 가 의존성을 선언하면 선택 사항
├── setup.cfg-tpl               # 개발 도구 설정
├── README.md-tpl               # ✅ 프로젝트 문서 (필수)
├── .env-tpl                    # 환경 변수 템플릿
└── .gitignore-tpl              # Git ignore 파일
```

**최소 필수 파일.** 템플릿은 다음을 반드시 제공해야 합니다:

- `tests/` 디렉터리
- `README.md-tpl`
- `pyproject.toml-tpl` (PEP 621)
- `pyproject.toml-tpl` 의 `[project].dependencies` 또는 `requirements.txt-tpl` 에 `fastapi` 의존성 선언

`pyproject.toml-tpl`이 `[project].dependencies`를 선언한다면 `requirements.txt-tpl`은 필수가 아닙니다. 다만 템플릿이 두 파일을 모두 제공한다면 내용이 서로 일치해야 합니다. 두 파일 사이에 의존성 불일치가 있으면 검사가 실패합니다.

**새 템플릿은 pyproject를 우선해야 하며 `setup.py-tpl`을 제공하면 안 됩니다.** v1.4.0 기준으로 번들 템플릿 중 이 파일을 가진 템플릿은 없습니다. 저장소 밖의 템플릿이 계속 동작하도록 검사 단계에서는 여전히 이 파일을 허용하지만, 이는 레거시 경로입니다.

**Python 3.12를 일관되게 대상으로 하세요**: `requires-python = ">=3.12"`, black `target-version = ["py312"]`, mypy `python_version = "3.12"`, 그리고 Docker 베이스 이미지는 `python:3.12-slim`을 사용합니다. 검사 단계에서는 세 가지 고정 값이 서로 일치하는지 확인합니다.

**생성된 프로젝트의 런타임 의존성으로 `FastAPI-fastkit`을 절대 선언하지 마세요.** CLI는 개발 도구입니다. 템플릿의 의존성 목록에는 생성된 애플리케이션이 실제로 import하는 패키지만 들어 있어야 합니다.

### 파일 작성 가이드

#### 1. main.py-tpl 작성

```python
"""
FastAPI application entry point

This file is the main application for the <project_name> project created with FastAPI-fastkit.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.api import api_router
from core.config import settings

# FastAPI 앱 생성 (inspector 검증을 위해 필수)
app = FastAPI(
    title="<project_name>",
    description="Project created with FastAPI-fastkit",
    version="1.0.0",
)

# CORS 미들웨어 구성
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Hello from <project_name>!"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### 2. pyproject.toml-tpl 작성 (권장)

최신 템플릿은 PEP 621 형식의 `pyproject.toml-tpl`로 메타데이터와 의존성을 선언해야 합니다. 최소한 이 파일은 `[project]` 섹션에 `name`, `version`, `description`, 그리고 `fastapi`가 포함된 `dependencies` 리스트를 가져야 합니다. 또한 사용자 워크스페이스 안의 다른 FastAPI 프로젝트와 생성된 프로젝트를 구분할 수 있도록 `is_fastkit_project()`가 인식하는 두 가지 FastAPI-fastkit 식별 마커도 함께 담아야 합니다:

- `description` 의 `[FastAPI-fastkit templated]` 접두사
- `managed = true` 를 가진 별도의 `[tool.fastapi-fastkit]` 테이블

검출은 둘 중 하나만 있어도 인식합니다 (대소문자 구분 없음). 메타데이터 주입 단계가 템플릿이 마커를 빠뜨려도 프로젝트 생성 시점에 추가해 주지만, 작성자는 명시적으로 포함해 두는 것이 좋습니다.

```toml
[project]
name = "<project_name>"
version = "0.1.0"
description = "[FastAPI-fastkit templated] <description>"
authors = [
    {name = "<author>", email = "<author_email>"},
]
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.34.0",
    "pydantic>=2.10.0",
    "pydantic-settings>=2.7.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "httpx>=0.28.0",
]

[tool.fastapi-fastkit]
managed = true

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

#### 3. requirements.txt-tpl 작성 (선택)

`pyproject.toml-tpl` 이 `[project].dependencies` 를 선언한다면 선택 사항입니다. `pip` 단독 워크플로를 선호하는 템플릿에는 여전히 유용합니다.

```txt
# FastAPI 핵심 의존성 (필수)
fastapi==0.104.1
uvicorn[standard]==0.24.0

# 데이터 검증
pydantic==2.5.0
pydantic-settings==2.1.0

# 환경 변수 관리
python-dotenv==1.0.0

# 데이터베이스 (필요한 경우)
sqlalchemy==2.0.23
alembic==1.13.0

# 개발 도구
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2

# 코드 품질
black==23.11.0
isort==5.12.0
mypy==1.7.1
```

#### 4. 라우트 앵커

`main.py-tpl`이나 API 집계 모듈을 제공하는 템플릿은 `fastkit addroute`가 코드를 삽입할 위치를 표시해 두어야 합니다:

```python
from src.app.api import health

# fastkit:imports

api_router = APIRouter()
api_router.include_router(health.router)

# fastkit:routes
```

앵커가 없으면 `addroute`는 AST 기반 삽입 방식으로 대신 동작해 import 블록과 라우터 등록 위치를 직접 찾습니다. 따라서 앵커가 없는 템플릿도 동작은 하지만, 결과를 예측하기가 더 어렵습니다. 이 파일들을 수정할 때는 앵커 주석을 그대로 유지하세요.

#### 5. 테스트 파일 작성

```python
# tests/test_items.py-tpl
"""
Items API test module
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_health_check():
    """Test health check"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_create_item():
    """Test item creation"""
    item_data = {
        "name": "Test Item",
        "description": "Test Description"
    }
    response = client.post("/api/v1/items/", json=item_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == item_data["name"]
    assert data["description"] == item_data["description"]

def test_read_items():
    """Test reading items list"""
    response = client.get("/api/v1/items/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

## 🔍 3단계: 로컬 검증

### 자동 검증 스크립트 실행

새 템플릿이 준비되면 다음 명령으로 검증하세요:

```bash
# 모든 템플릿 검증
make inspect-templates

# 특정 템플릿만 검증
make inspect-template TEMPLATES="fastapi-your-template"

# verbose 출력으로 검증
python scripts/inspect-templates.py --templates "fastapi-your-template" --verbose

# 빠른 로컬 반복 실행: 네트워크 조회 없음, 서버 실행 없음
python scripts/inspect-templates.py --templates "fastapi-your-template" \
    --offline --no-smoke

# PR을 열기 전 전체 검사 (생성된 프로젝트에 mypy 검사 추가)
python scripts/inspect-templates.py --templates "fastapi-your-template" --mypy
```

`--offline`은 PyPI 의존성 최신성 조회를 건너뛰고, `--no-smoke`는 가장 느린 단계인 생성된 프로젝트 실행을 건너뛰며, `--mypy`는 생성된 프로젝트의 타입을 검사합니다. 각 검사가 하는 일은 [템플릿 품질 보증](../reference/template-quality-assurance.md)을 참고하세요.

!!! note

    PR을 제출하면 **Template PR Inspection** 워크플로가 자동으로 실행되어 템플릿 변경 사항을 검증합니다. 검증 결과는 PR에 직접 피드백으로 남습니다.

### 검증 체크리스트

inspector 가 자동으로 검증하는 항목들입니다:

#### ✅ 파일 구조 검증

- [ ] `tests/` 디렉터리 존재
- [ ] `README.md-tpl` 파일 존재
- [ ] `pyproject.toml-tpl` 존재 (새 템플릿에는 `setup.py-tpl` 없음)

#### ✅ 파일 확장자 검증

- [ ] 모든 Python 파일이 `.py-tpl` 확장자 사용
- [ ] `.py` 확장자 파일이 존재하지 않음

#### ✅ 의존성 검증

- [ ] 다음 중 최소 한 곳에 `fastapi` 가 선언됨:
    - [ ] `pyproject.toml-tpl` 의 `[project].dependencies` (권장)
    - [ ] `requirements.txt-tpl`
- [ ] `requirements.txt-tpl` 과 `[project].dependencies` 의 내용이 서로 어긋나지 않음
- [ ] `FastAPI-fastkit` 이 런타임 의존성이 **아님**

#### ✅ FastAPI 구현 검증

- [ ] `main.py-tpl` 에 `FastAPI` import 존재
- [ ] `main.py-tpl` 에 `app = FastAPI()` 같은 앱 생성 코드 존재

#### ✅ 테스트 실행 검증

- [ ] 가상 환경 생성 성공
- [ ] 의존성 설치 성공
- [ ] 모든 pytest 테스트 통과

#### ✅ 스모크 테스트

- [ ] 생성된 프로젝트가 uvicorn으로 실행됨
- [ ] `/docs` 가 응답함
- [ ] `/health` 가 응답함

uvicorn 대상은 생성된 `pyproject.toml`의 `[tool.fastapi-fastkit].app_module`, `template-config.yml`의 `app_module`, 관례적인 `main.py` 위치 순서로 결정됩니다.

#### ✅ 설정 일관성

- [ ] `requires-python`, black `target-version`, mypy `python_version` 이 모두 Python 3.12를 가리킴
- [ ] `requirements.txt-tpl` 과 `[project].dependencies` 사이에 의존성 불일치가 없음
- [ ] `FastAPI-fastkit` 에 대한 자기 의존성이 없음

#### ✅ 플레이스홀더 잔여 확인

- [ ] 프로젝트 생성 후 남아 있는 `<placeholder>`가 없음

#### ✅ 자동 템플릿 테스트

FastAPI-fastkit 은 모든 템플릿에 대해 종합 테스트를 실행하는 **자동 템플릿 테스트** 시스템을 포함합니다:

**테스트 커버리지:**

- ✅ 템플릿 생성 과정
- ✅ 프로젝트 메타데이터 주입
- ✅ 가상 환경 설정
- ✅ 의존성 설치 (모든 패키지 매니저)
- ✅ 기본 프로젝트 구조 검증
- ✅ FastAPI 프로젝트 식별

**테스트 실행:**

```console
# 모든 템플릿을 자동으로 테스트
$ pytest tests/test_templates/test_all_templates.py -v

# 특정 템플릿만 테스트
$ pytest tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[your-template-name] -v
```

**템플릿 테스트 자동 발견:**
새 템플릿은 수동 설정 없이 **자동으로 발견**돼 테스트됩니다:

1. ✅ **추가 설정 없음**: 템플릿 추가 → 자동 테스트
2. ✅ **일관된 테스트**: 모든 템플릿에 동일한 품질 기준
3. ✅ **다중 패키지 매니저**: UV, PDM, Poetry, PIP 로 테스트
4. ✅ **종합 검증**: 구조, 메타데이터, 동작 검증

**기여자에게 의미하는 것:**

- 🚀 **`FastAPI-fastkit` 메인 소스 testcase 에 별도 테스트 파일 불필요**: 템플릿이 자동으로 테스트됨
- ⚡ **빠른 개발**: 테스트 설정이 아닌 템플릿 콘텐츠에 집중
- 🛡️ **품질 보증**: 모든 템플릿에 일관된 테스트
- 🔄 **CI/CD 통합**: PR 에서 자동 테스트

**여전히 직접 테스트가 필요한 영역:**

- 🧪 **템플릿 고유 동작**: 비즈니스 로직과 커스텀 기능
- 🔧 **통합 테스트**: 외부 서비스와 복잡한 워크플로
- 📱 **엔드투엔드 시나리오**: 사용자의 전체 워크플로

**테스트 모범 사례:**

```console
# 1. 로컬에서 템플릿 테스트
$ fastkit startdemo your-template-name

# 2. 자동 테스트 실행
$ pytest tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[your-template-name] -v

# 3. 다양한 패키지 매니저로 테스트
$ fastkit startdemo your-template-name --package-manager poetry
$ fastkit startdemo your-template-name --package-manager pdm
$ fastkit startdemo your-template-name --package-manager uv
```

### 수동 검증 체크리스트

자동 검증 외에도 다음 항목을 직접 점검하세요:

#### 🔧 코드 품질

- [ ] 코드가 PEP 8 스타일 가이드를 따름
- [ ] 적절한 타입 힌트 사용
- [ ] 의미 있는 변수명과 함수명
- [ ] 적절한 주석과 docstring

#### 🏗️ 아키텍처

- [ ] 관심사 분리 (API, 비즈니스 로직, 데이터 접근의 분리)
- [ ] 재사용 가능한 컴포넌트 설계
- [ ] 확장 가능한 구조
- [ ] 보안 모범 사례 적용

#### 📚 문서

- [ ] README.md-tpl 이 PROJECT_README_TEMPLATE.md 형식을 따름
- [ ] 설치와 실행 방법이 명시됨
- [ ] API 문서 (OpenAPI/Swagger)
- [ ] 환경 변수 설명

## 📚 4단계: 문서화

### README.md-tpl 작성

[PROJECT_README_TEMPLATE.md](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/PROJECT_README_TEMPLATE.md) 가이드를 기준으로 작성하세요.

### 템플릿 설명 문서 작성

`src/fastapi_fastkit/fastapi_project_template/README.md` 에 새 템플릿에 대한 설명을 추가하세요:

```markdown
## fastapi-your-template

여기에 새 템플릿에 대한 짧은 설명과 사용 사례를 작성하세요.

### Features:
- 기능 1
- 기능 2
- 기능 3

### Use Cases:
- 사용 사례 1
- 사용 사례 2
```

## 🚀 5단계: 제출과 검토

### PR 생성 전 체크리스트

- [ ] 모든 자동 검증 통과 (`make inspect-templates`)
- [ ] 코드 포매팅 완료 (`make format`)
- [ ] 린트 검사 통과 (`make lint`)
- [ ] 모든 테스트 통과 (`make test`)
- [ ] 문서 작성 완료
- [ ] CONTRIBUTING.md 가이드라인 준수

### PR 제목과 설명

```
[TEMPLATE] Add fastapi-{template-name} template

## Overview
새 {purpose} 템플릿을 추가합니다.

## Key Features
- 기능 1
- 기능 2
- 기능 3

## Validation Results
- [ ] Inspector 검증 통과
- [ ] 모든 테스트 통과
- [ ] 문서 작성 완료

## Usage Example
\```bash
fastkit startdemo
# 템플릿 선택: fastapi-{template-name}
\```

## Related Issues
Closes #issue-number
```

### 검토 프로세스

1. **자동 검증**: GitHub Actions 가 템플릿을 자동으로 검증합니다
    - **Template PR Inspection**: 템플릿을 수정하는 PR 에서 `inspect-changed-templates.py` 실행
    - **Weekly Inspection**: 매주 수요일 전체 템플릿 검증
2. **코드 검토**: 메인테이너와 커뮤니티가 코드를 검토합니다
3. **테스트**: 다양한 환경에서 템플릿이 테스트됩니다
4. **문서 검토**: 문서의 정확성과 완전성을 검토합니다
5. **승인과 머지**: 모든 요구 사항을 만족하면 main 브랜치에 머지

!!! note

    검증 결과가 자동 PR 코멘트로 달립니다. 리뷰 요청 전에 이 코멘트들을 먼저 확인해 주세요!

## 🎯 모범 사례

### 보안 고려 사항

- 민감한 정보는 환경 변수로 관리
- 적절한 CORS 설정
- 입력 데이터 검증
- SQL 인젝션 방지

### 성능 최적화

- 비동기 처리 활용
- 데이터베이스 쿼리 최적화
- 적절한 캐싱 전략
- 응답 압축 설정

### 유지보수성

- 명확한 코드 구조
- 포괄적인 테스트 커버리지
- 자세한 문서
- 로깅과 모니터링 설정

## 🆘 도움이 필요하신가요?

- 📖 [개발 환경 설정 가이드](development-setup.md)
- 📋 [코드 가이드라인](code-guidelines.md)
- 💬 [GitHub Discussions](https://github.com/bnbong/FastAPI-fastkit/discussions)
- 📧 [메인테이너에게 연락](mailto:bbbong9@gmail.com)

새 템플릿을 추가하는 일은 FastAPI-fastkit 커뮤니티에 큰 도움이 됩니다.
당신의 아이디어와 노력이 다른 개발자들에게 큰 도움이 될 것입니다! 🚀
