# コードガイドライン

FastAPI-fastkit へ貢献する際のコーディング標準とベストプラクティスをまとめた包括的なガイドです。

## 概要

これらのガイドラインは、FastAPI-fastkit プロジェクト全体でコード品質、一貫性、保守性を保つためのものです。これらの基準に従うことで、読みやすく、保守しやすく、拡張しやすいコードベースが維持できます。

## Python のコードスタイル

### PEP 8 準拠

[PEP 8](https://www.python.org/dev/peps/pep-0008/) に従い、次の固有設定を使用します:

- **行長**: 88 文字 (Black デフォルト)
- **インデント**: スペース 4 つ (タブ禁止)
- **末尾カンマ**: 複数行の構造では必須
- **文字列クオート**: ダブルクオート推奨

### コードフォーマット

自動フォーマットには **Black** を使用します:

```python
# 良い例 ✅
def create_project(
    name: str,
    template: str,
    options: Dict[str, Any],
) -> ProjectResult:
    """Create a new FastAPI project."""
    return ProjectResult(name=name, template=template)

# 悪い例 ❌
def create_project(name: str, template: str, options: Dict[str,Any])->ProjectResult:
    """Create a new FastAPI project."""
    return ProjectResult(name=name,template=template)
```

### import の整理

import の整理には **isort** を使用します:

```python
# 標準ライブラリ
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union

# サードパーティ
import click
import pydantic
from fastapi import FastAPI

# ローカル
from fastapi_fastkit.commands import BaseCommand
from fastapi_fastkit.utils import validation
from fastapi_fastkit.templates.manager import TemplateManager
```

## 型ヒント

### 必須の型ヒント

すべての公開関数とメソッドには型ヒントが必要です:

```python
# 良い例 ✅
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
        # 実装 ...
        created_files.append(file_path)
    return created_files

# 悪い例 ❌
def validate_project_name(name):
    return name.isidentifier() and not name.startswith('_')
```

### 複雑な型注釈

複雑な構造には適切な型注釈を使用します:

```python
from typing import Dict, List, Optional, Union, Tuple, Any
from pathlib import Path

# 複雑な型のエイリアス
ProjectConfig = Dict[str, Union[str, bool, List[str]]]
FileMapping = Dict[Path, str]
ValidationResult = Tuple[bool, Optional[str]]

def process_template(
    template_path: Path,
    config: ProjectConfig,
    output_dir: Optional[Path] = None,
) -> ValidationResult:
    """Process template with configuration."""
    # 実装 ...
    return True, None
```

## 命名規則

### 変数と関数

- 変数と関数には **snake_case**
- **目的が分かる名前** を付ける
- **省略形は避ける** (一般的に通じるものを除く)

```python
# 良い例 ✅
project_name = "my-api"
template_directory = Path("templates")
user_input_data = get_user_input()

def validate_email_address(email: str) -> bool:
    """Validate email address format."""
    return "@" in email and "." in email

# 悪い例 ❌
proj_nm = "my-api"
temp_dir = Path("templates")
usr_data = get_input()

def validate_email(e):
    return "@" in e and "." in e
```

### クラス

- クラス名には **PascalCase**
- **記述的かつ具体的** な名前

```python
# 良い例 ✅
class SomeClass:
    """Represents example class of FastAPI-fastkit."""
    pass

class SomeClassValidationError(Exception):
    """Raised when example class validation fails."""
    pass

class UserInputHandler:
    """Handles user input validation and processing."""
    pass

# 悪い例 ❌
class Class:
    pass

class Error(Exception):
    pass

class Handler:
    pass
```

### 定数

- アンダースコア区切りの **UPPER_CASE**
- **モジュールレベル** に限定

```python
# 良い例 ✅
DEFAULT_TEMPLATE_NAME = "fastapi-default"
MAX_PROJECT_NAME_LENGTH = 50
SUPPORTED_PYTHON_VERSIONS = ["3.8", "3.9", "3.10", "3.11", "3.12"]

# 悪い例 ❌
default_template = "fastapi-default"
maxLength = 50
versions = ["3.8", "3.9", "3.10", "3.11", "3.12"]
```

## ドキュメント標準

### docstring

すべての公開 API には **Google スタイルの docstring** を使用します:

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
    # 実装 ...
    pass
```

### コメント

- **何 (WHAT) ではなく、なぜ (WHY) を説明**
- **必要最小限** に — コードは自己説明的であるべき
- **コード変更時にコメントも更新**

```python
# 良い例 ✅
def validate_dependencies(requirements: List[str]) -> bool:
    """Validate project dependencies."""
    # 実験的なパッケージを許可するため、開発モードでは検証をスキップする
    if os.getenv("FASTKIT_DEV_MODE"):
        return True

    # 既知のセキュリティ脆弱性に対して各要件を確認する
    for requirement in requirements:
        if is_vulnerable_package(requirement):
            return False

    return True

# 悪い例 ❌
def validate_dependencies(requirements: List[str]) -> bool:
    """Validate project dependencies."""
    # dev モードかチェック
    if os.getenv("FASTKIT_DEV_MODE"):
        return True

    # 要件をループ
    for requirement in requirements:
        # 脆弱かチェック
        if is_vulnerable_package(requirement):
            return False

    # true を返す
    return True
```

## エラー処理

### 例外処理

- 可能な限り **具体的な例外をキャッチ**
- **意味のあるエラーメッセージ** を提供
- **エラーは適切にログ出力**

```python
# 良い例 ✅
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

# 悪い例 ❌
def load_template_config(template_path: Path) -> Dict[str, Any]:
    """Load template configuration from file."""
    config_file = template_path / "template.yaml"

    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise Exception(f"Error loading config: {e}")
```

### カスタム例外

エラー条件ごとに専用の例外を定義します:

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

## テスト基準

### テスト構造

明快な構成と命名でテストを整理します:

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

### テストカバレッジ

- 新規コードでは **90% 以上のカバレッジ** を目標に
- **エッジケースとエラー条件** をテスト
- **外部依存はモック**

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

## import ガイドライン

### import の整理

!!! note

    `isort` フォーマッタが自動で import を整えます。`bash scripts/format.sh` を実行するだけで簡単に整理できます。

1. **標準ライブラリ** を最初
2. **サードパーティ** を次に
3. **ローカルアプリケーション** を最後に
4. 各グループの間に **空行 1 行**

```python
# 標準ライブラリ
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# サードパーティ
import click
import pydantic
import yaml
from fastapi import FastAPI

# ローカルアプリケーション
from fastapi_fastkit.commands.base import BaseCommand
from fastapi_fastkit.utils.validation import validate_project_name
from fastapi_fastkit.templates import TemplateManager
```

### import のベストプラクティス

- **ワイルドカード import を避ける** (`from module import *`)
- 明快さのため **絶対 import を使う**
- 多数の項目を import するときは **モジュールを import する** (個別項目ではなく)

```python
# 良い例 ✅
from fastapi_fastkit.utils import validation, files, formatting

# 良い例 ✅ (少数のみ import する場合)
from fastapi_fastkit.utils.validation import validate_email, validate_project_name

# 悪い例 ❌
from fastapi_fastkit.utils.validation import *

# 悪い例 ❌ (多数の項目を import する場合)
from fastapi_fastkit.utils.validation import (
    validate_email, validate_project_name, validate_template_name,
    validate_dependencies, validate_python_version, validate_directory
)
```

## セキュリティガイドライン

### 入力検証

ユーザー入力は常に検証 / サニタイズしてください:

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

    # 危険な文字を取り除いてサニタイズ
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '', name)

    return sanitized
```

### ファイル操作

ファイルパスや操作には注意してください:

```python
def create_file_safely(file_path: Path, content: str, base_dir: Path) -> None:
    """Create file safely within base directory."""
    # ディレクトリトラバーサル攻撃を防ぐためにパスを解決
    resolved_path = file_path.resolve()
    resolved_base = base_dir.resolve()

    # ファイルがベースディレクトリ内にあることを確認
    try:
        resolved_path.relative_to(resolved_base)
    except ValueError:
        raise SecurityError(f"File path outside base directory: {file_path}")

    # 親ディレクトリを安全に作成
    resolved_path.parent.mkdir(parents=True, exist_ok=True)

    # 適切な権限でファイルを書き込み
    resolved_path.write_text(content, encoding='utf-8')
    resolved_path.chmod(0o644)  # 所有者は読み書き、それ以外は読み取りのみ
```

## パフォーマンスガイドライン

### 効率的なコードの書き方

- 大きなデータセットには **ジェネレータを使う**
- **早すぎる最適化は避ける**
- **最適化前にプロファイル**

```python
# 良い例 ✅ — メモリ効率のためのジェネレータ
def process_large_template(template_files: List[Path]) -> Iterator[ProcessedFile]:
    """Process template files efficiently."""
    for file_path in template_files:
        content = file_path.read_text()
        processed_content = process_template_content(content)
        yield ProcessedFile(path=file_path, content=processed_content)

# 悪い例 ❌ — すべてをメモリにロード
def process_large_template(template_files: List[Path]) -> List[ProcessedFile]:
    """Process template files."""
    results = []
    for file_path in template_files:
        content = file_path.read_text()
        processed_content = process_template_content(content)
        results.append(ProcessedFile(path=file_path, content=processed_content))
    return results
```

### キャッシュ

重い処理にはキャッシュを使います:

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

## Git コミットガイドライン

### コミットメッセージ形式

Conventional Commits 形式を使います:

```
type(scope): description

[optional body]

[optional footer]
```

### コミット種別

- **feat**: 新機能
- **fix**: バグ修正
- **docs**: ドキュメント変更
- **style**: コードスタイル変更 (フォーマットなど)
- **refactor**: リファクタリング
- **test**: テストの追加 / 更新
- **chore**: メンテナンス作業

### 例

```bash
# 良い例 ✅
feat(cli): add template validation command

Add new command to validate template structure and configuration.
The command checks for required files, validates YAML syntax,
and ensures template follows conventions.

Closes #123

# 良い例 ✅
fix(templates): handle missing dependency files gracefully

When a template references a requirements file that doesn't exist,
show a clear error message instead of crashing.

# 悪い例 ❌
update stuff

# 悪い例 ❌
Fixed bug
```

## コードレビューガイドライン

### 著者向け

レビュー依頼前に確認してほしいこと:

1. **すべてのテストを実行** し、通過していることを確認
2. **コードカバレッジ** が維持されているか確認
3. 必要に応じて **ドキュメントを更新**
4. **コミットメッセージ規約** に従う
5. PR は **小さく、焦点を絞った形** で

### レビュアー向け

コードレビューの際の観点:

1. **機能性** — 意図どおり動作するか?
2. **テスト** — エッジケースまでカバーされているか?
3. **ドキュメント** — 明快で最新か?
4. **コードスタイル** — プロジェクト規約に従っているか?
5. **セキュリティ** — 潜在的な脆弱性はないか?

### レビューチェックリスト

- [ ] コードがスタイルガイドラインに従っている
- [ ] テストが十分で、すべて通過している
- [ ] ドキュメントが更新されている
- [ ] セキュリティ上の問題がない
- [ ] パフォーマンス考慮がされている
- [ ] エラーハンドリングが適切
- [ ] コミットメッセージが規約に従っている

## ツールと自動化

### Pre-commit フック

基準の徹底に pre-commit フックを使用します:

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

    Pre-commit フックは隔離された Python 環境 (`language: python`) を使います。

### IDE 設定

VS Code の推奨設定:

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

## 次のステップ

このガイドラインを把握したら:

1. [開発環境セットアップ](development-setup.md) に従って **開発環境を構築**
2. **小さな貢献から始めて** 慣れる
3. 不明点があれば GitHub Discussions で **質問**
4. ガイドラインの実例を確認するため **既存コードを読む**

!!! tip "クイックリファレンス"
    - `make check-all` でコードがガイドラインに準拠しているか検証
    - 早期発見のため pre-commit フックをセットアップ
    - 迷ったら既存コードを参照
    - コードレビューでの質問もどうぞ気軽に

これらのガイドラインに従うことで、FastAPI-fastkit の高いコード品質が保たれ、誰にとっても協働がしやすくなります! 🚀
