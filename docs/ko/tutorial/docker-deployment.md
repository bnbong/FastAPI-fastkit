# Docker 컨테이너화와 배포

FastAPI 애플리케이션을 Docker로 컨테이너화해 일관된 개발 환경을 만들고 배포까지 준비하는 방법을 배웁니다. `fastapi-dockerized` 템플릿으로 완전한 Docker 기반 배포 환경을 구성합니다.

## 이 튜토리얼에서 배우는 내용

- Docker로 FastAPI 애플리케이션 컨테이너화
- 멀티 스테이지 빌드로 최적화된 Docker 이미지 만들기
- Docker Compose로 개발 환경 구성
- 프로덕션 배포용 Docker 설정
- 컨테이너 모니터링과 로그 관리
- CI/CD 파이프라인 구축

## 사전 요구 사항

- [데이터베이스 통합 튜토리얼](database-integration.md) 완료
- Docker와 Docker Compose 설치
- 기본 Docker 명령에 대한 이해
- 컨테이너 개념의 기초 지식

## Docker 컨테이너화의 장점

### 기존 방식 vs Docker 방식

| 항목 | 기존 방식 | Docker 방식 |
|----------|---------------------|-----------------|
| **환경 일관성** | 환경 간 차이 발생 | 어디서나 동일한 환경 |
| **의존성 관리** | 수동 설치 필요 | 모든 의존성이 이미지에 포함 |
| **배포 속도** | 느림 | 빠른 배포 가능 |
| **확장성** | 제한적 | 손쉬운 스케일링 |
| **롤백** | 복잡 | 이전 버전으로 즉시 롤백 |
| **자원 사용** | 무거움 | 가벼운 컨테이너 |

## 1단계: Docker 기반 프로젝트 생성

`fastapi-dockerized` 템플릿으로 프로젝트를 만듭니다:

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

## 2단계: Docker 설정 파일 분석

생성된 프로젝트의 Docker 관련 파일들을 살펴봅시다:

```
dockerized-todo-api/
├── Dockerfile                    # Docker 이미지 빌드 설정
├── docker-compose.yml           # 개발 환경 컨테이너 구성
├── docker-compose.prod.yml      # 프로덕션 환경 구성
├── .dockerignore               # Docker 빌드 시 제외할 파일
├── scripts/
│   ├── start.sh                # 컨테이너 시작 스크립트
│   ├── prestart.sh             # 시작 전 초기화 스크립트
│   └── gunicorn.conf.py        # Gunicorn 설정
├── src/
│   ├── main.py                 # FastAPI 애플리케이션
│   └── ...                     # 기타 소스 코드
└── requirements.txt            # Python 의존성
```

### Dockerfile 분석

```dockerfile
# 멀티 스테이지 빌드를 사용한 최적화된 Dockerfile

# ============================================
# 1단계: 빌드 스테이지
# ============================================
FROM python:3.12-slim as builder

# 빌드 도구 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ============================================
# 2단계: 런타임 스테이지
# ============================================
FROM python:3.12-slim

# 시스템 갱신과 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# non-root 사용자 생성 (보안 강화)
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 애플리케이션 디렉터리 생성
WORKDIR /app

# 빌드 스테이지에서 Python 패키지 복사
COPY --from=builder /root/.local /home/appuser/.local

# 애플리케이션 코드 복사
COPY . .

# 파일 권한 설정
RUN chown -R appuser:appuser /app
RUN chmod +x scripts/start.sh scripts/prestart.sh

# Python 패키지 경로를 PATH 에 추가
ENV PATH=/home/appuser/.local/bin:$PATH

# non-root 사용자로 전환
USER appuser

# 헬스 체크 구성
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 포트 노출
EXPOSE 8000

# 시작 스크립트 실행
CMD ["./scripts/start.sh"]
```

### Docker Compose 개발 환경 (`docker-compose.yml`)

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
      # 개발용 볼륨 마운트 (코드 변경 시 자동 리로드)
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

  # Redis (캐싱 및 세션 저장소)
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

  # Nginx (리버스 프록시)
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

### Docker Compose 프로덕션 환경 (`docker-compose.prod.yml`)

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

## 3단계: 시작 스크립트 구성

### 메인 시작 스크립트 (`scripts/start.sh`)

```bash
#!/bin/bash

set -e

# 환경 변수 설정
export PYTHONPATH=/app:$PYTHONPATH

# 시작 전 스크립트 실행
echo "Running pre-start script..."
./scripts/prestart.sh

# 환경에 따라 실행 모드 결정
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

### 시작 전 스크립트 (`scripts/prestart.sh`)

```bash
#!/bin/bash

set -e

echo "Running pre-start checks..."

# Python 모듈과 의존성 확인
echo "Checking Python dependencies..."
python -c "import fastapi, uvicorn, pydantic; print('✓ Core dependencies OK')"

# 환경 변수 확인
if [[ -z "$ENVIRONMENT" ]]; then
    export ENVIRONMENT="development"
    echo "ℹ ENVIRONMENT not set, defaulting to development"
fi

# 로그 디렉터리 생성
mkdir -p /app/logs
touch /app/logs/app.log

# health 엔드포인트 존재 확인
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

### Gunicorn 설정 (`scripts/gunicorn.conf.py`)

```python
import multiprocessing
import os

# 서버 소켓
bind = "0.0.0.0:8000"
backlog = 2048

# 워커 프로세스
workers = int(os.getenv("WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100

# 워커 재시작 설정
preload_app = True
timeout = 120
keepalive = 2

# 로깅
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 프로세스 이름
proc_name = "dockerized-todo-api"

# 보안
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# 성능 튜닝
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

## 4단계: 헬스 체크와 모니터링 구현

### 헬스 체크 엔드포인트 추가 (`src/main.py`)

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

# 애플리케이션 시작 시간
start_time = time.time()

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Container health check endpoint
    """
    current_time = time.time()
    uptime = current_time - start_time

    # 시스템 자원 정보
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

    # 모든 체크가 통과했는지 확인
    all_checks_passed = all(health_data["checks"].values())

    if not all_checks_passed:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=health_data
        )

    return health_data

async def check_database_connection() -> bool:
    """Check database connection status"""
    try:
        # 실제 구현에서는 데이터베이스 연결을 테스트
        return True
    except Exception:
        return False

async def check_redis_connection() -> bool:
    """Check Redis connection status"""
    try:
        # 실제 구현에서는 Redis 연결을 테스트
        return True
    except Exception:
        return False

def check_disk_space() -> bool:
    """Check disk space"""
    disk_usage = psutil.disk_usage('/')
    free_percentage = (disk_usage.free / disk_usage.total) * 100
    return free_percentage > 10  # 10% 이상 여유 공간 필요

@app.get("/health/ready", status_code=status.HTTP_200_OK)
async def readiness_check():
    """
    Kubernetes readiness probe endpoint
    """
    # 애플리케이션이 트래픽을 받을 준비가 됐는지 확인
    return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}

@app.get("/health/live", status_code=status.HTTP_200_OK)
async def liveness_check():
    """
    Kubernetes liveness probe endpoint
    """
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}
```

## 5단계: Nginx 리버스 프록시 구성

### 개발 환경 Nginx 설정 (`nginx/nginx.conf`)

```nginx
events {
    worker_connections 1024;
}

http {
    upstream fastapi_backend {
        # 컨테이너 이름으로 백엔드 지정
        server app:8000;
    }

    # 로그 형식 정의
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    'rt=$request_time uct="$upstream_connect_time" '
                    'uht="$upstream_header_time" urt="$upstream_response_time"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # 기본 설정
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;

    # Gzip 압축
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript
               application/json application/javascript application/xml+rss
               application/atom+xml image/svg+xml;

    server {
        listen 80;
        server_name localhost;

        # 보안 헤더
        add_header X-Content-Type-Options nosniff;
        add_header X-Frame-Options DENY;
        add_header X-XSS-Protection "1; mode=block";

        # 헬스 체크 엔드포인트
        location /health {
            proxy_pass http://fastapi_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # 헬스 체크는 빠르게 응답해야 함
            proxy_connect_timeout 5s;
            proxy_send_timeout 5s;
            proxy_read_timeout 5s;
        }

        # API 엔드포인트
        location / {
            proxy_pass http://fastapi_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # 타임아웃 설정
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;

            # 버퍼링 설정
            proxy_buffering on;
            proxy_buffer_size 4k;
            proxy_buffers 8 4k;
        }

        # 정적 파일 캐싱 (향후 사용)
        location /static {
            expires 1y;
            add_header Cache-Control public;
            add_header ETag "";
        }
    }
}
```

### 프로덕션 Nginx 설정 (`nginx/nginx.prod.conf`)

```nginx
events {
    worker_connections 2048;
}

http {
    upstream fastapi_backend {
        # 여러 app 인스턴스에 대한 로드 밸런싱
        server app:8000 max_fails=3 fail_timeout=30s;
        # server app2:8000 max_fails=3 fail_timeout=30s;  # 스케일링용

        # Keep-alive
        keepalive 32;
    }

    # 보안 설정
    server_tokens off;

    # 레이트 제한
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=health:10m rate=100r/s;

    # SSL 설정
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

        # 보안 헤더
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Content-Type-Options nosniff always;
        add_header X-Frame-Options DENY always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;

        # 헬스 체크 (레이트 제한 적용)
        location /health {
            limit_req zone=health burst=20 nodelay;
            proxy_pass http://fastapi_backend;
            include /etc/nginx/proxy_params;
        }

        # API 엔드포인트 (레이트 제한 적용)
        location / {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://fastapi_backend;
            include /etc/nginx/proxy_params;
        }
    }
}
```

## 6단계: 컨테이너 빌드와 실행

### 개발 환경에서 실행

<div class="termy">

```console
$ cd dockerized-todo-api

# Docker 이미지 빌드
$ docker-compose build
Building app
Step 1/15 : FROM python:3.12-slim as builder
 ---> abc123def456
Step 2/15 : RUN apt-get update && apt-get install -y build-essential curl
 ---> Running in xyz789abc123
...
Successfully built def456ghi789
Successfully tagged dockerized-todo-api_app:latest

# 컨테이너 실행 (백그라운드)
$ docker-compose up -d
Creating network "dockerized-todo-api_app-network" with driver "bridge"
Creating volume "dockerized-todo-api_redis_data" with default driver
Creating dockerized-todo-redis ... done
Creating dockerized-todo-api   ... done
Creating dockerized-todo-nginx ... done

# 컨테이너 상태 확인
$ docker-compose ps
        Name                      Command               State                    Ports
------------------------------------------------------------------------------------------------
dockerized-todo-api    ./scripts/start.sh               Up (healthy)   8000/tcp
dockerized-todo-nginx  /docker-entrypoint.sh ngin ...   Up             0.0.0.0:80->80/tcp, :::80->80/tcp
dockerized-todo-redis  docker-entrypoint.sh redis ...   Up (healthy)   0.0.0.0:6379->6379/tcp, :::6379->6379/tcp
```

</div>

### 로그 확인

<div class="termy">

```console
# 모든 서비스 로그 확인
$ docker-compose logs

# 특정 서비스 로그 확인
$ docker-compose logs app
$ docker-compose logs nginx
$ docker-compose logs redis

# 실시간 로그 확인
$ docker-compose logs -f app
```

</div>

### 헬스 체크 테스트

<div class="termy">

```console
# 기본 헬스 체크
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

# Kubernetes probe 테스트
$ curl http://localhost/health/ready
$ curl http://localhost/health/live
```

</div>

## 7단계: 프로덕션 배포

### 환경 변수 설정 (`.env.prod`)

```bash
# 애플리케이션 설정
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-super-secret-key-here
WORKERS=4

# 데이터베이스 설정
DATABASE_URL=postgresql://user:password@db:5432/todoapp
REDIS_URL=redis://:password@redis:6379/0
REDIS_PASSWORD=your-redis-password

# 로깅 설정
LOG_LEVEL=info
LOG_FILE=/app/logs/app.log

# 보안 설정
ALLOWED_HOSTS=["your-domain.com"]
CORS_ORIGINS=["https://your-frontend.com"]

# 모니터링
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

### 프로덕션 배포 명령

<div class="termy">

```console
# 프로덕션 환경에 배포
$ docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# 스케일링 (app 인스턴스 수 늘리기)
$ docker-compose -f docker-compose.prod.yml up -d --scale app=3

# 롤링 업데이트
$ docker-compose -f docker-compose.prod.yml build app
$ docker-compose -f docker-compose.prod.yml up -d --no-deps app

# 백업 전 안전한 종료
$ docker-compose -f docker-compose.prod.yml down --timeout 30
```

</div>

## 8단계: 모니터링과 로깅

### Docker 컨테이너 자원 모니터링

<div class="termy">

```console
# 실시간 자원 사용량 확인
$ docker stats

CONTAINER ID   NAME                    CPU %     MEM USAGE / LIMIT     MEM %     NET I/O           BLOCK I/O         PIDS
abc123def456   dockerized-todo-api     2.34%     128.5MiB / 1GiB       12.55%    1.23MB / 456kB    12.3MB / 4.56MB   15
def456ghi789   dockerized-todo-nginx   0.12%     12.5MiB / 256MiB      4.88%     456kB / 1.23MB    1.23MB / 456kB    3
ghi789jkl012   dockerized-todo-redis   1.45%     32.1MiB / 512MiB      6.27%     789kB / 2.34MB    4.56MB / 1.23MB   4

# 특정 컨테이너 상세 정보 확인
$ docker inspect dockerized-todo-api

# 컨테이너 내부 프로세스 확인
$ docker-compose exec app ps aux
```

</div>

### 로그 집계와 분석

```yaml
# docker-compose.logging.yml
version: '3.8'

services:
  # 로그 집계용 ELK Stack
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

  # 로그 수집용 Fluentd
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

### Prometheus 메트릭 수집

```python
# src/monitoring.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Request, Response
import time

# 메트릭 정의
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

## 9단계: CI/CD 파이프라인 구축

### GitHub Actions 워크플로 (`.github/workflows/deploy.yml`)

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

            # 새 이미지 풀
            docker-compose -f docker-compose.prod.yml pull

            # 롤링 업데이트
            docker-compose -f docker-compose.prod.yml up -d --no-deps app

            # 헬스 체크
            sleep 30
            curl -f http://localhost/health || exit 1

            # 이전 이미지 정리
            docker image prune -f
```

## 10단계: 보안 강화

### 컨테이너 보안 설정

```dockerfile
# Dockerfile 에 보안 강화 추가

# non-root 사용자로 실행
USER appuser

# 읽기 전용 루트 파일 시스템
# docker run --read-only --tmpfs /tmp dockerized-todo-api

# 권한 제한
# docker run --cap-drop=ALL dockerized-todo-api

# 네트워크 격리
# docker run --network=none dockerized-todo-api
```

### Docker Compose 보안 설정

```yaml
# docker-compose.yml 에 보안 설정 추가
services:
  app:
    # ... 기존 설정 ...
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

### 시크릿 관리

```yaml
# docker-compose.yml 에 시크릿 설정 추가
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

## 다음 단계

Docker 컨테이너화를 마쳤습니다! 다음으로 시도해 볼 만한 것들:

1. **[커스텀 응답 처리](custom-response-handling.md)** — 고급 API 응답 형식 구현
<!-- 2. **[Kubernetes Deployment](kubernetes-deployment.md)** - Kubernetes orchestration -->
<!-- 3. **[Microservices Architecture](microservices-architecture.md)** - Service separation and scaling -->
<!-- 4. **[Performance Optimization](performance-optimization.md)** - Caching, load balancing, CDN -->

## 요약

이 튜토리얼에서는 Docker로 다음 작업을 진행했습니다:

- ✅ 멀티 스테이지 빌드로 최적화된 컨테이너 이미지 생성
- ✅ Docker Compose 로 개발 / 프로덕션 환경 구성
- ✅ Nginx 리버스 프록시와 로드 밸런싱 구성
- ✅ 헬스 체크와 모니터링 시스템 구축
- ✅ CI/CD 파이프라인을 통한 자동화된 배포 구현
- ✅ 프로덕션 수준의 보안 설정 적용
- ✅ 로깅과 메트릭 수집 시스템 구현

이제 FastAPI 애플리케이션을 안전하고 효율적으로 프로덕션 환경에 배포할 수 있습니다!
