---
title: "从零开发 Kubernetes Operator：Kubebuilder 实战教程"
source: "https://mp.weixin.qq.com/s/Ts9MxQOpQVaUtw6YbHXogw"
created: 2026-06-28
tags:
  - kubernetes
  - operator
  - kubebuilder
  - crd
  - go
---

# 从零开发 Kubernetes Operator

## 什么是 Operator？

Operator 的主要目标是将工程师的逻辑转换为代码，以便实现原生 Kubernetes 无法完成的某些任务的自动化。

例如，Operator 可以在 Kubernetes 中部署和维护 MySQL、Elasticsearch 或 GitLab Runner 等工具，自动配置这些工具，根据事件调整系统状态，并对故障做出反应。

Operator 由两个组件组成：

- **CRD（Custom Resource Definition）**：Kubernetes 自定义类型的资源蓝图，用于描述其规范（Spec）和状态（Status）。CRD 的实例称为自定义资源（CR）
- **Controller（控制器）**：持续监视集群状态，并根据事件做出变更，目标是将资源的当前状态变为用户在 CR Spec 中定义的期望状态

控制器的类比：恒温器。设置温度 = 期望状态，房间实际温度 = 当前状态，恒温器通过打开或关闭空调使实际状态接近期望状态。

**Manager（管理器）** 负责启动所有控制器，并使控制循环共存。假设项目中有两个 CRD 和两个控制器，管理器将启动这两个控制器并使它们共存。

## 构建 Operator

可以使用 controller-runtime 从头构建，也可以使用框架加速开发：**Kubebuilder** 或 **OperatorSDK**（两个项目目前正在合并）。本文选择 Kubebuilder。

### 开发环境准备

```bash
# 必备工具
# Go v1.17.9+
# Docker 17.03+
# kubectl v1.11.3+
# K8s v1.11.3+ 集群（建议用 kind 设置本地集群）

# 安装 kubebuilder
curl -L -o kubebuilder https://go.kubebuilder.io/dl/latest/$(go env GOOS)/$(go env GOARCH) \
  && chmod +x kubebuilder \
  && mv kubebuilder /usr/local/bin/

# 验证
kubebuilder version
```

### 初始化项目

```bash
# 初始化新项目（下载 controller-runtime 二进制文件并准备项目）
kubebuilder init --domain my.domain --repo my.domain/tutorial

# 创建新的 API（CRD）和 Controller
kubebuilder create api --group tutorial --version v1 --kind Foo
# 提示创建 CRD 和 Controller 时均按 yes
```

生成的项目结构（Go 项目）：

```
├── main.go          # 项目入口，设置并运行管理器
├── config/          # K8s 部署 Operator 的 manifest
├── Dockerfile       # 构建管理器镜像的容器文件
├── api/v1/          # Foo CRD 定义
└── controllers/     # Foo 控制器
```

### 自定义 CRD

Foo CRD 的定义中有 `name` 字段（Foo 正在寻找的朋友的名称）。如果 Foo 找到了一个朋友（一个和朋友同名的 Pod），`happy` 状态将被设置为 true。

```go
// api/v1/foo_types.go
package v1

import (
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

// FooSpec defines the desired state of Foo
type FooSpec struct {
    // Name of the friend Foo is looking for
    Name string `json:"name"`
}

// FooStatus defines the observed state of Foo
type FooStatus struct {
    // Happy will be set to true if Foo found a friend
    Happy bool `json:"happy,omitempty"`
}

//+kubebuilder:object:root=true
//+kubebuilder:subresource:status

// Foo is the Schema for the foos API
type Foo struct {
    metav1.TypeMeta   `json:",inline"`
    metav1.ObjectMeta `json:"metadata,omitempty"`

    Spec   FooSpec   `json:"spec,omitempty"`
    Status FooStatus `json:"status,omitempty"`
}
```

### 实现 Controller

控制器逻辑：通过 Reconcile 请求获取 Foo 资源 → 获取 Foo 朋友的名称 → 列出所有同名的 Pod → 如果找到则设置 `happy=true`，否则设为 `false`。

控制器也会对 Pod 事件做出反应——如果创建了一个新 Pod，Foo 资源能够相应更新其状态。

```go
// controllers/foo_controller.go
package controllers

import (
    "context"

    corev1 "k8s.io/api/core/v1"
    "k8s.io/apimachinery/pkg/runtime"
    "k8s.io/apimachinery/pkg/types"
    ctrl "sigs.k8s.io/controller-runtime"
    "sigs.k8s.io/controller-runtime/pkg/client"
    "sigs.k8s.io/controller-runtime/pkg/handler"
    "sigs.k8s.io/controller-runtime/pkg/log"
    "sigs.k8s.io/controller-runtime/pkg/reconcile"
    "sigs.k8s.io/controller-runtime/pkg/source"

    tutorialv1 "my.domain/tutorial/api/v1"
)

type FooReconciler struct {
    client.Client
    Scheme *runtime.Scheme
}

// RBAC 权限标记
//+kubebuilder:rbac:groups=tutorial.my.domain,resources=foos,verbs=get;list;watch;create;update;patch;delete
//+kubebuilder:rbac:groups=tutorial.my.domain,resources=foos/status,verbs=get;update;patch
//+kubebuilder:rbac:groups="",resources=pods,verbs=get;list;watch

func (r *FooReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    log := log.FromContext(ctx)
    log.Info("reconciling foo custom resource")

    // 1. 获取触发 reconciliation 的 Foo 资源
    var foo tutorialv1.Foo
    if err := r.Get(ctx, req.NamespacedName, &foo); err != nil {
        log.Error(err, "unable to fetch Foo")
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }

    // 2. 列出所有 Pod，查找与 Foo 朋友同名的 Pod
    var podList corev1.PodList
    var friendFound bool
    if err := r.List(ctx, &podList); err != nil {
        log.Error(err, "unable to list pods")
    } else {
        for _, item := range podList.Items {
            if item.GetName() == foo.Spec.Name {
                log.Info("pod linked to a foo custom resource found", "name", item.GetName())
                friendFound = true
            }
        }
    }

    // 3. 更新 Foo 的 happy 状态
    foo.Status.Happy = friendFound
    if err := r.Status().Update(ctx, &foo); err != nil {
        log.Error(err, "unable to update foo's happy status")
        return ctrl.Result{}, err
    }

    log.Info("foo custom resource reconciled")
    return ctrl.Result{}, nil
}

// 设置 Controller：监听 Foo 资源 + 监听 Pod 事件
func (r *FooReconciler) SetupWithManager(mgr ctrl.Manager) error {
    return ctrl.NewControllerManagedBy(mgr).
        For(&tutorialv1.Foo{}).
        Watches(
            &source.Kind{Type: &corev1.Pod{}},
            handler.EnqueueRequestsFromMapFunc(r.mapPodsReqToFooReq),
        ).
        Complete(r)
}

// Pod 事件映射：只有当 Pod 名称是某个 Foo 的"朋友"时，才触发该 Foo 的 reconciliation
func (r *FooReconciler) mapPodsReqToFooReq(obj client.Object) []reconcile.Request {
    ctx := context.Background()
    log := log.FromContext(ctx)

    req := []reconcile.Request{}
    var list tutorialv1.FooList
    if err := r.Client.List(context.TODO(), &list); err != nil {
        log.Error(err, "unable to list foo custom resources")
    } else {
        for _, item := range list.Items {
            if item.Spec.Name == obj.GetName() {
                req = append(req, reconcile.Request{
                    NamespacedName: types.NamespacedName{Name: item.Name, Namespace: item.Namespace},
                })
                log.Info("pod linked to a foo custom resource issued an event", "name", obj.GetName())
            }
        }
    }
    return req
}
```

### 运行与测试

```bash
# 1. 更新 manifest
make manifests

# 2. 安装 CRD 到集群
make install
kubectl get crds
# foos.tutorial.my.domain

# 3. 运行控制器（也可部署为集群中的 Deployment）
make run
```

**测试流程**：

```yaml
# 创建两个 Foo 自定义资源
apiVersion: tutorial.my.domain/v1
kind: Foo
metadata:
  name: foo-01
spec:
  name: jack    # 寻找名为 jack 的 Pod
---
apiVersion: tutorial.my.domain/v1
kind: Foo
metadata:
  name: foo-02
spec:
  name: joe     # 寻找名为 joe 的 Pod
```

```bash
kubectl apply -f config/samples
# 此时两个 Foo 的 happy 状态都为 false（没有同名 Pod）

# 部署一个名为 jack 的 Pod
kubectl apply -f jack-pod.yaml
# 控制器检测到 Pod 创建事件 → 触发 foo-01 的 reconciliation → happy 变为 true
# foo-02 不受影响（它的朋友是 joe）

# 修改 foo-02 的 spec.name 为 jack
# 控制器触发 reconciliation → foo-02 的 happy 也变为 true

# 删除 jack Pod → 两个 Foo 的 happy 都回到 false
```

## 进阶方向

- 优化事件过滤（避免事件重复提交）
- 完善 RBAC 权限
- 改进日志记录系统
- 当 Operator 更新资源时触发 Kubernetes 事件
- 获取 Foo 自定义资源时添加自定义字段（如显示 happy 状态）
- 编写单元测试和端到端测试

## Operator 开发工具对比

| 工具 | 定位 | 语言 | 说明 |
|------|------|------|------|
| **Kubebuilder** | 官方推荐框架 | Go | 文档清晰、久经考验，与 OperatorSDK 正在合并 |
| **OperatorSDK** | Red Hat 主导 | Go/Ansible/Helm | 支持多种方式构建 Operator |
| **controller-runtime** | 底层库 | Go | Kubebuilder/OperatorSDK 的底层依赖，可从头构建 |
| **Metacontroller** | 轻量级 | 任意语言 | 通过 Webhook 方式，用任意语言实现控制器逻辑 |

**GitHub 完整代码**：项目提供了完整的示例代码，可直接参考。
