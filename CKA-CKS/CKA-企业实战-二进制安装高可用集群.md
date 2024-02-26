# 二进制安装 vs kubeadm安装

- kubeadm是官方提供的开源工具，用于快速搭建kubernetes集群，相当于用程序脚本帮我们装好了集群，属于自动部署，简化部署操作，自动部署屏蔽了很多细节，使得对各个模块感知很少，如果对k8s架构组件理解不深的话，遇到问题比较难排查。Kubeadm初始化k8s，所有的组件都是以pod形式运行的，具备故障自恢复能力。kubeadm适合需要经常部署k8s，或者对自动化要求比较高的场景下使用。

- 二进制：在官网下载相关组件的二进制包，如果手动安装，对kubernetes理解也会更全面。 

- Kubeadm和二进制都适合生产环境，在生产环境运行都很稳定，具体如何选择，可以根据实际项目进行评估。

# 二进制安装多master高可用集群

## 架构图

![image-20240226204836549](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402262048651.png)

## 实验机器规划

- 操作系统：centos7.6
- 配置：4Gib内存/4vCPU/40G硬盘
- 网络：NAT
- 开启虚拟机的虚拟化

| K8S集群角色 | Ip             | 主机名          | 安装的组件                                                   |
| ----------- | -------------- | --------------- | ------------------------------------------------------------ |
| 控制节点    | 192.168.40.180 | xianchaomaster1 | apiserver、controller-manager、scheduler、etcd、docker、keepalived、nginx |
| 控制节点    | 192.168.40.181 | xianchaomaster2 | apiserver、controller-manager、scheduler、etcd、docker、keepalived、nginx |
| 控制节点    | 192.168.40.182 | xianchaomaster3 | apiserver、controller-manager、scheduler、etcd、docker       |
| 工作节点    | 192.168.40.183 | xianchaonode1   | kubelet、kube-proxy、docker、calico、coredns                 |
| Vip         | 192.168.40.199 |                 |                                                              |

## 实验环境准备

### 设置静态IP

~~~sh
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

### 修改主机名

~~~sh
hostnamectl set-hostname master1 && bash #master2 master3 node1
~~~

### 配置hosts文件

~~~sh
tee -a /etc/hosts << 'EOF'
192.168.40.180   master1
192.168.40.181   master2
192.168.40.182   master3
192.168.40.183   node1
EOF
~~~

### 配置ssh免密登录

~~~sh
ssh-keygen -t rsa
ssh-copy-id -i .ssh/id_rsa.pub master1
~~~

### 关闭firewalld

~~~sh
systemctl stop firewalld && systemctl disable firewalld
~~~

### 关闭Selinux

~~~bash
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
reboot -f
~~~

### 关闭交换分区

~~~bash
swapoff -a
vim /etc/fstab
#/dev/mapper/centos-swap swap      swap    defaults        0 0
~~~

### 修改内核参数-开路由转发

~~~bash
modprobe br_netfilter 
lsmod | grep br_netfilter
echo "modprobe br_netfilter" >> /etc/profile
cat > /etc/sysctl.d/k8s.conf <<EOF
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1 
EOF
sysctl -p /etc/sysctl.d/k8s.conf 
~~~

### 配置阿里云repo源

~~~sh
#安装rzsz命令
yum install lrzsz -y
#安装scp
yum install openssh-clients
#备份基础repo源
mkdir /root/repo.bak/
mv /etc/yum.repos.d/* /root/repo.bak/
#下载阿里云的repo源
#把CentOS-Base.repo文件上传到xianchaomaster1主机的/etc/yum.repos.d/目录下
#或者直接创建/etc/yum.repos.d/CentOS-Base.repo
vi /etc/yum.repos.d/CentOS-Base.repo
~~~

~~~yaml
# CentOS-Base.repo
#
# The mirror system uses the connecting IP address of the client and the
# update status of each mirror to pick mirrors that are updated to and
# geographically close to the client.  You should use this for CentOS updates
# unless you are manually picking other mirrors.
#
# If the mirrorlist= does not work for you, as a fall back you can try the 
# remarked out baseurl= line instead.
#
#
 
[base]
name=CentOS-$releasever - Base - mirrors.aliyun.com
failovermethod=priority
baseurl=http://mirrors.aliyun.com/centos/$releasever/os/$basearch/
        http://mirrors.aliyuncs.com/centos/$releasever/os/$basearch/
        http://mirrors.cloud.aliyuncs.com/centos/$releasever/os/$basearch/
gpgcheck=1
gpgkey=http://mirrors.aliyun.com/centos/RPM-GPG-KEY-CentOS-7
 
#released updates 
[updates]
name=CentOS-$releasever - Updates - mirrors.aliyun.com
failovermethod=priority
baseurl=http://mirrors.aliyun.com/centos/$releasever/updates/$basearch/
        http://mirrors.aliyuncs.com/centos/$releasever/updates/$basearch/
        http://mirrors.cloud.aliyuncs.com/centos/$releasever/updates/$basearch/
gpgcheck=1
gpgkey=http://mirrors.aliyun.com/centos/RPM-GPG-KEY-CentOS-7
 
#additional packages that may be useful
[extras]
name=CentOS-$releasever - Extras - mirrors.aliyun.com
failovermethod=priority
baseurl=http://mirrors.aliyun.com/centos/$releasever/extras/$basearch/
        http://mirrors.aliyuncs.com/centos/$releasever/extras/$basearch/
        http://mirrors.cloud.aliyuncs.com/centos/$releasever/extras/$basearch/
gpgcheck=1
gpgkey=http://mirrors.aliyun.com/centos/RPM-GPG-KEY-CentOS-7
 
#additional packages that extend functionality of existing packages
[centosplus]
name=CentOS-$releasever - Plus - mirrors.aliyun.com
failovermethod=priority
baseurl=http://mirrors.aliyun.com/centos/$releasever/centosplus/$basearch/
        http://mirrors.aliyuncs.com/centos/$releasever/centosplus/$basearch/
        http://mirrors.cloud.aliyuncs.com/centos/$releasever/centosplus/$basearch/
gpgcheck=1
enabled=0
gpgkey=http://mirrors.aliyun.com/centos/RPM-GPG-KEY-CentOS-7
 
#contrib - packages by Centos Users
[contrib]
name=CentOS-$releasever - Contrib - mirrors.aliyun.com
failovermethod=priority
baseurl=http://mirrors.aliyun.com/centos/$releasever/contrib/$basearch/
        http://mirrors.aliyuncs.com/centos/$releasever/contrib/$basearch/
        http://mirrors.cloud.aliyuncs.com/centos/$releasever/contrib/$basearch/
gpgcheck=1
enabled=0
gpgkey=http://mirrors.aliyun.com/centos/RPM-GPG-KEY-CentOS-7
~~~

### 配置阿里云docker源

~~~sh
yum install yum-utils -y
yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo 
#会把阿里云的docker源的配置给拉下来。
~~~

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

- 不开启ipvs将会使用iptables进行数据包转发，但是效率低，所以官网推荐需要开通ipvs。

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

### 安装配置docker-ce

- 安装

~~~sh
yum install docker-ce docker-ce-cli containerd.io -y 
systemctl start docker && systemctl enable docker.service && systemctl status docker
~~~

- 配置镜像加速器

~~~sh
tee /etc/docker/daemon.json << 'EOF'
{
 "registry-mirrors":["https://rsbud4vc.mirror.aliyuncs.com","https://registry.docker-cn.com","https://docker.mirrors.ustc.edu.cn","https://dockerhub.azk8s.cn","http://hub-mirror.c.163.com","http://qtid6917.mirror.aliyuncs.com", "https://rncxm540.mirror.aliyuncs.com"],
  "exec-opts": ["native.cgroupdriver=systemd"]
} 
EOF
systemctl daemon-reload
systemctl restart docker
systemctl status docker
#修改docker文件驱动为systemd，默认为cgroupfs，kubelet默认使用systemd，两者必须一致才可以。
~~~

## 搭建etcd集群



