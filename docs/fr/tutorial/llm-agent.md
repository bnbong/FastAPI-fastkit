# Agent LLM en streaming avec `fastapi-llm-agent`

Construisez un backend de chat qui diffuse les jetons au fur et à mesure de leur génération et qui peut réellement *agir* — appeler des outils, lire leurs résultats et continuer. Ce tutoriel parcourt le modèle `fastapi-llm-agent` : le protocole d'événements SSE, la boucle d'appels d'outils et son plafond d'itérations, la mémoire de conversation derrière une interface, et une suite de tests qui ne touche jamais au réseau.

## Ce que vous apprendrez

- Générer un projet avec `fastkit startdemo fastapi-llm-agent`
- Les types d'événements SSE qu'un client doit gérer, et ce que chacun signifie
- Comment fonctionne, étape par étape, un tour de la boucle d'appels d'outils
- Ajouter votre propre outil
- Remplacer le stockage de conversations en mémoire du processus par un vrai stockage
- Pourquoi les tests sont déterministes et gratuits à exécuter

## Prérequis

- Python 3.12+
- FastAPI-fastkit installé (`pip install fastapi-fastkit`)
- Une clé d'API Anthropic — uniquement pour dialoguer avec un vrai modèle. La suite de tests générée s'exécute sans clé.
- Être familier avec `async`/`await` et les générateurs asynchrones

## Étape 1 : Générer et configurer

```console
$ fastkit startdemo fastapi-llm-agent
Enter the project name: support-agent
Enter the author name: Developer Kim
Enter the author email: developer@example.com
Enter the project description: Streaming support assistant
Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y
```

Placez votre clé dans `.env` avant le premier lancement :

```bash
ANTHROPIC_API_KEY=sk-ant-...
LLM_MODEL=claude-sonnet-5
LLM_MAX_TOKENS=4096
MAX_TOOL_ITERATIONS=5
```

La clé est lue par pydantic-settings et transmise au client lors de sa construction. Elle n'est jamais écrite dans le code source ni intégrée à l'image Docker.

```console
$ cd support-agent
$ bash scripts/run-server.sh
$ bash scripts/chat.sh "What is 12 * 34?"
```

!!! tip "Utiliser une passerelle au lieu de l'API Anthropic"
    Définissez `LLM_BASE_URL` (et `LLM_AUTH_TOKEN` si la passerelle utilise une authentification bearer) pour pointer vers LiteLLM, un proxy interne ou un serveur local. Le format d'échange reste l'API Messages d'Anthropic ; la traduction vers d'autres fournisseurs relève de la passerelle, pas de l'application.

## Étape 2 : L'arborescence générée

```
support-agent/
├── pyproject.toml              # métadonnées PEP 621 + [tool.fastapi-fastkit]
├── requirements.txt
├── Dockerfile
├── .env
├── scripts/
│   ├── chat.sh                 # envoie un message à un serveur en cours d'exécution
│   ├── format.sh  lint.sh  run-server.sh  test.sh
├── src/
│   └── app/
│       ├── main.py             # application FastAPI + lifespan
│       ├── core/config.py      # pydantic-settings (la clé d'API se trouve ici)
│       ├── llm/
│       │   ├── client.py       # fabrique AsyncAnthropic
│       │   ├── tools.py        # schémas d'outils + gestionnaires
│       │   └── agent.py        # agent en streaming + boucle d'outils
│       ├── memory/
│       │   ├── base.py         # interface ConversationStore
│       │   └── in_memory.py    # implémentation locale au processus
│       ├── schemas/chat.py     # corps de requête + enveloppe d'événement SSE
│       └── api/
│           ├── router.py       # regroupe la santé et le chat
│           ├── deps.py         # dépendances store / agent
│           ├── health.py       # GET /health
│           └── chat.py         # POST /chat (SSE), historique des conversations
└── tests/
    ├── conftest.py             # faux client Anthropic scénarisé
    ├── test_health.py  test_chat.py  test_tools.py  test_memory.py
```

Trois frontières méritent d'être remarquées d'emblée : le **client** est créé par une fabrique (les tests peuvent donc en substituer un), la **mémoire** est une interface dotée d'une implémentation triviale (la production peut donc en substituer une), et les **outils** sont une liste de schémas plus un dictionnaire de gestionnaires (en ajouter un ne touche donc qu'un seul fichier).

## Étape 3 : Les points d'extrémité

| Méthode | Point d'extrémité            | Description                       |
|---------|------------------------------|-----------------------------------|
| GET     | `/api/v1/health`             | Sonde de vivacité                 |
| POST    | `/api/v1/chat`               | Diffuser une réponse en SSE       |
| GET     | `/api/v1/conversations/{id}` | Lire l'historique enregistré      |
| DELETE  | `/api/v1/conversations/{id}` | Oublier une conversation          |

`POST /api/v1/chat` accepte `{"message": "...", "conversation_id": "..."}`. Omettez `conversation_id` pour démarrer une nouvelle conversation, puis récupérez l'identifiant attribué dans l'événement `done` final.

## Étape 4 : Le protocole de flux

Chaque message SSE porte son type dans le champ `event:` et une enveloppe JSON dans `data:`. Un client doit en gérer cinq, plus les erreurs :

| Événement     | Champs                          | Signification                         |
|---------------|---------------------------------|---------------------------------------|
| `token`       | `text`                          | Un fragment de la réponse de l'assistant |
| `tool_use`    | `tool_name`, `tool_input`       | Claude a demandé un outil             |
| `tool_result` | `tool_name`, `tool_output`      | L'outil s'est exécuté                 |
| `usage`       | `input_tokens`, `output_tokens` | Consommation de jetons par tour       |
| `done`        | `conversation_id`               | Le tour est terminé                   |
| `error`       | `detail`                        | Un échec est survenu en cours de flux |

`tool_use` et `tool_result` ne sont pas décoratifs — ce sont eux qui permettent à une interface d'afficher « recherche… » au lieu d'une pause inexpliquée pendant l'exécution d'un outil.

L'utilisation des jetons est également écrite dans le logger `app.agent` à chaque tour : la consommation est donc visible dans les journaux du serveur sans instrumenter de client.

## Étape 5 : Un tour de boucle

`ChatAgent.stream` dans `src/app/llm/agent.py` constitue tout le moteur. Un tour se déroule ainsi :

1. Charger l'historique de la conversation depuis le stockage.
2. Ouvrir une requête en streaming avec l'historique, le nouveau message de l'utilisateur et les schémas d'outils.
3. Émettre chaque fragment de texte sous forme d'événement `token` dès son arrivée.
4. À la fin du flux, lire le message final ; émettre un événement `usage` et journaliser le nombre de jetons.
5. **Si `stop_reason != "tool_use"`,** l'assistant a terminé : enregistrer le tour, émettre `done`, retourner.
6. **Sinon,** pour chaque bloc `tool_use` : émettre `tool_use`, exécuter le gestionnaire, émettre `tool_result` et collecter la sortie.
7. Renvoyer tous les résultats d'outils dans un unique message `user` — c'est ce qu'exige l'API Messages — et reprendre à l'étape 2.

La boucle est bornée par `MAX_TOOL_ITERATIONS` (5 par défaut). Si Claude continue de demander des outils au-delà du plafond, le tour est enregistré, un avertissement est journalisé et un événement `error` est émis, plutôt que de laisser le serveur tourner en boucle :

```python
yield AgentEvent(
    type="error",
    detail=(
        "The assistant exceeded the tool-call limit of "
        f"{self._max_tool_iterations} iterations."
    ),
)
```

Un tel plafond n'a rien de facultatif dans une boucle d'agent. Sans lui, un modèle qui comprend mal le résultat d'un outil peut vous facturer indéfiniment.

## Étape 6 : Les outils fournis

| Outil          | Rôle                                                              |
|----------------|-------------------------------------------------------------------|
| `calculator`   | Arithmétique, analysée en AST avec liste blanche — pas `eval`     |
| `current_time` | Heure actuelle dans un fuseau horaire IANA                        |

Le `calculator` mérite qu'on s'y attarde. Il analyse l'expression avec `ast` et ne parcourt que des types de nœuds en liste blanche : un argument d'outil provenant d'un modèle ne peut donc pas exécuter de Python arbitraire. Tout outil qui accepte une entrée générée par un modèle a besoin de la même rigueur : **la sortie d'un modèle est une entrée non fiable.**

### Ajouter un outil

Tout se trouve dans `src/app/llm/tools.py` :

1. Ajoutez un schéma à `TOOL_SCHEMAS` — `name`, `description` et un `input_schema` au format JSON Schema.
2. Enregistrez le gestionnaire dans `TOOL_HANDLERS` sous le même nom.

Deux points à soigner :

- **La description est la seule instruction que Claude reçoit** sur le moment où recourir à l'outil. C'est de l'ingénierie de prompt, pas de la documentation — des descriptions vagues produisent des outils jamais appelés, ou appelés en permanence.
- **Les gestionnaires doivent renvoyer une chaîne et transformer leurs propres échecs en message lisible** plutôt que de lever une exception. La boucle renvoie ce texte tel quel au modèle : « aucune ville nommée X n'a été trouvée » permet au modèle de se rattraper, alors qu'une exception met fin au tour.

## Étape 7 : La mémoire de conversation

`ConversationStore` (`src/app/memory/base.py`) est l'interface ; le fichier `in_memory.py` fourni l'implémente avec un dictionnaire. Cela convient pour un processus unique et ne convient pour rien d'autre — un redémarrage efface tout, et deux workers ne s'accordent pas sur l'historique.

Pour en faire un vrai stockage : implémentez la même interface au-dessus de Redis ou d'une base de données, et renvoyez-la depuis `get_store()` dans `src/app/api/deps.py`. Rien ne change dans l'agent ni dans les routeurs, car aucun des deux ne nomme jamais la classe concrète.

## Étape 8 : Les tests

```console
$ bash scripts/test.sh    # or: pytest
```

`tests/conftest.py` rejoue des tours scénarisés à travers une imitation de `AsyncAnthropic.messages.stream`. La suite est ainsi déterministe, s'exécute hors ligne, ne coûte rien et couvre tout de même les chemins qui comptent : le chemin de streaming et la boucle d'outils complète, y compris un tour où un outil est appelé puis où le modèle répond.

C'est le modèle à conserver lorsque vous étendez l'agent. Tester une intégration LLM contre le modèle réel donne une suite lente, instable et coûteuse, qui ne peut toujours pas vérifier ce que le modèle dira. Tester la *boucle* contre un client scénarisé vérifie exactement ce que vous avez écrit.

## Étape 9 : Points d'extension

- **Historique persistant** — implémentez `ConversationStore` au-dessus de Redis ou d'une base de données (étape 7).
- **RAG** — la recherche documentaire est délibérément hors du périmètre du modèle. Le point d'insertion naturel est `ChatAgent.stream` : récupérez le contexte avant la première requête et ajoutez-le en tête du prompt système, ou exposez votre index comme un outil supplémentaire et laissez le modèle décider quand chercher.
- **Authentification et limitation de débit** — tel qu'il est livré, `POST /chat` n'est pas authentifié. Ajoutez une dépendance au routeur avant de l'exposer publiquement ; le [tutoriel Authentification JWT](auth-jwt.md) contient les gardes que vous réutiliseriez.

## Récapitulatif

- **Génération** : `fastkit startdemo fastapi-llm-agent`, définir `ANTHROPIC_API_KEY`, `bash scripts/run-server.sh`.
- **Streaming** : SSE avec les événements `token` / `tool_use` / `tool_result` / `usage` / `done` / `error`.
- **Boucle** : flux → appels d'outils → résultats renvoyés dans un seul message utilisateur → répétition, bornée par `MAX_TOOL_ITERATIONS`.
- **Outils** : un schéma dans `TOOL_SCHEMAS` et un gestionnaire dans `TOOL_HANDLERS` ; traitez l'entrée des outils comme non fiable.
- **Mémoire** : interface `ConversationStore`, implémentation par dictionnaire, à remplacer dans `get_store()`.
- **Tests** : un faux client scénarisé, de sorte que la suite est hors ligne et déterministe.

## Pour aller plus loin

- [Intégration MCP](mcp-integration.md) — si vous avez besoin d'un serveur MCP plutôt que d'un agent de chat.
- [Authentification JWT](auth-jwt.md) — placer des comptes devant le point d'extrémité de chat.
- [Quel starter choisir ?](../user-guide/choosing-a-starter.md)
