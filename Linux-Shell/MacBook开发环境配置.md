---
title: MacBook 开发环境配置
tags:
  - macOS
  - homebrew
  - zsh
  - kubectl
  - obsidian
aliases:
  - Mac开发环境
---

# 配置 Zsh 与 Oh My Zsh

macOS 15 默认使用 Zsh。Oh My Zsh 的安装、主题和插件配置集中记录在 [[Linux-Shell/配置zsh终端#macOS 配置|Zsh 终端配置]]，包括此处使用的 `af-magic`、Powerlevel9k/10k、`zsh-syntax-highlighting` 和 `zsh-autosuggestions`。

---

# 安装homebrew

homebrew官网：

```text
英文：
https://brew.sh
中文：
https://brew.sh/index_zh-cn
```

安装命令：

~~~sh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
~~~

运行需要提前获取管理员权限。系统可能会提示你安装 Xcode 命令行工具（如果尚未安装）。

装完之后配一下环境变量：

~~~sh
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
source ~/.zshrc
~~~

## homebrew换源
中国内地用户可能由于网络问题无法安装，可尝试修改Homebrew安装源以解决此问题。以使用中科大开源镜像站为例：

**设置Hombrew安装源为科大源**
Homebrew支持通过修改环境变量设置安装源，首次安装Homebrew时也可以通过此方式加速下载过程。
```bash
export HOMEBREW_INSTALL_FROM_API=1
export HOMEBREW_BREW_GIT_REMOTE="https://mirrors.ustc.edu.cn/brew.git"
export HOMEBREW_CORE_GIT_REMOTE="https://mirrors.ustc.edu.cn/homebrew-core.git"
export HOMEBREW_BOTTLE_DOMAIN="https://mirrors.ustc.edu.cn/homebrew-bottles"
export HOMEBREW_API_DOMAIN="https://mirrors.ustc.edu.cn/homebrew-bottles/api"
brew update
```
# 安装git

用homebrew安装：

~~~sh
brew install git
~~~

# 安装python3

用homebrew安装：

~~~sh
brew install python
~~~

# 安装kubectl

用homebrew安装：https://kubernetes.io/docs/tasks/tools/install-kubectl-macos/#install-with-homebrew-on-macos

~~~sh
brew install kubectl
~~~

## 配置自动补全

https://kubernetes.io/docs/tasks/tools/install-kubectl-macos/#optional-kubectl-configurations-and-plugins

在.zshrc里面加上：

~~~sh
autoload -Uz compinit
compinit
source <(kubectl completion zsh)
~~~

## 配置alias

有现成工具可以用：https://github.com/ahmetb/kubectl-aliases

1. git clone下来这个仓库
2. 把里面的[.kubectl_aliases](https://github.com/ahmetb/kubectl-aliases/blob/master/.kubectl_aliases)文件拷贝到home目录下

3. .zshrc里面加上：

~~~sh
[ -f ~/.kubectl_aliases ] && source ~/.kubectl_aliases
~~~

1. 测试`k v`看能不能补全和运行

# 安装Obsidian
官网下载安装包安装即可。
## 插件
1. Editing Toolbar
2. Outliner
3. Git
4. awesome image 

## 主题
- Baseline
- Blue Topaz

## 不同Vault配置
每个vault下面会有一个.obsidian目录，保存了所有主题、插件等设置。
更换其他vault打开之后，由于换了新的.obsidian配置目录，所以原先的配置并不存在。此时将一个配置好的vault的.obsidian目录里面的所有内容复制到新vault即可。