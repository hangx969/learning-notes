# ArgoCD GitOps 仓库从 GitHub 迁移到 Gitee（双 Remote 推送）

## 问题背景

在使用 ArgoCD 部署应用时，`argocd-repo-server` 需要从 Git 仓库拉取代码（执行 `helm dependency build`、`kustomize build` 等操作）。原始仓库托管在 GitHub（`https://github.com/hangx969/local-k8s-gitops.git`），但由于集群部署在国内网络环境，频繁出现以下问题：

1. **DNS 解析失败**：CoreDNS 转发 `github.com` 的 DNS 查询到上游 DNS 超时，导致 `no such host`
2. **连接超时**：即使 DNS 解析成功，HTTPS 连接 GitHub 也经常超时
3. **repo-server CrashLoopBackOff**：Git 操作失败 → manifest 生成失败 → liveness probe 超时 → 容器被杀 → 反复重启

这些问题的根因是**集群到 GitHub 的网络链路不稳定**，属于基础设施层面的问题，无法通过 Kubernetes 或 ArgoCD 的配置来根本解决。

## 解决方案

### 核心思路

将 GitOps 仓库镜像到 **Gitee**（国内 Git 托管平台），让 ArgoCD 从 Gitee 拉取代码。同时保留 GitHub 作为主仓库，通过 Git 双 Remote 配置实现一次推送同步更新两个平台。

### 1. 在 Gitee 创建镜像仓库

在 Gitee 上通过"导入仓库"功能，从 GitHub 导入：

- Gitee 仓库地址：`https://gitee.com/hangxu969/local-k8s-gitops.git`
- 设置仓库为**公开**（ArgoCD 无需认证即可拉取）

### 2. 修改 ArgoCD 配置

将所有引用 GitHub 仓库地址的地方改为 Gitee：

#### 2.1 ApplicationSet（Git 生成器的 repoURL）

```yaml
# argocd/applicationsets/appset-helm.yaml
# argocd/applicationsets/appset-kustomize.yaml
repoURL: https://gitee.com/hangxu969/local-k8s-gitops.git
```

#### 2.2 AppProject（sourceRepos 白名单）

```yaml
# argocd/projects/default-project.yaml
sourceRepos:
  - "https://gitee.com/hangxu969/local-k8s-gitops.git"
  - "https://charts.external-secrets.io"
  # ... 其他 Helm 仓库
```

#### 2.3 ArgoCD Repo Secret

```bash
# 更新集群中的 repo secret
kubectl -n argocd patch secret repo-local-k8s-gitops --type merge \
  -p "{\"data\":{\"url\":\"$(echo -n 'https://gitee.com/hangxu969/local-k8s-gitops.git' | base64)\"}}"
```

### 3. 配置 Git 双 Remote 推送

在本地仓库中配置三个 remote，实现灵活推送：

```bash
# 查看初始状态（仅 origin 指向 GitHub）
git remote -v
# origin  git@github.com:hangx969/local-k8s-gitops.git (fetch)
# origin  git@github.com:hangx969/local-k8s-gitops.git (push)

# 添加 gitee remote（单独推送到 Gitee 时使用）
git remote add gitee https://gitee.com/hangxu969/local-k8s-gitops.git

# 添加 all remote（一次推送到两个平台）
git remote add all git@github.com:hangx969/local-k8s-gitops.git
git remote set-url --add --push all git@github.com:hangx969/local-k8s-gitops.git
git remote set-url --add --push all https://gitee.com/hangxu969/local-k8s-gitops.git
```

配置完成后的 remote 结构：

```
all     git@github.com:hangx969/local-k8s-gitops.git (fetch)
all     git@github.com:hangx969/local-k8s-gitops.git (push)
all     https://gitee.com/hangxu969/local-k8s-gitops.git (push)
gitee   https://gitee.com/hangxu969/local-k8s-gitops.git (fetch)
gitee   https://gitee.com/hangxu969/local-k8s-gitops.git (push)
origin  git@github.com:hangx969/local-k8s-gitops.git (fetch)
origin  git@github.com:hangx969/local-k8s-gitops.git (push)
```

### 4. 日常使用

```bash
# 推荐：一次推送到 GitHub + Gitee（ArgoCD 能立即同步）
git push all main

# 仅推送到 GitHub
git push origin main

# 仅推送到 Gitee
git push gitee main
```

## 补充说明

### 为什么不用 GitHub Actions 自动同步？

GitHub Actions 需要 GitHub 的 webhook 触发，而我们的问题正是 GitHub 网络不稳定。用双 Remote 推送更直接可靠，不依赖任何第三方服务。

### 为什么 Gitee 仓库设为公开？

ArgoCD 的 repo secret 目前只配置了 `type: git` 和 `url`，没有 username/password。公开仓库可以免认证拉取，配置最简单。如果需要改为私有仓库，需要在 repo secret 中添加 Gitee 的 username 和 personal access token。

### .git/config 中的 remote 配置

双 Remote 配置写在 `.git/config` 中（不会被提交到 Git），内容如下：

```ini
[remote "origin"]
    url = git@github.com:hangx969/local-k8s-gitops.git
    fetch = +refs/heads/*:refs/remotes/origin/*
[remote "gitee"]
    url = https://gitee.com/hangxu969/local-k8s-gitops.git
    fetch = +refs/heads/*:refs/remotes/gitee/*
[remote "all"]
    url = git@github.com:hangx969/local-k8s-gitops.git
    fetch = +refs/heads/*:refs/remotes/all/*
    pushurl = git@github.com:hangx969/local-k8s-gitops.git
    pushurl = https://gitee.com/hangxu969/local-k8s-gitops.git
```

### 其他同步方案对比

| 方案 | 优点 | 缺点 |
|------|------|------|
| **双 Remote 推送**（当前方案）| 简单可靠，不依赖第三方 | 需要手动 `git push all` |
| Gitee API 同步 | 可脚本化 | 仅 Fork 仓库可用，导入仓库不支持 |
| GitHub Actions 镜像 | 全自动 | 依赖 GitHub 网络，有 CI 延迟 |
| Gitee 定时同步 | 无需本地操作 | 同步频率受限（通常 1 小时），不够及时 |
