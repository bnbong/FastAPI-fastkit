# 아키텍처 프리셋 / 기능 매트릭스

대화형 `fastkit init --interactive`는 기능을 고르기 전에 먼저 **아키텍처 프리셋**([issue #44](https://github.com/bnbong/FastAPI-fastkit/issues/44))을 묻습니다. 이 프리셋이 생성될 프로젝트의 레이아웃을 결정합니다. 프리셋마다 베이스 템플릿이 다르고, 생성된 설정 파일도 일괄적으로 `src/config/` 아래에 두지 않고 각 구조에 맞는 위치에 배치됩니다.

이 페이지는 각 프리셋이 어떤 역할을 하는지, 파일이 어디에 생성되는지, 그리고 어떤 기능 조합에서 수동 연결이 필요한지를 한눈에 보여 주는 기준 문서입니다.

## 프리셋 → 베이스 템플릿

| 프리셋 | 베이스 템플릿 | 설명 |
|---|---|---|
| `minimal` | `fastapi-empty` | 가장 작은 동작 가능한 FastAPI 앱입니다. 플레이스홀더 `main.py`가 기능 선택에 따라 다시 생성됩니다. |
| `single-module` | `fastapi-single-module` | 단일 파일 FastAPI 앱입니다. `main.py`가 다시 생성됩니다. |
| `classic-layered` | `fastapi-default` | 계층형 분할(`api/routes`, `crud`, `schemas`, `core`) 구조입니다. 템플릿이 제공하는 `main.py`는 그대로 유지됩니다. |
| `domain-starter` | `fastapi-domain-starter` | 도메인 지향 구조(`src/app/domains/<concept>/`)입니다. 템플릿이 제공하는 `main.py`는 그대로 유지됩니다. **권장 기본값입니다.** |

## 생성 파일 위치

| 프리셋 | `main.py` 오버레이 | 데이터베이스 설정 위치 | 인증 설정 위치 |
|---|---|---|---|
| `minimal` | `src/main.py`에서 다시 생성 | `src/config/database.py` | `src/config/auth.py` |
| `single-module` | `src/main.py`에서 다시 생성 | `src/config/database.py` | `src/config/auth.py` |
| `classic-layered` | 보존 (템플릿 제공) | `src/core/database.py` | `src/core/auth.py` |
| `domain-starter` | 보존 (템플릿 제공) | `src/app/core/database.py` | `src/app/core/auth.py` |

## 프리셋별 데이터베이스 / 인증 기능 지원

아래 기능은 **모든** 프리셋에서 지원됩니다. 즉, 패키지 설치 자체는 항상 성공합니다. 차이는 동적으로 다시 쓰는 `main.py`가 해당 기능을 자동으로 연결해 주는지 여부에 있습니다.

| 기능 | `minimal` / `single-module` | `classic-layered` / `domain-starter` |
|---|---|---|
| **데이터베이스** (PostgreSQL, MySQL, SQLite, MongoDB) | 설정 모듈을 생성하고, 추가로 다시 생성된 `main.py`에 `await init_db()` 호출용 스텁을 넣어 줍니다. | 설정 모듈을 프리셋에 맞는 경로에 생성합니다. 템플릿이 제공하는 `main.py`는 **그대로 유지**되므로, `get_db()`를 라우터에 직접 연결해야 합니다. |
| **인증** (JWT, FastAPI-Users, OAuth2, Session-based) | 인증 설정 모듈을 생성합니다. JWT의 경우 다시 생성된 `main.py`에 `HTTPBearer` import까지 추가합니다. | 인증 설정 모듈을 프리셋에 맞는 경로에 생성합니다. `main.py`에는 import가 추가되지 않으므로 의존성을 직접 연결해야 합니다. |
| **백그라운드 작업** (Celery, Dramatiq) | 패키지가 설치됩니다. 현재 main.py 오버레이는 없습니다. | 동일. |
| **캐싱** (Redis) | 패키지가 설치됩니다. 현재 main.py 오버레이는 없습니다. | 동일. |
| **CORS** (유틸리티) | 다시 생성된 `main.py`에 `allow_origins=['*']` 형태로 `CORSMiddleware`가 추가됩니다. | 템플릿이 제공하는 `main.py`에 **이미 연결**돼 있습니다 (`settings.all_cors_origins` 조건부). `.env`의 `BACKEND_CORS_ORIGINS` 값만 채우면 활성화되므로 코드를 수정할 필요가 없습니다. |
| **테스트** (Basic / Coverage / Advanced) | 프로젝트 루트에 `pytest.ini` 가 생성됩니다. | 동일. |
| **배포** (Docker, docker-compose) | 프로젝트 루트에 `Dockerfile` 또는 `docker-compose.yml` 이 작성됩니다. | 동일. |

## "프리셋 호환성" 경고가 표시되는 시점

템플릿이 제공하는 `main.py`를 **그대로 유지하는** 프리셋(`classic-layered`, `domain-starter`)에서는 일부 기능이 앱에 자동으로 연결되지 않습니다. 그래서 CLI는 생성이 끝난 직후, 어떤 선택이 수동 연결을 필요로 하는지 정리한 경고를 한 번 보여 줍니다:

| 선택한 기능 | `classic-layered` / `domain-starter` 에서 경고가 발생하나? |
|---|---|
| `CORS` (유틸리티) | ❌ — 템플릿이 제공하는 `main.py`에 이미 연결돼 있습니다. `.env`에 `BACKEND_CORS_ORIGINS`만 채우면 됩니다. |
| `Rate-Limiting` (유틸리티) | ✅ — `slowapi` 리미터 설정이 추가되지 않음 |
| `Prometheus` (모니터링) | ✅ — `Instrumentator().instrument(app)` 호출이 추가되지 않음 |
| 모든 데이터베이스 / 인증 선택 | ⚠️ — 설정 파일은 생성되지만, 라우터에 `Depends()` 로 연결하는 작업은 직접 해야 함 |

`minimal` 과 `single-module` 프리셋에서는 동적 `main.py` 오버레이가 CORS, 레이트 제한, Prometheus 계측을 자동으로 처리하므로 경고가 발생하지 않습니다.

## 지원되지 않는 조합 (안전 우선)

생성기는 의도적으로 템플릿이 제공하는 `main.py` 안에 생성 코드를 무리하게 끼워 넣지 **않습니다**. 그렇게 하면 import가 깨지거나 라우터가 중복될 위험이 있기 때문입니다. 현재 동작 계약은 다음과 같습니다:

- 선택한 패키지는 항상 설치됩니다 (`pip freeze` 결과가 사용자의 의도와 맞도록).
- 생성된 설정 모듈은 항상 프리셋에 맞는 경로에 놓입니다.
- `main.py` 보존 프리셋에서는 어떤 선택이 여전히 수동 연결을 필요로 하는지 사용자에게 알려 줍니다. 즉, 조용히 깨진 코드를 넘기지 않습니다.

모든 기능을 자동으로 연결하고 싶다면 `minimal`이나 `single-module`을 고르세요. 두 프리셋은 기능 플래그를 바탕으로 `main.py`를 다시 생성합니다.
