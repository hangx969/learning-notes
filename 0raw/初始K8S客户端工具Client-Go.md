---
title: "初始K8S客户端工具Client-Go"
source: "https://mp.weixin.qq.com/s/2OwhjnvJHL2YOAcP3IzQEA"
author:
  - "[[王子恒]]"
published:
created: 2026-04-23
description:
tags:
  - "clippings"
---
王子恒 *2025年11月18日 14:12*

## 初始K8S客户端工具Client-Go

- 引言
- 一、Client-Go简介
- 安装client-go
	- 1.1、学习Client-Go的用途
	- 1.2、client-go的功能
- 二、Client-Go的基本使用
- 2.1、执行Create
	- 2.2、执行Update
	- 2.3、执行List
	- 2.4、执行Delete
- 三、Client-Go+Gin
- 3.1、Cretae 接口
	- 3.2、Gin框架的模板渲染

## 引言

- Kubernetes是一个开源的容器编排平台，它由许多组件组成，每个组件都扮演着不同的角色。client-go是Kubernetes官方提供的Go语言客户端库，用于与Kubernetes API进行交互。
- 同样而言，别的语言也有相对应的库，比如Python的库就名为kubernetes。
- 以下为官方提供的Kubernetes架构图。
![图片](https://mmbiz.qpic.cn/mmbiz_png/K6fzwF0Fr1zA7IU6emS0jVJOKgm9b0Emlumg1yTc032mLKpJUHIicbniaia2JnicMpwxzUmcJ9A9SnZ3iaHlA7Vic09Q/640?wx_fmt=png&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

## 一、Client-Go简介

- client-go是Kubernetes官方提供的Go语言客户端库，它为开发者提供了Kubernetes API进行交互的便捷方式。它封装了与Kubernetes API服务器通信的细节，使开发者能够轻松的创建、更新呢和删除Kubernetes资源对象。
- 官方地址：https://github.com/kubernetes/client-go

### 安装client-go

- 根据以下官方推荐去安装自己的client-go版本
![图片](https://mmbiz.qpic.cn/mmbiz_png/K6fzwF0Fr1zA7IU6emS0jVJOKgm9b0EmlibOaXFear0jFklrFYwibA5wK63EFw9wibg2NHD9GmbiaAmqHfBtlAHWxw/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=1)

```
# 安装最新版本
go get k8s.io/client-go@latest

# 安装执行版本
go get k8s.io/client-go@v0.20.4
```

### 1.1、学习Client-Go的用途

- 开发Kubernetes原生应用（Operators/Controllers）
- 使用Client-go可以编写自定义控制器（Controller）或者Operator，实现对自定义资源（CRD）的管理。
	- 比如：自动创建备份、监控特定资源状态并做出响应等。
- 自动化运维工具开发
- 编写脚本或者工具来批量创建/删除/更新Pod、Deployment、Service等资源。
	- 实现集群状态巡检、资源清理、权限审计等功能。
- 集成Kubernetes到现有系统
- 如果你的公司内部系统需要和Kubernetes集群联动（比如CI/CD平台部署服务），client-go提供了稳定可靠的API接口封装。
	- 可以替代kubectl命令行操作，实现更高效、可编程的控制逻辑。
- 深入理解Kubernetes结构和工作机制
- client-go中包含了informer、Lister、Workqueue、Reflector等核心组件，这些正是Kubernetes控制器模式的基础。
	- 学习它有助于理解Kubernetes如何监听资源变化、如何实现最终一致性等底层机制。
- 构建CLI工具或者Web控制台
- 很多Kubernetes生态工具（如Helm、K9s、Lens）底层都依赖client-go。
	- 你可以基于它开发自己的命令行工具或者可视化界面。
- 提高求职竞争力
- 在云原生岗位（SRE、平台工程师、DevOps工程师等）面试中，熟悉client-go和控制器模式是加分项，甚至是硬性要求。

### 1.2、client-go的功能

- 资源操作
- client-go提供了一组丰富的方法，用于对Kubernetes资源对象进行增删改查操作。开发者可以使用client-go创建、更新和删除Pod、Service、Deployment等资源对象，以及执行其他与资源相关的操作。
- 资源监听
- client-go支持对Kubernetes资源对象进行监听，以便在资源状态发生变化时及时获取通知。开发者可以注册回调函数，处理资源的添加、更新和删除事件，实现对基区努状态的实时监听和相应。
- 认证和授权
- clientg-go提供了与Kubernetes API服务器进行认证和授权的功能。它支持多种认证方式，如基于令牌的认证、基于证书的认证等。开发者可以使用client-go与安全的Kubernetes集群进行交互，确保数据传输的安全性和可信度。
- 错误处理和重试
- client-go具有强大的错误处理和重试机制，以应对网络故障和API调用失败。它提供了一系列的错误类型和重试策略，开发者可以根据需要进行配置，确保API调用的稳定性和可靠性。
- 扩展性和定制化
- client-go提供了丰富的口站点和接口，使开发者能够对其进行定制化和扩展。开发者可以编写自定义的拦截器、插件和扩展，以满足特定的业务需求，并于clinet-go无缝集成。

## 二、Client-Go的基本使用

- 如果是在集群外部使用client-go操作集群，需要拿到集群的config文件，并且放在自己windows的用户家目录下的.kube下（ `C:\Users\Administrator\.kube` ），因为linux的也是.kube，不过这不是必然的，其实放在什么地方都无所谓，只要代码能拿到这个文件按即可，获取直接调用api server也行。

### 2.1、执行Create

```
package main

import (
 "context"
 "flag"
 "fmt"
 "path/filepath"

 appsv1 "k8s.io/api/apps/v1"
 apiv1 "k8s.io/api/core/v1"
 metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
 "k8s.io/client-go/kubernetes"
 "k8s.io/client-go/tools/clientcmd"
 "k8s.io/client-go/util/homedir"
 "k8s.io/utils/ptr"
)

func main() {
 // 拿到 config 配置
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

 /*
  定义一个 deployment 操作客户端对象
  deployment 资源是在 apps/v1 这个 api下的所以需要 .AppsV1.Deployments
  apiv1.NamespaceDefault 表示在 default 命名空间下创建 deployment
  *** 它的源码如下, 是一个接口, 里面包含了一个 Deployments 的方法, 需要传入一个 string 类型的命名空间 ***
  type DeploymentsGetter interface {
   Deployments(namespace string) DeploymentInterface
  }
 */
 deploymentsClient := clientset.AppsV1().Deployments(apiv1.NamespaceDefault)

 // 创建 deployment 结构体实例
 deployment := &appsv1.Deployment{
  ObjectMeta: metav1.ObjectMeta{
   Name: "demo-deployment",
  },
  Spec: appsv1.DeploymentSpec{
   Replicas: ptr.To[int32](2),
   Selector: &metav1.LabelSelector{
    MatchLabels: map[string]string{
     "app": "demo",
    },
   },
   Template: apiv1.PodTemplateSpec{
    ObjectMeta: metav1.ObjectMeta{
     Labels: map[string]string{
      "app": "demo",
     },
    },
    Spec: apiv1.PodSpec{
     Containers: []apiv1.Container{
      {
       Name:            "web",
       Image:           "nginx:1.12",
       ImagePullPolicy: "IfNotPresent",
       Ports: []apiv1.ContainerPort{
        {
         Name:          "http",
         Protocol:      apiv1.ProtocolTCP,
         ContainerPort: 80,
        },
       },
      },
     },
    },
   },
  },
 }

 // 创建 Deployment
 fmt.Println("Creating deployment...")
 // 如果创建成功，Kubernetes API Server 会返回实际存储在 etcd 中的完整 Deployment 对象。
 result, err := deploymentsClient.Create(context.TODO(), deployment, metav1.CreateOptions{})
 if err != nil {
  panic(err)
 }

 fmt.Printf("Created deployment %q.\n", result.GetObjectMeta().GetName())
}

# 运行后的终端回显
Creating deployment...
Created deployment "demo-deployment".
```
- 运行之后，我们去集群查看一下是否创建成功
```
# 命令查看
[root@master1 ~]# kubectl get pod --show-labels -l app=demo
NAME                             READY   STATUS    RESTARTS   AGE     LABELS
demo-deployment-7fd4444d-9pnrs   1/1     Running   0          5m56s   app=demo,pod-template-hash=7fd4444d
demo-deployment-7fd4444d-thg8s   1/1     Running   0          5m56s   app=demo,pod-template-hash=7fd4444d
```

### 2.2、执行Update

```
package main

import (
 "context"
 "flag"
 "fmt"
 "path/filepath"

 apiv1 "k8s.io/api/core/v1"
 metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
 "k8s.io/client-go/kubernetes"
 "k8s.io/client-go/tools/clientcmd"
 "k8s.io/client-go/util/homedir"
 "k8s.io/client-go/util/retry"
 "k8s.io/utils/ptr"
)

func main() {
 // 拿到 config 配置
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

 /*
  定义一个 deployment 操作客户端对象
  deployment 资源是在 apps/v1 这个 api下的所以需要 .AppsV1.Deployments
  apiv1.NamespaceDefault 表示在 default 命名空间下创建 deployment
  *** 它的源码如下, 是一个接口, 里面包含了一个 Deployments 的方法, 需要传入一个 string 类型的命名空间 ***
  type DeploymentsGetter interface {
   Deployments(namespace string) DeploymentInterface
  }
 */
 deploymentsClient := clientset.AppsV1().Deployments(apiv1.NamespaceDefault)

 // Update Deployment
 fmt.Println("Updating deployment...")

 /*
  采用冲突重试机制（Retry on Conflict） 来保证更新的可靠性
  Kubernetes使用 乐观锁机制:
   每个资源都有 metadata.resourceVersion 字段
   当你 Update 一个资源时，API Server 会检查你提交的对象的 resourceVersion 是否与当前集群中的一致
   如果不一致（说明别人已经改过），就会返回 409 Conflict 错误。
 */
 retryErr := retry.RetryOnConflict(retry.DefaultRetry, func() error {
  //在尝试更新之前获取最新版本的Deployment
  // RetryOnConflict使用指数回退来避免耗尽apisserver
  result, getErr := deploymentsClient.Get(context.TODO(), "demo-deployment", metav1.GetOptions{})
  if getErr != nil {
   panic(fmt.Errorf("Failed to get latest version of Deployment: %v", getErr))
  }

  result.Spec.Replicas = ptr.To[int32](1)                        // 更新副本字段为1, 也就是缩小到一个 pod
  result.Spec.Template.Spec.Containers[0].Image = "nginx:latest" //  更新镜像
  _, updateErr := deploymentsClient.Update(context.TODO(), result, metav1.UpdateOptions{})
  return updateErr
 })
 if retryErr != nil {
  panic(fmt.Errorf("Update failed: %v", retryErr))
 }
 fmt.Println("Updated deployment...")

}

# 运行后的终端回显
Updating deployment...
Updated deployment...
```
- 这次我们直接使用代码去查看资源

### 2.3、执行List

```
package main

import (
 "context"
 "flag"
 "fmt"
 "path/filepath"

 apiv1 "k8s.io/api/core/v1"
 metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
 "k8s.io/client-go/kubernetes"
 "k8s.io/client-go/tools/clientcmd"
 "k8s.io/client-go/util/homedir"
)

func main() {
 // 拿到 config 配置
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

 /*
  定义一个 deployment 操作客户端对象
  deployment 资源是在 apps/v1 这个 api下的所以需要 .AppsV1.Deployments
  apiv1.NamespaceDefault 表示在 default 命名空间下创建 deployment
  *** 它的源码如下, 是一个接口, 里面包含了一个 Deployments 的方法, 需要传入一个 string 类型的命名空间 ***
  type DeploymentsGetter interface {
   Deployments(namespace string) DeploymentInterface
  }
 */
 deploymentsClient := clientset.AppsV1().Deployments(apiv1.NamespaceDefault)

 // List Deployments
 fmt.Printf("Listing deployments in namespace %q:\n", apiv1.NamespaceDefault)
 list, err := deploymentsClient.List(context.TODO(), metav1.ListOptions{})
 if err != nil {
  panic(err)
 }
 for _, d := range list.Items {
  fmt.Printf(" * %s (%d replicas)\n", d.Name, *d.Spec.Replicas)
  for _, c := range d.Spec.Template.Spec.Containers {
   fmt.Printf("   - %s (%s)\n", c.Name, c.Image)
  }
 }

}

# 运行后的终端回显
Listing deployments in namespace "default":
 * demo-deployment (1 replicas)   # deployment 名字
   - web (nginx:latest)           # 使用的image
 * nfs-provisioner (1 replicas)
   - nfs-provisioner (registry.cn-beijing.aliyuncs.com/mydlq/nfs-subdir-external-provisioner:v4.0.0)
```

### 2.4、执行Delete

```
package main

import (
 "context"
 "flag"
 "fmt"
 "path/filepath"

 apiv1 "k8s.io/api/core/v1"
 metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
 "k8s.io/client-go/kubernetes"
 "k8s.io/client-go/tools/clientcmd"
 "k8s.io/client-go/util/homedir"
)

func main() {
 // 拿到 config 配置
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

 /*
  定义一个 deployment 操作客户端对象
  deployment 资源是在 apps/v1 这个 api下的所以需要 .AppsV1.Deployments
  apiv1.NamespaceDefault 表示在 default 命名空间下创建 deployment
  *** 它的源码如下, 是一个接口, 里面包含了一个 Deployments 的方法, 需要传入一个 string 类型的命名空间 ***
  type DeploymentsGetter interface {
   Deployments(namespace string) DeploymentInterface
  }
 */
 deploymentsClient := clientset.AppsV1().Deployments(apiv1.NamespaceDefault)

 // Delete Deployment
 fmt.Println("Deleting deployment...")
 /*
   deletePolicy为删除策略, 可选值为 Foreground, Background, Orphan

   Kubernetes 提供三种 DeletionPropagation 策略：

  策略 行为 特点
  Foreground
  metav1.DeletePropagationForeground 先删子资源（dependents），再删父资源 ✅ 安全、有序
  ❌ 删除操作会阻塞直到所有子资源被清理完
  Background
  metav1.DeletePropagationBackground 先删父资源，后台异步删子资源 ⚡ 快速返回
  ⚠️ 父资源立即消失，子资源稍后清理
  Orphan
  metav1.DeletePropagationOrphan 只删父资源，子资源变为“孤儿”（ownerReferences 被清空） 🧩 子资源继续运行
  🔧 常用于迁移或调试
 */
 deletePolicy := metav1.DeletePropagationForeground
 if err := deploymentsClient.Delete(context.TODO(), "demo-deployment", metav1.DeleteOptions{
  PropagationPolicy: &deletePolicy,
 }); err != nil {
  panic(err)
 }
 fmt.Println("Deleted deployment.")

}

# 运行后的终端回显
Deleting deployment...
Deleted deployment.
```
- 此时再去使用kubectl查看的话，资源就会已经被删除了。
```
[root@master1 ~]# kubectl get pod --show-labels -l app=demo -o wide
No resources found in default namespace.
```

## 三、Client-Go+Gin

- 那么好既然学习了Client-Go又正好你会Go 的 Web Gin框架，这个时候我们的玩法就很多了，比如我们可以使用这两个去写API接口，通过API接口去操作你的Kubernetes集群。
- 以下代码非专业。

### 3.1、Cretae 接口

```
package main

import (
 "context"
 //"flag"
 "net/http"
 "os"
 "path/filepath"

 "github.com/gin-gonic/gin"
 appsv1 "k8s.io/api/apps/v1"
 apiv1 "k8s.io/api/core/v1"
 metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
 "k8s.io/client-go/kubernetes"
 "k8s.io/client-go/rest"
 "k8s.io/client-go/tools/clientcmd"
 "k8s.io/client-go/util/homedir"
)

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

// 请求体结构
type DeployRequest struct {
 Name      string \`json:"name" binding:"required"\`
 Namespace string \`json:"namespace" binding:"required"\`
 Replicas  int32  \`json:"replicas"\`
 Image     string \`json:"image" binding:"required"\`
}

func createDeployment(c *gin.Context) {
 var req DeployRequest
 // 绑定请求体
 if err := c.ShouldBindJSON(&req); err != nil {
  c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
  return
 }

 // 永远创建一个副本数大于 0 的 deployment
 if req.Replicas <= 0 {
  req.Replicas = 1
 }

 // 创建 deployment 构建对象
 deployment := &appsv1.Deployment{
  ObjectMeta: metav1.ObjectMeta{
   Name:      req.Name,
   Namespace: req.Namespace,
  },
  Spec: appsv1.DeploymentSpec{
   Replicas: &req.Replicas,
   Selector: &metav1.LabelSelector{
    MatchLabels: map[string]string{"app": req.Name},
   },
   Template: apiv1.PodTemplateSpec{
    ObjectMeta: metav1.ObjectMeta{
     Labels: map[string]string{"app": req.Name},
    },
    Spec: apiv1.PodSpec{
     Containers: []apiv1.Container{
      {
       Name:            "app",
       Image:           req.Image,
       ImagePullPolicy: "IfNotPresent",
       Ports:           []apiv1.ContainerPort{{ContainerPort: 80}},
      },
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

 c.JSON(http.StatusCreated, gin.H{
  "message": "Deployment created",
  "name":    result.Name,
  "ns":      result.Namespace,
 })
}

func main() {

 // route
 r := gin.Default()

 // Create 接口
 r.POST("/deploy", createDeployment)

 // 9000 是一个神奇的端口
 if err := r.Run(":9000"); err != nil {
  panic(err)
 }
 
}
```
- 此时我们直接在windows的cmd去调一下这个接口去看一下我们写的这个接口的效果。
- 其实最好还是打开一个虚拟机，把IP地址更改为你的宿主机即可，不知道为什么在cmd复制粘贴会出现问题。
- 以下请求体中的字段就不用介绍了吧，了解K8S的应该都清楚。
```
curl -X POST http://10.1.30.66:9000/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-web",    
    "namespace": "default",
    "replicas": 2,
    "image": "nginx:latest"
  }'
  
# 执行成功的回显内容  
 {"message":"Deployment created","name":"my-web","ns":"default"}
```
- 去看一下是否创建出了我们指定的资源。
```
[root@master1 ~]# kubectl get pod
NAME                              READY   STATUS    RESTARTS        AGE
my-web-55bdf964db-s2ww8           1/1     Running   0               62s
my-web-55bdf964db-zjzhx           1/1     Running   0               62s
```
- 以上就是一个很简单的接口的实现了，基于此接口你应该也可以写出来删除、查看、更新的接口。
- 你以为到这里就文章就结束了嘛？nonono，没有前端页面支撑的接口我觉得不完美，下面我们写一个demo，使其能够通过web页面直接去操作我们的接口，摇身一变身成为运维开发，节目效果，这些也即是九牛一毛上的毛尖尖。

### 3.2、Gin框架的模板渲染

- Gin 是 Go 语言生态中高性能的 Web 框架，其内置的模板渲染功能基于 Go 标准库 `html/template` 实现，同时扩展了更便捷的模板加载、变量传递、模板继承等特性，非常适合开发动态 HTML 页面。

#### 3.2.1、前端代码

```
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>K8s Deployment 创建工具</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Arial', sans-serif;
        }
        body {
            background-color: #f5f7fa;
            padding: 2rem;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            padding: 2.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 15px rgba(0,0,0,0.05);
        }
        h1 {
            color: #2d3748;
            margin-bottom: 2rem;
            text-align: center;
            font-size: 1.8rem;
        }
        .form-group {
            margin-bottom: 1.5rem;
        }
        label {
            display: block;
            margin-bottom: 0.5rem;
            color: #4a5568;
            font-weight: 500;
        }
        input {
            width: 100%;
            padding: 0.8rem 1rem;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            font-size: 1rem;
            transition: border 0.3s;
        }
        input:focus {
            outline: none;
            border-color: #4299e1;
            box-shadow: 0 0 0 3px rgba(66,153,225,0.1);
        }
        button {
            width: 100%;
            padding: 1rem;
            background-color: #4299e1;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s;
        }
        button:hover {
            background-color: #3182ce;
        }
        button:disabled {
            background-color: #a0aec0;
            cursor: not-allowed;
        }
        .message {
            margin-top: 1.5rem;
            padding: 1rem;
            border-radius: 6px;
            display: none;
        }
        .success {
            background-color: #e8f4f8;
            color: #22c55e;
            border: 1px solid #d1fae5;
        }
        .error {
            background-color: #fef2f2;
            color: #ef4444;
            border: 1px solid #fecaca;
        }
        .hint {
            font-size: 0.875rem;
            color: #718096;
            margin-top: 0.3rem;
        }
    </style>
</head>
<body>
<div class="container">
    <h1>创建 K8s Deployment</h1>
    <form id="deployForm">
        <div class="form-group">
            <label for="name">Deployment 名称 <span style="color: #ef4444;">*</span></label>
            <input type="text" id="name" required placeholder="例如：my-app-deploy">
            <div class="hint">请输入唯一的 Deployment 名称，支持字母、数字、连字符和下划线</div>
        </div>

        <div class="form-group">
            <label for="namespace">命名空间 <span style="color: #ef4444;">*</span></label>
            <input type="text" id="namespace" required placeholder="例如：default">
            <div class="hint">目标命名空间需提前存在（默认：default）</div>
        </div>

        <div class="form-group">
            <label for="replicas">副本数</label>
            <input type="number" id="replicas" min="1" value="1" placeholder="默认：1">
            <div class="hint">最小为1，为空时默认创建1个副本</div>
        </div>

        <div class="form-group">
            <label for="image">镜像地址 <span style="color: #ef4444;">*</span></label>
            <input type="text" id="image" required placeholder="例如：nginx:1.25 或 registry.example.com/my-app:v1">
            <div class="hint">请填写完整的镜像名称（含仓库地址和标签，如需要）</div>
        </div>

        <button type="submit" id="submitBtn">创建 Deployment</button>
    </form>

    <div id="successMsg" class="message success"></div>
    <div id="errorMsg" class="message error"></div>
</div>

<script>
    const form = document.getElementById('deployForm');
    const submitBtn = document.getElementById('submitBtn');
    const successMsg = document.getElementById('successMsg');
    const errorMsg = document.getElementById('errorMsg');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        submitBtn.disabled = true;
        submitBtn.textContent = '创建中...';
        successMsg.style.display = 'none';
        errorMsg.style.display = 'none';

        // 收集表单数据
        const formData = {
            name: document.getElementById('name').value.trim(),
            namespace: document.getElementById('namespace').value.trim() || 'default',
            replicas: parseInt(document.getElementById('replicas').value) || 1,
            image: document.getElementById('image').value.trim()
        };

        try {
            // 调用后端接口
            const response = await fetch('http://localhost:9000/deploy', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            });

            const result = await response.json();

            if (response.ok) {
                // 显示成功信息
                successMsg.textContent = \`✅ 成功创建 Deployment！名称：${result.name}，命名空间：${result.ns}\`;
                successMsg.style.display = 'block';
                form.reset(); // 重置表单
            } else {
                throw new Error(result.error || '创建失败，请检查参数或服务状态');
            }
        } catch (err) {
            // 显示错误信息
            errorMsg.textContent = \`❌ ${err.message}\`;
            errorMsg.style.display = 'block';
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = '创建 Deployment';
        }
    });
</script>
</body>
</html>
```

#### 3.2.2、调整main函数

- 主要是添加了 `r.LoadHTMLGlob("./index.html")` ，把模板渲染进来，然后访问 `/` 路由返回前端页面，重新启动程序。
- 访问: http://localhost:9000
```
func main() {

 // route
 r := gin.Default()

 // 模板渲染
 r.LoadHTMLGlob("./index.html")
 // 访问 / 路由, 将会把前端页面返回
 r.GET("/", func(c *gin.Context) {
  c.HTML(http.StatusOK, "index.html", gin.H{"主题": "Deployments"})
 })

 // Create 接口
 r.POST("/deploy", createDeployment)

 // 9000 是一个神奇的端口
 if err := r.Run(":9000"); err != nil {
  panic(err)
 }

}
```
![图片](https://mmbiz.qpic.cn/mmbiz_png/K6fzwF0Fr1zA7IU6emS0jVJOKgm9b0EmBwntYseD0lGhRGhPAjbbS3ZySL9xVk6wfGicII37nFGcjp8P1zdJibug/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=2)

- 现在我们就可以通过 web 页面去操作集群了。
![图片](https://mmbiz.qpic.cn/mmbiz_png/K6fzwF0Fr1zA7IU6emS0jVJOKgm9b0EmQGNpianicy4Ba9YM4ogrHJMpbiauAgtK4Szq7nHyCRJRIf60VK98xkSeA/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=3)

![图片](https://mmbiz.qpic.cn/mmbiz_png/K6fzwF0Fr1zA7IU6emS0jVJOKgm9b0EmicCeWtbH0N9D3ic55VfuR3Vic6cPmibpkgMYZs0Hf6QUZ5ohTlCU4Yx26A/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=4)

- 现在去集群查看资源
```
[root@master1 ~]# kubectl get pod 
NAME                              READY   STATUS    RESTARTS        AGE
gin-test-74854ccf7d-ptccw         1/1     Running   0               50s
```
- 好啦，就这些啦，更多功能去自己挖掘吧，因为我也在挖掘，没啦没啦，干活去了。

---

扫码加小助手微信，拉你进技术交流群🔥

我是南哥，日常分享云原生高质量文章，下面是我录制的课程，有需要可以购买！

继续滑动看下一个

CIT云原生

向上滑动看下一个