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

# git文件操作

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

- git status [filename]
- git status

# 免密码登录git

- 配SSH公钥。git clone可选择使用ssh链接。


# 本地内容同步到远程仓库

## 添加所有文件到暂存区

```bash
git add .
```

## 提交暂存区的内容到本地仓库

```bash
git commit -m “comments”
```

## 提交至远程仓库

```bash
git push origin main
//或者直接 git push
```

- git -u
  - 第一次加了参数-u后，以后即可直接用git push代替git push origin master

## 忽略文件

被忽略的文件在 .gitignore里面，可以配置正则规则.

# 从远程仓库拉取更新内容到本地

```bash
//方法一
git fetch origin main #从远程的origin仓库的master分支下载代码到本地的origin master
git log -p main.. origin/main #比较本地的仓库和远程参考的区别
git merge origin/main #把远程下载下来的代码合并到本地仓库，远程的和本地的合并

//方法二
git fetch origin master:temp #从远程的origin仓库的master分支下载到本地并新建一个分支temp
git diff temp #比较master分支和temp分支的不同
git merge temp #合并temp分支到master分支
git branch -d temp #删除temp
```

# 初始化本地仓库并拉取远程内容

- 本地新建文件夹

- 文件夹内打开git bash

  ```shell
  git init
  git remote add origin <git repo link>
  git pull --rebase origin main
  ```

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

  4. **提交您的更改：**
     
     ```bash
     git commit -m "描述您的更改"
     ```
     
     这里的 "描述您的更改" 应该替换为具体描述您所做更改的信息，帮助其他开发者理解此次提交的目的。
     
  5. 将 "dev" 分支推送到远程仓库：
     ```bash
     git push origin dev
     ```

     如果是第一次将这个分支推送到远程仓库，Git 会创建远程的 "dev" 分支。

  

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

    

    