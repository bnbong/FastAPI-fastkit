<p align="center">
    <img align="top" width="70%" src="https://bnbong.github.io/projects/img/fastkit_general_logo.png" alt="FastAPI-fastkit"/>
</p>
<p align="center">
<em><b>FastAPI-fastkit</b>: Fast, easy-to-use starter kit for new users of Python and FastAPI</em>
</p>
<p align="center">
<a href="https://pypi.org/project/fastapi-fastkit" target="_blank">
    <img src="https://img.shields.io/pypi/v/fastapi-fastkit" alt="PyPI - Version">
</a>
<a href="https://github.com/bnbong/FastAPI-fastkit/releases" target="_blank">
    <img src="https://img.shields.io/github/v/release/bnbong/FastAPI-fastkit" alt="GitHub Release">
</a>
</p>

---

This project was created to speed up the configuration of the development environment needed to develop Python-based web apps for new users of Python and [FastAPI](https://github.com/fastapi/fastapi).

This project was inspired by the `SpringBoot initializer` & Python Django's `django-admin` cli operation.

## Key Features

- **Immediate FastAPI project creation** : Super-fast FastAPI workspace & project creation via CLI, inspired by `django-admin`feature of [Python Django](https://github.com/django/django)
- **Prettier CLI outputs** : beautiful CLI experiment ([rich library](https://github.com/Textualize/rich) feature)
- **Standards-based FastAPI project template** : All FastAPI-fastkit templates are based on Python standards and FastAPI's common use

## Installation

Install `FastAPI-fastkit` at your Python environment.

<div class="termy">

```console
$ pip install FastAPI-fastkit
---> 100%
```

</div>


## Usage

### Create a new FastAPI project workspace environment immediately

You can now start new FastAPI project really fast with FastAPI-fastkit!

Create a new FastAPI project workspace immediately with:

<div class="termy">

```console
$ fastkit init
Enter the project name: <your-project-name>
Enter the author name: <your-name>
Enter the author email: <your-email>
Enter the project description: <your-project-description>

Available Stacks and Dependencies:
      MINIMAL Stack
┌──────────────┬─────────┐
│ Dependency 1 │ fastapi │
│ Dependency 2 │ uvicorn │
└──────────────┴─────────┘


       STANDARD Stack
┌──────────────┬────────────┐
│ Dependency 1 │ fastapi    │
│ Dependency 2 │ uvicorn    │
│ Dependency 3 │ sqlalchemy │
│ Dependency 4 │ alembic    │
│ Dependency 5 │ pytest     │
└──────────────┴────────────┘


           FULL Stack
┌──────────────┬────────────────┐
│ Dependency 1 │ fastapi        │
│ Dependency 2 │ uvicorn        │
│ Dependency 3 │ sqlalchemy     │
│ Dependency 4 │ alembic        │
│ Dependency 5 │ pytest         │
│ Dependency 6 │ redis          │
│ Dependency 7 │ celery         │
│ Dependency 8 │ docker-compose │
└──────────────┴────────────────┘


Select stack (minimal, standard, full): minimal
  Creating Project:
 new-fastapi-project
┌───────────┬────────┐
│ Component │ Status │
│ fastapi   │ ✓      │
│ uvicorn   │ ✓      │
└───────────┴────────┘
Creating virtual environment...
Installing dependencies...
⠙ Setting up project environment...Collecting <packages~>

---> 100%

╭─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── Success ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ ✨ Dependencies installed successfully                                                                                                                                                                                                                                                │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── Success ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ ✨ FastAPI project '<your-project-name>' has been created successfully and saved to '<your-project-path>'!                                                                                                                                                     │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── Info ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ ℹ To start your project, run 'fastkit runserver' at newly created FastAPI project directory                                                                                                                                                                                           │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

</div>

This command will create a new FastAPI project workspace environment with Python virtual environment.

### Add a new route to the FastAPI project

`FastAPI-fastkit` makes it easy to expand your FastAPI project.

Add a new route endpoint to your FastAPI project with:

<div class="termy">

```console
$ fastkit addroute <your-project-name> <new-route-name>

---> 100%

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── Info ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ ℹ Updated main.py to include the API router                                                                                                                                                                                                                                           │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── Success ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ ✨ Successfully added new route '<new-route-name>' to project '<your-project-name>'.                                                                                                                                                                                                                                   │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

</div>

### Place a structured FastAPI demo project immediately

You can also start with a structured FastAPI demo project.

Demo projects are consist of various tech stacks with simple item CRUD endpoints implemented.

Place a structured FastAPI demo project immediately with:

<div class="termy">

```console
$ fastkit startdemo
Enter the project name: <your-project-name>
Enter the author name: <your-name>
Enter the author email: <your-email>
Enter the project description: <your-project-description>
Deploying FastAPI project using 'fastapi-default' template
Template path:
/<fastapi_fastkit-package-path>/fastapi_project_template/fastapi-defau
lt


                    Project Information
┌──────────────┬──────────────────────────────────────────┐
│ Project Name │ <your-project-name>                      │
│ Author       │ <your-name>                              │
│ Author Email │ <your-email>                             │
│ Description  │ <your-project-description>               │
└──────────────┴──────────────────────────────────────────┘

Do you want to proceed with project creation? [y/N]: y
FastAPI template project will deploy at '<your-project-path>'

---> 100%

╭─────────────────────────────────────────────────────────────────── Success ────────────────────────────────────────────────────────────────────╮
│ ✨ FastAPI project '<your-project-name>' from 'fastapi-default' has been created and saved to                                                  │
│ <your-project-path>!                                                                                                                           │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

</div>

To view the list of available FastAPI demos, check with:

<div class="termy">

```console
$ fastkit list-templates
```

</div>

## Significance of FastAPI-fastkit

FastAPI-fastkit aims to provide a fast and easy-to-use starter kit for new users of Python and FastAPI.

This idea was initiated with the aim of full fill to help FastAPI newcomers to learn from the beginning, which is the production significance of the FastAPI-cli package added with the [FastAPI 0.111.0 version update](https://github.com/fastapi/fastapi/releases/tag/0.111.0).

As one person who has been using and loving FastAPI for a long time, I wanted to develop a project that could help me a little bit to practice [the wonderful motivation](https://github.com/fastapi/fastapi/pull/11522#issuecomment-2264639417) that FastAPI developer [tiangolo](https://github.com/tiangolo) has.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/bnbong/FastAPI-fastkit/blob/main/LICENSE) file for details.
