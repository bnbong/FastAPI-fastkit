# Contenedorización y despliegue con Docker

Aprende a contenedorizar aplicaciones FastAPI con Docker para construir entornos de desarrollo consistentes y preparar el despliegue a producción. Configuraremos un entorno de despliegue completo basado en Docker usando la plantilla `fastapi-dockerized`.

## Lo que aprenderás en este tutorial

- Contenedorizar aplicaciones FastAPI con Docker
- Crear imágenes Docker optimizadas con builds multi-stage
- Configurar entornos de desarrollo con Docker Compose
- Configuración Docker para despliegue a producción
- Monitorización de contenedores y gestión de logs
- Construir pipelines CI/CD

## Requisitos previos

- Haber completado el [tutorial de integración con base de datos](database-integration.md)
- Docker y Docker Compose instalados
- Conocimiento de comandos Docker básicos
- Conceptos básicos sobre contenedores

## Ventajas de contenedorizar con Docker

### Enfoque tradicional vs Docker

| Categoría | Enfoque tradicional | Enfoque Docker |
|---|---|---|
| **Consistencia de entornos** | Diferencias entre entornos | Mismo entorno en todas partes |
| **Gestión de dependencias** | Instalación manual | Todas las dependencias en la imagen |
| **Velocidad de despliegue** | Lenta | Despliegue rápido |
| **Escalabilidad** | Limitada | Escalado fácil |
| **Rollback** | Complejo | Rollback inmediato a la versión previa |
| **Uso de recursos** | Pesado | Contenedores ligeros |

## Paso 1: Crear un proyecto basado en Docker

Crea un proyecto con la plantilla `fastapi-dockerized`:

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

## Paso 2: Analizar los archivos de configuración de Docker

Examinemos los archivos relacionados con Docker del proyecto generado:

```
dockerized-todo-api/
├── Dockerfile                    # Configuración de build de la imagen
├── docker-compose.yml           # Setup del contenedor de desarrollo
├── docker-compose.prod.yml      # Configuración del entorno de producción
├── .dockerignore               # Archivos a excluir del build
├── scripts/
│   ├── start.sh                # Script de arranque del contenedor
│   ├── prestart.sh             # Script de inicialización previa
│   └── gunicorn.conf.py        # Configuración de Gunicorn
├── src/
│   ├── main.py                 # Aplicación FastAPI
│   └── ...                     # Otro código fuente
└── requirements.txt            # Dependencias de Python
```

### Análisis del Dockerfile

```dockerfile
# Dockerfile optimizado con build multi-stage

# ============================================
# Stage 1: Build
# ============================================
FROM python:3.12-slim as builder

# Instalar herramientas de build
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de dependencias e instalar
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ============================================
# Stage 2: Runtime
# ============================================
FROM python:3.12-slim

# Actualización del sistema e instalación de paquetes esenciales
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Crear usuario no root (mejora de seguridad)
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Crear directorio de la aplicación
WORKDIR /app

# Copiar paquetes Python desde el stage de build
COPY --from=builder /root/.local /home/appuser/.local

# Copiar el código de la aplicación
COPY . .

# Configurar permisos
RUN chown -R appuser:appuser /app
RUN chmod +x scripts/start.sh scripts/prestart.sh

# Añadir la ruta de paquetes Python al PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Cambiar al usuario no root
USER appuser

# Configurar health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Exponer puerto
EXPOSE 8000

# Ejecutar el script de arranque
CMD ["./scripts/start.sh"]
```

### Entorno de desarrollo con Docker Compose (`docker-compose.yml`)

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
      # Volumen montado para desarrollo (recarga automática al cambiar el código)
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

  # Redis (para caché y almacenamiento de sesión)
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

  # Nginx (proxy inverso)
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

### Entorno de producción con Docker Compose (`docker-compose.prod.yml`)

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

## Paso 3: Configurar los scripts de arranque

### Script principal de arranque (`scripts/start.sh`)

```bash
#!/bin/bash

set -e

# Definir variables de entorno
export PYTHONPATH=/app:$PYTHONPATH

# Ejecutar script previo al arranque
echo "Running pre-start script..."
./scripts/prestart.sh

# Determinar el modo según el entorno
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

### Script previo al arranque (`scripts/prestart.sh`)

```bash
#!/bin/bash

set -e

echo "Running pre-start checks..."

# Comprobar módulos Python y dependencias
echo "Checking Python dependencies..."
python -c "import fastapi, uvicorn, pydantic; print('✓ Core dependencies OK')"

# Comprobar variables de entorno
if [[ -z "$ENVIRONMENT" ]]; then
    export ENVIRONMENT="development"
    echo "ℹ ENVIRONMENT not set, defaulting to development"
fi

# Crear directorio de logs
mkdir -p /app/logs
touch /app/logs/app.log

# Comprobar si el endpoint de health existe
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

### Configuración de Gunicorn (`scripts/gunicorn.conf.py`)

```python
import multiprocessing
import os

# Socket del servidor
bind = "0.0.0.0:8000"
backlog = 2048

# Procesos worker
workers = int(os.getenv("WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100

# Configuración de reinicio de workers
preload_app = True
timeout = 120
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Nombre del proceso
proc_name = "dockerized-todo-api"

# Seguridad
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Tuning de rendimiento
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

## Paso 4: Implementar health check y monitorización

### Añadir endpoint de health check (`src/main.py`)

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

# Hora de arranque de la aplicación
start_time = time.time()

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Endpoint de health check del contenedor
    """
    current_time = time.time()
    uptime = current_time - start_time

    # Información de recursos del sistema
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

    # Comprobar si todos los checks han pasado
    all_checks_passed = all(health_data["checks"].values())

    if not all_checks_passed:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=health_data
        )

    return health_data

async def check_database_connection() -> bool:
    """Comprobar el estado de la conexión a la base de datos"""
    try:
        # En la implementación real, probar la conexión a la BD
        return True
    except Exception:
        return False

async def check_redis_connection() -> bool:
    """Comprobar el estado de la conexión a Redis"""
    try:
        # En la implementación real, probar la conexión a Redis
        return True
    except Exception:
        return False

def check_disk_space() -> bool:
    """Comprobar el espacio en disco"""
    disk_usage = psutil.disk_usage('/')
    free_percentage = (disk_usage.free / disk_usage.total) * 100
    return free_percentage > 10  # Hace falta al menos un 10% libre

@app.get("/health/ready", status_code=status.HTTP_200_OK)
async def readiness_check():
    """
    Endpoint para readiness probe de Kubernetes
    """
    # Comprobar si la app está lista para recibir tráfico
    return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}

@app.get("/health/live", status_code=status.HTTP_200_OK)
async def liveness_check():
    """
    Endpoint para liveness probe de Kubernetes
    """
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}
```

## Paso 5: Configurar Nginx como proxy inverso

### Configuración de Nginx para desarrollo (`nginx/nginx.conf`)

```nginx
events {
    worker_connections 1024;
}

http {
    upstream fastapi_backend {
        # Especificar backend por nombre de contenedor
        server app:8000;
    }

    # Definir formato de log
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    'rt=$request_time uct="$upstream_connect_time" '
                    'uht="$upstream_header_time" urt="$upstream_response_time"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # Configuración por defecto
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;

    # Compresión gzip
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript
               application/json application/javascript application/xml+rss
               application/atom+xml image/svg+xml;

    server {
        listen 80;
        server_name localhost;

        # Cabeceras de seguridad
        add_header X-Content-Type-Options nosniff;
        add_header X-Frame-Options DENY;
        add_header X-XSS-Protection "1; mode=block";

        # Endpoint de health check
        location /health {
            proxy_pass http://fastapi_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # El health check debe responder rápido
            proxy_connect_timeout 5s;
            proxy_send_timeout 5s;
            proxy_read_timeout 5s;
        }

        # Endpoint de la API
        location / {
            proxy_pass http://fastapi_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Timeouts
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;

            # Buffering
            proxy_buffering on;
            proxy_buffer_size 4k;
            proxy_buffers 8 4k;
        }

        # Caché de archivos estáticos (uso futuro)
        location /static {
            expires 1y;
            add_header Cache-Control public;
            add_header ETag "";
        }
    }
}
```

### Configuración de Nginx para producción (`nginx/nginx.prod.conf`)

```nginx
events {
    worker_connections 2048;
}

http {
    upstream fastapi_backend {
        # Balanceo de carga entre varias instancias de la app
        server app:8000 max_fails=3 fail_timeout=30s;
        # server app2:8000 max_fails=3 fail_timeout=30s;  # Para escalado

        # Keep-alive
        keepalive 32;
    }

    # Configuración de seguridad
    server_tokens off;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=health:10m rate=100r/s;

    # Configuración SSL
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

        # Cabeceras de seguridad
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Content-Type-Options nosniff always;
        add_header X-Frame-Options DENY always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;

        # Health check (con rate limit)
        location /health {
            limit_req zone=health burst=20 nodelay;
            proxy_pass http://fastapi_backend;
            include /etc/nginx/proxy_params;
        }

        # Endpoint de la API (con rate limit)
        location / {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://fastapi_backend;
            include /etc/nginx/proxy_params;
        }
    }
}
```

## Paso 6: Construir y ejecutar los contenedores

### Ejecutar en entorno de desarrollo

<div class="termy">

```console
$ cd dockerized-todo-api

# Construir la imagen Docker
$ docker-compose build
Building app
Step 1/15 : FROM python:3.12-slim as builder
 ---> abc123def456
Step 2/15 : RUN apt-get update && apt-get install -y build-essential curl
 ---> Running in xyz789abc123
...
Successfully built def456ghi789
Successfully tagged dockerized-todo-api_app:latest

# Ejecutar los contenedores (en segundo plano)
$ docker-compose up -d
Creating network "dockerized-todo-api_app-network" with driver "bridge"
Creating volume "dockerized-todo-api_redis_data" with default driver
Creating dockerized-todo-redis ... done
Creating dockerized-todo-api   ... done
Creating dockerized-todo-nginx ... done

# Comprobar el estado de los contenedores
$ docker-compose ps
        Name                      Command               State                    Ports
------------------------------------------------------------------------------------------------
dockerized-todo-api    ./scripts/start.sh               Up (healthy)   8000/tcp
dockerized-todo-nginx  /docker-entrypoint.sh ngin ...   Up             0.0.0.0:80->80/tcp, :::80->80/tcp
dockerized-todo-redis  docker-entrypoint.sh redis ...   Up (healthy)   0.0.0.0:6379->6379/tcp, :::6379->6379/tcp
```

</div>

### Revisar los logs

<div class="termy">

```console
# Ver los logs de todos los servicios
$ docker-compose logs

# Logs de un servicio concreto
$ docker-compose logs app
$ docker-compose logs nginx
$ docker-compose logs redis

# Logs en tiempo real
$ docker-compose logs -f app
```

</div>

### Probar el health check

<div class="termy">

```console
# Health check básico
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

# Probar las probes de Kubernetes
$ curl http://localhost/health/ready
$ curl http://localhost/health/live
```

</div>

## Paso 7: Despliegue a producción

### Definir variables de entorno (`.env.prod`)

```bash
# Configuración de la aplicación
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-super-secret-key-here
WORKERS=4

# Configuración de base de datos
DATABASE_URL=postgresql://user:password@db:5432/todoapp
REDIS_URL=redis://:password@redis:6379/0
REDIS_PASSWORD=your-redis-password

# Configuración de logs
LOG_LEVEL=info
LOG_FILE=/app/logs/app.log

# Configuración de seguridad
ALLOWED_HOSTS=["your-domain.com"]
CORS_ORIGINS=["https://your-frontend.com"]

# Monitorización
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

### Comando de despliegue a producción

<div class="termy">

```console
# Desplegar en producción
$ docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# Escalado (escalar las instancias de app)
$ docker-compose -f docker-compose.prod.yml up -d --scale app=3

# Rolling update
$ docker-compose -f docker-compose.prod.yml build app
$ docker-compose -f docker-compose.prod.yml up -d --no-deps app

# Apagar de forma segura antes de un backup
$ docker-compose -f docker-compose.prod.yml down --timeout 30
```

</div>

## Paso 8: Monitorización y logs

### Monitorización de recursos de los contenedores Docker

<div class="termy">

```console
# Ver el uso de recursos en tiempo real
$ docker stats

CONTAINER ID   NAME                    CPU %     MEM USAGE / LIMIT     MEM %     NET I/O           BLOCK I/O         PIDS
abc123def456   dockerized-todo-api     2.34%     128.5MiB / 1GiB       12.55%    1.23MB / 456kB    12.3MB / 4.56MB   15
def456ghi789   dockerized-todo-nginx   0.12%     12.5MiB / 256MiB      4.88%     456kB / 1.23MB    1.23MB / 456kB    3
ghi789jkl012   dockerized-todo-redis   1.45%     32.1MiB / 512MiB      6.27%     789kB / 2.34MB    4.56MB / 1.23MB   4

# Ver los detalles de un contenedor concreto
$ docker inspect dockerized-todo-api

# Ver los procesos internos del contenedor
$ docker-compose exec app ps aux
```

</div>

### Agregación y análisis de logs

```yaml
# docker-compose.logging.yml
version: '3.8'

services:
  # ELK Stack para agregación de logs
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

  # Fluentd para recopilar logs
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

### Recolección de métricas con Prometheus

```python
# src/monitoring.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Request, Response
import time

# Definir métricas
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
    """Middleware de recolección de métricas Prometheus"""
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
    """Endpoint de métricas Prometheus"""
    return Response(generate_latest(), media_type="text/plain")
```

## Paso 9: Construir el pipeline CI/CD

### Flujo de trabajo con GitHub Actions (`.github/workflows/deploy.yml`)

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

            # Bajar la nueva imagen
            docker-compose -f docker-compose.prod.yml pull

            # Rolling update
            docker-compose -f docker-compose.prod.yml up -d --no-deps app

            # Health check
            sleep 30
            curl -f http://localhost/health || exit 1

            # Limpiar imagen anterior
            docker image prune -f
```

## Paso 10: Mejorar la seguridad

### Configuración de seguridad de los contenedores

```dockerfile
# Añadir refuerzos de seguridad al Dockerfile

# Ejecutar como usuario no root
USER appuser

# Sistema de archivos raíz de solo lectura
# docker run --read-only --tmpfs /tmp dockerized-todo-api

# Limitar permisos
# docker run --cap-drop=ALL dockerized-todo-api

# Aislamiento de red
# docker run --network=none dockerized-todo-api
```

### Configuración de seguridad de Docker Compose

```yaml
# Añadir configuración de seguridad a docker-compose.yml
services:
  app:
    # ... configuración existente ...
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

### Gestión de secretos

```yaml
# Añadir configuración de secretos a docker-compose.yml
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

## Próximos pasos

¡Has terminado la contenedorización con Docker! Próximos pasos:

1. **[Manejo personalizado de respuestas](custom-response-handling.md)** - Implementar formatos de respuesta avanzados
<!-- 2. **[Kubernetes Deployment](kubernetes-deployment.md)** - Kubernetes orchestration -->
<!-- 3. **[Microservices Architecture](microservices-architecture.md)** - Service separation and scaling -->
<!-- 4. **[Performance Optimization](performance-optimization.md)** - Caching, load balancing, CDN -->

## Resumen

En este tutorial hemos usado Docker para:

- ✅ Crear imágenes de contenedor optimizadas con builds multi-stage
- ✅ Configurar entornos de desarrollo / producción con Docker Compose
- ✅ Configurar Nginx como proxy inverso con balanceo de carga
- ✅ Construir sistemas de health check y monitorización
- ✅ Implementar despliegue automatizado vía pipelines CI/CD
- ✅ Configurar seguridad de nivel producción
- ✅ Implementar sistemas de logs y recolección de métricas

¡Ahora puedes desplegar aplicaciones FastAPI a entornos de producción de forma segura y eficiente!
