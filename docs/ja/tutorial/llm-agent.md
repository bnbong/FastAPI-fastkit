# `fastapi-llm-agent` によるストリーミング LLM エージェント

生成されたトークンをそのままストリーミングし、実際に *行動* できる — ツールを呼び出し、その結果を読み、
処理を続けられる — チャットバックエンドを構築します。このチュートリアルでは `fastapi-llm-agent`
テンプレートを取り上げます。SSE イベントプロトコル、ツール呼び出しループとその反復上限、インターフェースの
背後にある会話メモリ、そしてネットワークに一切触れないテストスイートを順に確認します。

## 学べること

- `fastkit startdemo fastapi-llm-agent` でプロジェクトを生成する
- クライアントが処理すべき SSE イベントの種類と、それぞれの意味
- ツール呼び出しループの 1 ターンがどのように動くか (ステップごとに)
- 独自のツールを追加する
- プロセス内の会話ストアを本物のストアに差し替える
- テストが決定的で、無料で実行できる理由

## 前提条件

- Python 3.12 以上
- FastAPI-fastkit がインストール済み (`pip install fastapi-fastkit`)
- Anthropic API キー — 本物のモデルと対話する場合にのみ必要です。生成されるテストスイートはキーなしで実行できます。
- `async`/`await` と非同期ジェネレーターに慣れていること

## ステップ 1: 生成と設定

```console
$ fastkit startdemo fastapi-llm-agent
Enter the project name: support-agent
Enter the author name: Developer Kim
Enter the author email: developer@example.com
Enter the project description: Streaming support assistant
Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y
```

最初に実行する前に、キーを `.env` に設定します:

```bash
ANTHROPIC_API_KEY=sk-ant-...
LLM_MODEL=claude-sonnet-5
LLM_MAX_TOKENS=4096
MAX_TOOL_ITERATIONS=5
```

キーは pydantic-settings によって読み込まれ、構築時にクライアントへ渡されます。ソースコードに書き込まれる
ことも、Docker イメージに焼き込まれることもありません。

```console
$ cd support-agent
$ bash scripts/run-server.sh
$ bash scripts/chat.sh "What is 12 * 34?"
```

!!! tip "Anthropic API の代わりにゲートウェイを使う"
    `LLM_BASE_URL` (ゲートウェイが bearer 認証を使う場合は `LLM_AUTH_TOKEN` も) を設定すると、LiteLLM、
    社内プロキシ、ローカルサーバーを向けられます。通信形式は Anthropic Messages API のままです。
    他のプロバイダー向けの変換はアプリではなくゲートウェイの役割です。

## ステップ 2: 生成されるツリー

```
support-agent/
├── pyproject.toml              # PEP 621 メタデータ + [tool.fastapi-fastkit]
├── requirements.txt
├── Dockerfile
├── .env
├── scripts/
│   ├── chat.sh                 # 起動中のサーバーにメッセージを 1 件送信
│   ├── format.sh  lint.sh  run-server.sh  test.sh
├── src/
│   └── app/
│       ├── main.py             # FastAPI アプリ + lifespan
│       ├── core/config.py      # pydantic-settings (API キーはここ)
│       ├── llm/
│       │   ├── client.py       # AsyncAnthropic ファクトリ
│       │   ├── tools.py        # ツールスキーマ + ハンドラ
│       │   └── agent.py        # ストリーミングエージェント + ツールループ
│       ├── memory/
│       │   ├── base.py         # ConversationStore インターフェース
│       │   └── in_memory.py    # プロセスローカルの実装
│       ├── schemas/chat.py     # リクエストボディ + SSE イベントエンベロープ
│       └── api/
│           ├── router.py       # health + chat を集約
│           ├── deps.py         # store / agent の依存性
│           ├── health.py       # GET /health
│           └── chat.py         # POST /chat (SSE)、会話履歴
└── tests/
    ├── conftest.py             # スクリプト化された偽の Anthropic クライアント
    ├── test_health.py  test_chat.py  test_tools.py  test_memory.py
```

最初に注目しておきたい境界が 3 つあります: **クライアント** はファクトリで作成される (そのためテストで
差し替えられる)、**メモリ** は単純な実装を持つインターフェースである (そのため本番環境で差し替えられる)、
そして **ツール** はスキーマのリストとハンドラの dict で構成される (そのため 1 つ追加しても触るファイルは
1 つだけ) という点です。

## ステップ 3: エンドポイント

| メソッド | エンドポイント                 | 説明                     |
|--------|------------------------------|-------------------------|
| GET    | `/api/v1/health`             | Liveness プローブ        |
| POST   | `/api/v1/chat`               | 返答を SSE でストリーミング |
| GET    | `/api/v1/conversations/{id}` | 保存された履歴を読む      |
| DELETE | `/api/v1/conversations/{id}` | 会話を破棄する            |

`POST /api/v1/chat` は `{"message": "...", "conversation_id": "..."}` を受け取ります。
新しい会話を始めるときは `conversation_id` を省略し、割り当てられた id を最後の `done` イベントから
読み取ります。

## ステップ 4: ストリームプロトコル

各 SSE メッセージは、`event:` フィールドに種類を、`data:` に JSON エンベロープを持ちます。
クライアントは 5 種類のイベントとエラーを処理する必要があります:

| イベント        | フィールド                        | 意味                           |
|---------------|---------------------------------|--------------------------------|
| `token`       | `text`                          | アシスタントの返答の一部         |
| `tool_use`    | `tool_name`, `tool_input`       | Claude がツールを要求した        |
| `tool_result` | `tool_name`, `tool_output`      | ツールが実行された               |
| `usage`       | `input_tokens`, `output_tokens` | ターンごとのトークン消費量       |
| `done`        | `conversation_id`               | ターンが完了した                 |
| `error`       | `detail`                        | ストリームの途中で何かが失敗した |

`tool_use` と `tool_result` は飾りではありません — ツールの実行中に、説明のない待ち時間ではなく
「検索中…」と UI に表示できるのはこれらのおかげです。

トークン使用量はターンごとに `app.agent` ロガーにも書き込まれるため、クライアントに計測を組み込まなくても
サーバーログで消費量を確認できます。

## ステップ 5: ループの 1 ターン

`src/app/llm/agent.py` の `ChatAgent.stream` がエンジンのすべてです。1 ターンは次のように進みます:

1. ストアから会話履歴を読み込みます。
2. 履歴、新しいユーザーメッセージ、ツールスキーマを使ってストリーミングリクエストを開始します。
3. テキストのチャンクが届くたびに、`token` イベントとして yield します。
4. ストリームが終わったら最終メッセージを読み、`usage` イベントを送出してトークン数をログに記録します。
5. **`stop_reason != "tool_use"` の場合、** アシスタントの処理は完了です: ターンを永続化し、`done` を
   送出して return します。
6. **そうでない場合、** 各 `tool_use` ブロックについて: `tool_use` を送出し、ハンドラを実行し、
   `tool_result` を送出して、出力を集めます。
7. すべてのツール結果を 1 つの `user` メッセージとして送り返し — これは Messages API が要求する形です —
   ステップ 2 からループします。

ループは `MAX_TOOL_ITERATIONS` (デフォルトは 5) で上限が設けられています。上限を超えても Claude が
ツールを要求し続ける場合、サーバーが空回りし続けるのではなく、ターンが永続化され、警告がログに記録され、
`error` イベントが送出されます:

```python
yield AgentEvent(
    type="error",
    detail=(
        "The assistant exceeded the tool-call limit of "
        f"{self._max_tool_iterations} iterations."
    ),
)
```

エージェントループにおいて、このような上限は任意ではありません。上限がなければ、ツールの結果を誤解した
モデルが際限なく課金し続ける可能性があります。

## ステップ 6: 付属のツール

| ツール          | 目的                                                     |
|----------------|----------------------------------------------------------|
| `calculator`   | 算術計算。AST に解析してホワイトリストで制限 — `eval` は使わない |
| `current_time` | IANA タイムゾーンでの現在時刻                              |

`calculator` はもう一度よく見ておく価値があります。式を `ast` で解析し、ホワイトリストに含まれるノード型
だけを辿るため、モデルから渡されたツール引数が任意の Python を実行することはできません。モデルが生成した
入力を受け付けるツールには、すべて同じ規律が必要です: **モデルの出力は信頼できない入力です。**

### ツールを追加する

すべては `src/app/llm/tools.py` にあります:

1. `TOOL_SCHEMAS` にスキーマを追加します — `name`、`description`、JSON Schema の `input_schema`。
2. 同じ名前で `TOOL_HANDLERS` にハンドラを登録します。

正しく押さえておくべき点が 2 つあります:

- **説明文は、そのツールをいつ使うべきかについて Claude が受け取る指示のすべてです。** これはドキュメント
  ではなくプロンプトエンジニアリングです — 曖昧な説明文からは、一度も呼ばれないツールか、絶えず呼ばれる
  ツールが生まれます。
- **ハンドラは文字列を返し、自身の失敗は例外を送出するのではなく読みやすいメッセージに変換するべきです。**
  ループはそのテキストをそのままモデルに返すため、「X という名前の都市は見つかりませんでした」であれば
  モデルは立て直せますが、例外はターンを終わらせてしまいます。

## ステップ 7: 会話メモリ

`ConversationStore` (`src/app/memory/base.py`) がインターフェースで、付属の `in_memory.py` は dict で
それを実装しています。単一プロセスならこれで十分ですが、それ以外の用途には向きません — 再起動するとすべて
忘れてしまい、2 つのワーカー間で履歴が食い違います。

本格的にするには: 同じインターフェースを Redis やデータベースに対して実装し、`src/app/api/deps.py` の
`get_store()` からそれを返します。エージェントも router も具象クラスの名前を一切参照していないため、
どちらも変更する必要はありません。

## ステップ 8: テスト

```console
$ bash scripts/test.sh    # または: pytest
```

`tests/conftest.py` は、`AsyncAnthropic.messages.stream` を模倣する偽物を通じてスクリプト化された
ターンを再生します。そのためテストスイートは決定的で、オフラインで実行でき、費用もかかりません。それでいて、
重要なパス — ストリーミングのパスと、ツールが呼び出されてからモデルが答えるターンを含むツールループ全体 —
をカバーします。

エージェントを拡張するときも、このパターンを守りましょう。LLM 連携を本物のモデルに対してテストすると、
遅く、不安定で、高価なうえに、モデルが何を言うかをアサートすることもできないテストスイートになります。
スクリプト化されたクライアントに対して *ループ* をテストすれば、自分が書いたものをそのままアサートできます。

## ステップ 9: 拡張ポイント

- **永続的な履歴** — `ConversationStore` を Redis やデータベースに対して実装します (ステップ 7)。
- **RAG** — 検索 (retrieval) はテンプレートの対象外として意図的に外しています。自然な接合点は
  `ChatAgent.stream` です: 最初のリクエストの前にコンテキストを取得してシステムプロンプトの先頭に付け加えるか、
  インデックスをもう 1 つのツールとして公開し、いつ検索するかをモデルに判断させます。
- **認証とレート制限** — 出荷時の `POST /chat` は認証なしです。公開する前に router に依存性を
  付けてください。再利用できるガードは [JWT 認証チュートリアル](auth-jwt.md) にあります。

## まとめ

- **生成**: `fastkit startdemo fastapi-llm-agent`、`ANTHROPIC_API_KEY` を設定、
  `bash scripts/run-server.sh`。
- **ストリーミング**: `token` / `tool_use` / `tool_result` / `usage` / `done` / `error` イベントを
  使う SSE。
- **ループ**: ストリーム → ツール呼び出し → 結果を 1 つの user メッセージとして返す → 繰り返し。
  `MAX_TOOL_ITERATIONS` で上限を設定。
- **ツール**: `TOOL_SCHEMAS` のスキーマと `TOOL_HANDLERS` のハンドラ。ツールの入力は信頼できないものとして扱う。
- **メモリ**: `ConversationStore` インターフェースと dict による実装。`get_store()` で差し替え。
- **テスト**: スクリプト化された偽のクライアントにより、テストスイートはオフラインかつ決定的。

## 次に学ぶこと

- [MCP との統合](mcp-integration.md) — チャットエージェントではなく MCP サーバーが必要な場合。
- [JWT 認証](auth-jwt.md) — チャットエンドポイントの前にアカウントを置く方法。
- [どのスターターを選ぶべき?](../user-guide/choosing-a-starter.md)
