# ¿Qué starter elegir?

FastAPI-fastkit ofrece varias formas de arrancar un proyecto. Esta página es una **ayuda para decidir** dirigida a quienes empiezan: elige un camino aquí y luego salta a [Inicio rápido](quick-start.md) para crear realmente el proyecto.

Si no lo tienes claro, la respuesta corta es:

> **Empieza con `fastkit init --interactive` y elige el preset `domain-starter`.** Es la opción recomendada para las APIs modernas.

El resto de esta página explica por qué y cuándo elegir otra cosa.

## TL;DR — elige por tipo de usuario

| Eres... | Empieza por |
|---|---|
| Nuevo en FastAPI y quieres una guía paso a paso | `fastkit init --interactive` (preset: **`domain-starter`**) |
| Quieres una demo CRUD funcionando para leerla y modificarla | `fastkit startdemo fastapi-default` |
| Quieres el scaffold más pequeño posible | `fastkit init --interactive` (preset: **`minimal`**) |
| Escribes un prototipo rápido / un script de un solo archivo | `fastkit init --interactive` (preset: **`single-module`**) |
| Necesitas una base de datos real (PostgreSQL + SQLAlchemy + Alembic) | `fastkit startdemo fastapi-psql-orm` |
| Quieres un layout de dominio orientado a producción para una API mediana | `fastkit init --interactive` (preset: **`domain-starter`**) |

## `startdemo` vs `init --interactive` — ¿en qué se diferencian?

Estas son las dos puertas de entrada principales. Sirven a propósitos distintos.

### `fastkit startdemo <template>`

Deja en disco un **proyecto de ejemplo completo y funcional** basado en una de las plantillas que se distribuyen (`fastapi-default`, `fastapi-async-crud`, `fastapi-psql-orm`, `fastapi-domain-starter`, ...). El código fuente de la plantilla se pega tal cual, con los marcadores de metadatos (`<project_name>`, etc.) rellenados.

- ✅ El camino más rápido a una demo ejecutable.
- ✅ Todo el código es real y legible — ideal para aprender con ejemplos.
- ❌ La pila y la estructura de la plantilla son fijas; por ejemplo, no puedes activar CORS y a la vez dejar fuera la autenticación al generar el proyecto.

```console
$ fastkit list-templates              # ver lo disponible
$ fastkit startdemo fastapi-default   # generar un proyecto a partir de una
```

### `fastkit init --interactive`

Te guía con un **asistente paso a paso**: metadatos del proyecto → preset de arquitectura → selección de funcionalidades (base de datos, autenticación, testing, despliegue, ...) → gestor de paquetes → confirmación. El generador elige una plantilla base adecuada para cada preset y añade encima las funcionalidades que selecciones.

- ✅ Tú armas la pila que realmente quieres.
- ✅ El preset de arquitectura define la estructura del proyecto (single-file, layered, orientada a dominios, ...).
- ❌ Los presets más completos que conservan `main.py` (`classic-layered`, `domain-starter`) generan módulos de configuración, pero esperan que conectes tú mismo esos módulos al router incluido. Consulta la [matriz de presets / features](../reference/preset-feature-matrix.md) para ver el contrato de cada preset y de cada funcionalidad.

```console
$ fastkit init --interactive
```

## Los cuatro presets de arquitectura

Estos aparecen dentro de `fastkit init --interactive` tras los prompts de información del proyecto. Usa esta sección para decidir cuál elegir.

### `minimal` — empezar lo más simple posible y crecer después

La app FastAPI viable más pequeña. Scaffold vacío + un único `src/main.py` regenerado a partir de tus banderas de features. CORS, rate limiting e instrumentación con Prometheus se conectan automáticamente en `main.py` si los seleccionas.

- 👤 **Para quién**: gente que quiere añadir estructura por su cuenta a medida que el proyecto crece, o que está explorando FastAPI sin opiniones predefinidas sobre el layout.
- 📦 **Plantilla base**: `fastapi-empty`.
- 🧠 **Modelo mental**: "dame un archivo con FastAPI importado y déjame averiguar el resto".

### `single-module` — prototipo estilo script

Todo vive en un solo módulo. Misma capa de regeneración de `main.py` que `minimal`.

- 👤 **Para quién**: cuando escribes un script de pegamento, un webhook pequeño o un prototipo de un día que no necesita fronteras entre paquetes.
- 📦 **Plantilla base**: `fastapi-single-module`.
- 🧠 **Modelo mental**: "quiero un único archivo de Python que pueda ejecutar y leer de una sentada".

### `classic-layered` — partición en capas (api / crud / schemas / core)

El layout "estilo Django" divide el código horizontalmente por responsabilidad: todos los routers en `api/`, toda la lógica CRUD en `crud/`, todos los esquemas Pydantic en `schemas/` y toda la configuración en `core/`. El `main.py` que trae la plantilla se **conserva** (ya incluye CORS); las configuraciones generadas de base de datos y autenticación se guardan en `src/core/`.

- 👤 **Para quién**: equipos familiarizados con layouts estilo Django/Rails, proyectos con muchos endpoints pequeños que comparten la misma cañería CRUD.
- 📦 **Plantilla base**: `fastapi-default`.
- 🧠 **Modelo mental**: "divide el código por _qué es_".

### `domain-starter` — orientado a dominios (opción recomendada)

El código se divide verticalmente por **concepto de negocio**: cada dominio agrupa su propio router, service, repository y schemas dentro de `src/app/domains/<concept>/`. Incluye un endpoint `/health` y un dominio de ejemplo `items` que puedes copiar y renombrar para cada concepto nuevo. El `main.py` que trae la plantilla (en `src/app/`) se conserva; las configuraciones generadas se guardan en `src/app/core/`.

- 👤 **Para quién**: APIs medianas que crecerán con varios conceptos distintos (users, orders, billing, ...). Es la opción moderna recomendada.
- 📦 **Plantilla base**: `fastapi-domain-starter`.
- 🧠 **Modelo mental**: "divide el código por _qué hace_ para el negocio".

## Matriz de comparación

Comparativa rápida en paralelo.

| | `minimal` | `single-module` | `classic-layered` | `domain-starter` |
|---|---|---|---|---|
| Plantilla base | `fastapi-empty` | `fastapi-single-module` | `fastapi-default` | `fastapi-domain-starter` |
| Punto de entrada del proyecto | `src/main.py` | `src/main.py` | `src/main.py` | `src/app/main.py` |
| Ubicación de los routers | (los añades tú) | (dentro de `main.py`) | `src/api/routes/` | `src/app/domains/<concept>/router.py` |
| Carpetas por dominio | ❌ | ❌ | ❌ | ✅ |
| Endpoint `/health` integrado | ✅ | ✅ | ❌ | ✅ |
| `main.py` regenerado desde features | ✅ | ✅ | ❌ | ❌ |
| CORS pre-conectado en `main.py` | añadido si se selecciona | añadido si se selecciona | sí (vía env) | sí (vía env) |
| pyproject-first | opcional | opcional | opcional | ✅ |
| Ideal para | "haré crecer mi propia estructura" | "prototipo en un archivo" | "dividir por preocupación" | "dividir por concepto de negocio" |

Para ver el contrato completo, funcionalidad por funcionalidad (rutas de destino de las configuraciones de base de datos y auth, qué selecciones necesitan cableado manual y cuáles se conectan solas, cuándo saltan los avisos), consulta la [matriz de presets de arquitectura](../reference/preset-feature-matrix.md).

## Elegir una plantilla de `startdemo`

`fastkit startdemo <template>` es la mejor opción cuando quieres un **ejemplo completo y ejecutable** en lugar de un ensamblaje guiado. La mayoría de las plantillas se corresponden aproximadamente con uno de los cuatro presets de arriba, pero añaden código de ejemplo extra (endpoints CRUD sobre un almacén mock, manejo personalizado de respuestas, herramientas de Docker, etc.).

| Plantilla | Preset más cercano | Cuándo elegirla |
|---|---|---|
| `fastapi-default` | `classic-layered` | Demo CRUD que funciona con el layout en capas. Buen primer paso. |
| `fastapi-empty` | `minimal` | Scaffold pelado; la misma forma a la que llega `minimal`. |
| `fastapi-single-module` | `single-module` | Demo en un solo archivo. |
| `fastapi-domain-starter` | `domain-starter` | Opción moderna recomendada; trae un dominio de ejemplo `items`. |
| `fastapi-async-crud` | `classic-layered` | Equivalente async a `fastapi-default`. |
| `fastapi-custom-response` | `classic-layered` | Demuestra envelopes / formato de respuesta personalizados. |
| `fastapi-dockerized` | `classic-layered` | Añade un Dockerfile listo para producción al layout default. |
| `fastapi-psql-orm` | (sin preset directo) | PostgreSQL + SQLAlchemy + Alembic. Elígela cuando necesites una base de datos real. |
| `fastapi-mcp` | (sin preset directo) | Integración con Model Context Protocol. |

`fastkit list-templates` muestra la lista viva con descripciones de una línea.

## Preguntas frecuentes

**P. ¿Tengo que elegir un preset / plantilla desde el principio?**
No — siempre puedes reorganizar a mano el código generado más tarde. Los presets son puntos de partida, no contratos. No le des demasiadas vueltas a la elección.

**P. ¿Cuál es la opción "moderna"?**
`domain-starter`. Es pyproject-first, trae un endpoint `/health` y usa el layout al que convergen la mayoría de los proyectos FastAPI medianos bien mantenidos.

**P. ¿Puedo pasar de `classic-layered` a `domain-starter` más tarde?**
Sí, pero es una refactorización manual — no hay comando de migración. Si crees que tu proyecto va a crecer lo suficiente como para necesitar carpetas de dominio, empieza ahí.

**P. ¿Y si solo quiero aprender FastAPI?**
Empieza con `fastkit startdemo fastapi-default` — lee el código, ejecuta los tests, cambia algunos endpoints. Cuando te sientas cómodo, `fastkit init --interactive` con el preset `domain-starter` es el paso natural siguiente.

**P. ¿Dónde veo los archivos exactos que genera cada preset?**
La [matriz de presets de arquitectura](../reference/preset-feature-matrix.md) es la página de referencia para eso.

## Próximos pasos

- [Inicio rápido](quick-start.md) — crear de verdad tu primer proyecto.
- [Crear proyectos](creating-projects.md) — recorrido más profundo de los flags de la CLI.
- [Tutorial del proyecto orientado a dominios](../tutorial/domain-starter.md) — si elegiste `domain-starter`, este es el recorrido de principio a fin del árbol generado, el ejemplo `items` incluido y cómo añadir tu siguiente dominio.
- [Matriz de presets de arquitectura](../reference/preset-feature-matrix.md) — el contrato completo por preset y por feature.
