# 開発環境のセットアップ

FastAPI-fastkit に貢献するための開発環境を整える包括的なガイドです。

## 前提条件

開始前に、次が用意されているか確認してください:

- **Python 3.12 以上** がインストール済み
- **Git** がインストールされ設定済み
- **Python と FastAPI の基礎知識**
- **テキストエディタまたは IDE** (VS Code、PyCharm など)

## Makefile による簡単セットアップ

FastAPI-fastkit には、開発環境を簡単に整えるための Makefile が用意されています:

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

このコマンド 1 つで:

- パッケージを開発用依存関係込みの editable モードでインストール
- pre-commit フックをセットアップ
- 開発ツールを設定

!!! note

    このコマンドを実行する前に、仮想環境を作成して有効化しておくのが推奨です。

## 手動セットアップ

手動セットアップを好む場合、または Makefile が動作しない環境では:

### 1. リポジトリをクローン

<div class="termy">

```console
$ git clone https://github.com/bnbong/FastAPI-fastkit.git
$ cd FastAPI-fastkit
```

</div>

### 2. 仮想環境の作成

<div class="termy">

```console
$ python -m venv .venv
$ source .venv/bin/activate  # Windows の場合: .venv\Scripts\activate
```

</div>

### 3. 依存関係のインストール

<div class="termy">

```console
# editable モードで開発用依存も含めてインストール
$ pip install -e ".[dev]"

# あるいは requirements ファイルから
$ pip install -r requirements.txt
$ pip install -r requirements-dev.txt
```

</div>

### 4. Pre-commit フックの設定

<div class="termy">

```console
$ pre-commit install
pre-commit installed at .git/hooks/pre-commit
```

</div>

### 5. インストールの確認

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

## 開発ツール

開発環境にはコード品質を保つためのツールが含まれます:

### ワンライナーコマンド

Makefile を使う:

```console
$ make format lint
Running isort...
Running black...
Running mypy...
✅ All checks passed!
```

付属のスクリプトを使う:

```console
$ ./scripts/format.sh
$ ./scripts/lint.sh
```

### コードフォーマット

**Black** — コードフォーマッタ:

<div class="termy">

```console
$ black src/ tests/
reformatted src/main.py
reformatted tests/test_cli.py
All done! ✨ 🍰 ✨
```

</div>

**isort** — import ソーター:

<div class="termy">

```console
$ isort src/ tests/
Fixing import order in src/main.py
```

</div>

### コードリンティング

**mypy** — 型チェック:

<div class="termy">

```console
$ mypy src/
Success: no issues found in 12 source files
```

</div>

## 利用できる Make コマンド

プロジェクトの Makefile は、よくある開発作業に便利なコマンドを提供します:

### セットアップコマンド

| コマンド | 説明 |
|---|---|
| `make install` | パッケージを本番モードでインストール |
| `make install-dev` | 開発用依存関係込みでインストール |
| `make install-test` | テスト用にインストール (アンインストール + 再インストール) |
| `make uninstall` | パッケージをアンインストール |
| `make clean` | ビルド成果物とキャッシュを削除 |

### コード品質コマンド

| コマンド | 説明 |
|---|---|
| `make format` | black と isort でコードをフォーマット |
| `make format-check` | 変更せずにフォーマットを確認 |
| `make lint` | すべてのリンティング (isort、black、mypy) を実行 |

### テストコマンド

| コマンド | 説明 |
|---|---|
| `make test` | すべてのテストを実行 |
| `make test-verbose` | 詳細出力付きでテスト実行 |
| `make test-coverage` | カバレッジレポート付きでテスト実行 |
| `make coverage-report` | 詳細なカバレッジレポートを生成 (FORMAT=html/xml/json/all) |

### テンプレート検査コマンド

| コマンド | 説明 |
|---|---|
| `make inspect-templates` | すべてのテンプレートを検査 |
| `make inspect-templates-verbose` | 詳細出力付きで検査 |
| `make inspect-template` | 特定のテンプレートを検査 (TEMPLATES パラメータ) |

### ドキュメントコマンド

| コマンド | 説明 |
|---|---|
| `make serve-docs` | ドキュメントをローカルで配信 |
| `make build-docs` | ドキュメントをビルド |

### 翻訳コマンド

| コマンド | 説明 |
|---|---|
| `make translate` | ドキュメントを翻訳 (LANG、PROVIDER、MODEL パラメータ) |

### 例

<div class="termy">

```console
# コードをフォーマットしてすべてのチェックを実行
$ make format lint
Running isort...
Running black...
Running mypy...
✅ All checks passed!

# カバレッジ付きでテスト実行
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

# HTML カバレッジレポートを生成
$ make coverage-report FORMAT=html
🌐 Opening HTML coverage report in browser...

# ドキュメントを韓国語へ翻訳
$ make translate LANG=ko PROVIDER=github MODEL=gpt-4o-mini
Starting translation...
Running: python scripts/translate.py --target-lang ko --api-provider github --model gpt-4o-mini
```

</div>

## プロジェクト構造

開発の前にプロジェクト構造を理解しておきましょう:

```bash
FastAPI-fastkit/
├── src/
│   ├── fastapi_fastkit/
│   │   ├── __main__.py                      # アプリのエントリポイント
│   │   ├── backend/
│   │   │   ├── inspector.py                 # FastAPI-fastkit テンプレートインスペクタ
│   │   │   ├── interactive/
│   │   │   │   ├── config_builder.py        # 対話型モードの設定ビルダー
│   │   │   │   ├── prompts.py               # 対話型モードのプロンプト
│   │   │   │   ├── selectors.py             # 対話型モードのセレクタ
│   │   │   │   └── validators.py            # 対話型モードの入力バリデータ
│   │   │   ├── main.py                      # バックエンドのロジックエントリポイント
│   │   │   ├── package_managers/
│   │   │   │   ├── base.py                  # パッケージマネージャーのベースクラス
│   │   │   │   ├── factory.py               # パッケージマネージャーファクトリ
│   │   │   │   ├── pdm_manager.py           # PDM パッケージマネージャー
│   │   │   │   ├── pip_manager.py           # pip パッケージマネージャー
│   │   │   │   ├── poetry_manager.py        # Poetry パッケージマネージャー
│   │   │   │   └── uv_manager.py            # uv パッケージマネージャー
│   │   │   ├── project_builder/
│   │   │   │   ├── config_generator.py      # 設定ジェネレータ
│   │   │   │   └── dependency_collector.py  # 依存関係収集
│   │   │   └── transducer.py                # プロジェクトビルダー用トランスデューサ
│   │   ├── cli.py                           # FastAPI-fastkit のメイン CLI エントリポイント
│   │   ├── core/
│   │   │   ├── exceptions.py                # 例外処理
│   │   │   └── settings.py                  # 設定
│   │   ├── fastapi_project_template/
│   │   │   ├── PROJECT_README_TEMPLATE.md   # fastkit テンプレート用 README ベース
│   │   │   ├── README.md                    # fastkit テンプレートの README
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
│   │       ├── logging.py                   # ロギング設定
│   │       └── main.py                      # FastAPI-fastkit のメインエントリポイント
│   └── logs
├── tests
│   ├── conftest.py                          # pytest 設定
│   ├── test_backends/
│   ├── test_cli_operations/
│   ├── test_core.py
│   ├── test_rich/
│   ├── test_templates/
│   └── test_utils.py
├── uv.lock
├── docs/                                    # ドキュメント
├── scripts/                                 # 開発スクリプト
├── mkdocs.yml
├── overrides/                               # mkdocs オーバーライド
├── pdm.lock
├── pyproject.toml
├── requirements-docs.txt                    # ドキュメント用依存
├── requirements.txt                         # 開発用依存
├── CHANGELOG.md
├── CITATION.cff
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE
├── MANIFEST.in
├── Makefile
├── README.md
├── SECURITY.md
└── env.example                              # 環境変数の例 (翻訳用 AI モデルの env を構成)
```

### 主要ディレクトリ

- **`src/fastapi_fastkit/`** — メインパッケージのソース
    - **`cli.py`** — メイン CLI のエントリポイント
    - **`backend/`** — コアのバックエンドロジック
        - **`inspector.py`** — テンプレートインスペクタ
        - **`interactive/`** — 対話型モードの構成要素 (プロンプト、セレクタ、バリデータ)
        - **`package_managers/`** — パッケージマネージャー実装 (pip、uv、pdm、poetry)
        - **`project_builder/`** — プロジェクト構築ユーティリティ
        - **`transducer.py`** — テンプレートトランスデューサ
    - **`core/`** — コアの設定と例外
    - **`fastapi_project_template/`** — プロジェクトテンプレート (fastapi-default、fastapi-async-crud など)
    - **`utils/`** — 共有ユーティリティ
- **`tests/`** — テストスイート
    - **`test_backends/`** — バックエンド固有のテスト
    - **`test_cli_operations/`** — CLI 操作のテスト
    - **`test_templates/`** — テンプレートシステムのテスト
- **`docs/`** — ドキュメント (MkDocs)
    - ユーザーガイド、チュートリアル、API リファレンス

## 開発ワークフロー

### 1. 機能ブランチを作成

<div class="termy">

```console
$ git checkout -b feature/add-new-template
Switched to a new branch 'feature/add-new-template'
```

</div>

### 2. 変更を実装

コードを編集し、機能を追加・バグを修正します...

### 3. テストとチェックを実行

<div class="termy">

```console
$ make dev-check
Running all quality checks...
Running all tests...
✅ All tests passed!
```

</div>

### 4. 変更をコミット

pre-commit フックが自動的に実行されます:

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

### 5. push して PR を作成する

<div class="termy">

```console
$ git push origin feature/add-new-template
$ gh pr create --title "Add new FastAPI template with authentication"
```

</div>

## テスト

### テストの実行

**すべてのテスト:**

<div class="termy">

```console
$ make test
# または
$ python -m pytest
```

</div>

**特定のテストファイル:**

<div class="termy">

```console
$ python -m pytest tests/test_cli.py -v
```

</div>

**カバレッジ付き:**

<div class="termy">

```console
$ make test-coverage
# または
$ python -m pytest --cov=src --cov-report=html
```

</div>

### テストの書き方

新機能を追加する際は、必ずテストも含めてください:

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

### テストの種類

**単体テスト** — 個別の関数やクラスをテスト:

```python
def test_validate_project_name():
    assert validate_project_name("valid-name") is True
    assert validate_project_name("invalid name!") is False
```

**統合テスト** — コマンドの相互作用をテスト:

```python
def test_init_command_creates_project(tmp_path):
    result = runner.invoke(cli, ['init'], input='test-project\n...')
    assert result.exit_code == 0
    assert (tmp_path / "test-project").exists()
```

**エンドツーエンドテスト** — 完全なワークフローをテスト:

```python
def test_full_project_creation_workflow(tmp_path):
    # プロジェクトを作成
    result = runner.invoke(cli, ['init'], input='...')
    assert result.exit_code == 0

    # ルートを追加
    result = runner.invoke(cli, ['addroute', 'test-project', 'users'])
    assert result.exit_code == 0

    # ファイルが存在することを検証
    assert (tmp_path / "test-project" / "src" / "api" / "routes" / "users.py").exists()
```

## ドキュメント

### ドキュメントをローカルで配信

<div class="termy">

```console
$ make serve-docs
INFO     -  Building documentation...
INFO     -  Cleaning site directory
INFO     -  Documentation built in 0.43 seconds
INFO     -  [14:30:00] Serving on http://127.0.0.1:8000/
```

</div>

### ドキュメントのビルド

<div class="termy">

```console
$ make build-docs
INFO     -  Building documentation...
INFO     -  Documentation built in 0.43 seconds
```

</div>

### ドキュメントの書き方

ドキュメントは Markdown で書かれ、MkDocs でビルドされます。例の構造:

**機能ガイドのテンプレート:**

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

`mkdocs-material` の詳しい使い方は、[mkdocs-material のドキュメント](https://squidfunk.github.io/mkdocs-material/reference/admonitions/) を参照してください。

## コードスタイルガイドライン

### Python のコードスタイル

[PEP 8](https://www.python.org/dev/peps/pep-0008/) に従い、次の固有ルールを採用:

- **行長**: 88 文字 (Black デフォルト)
- **import**: isort で整理
- **型ヒント**: すべての公開関数で必須
- **docstring**: すべての公開 API で Google スタイル

### 例

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

    # 実装 ...
    return created_files
```

## 環境変数

開発時には次の環境変数を設定できます:

| 変数 | 説明 | デフォルト |
|---|---|---|
| `FASTKIT_DEBUG` | デバッグログを有効化 | `False` |
| `FASTKIT_DEV_MODE` | 開発機能を有効化 | `False` |
| `FASTKIT_TEMPLATE_DIR` | カスタムテンプレートディレクトリ | 組み込みテンプレート |
| `FASTKIT_CONFIG_DIR` | 設定ディレクトリ | `~/.fastkit` |
| `TRANSLATION_API_KEY` | 翻訳 API キー ([Github AI モデルプロバイダ](https://github.com/marketplace/models/azure-openai) を使う場合は GitHub PAT を指定) | `None` |

<div class="termy">

```console
$ export FASTKIT_DEBUG=true
$ export FASTKIT_DEV_MODE=true
$ fastkit init
DEBUG: Loading configuration from /home/user/.fastkit/
DEBUG: Available templates: ['fastapi-default', ...]
```

</div>

ほかの環境変数設定については、[@settings.py](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/core/settings.py) モジュールを参照してください。

## トラブルシューティング

### よくある問題

**1. pre-commit フックが失敗する:**

<div class="termy">

```console
$ git commit -m "Fix bug"
black....................................................................Failed
hookid: black

Files were modified by this hook. Additional output:

would reformat src/cli.py
```

</div>

**解決策:** フォーマッタを実行し、再度コミット:

<div class="termy">

```console
$ make format
$ git add .
$ git commit -m "Fix bug"
```

</div>

**2. 異なる Python バージョンでテストが失敗する:**

**解決策:** tox で複数の Python バージョンをテスト:

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

**3. 開発時の import エラー:**

**解決策:** editable モードでインストール:
<div class="termy">

```console
$ pip install -e .
```

</div>

### ヘルプ

- **[GitHub Issues](https://github.com/bnbong/FastAPI-fastkit/issues)**: バグ報告と機能リクエスト
- **[GitHub Discussions](https://github.com/bnbong/FastAPI-fastkit/discussions)**: 質問とアイデア共有
- **ドキュメント**: [ユーザーガイド](../user-guide/installation.md) を参照

## コントリビュートガイドライン

### PR 提出前

1. **すべてのチェックを実行:** `make dev-check`
2. 必要に応じて **ドキュメントを更新**
3. 新機能には **テストを追加**
4. **コミットメッセージ規約に従う**

### コミットメッセージ形式

```
type(scope): brief description

Longer description if needed

Fixes #123
```

**種別:**

- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント変更
- `style`: コードスタイル変更
- `refactor`: リファクタリング
- `test`: テストの追加・変更
- `chore`: メンテナンス作業

**例:**

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

## リリースプロセス

メンテナー向けのリリース手順:

1. `setup.py` と `__init__.py` で **バージョンを更新**
2. **CHANGELOG.md を更新**
3. **リリース PR を作成**
4. マージ後に **タグを付与**
5. **GitHub Actions** が自動でビルドおよび公開

<div class="termy">

```console
$ git tag v1.2.0
$ git push origin v1.2.0
```

</div>

## 次のステップ

開発環境が整ったら:

1. アーキテクチャを把握するため [**コードベースを探索**](https://github.com/bnbong/FastAPI-fastkit/tree/main/src/fastapi_fastkit) する
2. **テストスイートを実行** してすべて動作することを確認
3. GitHub から取り組む [**Issue**](https://github.com/bnbong/FastAPI-fastkit/issues) を選ぶ
4. ほかの貢献者とつながるため [**Discussions**](https://github.com/bnbong/FastAPI-fastkit/discussions) に参加

Happy coding! 🚀

!!! tip "開発のヒント"
    - コミット前に `make dev-check` を実行
    - テストを先に書く (TDD アプローチ)
    - コミットは小さく、焦点を絞る
    - 新機能には合わせてドキュメントを更新
