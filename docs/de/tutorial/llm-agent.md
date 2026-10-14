# Streaming-LLM-Agent mit `fastapi-llm-agent`

Bauen Sie ein Chat-Backend, das Tokens streamt, während sie erzeugt werden, und das tatsächlich etwas *tun* kann — Tools aufrufen, deren Ergebnisse lesen und weitermachen. Dieses Tutorial führt Sie durch die Vorlage `fastapi-llm-agent`: das SSE-Ereignisprotokoll, die Tool-Call-Schleife und ihre Iterationsobergrenze, den Konversationsspeicher hinter einer Schnittstelle und eine Testsuite, die nie auf das Netzwerk zugreift.

## Was Sie lernen werden

- Ein Projekt mit `fastkit startdemo fastapi-llm-agent` generieren
- Welche SSE-Ereignistypen ein Client verarbeiten muss und was jeder davon bedeutet
- Wie ein Durchlauf der Tool-Call-Schleife Schritt für Schritt funktioniert
- Ein eigenes Tool hinzufügen
- Den prozessinternen Konversationsspeicher durch einen echten ersetzen
- Warum die Tests deterministisch sind und nichts kosten

## Voraussetzungen

- Python 3.12+
- FastAPI-fastkit installiert (`pip install fastapi-fastkit`)
- Einen Anthropic-API-Schlüssel — nur, um mit einem echten Modell zu sprechen. Die generierte Testsuite läuft ohne Schlüssel.
- Vertrautheit mit `async`/`await` und asynchronen Generatoren

## Schritt 1: Generieren und konfigurieren

```console
$ fastkit startdemo fastapi-llm-agent
Enter the project name: support-agent
Enter the author name: Developer Kim
Enter the author email: developer@example.com
Enter the project description: Streaming support assistant
Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y
```

Tragen Sie Ihren Schlüssel vor dem ersten Start in `.env` ein:

```bash
ANTHROPIC_API_KEY=sk-ant-...
LLM_MODEL=claude-sonnet-5
LLM_MAX_TOKENS=4096
MAX_TOOL_ITERATIONS=5
```

Der Schlüssel wird von pydantic-settings gelesen und dem Client bei der Erzeugung übergeben. Er wird nie in den Quellcode geschrieben und nie in das Docker-Image eingebacken.

```console
$ cd support-agent
$ bash scripts/run-server.sh
$ bash scripts/chat.sh "What is 12 * 34?"
```

!!! tip "Ein Gateway statt der Anthropic-API verwenden"
    Setzen Sie `LLM_BASE_URL` (und `LLM_AUTH_TOKEN`, falls das Gateway Bearer-Authentifizierung verwendet), um auf LiteLLM, einen internen Proxy oder einen lokalen Server zu zeigen. Das Übertragungsformat bleibt die Anthropic Messages API; die Übersetzung für andere Anbieter ist Aufgabe des Gateways, nicht der App.

## Schritt 2: Der generierte Baum

```
support-agent/
├── pyproject.toml              # PEP 621 metadata + [tool.fastapi-fastkit]
├── requirements.txt
├── Dockerfile
├── .env
├── scripts/
│   ├── chat.sh                 # send one message to a running server
│   ├── format.sh  lint.sh  run-server.sh  test.sh
├── src/
│   └── app/
│       ├── main.py             # FastAPI app + lifespan
│       ├── core/config.py      # pydantic-settings (API key lives here)
│       ├── llm/
│       │   ├── client.py       # AsyncAnthropic factory
│       │   ├── tools.py        # tool schemas + handlers
│       │   └── agent.py        # streaming agent + tool loop
│       ├── memory/
│       │   ├── base.py         # ConversationStore interface
│       │   └── in_memory.py    # process-local implementation
│       ├── schemas/chat.py     # request bodies + SSE event envelope
│       └── api/
│           ├── router.py       # aggregates health + chat
│           ├── deps.py         # store / agent dependencies
│           ├── health.py       # GET /health
│           └── chat.py         # POST /chat (SSE), conversation history
└── tests/
    ├── conftest.py             # scripted fake Anthropic client
    ├── test_health.py  test_chat.py  test_tools.py  test_memory.py
```

Drei Grenzen sollten Sie gleich zu Beginn beachten: Der **Client** wird von einer Factory erzeugt (sodass Tests ihn ersetzen können), der **Speicher** ist eine Schnittstelle mit einer trivialen Implementierung (sodass die Produktion sie ersetzen kann), und **Tools** sind eine Schema-Liste plus ein Handler-Dict (sodass das Hinzufügen eines Tools nur eine Datei berührt).

## Schritt 3: Die Endpunkte

| Methode | Endpunkt                     | Beschreibung                  |
|---------|------------------------------|-------------------------------|
| GET     | `/api/v1/health`             | Liveness-Probe                |
| POST    | `/api/v1/chat`               | Eine Antwort als SSE streamen |
| GET     | `/api/v1/conversations/{id}` | Gespeicherten Verlauf lesen   |
| DELETE  | `/api/v1/conversations/{id}` | Eine Konversation vergessen   |

`POST /api/v1/chat` nimmt `{"message": "...", "conversation_id": "..."}` entgegen. Lassen Sie `conversation_id` weg, um eine neue Konversation zu beginnen, und lesen Sie die zugewiesene ID aus dem abschließenden `done`-Ereignis aus.

## Schritt 4: Das Stream-Protokoll

Jede SSE-Nachricht trägt ihren Typ im Feld `event:` und eine JSON-Hülle in `data:`. Ein Client muss fünf davon plus Fehler verarbeiten:

| Ereignis      | Felder                          | Bedeutung                          |
|---------------|---------------------------------|------------------------------------|
| `token`       | `text`                          | Ein Teil der Assistentenantwort    |
| `tool_use`    | `tool_name`, `tool_input`       | Claude hat ein Tool angefordert    |
| `tool_result` | `tool_name`, `tool_output`      | Das Tool wurde ausgeführt          |
| `usage`       | `input_tokens`, `output_tokens` | Token-Verbrauch pro Durchlauf      |
| `done`        | `conversation_id`               | Der Durchlauf ist abgeschlossen    |
| `error`       | `detail`                        | Mitten im Stream ist etwas fehlgeschlagen |

`tool_use` und `tool_result` sind keine Dekoration — sie ermöglichen es einer UI, „searching…“ anzuzeigen, statt einer unerklärten Pause, während ein Tool läuft.

Der Token-Verbrauch wird außerdem bei jedem Durchlauf in den Logger `app.agent` geschrieben, sodass die Kosten in den Server-Logs sichtbar sind, ohne einen Client instrumentieren zu müssen.

## Schritt 5: Ein Durchlauf der Schleife

`ChatAgent.stream` in `src/app/llm/agent.py` ist die gesamte Engine. Ein Durchlauf sieht so aus:

1. Den Konversationsverlauf aus dem Speicher laden.
2. Eine Streaming-Anfrage mit dem Verlauf, der neuen Benutzernachricht und den Tool-Schemas öffnen.
3. Jeden eintreffenden Textabschnitt sofort als `token`-Ereignis ausgeben.
4. Wenn der Stream endet, die finale Nachricht lesen; ein `usage`-Ereignis ausgeben und die Token-Zahlen loggen.
5. **Wenn `stop_reason != "tool_use"`,** ist der Assistent fertig: den Durchlauf speichern, `done` ausgeben, zurückkehren.
6. **Andernfalls** für jeden `tool_use`-Block: `tool_use` ausgeben, den Handler ausführen, `tool_result` ausgeben und die Ausgabe sammeln.
7. Alle Tool-Ergebnisse als eine einzige `user`-Nachricht zurücksenden — das verlangt die Messages API — und ab Schritt 2 wiederholen.

Die Schleife ist durch `MAX_TOOL_ITERATIONS` begrenzt (standardmäßig 5). Fordert Claude über diese Grenze hinaus weiter Tools an, wird der Durchlauf gespeichert, eine Warnung geloggt und ein `error`-Ereignis ausgegeben, statt den Server endlos weiterlaufen zu lassen:

```python
yield AgentEvent(
    type="error",
    detail=(
        "The assistant exceeded the tool-call limit of "
        f"{self._max_tool_iterations} iterations."
    ),
)
```

Eine solche Obergrenze ist in einer Agent-Schleife nicht optional. Ohne sie kann Ihnen ein Modell, das ein Tool-Ergebnis missversteht, unbegrenzt Kosten verursachen.

## Schritt 6: Die mitgelieferten Tools

| Tool           | Zweck                                                                |
|----------------|----------------------------------------------------------------------|
| `calculator`   | Arithmetik, in einen AST geparst und per Whitelist geprüft — kein `eval` |
| `current_time` | Aktuelle Uhrzeit in einer IANA-Zeitzone                               |

Der `calculator` verdient einen zweiten Blick. Er parst den Ausdruck mit `ast` und durchläuft nur Knotentypen aus einer Whitelist, sodass ein von einem Modell stammendes Tool-Argument kein beliebiges Python ausführen kann. Jedes Tool, das modellgenerierte Eingaben akzeptiert, braucht dieselbe Disziplin: **Modellausgabe ist nicht vertrauenswürdige Eingabe.**

### Ein Tool hinzufügen

Alles liegt in `src/app/llm/tools.py`:

1. Hängen Sie ein Schema an `TOOL_SCHEMAS` an — `name`, `description` und ein JSON-Schema als `input_schema`.
2. Registrieren Sie den Handler unter demselben Namen in `TOOL_HANDLERS`.

Zwei Dinge sollten Sie richtig machen:

- **Die Beschreibung ist die gesamte Anweisung, die Claude** darüber erhält, wann es zu dem Tool greifen soll. Das ist Prompt-Engineering, keine Dokumentation — vage Beschreibungen führen zu Tools, die nie aufgerufen werden, oder ständig.
- **Handler sollten einen String zurückgeben und ihre eigenen Fehler in eine lesbare Meldung umwandeln,** statt eine Ausnahme auszulösen. Die Schleife gibt diesen Text direkt an das Modell zurück, sodass „no city named X was found“ dem Modell erlaubt, sich zu erholen, während eine Ausnahme den Durchlauf beendet.

## Schritt 7: Konversationsspeicher

`ConversationStore` (`src/app/memory/base.py`) ist die Schnittstelle; das mitgelieferte `in_memory.py` implementiert sie mit einem Dict. Das genügt für einen einzelnen Prozess und ist für alles andere falsch — ein Neustart vergisst alles, und zwei Worker sind sich über den Verlauf uneinig.

Für den echten Einsatz implementieren Sie dieselbe Schnittstelle gegen Redis oder eine Datenbank und geben sie aus `get_store()` in `src/app/api/deps.py` zurück. Am Agent und an den Routern ändert sich nichts, da keiner von beiden jemals die konkrete Klasse nennt.

## Schritt 8: Die Tests

```console
$ bash scripts/test.sh    # or: pytest
```

`tests/conftest.py` spielt vorgeskriptete Durchläufe über ein Fake ab, das `AsyncAnthropic.messages.stream` nachahmt. Daher ist die Suite deterministisch, läuft offline, kostet nichts und deckt dennoch die Pfade ab, auf die es ankommt: den Streaming-Pfad und die vollständige Tool-Schleife, einschließlich eines Durchlaufs, in dem ein Tool aufgerufen wird und das Modell anschließend antwortet.

Dieses Muster sollten Sie beibehalten, wenn Sie den Agent erweitern. Eine LLM-Integration gegen das Live-Modell zu testen, ergibt eine langsame, unzuverlässige und teure Suite, die trotzdem nicht prüfen kann, was das Modell sagen wird. Die *Schleife* gegen einen vorgeskripteten Client zu testen, prüft genau das, was Sie geschrieben haben.

## Schritt 9: Erweiterungspunkte

- **Persistenter Verlauf** — implementieren Sie `ConversationStore` gegen Redis oder eine Datenbank (Schritt 7).
- **RAG** — Retrieval liegt in der Vorlage bewusst außerhalb des Umfangs. Die naheliegende Nahtstelle ist `ChatAgent.stream`: Holen Sie vor der ersten Anfrage Kontext und stellen Sie ihn dem System-Prompt voran, oder stellen Sie Ihren Index als weiteres Tool bereit und lassen Sie das Modell entscheiden, wann es sucht.
- **Authentifizierung und Rate Limiting** — `POST /chat` ist im Auslieferungszustand nicht authentifiziert. Hängen Sie eine Dependency an den Router, bevor Sie ihn öffentlich zugänglich machen; das [Tutorial zur JWT-Authentifizierung](auth-jwt.md) enthält die Guards, die Sie wiederverwenden würden.

## Rückblick

- **Generierung**: `fastkit startdemo fastapi-llm-agent`, `ANTHROPIC_API_KEY` setzen, `bash scripts/run-server.sh`.
- **Streaming**: SSE mit den Ereignissen `token` / `tool_use` / `tool_result` / `usage` / `done` / `error`.
- **Schleife**: Stream → Tool-Aufrufe → Ergebnisse als eine Benutzernachricht zurück → wiederholen, begrenzt durch `MAX_TOOL_ITERATIONS`.
- **Tools**: ein Schema in `TOOL_SCHEMAS` und ein Handler in `TOOL_HANDLERS`; behandeln Sie Tool-Eingaben als nicht vertrauenswürdig.
- **Speicher**: `ConversationStore`-Schnittstelle, Dict-Implementierung, Austausch in `get_store()`.
- **Tests**: ein vorgeskripteter Fake-Client, sodass die Suite offline und deterministisch läuft.

## Wie es weitergeht

- [MCP-Integration](mcp-integration.md) — wenn Sie einen MCP-Server statt eines Chat-Agents brauchen.
- [JWT-Authentifizierung](auth-jwt.md) — Konten vor den Chat-Endpunkt stellen.
- [Welchen Starter soll ich wählen?](../user-guide/choosing-a-starter.md)
