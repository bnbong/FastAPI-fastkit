# `fastapi-auth-jwt`로 JWT 인증 구현

첫 커밋부터 실제 계정 기능을 갖춘 API를 만들어 봅니다. 이 튜토리얼에서는
`fastapi-auth-jwt` 템플릿을 처음부터 끝까지 따라가면서 토큰 쌍을 발급하고
회전하는 방식, 재사용된 refresh 토큰이 거부되는 이유, 역할(role)과
스코프(scope) 가드가 연결되는 방식, 그리고 SQLite에서 다른 데이터베이스로
옮길 때 무엇이 달라지는지 살펴봅니다.

## 배우는 내용

- `fastkit startdemo fastapi-auth-jwt`로 프로젝트를 생성하는 방법
- access 토큰과 refresh 토큰의 차이, 그리고 토큰 회전(rotation)이 중요한 이유
- `get_current_user`, `get_current_active_superuser`, `require_scopes(...)`가
  라우트를 보호하는 방식
- 비밀번호 해싱이 이루어지는 위치와 argon2id를 사용하는 이유
- 번들된 SQLite 파일에서 Alembic을 사용해 PostgreSQL로 옮기는 방법

## 사전 요구 사항

- Python 3.12+
- FastAPI-fastkit 설치 (`pip install fastapi-fastkit`)
- FastAPI 의존성과 pydantic 스키마를 다루는 데 익숙함

FastAPI 앱을 한 번도 만들어 본 적이 없다면
[기본 API 서버 구축](basic-api-server.md)을 먼저 마치고 돌아오세요. 이
템플릿은 기본 개념을 이미 알고 있다고 가정합니다.

## 1단계: 프로젝트 생성

```console
$ fastkit startdemo fastapi-auth-jwt
Enter the project name: accounts-api
Enter the author name: Developer Kim
Enter the author email: developer@example.com
Enter the project description: Accounts and sessions service
Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y
```

그다음 서버를 실행합니다:

```console
$ cd accounts-api
$ bash scripts/run-server.sh    # 또는: uvicorn src.app.main:app --reload
```

앱은 SQLite(`sqlite:///./app.db`)로 시작하고 시작 시점에 테이블을 직접
생성하므로, 먼저 설치하거나 설정해야 할 것이 없습니다. API 문서는
<http://127.0.0.1:8000/docs>에서 확인할 수 있습니다.

!!! tip "생성하기 전에 미리 보기"
    `fastkit startdemo fastapi-auth-jwt --dry-run`은 아무 파일도 쓰지 않고
    파일 트리와 패키지 목록만 출력합니다. 어떤 결과물을 받게 될지 미리
    확인할 때 유용합니다.

## 2단계: 생성된 트리

```
accounts-api/
├── pyproject.toml              # PEP 621 메타데이터 + [tool.fastapi-fastkit]
├── requirements.txt
├── alembic.ini
├── Dockerfile
├── .env                        # SECRET_KEY, DATABASE_URL, 토큰 수명
├── scripts/
│   ├── format.sh  lint.sh  run-server.sh  test.sh
├── src/
│   └── app/
│       ├── main.py             # FastAPI() + lifespan + CORS + api_router
│       ├── core/
│       │   ├── config.py       # pydantic-settings
│       │   └── security.py     # argon2 해싱 + JWT 인코딩/디코딩
│       ├── db/session.py       # 엔진 + get_session 의존성
│       ├── api/
│       │   ├── router.py       # health와 모든 도메인 라우터를 집계
│       │   ├── health.py       # GET /health
│       │   └── deps.py         # 세션, 현재 사용자, 역할/스코프 가드
│       ├── domains/
│       │   ├── auth/           # 로그인, refresh 회전, 로그아웃
│       │   └── users/          # 회원 가입과 프로필
│       └── alembic/            # 마이그레이션 환경 + versions/
└── tests/
    ├── conftest.py  test_health.py  test_auth.py  test_users.py
```

레이아웃은 `domain-starter`와 같은 형태입니다. 각 도메인은 `router.py`(전송),
`service.py`(비즈니스 로직), `repository.py`(데이터 접근), `models.py`(테이블),
`schemas.py`(API 입출력)를 소유합니다. 인증과 관련된 코드는 `auth/`에,
계정과 관련된 코드는 `users/`에 있으며, 두 도메인은 서로의 내부 구현에
접근하지 않습니다.

## 3단계: 회원 가입, 로그인, 보호된 라우트 호출

```console
# 1. 회원 가입
$ curl -X POST http://127.0.0.1:8000/api/v1/auth/register \
    -H 'Content-Type: application/json' \
    -d '{"email": "alice@example.com", "password": "s3cret-password"}'

# 2. 로그인: 폼 인코딩을 사용한다는 점에 유의하세요. OAuth2 password flow입니다
$ curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
    -d 'username=alice@example.com&password=s3cret-password'
{"access_token": "...", "refresh_token": "...", "token_type": "bearer"}

# 3. 보호된 라우트 호출
$ curl http://127.0.0.1:8000/api/v1/users/me \
    -H "Authorization: Bearer $ACCESS_TOKEN"
```

Swagger의 "Authorize" 버튼도 같은 흐름으로 동작하므로, 브라우저를 벗어나지
않고 `/docs`에서 보호된 라우트를 직접 호출해 볼 수 있습니다.

전체 엔드포인트는 다음과 같습니다:

| 메서드 | 엔드포인트                  | 인증          | 설명                              |
|--------|-----------------------------|---------------|-----------------------------------|
| GET    | `/api/v1/health`            | —             | Liveness probe                    |
| POST   | `/api/v1/auth/register`     | —             | 계정 생성                         |
| POST   | `/api/v1/auth/login`        | —             | OAuth2 password 폼 → 토큰 쌍      |
| POST   | `/api/v1/auth/refresh`      | refresh 토큰  | 새 토큰 쌍으로 회전               |
| POST   | `/api/v1/auth/logout`       | refresh 토큰  | refresh 토큰 하나를 폐기          |
| POST   | `/api/v1/auth/logout-all`   | access 토큰   | 사용자의 모든 세션을 폐기         |
| GET    | `/api/v1/users/me`          | access 토큰   | 현재 사용자의 프로필              |
| PATCH  | `/api/v1/users/me`          | access 토큰   | 현재 사용자의 프로필 수정         |
| GET    | `/api/v1/users/me/scopes`   | 스코프 `me`   | 스코프로 보호되는 예제 라우트     |
| GET    | `/api/v1/users`             | superuser     | 역할로 보호되는 사용자 목록       |

## 4단계: 토큰이 두 개인 이유

로그인하면 토큰 **쌍**이 반환됩니다:

- **access 토큰**은 수명이 짧고(`ACCESS_TOKEN_EXPIRE_MINUTES`, 기본값 30분)
  모든 요청에 함께 전송됩니다. 수명이 짧기 때문에 유출되더라도 금방 쓸 수
  없게 됩니다.
- **refresh 토큰**은 수명이 길고(`REFRESH_TOKEN_EXPIRE_DAYS`, 기본값 14일)
  새 토큰 쌍을 받는 단 한 가지 용도로만 사용됩니다.

여기까지는 특별할 것이 없습니다. 이 템플릿이 흔한 JWT 예제 코드와 다른
점은 refresh 토큰을 **추적하고 회전한다**는 것입니다. 발급되는 모든 refresh
토큰에는 `jti` 클레임이 붙고, 그 `jti`가 데이터베이스에 기록됩니다:

```python
def issue_token_pair(self, user: User) -> TokenPair:
    scopes = user.scope_list
    access_token, _, _ = create_access_token(str(user.id), scopes)
    refresh_token, jti, expires_at = create_refresh_token(str(user.id), scopes)
    self.refresh_tokens.add(jti, user.id or 0, expires_at)
    return TokenPair(access_token=access_token, refresh_token=refresh_token)
```

토큰을 갱신할 때는 새 쌍을 발급하기 **전에** 제출된 토큰을 먼저 폐기합니다:

```python
def rotate(self, refresh_token: str) -> TokenPair:
    payload = decode_token(refresh_token, REFRESH_TOKEN_TYPE)
    record = self.refresh_tokens.get_by_jti(str(payload.get("jti")))
    if record is None or record.revoked:
        raise TokenError("refresh token is no longer valid")
    ...
    self.refresh_tokens.revoke(record)
    return self.issue_token_pair(user)
```

직접 확인해 보세요. 한 번 갱신한 다음, *이전* refresh 토큰을 다시 보내 봅니다.

```console
$ curl -X POST http://127.0.0.1:8000/api/v1/auth/refresh \
    -H 'Content-Type: application/json' \
    -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}"
# → 새 토큰 쌍

$ curl -X POST http://127.0.0.1:8000/api/v1/auth/refresh \
    -H 'Content-Type: application/json' \
    -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}"
# → 401: 토큰은 사용된 순간 무효화되었습니다
```

바로 이 한 가지 성질 덕분에, 탈취된 refresh 토큰이 영구적인 백도어가 되지
않고 한 번만 쓸 수 있으며 탐지 가능한 실패로 끝납니다.

로그아웃도 같은 방식으로 동작합니다. 이것 역시 일반적인 JWT 구성에서는
대개 할 수 없는 기능입니다. `POST /auth/logout`은 토큰 하나를 폐기하고,
`POST /auth/logout-all`은 해당 사용자에게 속한 모든 refresh 토큰을
폐기합니다.

## 5단계: 비밀번호

해싱은 `src/app/core/security.py`에서 이루어지며, `pwdlib`을 통해
**argon2id**를 사용합니다. argon2id는 레거시 bcrypt 구성이 아니라 현재
권장되는 기본값입니다. 라우터와 서비스는 비밀번호를 검증하는 순간을 제외하면
평문 비밀번호를 볼 일이 없고, `hashed_password`는 어떤 응답 스키마에도
포함되지 않습니다.

여기에서는 따로 설정할 것이 없습니다. 여러분이 *반드시* 설정해야 하는 것은
서명 키 하나뿐입니다.

## 6단계: 역할과 스코프

FastAPI 의존성 형태로 세 가지 가드가 제공됩니다:

```python
CurrentUser = Annotated[User, Depends(get_current_user)]
```

- **`get_current_user`**는 bearer access 토큰을 디코딩해 사용자를 불러오고,
  비활성 계정은 `403`으로 거부합니다. 형식이 잘못되었거나, 만료되었거나,
  삭제된 사용자를 가리키는 토큰은 모두 `401`을 반환합니다.
- **`get_current_active_superuser`**는 그 위에 `is_superuser` 검사를 한 단계
  더 얹습니다. `GET /api/v1/users`가 이 가드를 사용합니다.
- **`require_scopes(...)`**는 특정 스코프를 요구하는 의존성을 만들어 줍니다:

```python
from fastapi import Depends
from src.app.api.deps import require_scopes

@router.get("/reports", dependencies=[Depends(require_scopes("reports"))])
def read_reports() -> list[str]:
    ...
```

스코프는 사용자 행(row)에 쉼표로 구분된 문자열(`scopes: str`)로 저장되고,
`scope_list` 프로퍼티를 통해 다시 읽히며, 발급되는 모든 토큰에 복사됩니다.
스타터 템플릿에서 동작하는 가장 단순한 방식을 의도적으로 택한 것입니다.
권한 모델이 문자열 하나로 감당할 수 없을 만큼 커지면, 이 컬럼을 역할
테이블로 바꾸고 의존성 시그니처는 그대로 유지하세요. 그러면 라우터 쪽은
아무것도 옮길 필요가 없습니다.

## 7단계: 보호된 도메인 추가

예를 들어 로그인한 사용자만 접근할 수 있는 `orders` 도메인을 추가하려면
다음과 같이 진행합니다:

1. `users/`와 같은 구조로 `src/app/domains/orders/`를 만듭니다
   (`models.py`, `schemas.py`, `repository.py`, `service.py`, `router.py`).
2. 계정이 필요한 라우트에서는 `CurrentUser`를 매개변수로 받거나, 라우터에
   `Depends(require_scopes("orders"))`를 붙입니다.
3. `src/app/api/router.py`의 `# fastkit:routes` 앵커 위에 라우터를 등록합니다.
   `fastkit addroute`도 같은 앵커에 코드를 쓰기 때문에, 직접 작성한 라우트와
   생성된 라우트가 한곳에 모입니다.
4. 마이그레이션을 생성합니다: `alembic revision --autogenerate -m "add orders"`.
5. 새 엔드포인트용으로 `tests/test_users.py`와 같은 형태의 테스트를 작성합니다.

## 8단계: 지금은 SQLite, 나중에는 PostgreSQL

기본 `DATABASE_URL`은 로컬 SQLite 파일이며, 앱은 시작할 때
`create_db_and_tables()`를 호출합니다. 그래서 `pytest`와 `uvicorn` 모두 별도
설정 없이 동작합니다. 로컬 개발을 넘어서는 환경에서는 Alembic이 스키마를
관리하도록 맡기세요:

```console
$ export DATABASE_URL='postgresql+psycopg://postgres:postgres@localhost:5432/app_db'
$ alembic upgrade head
```

모델을 변경한 뒤에는 다음 명령을 실행합니다:

```console
$ alembic revision --autogenerate -m "add profile fields"
```

## 9단계: 배포 전에

`.env`에 있는 두 설정이 이 앱을 데모로 둘지 실제 서비스로 쓸지를 결정합니다:

- **`SECRET_KEY`**는 모든 토큰에 서명합니다. 값을 설정하지 않으면 프로세스마다
  임의의 키가 생성됩니다. 그러면 재시작할 때마다 모든 사용자가 로그아웃되고,
  워커가 여러 개일 때 워커마다 유효한 토큰을 다르게 판단하게 됩니다. 키를
  하나 생성해 고정해 두세요:

  ```console
  $ python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```

- **`DATABASE_URL`**은 사용할 데이터베이스를 선택합니다. 기본값인 SQLite는
  프로덕션용 저장소가 아닙니다.

필요하다면 `FIRST_SUPERUSER_EMAIL`과 `FIRST_SUPERUSER_PASSWORD`를 설정해
시작 시점에 superuser 계정을 미리 만들어 둘 수 있고, `BACKEND_CORS_ORIGINS`에
프런트엔드 origin 목록을 쉼표로 구분해 지정할 수 있습니다.

## 10단계: 테스트

```console
$ bash scripts/test.sh    # 또는: pytest
```

테스트 스위트는 인메모리 SQLite 데이터베이스를 대상으로 `httpx.AsyncClient`를
실행합니다. 회원 가입 → 로그인 → me → 갱신 → 로그아웃으로 이어지는 정상
경로 전체와, 실제로 중요한 거부 경로(잘못된 비밀번호, 형식이 잘못된 토큰,
만료된 토큰, 4단계에서 다룬 재사용된 refresh 토큰)를 검증합니다. 인증 규칙을
확장할 때는 이 거부 테스트부터 먼저 확장하세요. 망가진 가드를 잡아내는
테스트가 바로 이 테스트들입니다.

## 정리

- **생성**: `fastkit startdemo fastapi-auth-jwt` →
  `bash scripts/run-server.sh` → `/docs`에서 문서 확인.
- **토큰**: 요청에는 수명이 짧은 access 토큰을 사용하고, refresh 토큰은
  `jti`로 추적하며 회전시키므로 재사용이 실패하고 로그아웃이 실제로
  동작합니다.
- **가드**: `get_current_user`, `get_current_active_superuser`,
  `require_scopes(...)`를 일반 의존성으로 사용합니다.
- **저장소**: SQLite는 설정 없이 바로 쓸 수 있고, PostgreSQL은
  `DATABASE_URL`을 설정하고 `alembic upgrade head`를 실행하면 됩니다.
- **배포 전**: `SECRET_KEY`를 고정하고, `DATABASE_URL`이 실제 데이터베이스를
  가리키도록 설정합니다.

## 다음 단계

- [SQLModel 영속성](sqlmodel.md): 같은 도메인 레이아웃을 바탕으로 비동기 데이터
  접근, 마이그레이션, 제네릭 CRUD에 집중합니다.
- [도메인 지향 프로젝트](domain-starter.md): 이 템플릿의 기반이 되는
  레이아웃을 인증 기능 없이 다룹니다.
- [어떤 스타터를 선택해야 할까?](../user-guide/choosing-a-starter.md): 이
  템플릿을 다른 템플릿과 비교합니다.
