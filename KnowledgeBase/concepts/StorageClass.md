---
title: StorageClass
tags:
  - knowledgebase/concept
  - kubernetes/storage
date: 2026-05-04
sources:
  - "[[Docker-Kubernetes/k8s-basic-resources/k8s基础-storage]]"
  - "[[Docker-Kubernetes/k8s-storage/helm部署nfs-subdir-external-provisioner]]"
  - "[[Docker-Kubernetes/k8s-storage/k8s-ceph部署与集成]]"
aliases:
  - 存储类
  - SC
  - Kubernetes StorageClass
---

# StorageClass

## 定义

StorageClass 是 Kubernetes 提供的动态创建 PersistentVolume（PV）的模板机制。集群管理员通过创建 StorageClass 定义存储的属性（如大小、类型）和所使用的 CSI 存储插件（如 NFS、Ceph），当用户创建 PVC 时，Kubernetes 根据 PVC 中指定的 StorageClass 自动调用对应的存储插件创建 PV，从而免去手动创建和管理大量 PV 的运维负担。

## 核心要点

- **动态供应**：StorageClass 的核心价值是实现 PV 的动态供应。创建 PVC 时只需指定 `storageClassName`，Kubernetes 即自动创建匹配的 PV，无需管理员预先手动创建
- **Provisioner（供应商）**：每个 StorageClass 必须指定 `provisioner` 字段，声明使用哪种 CSI 存储插件。同一集群可同时存在多个 StorageClass 对接不同存储后端（如 `nfs.csi.k8s.io`、`rbd.csi.ceph.com`）
- **回收策略（reclaimPolicy）**：定义 PVC 删除后 PV 的处理方式。动态存储默认为 `Delete`（PV 随 PVC 一起删除），生产环境管理员手动维护的 PV 推荐 `Retain`（保留数据，需手动清理）
- **卷绑定模式（volumeBindingMode）**：`Immediate` 表示 PVC 创建后立即绑定 PV；`WaitForFirstConsumer` 表示等待 Pod 调度后再绑定，适用于 Local PV 等需要与 Pod 同节点的场景
- **默认存储类**：可通过 annotation `storageclass.kubernetes.io/is-default-class: "true"` 设置默认 StorageClass，PVC 未指定 `storageClassName` 时自动使用默认类
- **Parameters**：StorageClass 的 `parameters` 字段传递存储后端的配置参数，如 NFS 的 server 地址和共享路径、Ceph 的 pool 名称等

## 与其他概念的关系

- [[KnowledgeBase/concepts/PV-PVC|PV-PVC]]：StorageClass 是 PV 的动态创建模板，PVC 通过 `storageClassName` 引用 StorageClass 来触发自动创建 PV
- [[KnowledgeBase/concepts/分布式存储]]：StorageClass 的存储后端可以是 NFS、Ceph、CubeFS 等分布式存储系统
- [[KnowledgeBase/concepts/StatefulSet]]：StatefulSet 的 `volumeClaimTemplates` 结合 StorageClass 可为每个 Pod 副本自动创建独立的 PVC/PV
- [[KnowledgeBase/entities/NFS|NFS]]：通过 nfs-subdir-external-provisioner 或 CSI Driver 实现 NFS 的 StorageClass 动态供应
- [[KnowledgeBase/entities/Ceph|Ceph]]：通过 Ceph CSI 插件（RBD/CephFS）实现企业级分布式存储的 StorageClass 动态供应

## 在本仓库中的覆盖

- [[Docker-Kubernetes/k8s-basic-resources/k8s基础-storage]]：系统性介绍了 StorageClass 的概念、CSI 机制、NFS 存储类的两种实现方式（nfs-subdir 插件和 CSI Driver）、默认存储类设置，以及结合 StatefulSet volumeClaimTemplates 的使用
- [[Docker-Kubernetes/k8s-storage/helm部署nfs-subdir-external-provisioner]]：通过 Helm 部署 nfs-subdir-external-provisioner 实现 NFS StorageClass 动态供应的完整实战
- [[Docker-Kubernetes/k8s-storage/k8s-ceph部署与集成]]：Ceph 分布式存储的部署与 K8s 集成，涉及 RBD StorageClass 配置
- [[Docker-Kubernetes/k8s-db-middleware/k8s基于yaml部署mysql主从高可用]]：包含 NFS Provisioner 的完整搭建流程，通过 StorageClass 动态供给 PV

## 知识空白

- CSI 驱动开发与自定义 StorageClass 的高级配置尚未覆盖
- StorageClass 的存储容量跟踪（Storage Capacity Tracking）功能未涉及
- 多集群环境下 StorageClass 的统一管理策略未讨论
- 基于 StorageClass 的存储配额（ResourceQuota for StorageClass）未覆盖
