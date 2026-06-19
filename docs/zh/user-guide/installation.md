# 安装

本指南介绍如何安装 FastAPI-fastkit。

## 系统要求

要使用 FastAPI-fastkit,您需要满足以下条件：

- **Python**:3.12 或更高版本
- **操作系统**:支持 Windows、macOS、Linux

## 安装方式

### 使用 pip 安装(推荐)

最简单的方式是：

<div class="termy">

```console
$ pip install FastAPI-fastkit
---> 100%
Successfully installed FastAPI-fastkit
```

</div>

### 安装指定版本

如果要安装指定版本：

<div class="termy">

```console
$ pip install FastAPI-fastkit==1.0.0
---> 100%
Successfully installed FastAPI-fastkit-1.0.0
```

</div>

### 安装开发版

直接从 GitHub 安装最新的开发版本:

<div class="termy">

```console
$ pip install git+https://github.com/bnbong/FastAPI-fastkit.git
---> 100%
Successfully installed FastAPI-fastkit
```

</div>

!!! warning "开发版警告"
    开发版可能不稳定,不建议用于生产环境。

## 配置虚拟环境(推荐)

强烈建议使用虚拟环境,以避免依赖冲突：

### 使用 venv

<div class="termy">

```console
$ python -m venv fastapi-env
$ source fastapi-env/bin/activate  # Linux/macOS
$ fastapi-env\Scripts\activate     # Windows
$ pip install FastAPI-fastkit
```

</div>

### 使用 conda

<div class="termy">

```console
$ conda create -n fastapi-env python=3.12
$ conda activate fastapi-env
$ pip install FastAPI-fastkit
```

</div>

## 校验安装

安装完成后,请确认 FastAPI-fastkit 已正确安装：

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

## 故障排查

### 找不到命令

若出现 “command not found” 错误:

1. **确认 FastAPI-fastkit 已安装**:

   <div class="termy">
   ```console
   $ pip show FastAPI-fastkit
   ```
   </div>

2. **检查虚拟环境**:

   <div class="termy">
   ```console
   $ which python
   $ which pip
   ```
   </div>

3. **重新安装 FastAPI-fastkit**:

   <div class="termy">
   ```console
   $ pip uninstall FastAPI-fastkit
   $ pip install FastAPI-fastkit
   ```
   </div>

### 权限错误

若在安装过程中遇到权限错误:

**在 Linux/macOS 上:**

<div class="termy">

```console
$ pip install --user FastAPI-fastkit
```

</div>

**在 Windows 上(以管理员身份运行):**

<div class="termy">

```console
$ pip install FastAPI-fastkit
```

</div>

### Python 版本兼容性

FastAPI-fastkit 需要 Python 3.12 及以上版本。请先检查当前 Python 版本：

<div class="termy">

```console
$ python --version
Python 3.12.0
```

</div>

如果版本较旧,请升级 Python：

- **官方 Python**:[python.org/downloads](https://www.python.org/downloads/)
- **使用 pyenv**:`pyenv install 3.12.0`
- **使用 conda**:`conda install python=3.12`

## 下一步

安装完成后:

1. **[快速上手](quick-start.md)**:5 分钟内创建您的第一个项目
2. **[入门教程](../tutorial/getting-started.md)**:分步详细教程
3. **[CLI 参考](cli-reference.md)**:完整的命令参考

!!! tip "安装小贴士"
    - 始终使用虚拟环境隔离不同项目
    - 让 FastAPI-fastkit 保持最新
    - 查看 [GitHub 仓库](https://github.com/bnbong/FastAPI-fastkit) 获取更新与问题反馈
