# Aseguramiento de calidad de las plantillas

FastAPI-fastkit ofrece una validación automatizada e integral de las plantillas para garantizar que todas mantengan una calidad alta y sigan funcionando en distintos entornos y gestores de paquetes.

## Aseguramiento de calidad multicapa

FastAPI-fastkit emplea **dos sistemas de aseguramiento de calidad complementarios**:

### 1. Inspección estática de plantillas
**Validación automatizada semanal de la estructura y la sintaxis de las plantillas**

### 2. Pruebas dinámicas de plantillas
**Pruebas completas de extremo a extremo creando proyectos reales**

## Inspección automatizada semanal

Cada miércoles a medianoche (UTC), nuestro flujo de trabajo de GitHub Actions inspecciona automáticamente todas las plantillas FastAPI para asegurarse de que cumplen los estándares de calidad:

- ✅ **Validación de la estructura de archivos** — comprueba que existen todos los archivos y directorios requeridos
- ✅ **Verificación de extensiones** — valida que los archivos de plantilla usan las extensiones `.py-tpl` correctas
- ✅ **Comprobación de dependencias** — confirma que FastAPI y las dependencias necesarias están bien declaradas
- ✅ **Implementación de FastAPI** — verifica que las plantillas contienen una inicialización adecuada de la app FastAPI
- ✅ **Ejecución de pruebas** — ejecuta las pruebas de la plantilla para confirmar que funcionan
- ✅ **Prueba de humo** — arranca el proyecto generado con uvicorn y sondea su superficie HTTP
- ✅ **Coherencia de la configuración** — versiones de Python fijadas, divergencia de dependencias, autodependencia
- ✅ **Restos de marcadores** — ningún `<placeholder>` sobrevive a la generación del proyecto
- ✅ **Actualidad de las dependencias** — avisa de las versiones fijadas que van por detrás de su última versión en PyPI

## Qué hace cada comprobación

La inspección genera un **proyecto real** a partir de la plantilla — copia, conversión de `-tpl`, inyección de metadatos — y después ejecuta cada comprobación sobre ese proyecto generado, no sobre el código fuente de la plantilla. Una comprobación que solo lee la plantilla no puede detectar un marcador que la generación no consiguió sustituir.

### Prueba de humo

El proyecto generado se inicia con uvicorn en un puerto libre, y el inspector consulta periódicamente hasta que el servidor responde o se agota el tiempo de espera. Una vez arrancado, se solicitan `/docs` y `/health` y se comprueban sus códigos de estado. Después se termina el proceso del servidor, recurriendo a `SIGKILL` si no se detiene.

El objetivo de uvicorn se resuelve en este orden: `[tool.fastapi-fastkit].app_module` en el `pyproject.toml` generado, después `app_module` en el `template-config.yml` de la plantilla y, por último, las ubicaciones convencionales de `main.py`. Es el mismo contrato que usa `fastkit runserver`, así que una plantilla cuya prueba de humo arranca es una plantilla cuyo proyecto generado se ejecuta.

Esta es la comprobación que detecta lo que el análisis estático no puede: un import que solo se resuelve en tiempo de ejecución, un `lifespan` que lanza una excepción, un campo de configuración sin valor por defecto.

### Coherencia de la configuración

Se validan tres cosas contra el `pyproject.toml-tpl` de la plantilla:

- **Las versiones de Python fijadas coinciden y apuntan a 3.12** — `requires-python`, el `target-version` de black y el `python_version` de mypy. Una plantilla que formatea como `py311` mientras declara `>=3.12` es un bug esperando a llegar a un colaborador.
- **Sin divergencia de dependencias** — los paquetes declarados en `requirements.txt-tpl` y en `[project].dependencies` no deben contradecirse. Las plantillas incluyen ambos archivos por compatibilidad con los gestores de paquetes, y dos listas siempre acaban divergiendo si nada las comprueba.
- **Sin autodependencia** — un proyecto generado no debe declarar `FastAPI-fastkit` como dependencia de ejecución. La CLI es una herramienta de desarrollo; incluirla en cada app generada arrastra todo el árbol de dependencias de fastkit a proyectos que no tienen nada que ver.

### Restos de marcadores

Cada `<project_name>`, `<description>` y similares debe sustituirse durante la generación. Cualquier `<placeholder>` que siga presente en el proyecto generado es un error — significa que la inyección de metadatos no conoce ese archivo y que el usuario lo recibiría tal cual.

### Actualidad de las dependencias

Las versiones fijadas se comparan con la última versión publicada en PyPI y se informan como avisos, nunca como errores — una plantilla que va una versión menor por detrás es información, no un fallo. Es la única comprobación que accede a la red, y `--offline` la omite.

## Sistema automatizado de pruebas de plantillas

FastAPI-fastkit incluye un **sistema automatizado de pruebas revolucionario** que valida cada plantilla de forma integral:

### Descubrimiento dinámico de plantillas

El sistema de pruebas **descubre automáticamente todas las plantillas** sin configuración manual:

```console
# Probar todas las plantillas automáticamente
$ pytest tests/test_templates/test_all_templates.py -v

# Los resultados muestran todas las plantillas descubiertas
PASSED tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[fastapi-default]
PASSED tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[fastapi-async-crud]
PASSED tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[fastapi-dockerized]
PASSED tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[fastapi-psql-orm]
```

### Cobertura de pruebas integral

Cada plantilla pasa por **pruebas completas de extremo a extremo**:

#### ✅ Proceso de creación del proyecto
- Copiado de la plantilla y transformación de archivos
- Inyección de metadatos del proyecto (nombre, autor, descripción)
- Validación de la estructura de archivos

#### ✅ Compatibilidad con gestores de paquetes
- **UV** (por defecto): gestor rápido basado en Rust
- **PDM**: gestión moderna de dependencias Python
- **Poetry**: gestión de dependencias consolidada
- **PIP**: gestor de paquetes tradicional

#### ✅ Gestión de entornos virtuales
- Creación del entorno para cada gestor de paquetes
- Verificación de la instalación de dependencias
- Flujos específicos de cada gestor

#### ✅ Resolución de dependencias
- Generación de `pyproject.toml` (UV, PDM, Poetry)
- Generación de `requirements.txt` (PIP)
- Cumplimiento de metadatos (PEP 621)
- Configuración del build system

#### ✅ Validación de la estructura del proyecto
- Identificación del proyecto como FastAPI
- Existencia de los archivos requeridos
- Verificación de la estructura de directorios

### Ejemplos de ejecución de pruebas

**Ejecutar todas las pruebas de plantillas:**
```console
$ pytest tests/test_templates/test_all_templates.py -v
```

**Probar una plantilla concreta:**
```console
$ pytest tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[fastapi-default] -v
```

**Probar con un entorno PDM:**
```console
$ pdm run pytest tests/test_templates/test_all_templates.py -v
```

### Integración continua

El sistema de pruebas automatizado corre en **pipelines CI/CD**:

- ✅ **Validación en pull requests**: cada PR prueba las plantillas afectadas
- ✅ **Pruebas nocturnas**: validación completa de la suite de plantillas
- ✅ **Pruebas multi-gestor**: validación cruzada con todos los gestores
- ✅ **Pruebas multientorno**: varias versiones de Python y plataformas

### Beneficios para colaboradores

**Pruebas sin configuración:**

- 🚀 Añade una plantilla nueva → pruebas automáticas
- ⚡ No hace falta crear archivos de prueba manualmente
- 🛡️ Estándares de calidad consistentes

**Cobertura completa:**

- 🔍 Pruebas de extremo a extremo para la creación de proyectos
- 📦 Validación con varios gestores de paquetes
- 🏗️ Pruebas completas de resolución de dependencias
- ✅ Simulación de uso real

**Experiencia de desarrollo:**

- 🎯 **Foco en el contenido de la plantilla**: las pruebas son automáticas
- 🔄 **Feedback inmediato**: ejecución rápida de las pruebas
- 📊 **Resultados claros**: informe detallado
- 🚫 **Sin boilerplate**: cero configuración de pruebas

## Inspección manual de plantillas

Para desarrollo y depuración, puedes inspeccionar las plantillas manualmente con nuestro script local o con los comandos del Makefile:

### Usar el script de inspección directamente

```console
# Inspeccionar todas las plantillas
$ python scripts/inspect-templates.py

# Inspeccionar plantillas concretas
$ python scripts/inspect-templates.py --templates fastapi-default,fastapi-async-crud

# Salida detallada
$ python scripts/inspect-templates.py --verbose

# Guardar los resultados en un archivo
$ python scripts/inspect-templates.py --output my_results.json
```

#### Flags de inspección

| Flag | Efecto | Úsalo cuando |
|---|---|---|
| `--offline` | Omite todas las consultas de red (informe de actualidad de las dependencias) | No tienes red o quieres una ejecución rápida y aislada |
| `--no-smoke` | Omite el arranque del proyecto generado con uvicorn | Solo iteras sobre la estructura; la prueba de humo es el paso más lento |
| `--mypy` | Comprueba los tipos del proyecto generado con mypy | Antes de enviar una plantilla — es opcional porque es lento |
| `--templates` | Lista de plantillas a inspeccionar, separadas por comas | Trabajas en una sola plantilla |
| `--verbose` | Salida detallada | Depuras un fallo |
| `--output` | Ruta del archivo de resultados JSON | Quieres conservar varias ejecuciones una al lado de otra |

Un ciclo local rápido sobre una sola plantilla:

```console
$ python scripts/inspect-templates.py \
    --templates fastapi-sqlmodel --offline --no-smoke --verbose
```

...y la comprobación completa antes de abrir un PR:

```console
$ python scripts/inspect-templates.py --templates fastapi-sqlmodel --mypy
```

### Usar los comandos del Makefile

```console
# Inspeccionar todas las plantillas
$ make inspect-templates

# Inspeccionar con salida detallada
$ make inspect-templates-verbose

# Inspeccionar plantillas concretas
$ make inspect-template TEMPLATES="fastapi-default,fastapi-async-crud"
```

## Resultados de la inspección

- Las **inspecciones exitosas** se registran en las salidas y artefactos del flujo de trabajo
- Las **inspecciones fallidas** crean automáticamente issues de GitHub con informes detallados
- El **historial de inspecciones** se conserva 30 días en los artefactos de GitHub Actions

## Entender la salida de la inspección

Al ejecutar la inspección verás algo así:

```console
📋 Found 6 templates to inspect: fastapi-async-crud, fastapi-custom-response, fastapi-default, fastapi-dockerized, fastapi-empty, fastapi-psql-orm
============================================================
🔍 Inspecting template: fastapi-async-crud
   Path: /path/to/src/fastapi_fastkit/fastapi_project_template/fastapi-async-crud
✅ fastapi-async-crud: PASSED
----------------------------------------
🔍 Inspecting template: fastapi-custom-response
   Path: /path/to/src/fastapi_fastkit/fastapi_project_template/fastapi-custom-response
✅ fastapi-custom-response: PASSED
----------------------------------------
...
============================================================
📊 INSPECTION SUMMARY
   Total templates: 6
   ✅ Passed: 6
   ❌ Failed: 0
🎉 All templates passed inspection!
📄 Results saved to: template_inspection_results.json
```

## Requisitos de la plantilla

Para que una plantilla pase la inspección, debe cumplir estos requisitos:

### Estructura de archivos
- Debe contener un directorio `src/` con archivos fuente Python
- Los archivos Python deben usar la extensión `.py-tpl`
- Debe incluir un directorio `tests/` y un archivo `README.md-tpl`
- Debe incluir `pyproject.toml-tpl` (PEP 621). Las plantillas incluidas priorizan pyproject y ya no traen `setup.py-tpl`; la inspección todavía lo acepta para que las plantillas de terceros sigan funcionando, pero las plantillas nuevas no deben añadirlo.
- `requirements.txt-tpl` es opcional cuando `pyproject.toml-tpl` declara `[project].dependencies` — pero, cuando ambos están presentes, deben coincidir (ver *Coherencia de la configuración*)
- Debe apuntar a Python 3.12 de forma coherente: `requires-python = ">=3.12"`, black `target-version = ["py312"]`, mypy `python_version = "3.12"` y `python:3.12-slim` para cualquier imagen base de Docker
- No debe declarar `FastAPI-fastkit` como dependencia de ejecución
- No debe dejar ningún `<placeholder>` sin sustituir después de la generación

### Requisitos de FastAPI
- Debe contener la inicialización de la app FastAPI
- Debe declarar `fastapi` como dependencia en al menos uno de: `pyproject.toml-tpl` `[project].dependencies`, `requirements.txt-tpl`, o `setup.py-tpl` `install_requires`
- Todos los archivos de la plantilla deben tener sintaxis Python válida

### Marcadores de identidad
Las plantillas deberían llevar marcadores de identidad de FastAPI-fastkit para que los proyectos generados puedan distinguirse de otros proyectos FastAPI no relacionados dentro del espacio de trabajo del usuario:

- `pyproject.toml-tpl` — tanto un prefijo `[FastAPI-fastkit templated]` en `description` como una tabla `[tool.fastapi-fastkit]` con `managed = true`.
- `setup.py-tpl` — prefijo `[FastAPI-fastkit templated]` en el argumento `description` de `setup()`.

`is_fastkit_project()` acepta cualquiera de ellos (`pyproject` tiene prioridad y `setup.py` queda como compatibilidad heredada; la comparación no distingue entre mayúsculas y minúsculas). La inyección de metadatos asegura que los marcadores lleguen a los proyectos generados aunque la plantilla los olvide.

### Estándares de calidad
- Todos los archivos de la plantilla deben ser sintácticamente correctos
- Las dependencias deben estar especificadas correctamente
- La estructura de la plantilla debe seguir las convenciones de FastAPI-fastkit

Este aseguramiento de calidad automatizado garantiza que todas las plantillas sigan siendo fiables y estén listas para usarse en producción.
