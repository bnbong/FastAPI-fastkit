# 코드 가이드라인

FastAPI-fastkit에 기여하는 모든 분을 위한 종합 코딩 표준과 모범 사례입니다.

## 개요

이 가이드라인은 FastAPI-fastkit 프로젝트 전반에서 코드 품질과 일관성, 유지보수성을 지키기 위해 마련됐습니다. 이 기준을 따르면 읽기 쉽고, 유지보수하기 편하며, 확장에도 유리한 코드베이스를 만드는 데 도움이 됩니다.

## Python 코드 스타일

### PEP 8 준수

[PEP 8](https://www.python.org/dev/peps/pep-0008/)을 기본으로 하되, 아래 규칙도 함께 따라 주세요:

- **줄 길이**: 88자 (Black 기본값)
- **들여쓰기**: 공백 4칸 (탭 사용 금지)
- **후행 쉼표(trailing comma)**: 여러 줄 구조에서는 필수
- **문자열 따옴표**: 큰따옴표 권장

### 코드 포매팅

자동 코드 포매터로 **Black**을 사용합니다:

```python
# Good ✅
def create_project(
    name: str,
    template: str,
    options: Dict[str, Any],
) -> ProjectResult:
    """Create a new FastAPI project."""
    return ProjectResult(name=name, template=template)

# Bad ❌
def create_project(name: str, template: str, options: Dict[str,Any])->ProjectResult:
    """Create a new FastAPI project."""
    return ProjectResult(name=name,template=template)
```

### Import 정리

import 정리는 **isort**로 처리합니다:

```python
# Standard library imports
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union

# Third-party imports
import click
import pydantic
from fastapi import FastAPI

# Local imports
from fastapi_fastkit.commands import BaseCommand
from fastapi_fastkit.utils import validation
from fastapi_fastkit.templates.manager import TemplateManager
```

## 타입 힌트

### 타입 힌트 필수

모든 공개 함수와 메서드에는 타입 힌트가 들어가야 합니다:

```python
# Good ✅
def validate_project_name(name: str) -> bool:
    """Validate project name format."""
    return name.isidentifier() and not name.startswith('_')

def create_files(
    files: List[Path],
    template_data: Dict[str, Any]
) -> List[Path]:
    """Create files from template data."""
    created_files = []
    for file_path in files:
        # Implementation...
        created_files.append(file_path)
    return created_files

# Bad ❌
def validate_project_name(name):
    return name.isidentifier() and not name.startswith('_')
```

### 복잡한 타입 어노테이션

복잡한 구조에는 적절한 타입 어노테이션을 사용하세요:

```python
from typing import Dict, List, Optional, Union, Tuple, Any
from pathlib import Path

# 복잡한 타입에 대한 타입 별칭
ProjectConfig = Dict[str, Union[str, bool, List[str]]]
FileMapping = Dict[Path, str]
ValidationResult = Tuple[bool, Optional[str]]

def process_template(
    template_path: Path,
    config: ProjectConfig,
    output_dir: Optional[Path] = None,
) -> ValidationResult:
    """Process template with configuration."""
    # Implementation...
    return True, None
```

## 명명 규칙

### 변수와 함수

- 변수와 함수는 **snake_case**
- 의도를 설명하는 **서술적인 이름**
- 흔히 통용되는 약어가 아니라면 **약어 회피**

```python
# Good ✅
project_name = "my-api"
template_directory = Path("templates")
user_input_data = get_user_input()

def validate_email_address(email: str) -> bool:
    """Validate email address format."""
    return "@" in email and "." in email

# Bad ❌
proj_nm = "my-api"
temp_dir = Path("templates")
usr_data = get_input()

def validate_email(e):
    return "@" in e and "." in e
```

### 클래스

- 클래스명은 **PascalCase**
- **서술적이고 구체적인** 이름

```python
# Good ✅
class SomeClass:
    """Represents example class of FastAPI-fastkit."""
    pass

class SomeClassValidationError(Exception):
    """Raised when example class validation fails."""
    pass

class UserInputHandler:
    """Handles user input validation and processing."""
    pass

# Bad ❌
class Class:
    pass

class Error(Exception):
    pass

class Handler:
    pass
```

### 상수

- 언더스코어로 구분된 **UPPER_CASE**
- **모듈 수준** 상수만 허용

```python
# Good ✅
DEFAULT_TEMPLATE_NAME = "fastapi-default"
MAX_PROJECT_NAME_LENGTH = 50
SUPPORTED_PYTHON_VERSIONS = ["3.8", "3.9", "3.10", "3.11", "3.12"]

# Bad ❌
default_template = "fastapi-default"
maxLength = 50
versions = ["3.8", "3.9", "3.10", "3.11", "3.12"]
```

## 문서 표준

### Docstring

모든 공개 API 에는 **Google 스타일 docstring** 을 사용하세요:

```python
def create_project_structure(
    project_name: str,
    template_path: Path,
    output_directory: Optional[Path] = None,
    overwrite: bool = False,
) -> List[Path]:
    """Create project structure from template.

    Creates a new FastAPI project structure by copying and processing
    template files. Supports variable substitution and file customization.

    Args:
        project_name: Name of the project to create. Must be a valid
            Python identifier.
        template_path: Path to the template directory containing
            source files and configuration.
        output_directory: Directory where project will be created.
            Defaults to current working directory.
        overwrite: Whether to overwrite existing files. If False,
            raises error when files exist.

    Returns:
        List of created file paths in order of creation.

    Raises:
        ValueError: If project_name is invalid or empty.
        FileExistsError: If output directory exists and overwrite is False.
        TemplateNotFoundError: If template_path doesn't exist.
        PermissionError: If insufficient permissions to create files.

    Example:
        ```python
        template_path = Path("templates/fastapi-default")
        created_files = create_project_structure(
            project_name="my-api",
            template_path=template_path,
            output_directory=Path("./projects"),
            overwrite=False
        )
        print(f"Created {len(created_files)} files")
        ```
    """
    # Implementation here...
    pass
```

### 주석

- **무엇이 아니라 왜** 를 설명
- **꼭 필요할 때만 사용** — 코드는 자체로 설명적이어야 함
- 코드가 바뀌면 **주석도 함께 갱신**

```python
# Good ✅
def validate_dependencies(requirements: List[str]) -> bool:
    """Validate project dependencies."""
    # 개발 모드에서는 실험적 패키지를 허용하기 위해 검증을 건너뜀
    if os.getenv("FASTKIT_DEV_MODE"):
        return True

    # 알려진 보안 취약점이 있는지 각 의존성을 확인
    for requirement in requirements:
        if is_vulnerable_package(requirement):
            return False

    return True

# Bad ❌
def validate_dependencies(requirements: List[str]) -> bool:
    """Validate project dependencies."""
    # dev 모드인지 확인
    if os.getenv("FASTKIT_DEV_MODE"):
        return True

    # requirements 를 순회
    for requirement in requirements:
        # 취약한지 확인
        if is_vulnerable_package(requirement):
            return False

    # true 반환
    return True
```

## 에러 처리

### 예외 처리

- 가능하면 **구체적인 예외를 잡기**
- **의미 있는 에러 메시지** 제공
- 에러를 **적절히 로깅**

```python
# Good ✅
def load_template_config(template_path: Path) -> Dict[str, Any]:
    """Load template configuration from file."""
    config_file = template_path / "template.yaml"

    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise TemplateNotFoundError(
            f"Template configuration not found: {config_file}"
        )
    except yaml.YAMLError as e:
        raise TemplateConfigError(
            f"Invalid YAML syntax in {config_file}: {e}"
        )
    except PermissionError:
        raise TemplateAccessError(
            f"Permission denied reading {config_file}"
        )

# Bad ❌
def load_template_config(template_path: Path) -> Dict[str, Any]:
    """Load template configuration from file."""
    config_file = template_path / "template.yaml"

    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise Exception(f"Error loading config: {e}")
```

### 커스텀 예외

서로 다른 에러 조건에 대한 구체적인 예외를 정의하세요:

```python
class FastKitError(Exception):
    """Base exception for FastAPI-fastkit errors."""
    pass

class ProjectCreationError(FastKitError):
    """Raised when project creation fails."""
    pass

class TemplateNotFoundError(FastKitError):
    """Raised when template is not found."""
    pass

class ValidationError(FastKitError):
    """Raised when input validation fails."""

    def __init__(self, message: str, field: str = None):
        super().__init__(message)
        self.field = field
```

## 테스트 표준

### 테스트 구조

테스트를 명확한 구조와 명명으로 정리하세요:

```python
class TestProjectCreation:
    """Test project creation functionality."""

    def test_create_project_with_valid_name(self, tmp_path):
        """Test project creation with valid project name."""
        project_name = "test-project"
        result = create_project(project_name, template="minimal", output=tmp_path)

        assert result.success is True
        assert (tmp_path / project_name).exists()
        assert (tmp_path / project_name / "src" / "main.py").exists()

    def test_create_project_with_invalid_name(self):
        """Test project creation fails with invalid name."""
        with pytest.raises(ValueError, match="Invalid project name"):
            create_project("invalid-project-name!", template="minimal")

    def test_create_project_overwrites_existing(self, tmp_path):
        """Test project creation overwrites existing directory when forced."""
        project_name = "existing-project"
        project_dir = tmp_path / project_name
        project_dir.mkdir()

        result = create_project(
            project_name,
            template="minimal",
            output=tmp_path,
            overwrite=True
        )

        assert result.success is True
        assert project_dir.exists()
```

### 테스트 커버리지

- 새 코드는 **90% 이상의 커버리지** 목표
- **엣지 케이스**와 에러 상황을 테스트
- **외부 의존성을 모킹**

```python
def test_template_download_with_network_error(mock_requests):
    """Test template download handles network errors gracefully."""
    mock_requests.get.side_effect = requests.ConnectionError("Network unreachable")

    with pytest.raises(TemplateDownloadError, match="Network error"):
        download_template("https://example.com/template.zip")

def test_file_creation_with_permission_error(mock_open):
    """Test file creation handles permission errors."""
    mock_open.side_effect = PermissionError("Permission denied")

    with pytest.raises(FileCreationError, match="Permission denied"):
        create_file(Path("/restricted/file.py"), content="test")
```

## Import 가이드라인

### Import 정리

!!! note

    `isort` 포매터가 import 를 자동으로 정리해 주므로, `bash scripts/format.sh` 만 실행하면 import 정리는 손쉽게 끝납니다.

1. **표준 라이브러리** import 먼저
2. **서드파티** import 그 다음
3. **로컬 애플리케이션** import 마지막
4. 각 그룹 사이에 **빈 줄** 하나

```python
# Standard library
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Third-party
import click
import pydantic
import yaml
from fastapi import FastAPI

# Local application
from fastapi_fastkit.commands.base import BaseCommand
from fastapi_fastkit.utils.validation import validate_project_name
from fastapi_fastkit.templates import TemplateManager
```

### Import 모범 사례

- **wildcard import 금지** (`from module import *`)
- 명확성을 위해 **절대 경로 import 사용**
- 항목을 많이 가져올 때는 **개별 항목이 아닌 모듈을 import**

```python
# Good ✅
from fastapi_fastkit.utils import validation, files, formatting

# Good ✅ (적은 수의 항목을 가져올 때)
from fastapi_fastkit.utils.validation import validate_email, validate_project_name

# Bad ❌
from fastapi_fastkit.utils.validation import *

# Bad ❌ (많은 항목을 가져올 때)
from fastapi_fastkit.utils.validation import (
    validate_email, validate_project_name, validate_template_name,
    validate_dependencies, validate_python_version, validate_directory
)
```

## 보안 가이드라인

### 입력 검증

사용자 입력은 항상 검증하고 정화하세요:

```python
def validate_project_name(name: str) -> str:
    """Validate and sanitize project name."""
    if not name:
        raise ValueError("Project name cannot be empty")

    if not name.isidentifier():
        raise ValueError("Project name must be a valid Python identifier")

    if name.startswith('_'):
        raise ValueError("Project name cannot start with underscore")

    if len(name) > 50:
        raise ValueError("Project name too long (max 50 characters)")

    # 위험한 문자를 제거해 정화
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '', name)

    return sanitized
```

### 파일 작업

파일 경로와 작업은 신중히 다루세요:

```python
def create_file_safely(file_path: Path, content: str, base_dir: Path) -> None:
    """Create file safely within base directory."""
    # 디렉터리 traversal 공격을 방지하기 위해 resolve
    resolved_path = file_path.resolve()
    resolved_base = base_dir.resolve()

    # 파일이 base 디렉터리 안에 있는지 확인
    try:
        resolved_path.relative_to(resolved_base)
    except ValueError:
        raise SecurityError(f"File path outside base directory: {file_path}")

    # 부모 디렉터리를 안전하게 생성
    resolved_path.parent.mkdir(parents=True, exist_ok=True)

    # 적절한 권한으로 파일 작성
    resolved_path.write_text(content, encoding='utf-8')
    resolved_path.chmod(0o644)  # 소유자는 읽기/쓰기, 그 외에는 읽기만
```

## 성능 가이드라인

### 효율적인 코드 작성

- 큰 데이터셋에는 **제너레이터 사용**
- **조기 최적화 금지**
- **최적화 전에 프로파일링**

```python
# Good ✅ — 메모리 효율을 위한 제너레이터
def process_large_template(template_files: List[Path]) -> Iterator[ProcessedFile]:
    """Process template files efficiently."""
    for file_path in template_files:
        content = file_path.read_text()
        processed_content = process_template_content(content)
        yield ProcessedFile(path=file_path, content=processed_content)

# Bad ❌ — 모든 것을 메모리에 적재
def process_large_template(template_files: List[Path]) -> List[ProcessedFile]:
    """Process template files."""
    results = []
    for file_path in template_files:
        content = file_path.read_text()
        processed_content = process_template_content(content)
        results.append(ProcessedFile(path=file_path, content=processed_content))
    return results
```

### 캐싱

비싼 작업에는 캐싱을 사용하세요:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_template_metadata(template_path: Path) -> TemplateMetadata:
    """Get template metadata with caching."""
    config_file = template_path / "template.yaml"

    if not config_file.exists():
        return TemplateMetadata(name=template_path.name)

    config = yaml.safe_load(config_file.read_text())
    return TemplateMetadata.from_config(config)
```

## Git 커밋 가이드라인

### 커밋 메시지 형식

conventional commit 형식을 사용하세요:

```
type(scope): description

[optional body]

[optional footer]
```

### 커밋 타입

- **feat**: 새 기능
- **fix**: 버그 수정
- **docs**: 문서 변경
- **style**: 코드 스타일 변경 (포매팅 등)
- **refactor**: 코드 리팩터링
- **test**: 테스트 추가 또는 갱신
- **chore**: 유지보수 작업

### 예시

```bash
# Good ✅
feat(cli): add template validation command

Add new command to validate template structure and configuration.
The command checks for required files, validates YAML syntax,
and ensures template follows conventions.

Closes #123

# Good ✅
fix(templates): handle missing dependency files gracefully

When a template references a requirements file that doesn't exist,
show a clear error message instead of crashing.

# Bad ❌
update stuff

# Bad ❌
Fixed bug
```

## 코드 리뷰 가이드라인

### 작성자에게

코드 리뷰를 요청하기 전에:

1. **모든 테스트 실행**하고 통과 확인
2. **코드 커버리지 유지** 확인
3. 필요 시 **문서 갱신**
4. **커밋 메시지** 컨벤션 준수
5. PR은 **작고 목적이 분명하게** 유지

### 리뷰어에게

코드를 리뷰할 때:

1. **동작 확인** — 의도한 대로 작동하는가?
2. **테스트 검토** — 엣지 케이스가 다뤄졌는가?
3. **문서 검증** — 명확하고 최신 상태인가?
4. **코드 스타일 점검** — 프로젝트 컨벤션을 따르는가?
5. **보안 고려** — 잠재적 취약점은 없는가?

### 리뷰 체크리스트

- [ ] 코드가 스타일 가이드라인을 따름
- [ ] 테스트가 종합적이고 통과함
- [ ] 문서가 갱신됨
- [ ] 보안 취약점 없음
- [ ] 성능 측면이 고려됨
- [ ] 에러 처리가 적절함
- [ ] 커밋 메시지가 컨벤션을 따름

## 도구와 자동화

### Pre-commit 훅

표준을 강제하기 위해 pre-commit 훅을 사용합니다:

```yaml
# .pre-commit-config.yaml
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-toml

-   repo: local
    hooks:
    -   id: format
        name: format
        entry: black --config pyproject.toml --check .
        language: python
        types: [python]
        additional_dependencies: ['black>=24.10.0']
        pass_filenames: false

    -   id: isort-check
        name: isort check
        entry: isort --sp pyproject.toml --check-only --diff .
        language: python
        types: [python]
        additional_dependencies: ['isort>=5.13.2']
        pass_filenames: false

    -   id: isort-fix
        name: isort fix
        entry: isort --sp pyproject.toml .
        language: python
        types: [python]
        additional_dependencies: ['isort>=5.13.2']
        pass_filenames: false

    -   id: black-fix
        name: black fix
        entry: black --config pyproject.toml .
        language: python
        types: [python]
        additional_dependencies: ['black>=24.10.0']
        pass_filenames: false

    -   id: mypy
        name: mypy
        entry: mypy --config-file pyproject.toml src
        language: python
        types: [python]
        additional_dependencies:
          - mypy>=1.12.0
          - rich>=13.9.2
          - click>=8.1.7
          - pyyaml>=6.0.0
          - types-PyYAML>=6.0.12
        pass_filenames: false

ci:
    autofix_commit_msg: 🎨 [pre-commit.ci] Auto format from pre-commit.com hooks
    autoupdate_commit_msg: ⬆ [pre-commit.ci] pre-commit autoupdate
```

!!! note

    Pre-commit 훅은 격리된 Python 환경 (`language: python`) 에서 실행됩니다.

### IDE 설정

권장 VS Code 설정:

```json
{
    "python.linting.enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.path": "isort",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

## 다음 단계

이 가이드라인을 읽은 뒤에는 다음 순서로 진행해 보세요:

1. [개발 환경 설정](development-setup.md)을 따라 **개발 환경 준비**
2. 익숙해질 수 있도록 **작은 기여부터 연습**
3. 불명확한 부분은 GitHub Discussions에서 **질문하기**
4. **기존 코드를 살펴보며** 가이드라인이 실제로 어떻게 적용됐는지 확인

!!! tip "빠른 참조"
    - `make check-all` 로 코드가 모든 가이드라인을 따르는지 검증
    - 이슈를 조기에 잡기 위해 pre-commit 훅을 설정
    - 의문이 있으면 기존 코드 예시 참고
    - 코드 리뷰에서 도움이 필요하면 주저하지 말고 요청

이 가이드라인을 따르면 FastAPI-fastkit의 높은 코드 품질을 유지하면서, 모두가 더 편하게 협업할 수 있습니다! 🚀
