# kubernetes模块

Kubernetes 模块（kubernetes）是一个 Python 客户端库，用于与 Kubernetes 集群进行交互。通过这个模块，你可以在 Python 脚本中管理 Kubernetes 资源，对各种资源进行增删改查。

Kubernetes 模块操作 k8s 集群需要了解的一些基础概念：

1. Kubernetes API
   - kubernetes 模块使用 Kubernetes API 来管理集群资源。API 提供了对集群中各种资源（如Pods、Nodes、Services 等）的 CRUD（创建、读取、更新、删除）操作。

2. 配置文件
   - Kubernetes 配置文件用于存储集群的连接信息。它通常位于 k8s 控制节点的~/.kube/config，你可以通过 config_file 参数指定其他位置。
   - kubectl客户端，先通过`$KUBECONFIG`环境变量查找kubeconfig文件位置，没找到的话，去`~/.kube/config/`目录下找kubeconfig文件
3. 核心方法
   - `CoreV1Api`: 主要用于管理 k8s 集群的核心资源，如 Pods、Services、Nodes 等。
   - `AppsV1Api`: 用于管理 k8s 应用程序资源，如 Deployments、StatefulSets 等。

## 安装

~~~python
pip3 install kubernetes
# 清华源速度更快
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple kubernetes
~~~

## 基本配置

### 导入模块

~~~python
from kubernetes import client, config
~~~

从 Kubernetes 库中导入 client 和 config 模块。它的作用如下：
1. kubernetes：
  - 通过 kubernetes 库，你可以使用 Python 脚本与 Kubernetes API 进行交互，以便管理和操作 Kubernetes 集群中的各种资源（如 Pods、Services、Deployments 等）。
2. client：
  - client 模块包含 Kubernetes API 的具体类和方法，这些类用于与Kubernetes API 交互。
  - 例如，CoreV1Api 就是 client 模块中的一个类，通过它可以操作 Kubernetes 的核心资源（如 Pods、Services 等）。
3. config：
  - config 模块用于处理 Kubernetes 客户端的配置信息，主要是用于加载Kubernetes 集群的连接配置。它帮助你的脚本找到并连接到正确的 Kubernetes 集群。
  - 例如，`config.load_kube_config()` 用于加载本地的 kubeconfig 文件（通常位于 `~/.kube/config`），使 Python 脚本能够连接到你本地配置的 Kubernetes集群。
  - 如果是在集群内运行，你可以使用 `config.load_incluster_config()`，它会自动
    加载集群内部的认证信息。
### 加载配置文件
1. 如果你的 config 文件放在默认位置（~/.kube/config），可以这样加载：`config.load_kube_config()`
2. 如果config文件需要指定路径：`config.load_kube_config(config_file='D:/config')`

# 常用操作

## 获取所有api资源



## 获取节点列表

## 获取所有ns下的pod

## 创建pod
