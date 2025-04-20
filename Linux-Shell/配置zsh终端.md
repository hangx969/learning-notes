# zsh

- 上面提到了Zsh，它是Linux命令解释器的一种，CentOS默认的命令解释器是Bash，常用的还有sh、csh和tcsh。对比默认的Bash，Zsh的功能更强大，拥有大量插件，可以实现更强大的命令补全，命令高亮等功能。

# ohmyzsh

- OhMyZsh是一款开源工具，可以用于管理Zsh（Linux命令解释器的一种）的配置。使用OhMyZsh可以让你看起来像有10年工作经验的程序员，OhMyZsh有几百种插件可以供你使用，还有各种炫酷的主题。OhMyZsh非常流行，在Github上已经有`137K+`Star！

# 安装zsh

- 安装Zsh的方法很多，使用yum来安装很方便，不过OhMyZsh官方建议安装`5.0.8`以上版本，我们先来看下yum中的zsh版本号；

```sh
yum info zsh
```

- 如果你的版本号大于`5.0.8`可以使用yum来安装，使用如下命令即可，如果小于可以使用源码来安装；

```
yum -y install zsh
```

- 源码安装需要先下载Zsh的源码包，下载地址：https://zsh.sourceforge.io/Arc/source.html

- 先把下载好的源码包放到指定目录，然后使用如下命令进行解压安装；

```sh
# 安装依赖
yum -y install gcc perl-ExtUtils-MakeMaker git
yum -y install ncurses-devel
# 解压
tar xvf zsh-5.9.tar.xz
cd zsh-5.9
# 检查安装环境依赖是否完善
./configure
# 编译并安装
make && make install
```

- 安装完成后可以使用如下命令查看Zsh的路径；

```sh
whereis zsh
```

- 再把Zsh的路径添加到`/etc/shells`文件中去，在这里我们可以看到系统支持的所有命令解释器；

```sh
vim /etc/shells 
# 添加内容如下
/usr/local/bin/zsh
```

- 最后查看下Zsh版本号，用于检测Zsh是否安装成功了。

```sh
zsh --version
```

# 安装onmyzsh

- 接下来我们来安装OhMyZsh，直接使用如下命令安装；

```sh
#墙外
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
#墙内
sh -c "$(curl -fsSL https://install.ohmyz.sh/)"
```

- 如果遇到下载不下来的情况，可以先创建一个`install.sh`文件，然后从Github上复制该文件内容，再使用如下命令安装：

```
# install.sh 地址：https://github.com/ohmyzsh/ohmyzsh/blob/master/tools/install.sh
./install.sh
```

- 安装完成后会提示你修改Linux使用的默认shell，使用如下命令可查看修改默认shell；

```sh
# 查看当前在使用的shell
echo $SHELL
# 也可以使用下面命令自行修改默认shell
chsh -s $(which zsh)
```

- 安装成功后配置文件为`.zshrc`，安装目录为`.oh-my-zsh`，安装目录结构如下。

![图片](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202401081016712.png)

## 主题修改

- OhMyZsh的主题非常丰富，自带主题都在`themes`文件夹中；

- 修改主题只需修改配置文件`.zshrc`的`ZSH_THEME`属性即可，下面我们把主题改为`af-magic`；

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

## 使用插件

- OhMyZsh的自带插件都在`plugins`目录下，统计了下，多达305个。

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

### zsh-history-substring-search

> 可以搜索命令历史的插件，使用`Ctrl+R`快捷键触发，模糊搜索历时使用的命令。

- 下载插件到指定目录，使用如下命令即可；

```
git clone https://github.com/zsh-users/zsh-history-substring-search ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-history-substring-search
```

- 然后修改配置文件`.zshrc`，在plugins中添加插件`zsh-history-substring-search`；
- 接下来我们就可以通过`Ctrl+R`快捷键触发，然后进行命令搜索补全了。

### docker

> 自带插件，可以实现docker命令补全和自动提示。

- 作为自带插件无需下载，直接修改配置文件`.zshrc`，在plugins中添加插件`docker`；
- 当我们输入docker开头的命令时，使用`Tab`键可以出现提示并自动补全。

#### git

> 自带插件，添加了很多git的快捷命令。

- 直接修改配置文件`.zshrc`，在plugins中添加插件`git`；
- 该插件对于Git命令提供了非常多的快捷使用方式，比如下面的常用命令；

| 快捷别名 | 命令           |
| :------- | :------------- |
| g        | git            |
| gcl      | git clone      |
| ga       | git add        |
| gc       | git commit     |
| ggp      | git push       |
| ggl      | git pull       |
| gst      | git status     |
| gb       | git branch     |
| glg      | git log --stat |

#### z

> 自带插件，可以快速跳转到上个cd的目录下。

- 直接修改配置文件`.zshrc`，在plugins中添加插件`z`，最终配置效果如下；

```
plugins=(
        git
        zsh-syntax-highlighting
        zsh-autosuggestions
        zsh-history-substring-search
        docker
        z
)
```

- 我们先切换到`.oh-my-zsh/custom/plugins`目录下，然后再切换到其他目录下，之后直接使用`z plug`命令就可以切换回去了。