# Installation

This guide explains how to install FastAPI-fastkit.

## Requirements

To use FastAPI-fastkit, you need to meet the following requirements:

- **Python**: 3.12 or higher
- **Operating System**: Windows, macOS, Linux supported

## Installation Methods

### Install with pip (Recommended)

The simplest installation method:

<div class="termy">

```console
$ pip install FastAPI-fastkit
---> 100%
Successfully installed FastAPI-fastkit
```

</div>

### Install Specific Version

To install a specific version:

<div class="termy">

```console
$ pip install FastAPI-fastkit==1.0.0
---> 100%
Successfully installed FastAPI-fastkit-1.0.0
```

</div>

### Install Development Version

To install the latest development version directly from GitHub:

<div class="termy">

```console
$ pip install git+https://github.com/bnbong/FastAPI-fastkit.git
---> 100%
Successfully installed FastAPI-fastkit
```

</div>

!!! warning "Development Version Warning"
    Development versions may be unstable and are not recommended for production environments.

## Virtual Environment Setup (Recommended)

It's highly recommended to use a virtual environment to avoid dependency conflicts:

### Using venv

<div class="termy">

```console
$ python -m venv fastapi-env
$ source fastapi-env/bin/activate  # Linux/macOS
$ fastapi-env\Scripts\activate     # Windows
$ pip install FastAPI-fastkit
```

</div>

### Using conda

<div class="termy">

```console
$ conda create -n fastapi-env python=3.12
$ conda activate fastapi-env
$ pip install FastAPI-fastkit
```

</div>

## Verify Installation

After installation, verify that FastAPI-fastkit is installed correctly:

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

## Troubleshooting

### Command not found

If you get a "command not found" error:

1. **Check if FastAPI-fastkit is installed**:

   <div class="termy">
   ```console
   $ pip show FastAPI-fastkit
   ```
   </div>

2. **Check your virtual environment**:

   <div class="termy">
   ```console
   $ which python
   $ which pip
   ```
   </div>

3. **Reinstall FastAPI-fastkit**:

   <div class="termy">
   ```console
   $ pip uninstall FastAPI-fastkit
   $ pip install FastAPI-fastkit
   ```
   </div>

### Permission errors

If you encounter permission errors during installation:

**On Linux/macOS:**

<div class="termy">

```console
$ pip install --user FastAPI-fastkit
```

</div>

**On Windows (Run as Administrator):**

<div class="termy">

```console
$ pip install FastAPI-fastkit
```

</div>

### Python version compatibility

FastAPI-fastkit requires Python 3.12+. Check your Python version:

<div class="termy">

```console
$ python --version
Python 3.12.0
```

</div>

If you have an older version, please upgrade Python:

- **Official Python**: [python.org/downloads](https://www.python.org/downloads/)
- **With pyenv**: `pyenv install 3.12.0`
- **With conda**: `conda install python=3.12`

## Next Steps

Once installation is complete:

1. **[Quick Start](quick-start.md)**: Create your first project in 5 minutes
2. **[Getting Started Tutorial](../tutorial/getting-started.md)**: Step-by-step detailed tutorial
3. **[CLI Reference](cli-reference.md)**: Complete command reference

!!! tip "Installation Tips"
    - Always use virtual environments for project isolation
    - Keep FastAPI-fastkit updated to the latest version
    - Check the [GitHub repository](https://github.com/bnbong/FastAPI-fastkit) for updates and issues
