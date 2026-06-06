---
title: K8s PodDisruptionBudget 实战
tags:
  - knowledgebase/source
  - docker-kubernetes/k8s
  - high-availability
date: 2026-06-06
sources:
  - "[[Docker-Kubernetes/k8s-basic-resources/k8s-PodDisruptionBudget实战]]"
aliases:
  - PDB实战摘要
---

# K8s PodDisruptionBudget 实战

## 元信息
- **原始文档**：[[Docker-Kubernetes/k8s-basic-resources/k8s-PodDisruptionBudget实战]]
- **领域**：Kubernetes / 高可用
- **摄入日期**：2026-06-06

## 摘要
系统讲解 PodDisruptionBudget（PDB）——K8s 自愿中断场景下的可用性保护机制。覆盖两种配置方式（minAvailable / maxUnavailable）、与 drain 和滚动更新的配合原理、三种生产配置模式（高可用服务/StatefulSet/批处理）、四大常见陷阱及验证方法。

## 关键知识点
1. **PDB 只对自愿中断生效**（drain/滚动更新/集群升级），不防护非自愿中断（节点宕机/OOMKill）
2. **两种配置二选一**：`minAvailable`（至少保持 N 个可用）或 `maxUnavailable`（最多允许 N 个不可用），均支持百分比（向下取整）
3. **PDB 与 Deployment 策略的关系**：两者同时存在时 PDB 约束更严格，每步操作必须同时满足两者
4. **四大陷阱**：① 单副本 + minAvailable:1 → drain 永久阻塞 ② minAvailable = replicas → 节点维护无法进行 ③ 空 selector 误保护所有 Pod ④ PDB 百分比 + HPA 最小副本数计算失误
5. **最稳健配置**（支付类核心服务）：Deployment `maxUnavailable: 0` + `maxSurge: 1` + PDB `minAvailable: replicas-1` + `readinessProbe` + `terminationGracePeriodSeconds`
6. **验证方法**：`kubectl get pdb`（看 ALLOWED DISRUPTIONS 列）、`kubectl get events --field-selector reason=DisruptionTarget`、eviction API 测试（PDB 阻止返回 429）

## 涉及的概念与实体
- [[KnowledgeBase/entities/Kubernetes]]
- [[KnowledgeBase/concepts/高可用架构]]

## 值得注意
- PDB 是知识库中 K8s 基础资源的补充——已有 Pod/Deployment/Service/RBAC/CRD 等，PDB 补齐了"中断保护"这一维度
- 与 HPA（扩缩容）存在交互关系，配置时需联动考虑
- 文章的四大陷阱是生产环境高频踩坑点，可作为 PDB 配置的检查清单
