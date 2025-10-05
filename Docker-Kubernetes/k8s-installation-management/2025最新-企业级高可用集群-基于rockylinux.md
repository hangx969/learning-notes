# 企业级高可用集群架构设计

## 架构图

![image-20251004212113888](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202510042121022.png)

1. 控制节点：

   - 只要上了生产，一定就是3个，不能是1个。因为后期扩容控制节点会非常麻烦甚至无法扩容。
   - 3 Master已经可以应对95%以上的场景，足够用了，无需再多。
   - 如果前期负载小（10-20个微服务），宁愿没有工作节点，直接部署在master上，后期负载上来再扩工作节点。

2. 控制节点前端负载均衡：

   - 软件负载均衡，可以用keepalived+haproxy/nginx的方案

   - 有硬件支持的话用F5代理，直接代理apiserver的6443端口负载均衡
   - 在公有云上一般不需要keepalived和haproxy，直接用公有云的SLB

3. 工作节点：一开始上3-5个，够用，后面负载高了随时动态扩容。

## 控制节点资源配置

| 工作节点数量 | 控制节点数量 | 控制节点配置 | Etcd节点配置              | Master & Etcd                                     | 备注                                                         |
| ------------ | ------------ | ------------ | ------------------------- | ------------------------------------------------- | ------------------------------------------------------------ |
| 0-100        | 3            | /            | /                         | 8C + 32G + 128G SSD<br />或者：4C + 8G + 128G SSD | 1. Etcd和Master部署到一起<br />2. SSD必备，etcd对硬盘性能要求非常高。对空间要求不高（2万个pod大概也就占20G etcd） |
| 100-250      | 3            | /            | /                         | 16C + 32G + 128G SSD                              | 1. 能支撑2万个pod级别 <br />2. Etcd和Master部署到一起也是可以的 |
| 250-500      | 3            | 16C + 32G    | 8C + 32G + (512G SSD * 5) |                                                   | 1. Etcd和Master分开部署<br />2. Etcd拆成5个节点，跨机房部署，容忍挂2个节点 |

## 工作节点资源配置

1. 可以理解为无状态的，数量、CPU、内存可以随时扩容。
2. 推荐单节点配置：(8C + 32G) / (16C + 64G)
3. 最低节点数：3个。两个风险太高：如果一个挂了，pod全飘到另一个节点上扛不住。

总之，生产环境搭建集群，最低需要3主3从6个节点。

## 磁盘划分

### 控制节点

| 根分区（100G） | Etcd数据盘（100G NVME SSD） | 数据盘（500G SSD）                                           |
| -------------- | --------------------------- | ------------------------------------------------------------ |
| /              | /var/lib/etcd               | /data, /var/lib/kubelet, /var/lib/containers                 |
| 存储系统数据   | 需要高性能                  | 1. 可以把磁盘分成三个区，分别挂到三个目录<br />2. 也可以只挂到/data下，创建两个目录软链到kubelet和containers【推荐】 |

### 工作节点

| 根分区（100G） | 数据盘（500G SSD）                                           |
| -------------- | ------------------------------------------------------------ |
| /              | /data, /var/lib/kubelet, /var/lib/containers                 |
|                | 只挂到/data下，创建两个目录软链到kubelet和containers【推荐】 |

## 网络划分

网段划分非常重要，属于软件层面的划分，如果划分不合适的话可能需要重建集群。

下面三个网段不能有任何冲突。

|      | 节点网段                         | Service网段                                                  | Pod网段                  |
| ---- | -------------------------------- | ------------------------------------------------------------ | ------------------------ |
| 网段 | 192.168.40.0/24                  | 10.96.0.0/16                                                 | 172.16.0.0/16            |
| 来源 | 局域网分配的                     | CNI插件划分的                                                | controller-manager划分的 |
| 备注 | 一般节点网段都是已经提前划分好的 | 保留IP：<br />1. CoreDNS Service IP：**10.96.0.10** (svc网段的第10个IP)<br />2. API Server Service IP：**10.96.0.1**（svc网段的第1个IP） |                          |

注意：

1. 上面三个内网网段可以互相替换。

   - 假如节点网段已经分配172.16，那么可以Pod网段给192.168，svc网段给10.96
   - 假如节点网段已经占了192.168和172.16，那么只能用10.96划分给pod和svc，可以用子网掩码来划分两个子网。一般pod会比svc的ip需求多一些。直接问大模型怎么划分。

2. 注意内网网段是固定有限的：

   > 1. **A类私有地址段**：`10.0.0.0/8`
   >    - IP范围：10.0.0.0 - 10.255.255.255
   >    - 子网掩码：255.0.0.0
   >    - 可用地址数：约1677万个
   > 2. **B类私有地址段**：`172.16.0.0/12`
   >    - IP范围：172.16.0.0 - 172.31.255.255
   >    - 子网掩码：255.240.0.0
   >    - 可用地址数：约104万个
   > 3. **C类私有地址段**：`192.168.0.0/16`
   >    - IP范围：192.168.0.0 - 192.168.255.255
   >    - 子网掩码：255.255.0.0
   >    - 可用地址数：约6.5万个

   所以192.0.0.0/16这样的网段，是包含了一部分公网IP的，不能用作k8s网段，会和公网IP冲突。

3. 对于keepalived的VIP：

   - 不能和公司内网IP重复，需要用一个不存在的，并且属于局域网内的IP。提前ping一下，ping不通才能用。
   - 私有云上搭建需要问管理员是否支持VIP。（比如某些Openstack集群可能不支持VIP）


# 企业级高可用架构落地实战

## 节点准备

1. 实验用，准备3台VMWare VM作为Master，每台：
   - 4C4G
   - 一块自带的40G硬盘
   - 加一块10G盘，给etcd用
   - 加一块40G盘，作为数据盘
2. 准备2台VM作为Node，每台：
   -  4C4G
   -  一块自带的40G盘
   -  加一块40G盘作为数据盘

~~~sh
fdisk -l # 查看新增磁盘
~~~

## 实验环境规划

| 主机名  | IP                              | 备注                                                         |
| ------- | ------------------------------- | ------------------------------------------------------------ |
| m01~m03 | 192.168.40.190 ~ 192.168.40.192 | master节点*3                                                 |
| n01~n03 | 192.168.40.193 ~ 192.168.40.195 | worker节点*3                                                 |
| /       | 192.168.40.199                  | keepalived VIP<br />注：<br />1. 不能和公司内网IP重复，需要用一个不存在的，并且属于局域网内的IP。提前ping一下，ping不通才能用。<br />2. 私有云上搭建需要问管理员是否支持VIP |

| 配置信息    | 备注                                                         |
| ----------- | ------------------------------------------------------------ |
| OS Version  | Rocky Linux 9                                                |
| containerd  | latest                                                       |
| kubernetes  | 1.17+都适用。<br />注意：生产环境建议用小版本>5的，比如1.28.5以后才建议用于生产环境 |
| Pod网段     | 172.16.0.0/16                                                |
| Service网段 | 10.96.0.0/16                                                 |

## 节点磁盘挂载

实验中都用fdisk直接分区，也可以用LVM创建逻辑卷来挂载。

### 挂载etcd数据盘

Master节点才需要这个配置

~~~sh
mkdir -p /var/lib/etcd
# etcd盘可以直接新建分区划给etcd
fdisk /dev/sd
n
p
w

# 格式化
mkfs.xfs /dev/sd

# 持久挂载
blkid /dev/sd

tee -a /etc/fstab <<'EOF'
UUID=xxx    /var/lib/etcd     xfs    defaults    0 0
EOF

systemctl daemon-reload && mount -a
df -Th
~~~

### 挂载data盘

Master和Worker节点都要配置

~~~sh
mkdir -p /data
fdisk /dev/sd
n
p
w

# 格式化
mkfs.xfs /dev/sd

# 持久挂载
blkid /dev/sd

tee -a /etc/fstab <<'EOF'
UUID=xxx    /data    xfs    defaults    0 0
EOF

systemctl daemon-reload && mount -a
df -Th
~~~

创建kubelet和containers目录和软链：

~~~sh
mkdir -p /data/kubelet
mkdir -p /data/containers
ln -s /data/kubelet /var/lib/kubelet
ln -s /data/containers /var/lib/containers
~~~

## 基本配置

所有节点更改主机名:

~~~sh
hostnamectl set-hostname m01
~~~

所有节点更改hosts

~~~sh
tee -a /etc/hosts <<'EOF'
192.168.40.190   m01  
192.168.40.191   m02
192.168.40.192   m03
192.168.40.193   n01
192.168.40.194   n02
192.168.40.195   n03
EOF
~~~

所有节点配置默认yum源：

~~~sh
sed -e 's|^mirrorlist=|#mirrorlist=|g' \
    -e 's|^#baseurl=http://dl.rockylinux.org/$contentdir|baseurl=https://mirrors.aliyun.com/rockylinux|g' \
    -i.bak \
    /etc/yum.repos.d/rocky-*.repo

dnf makecache
yum makecache
~~~

所有节点安装基本软件包：

~~~sh
yum update -y
yum install -y yum-utils device-mapper-persistent-data lvm2 wget net-tools nfs-utils lrzsz gcc gcc-c++ make cmake libxml2-devel openssl-devel curl curl-devel unzip sudo libaio-devel vim ncurses-devel autoconf automake epel-release openssh-server telnet coreutils iputils iproute nmap-ncat jq psmisc git bash-completion rsyslog
~~~

所有节点关闭防火墙、selinux、swap、dnsmasq，开启rsyslog：

~~~sh
systemctl disable --now firewalld
systemctl disable --now dnsmasq

setenforce 0
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
sed -i 's#SELINUX=enforcing#SELINUX=disabled#g' /etc/sysconfig/selinux

systemctl enbable --now rsyslog

swapoff -a && sysctl -w vm.swappiness=0
sed -ri '/^[^#]*swap/s@^@#@' /etc/fstab
systemctl daemon-reload && mount -a
~~~

所有节点安装ntpdate：(实际生产使用中发现chrony没有ntpdate可靠)

~~~sh
dnf install -y epel-release
dnf config-manager --set-enabled epel
dnf install ntpsec
~~~

所有节点同步时间并配置上海时区：

~~~sh
ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
echo 'Asia/Shanghai' > /etc/timezone
ntpdate time2.aliyun.com

# 加入到crontab
crontab -e
*/5 * * * * /usr/sbin/ntpdate time2.aliyun.com
~~~

所有节点配置limit：

~~~sh
ulimit -SHn 65535
tee -a /etc/security/limits.conf <<'EOF'
* soft nofile 65536
* hard nofile 131072
* soft nproc 65535
* hard nproc 655350
* soft memlock unlimited
* hard memlock unlimited
~~~

m01免密登录其他节点（安装过程中的各种配置文件均在m01上操作），集群管理也在m01上操作

~~~sh
ssh-keygen -t rsa
for i in m01 m02 m03 n01 n02 n03;do ssh-copy-id -i .ssh/id_rsa.pub $i;done
~~~

## 内核优化

所有节点安装ipvsadm：

~~~sh
yum install -y ipvsadm ipset sysstat conntrack libsecomp -y
~~~

所有节点配置ipvs模块：

~~~sh
modprobe -- ip vs
modprobe -- ip vs rr
modprobe -- ip vs wrr
modprobe -- ip vs sh
modprobe -- nf conntrack
~~~

所有节点创建/etc/modules-load.d/ipvs.conf，并配置开机自动加载：

~~~sh
tee /etc/modules-load.d/ipvs.conf <<'EOF'
ip_vs
ip_vs_lc
ip_vs_wlc
ip_vs_rr
ip_vs_wrr
ip_vs_lblc
ip_vs_lblcr
ip_vs_dh
ip_vs_sh
ip_vs_fo
ip_vs_nq
ip_vs_sed
ip_vs_ftp
nf_conntrack
ip_tables
ip_set
xt_set
ipt_set
ipt_rpfilter
ipt_REJECT
ipip
EOF
~~~

~~~sh
systemctl enable --now systemd-modules-load.service
# 如有报错可以忽略
~~~

所有节点内核优化配置：【针对4C4G虚拟机】

~~~sh
cat <<EOF > /etc/sysctl.d/k8s.conf
net.ipv4.ip_forward = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
fs.may_detach_mounts = 1
net.ipv4.conf.all.route_localnet = 1
vm.overcommit_memory = 1
vm.panic_on_oom = 0
fs.inotify.max_user_watches = 89100
fs.file-max = 52706963
fs.nr_open = 52706963
net.netfilter.nf_conntrack_max = 2310720

net.ipv4.tcp_keepalive_time = 600
net.ipv4.tcp_keepalive_probes = 3
net.ipv4.tcp_keepalive_intvl = 15
net.ipv4.tcp_max_tw_buckets = 36000
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_max_orphans = 327680
net.ipv4.tcp_orphan_retries = 3
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_max_syn_backlog = 16384
net.ipv4.tcp_timestamps = 0
net.core.somaxconn = 16384
EOF
~~~

加载新参数：

~~~sh
modprobe br_netfilter
modprobe nf_conntrack
sysctl --system
reboot
# 检查内核模块是否加载
lsmod | grep --color=auto -e ip_vs -e nf_conntrack
~~~

## 高可用组件安装

> 注意：
>
> 1. 如果安装的不是高可用集群，不需要安装haproxy和keepalived
> 2. 公有云上自建集群，用公有云的SLB服务即可代替haproxy和keepalived。因为公有云大多数不支持keepalived VIP漂移

所有master节点上安装：

~~~sh
yum install -y haproxy keepalived
~~~

### 配置haproxy

所有master节点配置haproxy：

~~~sh
mkdir /etc/haproxy
# 清空原配置，添加新配置
tee /etc/haproxy/haproxy.cfg <<'EOF'
global
  maxconn 2000
  ulimit-n 16384
  log 127.0.0.1 local0 err
  stats timeout 30s
defaults
  log global
  mode http
  option httplog
  timeout connect 5000
  timeout client 50000
  timeout server 50000
  timeout http-request 15s
  timeout http-keep-alive 15s
  
frontend k8s-master
  bind 0.0.0.0:16443
  bind 127.0.0.1:16443
  mode tcp
  option tcplog
  tcp-request inspect-delay 5s
  default_backend k8s-master

backend k8s-master
  mode tcp
  option tcplog
  option tcp-check
  balance roundrobin
  default-server inter 10s downinter 5s rise 2 fail 2 slowstart 60s maxconn 250 maxqueue 256 weight 100
  server k8s-master01  192.168.40.190:6443  check
  server k8s-master02  192.168.40.191:6443  check
  server k8s-master03  192.168.40.192:6443  check
EOF
~~~

> 注意这段配置：
>
> server k8s-master01  192.168.40.190:6443  check
> server k8s-master02  192.168.40.191:6443  check
> server k8s-master03  192.168.40.192:6443  check
>
> 只关心实际IP地址，实际主机名不是k8s-master01也没关系，只要IP地址正确即可

### 配置keepalived

注意修改三个字段：

~~~sh
interface ens160 # 主机网卡名
mcast_src_ip 192.168.40.130 # 当前节点的IP
virtual_ipaddress {
    192.168.40.199 # VIP的地址
}
~~~

#### Master01配置

~~~sh
mkdir /etc/keepalived
# 清空原配置，添加新配置
tee /etc/keepalived/keepalived.conf <<'EOF'
! Configuration File for keepalived
global_defs {
    router_id LVS_DEVEL
    script_user root
    enable_script_security
}
vrrp_script chk_apiserver {
    script "/etc/keepalived/check_apiserver.sh"
    interval 5
    weight -5
    fall 2
    rise 1
}
vrrp_instance VI_1 {
    state MASTER
    interface ens160
    mcast_src_ip 192.168.40.190
    virtual_router_id 51
    priority 101
    advert_int 2
    authentication {
        auth_type PASS
        auth_pass K8SHA_KA_AUTH
    }
    virtual_ipaddress {
        192.168.40.199
    }
    track_script {
        chk_apiserver
    }
}
EOF
~~~

#### Master02配置

~~~sh
mkdir /etc/keepalived
# 清空原配置，添加新配置
tee /etc/keepalived/keepalived.conf <<'EOF'
! Configuration File for keepalived
global_defs {
    router_id LVS_DEVEL
    script_user root
    enable_script_security
}
vrrp_script chk_apiserver {
    script "/etc/keepalived/check_apiserver.sh"
    interval 5
    weight -5
    fall 2
    rise 1
}
vrrp_instance VI_1 {
    state MASTER
    interface ens160
    mcast_src_ip 192.168.40.191
    virtual_router_id 51
    priority 101
    advert_int 2
    authentication {
        auth_type PASS
        auth_pass K8SHA_KA_AUTH
    }
    virtual_ipaddress {
        192.168.40.199
    }
    track_script {
        chk_apiserver
    }
}
EOF
~~~

#### Master03配置

~~~sh
mkdir /etc/keepalived
# 清空原配置，添加新配置
tee /etc/keepalived/keepalived.conf <<'EOF'
! Configuration File for keepalived
global_defs {
    router_id LVS_DEVEL
    script_user root
    enable_script_security
}
vrrp_script chk_apiserver {
    script "/etc/keepalived/check_apiserver.sh"
    interval 5
    weight -5
    fall 2
    rise 1
}
vrrp_instance VI_1 {
    state MASTER
    interface ens160
    mcast_src_ip 192.168.40.192
    virtual_router_id 51
    priority 101
    advert_int 2
    authentication {
        auth_type PASS
        auth_pass K8SHA_KA_AUTH
    }
    virtual_ipaddress {
        192.168.40.199
    }
    track_script {
        chk_apiserver
    }
}
EOF
~~~

#### 健康检查文件

所有Master节点添加keepalived健康检查文件：

~~~sh
tee /etc/keepalived/check_apiserver.sh <<'EOF'
#!/bin/bash
err=0
for k in $(seq 1 3)
do
    check_code=$(pgrep haproxy)
    if [[ $check_code == "" ]]; then
        err=$(expr $err + 1)
        sleep 1
        continue
    else
        err=0
        break
    fi
done

if [[ $err != "0" ]]; then
    echo "systemctl stop keepalived"
    /usr/bin/systemctl stop keepalived
    exit 1
else
    exit 0
fi
EOF
~~~

添加权限：

~~~sh
chmod +x /etc/keepalived/check_apiserver.sh
~~~

### 启动服务

所有Master节点启动服务

~~~sh
systemctl daemon-reload
systemctl enable --now haproxy
systemctl enable --now keepalived
~~~

### 测试VIP

所有Master和Worker节点测试VIP：

~~~sh
# ping必须全通
ping 192.168.40.199 -c 4
# telnet端口必须全通：出现 ] 说明是通的
telnet 192.168.40.199 16443
~~~

> 如果ping不通且telnet没有出现 ] ，则认为VIP不同，不可继续安装。需要排查keepalived的问题，比如防火墙和selinux，haproxy和keepalived的状态，监听端口等。排查步骤：
>
> 1.	确认VIP是否正确
> 2.	所有节点查看防火墙状态必须为disable和inactive：systemctl status firewalld
> 3.	所有节点查看selinux状态，必须为disable：getenforce
> 4.	master节点查看haproxy和keepalived状态：systemctl status keepalived haproxy
> 5.	master节点查看监听端口：netstat -lntp
>
> 如果以上都没有问题，需要确认：
>
> 1.	是否是公有云机器
> 2.	是否是私有云机器（类似OpenStack）
> 3.	上述公有云一般都是不支持keepalived，私有云可能也有限制，需要和自己的私有云管理员咨询

### 快照

完成keepalived测试之后，可以把所有VM关机拍快照。

## Runtime安装

如果安装的版本低于1.24，选择Docker和Containerd均可，高于1.24建议选择Containerd作为Runtime，不再推荐使用Docker作为Runtime。

### 安装docker和containerd

所有节点安装docker和containerd：

~~~sh
yum-config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
yum clean all && yum makecache
yum install docker-ce containerd -y
~~~

【可选】启动docker：（可以无需启动Docker，只需要配置和启动Containerd即可）

~~~sh
systemctl enable docker --now
# 配置docker镜像加速器，k8s所有节点均按照以下配置
tee /etc/docker/daemon.json <<'EOF'
{
 "registry-mirrors":["https://x6j7eqtq.mirror.aliyuncs.com","https://docker.lmirror.top","https://docker.m.daocloud.io", "https://hub.uuuadc.top","https://docker.anyhub.us.kg","https://dockerhub.jobcher.com","https://dockerhub.icu","https://docker.ckyl.me","https://docker.awsl9527.cn","https://docker.laoex.link"]
} 
EOF
#重启docker：
systemctl daemon-reload && systemctl restart docker && systemctl status docker
~~~

### 配置containerd

1. 首先配置Containerd所需的模块（所有节点）：

~~~sh
cat <<EOF | tee /etc/modules-load.d/containerd.conf
overlay
br_netfilter
EOF
~~~

2. 所有节点加载模块：

~~~sh
modprobe -- overlay
modprobe -- br_netfilter
~~~

3. 所有节点，配置Containerd所需的内核：

~~~sh
cat <<EOF | tee /etc/sysctl.d/99-kubernetes-cri.conf
net.bridge.bridge-nf-call-iptables  = 1
net.ipv4.ip_forward                 = 1
net.bridge.bridge-nf-call-ip6tables = 1
EOF
~~~

4. 所有节点加载内核：

~~~sh
sysctl --system
~~~

5. 所有节点生成containerd配置文件：

~~~sh
mkdir -p /etc/containerd
containerd config default | tee /etc/containerd/config.toml
~~~

6. 修改containerd配置的pause镜像和Cgroup：

~~~sh
sed -i 's#SystemdCgroup = false#SystemdCgroup = true#g' /etc/containerd/config.toml
sed -i 's#k8s.gcr.io/pause#registry.cn-hangzhou.aliyuncs.com/google_containers/pause#g'  /etc/containerd/config.toml
sed -i 's#registry.gcr.io/pause#registry.cn-hangzhou.aliyuncs.com/google_containers/pause#g'  /etc/containerd/config.toml
sed -i 's#registry.k8s.io/pause#registry.cn-hangzhou.aliyuncs.com/google_containers/pause#g'  /etc/containerd/config.toml
~~~

7. 【可选】如果有连接harbor的需求，更改配置文件的这一部分：

~~~toml
    [plugins."io.containerd.grpc.v1.cri".registry]
      config_path = ""

      [plugins."io.containerd.grpc.v1.cri".registry.auths]

      [plugins."io.containerd.grpc.v1.cri".registry.configs]
        [plugins."io.containerd.grpc.v1.cri".registry.configs."harbor.hanxux.local".tls]
            insecure_skip_verify = true
            ca_file = ""
            cert_file = ""
            key_file = ""
        [plugins."io.containerd.grpc.v1.cri".registry.configs."harbor.hanxux.local".auth]
            username = "admin"
            password = "Harbor12345"

      [plugins."io.containerd.grpc.v1.cri".registry.headers]

      [plugins."io.containerd.grpc.v1.cri".registry.mirrors]
         [plugins."io.containerd.grpc.v1.cri".registry.mirrors."harbor.hanxux.local"]
            endpoint = ["http://harbor.hanxux.local"]
          [plugins."io.containerd.grpc.v1.cri".registry.mirrors."docker.io"]
             endpoint = ["https://x6j7eqtq.mirror.aliyuncs.com","https://docker.lmirror.top","https://docker.m.daocloud.io", "https://hub.uuuadc.top","https://docker.anyhub.us.kg","https://dockerhub.jobcher.com","https://dockerhub.icu","https://docker.ckyl.me","https://docker.awsl9527.cn","https://docker.laoex.link"]
~~~

8. 所有节点启动Containerd，并配置开机自启动：

~~~sh
systemctl daemon-reload
systemctl enable --now containerd
~~~

9. 【可选】`crictl`是一个命令行工具，用来验证 CRI 兼容性。若报错没有安装 `crictl`，可以执行：

~~~sh
VERSION="1.25.0"
curl -L -o /usr/local/bin/crictl "https://github.com/kubernetes-sigs/cri-tools/releases/download/v${VERSION}/crictl-v${VERSION}-linux-amd64.tar.gz"
tar zxvf /usr/local/bin/crictl -C /usr/local/bin
chmod +x /usr/local/bin/crictl
~~~

9. 【可选】所有节点配置crictl客户端连接的运行时位置：

~~~sh
cat > /etc/crictl.yaml <<EOF
runtime-endpoint: unix:///run/containerd/containerd.sock
image-endpoint: unix:///run/containerd/containerd.sock
timeout: 10
debug: false
EOF
~~~

~~~sh
systemctl restart containerd
# 验证配置
containerd --version
crictl info
~~~

## K8s组件安装

1. 所有节点配置源：==注意这里需要更改k8s版本号，只用写minor version，不用写patch版本==

~~~sh
cat <<EOF | tee /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://mirrors.aliyun.com/kubernetes-new/core/stable/v1.33/rpm/
enabled=1
gpgcheck=1
gpgkey=https://mirrors.aliyun.com/kubernetes-new/core/stable/v1.33/rpm/repodata/repomd.xml.key
EOF
~~~

2. 所有节点安装kubelet、kubectl、kubeadm：==注意版本需要对应k8s版本号==

~~~sh
yum clean all && yum makecache
yum install kubeadm-1.33* kubelet-1.33* kubectl-1.33* -y
~~~

3. 所有节点开机自启动kubelet：（由于还未初始化，没有kubelet的配置文件，此时kubelet无法启动，无需关心）

~~~sh
systemctl daemon-reload
systemctl enable --now kubelet
~~~

4. 【离线安装方法】如果安装报找不到指定的源，可以按照下面的网址，下载指定版本的rpm文件，传到linux机器：

   - https://mirrors.aliyun.com/kubernetes-new/core/stable/v1.33
   - https://mirrors.aliyun.com/kubernetes-new/core/stable/v1.33/rpm/x86_64/?spm=a2c6h.25603864.0.0.7ced7af3l8FcI0

   基于上面下载到linux机器的rpm文件，手动安装：`rpm -ivh ./*`

## 集群初始化

1. 以下操作在Master01节点执行。集群初始化只在master01执行一遍，其余节点都是join过来的。

~~~sh
vim kubeadm-config.yaml
~~~

~~~yaml
apiVersion: kubeadm.k8s.io/v1beta4
bootstrapTokens:
- groups:
  - system:bootstrappers:kubeadm:default-node-token
  token: 7t2weq.bjbawausm0jaxury
  ttl: 24h0m0s
  usages:
  - signing
  - authentication
kind: InitConfiguration
localAPIEndpoint:
  advertiseAddress: 192.168.181.130 # master01地址
  bindPort: 6443
nodeRegistration:
  criSocket: unix:///var/run/containerd/containerd.sock
  imagePullPolicy: IfNotPresent
  imagePullSerial: true
  name: m01 # hostname
  taints:
  - effect: NoSchedule
    key: node-role.kubernetes.io/control-plane
timeouts:
  controlPlaneComponentHealthCheck: 4m0s
  discovery: 5m0s
  etcdAPICall: 2m0s
  kubeletHealthCheck: 4m0s
  kubernetesAPICall: 1m0s
  tlsBootstrap: 5m0s
  upgradeManifests: 5m0s
---
apiServer:
  certSANs:
  - 192.168.40.199 # VIP
apiVersion: kubeadm.k8s.io/v1beta4
caCertificateValidityPeriod: 876000h0m0s
certificateValidityPeriod: 876000h0m0s
certificatesDir: /etc/kubernetes/pki
clusterName: kubernetes
controlPlaneEndpoint: 192.168.40.199:16443 # VIP
controllerManager: {}
dns: {}
encryptionAlgorithm: RSA-2048
etcd:
  local:
    dataDir: /var/lib/etcd # 设置为提前挂载好的磁盘位置
imageRepository: registry.cn-hangzhou.aliyuncs.com/google_containers
kind: ClusterConfiguration
kubernetesVersion: v1.33.4 # 要与kubeadm version的patch版本保持一致
networking:
  dnsDomain: cluster.local
  podSubnet: 172.16.0.0/16
  serviceSubnet: 10.96.0.0/16
proxy: {}         
scheduler: {}
~~~

2. 更新kubeadm文件：

~~~sh
kubeadm config migrate --old-config kubeadm-config.yaml --new-config kubeadm-config-new.yaml
# 进入kubeadm-config-new.yaml文件，修改一个字段：
timeouts:
  controlPlaneComponentHealthCheck: 4m0s
~~~

3. 复制到其他master节点：==其他节点配置文件不需要更改，包括IP地址也不需要更改==

~~~sh
for i in m02 m03; do scp kubeadm-config-new.yaml $i:/root/; done
~~~

4. 所有Master节点提前下载镜像，可以节省初始化时间：

~~~sh
kubeadm config images pull --config /root/kubeadm-config-new.yaml
~~~

5. 在Master01节点初始化集群，初始化以后会在/etc/kubernetes目录下生成对应的证书和配置文件，之后其他Master节点加入Master01即可：==初始化操作仅在master01节点执行，其它任何节点勿操作==

~~~sh
kubeadm init --config /root/kubeadm-config-new.yaml --upload-certs --ignore-preflight-errors=SystemVerification
~~~

6. 初始化成功以后，控制台输出里面，会产生两个join命令，一个是给control plane用，一个是给data node用：

~~~sh
kubeadm join 192.168.40.199:16443 --token xxx \
--discovery-token-ca-cert-hash sha256:xxx \
--control-plane --certificate-key xxx

kubeadm join 192.168.40.199:16443 --token xxx \
	--discovery-token-ca-cert-hash xxx
~~~

### 加入节点

如果join命令没保存，在master01运行：

~~~sh
kubeadm token create --print-join-command
~~~

1. 在Master02和03上运行join命令加入集群
2. 在Worker nodes上运行join命令加入集群

### 创建kubeconfig

admin.conf是集群的钥匙，安全起见最好是仅在这一台master上执行。如需在其他节点运行，需要拷贝admin.conf到对应节点。

~~~sh
mkdir -p $HOME/.kube
cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
chown $(id -u):$(id -g) $HOME/.kube/config

# 1. 设置kubectl的alias为k：
whereis kubectl ## kubectl: /usr/bin/kubectl
echo "alias k=/usr/bin/kubectl">>/etc/profile
source /etc/profile

# 2. 设置alias的自动补全：
source <(kubectl completion bash | sed 's/kubectl/k/g')

# 3. 解决每次启动k都会失效，要重新刷新环境变量（source /etc/profile）的问题：在~/.bashrc文件中添加以下代码：source /etc/profile
echo "source /etc/profile" >> ~/.bashrc

# 4. 给alias k也配置补全
tee -a ~/.bashrc <<'EOF'
alias k='kubectl'
complete -o default -F __start_kubectl k
source <(kubectl completion bash)
EOF

# 使命令生效
source ~/.bashrc
~~~

### 问题排查

如果初始化失败，使用如下命令重置后再次初始化，命令如下（没有失败不要执行）：

~~~sh
kubeadm reset -f ; ipvsadm --clear  ; rm -rf ~/.kube
~~~

如果多次尝试都是初始化失败，需要看系统日志，CentOS/RockyLinux日志路径:/var/log/messages，Ubuntu系列日志路径/var/log/syslog：

~~~sh
tail -f /var/log/messages | grep -v "not found"
~~~

经常出错的原因：
1.	Containerd的配置文件修改的不对，自行参考《安装containerd》小节核对。（一般伴有PLEG报错信息）
2.	kubeadm yaml配置问题，比如非高可用集群忘记修改16443端口为6443
3.	kubeadm yaml配置问题，三个网段有交叉，出现IP地址冲突
4.	VIP不通导致无法初始化成功，此时messages日志会有VIP超时的报错

## 安装网络插件Calico

所有节点禁止NetworkManager管理Calico的网络接口，防止有冲突或干扰：

~~~sh
cat >>/etc/NetworkManager/conf.d/calico.conf<<EOF
[keyfile]
unmanaged-devices=interface-name:cali*;interface-name:tunl*;interface-name:vxlan.calico;interface-name:vxlan-v6.calico;interface-name:wireguard.cali;interface-name:wg-v6.cali
EOF

systemctl daemon-reload
systemctl restart NetworkManager
~~~

