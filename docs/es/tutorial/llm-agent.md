# Agente LLM con streaming con `fastapi-llm-agent`

Construye un backend de chat que transmite los tokens a medida que se
generan y que puede *hacer* cosas de verdad — llamar a herramientas, leer
sus resultados y seguir adelante. Este tutorial recorre la plantilla
`fastapi-llm-agent`: el protocolo de eventos SSE, el bucle de llamadas a
herramientas y su límite de iteraciones, la memoria de conversación detrás
de una interfaz y una suite de tests que nunca toca la red.

## Qué vas a aprender

- Generar un proyecto con `fastkit startdemo fastapi-llm-agent`
- Los tipos de eventos SSE que un cliente tiene que manejar y qué significa
  cada uno
- Cómo funciona, paso a paso, un turno del bucle de llamadas a herramientas
- Añadir tu propia herramienta
- Sustituir el almacén de conversaciones en proceso por uno real
- Por qué los tests son deterministas y gratuitos de ejecutar

## Requisitos previos

- Python 3.12+
- FastAPI-fastkit instalado (`pip install fastapi-fastkit`)
- Una API key de Anthropic — solo para hablar con un modelo real. La suite
  de tests generada se ejecuta sin ella.
- Familiaridad con `async`/`await` y con los generadores asíncronos

## Paso 1: Generar y configurar

```console
$ fastkit startdemo fastapi-llm-agent
Enter the project name: support-agent
Enter the author name: Developer Kim
Enter the author email: developer@example.com
Enter the project description: Streaming support assistant
Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y
```

Pon tu clave en `.env` antes de la primera ejecución:

```bash
ANTHROPIC_API_KEY=sk-ant-...
LLM_MODEL=claude-sonnet-5
LLM_MAX_TOKENS=4096
MAX_TOOL_ITERATIONS=5
```

pydantic-settings lee la clave y se la pasa al cliente al construirlo.
Nunca se escribe en el código fuente ni se incrusta en la imagen de Docker.

```console
$ cd support-agent
$ bash scripts/run-server.sh
$ bash scripts/chat.sh "What is 12 * 34?"
```

!!! tip "Usar un gateway en lugar de la API de Anthropic"
    Define `LLM_BASE_URL` (y `LLM_AUTH_TOKEN` si el gateway usa
    autenticación bearer) para apuntar a LiteLLM, a un proxy interno o a un
    servidor local. El formato de transmisión sigue siendo la Messages API de
    Anthropic; traducir para otros proveedores es tarea del gateway, no de
    la app.

## Paso 2: El árbol generado

```
support-agent/
├── pyproject.toml              # Metadatos PEP 621 + [tool.fastapi-fastkit]
├── requirements.txt
├── Dockerfile
├── .env
├── scripts/
│   ├── chat.sh                 # envía un mensaje a un servidor en ejecución
│   ├── format.sh  lint.sh  run-server.sh  test.sh
├── src/
│   └── app/
│       ├── main.py             # app FastAPI + lifespan
│       ├── core/config.py      # pydantic-settings (aquí vive la API key)
│       ├── llm/
│       │   ├── client.py       # fábrica de AsyncAnthropic
│       │   ├── tools.py        # esquemas de herramientas + handlers
│       │   └── agent.py        # agente con streaming + bucle de herramientas
│       ├── memory/
│       │   ├── base.py         # interfaz ConversationStore
│       │   └── in_memory.py    # implementación local al proceso
│       ├── schemas/chat.py     # cuerpos de petición + envoltorio de eventos SSE
│       └── api/
│           ├── router.py       # agrega health + chat
│           ├── deps.py         # dependencias de store / agente
│           ├── health.py       # GET /health
│           └── chat.py         # POST /chat (SSE), historial de conversación
└── tests/
    ├── conftest.py             # cliente Anthropic falso con guion
    ├── test_health.py  test_chat.py  test_tools.py  test_memory.py
```

Conviene fijarse desde el principio en tres fronteras: el **cliente** se
crea con una fábrica (para que los tests puedan sustituirlo), la
**memoria** es una interfaz con una implementación trivial (para que
producción pueda sustituirla) y las **herramientas** son una lista de
esquemas más un diccionario de handlers (para que añadir una solo toque un
archivo).

## Paso 3: Los endpoints

| Método | Endpoint                     | Descripción                     |
|--------|------------------------------|---------------------------------|
| GET    | `/api/v1/health`             | Probe de liveness               |
| POST   | `/api/v1/chat`               | Transmite una respuesta por SSE |
| GET    | `/api/v1/conversations/{id}` | Leer el historial guardado      |
| DELETE | `/api/v1/conversations/{id}` | Olvidar una conversación        |

`POST /api/v1/chat` recibe `{"message": "...", "conversation_id": "..."}`.
Omite `conversation_id` para empezar una conversación nueva y lee el id
asignado en el evento final `done`.

## Paso 4: El protocolo de streaming

Cada mensaje SSE lleva su tipo en el campo `event:` y un envoltorio JSON en
`data:`. Un cliente tiene que manejar cinco de ellos además de los errores:

| Evento        | Campos                          | Significado                            |
|---------------|---------------------------------|----------------------------------------|
| `token`       | `text`                          | Un fragmento de la respuesta del asistente |
| `tool_use`    | `tool_name`, `tool_input`       | Claude ha pedido una herramienta       |
| `tool_result` | `tool_name`, `tool_output`      | La herramienta se ha ejecutado         |
| `usage`       | `input_tokens`, `output_tokens` | Consumo de tokens por turno            |
| `done`        | `conversation_id`               | El turno ha terminado                  |
| `error`       | `detail`                        | Algo falló a mitad del stream          |

`tool_use` y `tool_result` no son decoración — son lo que permite que una
interfaz muestre "buscando…" en lugar de una pausa sin explicación mientras
se ejecuta una herramienta.

El uso de tokens también se escribe en el logger `app.agent` en cada turno,
así que el consumo es visible en los logs del servidor sin instrumentar un
cliente.

## Paso 5: Un turno del bucle

`ChatAgent.stream` en `src/app/llm/agent.py` es todo el motor. Un turno
transcurre así:

1. Cargar el historial de la conversación desde el store.
2. Abrir una petición en streaming con el historial, el nuevo mensaje del
   usuario y los esquemas de las herramientas.
3. Emitir cada fragmento de texto como evento `token` en cuanto llega.
4. Cuando termina el stream, leer el mensaje final; emitir un evento
   `usage` y registrar en el log el recuento de tokens.
5. **Si `stop_reason != "tool_use"`,** el asistente ha terminado: guardar
   el turno, emitir `done` y volver.
6. **En caso contrario,** para cada bloque `tool_use`: emitir `tool_use`,
   ejecutar el handler, emitir `tool_result` y recoger la salida.
7. Enviar todos los resultados de herramientas de vuelta en un único
   mensaje `user` — es lo que exige la Messages API — y repetir desde el
   paso 2.

El bucle está limitado por `MAX_TOOL_ITERATIONS` (5 por defecto). Si Claude
sigue pidiendo herramientas más allá del límite, el turno se guarda, se
registra una advertencia y se emite un evento `error` en lugar de dejar el
servidor dando vueltas:

```python
yield AgentEvent(
    type="error",
    detail=(
        "The assistant exceeded the tool-call limit of "
        f"{self._max_tool_iterations} iterations."
    ),
)
```

Un límite así no es opcional en un bucle de agente. Sin él, un modelo que
malinterpreta el resultado de una herramienta puede generarte costes de
forma indefinida.

## Paso 6: Las herramientas incluidas

| Herramienta    | Propósito                                                       |
|----------------|-----------------------------------------------------------------|
| `calculator`   | Aritmética, analizada como AST con lista blanca — no `eval`     |
| `current_time` | Hora actual en una zona horaria IANA                            |

La `calculator` merece una segunda mirada. Analiza la expresión con `ast` y
solo recorre tipos de nodo de una lista blanca, así que un argumento de
herramienta que viene de un modelo no puede ejecutar Python arbitrario.
Cualquier herramienta que acepte entrada generada por el modelo necesita la
misma disciplina: **la salida del modelo es entrada no confiable.**

### Añadir una herramienta

Todo vive en `src/app/llm/tools.py`:

1. Añade un esquema a `TOOL_SCHEMAS` — `name`, `description` y un
   `input_schema` en JSON Schema.
2. Registra el handler en `TOOL_HANDLERS` con el mismo nombre.

Dos cosas que hay que hacer bien:

- **La descripción es toda la instrucción que recibe Claude** sobre cuándo
  recurrir a la herramienta. Es prompt engineering, no documentación — las
  descripciones vagas producen herramientas que nunca se llaman o que se
  llaman constantemente.
- **Los handlers deben devolver una cadena y convertir sus propios fallos
  en un mensaje legible** en lugar de lanzar una excepción. El bucle
  devuelve ese texto directamente al modelo, así que "no city named X was
  found" permite que el modelo se recupere, mientras que una excepción
  termina el turno.

## Paso 7: Memoria de conversación

`ConversationStore` (`src/app/memory/base.py`) es la interfaz; el
`in_memory.py` incluido la implementa con un diccionario. Eso sirve para un
único proceso y es incorrecto para cualquier otra cosa — un reinicio lo
olvida todo y dos workers discrepan sobre el historial.

Para hacerlo real: implementa la misma interfaz sobre Redis o una base de
datos y devuélvela desde `get_store()` en `src/app/api/deps.py`. No cambia
nada en el agente ni en los routers, porque ninguno de los dos nombra nunca
la clase concreta.

## Paso 8: Los tests

```console
$ bash scripts/test.sh    # o: pytest
```

`tests/conftest.py` reproduce turnos con guion a través de un objeto falso
que imita `AsyncAnthropic.messages.stream`. Así, la suite es determinista,
se ejecuta sin conexión, no cuesta nada y aun así cubre los caminos que
importan: el camino de streaming y el bucle completo de herramientas,
incluido un turno en el que se llama a una herramienta y después el modelo
responde.

Este es el patrón que conviene mantener a medida que amplíes el agente.
Probar una integración LLM contra el modelo real te da una suite lenta,
inestable y cara que, aun así, no puede afirmar lo que dirá el modelo.
Probar el *bucle* contra un cliente con guion afirma exactamente lo que tú
escribiste.

## Paso 9: Puntos de extensión

- **Historial persistente** — implementa `ConversationStore` sobre Redis o
  una base de datos (Paso 7).
- **RAG** — la recuperación queda deliberadamente fuera del alcance de la
  plantilla. El punto de unión natural es `ChatAgent.stream`: obtén el
  contexto antes de la primera petición y antepónlo al system prompt, o
  expón tu índice como una herramienta más y deja que el modelo decida
  cuándo buscar.
- **Autenticación y rate limiting** — `POST /chat` viene sin autenticación.
  Añade una dependencia al router antes de exponerlo públicamente; el
  [tutorial de Autenticación JWT](auth-jwt.md) tiene los guards que
  reutilizarías.

## Resumen

- **Generación**: `fastkit startdemo fastapi-llm-agent`, define
  `ANTHROPIC_API_KEY`, `bash scripts/run-server.sh`.
- **Streaming**: SSE con eventos `token` / `tool_use` / `tool_result` /
  `usage` / `done` / `error`.
- **Bucle**: stream → llamadas a herramientas → resultados de vuelta en un
  único mensaje de usuario → repetir, limitado por `MAX_TOOL_ITERATIONS`.
- **Herramientas**: un esquema en `TOOL_SCHEMAS` y un handler en
  `TOOL_HANDLERS`; trata la entrada de las herramientas como no confiable.
- **Memoria**: interfaz `ConversationStore`, implementación con
  diccionario, sustitúyela en `get_store()`.
- **Tests**: un cliente falso con guion, así que la suite funciona sin
  conexión y es determinista.

## Siguientes pasos

- [Integración con MCP](mcp-integration.md) — si necesitas un servidor MCP
  en lugar de un agente de chat.
- [Autenticación JWT](auth-jwt.md) — poner cuentas delante del endpoint de
  chat.
- [¿Qué starter elegir?](../user-guide/choosing-a-starter.md)
