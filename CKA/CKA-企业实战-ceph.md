# ceph简介

## 类型

- ceph是一种开源的分布式的存储系统，包含以下几种存储类型：

  - 块存储（rbd）
    - 块设备可理解成一块硬盘，用户可以直接使用不含文件系统的块设备，也可以将其格式化成特定的文件系统，由文件系统来组织管理存储空间，从而为用户提供丰富而友好的数据操作支持。
    - linux系统中，ls /dev/下有很多块设备文件，这些文件就是我们添加硬盘时识别出来的；
    - *rbd*就是由Ceph集群提供出来的块设备。可以这样理解，sda是通过数据线连接到了真实的硬盘，而rbd是通过网络连接到了Ceph集群中的一块存储区域，往rbd设备文件写入数据，最终会被存储到Ceph集群的这块区域中；
  - 文件系统（cephfs）
    - 用户可以在块设备上创建xfs、ext4等文件系统，Ceph集群实现了自己的文件系统来组织管理集群的存储空间，用户可以直接将Ceph集群的文件系统挂载到用户机上使用。
    - Ceph有了块设备接口，在块设备上完全可以构建一个文件系统，那么Ceph为什么还需要文件系统接口呢？
      - 主要是因为应用场景的不同，Ceph的块设备具有优异的读写性能，但不能多处挂载同时读写（ReadWriteOnce），目前主要用在OpenStack上作为虚拟磁盘，而Ceph的文件系统接口读写性能较块设备接口差，但具有优异的共享性（ReadWriteMany）。

  - 对象存储(RADOS Fateway)
    - Ceph对象存储使用Ceph对象网关守护进程（radosgw），它是一个用于与Ceph存储集群交互的HTTP服务器。由于它提供与OpenStack Swift和Amazon S3兼容的接口，因此Ceph对象网关具有自己的用户管理。 Ceph对象网关可以将数据存储在用于存储来自Ceph文件系统客户端或Ceph块设备客户端的数据的相同Ceph存储集群中。
    - 使用方式就是通过http协议上传下载删除对象（文件即对象）。
    - ***有了块设备接口存储和文件系统接口存储，为什么还整个对象存储呢\******?\***
      - Ceph的块设备存储具有优异的存储性能但不具有共享性，而Ceph的文件系统具有共享性然而性能较块设备存储差，为什么不权衡一下存储性能和共享性，整个具有共享性而存储性能好于文件系统存储的存储呢，对象存储就这样出现了。

> 分布式存储的优点：
>
> - **高可靠：**既满足存储读取不丢失，还要保证数据长期存储。在保证部分硬件损坏后依然可以保证数据安全。
> - **高性能：**读写速度快。
> - **可扩展：**分布式存储的优势就是“分布式”，所谓的“分布式”就是能够将多个物理节点整合在一起形成共享的存储池，节点可以线性扩充，这样可以源源不断的通过扩充节点提升性能和扩大容量，这是传统存储阵列无法做到的。

## 核心组件

在ceph集群中，不管你是想要提供对象存储，块设备存储，还是文件系统存储，所有Ceph存储集群部署都是从设置每个Ceph节点，网络和Ceph存储开始的。 Ceph存储集群至少需要一个Ceph Monitor，Ceph Manager和Ceph OSD（对象存储守护进程）。运行Ceph Filesystem客户端时也需要Ceph元数据服务器。

- Monitors：
  - Ceph监视器（ceph-mon）维护集群状态的映射，包括监视器映射，管理器映射，OSD映射和CRUSH映射。这些映射是Ceph守护进程相互协调所需的关键集群状态。监视器还负责管理守护进程和客户端之间的身份验证。冗余和高可用性通常至少需要三个监视器。
- Managers：
  - Ceph Manager守护程序（ceph-mgr）负责跟踪运行时指标和Ceph集群的当前状态，包括存储利用率，当前性能指标和系统负载。 Ceph Manager守护进程还托管基于python的模块来管理和公开Ceph集群信息，包括基于Web的Ceph Dashboard和REST API。高可用性通常至少需要两名Managers。
- Ceph OSD：
  - Ceph OSD（对象存储守护进程，ceph-osd）存储数据，处理数据复制，恢复，重新平衡，并通过检查其他Ceph OSD守护进程来获取心跳，为Ceph监视器和管理器提供一些监视信息。冗余和高可用性通常至少需要3个Ceph OSD。
- MDS：
  - Ceph元数据服务器（MDS，ceph-mds）代表Ceph文件系统存储元数据（即，Ceph块设备和Ceph对象存储不使用MDS）。 Ceph元数据服务器允许POSIX文件系统用户执行基本命令（如ls，find等），而不会给Ceph存储集群带来巨大负担。

# 搭建ceph集群准备工作

## 配置3台主机静态IP

- master1-admin是管理节点 ：192.168.40.7
- node1-monitor是监控节点：192.168.40.8
- node2-osd是对象存储节点：192.168.40.9

~~~yaml
#修改/etc/sysconfig/network-scripts/ifcfg-ens33文件，变成如下：
TYPE=Ethernet
PROXY_METHOD=none
BROWSER_ONLY=no
BOOTPROTO=static
IPADDR=192.168.40.200
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
NAME=ens33
DEVICE=ens33
ONBOOT=yes

#修改配置文件之后需要重启网络服务才能使配置生效，重启网络服务命令如下：
service network restart
~~~

## 配置主机名

~~~sh
hostnamectl set-hostname master1-admin && bash
hostnamectl set-hostname node1-monitor && bash
hostnamectl set-hostname node2-osd && bash
~~~

## 配置hosts文件

~~~sh
#3台机器上/etc/hosts中增加：
192.168.40.7   master1-admin  
192.168.40.8   node1-monitor  
192.168.40.9   node2-osd  
~~~

## 配置互相ssh登录

~~~sh
#设置root密码
passwd root
Aa111111111
#以master1-admin为例
ssh-keygen -t rsa
ssh-copy-id master1-admin
ssh-copy-id node1-monitor
ssh-copy-id node2-osd 
~~~

## 关闭防火墙

~~~sh
#3台都执行
systemctl stop firewalld && systemctl disable firewalld
~~~

## 关闭selinux

~~~sh
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
~~~

## 配置ceph源

~~~sh
#3台都执行
yum install -y yum-utils 
yum-config-manager --add-repo https://dl.fedoraproject.org/pub/epel/7/x86_64/ 
yum install --nogpgcheck -y epel-release
rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-7 
rm /etc/yum.repos.d/dl.fedoraproject.org*
~~~

~~~xml
vim /etc/yum.repos.d/ceph.repo

[Ceph]
name=Ceph packages for $basearch
baseurl=http://mirrors.aliyun.com/ceph/rpm-jewel/el7/x86_64/ 
enabled=1 
gpgcheck=0 
type=rpm-md 
gpgkey=https://mirrors.aliyun.com/ceph/keys/release.asc 
priority=1
[Ceph-noarch] 
name=Ceph noarch packages 
baseurl=http://mirrors.aliyun.com/ceph/rpm-jewel/el7/noarch/ 
enabled=1 
gpgcheck=0 
type=rpm-md 
gpgkey=https://mirrors.aliyun.com/ceph/keys/release.asc 
priority=1 
[ceph-source]
name=Ceph source packages 
baseurl=http://mirrors.aliyun.com/ceph/rpm-jewel/el7/SRPMS/ 
enabled=1 
gpgcheck=0 
type=rpm-md 
gpgkey=https://mirrors.aliyun.com/ceph/keys/release.asc 
priority=1
~~~

## 配置时间同步

~~~sh
service ntpd stop
ntpdate cn.pool.ntp.org

crontab -e
* */1 * * * /usr/sbin/ntpdate   cn.pool.ntp.org

service crond restart
~~~

## 安装基础软件包

~~~sh
yum install -y yum-utils device-mapper-persistent-data lvm2 wget net-tools nfs-utils lrzsz gcc gcc-c++ make cmake libxml2-devel openssl-devel curl curl-devel unzip sudo ntp libaio-devel wget vim ncurses-devel autoconf automake zlib-devel  python-devel epel-release openssh-server socat  ipvsadm conntrack ntpdate telnet deltarpm
~~~

# 安装ceph集群

## 安装ceph

~~~sh
#master1-admin上执行，安装ceph-deploy
yum install python-setuptools ceph-deploy -y
#3台上都执行，安装ceph
yum install ceph ceph-radosgw  -y
#确认ceph版本
ceph --version
~~~

## 创建monitor节点

~~~sh
#master1-admin上创建一个目录，用于保存 ceph-deploy 生成的配置文件信息
cd /etc/ceph
ceph-deploy new master1-admin node1-monitor node2-osd
ls
#生成了如下配置文件，Ceph配置文件、一个monitor密钥环和一个日志文件
#ceph.conf  ceph-deploy-ceph.log  ceph.mon.keyring
~~~

## 安装ceph-monitor

~~~sh
#把ceph.conf配置文件里的默认副本数从3改成1 。把osd_pool_default_size = 2 加入[global]段，这样只有2个osd也能达到active+clean状态：
vim /etc/ceph/ceph.conf
[global]
fsid = c617a513-0b8e-40a4-ba5a-741bbc9a13d8
mon_initial_members = master1-admin, node1-monitor, node2-osd
mon_host = 192.168.40.7,192.168.40.8,192.168.40.9
auth_cluster_required = cephx
auth_service_required = cephx
auth_client_required = cephx
osd_pool_default_size = 2
mon clock drift allowed = 0.500 
mon clock drift warn backoff = 10

#mon clock drift allowed ，监视器间允许的时钟漂移量，默认值0.05
#这个设置定义了在发出警告之前，监视器的时间漂移必须超过 mon clock drift allowed 的多少倍。这意味着，如果 mon clock drift allowed 是0.500秒，那么只有当监视器的时间漂移超过5秒时，才会发出警告。
~~~

~~~sh
#初始化monitor，收集所有密钥
#master1-admin上
cd /etc/ceph
ceph-deploy mon create-initial
ls *.keyring
~~~

## 部署osd服务

~~~sh
#准备osd，在master1-admin上
cd /etc/ceph/
ceph-deploy osd prepare master1-admin:/dev/sdc
ceph-deploy osd prepare node1-monitor:/dev/sdc 
ceph-deploy osd prepare node2-osd:/dev/sdc

#激活osd，在master1-admin上
ceph-deploy osd activate master1-admin:/dev/sdc1
ceph-deploy osd activate node1-monitor:/dev/sdc1
ceph-deploy osd activate node2-osd:/dev/sdc1

#查看状态：
ceph-deploy osd list master1-admin node1-monitor node2-osd
~~~

## 创建ceph文件系统

- 要使用Ceph文件系统，你的Ceph的存储集群里至少需要存在一个Ceph的元数据服务器(mds)。

### 创建mds

~~~sh
#master1-admin上
ceph-deploy mds create master1-admin node1-monitor node2-osd
#查看ceph当前文件系统
ceph fs ls   
~~~

> 一个cephfs至少要求两个librados存储池，一个为data，一个为metadata。当配置这两个存储池时，注意：
>
> 1. 为metadata pool设置较高级别的副本级别，因为metadata的损坏可能导致整个文件系统不可用。
> 2. 建议metadata pool使用低延时存储，比如SSD，因为metadata会直接影响客户端的响应速度。

### 创建osd存储池

~~~sh
#master1-admin上
ceph osd pool create cephfs_data 128
ceph osd pool create cephfs_metadata 128
~~~

> 上面的128是pg_num的值，确定 pg_num 取值是强制性的，因为不能自动计算。下面是几个常用的值：
>
> - 少于 5 个 OSD 时可把 pg_num 设置为 128
>
> - OSD 数量在 5 到 10 个时，可把 pg_num 设置为 512
>
> - OSD 数量在 10 到 50 个时，可把 pg_num 设置为 4096
>
> - OSD 数量大于 50 时，你得理解权衡方法、以及如何自己计算 pg_num 取值
>
> 自己计算 pg_num 取值时可借助 pgcalc 工具：随着 OSD 数量的增加，正确的 pg_num 取值变得更加重要，因为它显著地影响着集群的行为、以及出错时的数据持久性（即灾难性事件导致数据丢失的概率）。

### 创建文件系统

~~~sh
ceph fs new hangtestfs cephfs_metadata cephfs_data
#查看创建后的cephfs
ceph fs ls
#查看mds节点状态
ceph mds stat 
#查看存储集群状态信息
ceph -s
~~~

# 测试k8s集群挂载ceph rbd

~~~yaml

~~~





# 基于ceph rbd生成pv