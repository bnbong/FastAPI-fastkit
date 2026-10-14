# JWT-Authentifizierung mit `fastapi-auth-jwt`

Bauen Sie eine API, die vom ersten Commit an echte Konten hat. Dieses Tutorial führt Sie vollständig durch die Vorlage `fastapi-auth-jwt`: wie Token-Paare ausgestellt und rotiert werden, warum ein erneut eingespielter Refresh-Token abgelehnt wird, wie die Rollen- und Scope-Guards verdrahtet sind und was sich ändert, wenn Sie SQLite hinter sich lassen.

## Was Sie lernen werden

- Ein Projekt mit `fastkit startdemo fastapi-auth-jwt` generieren
- Den Unterschied zwischen Access-Token und Refresh-Token und warum Rotation wichtig ist
- Wie `get_current_user`, `get_current_active_superuser` und `require_scopes(...)` eine Route schützen
- Wo das Passwort-Hashing stattfindet und warum es argon2id ist
- Von der mitgelieferten SQLite-Datei mit Alembic zu PostgreSQL wechseln

## Voraussetzungen

- Python 3.12+
- FastAPI-fastkit installiert (`pip install fastapi-fastkit`)
- Sicherer Umgang mit FastAPI-Dependencies und Pydantic-Schemas

Wenn Sie noch nie eine FastAPI-App gebaut haben, beginnen Sie mit [Einen einfachen API-Server bauen](basic-api-server.md) und kehren Sie dann zurück — diese Vorlage setzt die Grundlagen voraus.

## Schritt 1: Das Projekt generieren

```console
$ fastkit startdemo fastapi-auth-jwt
Enter the project name: accounts-api
Enter the author name: Developer Kim
Enter the author email: developer@example.com
Enter the project description: Accounts and sessions service
Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y
```

Starten Sie es anschließend:

```console
$ cd accounts-api
$ bash scripts/run-server.sh    # or: uvicorn src.app.main:app --reload
```

Die App startet mit SQLite (`sqlite:///./app.db`) und legt ihre Tabellen beim Start an, sodass Sie vorher nichts installieren oder konfigurieren müssen. Die Dokumentation finden Sie unter <http://127.0.0.1:8000/docs>.

!!! tip "Vorschau vor dem Festlegen"
    `fastkit startdemo fastapi-auth-jwt --dry-run` gibt den Dateibaum und die Paketliste aus, ohne etwas zu schreiben — praktisch, um zu sehen, was Sie gleich bekommen.

## Schritt 2: Der generierte Baum

```
accounts-api/
├── pyproject.toml              # PEP 621 metadata + [tool.fastapi-fastkit]
├── requirements.txt
├── alembic.ini
├── Dockerfile
├── .env                        # SECRET_KEY, DATABASE_URL, token lifetimes
├── scripts/
│   ├── format.sh  lint.sh  run-server.sh  test.sh
├── src/
│   └── app/
│       ├── main.py             # FastAPI() + lifespan + CORS + api_router
│       ├── core/
│       │   ├── config.py       # pydantic-settings
│       │   └── security.py     # argon2 hashing + JWT encode/decode
│       ├── db/session.py       # engine + get_session dependency
│       ├── api/
│       │   ├── router.py       # aggregates health + every domain router
│       │   ├── health.py       # GET /health
│       │   └── deps.py         # session, current user, role/scope guards
│       ├── domains/
│       │   ├── auth/           # login, refresh rotation, logout
│       │   └── users/          # registration and profiles
│       └── alembic/            # migration environment + versions/
└── tests/
    ├── conftest.py  test_health.py  test_auth.py  test_users.py
```

Das Layout folgt der Form von `domain-starter`: Jede Domäne besitzt ihre eigene `router.py` (Transport), `service.py` (Geschäftslogik), `repository.py` (Datenzugriff), `models.py` (Tabellen) und `schemas.py` (API-Ein-/Ausgabe). Authentifizierungsbelange liegen in `auth/`, Kontobelange in `users/`, und keine der beiden Domänen greift auf die Interna der anderen zu.

## Schritt 3: Registrieren, anmelden, eine geschützte Route aufrufen

```console
# 1. register
$ curl -X POST http://127.0.0.1:8000/api/v1/auth/register \
    -H 'Content-Type: application/json' \
    -d '{"email": "alice@example.com", "password": "s3cret-password"}'

# 2. log in — note the form encoding: this is the OAuth2 password flow
$ curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
    -d 'username=alice@example.com&password=s3cret-password'
{"access_token": "...", "refresh_token": "...", "token_type": "bearer"}

# 3. call a protected route
$ curl http://127.0.0.1:8000/api/v1/users/me \
    -H "Authorization: Bearer $ACCESS_TOKEN"
```

Die Schaltfläche „Authorize“ in Swagger steuert denselben Ablauf, sodass Sie geschützte Routen direkt aus `/docs` heraus ausprobieren können, ohne den Browser zu verlassen.

Die vollständige Oberfläche:

| Methode | Endpunkt                    | Auth          | Beschreibung                               |
|---------|-----------------------------|---------------|--------------------------------------------|
| GET     | `/api/v1/health`            | —             | Liveness-Probe                             |
| POST    | `/api/v1/auth/register`     | —             | Ein Konto anlegen                          |
| POST    | `/api/v1/auth/login`        | —             | OAuth2-Passwortformular → Token-Paar       |
| POST    | `/api/v1/auth/refresh`      | Refresh-Token | In ein neues Token-Paar rotieren           |
| POST    | `/api/v1/auth/logout`       | Refresh-Token | Einen Refresh-Token widerrufen             |
| POST    | `/api/v1/auth/logout-all`   | Access-Token  | Alle Sitzungen des Benutzers widerrufen    |
| GET     | `/api/v1/users/me`          | Access-Token  | Profil des aktuellen Benutzers             |
| PATCH   | `/api/v1/users/me`          | Access-Token  | Profil des aktuellen Benutzers aktualisieren |
| GET     | `/api/v1/users/me/scopes`   | Scope `me`    | Beispielroute mit Scope-Prüfung            |
| GET     | `/api/v1/users`             | Superuser     | Benutzerliste mit Rollenprüfung            |

## Schritt 4: Zwei Tokens, und warum

Eine Anmeldung liefert ein **Paar** zurück:

- Der **Access-Token** ist kurzlebig (`ACCESS_TOKEN_EXPIRE_MINUTES`, standardmäßig 30) und wird bei jeder Anfrage mitgeschickt. Weil er kurzlebig ist, wird ein geleakter Token schnell unbrauchbar.
- Der **Refresh-Token** ist langlebig (`REFRESH_TOKEN_EXPIRE_DAYS`, standardmäßig 14) und dient genau einem Zweck: ein neues Paar zu erhalten.

Bis hierhin ist nichts ungewöhnlich. Was diese Vorlage von einem durchschnittlichen JWT-Snippet unterscheidet, ist, dass Refresh-Tokens **erfasst und rotiert** werden. Jeder ausgestellte Refresh-Token erhält einen `jti`-Claim, und dieser `jti` wird in die Datenbank geschrieben:

```python
def issue_token_pair(self, user: User) -> TokenPair:
    scopes = user.scope_list
    access_token, _, _ = create_access_token(str(user.id), scopes)
    refresh_token, jti, expires_at = create_refresh_token(str(user.id), scopes)
    self.refresh_tokens.add(jti, user.id or 0, expires_at)
    return TokenPair(access_token=access_token, refresh_token=refresh_token)
```

Beim Refresh wird der vorgelegte Token widerrufen, **bevor** das neue Paar ausgestellt wird:

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

Probieren Sie es aus: Führen Sie einmal einen Refresh durch und senden Sie dann den *alten* Refresh-Token erneut.

```console
$ curl -X POST http://127.0.0.1:8000/api/v1/auth/refresh \
    -H 'Content-Type: application/json' \
    -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}"
# → new pair

$ curl -X POST http://127.0.0.1:8000/api/v1/auth/refresh \
    -H 'Content-Type: application/json' \
    -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}"
# → 401: the token died the moment it was used
```

Genau diese eine Eigenschaft macht aus einem gestohlenen Refresh-Token statt einer dauerhaften Hintertür einen erkennbaren, einmaligen Fehlschlag.

Logout funktioniert auf dieselbe Weise, und das ist die andere Sache, die einfache JWT-Setups normalerweise nicht können: `POST /auth/logout` widerruft einen Token, `POST /auth/logout-all` widerruft alle Refresh-Tokens des Benutzers.

## Schritt 5: Passwörter

Das Hashing liegt in `src/app/core/security.py` und läuft über `pwdlib` mit **argon2id** — dem aktuell empfohlenen Standard, nicht einer veralteten bcrypt-Konfiguration. Nichts in den Routern oder Services sieht jemals ein Klartext-Passwort über den Moment der Verifikation hinaus, und `hashed_password` ist nie Teil eines Antwort-Schemas.

Hier müssen Sie nichts konfigurieren. Das Einzige, was Sie konfigurieren *müssen*, ist der Signaturschlüssel.

## Schritt 6: Rollen und Scopes

Drei Guards werden als FastAPI-Dependencies mitgeliefert:

```python
CurrentUser = Annotated[User, Depends(get_current_user)]
```

- **`get_current_user`** dekodiert den Bearer-Access-Token, lädt den Benutzer und weist inaktive Konten mit `403` ab. Alles, was fehlerhaft oder abgelaufen ist oder auf einen gelöschten Benutzer verweist, wird mit `401` beantwortet.
- **`get_current_active_superuser`** legt eine `is_superuser`-Prüfung darüber. `GET /api/v1/users` verwendet ihn.
- **`require_scopes(...)`** erzeugt eine Dependency, die bestimmte Scopes verlangt:

```python
from fastapi import Depends
from src.app.api.deps import require_scopes

@router.get("/reports", dependencies=[Depends(require_scopes("reports"))])
def read_reports() -> list[str]:
    ...
```

Scopes liegen in der Benutzerzeile als kommagetrennter String (`scopes: str`, ausgelesen über die Property `scope_list`) und werden in jeden ausgestellten Token kopiert. Das ist bewusst die einfachste Lösung, die für einen Starter funktioniert. Wenn Ihr Berechtigungsmodell einem String entwächst, ersetzen Sie die Spalte durch eine Rollentabelle und lassen die Signaturen der Dependencies unverändert — in den Routern muss nichts verschoben werden.

## Schritt 7: Eine geschützte Domäne hinzufügen

Um zum Beispiel eine `orders`-Domäne hinzuzufügen, die nur angemeldete Benutzer erreichen können:

1. Legen Sie `src/app/domains/orders/` nach dem Vorbild von `users/` an (`models.py`, `schemas.py`, `repository.py`, `service.py`, `router.py`).
2. Nehmen Sie `CurrentUser` als Parameter in die Routen auf, die ein Konto benötigen, oder hängen Sie `Depends(require_scopes("orders"))` an den Router.
3. Registrieren Sie den Router in `src/app/api/router.py` oberhalb des Ankers `# fastkit:routes`. `fastkit addroute` schreibt in dieselben Anker, sodass handgeschriebene und generierte Routen an einer Stelle bleiben.
4. Generieren Sie eine Migration: `alembic revision --autogenerate -m "add orders"`.
5. Bilden Sie `tests/test_users.py` für die neuen Endpunkte nach.

## Schritt 8: Jetzt SQLite, später PostgreSQL

Die Standard-`DATABASE_URL` ist eine lokale SQLite-Datei, und die App ruft beim Start `create_db_and_tables()` auf. Deshalb funktionieren `pytest` und `uvicorn` ohne jede Einrichtung. Für alles über die lokale Entwicklung hinaus sollten Sie stattdessen Alembic das Schema verwalten lassen:

```console
$ export DATABASE_URL='postgresql+psycopg://postgres:postgres@localhost:5432/app_db'
$ alembic upgrade head
```

Nach einer Modelländerung:

```console
$ alembic revision --autogenerate -m "add profile fields"
```

## Schritt 9: Vor dem Deployment

Zwei Einstellungen in `.env` entscheiden, ob dies eine Demo oder ein echter Dienst ist:

- **`SECRET_KEY`** signiert jeden Token. Bleibt er ungesetzt, wird pro Prozess ein zufälliger Schlüssel erzeugt — das meldet bei jedem Neustart alle Benutzer ab und führt dazu, dass mehrere Worker sich uneinig sind, welche Tokens gültig sind. Erzeugen Sie einen Schlüssel und legen Sie ihn fest:

  ```console
  $ python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```

- **`DATABASE_URL`** wählt die Datenbank aus. Der SQLite-Standard ist kein Produktionsspeicher.

Optional können Sie `FIRST_SUPERUSER_EMAIL` und `FIRST_SUPERUSER_PASSWORD` setzen, damit beim Start ein Superuser angelegt wird, und `BACKEND_CORS_ORIGINS` auf eine kommagetrennte Liste von Frontend-Origins setzen.

## Schritt 10: Die Tests

```console
$ bash scripts/test.sh    # or: pytest
```

Die Testsuite führt `httpx.AsyncClient` gegen eine In-Memory-SQLite-Datenbank aus und deckt den gesamten Erfolgspfad ab — register → login → me → refresh → logout — sowie die Ablehnungspfade, auf die es wirklich ankommt: falsches Passwort, fehlerhafter Token, abgelaufener Token und der erneut eingespielte Refresh-Token aus Schritt 4. Wenn Sie die Authentifizierungsregeln erweitern, erweitern Sie zuerst diese Ablehnungstests; sie sind es, die einen kaputten Guard aufdecken.

## Rückblick

- **Generierung**: `fastkit startdemo fastapi-auth-jwt` → `bash scripts/run-server.sh` → Dokumentation unter `/docs`.
- **Tokens**: kurzlebiger Access-Token für Anfragen, rotierender Refresh-Token, der über `jti` erfasst wird, sodass Wiederholungen fehlschlagen und Logout tatsächlich wirkt.
- **Guards**: `get_current_user`, `get_current_active_superuser` und `require_scopes(...)` als einfache Dependencies.
- **Speicherung**: SQLite ohne Aufwand, PostgreSQL durch Setzen von `DATABASE_URL` und Ausführen von `alembic upgrade head`.
- **Vor dem Deployment**: `SECRET_KEY` festlegen und `DATABASE_URL` auf eine echte Datenbank zeigen lassen.

## Wie es weitergeht

- [SQLModel-Persistenz](sqlmodel.md) — dasselbe Domänen-Layout mit Fokus auf asynchronem Datenzugriff, Migrationen und generischem CRUD.
- [Domänenorientiertes Projekt](domain-starter.md) — das Layout, auf dem diese Vorlage aufbaut, ohne die Authentifizierungsmechanik.
- [Welchen Starter soll ich wählen?](../user-guide/choosing-a-starter.md) — wie sich diese Vorlage mit den übrigen vergleicht.
