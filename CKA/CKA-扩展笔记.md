# k8s高可用和节点规划

- apiserver和etcd要做高可用。etcd要做数据备份。

- k8s集群机器如果暴力关机，再启动之后某些组件很有可能坏掉了，集群就起不来了。

- etcd一般做三个或者5个备份 - 因为有奇数选举机制：

  - leader选举算法采用了paxos协议。

  - paxos核心思想：当多数server写成功，则任务数据写成功。如果有3个server则2个写成功即可，当有4个或5个server，则3个写成功即可。服务器数量一般为单数个：如果有3个server，最多允许有一个server挂掉，如果有4个server，则同样最多允许一个server挂掉，因此，我们可以看出，3台服务器和4台服务器的容灾能力是一样的，为了节省服务器资源，我们通常采用奇数数量，作为服务器部署数量。

- 节点数量规划：

  1. 部署多个节点达到总部署服务的要求（每个节点配置可以小些）
     缺点：管理机器多

  2. 部署少量工作节点达到部署服务要求（每个节点配置可以大些）
     缺点：在更少的节点上运行相同的工作负载自然意味着在每个节点上运行更多的pods，每个pod在运行在节点上的Kubernetes代理上引入了一些开销——比如容器运行时(例如Docker)、kubelet和cAdvisor。

     例如，kubelet对节点上的每个容器执行定期的活性和准备性探测——容器越多，意味着kubelet在每次迭代中要做的工作就越多。

     cAdvisor收集节点上所有容器的资源使用统计信息，kubelet定期查询这些信息并在其API上公开——同样，这意味着在每次迭代中cAdvisor和kubelet都要做更多的工作。如果Pod的数量变大，这些事情可能会开始降低系统的速度，甚至使系统变得不可靠。

# 制作k8s安装需要的离线yum源

> 要全内网环境安装docker、k8s和相关依赖，需要在内部提供安装k8s、docker需要的yum源。首先需要在联网机器上把镜像拉下来。

## 制作安装docker需要的离线yum源

1、添加docker在线源

```bash
yum-config-manager --add-repo https://download.docker.com/linux/centos/dockerce.repo
```

2、通过如下命令download远程yum源文件，建立本地docker repo库

```bash
yum install --downloadonly --downloaddir=/mnt/docker-ce docker-ce
createrepo -d /mnt/docker-ce
```

3、把/mnt/docker-c下自动下载的rpm打包，传到内网机器，用过如下方法安装：

```bash
rpm -Uvh *.rpm --nodeps --force #这是强制安装当前文件夹中所有的rpm包，忽略依赖去安装
```

## 制作安装k8s命令行工具需要的离线yum源

1、添加k8s在线源

```bash
cat <<EOF > /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://mirrors.aliyun.com/kubernetes/yum/doc/yum-key.gpg
https://mirrors.aliyun.com/kubernetes/yum/doc/rpm-package-key.gpg
EOF
```

2、通过如下命令download远程yum源文件，建立本地k8s repo库

```bash
yum install --downloadonly --resolve kubeadm kubelet kubectl --destdir /mnt/k8s
createrepo -d /mnt/k8s
```

3、把/mnt/k8s下自动下载的rpm打包，传到内网机器，用过如下方法安装：

```bash
rpm -Uvh *.rpm --nodeps --force #这是强制安装当前文件夹中所有的rpm包，忽略依赖去安装
```

## 制作不同版本k8s集群需要的离线镜像

```bash
#如果用docker做容器，按照下面方面制作离线镜像
kubeadm config print init-defaults > kubeadm.yaml
#修改kubeadm.yaml配置文件如下：
imageRepository: registry.cn-hangzhou.aliyuncs.com/google_containers
#上述配置表示，安装k8s需要的镜像要从阿里云镜像仓库拉取

#通过如下命令下载镜像：
kubeadm config images pull --config kubeadm.yaml
#然后把下载好的镜像打包镜像：
docker save -o a.tar.gz registry.aliyuncs.com/google_containers/pause:3.7 jenkins/jenkins:latest ....
#传到内网k8s节点，通过如下命令导出镜像：
ctr -n=k8s.io images import a.tar.gz
docker load -i a.tar.gz
```

```bash
#如果用containerd做容器，按照下面方面制作离线镜像
kubeadm config print init-defaults > kubeadm.yaml
#修改kubeadm.yaml配置文件如下：
imageRepository: registry.cn-hangzhou.aliyuncs.com/google_containers
#上述配置表示，安装k8s需要的镜像要从阿里云镜像仓库拉取
#通过如下命令下载镜像：
kubeadm config images pull --config kubeadm.yaml

ctr -n=k8s.io images ls
#ls出来的的所有镜像做到离线文件里
ctr -n=k8s.io images export k8s1.28.0.tar.gz
#导入到内网环境解压
ctr -n=k8s.io images import k8s1.28.0.tar.gz
```

# ctr和crictl区别

- 背景：在部署k8s的过程中，经常要对镜像进行操作（拉取、删除、查看等）

- 问题：使用过程中会发现ctr和crictl有很多相同功能，也有些不同，那区别到底在哪里？

- 说明：

1. ctr是containerd自带的CLI命令行工具，crictl是k8s中CRI（容器运行时接口）的客户端，k8s使用该客户端和containerd进行交互；

```bash
cat /etc/crictl.yaml 
runtime-endpoint: unix:///run/containerd/containerd.sock
image-endpoint: unix:///run/containerd/containerd.sock
timeout: 10
debug: false
pull-image-on-create: false
disable-pull-on-run: false
```

2.ctr和crictl命令具体区别如下，也可以--help查看。

- crictl缺少对具体镜像的管理能力，可能是k8s层面镜像管理可以由用户自行控制，能配置pod里面容器的统一镜像仓库，镜像的管理可以有habor等插件进行处理。

![image-20231023220844831](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202401021029023.png)                             

（注：docker save -o打包的镜像，用ctr -n=k8s.io images import可以解压出来）

# k8s舍弃dockershim

- 调用链上看 - 用containerd更高效
  - 用dockerd作为容器运行时：kubelet --> dockershim --> dockerd --> containerd
  - 用containerd作为容器运行时：kubelet --> CRI pulgin(containerd进程内) --> containerd

- 资源利用率上看 - 用containerd更精简
  - （Docker不是一个纯粹的容器运行时，具有大量其他功能）。

# containerd和docker作为容器运行时的区别

- 拉取镜像时：

  ~~~sh
  #containerd需要写明完整镜像路径
  ctr -n=k8s.io images pull docker.io/library/centos:latest
  #docker拉镜像可以简写
  docker pull centos
  ~~~

  
