# クイックスタート

FastAPI-fastkit で 5 分以内に最初の FastAPI プロジェクトを作成しましょう!

!!! tip "どのスターターを選べばよいか分からないとき"
    `startdemo` テンプレートと対話型のアーキテクチャプリセット (`minimal` / `single-module` / `classic-layered` / `domain-starter`) を初心者向けに比較した [**どのスターターを選ぶべき?**](choosing-a-starter.md) を参照してください。短く言えば、**`fastkit init --interactive` の `domain-starter` プリセットが現在の推奨デフォルト** です。

## 1. プロジェクトの作成

FastAPI-fastkit の `init` コマンドで新しいプロジェクトを作成します:

<div class="termy">

```console
$ fastkit init
Enter the project name: my-first-app
Enter the author name: Your Name
Enter the author email: your.email@example.com
Enter the project description: My first FastAPI application

           Project Information
┌──────────────┬─────────────────────────────┐
│ Project Name │ my-first-app                │
│ Author       │ Your Name                   │
│ Author Email │ your.email@example.com      │
│ Description  │ My first FastAPI application│
└──────────────┴─────────────────────────────┘

Available Stacks and Dependencies:
           MINIMAL Stack
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ pydantic          │
│ Dependency 4 │ pydantic-settings │
└──────────────┴───────────────────┘

           STANDARD Stack
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ sqlalchemy        │
│ Dependency 4 │ alembic           │
│ Dependency 5 │ pytest            │
│ Dependency 6 │ pydantic          │
│ Dependency 7 │ pydantic-settings │
└──────────────┴───────────────────┘

             FULL Stack
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ sqlalchemy        │
│ Dependency 4 │ alembic           │
│ Dependency 5 │ pytest            │
│ Dependency 6 │ redis             │
│ Dependency 7 │ celery            │
│ Dependency 8 │ pydantic          │
│ Dependency 9 │ pydantic-settings │
└──────────────┴───────────────────┘

Select stack (minimal, standard, full): minimal

Available Package Managers:
                   Package Managers
┌────────┬────────────────────────────────────────────┐
│ PIP    │ Standard Python package manager            │
│ UV     │ Fast Python package manager                │
│ PDM    │ Modern Python dependency management        │
│ POETRY │ Python dependency management and packaging │
└────────┴────────────────────────────────────────────┘

Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y

✨ FastAPI project 'my-first-app' has been created successfully!
```

</div>

## 2. 仮想環境の有効化

プロジェクトディレクトリへ移動し、仮想環境を有効化します:

<div class="termy">

```console
$ cd my-first-app
$ source .venv/bin/activate  # Linux/macOS
$ .venv\Scripts\activate     # Windows
```

</div>

## 3. 開発サーバーの起動

FastAPI 開発サーバーを起動します:

<div class="termy">

```console
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [28720]
INFO:     Started server process [28722]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

</div>

!!! success "おめでとうございます!"
    FastAPI サーバーが起動中です! ブラウザで確認してみましょう。

## 4. API のテスト

ブラウザで次の URL を開いてみましょう:

### メインエンドポイント

[http://127.0.0.1:8000](http://127.0.0.1:8000) にアクセスすると、次のように表示されます:

```json
{"message": "Hello World"}
```

### 対話型 API ドキュメント

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) を開いてください。

これは自動生成される **Swagger UI** ドキュメントで、以下のことが可能です:

- すべての API エンドポイントを表示
- ブラウザから直接エンドポイントをテスト
- リクエスト / レスポンススキーマを確認

### 代替ドキュメント

[http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) を開いてください。

別のすっきりしたデザインの **ReDoc** ドキュメント画面です。

## 5. 最初のルートの追加

プロジェクトに新しい API ルートを追加してみましょう:

<div class="termy">

```console
$ fastkit addroute users my-first-app
                       Adding New Route
┌──────────────────┬──────────────────────────────────────────┐
│ Project          │ my-first-app                             │
│ Route Name       │ users                                    │
│ Target Directory │ ~/my-first-app                           │
└──────────────────┴──────────────────────────────────────────┘

Do you want to add route 'users' to project 'my-first-app'? [Y/n]: y

╭──────────────────────── Info ────────────────────────╮
│ ℹ Updated main.py to include the API router          │
╰──────────────────────────────────────────────────────╯
╭─────────────────────── Success ───────────────────────╮
│ ✨ Successfully added new route 'users' to project    │
│ `my-first-app`                                        │
╰───────────────────────────────────────────────────────╯
```

</div>

サーバーは自動的に再読み込みされ、新しいエンドポイントが利用可能になります:

- `GET /api/v1/users/` - すべてのユーザーを取得
- `POST /api/v1/users/` - 新しいユーザーを作成
- `GET /api/v1/users/{user_id}` - 特定のユーザーを取得
- `PUT /api/v1/users/{user_id}` - ユーザーを更新
- `DELETE /api/v1/users/{user_id}` - ユーザーを削除

## 6. 新しい API のテスト

### curl を使う

**すべてのユーザーを取得:**

<div class="termy">

```console
$ curl http://127.0.0.1:8000/api/v1/users/
[]
```

</div>

**新しいユーザーを作成:**

<div class="termy">

```console
$ curl -X POST "http://127.0.0.1:8000/api/v1/users/" \
     -H "Content-Type: application/json" \
     -d '{"title": "John Doe", "description": "Software Developer"}'
{
  "id": 1,
  "title": "John Doe",
  "description": "Software Developer"
}
```

</div>

### 対話型ドキュメントを使う

1. [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) にアクセスします。
2. **"users"** セクションを展開します。
3. **"POST /api/v1/users/"** をクリックします。
4. **"Try it out"** をクリックします。
5. リクエストボディを入力します:
   ```json
   {
     "title": "Jane Smith",
     "description": "Product Manager"
   }
   ```
6. **"Execute"** をクリックします。

## 7. プロジェクト構造の確認

生成されたプロジェクトは整理された構造を持ちます:

```
my-first-app/
├── .venv/                    # 仮想環境
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI アプリのエントリポイント
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py        # アプリ設定
│   ├── api/
│   │   ├── __init__.py
│   │   ├── api.py          # API ルーターをまとめる
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── items.py     # デフォルトの items ルート
│   │       └── users.py     # 新しく追加した users ルート
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── items.py         # items 用の CRUD 操作
│   │   └── users.py         # users 用の CRUD 操作
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── items.py         # items 用 Pydantic スキーマ
│   │   └── users.py         # users 用 Pydantic スキーマ
│   └── mocks/
│       ├── __init__.py
│       └── mock_items.json  # テストデータ
├── tests/                   # テストファイル
├── scripts/                 # ユーティリティスクリプト
├── requirements.txt         # Python 依存関係
├── setup.py                # パッケージ設定
└── README.md               # プロジェクトドキュメント
```

## 8. パッケージマネージャーの選択肢

FastAPI-fastkit は好みに合わせて複数の Python パッケージマネージャーをサポートしています:

### 利用可能なパッケージマネージャー

| マネージャー | 説明 | 適している場面 |
|---|---|---|
| **UV** | 高速な Python パッケージマネージャー (デフォルト) | 速度とパフォーマンス |
| **PDM** | モダンな Python 依存関係管理 | 高度な依存関係解決 |
| **Poetry** | Python 依存関係管理とパッケージング | Poetry 中心のワークフロー |
| **PIP** | 標準の Python パッケージマネージャー | 伝統的な Python 開発 |

### パッケージマネージャーの指定方法

好みのパッケージマネージャーは次の方法で指定できます:

#### 1. 対話型選択 (デフォルト)

`fastkit init` または `fastkit startdemo` を実行すると、選択プロンプトが表示されます:

<div class="termy">

```console
$ fastkit init
# ... プロジェクト情報とスタックを選択した後 ...

Available Package Managers:
                   Package Managers
┌────────┬────────────────────────────────────────────┐
│ PIP    │ Standard Python package manager            │
│ UV     │ Fast Python package manager                │
│ PDM    │ Modern Python dependency management        │
│ POETRY │ Python dependency management and packaging │
└────────┴────────────────────────────────────────────┘

Select package manager (pip, uv, pdm, poetry) [uv]: uv
```

</div>

#### 2. コマンドラインオプション

対話型プロンプトを飛ばし、パッケージマネージャーを直接指定できます:

<div class="termy">

```console
$ fastkit init --package-manager poetry
$ fastkit startdemo --package-manager pdm
```

</div>

### 生成される依存関係ファイル

各パッケージマネージャーはそれぞれ適切な依存関係ファイルを生成します:

- **UV/PDM**: `pyproject.toml` (PEP 621 形式)
- **Poetry**: `pyproject.toml` (Poetry 形式)
- **PIP**: `requirements.txt`

## 9. 次のステップ

おめでとうございます! 以下をすべて達成しました:

✅ 最初の FastAPI プロジェクトを作成
✅ 開発サーバーを起動
✅ 新しい API ルートを追加
✅ API をテスト

### 学習を続ける

1. **[最初のプロジェクトを作る](../tutorial/first-project.md)**: より複雑なブログ API を構築
2. **[プロジェクトの作成](creating-projects.md)**: 様々なスタックとオプションを学ぶ
3. **[ルートの追加](adding-routes.md)**: API 開発のスキルを身につける
4. **[テンプレートの利用](using-templates.md)**: あらかじめ用意されたプロジェクトテンプレートを試す

### さらに試してみる

次のコマンドで、より多くの機能を探索できます:

<div class="termy">

```console
# 利用可能なテンプレート一覧
$ fastkit list-templates

# テンプレートからプロジェクトを生成
$ fastkit startdemo

# ルートをさらに追加 (ルート名が先、プロジェクトディレクトリが後)
$ fastkit addroute products my-first-app
$ fastkit addroute orders my-first-app
```

</div>

!!! tip "開発のヒント"
    - ファイルを変更するとサーバーが自動的に再読み込みされます
    - 新機能を追加するたびに `/docs` で対話型ドキュメントを確認しましょう
    - 依存関係の分離のために仮想環境を活用しましょう
    - 生成されたコードを読んでプロジェクト構造を理解しましょう
