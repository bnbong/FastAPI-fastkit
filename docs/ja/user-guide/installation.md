# インストール

このガイドでは、FastAPI-fastkit のインストール方法を説明します。

## 動作要件

FastAPI-fastkit を使用するには、次の要件を満たす必要があります:

- **Python**: 3.12 以上
- **オペレーティングシステム**: Windows、macOS、Linux に対応

## インストール方法

### pip でインストール (推奨)

最もシンプルなインストール方法です:

<div class="termy">

```console
$ pip install FastAPI-fastkit
---> 100%
Successfully installed FastAPI-fastkit
```

</div>

### 特定バージョンをインストール

特定のバージョンをインストールする場合:

<div class="termy">

```console
$ pip install FastAPI-fastkit==1.0.0
---> 100%
Successfully installed FastAPI-fastkit-1.0.0
```

</div>

### 開発版をインストール

GitHub から直接、最新の開発版をインストールする場合:

<div class="termy">

```console
$ pip install git+https://github.com/bnbong/FastAPI-fastkit.git
---> 100%
Successfully installed FastAPI-fastkit
```

</div>

!!! warning "開発版に関する注意"
    開発版は不安定な可能性があり、本番環境での利用は推奨されません。

## 仮想環境のセットアップ (推奨)

依存関係の競合を避けるため、仮想環境の利用を強く推奨します:

### venv を使う

<div class="termy">

```console
$ python -m venv fastapi-env
$ source fastapi-env/bin/activate  # Linux/macOS
$ fastapi-env\Scripts\activate     # Windows
$ pip install FastAPI-fastkit
```

</div>

### conda を使う

<div class="termy">

```console
$ conda create -n fastapi-env python=3.12
$ conda activate fastapi-env
$ pip install FastAPI-fastkit
```

</div>

## インストールの確認

インストール後、FastAPI-fastkit が正しくインストールされているか確認しましょう:

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

## トラブルシューティング

### コマンドが見つからない

「command not found」エラーが出る場合:

1. **FastAPI-fastkit がインストールされているか確認**:

   <div class="termy">
   ```console
   $ pip show FastAPI-fastkit
   ```
   </div>

2. **仮想環境を確認**:

   <div class="termy">
   ```console
   $ which python
   $ which pip
   ```
   </div>

3. **FastAPI-fastkit を再インストール**:

   <div class="termy">
   ```console
   $ pip uninstall FastAPI-fastkit
   $ pip install FastAPI-fastkit
   ```
   </div>

### パーミッションエラー

インストール時にパーミッションエラーが発生する場合:

**Linux/macOS の場合:**

<div class="termy">

```console
$ pip install --user FastAPI-fastkit
```

</div>

**Windows の場合 (管理者として実行):**

<div class="termy">

```console
$ pip install FastAPI-fastkit
```

</div>

### Python バージョンの互換性

FastAPI-fastkit は Python 3.12 以上が必要です。Python のバージョンを確認しましょう:

<div class="termy">

```console
$ python --version
Python 3.12.0
```

</div>

古いバージョンを使っている場合、Python をアップグレードしてください:

- **公式 Python**: [python.org/downloads](https://www.python.org/downloads/)
- **pyenv の場合**: `pyenv install 3.12.0`
- **conda の場合**: `conda install python=3.12`

## 次のステップ

インストールが完了したら:

1. **[クイックスタート](quick-start.md)**: 5 分で最初のプロジェクトを作成
2. **[入門チュートリアル](../tutorial/getting-started.md)**: 段階的な詳細チュートリアル
3. **[CLI リファレンス](cli-reference.md)**: 全コマンドのリファレンス

!!! tip "インストールのヒント"
    - プロジェクト分離のため、常に仮想環境を利用しましょう
    - FastAPI-fastkit は最新版に更新を保ちましょう
    - 更新情報や Issue は [GitHub リポジトリ](https://github.com/bnbong/FastAPI-fastkit) で確認しましょう
