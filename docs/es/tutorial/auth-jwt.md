# Autenticación JWT con `fastapi-auth-jwt`

Construye una API con cuentas reales desde el primer commit. Este tutorial
recorre la plantilla `fastapi-auth-jwt` de principio a fin: cómo se emiten y
rotan los pares de tokens, por qué se rechaza un refresh token reutilizado,
cómo se conectan los guards de roles y scopes, y qué cambia cuando dejas
SQLite.

## Qué vas a aprender

- Generar un proyecto con `fastkit startdemo fastapi-auth-jwt`
- La diferencia entre el access token y el refresh token, y por qué importa
  la rotación
- Cómo `get_current_user`, `get_current_active_superuser` y
  `require_scopes(...)` protegen una ruta
- Dónde se hace el hash de contraseñas y por qué se usa argon2id
- Pasar del archivo SQLite incluido a PostgreSQL con Alembic

## Requisitos previos

- Python 3.12+
- FastAPI-fastkit instalado (`pip install fastapi-fastkit`)
- Soltura con las dependencias de FastAPI y los esquemas pydantic

Si nunca has construido una app FastAPI, empieza por
[Construir un servidor API básico](basic-api-server.md) y vuelve después —
esta plantilla da por sabidos los conceptos básicos.

## Paso 1: Generar el proyecto

```console
$ fastkit startdemo fastapi-auth-jwt
Enter the project name: accounts-api
Enter the author name: Developer Kim
Enter the author email: developer@example.com
Enter the project description: Accounts and sessions service
Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y
```

Después, ejecútalo:

```console
$ cd accounts-api
$ bash scripts/run-server.sh    # o: uvicorn src.app.main:app --reload
```

La app arranca sobre SQLite (`sqlite:///./app.db`) y crea sus tablas al
iniciar, así que no hay nada que instalar ni configurar antes. La
documentación está en <http://127.0.0.1:8000/docs>.

!!! tip "Previsualiza antes de comprometerte"
    `fastkit startdemo fastapi-auth-jwt --dry-run` muestra el árbol de archivos
    y la lista de paquetes sin escribir nada — útil para ver qué vas a
    obtener.

## Paso 2: El árbol generado

```
accounts-api/
├── pyproject.toml              # Metadatos PEP 621 + [tool.fastapi-fastkit]
├── requirements.txt
├── alembic.ini
├── Dockerfile
├── .env                        # SECRET_KEY, DATABASE_URL, duración de los tokens
├── scripts/
│   ├── format.sh  lint.sh  run-server.sh  test.sh
├── src/
│   └── app/
│       ├── main.py             # FastAPI() + lifespan + CORS + api_router
│       ├── core/
│       │   ├── config.py       # pydantic-settings
│       │   └── security.py     # hash argon2 + codificación/decodificación JWT
│       ├── db/session.py       # engine + dependencia get_session
│       ├── api/
│       │   ├── router.py       # agrega health + el router de cada dominio
│       │   ├── health.py       # GET /health
│       │   └── deps.py         # sesión, usuario actual, guards de rol/scope
│       ├── domains/
│       │   ├── auth/           # login, rotación de refresh, logout
│       │   └── users/          # registro y perfiles
│       └── alembic/            # entorno de migraciones + versions/
└── tests/
    ├── conftest.py  test_health.py  test_auth.py  test_users.py
```

La estructura es la forma de `domain-starter`: cada dominio tiene su propio
`router.py` (transporte), `service.py` (lógica de negocio), `repository.py`
(acceso a datos), `models.py` (tablas) y `schemas.py` (E/S de la API). Lo
relativo a la autenticación vive en `auth/`, lo relativo a las cuentas en
`users/`, y ninguno de los dos accede a los detalles internos del otro.

## Paso 3: Registrarse, iniciar sesión y llamar a una ruta protegida

```console
# 1. registro
$ curl -X POST http://127.0.0.1:8000/api/v1/auth/register \
    -H 'Content-Type: application/json' \
    -d '{"email": "alice@example.com", "password": "s3cret-password"}'

# 2. inicio de sesión — fíjate en la codificación de formulario: es el flujo de contraseña de OAuth2
$ curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
    -d 'username=alice@example.com&password=s3cret-password'
{"access_token": "...", "refresh_token": "...", "token_type": "bearer"}

# 3. llamar a una ruta protegida
$ curl http://127.0.0.1:8000/api/v1/users/me \
    -H "Authorization: Bearer $ACCESS_TOKEN"
```

El botón "Authorize" de Swagger sigue el mismo flujo, así que puedes probar
las rutas protegidas desde `/docs` sin salir del navegador.

La superficie completa:

| Método | Endpoint                    | Auth        | Descripción                              |
|--------|-----------------------------|-------------|------------------------------------------|
| GET    | `/api/v1/health`            | —           | Probe de liveness                        |
| POST   | `/api/v1/auth/register`     | —           | Crear una cuenta                         |
| POST   | `/api/v1/auth/login`        | —           | Formulario de contraseña OAuth2 → par de tokens |
| POST   | `/api/v1/auth/refresh`      | refresh tok | Rotar a un par de tokens nuevo           |
| POST   | `/api/v1/auth/logout`       | refresh tok | Revocar un refresh token                 |
| POST   | `/api/v1/auth/logout-all`   | access tok  | Revocar todas las sesiones del usuario   |
| GET    | `/api/v1/users/me`          | access tok  | Perfil del usuario actual                |
| PATCH  | `/api/v1/users/me`          | access tok  | Actualizar el perfil del usuario actual  |
| GET    | `/api/v1/users/me/scopes`   | scope `me`  | Ruta de ejemplo protegida por scope      |
| GET    | `/api/v1/users`             | superuser   | Listado de usuarios protegido por rol    |

## Paso 4: Dos tokens, y por qué

Un inicio de sesión devuelve un **par**:

- El **access token** es de corta duración (`ACCESS_TOKEN_EXPIRE_MINUTES`,
  30 por defecto) y viaja en cada petición. Como dura poco, uno que se
  filtre deja de funcionar enseguida.
- El **refresh token** es de larga duración (`REFRESH_TOKEN_EXPIRE_DAYS`, 14
  por defecto) y sirve exactamente para una cosa: obtener un par nuevo.

Nada de lo anterior es inusual. Lo que distingue a esta plantilla del
fragmento JWT típico es que los refresh tokens se **registran y rotan**.
Cada refresh token emitido recibe un claim `jti`, y ese `jti` se guarda en
la base de datos:

```python
def issue_token_pair(self, user: User) -> TokenPair:
    scopes = user.scope_list
    access_token, _, _ = create_access_token(str(user.id), scopes)
    refresh_token, jti, expires_at = create_refresh_token(str(user.id), scopes)
    self.refresh_tokens.add(jti, user.id or 0, expires_at)
    return TokenPair(access_token=access_token, refresh_token=refresh_token)
```

Al refrescar, el token presentado se revoca **antes** de emitir el par
nuevo:

```python
def rotate(self, refresh_token: str) -> TokenPair:
    payload = decode_token(refresh_token, REFRESH_TOKEN_TYPE)
    record = self.refresh_tokens.get_by_jti(str(payload.get("jti")))
    if record is None or record.revoked:
        raise TokenError("refresh token is no longer valid")
    ...
    self.refresh_tokens.revoke(record)
    return self.issue_token_pair(user)
```

Pruébalo: refresca una vez y luego vuelve a enviar el refresh token *antiguo*.

```console
$ curl -X POST http://127.0.0.1:8000/api/v1/auth/refresh \
    -H 'Content-Type: application/json' \
    -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}"
# → par nuevo

$ curl -X POST http://127.0.0.1:8000/api/v1/auth/refresh \
    -H 'Content-Type: application/json' \
    -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}"
# → 401: el token dejó de valer en el momento en que se usó
```

Esa única propiedad convierte un refresh token robado, que sería una puerta
trasera permanente, en un fallo detectable de un solo uso.

El logout funciona igual, y es lo otro que las configuraciones JWT simples
no suelen poder hacer: `POST /auth/logout` revoca un token y
`POST /auth/logout-all` revoca todos los refresh tokens del usuario.

## Paso 5: Contraseñas

El hash vive en `src/app/core/security.py` y pasa por `pwdlib` con
**argon2id** — el valor por defecto recomendado actualmente, no una
configuración heredada de bcrypt. Ningún router ni service ve nunca una
contraseña en texto plano más allá del momento en que se verifica, y
`hashed_password` nunca forma parte de un esquema de respuesta.

Aquí no tienes que configurar nada. Lo único que *sí* debes configurar es la
clave de firma.

## Paso 6: Roles y scopes

Se incluyen tres guards como dependencias de FastAPI:

```python
CurrentUser = Annotated[User, Depends(get_current_user)]
```

- **`get_current_user`** decodifica el access token bearer, carga el usuario
  y rechaza las cuentas inactivas con `403`. Cualquier token malformado,
  caducado o que apunte a un usuario eliminado devuelve `401`.
- **`get_current_active_superuser`** añade encima una comprobación de
  `is_superuser`. `GET /api/v1/users` la usa.
- **`require_scopes(...)`** construye una dependencia que exige scopes
  concretos:

```python
from fastapi import Depends
from src.app.api.deps import require_scopes

@router.get("/reports", dependencies=[Depends(require_scopes("reports"))])
def read_reports() -> list[str]:
    ...
```

Los scopes se guardan en la fila del usuario como una cadena separada por
comas (`scopes: str`, leída a través de la propiedad `scope_list`) y se
copian en cada token emitido. Es, a propósito, lo más simple que funciona
para un starter; cuando tu modelo de permisos se quede pequeño para una
cadena, sustituye la columna por una tabla de roles y mantén sin cambios las
firmas de las dependencias — no hay que mover nada en los routers.

## Paso 7: Añadir un dominio protegido

Para añadir, por ejemplo, un dominio `orders` al que solo puedan acceder los
usuarios autenticados:

1. Crea `src/app/domains/orders/` imitando `users/`
   (`models.py`, `schemas.py`, `repository.py`, `service.py`, `router.py`).
2. Recibe `CurrentUser` como parámetro en las rutas que necesitan una
   cuenta, o añade `Depends(require_scopes("orders"))` al router.
3. Registra el router en `src/app/api/router.py`, encima del ancla
   `# fastkit:routes`. `fastkit addroute` escribe en esas mismas anclas, así
   que las rutas escritas a mano y las generadas quedan en un mismo sitio.
4. Genera una migración: `alembic revision --autogenerate -m "add orders"`.
5. Replica `tests/test_users.py` para los nuevos endpoints.

## Paso 8: SQLite ahora, PostgreSQL después

El `DATABASE_URL` por defecto es un archivo SQLite local y la app llama a
`create_db_and_tables()` al arrancar; por eso tanto `pytest` como `uvicorn`
funcionan sin ninguna preparación. Para cualquier cosa más allá del
desarrollo local, deja que Alembic se encargue del esquema:

```console
$ export DATABASE_URL='postgresql+psycopg://postgres:postgres@localhost:5432/app_db'
$ alembic upgrade head
```

Después de un cambio en los modelos:

```console
$ alembic revision --autogenerate -m "add profile fields"
```

## Paso 9: Antes de desplegar

Dos ajustes de `.env` deciden si esto es una demo o un servicio real:

- **`SECRET_KEY`** firma cada token. Si no lo defines, se genera una clave
  aleatoria por proceso — lo que cierra la sesión de todo el mundo en cada
  reinicio y hace que varios workers discrepen sobre qué tokens son válidos.
  Genera una y fíjala:

  ```console
  $ python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```

- **`DATABASE_URL`** selecciona la base de datos. El SQLite por defecto no
  es un almacenamiento de producción.

Opcionalmente, define `FIRST_SUPERUSER_EMAIL` y `FIRST_SUPERUSER_PASSWORD`
para que se cree un superusuario al arrancar, y `BACKEND_CORS_ORIGINS` con
una lista separada por comas de orígenes del front-end.

## Paso 10: Los tests

```console
$ bash scripts/test.sh    # o: pytest
```

La suite ejecuta `httpx.AsyncClient` contra una base de datos SQLite en
memoria y cubre todo el camino feliz — registro → login → me → refresh →
logout — además de las rutas de rechazo que de verdad importan: contraseña
incorrecta, token malformado, token caducado y el refresh token reutilizado
del Paso 4. Cuando amplíes las reglas de autenticación, amplía primero esos
tests de rechazo; son los que detectan un guard roto.

## Resumen

- **Generación**: `fastkit startdemo fastapi-auth-jwt` →
  `bash scripts/run-server.sh` → documentación en `/docs`.
- **Tokens**: access token de corta duración para las peticiones y refresh
  token rotatorio registrado por `jti`, de modo que las reutilizaciones
  fallan y el logout es real.
- **Guards**: `get_current_user`, `get_current_active_superuser` y
  `require_scopes(...)` como dependencias normales.
- **Almacenamiento**: SQLite sin coste, PostgreSQL definiendo `DATABASE_URL`
  y ejecutando `alembic upgrade head`.
- **Antes de desplegar**: fija `SECRET_KEY` y apunta `DATABASE_URL` a una
  base de datos real.

## Siguientes pasos

- [Persistencia con SQLModel](sqlmodel.md) — la misma estructura de dominios
  centrada en el acceso asíncrono a datos, las migraciones y el CRUD
  genérico.
- [Proyecto orientado a dominios](domain-starter.md) — la estructura sobre la
  que se construye esta plantilla, sin la maquinaria de autenticación.
- [¿Qué starter elegir?](../user-guide/choosing-a-starter.md) —
  cómo se compara esta plantilla con las demás.
