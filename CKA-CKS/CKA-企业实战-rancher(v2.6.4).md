# Rancher介绍

- Rancher是一个开源的企业级多集群Kubernetes管理平台，实现了Kubernetes集群在混合云+本地数据中心的集中部署与管理，以确保集群的安全性，加速企业数字化转型。

- Rancher官方文档：https://docs.rancher.cn/

- Rancher和k8s的区别
  - Rancher和k8s都是用来作为容器的调度与编排系统。但是rancher不仅能够管理应用容器，更重要的一点是能够管理k8s集群。Rancher2.x底层基于k8s调度引擎，通过Rancher的封装，用户可以在不熟悉k8s概念的情况下轻松的通过Rancher来部署容器到k8s集群当中。

# Rancher部署

## 实验机器准备

- Rancher VM
  - 192.168.40.138；hostname：rancher；memory：6G；cpu：6vCPU

- K8S VM
  - version：1.23.1
  - master1：192.168.40.180
  - node1：192.168.40.181

## 安装前准备

### 配置主机名

~~~sh
#配置主机名
hostnamectl set-hostname rancher && bash
#rancher、master1、node1添加host
tee -a /etc/hosts << 'EOF'
192.168.40.180   master1
192.168.40.181   node1
192.168.40.138   rancher
EOF
~~~

### 配置ssh互信

~~~sh
ssh-keygen
ssh-copy-id -i ~/.ssh/id_rsa.pub master1 #node1 rancher
~~~

### 关闭防火墙

~~~sh
systemctl stop firewalld && systemctl disable firewalld
~~~

### 关闭selinux

~~~sh
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
reboot -f
~~~

### 关闭交换分区

~~~sh
swapoff -a
vim /etc/fstab
#注释掉swap部分
~~~

### 修改内核参数

~~~sh
#br_netfilter模块用于将桥接流量转发至iptables链，br_netfilter内核参数需要开启转发。
modprobe br_netfilter
echo "modprobe br_netfilter" >> /etc/profile
cat > /etc/sysctl.d/k8s.conf <<EOF
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
EOF
sysctl -p /etc/sysctl.d/k8s.conf
~~~

> ~~~sh
> cat > /etc/sysctl.d/k8s.conf <<EOF
> ...
> EOF
> ~~~
>
> - 这种方式也可以将两个EOF之间的内容写到文件中，与tee的区别是不会将内容输出到屏幕上
> - `cat > file` 也会覆盖文件的内容。如果你希望将内容追加到文件的末尾，你可以使用 `>>` 运算符，如 `cat >> file`

### 添加阿里云docker源

~~~sh
yum install -y yum-utils
yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
~~~

### 安装常用软件包

~~~sh
yum install -y yum-utils device-mapper-persistent-data lvm2 wget net-tools nfs-utils lrzsz gcc gcc-c++ make cmake libxml2-devel openssl-devel curl curl-devel unzip sudo ntp libaio-devel wget vim ncurses-devel autoconf automake zlib-devel  python-devel epel-release openssh-server socat  ipvsadm conntrack ntpdate 
~~~

### 时间同步

~~~sh
#跟网络时间做同步
ntpdate cn.pool.ntp.org
#把时间同步做成计划任务
crontab -e
* */1 * * * /usr/sbin/ntpdate   cn.pool.ntp.org
#重启crond服务
service crond restart
~~~

## 安装docker

- 安装启动docker

~~~sh
yum install docker-ce docker-ce-cli containerd.io -y
systemctl start docker && systemctl enable docker.service
~~~

- 修改配置文件

~~~sh
tee /etc/docker/daemon.json << 'EOF'
{
"registry-mirrors":["https://rsbud4vc.mirror.aliyuncs.com","https://registry.docker-cn.com","https://docker.mirrors.ustc.edu.cn","https://dockerhub.azk8s.cn","http://hub-mirror.c.163.com","http://qtid6917.mirror.aliyuncs.com", "https://rncxm540.mirror.aliyuncs.com"],
"exec-opts": ["native.cgroupdriver=systemd"]
} 
EOF
~~~

> - `tee /etc/docker/daemon.json`：`tee` 命令会将输入的内容同时写入到指定的文件（这里是 `/etc/docker/daemon.json`）和标准输出（通常是屏幕）。
>
> - `<< 'EOF'` 和 `EOF`：这是 shell 中的 "here document" 技术，它允许你直接在命令行中输入多行文本。这个文本会被当作前面命令的输入。在 `<< 'EOF'` 和 `EOF` 之间的所有内容都会被当作输入的内容。
>
> - `tee` 命令默认会覆盖目标文件的内容。如果希望将内容追加到文件的末尾，可以使用 `-a` 或 `--append`
>
>   ~~~sh
>   tee -a /etc/docker/daemon.json << 'EOF'
>   {
>   ...
>   } 
>   EOF
>   ~~~

- 重启docker

~~~sh
systemctl daemon-reload
systemctl restart docker
systemctl status docker
~~~

## 安装rancher

~~~sh
~~~

