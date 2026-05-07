# 어떤 스타터를 선택해야 할까?

FastAPI-fastkit은 프로젝트를 시작하는 여러 가지 방법을 제공합니다. 이 페이지는 처음 쓰는 분을 위한 **선택 가이드**입니다. 여기서 방향을 정한 뒤, 실제 프로젝트 생성은 [퀵 스타트](quick-start.md)로 넘어가 진행하세요.

확신이 없다면, 답은 다음과 같습니다:

> **`fastkit init --interactive`로 시작해서 `domain-starter` 프리셋을 선택하세요.** 현재 권장 기본값입니다.

이 페이지의 나머지 부분은 그 이유와, 다른 선택을 해야 할 경우를 설명합니다.

## TL;DR — 사용자 유형별 선택

| 당신이... | 시작점 |
|---|---|
| FastAPI가 처음이고 가이드를 따라 차근차근 시작하고 싶다 | `fastkit init --interactive` (preset: **`domain-starter`**) |
| 동작하는 CRUD 데모를 읽고 수정하면서 배우고 싶다 | `fastkit startdemo fastapi-default` |
| 가능한 가장 작은 스캐폴드를 원한다 | `fastkit init --interactive` (preset: **`minimal`**) |
| 빠른 프로토타입 / 단일 파일 스크립트를 작성한다 | `fastkit init --interactive` (preset: **`single-module`**) |
| 실제 데이터베이스가 필요하다 (PostgreSQL + SQLAlchemy + Alembic) | `fastkit startdemo fastapi-psql-orm` |
| 중간 규모 API에 어울리는 실전형 도메인 레이아웃을 원한다 | `fastkit init --interactive` (preset: **`domain-starter`**) |

## `startdemo`와 `init --interactive`는 무엇이 다른가?

이 둘이 메인 진입점이며, 서로 다른 용도를 갖습니다.

### `fastkit startdemo <template>`

기본 제공 템플릿(`fastapi-default`, `fastapi-async-crud`, `fastapi-psql-orm`, `fastapi-domain-starter`, ...) 가운데 하나를 바탕으로 **바로 실행해 볼 수 있는 완성형 예제 프로젝트**를 디스크에 생성합니다. 템플릿의 소스 코드는 거의 그대로 복사되고, 메타데이터 플레이스홀더(`<project_name>` 등)만 치환됩니다.

- ✅ 실행 가능한 데모까지 가장 빠른 경로.
- ✅ 모든 코드가 실제로 동작하고 읽기 쉬워, 예제로 학습하기에 좋음.
- ❌ 템플릿의 스택과 구조가 고정되어 있어, 생성 시점에 "CORS 만 켜고 인증은 빼는" 식의 조합은 불가능.

```console
$ fastkit list-templates              # 사용 가능한 템플릿 표시
$ fastkit startdemo fastapi-default   # 그중 하나로 프로젝트 생성
```

### `fastkit init --interactive`

**대화형 마법사**를 따라 진행합니다. 프로젝트 메타데이터 → 아키텍처 프리셋 → 기능 선택(데이터베이스, 인증, 테스트, 배포, ...) → 패키지 매니저 → 확인 순서로 이어집니다. 생성기는 프리셋별로 적절한 베이스 템플릿을 고르고, 그 위에 선택한 기능을 덧입힙니다.

- ✅ 실제로 원하는 스택을 직접 조립할 수 있음.
- ✅ 아키텍처 프리셋이 프로젝트 레이아웃(단일 파일, 계층형, 도메인 지향, ...)을 결정.
- ❌ `main.py`를 보존하는 프리셋(`classic-layered`, `domain-starter`)은 설정 모듈까지는 만들어 주지만, 해당 모듈을 라우터에 연결하는 작업은 사용자가 직접 해야 함. 프리셋과 기능 조합별 동작은 [아키텍처 프리셋 매트릭스](../reference/preset-feature-matrix.md)를 참고하세요.

```console
$ fastkit init --interactive
```

## 네 가지 아키텍처 프리셋

이 프리셋들은 `fastkit init --interactive` 의 프로젝트 정보 입력 다음 단계에서 나타납니다. 어떤 프리셋을 고를지 결정할 때 이 섹션을 사용하세요.

### `minimal` — 가장 단순하게 시작, 나중에 키우기

가장 작은 동작 가능한 FastAPI 앱. 빈 스캐폴드 + 선택한 기능 플래그로부터 재생성된 단일 `src/main.py` 입니다. CORS, 레이트 제한, Prometheus 계측은 선택 시 자동으로 `main.py` 에 연결됩니다.

- 👤 **대상**: 프로젝트가 자라면서 직접 구조를 잡고 싶거나, 특정 레이아웃에 얽매이지 않고 FastAPI를 탐색해 보고 싶은 사람.
- 📦 **베이스 템플릿**: `fastapi-empty`.
- 🧠 **이렇게 이해하면 쉽습니다**: "FastAPI를 import한 단일 파일 하나만 받고, 나머지는 내가 채워 넣는다."

### `single-module` — 스크립트형 프로토타입

모든 코드가 한 모듈 안에 존재합니다. `minimal` 과 동일하게 `main.py` 가 재생성되는 오버레이를 사용합니다.

- 👤 **대상**: 글루 스크립트, 작은 webhook, 또는 패키지 경계가 필요 없는 하루짜리 프로토타입.
- 📦 **베이스 템플릿**: `fastapi-single-module`.
- 🧠 **이렇게 이해하면 쉽습니다**: "한 번에 실행하고 한 번에 다 읽을 수 있는 Python 파일 하나면 충분하다."

### `classic-layered` — 계층형 분할 (api / crud / schemas / core)

"Django 풍" 레이아웃 — 코드를 관심사별로 수평 분할합니다: 라우터는 모두 `api/`, CRUD 로직은 모두 `crud/`, pydantic 스키마는 모두 `schemas/`, 설정은 모두 `core/`. 기본 제공된 `main.py` 는 **보존**되며 (이미 CORS 연결이 되어 있음), 생성된 데이터베이스/인증 설정 파일은 `src/core/` 아래에 배치됩니다.

- 👤 **대상**: Django/Rails 풍 레이아웃에 익숙한 팀, 공통 CRUD 배관을 공유하는 작은 엔드포인트가 많은 프로젝트.
- 📦 **베이스 템플릿**: `fastapi-default`.
- 🧠 **이렇게 이해하면 쉽습니다**: "코드를 *무엇을 담당하는지* 기준으로 나눈다."

### `domain-starter` — 도메인 지향 (권장 기본값)

코드를 **비즈니스 개념별**로 수직 분할합니다: 각 도메인은 자신의 router, service, repository, schemas 를 `src/app/domains/<concept>/` 아래에 소유합니다. `/health` 엔드포인트와, 새 개념마다 복사해 이름만 바꾸면 되는 `items` 예제 도메인이 함께 제공됩니다. 기본 제공된 `main.py` (`src/app/` 아래) 는 보존되며, 생성된 설정 파일은 `src/app/core/` 아래에 배치됩니다.

- 👤 **대상**: users, orders, billing처럼 여러 비즈니스 개념이 함께 자라날 중간 규모 API. 현재 권장 기본값.
- 📦 **베이스 템플릿**: `fastapi-domain-starter`.
- 🧠 **이렇게 이해하면 쉽습니다**: "코드를 *비즈니스적으로 무엇을 하는지* 기준으로 나눈다."

## 비교 매트릭스

한눈에 보는 비교표.

| | `minimal` | `single-module` | `classic-layered` | `domain-starter` |
|---|---|---|---|---|
| 베이스 템플릿 | `fastapi-empty` | `fastapi-single-module` | `fastapi-default` | `fastapi-domain-starter` |
| 프로젝트 진입점 | `src/main.py` | `src/main.py` | `src/main.py` | `src/app/main.py` |
| 라우터 위치 | (직접 추가) | (`main.py` 안) | `src/api/routes/` | `src/app/domains/<concept>/router.py` |
| 도메인별 폴더 | ❌ | ❌ | ❌ | ✅ |
| 내장 `/health` 엔드포인트 | ✅ | ✅ | ❌ | ✅ |
| 기능에서 `main.py` 재생성 | ✅ | ✅ | ❌ | ❌ |
| `main.py` 에 CORS 사전 연결 | 선택 시 추가 | 선택 시 추가 | 예 (env 기반) | 예 (env 기반) |
| pyproject 우선 | 선택 사항 | 선택 사항 | 선택 사항 | ✅ |
| 적합한 경우 | "구조는 내가 키운다" | "한 파일 프로토타입" | "관심사로 분할" | "비즈니스 개념으로 분할" |

기능별 전체 계약(데이터베이스 / 인증 설정 파일 경로, 어떤 선택이 자동 연결되고 어떤 선택은 수동 연결이 필요한지, 경고가 언제 발생하는지)은 [아키텍처 프리셋 매트릭스](../reference/preset-feature-matrix.md)를 참고하세요.

## `startdemo` 템플릿 선택하기

`fastkit startdemo <template>`는 기능을 직접 조합하는 방식보다 **완성된 실행 예제**가 필요할 때 가장 잘 맞습니다. 대부분의 템플릿은 위 네 가지 프리셋 중 하나와 대략 대응하지만, 목 스토어 기반 CRUD 엔드포인트, 응답 포매팅 예제, Docker 도구처럼 추가 예제 코드도 함께 제공합니다.

| 템플릿 | 가장 가까운 프리셋 | 선택 시점 |
|---|---|---|
| `fastapi-default` | `classic-layered` | 계층형 레이아웃 위의 동작하는 CRUD 데모. 좋은 첫 출발점. |
| `fastapi-empty` | `minimal` | 빈 스캐폴드. `minimal` 이 도달하는 모양과 동일. |
| `fastapi-single-module` | `single-module` | 단일 파일 데모. |
| `fastapi-domain-starter` | `domain-starter` | 현재 권장 기본값. items 도메인 예제 포함. |
| `fastapi-async-crud` | `classic-layered` | `fastapi-default` 의 비동기 버전. |
| `fastapi-custom-response` | `classic-layered` | 커스텀 응답 envelope / 포매팅을 보여줌. |
| `fastapi-dockerized` | `classic-layered` | 기본 레이아웃에 프로덕션 수준의 Dockerfile 추가. |
| `fastapi-psql-orm` | (직접 대응 프리셋 없음) | PostgreSQL + SQLAlchemy + Alembic. 실제 데이터베이스가 필요할 때. |
| `fastapi-mcp` | (직접 대응 프리셋 없음) | Model Context Protocol 통합. |

`fastkit list-templates` 는 한 줄 설명과 함께 현재 템플릿 목록을 보여줍니다.

## 자주 묻는 질문

**Q. 프리셋 / 템플릿을 미리 결정해야 하나요?**
아닙니다 — 생성된 코드는 나중에 손으로 자유롭게 재구성할 수 있습니다. 프리셋은 출발점일 뿐 계약이 아닙니다. 너무 깊게 고민하지 마세요.

**Q. 지금 추천하는 기본 선택은 무엇인가요?**
`domain-starter`입니다. pyproject를 우선으로 사용하고, `/health` 엔드포인트가 기본으로 들어 있으며, 관리가 쉬운 중간 규모 FastAPI 프로젝트 구조를 자연스럽게 따라갑니다.

**Q. 나중에 `classic-layered` 에서 `domain-starter` 로 바꿀 수 있나요?**
네, 단 마이그레이션 명령은 없으며 수동 리팩터링이 필요합니다. 프로젝트가 자라서 도메인 폴더가 필요해질 거라고 판단되면 처음부터 `domain-starter` 로 시작하세요.

**Q. 그냥 FastAPI를 학습하고 싶다면요?**
`fastkit startdemo fastapi-default`로 시작하세요. 코드를 읽고, 테스트를 실행하고, 엔드포인트 몇 개를 직접 바꿔 보세요. 익숙해지면 `fastkit init --interactive`의 `domain-starter` 프리셋으로 넘어가는 것이 자연스러운 다음 단계입니다.

**Q. 각 프리셋이 정확히 어떤 파일을 생성하는지는 어디서 보나요?**
[아키텍처 프리셋 매트릭스](../reference/preset-feature-matrix.md) 가 그 레퍼런스 페이지입니다.

## 다음 단계

- [퀵 스타트](quick-start.md) — 실제로 첫 프로젝트를 만들어 봅니다.
- [프로젝트 생성](creating-projects.md) — CLI 플래그를 더 깊이 다루는 안내.
- [도메인 지향 프로젝트 튜토리얼](../tutorial/domain-starter.md) — `domain-starter`를 골랐다면, 생성된 트리와 번들된 `items` 예제, 다음 도메인을 추가하는 방법까지 전체 흐름을 따라가며 설명합니다.
- [아키텍처 프리셋 매트릭스](../reference/preset-feature-matrix.md) — 프리셋별/기능별 전체 계약.
