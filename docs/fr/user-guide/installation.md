# Installation

Ce guide explique comment installer FastAPI-fastkit.

## Prérequis

Pour utiliser FastAPI-fastkit, vous devez remplir les conditions suivantes :

- **Python** : 3.12 ou supérieur
- **Système d'exploitation** : Windows, macOS, Linux pris en charge

## Méthodes d'installation

### Installation avec pip (recommandée)

La méthode d'installation la plus simple :

<div class="termy">

```console
$ pip install FastAPI-fastkit
---> 100%
Successfully installed FastAPI-fastkit
```

</div>

### Installer une version spécifique

Pour installer une version précise :

<div class="termy">

```console
$ pip install FastAPI-fastkit==1.0.0
---> 100%
Successfully installed FastAPI-fastkit-1.0.0
```

</div>

### Installer la version de développement

Pour installer la dernière version de développement directement depuis GitHub :

<div class="termy">

```console
$ pip install git+https://github.com/bnbong/FastAPI-fastkit.git
---> 100%
Successfully installed FastAPI-fastkit
```

</div>

!!! warning "Avertissement sur la version de développement"
    Les versions de développement peuvent être instables et ne sont pas recommandées pour les environnements de production.

## Configuration d'un environnement virtuel (recommandée)

Il est fortement recommandé d'utiliser un environnement virtuel pour éviter les conflits de dépendances :

### Avec venv

<div class="termy">

```console
$ python -m venv fastapi-env
$ source fastapi-env/bin/activate  # Linux/macOS
$ fastapi-env\Scripts\activate     # Windows
$ pip install FastAPI-fastkit
```

</div>

### Avec conda

<div class="termy">

```console
$ conda create -n fastapi-env python=3.12
$ conda activate fastapi-env
$ pip install FastAPI-fastkit
```

</div>

## Vérifier l'installation

Après l'installation, vérifiez que FastAPI-fastkit est correctement installé :

<div class="termy">

```console
$ fastkit --version
FastAPI-fastkit version 1.0.0
```

</div>

<div class="termy">

```console
$ fastkit --help
Usage: fastkit [OPTIONS] COMMAND [ARGS]...

  FastAPI-fastkit CLI

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  addroute       Add a new route to FastAPI project
  init           Create a new FastAPI project
  list-templates List available FastAPI templates
  runserver      Start FastAPI development server
  startdemo      Create FastAPI project from template
```

</div>

## Dépannage

### Commande introuvable

Si vous obtenez une erreur « command not found » :

1. **Vérifiez que FastAPI-fastkit est bien installé** :

   <div class="termy">
   ```console
   $ pip show FastAPI-fastkit
   ```
   </div>

2. **Vérifiez votre environnement virtuel** :

   <div class="termy">
   ```console
   $ which python
   $ which pip
   ```
   </div>

3. **Réinstallez FastAPI-fastkit** :

   <div class="termy">
   ```console
   $ pip uninstall FastAPI-fastkit
   $ pip install FastAPI-fastkit
   ```
   </div>

### Erreurs de permission

Si vous rencontrez des erreurs de permission lors de l'installation :

**Sous Linux/macOS :**

<div class="termy">

```console
$ pip install --user FastAPI-fastkit
```

</div>

**Sous Windows (exécutez en tant qu'administrateur) :**

<div class="termy">

```console
$ pip install FastAPI-fastkit
```

</div>

### Compatibilité des versions de Python

FastAPI-fastkit nécessite Python 3.12+. Vérifiez votre version de Python :

<div class="termy">

```console
$ python --version
Python 3.12.0
```

</div>

Si vous avez une version plus ancienne, mettez Python à niveau :

- **Python officiel** : [python.org/downloads](https://www.python.org/downloads/)
- **Avec pyenv** : `pyenv install 3.12.0`
- **Avec conda** : `conda install python=3.12`

## Étapes suivantes

Une fois l'installation terminée :

1. **[Démarrage rapide](quick-start.md)** : créez votre premier projet en 5 minutes
2. **[Tutoriel de prise en main](../tutorial/getting-started.md)** : tutoriel détaillé pas à pas
3. **[Référence CLI](cli-reference.md)** : référence complète des commandes

!!! tip "Astuces d'installation"
    - Utilisez toujours des environnements virtuels pour isoler vos projets
    - Maintenez FastAPI-fastkit à jour vers la dernière version
    - Consultez le [dépôt GitHub](https://github.com/bnbong/FastAPI-fastkit) pour les mises à jour et les tickets
