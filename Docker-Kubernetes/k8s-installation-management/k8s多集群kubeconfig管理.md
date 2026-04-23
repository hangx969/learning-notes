---
title: k8s多集群kubeconfig管理
tags:
  - kubernetes
  - k8s-installation
  - kubeconfig
aliases:
  - 多集群管理
  - kubeconfig管理
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

## 方案3：`flatten`

```sh
export KUBECONFIG=~/.kube/config:~/anotherconfig
kubectl config view --flatten
```

`--flatten`：将生成的 kubeconfig 文件扁平化为自包含的输出（用于创建可移植的kubeconfig 文件）

如果需要，还可以管道输出到另外一个新文件。

## 方案3：kubectl插件kconfig

`kubectl` 有个 `krew` 插件包管理器，可以通过 `krew` 安装 `konfig` 实用插件来管理 kubeconfig。

安装：

```sh
kubectl krew install konfig
```

`krew `插件 `konfig` 可以帮助你管理 `~/.kube/config`，使用 `konfig` 插件的语法如下:

```sh
kubectl konfig import -s new.yaml
```

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
