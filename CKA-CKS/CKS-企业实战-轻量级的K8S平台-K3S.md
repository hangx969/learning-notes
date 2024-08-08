# 边缘计算

![image-20240514212240562](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202405142122675.png)

- 边缘计算也称为边缘处理，是一种将服务器放置在本地设备（数据源）附近的网络技术，解决数据传输的延迟问题。这样的处理方式是在传感器附近或者设备产生数据的位置进行的，因此称之为边缘。“边缘”特指计算资源在地理分布上更加靠近数据源，而远离云数据中心的资源节点。典型的边缘计算分为物联网（例如：智慧城市，智能家居，大型商店等）和非物联网（例如：游戏，CDN 等）场景。
- 应用场景：在无人驾驶中，如果将传感器数据上传到云计算中心将会增加实时处理难度，并且受到网络制约，因此无人驾驶主要依赖车内计算单元来识别交通信号和障碍物，并且规划路径

# K3S介绍

- k3s是经过CNCF认证的由Rancher公司开发维护的一个轻量级的 Kubernetes 发行版，内核机制还是和 k8s 一样，但是剔除了很多外部依赖以及 K8s 的 alpha、beta 特性，同时改变了部署方式和运行方式，目的是轻量化 K8s，简单来说，K3s 就是阉割版 K8s，消耗资源极少。它主要用于**边缘计算、物联网**等场景。K3s 具有以下特点：
  - 安装简单，占用资源少，只需要512M内存就可以运行起来；
  - apiserver、scheduler等组件全部简化，并以进程的形式运行在节点上。把**控制节点程序都打包到一个二进制文件**里面，每个程序只需要占用100M内存；
  - 使用基于sqlite3的轻量级存储后端作为默认存储机制。同时支持使用etcd3、MySQL 和PostgreSQL作为存储机制；
  - 默认使用 local-path-provisioner 提供本地存储卷；默认安装了Helm controller 和 Traefik Ingress controller；
  - 所有control-plane组件的操作都**封装在单个二进制文件和进程中**，使K3s具有自动化和管理包括证书分发在内的复杂集群操作的能力。
  - 减少外部依赖，操作系统只需要安装较新的内核（centos7.6就可以，不需要升级内核）以及支持cgroup即可，k3s安装包已经包含了containerd、Flannel、CoreDNS。非常方便地一键式安装，不需要额外安装Docker、Flannel等组件。
- 与此同时，Rancher 中国团队推出了一款针对 K3s 的效率提升工具：**AutoK3s**。只需要输入一行命令，即可快速创建 K3s 集群并添加指定数量的 master 节点和 worker 节点。
- k3s和k8s具体有多大的差别：在实际的应用部署中，几乎没有任何差异，至少到目前为止，大部分所遇到的场景，k8s能满足的，k3s也能满足。

# K3S架构

- 单master架构
  - 控制节点（在K3s里叫做server node)，数据存储使用 sqlite 并内置在了控制节点上。
  - 每个 agent 节点都注册到同一个 server 节点。K3s 用户可以通过调用server节点上的K3s API来操作资源。

![image-20240514220329156](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202405142203219.png)

- 多master架构
  - K3s Server 节点：两个或者更多的server节点将为 Kubernetes API 提供服务并运行其他 control-plane 服务
  - 外部数据库：外部数据存储（与单节点 k3s 设置中使用的嵌入式 SQLite 数据存储相反）

## 应用案例

![image-20240514221358017](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202405142213092.png)

# 部署K3S-基于k8s-1.20

## 环境规划

- Linux 的内核版本在3.10以上，每台服务器上至少要有512MB的内存空间，硬盘中可用的存储空间必须大于500 MB。
- 虚机配置：
  - centos7.6，4Gib内存/6vCPU/100G硬盘，开启处理器-虚拟化引擎里面的虚拟化配置。

- 集群配置

| k3s集群角色 | IP             | 安装的组件 |
| ----------- | -------------- | ---------- |
| Server节点  | 192.168.40.200 | K3s server |
| Agent节点   | 192.168.40.138 | K3s agent  |

## 配置系统

- 与K8S的初始化步骤相同
- 配置yum源
- 关掉防火墙
- 关掉selinux
- 修改内核参数
- 关掉swap交换分区

## 安装containerd

~~~sh
#在server和agent上安装containerd
yum install containerd -y
systemctl start containerd --now
~~~

## 安装K3S

- rancher文档：[快速入门指南 | K3s](https://docs.k3s.io/zh/quick-start)

~~~sh
#server节点上
curl -sfL http://rancher-mirror.rancher.cn/k3s/k3s-install.sh | INSTALL_K3S_MIRROR=cn sh -
#如果国内网络以上命令不行的话，手动安装
#上传k3s1.20.6安装包到server节点和agent节点，上传k3s-install.sh
ctr images import k3s1.20.6.tar.gz
INSTALL_K3S_VERSION=v1.20.6+k3s1 && INSTALL_K3S_MIRROR=cn && sh k3s-install.sh
#验证安装
k3s kubectl get nodes
#kubectl get nodes也行
k3s kubectl get pods -n kube-system
#部署完成之后，上面所有kube-system的进程都由 k3s 这个 service 来创建管理：
systemctl status k3s
ss -antulp | grep 6443 #apiserver
ss -antulp | grep 10250 # kubelet
ss -antulp | grep 10251 #scheduler
ss -antulp | grep 10252 #controller manager
#这些控制平面组件都由同一个进程管理
~~~

## 扩容agent节点

- 提取join token

~~~sh
#添加worker节点。在这些节点上安装K3s之后，需要一个join token。Join token存在于master节点的文件系统上。复制并将它保存。
cat /var/lib/rancher/k3s/server/node-token
~~~

- 扩容agent节点

~~~sh
#在agent节点上执行如下，把work节点加入k3s:
curl -sfL http://rancher-mirror.rancher.cn/k3s/k3s-install.sh | INSTALL_K3S_MIRROR=cn K3S_URL=https://192.168.40.200:6443 K3S_TOKEN=K1061ead9dd84d99881259235b6a29779e71b2d65443248abecb6304fd6b53f0d9c::server:0b4d47cf632a46a077705c17365f6280  sh -
~~~

- 查看agent节点

~~~sh
#server node上
k3s kubectl get nodes
#给工作节点打标签
kubectl label node rancher node-role.kubernetes.io/worker=worker
#agent节点由k3s-agent管理
systemctl status k3s-agent
~~~

## 卸载k3s集群

- [Uninstalling K3s | K3s](https://docs.k3s.io/zh/installation/uninstall)

~~~sh
#server节点
/usr/local/bin/k3s-uninstall.sh
#agent节点
/usr/local/bin/k3s-agent-uninstall.sh
~~~

