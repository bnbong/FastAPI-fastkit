# 설치

이 가이드는 FastAPI-fastkit 설치 방법을 안내합니다.

## 요구 사항

FastAPI-fastkit을 사용하려면 다음 요구 사항을 충족해야 합니다:

- **Python**: 3.12 이상
- **운영체제**: Windows, macOS, Linux 지원

## 설치 방법

### pip으로 설치 (권장)

가장 간단한 설치 방법:

<div class="termy">

```console
$ pip install FastAPI-fastkit
---> 100%
Successfully installed FastAPI-fastkit
```

</div>

### 특정 버전 설치

특정 버전을 설치하려면:

<div class="termy">

```console
$ pip install FastAPI-fastkit==1.0.0
---> 100%
Successfully installed FastAPI-fastkit-1.0.0
```

</div>

### 개발 버전 설치

GitHub에서 최신 개발 버전을 직접 설치하려면:

<div class="termy">

```console
$ pip install git+https://github.com/bnbong/FastAPI-fastkit.git
---> 100%
Successfully installed FastAPI-fastkit
```

</div>

!!! warning "개발 버전 주의"
    개발 버전은 불안정할 수 있으며 프로덕션 환경에서는 권장되지 않습니다.

## 가상 환경 설정 (권장)

의존성 충돌을 피하기 위해 가상 환경 사용을 강력히 권장합니다:

### venv 사용

<div class="termy">

```console
$ python -m venv fastapi-env
$ source fastapi-env/bin/activate  # Linux/macOS
$ fastapi-env\Scripts\activate     # Windows
$ pip install FastAPI-fastkit
```

</div>

### conda 사용

<div class="termy">

```console
$ conda create -n fastapi-env python=3.12
$ conda activate fastapi-env
$ pip install FastAPI-fastkit
```

</div>

## 설치 확인

설치가 끝나면 FastAPI-fastkit이 올바르게 설치되었는지 확인하세요:

<div class="termy">

```console
$ fastkit --version
FastAPI-fastkit version 1.0.0
```

</div>

<div class="termy">

```console
$ fastkit --help
Usage: fastkit [OPTIONS] COMMAND [ARGS]...

  FastAPI-fastkit CLI

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  addroute       Add a new route to FastAPI project
  init           Create a new FastAPI project
  list-templates List available FastAPI templates
  runserver      Start FastAPI development server
  startdemo      Create FastAPI project from template
```

</div>

## 문제 해결

### Command not found

"command not found" 오류가 발생하는 경우:

1. **FastAPI-fastkit이 설치되어 있는지 확인**:

   <div class="termy">
   ```console
   $ pip show FastAPI-fastkit
   ```
   </div>

2. **가상 환경 확인**:

   <div class="termy">
   ```console
   $ which python
   $ which pip
   ```
   </div>

3. **FastAPI-fastkit 재설치**:

   <div class="termy">
   ```console
   $ pip uninstall FastAPI-fastkit
   $ pip install FastAPI-fastkit
   ```
   </div>

### 권한 오류

설치 중 권한 오류가 발생하는 경우:

**Linux/macOS:**

<div class="termy">

```console
$ pip install --user FastAPI-fastkit
```

</div>

**Windows (관리자 권한으로 실행):**

<div class="termy">

```console
$ pip install FastAPI-fastkit
```

</div>

### Python 버전 호환성

FastAPI-fastkit은 Python 3.12 이상이 필요합니다. Python 버전을 확인하세요:

<div class="termy">

```console
$ python --version
Python 3.12.0
```

</div>

이전 버전을 사용 중이라면 Python을 업그레이드하세요:

- **공식 Python**: [python.org/downloads](https://www.python.org/downloads/)
- **pyenv**: `pyenv install 3.12.0`
- **conda**: `conda install python=3.12`

## 다음 단계

설치가 완료되면:

1. **[퀵 스타트](quick-start.md)**: 5분 안에 첫 프로젝트 만들기
2. **[입문 튜토리얼](../tutorial/getting-started.md)**: 단계별 상세 튜토리얼
3. **[CLI 레퍼런스](cli-reference.md)**: 전체 명령어 레퍼런스

!!! tip "설치 팁"
    - 프로젝트 격리를 위해 항상 가상 환경을 사용하세요
    - FastAPI-fastkit을 최신 버전으로 유지하세요
    - 업데이트와 이슈는 [GitHub 저장소](https://github.com/bnbong/FastAPI-fastkit)에서 확인하세요
