---
title: K8s部署防火墙端口配置
tags:
  - kubernetes
  - k8s-installation
  - security
  - firewall
aliases:
  - k8s防火墙端口
---

# K8s 部署防火墙端口配置

> 来源：[部署K8S时关闭防火墙被吐槽了，我连夜整理全部需要开放的端口](https://mp.weixin.qq.com/s/q0qyYq7l0SssaQ1IgfuqxQ)

生产环境正确做法：**开启 firewalld + 精准开放 Kubernetes 所需端口**，而不是 `systemctl disable --now firewalld` 一关了之。

---

## 1 容器运行时（containerd）

**不需要额外开放端口**。containerd 使用 Unix Socket（`/run/containerd/containerd.sock`），不监听 TCP/UDP，不对外暴露服务。

## 2 kubeadm 核心端口

### Master 节点

| 端口 | 协议 | 用途 |
|------|------|------|
| 6443/tcp | TCP | API Server |
| 2379-2380/tcp | TCP | etcd |
| 10250/tcp | TCP | kubelet API |
| 10257/tcp | TCP | controller-manager |
| 10259/tcp | TCP | scheduler |

### Worker 节点

| 端口 | 协议 | 用途 |
|------|------|------|
| 10250/tcp | TCP | kubelet API |
| 30000-32767/tcp/udp | TCP/UDP | NodePort 服务 |

## 3 kubelet 内部端口

| 端口 | 用途 | 是否需要防火墙放行 |
|------|------|---------------------|
| 10248/tcp | kubelet 本地健康检查 | 本地监听，不需开放 |
| 10250/tcp | kubelet API | 对 Master 开放 |

> 节点上看到 10248 是正常现象，它绑定在 127.0.0.1 或 CNI 网卡上，本地使用。

## 4 kube-proxy 端口

| 端口 | 用途 | 是否开放 |
|------|------|----------|
| 10249/tcp | healthz / metrics（本地） | 本地监听，不需要开放 |
| 10256/tcp | IPVS healthz（IPVS 模式必需） | Worker 节点需要放通 |
| 80/tcp、443/tcp | 对外健康检查 / LB | 视 Ingress 模式而定 |

> 10249 只是本地健康检查，不需放行；10256 是 IPVS 模式健康检查，必须放通。

## 5 Calico 网络端口

根据 Calico 模式不同，需要开放的端口：

| 模式 | 端口/协议 | 用途 |
|------|-----------|------|
| IP-in-IP | 协议 4（IPIP） | 跨节点封包 |
| VXLAN | 4789/udp | VXLAN 封装 |
| BGP | 179/tcp | BGP 路由同步 |
| Typha（大集群） | 5473/tcp | Typha ↔ Felix 通信 |

> 如果不使用 BGP 或 Typha，可以不开放 179/5473。

## 6 Ingress 端口

### NodePort 模式

- NodePort 范围 30000-32767/tcp/udp
- 外部访问无需额外端口，Worker 已开放 NodePort 范围

### HostNetwork 模式

- HTTP：80/tcp
- HTTPS：443/tcp
- 必须开放对应端口

> LoadBalancer 模式一般由云提供负载均衡，不需节点开放 80/443。

## 7 firewalld 配置

### Master 节点

```bash
# 开启防火墙并设置开机自启动
systemctl enable --now firewalld

# Kubernetes 核心资源
firewall-cmd --permanent --add-port=6443/tcp
firewall-cmd --permanent --add-port=2379-2380/tcp
firewall-cmd --permanent --add-port=10250/tcp
firewall-cmd --permanent --add-port=10257/tcp
firewall-cmd --permanent --add-port=10259/tcp
firewall-cmd --permanent --add-port=10256/tcp

# Ingress HostNetwork / NodePort（可选）
firewall-cmd --permanent --add-port=80/tcp
firewall-cmd --permanent --add-port=443/tcp
firewall-cmd --permanent --add-port=30000-32767/tcp
firewall-cmd --permanent --add-port=30000-32767/udp

# Calico 网络插件
firewall-cmd --permanent --add-port=4789/udp
firewall-cmd --permanent --add-port=179/tcp
firewall-cmd --permanent --add-port=5473/tcp
firewall-cmd --permanent --add-protocol=ipip

# 重新加载防火墙
firewall-cmd --reload
```

> Master 节点本地自检端口 10248/10249 不用放行。NodePort 端口可根据实际使用按需开放。

### Worker 节点

```bash
# 开启防火墙并设置开机自启动
systemctl enable --now firewalld

# kubelet
firewall-cmd --permanent --add-port=10250/tcp

# kube-proxy IPVS
firewall-cmd --permanent --add-port=10256/tcp

# Ingress HostNetwork / NodePort（可选）
firewall-cmd --permanent --add-port=80/tcp
firewall-cmd --permanent --add-port=443/tcp
firewall-cmd --permanent --add-port=30000-32767/tcp
firewall-cmd --permanent --add-port=30000-32767/udp

# Calico 网络插件
firewall-cmd --permanent --add-port=4789/udp
firewall-cmd --permanent --add-port=179/tcp
firewall-cmd --permanent --add-port=5473/tcp
firewall-cmd --permanent --add-protocol=ipip

# 重新加载防火墙
firewall-cmd --reload
```

> Worker 节点本地自检端口 10248/10249 也无需放行。Worker 不需要开放 6443。

## 8 验证

```bash
# 检查防火墙策略
firewall-cmd --list-all

# 检查集群状态
kubectl get node

# 检查 Pod 状态
kubectl get pod -A
```

> [!tip] 提示
> 配置后建议重启节点再验证，确保 firewalld 开机自启且规则持久化生效。如果后续发布新服务，需要根据对应端口进行开放。

## 端口速查总结

| 组件 | 端口 | Master | Worker | 备注 |
|------|------|--------|--------|------|
| API Server | 6443 | **是** | 否 | |
| etcd | 2379-2380 | **是** | 否 | |
| kubelet API | 10250 | **是** | **是** | |
| controller-manager | 10257 | **是** | 否 | |
| scheduler | 10259 | **是** | 否 | |
| kube-proxy IPVS | 10256 | **是** | **是** | IPVS 模式必需 |
| kubelet healthz | 10248 | 否 | 否 | 本地监听 |
| kube-proxy healthz | 10249 | 否 | 否 | 本地监听 |
| NodePort | 30000-32767 | 可选 | **是** | |
| Calico VXLAN | 4789/udp | **是** | **是** | VXLAN 模式 |
| Calico IPIP | 协议 4 | **是** | **是** | IPIP 模式 |
| Calico BGP | 179 | 可选 | 可选 | BGP 模式 |
| Calico Typha | 5473 | 可选 | 可选 | 大集群 |
| Ingress HTTP(S) | 80/443 | 可选 | 可选 | HostNetwork 模式 |
