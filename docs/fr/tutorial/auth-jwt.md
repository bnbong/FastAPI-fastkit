# Authentification JWT avec `fastapi-auth-jwt`

Construisez une API dotée de véritables comptes dès le premier commit. Ce tutoriel parcourt le modèle `fastapi-auth-jwt` de bout en bout : comment les paires de jetons sont émises et renouvelées par rotation, pourquoi un jeton de rafraîchissement rejoué est refusé, comment les gardes de rôle et de portée (scope) sont câblées, et ce qui change lorsque vous quittez SQLite.

## Ce que vous apprendrez

- Générer un projet avec `fastkit startdemo fastapi-auth-jwt`
- La différence entre le jeton d'accès et le jeton de rafraîchissement, et pourquoi la rotation est importante
- Comment `get_current_user`, `get_current_active_superuser` et `require_scopes(...)` protègent une route
- Où a lieu le hachage des mots de passe et pourquoi il repose sur argon2id
- Passer du fichier SQLite fourni à PostgreSQL avec Alembic

## Prérequis

- Python 3.12+
- FastAPI-fastkit installé (`pip install fastapi-fastkit`)
- À l'aise avec les dépendances FastAPI et les schémas pydantic

Si vous n'avez encore jamais construit d'application FastAPI, commencez par [Construire un serveur d'API basique](basic-api-server.md) puis revenez ici — ce modèle suppose les bases acquises.

## Étape 1 : Générer le projet

```console
$ fastkit startdemo fastapi-auth-jwt
Enter the project name: accounts-api
Enter the author name: Developer Kim
Enter the author email: developer@example.com
Enter the project description: Accounts and sessions service
Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y
```

Lancez-le ensuite :

```console
$ cd accounts-api
$ bash scripts/run-server.sh    # or: uvicorn src.app.main:app --reload
```

L'application démarre sur SQLite (`sqlite:///./app.db`) et crée ses tables au démarrage : il n'y a donc rien à installer ni à configurer au préalable. La documentation est disponible à <http://127.0.0.1:8000/docs>.

!!! tip "Prévisualiser avant de vous engager"
    `fastkit startdemo fastapi-auth-jwt --dry-run` affiche l'arborescence des fichiers et la liste des paquets sans rien écrire — pratique pour voir ce que vous allez obtenir.

## Étape 2 : L'arborescence générée

```
accounts-api/
├── pyproject.toml              # métadonnées PEP 621 + [tool.fastapi-fastkit]
├── requirements.txt
├── alembic.ini
├── Dockerfile
├── .env                        # SECRET_KEY, DATABASE_URL, durées de vie des jetons
├── scripts/
│   ├── format.sh  lint.sh  run-server.sh  test.sh
├── src/
│   └── app/
│       ├── main.py             # FastAPI() + lifespan + CORS + api_router
│       ├── core/
│       │   ├── config.py       # pydantic-settings
│       │   └── security.py     # hachage argon2 + encodage/décodage JWT
│       ├── db/session.py       # moteur + dépendance get_session
│       ├── api/
│       │   ├── router.py       # regroupe la santé et tous les routeurs de domaine
│       │   ├── health.py       # GET /health
│       │   └── deps.py         # session, utilisateur courant, gardes de rôle/portée
│       ├── domains/
│       │   ├── auth/           # connexion, rotation du rafraîchissement, déconnexion
│       │   └── users/          # inscription et profils
│       └── alembic/            # environnement de migration + versions/
└── tests/
    ├── conftest.py  test_health.py  test_auth.py  test_users.py
```

La disposition reprend la forme de `domain-starter` : chaque domaine possède son `router.py` (transport), son `service.py` (logique métier), son `repository.py` (accès aux données), son `models.py` (tables) et son `schemas.py` (entrées/sorties de l'API). Les préoccupations d'authentification vivent dans `auth/`, celles des comptes dans `users/`, et aucun des deux ne touche aux éléments internes de l'autre.

## Étape 3 : S'inscrire, se connecter, appeler une route protégée

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

Le bouton « Authorize » de Swagger pilote le même flux : vous pouvez donc exercer les routes protégées depuis `/docs` sans quitter le navigateur.

L'ensemble des points d'extrémité :

| Méthode | Point d'extrémité           | Auth        | Description                                  |
|---------|-----------------------------|-------------|----------------------------------------------|
| GET     | `/api/v1/health`            | —           | Sonde de vivacité                            |
| POST    | `/api/v1/auth/register`     | —           | Créer un compte                              |
| POST    | `/api/v1/auth/login`        | —           | Formulaire de mot de passe OAuth2 → paire de jetons |
| POST    | `/api/v1/auth/refresh`      | refresh tok | Rotation vers une nouvelle paire de jetons   |
| POST    | `/api/v1/auth/logout`       | refresh tok | Révoquer un jeton de rafraîchissement        |
| POST    | `/api/v1/auth/logout-all`   | access tok  | Révoquer toutes les sessions de l'utilisateur |
| GET     | `/api/v1/users/me`          | access tok  | Profil de l'utilisateur courant              |
| PATCH   | `/api/v1/users/me`          | access tok  | Mettre à jour le profil de l'utilisateur courant |
| GET     | `/api/v1/users/me/scopes`   | scope `me`  | Route d'exemple conditionnée par une portée  |
| GET     | `/api/v1/users`             | superuser   | Liste des utilisateurs conditionnée par un rôle |

## Étape 4 : Deux jetons, et pourquoi

Une connexion renvoie une **paire** :

- Le **jeton d'accès** a une durée de vie courte (`ACCESS_TOKEN_EXPIRE_MINUTES`, 30 par défaut) et accompagne chaque requête. Comme sa durée de vie est courte, un jeton divulgué cesse rapidement de fonctionner.
- Le **jeton de rafraîchissement** a une durée de vie longue (`REFRESH_TOKEN_EXPIRE_DAYS`, 14 par défaut) et ne sert qu'à une seule chose : obtenir une nouvelle paire.

Rien de tout cela n'est inhabituel. Ce qui distingue ce modèle de l'extrait JWT moyen, c'est que les jetons de rafraîchissement sont **suivis et renouvelés par rotation**. Chaque jeton de rafraîchissement émis reçoit une revendication `jti`, et ce `jti` est écrit en base de données :

```python
def issue_token_pair(self, user: User) -> TokenPair:
    scopes = user.scope_list
    access_token, _, _ = create_access_token(str(user.id), scopes)
    refresh_token, jti, expires_at = create_refresh_token(str(user.id), scopes)
    self.refresh_tokens.add(jti, user.id or 0, expires_at)
    return TokenPair(access_token=access_token, refresh_token=refresh_token)
```

Lors d'un rafraîchissement, le jeton présenté est révoqué **avant** l'émission de la nouvelle paire :

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

Essayez : rafraîchissez une fois, puis renvoyez l'*ancien* jeton de rafraîchissement.

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

C'est cette seule propriété qui transforme un jeton de rafraîchissement volé, porte dérobée permanente, en un échec détectable et à usage unique.

La déconnexion fonctionne de la même manière, ce qui est l'autre chose que les configurations JWT classiques ne savent généralement pas faire : `POST /auth/logout` révoque un jeton, `POST /auth/logout-all` révoque tous les jetons de rafraîchissement appartenant à l'utilisateur.

## Étape 5 : Les mots de passe

Le hachage se trouve dans `src/app/core/security.py` et passe par `pwdlib` avec **argon2id** — le choix par défaut recommandé aujourd'hui, et non une ancienne configuration bcrypt. Aucun routeur ni service ne voit jamais un mot de passe en clair au-delà de l'instant où il est vérifié, et `hashed_password` ne fait jamais partie d'un schéma de réponse.

Vous n'avez rien à configurer ici. La seule chose que vous *devez* configurer est la clé de signature.

## Étape 6 : Rôles et portées

Trois gardes sont fournies sous forme de dépendances FastAPI :

```python
CurrentUser = Annotated[User, Depends(get_current_user)]
```

- **`get_current_user`** décode le jeton d'accès bearer, charge l'utilisateur et rejette les comptes inactifs avec `403`. Tout jeton malformé, expiré ou pointant vers un utilisateur supprimé renvoie `401`.
- **`get_current_active_superuser`** ajoute par-dessus une vérification `is_superuser`. `GET /api/v1/users` l'utilise.
- **`require_scopes(...)`** construit une dépendance qui exige des portées précises :

```python
from fastapi import Depends
from src.app.api.deps import require_scopes

@router.get("/reports", dependencies=[Depends(require_scopes("reports"))])
def read_reports() -> list[str]:
    ...
```

Les portées sont stockées sur la ligne de l'utilisateur sous forme de chaîne séparée par des virgules (`scopes: str`, relue via la propriété `scope_list`) et sont copiées dans chaque jeton émis. C'est délibérément la solution la plus simple qui fonctionne pour un starter ; lorsque votre modèle de permissions dépasse ce qu'une chaîne peut exprimer, remplacez la colonne par une table de rôles et conservez les signatures des dépendances inchangées — rien n'a besoin de bouger dans les routeurs.

## Étape 7 : Ajouter un domaine protégé

Pour ajouter, par exemple, un domaine `orders` accessible uniquement aux utilisateurs connectés :

1. Créez `src/app/domains/orders/` sur le modèle de `users/` (`models.py`, `schemas.py`, `repository.py`, `service.py`, `router.py`).
2. Prenez `CurrentUser` en paramètre dans les routes qui nécessitent un compte, ou attachez `Depends(require_scopes("orders"))` au routeur.
3. Enregistrez le routeur dans `src/app/api/router.py`, au-dessus de l'ancre `# fastkit:routes`. `fastkit addroute` écrit dans ces mêmes ancres, si bien que les routes écrites à la main et les routes générées restent au même endroit.
4. Générez une migration : `alembic revision --autogenerate -m "add orders"`.
5. Calquez `tests/test_users.py` pour les nouveaux points d'extrémité.

## Étape 8 : SQLite maintenant, PostgreSQL plus tard

La `DATABASE_URL` par défaut est un fichier SQLite local et l'application appelle `create_db_and_tables()` au démarrage : c'est pourquoi `pytest` et `uvicorn` fonctionnent tous deux sans aucune configuration. Pour tout ce qui dépasse le développement local, laissez plutôt Alembic gérer le schéma :

```console
$ export DATABASE_URL='postgresql+psycopg://postgres:postgres@localhost:5432/app_db'
$ alembic upgrade head
```

Après une modification de modèle :

```console
$ alembic revision --autogenerate -m "add profile fields"
```

## Étape 9 : Avant de déployer

Deux paramètres de `.env` décident s'il s'agit d'une démo ou d'un vrai service :

- **`SECRET_KEY`** signe chaque jeton. Si vous la laissez vide, une clé aléatoire est générée pour chaque processus — ce qui déconnecte tout le monde à chaque redémarrage et fait que plusieurs workers ne s'accordent pas sur les jetons valides. Générez-en une et fixez-la :

  ```console
  $ python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```

- **`DATABASE_URL`** sélectionne la base de données. La valeur SQLite par défaut n'est pas un stockage de production.

Vous pouvez aussi définir `FIRST_SUPERUSER_EMAIL` et `FIRST_SUPERUSER_PASSWORD` pour qu'un superutilisateur soit créé au démarrage, et `BACKEND_CORS_ORIGINS` avec une liste d'origines front-end séparées par des virgules.

## Étape 10 : Les tests

```console
$ bash scripts/test.sh    # or: pytest
```

La suite exécute `httpx.AsyncClient` contre une base SQLite en mémoire et couvre tout le parcours nominal — inscription → connexion → me → rafraîchissement → déconnexion — ainsi que les chemins de rejet qui comptent vraiment : mauvais mot de passe, jeton malformé, jeton expiré, et le jeton de rafraîchissement rejoué de l'étape 4. Lorsque vous étendez les règles d'authentification, étendez d'abord ces tests de rejet ; ce sont eux qui détectent une garde défaillante.

## Récapitulatif

- **Génération** : `fastkit startdemo fastapi-auth-jwt` → `bash scripts/run-server.sh` → documentation à `/docs`.
- **Jetons** : jeton d'accès à courte durée de vie pour les requêtes, jeton de rafraîchissement renouvelé par rotation et suivi par `jti`, de sorte que les rejeux échouent et que la déconnexion est réelle.
- **Gardes** : `get_current_user`, `get_current_active_superuser` et `require_scopes(...)` sous forme de simples dépendances.
- **Stockage** : SQLite sans effort, PostgreSQL en définissant `DATABASE_URL` et en exécutant `alembic upgrade head`.
- **Avant de déployer** : fixez `SECRET_KEY`, pointez `DATABASE_URL` vers une vraie base de données.

## Pour aller plus loin

- [Persistance asynchrone avec SQLModel](sqlmodel.md) — la même disposition par domaines, centrée sur l'accès asynchrone aux données, les migrations et le CRUD générique.
- [FastAPI orienté domaine](domain-starter.md) — la disposition sur laquelle repose ce modèle, sans la machinerie d'authentification.
- [Quel starter choisir ?](../user-guide/choosing-a-starter.md) — comment ce modèle se compare aux autres.
