---
title: ArgoCD部署Helm应用时域名解析失败问题排查与解决
tags:
  - kubernetes
  - cicd
  - argocd
  - troubleshooting
  - dns
aliases:
  - ArgoCD DNS解析问题
---

## 问题背景

在使用 ArgoCD（v3.3.6）通过 ApplicationSet + Umbrella Chart 模式部署 external-secrets 时，Application 长期处于 `Unknown` 状态，先后出现两个阶段的报错。

### 阶段一：域名完全无法解析（no such host）

ArgoCD Application 报错：

```text
ComparisonError: Failed to load target state: failed to generate manifest for source 1 of 1:
rpc error: code = Unknown desc = Manifest generation error (cached):
`helm dependency build` failed exit status 1:
Error: could not download https://charts.external-secrets.io/external-secrets-2.2.0.tgz:
failed to fetch https://charts.external-secrets.io/index.yaml:
Get "https://charts.external-secrets.io/index.yaml":
dial tcp: lookup charts.external-secrets.io on 10.96.0.10:53: no such host
```

原因：CoreDNS Pod 无法将 DNS 查询转发到上游 DNS 服务器，forward 插件超时报 `i/o timeout`。CoreDNS 默认从节点的 `/etc/resolv.conf` 读取上游 DNS 地址，当该配置不稳定或上游不可达时，所有外部域名解析均会失败。

### 阶段二：IPv6 连接不可达（network is unreachable）

**重启 CoreDNS 后**上游转发恢复，但紧接着暴露了第二个问题：

```text
ComparisonError: Failed to load target state: failed to generate manifest for source 1 of 1:
rpc error: code = Unknown desc = Manifest generation error (cached):
`helm dependency build` failed exit status 1:
Error: could not download https://charts.external-secrets.io/external-secrets-2.2.0.tgz:
failed to fetch https://charts.external-secrets.io/index.yaml:
Get "https://charts.external-secrets.io/index.yaml":
dial tcp [2606:50c0:8003::154]:443: connect: network is unreachable
```

关键信息：Helm 尝试连接的是 **IPv6 地址** `[2606:50c0:8003::154]:443`，而非 IPv4 地址。

## 环境信息

| 组件 | 版本/信息 |
|------|----------|
| Kubernetes | v1.35.3 |
| ArgoCD | v3.3.6 |
| CoreDNS | v1.13.1（Go 1.25.2 编译） |
| Helm | v3.19.4（无 CGO，纯 Go DNS） |
| 节点系统 | Rocky Linux 10.1, aarch64 |
| CNI | Calico |
| 集群拓扑 | 3 节点（1 control-plane + 2 worker） |

## 根因分析

### 1. CoreDNS 上游 DNS 转发失败（阶段一根因）

CoreDNS 的 forward 插件默认配置为：

```text
forward . /etc/resolv.conf
```

这会读取 **CoreDNS Pod 所在宿主机节点**的 `/etc/resolv.conf`，使用其中的 nameserver 作为上游 DNS。在 kubeadm 部署的集群中，这个文件通常指向从 DHCP 或 NetworkManager 获取的 DNS 服务器（如路由器网关地址 `192.168.x.1` 或 ISP 分配的 DNS）。

当宿主机的上游 DNS 服务器不稳定、不可达或响应缓慢时，CoreDNS 的 forward 插件会超时（`i/o timeout`），导致所有外部域名解析失败，Pod 中的应用看到的就是 `no such host`。

### 2. Go 纯 DNS 解析器的 IPv6 缺陷（阶段二根因）

ArgoCD 的 repo-server 组件负责执行 `helm dependency build`。Pod 内的 Helm 二进制文件是 **不带 CGO 编译** 的（即 `GODEBUG=netdns=go`），使用 Go 的纯 DNS 解析器。

当 Go 的纯 DNS 解析器查询 `charts.external-secrets.io` 时：

1. 同时发起 A（IPv4）和 AAAA（IPv6）查询
2. 收到 AAAA 记录后，Go 的 `net.Dialer` **优先尝试 IPv6 连接**
3. 集群节点/Pod 网络并未启用 IPv6 路由，连接失败报 `network is unreachable` 或 `cannot assign requested address`
4. **Go 的 HTTP Dialer 在遇到 `EADDRNOTAVAIL` 或 `ENETUNREACH` 时不会自动回退到 IPv4**——这是 Go 标准库的已知行为

这意味着只要 DNS 返回了 AAAA 记录，Helm 就会尝试 IPv6 并失败，即使 IPv4 完全可用。

### 3. 排除的方案

| 尝试的方案 | 为什么无效 |
|-----------|-----------|
| 在 Worker 节点上通过 sysctl 禁用 IPv6 | sysctl 设置不会传播到 Pod 的网络命名空间 |
| 用 Init Container 在 Pod 内禁用 IPv6 | Go 的 Dialer 对 `EADDRNOTAVAIL` 也不会回退 IPv4 |
| 修改 ndots/search 域 | 不影响 IPv6 行为 |
| 在 CoreDNS Corefile 的**单个 Server Block** 中用 `template` 抑制 AAAA | cluster.local 域的 AAAA 查询会返回 NOERROR，与 A 查询的 NXDOMAIN 冲突，导致 Go 的搜索域遍历行为异常 |

## 解决方案

### 方案核心：CoreDNS 双 Server Block + AAAA 抑制

通过修改 CoreDNS 的 ConfigMap（`kube-system/coredns`），将 Corefile 拆分为两个 Server Block：

- **cluster.local Block**：正常处理集群内部域名（保留 cache）
- **.:53 Block**：处理外部域名，用 `template` 插件对所有 AAAA 查询返回空应答（NOERROR + 空记录），并移除 cache 避免缓存干扰

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: coredns
  namespace: kube-system
data:
  Corefile: |
    # ============================================
    # Server Block 1: 集群内部域名（正常处理）
    # ============================================
    cluster.local in-addr.arpa ip6.arpa {
        errors
        health {
            lameduck 5s
        }
        ready
        kubernetes cluster.local in-addr.arpa ip6.arpa {
            pods insecure
            fallthrough in-addr.arpa ip6.arpa
            ttl 30
        }
        prometheus :9153
        cache 30
        loop
        reload
        loadbalance
    }

    # ============================================
    # Server Block 2: 外部域名
    # - 用 template 抑制 AAAA 响应（返回空应答）
    # - 不使用 cache（避免 AAAA NOERROR 与 A NXDOMAIN 的缓存冲突）
    # - 指定明确的上游 DNS 服务器
    # ============================================
    .:53 {
        errors
        health {
            lameduck 5s
        }
        ready

        # 关键：对所有外部域名的 AAAA 查询返回空应答
        # rcode 设为 NOERROR，但不返回任何 AAAA 记录
        # Go 解析器收到空 AAAA 后会回退使用 A 记录（IPv4）
        template IN AAAA {
            rcode NOERROR
        }

        # 指定上游 DNS，使用 sequential 策略（优先第一个）
        forward . 114.114.114.114 8.8.8.8 {
            policy sequential
            max_concurrent 1000
        }

        prometheus :9153
        loop
        reload
        loadbalance
    }
```

### 关键设计选择

1. **为什么要拆分为两个 Server Block？**
   - 如果在单个 Server Block 中对所有域名应用 `template IN AAAA`，会影响 cluster.local 的解析：当 Go 解析器对 `charts.external-secrets.io` 在搜索域展开后查询 `charts.external-secrets.io.cluster.local` 时，AAAA 查询被 template 拦截返回 NOERROR，而 A 查询返回 NXDOMAIN。Go 解析器认为 "AAAA 成功了所以这个域名可能存在"，导致搜索域遍历异常。
   - 拆分后，cluster.local Server Block 不受 template 影响，外部域名的 AAAA 查询才会被拦截。

2. **为什么外部 Server Block 不用 cache？**
   - CoreDNS 的 cache 插件会缓存 template 生成的 AAAA NOERROR 响应。当后续的 A 查询到达时，cache 中已有该域名的 NOERROR 状态，可能干扰正常的 A 记录解析。
   - 去掉 cache 后，每次查询都走 forward，template 只拦截 AAAA，A 查询正常转发。

3. **为什么指定 `114.114.114.114` 和 `8.8.8.8`？**
   - 集群部署在中国大陆网络环境，使用国内 DNS（114）作为首选，Google DNS（8.8.8.8）作为备选。
   - `policy sequential` 确保优先使用第一个可用的 DNS 服务器。

### 补充：repo-server dnsConfig 优化

除了 CoreDNS 配置，还对 ArgoCD 的 repo-server Deployment 添加了 dnsConfig，提高 DNS 解析的可靠性：

```bash
kubectl -n argocd patch deployment argocd-repo-server --type strategic -p '{
  "spec": {
    "template": {
      "spec": {
        "dnsConfig": {
          "options": [
            {"name": "ndots", "value": "2"},
            {"name": "timeout", "value": "10"},
            {"name": "attempts", "value": "5"},
            {"name": "single-request-reopen"}
          ]
        }
      }
    }
  }
}'
```

| 参数 | 说明 |
|------|------|
| `ndots: 2` | 减少不必要的搜索域展开（外部域名通常含 2+ 个点，直接查询完整域名） |
| `timeout: 10` | DNS 查询超时 10 秒（默认 5 秒在网络不佳时可能不够） |
| `attempts: 5` | 最多重试 5 次 |
| `single-request-reopen` | A 和 AAAA 查询使用不同的源端口，避免某些 DNS 服务器将两个查询的响应混淆 |

## 附：CRD 注解过大导致同步失败

DNS 问题解决后，ArgoCD 同步 external-secrets 时又遇到了一个新错误：

```text
CustomResourceDefinition.apiextensions.k8s.io "clustersecretstores.external-secrets.io" is invalid:
metadata.annotations: Too long: may not be more than 262144 bytes
```

### 原因

ArgoCD 默认使用 `kubectl apply`（Client-Side Apply），会将完整的资源清单存储在 `kubectl.kubernetes.io/last-applied-configuration` 注解中。external-secrets 的 CRD 非常大，序列化后超过了 Kubernetes 的 262144 字节注解限制。

### 解决方案

在 ApplicationSet 的 `syncOptions` 中添加 `ServerSideApply=true`：

```yaml
syncOptions:
  - CreateNamespace=true
  - ApplyOutOfSyncOnly=true
  - Validate=true
  - PrunePropagationPolicy=foreground
  - ServerSideApply=true  # 使用服务端 Apply，不写入 last-applied-configuration 注解
```

Server-Side Apply（SSA）使用服务端的字段管理机制（Field Management），不再需要 `last-applied-configuration` 注解，从根本上绕过了注解大小限制。

## 最终结果

经过以上修复：

1. `helm dependency build` 成功完成（DNS 解析走 IPv4）
2. ArgoCD manifest 生成成功（Application 从 `Unknown` 变为 `OutOfSync`）
3. CRD 通过 Server-Side Apply 成功同步
4. external-secrets 所有 3 个 Pod（controller、cert-controller、webhook）正常运行
5. Application 状态：`Synced` + `Healthy`

## 总结

| 问题 | 根因 | 解决方案 |
|------|------|---------|
| Helm 域名解析失败 | Go 纯 DNS 解析器优先 IPv6，集群无 IPv6 路由 | CoreDNS 双 Server Block + template 抑制 AAAA |
| CRD 同步失败 | last-applied-configuration 注解超过 262KB | 启用 ServerSideApply=true |
