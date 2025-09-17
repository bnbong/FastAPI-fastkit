# Docker Containerization and Deployment

Learn how to containerize FastAPI applications with Docker to build consistent development environments and prepare for production deployment. We'll set up a complete Docker-based deployment environment using the `fastapi-dockerized` template.

## What You'll Learn in This Tutorial

- Containerizing FastAPI applications with Docker
- Creating optimized Docker images with multi-stage builds
- Setting up development environments with Docker Compose
- Docker configuration for production deployment
- Container monitoring and log management
- Building CI/CD pipelines

## Prerequisites

- Completed the [Database Integration Tutorial](database-integration.md)
- Docker and Docker Compose installed
- Understanding of basic Docker commands
- Basic knowledge of container concepts

## Advantages of Docker Containerization

### Traditional vs Docker Approach

| Category | Traditional Approach | Docker Approach |
|----------|---------------------|-----------------|
| **Environment Consistency** | Differences between environments | Same environment everywhere |
| **Dependency Management** | Manual installation required | All dependencies included in image |
| **Deployment Speed** | Slow | Fast deployment possible |
| **Scalability** | Limited | Easy scaling |
| **Rollback** | Complex | Immediate rollback to previous version |
| **Resource Usage** | Heavy | Lightweight containers |

## Step 1: Creating Docker-based Project

Create a project using the `fastapi-dockerized` template:

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

## Step 2: Analyzing Docker Configuration Files

Let's examine the Docker-related files in the generated project:

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
└── requirements.txt            # Python dependencies
```

### Dockerfile Analysis

```dockerfile
# Optimized Dockerfile using multi-stage build

# ============================================
# Stage 1: Build stage
# ============================================
FROM python:3.12-slim as builder

# Install build tools
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file and install
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ============================================
# Stage 2: Runtime stage
# ============================================
FROM python:3.12-slim

# System update and essential package installation
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user (security enhancement)
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Create application directory
WORKDIR /app

# Copy Python packages from build stage
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY . .

# Set file permissions
RUN chown -R appuser:appuser /app
RUN chmod +x scripts/start.sh scripts/prestart.sh

# Add Python package path to PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Switch to non-root user
USER appuser

# Configure health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Execute startup script
CMD ["./scripts/start.sh"]
```

### Docker Compose development environment (`docker-compose.yml`)

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
      # Mount volume for development (auto-reload on code changes)
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

### Docker Compose production environment (`docker-compose.prod.yml`)

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

## Step 3: Configure startup scripts

### Main startup script (`scripts/start.sh`)

```bash
#!/bin/bash

set -e

# Set environment variables
export PYTHONPATH=/app:$PYTHONPATH

# Run pre-start script
echo "Running pre-start script..."
./scripts/prestart.sh

# Determine execution mode based on environment
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

### Pre-start script (`scripts/prestart.sh`)

```bash
#!/bin/bash

set -e

echo "Running pre-start checks..."

# Check Python modules and dependencies
echo "Checking Python dependencies..."
python -c "import fastapi, uvicorn, pydantic; print('✓ Core dependencies OK')"

# Check environment variables
if [[ -z "$ENVIRONMENT" ]]; then
    export ENVIRONMENT="development"
    echo "ℹ ENVIRONMENT not set, defaulting to development"
fi

# Create log directory
mkdir -p /app/logs
touch /app/logs/app.log

# Check if health endpoint is present
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

### Gunicorn configuration (`scripts/gunicorn.conf.py`)

```python
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker process
workers = int(os.getenv("WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100

# Worker restart settings
preload_app = True
timeout = 120
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process name
proc_name = "dockerized-todo-api"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Performance tuning
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

## Step 4: Implement health check and monitoring

### Add health check endpoint (`src/main.py`)

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

# Application start time
start_time = time.time()

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Container health check endpoint
    """
    current_time = time.time()
    uptime = current_time - start_time

    # System resource information
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

    # Check if all checks passed
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
        # In actual implementation, test database connection
        return True
    except Exception:
        return False

async def check_redis_connection() -> bool:
    """Check Redis connection status"""
    try:
        # In actual implementation, test Redis connection
        return True
    except Exception:
        return False

def check_disk_space() -> bool:
    """Check disk space"""
    disk_usage = psutil.disk_usage('/')
    free_percentage = (disk_usage.free / disk_usage.total) * 100
    return free_percentage > 10  # 10% or more free space needed

@app.get("/health/ready", status_code=status.HTTP_200_OK)
async def readiness_check():
    """
    Kubernetes readiness probe endpoint
    """
    # Check if application is ready to receive traffic
    return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}

@app.get("/health/live", status_code=status.HTTP_200_OK)
async def liveness_check():
    """
    Kubernetes liveness probe endpoint
    """
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}
```

## Step 5: Configure Nginx reverse proxy

### Development environment Nginx configuration (`nginx/nginx.conf`)

```nginx
events {
    worker_connections 1024;
}

http {
    upstream fastapi_backend {
        # Specify backend by container name
        server app:8000;
    }

    # Define log format
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    'rt=$request_time uct="$upstream_connect_time" '
                    'uht="$upstream_header_time" urt="$upstream_response_time"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # Default settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript
               application/json application/javascript application/xml+rss
               application/atom+xml image/svg+xml;

    server {
        listen 80;
        server_name localhost;

        # Security headers
        add_header X-Content-Type-Options nosniff;
        add_header X-Frame-Options DENY;
        add_header X-XSS-Protection "1; mode=block";

        # Health check endpoint
        location /health {
            proxy_pass http://fastapi_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Health check should respond quickly
            proxy_connect_timeout 5s;
            proxy_send_timeout 5s;
            proxy_read_timeout 5s;
        }

        # API endpoint
        location / {
            proxy_pass http://fastapi_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Timeout settings
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;

            # Buffering settings
            proxy_buffering on;
            proxy_buffer_size 4k;
            proxy_buffers 8 4k;
        }

        # Static file caching (future use)
        location /static {
            expires 1y;
            add_header Cache-Control public;
            add_header ETag "";
        }
    }
}
```

### Production Nginx configuration (`nginx/nginx.prod.conf`)

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

## Step 6: Build and run containers

### Run in development environment

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

### Check logs

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

### Health check test

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

## Step 7: Production deployment

### Set environment variables (`.env.prod`)

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

### Production deployment command

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

## Step 8: Monitoring and logging

### Docker container resource monitoring

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

### Log aggregation and analysis

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

### Prometheus metric collection

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

## Step 9: Build CI/CD pipeline

### GitHub Actions workflow (`.github/workflows/deploy.yml`)

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

## Step 10: Enhance security

### Container security settings

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

### Docker Compose security settings

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

### Secrets management

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

## Next Steps

You've completed Docker containerization! Next things to try:

1. **[Custom Response Handling](custom-response-handling.md)** - Implementing advanced API response formats
<!-- 2. **[Kubernetes Deployment](kubernetes-deployment.md)** - Kubernetes orchestration -->
<!-- 3. **[Microservices Architecture](microservices-architecture.md)** - Service separation and scaling -->
<!-- 4. **[Performance Optimization](performance-optimization.md)** - Caching, load balancing, CDN -->

## Summary

In this tutorial, we used Docker to:

- ✅ Create optimized container images with multi-stage builds
- ✅ Set up development/production environments with Docker Compose
- ✅ Configure Nginx reverse proxy and load balancing
- ✅ Build health check and monitoring systems
- ✅ Implement automated deployment through CI/CD pipelines
- ✅ Set up production-level security configurations
- ✅ Implement logging and metrics collection systems

Now you can safely and efficiently deploy FastAPI applications to production environments!
