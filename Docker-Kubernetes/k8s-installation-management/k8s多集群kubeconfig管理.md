---
title: k8s多集群kubeconfig管理
tags:
  - kubernetes
  - k8s-installation
  - kubeconfig
  - kubectx
  - kubens
aliases:
  - 多集群管理
  - kubeconfig管理
  - kubectx与kubens
date: 2026-09-12
sources:
  - "[[0raw/多集群切换乱？用kubectx]]"
---

# 多集群管理

在实际生产环境中,往往需要维护多个k8s集群,如何实现在一台机器上操作多个集群。通过设置kubeconfig文件来实现。

# 合并多个kubeconfig文件

## 方案1：kubectl config命令

假设存在两套集群,集群1：master1/node1、集群2：master2/node2。现在在master1上配置访问master2的集群

查看两个集群

```sh
kubectl config view
#或者直接查看config文件
cat /root/.kube/config
```

在集群1上添加集群2的信息

```sh
#添加cluster，在集群1上
kubectl config set-cluster k8smaster2 --server=https://192.168.40.185:6443 --insecure-skip-tls-verify=true

#添加user
##集群2上获取token
kubeadm token create --print-join-command
##集群1上设置token
kubectl config set-credentials k8smaster2-user --token=xxx

#添加context，集群1上
kubectl config set-context k8smaster2-context --cluster=k8smaster2  --user=k8smaster2-user

#可以在集群1上通过切换context来操作
kubectl config use-context k8smaster2-context
```

## 方案2：`KUBECONFIG` 环境变量指向多个文件

通过在 KUBECONFIG 环境变量中指定多个文件，可以临时将 KUBECONFIG 文件组合在一起，并在 `kubectl `中使用。如下，那么kubeconfig 是在内存中做的合并：

```sh
export KUBECONFIG=~/.kube/config:~/another-config-file-location
```

> [!important] 多文件合并优先级
> Kubernetes 的规则是：**第一个设置某个值或同名 map key 的文件胜出**，不是后面的文件覆盖前面的文件。例如两个文件都定义了名为 `prod` 的 context，使用前一个文件中的完整定义。可用 `kubectl config view` 检查最终合并结果。

## 方案3：`flatten` 导出

```sh
export KUBECONFIG=~/.kube/config:~/anotherconfig
kubectl config view --flatten
```

`--flatten`：将生成的 kubeconfig 文件扁平化为自包含的输出（用于创建可移植的kubeconfig 文件）

如果需要，还可以管道输出到另外一个新文件。

## 方案4：kubectl 插件 konfig

`kubectl` 有个 `krew` 插件包管理器，可以通过 `krew` 安装 `konfig` 实用插件来管理 kubeconfig。

安装：

```sh
kubectl krew install konfig
```

`krew `插件 `konfig` 可以帮助你管理 `~/.kube/config`，使用 `konfig` 插件的语法如下:

```sh
kubectl konfig import -s new.yaml
```

# kubectx 与 kubens：多集群快速切换

`kubectx` 用来切换 kubeconfig 中的 context，`kubens` 用来修改当前 context 的默认 namespace。它们没有引入新的 Kubernetes 连接机制，而是把 `kubectl config use-context` 和 namespace 配置封装成更短、更适合交互操作的命令。

## context 的组成与切换原理

kubeconfig 的核心关系如下：

- `clusters`：API Server 地址、CA 等集群连接信息。
- `users`：证书、Token 或 `exec` 凭证等身份信息。
- `contexts`：把一个 cluster、一个 user 和可选的默认 namespace 组合起来。
- `current-context`：kubectl 默认使用的 context。

原生 kubectl 已经能够完成查看和切换：

```sh
kubectl config get-contexts
kubectl config current-context
kubectl config use-context prod-ap-sg
```

kubectx 的价值在于缩短命令、支持返回上一个 context、重命名长 context，并可配合 `fzf` 进行交互式模糊选择。

## 安装

优先使用项目官方列出的包管理方式，避免在笔记中固定某个可能过期的 release 版本：

| 平台/方式 | 命令 |
|---|---|
| macOS 或 Linux（Homebrew） | `brew install kubectx` |
| Debian/Ubuntu | `sudo apt install kubectx` |
| Arch Linux | `sudo pacman -S kubectx` |
| Windows（Chocolatey） | `choco install kubens kubectx` |
| Windows（Scoop） | `scoop bucket add main && scoop install main/kubens main/kubectx` |
| kubectl Krew 插件 | `kubectl krew install ctx && kubectl krew install ns` |

Krew 方式对应的命令是 `kubectl ctx` 和 `kubectl ns`；独立安装则使用 `kubectx` 和 `kubens`。

## kubectx 常用操作

```sh
# 列出 context；安装 fzf 后会进入交互式模糊选择
kubectx

# 切换到指定 context
kubectx prod-ap-sg

# 返回上一个 context，适合 dev/prod 往返
kubectx -

# 将云厂商生成的长 context 重命名为短名称：新名称=旧名称
kubectx prod-ap-sg=arn:aws:eks:ap-southeast-1:123456789012:cluster/prod-ap-sg

# 启动只暴露指定 context 的隔离 shell
kubectx -s prod-ap-sg

# 启动阻止写操作的只读 shell
kubectx -r prod-ap-sg
```

> [!note] 交互式选择条件
> 只有当 `fzf` 在 `PATH` 中时，无参数运行 `kubectx`/`kubens` 才会显示可搜索菜单。设置 `KUBECTX_IGNORE_FZF=1` 可临时关闭该行为。没有 `fzf` 时仍可列出名称并通过参数精确切换。

`kubectx -r` 是本地防误操作层，不应替代 Kubernetes RBAC。生产环境仍应使用受限凭证，并把日常 context 绑定到只读或最小权限身份。

## kubens 常用操作

```sh
# 列出 namespace；安装 fzf 后可交互选择
kubens

# 修改当前 context 的默认 namespace
kubens kube-system

# 返回上一个 namespace
kubens -

# 即使 namespace 尚不存在也强制设置
kubens namespace-404 -f
```

执行 `kubens monitoring` 后，后续 `kubectl get pods` 默认查询 `monitoring`，无需每次附加 `-n monitoring`。切换 context 后应重新确认默认 namespace，因为 namespace 是 context 的组成部分。

## 使用 kube-ps1 持续显示当前位置

只依赖记忆区分 dev、staging、prod 风险很高。`kube-ps1` 可以把当前 context 和 namespace 常驻显示在 Bash/Zsh 提示符中。

```sh
# macOS
brew install kube-ps1

# 或从源码安装
git clone https://github.com/jonmosco/kube-ps1.git ~/.kube-ps1
source ~/.kube-ps1/kube-ps1.sh
```

根据 context 名称动态着色：

```sh
kube_ps1_ctx_color() {
  local context="$1"

  case "$context" in
    *prod*)          echo red ;;
    *staging*|*stg*) echo yellow ;;
    *dev*)           echo green ;;
    *)               echo cyan ;;
  esac
}

export KUBE_PS1_CTX_COLOR_FUNCTION=kube_ps1_ctx_color
export KUBE_PS1_PREFIX="["
export KUBE_PS1_SUFFIX="] "
```

将它接入提示符：

```sh
# Bash
PS1='$(kube_ps1)'$PS1

# Zsh
PROMPT='$(kube_ps1)'$PROMPT
```

最终提示符会持续显示类似 `[prod-ap-sg:default]` 的信息。动态颜色应使用 kube-ps1 官方的 `KUBE_PS1_CTX_COLOR_FUNCTION`，无需修改 `PROMPT_COMMAND`。

## 多 kubeconfig 合并与排错

Linux/macOS 使用冒号分隔多个文件，Windows 使用分号：

```sh
export KUBECONFIG="${HOME}/.kube/config:${HOME}/.kube/eks.yaml:${HOME}/.kube/gke.yaml"

# 查看合并后的有效配置
kubectl config view
kubectl config get-contexts
kubectl config get-users
```

同名 context、cluster 或 user 冲突时，**列表中第一个定义该键的文件胜出**。因此应给 context 加上环境、账号或地域信息，例如 `prod-aws-a-sg`、`prod-gcp-a-tw`，不要在多个文件中都使用笼统的 `prod`。

需要生成单一、自包含的 kubeconfig 时：

```sh
KUBECONFIG="${HOME}/.kube/config:${HOME}/.kube/eks.yaml:${HOME}/.kube/gke.yaml" \
  kubectl config view --flatten > "${HOME}/merged-kubeconfig.yaml"

chmod 600 "${HOME}/merged-kubeconfig.yaml"
KUBECONFIG="${HOME}/merged-kubeconfig.yaml" kubectl config get-contexts
```

`--flatten` 会把外部证书引用转成内联数据，便于迁移，但也会让单个文件包含更多敏感凭证。不要提交到 Git，也不要接收和直接使用不可信 kubeconfig；其中的 `exec` 凭证插件可能执行本地命令。

## 生产环境防误操作清单

- [ ] context 名称包含环境、云账号/项目和地域，避免重名。
- [ ] 提示符持续显示 context 和 namespace，生产环境使用醒目颜色。
- [ ] 日常生产 context 使用只读或最小权限凭证，写权限单独建 context。
- [ ] 高风险操作前运行 `kubectl config current-context`，必要时显式传入 `--context`。
- [ ] 进入并行排障场景时使用 `kubectx -s` 隔离 shell，降低全局 context 来回切换的风险。
- [ ] 多 kubeconfig 合并后用 `kubectl config view` 检查同名条目和实际生效配置。
- [ ] 合并后的 kubeconfig 权限设置为 `600`，不进入代码仓库或共享聊天记录。
- [ ] `kubectx -r`、提示符颜色和 shell 包装只能辅助防呆，真正的权限边界仍是认证凭证与 RBAC。

## 参考资料

- [kubectx/kubens 官方仓库](https://github.com/ahmetb/kubectx)
- [Kubernetes：使用 kubeconfig 文件组织集群访问](https://kubernetes.io/zh-cn/docs/concepts/configuration/organize-cluster-access-kubeconfig/)
- [kube-ps1 官方仓库](https://github.com/jonmosco/kube-ps1)
- 原始剪藏：[[0raw/多集群切换乱？用kubectx]]

# OIDC 认证：kubelogin

> 来源：[K8S工具推荐：告别复杂认证！Kubernetes登录神器kubelogin指南](https://mp.weixin.qq.com/s?__biz=MzkxNzAyMzA3Nw==&mid=2247485698&idx=1&sn=47443ce3322a407525cd6ccdffbffb29)

传统 kubeconfig 使用静态证书或长期 token，存在密钥泄露风险。kubelogin 是基于 OpenID Connect（OIDC）的 kubectl 插件，实现浏览器一键登录 + 短期令牌自动刷新。

- 官方仓库：https://github.com/int128/kubelogin

## 核心特性

| 特性 | 说明 |
|------|------|
| 浏览器一键登录 | 运行 kubectl 命令时自动弹出浏览器完成 OIDC 认证（支持 Google / Azure AD 等） |
| 短期令牌 | 默认 1 小时有效期的 ID Token，替代长期静态凭证 |
| 自动刷新 | 通过 Refresh Token 自动续期，无需手动重新认证 |
| 加密存储 | 令牌存储在系统钥匙串中（macOS Keychain / Windows Credential Manager） |
| 无缝集成 | 作为 kubectl 插件运行，不改变现有 kubectl 工作流 |

## 安装

```bash
# macOS
brew install kubelogin

# Windows
choco install kubelogin

# krew 插件方式
kubectl krew install oidc-login
```

## kubeconfig 配置

在 kubeconfig 的 users 段使用 exec 模式调用 kubelogin：

```yaml
users:
- name: oidc
  user:
    exec:
      apiVersion: client.authentication.k8s.io/v1
      command: kubectl
      args:
        - oidc-login
        - get-token
        - --oidc-issuer-url=ISSUER_URL
        - --oidc-client-id=YOUR_CLIENT_ID
```

配置完成后，正常执行 `kubectl get pods` 等命令时会自动触发浏览器认证流程。

## 适用场景

- **企业 SSO 集成**：接入公司统一身份认证（Azure AD、Okta、Keycloak 等）
- **多团队共享集群**：每个用户用自己的身份登录，便于审计和权限控制
- **合规审计要求**：所有操作都关联到具体用户身份，满足安全合规
- **开发测试环境快速切换**：浏览器登录比手动管理证书/token 更高效

> [!tip] 调试
> 添加 `-v1` 参数查看详细认证日志：`kubectl oidc-login get-token -v1`
