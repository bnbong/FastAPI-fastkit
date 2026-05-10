# Docker でのコンテナ化とデプロイ

FastAPI アプリケーションを Docker でコンテナ化して、一貫した開発環境と本番デプロイの準備を整える方法を学びます。`fastapi-dockerized` テンプレートを使い、完全な Docker ベースのデプロイ環境を構築します。

## このチュートリアルで学ぶこと

- Docker による FastAPI アプリケーションのコンテナ化
- マルチステージビルドで最適化された Docker イメージの作成
- Docker Compose による開発環境のセットアップ
- 本番デプロイ向けの Docker 構成
- コンテナ監視とログ管理
- CI/CD パイプラインの構築

## 前提条件

- [データベース統合チュートリアル](database-integration.md) を完了済み
- Docker と Docker Compose がインストール済み
- 基本的な Docker コマンドの理解
- コンテナの基礎概念

## Docker コンテナ化の利点

### 従来手法と Docker 手法の比較

| 項目 | 従来手法 | Docker 手法 |
|---|---|---|
| **環境の一貫性** | 環境ごとに差異 | どこでも同じ環境 |
| **依存関係管理** | 手動インストールが必要 | すべての依存関係をイメージに含む |
| **デプロイ速度** | 遅い | 高速デプロイが可能 |
| **拡張性** | 限定的 | 容易にスケール |
| **ロールバック** | 複雑 | 直前バージョンへ即座に戻せる |
| **リソース利用** | 重い | 軽量なコンテナ |

## ステップ 1: Docker ベースプロジェクトの作成

`fastapi-dockerized` テンプレートでプロジェクトを作成します:

<div class="termy">

```console
$ fastkit startdemo fastapi-dockerized
Enter the project name: dockerized-todo-api
Enter the author name: Developer Kim
Enter the author email: developer@example.com
Enter the project description: Dockerized todo management API
Deploying FastAPI project using 'fastapi-dockerized' template

           Project Information
┌──────────────┬─────────────────────────────────────────────┐
│ Project Name │ dockerized-todo-api                         │
│ Author       │ Developer Kim                               │
│ Author Email │ developer@example.com                       │
│ Description  │ Dockerized todo management API              │
└──────────────┴─────────────────────────────────────────────┘

       Template Dependencies
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ pydantic          │
│ Dependency 4 │ pydantic-settings │
│ Dependency 5 │ python-dotenv     │
└──────────────┴───────────────────┘

Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y

✨ FastAPI project 'dockerized-todo-api' from 'fastapi-dockerized' has been created successfully!
```

</div>

## ステップ 2: Docker 設定ファイルの解析

生成プロジェクトに含まれる Docker 関連ファイルを見ていきましょう:

```
dockerized-todo-api/
├── Dockerfile                    # Docker イメージのビルド設定
├── docker-compose.yml           # 開発環境のコンテナ構成
├── docker-compose.prod.yml      # 本番環境の構成
├── .dockerignore               # Docker ビルドから除外するファイル
├── scripts/
│   ├── start.sh                # コンテナ起動スクリプト
│   ├── prestart.sh             # 起動前の初期化スクリプト
│   └── gunicorn.conf.py        # Gunicorn 設定
├── src/
│   ├── main.py                 # FastAPI アプリ
│   └── ...                     # その他のソースコード
└── requirements.txt            # Python 依存関係
```

### Dockerfile の解析

```dockerfile
# マルチステージビルドで最適化した Dockerfile

# ============================================
# ステージ 1: ビルドステージ
# ============================================
FROM python:3.12-slim as builder

# ビルドツールをインストール
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 依存関係ファイルをコピーしてインストール
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ============================================
# ステージ 2: ランタイムステージ
# ============================================
FROM python:3.12-slim

# システム更新と必要パッケージのインストール
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 非 root ユーザーを作成 (セキュリティ強化)
RUN groupadd -r appuser && useradd -r -g appuser appuser

# アプリケーションディレクトリを作成
WORKDIR /app

# ビルドステージから Python パッケージをコピー
COPY --from=builder /root/.local /home/appuser/.local

# アプリケーションコードをコピー
COPY . .

# ファイル権限を設定
RUN chown -R appuser:appuser /app
RUN chmod +x scripts/start.sh scripts/prestart.sh

# Python パッケージのパスを PATH に追加
ENV PATH=/home/appuser/.local/bin:$PATH

# 非 root ユーザーへ切り替え
USER appuser

# ヘルスチェックを設定
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# ポートを公開
EXPOSE 8000

# 起動スクリプトを実行
CMD ["./scripts/start.sh"]
```

### Docker Compose 開発環境 (`docker-compose.yml`)

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: dockerized-todo-api
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=development
      - DEBUG=true
      - RELOAD=true
    volumes:
      # 開発用にボリュームをマウント (コード変更で自動リロード)
      - ./src:/app/src:ro
      - ./scripts:/app/scripts:ro
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Redis (キャッシュとセッションストア用)
  redis:
    image: redis:7-alpine
    container_name: dockerized-todo-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Nginx (リバースプロキシ)
  nginx:
    image: nginx:alpine
    container_name: dockerized-todo-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - app
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  redis_data:

networks:
  app-network:
    driver: bridge
```

### Docker Compose 本番環境 (`docker-compose.prod.yml`)

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    restart: always
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
      - WORKERS=4
      - MAX_WORKERS=8
    volumes:
      - app_logs:/app/logs
    networks:
      - app-network
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3

  redis:
    image: redis:7-alpine
    restart: always
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - app-network
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.prod.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - nginx_logs:/var/log/nginx
    depends_on:
      - app
    networks:
      - app-network
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M

volumes:
  redis_data:
  app_logs:
  nginx_logs:

networks:
  app-network:
    driver: overlay
    attachable: true
```

## ステップ 3: 起動スクリプトの設定

### メイン起動スクリプト (`scripts/start.sh`)

```bash
#!/bin/bash

set -e

# 環境変数を設定
export PYTHONPATH=/app:$PYTHONPATH

# 起動前スクリプトを実行
echo "Running pre-start script..."
./scripts/prestart.sh

# 環境に応じて実行モードを決定
if [[ "$ENVIRONMENT" == "production" ]]; then
    echo "Starting production server with Gunicorn..."
    exec gunicorn src.main:app \
        --config scripts/gunicorn.conf.py \
        --bind 0.0.0.0:8000 \
        --workers ${WORKERS:-4} \
        --worker-class uvicorn.workers.UvicornWorker \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --preload \
        --access-logfile - \
        --error-logfile -
else
    echo "Starting development server with Uvicorn..."
    if [[ "$RELOAD" == "true" ]]; then
        exec uvicorn src.main:app \
            --host 0.0.0.0 \
            --port 8000 \
            --reload \
            --reload-dir src \
            --log-level debug
    else
        exec uvicorn src.main:app \
            --host 0.0.0.0 \
            --port 8000 \
            --log-level info
    fi
fi
```

### 起動前スクリプト (`scripts/prestart.sh`)

```bash
#!/bin/bash

set -e

echo "Running pre-start checks..."

# Python モジュールと依存関係をチェック
echo "Checking Python dependencies..."
python -c "import fastapi, uvicorn, pydantic; print('✓ Core dependencies OK')"

# 環境変数を確認
if [[ -z "$ENVIRONMENT" ]]; then
    export ENVIRONMENT="development"
    echo "ℹ ENVIRONMENT not set, defaulting to development"
fi

# ログディレクトリを作成
mkdir -p /app/logs
touch /app/logs/app.log

# health エンドポイントが存在するか確認
echo "Checking health endpoint..."
python -c "
from src.main import app
routes = [route.path for route in app.routes]
if '/health' not in routes:
    print('⚠ Warning: /health endpoint not found')
else:
    print('✓ Health endpoint OK')
"

echo "Pre-start checks completed successfully!"
```

### Gunicorn 設定 (`scripts/gunicorn.conf.py`)

```python
import multiprocessing
import os

# サーバーソケット
bind = "0.0.0.0:8000"
backlog = 2048

# ワーカープロセス
workers = int(os.getenv("WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100

# ワーカー再起動設定
preload_app = True
timeout = 120
keepalive = 2

# ロギング
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# プロセス名
proc_name = "dockerized-todo-api"

# セキュリティ
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# パフォーマンスチューニング
def when_ready(server):
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def worker_abort(worker):
    worker.log.info("worker received SIGABRT signal")
```

## ステップ 4: ヘルスチェックとモニタリングの実装

### ヘルスチェックエンドポイントを追加 (`src/main.py`)

```python
from fastapi import FastAPI, status, Depends
from fastapi.responses import JSONResponse
import psutil
import time
from datetime import datetime

app = FastAPI(
    title="Dockerized Todo API",
    description="Dockerized todo management API",
    version="1.0.0"
)

# アプリケーション開始時刻
start_time = time.time()

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    コンテナのヘルスチェックエンドポイント
    """
    current_time = time.time()
    uptime = current_time - start_time

    # システムリソース情報
    memory_info = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent(interval=1)

    health_data = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": round(uptime, 2),
        "version": app.version,
        "system": {
            "memory_usage_percent": memory_info.percent,
            "memory_available_mb": round(memory_info.available / 1024 / 1024, 2),
            "cpu_usage_percent": cpu_percent,
        },
        "checks": {
            "database": await check_database_connection(),
            "redis": await check_redis_connection(),
            "disk_space": check_disk_space(),
        }
    }

    # すべてのチェックが通ったか確認
    all_checks_passed = all(health_data["checks"].values())

    if not all_checks_passed:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=health_data
        )

    return health_data

async def check_database_connection() -> bool:
    """データベース接続状態を確認"""
    try:
        # 実装ではデータベース接続をテストする
        return True
    except Exception:
        return False

async def check_redis_connection() -> bool:
    """Redis 接続状態を確認"""
    try:
        # 実装では Redis 接続をテストする
        return True
    except Exception:
        return False

def check_disk_space() -> bool:
    """ディスク空き容量を確認"""
    disk_usage = psutil.disk_usage('/')
    free_percentage = (disk_usage.free / disk_usage.total) * 100
    return free_percentage > 10  # 10% 以上の空きが必要

@app.get("/health/ready", status_code=status.HTTP_200_OK)
async def readiness_check():
    """
    Kubernetes readiness プローブのエンドポイント
    """
    # アプリケーションがトラフィックを受け入れる準備ができているか確認
    return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}

@app.get("/health/live", status_code=status.HTTP_200_OK)
async def liveness_check():
    """
    Kubernetes liveness プローブのエンドポイント
    """
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}
```

## ステップ 5: Nginx リバースプロキシの構成

### 開発環境の Nginx 設定 (`nginx/nginx.conf`)

```nginx
events {
    worker_connections 1024;
}

http {
    upstream fastapi_backend {
        # コンテナ名でバックエンドを指定
        server app:8000;
    }

    # ログフォーマットを定義
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    'rt=$request_time uct="$upstream_connect_time" '
                    'uht="$upstream_header_time" urt="$upstream_response_time"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # デフォルト設定
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;

    # gzip 圧縮
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript
               application/json application/javascript application/xml+rss
               application/atom+xml image/svg+xml;

    server {
        listen 80;
        server_name localhost;

        # セキュリティヘッダー
        add_header X-Content-Type-Options nosniff;
        add_header X-Frame-Options DENY;
        add_header X-XSS-Protection "1; mode=block";

        # ヘルスチェックエンドポイント
        location /health {
            proxy_pass http://fastapi_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # ヘルスチェックは素早く応答する
            proxy_connect_timeout 5s;
            proxy_send_timeout 5s;
            proxy_read_timeout 5s;
        }

        # API エンドポイント
        location / {
            proxy_pass http://fastapi_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # タイムアウト設定
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;

            # バッファ設定
            proxy_buffering on;
            proxy_buffer_size 4k;
            proxy_buffers 8 4k;
        }

        # 静的ファイルのキャッシュ (将来用)
        location /static {
            expires 1y;
            add_header Cache-Control public;
            add_header ETag "";
        }
    }
}
```

### 本番環境の Nginx 設定 (`nginx/nginx.prod.conf`)

```nginx
events {
    worker_connections 2048;
}

http {
    upstream fastapi_backend {
        # 複数 app インスタンスのロードバランス
        server app:8000 max_fails=3 fail_timeout=30s;
        # server app2:8000 max_fails=3 fail_timeout=30s;  # スケール用

        # Keep-alive
        keepalive 32;
    }

    # セキュリティ設定
    server_tokens off;

    # レート制限
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=health:10m rate=100r/s;

    # SSL 設定
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # セキュリティヘッダー
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Content-Type-Options nosniff always;
        add_header X-Frame-Options DENY always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;

        # ヘルスチェック (レート制限あり)
        location /health {
            limit_req zone=health burst=20 nodelay;
            proxy_pass http://fastapi_backend;
            include /etc/nginx/proxy_params;
        }

        # API エンドポイント (レート制限あり)
        location / {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://fastapi_backend;
            include /etc/nginx/proxy_params;
        }
    }
}
```

## ステップ 6: コンテナのビルドと実行

### 開発環境での実行

<div class="termy">

```console
$ cd dockerized-todo-api

# Docker イメージをビルド
$ docker-compose build
Building app
Step 1/15 : FROM python:3.12-slim as builder
 ---> abc123def456
Step 2/15 : RUN apt-get update && apt-get install -y build-essential curl
 ---> Running in xyz789abc123
...
Successfully built def456ghi789
Successfully tagged dockerized-todo-api_app:latest

# コンテナをバックグラウンドで起動
$ docker-compose up -d
Creating network "dockerized-todo-api_app-network" with driver "bridge"
Creating volume "dockerized-todo-api_redis_data" with default driver
Creating dockerized-todo-redis ... done
Creating dockerized-todo-api   ... done
Creating dockerized-todo-nginx ... done

# コンテナ状態を確認
$ docker-compose ps
        Name                      Command               State                    Ports
------------------------------------------------------------------------------------------------
dockerized-todo-api    ./scripts/start.sh               Up (healthy)   8000/tcp
dockerized-todo-nginx  /docker-entrypoint.sh ngin ...   Up             0.0.0.0:80->80/tcp, :::80->80/tcp
dockerized-todo-redis  docker-entrypoint.sh redis ...   Up (healthy)   0.0.0.0:6379->6379/tcp, :::6379->6379/tcp
```

</div>

### ログの確認

<div class="termy">

```console
# すべてのサービスのログを表示
$ docker-compose logs

# 特定サービスのログを表示
$ docker-compose logs app
$ docker-compose logs nginx
$ docker-compose logs redis

# リアルタイムログ
$ docker-compose logs -f app
```

</div>

### ヘルスチェックのテスト

<div class="termy">

```console
# 基本のヘルスチェック
$ curl http://localhost/health
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00.123456",
  "uptime_seconds": 45.67,
  "version": "1.0.0",
  "system": {
    "memory_usage_percent": 25.3,
    "memory_available_mb": 3072.45,
    "cpu_usage_percent": 5.2
  },
  "checks": {
    "database": true,
    "redis": true,
    "disk_space": true
  }
}

# Kubernetes プローブのテスト
$ curl http://localhost/health/ready
$ curl http://localhost/health/live
```

</div>

## ステップ 7: 本番デプロイ

### 環境変数の設定 (`.env.prod`)

```bash
# アプリケーション設定
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-super-secret-key-here
WORKERS=4

# データベース設定
DATABASE_URL=postgresql://user:password@db:5432/todoapp
REDIS_URL=redis://:password@redis:6379/0
REDIS_PASSWORD=your-redis-password

# ロギング設定
LOG_LEVEL=info
LOG_FILE=/app/logs/app.log

# セキュリティ設定
ALLOWED_HOSTS=["your-domain.com"]
CORS_ORIGINS=["https://your-frontend.com"]

# モニタリング
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

### 本番デプロイコマンド

<div class="termy">

```console
# 本番環境にデプロイ
$ docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# スケーリング (app インスタンスのスケール)
$ docker-compose -f docker-compose.prod.yml up -d --scale app=3

# ローリングアップデート
$ docker-compose -f docker-compose.prod.yml build app
$ docker-compose -f docker-compose.prod.yml up -d --no-deps app

# バックアップ前の安全な停止
$ docker-compose -f docker-compose.prod.yml down --timeout 30
```

</div>

## ステップ 8: モニタリングとロギング

### Docker コンテナのリソース監視

<div class="termy">

```console
# リアルタイムのリソース使用量を確認
$ docker stats

CONTAINER ID   NAME                    CPU %     MEM USAGE / LIMIT     MEM %     NET I/O           BLOCK I/O         PIDS
abc123def456   dockerized-todo-api     2.34%     128.5MiB / 1GiB       12.55%    1.23MB / 456kB    12.3MB / 4.56MB   15
def456ghi789   dockerized-todo-nginx   0.12%     12.5MiB / 256MiB      4.88%     456kB / 1.23MB    1.23MB / 456kB    3
ghi789jkl012   dockerized-todo-redis   1.45%     32.1MiB / 512MiB      6.27%     789kB / 2.34MB    4.56MB / 1.23MB   4

# 特定コンテナの詳細
$ docker inspect dockerized-todo-api

# コンテナ内部のプロセスを確認
$ docker-compose exec app ps aux
```

</div>

### ログ集約と分析

```yaml
# docker-compose.logging.yml
version: '3.8'

services:
  # ELK Stack (ログ集約)
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.6.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    networks:
      - logging

  logstash:
    image: docker.elastic.co/logstash/logstash:8.6.0
    volumes:
      - ./logstash/pipeline:/usr/share/logstash/pipeline:ro
      - ./logstash/config:/usr/share/logstash/config:ro
    networks:
      - logging
    depends_on:
      - elasticsearch

  kibana:
    image: docker.elastic.co/kibana/kibana:8.6.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    networks:
      - logging
    depends_on:
      - elasticsearch

  # Fluentd (ログ収集)
  fluentd:
    image: fluent/fluentd:v1.16-debian-1
    volumes:
      - ./fluentd/conf:/fluentd/etc:ro
      - /var/log:/var/log:ro
    networks:
      - logging
    depends_on:
      - elasticsearch

volumes:
  elasticsearch_data:

networks:
  logging:
    driver: bridge
```

### Prometheus メトリクス収集

```python
# src/monitoring.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Request, Response
import time

# メトリクスの定義
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'active_connections',
    'Number of active connections'
)

async def metrics_middleware(request: Request, call_next):
    """Prometheus メトリクス収集ミドルウェア"""
    start_time = time.time()
    method = request.method
    endpoint = request.url.path

    ACTIVE_CONNECTIONS.inc()

    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception as e:
        status_code = 500
        raise
    finally:
        duration = time.time() - start_time
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
        ACTIVE_CONNECTIONS.dec()

    return response

@app.get("/metrics")
async def get_metrics():
    """Prometheus メトリクスエンドポイント"""
    return Response(generate_latest(), media_type="text/plain")
```

## ステップ 9: CI/CD パイプラインの構築

### GitHub Actions ワークフロー (`.github/workflows/deploy.yml`)

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-asyncio httpx

      - name: Run tests
        run: |
          pytest tests/ -v --cov=src --cov-report=xml

      - name: Upload coverage reports
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v4

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=sha
            type=raw,value=latest

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./Dockerfile
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v4

      - name: Deploy to production
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.PROD_USERNAME }}
          key: ${{ secrets.PROD_SSH_KEY }}
          script: |
            cd /opt/dockerized-todo-api

            # 新しいイメージをプル
            docker-compose -f docker-compose.prod.yml pull

            # ローリングアップデート
            docker-compose -f docker-compose.prod.yml up -d --no-deps app

            # ヘルスチェック
            sleep 30
            curl -f http://localhost/health || exit 1

            # 古いイメージを削除
            docker image prune -f
```

## ステップ 10: セキュリティの強化

### コンテナのセキュリティ設定

```dockerfile
# Dockerfile にセキュリティ設定を追加

# 非 root ユーザーで実行
USER appuser

# 読み取り専用ルートファイルシステム
# docker run --read-only --tmpfs /tmp dockerized-todo-api

# 権限の制限
# docker run --cap-drop=ALL dockerized-todo-api

# ネットワーク隔離
# docker run --network=none dockerized-todo-api
```

### Docker Compose のセキュリティ設定

```yaml
# docker-compose.yml にセキュリティ設定を追加
services:
  app:
    # ... 既存の設定 ...
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
    read_only: true
    tmpfs:
      - /tmp
      - /app/logs
    user: "1000:1000"
```

### シークレットの管理

```yaml
# docker-compose.yml に secrets 設定を追加
version: '3.8'

services:
  app:
    secrets:
      - db_password
      - api_key
    environment:
      - DB_PASSWORD_FILE=/run/secrets/db_password
      - API_KEY_FILE=/run/secrets/api_key

secrets:
  db_password:
    file: ./secrets/db_password.txt
  api_key:
    external: true
```

## 次のステップ

Docker でのコンテナ化が完了しました! 次に試すこと:

1. **[カスタムレスポンス処理](custom-response-handling.md)** - 高度な API レスポンス形式の実装
<!-- 2. **[Kubernetes Deployment](kubernetes-deployment.md)** - Kubernetes orchestration -->
<!-- 3. **[Microservices Architecture](microservices-architecture.md)** - Service separation and scaling -->
<!-- 4. **[Performance Optimization](performance-optimization.md)** - Caching, load balancing, CDN -->

## まとめ

このチュートリアルでは、Docker を使って次を行いました:

- ✅ マルチステージビルドで最適化したコンテナイメージを作成
- ✅ Docker Compose で開発 / 本番環境を構築
- ✅ Nginx リバースプロキシとロードバランスを設定
- ✅ ヘルスチェックとモニタリング体制を構築
- ✅ CI/CD パイプラインによる自動デプロイを実装
- ✅ 本番レベルのセキュリティ設定を実施
- ✅ ログとメトリクス収集の仕組みを構築

これで FastAPI アプリケーションを本番環境へ安全かつ効率的にデプロイできます!
