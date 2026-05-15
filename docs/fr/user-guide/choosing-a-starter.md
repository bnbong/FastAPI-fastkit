# Quel starter choisir ?

FastAPI-fastkit propose plusieurs façons d'amorcer un projet. Cette page est une **aide à la décision** pour les nouveaux venus : choisissez un chemin ici, puis allez sur [Démarrage rapide](quick-start.md) pour créer concrètement le projet.

Si vous hésitez, la réponse courte est :

> **Commencez par `fastkit init --interactive` et sélectionnez le préréglage `domain-starter`.** C'est l'option recommandée pour les projets d'API modernes.

Le reste de cette page explique pourquoi, et quand opter pour autre chose.

## TL;DR — choisir selon le profil d'utilisateur

| Vous êtes... | Commencez avec |
|---|---|
| Nouveau sur FastAPI, vous voulez une démonstration guidée | `fastkit init --interactive` (préréglage : **`domain-starter`**) |
| Vous voulez une démo CRUD fonctionnelle à lire et modifier | `fastkit startdemo fastapi-default` |
| Vous voulez le squelette le plus minimal possible | `fastkit init --interactive` (préréglage : **`minimal`**) |
| Vous écrivez un prototype rapide ou un script monofichier | `fastkit init --interactive` (préréglage : **`single-module`**) |
| Vous avez besoin d'une vraie base de données (PostgreSQL + SQLAlchemy + Alembic) | `fastkit startdemo fastapi-psql-orm` |
| Vous voulez une disposition orientée domaine pour une API de taille moyenne | `fastkit init --interactive` (préréglage : **`domain-starter`**) |

## `startdemo` vs `init --interactive` — quelle différence ?

Ce sont les deux points d'entrée principaux. Ils répondent à des besoins différents.

### `fastkit startdemo <template>`

Dépose sur disque un projet d'**exemple complet et fonctionnel** basé sur l'un des modèles livrés (`fastapi-default`, `fastapi-async-crud`, `fastapi-psql-orm`, `fastapi-domain-starter`, …). Le code source du modèle est copié tel quel, avec les emplacements de métadonnées (`<project_name>`, etc.) remplis.

- ✅ Le chemin le plus rapide vers une démo exécutable.
- ✅ Tout le code est réel et lisible — idéal pour apprendre par l'exemple.
- ❌ La pile et la structure du modèle sont fixes ; impossible de choisir CORS mais d'abandonner l'authentification au passage.

```console
$ fastkit list-templates              # show what's available
$ fastkit startdemo fastapi-default   # generate a project from one
```

### `fastkit init --interactive`

Vous guide à travers un **assistant pas à pas** : métadonnées du projet → préréglage d'architecture → sélections de fonctionnalités (base de données, authentification, tests, déploiement, …) → gestionnaire de paquets → confirmation. Le générateur choisit un modèle de base approprié par préréglage et superpose les fonctionnalités sélectionnées.

- ✅ Vous assemblez exactement la pile que vous voulez.
- ✅ Le préréglage d'architecture façonne la disposition du projet (monofichier, en couches, orientée domaine, …).
- ❌ Les préréglages les plus complets qui conservent `main.py` (`classic-layered`, `domain-starter`) génèrent bien les modules de configuration, mais vous laissent les raccorder vous-même aux routeurs fournis. Consultez la [Matrice des préréglages d'architecture](../reference/preset-feature-matrix.md) pour voir précisément ce que couvre chaque préréglage et chaque fonctionnalité.

```console
$ fastkit init --interactive
```

## Les quatre préréglages d'architecture

Ils apparaissent dans `fastkit init --interactive` après les invites de saisie des informations du projet. Utilisez cette section pour décider lequel choisir.

### `minimal` — commencer au plus simple, étoffer plus tard

L'application FastAPI la plus légère possible. On part d'un squelette vide avec un unique `src/main.py`, régénéré à partir des fonctionnalités que vous sélectionnez. CORS, limitation de débit et instrumentation Prometheus sont ajoutés automatiquement à `main.py` lorsqu'ils sont choisis.

- 👤 **Pour qui** : les personnes qui veulent ajouter elles-mêmes de la structure au fur et à mesure, ou qui explorent FastAPI sans a priori sur la disposition.
- 📦 **Modèle de base** : `fastapi-empty`.
- 🧠 **Modèle mental** : « donnez-moi un seul fichier avec FastAPI importé et laissez-moi faire le reste. »

### `single-module` — prototype façon script

Tout vit dans un seul module. Même superposition de régénération de `main.py` que `minimal`.

- 👤 **Pour qui** : écrire un script glue, un petit webhook ou un prototype d'une journée qui n'a pas besoin de frontières de package.
- 📦 **Modèle de base** : `fastapi-single-module`.
- 🧠 **Modèle mental** : « je veux un seul fichier Python que je peux exécuter et lire d'une traite. »

### `classic-layered` — découpe en couches (api / crud / schemas / core)

La disposition « à la Django » : le code est réparti horizontalement par rôle. Les routeurs vont dans `api/`, la logique CRUD dans `crud/`, les schémas Pydantic dans `schemas/` et la configuration dans `core/`. Le `main.py` fourni par le modèle est **conservé** (il gère déjà CORS) ; les fichiers de configuration générés pour la base de données et l'authentification sont placés dans `src/core/`.

- 👤 **Pour qui** : équipes familières des dispositions de type Django/Rails, projets avec de nombreux petits points d'extrémité partageant une plomberie CRUD commune.
- 📦 **Modèle de base** : `fastapi-default`.
- 🧠 **Modèle mental** : « découper le code selon ce qu'il _est_. »

### `domain-starter` — orienté domaine (option recommandée)

Le code est organisé verticalement par **concept métier** : chaque domaine possède son propre routeur, son service, son dépôt et ses schémas dans `src/app/domains/<concept>/`. Le modèle inclut aussi un endpoint `/health` et un domaine d'exemple `items`, que vous pouvez copier et renommer pour chaque nouveau concept. Le `main.py` fourni (sous `src/app/`) est conservé ; les fichiers de configuration générés sont placés dans `src/app/core/`.

- 👤 **Pour qui** : les API de taille moyenne qui vont accueillir plusieurs concepts distincts (users, orders, billing, …). C'est l'option moderne recommandée.
- 📦 **Modèle de base** : `fastapi-domain-starter`.
- 🧠 **Modèle mental** : « découper le code selon ce qu'il _fait_ pour le métier. »

## Matrice de comparaison

Une vue côte à côte d'un coup d'œil.

| | `minimal` | `single-module` | `classic-layered` | `domain-starter` |
|---|---|---|---|---|
| Modèle de base | `fastapi-empty` | `fastapi-single-module` | `fastapi-default` | `fastapi-domain-starter` |
| Point d'entrée du projet | `src/main.py` | `src/main.py` | `src/main.py` | `src/app/main.py` |
| Emplacement des routeurs | (vous les ajoutez) | (à l'intérieur de `main.py`) | `src/api/routes/` | `src/app/domains/<concept>/router.py` |
| Dossiers par domaine | ❌ | ❌ | ❌ | ✅ |
| Point d'extrémité `/health` intégré | ✅ | ✅ | ❌ | ✅ |
| `main.py` régénéré à partir des fonctionnalités | ✅ | ✅ | ❌ | ❌ |
| CORS pré-câblé dans `main.py` | ajouté si sélectionné | ajouté si sélectionné | oui (piloté par env) | oui (piloté par env) |
| pyproject d'abord | optionnel | optionnel | optionnel | ✅ |
| Idéal pour | « je ferai évoluer ma propre structure » | « prototype monofichier » | « découper par préoccupation » | « découper par concept métier » |

Pour le contrat complet par fonctionnalité (chemins cibles de configuration base de données / authentification, sélections nécessitant un câblage manuel vs automatique, déclenchement des avertissements), consultez la [Matrice des préréglages d'architecture](../reference/preset-feature-matrix.md).

## Choisir un modèle `startdemo`

`fastkit startdemo <template>` est idéal quand vous voulez un **exemple complet et exécutable** plutôt qu'un assemblage guidé. La plupart des modèles correspondent grossièrement à l'un des quatre préréglages ci-dessus, mais ils embarquent du code d'exemple supplémentaire (points d'extrémité CRUD sur un magasin factice, gestion de réponses personnalisée, outillage Docker, etc.).

| Modèle | Préréglage le plus proche | Quand le choisir |
|---|---|---|
| `fastapi-default` | `classic-layered` | Démo CRUD fonctionnelle avec la disposition en couches. Bon point de départ. |
| `fastapi-empty` | `minimal` | Squelette nu ; même forme que celle obtenue par `minimal`. |
| `fastapi-single-module` | `single-module` | Démo monofichier. |
| `fastapi-domain-starter` | `domain-starter` | Valeur par défaut moderne recommandée ; livré avec un exemple de domaine items. |
| `fastapi-async-crud` | `classic-layered` | Équivalent asynchrone de `fastapi-default`. |
| `fastapi-custom-response` | `classic-layered` | Illustre les enveloppes / formats de réponses personnalisés. |
| `fastapi-dockerized` | `classic-layered` | Ajoute un Dockerfile prêt pour la production à la disposition par défaut. |
| `fastapi-psql-orm` | (aucun préréglage direct) | PostgreSQL + SQLAlchemy + Alembic. À choisir lorsque vous avez besoin d'une vraie base de données. |
| `fastapi-mcp` | (aucun préréglage direct) | Intégration du Model Context Protocol. |

`fastkit list-templates` affiche la liste à jour avec une description en une ligne.

## Questions fréquentes

**Q. Faut-il choisir un préréglage / modèle dès le départ ?**
Non — vous pouvez toujours réorganiser le code généré à la main par la suite. Les préréglages sont des points de départ, pas des contrats. Ne sur-réfléchissez pas ce choix.

**Q. Quel est le choix « moderne » ?**
`domain-starter`. Il adopte une approche pyproject-first, fournit un endpoint `/health` et suit la structure vers laquelle convergent la plupart des projets FastAPI de taille moyenne bien entretenus.

**Q. Puis-je passer de `classic-layered` à `domain-starter` plus tard ?**
Oui, mais c'est un refactoring manuel — il n'existe pas de commande de migration. Si vous pensez que votre projet grandira au point de nécessiter des dossiers par domaine, commencez directement par là.

**Q. Et si je veux simplement apprendre FastAPI ?**
Commencez avec `fastkit startdemo fastapi-default` — lisez le code, exécutez les tests, modifiez quelques points d'extrémité. Une fois à l'aise, `fastkit init --interactive` avec le préréglage `domain-starter` est l'étape suivante naturelle.

**Q. Où voir les fichiers exacts générés par chaque préréglage ?**
La [Matrice des préréglages d'architecture](../reference/preset-feature-matrix.md) est la page de référence à ce sujet.

## Étapes suivantes

- [Démarrage rapide](quick-start.md) — créer concrètement votre premier projet.
- [Créer des projets](creating-projects.md) — visite plus approfondie des drapeaux du CLI.
- [Tutoriel Projet orienté domaine](../tutorial/domain-starter.md) — si vous avez choisi `domain-starter`, vous y trouverez un parcours complet de l'arborescence générée, de l'exemple `items` fourni et de la façon d'ajouter votre prochain domaine.
- [Matrice des préréglages d'architecture](../reference/preset-feature-matrix.md) — le contrat complet par préréglage / par fonctionnalité.
