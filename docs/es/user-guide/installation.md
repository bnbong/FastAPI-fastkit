# Instalación

Esta guía explica cómo instalar FastAPI-fastkit.

## Requisitos

Para usar FastAPI-fastkit, necesitas cumplir los siguientes requisitos:

- **Python**: 3.12 o superior
- **Sistema operativo**: Windows, macOS y Linux soportados

## Métodos de instalación

### Instalar con pip (recomendado)

El método de instalación más simple:

<div class="termy">

```console
$ pip install FastAPI-fastkit
---> 100%
Successfully installed FastAPI-fastkit
```

</div>

### Instalar una versión específica

Para instalar una versión concreta:

<div class="termy">

```console
$ pip install FastAPI-fastkit==1.0.0
---> 100%
Successfully installed FastAPI-fastkit-1.0.0
```

</div>

### Instalar la versión de desarrollo

Para instalar la última versión de desarrollo directamente desde GitHub:

<div class="termy">

```console
$ pip install git+https://github.com/bnbong/FastAPI-fastkit.git
---> 100%
Successfully installed FastAPI-fastkit
```

</div>

!!! warning "Aviso sobre la versión de desarrollo"
    Las versiones de desarrollo pueden ser inestables y no se recomiendan para entornos de producción.

## Configurar un entorno virtual (recomendado)

Se recomienda encarecidamente usar un entorno virtual para evitar conflictos de dependencias:

### Usando venv

<div class="termy">

```console
$ python -m venv fastapi-env
$ source fastapi-env/bin/activate  # Linux/macOS
$ fastapi-env\Scripts\activate     # Windows
$ pip install FastAPI-fastkit
```

</div>

### Usando conda

<div class="termy">

```console
$ conda create -n fastapi-env python=3.12
$ conda activate fastapi-env
$ pip install FastAPI-fastkit
```

</div>

## Verificar la instalación

Tras la instalación, comprueba que FastAPI-fastkit está correctamente instalado:

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

## Solución de problemas

### Comando no encontrado

Si obtienes un error "command not found":

1. **Comprueba si FastAPI-fastkit está instalado**:

   <div class="termy">
   ```console
   $ pip show FastAPI-fastkit
   ```
   </div>

2. **Comprueba tu entorno virtual**:

   <div class="termy">
   ```console
   $ which python
   $ which pip
   ```
   </div>

3. **Reinstala FastAPI-fastkit**:

   <div class="termy">
   ```console
   $ pip uninstall FastAPI-fastkit
   $ pip install FastAPI-fastkit
   ```
   </div>

### Errores de permisos

Si encuentras errores de permisos durante la instalación:

**En Linux/macOS:**

<div class="termy">

```console
$ pip install --user FastAPI-fastkit
```

</div>

**En Windows (ejecutar como administrador):**

<div class="termy">

```console
$ pip install FastAPI-fastkit
```

</div>

### Compatibilidad de versión de Python

FastAPI-fastkit requiere Python 3.12+. Comprueba tu versión de Python:

<div class="termy">

```console
$ python --version
Python 3.12.0
```

</div>

Si tienes una versión más antigua, actualiza Python:

- **Python oficial**: [python.org/downloads](https://www.python.org/downloads/)
- **Con pyenv**: `pyenv install 3.12.0`
- **Con conda**: `conda install python=3.12`

## Próximos pasos

Una vez completada la instalación:

1. **[Inicio rápido](quick-start.md)**: Crea tu primer proyecto en 5 minutos
2. **[Tutorial inicial](../tutorial/getting-started.md)**: Tutorial paso a paso detallado
3. **[Referencia de la CLI](cli-reference.md)**: Referencia completa de comandos

!!! tip "Consejos de instalación"
    - Usa siempre entornos virtuales para aislar los proyectos
    - Mantén FastAPI-fastkit actualizado a la última versión
    - Revisa el [repositorio de GitHub](https://github.com/bnbong/FastAPI-fastkit) para actualizaciones e incidencias
