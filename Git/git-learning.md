---
title: Git 学习笔记
tags:
  - git
  - github
  - version-control
aliases:
  - Git学习
  - Git基础
---

# Git 学习笔记

本文整理版本控制、Git 的基本概念、常用命令、分支工作流及故障排查。示例中的仓库地址、分支名和文件路径需按实际环境替换。

## 版本控制

### 版本控制工具

主流版本：

- Git
- SVN（subversion）
- CVS
- VSS
- TFS

### 版本控制分类

- **本地版本控制**：版本历史保存在本机。
- **集中式版本控制（如 SVN）**：中央服务器保存主要版本历史，团队通过服务器共享变更。通常需要连接服务器才能同步或提交。
- **分布式版本控制（如 Git）**：每个克隆仓库都保存项目的提交历史，可以在本地提交、查看历史和创建分支；与其他成员协作时再通过远程仓库交换提交。

## Git 基本概念

### 工作区、暂存区与仓库

![图片](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202209111100348.png)

- **工作区（working tree）**：实际编辑文件的目录。
- **暂存区（index / staging area）**：记录下一次提交准备包含的内容。
- **本地仓库（repository）**：保存提交历史和对象，通常位于 `.git` 目录。
- **远程仓库（remote）**：用于与其他人共享提交的仓库，例如 GitHub 上的仓库。

### 基本工作流程

1. 从远程仓库克隆项目。
2. 在工作区新增、修改或删除文件。
3. 使用 `git add` 将变更加入暂存区。
4. 使用 `git commit` 在本地创建提交。
5. 使用 `git push` 将本地提交推送到远程仓库。

![图片](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202209111100296.jpeg)

### 文件状态

| 状态 | 含义 |
| --- | --- |
| Untracked（未跟踪） | 文件尚未加入 Git 跟踪；`git add` 后可进入暂存区。 |
| Unmodified（未修改） | 已跟踪文件与当前提交一致。 |
| Modified（已修改） | 已跟踪文件在工作区发生变化，尚未暂存该变化。 |
| Staged（已暂存） | 变更已加入暂存区，准备在下次提交中保存。 |

`git rm` 会将删除操作加入暂存区；提交后，该文件才不再被跟踪。取消暂存可用 `git restore --staged <文件路径>`；丢弃工作区中尚未暂存的修改可用 `git restore <文件路径>`。后者会丢失对应的工作区修改。

```sh
git status
git status -- <文件路径>
```

## Git 配置

```sh
# 查看当前生效的配置及其来源
git config --list --show-origin

# 查看或编辑系统级配置
git config --system --list
git config --system --edit

# 查看或编辑用户级配置
git config --global --list
git config --global --edit

# 设置提交身份
git config --global user.name "你的姓名"
git config --global user.email "you@example.com"
```

## 创建与连接仓库

![图片](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202209111100768.png)

### 创建仓库

初始化当前目录，或从远程克隆仓库：

```sh
git init
git clone <仓库地址>
```

`git init` 会创建用于保存仓库元数据的 `.git` 目录；`git clone` 会取得远程仓库可访问的提交历史。

### 配置分支和远程仓库

```sh
git branch -M main
git remote add origin https://github.com/hangx969/Scripts.git
```

`git branch -M main` 会将当前分支重命名为 `main`；仅在需要时使用。添加前可先运行 `git remote -v` 检查是否已有 `origin`。

### 更换远程仓库地址

需要将 HTTPS 地址改为 SSH 地址时：

```sh
git remote -v
git remote set-url origin git@github.com:hangx969/Scripts.git
```

### 使用 SSH 连接 GitHub

1. 在 GitHub 账号中添加本机 SSH 公钥。
2. 克隆时使用 SSH 地址，或将现有 remote 改为 SSH 地址。HTTPS 连接也可用凭据管理器或访问令牌认证，无须每次手动输入凭据。

   <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202412281415127.png" alt="image-20241228141528061" style="zoom:67%;" />

```sh
git remote add origin git@github.com:hangx969/k8s-platform-tools.git
git remote -v
```

已有 `origin` 时，使用 `git remote set-url origin <SSH 地址>`，不要再次执行 `git remote add`。

## Git 分支管理

### 查看分支

```sh
# 查看本地分支
git branch
# 查看远程分支
git branch -r
# 查看本地远程所有分支的汇总
git branch -a
```

### 更新远程跟踪分支

```sh
# 从远程拉取最新的分支/标签信息到本地，顺手清理本地那些"远程已经删除"的origin/xxx分支
git fetch -p
```

### 删除本地分支

```sh
git branch -d xxx
```

> [!warning] 注意
> - `-d`：仅在分支已完全合并到其上游分支（未设置上游时为当前分支）时删除。
> - `-D`：无论是否合并都删除分支引用；未合并的提交可能因此难以找回。

### 删除远程分支

```sh
git push origin --delete feature-x
```

### 分支工作流程

以下以 `main` 为主分支、`dev` 为开发分支。实际分支名称和合并策略以仓库约定为准。

1. 切换到主分支并获取最新提交：

   ```sh
   git switch main
   git pull --rebase origin main
   ```

2. 创建并切换到开发分支：

   ```sh
   git switch -c dev
   ```

3. 暂存、提交并首次推送分支：

   ```sh
   git add <文件路径>
   git commit -m "描述更改"
   git push -u origin dev
   ```

## 查看历史与恢复修改

```sh
git log                         # 查看提交记录
git status                      # 查看工作区与暂存区状态
git diff -- <文件路径>          # 查看尚未暂存的修改
git diff --staged               # 查看已暂存的修改
git restore -- <文件路径>       # 丢弃未暂存的工作区修改
git restore --staged <文件路径> # 取消暂存
```

> [!warning] 重置与强制推送
> `git reset --hard` 会丢弃已跟踪文件的未提交修改；`git reset --hard <commit-id>` 还会移动当前分支。重写已共享历史后可能需要 `git push --force-with-lease`，执行前应与协作者协调并确认目标分支。

## 常用开发流程

### 初始化本地仓库并连接远程

如果远程仓库已有提交，优先直接克隆：

```sh
git clone <仓库地址>
```

如果是在已有本地项目中初始化 Git，再添加远程仓库：

```sh
git init
git remote add origin <仓库地址>
git fetch origin
```

确认本地与远程的提交历史关系后，再选择合并或变基。

### 将本地更改推送到远程

```sh
git status
git switch -c aaa-bbb-ccc        # 如需新分支，先创建并切换
git add <文件路径>               # 按需暂存文件；git add . 会暂存当前目录下的变更
git commit -m "描述更改"
git push -u origin aaa-bbb-ccc   # 首次推送并设置上游分支
```

设置上游分支后，在该分支上通常可直接使用 `git push`。

### 合并 Pull Request

将开发分支推送到远程后，可在代码托管平台创建并合并 Pull Request。常见策略：

- **Rebase and merge**：将 PR 的提交逐个重放到目标分支，通常不创建合并提交。
- **Merge commit**：创建合并提交，保留分叉与合并的历史。
- **Squash and merge**：将 PR 的变更压缩为一个提交后合并。

GitHub 和 Azure DevOps 的实际按钮名称、可用策略及分支保护规则可能不同，应以仓库配置为准。

### 更新本地主分支

远程 PR 合并后，切换到本地 `main` 并同步：

```sh
git switch main
git pull --rebase origin main
```

确认开发分支已合并且不再需要后，再用 `git branch -d aaa-bbb-ccc` 删除本地分支。

### 将 main 的更新纳入开发分支

开发期间如果远程 `main` 有新提交，可在推送开发分支前同步：

```sh
git switch dev
git fetch origin
git rebase origin/main  # 将 dev 的提交重放到最新 main 之后
# 或使用 git merge origin/main，保留合并历史
```

`rebase` 会改写当前分支上的提交；如果分支已由多人共享，应先协调。若发生冲突，解决后运行 `git add <文件路径>` 和 `git rebase --continue`。

### 为提交打标签

标签用于标记某个特定提交，常用于发布版本，但不一定代表破坏性变更。以下示例在 PR 合并后给最新的 `main` 提交打标签：

```sh
git switch main
git pull --rebase origin main
git tag 0.4.1
git push origin 0.4.1
```

## 历史与跟踪清理

### 重建提交历史

> [!danger] 会重写历史
> 以下操作会改变目标分支的提交历史。先备份仓库并与协作者协调；受保护分支可能禁止强制推送。远程旧对象、其他分支、标签和协作者的克隆不会因重建 `main` 自动清除。

如果只想让 `main` 从一个新提交开始，可在仓库中创建孤立分支：

```sh
git switch --orphan new-main
git add -A
git commit -m "Initial commit"
git branch -M main
git push --force-with-lease origin main
```

在确认新分支可用后，再处理不再需要的本地分支。若需从所有相关历史中移除某个文件，应使用 `git-filter-repo` 等历史重写工具，并处理其他分支、标签和远程副本；仅重建 `main` 不足以完成全库清理。

### 重新初始化本地仓库

如果需要舍弃**本地**仓库元数据并从当前文件重新创建初始提交，可以删除 `.git` 后重新初始化。此操作会清除本地分支、标签、配置和提交历史；先备份仓库，并确认不需要这些记录。

```sh
cd <仓库目录>
rm -rf .git
git init
git config user.name "你的姓名"
git config user.email "you@example.com"
git add -A
git commit -m "Initial commit"
git branch -M main
git remote add origin <远程仓库地址>
git fetch origin main
git push --force-with-lease origin main
```

这只会重建并更新目标分支；其他远程引用及协作者的克隆不会自动清理。

### 停止跟踪已被忽略的文件

`.gitignore` 只会忽略尚未被跟踪的文件；已提交文件需要先从索引中移除，再提交删除记录：

```sh
# 先在 .gitignore 中添加相应规则
git rm -r --cached -- Python/python-manuscripts
git commit -m "Stop tracking Python/python-manuscripts files"
git push origin main
```

`--cached` 保留工作区文件。不要在后续执行 `git add` 把这些文件重新纳入跟踪。

## Git 代理配置

### HTTP(S) 代理

Git 的 `http.proxy` 配置可用于 HTTP 与 HTTPS 传输。按需设置代理，完成后再移除：

```sh
git config --global http.proxy 'socks5://127.0.0.1:7890'
git config --global --unset http.proxy
```

### SSH 代理

SSH 连接使用 `~/.ssh/config` 中的 `ProxyCommand`。以下示例仅针对 `github.com`，端口需与本机代理一致：

```ssh-config
Host github.com
    ProxyCommand nc -X 5 -x 127.0.0.1:7890 %h %p
```

如果 `Host github.com` 已有身份或端口配置，将这一行加入现有配置块。

## 常用工具与资源

- 图形客户端：GitKraken、TortoiseGit（Windows）、Fork、Sourcetree。
- 编辑器扩展：VS Code 的 Git Graph。
- 交互式练习：[Learn Git Branching](https://learngitbranching.js.org/?locale=zh_CN)。
- 命令别名：可按需使用 Zsh 的 Git 插件。

## Git 操作练习

以下练习以默认分支 `main`、文件 `myfile.txt` 为例，按顺序演示提交、分支、合并、变基和远程操作。练习素材：[Git 教程](https://www.bookstack.cn/read/backlog-git-tutorial/35.md)、[视频教程](https://www.youtube.com/watch?v=tRZGeaHPoaw&ab_channel=KevinStratvert)。

### 初始化与第一次提交

```sh
git config --global user.name "你的姓名"
git config --global user.email "you@example.com"
git init
git branch -M main
# 创建并编辑 myfile.txt
git status
git add myfile.txt
git commit -m "first commit"
git log --oneline
```

可使用 `git <子命令> -h` 查看简要帮助，或使用 `git help <子命令>` 打开完整手册。

### 创建、合并与删除分支

```sh
git switch -c issue1
# 修改 myfile.txt
git add myfile.txt
git commit -m "add new content"

git switch main
git merge issue1
git branch -d issue1
```

此时若 `main` 没有独立的新提交，合并通常是快进合并。

### 并行修改与冲突

```sh
git switch -c issue2 main
# 修改 myfile.txt 并提交
git add myfile.txt
git commit -m "add content from issue2"

git switch -c issue3 main
# 修改同一位置并提交
git add myfile.txt
git commit -m "add content from issue3"

git switch main
git merge issue2
git merge issue3
```

如果两条分支修改了同一位置，第二次合并可能产生冲突。手动编辑文件，移除冲突标记并确定最终内容，然后完成合并：

```sh
git add myfile.txt
git commit
```

### 练习变基

在**独立的练习仓库**中，可重新构造上述两条分支，从冲突发生前的状态尝试变基。不要在包含未保存工作的仓库中为练习执行 `git reset --hard`。

```sh
git switch issue3
git rebase issue2
# 如遇冲突，编辑 myfile.txt 后继续
git add myfile.txt
git rebase --continue
# 如果要放弃变基，使用 git rebase --abort
```

变基成功后，可切回 `main` 并合并 `issue3`；如果 `main` 指向 `issue2` 的提交，通常可以快进合并。变基会改变提交 ID。

### 连接 GitHub 远程仓库

先在 GitHub 创建仓库，再在本地配置远程地址并推送：

```sh
git remote add origin https://github.com/cengxiye/learn-git-2024.git
git push -u origin main
```

`-u` 用于设置上游分支，之后在该分支上通常可直接执行 `git push` 或 `git pull`。GitHub 仓库页面还提供 About、Issues、Actions、Projects、Wiki、Security、Insights、Settings 和 Releases 等功能。

### 推送、拉取与克隆

```sh
# 修改 myfile.txt 后提交并推送
git add myfile.txt
git commit -m "change file, to be pushed to origin"
git push

# 获取远程更新并整合到当前分支
git pull

# 只获取远程信息，再比较本地与远程分支
git fetch
git diff main origin/main

# 首次获取另一个仓库
git clone https://github.com/cengxiye/sid.github.io.git
```

`git fetch` 只获取远程提交和引用，不会自动整合到当前分支；`git pull` 会先 fetch，再按参数或配置采用快进、合并或变基等方式整合。`git clone` 用于创建新的本地仓库副本。

## 故障排查

### 大文件导致推送失败

如果 GitHub 拒绝包含超限文件的推送，即使工作区已经删除该文件，只要待推送的提交历史仍包含它，推送仍可能失败。先确认报错指出的文件路径，再决定是改用 Git LFS，还是在备份并协调协作者后使用 `git-filter-repo` 从相关历史中移除它。历史重写后还需检查其他分支、标签和已有克隆。

如果 `git pull` 出现以下错误，不要直接认定为文件过大：

```text
fetch-pack: unexpected disconnect while reading sideband packet
fatal: early EOF
fatal: fetch-pack: invalid index-pack output
```

这类错误也可能来自网络中断、代理或传输链路问题。先重试并检查网络、代理及远程服务状态；不要为排查而关闭 TLS 证书校验。

### GitHub SSH 22 端口连接超时

出现 `ssh: connect to host github.com port 22: Connection timed out` 时，先检查 SSH 调试输出：

```sh
ssh -vT git@github.com
```

如果确认是 22 端口被网络阻断，可按 GitHub 官方方案尝试 `ssh.github.com` 的 443 端口：

```sh
ssh -T -p 443 git@ssh.github.com
```

测试成功后，在 `~/.ssh/config` 中配置：

```ssh-config
Host github.com
    HostName ssh.github.com
    User git
    Port 443
```

再次执行 `ssh -T git@github.com` 验证身份。GitHub 返回“successfully authenticated”且提示不提供 shell 访问时，说明 SSH 认证成功。配置前若已有 `Host github.com` 块，应合并设置，避免覆盖原有的 `IdentityFile` 等选项。

### 多 GitHub 账号的 SSH 密钥冲突

#### 问题背景

在同一台机器上配置了多个 GitHub 账号的 SSH 密钥（例如工作账号 `ds-hangxu` 和个人账号 `hangx969`），push 个人仓库时报错：

```
ERROR: Permission to hangx969/learning-notes.git denied to ds-hangxu.
fatal: Could not read from remote repository.
Please make sure you have the correct access rights and the repository exists.
```

原因可能是 SSH 在连接时提供了工作账号的密钥，GitHub 因而将连接识别为没有该仓库权限的工作账号。可以用 `ssh -vT git@github.com` 查看实际尝试的密钥。

#### 解决办法

1. 修改 `~/.ssh/config`，为不同账号配置不同的 Host 别名，并使用 `IdentitiesOnly yes` 指定密钥：

   ```ssh-config
   # 工作账号
   Host github.com
       HostName github.com
       User git
       IdentityFile ~/.ssh/id_ed25519_ds_github
       IdentitiesOnly yes

   # 个人账号
   Host github-personal
       HostName github.com
       User git
       IdentityFile ~/.ssh/id_ed25519
       IdentitiesOnly yes
   ```

2. 将个人仓库的 remote URL 改为使用别名：

   ```sh
   cd ~/github-repo/learning-notes
   git remote set-url origin git@github-personal:hangx969/learning-notes.git
   ```

3. 验证连接身份：

   ```sh
   # 验证工作账号
   ssh -T git@github.com
   # Hi ds-hangxu! You've successfully authenticated...

   # 验证个人账号
   ssh -T git@github-personal
   # Hi hangx969! You've successfully authenticated...
   ```

4. 按仓库流程提交并推送更改。
> [!tip] 关键点
> - `IdentitiesOnly yes` 是关键配置，确保 SSH 只使用指定的密钥文件，不会尝试 ssh-agent 中的其他密钥。
> - Host 别名（如 `github-personal`）仅用于 SSH 路由，Git 实际连接的仍然是 `github.com`。
> - 需要使用个人密钥的仓库，应将相应 remote URL 的主机名改为 `github-personal`。
