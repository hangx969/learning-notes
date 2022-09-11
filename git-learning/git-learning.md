# Git

## 版本控制

### 版本控制工具 

主流版本：

- Git
- SVN（subversion）
- CVS

- VSS
- TFS

### 版本控制分类

- 本地版本控制

- 集中版本控制：SVN

  - 版本都保存在服务器上。用户需要联网从中央服务器上拉下来最新版本再修改提交。必须联网才能工作，对带宽要求比较高。

  - 用户自己电脑上只有某一部分文件。

- 分布式版本控制：Git

  - 每个用户电脑上都有完整的所有的版本数据。不会因为服务器坏掉造成不能工作的情况。

  - 协同方法：一个人改了文件A，另一个人也改了文件A，互相把修改推送给对方就可以看到对方的修改。
  - git是本地代码库，局域网联网就可以进行多人开发，把最终版本提价到远程即可。

### Git配置

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

### Git基本理论

#### 基本组成

![图片](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202209111100348.png)

- 工作目录 working directory

  平时本地写代码的地方

- 暂存区 stage / index

  临时存放改动，只是一些文件。

- 仓库区：本地仓库repository

- 远程仓库：remote

  托管代码的服务器

#### 工作流程

- 在工作目录中添加文件
- 将需要进行版本管理的文件存入暂存区域
- 将暂存区域的文件提交到git仓库

![图片](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202209111100296.jpeg)

### Git项目搭建

![图片](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202209111100768.png)

#### 创建仓库

1. 创建本地仓库

   ```
   git init #会在当前路径下创建出一个隐藏文件夹 .git，存放git的版本、管理等信息
   ```

2. 克隆远程仓库

   ```
   # 克隆一个项目和它的整个代码历史(版本信息)
   $ git clone [url]  # https://gitee.com/kuangstudy/openclass.git
   ```

#### git文件操作

文件四种状态

- Untracked: 未跟踪, 此文件在文件夹中, 但并没有加入到git库, 不参与版本控制. 通过git add 状态变为Staged.
- Unmodify: 文件已经入库, 未修改, 即版本库中的文件快照内容与文件夹中完全一致. 这种类型的文件有两种去处, 如果它被修改, 而变为Modified. 如果使用git rm移出版本库, 则成为Untracked文件
- Modified: 文件已修改, 仅仅是修改, 并没有进行其他的操作. 这个文件也有两个去处, 通过git add可进入暂存staged状态, 使用git checkout 则丢弃修改过, 返回到unmodify状态, 这个git checkout即从库中取出文件, 覆盖当前修改 !
- Staged: 暂存状态. 执行git commit则将修改同步到库中, 这时库中的文件和本地文件又变为一致, 文件为Unmodify状态. 执行git reset HEAD filename取消暂存, 文件状态为Modified

 查看文件状态

- git status [filename]
- git status

#### 免密码登录git

配SSH公钥。git clone可选择使用ssh链接

### 本地内容同步到远程仓库

#### 添加所有文件到暂存区

git add .

#### 提交暂存区的内容到本地仓库

git commit -m “”

#### 提交至远程仓库

git push origin main

#### 忽略文件

被忽略的文件在 .gitignore里面，可以配置正则规则.



### 从远程仓库拉取内容到本地

- 本地新建文件夹

- 文件夹内打开git bash

  ```shell
  git init
  git remote add origin <git repo link>
  git pull --rebase origin main
  ```

### Git分支管理

master主分支应该非常稳定，用来发布新版本，一般情况下不允许在上面工作，工作一般情况下在新建的dev分支上工作，工作完后，比如上要发布，或者说dev分支代码稳定后可以合并到主分支master上来。