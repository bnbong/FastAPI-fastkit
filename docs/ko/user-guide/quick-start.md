# 퀵 스타트

FastAPI-fastkit으로 5분 안에 첫 FastAPI 프로젝트를 만들어 보세요!

!!! tip "어떤 스타터를 골라야 할지 모르겠다면?"
    `startdemo` 템플릿과 대화형 아키텍처 프리셋(`minimal` / `single-module` / `classic-layered` / `domain-starter`)을 입문자도 이해하기 쉽게 비교한 [**어떤 스타터를 선택해야 할까?**](choosing-a-starter.md)를 참고하세요. 짧게 말하면 **`fastkit init --interactive`의 `domain-starter` 프리셋이 현재 권장 기본값입니다.**

## 1. 프로젝트 생성

FastAPI-fastkit의 `init` 명령으로 새 프로젝트를 만듭니다:

<div class="termy">

```console
$ fastkit init
Enter the project name: my-first-app
Enter the author name: Your Name
Enter the author email: your.email@example.com
Enter the project description: My first FastAPI application

           Project Information
┌──────────────┬─────────────────────────────┐
│ Project Name │ my-first-app                │
│ Author       │ Your Name                   │
│ Author Email │ your.email@example.com      │
│ Description  │ My first FastAPI application│
└──────────────┴─────────────────────────────┘

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

✨ FastAPI project 'my-first-app' has been created successfully!
```

</div>

## 2. 가상 환경 활성화

프로젝트 폴더로 이동해 가상 환경을 활성화합니다:

<div class="termy">

```console
$ cd my-first-app
$ source .venv/bin/activate  # Linux/macOS
$ .venv\Scripts\activate     # Windows
```

</div>

## 3. 개발 서버 시작

FastAPI 개발 서버를 시작합니다:

<div class="termy">

```console
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [28720]
INFO:     Started server process [28722]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

</div>

!!! success "축하합니다!"
    FastAPI 서버가 실행 중입니다! 브라우저에서 확인해 보세요.

## 4. API 테스트

브라우저에서 다음 URL을 열어 보세요:

### 메인 엔드포인트

[http://127.0.0.1:8000](http://127.0.0.1:8000) 에 접속하면 다음과 같이 표시됩니다:

```json
{"message": "Hello World"}
```

### 대화형 API 문서

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) 를 방문하세요.

자동 생성되는 **Swagger UI** 문서로, 여기서 다음을 할 수 있습니다:

- 모든 API 엔드포인트 보기
- 브라우저에서 직접 엔드포인트 테스트
- 요청/응답 스키마 확인

### 대안 문서

[http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) 를 방문하세요.

다른 형태의 깔끔한 디자인을 가진 **ReDoc** 문서 인터페이스입니다.

## 5. 첫 라우트 추가

프로젝트에 새 API 라우트를 추가해 봅시다:

<div class="termy">

```console
$ fastkit addroute users my-first-app
                       Adding New Route
┌──────────────────┬──────────────────────────────────────────┐
│ Project          │ my-first-app                             │
│ Route Name       │ users                                    │
│ Target Directory │ ~/my-first-app                           │
└──────────────────┴──────────────────────────────────────────┘

Do you want to add route 'users' to project 'my-first-app'? [Y/n]: y

╭──────────────────────── Info ────────────────────────╮
│ ℹ Updated main.py to include the API router          │
╰──────────────────────────────────────────────────────╯
╭─────────────────────── Success ───────────────────────╮
│ ✨ Successfully added new route 'users' to project    │
│ `my-first-app`                                        │
╰───────────────────────────────────────────────────────╯
```

</div>

서버가 자동으로 재시작되며, 이제 다음과 같은 새 엔드포인트들이 생깁니다:

- `GET /api/v1/users/` - 모든 사용자 조회
- `POST /api/v1/users/` - 새 사용자 생성
- `GET /api/v1/users/{user_id}` - 특정 사용자 조회
- `PUT /api/v1/users/{user_id}` - 사용자 수정
- `DELETE /api/v1/users/{user_id}` - 사용자 삭제

## 6. 새 API 테스트

### curl 사용

**모든 사용자 조회:**

<div class="termy">

```console
$ curl http://127.0.0.1:8000/api/v1/users/
[]
```

</div>

**새 사용자 생성:**

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
```

</div>

### 대화형 문서 사용

1. [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) 를 방문합니다.
2. **"users"** 섹션을 펼칩니다.
3. **"POST /api/v1/users/"** 를 클릭합니다.
4. **"Try it out"** 을 클릭합니다.
5. 요청 본문을 채웁니다:
   ```json
   {
     "title": "Jane Smith",
     "description": "Product Manager"
   }
   ```
6. **"Execute"** 를 클릭합니다.

## 7. 프로젝트 구조 살펴보기

생성된 프로젝트는 깔끔하게 정돈된 구조를 가집니다:

```
my-first-app/
├── .venv/                    # 가상 환경
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI 앱 진입점
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py        # 앱 설정
│   ├── api/
│   │   ├── __init__.py
│   │   ├── api.py          # API 라우터 모음
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── items.py     # 기본 items 라우트
│   │       └── users.py     # 새로 추가한 users 라우트
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── items.py         # items용 CRUD 작업
│   │   └── users.py         # users용 CRUD 작업
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── items.py         # items용 Pydantic 스키마
│   │   └── users.py         # users용 Pydantic 스키마
│   └── mocks/
│       ├── __init__.py
│       └── mock_items.json  # 테스트 데이터
├── tests/                   # 테스트 파일
├── scripts/                 # 유틸리티 스크립트
├── requirements.txt         # Python 의존성
├── setup.py                # 패키지 설정
└── README.md               # 프로젝트 문서
```

## 8. 패키지 매니저 옵션

FastAPI-fastkit은 사용자의 선호에 맞는 여러 Python 패키지 매니저를 지원합니다:

### 사용 가능한 패키지 매니저

| 매니저 | 설명 | 적합한 경우 |
|---|---|---|
| **UV** | 빠른 Python 패키지 매니저 (기본값) | 속도와 성능 |
| **PDM** | 현대적인 Python 의존성 관리 | 고급 의존성 해석 |
| **Poetry** | Python 의존성 관리 및 패키징 | Poetry 기반 워크플로 |
| **PIP** | 표준 Python 패키지 매니저 | 전통적인 Python 개발 |

### 패키지 매니저 지정

선호하는 패키지 매니저는 다음과 같은 방식으로 지정할 수 있습니다:

#### 1. 대화형 선택 (기본)

`fastkit init` 또는 `fastkit startdemo` 를 실행하면 선택 프롬프트가 뜹니다:

<div class="termy">

```console
$ fastkit init
# ... 프로젝트 정보 및 스택 선택 후 ...

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

#### 2. 명령줄 옵션

대화형 프롬프트를 건너뛰고 패키지 매니저를 직접 지정할 수 있습니다:

<div class="termy">

```console
$ fastkit init --package-manager poetry
$ fastkit startdemo --package-manager pdm
```

</div>

### 생성되는 의존성 파일

각 패키지 매니저는 적절한 의존성 파일을 생성합니다:

- **UV/PDM**: `pyproject.toml` (PEP 621 형식)
- **Poetry**: `pyproject.toml` (Poetry 형식)
- **PIP**: `requirements.txt`

## 9. 다음 단계

축하합니다! 다음을 모두 성공적으로 마쳤습니다:

✅ 첫 FastAPI 프로젝트 생성
✅ 개발 서버 실행
✅ 새 API 라우트 추가
✅ API 테스트

### 학습 이어가기

1. **[첫 프로젝트 만들기](../tutorial/first-project.md)**: 더 복잡한 블로그 API 구축
2. **[프로젝트 생성](creating-projects.md)**: 다양한 스택과 옵션 학습
3. **[라우트 추가](adding-routes.md)**: API 개발 기술 익히기
4. **[템플릿 사용](using-templates.md)**: 사전 구축된 프로젝트 템플릿 탐색

### 더 실험해 보기

다음 명령들을 사용해 더 많은 기능을 탐색해 보세요:

<div class="termy">

```console
# 사용 가능한 템플릿 목록
$ fastkit list-templates

# 템플릿으로 프로젝트 생성
$ fastkit startdemo

# 라우트 더 추가 (라우트 이름이 첫째, 프로젝트 디렉터리가 둘째)
$ fastkit addroute products my-first-app
$ fastkit addroute orders my-first-app
```

</div>

!!! tip "개발 팁"
    - 파일을 변경하면 서버가 자동으로 재시작됩니다
    - 새 기능을 추가할 때마다 `/docs` 에서 대화형 문서를 확인하세요
    - 의존성 격리를 위해 가상 환경을 사용하세요
    - 생성된 코드를 살펴보며 프로젝트 구조를 이해하세요
