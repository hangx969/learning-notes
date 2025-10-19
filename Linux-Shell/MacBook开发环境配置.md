# 配置oh-my-zsh

MacOS 15中zsh已经是默认的命令行终端。只需要配一个oh-my-zsh。

安装：

~~~sh
sh -c "$(curl -fsSL https://raw.github.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"
~~~

安装过程会提示覆盖当前的zshrc，先把需要添加的内容放进当前zshrc，然后选择n，不要覆盖：

~~~sh
vim .zshrc
# 加上下面内容
export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME="robbyrussell"
plugins=(git)

source $ZSH/oh-my-zsh.sh
~~~

## 主题

OhMyZsh的主题非常丰富，自带主题都在`themes`文件夹中；修改主题只需修改配置文件`.zshrc`的`ZSH_THEME`属性即可，下面我们把主题改为`af-magic`；

```sh
vim ~/.zshrc
# 修改如下内容
ZSH_THEME="af-magic"
# 刷新配置，每次修改后都需要
source ~/.zshrc
```

### powerlevel9k

~~~sh
git clone https://github.com/bhilburn/powerlevel9k.git ~/.oh-my-zsh/custom/themes/powerlevel9k
vim /root/.zshrc
#修改主题配置为powerlevel9k
ZSH_THEME="powerlevel9k/powerlevel9k"
source ~/.zshrc
~~~

### powerlevel10k

```sh
git clone https://github.com/romkatv/powerlevel10k.git $ZSH_CUSTOM/themes/powerlevel10k
vim /root/.zshrc
#修改主题配置为powerlevel10k
ZSH_THEME="powerlevel10k/powerlevel10k”
source ~/.zshrc
```

## 插件

OhMyZsh的自带插件都在`plugins`目录下，统计了下，多达305个。

### zsh-syntax-highlighting

> 平时我们输入Linux命令的时候，只有在执行的时候才知道输错命令了，这款插件可以实时检测命令是否出错。

- 下载插件到指定目录，使用如下命令即可；

```sh
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
```

- 然后修改配置文件`.zshrc`，在plugins中添加插件`zsh-syntax-highlighting`；

```sh
plugins=(
        git
        zsh-syntax-highlighting
)
```

- 接下来再输入命令时就有高亮提示了，正确命令会显示绿色。

### zsh-autosuggestions

> 自动补全插件，输入命令后会自动提示相关命令，使用方向键`→`可以实现自动补全。

- 下载插件到指定目录，使用如下命令即可；

```sh
git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
```

- 然后修改配置文件`.zshrc`，在plugins中添加插件`zsh-autosuggestions`；
- 此时我们输入命令前缀就会直接提示命令，然后按方向键`→`就可以实现自动补全了。

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

## Test Outliner

- 111
- 222
- 333
	- 444
- 555
- 777