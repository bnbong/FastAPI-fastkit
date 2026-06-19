# Docker 容器化与部署

学习如何用 Docker 把 FastAPI 应用容器化,构建一致的开发环境并为生产部署做准备。本节我们将通过 `fastapi-dockerized` 模板搭建一套完整的 Docker 部署环境。

## 您将学到的内容

- 用 Docker 把 FastAPI 应用容器化
- 通过多阶段构建生成优化的 Docker 镜像
- 用 Docker Compose 搭建开发环境
- 面向生产部署的 Docker 配置
- 容器监控与日志管理
- 构建 CI/CD 流水线

## 前置条件

- 完成 [数据库集成教程](database-integration.md)
- 已安装 Docker 与 Docker Compose
- 熟悉常见的 Docker 命令
- 对容器概念有基础认知

## Docker 容器化的优势

### 传统方式 vs Docker 方式

| 类别 | 传统方式 | Docker 方式 |
|----------|---------------------|-----------------|
| **环境一致性** | 各环境间存在差异 | 各处环境一致 |
| **依赖管理** | 需要手动安装 | 所有依赖打入镜像 |
| **部署速度** | 慢 | 可快速部署 |
| **可扩展性** | 受限 | 易于扩展 |
| **回滚** | 复杂 | 可立即回滚到上一版本 |
| **资源占用** | 较重 | 轻量级容器 |

## 第 1 步:创建基于 Docker 的项目

使用 `fastapi-dockerized` 模板创建项目:

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

## 第 2 步:分析 Docker 配置文件

让我们看看生成项目中的 Docker 相关文件:

```
dockerized-todo-api/
├── Dockerfile                    # Docker image build configuration
├── docker-compose.yml           # Development environment container setup
├── docker-compose.prod.yml      # Production environment configuration
├── .dockerignore               # Files to exclude during Docker build
├── scripts/
│   ├── start.sh                # Container startup script
│   ├── prestart.sh             # Pre-start initialization script
│   └── gunicorn.conf.py        # Gunicorn configuration
├── src/
│   ├── main.py                 # FastAPI application
│   └── ...                     # Other source code
└── requirements.txt            # Python 依赖
```

### Dockerfile 解析

```dockerfile
# 使用多阶段构建优化 Dockerfile

# ============================================
# 阶段 1：构建阶段
# ============================================
FROM python:3.12-slim as builder

# 安装构建工具
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ============================================
# 阶段 2：运行阶段
# ============================================
FROM python:3.12-slim

# 更新系统并安装必要软件包
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 创建非 root 用户（增强安全性）
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 创建应用目录
WORKDIR /app

# 从构建阶段复制 Python 包
COPY --from=builder /root/.local /home/appuser/.local

# 复制应用代码
COPY . .

# 设置文件权限
RUN chown -R appuser:appuser /app
RUN chmod +x scripts/start.sh scripts/prestart.sh

# 将 Python 包路径加入 PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# 切换到非 root 用户
USER appuser

# 配置健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 暴露端口
EXPOSE 8000

# 执行启动脚本
CMD ["./scripts/start.sh"]
```

### Docker Compose 开发环境(`docker-compose.yml`)

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
      # 挂载开发用卷（代码变化时自动重载）
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

  # Redis (for caching and session store)
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

  # Nginx (reverse proxy)
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

### Docker Compose 生产环境(`docker-compose.prod.yml`)

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

## 第 3 步:配置启动脚本

### 主启动脚本(`scripts/start.sh`)

```bash
#!/bin/bash

set -e

# 设置环境变量
export PYTHONPATH=/app:$PYTHONPATH

# 运行预启动脚本
echo "Running pre-start script..."
./scripts/prestart.sh

# 根据环境决定运行模式
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

### 预启动脚本(`scripts/prestart.sh`)

```bash
#!/bin/bash

set -e

echo "Running pre-start checks..."

# 检查 Python 模块和依赖
echo "Checking Python dependencies..."
python -c "import fastapi, uvicorn, pydantic; print('✓ Core dependencies OK')"

# 检查环境变量
if [[ -z "$ENVIRONMENT" ]]; then
    export ENVIRONMENT="development"
    echo "ℹ ENVIRONMENT not set, defaulting to development"
fi

# 创建日志目录
mkdir -p /app/logs
touch /app/logs/app.log

# 检查是否存在 health 端点
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

### Gunicorn 配置(`scripts/gunicorn.conf.py`)

```python
import multiprocessing
import os

# 服务端监听配置
bind = "0.0.0.0:8000"
backlog = 2048

# Worker 进程配置
workers = int(os.getenv("WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100

# Worker 重启设置
preload_app = True
timeout = 120
keepalive = 2

# 日志配置
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 进程名称
proc_name = "dockerized-todo-api"

# 安全限制
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# 性能调优
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

## 第 4 步:实现健康检查与监控

### 添加健康检查端点(`src/main.py`)

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

# 应用启动时间
start_time = time.time()

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    容器健康检查端点
    """
    current_time = time.time()
    uptime = current_time - start_time

    # 系统资源信息
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

    # 检查所有健康项是否通过
    all_checks_passed = all(health_data["checks"].values())

    if not all_checks_passed:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=health_data
        )

    return health_data

async def check_database_connection() -> bool:
    """检查数据库连接状态"""
    try:
        # 在实际实现中，这里应执行数据库连通性检测
        return True
    except Exception:
        return False

async def check_redis_connection() -> bool:
    """检查 Redis 连接状态"""
    try:
        # 在实际实现中，这里应执行 Redis 连通性检测
        return True
    except Exception:
        return False

def check_disk_space() -> bool:
    """检查磁盘空间"""
    disk_usage = psutil.disk_usage('/')
    free_percentage = (disk_usage.free / disk_usage.total) * 100
    return free_percentage > 10  # 至少保留 10% 可用空间

@app.get("/health/ready", status_code=status.HTTP_200_OK)
async def readiness_check():
    """
    Kubernetes 就绪探针端点
    """
    # 检查应用是否已准备好接收流量
    return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}

@app.get("/health/live", status_code=status.HTTP_200_OK)
async def liveness_check():
    """
    Kubernetes 存活探针端点
    """
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}
```

## 第 5 步:配置 Nginx 反向代理

### 开发环境 Nginx 配置(`nginx/nginx.conf`)

```nginx
events {
    worker_connections 1024;
}

http {
    upstream fastapi_backend {
        # 通过容器名指定后端服务
        server app:8000;
    }

    # 定义日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    'rt=$request_time uct="$upstream_connect_time" '
                    'uht="$upstream_header_time" urt="$upstream_response_time"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # 默认设置
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript
               application/json application/javascript application/xml+rss
               application/atom+xml image/svg+xml;

    server {
        listen 80;
        server_name localhost;

        # 安全响应头
        add_header X-Content-Type-Options nosniff;
        add_header X-Frame-Options DENY;
        add_header X-XSS-Protection "1; mode=block";

        # 健康检查端点
        location /health {
            proxy_pass http://fastapi_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # 健康检查应快速返回
            proxy_connect_timeout 5s;
            proxy_send_timeout 5s;
            proxy_read_timeout 5s;
        }

        # API 入口
        location / {
            proxy_pass http://fastapi_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # 超时设置
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;

            # 缓冲设置
            proxy_buffering on;
            proxy_buffer_size 4k;
            proxy_buffers 8 4k;
        }

        # 静态文件缓存（后续可扩展）
        location /static {
            expires 1y;
            add_header Cache-Control public;
            add_header ETag "";
        }
    }
}
```

### 生产环境 Nginx 配置(`nginx/nginx.prod.conf`)

```nginx
events {
    worker_connections 2048;
}

http {
    upstream fastapi_backend {
        # Load balancing for multiple app instances
        server app:8000 max_fails=3 fail_timeout=30s;
        # server app2:8000 max_fails=3 fail_timeout=30s;  # For scaling

        # Keep-alive
        keepalive 32;
    }

    # Security settings
    server_tokens off;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=health:10m rate=100r/s;

    # SSL settings
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

        # Security headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Content-Type-Options nosniff always;
        add_header X-Frame-Options DENY always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;

        # Health check (rate limit applied)
        location /health {
            limit_req zone=health burst=20 nodelay;
            proxy_pass http://fastapi_backend;
            include /etc/nginx/proxy_params;
        }

        # API endpoint (rate limit applied)
        location / {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://fastapi_backend;
            include /etc/nginx/proxy_params;
        }
    }
}
```

## 第 6 步:构建并运行容器

### 在开发环境运行

<div class="termy">

```console
$ cd dockerized-todo-api

# Build Docker image
$ docker-compose build
Building app
Step 1/15 : FROM python:3.12-slim as builder
 ---> abc123def456
Step 2/15 : RUN apt-get update && apt-get install -y build-essential curl
 ---> Running in xyz789abc123
...
Successfully built def456ghi789
Successfully tagged dockerized-todo-api_app:latest

# Run container (background)
$ docker-compose up -d
Creating network "dockerized-todo-api_app-network" with driver "bridge"
Creating volume "dockerized-todo-api_redis_data" with default driver
Creating dockerized-todo-redis ... done
Creating dockerized-todo-api   ... done
Creating dockerized-todo-nginx ... done

# Check container status
$ docker-compose ps
        Name                      Command               State                    Ports
------------------------------------------------------------------------------------------------
dockerized-todo-api    ./scripts/start.sh               Up (healthy)   8000/tcp
dockerized-todo-nginx  /docker-entrypoint.sh ngin ...   Up             0.0.0.0:80->80/tcp, :::80->80/tcp
dockerized-todo-redis  docker-entrypoint.sh redis ...   Up (healthy)   0.0.0.0:6379->6379/tcp, :::6379->6379/tcp
```

</div>

### 查看日志

<div class="termy">

```console
# Check all service logs
$ docker-compose logs

# Check specific service logs
$ docker-compose logs app
$ docker-compose logs nginx
$ docker-compose logs redis

# Check real-time logs
$ docker-compose logs -f app
```

</div>

### 健康检查测试

<div class="termy">

```console
# Basic health check
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

# Kubernetes probe test
$ curl http://localhost/health/ready
$ curl http://localhost/health/live
```

</div>

## 第 7 步:生产部署

### 设置环境变量(`.env.prod`)

```bash
# Application settings
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-super-secret-key-here
WORKERS=4

# Database settings
DATABASE_URL=postgresql://user:password@db:5432/todoapp
REDIS_URL=redis://:password@redis:6379/0
REDIS_PASSWORD=your-redis-password

# Logging settings
LOG_LEVEL=info
LOG_FILE=/app/logs/app.log

# Security settings
ALLOWED_HOSTS=["your-domain.com"]
CORS_ORIGINS=["https://your-frontend.com"]

# Monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

### 生产部署命令

<div class="termy">

```console
# Deploy in production environment
$ docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# Scaling (app instance scaling)
$ docker-compose -f docker-compose.prod.yml up -d --scale app=3

# Rolling update
$ docker-compose -f docker-compose.prod.yml build app
$ docker-compose -f docker-compose.prod.yml up -d --no-deps app

# Safe shutdown before backup
$ docker-compose -f docker-compose.prod.yml down --timeout 30
```

</div>

## 第 8 步:监控与日志

### Docker 容器资源监控

<div class="termy">

```console
# Check real-time resource usage
$ docker stats

CONTAINER ID   NAME                    CPU %     MEM USAGE / LIMIT     MEM %     NET I/O           BLOCK I/O         PIDS
abc123def456   dockerized-todo-api     2.34%     128.5MiB / 1GiB       12.55%    1.23MB / 456kB    12.3MB / 4.56MB   15
def456ghi789   dockerized-todo-nginx   0.12%     12.5MiB / 256MiB      4.88%     456kB / 1.23MB    1.23MB / 456kB    3
ghi789jkl012   dockerized-todo-redis   1.45%     32.1MiB / 512MiB      6.27%     789kB / 2.34MB    4.56MB / 1.23MB   4

# Check specific container details
$ docker inspect dockerized-todo-api

# Check container internal processes
$ docker-compose exec app ps aux
```

</div>

### 日志聚合与分析

```yaml
# docker-compose.logging.yml
version: '3.8'

services:
  # ELK Stack for log aggregation
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

  # Fluentd for log collection
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

### Prometheus 指标收集

```python
# src/monitoring.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Request, Response
import time

# Define metrics
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
    """Prometheus metric collection middleware"""
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
    """Prometheus metric endpoint"""
    return Response(generate_latest(), media_type="text/plain")
```

## 第 9 步:构建 CI/CD 流水线

### GitHub Actions 工作流(`.github/workflows/deploy.yml`)

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

            # Pull new image
            docker-compose -f docker-compose.prod.yml pull

            # Rolling update
            docker-compose -f docker-compose.prod.yml up -d --no-deps app

            # Health check
            sleep 30
            curl -f http://localhost/health || exit 1

            # Clean up previous image
            docker image prune -f
```

## 第 10 步:加强安全

### 容器安全设置

```dockerfile
# Add security enhancement to Dockerfile

# Run as non-root user
USER appuser

# Read-only root filesystem
# docker run --read-only --tmpfs /tmp dockerized-todo-api

# Limit permissions
# docker run --cap-drop=ALL dockerized-todo-api

# Network isolation
# docker run --network=none dockerized-todo-api
```

### Docker Compose 安全设置

```yaml
# Add security settings to docker-compose.yml
services:
  app:
    # ... existing settings ...
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

### 机密管理

```yaml
# Add secrets settings to docker-compose.yml
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

## 下一步

恭喜您完成了 Docker 容器化!接下来可以尝试:

1. **[自定义响应处理](custom-response-handling.md)** —— 实现进阶的 API 响应格式
<!-- 2. **[Kubernetes Deployment](kubernetes-deployment.md)** - Kubernetes orchestration -->
<!-- 3. **[Microservices Architecture](microservices-architecture.md)** - Service separation and scaling -->
<!-- 4. **[Performance Optimization](performance-optimization.md)** - Caching, load balancing, CDN -->

## 小结

在本教程中,我们用 Docker 完成了:

- ✅ 通过多阶段构建生成优化的容器镜像
- ✅ 用 Docker Compose 搭建开发 / 生产环境
- ✅ 配置 Nginx 反向代理与负载均衡
- ✅ 构建健康检查与监控体系
- ✅ 通过 CI/CD 流水线实现自动化部署
- ✅ 配置生产级别的安全设置
- ✅ 实现日志与指标收集系统

现在您可以安全、高效地把 FastAPI 应用部署到生产环境!
