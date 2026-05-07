# 템플릿 품질 보증

FastAPI-fastkit은 모든 템플릿이 다양한 환경과 패키지 매니저에서 일관된 품질과 동작을 유지하도록 종합적인 자동 검증 시스템을 제공합니다.

## 다층 품질 보증

FastAPI-fastkit은 **서로 보완하는 두 가지 품질 보증 시스템**을 운영합니다:

### 1. 정적 템플릿 검사 (Static Template Inspection)
**템플릿 구조와 문법에 대한 매주 자동 검증**

### 2. 동적 템플릿 테스트 (Dynamic Template Testing)
**실제 프로젝트 생성을 동반한 종합 엔드투엔드 테스트**

## 매주 자동 검사

매주 수요일 자정 (UTC) 에 GitHub Actions 워크플로가 모든 FastAPI 템플릿이 품질 기준을 만족하는지 자동으로 검사합니다:

- ✅ **파일 구조 검증** — 필수 파일과 디렉터리가 모두 있는지 확인
- ✅ **파일 확장자 검증** — 템플릿 파일이 올바른 `.py-tpl` 확장자를 쓰는지 확인
- ✅ **의존성 확인** — FastAPI 와 필수 의존성이 제대로 선언돼 있는지 확인
- ✅ **FastAPI 구현 확인** — 템플릿이 적절한 FastAPI 앱 초기화를 포함하는지 확인
- ✅ **테스트 실행** — 템플릿 테스트를 실행해 동작을 확인

## 자동 템플릿 테스트 시스템

FastAPI-fastkit은 모든 템플릿을 폭넓게 검증할 수 있는 **자동 테스트 시스템**을 갖추고 있습니다:

### 동적 템플릿 자동 발견

테스트 시스템은 **수동 설정 없이 모든 템플릿을 자동으로 발견**합니다:

```console
# 모든 템플릿을 자동으로 테스트
$ pytest tests/test_templates/test_all_templates.py -v

# 발견된 모든 템플릿이 결과에 표시됨
PASSED tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[fastapi-default]
PASSED tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[fastapi-async-crud]
PASSED tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[fastapi-dockerized]
PASSED tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[fastapi-psql-orm]
```

### 종합 테스트 커버리지

각 템플릿은 **종합적인 엔드투엔드 테스트**를 거칩니다:

#### ✅ 프로젝트 생성 과정

- 템플릿 복사와 파일 변환
- 프로젝트 메타데이터 주입 (이름, 작성자, 설명)
- 파일 구조 검증

#### ✅ 패키지 매니저 호환성

- **UV** (기본값): Rust 기반의 빠른 패키지 매니저
- **PDM**: 현대적인 Python 의존성 관리
- **Poetry**: 검증된 의존성 관리
- **PIP**: 전통적인 Python 패키지 매니저

#### ✅ 가상 환경 관리

- 패키지 매니저별 환경 생성
- 의존성 설치 검증
- 패키지 매니저 고유 워크플로

#### ✅ 의존성 해석

- `pyproject.toml` 생성 (UV, PDM, Poetry)
- `requirements.txt` 생성 (PIP)
- 메타데이터 규격 준수 (PEP 621)
- 빌드 시스템 설정

#### ✅ 프로젝트 구조 검증

- FastAPI 프로젝트 식별
- 필수 파일 존재 여부
- 디렉터리 구조 검증

### 테스트 실행 예시

**모든 템플릿 테스트 실행:**

```console
$ pytest tests/test_templates/test_all_templates.py -v
```

**특정 템플릿만 테스트:**

```console
$ pytest tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[fastapi-default] -v
```

**PDM 환경에서 테스트:**

```console
$ pdm run pytest tests/test_templates/test_all_templates.py -v
```

### 지속적 통합 (CI)

자동 테스트 시스템은 **CI/CD 파이프라인**에서도 동작합니다:

- ✅ **PR 검증**: 모든 PR은 영향 받는 템플릿을 테스트
- ✅ **야간 테스트**: 전체 템플릿 모음에 대한 검증
- ✅ **패키지 매니저 테스트**: 모든 매니저로 교차 검증
- ✅ **환경 테스트**: 여러 Python 버전과 플랫폼

### 기여자가 얻는 이점

**추가 설정 없는 테스트:**

- 🚀 새 템플릿 추가 → 자동 테스트
- ⚡ 수동 테스트 파일 생성 불필요
- 🛡️ 일관된 품질 기준

**종합 커버리지:**

- 🔍 엔드투엔드 프로젝트 생성 테스트
- 📦 다중 패키지 매니저 검증
- 🏗️ 완전한 의존성 해석 테스트
- ✅ 실사용 시나리오 시뮬레이션

**개발자 경험:**

- 🎯 **템플릿 콘텐츠에 집중**: 테스트는 자동
- 🔄 **즉시 피드백**: 빠른 테스트 실행
- 📊 **명확한 결과**: 상세한 테스트 리포트
- 🚫 **별도 보일러플레이트 불필요**: 테스트 설정을 따로 만들 필요 없음

## 수동 템플릿 검사

개발과 디버깅 목적으로 로컬 검사 스크립트나 Makefile 명령으로 템플릿을 직접 검사할 수 있습니다:

### 검사 스크립트 직접 실행

```console
# 모든 템플릿 검사
$ python scripts/inspect-templates.py

# 특정 템플릿만 검사
$ python scripts/inspect-templates.py --templates fastapi-default,fastapi-async-crud

# 자세한 정보를 포함한 verbose 출력
$ python scripts/inspect-templates.py --verbose

# 결과를 사용자 지정 파일로 저장
$ python scripts/inspect-templates.py --output my_results.json
```

### Makefile 명령 사용

```console
# 모든 템플릿 검사
$ make inspect-templates

# verbose 출력으로 검사
$ make inspect-templates-verbose

# 특정 템플릿만 검사
$ make inspect-template TEMPLATES="fastapi-default,fastapi-async-crud"
```

## 검사 결과

- **성공한 검사**는 워크플로 출력과 아티팩트에 기록됩니다
- **실패한 검사**는 자세한 오류 리포트와 함께 GitHub 이슈를 자동으로 생성합니다
- **검사 이력**은 GitHub Actions 아티팩트에 30일 동안 보존됩니다

## 검사 출력 이해하기

템플릿 검사를 실행하면 다음과 같은 출력을 볼 수 있습니다:

```console
📋 Found 6 templates to inspect: fastapi-async-crud, fastapi-custom-response, fastapi-default, fastapi-dockerized, fastapi-empty, fastapi-psql-orm
============================================================
🔍 Inspecting template: fastapi-async-crud
   Path: /path/to/src/fastapi_fastkit/fastapi_project_template/fastapi-async-crud
✅ fastapi-async-crud: PASSED
----------------------------------------
🔍 Inspecting template: fastapi-custom-response
   Path: /path/to/src/fastapi_fastkit/fastapi_project_template/fastapi-custom-response
✅ fastapi-custom-response: PASSED
----------------------------------------
...
============================================================
📊 INSPECTION SUMMARY
   Total templates: 6
   ✅ Passed: 6
   ❌ Failed: 0
🎉 All templates passed inspection!
📄 Results saved to: template_inspection_results.json
```

## 템플릿 요구 사항

템플릿이 검사를 통과하려면 다음 요구 사항을 충족해야 합니다:

### 파일 구조

- Python 소스 파일이 들어 있는 `src/` 디렉터리가 있어야 합니다
- Python 파일은 `.py-tpl` 확장자를 사용해야 합니다
- `tests/` 디렉터리와 `README.md-tpl` 파일을 포함해야 합니다
- **최소 하나 이상**의 메타데이터 파일을 포함해야 합니다:
    - `pyproject.toml-tpl` (권장, PEP 621), 또는
- `setup.py-tpl` (레거시, 여전히 허용)
- `pyproject.toml-tpl` 이 `[project].dependencies` 를 선언한다면 `requirements.txt-tpl` 은 선택 사항입니다

### FastAPI 요구 사항

- FastAPI 앱 초기화를 포함해야 합니다
- 다음 중 최소 한 곳에 `fastapi` 를 의존성으로 선언해야 합니다: `pyproject.toml-tpl` 의 `[project].dependencies`, `requirements.txt-tpl`, 또는 `setup.py-tpl` 의 `install_requires`
- 모든 템플릿 파일이 유효한 Python 문법이어야 합니다

### 식별 마커

생성된 프로젝트가 사용자 워크스페이스에 있는 다른 FastAPI 프로젝트와 구분되도록, 템플릿은 FastAPI-fastkit 식별 마커를 갖고 있어야 합니다:

- `pyproject.toml-tpl` — `description` 의 `[FastAPI-fastkit templated]` 접두사와 `managed = true` 를 가진 `[tool.fastapi-fastkit]` 테이블 모두.
- `setup.py-tpl` — `setup()` 의 `description` 인자에 `[FastAPI-fastkit templated]` 접두사.

`is_fastkit_project()`는 둘 중 하나만 있어도 인식합니다 (`pyproject`가 우선이고, `setup.py`는 레거시 fallback입니다. 매칭은 대소문자를 구분하지 않습니다). 메타데이터 주입 단계가 템플릿에서 마커를 빠뜨렸더라도, 생성된 프로젝트에는 마커가 들어가도록 보장합니다.

### 품질 기준

- 모든 템플릿 파일은 문법적으로 올바라야 합니다
- 의존성이 적절하게 명시돼야 합니다
- 템플릿 구조는 FastAPI-fastkit 컨벤션을 따라야 합니다

이 자동 품질 보증 시스템은 모든 템플릿이 신뢰할 수 있고, 실사용에도 무리가 없는 상태를 유지하도록 돕습니다.
