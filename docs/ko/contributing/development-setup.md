# 개발 환경 설정

FastAPI-fastkit에 기여하기 위한 개발 환경 준비 가이드입니다.

## 사전 요구 사항

시작하기 전에 다음을 갖춰 두세요:

- **Python 3.12 이상** 설치
- **Git** 설치 및 설정 완료
- Python과 FastAPI에 대한 **기초 지식**
- **텍스트 에디터 또는 IDE** (VS Code, PyCharm 등)

## Makefile로 빠르게 설정하기

FastAPI-fastkit은 개발 환경을 손쉽게 준비할 수 있도록 Makefile을 제공합니다:

<div class="termy">

```console
$ git clone https://github.com/bnbong/FastAPI-fastkit.git
$ cd FastAPI-fastkit
$ make install-dev
Setting up development environment...
Creating virtual environment...
Installing dependencies...
Installing pre-commit hooks...
✅ Development environment ready!
```

</div>

이 명령 하나로 다음 작업이 함께 이뤄집니다:

- 개발 의존성과 함께 패키지를 `editable` 모드로 설치
- pre-commit 훅 설정
- 개발 도구 구성

!!! note

    이 명령을 실행하기 전에 가상 환경을 만들어 활성화해 두세요.

## 수동 설정

직접 설정하고 싶거나 사용 중인 환경에서 Makefile이 동작하지 않는다면:

### 1. 저장소 clone

<div class="termy">

```console
$ git clone https://github.com/bnbong/FastAPI-fastkit.git
$ cd FastAPI-fastkit
```

</div>

### 2. 가상 환경 생성

<div class="termy">

```console
$ python -m venv .venv
$ source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

</div>

### 3. 의존성 설치

<div class="termy">

```console
# 개발 의존성과 함께 editable 모드로 패키지 설치
$ pip install -e ".[dev]"

# 또는 requirements 파일로 설치
$ pip install -r requirements.txt
$ pip install -r requirements-dev.txt
```

</div>

### 4. Pre-commit 훅 설정

<div class="termy">

```console
$ pre-commit install
pre-commit installed at .git/hooks/pre-commit
```

</div>

### 5. 설치 확인

<div class="termy">

```console
$ fastkit --version
fastapi-fastkit, version 1.2.1

$ python -m pytest tests/
======================== test session starts ========================
collected 45 items
tests/test_cli.py::test_init_command PASSED
tests/test_templates.py::test_template_listing PASSED
...
======================== 45 passed in 2.34s ========================
```

</div>

## 개발 도구

개발 환경에는 코드 품질을 유지하기 위한 여러 도구가 포함돼 있습니다:

### 한 번에 실행하는 명령

Makefile 사용:

```console
$ make format lint
Running isort...
Running black...
Running mypy...
✅ All checks passed!
```

제공되는 스크립트 사용:

```console
$ ./scripts/format.sh
$ ./scripts/lint.sh
```

### 코드 포매팅

**Black** — 코드 포매터:

<div class="termy">

```console
$ black src/ tests/
reformatted src/main.py
reformatted tests/test_cli.py
All done! ✨ 🍰 ✨
```

</div>

**isort** — import 정렬:

<div class="termy">

```console
$ isort src/ tests/
Fixing import order in src/main.py
```

</div>

### 코드 린팅

**mypy** — 타입 체크:

<div class="termy">

```console
$ mypy src/
Success: no issues found in 12 source files
```

</div>

## 사용 가능한 Make 명령

프로젝트 Makefile 은 일반적인 개발 작업을 위한 편의 명령들을 제공합니다:

### 설정 명령

| 명령 | 설명 |
|---------|-------------|
| `make install` | 프로덕션 모드로 패키지 설치 |
| `make install-dev` | 개발 의존성과 함께 패키지 설치 |
| `make install-test` | 테스트용 패키지 설치 (제거 후 재설치) |
| `make uninstall` | 패키지 제거 |
| `make clean` | 빌드 아티팩트와 캐시 파일 정리 |

### 코드 품질 명령

| 명령 | 설명 |
|---------|-------------|
| `make format` | black 과 isort 로 코드 포매팅 |
| `make format-check` | 변경 없이 코드 포맷 검증만 |
| `make lint` | 모든 린트 검사 실행 (isort, black, mypy) |

### 테스트 명령

| 명령 | 설명 |
|---------|-------------|
| `make test` | 모든 테스트 실행 |
| `make test-verbose` | verbose 출력으로 테스트 실행 |
| `make test-coverage` | 커버리지 리포트와 함께 테스트 실행 |
| `make coverage-report` | 상세 커버리지 리포트 생성 (FORMAT=html/xml/json/all) |

### 템플릿 검사 명령

| 명령 | 설명 |
|---------|-------------|
| `make inspect-templates` | 모든 템플릿에 대해 검사 실행 |
| `make inspect-templates-verbose` | verbose 출력으로 템플릿 검사 |
| `make inspect-template` | 특정 템플릿 검사 (TEMPLATES 파라미터) |

### 문서 명령

| 명령 | 설명 |
|---------|-------------|
| `make serve-docs` | 문서를 로컬에서 서빙 |
| `make build-docs` | 문서 빌드 |

### 번역 명령

| 명령 | 설명 |
|---------|-----------|
| `make translate` | 문서 번역 (LANG, PROVIDER, MODEL 파라미터) |

### 예시

<div class="termy">

```console
# 코드 포맷 후 모든 검사 실행
$ make format lint
Running isort...
Running black...
Running mypy...
✅ All checks passed!

# 커버리지와 함께 테스트 실행
$ make test-coverage
======================== test session starts ========================
collected 45 items
tests/test_cli.py::test_init_command PASSED
...
======================== 45 passed in 2.34s ========================

---------- coverage: platform darwin, python 3.12.1-final-0 ----------
Name                     Stmts   Miss  Cover
--------------------------------------------
src/main.py                 45      2    96%
src/cli.py                  89      5    94%
src/templates.py            67      3    96%
--------------------------------------------
TOTAL                      201     10    95%

# HTML 커버리지 리포트 생성
$ make coverage-report FORMAT=html
🌐 Opening HTML coverage report in browser...

# 한국어로 문서 번역
$ make translate LANG=ko PROVIDER=github MODEL=gpt-4o-mini
Starting translation...
Running: python scripts/translate.py --target-lang ko --api-provider github --model gpt-4o-mini
```

</div>

## 프로젝트 구조

개발을 위해 프로젝트 구조를 이해해 두는 것이 중요합니다:

```bash
FastAPI-fastkit/
├── src/
│   ├── fastapi_fastkit/
│   │   ├── __main__.py                      # 애플리케이션 진입점
│   │   ├── backend/
│   │   │   ├── inspector.py                 # FastAPI-fastkit 템플릿 inspector
│   │   │   ├── interactive/
│   │   │   │   ├── config_builder.py        # 대화형 모드용 설정 빌더
│   │   │   │   ├── prompts.py               # 대화형 모드용 프롬프트
│   │   │   │   ├── selectors.py             # 대화형 모드용 selector 로직
│   │   │   │   └── validators.py            # 대화형 모드용 사용자 입력 validator
│   │   │   ├── main.py                      # 백엔드 로직 진입점
│   │   │   ├── package_managers/
│   │   │   │   ├── base.py                  # 패키지 매니저 base 클래스
│   │   │   │   ├── factory.py               # 패키지 매니저 factory
│   │   │   │   ├── pdm_manager.py           # PDM 패키지 매니저
│   │   │   │   ├── pip_manager.py           # pip 패키지 매니저
│   │   │   │   ├── poetry_manager.py        # Poetry 패키지 매니저
│   │   │   │   └── uv_manager.py            # uv 패키지 매니저
│   │   │   ├── project_builder/
│   │   │   │   ├── config_generator.py      # 프로젝트 빌더용 설정 생성기
│   │   │   │   └── dependency_collector.py  # 프로젝트 빌더용 의존성 수집기
│   │   │   └── transducer.py                # 프로젝트 빌더용 transducer
│   │   ├── cli.py                           # FastAPI-fastkit 메인 CLI 진입점
│   │   ├── core/
│   │   │   ├── exceptions.py                # 예외 처리
│   │   │   └── settings.py                  # 설정 구성
│   │   ├── fastapi_project_template/
│   │   │   ├── PROJECT_README_TEMPLATE.md   # fastkit 템플릿 프로젝트의 base README 파일
│   │   │   ├── README.md                    # fastkit 템플릿 README
│   │   │   ├── fastapi-async-crud/
│   │   │   ├── fastapi-custom-response/
│   │   │   ├── fastapi-default/
│   │   │   ├── fastapi-dockerized/
│   │   │   ├── fastapi-empty/
│   │   │   ├── fastapi-mcp/
│   │   │   ├── fastapi-psql-orm/
│   │   │   ├── fastapi-single-module/
│   │   │   └── modules/
│   │   │       ├── api/
│   │   │       │   └── routes/
│   │   │       ├── crud/
│   │   │       └── schemas/
│   │   ├── py.typed
│   │   └── utils/
│   │       ├── logging.py                   # 로깅 설정
│   │       └── main.py                      # FastAPI-fastkit 메인 진입점
│   └── logs
├── tests
│   ├── conftest.py                          # pytest 설정
│   ├── test_backends/
│   ├── test_cli_operations/
│   ├── test_core.py
│   ├── test_rich/
│   ├── test_templates/
│   └── test_utils.py
├── uv.lock
├── docs/                                    # 문서
├── scripts/                                 # 개발 스크립트
├── mkdocs.yml
├── overrides/                               # mkdocs 오버라이드
├── pdm.lock
├── pyproject.toml
├── requirements-docs.txt                    # 문서용 requirements
├── requirements.txt                         # 개발용 requirements
├── CHANGELOG.md
├── CITATION.cff
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE
├── MANIFEST.in
├── Makefile
├── README.md
├── SECURITY.md
└── env.example                              # 환경 변수 예시 (번역 AI 모델 환경 변수 포함)
```

### 핵심 디렉터리

- **`src/fastapi_fastkit/`** — 메인 패키지 소스 코드
    - **`cli.py`** — 메인 CLI 진입점
    - **`backend/`** — 핵심 백엔드 로직
        - **`inspector.py`** — 템플릿 inspector
        - **`interactive/`** — 대화형 모드 컴포넌트 (prompts, selectors, validators)
        - **`package_managers/`** — 패키지 매니저 구현 (pip, uv, pdm, poetry)
        - **`project_builder/`** — 프로젝트 빌드 유틸리티
        - **`transducer.py`** — 템플릿 transducer
    - **`core/`** — 핵심 설정과 예외
    - **`fastapi_project_template/`** — 프로젝트 템플릿 (fastapi-default, fastapi-async-crud 등)
    - **`utils/`** — 공유 유틸리티 함수
- **`tests/`** — 테스트 스위트
    - **`test_backends/`** — 백엔드 관련 테스트
    - **`test_cli_operations/`** — CLI 동작 테스트
    - **`test_templates/`** — 템플릿 시스템 테스트
- **`docs/`** — 문서 (MkDocs)
    - 사용자 가이드, 튜토리얼, API 레퍼런스

## 개발 워크플로

### 1. 기능 브랜치 생성

<div class="termy">

```console
$ git checkout -b feature/add-new-template
Switched to a new branch 'feature/add-new-template'
```

</div>

### 2. 변경 사항 작성

코드 편집, 기능 추가, 버그 수정...

### 3. 테스트와 검사 실행

<div class="termy">

```console
$ make dev-check
Running all quality checks...
Running all tests...
✅ All tests passed!
```

</div>

### 4. 변경 사항 커밋

Pre-commit 훅이 자동으로 실행됩니다:

<div class="termy">

```console
$ git add .
$ git commit -m "Add new FastAPI template with authentication"
format...................................................................Passed
isort-check..............................................................Passed
black-fix................................................................Passed
mypy.....................................................................Passed
[feature/add-new-template abc1234] Add new FastAPI template with authentication
```

</div>

### 5. Push 후 Pull Request 생성

<div class="termy">

```console
$ git push origin feature/add-new-template
$ gh pr create --title "Add new FastAPI template with authentication"
```

</div>

## 테스트

### 테스트 실행

**모든 테스트:**

<div class="termy">

```console
$ make test
# 또는
$ python -m pytest
```

</div>

**특정 테스트 파일:**

<div class="termy">

```console
$ python -m pytest tests/test_cli.py -v
```

</div>

**커버리지와 함께:**

<div class="termy">

```console
$ make test-coverage
# 또는
$ python -m pytest --cov=src --cov-report=html
```

</div>

### 테스트 작성

새 기능을 추가할 때는 항상 테스트를 함께 작성하세요:

```python
# tests/test_commands/test_new_feature.py
import pytest
from fastapi_fastkit.commands.new_feature import NewFeatureCommand

class TestNewFeatureCommand:
    def test_command_success(self):
        """Test successful command execution"""
        command = NewFeatureCommand()
        result = command.execute(valid_args)
        assert result.success is True
        assert result.message == "Feature executed successfully"

    def test_command_validation_error(self):
        """Test command with invalid arguments"""
        command = NewFeatureCommand()
        with pytest.raises(ValueError, match="Invalid argument"):
            command.execute(invalid_args)

    def test_command_edge_case(self):
        """Test edge case handling"""
        command = NewFeatureCommand()
        result = command.execute(edge_case_args)
        assert result.success is True
        assert "warning" in result.message.lower()
```

### 테스트 카테고리

**단위 테스트** — 개별 함수와 클래스 테스트:

```python
def test_validate_project_name():
    assert validate_project_name("valid-name") is True
    assert validate_project_name("invalid name!") is False
```

**통합 테스트** — 명령 간 상호 작용 테스트:

```python
def test_init_command_creates_project(tmp_path):
    result = runner.invoke(cli, ['init'], input='test-project\n...')
    assert result.exit_code == 0
    assert (tmp_path / "test-project").exists()
```

**종단간 테스트** — 전체 워크플로를 검증하는 테스트:

```python
def test_full_project_creation_workflow(tmp_path):
    # 프로젝트 생성
    result = runner.invoke(cli, ['init'], input='...')
    assert result.exit_code == 0

    # 라우트 추가
    result = runner.invoke(cli, ['addroute', 'test-project', 'users'])
    assert result.exit_code == 0

    # 파일 존재 확인
    assert (tmp_path / "test-project" / "src" / "api" / "routes" / "users.py").exists()
```

## 문서

### 문서 로컬 서빙

<div class="termy">

```console
$ make serve-docs
INFO     -  Building documentation...
INFO     -  Cleaning site directory
INFO     -  Documentation built in 0.43 seconds
INFO     -  [14:30:00] Serving on http://127.0.0.1:8000/
```

</div>

### 문서 빌드

<div class="termy">

```console
$ make build-docs
INFO     -  Building documentation...
INFO     -  Documentation built in 0.43 seconds
```

</div>

### 문서 작성

문서는 Markdown으로 작성하며 MkDocs로 빌드합니다. 예시 구조는 다음과 같습니다:

**기능 가이드 템플릿:**

````markdown
# New Feature Guide

This guide explains how to use the new feature.

## Prerequisites

- FastAPI-fastkit installed
- Basic Python knowledge

## Usage

<div class="termy">

```console
$ fastkit new-feature --option value
✅ Feature executed successfully!
```

</div>

!!! tip "Pro Tip"
    Use `--help` to see all available options.
````

`mkdocs-material` 사용법이 더 궁금하다면 [mkdocs-material 문서](https://squidfunk.github.io/mkdocs-material/reference/admonitions/)를 참고하세요.

## 코드 스타일 가이드라인

### Python 코드 스타일

[PEP 8](https://www.python.org/dev/peps/pep-0008/)을 기본으로 하되, 아래 규칙도 함께 따라 주세요:

- **줄 길이**: 88자 (Black 기본값)
- **Import**: isort 로 정리
- **타입 힌트**: 모든 공개 함수에 필수
- **Docstring**: 모든 공개 API 에 Google 스타일

### 예시

```python
from typing import List, Optional
from pathlib import Path

def create_project_structure(
    project_name: str,
    template_path: Path,
    output_dir: Optional[Path] = None,
) -> List[Path]:
    """Create project structure from template.

    Args:
        project_name: Name of the project to create
        template_path: Path to the template directory
        output_dir: Output directory, defaults to current directory

    Returns:
        List of created file paths

    Raises:
        ValueError: If project_name is invalid
        FileNotFoundError: If template_path doesn't exist
    """
    if not project_name.isidentifier():
        raise ValueError(f"Invalid project name: {project_name}")

    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    # Implementation here...
    return created_files
```

## 환경 변수

개발할 때는 다음 환경 변수를 설정해 활용할 수 있습니다:

| 변수 | 설명 | 기본값 |
|----------|-------------|---------|
| `FASTKIT_DEBUG` | 디버그 로깅 활성화 | `False` |
| `FASTKIT_DEV_MODE` | 개발 기능 활성화 | `False` |
| `FASTKIT_TEMPLATE_DIR` | 커스텀 템플릿 디렉터리 | 내장 템플릿 |
| `FASTKIT_CONFIG_DIR` | 설정 디렉터리 | `~/.fastkit` |
| `TRANSLATION_API_KEY` | 번역 API 키 ([Github AI 모델 제공자](https://github.com/marketplace/models/azure-openai) 사용 시 Github PAT 입력) | `None` |

<div class="termy">

```console
$ export FASTKIT_DEBUG=true
$ export FASTKIT_DEV_MODE=true
$ fastkit init
DEBUG: Loading configuration from /home/user/.fastkit/
DEBUG: Available templates: ['fastapi-default', ...]
```

</div>

다른 환경 변수 설정은 [settings.py](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/core/settings.py) 모듈을 참고하세요.

## 문제 해결

### 자주 발생하는 문제

**1. Pre-commit 훅 실패:**

<div class="termy">

```console
$ git commit -m "Fix bug"
black....................................................................Failed
hookid: black

Files were modified by this hook. Additional output:

would reformat src/cli.py
```

</div>

**해결책:** 포매터를 실행하고 다시 커밋하세요:

<div class="termy">

```console
$ make format
$ git add .
$ git commit -m "Fix bug"
```

</div>

**2. 다른 Python 버전에서 테스트가 실패할 때:**

**해결 방법:** `tox`로 여러 Python 버전을 함께 테스트하세요:

<div class="termy">

```console
$ pip install tox
$ tox
py38: commands succeeded
py39: commands succeeded
py310: commands succeeded
py311: commands succeeded
py312: commands succeeded
```

</div>

**3. 개발 중 import 오류:**

**해결책:** 패키지를 editable 모드로 설치하세요:

<div class="termy">

```console
$ pip install -e .
```

</div>

### 도움 받기

- **[GitHub Issues](https://github.com/bnbong/FastAPI-fastkit/issues)**: 버그 신고와 기능 요청
- **[GitHub Discussions](https://github.com/bnbong/FastAPI-fastkit/discussions)**: 질문과 아이디어 공유
- **문서**: [사용자 가이드](../user-guide/installation.md) 확인

## 기여 가이드라인

### PR 제출 전

1. **모든 검사 실행:** `make dev-check`
2. 필요 시 **문서 갱신**
3. 새 기능에는 **테스트 추가**
4. **커밋 메시지 컨벤션 준수**

### 커밋 메시지 형식

```
type(scope): brief description

Longer description if needed

Fixes #123
```

**타입:**

- `feat`: 새 기능
- `fix`: 버그 수정
- `docs`: 문서 변경
- `style`: 코드 스타일 변경
- `refactor`: 코드 리팩터링
- `test`: 테스트 추가/변경
- `chore`: 유지보수 작업

**예시:**

```
feat(cli): add new template command

Add support for creating projects from custom templates.
The command accepts a template path and creates a new
project with the specified configuration.

Fixes #45

fix(templates): handle missing template files gracefully

When a template file is missing, show a clear error message
instead of crashing with a stack trace.

Fixes #67
```

## 릴리스 프로세스

메인테이너용 릴리스 프로세스:

1. `setup.py` 와 `__init__.py` 의 **버전 갱신**
2. **CHANGELOG.md 갱신**
3. **릴리스 PR 생성**
4. 머지 후 **태그 생성**
5. **GitHub Actions**가 자동으로 빌드와 배포를 수행

<div class="termy">

```console
$ git tag v1.2.0
$ git push origin v1.2.0
```

</div>

## 다음 단계

이제 개발 환경이 준비됐으니:

1. 아키텍처를 이해하기 위해 **[코드베이스 살펴보기](https://github.com/bnbong/FastAPI-fastkit/tree/main/src/fastapi_fastkit)**
2. 모든 것이 정상 동작하는지 **테스트 스위트 실행**
3. GitHub에서 작업할 **[이슈 고르기](https://github.com/bnbong/FastAPI-fastkit/issues)**
4. 다른 기여자들과 소통하고 싶다면 **[Discussions](https://github.com/bnbong/FastAPI-fastkit/discussions) 참여**

즐거운 코딩 되세요! 🚀

!!! tip "개발 팁"
    - 커밋 전에 `make dev-check` 사용
    - 테스트를 먼저 작성 (TDD 접근)
    - 커밋은 작고 집중되게 유지
    - 새 기능과 함께 문서도 갱신
