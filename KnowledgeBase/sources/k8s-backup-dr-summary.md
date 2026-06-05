---
title: K8s 备份与灾备实战
tags:
  - knowledgebase/source
  - docker-kubernetes/backup
  - disaster-recovery
date: 2026-06-05
sources:
  - "[[Docker-Kubernetes/k8s-backup-dr/k8s备份与灾备实战-三层容灾架构]]"
aliases:
  - K8s灾备摘要
---

# K8s 备份与灾备实战

## 元信息
- **原始文档**：[[Docker-Kubernetes/k8s-backup-dr/k8s备份与灾备实战-三层容灾架构]]
- **领域**：Kubernetes / 备份与灾备
- **摄入日期**：2026-06-05

## 摘要
以一个 etcd 数据被 rm -rf 的 P0 事故为引子，系统讲解 K8s 三层容灾架构（L1 etcd 快照 / L2 Velero 应用备份 / L3 应用数据备份）。覆盖 etcd 手动/自动化备份恢复全流程、Velero 安装配置与操作命令、6 大生产环境避坑指南、RTO/RPO 目标设定和 Prometheus 备份告警规则。

## 关键知识点
1. **三层备份模型**：L1 etcd 快照（保命，全集群，分钟级恢复）→ L2 Velero（后悔药，Namespace 粒度）→ L3 应用数据（终极保险，数据库原生工具）
2. **etcd 快照边界**：包含所有 K8s 资源定义/CRD/RBAC/Secret（含明文敏感信息）；不包含容器文件系统/PV 业务数据/Node 磁盘数据
3. **etcd 自动化备份**：CronJob + hostNetwork + nodeSelector(master) + 证书挂载 + S3 上传 + 7 天清理，每 6 小时执行
4. **etcd 恢复四步**：停 apiserver → etcdctl snapshot restore → 替换数据目录 → 启动 etcd 再启 apiserver
5. **Velero 核心操作**：`velero backup create --include-namespaces`（按 NS）/ `--selector`（按 Label）/ `velero restore create --namespace-mappings`（恢复到新 NS）/ `velero schedule create`（定时备份）
6. **六大生产避坑**：① 不做恢复验证=没有备份 ② etcd 与 Velero 时间差需记录 revision ③ etcd 快照含 Secret 明文须加密 ④ etcd 磁盘空间须启用 auto-compaction ⑤ 跨版本快照仅向前兼容 ⑥ Velero 不含 Node 状态/运行时状态/外部依赖/Webhook 配置
7. **三条铁律**：每月恢复演练、三层缺一不可、加密+异地存储

## 涉及的概念与实体
- [[KnowledgeBase/entities/Kubernetes]]
- [[KnowledgeBase/concepts/高可用架构]]

## 值得注意
- 文章提供了**完整可部署的 YAML**（etcd 备份 CronJob、恢复验证 CronJob、Prometheus 告警规则），可直接应用于生产环境
- 与知识库中已有的 [[Docker-Kubernetes/k8s-backup-dr/k8s集群备份恢复-Velero]] 形成互补——已有文章侧重 Velero 工具使用，本文提供**架构层面的三层容灾体系**和 etcd 快照实战
- RTO/RPO 目标设定对 SLA 承诺有直接参考价值
