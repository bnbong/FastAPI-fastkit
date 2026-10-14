# `fastapi-llm-agent`로 스트리밍 LLM 에이전트 구현

토큰이 생성되는 대로 스트리밍하고, 실제로 무언가를 *수행*할 수 있는 채팅
백엔드를 만들어 봅니다. 이 백엔드는 도구를 호출하고, 그 결과를 읽고, 이어서
작업을 계속할 수 있습니다. 이 튜토리얼에서는 `fastapi-llm-agent` 템플릿을
따라가면서 SSE 이벤트 프로토콜, 도구 호출 루프와 반복 횟수 상한, 인터페이스
뒤에 둔 대화 메모리, 그리고 네트워크에 전혀 접근하지 않는 테스트 스위트를
살펴봅니다.

## 배우는 내용

- `fastkit startdemo fastapi-llm-agent`로 프로젝트를 생성하는 방법
- 클라이언트가 처리해야 하는 SSE 이벤트 타입과 각 이벤트의 의미
- 도구 호출 루프의 한 턴이 단계별로 동작하는 방식
- 직접 도구를 추가하는 방법
- 프로세스 내부 대화 저장소를 실제 저장소로 교체하는 방법
- 테스트가 결정적(deterministic)이고 비용 없이 실행되는 이유

## 사전 요구 사항

- Python 3.12+
- FastAPI-fastkit 설치 (`pip install fastapi-fastkit`)
- Anthropic API 키: 실제 모델과 통신할 때만 필요합니다. 생성된 테스트
  스위트는 키 없이 실행됩니다.
- `async`/`await`와 비동기 제너레이터에 익숙함

## 1단계: 생성과 설정

```console
$ fastkit startdemo fastapi-llm-agent
Enter the project name: support-agent
Enter the author name: Developer Kim
Enter the author email: developer@example.com
Enter the project description: Streaming support assistant
Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y
```

처음 실행하기 전에 `.env`에 키를 넣어 두세요:

```bash
ANTHROPIC_API_KEY=sk-ant-...
LLM_MODEL=claude-sonnet-5
LLM_MAX_TOKENS=4096
MAX_TOOL_ITERATIONS=5
```

키는 pydantic-settings가 읽어서 클라이언트를 생성할 때 전달합니다. 소스
코드에 기록되지 않으며, Docker 이미지에도 포함되지 않습니다.

```console
$ cd support-agent
$ bash scripts/run-server.sh
$ bash scripts/chat.sh "What is 12 * 34?"
```

!!! tip "Anthropic API 대신 게이트웨이 사용하기"
    `LLM_BASE_URL`(게이트웨이가 bearer 인증을 사용한다면 `LLM_AUTH_TOKEN`도)을
    설정하면 LiteLLM, 사내 프록시, 로컬 서버를 가리키게 할 수 있습니다.
    통신 형식은 그대로 Anthropic Messages API를 사용합니다. 다른 제공자에
    맞게 변환하는 일은 앱이 아니라 게이트웨이가 담당합니다.

## 2단계: 생성된 트리

```
support-agent/
├── pyproject.toml              # PEP 621 메타데이터 + [tool.fastapi-fastkit]
├── requirements.txt
├── Dockerfile
├── .env
├── scripts/
│   ├── chat.sh                 # 실행 중인 서버에 메시지 하나 전송
│   ├── format.sh  lint.sh  run-server.sh  test.sh
├── src/
│   └── app/
│       ├── main.py             # FastAPI 앱 + lifespan
│       ├── core/config.py      # pydantic-settings (API 키를 여기서 읽음)
│       ├── llm/
│       │   ├── client.py       # AsyncAnthropic 팩토리
│       │   ├── tools.py        # 도구 스키마 + 핸들러
│       │   └── agent.py        # 스트리밍 에이전트 + 도구 루프
│       ├── memory/
│       │   ├── base.py         # ConversationStore 인터페이스
│       │   └── in_memory.py    # 프로세스 로컬 구현
│       ├── schemas/chat.py     # 요청 본문 + SSE 이벤트 엔벨로프
│       └── api/
│           ├── router.py       # health와 chat을 집계
│           ├── deps.py         # 저장소 / 에이전트 의존성
│           ├── health.py       # GET /health
│           └── chat.py         # POST /chat (SSE), 대화 기록
└── tests/
    ├── conftest.py             # 시나리오대로 응답하는 가짜 Anthropic 클라이언트
    ├── test_health.py  test_chat.py  test_tools.py  test_memory.py
```

먼저 눈여겨볼 경계가 세 가지 있습니다. **클라이언트**는 팩토리로 생성되므로
테스트에서 다른 클라이언트로 바꿔 넣을 수 있습니다. **메모리**는 단순한 구현을
갖춘 인터페이스이므로 프로덕션에서 다른 구현으로 바꿔 넣을 수 있습니다.
**도구**는 스키마 목록과 핸들러 딕셔너리로 구성되므로 도구를 추가할 때 파일
하나만 수정하면 됩니다.

## 3단계: 엔드포인트

| 메서드 | 엔드포인트                   | 설명                    |
|--------|------------------------------|-------------------------|
| GET    | `/api/v1/health`             | Liveness probe          |
| POST   | `/api/v1/chat`               | 응답을 SSE로 스트리밍   |
| GET    | `/api/v1/conversations/{id}` | 저장된 대화 기록 조회   |
| DELETE | `/api/v1/conversations/{id}` | 대화 삭제               |

`POST /api/v1/chat`은 `{"message": "...", "conversation_id": "..."}`를 받습니다.
새 대화를 시작하려면 `conversation_id`를 생략하고, 마지막 `done` 이벤트에서
부여된 id를 읽어 오세요.

## 4단계: 스트림 프로토콜

각 SSE 메시지는 `event:` 필드에 타입을, `data:`에 JSON 엔벨로프를 담습니다.
클라이언트는 다섯 가지 이벤트와 오류 이벤트를 처리해야 합니다:

| 이벤트        | 필드                            | 의미                           |
|---------------|---------------------------------|--------------------------------|
| `token`       | `text`                          | 어시스턴트 응답의 일부 조각    |
| `tool_use`    | `tool_name`, `tool_input`       | Claude가 도구 호출을 요청함    |
| `tool_result` | `tool_name`, `tool_output`      | 도구가 실행됨                  |
| `usage`       | `input_tokens`, `output_tokens` | 턴마다 사용한 토큰 양          |
| `done`        | `conversation_id`               | 턴이 끝남                      |
| `error`       | `detail`                        | 스트리밍 도중 오류가 발생함    |

`tool_use`와 `tool_result`는 장식용 이벤트가 아닙니다. 이 이벤트가 있어야
UI가 도구가 실행되는 동안 설명 없이 멈춰 있지 않고 "검색 중…" 같은 상태를
표시할 수 있습니다.

토큰 사용량은 턴마다 `app.agent` 로거에도 기록되므로, 클라이언트를 따로
계측하지 않아도 서버 로그에서 사용량을 확인할 수 있습니다.

## 5단계: 루프의 한 턴

`src/app/llm/agent.py`에 있는 `ChatAgent.stream`이 엔진의 전부입니다. 한
턴은 다음과 같이 진행됩니다:

1. 저장소에서 대화 기록을 불러옵니다.
2. 대화 기록, 새 사용자 메시지, 도구 스키마를 담아 스트리밍 요청을 엽니다.
3. 텍스트 조각이 도착할 때마다 `token` 이벤트로 내보냅니다.
4. 스트림이 끝나면 최종 메시지를 읽고, `usage` 이벤트를 내보낸 뒤 토큰 수를
   로그로 기록합니다.
5. **`stop_reason != "tool_use"`라면** 어시스턴트의 응답이 끝난 것입니다. 턴을
   저장하고 `done`을 내보낸 뒤 반환합니다.
6. **그렇지 않다면** 각 `tool_use` 블록마다 `tool_use`를 내보내고, 핸들러를
   실행하고, `tool_result`를 내보낸 뒤 출력을 모읍니다.
7. 모든 도구 결과를 하나의 `user` 메시지로 묶어 다시 보냅니다. Messages API가
   이 형식을 요구하기 때문입니다. 그다음 2단계부터 다시 반복합니다.

루프는 `MAX_TOOL_ITERATIONS`(기본값 5)로 제한됩니다. Claude가 상한을 넘어서도
계속 도구를 요청하면, 서버가 끝없이 루프를 도는 대신 턴을 저장하고 경고를
로그로 남긴 뒤 `error` 이벤트를 내보냅니다:

```python
yield AgentEvent(
    type="error",
    detail=(
        "The assistant exceeded the tool-call limit of "
        f"{self._max_tool_iterations} iterations."
    ),
)
```

에이전트 루프에서 이런 상한은 선택 사항이 아닙니다. 상한이 없으면 도구
결과를 잘못 이해한 모델이 끝없이 비용을 발생시킬 수 있습니다.

## 6단계: 번들된 도구

| 도구           | 용도                                                     |
|----------------|----------------------------------------------------------|
| `calculator`   | 산술 계산. `eval`이 아니라 AST로 파싱한 뒤 허용 목록으로 검사 |
| `current_time` | IANA 시간대 기준의 현재 시각                              |

`calculator`는 한 번 더 살펴볼 만합니다. 이 도구는 `ast`로 수식을 파싱하고
허용 목록에 있는 노드 타입만 순회하므로, 모델이 넘긴 도구 인자로 임의의
Python 코드를 실행할 수 없습니다. 모델이 생성한 입력을 받는 도구라면 모두
같은 원칙을 지켜야 합니다. **모델의 출력은 신뢰할 수 없는 입력입니다.**

### 도구 추가

필요한 코드는 모두 `src/app/llm/tools.py`에 있습니다:

1. `TOOL_SCHEMAS`에 스키마를 추가합니다. 스키마에는 `name`, `description`,
   JSON Schema 형식의 `input_schema`가 들어갑니다.
2. 같은 이름으로 `TOOL_HANDLERS`에 핸들러를 등록합니다.

제대로 챙겨야 할 점이 두 가지 있습니다:

- **description은 Claude가 언제 이 도구를 사용해야 하는지 판단할 때 받는
  유일한 지시입니다.** 즉 문서가 아니라 프롬프트 엔지니어링에 해당합니다.
  설명이 모호하면 도구가 전혀 호출되지 않거나, 반대로 끊임없이 호출됩니다.
- **핸들러는 문자열을 반환해야 하고, 자신의 실패는 예외를 던지는 대신 읽을 수
  있는 메시지로 바꿔야 합니다.** 루프는 이 텍스트를 그대로 모델에 다시
  전달합니다. 그래서 "X라는 도시를 찾을 수 없습니다" 같은 메시지를 받으면
  모델이 상황을 복구할 수 있지만, 예외가 발생하면 턴이 끝나 버립니다.

## 7단계: 대화 메모리

`ConversationStore`(`src/app/memory/base.py`)는 인터페이스이고, 번들된
`in_memory.py`는 딕셔너리로 이를 구현합니다. 단일 프로세스에서는 충분하지만
그 밖의 환경에서는 적합하지 않습니다. 재시작하면 모든 내용이 사라지고,
워커가 둘 이상이면 워커마다 대화 기록이 서로 달라집니다.

실제 환경에서 쓰려면 같은 인터페이스를 Redis나 데이터베이스 기반으로 구현하고,
`src/app/api/deps.py`의 `get_store()`에서 그 구현을 반환하도록 바꾸세요.
에이전트와 라우터 모두 구체 클래스를 직접 참조하지 않으므로, 두 곳 모두
수정할 필요가 없습니다.

## 8단계: 테스트

```console
$ bash scripts/test.sh    # 또는: pytest
```

`tests/conftest.py`는 `AsyncAnthropic.messages.stream`을 흉내 내는 가짜
클라이언트로 미리 작성한 시나리오의 턴을 재생합니다. 그래서 테스트 스위트는
결정적으로 동작하고, 오프라인에서 실행되며, 비용이 들지 않습니다. 그러면서도
중요한 경로는 모두 검증합니다. 스트리밍 경로와 전체 도구 루프를 다루며,
도구를 호출한 뒤 모델이 답변하는 턴도 포함합니다.

에이전트를 확장할 때도 이 패턴을 유지하세요. 실제 모델을 대상으로 LLM 통합을
테스트하면 테스트 스위트가 느리고, 불안정하고, 비싸지며, 그런데도 모델이 무슨
말을 할지는 검증할 수 없습니다. 시나리오를 따르는 클라이언트로 *루프*를
테스트하면 여러분이 작성한 코드를 정확히 검증할 수 있습니다.

## 9단계: 확장 지점

- **영구적인 대화 기록**: Redis나 데이터베이스 기반으로 `ConversationStore`를
  구현합니다(7단계).
- **RAG**: 템플릿은 의도적으로 검색(retrieval) 기능을 범위에서 제외했습니다.
  자연스러운 확장 지점은 `ChatAgent.stream`입니다. 첫 요청 전에 컨텍스트를
  가져와 시스템 프롬프트 앞에 붙이거나, 인덱스를 도구 하나로 노출해 모델이
  검색할 시점을 결정하게 할 수 있습니다.
- **인증과 레이트 제한**: 기본 제공되는 `POST /chat`에는 인증이 없습니다. 공개적으로
  노출하기 전에 라우터에 의존성을 추가하세요. 재사용할 수 있는 가드는
  [JWT 인증 튜토리얼](auth-jwt.md)에 있습니다.

## 정리

- **생성**: `fastkit startdemo fastapi-llm-agent`, `ANTHROPIC_API_KEY` 설정,
  `bash scripts/run-server.sh`.
- **스트리밍**: `token` / `tool_use` / `tool_result` / `usage` / `done` /
  `error` 이벤트를 사용하는 SSE.
- **루프**: 스트리밍 → 도구 호출 → 결과를 하나의 user 메시지로 반환 → 반복.
  반복 횟수는 `MAX_TOOL_ITERATIONS`로 제한됩니다.
- **도구**: `TOOL_SCHEMAS`에 스키마를, `TOOL_HANDLERS`에 핸들러를 추가합니다.
  도구 입력은 신뢰할 수 없는 값으로 취급합니다.
- **메모리**: `ConversationStore` 인터페이스와 딕셔너리 구현을 제공하며,
  `get_store()`에서 교체합니다.
- **테스트**: 시나리오를 따르는 가짜 클라이언트를 사용하므로 테스트 스위트가
  오프라인에서 결정적으로 동작합니다.

## 다음 단계

- [MCP 통합](mcp-integration.md): 채팅 에이전트가 아니라 MCP 서버가 필요할 때
  참고하세요.
- [JWT 인증](auth-jwt.md): 채팅 엔드포인트 앞에 계정 기능을 추가합니다.
- [어떤 스타터를 선택해야 할까?](../user-guide/choosing-a-starter.md)
