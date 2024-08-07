# 本地VMWare环境搭建1.23版本K8S

## 环境规划

### k8s环境规划

 podSubnet（pod网段） 10.244.0.0/16

 serviceSubnet（service网段）: 10.96.0.0/12

### 实验环境规划

操作系统：centos7.9

配置： 4Gib内存/8vCPU/20G硬盘

网络：NAT模式

| K8S集群角色 | IP             | 主机名   | 安装的组件                                                   |
| ----------- | -------------- | -------- | ------------------------------------------------------------ |
| 控制节点    | 192.168.40.180 | master-1 | apiserver、controller-manager、scheduler、kubelet、etcd、kube-proxy、容器运行时、calico |
| 工作节点    | 192.168.40.181 | node-1   | Kube-proxy、calico、coredns、容器运行时、kubelet             |
| 工作节点    | 192.168.40.182 | node-2   | Kube-proxy、calico、coredns、容器运行时、kubelet             |

## 虚拟机准备

### 配置VMware虚拟机

- 安装VMware
- 下载CentOS7镜像
- 配置VMWare虚拟机，使用NAT模式。
- 安装CentOS系统

### 配置CentOS虚拟机网络

- 新搭建出来的虚拟机默认没有IP，需要先修改配置文件加一个IP

- vmware-编辑-虚拟机网络编辑器，先把网段和子网掩码设置好：

  <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202401021708568.png" alt="image-20231228195437108" style="zoom:50%;" />

- 修改网卡配置文件

  ~~~bash
  vi /etc/sysconfig/network-scripts/ifcfg-ens33
  
  TYPE=Ethernet
  PROXY_METHOD=none
  BROWSER_ONLY=no
  BOOTPROTO=static #static表示静态ip地址
  IPADDR=192.168.40.180 #ip地址，需要跟自己电脑所在网段一致
  NETMASK=255.255.255.0
  GATEWAY=192.168.40.2
  DNS1=192.168.40.2
  DEFROUTE=yes
  IPV4_FAILURE_FATAL=no
  IPV6INIT=yes
  IPV6_AUTOCONF=yes
  IPV6_DEFROUTE=yes
  IPV6_FAILURE_FATAL=no
  IPV6_ADDR_GEN_MODE=stable-privacy
  NAME=ens33 #网卡名字，跟DEVICE名字保持一致即可
  DEVICE=ens33 #网卡设备名，ip addr可看到自己的这个网卡设备名
  ONBOOT=yes #开机自启动网络，必须是yes
  ~~~

### 关闭Selinux

~~~bash
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
reboot -f
~~~

### SSH连接

- VSCode直接配置ssh host文件用内网IP登录。

#### 免密登录

- 客户端ssh-keygen生成公钥

- 把公钥复制到服务器端

  ```bash
  mkdir -p ~/.ssh/
  touch ~/.ssh/authorized_keys
  vi ~/.ssh/authorized_keys
  #将公钥值复制进去
  ```

- 编辑ssh配置文件

  ~~~bash
  sudo vim /etc/ssh/sshd_config
  #PubkeyAuthentication yes注释去掉，才可以使用公钥验证
  ~~~

- 重启ssh服务

  ~~~bash
  systemctl restart sshd.service 
  ~~~

- VsCode的ssh配置文件中加入公钥位置

  ~~~bash
  Host 192.168.40.180
    HostName 192.168.40.180
    User root
    IdentityFile /C:/Users/hangx/.ssh/id_rsa
  ~~~

### 克隆两台工作节点

- 虚拟机关机-右键克隆出两台新机器

- 修改两台机器网卡配置文件，配置静态IP

  ~~~bash
  vi /etc/sysconfig/network-scripts/ifcfg-ens33
  #IP修改成192.168.40.181,192.168.40.182
  ~~~

## 配置k8s环境准备

### 替换aliyun的epel源

~~~bash
yum install -y wget
wget -O /etc/yum.repos.d/epel-7.repo https://mirrors.aliyun.com/repo/epel-7.repo
yum clean all
~~~

### 升级系统到centos7.9

~~~bash
yum update -y
~~~

### 配置主机名

~~~bash
hostnamectl set-hostname master-1 && bash 
hostnamectl set-hostname node-1 && bash 
hostnamectl set-hostname node-2 && bash 
~~~

### 配置hosts文件

~~~bash
vim /etc/hosts
192.168.40.180   master-1  
192.168.40.181   node-1  
192.168.40.182   node-2
~~~

### 配置主机间无密码登录

~~~bash
ssh-keygen
ssh-copy-id master-1
ssh-copy-id node-1
ssh-copy-id node-2
~~~

### 关闭交换分区

~~~bash
swapoff -a
vim /etc/fstab
#/dev/mapper/centos-swap swap      swap    defaults        0 0
~~~

### 配置阿里云repo源

- 配置基础repo源

  ~~~bash
  #备份基础repo源
  mkdir /root/repo.bak
  cd /etc/yum.repos.d/
  mv * /root/repo.bak/
  #课件里面的阿里云的repo源
  #把CentOS-Base.repo和epel.repo文件上传到master1主机的/etc/yum.repos.d/目录下
  chmod o+w /etc/yum.repos.d
  #通过vscode拖进来
  ~~~

- 配置阿里云docker的repo源

  ```bash
  yum install yum-utils -y
  yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo 
  #会把阿里云的docker源的配置给拉下来。
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

### 安装基础软件包

~~~bash
yum install -y device-mapper-persistent-data lvm2 wget net-tools nfs-utils lrzsz gcc gcc-c++ make cmake libxml2-devel openssl-devel curl curl-devel unzip sudo ntp libaio-devel wget vim ncurses-devel autoconf automake zlib-devel  python-devel epel-release openssh-server socat conntrack telnet ipvsadm openssh-clients
~~~

> yum install如果出现报错：GPG key retrieval failed: [Errno 14] curl#37 - "Couldn't open file /etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-7"
>
> 意思是，yum源开启了GPG校验，需要在/etc/pki/rpm-gpg目录下存在对应安装文件的公钥文件，才能完成校验。
>
> 可以关闭掉校验：
>
> ~~~bash
> sed -i 's/pgcheck=1/pgcheck=0/g' /etc/yum.repos.d/epel.repo
> ~~~

### 配置时间同步

~~~bash
#安装ntpdate命令
yum install ntpdate -y
#跟网络时间做同步
ntpdate cn.pool.ntp.org
#把时间同步做成计划任务
crontab -e
* */1 * * * /usr/sbin/ntpdate   cn.pool.ntp.org
#重启crond服务
service crond restart
~~~

### 禁用firewalld

~~~bash
systemctl stop firewalld && systemctl disable firewalld
~~~

### 安装iptables

~~~sh
#安装iptables
yum install iptables-services -y
#禁用iptables
service iptables stop && systemctl disable iptables
#清空防火墙规则
iptables -F
~~~

### 开启IPVS

~~~sh
#把ipvs.modules上传到/etc/sysconfig/modules/目录下
vim /etc/sysconfig/modules/ipvs.modules
#脚本内容：
#!/bin/bash
ipvs_modules="ip_vs ip_vs_lc ip_vs_wlc ip_vs_rr ip_vs_wrr ip_vs_lblc ip_vs_lblcr ip_vs_dh ip_vs_sh ip_vs_nq ip_vs_sed ip_vs_ftp nf_conntrack"
for kernel_module in ${ipvs_modules}; do
 /sbin/modinfo -F filename ${kernel_module} > /dev/null 2>&1
 if [ 0 -eq 0 ]; then
 /sbin/modprobe ${kernel_module}
 fi
done
~~~

~~~sh
#赋权，加载内核模块
chmod 755 /etc/sysconfig/modules/ipvs.modules && bash /etc/sysconfig/modules/ipvs.modules && lsmod | grep ip_vs
~~~

> - ipvs (IP Virtual Server) 实现了传输层负载均衡，也就是我们常说的4层LAN交换，作为 Linux 内核的一部分。ipvs运行在主机上，在真实服务器集群前充当负载均衡器。ipvs可以将基于TCP和UDP的服务请求转发到真实服务器上，并使真实服务器的服务在单个 IP 地址上显示为虚拟服务。
>
> - kube-proxy支持 iptables 和 ipvs 两种模式， 在kubernetes v1.8 中引入了 ipvs 模式，在 v1.9 中处于 beta 阶段，在 v1.11 中已经正式可用了。iptables 模式在 v1.1 中就添加支持了，从 v1.2 版本开始 iptables 就是 kube-proxy 默认的操作模式，ipvs 和 iptables 都是基于netfilter的，但是ipvs采用的是hash表，因此当service数量达到一定规模时，hash查表的速度优势就会显现出来，从而提高service的服务性能。那么 ipvs 模式和 iptables 模式之间有哪些差异呢？
>
>   1、ipvs 为大型集群提供了更好的可扩展性和性能
>
>   2、ipvs 支持比 iptables 更复杂的复制均衡算法（最小负载、最少连接、加权等等）
>
>   3、ipvs 支持服务器健康检查和连接重试等功能

### 修改内核参数-开路由转发

~~~bash
modprobe br_netfilter 
echo "modprobe br_netfilter" >> /etc/profile
cat > /etc/sysctl.d/k8s.conf <<EOF
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1 
EOF
sysctl -p /etc/sysctl.d/k8s.conf 
~~~

## 安装K8S组件

### 安装配置docker

~~~bash
#docker也要安装，docker跟containerd不冲突，安装docker是为了能基于dockerfile构建镜像
yum install docker-ce -y
systemctl enable docker --now

#配置docker镜像加速器，k8s所有节点均按照以下配置:修改docker文件驱动为systemd，默认为cgroupfs，kubelet默认使用systemd，两者必须一致才可以。
vim /etc/docker/daemon.json
{
 "registry-mirrors":["https://y8y6vosv.mirror.aliyuncs.com","https://registry.docker-cn.com","https://docker.mirrors.ustc.edu.cn","https://dockerhub.azk8s.cn","http://hub-mirror.c.163.com"],
 "exec-opts": ["native.cgroupdriver=systemd"]
}
#重启docker：
systemctl daemon-reload && systemctl restart docker && systemctl status docker
~~~

### 安装k8s软件包

~~~bash
yum install -y kubelet-1.23.1 kubeadm-1.23.1 kubectl-1.23.1
systemctl enable kubelet
~~~

## 初始化集群

### kubeadm初始化k8s集群

~~~bash
kubeadm config print init-defaults > kubeadm.yaml
~~~

~~~yaml
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
  advertiseAddress: 192.168.40.180 #控制节点的ip
  bindPort: 6443
nodeRegistration:
  criSocket: /var/run/dockershim.sock
  imagePullPolicy: IfNotPresent
  name: master-1 #控制节点的hostname
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
imageRepository: registry.aliyuncs.com/google_containers #修改默认镜像仓库为阿里云
kind: ClusterConfiguration
kubernetesVersion: 1.23.1 #安装的版本
networking:
  dnsDomain: cluster.local
  serviceSubnet: 10.96.0.0/12 #指定service网段
  podSubnet: 10.244.0.0/16 #增加这一行，指定pod网段， 需要新增加这个
scheduler: {}
---
#新增配置，指定kubeproxy模式为ipvs
apiVersion: kubeproxy.config.k8s.io/v1alpha1
kind: KubeProxyConfiguration
mode: ipvs
---
#新增配置，指定kubelet配置为systemd
apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
cgroupDriver: systemd
~~~

~~~sh
kubeadm init --config=kubeadm.yaml --ignore-preflight-errors=SystemVerification
~~~

### 授权kubectl

~~~sh
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

#1. 设置kubectl的alias为k：
whereis kubectl # kubectl: /usr/bin/kubectl
echo "alias k=/usr/bin/kubectl">>/etc/profile
source /etc/profile
#2. 安装并设置alias的自动补全：
yum install -y bash-completion
source /usr/share/bash-completion/bash_completion
kubectl completion bash | sudo tee /etc/bash_completion.d/kubectl > /dev/null
##生成 bash 自动补全脚本，写入到 /etc/bash_completion.d/kubectl 文件中
source <(kubectl completion bash | sed 's/kubectl/k/g')
#3. 解决每次启动k都会失效，要重新刷新环境变量（source /etc/profile）的问题：在~/.bashrc文件中添加以下代码：source /etc/profile
echo "source /etc/profile" >> ~/.bashrc
#4. 给alias k也配置补全
vim ~/.bashrc
##加入以下
alias k='kubectl'
complete -o default -F __start_kubectl k
source <(kubectl completion bash)
##使命令生效
source ~/.bashrc
#安装了zsh的环境，把上面放到~/.zshrc中
echo "source /etc/profile" >> ~/.zshrc 
~~~

~~~sh
#config文件拷贝到两台node上
#node上
mkdir -p $HOME/.kube
#master上
scp $HOME/.kube/config node-1:/root/.kube/
~~~

### 扩容节点

~~~sh
kubeadm token create --print-join-command
kubeadm join 192.168.40.180:6443 --token gi3nxj.sd7cl2k1kg11751z --discovery-token-ca-cert-hash sha256:6e4da4d1909a6a07df108303f8d5f45e9d328128554d7db378cf784b3224b996 --ignore-preflight-errors=SystemVerification
kubectl label node node1 node-role.kubernetes.io/worker=worker
~~~

## 安装calico

~~~bash
#注：在线下载配置文件地址是： https://docs.projectcalico.org/manifests/calico.yaml
k apply -f calico.yaml    
~~~

~~~sh
#测试网络插件
kubectl run busybox --image busybox:1.28 --restart=Never --rm -it busybox -- sh
ping www.baidu.com
nslookup kubernetes.default.svc.cluster.local
~~~

