# テンプレート品質保証

FastAPI-fastkit はテンプレートの品質を高く保ち、さまざまな環境やパッケージマネージャーで確実に動作することを保証するため、包括的な自動検証の仕組みを提供しています。

## 多層的な品質保証

FastAPI-fastkit は **2 つの相補的な品質保証システム** を採用しています:

### 1. 静的テンプレート検査
**テンプレートの構造と構文を毎週自動で検証**

### 2. 動的テンプレートテスト
**実際にプロジェクトを生成して行うエンドツーエンドの包括的テスト**

## 自動週次検査

毎週水曜日の午前 0 時 (UTC) に、GitHub Actions のワークフローがすべての FastAPI テンプレートを自動で検査し、品質基準を満たしているかを確認します:

- ✅ **ファイル構造の検証** — 必要なファイルとディレクトリがすべて存在することを確認
- ✅ **拡張子の検証** — テンプレートファイルが正しい `.py-tpl` 拡張子を使っていることを検証
- ✅ **依存関係チェック** — FastAPI と必要な依存関係が正しく宣言されていることを確認
- ✅ **FastAPI 実装の検証** — テンプレートに適切な FastAPI アプリ初期化が含まれていることを検証
- ✅ **テスト実行** — テンプレートに含まれるテストを実行して機能を確認

## 自動テンプレートテストシステム

FastAPI-fastkit には、すべてのテンプレートを包括的に検証する **革新的な自動テストシステム** が含まれています:

### 動的テンプレート検出

テストシステムは **手動設定なしですべてのテンプレートを自動検出** します:

```console
# すべてのテンプレートを自動でテスト
$ pytest tests/test_templates/test_all_templates.py -v

# 検出されたすべてのテンプレートが結果に表示されます
PASSED tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[fastapi-default]
PASSED tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[fastapi-async-crud]
PASSED tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[fastapi-dockerized]
PASSED tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[fastapi-psql-orm]
```

### 包括的なテストカバレッジ

各テンプレートは **包括的なエンドツーエンドテスト** を受けます:

#### ✅ プロジェクト生成プロセス
- テンプレートのコピーとファイル変換
- プロジェクトメタデータの注入 (名前、作者、説明)
- ファイル構造の検証

#### ✅ パッケージマネージャー互換性
- **UV** (デフォルト): Rust 製の高速パッケージマネージャー
- **PDM**: モダンな Python 依存関係管理
- **Poetry**: 定番の依存関係管理
- **PIP**: 伝統的な Python パッケージマネージャー

#### ✅ 仮想環境の管理
- 各パッケージマネージャーごとの環境作成
- 依存関係インストールの検証
- マネージャー固有のワークフロー

#### ✅ 依存関係の解決
- `pyproject.toml` 生成 (UV、PDM、Poetry)
- `requirements.txt` 生成 (PIP)
- メタデータの準拠 (PEP 621)
- ビルドシステム設定

#### ✅ プロジェクト構造の検証
- FastAPI プロジェクトの識別
- 必須ファイルの存在
- ディレクトリ構造の検証

### テスト実行例

**すべてのテンプレートテストを実行:**
```console
$ pytest tests/test_templates/test_all_templates.py -v
```

**特定のテンプレートをテスト:**
```console
$ pytest tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[fastapi-default] -v
```

**PDM 環境でテスト:**
```console
$ pdm run pytest tests/test_templates/test_all_templates.py -v
```

### 継続的インテグレーション

自動テストシステムは **CI/CD パイプライン** で動作します:

- ✅ **プルリクエスト検証**: 各 PR が影響を受けるテンプレートをテスト
- ✅ **夜間テスト**: テンプレートスイート全体の検証
- ✅ **パッケージマネージャーテスト**: すべてのマネージャーで相互検証
- ✅ **環境テスト**: 複数の Python バージョンとプラットフォームで検証

### コントリビューターへのメリット

**設定不要のテスト:**

- 🚀 新しいテンプレートを追加 → 自動でテスト
- ⚡ テストファイルを手動で作成する必要なし
- 🛡️ 一貫した品質基準

**包括的なカバレッジ:**

- 🔍 エンドツーエンドのプロジェクト生成テスト
- 📦 複数のパッケージマネージャーでの検証
- 🏗️ 依存関係解決の完全テスト
- ✅ 実利用シナリオのシミュレーション

**開発体験:**

- 🎯 **テンプレート内容に集中**: テストは自動
- 🔄 **即時フィードバック**: 高速なテスト実行
- 📊 **明快な結果**: 詳細なテストレポート
- 🚫 **ボイラープレート不要**: テスト設定はゼロ

## 手動でのテンプレート検査

開発やデバッグ用途では、ローカル検査スクリプトまたは Makefile コマンドでテンプレートを手動検査できます:

### 検査スクリプトを直接使う

```console
# すべてのテンプレートを検査
$ python scripts/inspect-templates.py

# 特定のテンプレートを検査
$ python scripts/inspect-templates.py --templates fastapi-default,fastapi-async-crud

# 詳細情報付きで検査
$ python scripts/inspect-templates.py --verbose

# 結果を任意のファイルに保存
$ python scripts/inspect-templates.py --output my_results.json
```

### Makefile コマンドを使う

```console
# すべてのテンプレートを検査
$ make inspect-templates

# 詳細出力付きで検査
$ make inspect-templates-verbose

# 特定のテンプレートを検査
$ make inspect-template TEMPLATES="fastapi-default,fastapi-async-crud"
```

## 検査結果

- **検査が成功した場合** はワークフローの出力およびアーティファクトに記録されます
- **検査が失敗した場合** は GitHub Issue が自動で作成され、詳細なエラーレポートが添付されます
- **検査履歴** は GitHub Actions のアーティファクトとして 30 日間保存されます

## 検査出力の読み方

テンプレート検査を実行すると、次のような出力が得られます:

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

## テンプレート要件

テンプレートが検査を通過するには、次の要件を満たす必要があります:

### ファイル構造
- Python ソースファイルを含む `src/` ディレクトリが存在すること
- Python ファイルは `.py-tpl` 拡張子を使用すること
- `tests/` ディレクトリと `README.md-tpl` ファイルを含むこと
- 次のメタデータファイルのうち **少なくとも 1 つ** を含むこと:
    - `pyproject.toml-tpl` (推奨、PEP 621)、または
    - `setup.py-tpl` (レガシー、引き続き受け付け)
- `requirements.txt-tpl` は、`pyproject.toml-tpl` が `[project].dependencies` を宣言している場合は任意です

### FastAPI 要件
- FastAPI アプリの初期化を含むこと
- 次のいずれかに `fastapi` が依存関係として宣言されていること: `pyproject.toml-tpl` の `[project].dependencies`、`requirements.txt-tpl`、または `setup.py-tpl` の `install_requires`
- すべてのテンプレートファイルが妥当な Python 構文であること

### 識別マーカー
テンプレートは FastAPI-fastkit の識別マーカーを保持すべきです。これにより、生成されたプロジェクトが、ユーザーのワークスペース内の無関係な FastAPI プロジェクトと区別できるようになります:

- `pyproject.toml-tpl` — `description` の `[FastAPI-fastkit templated]` 接頭辞と、`managed = true` を持つ `[tool.fastapi-fastkit]` テーブルの両方。
- `setup.py-tpl` — `setup()` の `description` 引数に `[FastAPI-fastkit templated]` 接頭辞。

`is_fastkit_project()` はこれらのいずれかがあれば判定対象として扱います (pyproject が優先され、setup.py はレガシーフォールバック。マッチングは大文字小文字を区別しません)。メタデータ注入により、テンプレートがマーカーを入れ忘れていても、生成されたプロジェクトには確実に含まれます。

### 品質基準
- すべてのテンプレートファイルが構文的に正しいこと
- 依存関係が正しく指定されていること
- テンプレート構造が FastAPI-fastkit の規約に従っていること

この自動品質保証により、すべてのテンプレートは信頼性が高く、本番運用に耐える状態で維持されます。
