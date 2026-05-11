# Matriz de presets de arquitectura / funcionalidades

`fastkit init --interactive` pregunta por un **preset de arquitectura** ([issue #44](https://github.com/bnbong/FastAPI-fastkit/issues/44)) antes de recoger las selecciones de funcionalidades. El preset define la estructura del proyecto generado: cada preset parte de una plantilla base distinta y coloca los archivos de configuración en rutas diferentes, para que encajen con la estructura existente en lugar de crear un árbol paralelo `src/config/`.

Esta página es la referencia principal para saber qué hace cada preset, dónde se generan los archivos y qué combinaciones de funcionalidades requieren cableado manual.

## Preset → plantilla base

| Preset | Plantilla base | Descripción |
|---|---|---|
| `minimal` | `fastapi-empty` | La app FastAPI viable más pequeña — el `main.py` placeholder se regenera a partir de tus selecciones de features. |
| `single-module` | `fastapi-single-module` | App FastAPI en un solo archivo — `main.py` se regenera. |
| `classic-layered` | `fastapi-default` | Partición en capas (`api/routes`, `crud`, `schemas`, `core`). El `main.py` que trae la plantilla se conserva. |
| `domain-starter` | `fastapi-domain-starter` | Orientado a dominios (`src/app/domains/<concept>/`). El `main.py` que trae la plantilla se conserva. **Opción recomendada.** |

## Ubicación de los archivos generados

| Preset | Overlay de `main.py` | Destino de la config de base de datos | Destino de la config de autenticación |
|---|---|---|---|
| `minimal` | regenerado en `src/main.py` | `src/config/database.py` | `src/config/auth.py` |
| `single-module` | regenerado en `src/main.py` | `src/config/database.py` | `src/config/auth.py` |
| `classic-layered` | conservado (el que viene en la plantilla) | `src/core/database.py` | `src/core/auth.py` |
| `domain-starter` | conservado (el que viene en la plantilla) | `src/app/core/database.py` | `src/app/core/auth.py` |

## Soporte de base de datos / autenticación por preset

Estas funcionalidades están soportadas en **todos** los presets: la instalación de paquetes siempre se completa con éxito; la diferencia está en si la regeneración dinámica de `main.py` también las conecta automáticamente.

| Funcionalidad | `minimal` / `single-module` | `classic-layered` / `domain-starter` |
|---|---|---|
| **Base de datos** (PostgreSQL, MySQL, SQLite, MongoDB) | Genera el módulo de configuración **y** añade llamadas stub `await init_db()` en el `main.py` regenerado. | Genera el módulo de configuración en la ruta del preset. El `main.py` que viene en la plantilla se **conserva**, así que tienes que cablear `get_db()` en los routers manualmente. |
| **Autenticación** (JWT, FastAPI-Users, OAuth2, basada en sesiones) | Genera el módulo de configuración de auth. JWT también importa `HTTPBearer` en el `main.py` regenerado. | Genera el módulo de configuración de auth en la ruta del preset. No se añaden imports al `main.py` — cablea las dependencias manualmente. |
| **Tareas en segundo plano** (Celery, Dramatiq) | Los paquetes se instalan; por ahora no hay regeneración automática de `main.py`. | Igual. |
| **Caché** (Redis) | Los paquetes se instalan; por ahora no hay regeneración automática de `main.py`. | Igual. |
| **CORS** (utilidad) | Se añade `CORSMiddleware` al `main.py` regenerado con `allow_origins=['*']`. | **Ya cableado** en el `main.py` que trae la plantilla (condicional a `settings.all_cors_origins`). Actívalo definiendo `BACKEND_CORS_ORIGINS` en `.env` — no requiere cambios de código. |
| **Pruebas** (Basic / Coverage / Advanced) | Se genera `pytest.ini` en la raíz del proyecto. | Igual. |
| **Despliegue** (Docker, docker-compose) | Se escribe `Dockerfile` y/o `docker-compose.yml` en la raíz del proyecto. | Igual. |

## Cuándo verás un aviso de "Preset compatibility"

Para los presets que **conservan el `main.py` que trae la plantilla** (`classic-layered`, `domain-starter`), algunas selecciones de funcionalidad no se cablean automáticamente en la app. La CLI muestra al final de la generación un único aviso que lista qué selecciones requieren cableado manual:

| Funcionalidad seleccionada | ¿Dispara aviso bajo `classic-layered` / `domain-starter`? |
|---|---|
| `CORS` (utilidad) | ❌ — ya cableado en el `main.py` de la plantilla. Solo rellena `BACKEND_CORS_ORIGINS` en `.env`. |
| `Rate-Limiting` (utilidad) | ✅ — la configuración del limitador `slowapi` no se añade |
| `Prometheus` (monitorización) | ✅ — no se llama a `Instrumentator().instrument(app)` |
| Cualquier selección de base de datos / auth | ⚠️ — los archivos de configuración se generan, pero tienes que añadirlos con `Depends()` en tus routers |

Para los presets `minimal` y `single-module`, la regeneración dinámica de `main.py` se encarga automáticamente de CORS, rate limiting e instrumentación con Prometheus; no aparece ningún aviso.

## Combinaciones no soportadas (juego seguro)

El estratega deliberadamente **no** intenta inyectar el código generado en un `main.py` que trae la plantilla. Hacerlo correría el riesgo de producir imports rotos o duplicar routers. El contrato es:

- Los paquetes seleccionados siempre se instalan (así `pip freeze` refleja la intención del usuario).
- Los módulos de configuración generados siempre se guardan en la ruta apropiada para el preset.
- Para los presets que preservan `main.py`, se le indica al usuario qué selecciones todavía requieren cableado manual en lugar de entregar código silenciosamente roto.

Si necesitas que todas las funcionalidades se cableen automáticamente, elige `minimal` o `single-module` — esos presets regeneran `main.py` a partir de los feature flags.
