# FastAPI テンプレート作成ガイド

FastAPI-fastkit に新しい FastAPI プロジェクトテンプレートを追加するための包括的なガイドです。

## 🎯 概要

新しいテンプレートの追加は、次の 5 ステップで進めます:

1. **📋 計画と設計** — テンプレートの目的と構成を定義
2. **🏗️ テンプレートの実装** — 必要な構造とファイルを作成
3. **🔍 ローカル検証** — インスペクタでテンプレートを検証
4. **📚 ドキュメント** — README と利用ガイドを記述
5. **🚀 提出とレビュー** — PR を作成しコミュニティのレビューを受ける

## 📋 ステップ 1: 計画と設計

### テンプレートの目的を定義する

新しいテンプレートを作る前に、次の問いに答えてください:

- **このテンプレート固有の価値は何か?**
- **既存のテンプレートとどう差別化されるか?**
- **どのユーザー層が想定読者か?**
- **どんな技術スタックを含めるか?**

### テンプレートの命名規則

```
fastapi-{purpose}-{stack}
```

例:

- `fastapi-microservice` (マイクロサービステンプレート)
- `fastapi-graphql` (GraphQL 統合テンプレート)
- `fastapi-auth-jwt` (JWT 認証テンプレート)

### 技術スタックの計画

含めるメイン技術を事前に定義します:

```yaml
# 例: fastapi-microservice テンプレート
core_dependencies:
  - fastapi
  - uvicorn
  - pydantic
  - pydantic-settings

additional_features:
  - sqlalchemy (ORM)
  - alembic (マイグレーション)
  - redis (キャッシュ)
  - celery (バックグラウンドタスク)
  - pytest (テスト)

development_tools:
  - black (コードフォーマット)
  - isort (import ソート)
  - mypy (型チェック)
  - pre-commit (Git フック)
```

## 🏗️ ステップ 2: テンプレートの実装

### 必須ディレクトリ構造

```
fastapi-{template-name}/
├── src/                          # アプリケーションのソース
│   ├── main.py-tpl              # ✅ FastAPI アプリのエントリポイント (必須)
│   ├── __init__.py-tpl
│   ├── api/                     # API ルーター
│   │   ├── __init__.py-tpl
│   │   ├── api.py-tpl           # メインの API ルーター
│   │   └── routes/              # 個別ルート
│   │       ├── __init__.py-tpl
│   │       └── items.py-tpl     # サンプルルート
│   ├── core/                    # コア設定
│   │   ├── __init__.py-tpl
│   │   └── config.py-tpl        # 設定管理
│   ├── crud/                    # CRUD ロジック
│   │   ├── __init__.py-tpl
│   │   └── items.py-tpl
│   ├── schemas/                 # Pydantic モデル
│   │   ├── __init__.py-tpl
│   │   └── items.py-tpl
│   └── utils/                   # ユーティリティ
│       ├── __init__.py-tpl
│       └── helpers.py-tpl
├── tests/                       # ✅ テスト (必須)
│   ├── __init__.py-tpl
│   ├── conftest.py-tpl         # pytest 設定
│   └── test_items.py-tpl       # サンプルテスト
├── scripts/                     # スクリプト
│   ├── format.sh-tpl           # コードフォーマット
│   ├── lint.sh-tpl             # リンティング
│   ├── run-server.sh-tpl       # サーバー起動
│   └── test.sh-tpl             # テスト実行
├── pyproject.toml-tpl           # ✅ 一次メタデータ (PEP 621、推奨)
├── setup.py-tpl                # 🟡 レガシーメタデータ (互換のため受け付け)
├── requirements.txt-tpl         # 🟡 pyproject が依存関係を宣言する場合は任意
├── setup.cfg-tpl               # 開発ツール設定
├── README.md-tpl               # ✅ プロジェクトドキュメント (必須)
├── .env-tpl                    # 環境変数テンプレート
└── .gitignore-tpl              # Git ignore ファイル
```

**最低限必要なファイル。** テンプレートは次を提供する必要があります:

- `tests/` ディレクトリ
- `README.md-tpl`
- 少なくとも 1 つのメタデータファイル: `pyproject.toml-tpl` (推奨、PEP 621) または `setup.py-tpl` (レガシー、引き続き受け付け)
- 次のいずれかに `fastapi` を依存関係として宣言: `pyproject.toml-tpl` の `[project].dependencies`、`requirements.txt-tpl`、または `setup.py-tpl` の `install_requires`

`requirements.txt-tpl` は、`pyproject.toml-tpl` が `[project].dependencies` を宣言している場合は厳密には不要です。新しいテンプレートは **`pyproject.toml-tpl` を一次メタデータファイルとして採用すべきです**。

### ファイル作成ガイド

#### 1. main.py-tpl の書き方

```python
"""
FastAPI アプリのエントリポイント

このファイルは、FastAPI-fastkit で作成された <project_name> プロジェクトの
メインアプリケーションです。
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.api import api_router
from core.config import settings

# FastAPI アプリを作成 (インスペクタの検証で必須)
app = FastAPI(
    title="<project_name>",
    description="Project created with FastAPI-fastkit",
    version="1.0.0",
)

# CORS ミドルウェア設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API ルーターを登録
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {"message": "Hello from <project_name>!"}

@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### 2. pyproject.toml-tpl の書き方 (推奨)

新しいテンプレートは PEP 621 形式の `pyproject.toml-tpl` でメタデータと依存関係を宣言すべきです。最低限、`[project]` セクションに `name`、`version`、`description`、そして `fastapi` を含む `dependencies` リストを公開してください。テンプレートは、`is_fastkit_project()` がユーザーのワークスペース内の無関係な FastAPI プロジェクトと区別できるよう、FastAPI-fastkit の識別マーカーを 2 つ持つ必要があります:

- `description` の `[FastAPI-fastkit templated]` 接頭辞
- `managed = true` を持つ専用の `[tool.fastapi-fastkit]` テーブル

検出はどちらかのマーカーがあれば成功します (大文字小文字は区別しません)。テンプレートが省略していてもプロジェクト生成時にメタデータ注入が両方を追加しますが、作者は明示的に含めるべきです。

```toml
[project]
name = "<project_name>"
version = "0.1.0"
description = "[FastAPI-fastkit templated] <description>"
authors = [
    {name = "<author>", email = "<author_email>"},
]
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.34.0",
    "pydantic>=2.10.0",
    "pydantic-settings>=2.7.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "httpx>=0.28.0",
]

[tool.fastapi-fastkit]
managed = true

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

#### 3. requirements.txt-tpl の書き方 (任意)

`pyproject.toml-tpl` が `[project].dependencies` を宣言している場合は任意です。`pip` 中心のワークフローを好むテンプレートでは引き続き有用です。

```txt
# FastAPI コア依存 (必須)
fastapi==0.104.1
uvicorn[standard]==0.24.0

# データ検証
pydantic==2.5.0
pydantic-settings==2.1.0

# 環境変数管理
python-dotenv==1.0.0

# データベース (必要な場合)
sqlalchemy==2.0.23
alembic==1.13.0

# 開発ツール
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2

# コード品質
black==23.11.0
isort==5.12.0
mypy==1.7.1
```

#### 4. setup.py-tpl の書き方 (レガシー — pyproject がある場合は任意)

レガシーテンプレートのために残されています。`pyproject.toml-tpl` を提供する新規テンプレートでは、このファイルは不要です。

```python
"""
<project_name> パッケージのセットアップ

FastAPI-fastkit で作成されたプロジェクトです。
"""
from setuptools import find_packages, setup

# 依存関係リスト (型注釈が必要)
install_requires: list[str] = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "python-dotenv>=1.0.0",
]

setup(
    name="<project_name>",
    version="1.0.0",
    description="[FastAPI-fastkit templated] <description>",  # is_fastkit_project() が利用する識別マーカー
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="<author>",
    author_email="<author_email>",
    packages=find_packages(),
    install_requires=install_requires,
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
```

#### 5. テストファイルの書き方

```python
# tests/test_items.py-tpl
"""
Items API テストモジュール
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    """ルートエンドポイントのテスト"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_health_check():
    """ヘルスチェックのテスト"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_create_item():
    """item 作成のテスト"""
    item_data = {
        "name": "Test Item",
        "description": "Test Description"
    }
    response = client.post("/api/v1/items/", json=item_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == item_data["name"]
    assert data["description"] == item_data["description"]

def test_read_items():
    """item 一覧取得のテスト"""
    response = client.get("/api/v1/items/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

## 🔍 ステップ 3: ローカル検証

### 自動検証スクリプトの実行

新しいテンプレートが準備できたら、次のコマンドで検証します:

```bash
# すべてのテンプレートを検証
make inspect-templates

# 特定のテンプレートだけ検証
make inspect-template TEMPLATES="fastapi-your-template"

# 詳細出力付きで検証
python scripts/inspect-templates.py --templates "fastapi-your-template" --verbose
```

!!! note

    PR を提出すると、**Template PR Inspection** ワークフローが自動的に走り、テンプレート変更を検証します。フィードバックは PR に直接届きます。

### 検証チェックリスト

インスペクタが自動で確認する項目です:

#### ✅ ファイル構造の検証

- [ ] `tests/` ディレクトリが存在
- [ ] `README.md-tpl` ファイルが存在
- [ ] `pyproject.toml-tpl` (推奨) または `setup.py-tpl` (レガシー) のいずれかが存在

#### ✅ 拡張子の検証

- [ ] すべての Python ファイルが `.py-tpl` 拡張子
- [ ] `.py` 拡張子のファイルが存在しない

#### ✅ 依存関係の検証

- [ ] 次のいずれかに `fastapi` が宣言されている:
    - [ ] `pyproject.toml-tpl` の `[project].dependencies` (推奨)
    - [ ] `requirements.txt-tpl`
    - [ ] `setup.py-tpl` の `install_requires`

#### ✅ FastAPI 実装の検証

- [ ] `main.py-tpl` に `FastAPI` import がある
- [ ] `main.py-tpl` に `app = FastAPI()` のようなアプリ生成がある

#### ✅ テスト実行の検証

- [ ] 仮想環境の作成に成功
- [ ] 依存関係のインストールに成功
- [ ] すべての pytest テストが通過

#### ✅ 自動テンプレートテスト

FastAPI-fastkit には、すべてのテンプレートで包括的テストを走らせる **自動テンプレートテスト** が含まれます:

**テストカバレッジ:**

- ✅ テンプレート生成プロセス
- ✅ プロジェクトメタデータの注入
- ✅ 仮想環境のセットアップ
- ✅ 依存関係のインストール (すべてのパッケージマネージャー)
- ✅ 基本的なプロジェクト構造の検証
- ✅ FastAPI プロジェクトの識別

**テストの実行:**
```console
# すべてのテンプレートを自動テスト
$ pytest tests/test_templates/test_all_templates.py -v

# 特定のテンプレートをテスト
$ pytest tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[your-template-name] -v
```

**テンプレートテストの自動検出:**
新しいテンプレートは **設定なしで自動検出** されてテストされます:

1. ✅ **設定不要**: テンプレートを追加 → 自動でテスト
2. ✅ **一貫したテスト**: すべてのテンプレートに同じ品質基準
3. ✅ **複数のパッケージマネージャー**: UV、PDM、Poetry、PIP でテスト
4. ✅ **包括的な検証**: 構造、メタデータ、機能のチェック

**これがあなたにとって意味すること:**

- 🚀 **`FastAPI-fastkit` 本体側にテストファイルを追加する必要なし**: テンプレートは自動でテストされます
- ⚡ **開発の高速化**: テンプレート内容に集中、テストのお膳立て不要
- 🛡️ **品質保証**: すべてのテンプレートで一貫したテスト
- 🔄 **CI/CD 連携**: PR で自動的にテスト

**手動テストもまだ必要なケース:**

- 🧪 **テンプレート固有の機能**: ビジネスロジックや独自機能
- 🔧 **統合テスト**: 外部サービスや複雑なワークフロー
- 📱 **エンドツーエンドシナリオ**: ユーザーワークフロー全体

**テストのベストプラクティス:**
```console
# 1. テンプレートをローカルでテスト
$ fastkit startdemo your-template-name

# 2. 自動テストを実行
$ pytest tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[your-template-name] -v

# 3. 異なるパッケージマネージャーでテスト
$ fastkit startdemo your-template-name --package-manager poetry
$ fastkit startdemo your-template-name --package-manager pdm
$ fastkit startdemo your-template-name --package-manager uv
```

### 手動検証チェックリスト

自動検証に加えて、次の項目を手動でチェックしてください:

#### 🔧 コード品質

- [ ] PEP 8 スタイルガイドに従っている
- [ ] 適切な型ヒントを使用
- [ ] 意味のある変数名・関数名
- [ ] 適切なコメントと docstring

#### 🏗️ アーキテクチャ

- [ ] 関心事の分離 (API、ビジネスロジック、データアクセス)
- [ ] 再利用可能なコンポーネント設計
- [ ] 拡張可能な構造
- [ ] セキュリティのベストプラクティス適用

#### 📚 ドキュメント

- [ ] README.md-tpl が PROJECT_README_TEMPLATE.md の形式に従っている
- [ ] インストール / 実行方法が明記されている
- [ ] API ドキュメント (OpenAPI/Swagger)
- [ ] 環境変数の説明

## 📚 ステップ 4: ドキュメント

### README.md-tpl の作成

[PROJECT_README_TEMPLATE.md](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/PROJECT_README_TEMPLATE.md) のガイドに沿って書いてください。

### テンプレート説明ドキュメントの作成

新しいテンプレートの説明を `src/fastapi_fastkit/fastapi_project_template/README.md` に追加します:

```markdown
## fastapi-your-template

新しいテンプレートの簡単な説明とユースケースをここに書きます。

### 機能:
- 機能 1
- 機能 2
- 機能 3

### ユースケース:
- ユースケース 1
- ユースケース 2
```

## 🚀 ステップ 5: 提出とレビュー

### PR 作成前のチェックリスト

- [ ] すべての自動検証が通過 (`make inspect-templates`)
- [ ] コードフォーマット完了 (`make format`)
- [ ] リンティングチェック通過 (`make lint`)
- [ ] すべてのテスト通過 (`make test`)
- [ ] ドキュメント完成
- [ ] CONTRIBUTING.md ガイドラインに準拠

### PR タイトルと説明

```
[TEMPLATE] Add fastapi-{template-name} template

## Overview
Adds a new {purpose} template.

## Key Features
- Feature 1
- Feature 2
- Feature 3

## Validation Results
- [ ] Inspector validation passed
- [ ] All tests passed
- [ ] Documentation completed

## Usage Example
\```bash
fastkit startdemo
# Select template: fastapi-{template-name}
\```

## Related Issues
Closes #issue-number
```

### レビュープロセス

1. **自動検証**: GitHub Actions がテンプレートを自動検証します
    - **Template PR Inspection**: テンプレートを変更する PR で `inspect-changed-templates.py` を実行
    - **週次検査**: 毎週水曜日にテンプレート全体を検証
2. **コードレビュー**: メンテナーとコミュニティがコードをレビュー
3. **テスト**: テンプレートをさまざまな環境でテスト
4. **ドキュメントレビュー**: ドキュメントの正確性と完全性を確認
5. **承認とマージ**: すべての要件が満たされたら main ブランチへマージ

!!! note

    検証結果は PR に自動コメントとして届きます。レビュー依頼前に必ず確認してください!

## 🎯 ベストプラクティス

### セキュリティの考慮

- 機密情報は環境変数で管理
- 適切な CORS 設定
- 入力データの検証
- SQL インジェクション対策

### パフォーマンス最適化

- 非同期処理を活用
- データベースクエリの最適化
- 適切なキャッシュ戦略
- レスポンス圧縮の設定

### 保守性

- 明快なコード構造
- 包括的なテストカバレッジ
- 詳細なドキュメント
- ロギングとモニタリングのセットアップ

## 🆘 ヘルプが必要な場合

- 📖 [開発環境セットアップガイド](development-setup.md)
- 📋 [コードガイドライン](code-guidelines.md)
- 💬 [GitHub Discussions](https://github.com/bnbong/FastAPI-fastkit/discussions)
- 📧 [メンテナーへ連絡](mailto:bbbong9@gmail.com)

新しいテンプレートの追加は FastAPI-fastkit コミュニティへの大きな貢献です。
あなたのアイデアと努力が、ほかの開発者にとって大きな助けになります! 🚀
