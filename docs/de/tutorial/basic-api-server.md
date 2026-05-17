# Einen einfachen API-Server bauen

Lernen Sie, wie Sie mit FastAPI-fastkit schnell einen einfachen REST-API-Server aufbauen. Dieses Tutorial richtet sich an FastAPI-Einsteiger und behandelt das Erstellen grundlegender CRUD-APIs.

## Was Sie in diesem Tutorial lernen

- Einen einfachen API-Server mit dem Befehl `fastkit startdemo` erstellen
- Die Struktur eines FastAPI-Projekts verstehen
- Grundlegende CRUD-Endpunkte nutzen
- Die API testen und dokumentieren
- Methoden zur Erweiterung des Projekts

## Voraussetzungen

- Python 3.12 oder höher installiert
- FastAPI-fastkit installiert (`pip install fastapi-fastkit`)
- Grundkenntnisse in Python

## Schritt 1: Ein einfaches API-Projekt erstellen

Erstellen wir einen einfachen API-Server mit der Vorlage `fastapi-default`.

<div class="termy">

```console
$ fastkit startdemo fastapi-default
Enter the project name: my-first-api
Enter the author name: Developer Kim
Enter the author email: developer@example.com
Enter the project description: My first FastAPI server
Deploying FastAPI project using 'fastapi-default' template

           Project Information
┌──────────────┬────────────────────────────┐
│ Project Name │ my-first-api               │
│ Author       │ Developer Kim              │
│ Author Email │ developer@example.com      │
│ Description  │ My first FastAPI server    │
└──────────────┴────────────────────────────┘

       Template Dependencies
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ pydantic          │
│ Dependency 4 │ pydantic-settings │
│ Dependency 5 │ python-dotenv     │
└──────────────┴───────────────────┘

Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y

✨ FastAPI project 'my-first-api' from 'fastapi-default' has been created successfully!
```

</div>

## Schritt 2: Die generierte Projektstruktur verstehen

Untersuchen wir die Struktur des generierten Projekts:

```
my-first-api/
├── README.md                 # Projektdokumentation
├── requirements.txt          # Liste der Abhängigkeiten
├── setup.py                  # Paketkonfiguration
├── scripts/
│   └── run-server.sh        # Skript zum Starten des Servers
├── src/                     # Hauptquellcode
│   ├── main.py              # Einstiegspunkt der FastAPI-Anwendung
│   ├── core/
│   │   └── config.py        # Verwaltung der Konfiguration
│   ├── api/
│   │   ├── api.py           # Sammlung der API-Router
│   │   └── routes/
│   │       └── items.py     # Endpunkte rund um Items
│   ├── schemas/
│   │   └── items.py         # Definitionen der Datenmodelle
│   ├── crud/
│   │   └── items.py         # Logik zur Datenverarbeitung
│   └── mocks/
│       └── mock_items.json  # Test data
└── tests/                   # Test code
    ├── __init__.py
    ├── conftest.py
    └── test_items.py
```

### Beschreibung der wichtigsten Dateien

- **`src/main.py`**: Einstiegspunkt der FastAPI-Anwendung
- **`src/api/routes/items.py`**: Definitionen der item-bezogenen API-Endpunkte
- **`src/schemas/items.py`**: Definitionen der Datenstrukturen für Anfragen/Antworten
- **`src/crud/items.py`**: Logik für Datenoperationen
- **`src/mocks/mock_items.json`**: Beispieldaten für die Entwicklung

## Schritt 3: Den Server starten

Wechseln wir in das generierte Projektverzeichnis und starten den Server.

<div class="termy">

```console
$ cd my-first-api
$ fastkit runserver
Starting FastAPI server at 127.0.0.1:8000...

INFO:     Will watch for changes in these directories: ['/path/to/my-first-api']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

</div>

Sobald der Server erfolgreich läuft, können Sie folgende URLs in Ihrem Browser aufrufen:

- **API-Server**: http://127.0.0.1:8000
- **Swagger-UI-Dokumentation**: http://127.0.0.1:8000/docs
- **ReDoc-Dokumentation**: http://127.0.0.1:8000/redoc

## Schritt 4: Die API-Endpunkte erkunden

Die generierte API stellt standardmäßig folgende Endpunkte bereit:

| Methode | Endpunkt | Beschreibung |
|--------|----------|-------------|
| GET | `/items/` | Alle Items abrufen |
| GET | `/items/{item_id}` | Bestimmtes Item abrufen |
| POST | `/items/` | Neues Item anlegen |
| PUT | `/items/{item_id}` | Item aktualisieren |
| DELETE | `/items/{item_id}` | Item löschen |

### Die API testen

**1. Alle Items abrufen**

<div class="termy">

```console
$ curl -X GET "http://127.0.0.1:8000/items/"
[
  {
    "id": 1,
    "name": "Laptop",
    "description": "High-performance laptop",
    "price": 999.99,
    "tax": 99.99
  },
  {
    "id": 2,
    "name": "Mouse",
    "description": "Wireless mouse",
    "price": 29.99,
    "tax": 2.99
  }
]
```

</div>

**2. Ein neues Item anlegen**

<div class="termy">

```console
$ curl -X POST "http://127.0.0.1:8000/items/" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Keyboard",
       "description": "Mechanical keyboard",
       "price": 150.00,
       "tax": 15.00
     }'

{
  "id": 3,
  "name": "Keyboard",
  "description": "Mechanical keyboard",
  "price": 150.0,
  "tax": 15.0
}
```

</div>

**3. Ein bestimmtes Item abrufen**

<div class="termy">

```console
$ curl -X GET "http://127.0.0.1:8000/items/1"
{
  "id": 1,
  "name": "Laptop",
  "description": "High-performance laptop",
  "price": 999.99,
  "tax": 99.99
}
```

</div>

## Schritt 5: Die API mit Swagger UI testen

Rufen Sie http://127.0.0.1:8000/docs in Ihrem Browser auf, um die automatisch generierte API-Dokumentation zu sehen.

Was Sie mit Swagger UI machen können:

1. **API-Endpunkte anzeigen**: alle verfügbaren Endpunkte sehen
2. **Anfrage-/Antwortschemas prüfen**: Eingabe-/Ausgabeformate jedes Endpunkts einsehen
3. **APIs direkt testen**: echte API-Aufrufe per „Try it out"-Button durchführen
4. **Beispieldaten ansehen**: Beispielanfragen/-antworten für jeden Endpunkt einsehen

### So nutzen Sie Swagger UI

1. Klicken Sie auf den GET-Endpunkt `/items/`
2. Klicken Sie auf die Schaltfläche „Try it out"
3. Klicken Sie auf „Execute"
4. Sehen Sie sich die Antwort des Servers an

## Schritt 6: Die Code-Struktur verstehen

### Hauptanwendung (`src/main.py`)

```python
from fastapi import FastAPI
from src.api.api import api_router
from src.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
)

app.include_router(api_router)

@app.get("/")
def read_root():
    return {"message": "Hello World"}
```

### Item-Schema (`src/schemas/items.py`)

```python
from pydantic import BaseModel
from typing import Optional

class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    name: Optional[str] = None
    price: Optional[float] = None

class Item(ItemBase):
    id: int

    class Config:
        from_attributes = True
```

### CRUD-Logik (`src/crud/items.py`)

```python
from typing import List, Optional
from src.schemas.items import Item, ItemCreate, ItemUpdate

class ItemCRUD:
    def __init__(self):
        self.items: List[Item] = []
        self.next_id = 1

    def create_item(self, item: ItemCreate) -> Item:
        new_item = Item(id=self.next_id, **item.dict())
        self.items.append(new_item)
        self.next_id += 1
        return new_item

    def get_items(self) -> List[Item]:
        return self.items

    def get_item(self, item_id: int) -> Optional[Item]:
        return next((item for item in self.items if item.id == item_id), None)
```

## Schritt 7: Das Projekt erweitern

### Neue Routen hinzufügen

Sie können neue Endpunkte mit dem Befehl `fastkit addroute` hinzufügen:

<div class="termy">

```console
$ fastkit addroute user
                       Adding New Route
┌──────────────────┬──────────────────────────────────────────┐
│ Project          │ my-first-api                             │
│ Route Name       │ user                                     │
│ Target Directory │ /path/to/my-first-api                   │
└──────────────────┴──────────────────────────────────────────┘

Do you want to add route 'user' to the current project? [Y/n]: y

✨ Successfully added new route 'user' to the current project!
```

</div>

Dieser Befehl erstellt die folgenden Dateien:

- `src/api/routes/user.py` — Endpunkte zu Nutzern
- `src/schemas/user.py` — Datenmodelle für Nutzer
- `src/crud/user.py` — Verarbeitungslogik für Nutzerdaten

### Umgebungskonfiguration anpassen

Sie können die Datei `src/core/config.py` ändern, um Projektparameter anzupassen:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "My First API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "My first FastAPI server"
    API_V1_STR: str = "/api/v1"

    class Config:
        env_file = ".env"

settings = Settings()
```

## Schritt 8: Tests ausführen

Das Projekt enthält grundlegende Tests:

<div class="termy">

```console
$ pytest tests/ -v
======================== test session starts ========================
collected 4 items

tests/test_items.py::test_create_item PASSED                   [ 25%]
tests/test_items.py::test_read_items PASSED                    [ 50%]
tests/test_items.py::test_read_item PASSED                     [ 75%]
tests/test_items.py::test_update_item PASSED                   [100%]

======================== 4 passed in 0.15s ========================
```

</div>

## Nächste Schritte

Sie haben den Bau eines einfachen API-Servers abgeschlossen! Nächste Schritte zum Ausprobieren:

1. **[Asynchrone CRUD-APIs bauen](async-crud-api.md)** — lernen Sie komplexere asynchrone Verarbeitung
2. **[Datenbankintegration](database-integration.md)** — PostgreSQL und SQLAlchemy nutzen
3. **[Docker-Containerisierung](docker-deployment.md)** — auf ein Produktionsdeployment vorbereiten
4. **[Benutzerdefinierte Antwortbehandlung](custom-response-handling.md)** — erweiterte Konfiguration der Antwortformate

## Fehlerbehebung

### Häufige Probleme

**F. Der Server startet nicht**
A. Stellen Sie sicher, dass Ihre virtuelle Umgebung aktiviert ist und die Abhängigkeiten korrekt installiert wurden.

**F. Ich kann nicht auf API-Endpunkte zugreifen**
A. Prüfen Sie, dass der Server normal läuft und die Portnummer (Standard: 8000) korrekt ist.

**F. APIs erscheinen nicht in Swagger UI**
A. Prüfen Sie, dass der Router in `src/main.py` korrekt eingebunden ist.

## Zusammenfassung

In diesem Tutorial haben wir mit FastAPI-fastkit:

- ✅ Ein einfaches FastAPI-Projekt erstellt
- ✅ Die Projektstruktur verstanden
- ✅ CRUD-API-Endpunkte verwendet
- ✅ Die API dokumentiert und getestet
- ✅ Methoden zur Erweiterung des Projekts kennengelernt

Jetzt, da Sie die Grundlagen von FastAPI kennen, wagen Sie sich an komplexere Projekte!
