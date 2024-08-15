# 二进制安装 vs kubeadm安装

- kubeadm是官方提供的开源工具，用于快速搭建kubernetes集群，相当于用程序脚本帮我们装好了集群，属于自动部署，简化部署操作，自动部署屏蔽了很多细节，使得对各个模块感知很少，如果对k8s架构组件理解不深的话，遇到问题比较难排查。Kubeadm初始化k8s，所有的组件都是以pod形式运行的，具备故障自恢复能力。kubeadm适合需要经常部署k8s，或者对自动化要求比较高的场景下使用。

- 二进制：在官网下载相关组件的二进制包，如果手动安装，对kubernetes理解也会更全面。 

- Kubeadm和二进制都适合生产环境，在生产环境运行都很稳定，具体如何选择，可以根据实际项目进行评估。

# 二进制安装多master高可用集群1.20.7

## 架构图

![image-20240226215935013](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402262159081.png)

## 实验机器规划

- 操作系统：centos7.9

- 配置：4Gib内存/4vCPU/50G硬盘

  > 如果VM是从20G磁盘扩容到了50G，那么在VMWare上加完磁盘容量后需要扩容文件系统。由于使用的镜像的根分区是用的LVM，所以需要LVM扩容。参考文档：https://blog.csdn.net/yangfenggh/article/details/130475248

- 网络：NAT

- 开启虚拟机的虚拟化

| K8S集群角色 | Ip            | 主机名     | 安装的组件                                                   |
| ----------- | ------------- | ---------- | ------------------------------------------------------------ |
| 控制节点    | 172.16.183.76 | binmaster1 | apiserver、controller-manager、scheduler、etcd、docker、keepalived、nginx |
| 控制节点    | 172.16.183.77 | binmaster2 | apiserver、controller-manager、scheduler、etcd、docker、keepalived、nginx |
| 控制节点    | 172.16.183.78 | binmaster3 | apiserver、controller-manager、scheduler、etcd、docker       |
| 工作节点    | 172.16.183.79 | binnode1   | kubelet、kube-proxy、docker、calico、coredns                 |
| Vip         | 172.16.183.75 |            |                                                              |

## 实验环境准备

### 设置静态IP

~~~sh
vi /etc/sysconfig/network-scripts/ifcfg-ens33

TYPE=Ethernet
PROXY_METHOD=none
BROWSER_ONLY=no
BOOTPROTO=static #static表示静态ip地址
IPADDR=172.16.183.76 #ip地址，需要跟自己电脑所在网段一致
NETMASK=255.255.255.0
GATEWAY=172.16.183.2
DNS1=172.16.183.2
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

> - VMware上由模板机复制过来的VM，要删掉网卡配置的UUID字段

### 修改主机名

~~~sh
hostnamectl set-hostname binmaster1 && bash #binmaster2 binmaster3 binnode1
~~~

### 配置hosts文件

~~~sh
tee -a /etc/hosts << 'EOF'
172.16.183.76   binmaster1
172.16.183.77   binmaster2
172.16.183.78   binmaster3
172.16.183.79   binnode1
EOF
~~~

### 配置ssh免密登录

~~~sh
ssh-keygen -t rsa
ssh-copy-id -i .ssh/id_rsa.pub binmaster1
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
yum install openssh-clients -y
#备份基础repo源
mkdir /root/repo.bak/
mv /etc/yum.repos.d/* /root/repo.bak/
#下载阿里云的repo源
#把CentOS-Base.repo文件上传到master1主机的/etc/yum.repos.d/目录下
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
yum install -y device-mapper-persistent-data lvm2 wget net-tools nfs-utils lrzsz gcc gcc-c++ make cmake libxml2-devel openssl-devel curl curl-devel unzip sudo ntp libaio-devel wget vim ncurses-devel autoconf automake zlib-devel python-devel epel-release openssh-server socat conntrack telnet ipvsadm openssh-clients
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

### 配置ectd工作目录

~~~sh
#3台master上
mkdir -p /etc/etcd/ssl
~~~

### 安装签发证书工具cfssl

> cfssl 是 CloudFlare 开源的一款PKI/TLS工具。 CFSSL 包含一个命令行工具(cfssl, cfssljson)用于签名，可以生成CA，签发证书
> 使用cfssl需要两个文件：
> 1、创建自己的内部服务使用的CA认证中心
> 2、运行认证中心需要一个CA证书和相应的私钥。后者是极其敏感的数据。任何知道私钥的人都可以充当CA颁发证书。因此，私钥的保护至关重要

~~~sh
#在master1上
mkdir /data/work -p
cd /data/work/
#cfssl-certinfo_linux-amd64 、cfssljson_linux-amd64 、cfssl_linux-amd64上传到/data/work/目录下
ls
cfssl-certinfo_linux-amd64  cfssljson_linux-amd64  cfssl_linux-amd64
#把文件变成可执行权限
chmod +x *
mv cfssl_linux-amd64 /usr/local/bin/cfssl
mv cfssljson_linux-amd64 /usr/local/bin/cfssljson
mv cfssl-certinfo_linux-amd64 /usr/local/bin/cfssl-certinfo
~~~

### 配置CA证书请求

~~~sh
#生成ca证书请求文件,mater1上
#CA证书请求文件，也被称为CSR（Certificate Signing Request），是一种由服务器管理员或者网站所有者生成的特殊文件。它包含了公钥以及一些附加信息，如组织名称、常用名称（例如网站域名）等。这个文件会被发送给证书颁发机构（CA，Certificate Authority），CA会基于这个请求生成一个数字证书。
cd /data/work/
tee -a ca-csr.json << 'EOF'
{
  "CN": "kubernetes",
  "key": {
      "algo": "rsa",
      "size": 2048
  },
  "names": [
    {
      "C": "CN",
      "ST": "Hubei",
      "L": "Wuhan",
      "O": "k8s",
      "OU": "system"
    }
  ],
  "ca": {
          "expiry": "87600h"
  }
}
EOF
~~~

~~~sh
cfssl gencert -initca ca-csr.json  | cfssljson -bare ca
~~~

> 注： 
>
> - CN：Common Name（公用名称），kube-apiserver 从证书中提取该字段作为请求的用户名 (User Name)；浏览器使用该字段验证网站是否合法；对于 SSL 证书，一般为网站域名；而对于代码签名证书则为申请单位名称；而对于客户端证书则为证书申请者的姓名。
>
> - O：Organization（单位名称），kube-apiserver 从证书中提取该字段作为请求用户所属的组 (Group)；对于 SSL 证书，一般为网站域名；而对于代码签名证书则为申请单位名称；而对于客户端单位证书则为证书申请者所在单位名称。
>
> - L 字段：所在城市
>
> - S 字段：所在省份
>
> - C 字段：只能是国家字母缩写，如中国：CN

> - `cfssljson`是CloudFlare的PKI(TLS/SSL)工具包cfssl的一部分。这个命令主要用于处理cfssl生成的JSON格式的输出。
>
> - `cfssljson`的主要功能是从cfssl的输出中提取和写入证书，私钥和证书链。这对于自动化处理证书生成和部署非常有用。
>
> - 例如，你可以使用cfssl和cfssljson生成一个新的自签名证书：
>
> ```sh
> cfssl gencert -initca ca-csr.json | cfssljson -bare ca
> ```
>
> - 在这个例子中，`cfssl gencert -initca ca-csr.json`生成一个新的自签名证书和私钥，然后通过管道传递给`cfssljson -bare ca`，它从JSON输出中提取证书和私钥，并将它们分别写入`ca.pem`和`ca-key.pem`文件。后面所有证书都是由ca.pem这个证书来颁发的

### 生成CA证书文件

~~~sh
tee -a ca-config.json << 'EOF'
{
  "signing": {
      "default": {
          "expiry": "87600h"
        },
      "profiles": {
          "kubernetes": {
              "usages": [
                  "signing",
                  "key encipherment",
                  "server auth",
                  "client auth"
              ],
              "expiry": "87600h"
          }
      }
  }
}
EOF
~~~

### 生成etcd证书

~~~sh
#配置etcd证书请求，hosts的ip变成自己etcd所在节点的ip。可以预先写进去一些冗余的IP，方便后面扩容。 
tee -a etcd-csr.json << 'EOF'
{
  "CN": "etcd",
  "hosts": [
    "127.0.0.1",
    "172.16.183.76",
    "172.16.183.77",
    "172.16.183.78",
    "172.16.183.79",
    "172.16.183.75"
  ],
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [{
    "C": "CN",
    "ST": "Hubei",
    "L": "Wuhan",
    "O": "k8s",
    "OU": "system"
  }]
} 
EOF
#上述文件hosts字段中IP为所有etcd节点的集群内部通信IP，可以预留几个，做扩容用? 
cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=kubernetes etcd-csr.json | cfssljson  -bare etcd
ls etcd*.pem
#etcd-key.pem  etcd.pem
~~~

> 在生成证书过程中需要有四类文件
>
> 1. *.csr - 证书请求文件,base64格式，有-----BEGIN CERTIFICATE REQUEST-----标识
> 2. *csr.json - 证书请求文件，是上面格式的再封装，便于传给cfssl，json格式，大括号开始
> 3. *-key.pem - 私匙文件，base64格式，有-----BEGIN RSA PRIVATE KEY-----标识
> 4. *.pem - 证书文件，base64格式，可以用cfssl certinfo -cert 文件名查看有效期，有-----BEGIN CERTIFICATE-----标识

### 部署etcd集群

#### 上传镜像

- 上传etcd-v3.4.13-linux-amd64.tar.gz上传到master1的/data/work目录下

~~~sh
tar -xf etcd-v3.4.13-linux-amd64.tar.gz
cp -p etcd-v3.4.13-linux-amd64/etcd* /usr/local/bin/
#拷贝到另外两台
scp -r  etcd-v3.4.13-linux-amd64/etcd* binmaster2:/usr/local/bin/
scp -r  etcd-v3.4.13-linux-amd64/etcd* binmaster3:/usr/local/bin/
~~~

#### 创建配置文件

~~~sh
tee -a etcd.conf << 'EOF' 
#[Member]
ETCD_NAME="etcd1"
ETCD_DATA_DIR="/var/lib/etcd/default.etcd"
ETCD_LISTEN_PEER_URLS="https://172.16.183.76:2380"
ETCD_LISTEN_CLIENT_URLS="https://172.16.183.76:2379,http://127.0.0.1:2379"
#[Clustering]
ETCD_INITIAL_ADVERTISE_PEER_URLS="https://172.16.183.76:2380"
ETCD_ADVERTISE_CLIENT_URLS="https://172.16.183.76:2379"
ETCD_INITIAL_CLUSTER="etcd1=https://172.16.183.76:2380,etcd2=https://172.16.183.77:2380,etcd3=https://172.16.183.78:2380"
ETCD_INITIAL_CLUSTER_TOKEN="etcd-cluster"
ETCD_INITIAL_CLUSTER_STATE="new"
EOF
~~~

> ETCD_NAME：节点名称，集群中唯一 
>
> ETCD_DATA_DIR：数据目录 
>
> ETCD_LISTEN_PEER_URLS：集群通信监听地址 
>
> ETCD_LISTEN_CLIENT_URLS：客户端访问监听地址 
>
> ETCD_INITIAL_ADVERTISE_PEER_URLS：集群通告地址 
>
> ETCD_ADVERTISE_CLIENT_URLS：客户端通告地址 
>
> ETCD_INITIAL_CLUSTER：集群节点地址
>
> ETCD_INITIAL_CLUSTER_TOKEN：集群Token
>
> ETCD_INITIAL_CLUSTER_STATE：加入集群的当前状态，new是新集群，existing表示加入已有集群

#### 创建启动服务文件

~~~sh
#master1上
tee -a etcd.service << 'EOF'
[Unit]
Description=Etcd Server
After=network.target
After=network-online.target
Wants=network-online.target
 
[Service]
Type=notify
EnvironmentFile=-/etc/etcd/etcd.conf
WorkingDirectory=/var/lib/etcd/
ExecStart=/usr/local/bin/etcd \
  --cert-file=/etc/etcd/ssl/etcd.pem \
  --key-file=/etc/etcd/ssl/etcd-key.pem \
  --trusted-ca-file=/etc/etcd/ssl/ca.pem \
  --peer-cert-file=/etc/etcd/ssl/etcd.pem \
  --peer-key-file=/etc/etcd/ssl/etcd-key.pem \
  --peer-trusted-ca-file=/etc/etcd/ssl/ca.pem \
  --peer-client-cert-auth \
  --client-cert-auth
Restart=on-failure
RestartSec=5
LimitNOFILE=65536
 
[Install]
WantedBy=multi-user.target
EOF
~~~

~~~sh
#master1上，把前面生成的证书文件转移到/etc/etcd/ssl/
cd /data/work
cp ca*.pem /etc/etcd/ssl/
cp etcd*.pem /etc/etcd/ssl/
cp etcd.conf /etc/etcd/
cp etcd.service /usr/lib/systemd/system/ # 这是系统启动脚本的目录
for i in binmaster2 binmaster3;do rsync -vaz etcd.conf $i:/etc/etcd/;done
for i in binmaster2 binmaster3;do rsync -vaz etcd*.pem ca*.pem $i:/etc/etcd/ssl/;done
for i in binmaster2 binmaster3;do rsync -vaz etcd.service $i:/usr/lib/systemd/system/;done
~~~

#### 启动etcd集群

~~~sh
#3台master上，创建etcd的数据目录
mkdir -p /var/lib/etcd/default.etcd
~~~

~~~sh
#master2上
tee -a /etc/etcd/etcd.conf << 'EOF' 
#[Member]
ETCD_NAME="etcd2"
ETCD_DATA_DIR="/var/lib/etcd/default.etcd"
ETCD_LISTEN_PEER_URLS="https://172.16.183.77:2380"
ETCD_LISTEN_CLIENT_URLS="https://172.16.183.77:2379,http://127.0.0.1:2379"
#[Clustering]
ETCD_INITIAL_ADVERTISE_PEER_URLS="https://172.16.183.77:2380"
ETCD_ADVERTISE_CLIENT_URLS="https://172.16.183.77:2379"
ETCD_INITIAL_CLUSTER="etcd1=https://172.16.183.76:2380,etcd2=https://172.16.183.77:2380,etcd3=https://172.16.183.78:2380"
ETCD_INITIAL_CLUSTER_TOKEN="etcd-cluster"
ETCD_INITIAL_CLUSTER_STATE="new"
EOF
~~~

~~~sh
#master3上
tee -a /etc/etcd/etcd.conf << 'EOF'
#[Member]
ETCD_NAME="etcd3"
ETCD_DATA_DIR="/var/lib/etcd/default.etcd"
ETCD_LISTEN_PEER_URLS="https://172.16.183.78:2380"
ETCD_LISTEN_CLIENT_URLS="https://172.16.183.78:2379,http://127.0.0.1:2379"
#[Clustering]
ETCD_INITIAL_ADVERTISE_PEER_URLS="https://172.16.183.78:2380"
ETCD_ADVERTISE_CLIENT_URLS="https://172.16.183.78:2379"
ETCD_INITIAL_CLUSTER="etcd1=https://172.16.183.76:2380,etcd2=https://172.16.183.77:2380,etcd3=https://172.16.183.78:2380"
ETCD_INITIAL_CLUSTER_TOKEN="etcd-cluster"
ETCD_INITIAL_CLUSTER_STATE="new"
EOF
~~~

~~~sh
#master1\2\3上
systemctl daemon-reload
systemctl enable etcd.service
systemctl start etcd.service
#启动etcd的时候，先启动master1的etcd服务，会一直卡住在启动的状态，然后接着再启动master2的etcd，这样master1这个节点etcd才会正常起来
#3台上检查etcd状态
systemctl status etcd
~~~

### 查看etcd集群健康状态

~~~sh
#master1上
ETCDCTL_API=3 #设置etcdctl api版本为3
echo $ETCDCTL_API
/usr/local/bin/etcdctl --write-out=table --cacert=/etc/etcd/ssl/ca.pem --cert=/etc/etcd/ssl/etcd.pem --key=/etc/etcd/ssl/etcd-key.pem --endpoints=https://172.16.183.76:2379,https://172.16.183.77:2379,https://172.16.183.78:2379  endpoint health
~~~

## 安装k8s组件

- Kubernetes API的请求从发起到其持久化⼊库的流程如下：
  1. 认证阶段（Authentication）
     - 判断⽤户是否为能够访问集群的合法⽤户。
     - apiserver⽬前提供了9种认证机制。每⼀种认证机制被实例化后会成为认证器（Authenticator），每⼀个认证器都被封装在http.Handler请求处理函数中，它们接收组件或客户端的请求并认证请求。
     - 假设所有的认证器都被启⽤，当客户端发送请求到kube-apiserver服务，该请求会进⼊Authentication Handler函数（处理认证相关的Handler函数）。在Authentication Handler函数中，会遍历已启⽤的认证器列表，尝试执⾏每个认证器，当有⼀个认证器返回true时，则认证成功，否则继续尝试下⼀个认证器；如果⽤户是个⾮法⽤户，那apiserver会返回⼀个401的状态码，并终⽌该请求。
  2. clientCA认证
     - X509认证是Kubernetes组件间默认使⽤的认证⽅式，同时也是kubectl客户端对应的kube-config中经常使⽤到的访问凭证。它是⼀个⽐较安全的⽅式。
     - ⾸先访问者会使⽤由集群CA签发的，或是添加在apiserver配置中的授信CA签发的客户端证书去访问apiserver。apiserver在接收到请求后，会进⾏TLS的握⼿流程。
     - 除了验证证书的合法性，apiserver还会校验客户端证书的请求源地址等信息，开启双向认证。

### 下载安装包

- 二进制包所在的github地址如下：https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG/，可以按照版本下载二进制包。控制节点组件，找到Server Binaries，下载amd64版本的。server binaries二进制包里面就包含了：controller-manager，apiserver，scheduler等控制平面组件。其实也包含了工作节点需要的kubelet和kubeproxy
- 这里下载的是1.20.7版本

~~~sh
#把kubernetes-server-linux-amd64.tar.gz上传到master1上的/data/work目录下:
#master1上
cd /data/work
tar zxvf kubernetes-server-linux-amd64.tar.gz
cd kubernetes/server/bin/
cp kube-apiserver kube-controller-manager kube-scheduler kubectl /usr/local/bin/
rsync -vaz kube-apiserver kube-controller-manager kube-scheduler kubectl binmaster2:/usr/local/bin/
rsync -vaz kube-apiserver kube-controller-manager kube-scheduler kubectl binmaster3:/usr/local/bin/
#kubelet kubeproxy放到工作节点
scp kubelet kube-proxy binnode1:/usr/local/bin/
cd /data/work/
mkdir -p /etc/kubernetes/ssl/
mkdir -p /var/log/kubernetes
~~~

### 部署apiserver组件

#### bootstrapping机制

- 启动TLS Bootstrapping 机制
  - Master apiserver启用TLS认证后，每个节点的 kubelet 组件都要使用由 apiserver 使用的 CA 签发的有效证书才能与 apiserver 通讯，当Node节点很多时，这种客户端证书颁发需要大量工作，同样也会增加集群扩展复杂度。
  - 为了简化流程，Kubernetes引入了TLS bootstraping机制来自动颁发客户端证书，kubelet会以一个低权限用户自动向apiserver申请证书，kubelet的证书由apiserver动态签署。

  - Bootstrap 是很多系统中都存在的程序，比如 Linux 的bootstrap，bootstrap 一般都是作为预先配置在开启或者系统启动的时候加载，这可以用来生成一个指定环境。Kubernetes 的 kubelet 在启动时同样可以加载一个这样的配置文件，这个文件的内容类似如下形式：

~~~yaml
apiVersion: v1
clusters: null
contexts:
- context:
    cluster: kubernetes
    user: kubelet-bootstrap
  name: default
current-context: default
kind: Config
preferences: {}
users:
- name: kubelet-bootstrap
  user: {}
~~~

- Bootstrap具体引导过程
  - TLS 作用 
    TLS 的作用就是对通讯加密，防止中间人窃听；同时如果证书不信任的话根本就无法与 apiserver 建立连接，更不用提有没有权限向apiserver请求指定内容。
  - RBAC 作用 
    当 TLS 解决了通讯问题后，那么权限问题就应由 RBAC 解决；RBAC 中规定了一个用户或者用户组(subject)具有请求哪些 api 的权限；在配合 TLS 加密的时候，实际上 apiserver 读取客户端证书的 `CN` 字段作为用户名，读取 `O` 字段作为用户组.
  - 以上说明：第一，想要与 apiserver 通讯就必须采用由 apiserver CA 签发的证书，这样才能形成信任关系，建立 TLS 连接；第二，可以**通过证书的 CN、O 字段来提供 RBAC 所需的用户与用户组**。

- kubelet 首次启动流程 

  - TLS bootstrapping 功能是让 kubelet 组件去 apiserver 申请证书，然后用于连接 apiserver；那么第一次启动时没有证书如何连接 apiserver ?

  - 在apiserver 配置中指定了一个 `token.csv` 文件，该文件中是一个预设的用户配置；
    - 同时该用户的Token和apiserver CA签发的用户被写入了kubelet的`bootstrap.kubeconfig` 配置文件中；
    - 这样在首次请求时，kubelet 使用 `bootstrap.kubeconfig` 中被apiserver CA信任的用户与apiserver连接，使用 `bootstrap.kubeconfig` 中的用户 Token 来向 apiserver 声明自己的 RBAC 授权身份.

  - token.csv格式:

    `3940fd7fbb391d1b4d861ad17a1f0613,kubelet-bootstrap,10001,"system:kubelet-bootstrap"`

  - 首次启动时，可能与遇到 kubelet 报 401 无权访问 apiserver 的错误；这是因为在默认情况下，kubelet 通过 `bootstrap.kubeconfig` 中的预设用户 Token 声明了自己的身份，然后创建 CSR 请求。但是不要忘记这个用户在我们不处理的情况下他没任何权限的，包括创建CSR请求的权限也没有。所以需要创建一个 `ClusterRoleBinding`，将预设用户 `kubelet-bootstrap` 与内置的 `ClusterRole system:node-bootstrapper` 绑定到一起，使其能够发起 CSR 请求。

#### 创建token.csv文件

~~~sh
#master1上
cat > token.csv << EOF
$(head -c 16 /dev/urandom | od -An -t x | tr -d ' '),kubelet-bootstrap,10001,"system:kubelet-bootstrap"
EOF
#格式：token，用户名，UID，用户组
~~~

#### 创建csr请求文件

- 集群中所有系统组件与apiserver通讯⽤到的证书，其实都是由集群根CA签发的

- 注：如果 hosts 字段不为空则需要指定授权使用该证书的 IP 或域名列表。由于该证书后续被 kubernetes master 集群使用，需要将master节点的IP都填上，同时还需要填写 service 网络的首个IP。(一般是 kube-apiserver 指定的 service-cluster-ip-range 网段的第一个IP，如 10.255.0.1)

~~~sh
#master1上
tee -a kube-apiserver-csr.json << 'EOF'
{
  "CN": "kubernetes",
  "hosts": [
    "127.0.0.1",
    "172.16.183.76",
    "172.16.183.77",
    "172.16.183.78",
    "172.16.183.79",
    "172.16.183.75",
    "10.255.0.1",
    "kubernetes",
    "kubernetes.default",
    "kubernetes.default.svc",
    "kubernetes.default.svc.cluster",
    "kubernetes.default.svc.cluster.local"
  ],
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "C": "CN",
      "ST": "Hubei",
      "L": "Wuhan",
      "O": "k8s",
      "OU": "system"
    }
  ]
}
EOF
~~~

#### 生成证书

~~~sh
#master1上
cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=kubernetes kube-apiserver-csr.json | cfssljson -bare kube-apiserver
~~~

#### 创建apiserver的配置文件

~~~sh
#master1上
tee -a kube-apiserver.conf << 'EOF'
KUBE_APISERVER_OPTS="--enable-admission-plugins=NamespaceLifecycle,NodeRestriction,LimitRanger,ServiceAccount,DefaultStorageClass,ResourceQuota \
  --anonymous-auth=false \
  --bind-address=172.16.183.76 \
  --secure-port=6443 \
  --advertise-address=172.16.183.76 \
  --insecure-port=0 \
  --authorization-mode=Node,RBAC \
  --runtime-config=api/all=true \
  --enable-bootstrap-token-auth \
  --service-cluster-ip-range=10.255.0.0/16 \
  --token-auth-file=/etc/kubernetes/token.csv \
  --service-node-port-range=30000-50000 \
  --tls-cert-file=/etc/kubernetes/ssl/kube-apiserver.pem  \
  --tls-private-key-file=/etc/kubernetes/ssl/kube-apiserver-key.pem \
  --client-ca-file=/etc/kubernetes/ssl/ca.pem \
  --kubelet-client-certificate=/etc/kubernetes/ssl/kube-apiserver.pem \
  --kubelet-client-key=/etc/kubernetes/ssl/kube-apiserver-key.pem \
  --service-account-key-file=/etc/kubernetes/ssl/ca-key.pem \
  --service-account-signing-key-file=/etc/kubernetes/ssl/ca-key.pem  \
  --service-account-issuer=https://kubernetes.default.svc.cluster.local \
  --etcd-cafile=/etc/etcd/ssl/ca.pem \
  --etcd-certfile=/etc/etcd/ssl/etcd.pem \
  --etcd-keyfile=/etc/etcd/ssl/etcd-key.pem \
  --etcd-servers=https://172.16.183.76:2379,https://172.16.183.77:2379,https://172.16.183.78:2379 \
  --enable-swagger-ui=true \
  --allow-privileged=true \
  --apiserver-count=3 \
  --audit-log-maxage=30 \
  --audit-log-maxbackup=3 \
  --audit-log-maxsize=100 \
  --audit-log-path=/var/log/kube-apiserver-audit.log \
  --event-ttl=1h \
  --alsologtostderr=true \
  --logtostderr=false \
  --log-dir=/var/log/kubernetes \
  --v=4"
EOF
~~~

> 注： 
>
> --logtostderr：启用日志 
>
> --v：日志等级 
>
> --log-dir：日志目录 
>
> --etcd-servers：etcd集群地址 
>
> --bind-address：监听地址 
>
> --secure-port：https安全端口 
>
> --advertise-address：集群通告地址 
>
> --allow-privileged：启用授权 
>
> --service-cluster-ip-range：Service虚拟IP地址段 
>
> --enable-admission-plugins：准入控制模块 
>
> --authorization-mode：认证授权，启用RBAC授权和节点自管理 
>
> --enable-bootstrap-token-auth：启用TLS bootstrap机制 
>
> --token-auth-file：bootstrap token文件 
>
> --service-node-port-range：Service nodeport类型默认分配端口范围 
>
> --kubelet-client-xxx：apiserver访问kubelet客户端证书 
>
> --tls-xxx-file：apiserver https证书 
>
> --etcd-xxxfile：连接Etcd集群证书 –
>
> -audit-log-xxx：审计日志

#### 创建服务启动文件

~~~sh
#master1上
tee -a kube-apiserver.service << 'EOF'
[Unit]
Description=Kubernetes API Server
Documentation=https://github.com/kubernetes/kubernetes
After=etcd.service
Wants=etcd.service
 
[Service]
EnvironmentFile=-/etc/kubernetes/kube-apiserver.conf
ExecStart=/usr/local/bin/kube-apiserver $KUBE_APISERVER_OPTS
Restart=on-failure
RestartSec=5
Type=notify
LimitNOFILE=65536
 
[Install]
WantedBy=multi-user.target
EOF
~~~

~~~sh
cp ca*.pem /etc/kubernetes/ssl
cp kube-apiserver*.pem /etc/kubernetes/ssl/
cp token.csv /etc/kubernetes/
cp kube-apiserver.conf /etc/kubernetes/
cp kube-apiserver.service /usr/lib/systemd/system/
rsync -vaz token.csv binmaster2:/etc/kubernetes/
rsync -vaz token.csv binmaster3:/etc/kubernetes/
rsync -vaz kube-apiserver*.pem binmaster2:/etc/kubernetes/ssl/
rsync -vaz kube-apiserver*.pem binmaster3:/etc/kubernetes/ssl/
rsync -vaz ca*.pem binmaster2:/etc/kubernetes/ssl/
rsync -vaz ca*.pem binmaster3:/etc/kubernetes/ssl/
rsync -vaz kube-apiserver.conf binmaster2:/etc/kubernetes/
rsync -vaz kube-apiserver.conf binmaster3:/etc/kubernetes/
rsync -vaz kube-apiserver.service binmaster2:/usr/lib/systemd/system/
rsync -vaz kube-apiserver.service binmaster3:/usr/lib/systemd/system/
~~~

~~~sh
#修改master2和master3上的kube-apiserver.conf文件的IP地址(--bind-address，--advertise-address)
#3台master上执行
systemctl daemon-reload
systemctl enable kube-apiserver
systemctl start kube-apiserver
systemctl status kube-apiserver
curl --insecure https://172.16.183.76:6443/
#上面看到401，这个是正常的的状态，还没认证
~~~

### 部署kubectl组件

#### 配置kubeconfig文件

- Kubectl操作资源的时候，怎么知道连接到哪个集群？需要一个文件/etc/kubernetes/admin.conf，kubectl会根据这个文件的配置，去访问k8s资源。/etc/kubernetes/admin.conf文件记录了访问的k8s集群，和用到的证书。

~~~sh
#可以设置一个环境变量KUBECONFIG，这样操作kubectl，就会自动加载KUBECONFIG来操作要管理哪个集群的k8s资源了
#直接命令行定义环境变量，只对当前的shell有效
export KUBECONFIG=/etc/kubernetes/admin.conf
#编辑/etc/profile，对于所有用户，永久生效（也可以在用户家目录下的.bash_profile增加环境变量，对当前用户永久生效）
tee -a /etc/profile << 'EOF'
export KUBECONFIG=/etc/kubernetes/admin.conf
EOF
source /etc/profile
#也可以按照下面方法，这个是在kubeadm初始化k8s的时候会告诉我们要用的方法
cp /etc/kubernetes/admin.conf /root/.kube/config 
#如果设置了KUBECONFIG，那就会先找到KUBECONFIG去操作k8s，如果没有KUBECONFIG变量，那就会使用/root/.kube/config文件决定管理哪个k8s集群的资源。
~~~

==二进制安装这里没有admin.conf这个文件，直接就用/root/.kube/config，所以不用做上面的步骤==

#### 创建csr请求文件

~~~sh
#master1上
cd /data/work
#创建一个集群管理员的user，叫admin，组是system:master，这个组已经预先内置了cluster-admin的权限。
tee -a admin-csr.json << 'EOF' 
{
  "CN": "admin",
  "hosts": [],
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "C": "CN",
      "ST": "Hubei",
      "L": "Wuhan",
      "O": "system:masters",             
      "OU": "system"
    }
  ]
}
EOF
~~~

> 说明：
>
> - 后续 kube-apiserver 使用 RBAC 对客户端(如 kubelet、kube-proxy、Pod)请求进行授权； 
>
> - kube-apiserver 预定义了一些 RBAC 使用的 RoleBindings，如 cluster-admin 将 Group system:masters 与 Role cluster-admin 绑定，该 Role 授予了调用apiserver的所有API的权限； 
>
> - O指定该证书的 Group 为 system:masters，kubelet 使用该证书访问apiserver时，由于证书被 CA 签名，所以认证通过；同时由于证书用户组为经过预授权的 system:masters，所以被授予访问所有 API 的权限；

> 注： 
>
> - 这个admin证书是将来生成管理员用的kube config 配置文件用的，现在我们一般建议使用RBAC来对kubernetes进行角色权限控制，kubernetes将证书中的CN字段作为User， O 字段作为 Group； "O": "system:masters", 必须是system:masters，否则后面kubectl create clusterrolebinding报错。

#### 生成证书

~~~sh
#master1上
cd /data/work
#用apiserver的证书颁发机构，给kubectl客户端签发了一个admin客户端证书
cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=kubernetes admin-csr.json | cfssljson -bare admin
cp admin*.pem /etc/kubernetes/ssl/
~~~

#### 配置安全上下文

- 创建kubeconfig配置文件

~~~sh
#kubeconfig 为 kubectl 的配置文件，包含访问 apiserver 的所有信息，如 apiserver 地址、CA 证书和自身使用的证书（这里如果报错找不到kubeconfig路径，请手动复制到相应路径下，没有则忽略）
#1.设置集群参数
cd /data/work
kubectl config set-cluster kubernetes --certificate-authority=ca.pem --embed-certs=true --server=https://172.16.183.76:6443 --kubeconfig=kube.config #这一步会生成kube.config文件，就是后面的/kube/config文件。
##查看kube.config内容
vim kube.config
#2.设置客户端认证参数
kubectl config set-credentials admin --client-certificate=admin.pem --client-key=admin-key.pem --embed-certs=true --kubeconfig=kube.config
#3.设置上下文参数
kubectl config set-context kubernetes --cluster=kubernetes --user=admin --kubeconfig=kube.config
#4.设置当前上下文
kubectl config use-context kubernetes --kubeconfig=kube.config
mkdir ~/.kube -p
cp kube.config ~/.kube/config
#5.授权kubernetes证书访问kubelet api权限，目的是可以创建资源。#注意这里的用户是kubernetes，这是前面apiserver的ca-csr文件里面定义的CN=kubernetes，代表给apiserver赋予api的权限
kubectl create clusterrolebinding kube-apiserver:kubelet-apis --clusterrole=system:kubelet-api-admin --user kubernetes

##查看集群组件状态
kubectl cluster-info
kubectl get componentstatuses
kubectl get all --all-namespaces
~~~

```sh
#同步kubectl文件到其他节点
##master2和3上
mkdir /root/.kube/ -p
##master1上
rsync -vaz /root/.kube/config binmaster2:/root/.kube/
rsync -vaz /root/.kube/config binmaster3:/root/.kube/
#配置kubectl子命令补全
##master1上
yum install -y bash-completion
source /usr/share/bash-completion/bash_completion
source <(kubectl completion bash)
kubectl completion bash > ~/.kube/completion.bash.inc
source '/root/.kube/completion.bash.inc'
source $HOME/.bash_profile
```

### 部署kube-controller-manager组件

#### 创建csr请求文件

```sh
#master1上
cd /data/work
tee -a kube-controller-manager-csr.json << 'EOF' 
{
    "CN": "system:kube-controller-manager",
    "key": {
        "algo": "rsa",
        "size": 2048
    },
    "hosts": [
      "127.0.0.1",
      "172.16.183.76",
      "172.16.183.77",
      "172.16.183.78",
      "172.16.183.79"
    ],
    "names": [
      {
        "C": "CN",
        "ST": "Hubei",
        "L": "Wuhan",
        "O": "system:kube-controller-manager",
        "OU": "system"
      }
    ]
}
EOF
```

> 注：hosts 列表包含所有 kube-controller-manager 节点 IP； CN 为 system:kube-controller-manager、O 为 system:kube-controller-manager，kubernetes 内置的 ClusterRoleBindings system:kube-controller-manager 赋予 kube-controller-manager 工作所需的权限

#### 生成证书

~~~sh
#master1上
cd /data/work
cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=kubernetes kube-controller-manager-csr.json | cfssljson -bare kube-controller-manager
~~~

#### 创建kube-controller-manager的kubeconfig

~~~sh
#master1上
cd /data/work
#1.设置集群参数，指定apiserver信任的
kubectl config set-cluster kubernetes --certificate-authority=ca.pem --embed-certs=true --server=https://172.16.183.76:6443 --kubeconfig=kube-controller-manager.kubeconfig
#2.设置客户端认证参数,指定客户端使用的证书
kubectl config set-credentials system:kube-controller-manager --client-certificate=kube-controller-manager.pem --client-key=kube-controller-manager-key.pem --embed-certs=true --kubeconfig=kube-controller-manager.kubeconfig
#3.设置上下文参数
kubectl config set-context system:kube-controller-manager --cluster=kubernetes --user=system:kube-controller-manager --kubeconfig=kube-controller-manager.kubeconfig
#4.设置当前上下文
kubectl config use-context system:kube-controller-manager --kubeconfig=kube-controller-manager.kubeconfig
~~~

#### 创建配置文件kube-controller-manager.conf

~~~sh
#master1上
cd /data/work
tee -a kube-controller-manager.conf <<'EOF'
KUBE_CONTROLLER_MANAGER_OPTS="--port=0 \
  --secure-port=10252 \
  --bind-address=127.0.0.1 \
  --kubeconfig=/etc/kubernetes/kube-controller-manager.kubeconfig \
  --service-cluster-ip-range=10.255.0.0/16 \
  --cluster-name=kubernetes \
  --cluster-signing-cert-file=/etc/kubernetes/ssl/ca.pem \
  --cluster-signing-key-file=/etc/kubernetes/ssl/ca-key.pem \
  --allocate-node-cidrs=true \
  --cluster-cidr=10.0.0.0/16 \
  --experimental-cluster-signing-duration=87600h \
  --root-ca-file=/etc/kubernetes/ssl/ca.pem \
  --service-account-private-key-file=/etc/kubernetes/ssl/ca-key.pem \
  --leader-elect=true \
  --feature-gates=RotateKubeletServerCertificate=true \
  --controllers=*,bootstrapsigner,tokencleaner \
  --horizontal-pod-autoscaler-use-rest-clients=true \
  --horizontal-pod-autoscaler-sync-period=10s \
  --tls-cert-file=/etc/kubernetes/ssl/kube-controller-manager.pem \
  --tls-private-key-file=/etc/kubernetes/ssl/kube-controller-manager-key.pem \
  --use-service-account-credentials=true \
  --alsologtostderr=true \
  --logtostderr=false \
  --log-dir=/var/log/kubernetes \
  --v=2"
EOF
#这里的--bind-address=127.0.0.1 ，绑定了本机IP而非网卡IP，官方在1.20之后是这样设计的，为了避免物理机上curl能访问到，更安全。
~~~

#### 创建启动文件

~~~sh
#master1上
cd /data/work
tee -a kube-controller-manager.service << 'EOF' 
[Unit]
Description=Kubernetes Controller Manager
Documentation=https://github.com/kubernetes/kubernetes
[Service]
EnvironmentFile=-/etc/kubernetes/kube-controller-manager.conf
ExecStart=/usr/local/bin/kube-controller-manager $KUBE_CONTROLLER_MANAGER_OPTS
Restart=on-failure
RestartSec=5
[Install]
WantedBy=multi-user.target
EOF
~~~

#### 启动服务

~~~sh
#master1上
cd /data/work
cp kube-controller-manager*.pem /etc/kubernetes/ssl/
cp kube-controller-manager.kubeconfig /etc/kubernetes/
cp kube-controller-manager.conf /etc/kubernetes/
cp kube-controller-manager.service /usr/lib/systemd/system/
rsync -vaz kube-controller-manager*.pem binmaster2:/etc/kubernetes/ssl/
rsync -vaz kube-controller-manager*.pem binmaster3:/etc/kubernetes/ssl/
rsync -vaz kube-controller-manager.kubeconfig kube-controller-manager.conf binmaster2:/etc/kubernetes/
rsync -vaz kube-controller-manager.kubeconfig kube-controller-manager.conf binmaster3:/etc/kubernetes/
rsync -vaz kube-controller-manager.service binmaster2:/usr/lib/systemd/system/
rsync -vaz kube-controller-manager.service binmaster3:/usr/lib/systemd/system/
#master1、2、3上
systemctl daemon-reload 
systemctl enable kube-controller-manager
systemctl start kube-controller-manager
systemctl status kube-controller-manager
ss -antulp | grep 10252 #查看端口占用
~~~

## 部署kube-scheduler组件

### 创建csr请求

```sh
#master1上
cd /data/work
tee -a kube-scheduler-csr.json <<'EOF'
{
    "CN": "system:kube-scheduler",
    "hosts": [
      "127.0.0.1",
      "172.16.183.76",
      "172.16.183.77",
      "172.16.183.78",
      "172.16.183.79"
    ],
    "key": {
        "algo": "rsa",
        "size": 2048
    },
    "names": [
      {
        "C": "CN",
        "ST": "Hubei",
        "L": "Wuhan",
        "O": "system:kube-scheduler",
        "OU": "system"
      }
    ]
}
EOF
```

> - 证书请求文件让system:kube-scheduler这个用户被api-server信任，后面scheduler就能访问apiserver了，至于权限是由kubernetes 内置的 ClusterRoleBindings system:kube-scheduler 将赋予 kube-scheduler 工作所需的权限。
> - hosts 列表包含所有 kube-scheduler 节点 IP； CN 为 system:kube-scheduler、O 为 system:kube-scheduler，

### 生成证书

```sh
cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=kubernetes kube-scheduler-csr.json | cfssljson -bare kube-scheduler
```

### 创建kubeconfig

1. 设置集群参数

```sh
kubectl config set-cluster kubernetes --certificate-authority=ca.pem --embed-certs=true --server=https://172.16.183.76:6443 --kubeconfig=kube-scheduler.kubeconfig
```

2. 设置客户端认证参数

```sh
kubectl config set-credentials system:kube-scheduler --client-certificate=kube-scheduler.pem --client-key=kube-scheduler-key.pem --embed-certs=true --kubeconfig=kube-scheduler.kubeconfig
```

3. 设置上下文参数

```sh
#上下文的名称随便起，但是用户和集群要写对，跟证书请求文件中一致
kubectl config set-context system:kube-scheduler --cluster=kubernetes --user=system:kube-scheduler --kubeconfig=kube-scheduler.kubeconfig
```

4. 设置当前上下文

```sh
kubectl config use-context system:kube-scheduler --kubeconfig=kube-scheduler.kubeconfig
```

### 创建配置文件kube-scheduler.conf

```sh
tee -a kube-scheduler.conf <<'EOF' 
KUBE_SCHEDULER_OPTS="--address=127.0.0.1 \
--kubeconfig=/etc/kubernetes/kube-scheduler.kubeconfig \
--leader-elect=true \
--alsologtostderr=true \
--logtostderr=false \
--log-dir=/var/log/kubernetes \
--v=2"
EOF
#kube-scheduler.kubeconfig里面已经指定了apiserver地址以及证书。
```

### 创建服务启动文件

```sh
tee -a kube-scheduler.service <<'EOF' 
[Unit]
Description=Kubernetes Scheduler
Documentation=https://github.com/kubernetes/kubernetes
 
[Service]
EnvironmentFile=-/etc/kubernetes/kube-scheduler.conf
ExecStart=/usr/local/bin/kube-scheduler $KUBE_SCHEDULER_OPTS
Restart=on-failure
RestartSec=5
 
[Install]
WantedBy=multi-user.target
EOF
```

### 启动服务

```sh
#master1上
cp kube-scheduler*.pem /etc/kubernetes/ssl/
cp kube-scheduler.kubeconfig /etc/kubernetes/
cp kube-scheduler.conf /etc/kubernetes/
cp kube-scheduler.service /usr/lib/systemd/system/
rsync -vaz kube-scheduler*.pem binmaster2:/etc/kubernetes/ssl/
rsync -vaz kube-scheduler*.pem binmaster3:/etc/kubernetes/ssl/
rsync -vaz kube-scheduler.kubeconfig kube-scheduler.conf binmaster2:/etc/kubernetes/
rsync -vaz kube-scheduler.kubeconfig kube-scheduler.conf binmaster3:/etc/kubernetes/
rsync -vaz kube-scheduler.service binmaster2:/usr/lib/systemd/system/
rsync -vaz kube-scheduler.service binmaster3:/usr/lib/systemd/system/
#master 1、2、3上
systemctl daemon-reload
systemctl enable kube-scheduler
systemctl start kube-scheduler
systemctl status kube-scheduler
```

## 导入coredns镜像包

```sh
#把pause-cordns.tar.gz上传到node1节点，手动解压。pause和coredns是工作节点调度创建pod需要用到。
docker load -i pause-cordns.tar.gz
```

## 部署kubelet组件

- kubelet： 每个Node节点上的kubelet定期就会调用API Server的REST接口报告自身状态，API Server接收这些信息后，将节点状态信息更新到etcd中。kubelet也通过API Server监听Pod信息，从而对Node机器上的POD进行管理，如创建、删除、更新Pod。
- master节点上不需要调度pod，所以不需要安装kubelet 

### 配置bootstrap token

```sh
#在master1上
cd /data/work/
BOOTSTRAP_TOKEN=$(awk -F "," '{print $1}' /etc/kubernetes/token.csv)
kubectl config set-cluster kubernetes --certificate-authority=ca.pem --embed-certs=true --server=https://172.16.183.76:6443 --kubeconfig=kubelet-bootstrap.kubeconfig
kubectl config set-credentials kubelet-bootstrap --token=${BOOTSTRAP_TOKEN} --kubeconfig=kubelet-bootstrap.kubeconfig
kubectl config set-context default --cluster=kubernetes --user=kubelet-bootstrap --kubeconfig=kubelet-bootstrap.kubeconfig
kubectl config use-context default --kubeconfig=kubelet-bootstrap.kubeconfig
kubectl create clusterrolebinding kubelet-bootstrap --clusterrole=system:node-bootstrapper --user=kubelet-bootstrap
```

### 创建配置文件kubelet.json

- "cgroupDriver": "systemd"要和docker的驱动一致。
- address替换为各个worker节点的IP地址。

```sh
tee -a kubelet.json <<'EOF'
{
  "kind": "KubeletConfiguration",
  "apiVersion": "kubelet.config.k8s.io/v1beta1",
  "authentication": {
    "x509": {
      "clientCAFile": "/etc/kubernetes/ssl/ca.pem"
    },
    "webhook": {
      "enabled": true,
      "cacheTTL": "2m0s"
    },
    "anonymous": {
      "enabled": false
    }
  },
  "authorization": {
    "mode": "Webhook",
    "webhook": {
      "cacheAuthorizedTTL": "5m0s",
      "cacheUnauthorizedTTL": "30s"
    }
  },
  "address": "172.16.183.79",
  "port": 10250,
  "readOnlyPort": 10255,
  "cgroupDriver": "systemd",
  "hairpinMode": "promiscuous-bridge",
  "serializeImagePulls": false,
  "featureGates": {
    "RotateKubeletClientCertificate": true,
    "RotateKubeletServerCertificate": true
  },
  "clusterDomain": "cluster.local.",
  "clusterDNS": ["10.255.0.2"]
}
EOF
```

### 创建kubelet服务启动文件

```sh
tee -a kubelet.service <<'EOF'
[Unit]
Description=Kubernetes Kubelet
Documentation=https://github.com/kubernetes/kubernetes
After=docker.service
Requires=docker.service
[Service]
WorkingDirectory=/var/lib/kubelet
ExecStart=/usr/local/bin/kubelet \
  --bootstrap-kubeconfig=/etc/kubernetes/kubelet-bootstrap.kubeconfig \ #这个config是为了kubelet第一次和apiserver通信的时候自动生成证书保存到下面的目录里面
  --cert-dir=/etc/kubernetes/ssl \
  --kubeconfig=/etc/kubernetes/kubelet.kubeconfig \
  --config=/etc/kubernetes/kubelet.json \
  --network-plugin=cni \
  --pod-infra-container-image=k8s.gcr.io/pause:3.2 \
  --alsologtostderr=true \
  --logtostderr=false \
  --log-dir=/var/log/kubernetes \
  --v=2
  #如果1.24以上用containerd作为容器运行时，加这个参数
  --container-runtime-endpoint=unix:///run/containerd/containerd.sock
Restart=on-failure
RestartSec=5
 
[Install]
WantedBy=multi-user.target
EOF
```

- kubelet 启动时实际需要指定两个配置⽂件
  - --kubeconfig 指定的是kube-config ⽂件，其中内置了集群根CA 公钥以及⾃⼰作为客户端的公钥和私钥
  - --config 指定的是kubelet的配置

```sh
#node1上
mkdir /etc/kubernetes/ssl -p
#master1上
scp kubelet-bootstrap.kubeconfig kubelet.json binnode1:/etc/kubernetes/
scp ca.pem binnode1:/etc/kubernetes/ssl/
scp kubelet.service binnode1:/usr/lib/systemd/system/
```

### 启动kubelet服务

```sh
#node1上
mkdir /var/lib/kubelet
mkdir /var/log/kubernetes
systemctl daemon-reload
systemctl enable kubelet
systemctl start kubelet
systemctl status kubelet
#确认kubelet服务启动成功后，接着到binmaster1节点上Approve一下bootstrap请求
#执行如下命令可以看到一个worker节点发送了一个 CSR 请求：
kubectl get csr
kubectl certificate approve node-csr-xxxx
kubectl get nodes
#会显示binnode1的notready状态，是因为还未安装网络插件。kubelet暂时不能与apiserver通信
```

## 部署kube-proxy组件

### 创建csr请求

```sh
#在master1上
cd /data/work/
tee -a kube-proxy-csr.json <<'EOF' 
{
  "CN": "system:kube-proxy",
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "C": "CN",
      "ST": "Hubei",
      "L": "Wuhan",
      "O": "k8s",
      "OU": "system"
    }
  ]
}
EOF
```

### 生成证书

~~~sh
#在master1上
cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=kubernetes kube-proxy-csr.json | cfssljson -bare kube-proxy
~~~

### 创建kubeconfig文件

~~~sh
#在master1上
kubectl config set-cluster kubernetes --certificate-authority=ca.pem --embed-certs=true --server=https://172.16.183.76:6443 --kubeconfig=kube-proxy.kubeconfig
kubectl config set-credentials kube-proxy --client-certificate=kube-proxy.pem --client-key=kube-proxy-key.pem --embed-certs=true --kubeconfig=kube-proxy.kubeconfig
kubectl config set-context default --cluster=kubernetes --user=kube-proxy --kubeconfig=kube-proxy.kubeconfig
kubectl config use-context default --kubeconfig=kube-proxy.kubeconfig
~~~

### 创建kube-proxy配置文件

~~~sh
#在master1上
tee -a kube-proxy.yaml <<'EOF'
apiVersion: kubeproxy.config.k8s.io/v1alpha1
bindAddress: 172.16.183.79
clientConnection:
  kubeconfig: /etc/kubernetes/kube-proxy.kubeconfig
clusterCIDR: 172.16.183.0/24
healthzBindAddress: 172.16.183.79:10256
kind: KubeProxyConfiguration
metricsBindAddress: 172.16.183.79:10249
mode: "ipvs"
EOF
~~~

### 创建服务启动文件

~~~sh
#在master1上
tee -a kube-proxy.service <<'EOF'
[Unit]
Description=Kubernetes Kube-Proxy Server
Documentation=https://github.com/kubernetes/kubernetes
After=network.target
 
[Service]
WorkingDirectory=/var/lib/kube-proxy
ExecStart=/usr/local/bin/kube-proxy \
  --config=/etc/kubernetes/kube-proxy.yaml \
  --alsologtostderr=true \
  --logtostderr=false \
  --log-dir=/var/log/kubernetes \
  --v=2
Restart=on-failure
RestartSec=5
LimitNOFILE=65536
 
[Install]
WantedBy=multi-user.target
EOF
~~~

~~~sh
scp  kube-proxy.kubeconfig kube-proxy.yaml binnode1:/etc/kubernetes/
scp  kube-proxy.service binnode1:/usr/lib/systemd/system/
~~~

### 启动服务

~~~sh
#node1上
mkdir -p /var/lib/kube-proxy
systemctl daemon-reload
systemctl enable kube-proxy
systemctl start kube-proxy
systemctl status kube-proxy
~~~

## 部署calico组件

~~~sh
#上传calico镜像，calico.tar.gz上传到node1节点，手动解压。calico pod运行在工作节点
docker load -i calico.tar.gz
#把calico.yaml文件上传到master1上的的/data/work目录
kubectl apply -f calico.yaml
~~~

## 部署coredns组件

~~~sh
#上传coredns.yaml到master1
kubectl apply -f coredns.yaml
#测试coredns
kubectl run busybox --image busybox:1.28 --restart=Never --rm -it busybox -- sh
ping www.baidu.com
nslookup kubernetes.default.svc.cluster.local #解析内部Service的名称，是通过coreDNS去解析的。
~~~

## keepalived+nginx实现apiserver高可用

### 准备epel.repo

~~~sh
#把epel.repo上传到binmaster1的/etc/yum.repos.d目录下.
scp /etc/yum.repos.d/epel.repo binmaster2:/etc/yum.repos.d/
scp /etc/yum.repos.d/epel.repo binmaster3:/etc/yum.repos.d/
scp /etc/yum.repos.d/epel.repo binnode1:/etc/yum.repos.d/
#安装nginx主备
#在master1和master2上做nginx主备安装
yum install nginx keepalived -y
~~~

### 修改nginx配置文件

~~~sh
#在master1和master2上，修改nginx配置文件。主备一样
mkdir -p /etc/nginx/
tee /etc/nginx/nginx.conf <<'EOF'
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /run/nginx.pid;

include /usr/share/nginx/modules/*.conf;

events {
    worker_connections 1024;
}

# 四层负载均衡，为两台Master apiserver组件提供负载均衡
stream {

    log_format  main  '$remote_addr $upstream_addr - [$time_local] $status $upstream_bytes_sent';

    access_log  /var/log/nginx/k8s-access.log  main;

    upstream k8s-apiserver {
       server 172.16.183.76:6443;   # binmaster1 APISERVER IP:PORT
       server 172.16.183.77:6443;   # binmaster2 APISERVER IP:PORT
       server 172.16.183.78:6443;   # binmaster3 APISERVER IP:PORT

    }
    
    server {
       listen 16443; # 由于nginx与master节点复用，这个监听端口不能是6443，否则会冲突。访问master1的16443端口，请求会被代理到upstream的3台节点
       proxy_pass k8s-apiserver;
    }
}

http {
    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile            on;
    tcp_nopush          on;
    tcp_nodelay         on;
    keepalive_timeout   65;
    types_hash_max_size 2048;

    include             /etc/nginx/mime.types;
    default_type        application/octet-stream;

    server {
        listen       80 default_server;
        server_name  _;

        location / {
        }
    }
}
EOF
~~~

### 修改keepalived配置文件

#### 主keepalived节点

~~~sh
#主keepalived配置 - keepalived主要用来提供VIP
mkdir -p /etc/keepalived/
tee /etc/keepalived/keepalived.conf <<'EOF'
global_defs { 
   notification_email { 
     acassen@firewall.loc 
     failover@firewall.loc 
     sysadmin@firewall.loc 
   } 
   notification_email_from Alexandre.Cassen@firewall.loc  
   smtp_server 127.0.0.1 
   smtp_connect_timeout 30 
   router_id NGINX_MASTER
} 

vrrp_script check_nginx {
    script "/etc/keepalived/check_nginx.sh"
}

vrrp_instance VI_1 { 
    state MASTER 
    interface ens33  # 修改为实际网卡名
    virtual_router_id 51 # VRRP 路由 ID实例，每个实例是唯一的 
    priority 100    # 优先级，备服务器设置 90 
    advert_int 1    # 指定VRRP 心跳包通告间隔时间，默认1秒 
    authentication { 
        auth_type PASS      
        auth_pass 1111 
    }  
    # 虚拟IP
    virtual_ipaddress { 
        172.16.183.75/24
    } 
    track_script {
        check_nginx
    } 
}
EOF
#vrrp_script：指定检查nginx工作状态脚本（根据nginx状态判断是否故障转移）
#virtual_ipaddress：虚拟IP（VIP）
~~~

~~~sh
#master1上
cd ~
tee /etc/keepalived/check_nginx.sh <<'EOF' 
#!/bin/bash
count=$(ps -ef |grep nginx | grep sbin | egrep -cv "grep|$$")
if [ "$count" -eq 0 ];then
    systemctl stop keepalived
fi
EOF
chmod +x  /etc/keepalived/check_nginx.sh
~~~

#### 备keepalived节点

~~~sh
tee /etc/keepalived/keepalived.conf <<'EOF'
global_defs { 
   notification_email { 
     acassen@firewall.loc 
     failover@firewall.loc 
     sysadmin@firewall.loc 
   } 
   notification_email_from Alexandre.Cassen@firewall.loc  
   smtp_server 127.0.0.1 
   smtp_connect_timeout 30 
   router_id NGINX_BACKUP
} 

vrrp_script check_nginx {
    script "/etc/keepalived/check_nginx.sh"
}

vrrp_instance VI_1 { 
    state BACKUP 
    interface ens33
    virtual_router_id 51 # VRRP 路由 ID实例，每个实例是唯一的 
    priority 90
    advert_int 1
    authentication { 
        auth_type PASS      
        auth_pass 1111 
    }  
    virtual_ipaddress { 
        172.16.183.75/24
    } 
    track_script {
        check_nginx
    } 
}
EOF
~~~

~~~sh
#master2上
cd ~
cat /etc/keepalived/check_nginx.sh 
#!/bin/bash
count=$(ps -ef |grep nginx | grep sbin | egrep -cv "grep|$$")
if [ "$count" -eq 0 ];then
    systemctl stop keepalived
fi
chmod +x /etc/keepalived/check_nginx.sh
#注：keepalived根据脚本返回状态码（0为工作正常，非0不正常）判断是否故障转移。当nginx服务出现故障时，自动停止keepalived服务，触发故障切换。VIP就会切走。
~~~

### 启动服务

~~~sh
#master1和2上
systemctl daemon-reload
yum install nginx-mod-stream -y
systemctl start nginx
systemctl start keepalived
systemctl enable nginx keepalived
~~~

- 测试keepalived工作：stop掉master1上的nginx，vip会漂移到master2上

  `service stop nginx`

### 配置worker节点与master的连接

~~~sh
#目前所有的Worker Node组件连接都还是master1 Node，如果不改为连接VIP走负载均衡器，那么Master还是单点故障。
#因此接下来就是要改所有Worker Node（kubectl get node命令查看到的节点）组件配置文件，由原来172.16.183.76修改为172.16.183.75（VIP）。
#在所有Worker Node执行：
sed -i 's#172.16.183.76:6443#172.16.183.75:16443#' /etc/kubernetes/kubelet-bootstrap.kubeconfig
sed -i 's#172.16.183.76:6443#172.16.183.75:16443#' /etc/kubernetes/kubelet.json
sed -i 's#172.16.183.76:6443#172.16.183.75:16443#' /etc/kubernetes/kubelet.kubeconfig
sed -i 's#172.16.183.76:6443#172.16.183.75:16443#' /etc/kubernetes/kube-proxy.yaml
sed -i 's#172.16.183.76:6443#172.16.183.75:16443#' /etc/kubernetes/kube-proxy.kubeconfig
systemctl restart kubelet kube-proxy
~~~

?question:不是有3台master节点吗？VIP漂移只发生在两个master上？master3是否也要设置为备用节点？ 不需要，k8s组件请求apiserver的时候走的是VIP+16443端口，也就是nginx，nginx配置中已经将请求代理给了upstream的3台master。

# 二进制组件升级

## 下载二进制包

- 二进制包所在的github地址如下：https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG/，可以按照版本下载二进制包。控制节点组件，找到Server Binaries，下载amd64版本的。server binaries二进制包里面就包含了：controller-manager，apiserver，scheduler等控制平面组件。其实也包含了工作节点需要的kubelet和kubeproxy

## master节点升级

- 备份二进制文件

~~~sh
cd /usr/bin
mv kubectl kubectl.bak
systemctl stop kube-apiserver
systemctl stop kube-scheduler
systemctl stop kube-controller-manager
mv kube-apiserver kube-apiserver.bak
mv kube-controller-manager kube-controller-manager.bak
mv kube-scheduler kube-scheduler.bak
~~~

- 升级

~~~sh
tar xf kubernetes-server-linux-amd64.tar.gz
cp kubernetes/server/bin/kubectl /usr/bin/
cp kubernetes/server/bin/{kube-apiserver,kube-controller-manager,kube-scheduler} /usr/bin/
~~~

- 启动服务

~~~sh
systemctl start kube-apiserver
systemctl start kube-controller-manager
systemctl start kube-scheduler
~~~

> 如果升级完某些服务起不来，有可能是因为配置文件某些参数并不支持。可以查看服务状态中的报错:
>
> `systemctl status kube-apiserver -l`

## 工作节点升级

- 备份二进制文件

~~~sh
systemctl stop kubelet
systemctl stop kube-proxy
cd /usr/bin
mv kubelet kubelet.bak
mv kube-proxy kube-proxy.bak
~~~

- 升级

~~~sh
#回到控制节点，把二进制文件分发到node节点
scp kubernetes/server/bin/{kubelet,kube-proxy} node:/usr/bin/
~~~

- 启动服务

~~~sh
systemctl daemon-reload && systemctl start kubelet
systemctl daemon-reload && systemctl start kube-proxy
~~~

# 二进制安装多master集群-1.25

## 环境准备

- 机器规划

  - podSubnet（pod网段） 10.244.0.0/16
  - serviceSubnet（service网段）: 10.96.0.0/12
  - 操作系统：centos7.9
  - 配置： 4Gib内存/4vCPU/60G硬盘
  - 网络：NAT模式

  | K8S集群角色 | IP             | 主机名          | 安装的组件                                                   |
  | ----------- | -------------- | --------------- | ------------------------------------------------------------ |
  | 控制节点    | 192.168.40.180 | xianchaomaster1 | apiserver、controller-manager、schedule、etcd、kube-proxy、容器运行时、keepalived、nginx |
  | 控制节点    | 192.168.40.181 | xianchaomaster2 | apiserver、controller-manager、schedule、etcd、kube-proxy、容器运行时、keepalived、nginx |
  | 控制节点    | 192.168.40.182 | xianchaomaster3 | apiserver、controller-manager、schedule、etcd、kube-proxy、容器运行时、keepalived、nginx |
  | 工作节点    | 192.168.40.183 | xianchaonode1   | Kube-proxy、calico、coredns、容器运行时、kubelet             |
  | VIP         | 192.168.40.199 |                 |                                                              |

- 配置静态IP

- 关闭selinux

- 配置机器主机名

- 配置hosts文件

- 配置时间同步

- 安装基础软件包

- 配置ssh互信

- 关闭swap分区

- 开启内核转发

- 关闭firewalld防火墙

- 配置aliyun repo源

  ~~~sh
  #docker repo源
  yum install yum-utils -y
  yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
  
  
  #containerd repo源
  #k8s repo源
  
  
  
  #containerd repo源
  containerd repo源    
  ~~~

## 安装containerd

~~~sh
#所有节点安装
yum install  containerd.io-1.6.6 -y
mkdir -p /etc/containerd
containerd config default > /etc/containerd/config.toml
vim /etc/containerd/config.toml
#把SystemdCgroup = false修改成SystemdCgroup = true
#把sandbox_image = "k8s.gcr.io/pause:3.6"修改sandbox_image="registry.aliyuncs.com/google_containers/pause:3.7"
systemctl enable containerd  --now
~~~

- 配置containerd镜像加速器

~~~sh
vim /etc/containerd/config.toml文件
#找到config_path = ""，修改成如下目录：config_path = "/etc/containerd/certs.d"
mkdir /etc/containerd/certs.d/docker.io/ -p
vim /etc/containerd/certs.d/docker.io/hosts.toml
#写入如下内容：
[host."https://vh3bm52y.mirror.aliyuncs.com",host."https://registry.docker-cn.com"]
  capabilities = ["pull"]
#重启containerd：
systemctl restart containerd
~~~

## 安装crictl

- 安装包可以从这里下载：https://github.com/kubernetes-sigs/cri-tools/releases/

~~~sh
#所有节点
wget https://github.com/kubernetes-sigs/cri-tools/releases/download/v1.24.2/crictl-v1.24.2-linux-amd64.tar.gz
tar zxvf crictl-v1.24.2-linux-amd64.tar.gz -C /usr/bin/
cat > /etc/crictl.yaml <<EOF
runtime-endpoint: unix:///run/containerd/containerd.sock
image-endpoint: unix:///run/containerd/containerd.sock
timeout: 10
debug: false
EOF
systemctl restart  containerd
~~~

## 安装docker

~~~sh
#所有节点
yum install  docker-ce  -y
systemctl enable docker --now
~~~

- 配置加速器

~~~sh
#配置docker镜像加速器，k8s所有节点均按照以下配置
vim /etc/docker/daemon.json
#写入如下内容：
{
 "registry-mirrors":["https://vh3bm52y.mirror.aliyuncs.com","https://registry.docker-cn.com","https://docker.mirrors.ustc.edu.cn","https://dockerhub.azk8s.cn","http://hub-mirror.c.163.com"]
} 
#重启docker：
systemctl restart docker
~~~

# 搭建etcd集群

同上面1.20.7

# 安装k8s组件

同上面1.20.7

- 注：镜像解压用ctr -n=k8s.io images import

- 最后多一步：对系统用户kubernetes做授权

  ~~~sh
  kubectl create clusterrolebinding kubernetes-kubectl --clusterrole=cluster-admin --user=kubernetes
  ~~~
