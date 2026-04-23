---
title: Client-Go K8s客户端开发
tags:
  - go
  - kubernetes
  - client-go
  - cloud-native
aliases:
  - client-go
  - K8s客户端开发
---

# Client-Go — K8s 客户端开发

> 来源：[初始K8S客户端工具Client-Go](https://mp.weixin.qq.com/s/2OwhjnvJHL2YOAcP3IzQEA)

client-go 是 Kubernetes 官方提供的 Go 语言客户端库，封装了与 API Server 通信的细节，用于编程方式操作 K8s 资源。

- 官方仓库：https://github.com/kubernetes/client-go

## 用途

| 场景 | 说明 |
|------|------|
| Operator / Controller 开发 | 编写自定义控制器管理 CRD |
| 自动化运维工具 | 批量创建/删除/更新资源，集群巡检、资源清理、权限审计 |
| CI/CD 集成 | 替代 kubectl 命令行，实现可编程的部署控制 |
| CLI 工具 / Web 控制台 | Helm、K9s、Lens 底层都依赖 client-go |
| 理解 K8s 内核 | 包含 Informer、Lister、WorkQueue、Reflector 等核心组件 |

## 核心功能

- **资源操作**：对 Pod、Service、Deployment 等资源的 CRUD
- **资源监听**：注册回调处理资源的添加、更新、删除事件，实现实时监听
- **认证授权**：支持令牌认证、证书认证等多种方式
- **错误处理和重试**：内置乐观锁冲突重试机制（`retry.RetryOnConflict`）
- **扩展性**：提供拦截器、插件接口用于定制化

## 安装

```bash
# 安装最新版本
go get k8s.io/client-go@latest

# 安装指定版本
go get k8s.io/client-go@v0.20.4
```

> [!tip] 版本对应
> client-go 版本与 K8s 版本对应，参考官方 README 的兼容性矩阵。

## 初始化客户端

集群外部使用时，需要 kubeconfig 文件（通常在 `~/.kube/config`）：

```go
var kubeconfig *string
if home := homedir.HomeDir(); home != "" {
    kubeconfig = flag.String("kubeconfig", filepath.Join(home, ".kube", "config"), "(optional) absolute path to the kubeconfig file")
} else {
    kubeconfig = flag.String("kubeconfig", "", "absolute path to the kubeconfig file")
}
flag.Parse()

config, err := clientcmd.BuildConfigFromFlags("", *kubeconfig)
if err != nil {
    panic(err)
}
clientset, err := kubernetes.NewForConfig(config)
if err != nil {
    panic(err)
}
```

集群内部（Pod 中运行）使用 InClusterConfig 自动获取 ServiceAccount 凭证：

```go
config, err := rest.InClusterConfig()
```

## CRUD 操作示例

### Create — 创建 Deployment

```go
deploymentsClient := clientset.AppsV1().Deployments(apiv1.NamespaceDefault)

deployment := &appsv1.Deployment{
    ObjectMeta: metav1.ObjectMeta{
        Name: "demo-deployment",
    },
    Spec: appsv1.DeploymentSpec{
        Replicas: ptr.To[int32](2),
        Selector: &metav1.LabelSelector{
            MatchLabels: map[string]string{"app": "demo"},
        },
        Template: apiv1.PodTemplateSpec{
            ObjectMeta: metav1.ObjectMeta{
                Labels: map[string]string{"app": "demo"},
            },
            Spec: apiv1.PodSpec{
                Containers: []apiv1.Container{
                    {
                        Name:            "web",
                        Image:           "nginx:1.12",
                        ImagePullPolicy: "IfNotPresent",
                        Ports: []apiv1.ContainerPort{
                            {Name: "http", Protocol: apiv1.ProtocolTCP, ContainerPort: 80},
                        },
                    },
                },
            },
        },
    },
}

result, err := deploymentsClient.Create(context.TODO(), deployment, metav1.CreateOptions{})
fmt.Printf("Created deployment %q.\n", result.GetObjectMeta().GetName())
```

### Update — 冲突重试更新

Kubernetes 使用**乐观锁机制**：每个资源都有 `metadata.resourceVersion`，Update 时 API Server 检查版本是否一致，不一致则返回 409 Conflict。

```go
retryErr := retry.RetryOnConflict(retry.DefaultRetry, func() error {
    // 获取最新版本
    result, getErr := deploymentsClient.Get(context.TODO(), "demo-deployment", metav1.GetOptions{})
    if getErr != nil {
        panic(fmt.Errorf("Failed to get latest version of Deployment: %v", getErr))
    }

    result.Spec.Replicas = ptr.To[int32](1)                        // 缩容到 1 个副本
    result.Spec.Template.Spec.Containers[0].Image = "nginx:latest" // 更新镜像
    _, updateErr := deploymentsClient.Update(context.TODO(), result, metav1.UpdateOptions{})
    return updateErr
})
```

> [!important] RetryOnConflict
> `retry.RetryOnConflict` 使用指数回退重试，避免并发更新冲突。每次重试前重新 Get 最新版本，确保 resourceVersion 一致。

### List — 列出资源

```go
list, err := deploymentsClient.List(context.TODO(), metav1.ListOptions{})
for _, d := range list.Items {
    fmt.Printf(" * %s (%d replicas)\n", d.Name, *d.Spec.Replicas)
    for _, c := range d.Spec.Template.Spec.Containers {
        fmt.Printf("   - %s (%s)\n", c.Name, c.Image)
    }
}
```

### Delete — 删除策略

```go
deletePolicy := metav1.DeletePropagationForeground
err := deploymentsClient.Delete(context.TODO(), "demo-deployment", metav1.DeleteOptions{
    PropagationPolicy: &deletePolicy,
})
```

三种 DeletionPropagation 策略：

| 策略 | 行为 | 特点 |
|------|------|------|
| `Foreground` | 先删子资源，再删父资源 | 安全有序，删除会阻塞直到子资源清理完 |
| `Background` | 先删父资源，后台异步删子资源 | 快速返回，子资源稍后清理 |
| `Orphan` | 只删父资源，子资源变为孤儿 | 子资源继续运行，常用于迁移或调试 |

## 实战：Client-Go + Gin Web 控制台

将 client-go 与 Gin 框架结合，通过 HTTP API 和 Web 页面操作 K8s 集群。

### 初始化（支持集群内外）

```go
var clientset *kubernetes.Clientset

func init() {
    var config *rest.Config
    var err error

    // 尝试 in-cluster config（Pod 内运行）
    config, err = rest.InClusterConfig()
    if err != nil {
        // 回退到 kubeconfig（本地开发）
        kubeconfig := filepath.Join(homedir.HomeDir(), ".kube", "config")
        if _, err := os.Stat(kubeconfig); err == nil {
            config, err = clientcmd.BuildConfigFromFlags("", kubeconfig)
        } else {
            panic("failed to load kubeconfig")
        }
    }

    clientset, err = kubernetes.NewForConfig(config)
    if err != nil {
        panic(err)
    }
}
```

### Create 接口

```go
type DeployRequest struct {
    Name      string `json:"name" binding:"required"`
    Namespace string `json:"namespace" binding:"required"`
    Replicas  int32  `json:"replicas"`
    Image     string `json:"image" binding:"required"`
}

func createDeployment(c *gin.Context) {
    var req DeployRequest
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }
    if req.Replicas <= 0 {
        req.Replicas = 1
    }

    deployment := &appsv1.Deployment{
        ObjectMeta: metav1.ObjectMeta{Name: req.Name, Namespace: req.Namespace},
        Spec: appsv1.DeploymentSpec{
            Replicas: &req.Replicas,
            Selector: &metav1.LabelSelector{
                MatchLabels: map[string]string{"app": req.Name},
            },
            Template: apiv1.PodTemplateSpec{
                ObjectMeta: metav1.ObjectMeta{Labels: map[string]string{"app": req.Name}},
                Spec: apiv1.PodSpec{
                    Containers: []apiv1.Container{
                        {Name: "app", Image: req.Image, ImagePullPolicy: "IfNotPresent",
                         Ports: []apiv1.ContainerPort{{ContainerPort: 80}}},
                    },
                },
            },
        },
    }

    result, err := clientset.AppsV1().Deployments(req.Namespace).Create(
        context.TODO(), deployment, metav1.CreateOptions{})
    if err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
        return
    }
    c.JSON(http.StatusCreated, gin.H{"message": "Deployment created", "name": result.Name, "ns": result.Namespace})
}
```

### 路由注册 + 模板渲染

```go
func main() {
    r := gin.Default()

    // 模板渲染：加载前端页面
    r.LoadHTMLGlob("./index.html")
    r.GET("/", func(c *gin.Context) {
        c.HTML(http.StatusOK, "index.html", gin.H{"主题": "Deployments"})
    })

    // API 接口
    r.POST("/deploy", createDeployment)

    if err := r.Run(":9000"); err != nil {
        panic(err)
    }
}
```

调用示例：

```bash
curl -X POST http://localhost:9000/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-web",
    "namespace": "default",
    "replicas": 2,
    "image": "nginx:latest"
  }'
# 返回: {"message":"Deployment created","name":"my-web","ns":"default"}
```

> [!tip] 扩展方向
> 基于此框架可以扩展 Update/Delete/List 接口，构建完整的 K8s Web 管理控制台。Gin 的模板渲染（`html/template`）支持动态 HTML 页面，结合前端表单实现可视化操作。
