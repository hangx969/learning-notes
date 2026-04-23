---
title: "部署K8S时关闭防火墙被吐槽了，我连夜整理全部需要开放的端口"
source: "https://mp.weixin.qq.com/s/q0qyYq7l0SssaQ1IgfuqxQ"
author:
  - "[[运维李哥]]"
published:
created: 2026-04-23
description: "前面写了一篇K8S部署的文章被吐槽了，文章如下：领导让我部署一套Kubernetes集群，我咔咔咔给他搞定（1"
tags:
  - "clippings"
---
运维李哥 *2025年11月28日 07:30*

前面写了一篇K8S部署的文章被吐槽了，文章如下：

```
systemctl disable --now firewalld
```

这样做确实是为了方便部署，图省事。

为了避免这位未关注公众号的运维同行再吐槽，我就整理部署Kubernetes时所需要开放的防火墙端口，如果是云平台，可以开放对应的安全组策略。

其实在生产环境，正确做法也是这样：

> **开启 firewalld + 精准开放 Kubernetes 相关所需端口** 。

## 1 容器运行时

**如果使用containerd 作为容器运行时，不需要额外开放端口**

**原因：**

- 使用 Unix Socket（ `/run/containerd/containerd.sock` ）
- 不监听 TCP/UDP
- 不对外暴露服务

> 所以防火墙里不需要考虑 containerd。

## 2 kubeadm 核心端口

## 2.1 Master 节点汇总

| 端口 | 协议 | 用途 |
| --- | --- | --- |
| 6443/tcp | TCP | API Server |
| 2379-2380/tcp | TCP | etcd |
| 10250/tcp | TCP | kubelet API |
| 10257/tcp | TCP | controller-manager |
| 10259/tcp | TCP | scheduler |

## 2.2 Worker 节点端口汇总

| 端口 | 协议 | 用途 |
| --- | --- | --- |
| 10250/tcp | TCP | kubelet API |
| 30000-32767/tcp/udp | TCP/UDP | NodePort 服务 |

## 3 kubelet 内部端口

| 端口 | 用途 | 是否需要防火墙放行 |
| --- | --- | --- |
| 10248/tcp | kubelet本地健康检查 | 本地监听，不需开放 |
| 10250/tcp | kubelet API | 对 Master 开放 |

> 你在节点上看到 10248 是正常现象，它绑定在 127.0.0.1 或 CNI 网卡上，本地使用，不对外暴露。

## 4 kube-proxy 端口

| 端口 | 用途 | 是否开放 |
| --- | --- | --- |
| 10249/tcp | healthz / metrics（本地） | 本地监听，不需要开放 |
| 10256/tcp | IPVS healthz（IPVS 模式必需） | Worker 节点需要放通 |
| 80/tcp、443/tcp | 对外健康检查 / LB | 视 Ingress 模式而定，HostNetwork模式要开放 |

> **10249 只是本地健康检查，不需放行** 。 **10256 是 IPVS 模式健康检查，必须放通** 。

## 5 Calico 网络端口

Calico 根据模式不同，需要开放的端口：

| 模式 | 端口 / 协议 | 用途 |
| --- | --- | --- |
| IP-in-IP | 协议 4（IPIP） | 跨节点封包 |
| VXLAN | 4789/udp | VXLAN 封装 |
| BGP | 179/tcp | BGP 路由同步 |
| Typha（大集群） | 5473/tcp | Typha <-> Felix 通信 |

> 如果不使用 BGP 或 Typha，可以不开放 179/5473。

## 6 Ingress 端口

## 6.1 NodePort 模式

- NodePort 范围：30000-32767/tcp/udp
- 外部访问无需额外端口，Worker 已开放 NodePort 范围

## 6.2 HostNetwork 模式

- HTTP：80/tcp
- HTTPS：443/tcp
- 必须开放对应端口

> LoadBalancer 模式一般由云提供负载均衡，不需节点开放 80/443。

## 7 firewalld配置

### 7.1 master节点配置

配置Kubernetes核心端口及worker节点相关连接端口，Calico 网络插件，Ingress/NodePort 可选：

```
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

> Master 节点本地自检端口 10248/10249 不用放行。NodePort端口也可以可以根据实际使用来开放

### 7.2 Worker节点配置

Worker 节点主要跑 kubelet、kube-proxy、Pod（可能包含 NodePort / Ingress）：

```
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

> Worker 节点本地自检端口 10248/10249 也无需放行。 Worker 不需要开放 6443。

## 8 检查策略和集群信息

配置后，我特意重启了一下，再检查策略

```
# 检查策略
firewall-cmd --list-all

# 检查集群状态
kubectl get node

# 检查Pod状态
kubectl get pod -A
```


可以看到节点和Pod都是正常运行，需要注意的是：如果后续你发布了服务，需要根据对应的端口进行开放，不然就会导致服务不能访问。
