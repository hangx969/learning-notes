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

  # CentOS停更之后替换方案

  https://help.aliyun.com/zh/ecs/user-guide/options-for-dealing-with-centos-linux-end-of-life

  # 国产操作系统介绍

1. 银河麒麟操作系统 (Kylin OS)：（有免费的社区版）

   1. 开发者：国防科技大学

   1. 特点：主要面向政府、国防、教育等领域，具有较高的安全性和稳定性。Kylin OS 有多种版本，如桌面版和服务器版。

2. 中标麒麟 (NeoKylin)：（有免费的社区版）
   1. 开发者：银河麒麟与中标普华合作开发
   2. 特点：基于Linux内核，提供稳定和安全的操作环境，广泛应用于政府和企业。

3. 深度操作系统 (Deepin OS)：（有免费的社区版）
   1. 开发者：武汉深之度科技有限公司特点：用户界面美观，使用方便，针对普通用户和开发者，基于Debian。
   2. Deepin OS 以其深度定制的桌面环境（DDE）和丰富的软件生态而闻名。

4. UOS (统信操作系统)：（有免费的社区版）
   1. 开发者：统信软件技术有限公司
   2. 特点：面向企业级市场，整合了深度和中标麒麟的技术，提供统一的操作系统平台。
5. 欧拉：
   1. 华为开发的基于Linux内核的操作系统，主要用于企业服务器和云计算环境（有免费的）
6. 鸿蒙操作系统 (HarmonyOS)：（不是基于Linux内核，而是基于LiteOS微内核和其他技术）
   1. 开发者：华为
   2. 特点：不仅是一个手机操作系统，还适用于各种智能设备，如物联网设备、智能家居、汽车等。鸿蒙操作系统强调分布式架构和多设备协同
7. OpenHarmony：这是HarmonyOS的开源版本
