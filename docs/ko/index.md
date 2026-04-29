<p align="center">
    <img align="top" width="70%" src="https://bnbong.github.io/projects/img/fastkit_general_logo.png" alt="FastAPI-fastkit"/>
</p>
<p align="center">
<em><b>FastAPI-fastkit</b>: Python과 FastAPI 신규 사용자용 빠르고 사용하기 쉬운 스타터 키트</em>
</p>
<p align="center">
<a href="https://pypi.org/project/fastapi-fastkit" target="_blank">
    <img src="https://img.shields.io/pypi/v/fastapi-fastkit" alt="PyPI - Version">
</a>
<a href="https://github.com/bnbong/FastAPI-fastkit/releases" target="_blank">
    <img src="https://img.shields.io/github/v/release/bnbong/FastAPI-fastkit" alt="GitHub Release">
</a>
<a href="https://pepy.tech/project/fastapi-fastkit">
    <img src="https://static.pepy.tech/personalized-badge/fastapi-fastkit?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads" alt="PyPI Downloads">
</a>
</p>

---

이 프로젝트는 Python과 [FastAPI](https://github.com/fastapi/fastapi) 신규 사용자가 Python 기반 웹 앱을 개발하는 데 필요한 개발 환경 구성을 더욱 빠르게 할 수 있도록 만들었습니다.

이 프로젝트는 `SpringBoot initializer` 및 Python Django의 `django-admin` CLI 동작에서 영감을 받았습니다.

## 주요 기능

- **⚡ Immediate FastAPI project creation** : [Python Django](https://github.com/django/django)의 `django-admin` 기능에서 영감을 받은 CLI를 통해 초고속 FastAPI 워크스페이스 및 프로젝트 생성
- **✨ 대화형 프로젝트 빌더**: 데이터베이스, 인증, 캐싱, 모니터링 등 기능을 단계별로 안내하여 선택하고 코드를 자동 생성
- **🎨 Prettier CLI outputs** : [rich library](https://github.com/Textualize/rich) 기반의 아름다운 CLI 경험
- **📋 Standards-based FastAPI project templates** : 모든 FastAPI-fastkit 템플릿은 Python 표준과 FastAPI의 일반적 사용 패턴을 기반으로 구성
- **🔍 Automated template quality assurance** : 주간 자동화 테스트로 모든 템플릿이 정상 동작하며 최신 상태로 유지됨을 보장
- **🚀 Multiple project templates** : 다양한 사용 사례에 맞춘 사전 구성 템플릿 선택 가능(async CRUD, Docker, PostgreSQL 등)
- **📦 Multiple package manager support** : 의존성 관리를 위해 선호하는 Python 패키지 관리자(pip, uv, pdm, poetry)를 선택 가능

## 설치

Python 환경에 `FastAPI-fastkit`를 설치하세요.

<div class="termy">

```console
$ pip install FastAPI-fastkit
---> 100%
```

</div>


## 사용법

### FastAPI 프로젝트 워크스페이스 환경을 즉시 생성

이제 FastAPI-fastkit으로 매우 빠르게 새 FastAPI 프로젝트를 시작할 수 있습니다!

다음으로 즉시 새 FastAPI 프로젝트 워크스페이스를 생성하세요:

<div class="termy">

```console
$ fastkit init
Enter the project name: my-awesome-project
Enter the author name: John Doe
Enter the author email: john@example.com
Enter the project description: My awesome FastAPI project

           Project Information
┌──────────────┬────────────────────────────┐
│ Project Name │ my-awesome-project         │
│ Author       │ John Doe                   │
│ Author Email │ john@example.com           │
│ Description  │ My awesome FastAPI project │
└──────────────┴────────────────────────────┘

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

             FULL Stack
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ sqlalchemy        │
│ Dependency 4 │ alembic           │
│ Dependency 5 │ pytest            │
│ Dependency 6 │ redis             │
│ Dependency 7 │ celery            │
│ Dependency 8 │ pydantic          │
│ Dependency 9 │ pydantic-settings │
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
FastAPI project will deploy at '~your-project-path~'

╭──────────────────────── Info ────────────────────────╮
│ ℹ Injected metadata into setup.py                    │
╰──────────────────────────────────────────────────────╯
╭──────────────────────── Info ────────────────────────╮
│ ℹ Injected metadata into config file                 │
╰──────────────────────────────────────────────────────╯

        Creating Project:
       my-awesome-project
┌───────────────────┬───────────┐
│ Component         │ Collected │
│ fastapi           │ ✓         │
│ uvicorn           │ ✓         │
│ pydantic          │ ✓         │
│ pydantic-settings │ ✓         │
└───────────────────┴───────────┘

Creating virtual environment...

╭──────────────────────── Info ────────────────────────╮
│ ℹ venv created at                                    │
│ ~your-project-path~/my-awesome-project/.venv         │
│ To activate the virtual environment, run:            │
│                                                      │
│     source                                           │
│ ~your-project-path~/my-awesome-project/.venv/bin/act │
│ ivate                                                │
╰──────────────────────────────────────────────────────╯

Installing dependencies...
⠙ Setting up project environment...Collecting <packages~>

---> 100%

╭─────────────────────── Success ───────────────────────╮
│ ✨ Dependencies installed successfully                │
╰───────────────────────────────────────────────────────╯
╭─────────────────────── Success ───────────────────────╮
│ ✨ FastAPI project 'my-awesome-project' has been      │
│ created successfully and saved to                     │
│ ~your-project-path~!                                  │
╰───────────────────────────────────────────────────────╯
╭──────────────────────── Info ────────────────────────╮
│ ℹ To start your project, run 'fastkit runserver' at  │
│ newly created FastAPI project directory              │
╰──────────────────────────────────────────────────────╯
```

</div>

이 명령은 Python 가상 환경과 함께 새로운 FastAPI 프로젝트 워크스페이스 환경을 생성합니다.

### 대화형 모드로 프로젝트 생성 ✨ NEW!

보다 복잡한 프로젝트의 경우, 지능형 기능 선택을 통해 대화형 모드로 FastAPI 애플리케이션을 단계별로 구성하세요:

<div class="termy">

```console
$ fastkit init --interactive

⚡ FastAPI-fastkit Interactive Project Setup ⚡

📋 Basic Project Information
Enter the project name: my-fullstack-project
Enter the author name: John Doe
Enter the author email: john@example.com
Enter the project description: Full-stack FastAPI project with PostgreSQL and JWT

🧱 Architecture Preset
프로젝트 레이아웃을 선택합니다. Enter를 누르면 추천 기본값이 적용됩니다.
  1. minimal           - 가장 작은 FastAPI 앱
  2. single-module     - 단일 모듈 구성 (프로토타입 / 스크립트용)
  3. classic-layered   - api/routes + crud + schemas + core (fastapi-default 형태)
  4. domain-starter    - 도메인 지향 src/app/domains/<concept>/ (recommended)

Select architecture preset: [4]

🗄️ Database Selection
Select database (PostgreSQL, MySQL, MongoDB, Redis, SQLite, None):
  1. PostgreSQL - PostgreSQL database with SQLAlchemy
  2. MySQL - MySQL database with SQLAlchemy
  3. MongoDB - MongoDB with motor async driver
  4. Redis - Redis for caching and session storage
  5. SQLite - SQLite database for development
  6. None - No database

Select database: 1

🔐 Authentication Selection
Select authentication (JWT, OAuth2, FastAPI-Users, Session-based, None):
  1. JWT - JSON Web Token authentication
  2. OAuth2 - OAuth2 with password flow
  3. FastAPI-Users - Full featured user management
  4. Session-based - Cookie-based sessions
  5. None - No authentication

Select authentication: 1

⚙️ Background Tasks Selection
Select background tasks (Celery, Dramatiq, None):
  1. Celery - Distributed task queue
  2. Dramatiq - Fast and reliable task processing
  3. None - No background tasks

Select background tasks: 1

💾 Caching Selection
Select caching (Redis, fastapi-cache2, None):
  1. Redis - Redis caching
  2. fastapi-cache2 - Simple caching for FastAPI
  3. None - No caching

Select caching: 1

📊 Monitoring Selection
Select monitoring (Loguru, OpenTelemetry, Prometheus, None):
  1. Loguru - Simple and powerful logging
  2. OpenTelemetry - Observability framework
  3. Prometheus - Metrics and monitoring
  4. None - No monitoring

Select monitoring: 3


🧪 테스트 프레임워크 선택
테스트 프레임워크를 선택하세요 (Basic, Coverage, Advanced, None):
  1. Basic - API 테스트를 위한 pytest + httpx
  2. Coverage - Basic + 코드 커버리지
  3. Advanced - Coverage + 픽스처를 위한 faker + factory-boy
  4. None - 테스트 프레임워크 없음

테스트 프레임워크 선택: 2

🛠️ 추가 유틸리티
유틸리티를 선택하세요 (쉼표로 구분된 숫자, 예: 1,3,4):
  1. CORS - Cross-Origin Resource Sharing
  2. Rate-Limiting - 요청 속도 제한
  3. Pagination - 페이지네이션 지원
  4. WebSocket - WebSocket 지원

유틸리티 선택: 1

🚀 배포 구성
배포 옵션을 선택하세요:
  1. Docker - Dockerfile 생성
  2. docker-compose - docker-compose.yml 생성(Docker 포함)
  3. None - 배포 구성 없음

배포 옵션 선택: 2

📦 패키지 매니저 선택
패키지 매니저를 선택하세요 (pip, uv, pdm, poetry): uv

📝 사용자 정의 패키지(선택 사항)
사용자 정의 패키지 이름을 입력하세요(쉼표로 구분, 건너뛰려면 Enter):

───────────────── 선택된 구성 ─────────────────
프로젝트: my-fullstack-project
데이터베이스: PostgreSQL
인증: JWT
백그라운드 작업: Celery
캐싱: Redis
모니터링: Prometheus
테스트: Coverage
유틸리티: CORS
배포: Docker, docker-compose
패키지 매니저: uv
──────────────────────────────────────────────────────────

프로젝트 생성을 진행하시겠습니까? [Y/n]: y

╭─────────────────────── 성공 ───────────────────────╮
│ ✨ 선택한 기능이 포함된 main.py 생성              │
╰────────────────────────────────────────────────────╯
╭─────────────────────── 성공 ───────────────────────╮
│ ✨ 데이터베이스 구성 생성                          │
╰────────────────────────────────────────────────────╯
╭─────────────────────── 성공 ───────────────────────╮
│ ✨ 인증 구성 생성                                  │
╰────────────────────────────────────────────────────╯
╭─────────────────────── 성공 ───────────────────────╮
│ ✨ 테스트 구성 생성                                │
╰────────────────────────────────────────────────────╯
╭─────────────────────── 성공 ───────────────────────╮
│ ✨ Docker 배포 파일 생성                           │
╰────────────────────────────────────────────────────╯

가상 환경을 생성하는 중...
종속성을 설치하는 중...

----> 100%

╭─────────────────────── 성공 ───────────────────────╮
│ ✨ FastAPI 프로젝트 'my-fullstack-project'가       │
│   생성되었습니다!                                  │
│                                                    │
│ 생성된 파일:                                       │
│   • main.py (선택한 모든 기능 포함)               │
│   • src/config/database.py                         │
│   • src/config/auth.py                             │
│   • tests/conftest.py                              │
│   • Dockerfile                                     │
│   • docker-compose.yml                             │
│   • pyproject.toml / requirements.txt              │
╰────────────────────────────────────────────────────╯
```

</div>

대화형 모드가 제공하는 기능:
- 데이터베이스, 인증, 백그라운드 작업, 캐싱, 모니터링 등 기능에 대한 가이드형 선택
- 선택한 기능에 대한 자동 코드 생성(main.py, 구성 파일, Docker 파일)
- 자동 pip 호환성의 스마트 종속성 관리
- 호환되지 않는 조합을 방지하는 기능 검증
- 최대 유연성을 위한 Always Empty project를 기본 베이스로 제공

### FastAPI 프로젝트에 새 라우트를 추가하기

`FastAPI-fastkit`은 FastAPI 프로젝트 확장을 쉽게 만들어 줍니다.

다음으로 FastAPI 프로젝트에 새 라우트 엔드포인트를 추가하세요:

<div class="termy">

```console
$ fastkit addroute my-awesome-project user
                       새 라우트 추가 중
┌──────────────────┬──────────────────────────────────────────┐
│ 프로젝트         │ my-awesome-project                       │
│ 라우트 이름      │ user                                     │
│ 대상 디렉터리    │ ~your-project-path~                      │
└──────────────────┴──────────────────────────────────────────┘

프로젝트 'my-awesome-project'에 라우트 'user'를 추가하시겠습니까? [Y/n]: y

╭──────────────────────── 정보 ───────────────────────╮
│ ℹ API 라우터를 포함하도록 main.py를 업데이트했습니다 │
╰─────────────────────────────────────────────────────╯
╭─────────────────────── 성공 ───────────────────────╮
│ ✨ 새 라우트 'user'를 프로젝트에 성공적으로 추가했습니다 │
│ `my-awesome-project`                                  │
╰──────────────────────────────────────────────────────╯
```

</div>

### 구조화된 FastAPI 데모 프로젝트를 바로 배치하기

구조화된 FastAPI 데모 프로젝트로 시작할 수도 있습니다.

데모 프로젝트는 다양한 기술 스택으로 구성되어 있으며 간단한 아이템 CRUD 엔드포인트가 구현되어 있습니다.

다음 명령으로 구조화된 FastAPI 데모 프로젝트를 즉시 배치하세요:

<div class="termy">

```console
$ fastkit startdemo
프로젝트 이름을 입력하세요: my-awesome-demo
작성자 이름을 입력하세요: John Doe
작성자 이메일을 입력하세요: john@example.com
프로젝트 설명을 입력하세요: My awesome FastAPI demo
'fastapi-default' 템플릿을 사용하여 FastAPI 프로젝트를 배포합니다
템플릿 경로:
/~fastapi_fastkit-package-path~/fastapi_project_template/fastapi-default

           프로젝트 정보
┌──────────────┬─────────────────────────┐
│ 프로젝트 이름│ my-awesome-demo         │
│ 작성자       │ John Doe                │
│ 작성자 이메일│ john@example.com        │
│ 설명         │ My awesome FastAPI demo │
└──────────────┴─────────────────────────┘

       템플릿 종속성
┌──────────────┬───────────────────┐
│ 종속성 1     │ fastapi           │
│ 종속성 2     │ uvicorn           │
│ 종속성 3     │ pydantic          │
│ 종속성 4     │ pydantic-settings │
│ 종속성 5     │ python-dotenv     │
└──────────────┴───────────────────┘

사용 가능한 패키지 매니저:
                   패키지 매니저
┌────────┬────────────────────────────────────────────┐
│ PIP    │ 표준 Python 패키지 관리자                 │
│ UV     │ 빠른 Python 패키지 관리자                 │
│ PDM    │ 현대적인 Python 종속성 관리               │
│ POETRY │ Python 종속성 관리 및 패키징              │
└────────┴────────────────────────────────────────────┘

패키지 매니저를 선택하세요 (pip, uv, pdm, poetry) [uv]: uv
프로젝트 생성을 진행하시겠습니까? [y/N]: y
FastAPI 템플릿 프로젝트가 '~your-project-path~'에 배포됩니다

---> 100%

╭─────────────────────── 성공 ───────────────────────╮
│ ✨ 종속성이 성공적으로 설치되었습니다              │
╰────────────────────────────────────────────────────╯
╭─────────────────────── 성공 ───────────────────────╮
│ ✨ FastAPI 프로젝트 'my-awesome-demo'가            │
│ 'fastapi-default'에서 생성되어 다음 위치에 저장되었습니다 │
│ ~your-project-path~!                                │
╰────────────────────────────────────────────────────╯
```

</div>

사용 가능한 FastAPI 데모 목록을 보려면 다음을 확인하세요:

<div class="termy">

```console
$ fastkit list-templates
                      사용 가능한 템플릿
┌─────────────────────────┬───────────────────────────────────┐
│ fastapi-custom-response │ 커스텀 응답 시스템을 갖춘 비동기  │
│                         │ 아이템 관리 API                   │
│ fastapi-dockerized      │ Docker로 컨테이너화된 FastAPI     │
│                         │ 아이템 관리 API                   │
│ fastapi-empty           │ 설명 없음                         │
│ fastapi-async-crud      │ 비동기 아이템 관리 API 서버       │
│ fastapi-psql-orm        │ PostgreSQL을 사용하는 Docker로    │
│                         │ 컨테이너화된 FastAPI 아이템 관리 API │
│ fastapi-default         │ 간단한 FastAPI 프로젝트           │
└─────────────────────────┴───────────────────────────────────┘
```

</div>

## 문서

포괄적인 가이드와 상세한 사용법은 문서를 참고하세요:

- 📚 [User Guide](user-guide/quick-start.md) - 자세한 설치 및 사용 가이드
- 🎯 [Tutorial](tutorial/getting-started.md) - 초보자를 위한 단계별 튜토리얼
- 📖 [CLI Reference](user-guide/cli-reference.md) - 완전한 명령어 레퍼런스
- 🔍 [Template Quality Assurance](reference/template-quality-assurance.md) - 자동화된 테스트와 품질 기준

## 🚀 템플릿 기반 튜토리얼

사전 구성된 템플릿으로 실전 사용 사례를 통해 FastAPI 개발을 학습하세요:

### 📖 코어 튜토리얼

- [기본 API 서버 구축](tutorial/basic-api-server.md) - `fastapi-default` 템플릿을 사용해 첫 FastAPI 서버 만들기
- [비동기 CRUD API 구축](tutorial/async-crud-api.md) - `fastapi-async-crud` 템플릿으로 고성능 비동기 API 개발

### 🗄️ 데이터베이스 및 인프라

- [데이터베이스 통합](tutorial/database-integration.md) - `fastapi-psql-orm` 템플릿으로 PostgreSQL + SQLAlchemy 활용
- [Dockerizing 및 배포](tutorial/docker-deployment.md) - `fastapi-dockerized` 템플릿을 사용해 프로덕션 배포 환경 구성

### ⚡ 고급 기능

- **[커스텀 응답 처리 & 고급 API 설계](tutorial/custom-response-handling.md)** - `fastapi-custom-response` 템플릿으로 엔터프라이즈급 API 구축
- **[MCP와의 통합](tutorial/mcp-integration.md)** - `fastapi-mcp` 템플릿을 사용해 AI 모델과 통합된 API 서버 생성

각 튜토리얼은 다음을 제공합니다:
- ✅ **실용적인 예제** - 실제 프로젝트에서 바로 사용할 수 있는 코드
- ✅ **단계별 가이드** - 초보자도 쉽게 따라 할 수 있는 상세 설명
- ✅ **모범 사례** - 업계 표준 패턴과 보안 고려 사항
- ✅ **확장 방법** - 프로젝트를 한 단계 더 발전시키는 가이드

## 기여

커뮤니티의 기여를 환영합니다! FastAPI-fastkit은 Python과 FastAPI 입문자를 돕기 위해 설계되었으며, 여러분의 기여는 큰 영향을 미칠 수 있습니다.

### 기여할 수 있는 항목

- 🚀 **새로운 FastAPI 템플릿** - 다양한 사용 사례를 위한 템플릿 추가
- 🐛 **버그 수정** - 안정성과 신뢰성 개선에 도움
- 📚 **문서화** - 가이드, 예제, 번역 개선
- 🧪 **테스트** - 테스트 커버리지 확장 및 통합 테스트 추가
- 💡 **기능** - 새로운 CLI 기능 제안 및 구현

### 기여 시작하기

FastAPI-fastkit에 기여를 시작하려면 다음의 종합 가이드를 참고하세요:

- **[개발 환경 설정](contributing/development-setup.md)** - 개발 환경 설정에 대한 완전한 가이드
- **[코드 가이드라인](contributing/code-guidelines.md)** - 코딩 표준 및 모범 사례
- **[CONTRIBUTING.md](https://github.com/bnbong/FastAPI-fastkit/blob/main/CONTRIBUTING.md)** - 종합 기여 가이드
- **[CODE_OF_CONDUCT.md](https://github.com/bnbong/FastAPI-fastkit/blob/main/CODE_OF_CONDUCT.md)** - 프로젝트 원칙과 커뮤니티 기준
- **[SECURITY.md](https://github.com/bnbong/FastAPI-fastkit/blob/main/SECURITY.md)** - 보안 지침 및 신고 방법

## FastAPI-fastkit의 의의

FastAPI-fastkit은 Python과 FastAPI 신규 사용자에게 빠르고 쉽게 사용할 수 있는 스타터 키트를 제공하는 것을 목표로 합니다.

이 아이디어는 FastAPI 입문자가 처음부터 학습하도록 돕기 위한 취지로 시작되었으며, [FastAPI 0.111.0 버전 업데이트](https://github.com/fastapi/fastapi/releases/tag/0.111.0)에서 추가된 FastAPI-cli 패키지의 프로덕션적 의의와도 맥락을 같이합니다.

오랫동안 FastAPI를 사용해 오며 사랑해온 사람으로서, FastAPI 개발자 [tiangolo](https://github.com/tiangolo)가 밝힌 [멋진 동기](https://github.com/fastapi/fastapi/pull/11522#issuecomment-2264639417)를 실현하는 데 도움이 될 프로젝트를 만들고 싶었습니다.

FastAPI-fastkit은 다음을 제공함으로써 시작 단계와 프로덕션 준비 애플리케이션 구축 사이의 간극을 메웁니다:

- **즉각적인 생산성**: 초기 설정의 복잡성에 압도될 수 있는 신규 사용자에게 즉시 생산성을 제공
- **모범 사례**: 모든 템플릿에 모범 사례가 내장되어 올바른 FastAPI 패턴 학습에 도움
- **확장 가능한 기반**: 초보자에서 전문가로 성장함에 따라 함께 확장되는 기반
- **커뮤니티 주도 템플릿**: 실제 FastAPI 사용 패턴을 반영한 커뮤니티 중심 템플릿

## 다음 단계

FastAPI-fastkit을 시작할 준비가 되셨나요? 다음 단계를 따라 진행하세요:

### 🚀 빠른 시작

1. **[설치](user-guide/installation.md)**: FastAPI-fastkit 설치
2. **[퀵 스타트](user-guide/quick-start.md)**: 5분 만에 첫 프로젝트 만들기
3. **[입문 튜토리얼](tutorial/getting-started.md)**: 단계별 상세 튜토리얼

### 📚 심화 학습

- **[프로젝트 생성](user-guide/creating-projects.md)**: 다양한 스택으로 프로젝트 생성
- **[라우트 추가](user-guide/adding-routes.md)**: 프로젝트에 API 엔드포인트 추가
- **[템플릿 사용](user-guide/using-templates.md)**: 사전 구축된 프로젝트 템플릿 사용

### 🛠️ 기여하기

FastAPI-fastkit에 기여하고 싶으신가요?

- **[개발 환경 설정](contributing/development-setup.md)**: 개발 환경 설정
- **[코드 가이드라인](contributing/code-guidelines.md)**: 코딩 표준 및 모범 사례 준수
- **[기여 가이드라인](https://github.com/bnbong/FastAPI-fastkit/blob/main/CONTRIBUTING.md)**: 종합 기여 가이드

### 🔍 참고 자료

- **[CLI 레퍼런스](user-guide/cli-reference.md)**: 전체 CLI 명령 레퍼런스
- **[템플릿 품질 보증](reference/template-quality-assurance.md)**: 자동화된 테스트 및 품질 기준
- **[FAQ](reference/faq.md)**: 자주 묻는 질문
- **[GitHub 저장소](https://github.com/bnbong/FastAPI-fastkit)**: 소스 코드 및 이슈 트래킹

## 라이선스

이 프로젝트는 MIT 라이선스 하에 제공됩니다 - 자세한 내용은 [LICENSE](https://github.com/bnbong/FastAPI-fastkit/blob/main/LICENSE) 파일을 참조하세요.
