# どのスターターを選ぶべき?

FastAPI-fastkit には、プロジェクトを始めるための方法がいくつか用意されています。このページは初めての方のための **選び方ガイド** です。ここで方向性を決めたうえで、実際のプロジェクト生成は [クイックスタート](quick-start.md) に進んでください。

迷っている場合の答えは次のとおりです:

> **`fastkit init --interactive` で始め、`domain-starter` プリセットを選んでください。** これは現代的な API プロジェクトに対する推奨デフォルトです。

このページの残りの部分では、その理由と、別の選択を取るべき場面を説明します。

## TL;DR — ユーザータイプ別の選び方

| あなたが... | 出発点 |
|---|---|
| FastAPI が初めてで、ガイド付きで進めたい | `fastkit init --interactive` (preset: **`domain-starter`**) |
| 動作する CRUD デモを読み・書き換えながら学びたい | `fastkit startdemo fastapi-default` |
| 可能な限り小さいスキャフォールドが欲しい | `fastkit init --interactive` (preset: **`minimal`**) |
| 簡単なプロトタイプ / 単一ファイルのスクリプトを書く | `fastkit init --interactive` (preset: **`single-module`**) |
| 実際のデータベースが必要 (PostgreSQL + SQLAlchemy + Alembic) | `fastkit startdemo fastapi-psql-orm` |
| 中規模 API のための本番志向のドメインレイアウトが欲しい | `fastkit init --interactive` (preset: **`domain-starter`**) |

## `startdemo` と `init --interactive` の違いは?

これらが 2 つの主なエントリポイントで、それぞれ異なる用途を持ちます。

### `fastkit startdemo <template>`

同梱テンプレート (`fastapi-default`、`fastapi-async-crud`、`fastapi-psql-orm`、`fastapi-domain-starter`、...) のいずれかをもとに、**完成済みで動作する例題プロジェクト** をディスクに展開します。テンプレートのソースコードはほぼそのままコピーされ、メタデータのプレースホルダ (`<project_name>` など) のみが埋め込まれます。

- ✅ 動作するデモまでの最短ルート。
- ✅ コードはすべて実際に動き、読みやすい — 例題による学習に最適。
- ❌ テンプレートのスタックと構造は固定されており、生成時に「CORS だけ入れて認証は外す」といった組み合わせはできません。

```console
$ fastkit list-templates              # 利用可能なテンプレート一覧を表示
$ fastkit startdemo fastapi-default   # その中の 1 つでプロジェクトを生成
```

### `fastkit init --interactive`

**対話型ウィザード** に沿って進めます: プロジェクトメタデータ → アーキテクチャプリセット → 機能選択 (データベース、認証、テスト、デプロイ、...) → パッケージマネージャー → 確認、という流れです。ジェネレーターはプリセットごとに適切なベーステンプレートを選び、その上に選択した機能を重ねていきます。

- ✅ 自分が本当に欲しいスタックを組み立てられる。
- ✅ アーキテクチャプリセットがプロジェクトレイアウト (単一ファイル、レイヤー型、ドメイン指向、...) を決定。
- ❌ `main.py` をそのまま使う構成の充実したプリセット (`classic-layered`、`domain-starter`) では、設定モジュールは生成されますが、それを同梱のルーターに組み込む配線はユーザー自身が行う前提です。プリセット / 機能ごとの仕様は [アーキテクチャプリセットマトリクス](../reference/preset-feature-matrix.md) を参照してください。

```console
$ fastkit init --interactive
```

## 4 種類のアーキテクチャプリセット

これらは `fastkit init --interactive` のプロジェクト情報入力後に表示されます。どのプリセットを選ぶか決める際にこのセクションを使ってください。

### `minimal` — 最小から始め、後で育てる

最小構成の動作可能な FastAPI アプリ。空のスキャフォールド + 機能フラグから再生成された単一の `src/main.py` です。CORS、レート制限、Prometheus 計装は、選択時に自動で `main.py` に配線されます。

- 👤 **対象**: プロジェクトが成長するにつれて自分で構造を組み立てたい人や、特定のレイアウトに縛られず FastAPI を試したい人。
- 📦 **ベーステンプレート**: `fastapi-empty`。
- 🧠 **メンタルモデル**: 「FastAPI を import した 1 ファイルだけ用意してくれれば、残りは自分でやる」。

### `single-module` — スクリプト型プロトタイプ

すべてのコードが 1 モジュールの中にあります。`minimal` と同じ `main.py` 再生成オーバーレイを使います。

- 👤 **対象**: グルースクリプト、小さな webhook、あるいはパッケージ境界が不要な 1 日でできるプロトタイプ。
- 📦 **ベーステンプレート**: `fastapi-single-module`。
- 🧠 **メンタルモデル**: 「実行も通読もひと息でできる Python ファイル 1 つあれば十分」。

### `classic-layered` — レイヤー型分割 (api / crud / schemas / core)

「Django 風」レイアウト — コードを関心事ごとに水平分割します: ルーターはすべて `api/` に、CRUD ロジックはすべて `crud/` に、pydantic スキーマはすべて `schemas/` に、設定はすべて `core/` にまとめます。同梱の `main.py` は **保存** されており (CORS の配線済み)、生成されたデータベース / 認証設定は `src/core/` 配下に配置されます。

- 👤 **対象**: Django / Rails 風レイアウトに慣れたチーム、共通の CRUD 配管を共有する小さなエンドポイントが多いプロジェクト。
- 📦 **ベーステンプレート**: `fastapi-default`。
- 🧠 **メンタルモデル**: 「コードを *何であるか* で分ける」。

### `domain-starter` — ドメイン指向 (推奨デフォルト)

コードを **ビジネス概念ごと** に垂直分割します: 各ドメインが自身のルーター、サービス、リポジトリ、スキーマを `src/app/domains/<concept>/` 配下に持ちます。`/health` エンドポイントと、新しい概念ごとにコピーしてリネームする雛形となる `items` ドメインの例が同梱されています。同梱の `main.py` (`src/app/` 配下) は保存され、生成された設定は `src/app/core/` 配下に配置されます。

- 👤 **対象**: 複数の異なるビジネス概念 (users、orders、billing、...) に成長していく中規模 API。推奨される現代的なデフォルトです。
- 📦 **ベーステンプレート**: `fastapi-domain-starter`。
- 🧠 **メンタルモデル**: 「コードを *ビジネスにとって何をするか* で分ける」。

## 比較マトリクス

横並びで一目で比べられるようにしたものです。

| | `minimal` | `single-module` | `classic-layered` | `domain-starter` |
|---|---|---|---|---|
| ベーステンプレート | `fastapi-empty` | `fastapi-single-module` | `fastapi-default` | `fastapi-domain-starter` |
| プロジェクト入口 | `src/main.py` | `src/main.py` | `src/main.py` | `src/app/main.py` |
| ルーター配置 | (自分で追加) | (`main.py` の中) | `src/api/routes/` | `src/app/domains/<concept>/router.py` |
| ドメイン別フォルダ | ❌ | ❌ | ❌ | ✅ |
| `/health` エンドポイント標準搭載 | ✅ | ✅ | ❌ | ✅ |
| `main.py` を機能から再生成 | ✅ | ✅ | ❌ | ❌ |
| `main.py` に CORS 事前配線 | 選択時に追加 | 選択時に追加 | あり (環境変数駆動) | あり (環境変数駆動) |
| pyproject ファースト | 任意 | 任意 | 任意 | ✅ |
| 適した用途 | 「自分で構造を育てたい」 | 「1 ファイルのプロトタイプ」 | 「関心事で分ける」 | 「ビジネス概念で分ける」 |

機能ごとの完全な契約 (データベース / 認証の設定が配置されるパス、自動配線されない選択、警告が出る条件) は [アーキテクチャプリセットマトリクス](../reference/preset-feature-matrix.md) を参照してください。

## `startdemo` テンプレートの選び方

`fastkit startdemo <template>` は、ガイド付きで組み立てるよりも **完成済みで実行可能な例題** が欲しいときに最適です。ほとんどのテンプレートは前述の 4 つのプリセットのいずれかにおおむね対応していますが、追加のサンプルコード (モックストア上の CRUD エンドポイント、カスタムレスポンス処理、Docker ツールなど) を同梱しています。

| テンプレート | 最も近いプリセット | 選ぶ場面 |
|---|---|---|
| `fastapi-default` | `classic-layered` | レイヤー型レイアウトで動く CRUD デモ。最初の出発点として手堅い。 |
| `fastapi-empty` | `minimal` | 素のスキャフォールド。`minimal` と同じ形になります。 |
| `fastapi-single-module` | `single-module` | 単一ファイルのデモ。 |
| `fastapi-domain-starter` | `domain-starter` | 推奨される現代的デフォルト。items ドメインの例を同梱。 |
| `fastapi-async-crud` | `classic-layered` | `fastapi-default` の非同期版。 |
| `fastapi-custom-response` | `classic-layered` | カスタムレスポンスエンベロープ / フォーマットのデモ。 |
| `fastapi-dockerized` | `classic-layered` | デフォルトレイアウトに本番用の Dockerfile を追加。 |
| `fastapi-psql-orm` | (直接対応するプリセットなし) | PostgreSQL + SQLAlchemy + Alembic。実際のデータベースが必要なときに選択。 |
| `fastapi-mcp` | (直接対応するプリセットなし) | Model Context Protocol 連携。 |

`fastkit list-templates` で 1 行説明付きの最新リストを確認できます。

## よくある質問

**Q. プリセット / テンプレートは最初に決めないといけない?**
いいえ — 後から手動で生成済みコードを再構成することはいつでもできます。プリセットはあくまで出発点であり契約ではありません。選択を考え過ぎないでください。

**Q. 「現代的」な選択肢はどれ?**
`domain-starter` です。pyproject ファーストで、`/health` エンドポイントが付属し、よく運営されている中規模 FastAPI プロジェクトが収束していくレイアウトを採用しています。

**Q. 後から `classic-layered` から `domain-starter` に切り替えできる?**
できますが手動のリファクタリングです — マイグレーションコマンドはありません。プロジェクトがドメインフォルダを必要とするほど成長すると思うなら、最初からそこを選んでください。

**Q. とにかく FastAPI を学びたいだけ。**
まず `fastkit startdemo fastapi-default` から始めてください — コードを読み、テストを実行し、いくつかのエンドポイントを書き換えてみましょう。慣れてきたら、`fastkit init --interactive` で `domain-starter` プリセットを選ぶのが自然な次の一歩です。

**Q. 各プリセットが生成する正確なファイル一覧はどこで見られる?**
[アーキテクチャプリセットマトリクス](../reference/preset-feature-matrix.md) がそのリファレンスページです。

## 次のステップ

- [クイックスタート](quick-start.md) — 実際に最初のプロジェクトを作成。
- [プロジェクトの作成](creating-projects.md) — CLI フラグのより踏み込んだウォークスルー。
- [ドメイン指向プロジェクトのチュートリアル](../tutorial/domain-starter.md) — `domain-starter` を選んだ場合の、生成ツリー、同梱の `items` 例、次のドメインの追加方法までを通したエンドツーエンドの解説。
- [アーキテクチャプリセットマトリクス](../reference/preset-feature-matrix.md) — プリセット / 機能ごとの完全な契約。
