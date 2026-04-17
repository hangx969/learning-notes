---
title: k8s-installation-management 来源批量摘要
tags:
  - knowledgebase/source
  - docker-kubernetes/installation-management
date: 2026-04-17
sources:
  - "[[Docker-Kubernetes/k8s-installation-management/latest-version/安装k8s-1.35-基于rockylinux10-最新步骤]]"
  - "[[Docker-Kubernetes/k8s-installation-management/legacy-versions/安装k8s-1.33-基于rockylinux-最新步骤]]"
  - "[[Docker-Kubernetes/k8s-installation-management/legacy-versions/安装k8s-1.32-基于rockylinux]]"
  - "[[Docker-Kubernetes/k8s-installation-management/legacy-versions/安装k8s-1.30-基于rockylinux]]"
  - "[[Docker-Kubernetes/k8s-installation-management/legacy-versions/安装k8s-1.28]]"
  - "[[Docker-Kubernetes/k8s-installation-management/legacy-versions/安装k8s-1.26-1.27]]"
  - "[[Docker-Kubernetes/k8s-installation-management/legacy-versions/安装k8s-1.23]]"
  - "[[Docker-Kubernetes/k8s-installation-management/legacy-versions/安装k8s-1.20.6-高可用]]"
  - "[[Docker-Kubernetes/k8s-installation-management/二进制安装k8s高可用集群]]"
  - "[[Docker-Kubernetes/k8s-installation-management/2025最新-企业级高可用集群-基于rockylinux]]"
  - "[[Docker-Kubernetes/k8s-installation-management/etcd高可用配置以及模拟集群故障和恢复]]"
  - "[[Docker-Kubernetes/k8s-installation-management/k8s两地三中心架构]]"
  - "[[Docker-Kubernetes/k8s-installation-management/k8s生产环境优化与最佳实践]]"
  - "[[Docker-Kubernetes/k8s-installation-management/k8s迁移容器运行时-版本升级]]"
  - "[[Docker-Kubernetes/k8s-installation-management/k8s故障排查指南]]"
  - "[[Docker-Kubernetes/k8s-installation-management/k8s多集群kubeconfig管理]]"
---

# k8s-installation-management 来源批量摘要

## 元信息
- **原始目录**：`Docker-Kubernetes/k8s-installation-management/`
- **文档数量**：16 篇
- **领域**：Docker-Kubernetes
- **摄入日期**：2026-04-17

## 整体概述
本批次文档全面覆盖了 Kubernetes 集群从安装部署到生产运维的完整生命周期。内容包括从 k8s 1.20 到 1.35 的多版本 kubeadm/二进制安装指南（涵盖 CentOS 和 Rocky Linux 操作系统），企业级高可用集群架构设计（含两地三中心、异地多活方案），以及 etcd 高可用、容器运行时迁移、版本升级、故障排查、多集群管理等生产运维实践。文档整体呈现了从实验环境到生产环境的演进路径，以及从 Docker 到 containerd 的容器运行时迁移趋势。

## 各文档摘要

### [[Docker-Kubernetes/k8s-installation-management/latest-version/安装k8s-1.35-基于rockylinux10-最新步骤|安装k8s-1.35-基于rockylinux10]]
- 核心内容：在 Rocky Linux 10 上使用 kubeadm 安装 Kubernetes 1.35 的完整步骤，采用 containerd 2.x 运行时和 v1beta4 配置 API。
- 关键知识点：
  - Rocky Linux 10 使用 DNF5 包管理器，需配置阿里云镜像源
  - containerd 2.x 配置格式升级为 version = 3
  - kubeadm 配置 API 从 v1beta3 升级到 v1beta4
  - 网络插件使用 Calico 最新版

### [[Docker-Kubernetes/k8s-installation-management/legacy-versions/安装k8s-1.33-基于rockylinux-最新步骤|安装k8s-1.33-基于rockylinux]]
- 核心内容：在 Rocky Linux 8/9 上使用 kubeadm 安装 k8s 1.33 的详细步骤，包含完整的 K8s 架构组件介绍。
- 关键知识点：
  - Rocky Linux 8 执行 yum update 后会升级到 Rocky Linux 9
  - 使用 nmcli 命令配置网络（替代传统 ifcfg 配置文件）
  - 容器运行时为 containerd

### [[Docker-Kubernetes/k8s-installation-management/legacy-versions/安装k8s-1.32-基于rockylinux|安装k8s-1.32-基于rockylinux]]
- 核心内容：在 Rocky Linux 8 上安装 k8s 1.32 的步骤指南，采用单 master + 单 worker 的最小化实验环境。
- 关键知识点：
  - 使用 nmcli 和传统配置文件两种方式配置网络
  - 基础软件包安装清单（lvm2、gcc、openssl 等）
  - 关闭 selinux、swap 等系统准备步骤

### [[Docker-Kubernetes/k8s-installation-management/legacy-versions/安装k8s-1.30-基于rockylinux|安装k8s-1.30-基于rockylinux]]
- 核心内容：在 Rocky Linux 8 上安装 k8s 1.30，同时介绍了 CentOS 停更后的替代方案及国产操作系统生态。
- 关键知识点：
  - 详细介绍了 Rocky Linux 作为 CentOS 替代方案的定位
  - 梳理了银河麒麟、中标麒麟、Deepin、UOS、欧拉、鸿蒙等国产操作系统
  - Rocky Linux 自带 cockpit UI 管理面板

### [[Docker-Kubernetes/k8s-installation-management/legacy-versions/安装k8s-1.28|安装k8s-1.28]]
- 核心内容：在 CentOS 7.9 上使用 kubeadm 安装 k8s 1.28 的步骤，一主两从的典型实验环境。
- 关键知识点：
  - 使用 CentOS 7.9 + VMware NAT 网络模式
  - pod 网段 10.244.0.0/16，service 网段 10.96.0.0/12
  - 使用 Calico 网络插件

### [[Docker-Kubernetes/k8s-installation-management/legacy-versions/安装k8s-1.26-1.27|安装k8s-1.26-1.27]]
- 核心内容：在 CentOS 7.x 上安装 k8s 1.26 和 1.27 版本的步骤，包含完整的系统准备流程。
- 关键知识点：
  - 系统从 CentOS 7.6 升级到 7.9
  - 配置主机间 SSH 无密码登录
  - 关闭 selinux、配置静态 IP 和 hosts 文件

### [[Docker-Kubernetes/k8s-installation-management/legacy-versions/安装k8s-1.23|安装k8s-1.23]]
- 核心内容：在 CentOS 7.9 上使用 kubeadm 安装 k8s 1.23 版本，基于 VMware 虚拟化环境。
- 关键知识点：
  - 详细的 VMware 虚拟机网络配置步骤
  - pod 网段 10.244.0.0/16，service 网段 10.96.0.0/12
  - 配置 4GiB 内存 / 8vCPU / 20G 硬盘

### [[Docker-Kubernetes/k8s-installation-management/legacy-versions/安装k8s-1.20.6-高可用|安装k8s-1.20.6-高可用]]
- 核心内容：在 CentOS 7.9 上安装 k8s 1.20.6 多 master 高可用集群，并详细介绍了离线 yum 源的制作方法。
- 关键知识点：
  - 制作 Docker 和 k8s 的离线 yum 源，适用于全内网环境部署
  - 使用 rpm 强制安装方式处理离线依赖
  - K8s 核心组件架构介绍（API Server、Scheduler、Controller Manager、etcd）

### [[Docker-Kubernetes/k8s-installation-management/二进制安装k8s高可用集群|二进制安装k8s高可用集群]]
- 核心内容：通过二进制方式安装 k8s 1.20.7 多 master 高可用集群，使用 keepalived + nginx 实现负载均衡。
- 关键知识点：
  - 二进制安装 vs kubeadm 安装的对比分析
  - 3 master + 1 worker + VIP 的架构设计
  - 手动安装 etcd、apiserver、controller-manager、scheduler 等组件
  - 使用 keepalived 提供 VIP 高可用

### [[Docker-Kubernetes/k8s-installation-management/2025最新-企业级高可用集群-基于rockylinux|2025最新-企业级高可用集群]]
- 核心内容：企业级高可用 k8s 集群的架构设计与资源规划，涵盖控制节点、工作节点、磁盘和网络的详细配置方案。
- 关键知识点：
  - 控制节点资源配置表：0-100 节点用 8C+32G、100-250 用 16C+32G、250-500 需 etcd 分离
  - 磁盘划分：根分区 100G + etcd 数据盘 100G NVME SSD + 数据盘 500G SSD
  - 网段划分原则：节点网段、Service 网段、Pod 网段三者不能冲突
  - 生产环境最低 3 主 3 从共 6 个节点

### [[Docker-Kubernetes/k8s-installation-management/etcd高可用配置以及模拟集群故障和恢复|etcd高可用配置与故障恢复]]
- 核心内容：在 kubeadm 安装的多 master 集群中配置 etcd 高可用，并演示故障节点的剔除与重新加入流程。
- 关键知识点：
  - 修改 etcd.yaml 的 initial-cluster 参数实现 etcd 集群化
  - 使用 etcdctl member list/remove 管理 etcd 成员
  - 故障节点恢复流程：删除 etcd 成员 -> 拷贝证书 -> kubeadm join 重新加入

### [[Docker-Kubernetes/k8s-installation-management/k8s两地三中心架构|k8s两地三中心架构]]
- 核心内容：详细介绍 K8s 两地三中心和异地多活架构方案，以及智能 DNS、多集群管理等核心技术。
- 关键知识点：
  - 两地三中心（主备模式）vs 异地多活（多中心同时承载流量）
  - 核心技术栈：智能 DNS/GTM、Karmada、Thanos/VictoriaMetrics、TiDB/CockroachDB
  - 单集群异地多活（不推荐）vs 多集群异地多活（推荐）
  - 阿里云 GTM 和腾讯云 IGTM 的智能 DNS 产品对比

### [[Docker-Kubernetes/k8s-installation-management/k8s生产环境优化与最佳实践|k8s生产环境优化与最佳实践]]
- 核心内容：K8s 生产环境的节点规划、高可用设计、性能优化和应用管理最佳实践。
- 关键知识点：
  - 节点规划：多节点小配置 vs 少节点大配置的权衡
  - 默认最低配置：master 8G/8vCPU，worker 12G/12vCPU
  - 3 master 可管理 900 个 worker 节点
  - 服务高可用（反亲和力）、性能优化（节点亲和力、污点容忍）

### [[Docker-Kubernetes/k8s-installation-management/k8s迁移容器运行时-版本升级|k8s迁移容器运行时与版本升级]]
- 核心内容：将容器运行时从 Docker 迁移到 containerd 的完整操作流程，以及 k8s 版本升级方法。
- 关键知识点：
  - 迁移步骤：cordon/drain 节点 -> 卸载 Docker -> 安装 containerd -> 修改 kubelet 配置
  - containerd 配置要点：sandbox_image、SystemdCgroup、镜像加速
  - 使用 crictl 工具替代 docker 命令

### [[Docker-Kubernetes/k8s-installation-management/k8s故障排查指南|k8s故障排查指南]]
- 核心内容：K8s 集群常见故障的排查方法，覆盖 Pod 状态异常、健康探测、Service 超时等场景。
- 关键知识点：
  - Pod 状态排查：Pending（资源/调度问题）、ImagePullBackOff（镜像问题）、CrashLoopBackOff（代码/权限问题）、Evicted（资源不足）
  - livenessProbe 需设置 initialDelaySeconds 避免启动阶段误杀
  - Pod 和 Service 连接超时的常见排查思路

### [[Docker-Kubernetes/k8s-installation-management/k8s多集群kubeconfig管理|k8s多集群kubeconfig管理]]
- 核心内容：在一台机器上管理多个 K8s 集群的 kubeconfig 配置方法。
- 关键知识点：
  - 方案一：kubectl config set-cluster/set-credentials/set-context 命令
  - 方案二：KUBECONFIG 环境变量指向多个文件
  - 方案三：kubectl config view --flatten 合并配置
  - 方案四：krew 插件 konfig 管理 kubeconfig

## 涉及的概念与实体
- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]
- [[KnowledgeBase/entities/etcd|etcd]]
- [[KnowledgeBase/entities/containerd|containerd]]
- [[KnowledgeBase/entities/kubeadm|kubeadm]]
- [[KnowledgeBase/entities/RockyLinux|Rocky Linux]]
- [[KnowledgeBase/entities/Calico|Calico]]
- [[KnowledgeBase/entities/keepalived|keepalived]]
- [[KnowledgeBase/entities/Karmada|Karmada]]
- [[KnowledgeBase/concepts/高可用集群|高可用集群]]
- [[KnowledgeBase/concepts/异地多活|异地多活]]
- [[KnowledgeBase/concepts/两地三中心|两地三中心]]
- [[KnowledgeBase/concepts/容器运行时|容器运行时]]
- [[KnowledgeBase/concepts/智能DNS|智能DNS/GTM]]
- [[KnowledgeBase/concepts/联邦集群|联邦集群]]

## 交叉主题发现
- **操作系统迁移趋势**：文档清晰记录了从 CentOS 7.9 到 Rocky Linux 8/9/10 的迁移路径，反映了 CentOS 停更后企业级 Linux 生态的变化。
- **容器运行时演进**：从早期版本使用 Docker 到 k8s 1.24+ 全面转向 containerd，多篇文档详细记录了迁移步骤和配置变化。
- **高可用架构递进**：从单 master 实验环境到 3 master 生产环境，再到两地三中心和异地多活，呈现出逐步升级的架构演进路线。
- **kubeadm 配置 API 演进**：从 v1beta2 到 v1beta3 再到 v1beta4，配置格式随 k8s 版本持续演进。
- **离线部署能力**：k8s 1.20.6 文档中包含了制作离线 yum 源的详细方法，这是企业内网部署的关键能力。
