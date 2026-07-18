---
title: Finalizer
tags:
  - knowledgebase/concept
  - kubernetes/lifecycle
date: 2026-07-18
sources:
  - "[[Docker-Kubernetes/k8s-basic-resources/k8s基础-Finalizer与资源删除]]"
  - "[[Docker-Kubernetes/k8s-basic-resources/k8s基础-namespace-资源分配]]"
  - "[[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD基础]]"
  - "[[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD Image Updater]]"
aliases:
  - Finalizers
  - 终结器
---

# Finalizer

## 定义

Finalizer 是 Kubernetes 资源对象 `metadata.finalizers` 字段中的字符串列表，本质是一个"删除前钩子"。只要该列表非空，apiserver 收到删除请求后不会立即从 etcd 移除对象，而是先设置 `deletionTimestamp` 使其进入 `Terminating` 状态，等待对应 Controller 执行清理逻辑并移除自己的 Finalizer，列表清空后对象才会被真正删除。

## 核心要点

- 存在意义：防止资源关联的外部资源（云盘、负载均衡器等）因 K8s 对象被删除而泄漏
- 删除流程：`kubectl delete` → 检查 `finalizers` 非空 → 设置 `deletionTimestamp` 进入 Terminating → Controller 观察到该时间戳并执行清理 → 清理完成后移除自身 Finalizer → 列表清空后对象才被真正从 etcd 删除
- 内置 Finalizer：`kubernetes.io/pvc-protection`（PVC 保护）、`kubernetes.io/pv-protection`（PV 保护）、`foregroundDeletion`（前台删除，等待依赖资源先删除）、`orphan`（孤儿删除，不自动删除依赖资源）
- 第三方 Operator/工具也广泛使用自定义 Finalizer，例如 ArgoCD 的 `resources-finalizer.argocd.argoproj.io`（确保删除 Application/AppProject 前先清理其管理的所有资源）、Cert-Manager 的 `cert-manager.io/finalizer`
- 资源"删不掉"的五大常见场景：① 对应 Controller 已被卸载、② Controller 清理逻辑报错（如外部 API 凭证过期）、③ Namespace 内某资源卡住导致整个 Namespace 卡在 Terminating、④ Finalizer 与 ownerReferences 形成循环依赖、⑤ Controller 因节点/网络问题无法与 apiserver 通信
- 手动移除 Finalizer（`kubectl patch --type=merge -p '{"metadata":{"finalizers":null}}'`）等同于跳过清理逻辑，可能导致外部资源泄漏，只应在确认 Controller 确实不存在或已手动清理外部资源后使用
- 开发 Operator 时的 Finalizer 实现原则：清理逻辑必须幂等、清理失败时不移除 Finalizer（返回 `RequeueAfter` 重试）、Finalizer 命名用 `域名/功能` 格式避免冲突、需处理部分清理进度
- 与 Pod 级别优雅终止机制的区分：Finalizer 作用于资源对象级别，在 apiserver 层拦截删除请求，比 `preStop` 钩子和 `terminationGracePeriodSeconds`（作用于 Pod 级别）更早触发、更难绕过

## 与其他概念的关系

- [[KnowledgeBase/concepts/CRD]]：删除 Namespace 会级联删除其下的自定义资源实例，若这些实例带有 Finalizer 且对应 Controller 异常，会导致 Namespace 卡在 Terminating
- [[KnowledgeBase/concepts/Operator模式]]：Finalizer 的清理逻辑通常由 Operator 的 Controller 在 Reconcile 循环中实现（`controllerutil.AddFinalizer`/`RemoveFinalizer`），是 Operator 模式管理资源全生命周期的关键环节
- [[KnowledgeBase/entities/Kubernetes]]：Finalizer 是 K8s 声明式删除模型的核心机制之一
- [[KnowledgeBase/entities/ArgoCD]]：ArgoCD 用 `resources-finalizer.argocd.argoproj.io` 确保删除 Application/AppProject 时级联清理其管理的所有下游资源

## 在本仓库中的覆盖

- [[Docker-Kubernetes/k8s-basic-resources/k8s基础-Finalizer与资源删除]]：Finalizer 的完整机制、内置/常见 Finalizer 清单、五大"删不掉"场景的诊断与修复、controller-runtime 中编写 Finalizer 的完整代码示例、与 Graceful Shutdown 机制的区分
- [[Docker-Kubernetes/k8s-basic-resources/k8s基础-namespace-资源分配]]：Namespace 因 `spec.finalizers` 未清空卡在 Terminating 的实战修复脚本（导出 JSON 清空 finalizers 后 PUT 到 `/finalize` 端点）
- [[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD基础]]、[[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD Image Updater]]：ArgoCD Application/AppProject 上配置 `resources-finalizer.argocd.argoproj.io` 的实际 YAML 用法

## 知识空白

- Finalizer 与 Admission Webhook 的交互（Webhook 是否会拦截带 Finalizer 资源的更新请求）
- 大规模集群中残留 Finalizer 资源的批量巡检与告警方案
- OwnerReference + 垃圾回收（Garbage Collection）与 Finalizer 协同工作的完整案例
