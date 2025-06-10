# 什么是uv

简单来说，`uv` 是一个用 Rust 语言编写的、超级快的 Python 包安装和项目管理工具。你可以把它看作是 `pip`（我们常用的包安装工具）和 `venv`（创建虚拟环境的工具）的 “高速合体版”！

1. 节省时间：安装包的速度真的快到飞起！尤其是在安装很多包或者大型包（比如数据科学库）时，感受会非常明显。告别漫长的等待！
2. 简化操作：以前可能需要先用 `venv` 创建环境，再用 `pip` 安装包。`uv` 把这些常用操作整合起来了，一个命令就能搞定很多事。

官网地址：

- Astral (uv 的开发公司) 官网: https://astral.sh/
- uv GitHub 仓库: https://github.com/astral-sh/uv

# 安装uv

安装 `uv` 非常简单。打开你的终端（Windows 用户可能是 CMD 或 PowerShell，Mac/Linux 用户是 Terminal）：

- macOS / Linux:

  ```sh
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

- Windows (PowerShell):

  ```powershell
  irm https://astral.sh/uv/install.ps1 | iex
  ```

如果windows上遇到网络问题：

~~~powershell
powershell -ExecutionPolicy Bypass -c "irm https://gitee.com/jk01/uv/releases/download/0.6.14/uv-installer.ps1 | iex"
~~~

安装完成查看版本：

~~~sh
uv --version
~~~

> 注意：
>
> - windows上使用uv时，在pycharm创建新项目时，“解释器类型”选择“自定义环境”，“类型”选择“uv”，基础python选择uv安装的python路径
> - vscode中：按 Ctrl+Shift+P (或 Cmd+Shift+P on Mac) 打开命令面板，输入 Python: Select Interpreter (Python: 选择解释器)。在弹出的列表中，选择你用 uv 安装的 Python 3.10 版本。VS Code 通常会自动检测到。如果没找到，可以手动 "Enter interpreter path..." 指定路径。然后在终端中输入`uv venv`来激活虚拟环境。

# 实战入门

`uv` 的设计目标之一就是尽量兼容 `pip` 的使用习惯。让我们看看最常见的操作怎么用 `uv` 实现。

## 安装python

首先，用uv安装Python，以便后续创建虚拟环境，安装过程可能需要10分钟。

```sh
uv python install 3.10
```

> 建议安装3.10版本，3.11、3.12也可以，根据实际需要，后续文章会逐步讲

## 创建venv

想象一下，你在同时做好几个 Python 项目，每个项目可能需要不同版本的库。为了不让它们互相“打架”，我们需要为每个项目创建一个独立的“隔离区”，这就是 虚拟环境。

以前我们用：`python -m venv .venv` （`.venv` 是通常的虚拟环境文件夹名）

现在用 `uv`：

```sh
uv venv
```

这条命令会在你的当前目录下创建一个名为 `.venv` 的文件夹，里面包含了特定于这个项目的 Python 解释器和包。是不是更简洁了？

## 激活venv

创建好环境后，你需要“走进去”才能使用它。这叫 激活 环境。

- macOS / Linux (Bash/Zsh):

  ```sh
  source .venv/bin/activate
  ```

- Windows (CMD):

  ```sh
  .venv\Scripts\activate.bat
  ```

- Windows (PowerShell):

  ```sh
  .venv\Scripts\Activate.ps1
  ```

  (如果 PowerShell 提示执行策略问题，可能需要先运行 `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`)

激活成功后，你会看到命令行提示符前面多了 `(.venv)` 的字样，表示你现在在这个虚拟环境里了。

## 安装python包

假设你想安装一个用于网络请求的常用库 `requests`。

以前我们用：`pip install requests`

现在用 `uv`（请确保你的虚拟环境已激活）：

```sh
uv pip install requests
```

`uv` 可能在几秒甚至更短的时间内就完成了 `pip` 可能需要几十秒甚至几分钟的工作！

想一次安装多个包？

```sh
uv pip install requests beautifulsoup4 pandas
```

## 管理项目依赖

当你的项目越来越复杂，或者你想分享给别人时，需要一个清单告诉大家你用了哪些包。这个清单通常是 `requirements.txt` 文件。

- 生成依赖清单 (冻结环境):
  以前：`pip freeze > requirements.txt`

  现在：

  ```sh
  uv pip freeze > requirements.txt
  ```

  这会把你当前环境（`.venv`里）安装的所有包及其版本号记录到 `requirements.txt` 文件里。

- 根据清单安装依赖:

  假设你拿到了别人的项目，或者在新电脑上配置旧项目，可以用清单来安装所有必需的包。

  以前：`pip install -r requirements.txt`

  现在：

  ```sh
  uv pip install -r requirements.txt
  ```

  `uv` 会读取文件内容，并飞快地帮你装好所有依赖！

## 查看已安装的包

想看看当前环境里都装了哪些依赖？

以前：`pip list`

现在：

```sh
uv pip list
```

## 退出venv

当你完成了在这个项目上的工作，想要退出虚拟环境时：

```sh
deactivate
```

命令行前面的 `(.venv)` 就会消失。

# 对比

| 功能         | `pip` + `venv` (`python -m venv`) | `uv`                       | 优势 (uv)            |
| ------------ | --------------------------------- | -------------------------- | -------------------- |
| 创建虚拟环境 | `python -m venv .venv`            | `uv venv`                  | 命令更短             |
| 安装包       | `pip install <package>`           | `uv pip install <package>` | 速度极快 🚀           |
| 从文件安装   | `pip install -r requirements.txt` | `uv pip install -r ...`    | 速度极快 🚀           |
| 生成依赖文件 | `pip freeze > requirements.txt`   | `uv pip freeze > ...`      | 速度快               |
| 查看已安装包 | `pip list`                        | `uv pip list`              | 速度快               |
| 工具         | 两个独立工具 (`pip`, `venv`)      | 一个统一工具 (`uv`)        | 更整合，可能更简单   |
| 底层实现     | Python                            | Rust                       | 性能优势（通常更快） |
