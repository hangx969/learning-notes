# 版本控制

## 版本控制工具 

主流版本：

- Git
- SVN（subversion）
- CVS

- VSS
- TFS

## 版本控制分类

- 本地版本控制

- 集中版本控制：SVN

  - 版本都保存在服务器上。用户需要联网从中央服务器上拉下来最新版本再修改提交。必须联网才能工作，对带宽要求比较高。

  - 用户自己电脑上只有某一部分文件。

- 分布式版本控制：Git

  - 每个用户电脑上都有完整的所有的版本数据。不会因为服务器坏掉造成不能工作的情况。

  - 协同方法：一个人改了文件A，另一个人也改了文件A，互相把修改推送给对方就可以看到对方的修改。
  - git是本地代码库，局域网联网就可以进行多人开发，把最终版本提价到远程即可。

# Git配置

-  查看所有git 配置：

  ```shell
  git config -l
  ```

- 查看git系统配置：

  ```shell
  git config --system --list
  git config --system -e #直接打开配置文件
  ```

-  查看git本地配置：

  ```shell
  git config --global --list
  git config --global -e #直接打开配置文件
  ```

- 必须要配的：用户名和邮箱

  ```shell
   git config --global user.email ""
   git config --global user.name "" 
  ```

# Git基本理论

## 基本组成

![图片](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202209111100348.png)

- 工作目录 working directory

  平时本地写代码的地方

- 暂存区 stage / index

  临时存放改动，只是一些文件。

- 仓库区：本地仓库repository

- 远程仓库：remote

  托管代码的服务器

## 工作流程

- 从远程仓库中把项目clone到本地

- 在本地工作区中增删改
- 将更改的文件add到暂存区域
- 将暂存区域的文件commit到本地git仓库
- 从本地仓库push到远程仓库

![图片](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202209111100296.jpeg)

## git文件状态

文件四种状态

- Untracked:
  - 未跟踪, 此文件在文件夹中, 但并没有add到本地仓库, 不参与版本控制。通过git add 状态变为Staged.

- Unmodified
  - 文件已经入库, 未修改, 即版本库中的文件快照内容与文件夹中完全一致。这种类型的文件有两种去处, 如果它被修改, 而变为Modified。如果使用git rm移出版本库, 则成为Untracked文件

- Modified
  - 文件已修改, 仅仅是修改, 并没有进行其他的操作。 这个文件也有两个去处, 通过git add可进入暂存staged状态, 使用git checkout 则丢弃修改过, 返回到unmodify状态, 这个git checkout即从库中取出文件, 覆盖当前修改 !

- Staged
  - 暂存状态，文件已经暂存到暂存区。执行git commit则将修改同步到本地仓库中, 这时本地仓库中的文件和工作区文件变为一致, 文件为Unmodified状态. 执行git reset HEAD filename取消暂存, 文件状态为Modified


 查看文件状态

```sh
git status [filename]
git status
```

# Git项目搭建

![图片](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202209111100768.png)

## 创建仓库

1. 创建本地仓库

   ```bash
   git init #会在当前路径下创建出一个隐藏文件夹 .git，存放git的版本、管理等信息
   ```

2. 克隆远程仓库

   ```bash
   # 克隆一个项目和它的整个代码历史(版本信息)
   $ git clone [url]  # https://gitee.com/kuangstudy/openclass.git
   ```

## 配置branch和remote

```bash
git branch -M main
git remote add origin https://github.com/hangx969/Scripts.git
```

## 更换remote

有时候在一开始添加remote的时候添加的是https url，后面希望更换成ssh url：

~~~sh
# 查看当前remote
git remote -v
# 切换remote
git remote set-url origin git@ssh.xxxx
~~~

## 免密码登录git

- github设置中加入客户端的ssh公钥。

- git clone项目下来的时候，使用ssh链接而非http链接。（http链接是需要MFA的，后续每次push都需要输入用户名密码）

  <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202412281415127.png" alt="image-20241228141528061" style="zoom:67%;" />

- git remote add采用ssh的link

  ~~~sh
  git remote add origin git@github.com:hangx969/k8s-platform-tools.git】
  git add .
  git commit -m "xxx"
  git checkout -b xxx
  git push origin xxx
  ~~~


# Git分支管理

- master主分支应该非常稳定，用来发布新版本，一般情况下不允许在上面工作。

- 工作一般情况下在新建的dev分支上工作，工作完后，比如要发布，或者说dev分支代码稳定后可以合并到主分支master上来。

- 要将修改后的代码推送到新的分支 "dev" 上，您可以按照以下步骤使用 Git 命令来操作：

  1. 首先，确保您的本地仓库是最新的：

     ```bash
     git pull origin main  # 假设您从 main 分支拉取的最新代码
     ```

  2. 创建并切换到新的分支 "dev"：

     ```bash
     git checkout -b dev
     ```

     这个命令会创建一个名为 "dev" 的新分支，并自动切换到这个分支。

  3. 将您的代码更改添加到暂存区：

     ```bash
     git add .
     # 或者您可以只添加部分文件
     git add <文件路径>
     ```

  4. 提交您的更改：

     ```bash
     git commit -m "描述您的更改"
     ```

     这里的 "描述您的更改" 应该替换为具体描述您所做更改的信息，帮助其他开发者理解此次提交的目的。

  5. 将 "dev" 分支推送到远程仓库：

     ```bash
     git push origin dev
     ```

     如果是第一次将这个分支推送到远程仓库，Git 会创建远程的 "dev" 分支。

# 开发常用流程

## 初始化本地仓库并拉取远程仓库

- 本地新建文件夹

- 文件夹内打开git bash

  ```shell
  git init
  git remote add origin <git repo link>
  git pull --rebase origin main
  ```

## 本地更改推送到远程仓库

- 添加所有文件到暂存区

```bash
git add .
```

- 提交暂存区的内容到本地仓库

```bash
git commit -m “comments”
```

- 新建分支

~~~sh
git checkout -b aaa-bbb-ccc
~~~

- 提交至远程仓库的新分支

```bash
git push origin aaa-bbb-ccc
# git -u: 第一次加了参数-u后，以后即可直接用git push代替git push origin main
```

- 忽略文件
  - 被忽略的文件在 .gitignore里面，可以配置正则规则配置哪些文件不会被push到远端仓库

## Merge PR

推送新分支到远程仓库之后，在远程仓库上会执行创建Pull Request、Merge Pull Request等操作。

- 在github上一般采用“Merge and rebase”方式来merge PR：

  1. 先对PR分支执行rebase，PR分支的commit会加到main分支的最新状态上
  2. 再通过merge commit将PR的更改合并到main上

  这样main分支上会保留一个merge commit。

- azure devops上一般采用“Rebase and fast-forward”：

  1. 对 PR 的分支执行一个 rebase 操作，将 PR 分支上的提交重新应用到目标分支的最新状态上。
  2. 然后通过 fast-forward merge 将这些提交直接添加到目标分支中，不会创建 merge commit。

  合并后，目标分支上的提交历史是线性的，PR 的提交直接接在目标分支的最新提交之后。没有额外的 merge commit。

## 从远程仓库拉取更新内容到本地

本地推送完成新分支之后，远端仓库执行了merge PR操作，这样main分支的提交记录已经改变，需要把新的main分支同步到本地仓库：

```bash
git checkout main
git branch -D aaa-bbb-ccc
git pull --rebase origin main
```

# 清理操作

## 清除github repo的commit记录

```bash
#进入本地仓库的目录
cd /path/to/your/repository
#创建并切换到一个与当前分支无关的新的孤立分支。
git checkout --orphan newBranch
# 添加所有的文件到新分支
git add .
# 提交更改
git commit -am "Initial commit"
# 删除原始分支：因为我们将删除commit历史记录，所以不再需要原始分支
git branch -D main
# 将新的分支重命名为 main 分支
git branch -m main
# 强制将本地修改推送到远程仓库：由于我们已经改变了本地仓库的历史记录，所以必须使用强制推送选项
git push -f origin main
```

## 清除所有git history并覆盖到远端仓库

~~~sh
cd <repo dir>
rm -rf ./git
git init
git config user.name "xxxx"
git config user.email "xxxxx"
git add .
git commit -m "initial commit with cleaned history"
# git branch -M main
git remote add origin <remote-repo-url> # 去github repo上copy ssh url
git push -f origin main
~~~

此操作会覆盖掉远程仓库的历史记录。完成之后，repo就只会有一个干净的提交记录，所有历史记录都会被清除。

# git配置代理

## git代理

~~~sh
# 设置
git config --global http.proxy 'socks5://127.0.0.1:7890' 
git config --global https.proxy 'socks5://127.0.0.1:7890'

# 恢复
git config --global --unset http.proxy
git config --global --unset https.proxy
~~~

## gir clone ssh设置代理

~~~sh
vim ~/.ssh/config
# 全局
# ProxyCommand nc -X 5 -x 127.0.0.1:7890 %h %p
# 只为特定域名设定
Host github.com
    ProxyCommand nc -X 5 -x 127.0.0.1:7890 %h %p
~~~

# 实用git工具

- GitKraken
- tortoisegit （windows平台）
- fork
- sourceTree
- git graph (vscode插件)
- 学习git：https://learngitbranching.js.org/?locale=zh_CN

# Lab

~~~sh
# 基于以下内容创作本代码，用于讲解DevOps精讲课Git与Github章节
# https://www.bookstack.cn/read/backlog-git-tutorial/35.md
# https://www.youtube.com/watch?v=tRZGeaHPoaw&ab_channel=KevinStratvert

# 常用命令
git XXX -h # 询问git XXX是啥意思
git help XXX # 更详细的解释，打开一个本地html页面给你解释
git log --oneline # 看看我之前所有的commit历史（以简洁的形式）
git reset XXX # 回溯到某个commit上

# 事前预备
git config --global user.name "xxxx"
git config --global user.email "xxxx"
git init # 初始化文件夹
# 创建一个myfile.txt文件
git status # 这是我们超常用的命令
git add myfile.txt # git add . 可以track所有目录里文件
git commit -m "first commit" # 此时此刻，照张照片，贴在相册，可以回溯

# 建立分支
git branch issue1 # 建立一个名为issue1的分支
git branch # 查看所有分支，发现head还指在master

# 切换分支
git checkout issue1 # 切换到issue1分支，-b可以创建分支并切换，git switch -c是创建并切换（推荐）
# 修改myfile.txt文件
git add myfile.txt
git commit -m "add new content"
# 现在master落后于issue1，head指向issue1

# 合并分支 -- merge合并都是先在主线上，把其他分支往主线上合并
# 先切换master分支，然后把issue1分支导入到master分支
git checkout master
# 打开myfile.txt档案以确认内容，应该是旧的
git merge issue1 
# 打开myfile.txt档案以确认内容，应该是新的，此时head在master上

# 删除分支
# 既然issue1分支的内容已经顺利地合并到master分支了，现在可以将其删除了
git branch -d issue1 # 删除了issue1分支
git branch # 检查现在只有master分支了

# 并行操作
# 首先创建issue2分支和issue3分支，并切换到issue2分支
git branch issue2
git branch issue3
git checkout issue2
git branch
# 在issue2分支的myfile.txt添加commit命令的说明后提交
git add .\myfile.txt
git commit -m "add content from issue2"
# 接着，切换到issue3分支
git checkout issue3
# 打开myfile.txt档案，由于在issue2分支添加了新内容，所以issue3分支的myfile.txt里没有新内容
git add myfile.txt
git commit -m "add content from issue3"
# 对比切换到issue2和issue3分支

# 解决合并的冲突
# 把issue2分支和issue3分支的修改合并到master
# 切换master分支后，与issue2分支合并
git checkout master
git merge issue2 # 没有冲突，这是fast-forward合并
git merge issue3 # 出现冲突报警，由于在同一行进行了修改，所以产生了冲突
# 打开myfile.txt文件，处理冲突
git add myfile.txt
git commit -m "merge issue3"

# 用rebase合并
# 合并issue3分支的时候，使用rebase可以使提交的历史记录显得更简洁
# 现在暂时取消刚才的合并
git reset --hard HEAD~
# 画图解释目前的历史记录
# 切换到issue3分支后，对master执行rebase
git checkout issue3
git rebase master
# 和merge时的操作相同，修改在myfile.txt发生冲突的部分
# rebase的时候，修改冲突后的提交不是使用commit命令，而是执行rebase命令指定 —continue选项
# 若要取消rebase，指定 —abort选项
git add myfile.txt
git rebase --continue # 按i进入insert模式，输入comment，Esc后:wq保存并退出
# 这样，在master分支的issue3分支就可以fast-forward合并了，切换到master分支后执行合并
git checkout master
git merge issue3
# myfile.txt的最终内容和merge是一样的，但是历史记录拉成直线了

# 创建Github Repo
# 先在Github上创建一个Repo，创建完后，下面三行是自动生成的
git remote add origin https://github.com/cengxiye/learn-git-2024.git # 首先将远程仓库的地址添加到本地仓库，并将其命名为 "origin"
git branch -M main # 将当前分支（默认是master）重命名为main
git push -u origin main # 将本地的"main"分支推送到远程仓库"origin"。-u参数用于设置"origin"作为默认的远程仓库
# 以后可以直接使用git push而不需要指定远程仓库和分支。这个命令会将本地的"main"分支的内容推送到远程仓库，实现同步


# 简要介绍Github
# About，填写有关你这个Repo的信息
# Issue，提交bug和feature request，可以assign给其他人/可以加labels等等
# Actions，可以run test，测试你得代码
# Projects，可以管理你的项目
# Wiki，类似一个有关于你项目的百科
# Security，诸如代码安全扫描等
# Insights，查看项目数据
# Settings，设置你的项目
# Release，回到你Repo的主页，可以发布1.0版本你的release，你的代码被打包成zip

# PUSH
# 在main branch上，修改mytext.txt文件
git add .\myfile..txt
git commit -m "change file, to be pushed to origin"
git push
# 检查Github上的文件，已经更新

# PULL
# 在Github上修改txt
git pull
# 在本地main branch上，检查txt

# FETCH
# 在Github上修改txt
git fetch 
git diff main origin/main
# git fetch：只是将远程仓库的变更下载到本地，不会自动合并到当前分支
# git pull = git fetch + git merge

# CLONE
git clone https://github.com/cengxiye/sid.github.io.git
# 适用场景：使用 git clone 通常是在开始新项目或者从头开始的时候
# 适用场景：使用 git pull 通常是在你已经有了一个本地仓库，希望获取最新变更时
# 操作对象：git clone 操作的对象是整个远程仓库
# 操作对象：git pull 操作的对象是当前分支上的远程变更
# 执行时机：git clone 只需要执行一次，创建本地仓库的拷贝
# 执行时机：git pull 需要在你想要获取远程仓库变更时执行
~~~

# Troubleshooting

- 目录中有大文件，push的时候显示超过100MB不能上传，删除这个文件之后，push仍然会提交这个文件报错。

  - 解决：要从所有commit中把这个文件删掉，再push

    ```bash
    git filter-branch --force --index-filter "git rm --cached --ignore-unmatch xxx/xxx.exe" --prune-empty --tag-name-filter cat -- --all
    ```

- git pull时如果遇到报错

  ~~~sh
  fetch-pack: unexpected disconnect while reading sideband packet
  fatal: early EOF
  fatal: fetch-pack: invalid index-pack output
  ~~~

  - 原因：远程仓库的文件过大，需要设置本地仓库大小。

  - 解决：

    ~~~sh
    git config http.sslVerify "false"
    #若出现下列错误：
    git config http.sslVerify "false" fatal: not in a git directory
    #再继续执行即可解决
    git config --global http.sslVerify "false"
    #文件大小的上限设置：
    git config --global http.postBuffer 524288000
    ~~~

