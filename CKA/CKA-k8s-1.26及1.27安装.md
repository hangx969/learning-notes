# kubeadm安装k8s 1.26集群

## 安装准备步骤

- 修改机器IP，变成静态IP （云主机无需配置这个）

  ```bash
  vim /etc/sysconfig/network-scripts/ifcfg-ens33
  TYPE=Ethernet
  PROXY_METHOD=none
  BROWSER_ONLY=no
  BOOTPROTO=static #static表示静态ip地址
  IPADDR=192.168.40.180 #ip地址，需要跟自己电脑所在网段一致
  NETMASK=255.255.255.0  #子网掩码，需要跟自己电脑所在网段一致
  GATEWAY=192.168.40.2 #网关，在自己电脑打开cmd，输入ipconfig /all可看到
  DNS1=192.168.40.2 #DNS，在自己电脑打开cmd，输入ipconfig /all可看到 
  DEFROUTE=yes
  IPV4_FAILURE_FATAL=no
  IPV6INIT=yes
  IPV6_AUTOCONF=yes
  IPV6_DEFROUTE=yes
  IPV6_FAILURE_FATAL=no
  IPV6_ADDR_GEN_MODE=stable-privacy
  NAME=ens33 #网卡名字，跟DEVICE名字保持一致即可
  DEVICE=ens33 #网卡设备名，大家ip addr可看到自己的这个网卡设备名，每个人的机器可能这个名字不一样，需要写自己的
  ONBOOT=yes #开机自启动网络，必须是yes
  
  #修改配置文件之后需要重启网络服务才能使配置生效，重启网络服务命令如下：
  service network restart
  ```

- 关闭selinux

  ```bash
  sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config #修改selinux配置文件之后，重启机器，selinux配置才能永久生效
  reboot -f
  getenforce #显示Disabled说明selinux已经关闭
  ```

- 修改hostname

  ```bash
  hostnamectl set-hostname master-01 && bash
  hostnamectl set-hostname node-01 && bash
  ```

- 配Hosts文件

  ```bash
  #修改每台机器的/etc/hosts文件，增加如下三行：
  192.168.40.4 master-01
  192.168.40.5 node-01
  ```

- 配主机间无密码登录

  ```bash
  passwd root #设一个root密码
  ssh-keygen #一路回车
  ssh-copy-id master-01 #输入root密码
  ssh-copy-id node-01
  #在另外两台上也执行同样操作#
  ```

- 升级系统，7.6 - 7.9

  ```bash
  yum update -y
  cat /etc/redhat-release
  #CentOS Linux release 7.9.2009 (Core)
  ```

- 安装基础软件包

  ```bash
  ##这一步如果是国外的VM不需要修改源，用自带的源安装即可成功。
  yum install -y device-mapper-persistent-data lvm2 wget net-tools nfs-utils lrzsz gcc gcc-c++ make cmake libxml2-devel openssl-devel curl curl-devel unzip sudo ntp libaio-devel wget vim ncurses-devel autoconf automake zlib-devel  python-devel epel-release openssh-server socat  ipvsadm conntrack telnet ipvsadm
  ```

- 配置时间同步

  ```bash
  #安装ntpdate命令
  yum install ntpdate -y
  #跟网络时间做同步
  ntpdate cn.pool.ntp.org
  #把时间同步做成计划任务
  crontab -e
  * */1 * * * /usr/sbin/ntpdate   cn.pool.ntp.org
  #重启crond服务
  service crond restart
  ```

- 关闭交换分区

  ```bash
  #临时关闭
  swapoff -a
  #永久关闭：注释掉fatab的swap挂载
  vim /etc/fstab
  #/dev/mapper/centos-swap swap      swap    defaults        0 0
  ```

  > - Swap是交换分区，如果机器内存不够，会使用swap分区，但是swap分区的性能较低，k8s设计的时候为了能提升性能，默认是不允许使用交换分区的。
  > - Kubeadm初始化的时候会检测swap是否关闭，如果没关闭，那就初始化失败。如果不想要关闭交换分区，安装k8s的时候可以指定--ignore-preflight-errors=Swap来解决。

- 修改内核参数，开路由转发

  ```bash
  modprobe br_netfilter 
  # 加载br_netfilter模块可以使 iptables 规则可以在 Linux Bridges 上面工作，用于将桥接的流量转发至iptables链，k8s如果没有加载br_netfilter模块，会影响同node内的pod之间通过service来通信。
  # 加载这个模块是为了可以正常开启iptables和ip6tables参数
  
  echo "modprobe br_netfilter" >> /etc/profile
  
  cat > /etc/sysctl.d/k8s.conf <<EOF
  net.bridge.bridge-nf-call-ip6tables = 1
  net.bridge.bridge-nf-call-iptables = 1
  net.ipv4.ip_forward = 1 
  EOF
  #net.ipv4.ip_forward = 1做路由转发的
  ##net.ipv4.ip_forward是数据包转发：出于安全考虑，Linux系统默认是禁止数据包转发的。所谓转发即当主机拥有多于一块的网卡时，其中一块收到数据包，根据数据包的目的ip地址将数据包发往本机另一块网卡，该网卡根据路由表继续继续发送数据包。这通常是路由器所要实现的功能。
  ##要让Linux系统具有路由转发功能，需要配置一个Linux的内核参数net.ipv4.ip_forward。这个参数指定了Linux系统当前对路由转发功能的支持情况；其值为0时表示禁止进行IP转发；如果是1,则说明IP转发功能已经打开。
  
  sysctl -p /etc/sysctl.d/k8s.conf 
  #在运行时配置内核参数，-p：从指定的文件加载系统参数，如不指定即从/etc/sysctl.conf中加载
  ```

- 禁用firewalld防火墙

  ```bash
  systemctl stop firewalld && systemctl disable firewalld
  ```

- 配置阿里云的repo源

  ```bash
  #安装rzsz命令
  yum install lrzsz -y
  #安装scp：
  yum install -y openssh-clients
  #备份基础repo源
  mkdir /root/repo.bak
  cd /etc/yum.repos.d/
  mv * /root/repo.bak/
  
  #下载阿里云的repo源
  ###注意：用GLobalAzure的VM就不需要这面手动修改源了，用自带的源即可###
  #把CentOS-Base.repo和epel.repo文件上传到master1主机的/etc/yum.repos.d/目录下
  chmod 777 /etc/yum.repos.d/
  #通过vscode拖进来
  ```

- 配置阿里云docker的repo源

  ```bash
  yum install yum-utils -y
  yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo #会把阿里云的docker源的配置给拉下来。
  ```

- 配置安装k8s组件的阿里云repo源 

  ```bash
  cat >  /etc/yum.repos.d/kubernetes.repo <<EOF
  [kubernetes]
  name=Kubernetes
  baseurl=https://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes-el7-x86_64/
  enabled=1
  gpgcheck=0
  EOF
  ```

## 安装k8s组件

### 安装containerd并配置

```bash
yum install containerd.io-1.6.6 -y
#生成 containerd 的配置文件:
mkdir -p /etc/containerd
containerd config default > /etc/containerd/config.toml

#修改配置文件
vim /etc/containerd/config.toml
#SystemdCgroup = false ==> SystemdCgroup = true
#sandbox_image = "k8s.gcr.io/pause:3.6" ==> sandbox_image="registry.aliyuncs.com/google_containers/pause:3.7"

#配置 containerd 开机启动，并启动 containerd
systemctl enable containerd --now

#修改/etc/crictl.yaml文件，指定k8s的运行时和拉取镜像都使用containerd
cat > /etc/crictl.yaml <<EOF
runtime-endpoint: unix:///run/containerd/containerd.sock
image-endpoint: unix:///run/containerd/containerd.sock
timeout: 10
debug: false
EOF
systemctl restart containerd

#配置containerd镜像加速器，k8s所有节点均按照以下配置：
mkdir /etc/containerd/certs.d/docker.io/ -p
vim /etc/containerd/certs.d/docker.io/hosts.toml
#写入如下内容：
[host."https://y8y6vosv.mirror.aliyuncs.com",host."https://registry.docker-cn.com"]
  capabilities = ["pull"]
  
vim /etc/containerd/config.toml
#config_path = "" ==> config_path = "/etc/containerd/certs.d"
#保存退出
systemctl restart containerd
```

### 安装docker并配置

```bash
#docker也要安装，docker跟containerd不冲突，安装docker是为了能基于dockerfile构建镜像
yum install docker-ce -y
systemctl enable docker --now

#配置docker镜像加速器，k8s所有节点均按照以下配置
vim /etc/docker/daemon.json
{
 "registry-mirrors":["https://y8y6vosv.mirror.aliyuncs.com","https://registry.docker-cn.com","https://docker.mirrors.ustc.edu.cn","https://dockerhub.azk8s.cn","http://hub-mirror.c.163.com"]
} 

#重启docker：
systemctl daemon-reload && systemctl restart docker && systemctl status docker
```

### 安装初始化k8s需要的软件包

```bash
yum install -y kubelet-1.26.0 kubeadm-1.26.0 kubectl-1.26.0
systemctl enable kubelet
```

## 初始化集群

- 设置容器运行时

  ```bash
  crictl config runtime-endpoint unix:///run/containerd/containerd.sock
  #这个在先前/etc/crictl.yaml中已经配置过了
  ```

- 使用kubeadm初始化k8s集群

  ```bash
  #在控制节点上
  cd /root/
  kubeadm config print init-defaults > kubeadm.yaml
  #根据我们自己的需求修改配置，比如修改 imageRepository 的值，kube-proxy 的模式为 ipvs，需要注意的是由于我们使用的containerd作为运行时，所以在初始化节点的时候需要指定cgroupDriver为systemd
  ```

- kubeadm.yaml配置文件如下：

  ```yaml
  apiVersion: kubeadm.k8s.io/v1beta3
  bootstrapTokens:
  - groups:
    - system:bootstrappers:kubeadm:default-node-token
    token: abcdef.0123456789abcdef
    ttl: 24h0m0s
    usages:
    - signing
    - authentication
  kind: InitConfiguration
  localAPIEndpoint:
    advertiseAddress: 192.168.40.4 #控制节点的ip
    bindPort: 6443
  nodeRegistration:
    criSocket: unix:///run/containerd/containerd.sock ##指定containerd容器运行时
    imagePullPolicy: IfNotPresent
    name: master-01 #控制节点主机名
    taints: null
  ---
  apiServer:
    timeoutForControlPlane: 4m0s
  apiVersion: kubeadm.k8s.io/v1beta3
  certificatesDir: /etc/kubernetes/pki
  clusterName: kubernetes
  controllerManager: {}
  dns: {}
  etcd:
    local:
      dataDir: /var/lib/etcd
  imageRepository: registry.cn-hangzhou.aliyuncs.com/google_containers #registry.k8s.io #这是kubeadm安装控制节点组件时用的镜像源
  kind: ClusterConfiguration
  kubernetesVersion: 1.26.0 #这里的版本要和kubeadm\kubectl\kubelet的版本一致
  networking:
    dnsDomain: cluster.local
    podSubnet: 10.244.0.0/16 #指定pod网段
    serviceSubnet: 10.96.0.0/12
  scheduler: {}
  
  ---
  apiVersion: kubeproxy.config.k8s.io/v1alpha1
  kind: KubeProxyConfiguration
  mode: ipvs
  
  ---
  apiVersion: kubelet.config.k8s.io/v1beta1
  kind: KubeletConfiguration
  cgroupDriver: systemd
  ```

- 上传并解压K8s组件镜像离线包

  ```bash
  #解压
  ctr -n=k8s.io images import k8s_1.26.0.tar.gz
  #ctr是containerd自带的工具，有命名空间的概念，若是k8s相关的镜像，都默认在k8s.io这个命名空间，所以导入镜像时需要指定命令空间为k8s.io
  #crictl是k8s中CRI（容器运行时接口）的客户端，k8s使用该客户端和containerd进行交互
  #查看镜像
  crictl images 
  #或者
  ctr -n=k8s.io image ls
  ```

- 初始化集群

  ```bash
  kubeadm init --config=kubeadm.yaml --ignore-preflight-errors=SystemVerification
  #配置kubectl的配置文件config，相当于对kubectl进行授权，这样kubectl命令可以使用这个证书对k8s集群进行管理
  mkdir -p $HOME/.kube
  sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
  sudo chown $(id -u):$(id -g) $HOME/.kube/config
  ```

- 扩容工作节点

  ```bash
  kubeadm token create --print-join-command
  #在node-01上加参数 --ignore-preflight-errors=SystemVerification运行
  #工作节点打标签
  kubectl label nodes xianchaonode1 node-role.kubernetes.io/work=work
  ```

## 安装calico

```bash
#上传了Caclio.yaml
kubectl apply -f calico.yaml
#在线下载地址为：https://docs.projectcalico.org/manifests/calico.yaml
```

## 扩容控制节点

- 准备步骤和master-01的步骤一样。

- 装好kuneadm之后，需要额外执行的步骤：

  - 拷贝证书

    ```bash
    #把master-01节点的证书拷贝到master-02
    #在xianchaomaster2创建证书存放目录：
    cd /root && mkdir -p /etc/kubernetes/pki/etcd &&mkdir -p ~/.kube/
    
    #把master-01节点的证书拷贝到master-02上：
    scp /etc/kubernetes/pki/ca.crt xianchaomaster2:/etc/kubernetes/pki/
    scp /etc/kubernetes/pki/ca.key xianchaomaster2:/etc/kubernetes/pki/
    scp /etc/kubernetes/pki/sa.key xianchaomaster2:/etc/kubernetes/pki/
    scp /etc/kubernetes/pki/sa.pub xianchaomaster2:/etc/kubernetes/pki/
    scp /etc/kubernetes/pki/front-proxy-ca.crt xianchaomaster2:/etc/kubernetes/pki/
    scp /etc/kubernetes/pki/front-proxy-ca.key xianchaomaster2:/etc/kubernetes/pki/
    scp /etc/kubernetes/pki/etcd/ca.crt xianchaomaster2:/etc/kubernetes/pki/etcd/
    scp /etc/kubernetes/pki/etcd/ca.key xianchaomaster2:/etc/kubernetes/pki/etcd/
    ```

  - master-01的kubeadm-config ConfigMap 配置controlPlaneEndpoint

    ```bash
    kubectl -n kube-system edit cm kubeadm-config -o yaml
    #在apiversion字段平行下面添加如下字段：
    controlPlaneEndpoint: 192.168.40.4:6443 #是master-01的ip
    systemctl restart kubelet
    ```

  - kubeadm join

    ```bash
    #join命令添加参数：--control-plane --ignore-preflight-errors=SystemVerification
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

![image-20231023220844831](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310232208977.png)                             