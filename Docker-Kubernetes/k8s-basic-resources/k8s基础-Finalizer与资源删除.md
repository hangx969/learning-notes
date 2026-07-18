---
title: K8s基础-Finalizer与资源删除
tags:
  - kubernetes
  - k8s-basics
aliases:
  - K8s Finalizer
  - Finalizer与资源删除
---

# Finalizer：让资源"删不掉"的隐形守护者

如果你在K8s运维生涯中从未遇到过 `kubectl delete` 卡住不动的情况，要么你用的集群太小，要么你的运气太好了。

几乎每个K8s运维人员都经历过这个场景：删除一个Namespace、一个PVC、一个Custom Resource，命令执行后光标闪烁了半天，资源依然存在， `Terminating` 状态像一块狗皮膏药粘在那里，怎么都撕不掉。

罪魁祸首通常是一个叫做 **Finalizer** 的机制。

## Finalizer是什么？为什么需要它？

在K8s中，删除一个资源通常是瞬间完成的——apiserver收到DELETE请求，从etcd中移除对象，完事。但这有个问题：如果这个资源关联了外部资源，直接删除K8s对象会导致外部资源泄漏。

比如一个PVC绑定了云盘，如果你直接删除PVC对象，云盘不会被自动释放，你会在云厂商的账单上看到一笔不必要的开销。再比如一个Service创建了外部负载均衡器，直接删除Service对象，负载均衡器会残留在云上继续计费。

Finalizer就是为解决这个问题而生的。它本质上是一个"删除前钩子"——在资源被真正删除之前，K8s会先执行Finalizer中注册的清理逻辑，确保外部资源被正确释放。

## Finalizer的工作机制

Finalizer是资源对象 `metadata.finalizers` 字段中的一个字符串列表。当这个列表非空时，K8s不会从etcd中真正删除该对象。

整个删除流程如下：

```
1. 用户执行 kubectl delete pvc my-pvc
2. apiserver收到DELETE请求
3. 检查 metadata.finalizers 是否为空
   ├── 为空 → 直接从etcd删除对象，完成
   └── 非空 → 进入Terminating状态，不删除对象
4. 设置 deletionTimestamp（标记为正在删除）
5. 对应的Controller观察到deletionTimestamp
6. Controller执行清理逻辑（释放云盘等）
7. Controller清理完成后，从finalizers列表中移除自己的Finalizer
8. 当finalizers列表变为空 → apiserver从etcd中删除对象
```

用一段YAML来看更直观：

```
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
  finalizers:
  - kubernetes.io/pvc-protection    # PVC保护Finalizer
  deletionTimestamp: "2026-07-12T10:00:00Z"
  deletionGracePeriodSeconds: 0
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
  storageClassName: ceph-block
```

这个PVC有一个 `kubernetes.io/pvc-protection` 的Finalizer。只要这个Finalizer存在，PVC就不会被真正删除。只有当PVC不再被任何Pod使用时，PVC Controller才会移除这个Finalizer，PVC才会被删除。

## 常见的Finalizer

K8s内置了一些常用的Finalizer：

| Finalizer | 作用 | 添加者 |
| --- | --- | --- |
| `kubernetes.io/pvc-protection` | 防止PVC在Pod使用中被删除 | PVC Controller |
| `kubernetes.io/pv-protection` | 防止PV在PVC绑定中被删除 | PV Controller |
| `kubernetes.io/service-protection` | 确保Service的负载均衡器被正确清理 | Service Controller |
| `foregroundDeletion` | 前台删除模式，等待所有依赖资源先删除 | apiserver |
| `orphan` | 孤儿删除模式，不自动删除依赖资源 | apiserver |

第三方Operator也会添加自己的Finalizer，比如：

```
# Cert-Manager的Certificate
metadata:
  finalizers:
  - cert-manager.io/finalizer

# ArgoCD的Application
metadata:
  finalizers:
  - resources-finalizer.argocd.argoproj.io

# 自定义Operator
metadata:
  finalizers:
  - my-operator.example.com/cleanup
```

## 资源"删不掉"的五大场景

### 场景一：Controller已不存在

这是最常见的情况。某个Operator创建了一堆Custom Resource，每个都带着它的Finalizer。后来Operator被卸载了，但Custom Resource还在。现在你删除这些CR，它们的Finalizer永远不会被移除，因为负责移除Finalizer的Controller已经不在了。

```
# 删除CR卡住
kubectl delete mysqlcluster my-db
# 等待...等待...一直等待...

# 查看状态
kubectl get mysqlcluster my-db -o yaml | grep finalizers
# finalizers:
# - mysql.operator.example.com/finalizer
```

### 场景二：Controller清理逻辑报错

Controller存在，但清理逻辑执行失败。比如一个Operator的Finalizer逻辑需要调用外部API删除一个云资源，但API凭证过期了，清理逻辑一直报错，Finalizer一直无法被移除。

```
# 查看Controller日志
kubectl logs -n operator-system deploy/mysql-operator

# 常见报错
ERROR: failed to delete cloud resource: Unauthorized
ERROR: Reconciler error: failed to cleanup: timeout calling API
```

### 场景三：Namespace卡在Terminating

删除Namespace时，Namespace内的所有资源都需要先被删除。如果其中任何一个资源因为Finalizer卡住，整个Namespace都会卡在Terminating状态。

```
kubectl get namespace old-project
NAME          STATUS        AGE
old-project   Terminating   120d

# 检查Namespace内残留资源
kubectl api-resources --verbs=list --namespaced -o name | \
  xargs -n 1 kubectl get -n old-project --ignore-not-found
```

### 场景四：finalizers和ownerReferences冲突

一个资源有Finalizer，同时它又是另一个资源的Owner。当你删除父资源时，子资源因为Finalizer无法删除，父资源因为子资源未删除也无法删除，形成循环依赖。

### 场景五：APIServer无法到达Controller

Controller运行在Pod中，如果Pod所在节点Not Ready，或者网络策略阻断了Controller与apiserver的通信，Controller无法处理Finalizer逻辑。

## 诊断与解决

### 诊断步骤

```
# 第一步：查看资源的Finalizer
kubectl get <resource> <name> -o jsonpath='{.metadata.finalizers}'
echo

# 第二步：查看deletionTimestamp
kubectl get <resource> <name> -o jsonpath='{.metadata.deletionTimestamp}'
echo

# 第三步：查看关联的Controller是否在运行
kubectl get pods -n <controller-namespace> -l app=<controller-name>

# 第四步：查看Controller日志中的错误
kubectl logs -n <controller-namespace> deploy/<controller-name> | \
  grep -i "finalizer\|cleanup\|error"

# 第五步：检查Controller是否注册了该资源的watch
kubectl get <resource> <name> -o yaml | grep -A5 finalizers
```

### 安全移除Finalizer

如果确认Controller已不存在或清理逻辑无法修复，可以手动移除Finalizer：

```
# 方法一：kubectl patch
kubectl patch <resource> <name> --type=merge -p '{"metadata":{"finalizers":null}}'

# 方法二：kubectl edit
kubectl edit <resource> <name>
# 手动删除 finalizers 列表中的所有条目

# 方法三：JSON Patch（精确移除特定Finalizer）
kubectl patch <resource> <name> --type=json \
  -p='[{"op":"remove","path":"/metadata/finalizers/0"}]'
```

**注意：手动移除Finalizer意味着跳过了清理逻辑，可能导致外部资源泄漏。** 只有在确认外部资源已手动清理完毕，或Controller确实不存在时，才应该这样做。

### 批量清理卡住的资源

```
#!/bin/bash
# 批量清理某个Namespace中所有卡在Terminating的资源

NAMESPACE="old-project"

# 获取所有带Finalizer的Terminating资源
kubectl api-resources --verbs=list --namespaced -o name | while read resource; do
  kubectl get "$resource" -n "$NAMESPACE" -o json | \
    jq -r '.items[] | select(.metadata.deletionTimestamp != null) | "\(.kind)/\(.metadata.name)"' | \
    while read item; do
      echo "Removing finalizers from $item..."
      kubectl patch "$item" -n "$NAMESPACE" --type=merge \
        -p '{"metadata":{"finalizers":null}}'
    done
done
```

### Namespace卡在Terminating的终极修复

```
# 方法一：导出Namespace的JSON，移除finalizers和spec，重新PUT
kubectl get namespace <name> -o json | \
  jq 'del(.spec.finalizers, .metadata.finalizers)' | \
  kubectl replace --raw "/api/v1/namespaces/<name>/finalize" -f -

# 方法二：使用krew插件
kubectl krew install ns-remove-finalizer
kubectl ns-remove-finalizer <namespace>
```

## 编写自己的Finalizer

如果你在开发Operator，正确实现Finalizer是非常重要的。以下是一个使用controller-runtime的完整示例：

```
package controllers

import (
    "context"
    "fmt"

    ctrl "sigs.k8s.io/controller-runtime"
    "sigs.k8s.io/controller-runtime/pkg/client"
    "sigs.k8s.io/controller-runtime/pkg/controller/controllerutil"
    apierrors "k8s.io/apimachinery/pkg/api/errors"

    examplev1 "example.com/api/v1"
)

const myFinalizerName = "my-operator.example.com/finalizer"

func (r *MyResourceReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    var resource examplev1.MyResource
    if err := r.Get(ctx, req.NamespacedName, &resource); err != nil {
        if apierrors.IsNotFound(err) {
            return ctrl.Result{}, nil
        }
        return ctrl.Result{}, err
    }

    // 检查是否正在删除
    if !resource.DeletionTimestamp.IsZero() {
        // 资源正在被删除，执行清理逻辑
        return r.reconcileDelete(ctx, &resource)
    }

    // 资源正常存在，确保Finalizer已添加
    if !controllerutil.ContainsFinalizer(&resource, myFinalizerName) {
        controllerutil.AddFinalizer(&resource, myFinalizerName)
        if err := r.Update(ctx, &resource); err != nil {
            return ctrl.Result{}, err
        }
    }

    // 正常调谐逻辑...
    return ctrl.Result{}, nil
}

func (r *MyResourceReconciler) reconcileDelete(ctx context.Context, resource *examplev1.MyResource) (ctrl.Result, error) {
    // 1. 执行外部资源清理
    if err := r.cleanupExternalResources(ctx, resource); err != nil {
        // 清理失败，不移除Finalizer，等待下次调谐重试
        r.Log.Error(err, "failed to cleanup external resources")
        return ctrl.Result{RequeueAfter: 30}, nil  // 30秒后重试
    }

    // 2. 清理成功，移除Finalizer
    controllerutil.RemoveFinalizer(resource, myFinalizerName)
    if err := r.Update(ctx, resource); err != nil {
        return ctrl.Result{}, err
    }

    r.Log.Info("resource cleaned up successfully", "name", resource.Name)
    return ctrl.Result{}, nil
}

func (r *MyResourceReconciler) cleanupExternalResources(ctx context.Context, resource *examplev1.MyResource) error {
    // 清理外部资源，例如删除云盘、释放负载均衡器等
    // 必须是幂等的！因为可能被多次调用
    
    // 示例：删除外部数据库
    err := r.dbClient.DeleteDatabase(resource.Spec.DatabaseName)
    if err != nil && !isNotFound(err) {
        return fmt.Errorf("delete database: %w", err)
    }
    
    return nil
}
```

编写Finalizer时的关键原则：

**第一，清理逻辑必须幂等。** Controller可能在清理失败后多次重试，清理逻辑必须能安全地执行多次。

**第二，清理失败时不要移除Finalizer。** 只有在确认所有外部资源都已清理完毕后，才移除Finalizer。失败时返回 `RequeueAfter` ，让Controller稍后重试。

**第三，给Finalizer起一个唯一的名字。** 使用 `域名/功能` 的格式，避免与其他Operator的Finalizer冲突。

**第四，处理部分清理的情况。** 如果有多个外部资源需要清理，记录清理进度，下次重试时跳过已清理的资源。

## Finalizer与Graceful Shutdown的关系

Finalizer和 `preStop` 钩子、 `terminationGracePeriodSeconds` 经常被混淆，它们的作用层次不同：

```
| 机制                          | 作用层级         | 触发时机              |
|-------------------------------|-----------------|----------------------|
| preStop hook                  | Pod级别         | Pod被删除时           |
| terminationGracePeriodSeconds | Pod级别         | Pod删除超时强制杀死    |
| Finalizer                     | 资源对象级别      | 资源对象被删除时       |
| OwnerReference + Garbage Collection | 资源关系级别 | 父资源删除级联子资源    |
```

Finalizer是在apiserver层面拦截删除请求，它比Pod级别的优雅终止更早触发，也更难绕过。

## 总结

Finalizer是K8s资源管理中一个容易被忽视但极其重要的机制。它的存在确保了外部资源不会因为K8s对象的删除而泄漏，但同时也可能成为资源"删不掉"的元凶。

理解Finalizer的工作机制，掌握诊断和修复方法，是每个K8s运维人员和Operator开发者的必备技能。记住三个核心要点：

1. 1\. **Finalizer列表非空时，资源不会被真正删除**
2. 2\. **手动移除Finalizer等同于跳过清理逻辑，需谨慎**
3. 3\. **开发Operator时必须正确实现Finalizer，且清理逻辑必须幂等**

下次遇到资源卡在Terminating，不要慌——先看Finalizer，再看Controller，问题通常就在那里。
