# Inicio rápido

¡Crea tu primer proyecto FastAPI con FastAPI-fastkit en menos de 5 minutos!

!!! tip "¿No sabes qué starter elegir?"
    Mira [**¿Qué starter elegir?**](choosing-a-starter.md) para ver una comparación pensada para principiantes entre las plantillas de `startdemo` y los presets de arquitectura interactivos (`minimal` / `single-module` / `classic-layered` / `domain-starter`). En resumen: **`fastkit init --interactive` con el preset `domain-starter` es la opción moderna recomendada.**

## 1. Crear el proyecto

Usa el comando `init` de FastAPI-fastkit para crear un proyecto nuevo:

<div class="termy">

```console
$ fastkit init
Enter the project name: my-first-app
Enter the author name: Your Name
Enter the author email: your.email@example.com
Enter the project description: My first FastAPI application

           Project Information
┌──────────────┬─────────────────────────────┐
│ Project Name │ my-first-app                │
│ Author       │ Your Name                   │
│ Author Email │ your.email@example.com      │
│ Description  │ My first FastAPI application│
└──────────────┴─────────────────────────────┘

Available Stacks and Dependencies:
           MINIMAL Stack
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ pydantic          │
│ Dependency 4 │ pydantic-settings │
└──────────────┴───────────────────┘

           STANDARD Stack
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ sqlalchemy        │
│ Dependency 4 │ alembic           │
│ Dependency 5 │ pytest            │
│ Dependency 6 │ pydantic          │
│ Dependency 7 │ pydantic-settings │
└──────────────┴───────────────────┘

             FULL Stack
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ sqlalchemy        │
│ Dependency 4 │ alembic           │
│ Dependency 5 │ pytest            │
│ Dependency 6 │ redis             │
│ Dependency 7 │ celery            │
│ Dependency 8 │ pydantic          │
│ Dependency 9 │ pydantic-settings │
└──────────────┴───────────────────┘

Select stack (minimal, standard, full): minimal

Available Package Managers:
                   Package Managers
┌────────┬────────────────────────────────────────────┐
│ PIP    │ Standard Python package manager            │
│ UV     │ Fast Python package manager                │
│ PDM    │ Modern Python dependency management        │
│ POETRY │ Python dependency management and packaging │
└────────┴────────────────────────────────────────────┘

Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y

✨ FastAPI project 'my-first-app' has been created successfully!
```

</div>

## 2. Activar el entorno virtual

Entra en el directorio del proyecto y activa el entorno virtual:

<div class="termy">

```console
$ cd my-first-app
$ source .venv/bin/activate  # Linux/macOS
$ .venv\Scripts\activate     # Windows
```

</div>

## 3. Iniciar el servidor de desarrollo

Arranca el servidor de desarrollo de FastAPI:

<div class="termy">

```console
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [28720]
INFO:     Started server process [28722]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

</div>

!!! success "¡Enhorabuena!"
    ¡Tu servidor FastAPI está en marcha! Ábrelo en el navegador para comprobarlo.

## 4. Probar la API

Abre estas URLs en tu navegador:

### Endpoint principal

Entra en [http://127.0.0.1:8000](http://127.0.0.1:8000) y verás:

```json
{"message": "Hello World"}
```

### Documentación interactiva de la API

Visita [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

Es la documentación **Swagger UI** generada automáticamente, donde puedes:

- Ver todos los endpoints de la API
- Probar endpoints directamente desde el navegador
- Consultar los esquemas de petición / respuesta

### Documentación alternativa

Visita [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc).

Es la interfaz de documentación **ReDoc**, con un diseño distinto y limpio.

## 5. Añadir tu primera ruta

Vamos a añadir una nueva ruta a la API del proyecto:

<div class="termy">

```console
$ fastkit addroute users my-first-app
                       Adding New Route
┌──────────────────┬──────────────────────────────────────────┐
│ Project          │ my-first-app                             │
│ Route Name       │ users                                    │
│ Target Directory │ ~/my-first-app                           │
└──────────────────┴──────────────────────────────────────────┘

Do you want to add route 'users' to project 'my-first-app'? [Y/n]: y

╭──────────────────────── Info ────────────────────────╮
│ ℹ Updated main.py to include the API router          │
╰──────────────────────────────────────────────────────╯
╭─────────────────────── Success ───────────────────────╮
│ ✨ Successfully added new route 'users' to project    │
│ `my-first-app`                                        │
╰───────────────────────────────────────────────────────╯
```

</div>

El servidor se recargará automáticamente y ahora tendrás nuevos endpoints:

- `GET /api/v1/users/` - Obtener todos los usuarios
- `POST /api/v1/users/` - Crear un usuario nuevo
- `GET /api/v1/users/{user_id}` - Obtener un usuario concreto
- `PUT /api/v1/users/{user_id}` - Actualizar un usuario
- `DELETE /api/v1/users/{user_id}` - Eliminar un usuario

## 6. Probar la nueva API

### Con curl

**Obtener todos los usuarios:**

<div class="termy">

```console
$ curl http://127.0.0.1:8000/api/v1/users/
[]
```

</div>

**Crear un usuario nuevo:**

<div class="termy">

```console
$ curl -X POST "http://127.0.0.1:8000/api/v1/users/" \
     -H "Content-Type: application/json" \
     -d '{"title": "John Doe", "description": "Software Developer"}'
{
  "id": 1,
  "title": "John Doe",
  "description": "Software Developer"
}
```

</div>

### Con la documentación interactiva

1. Entra en [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
2. Despliega la sección **"users"**.
3. Pulsa **"POST /api/v1/users/"**.
4. Pulsa **"Try it out"**.
5. Rellena el cuerpo de la petición:
   ```json
   {
     "title": "Jane Smith",
     "description": "Product Manager"
   }
   ```
6. Pulsa **"Execute"**.

## 7. Explorar la estructura del proyecto

El proyecto generado tiene una estructura limpia y ordenada:

```
my-first-app/
├── .venv/                    # Entorno virtual
├── src/
│   ├── __init__.py
│   ├── main.py              # Punto de entrada de la app FastAPI
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py        # Configuración de la app
│   ├── api/
│   │   ├── __init__.py
│   │   ├── api.py          # Conjunto de routers de la API
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── items.py     # Ruta por defecto items
│   │       └── users.py     # Ruta users recién añadida
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── items.py         # Operaciones CRUD para items
│   │   └── users.py         # Operaciones CRUD para users
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── items.py         # Esquemas Pydantic para items
│   │   └── users.py         # Esquemas Pydantic para users
│   └── mocks/
│       ├── __init__.py
│       └── mock_items.json  # Datos de prueba
├── tests/                   # Archivos de pruebas
├── scripts/                 # Scripts de utilidades
├── requirements.txt         # Dependencias de Python
├── setup.py                # Configuración del paquete
└── README.md               # Documentación del proyecto
```

## 8. Opciones de gestor de paquetes

FastAPI-fastkit soporta varios gestores de paquetes de Python a tu gusto:

### Gestores disponibles

| Gestor | Descripción | Recomendado para |
|---|---|---|
| **UV** | Gestor rápido de paquetes Python (por defecto) | Velocidad y rendimiento |
| **PDM** | Gestión moderna de dependencias Python | Resolución avanzada de dependencias |
| **Poetry** | Gestión de dependencias y empaquetado Python | Flujos basados en Poetry |
| **PIP** | Gestor estándar de paquetes Python | Desarrollo tradicional en Python |

### Especificar el gestor de paquetes

Puedes especificar tu gestor preferido de varias maneras:

#### 1. Selección interactiva (por defecto)

Al ejecutar `fastkit init` o `fastkit startdemo` aparece un prompt:

<div class="termy">

```console
$ fastkit init
# ... tras la info del proyecto y la selección de stack ...

Available Package Managers:
                   Package Managers
┌────────┬────────────────────────────────────────────┐
│ PIP    │ Standard Python package manager            │
│ UV     │ Fast Python package manager                │
│ PDM    │ Modern Python dependency management        │
│ POETRY │ Python dependency management and packaging │
└────────┴────────────────────────────────────────────┘

Select package manager (pip, uv, pdm, poetry) [uv]: uv
```

</div>

#### 2. Opción de línea de comandos

Sáltate el prompt interactivo indicando el gestor directamente:

<div class="termy">

```console
$ fastkit init --package-manager poetry
$ fastkit startdemo --package-manager pdm
```

</div>

### Archivos de dependencias generados

Cada gestor genera los archivos de dependencias adecuados:

- **UV/PDM**: `pyproject.toml` (formato PEP 621)
- **Poetry**: `pyproject.toml` (formato Poetry)
- **PIP**: `requirements.txt`

## 9. Próximos pasos

¡Enhorabuena! Has conseguido todo lo siguiente:

✅ Crear tu primer proyecto FastAPI
✅ Arrancar el servidor de desarrollo
✅ Añadir una ruta nueva a la API
✅ Probar la API

### Seguir aprendiendo

1. **[Tu primer proyecto](../tutorial/first-project.md)**: Construye una API de blog más completa
2. **[Crear proyectos](creating-projects.md)**: Aprende los distintos stacks y opciones
3. **[Añadir rutas](adding-routes.md)**: Domina el desarrollo de la API
4. **[Usar plantillas](using-templates.md)**: Explora plantillas de proyecto ya preparadas

### Experimenta un poco más

Prueba estos comandos para explorar más funcionalidades:

<div class="termy">

```console
# Listar las plantillas disponibles
$ fastkit list-templates

# Crear un proyecto desde una plantilla
$ fastkit startdemo

# Añadir más rutas (nombre de la ruta primero, directorio del proyecto después)
$ fastkit addroute products my-first-app
$ fastkit addroute orders my-first-app
```

</div>

!!! tip "Consejos de desarrollo"
    - El servidor se reinicia automáticamente cuando cambias archivos
    - Comprueba la documentación interactiva en `/docs` cada vez que añadas algo nuevo
    - Usa el entorno virtual para mantener aisladas las dependencias
    - Lee el código generado para entender la estructura del proyecto
