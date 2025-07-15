# 容器运行时接口CRI

CRI（Container Runtime Interface）是Kubernetes中用于实现容器运行时和Kubernetes之间交互的标准化接口。

CRI定义了Kubernetes与底层容器运行时的通信协议和接口规范，可以让Kubernetes与不同的容器运行时进行交互，实现跨容器运行时的一致性，以达到在不需要改动任何代码的情况下支持多种运行时，比如Containerd、CRI-O、Kata等。

换句话说，只要这个容器运行时符合了CRI接口规范，k8s就能接入它来编排容器。所以k8s可以在不更改任何代码的情况下兼容多种容器运行时。

# 容器运行时管理pod流程

1. K8s收到客户端发来的操作pod的请求
2. K8s序列化请求，通过gRPC协议，发送给CRI
3. CRI拿到请求调用容器运行时去做对应操作。（注意容器是由容器运行时来管理的，而不是pod来管理的）

# containerd介绍

Containerd是一种容器运行时，可以管理容器的整个生命周期，包含镜像的传输、容器的运行和销毁、容器的监控，同时也可以管理更底层的存储和网络等。

Containerd属于Docker引擎中的一部分，在2016年12月从Docker Engine中剥离，成为了一个可以独立使用的容器运行时（Runtime），并且在2017年捐赠给了CNCF，成为了CNCF的顶级项目之一。Containerd是一个开源的容器运行时项目，同时也是CNCF体系中已经毕业的容器运行时。

由于containerd有docker背书，目前还是最广泛应用的容器运行时。我们一般不会直接用containerd作为容器管理平台，还是用docker，用containerd更多的还是用作容器运行时。

## containerd和docker的关系

Docker包含Containerd，但Containerd并不完全依赖于Docker。

Docker是一个完整的容器化平台，提供了镜像构建、容器管理、网络管理、存储管理等功能。而Containerd只是作为Docker的一个组件，负责容器的生命周期管理。

## 调用链

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202507152134702.png" alt="image-20250715213449459" style="zoom:33%;" />

docker把请求转给containerd，containerd转给RunC。注意本质上真正管理容器的是`底层容器运行时RunC`

# 命令行工具

1. ctr：containerd原生客户端工具。功能并不完善，不好用。
2. nerdctl：用于containerd并且友好兼容docker cli使用习惯。是ctr的替代品
3. crictl：为K8s设计的，遵循CRI接口规范。我们用户用的很少。

命令对比：

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202507152141594.png" alt="image-20250715214142382" style="zoom:50%;" />

## ctr

注意：

1. ctr image pull拉harbor镜像的时候，并不会读取/etc/containerd/config.toml的harbor配置，这是给kubelet用的，不是给ctr用的。ctr拉harbor镜像要用`ctr -n=k8s.io image pull --plain-http`
2. `ctr ns ls`：
   - ctr也有namespace的概念，用于资源隔离。但是ctr的ns和k8s的ns没有任何关系。
   - ctr默认会有一个default和一个k8s.io的ns。
   - k8s管理的镜像都在k8s.io的ns下面，所以k8s用的镜像都要用`ctr -n=k8s.io image import`来导入。不指定ns的时候默认会到default ns，k8s读不到。

## nerdctl

安装：

~~~sh
# 获取版本：
https://github.com/containerd/nerdctl/releases
# 下载工具：
https://github.com/containerd/nerdctl/releases/download/v1.7.6/nerdctl-1.7.6-linux-amd64.tar.gz
# 安装：
tar xf nerdctl-1.7.6-linux-amd64.tar.gz
mv nerdctl /usr/local/bin/
~~~

一般是在k8s集群故障，无法使用kubectl的时候，用nerdctl去看容器的情况
