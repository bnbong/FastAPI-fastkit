# Persistance asynchrone avec `fastapi-sqlmodel`

Construisez une API adossée à une base de données dans laquelle chaque concept n'est défini **qu'une seule fois**. Les classes SQLModel sont à la fois la table SQLAlchemy et le schéma pydantic : ajouter une colonne ne signifie donc pas modifier quatre fichiers. Ce tutoriel parcourt le modèle `fastapi-sqlmodel` : la hiérarchie des modèles, la base CRUD générique, les réponses paginées, les migrations Alembic asynchrones et la façon d'ajouter votre propre domaine.

## Ce que vous apprendrez

- Générer un projet avec `fastkit startdemo fastapi-sqlmodel`
- Comment `ItemBase` → `Item` / `ItemCreate` / `ItemUpdate` / `ItemPublic` élimine la duplication des schémas
- Ce que `CRUDBase` vous apporte gratuitement et où l'étendre
- L'enveloppe de liste `Page[T]` et l'endroit où ses limites sont appliquées
- Exécuter des migrations Alembic asynchrones et passer de SQLite à PostgreSQL

## Prérequis

- Python 3.12+
- FastAPI-fastkit installé (`pip install fastapi-fastkit`)
- Être familier avec `async`/`await` et les notions SQL de base

Si vous préférez la pile PostgreSQL synchrone basée sur Compose, consultez [Intégration de base de données](database-integration.md), qui utilise `fastapi-psql-orm`.

## Étape 1 : Générer et lancer

```console
$ fastkit startdemo fastapi-sqlmodel
Enter the project name: catalog-api
Enter the author name: Developer Kim
Enter the author email: developer@example.com
Enter the project description: Product catalog service
Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y
```

```console
$ cd catalog-api
$ bash scripts/migrate.sh        # alembic upgrade head
$ bash scripts/run-server.sh     # or: uvicorn src.app.main:app --reload
```

La `DATABASE_URL` par défaut est `sqlite+aiosqlite:///./app.db` : il n'y a donc aucun serveur de base de données à installer. La documentation est disponible à <http://127.0.0.1:8000/docs>.

## Étape 2 : L'arborescence générée

```
catalog-api/
├── pyproject.toml              # métadonnées PEP 621 + [tool.fastapi-fastkit]
├── requirements.txt
├── alembic.ini
├── Dockerfile
├── .env
├── scripts/
│   ├── format.sh  lint.sh  migrate.sh  run-server.sh  test.sh
├── src/
│   └── app/
│       ├── main.py             # application FastAPI + lifespan
│       ├── core/config.py      # pydantic-settings
│       ├── db/
│       │   ├── session.py      # moteur asynchrone, dépendance get_session
│       │   └── base.py         # agrégation des métadonnées pour Alembic
│       ├── crud/
│       │   ├── base.py         # CRUDBase générique
│       │   └── pagination.py   # enveloppe Page[T]
│       ├── alembic/
│       │   ├── env.py          # environnement de migration asynchrone
│       │   └── versions/0001_create_items_table.py
│       ├── api/
│       │   ├── router.py       # regroupe la santé et les routeurs de domaine
│       │   └── health.py       # GET /health
│       └── domains/items/      # le domaine d'exemple
│           ├── models.py       # table Item + schémas Create/Update/Public
│           ├── crud.py         # ItemCRUD(CRUDBase)
│           └── router.py       # routeur FastAPI
└── tests/
    ├── conftest.py  test_health.py  test_items.py  test_crud_base.py
```

Remarquez ce qu'un dossier de domaine ne contient *pas* : aucun `schemas.py` distinct de `models.py`, et aucun code répétitif de dépôt (repository) propre au domaine. Le premier disparaît dans SQLModel, le second dans `CRUDBase`.

## Étape 3 : Une seule définition de modèle par concept

Ouvrez `src/app/domains/items/models.py`. Tout dérive d'une base unique :

```python
class ItemBase(SQLModel):
    """Fields shared by the table and every request/response schema."""
    name: str = Field(min_length=1, max_length=128, index=True)
    description: str | None = Field(default=None, max_length=512)
    price: float = Field(ge=0)
    in_stock: bool = True


class Item(ItemBase, table=True):        # the actual table
    __tablename__ = "items"
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=_utcnow)


class ItemCreate(ItemBase): ...          # POST body — no server-assigned fields


class ItemUpdate(SQLModel):              # PATCH body — every field optional
    name: str | None = Field(default=None, min_length=1, max_length=128)
    ...


class ItemPublic(ItemBase):              # response — base + server-assigned
    id: int
    created_at: datetime
```

Quatre classes, quatre rôles distincts, un seul endroit où vivent les champs :

| Classe       | Rôle                               | Pourquoi elle est séparée |
|--------------|------------------------------------|---------------------------|
| `ItemBase`   | définitions de champs partagées    | l'unique source de vérité |
| `Item`       | la table de la base de données     | ajoute `id`, `created_at` |
| `ItemCreate` | corps de requête pour `POST`       | ne doit pas accepter `id` |
| `ItemUpdate` | corps de requête pour `PATCH`      | chaque champ est facultatif |
| `ItemPublic` | corps de réponse                   | expose les champs attribués par le serveur |

**Le bénéfice :** ajouter une colonne `sku` revient à ajouter une ligne dans `ItemBase`. La table reçoit la colonne, le corps de création l'accepte et la réponse la renvoie — sans aucune autre modification. `ItemUpdate` reste volontairement explicite : la sémantique de mise à jour partielle est une décision, pas une dérivation.

## Étape 4 : Un CRUD que vous ne réécrivez pas

`src/app/crud/base.py` est une classe générique paramétrée par le modèle de table et ses deux schémas d'entrée :

```python
class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    async def get(self, session, obj_id) -> ModelType | None: ...
    async def list(self, session, *, offset=0, limit=20) -> Sequence[ModelType]: ...
    async def count(self, session) -> int: ...
    async def create(self, session, obj_in) -> ModelType: ...
    async def update(self, session, db_obj, obj_in) -> ModelType: ...
    async def delete(self, session, db_obj) -> None: ...
```

Un détail mérite d'être bien assimilé — `update` utilise `exclude_unset=True` :

```python
changes: dict[str, Any] = obj_in.model_dump(exclude_unset=True)
```

C'est ce qui rend `PATCH` réellement partiel. Un champ que le client n'a pas envoyé est absent du dictionnaire et n'est donc jamais écrit ; sans `exclude_unset`, un `PATCH` écraserait silencieusement les colonnes non modifiées avec les valeurs par défaut du schéma.

Un domaine hérite de la base et n'ajoute que ce qui lui est propre :

```python
class ItemCRUD(CRUDBase[Item, ItemCreate, ItemUpdate]):
    """CRUD for Item, extended with a name search."""

    async def search_by_name(self, session, term, *, limit=20):
        statement = select(Item).where(Item.name.like(f"%{term}%")).limit(limit)
        result = await session.exec(statement)
        return result.all()


item_crud = ItemCRUD(Item)
```

## Étape 5 : Listes paginées

Les points d'extrémité de liste renvoient une enveloppe `Page[T]` plutôt qu'un simple tableau :

```json
{"items": [...], "total": 42, "offset": 0, "limit": 20}
```

Le plafonnement se fait dans le routeur, et non côté client :

```python
limit: int = Query(default=settings.DEFAULT_PAGE_LIMIT, ge=1)
...
limit = min(limit, settings.MAX_PAGE_LIMIT)
```

Ainsi, `?limit=100000` ne peut pas transformer une requête en parcours complet de la table. `Page` expose aussi une propriété `has_next` dérivée de `offset`, `len(items)` et `total`, ce qui correspond généralement à ce dont un front-end a réellement besoin.

Les points d'extrémité fournis par le domaine items :

| Méthode | Point d'extrémité         | Description                          |
|---------|---------------------------|--------------------------------------|
| GET     | `/api/v1/health`          | Sonde de vivacité                    |
| GET     | `/api/v1/items`           | Lister les éléments (`offset`, `limit`) |
| GET     | `/api/v1/items/{item_id}` | Lire un élément                      |
| POST    | `/api/v1/items`           | Créer un élément (`201`)             |
| PATCH   | `/api/v1/items/{item_id}` | Mettre à jour partiellement un élément |
| DELETE  | `/api/v1/items/{item_id}` | Supprimer un élément (`204`)         |

Essayez :

```console
$ curl -X POST http://127.0.0.1:8000/api/v1/items \
    -H 'Content-Type: application/json' \
    -d '{"name": "Keyboard", "price": 89.0}'

$ curl 'http://127.0.0.1:8000/api/v1/items?offset=0&limit=5'
```

## Étape 6 : Asynchrone de bout en bout

`src/app/db/session.py` construit un `AsyncEngine` par processus et distribue des sessions limitées à la requête :

```python
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session
```

Les routeurs en dépendent (`session: AsyncSession = Depends(get_session)`), `CRUDBase` la prend comme premier argument, et chaque appel à la base de données est attendu avec `await`. Rien dans le chemin de la requête ne bloque la boucle d'événements sur des E/S.

`create_db_and_tables()` se trouve aussi ici et est appelée depuis le `lifespan` de l'application. C'est une commodité pour la valeur SQLite par défaut et pour les tests — une fois qu'Alembic gère le schéma, définissez `CREATE_TABLES_ON_STARTUP=false`.

## Étape 7 : Ajouter un domaine

1. Créez `src/app/domains/<your_domain>/` sur le modèle de `items` (`models.py`, `crud.py`, `router.py`).
2. **Importez le modèle de table dans `src/app/db/base.py`.** C'est l'étape facile à oublier et déroutante à déboguer : l'autogénération d'Alembic et `create_db_and_tables` ne voient que les modèles qui ont été importés, si bien qu'un import manquant se traduit par une migration vide plutôt que par une erreur.
3. Enregistrez le routeur dans `src/app/api/router.py`. Les ancres `# fastkit:imports` et `# fastkit:routes` marquent l'endroit où `fastkit addroute` insère du code — placez le vôtre aux mêmes endroits.
4. Générez une migration : `alembic revision --autogenerate -m "add <domain>"`.
5. Ajoutez `tests/test_<your_domain>.py` sur le modèle de `tests/test_items.py`.

## Étape 8 : Migrations et PostgreSQL

L'environnement Alembic situé dans `src/app/alembic/env.py` est asynchrone : il s'exécute donc avec la même pile de pilotes que l'application. Au quotidien :

```console
$ bash scripts/migrate.sh                                  # upgrade head
$ alembic revision --autogenerate -m "add sku to items"    # after a model change
```

Changer de base de données se résume à changer d'URL et de pilote :

```console
$ uv pip install "asyncpg>=0.31.0"
$ export DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/app"
$ bash scripts/migrate.sh
```

Rien ne change dans les modèles, le CRUD ou les routeurs — c'est tout l'intérêt de garder le pilote derrière `create_engine`.

## Étape 9 : Les tests

```console
$ bash scripts/test.sh    # or: pytest
```

Chaque test s'exécute contre une base SQLite en mémoire toute neuve : pas de migrations, pas de fichiers de fixtures, pas de nettoyage entre les tests. `test_crud_base.py` exerce directement la base générique — sa lecture est utile avant de l'étendre, car il documente le comportement de `exclude_unset` et le contrat count/offset dont héritent vos propres domaines.

## Récapitulatif

- **Génération** : `fastkit startdemo fastapi-sqlmodel` → `bash scripts/migrate.sh` → `bash scripts/run-server.sh`.
- **Modèles** : `ItemBase` contient les champs ; la table et les schémas d'E/S en dérivent, si bien qu'une nouvelle colonne est déclarée une seule fois.
- **CRUD** : `CRUDBase` fournit get / list / count / create / update / delete ; les domaines en héritent pour leurs propres requêtes.
- **Listes** : enveloppe `Page[T]` avec plafonnement de la limite côté serveur.
- **Schéma** : Alembic asynchrone ; pensez à importer les nouveaux modèles dans `src/app/db/base.py`.
- **Base de données** : SQLite par défaut, PostgreSQL en modifiant `DATABASE_URL` et en installant `asyncpg`.

## Pour aller plus loin

- [Authentification JWT](auth-jwt.md) — placez des comptes et des routes protégées devant cette couche de données.
- [FastAPI orienté domaine](domain-starter.md) — la disposition commune aux deux modèles, sans base de données.
- [Quel starter choisir ?](../user-guide/choosing-a-starter.md)
