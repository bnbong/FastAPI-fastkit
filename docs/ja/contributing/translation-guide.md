# 翻訳ガイド

このガイドでは、FastAPI-fastkit ドキュメントの翻訳に貢献する方法を説明します。

## 原典と翻訳ポリシー

> **英語 (`en`) が FastAPI-fastkit ドキュメントの基準となる原文** です。それ以外のロケールは翻訳対象であり、リリース単位またはページ単位で英語より遅れる可能性があります。
>
> 翻訳されたページが英語ページと食い違う場合は、翻訳が追いつくまで **英語ページを信頼してください**。翻訳は貢献者が到達した範囲でそのまま提供されます — 部分的なカバレッジは通常の状態です。

このポリシーに対応するユーザー向けページは [翻訳ステータス](../reference/translation-status.md) で、各ロケールの実際の完成度と、未翻訳ページが MkDocs でどう表示されるかが書かれています (要約: 英語にフォールバックします)。

リポジトリルートの `CHANGELOG.md` も、正式なリリース履歴として英語のまま維持されます。ロケールが `changelog.md` を持つ場合、そのページは別途翻訳された changelog を維持するのではなく、正式な英語 changelog にリンクするか取り込む形にしてください (今後プロジェクト方針が変わった場合を除く)。

翻訳を貢献するときは、ステータスページの表も合わせて更新してください。これにより、利用者が言語切替メニューだけでは判断できない実際の利用可否を把握できます。

## 概要

FastAPI-fastkit は、AI を活用してドキュメントを複数言語へ翻訳する自動化システムを使用しています。このシステムは:

- 英語のソースドキュメントを読み込みます
- AI API (OpenAI または Anthropic) を使ってコンテンツを翻訳します
- 翻訳結果を言語別ディレクトリへ保存します
- レビュー用の GitHub Pull Request を作成します

自動化はあくまでたたき台を作るだけであり、マージ前には人によるレビューが必要です。AI が生成した翻訳は PR の "draft" として明示し、その言語に十分慣れたレビュアーが確認してから反映してください。

## 対応言語

下記はドキュメントサイトが現在 **ビルド** しているロケールです。ビルド対象として設定されているだけでは、そのロケールのページが翻訳済みであるとは **限りません** — ロケールごとの実際の完成度は [翻訳ステータス](../reference/translation-status.md) を参照してください。

- 🇰🇷 韓国語 (ko)
- 🇯🇵 日本語 (ja)
- 🇨🇳 中国語 (zh)
- 🇪🇸 スペイン語 (es)
- 🇫🇷 フランス語 (fr)
- 🇩🇪 ドイツ語 (de)

## 前提条件

### 1. 翻訳の依存関係をインストール

```bash
# pip でインストール
pip install openai anthropic

# または pdm
pdm install -G translation
```

### 2. API キーの設定

OpenAI または Anthropic のいずれかの API キーが必要です:

```bash
# OpenAI 用
export TRANSLATION_API_KEY="sk-..."

# または Anthropic 用
export TRANSLATION_API_KEY="sk-ant-..."
```

### 3. GitHub CLI のインストール (任意)

PR を自動生成する場合:

```bash
# macOS
brew install gh

# Linux
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh

# 認証
gh auth login
```

## 使い方

### Make コマンドを使う (推奨)

最も簡単な実行方法です:

```bash
# すべてのドキュメントをすべての言語へ翻訳
make translate

# 特定の言語へ翻訳
make translate LANG=ko

# API プロバイダとモデルを指定
make translate LANG=ko PROVIDER=openai MODEL=gpt-4
make translate LANG=ko PROVIDER=github MODEL=gpt-4o-mini
```

### スクリプトを直接使う

#### すべてのドキュメントを翻訳

すべての対応言語へドキュメント全体を翻訳:

```bash
python scripts/translate.py --api-provider openai
```

### 特定の言語へ翻訳

韓国語のみへ翻訳:

```bash
python scripts/translate.py --target-lang ko --api-provider openai
```

### 特定のファイルだけ翻訳

特定のドキュメントファイルのみ翻訳:

```bash
python scripts/translate.py \
  --target-lang ko \
  --files user-guide/installation.md user-guide/quick-start.md \
  --api-provider openai
```

### PR 作成をスキップ

GitHub PR を作らずに翻訳のみ実行:

```bash
python scripts/translate.py --target-lang ko --no-pr --api-provider openai
```

### Anthropic Claude を使う

OpenAI の代わりに Anthropic の Claude を使用:

```bash
python scripts/translate.py \
  --target-lang ko \
  --api-provider anthropic \
  --api-key "sk-ant-..."
```

## ディレクトリ構造

翻訳後のドキュメント構造は次のようになります:

```
docs/
├── en/                    # 英語 (原文)
│   ├── index.md
│   ├── user-guide/
│   │   ├── installation.md
│   │   ├── quick-start.md
│   │   └── ...
│   ├── tutorial/
│   └── ...
├── ko/                    # 韓国語
│   ├── index.md
│   ├── user-guide/
│   └── ...
├── ja/                    # 日本語
├── zh/                    # 中国語
├── es/                    # スペイン語
├── fr/                    # フランス語
├── de/                    # ドイツ語
├── css/                   # 共有アセット
├── js/                    # 共有アセット
└── img/                   # 共有アセット
```

## 翻訳ワークフロー

### 1. 英語でドキュメントを書く

すべてのドキュメントは、まず英語で `docs/en/` ディレクトリに記述します:

```bash
# 新しいドキュメントを作成
vim docs/en/user-guide/new-feature.md
```

### 2. 翻訳を実行

英語ドキュメントが完成したら、翻訳スクリプトを実行します:

```bash
python scripts/translate.py --target-lang ko
```

### 3. プルリクエストのレビュー

スクリプトは翻訳結果を含む Pull Request を作成します。PR を確認する際のポイント:

1. Markdown フォーマットが保持されているか
2. 技術用語が適切に扱われているか
3. コードサンプルが変更されていないか
4. 言語固有の問題がないか

### Changelog ポリシー

- リポジトリルートの `CHANGELOG.md` は英語のまま維持してください。
- ルート changelog 内のリリース履歴を別言語に書き換えるための翻訳 PR を出さないでください。
- ロケールに changelog ページが必要な場合は、`docs/<locale>/changelog.md` を基準となる英語版 changelog へのラッパーまたは案内ページとして扱ってください。

### 4. 承認とマージ (メンテナー向け)

翻訳が確認できたら:

```bash
gh pr review <pr-number> --approve
gh pr merge <pr-number>
```

### 5. ドキュメントのデプロイ

ドキュメントサイトは新しい翻訳を取り込んで自動的に再ビルドされます。

## 翻訳の設定

`scripts/translation_config.json` を編集してカスタマイズします:

```json
{
  "source_language": "en",
  "target_languages": [
    {
      "code": "ko",
      "name": "Korean",
      "native_name": "한국어",
      "enabled": true
    }
  ],
  "translation_settings": {
    "default_api_provider": "openai",
    "batch_size": 5,
    "preserve_formatting": true
  },
  "github_settings": {
    "create_pr_by_default": true,
    "branch_prefix": "translation"
  }
}
```

## ベストプラクティス

### ソースドキュメント

1. **明快な英語**: 翻訳しやすい平易で明確な英語を書く
2. **一貫した用語**: 技術用語は一貫して使う
3. **正しいコードブロック**: コードブロックには必ず言語を指定する
4. **リンクの検証**: すべての内部リンクは相対パスで指定する

### 翻訳レビュー

1. **技術用語**: 対象言語に適した訳になっているか確認
2. **文化的コンテキスト**: 例題のローカライズが必要かを確認
3. **フォーマット**: Markdown のフォーマットがすべて保持されているか確認
4. **コードの整合性**: コードブロックが書き換えられていないか確認

## トラブルシューティング

### API レート制限

API のレート制限に達した場合は、より小さなバッチで翻訳します:

```bash
# user guide のみ翻訳
python scripts/translate.py \
  --target-lang ko \
  --files user-guide/*.md
```

### 翻訳品質の問題

翻訳品質が低い場合:

1. API キーが有効か確認
2. 別の AI プロバイダを試す
3. 複雑なドキュメントを小さなセクションに分割
4. 翻訳結果を手動でレビューおよび編集

### GitHub PR 作成の失敗

PR 作成に失敗する場合:

```bash
# PR を作らずに翻訳
python scripts/translate.py --target-lang ko --no-pr

# 手動で PR を作成
git checkout -b translation/ko
git add docs/ko/
git commit -m "Add Korean translations"
git push -u origin translation/ko
gh pr create --title "Add Korean translations"
```

## 手動翻訳

手動で翻訳することもできます:

1. 英語ファイルを対象言語ディレクトリへコピー:
```bash
mkdir -p docs/ko/user-guide
cp docs/en/user-guide/installation.md docs/ko/user-guide/installation.md
```

2. 好みのエディタで編集
3. コミットして PR を作成

## 言語切替

ドキュメントサイトのトップナビゲーションには言語切替メニューがあります。利用者は次のことができます:

1. 言語セレクタをクリック
2. 好みの言語を選択
3. 翻訳済みドキュメント間を移動

## 新しい言語の追加

新しい言語を追加するには:

1. `scripts/translation_config.json` を編集:
```json
{
  "code": "pt",
  "name": "Portuguese",
  "native_name": "Português",
  "enabled": true
}
```

2. `mkdocs.yml` を更新:
```yaml
- locale: pt
  name: Português
  build: true
```

3. 翻訳を実行:
```bash
python scripts/translate.py --target-lang pt
```

## ヘルプが必要な場合

- **Issue**: 翻訳に関する問題は [GitHub Issues](https://github.com/bnbong/FastAPI-fastkit/issues) で報告してください
- **Discussions**: 質問は [GitHub Discussions](https://github.com/bnbong/FastAPI-fastkit/discussions) でどうぞ
- **コントリビュート**: [CONTRIBUTING.md](https://github.com/bnbong/FastAPI-fastkit/blob/main/CONTRIBUTING.md) を参照

## 翻訳品質基準

すべての翻訳は次の基準を満たす必要があります:

- ✅ Markdown フォーマットをすべて保持
- ✅ コードブロックは変更しない
- ✅ 技術用語を適切に扱う
- ✅ 正しい文法と表記
- ✅ 言語固有の慣習に従う
- ✅ すべてのリンクが正しく動作することを確認

FastAPI-fastkit の翻訳に貢献いただき、ありがとうございます! 🌍
