# K8s架构与核心组件

## K8S核心组件介绍

![image-20231017210542411](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310172105530.png)

### master组件

- API server 
  - 集群对外的统一入口，以RESTful API方式做操作。

- scheduler
  - 通过算法算出pod调度到哪个节点

- controller manager
  - 管理一系列的controller（deployment、stateful set、namespace等）

- etcd
  - 存储系统
- Calico：网络插件（给pod提供IP、提供网络policy等）
- kubeproxy 

### Worker Node组件

- kubelet
- kubeproxy
- coredns
- calico
- runtime（docker/containerd）



# kubeadm安装多master集群 

> kubedam和二进制安装k8s
>
> - kubeadm是官方提供的开源工具，是一个开源项目，用于快速搭建kubernetes集群，目前是比较方便和推荐使用的。kubeadm init 以及 kubeadm join 这两个命令可以快速创建 kubernetes 集群。Kubeadm初始化k8s，所有的组件都是以pod形式运行的，具备故障自恢复能力。kubeadm适合需要经常部署k8s，或者对自动化要求比较高的场景下使用。
>
> - 二进制：在官网下载相关组件的二进制包，如果手动安装，对kubernetes理解也会更全面。
>
> - Kubeadm和二进制都适合生产环境，在生产环境运行都很稳定，具体如何选择，可以根据实际项目进行评估。

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
  hostnamectl set-hostname master1 && bash
  ```

- 升级系统，7.6 - 7.9

  ```bash
  yum update -y
  cat /etc/redhat-release
  #CentOS Linux release 7.9.2009 (Core)
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

- 配置国内阿里云docker的repo源

  ```bash
  yum install yum-utils -y
  yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
  ```

- 配置安装k8s组件需要的阿里云的repo源 

  ```bash
  vim /etc/yum.repos.d/kubernetes.repo
  
  [kubernetes]
  name=Kubernetes
  baseurl=https://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes-el7-x86_64/
  enabled=1
  gpgcheck=0
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

- 安装基础软件包

  ```bash
  ##这一步如果是国外的VM不需要修改源，用自带的源安装即可成功。
  yum install -y yum-utils device-mapper-persistent-data lvm2 wget net-tools nfs-utils lrzsz gcc gcc-c++ make cmake libxml2-devel openssl-devel curl curl-devel unzip sudo ntp libaio-devel wget vim ncurses-devel autoconf automake zlib-devel  python-devel epel-release openssh-server socat  ipvsadm conntrack ntpdate telnet ipvsadm
  ```

- 安装docker服务并配置docker镜像加速器和驱动

  ```bash
  yum install docker-ce-20.10.6 docker-ce-cli-20.10.6 containerd.io -y
  systemctl start docker && systemctl enable docker && systemctl status docker
  
  #配置docker镜像加速器和驱动
  vim /etc/docker/daemon.json 
  {
   "registry-mirrors":["https://y8y6vosv.mirror.aliyuncs.com","https://registry.docker-cn.com","https://docker.mirrors.ustc.edu.cn","https://dockerhub.azk8s.cn","http://hub-mirror.c.163.com"],
    "exec-opts": ["native.cgroupdriver=systemd"]
  } 
  #修改docker文件驱动为systemd，默认为cgroupfs，kubelet默认使用systemd，两者必须一致才可以。
  systemctl daemon-reload && systemctl restart docker && systemctl status docker
  ```

- 安装初始化k8s需要的软件包

  ```bash
  yum install -y kubelet-1.20.6 kubeadm-1.20.6 kubectl-1.20.6
  systemctl enable kubelet 
  ```

- 到这里，复制一下master1 VM的OS盘，再创建两台VM出来。

  ```bash
  # 分别修改hostname
  hostnamectl set-hostname master2 && bash
  hostnamectl set-hostname node1 && bash
  ```

- 配Hosts文件

  ```bash
  #修改每台机器的/etc/hosts文件，增加如下三行：
  192.168.40.4 master1
  192.168.40.5 master2
  192.168.40.6 node1
  ```

- 配主机间无密码登录

  ```bash
  passwd root #设一个root密码
  ssh-keygen #一路回车
  ssh-copy-id master1 #输入root密码
  ssh-copy-id master2
  ssh-copy-id node1
  #在另外两台上也执行同样操作#
  ```

## keepalive+nginx实现k8s master节点高可用

- 安装nginx主备

  ```bash
  #在master1和2上装nginx和keeplived
  yum install nginx keepalived -y
  ```

- 修改nginx配置文件

  ```bash
  
  ```

  
