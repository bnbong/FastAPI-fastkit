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
- Debe incluir **al menos uno** de los archivos de metadatos:
    - `pyproject.toml-tpl` (preferido, PEP 621), o
    - `setup.py-tpl` (legacy, todavía aceptado)
- `requirements.txt-tpl` es opcional cuando `pyproject.toml-tpl` declara `[project].dependencies`

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
