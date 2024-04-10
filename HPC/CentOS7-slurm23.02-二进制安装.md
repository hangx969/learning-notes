# centos7.9部署slurm

- 本篇KB参考文档

  https://zhuanlan.zhihu.com/p/637824704

- 其他部署相关参考文档：

  https://icode.pku.edu.cn/SCOW/docs/slurm

  https://www.jianshu.com/p/37d19a0fe473

- slurm使用参考文档：

  https://docs.hpc.sjtu.edu.cn/job/slurm.html

  https://hpc.pku.edu.cn/_book/guide/quickStart.html

  http://faculty.bicmr.pku.edu.cn/~wenzw/pages/quickstart.html

- PBS官网

  https://slurm.schedmd.com/quickstart_admin.html#Config

## 环境准备

- CentOS 7 - root - root
- 控制节点m1：172.16.183.70/24
- 计算节点c1：172.16.183.71/24
- 计算节点c2：172.16.183.72/24

- gateway：172.16.183.2

- DNS1: 172.16.183.2

## 配置系统

### 设置主机名

~~~sh
hostnamectl set-hostname m1 && bash
hostnamectl set-hostname c1 && bash
hostnamectl set-hostname c2 && bash
~~~

### 添加hosts

~~~sh
cat >> /etc/hosts << EOF
172.16.183.70 m1
172.16.183.71 c1
172.16.183.72 c2
EOF
~~~

### 关闭防火墙

~~~sh
systemctl stop firewalld
systemctl disable firewalld
systemctl stop iptables
systemctl disable iptables
~~~

### 关闭selinux

~~~sh
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
reboot -f
~~~

### 修改资源限制

~~~sh
cat >> /etc/security/limits.conf << EOF
* hard nofile 1000000
* soft nofile 1000000
* soft core unlimited
* soft stack 10240
* soft memlock unlimited
* hard memlock unlimited
EOF
~~~

### 安装epel源

~~~sh
yum -y install http://mirrors.sohu.com/fedora-epel/epel-release-latest-7.noarch.rpm
~~~

### 升级系统至7.9

~~~sh
yum update -y
~~~

### 安装基础软件包

~~~sh
yum install -y device-mapper-persistent-data lvm2 wget net-tools nfs-utils lrzsz gcc gcc-c++ make cmake libxml2-devel openssl-devel curl curl-devel unzip sudo ntp libaio-devel wget vim ncurses-devel autoconf automake zlib-devel  python-devel epel-release openssh-server socat conntrack telnet ipvsadm openssh-clients
~~~

### 配置时区

~~~sh
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

### 关闭订阅管理器

~~~sh
# enabled=0关闭，enabled=1开启
vim /etc/yum/pluginconf.d/subscription-manager.conf
[main]
enabled=0
~~~

## 配置ssh免登录

~~~sh
ssh-keygen
ssh-copy-id -i .ssh/id_rsa.pub m1
ssh-copy-id -i .ssh/id_rsa.pub c1
ssh-copy-id -i .ssh/id_rsa.pub c2
~~~

## 配置nfs

### 控制节点配置nfs

- 安装nfs

~~~sh
yum -y install nfs-utils rpcbind
mkdir /software/
~~~

- 配置共享目录

```sh
vim /etc/exports
/software/ *(rw,async,insecure,no_root_squash)
# rw：读写的权限
# sync：表示文件同时写入硬盘和内存
# no_root_squash：当登录 NFS 主机使用共享目录的使用者是 root 时，其权限将被转换成为匿名使用者，通常它的 UID 与 GID，都会变成 nobody 身份
exportfs -arv
```

- 启动nfs

~~~sh
systemctl start nfs
systemctl start rpcbind
systemctl enable nfs
systemctl enable rpcbind
~~~

- 确认nfs启动

~~~sh
rpcinfo -p | grep nfs
#查看挂载权限
showmount -e 172.16.183.70
~~~

### 客户端挂载nfs

~~~sh
yum -y install nfs-utils
mkdir /software
mount 172.16.183.70:/software /software
#fstab挂载nfs
~~~

## 配置Munge

### 创建munge用户

- Munge用户要确保Master Node和Compute Nodes的UID和GID相同，所有节点都需要安装Munge；

~~~sh
#所有节点上
groupadd -g 1108 munge
useradd -m -c "Munge Uid 'N' Gid Emporium" -d /var/lib/munge -u 1108 -g munge -s /sbin/nologin munge
#-m：这个选项告诉 useradd 命令为新用户创建一个主目录。
#-c "Munge Uid 'N' Gid Emporium"：这个选项用于设置新用户的注释字段，通常用于存储用户的全名或其他信息。在这里，它被设置为 "Munge Uid 'N' Gid Emporium"。
#-d /var/lib/munge：这个选项用于指定新用户的主目录。在这里，主目录被设置为 /var/lib/munge。
#-u 1108：这个选项用于指定新用户的用户 ID（UID） 被设置为 1108。
#-g munge：这个选项用于指定新用户的初始登录组，被设置为 munge。
#-s /sbin/nologin：这个选项用于指定新用户的登录 shell。在这里，shell 被设置为 /sbin/nologin，这意味着用户不能登录到系统。
#munge：这是新创建的用户名。
~~~

### 生成熵池

~~~sh
#管理节点上
yum install -y rng-tools
~~~

- 使用/dev/urandom来做熵源

~~~sh
#管理节点上
rngd -r /dev/urandom
vim /usr/lib/systemd/system/rngd.service 
#修改如下参数
[Service]
ExecStart=/sbin/rngd -f -r /dev/urandom

systemctl daemon-reload
systemctl start rngd
systemctl enable rngd
~~~

### 部署munge

- 安装munge

~~~sh
# 安装 munge
# 管理节点
yum -y install munge munge-libs munge-devel
# 在管理节点执行，给计算节点安装munge
for i in `seq 1 2`; do ssh c$i yum -y install munge munge-libs munge-devel -y; done
~~~

- 创建全局秘钥

~~~sh
#在Master Node生成全局使用的秘钥文件：/etc/munge/munge.key
dd if=/dev/urandom bs=1 count=1024 > /etc/munge/munge.key
#或者
create-munge-key
~~~

- 密钥同步到所有计算节点

~~~sh
# Master Node执行
for i in `seq 1 2`; do scp /etc/munge/munge.key root@c$i:/etc/munge/ ; done
# 计算节点执行
chown munge: /etc/munge/munge.key
chmod 400 /etc/munge/munge.key
~~~

- 检查账户是否存在

~~~sh
#master node执行
for i in `seq 1 2`;do ssh c$i id munge;done
#uid=1108(munge) gid=1108(munge) groups=1108(munge)
#uid=1108(munge) gid=1108(munge) groups=1108(munge)
~~~

- 修改配置属主，启动所有节点

~~~sh
#master节点
chown munge: /etc/munge/munge.key
chmod 400 /etc/munge/munge.key
systemctl start munge
systemctl enable munge
~~~

~~~sh
# 设置各计算节点/etc/munge/munge.key  所有者为munge，并检查是否设置成功
for i in `seq 1 2`;do ssh c$i chown munge.munge /etc/munge/munge.key;ls -l /etc/munge/munge.key;done
# 设置各节点开机自动启动munge服务
for i in `seq 1 2`;do ssh c$i systemctl enable --now munge;done
# 重启并检查所有节点
for i in `seq 1 2`;do ssh c$i systemctl restart munge ;done
for i in `seq 1 2`;do ssh c$i ps -ef|grep munge ;done
~~~

### 测试munge服务

每个计算节点与控制节点进行连接验证

- 本地查看凭据

```sh
munge -n
```

- 本地解码

```sh
munge -n | unmunge
```

- 验证compute node，控制节点进行连接验证

```sh
munge -n | ssh m1 unmunge
```

- Munge凭证基准测试

```sh
remunge
```

## 配置slurm

### 创建slurm用户

~~~sh
#所有节点上
groupadd -g 1109 slurm
useradd -m -c "Slurm manager" -d /var/lib/slurm -u 1109 -g slurm -s /bin/bash slurm
~~~

- 检查slurm用户存在

~~~sh
for i in `seq 1 2`; do ssh c$i id slurm; done
~~~

### 安装slurm依赖

~~~sh
#所有节点
yum install gcc gcc-c++ readline-devel perl-ExtUtils-MakeMaker pam-devel rpm-build mysql-devel http-parser-devel json-c-devel libjwt  libjwt-devel python3 -y
~~~

### 编译slurm

~~~sh
#在master上执行
# wget https://download.schedmd.com/slurm/slurm-19.05.7.tar.bz2 
wget https://download.schedmd.com/slurm/slurm-23.02.2.tar.bz2
rpmbuild -ta --with mysql --with slurmrestd --with jwt slurm-23.02.2.tar.bz2

cd /root/rpmbuild/RPMS/x86_64/
yum localinstall -y slurm-*
~~~

### 设置Slurm的YUM仓库

```bash
# master节点，建立YUM仓库目录，把rpm包放到共享目录里面
mkdir -p /software/src/slurm
cp /root/rpmbuild/RPMS/x86_64/*.rpm /software/src/slurm/
```

- 建立YUM仓库RPM文件索引

```bash
#master节点
yum install createrepo -y
cd /software/src/slurm/ && createrepo .
```

- 生成repo配置文件

```bash
cat >/etc/yum.repos.d/slurm.repo<<EOF
[slurm]
name=slurm
baseurl=file:///software/src/slurm
gpgcheck=0
enable=1
EOF
```

- 为其它节点设置YUM仓库

```bash
for i in `seq 1 2`;do scp -p /etc/yum.repos.d/slurm.repo  root@c$i:/etc/yum.repos.d/;done
```

- 计算节点安装slurm

~~~sh
for i in `seq 1 2`;do ssh c$i yum -y install slurm slurm-perlapi slurm-slurmd;done
~~~

### 配置控制节点slurm

~~~sh
#master节点上
vim /etc/slurm/slurm.conf

ClusterName=cluster-test
ControlMachine=m1 # 控制节点的名称
ControlAddr=172.16.183.70 #控制节点的 IP
SlurmctldDebug=info
SlurmdDebug=debug3
GresTypes=gpu
MpiDefault=none
ProctrackType=proctrack/cgroup
SlurmctldPidFile=/var/run/slurmctld.pid
SlurmctldPort=6817
SlurmdPidFile=/var/run/slurmd.pid
SlurmdPort=6818
SlurmdSpoolDir=/var/spool/slurm
SlurmUser=slurm
StateSaveLocation=/var/spool/slurm/ctld
SwitchType=switch/none
TaskPlugin=task/affinity,task/cgroup
TaskPluginParam=verbose
MinJobAge=172800
AccountingStorageEnforce=associations
AccountingStorageHost=m1
AccountingStoragePort=6819
AccountingStorageType=accounting_storage/slurmdbd
AccountingStoreFlags=job_comment
SlurmctldLogFile=/var/log/slurm/slurmctld.log
SlurmdLogFile=/var/log/slurm/slurmd.log
#AuthAltTypes=auth/jwt
#AuthAltParameters=jwt_key=/var/spool/slurm/ctld/jwt_hs256.key
NodeName=m1,c[1-2] CPUs=2 RealMemory=1024 State=UNKNOWN # 控制节点的名称，计算节点名称
PartitionName=compute Nodes=c[1-2] Default=YES MaxTime=INFINITE State=UP #Nodes  计算节点的名称
~~~

### 配置同步/权限修改

~~~sh
# 复制配置文件（Master node执行）
for i in `seq 1 2`;do ssh c$i mkdir -p /etc/slurm ;done
for i in `seq 1 2`;do scp -p /etc/slurm/*.conf  root@c$i:/etc/slurm/;done
# 设置文件权限，所有节点执行
for i in `seq 1 2`;do ssh c$i mkdir -p /var/spool/slurm ;done
for i in `seq 1 2`;do ssh c$i chown slurm: /var/spool/slurm;done #只改属主
for i in `seq 1 2`;do ssh c$i mkdir -p /var/log/slurm;done
for i in `seq 1 2`;do ssh c$i chown slurm: /var/log/slurm;done
~~~

- 检查slurm配置是否正确

~~~sh
slurmd -C
~~~

## 搭建slurmdbd-mysql

### 安装MariaDB

~~~sh
cd /etc/yum.repos.d/
vim MariaDB.repo
~~~

- 打开[https://downloads.mariadb.org/mariadb/repositories/](https://link.jianshu.com/?t=https://downloads.mariadb.org/mariadb/repositories/)，选择CentOS版本后，生成repo内容，粘贴到MariaDB.repo

~~~sh
yum install -y MariaDB-server
~~~

### 配置MariaDB

~~~sh
service mysql start
#mysql_secure_installation
systemctl enable mariadb.service
systemctl status mariadb.service
mysql -u root -p
#设置密码为root
~~~

### 安装slurm accounting

- Accounting records可以为slurm收集每个作业步骤的信息。Accounting records可以写入一个简单的文本文件或数据库。

- 通过将文本文件指定为Accounting存储类型从而可以轻松地将数据存储到文本文件中。但是这个文件会变得越来越大，难以使用。因此，最简单且推荐的方法是使用数据库来存储信息。而Mysql是目前唯一支持的数据库。
- 创建slurm_acct_db数据库

~~~sh
mysql -u root -p

#slurm_acct_db数据库的配置
grant all on slurm_acct_db.* to 'slurm'@'172.16.183.%' identified by '!QAZ2wsx3edc' with grant option;
grant all on slurm_acct_db.* to 'slurm'@'localhost' identified by '!QAZ2wsx3edc' with grant option;
SHOW VARIABLES LIKE 'have_innodb';
create database slurm_acct_db;
quit;
~~~

### 配置slurmdbd.conf文件

~~~sh
cp /etc/slurm/slurmdbd.conf.example /etc/slurm/slurmdbd.conf
chown slurm: /etc/slurm/slurmdbd.conf
chmod 600 /etc/slurm/slurmdbd.conf
mkdir /var/log/slurm/
touch /var/log/slurm/slurmdbd.log
chown slurm: /var/log/slurm/slurmdbd.log
~~~

~~~sh
vim /etc/slurm/slurmdbd.conf

LogFile=/var/log/slurm/slurmdbd.log
DbdHost=localhost
DbdPort=6819
slurmUser=slurm
StorageHost=localhost
StoragePass=!QAZ2wsx3edc
StorageLoc=slurm_acct_db
~~~

### 创建systemd文件

~~~sh
cp /usr/lib/systemd/system/slurmctld.service /usr/lib/systemd/system/slurmd.service /usr/lib/systemd/system/slurmdbd.service /etc/systemd/system/
cat /etc/systemd/system/slurmctld.service
~~~

### 修改slurm.conf文件

~~~sh
vim /etc/slurm/slurm.conf

#在AccountingStorageType=accounting_storage/mysql后添加
AccountingStorageHost=localhost
AccountingStoragePort=3306
AccountingStoragePass=!QAZ2wsx3edc
AccountingStorageUser=slurm
~~~

### 启动SlurmDBD服务

~~~sh
systemctl enable slurmdbd
systemctl start slurmdbd
systemctl status slurmdbd
~~~

## 搭建slurmdbd-docker方法

### MariaDB搭建(docker)

- 初始化宿主机目录

```sh
mkdir -p /docker_data/mariadb/{log,data,conf}
```

- 修改数据库必备参数

```bash
vim /docker_data/mariadb/conf/my.cnf 
[mysqld]
 innodb_buffer_pool_size=1024M
 innodb_log_file_size=64M
 innodb_lock_wait_timeout=900

 character-set-server=utf8mb4

[client-server]
# Port or socket location where to connect
# port = 3306
#socket = /run/mysqld/mysqld.sock

socket = /var/lib/mysql/mysql.sock
```

- 安装docker

~~~sh
yum install -y yum-utils
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
yum install docker-ce docker-ce-cli containerd.io docker-compose-plugin
systemctl start docker
systemctl enable docker
~~~

- 启动db

~~~sh
docker run --name slurmdb -d -p 3306:3306 --env MARIADB_DATABASE=slurm_acct_db --env MARIADB_USER=root --env MARIADB_PASSWORD=123 --env MARIADB_ROOT_PASSWORD=123 -v /docker_data/mariadb/log:/var/log/mysql -v /docker_data/mariadb/data:/var/lib/mysql -v /docker_data/mariadb/conf:/etc/mysql/conf.d mariadb:11
~~~

- 检查参数生效

~~~sh
mysql -h m1 -P 3306 -u slurm slurm_acct_db -p
SHOW GLOBAL VARIABLES like 'innodb_buffer_pool_size';
~~~

- 设置数据库权限

~~~sh
mysql -h m1 -P 3306 -u root slurm_acct_db -p
# 生成slurm用户，以便该用户操作slurm_acct_db数据库，其密码是123
create user 'slurm'@'localhost' identified by '123';

# 生成账户数据库slurm_acct_db
CREATE DATABASE IF NOT EXISTS slurm_acct_db;
# 赋予slurm从本机localhost采用密码SomePassWD登录具备操作slurm_acct_db数据下所有表的全部权限
grant all on slurm_acct_db.* TO 'slurm'@'localhost' identified by '123' with grant option;
# 赋予slurm从system0采用密码123登录具备操作slurm_acct_db数据下所有表的全部权限
grant all on slurm_acct_db.* TO 'slurm'@'system0' identified by '123' with grant option;
#grant all on slurm_acct_db.* TO 'slurm'@'%' identified by '123' with grant option;

# 生成作业信息数据库slurm_jobcomp_db
create database slurm_jobcomp_db;
# 赋予slurm从本机localhost采用密码SomePassWD登录具备操作slurm_jobcomp_db数据下所有表的全部权限
grant all on slurm_jobcomp_db.* TO 'slurm'@'localhost' identified by '123' with grant option;
# 赋予slurm从m1采用密码SomePassWD登录具备操作slurm_jobcomp_db数据下所有表的全部权限
grant all on slurm_jobcomp_db.* TO 'slurm'@'m1' identified by '123' with grant option;
#grant all on slurm_jobcomp_db.* TO 'slurm'@'%' identified by '123' with grant option;
~~~

- 修改slurmdbd.conf配置

~~~sh
cp /etc/slurm/slurmdbd.conf.example /etc/slurm/slurmdbd.conf
~~~

~~~sh
#
# Example slurmdbd.conf file.
#
# See the slurmdbd.conf man page for more information.
#
# Archive info
#ArchiveJobs=yes
#ArchiveDir="/tmp"
#ArchiveSteps=yes
#ArchiveScript=
#JobPurge=12
#StepPurge=1
#
# Authentication info
AuthType=auth/munge
AuthInfo=/var/run/munge/munge.socket.2
#
# slurmDBD info
#DbdAddr=localhost
# 控制节点IP
DbdAddr=172.16.183.70
#DbdHost=localhost
DbdHost=m1
#DbdPort=7031
SlurmUser=slurm
#MessageTimeout=300
DebugLevel=verbose
#DefaultQOS=normal,standby
DefaultQOS=normal

LogFile=/var/log/slurm/slurmdbd.log
PidFile=/var/run/slurmdbd.pid
#PluginDir=/usr/lib/slurm
#PrivateData=accounts,users,usage,jobs
#TrackWCKey=yes
#
# Database info
StorageType=accounting_storage/mysql #StorageType=accounting_storage/slurmdbd is invalid in slurmdbd.conf
# 存储数据库地址
StorageHost=172.16.183.70
#StorageHost=localhost

StoragePort=3306
#StoragePort=1234
StoragePass=123
StorageUser=slurm
StorageLoc=slurm_acct_db
~~~

### 设置slurm文件、目录、权限

~~~sh
# /etc/slurm/slurmdbd.conf文件所有者须为slurm用户
chown slurm.slurm /etc/slurm/slurmdbd.conf
# /etc/slurm/slurmdbd.conf文件权限须为600
chmod 600 /etc/slurm/slurmdbd.conf
# /etc/slurm/slurm.conf文件所有者须为root用户
chown root /etc/slurm/slurm.conf

# 建立slurmctld服务存储其状态等的目录，由slurm.conf中StateSaveLocation参数定义：
mkdir /var/spool/slurmctld
# 设置/var/spool/slurmctld目录所有者为slurm用户：
chown slurm.slurm /var/spool/slurmctld
~~~

### 添加JWT键到控制器

~~~sh
mkdir -p /var/spool/slurm/ctld
dd if=/dev/random of=/var/spool/slurm/ctld/jwt_hs256.key bs=32 count=1
chown slurm:slurm /var/spool/slurm/ctld/jwt_hs256.key
chmod 0600 /var/spool/slurm/ctld/jwt_hs256.key
# chown root:root /etc/slurm
chmod 0755 /var/spool/slurm/ctld
chown slurm:slurm /var/spool/slurm/ctld
~~~

## 启动服务

~~~sh
# 启动控制节点Slurmdbd服务
systemctl restart slurmdbd && systemctl status slurmdbd
systemctl enable slurmdbd
# 启动控制节点slurmctld服务
systemctl restart slurmctld && systemctl status slurmctld
systemctl enable slurmctld
# 启动计算节点的服务
systemctl restart slurmd && systemctl status slurmd
systemctl enable slurmd
~~~

# Ubuntu 2204部署Slurm

## 实验机器规划

- OS：[ubuntu-22.04.4-live-server-amd64.iso](https://mirrors.tuna.tsinghua.edu.cn/ubuntu-releases/22.04/ubuntu-22.04.4-live-server-amd64.iso)

- 2vcpu，4GB内存。

- User：

  - hangx hangx
  - root root

- IP地址规划

  - 172.16.183.130 um1

  - 172.16.183.131 uc1

## 环境准备

- IP配置

  - Ubuntu系统安装时，可以在网卡配置页面，将ens33设置为静态IP。

  - Gateway: 172.16.183.2

  - name servers: 8.8.8.8,114.114.114.114


~~~sh
sudo vim /etc/netplan/00-installer-config.yaml
# This is the network config written by 'subiquity'
network:
  ethernets:
    ens33:
      addresses:
      - 172.16.183.130/24
      nameservers:
        addresses:
        - 8.8.8.8
        - 114.114.114.114
      routes:
      - to: default
        via: 172.16.183.2
  version: 2
~~~

- apt源设置

  - Ubuntu系统安装时，在mirror address页面上，配置为清华镜像源： https://mirrors.tuna.tsinghua.edu.cn/help/ubuntu/

  - 设置主机名


~~~sh
sudo hostnamectl set-hostname um1 && bash
sudo hostnamectl set-hostname uc1 && bash
~~~

- 添加hosts

~~~sh
cat >> /etc/hosts << EOF
172.16.183.130 um1
172.16.183.131 uc1
EOF
~~~

- 修改资源限制

~~~sh
cat >> /etc/security/limits.conf << EOF
* hard nofile 1000000
* soft nofile 1000000
* soft core unlimited
* soft stack 10240
* soft memlock unlimited
* hard memlock unlimited
EOF
~~~

- 配置时区

~~~sh
#安装ntpdate命令
apt install ntpdate -y
#跟网络时间做同步
ntpdate cn.pool.ntp.org
#把时间同步做成计划任务
crontab -e
* */1 * * * /usr/sbin/ntpdate   cn.pool.ntp.org
#重启crond服务
systemctl restart cron
~~~

- 配置ssh免登录

~~~sh
ssh-keygen
ssh-copy-id -i ~/.ssh/id_rsa.pub um1
ssh-copy-id -i ~/.ssh/id_rsa.pub uc1
~~~

## 配置munge

- Munge用户要确保Master Node和Compute Nodes的UID和GID相同，所有节点都需要安装Munge；

~~~sh
#所有节点上
groupadd -g 1108 munge
useradd -m -c "Munge Uid 'N' Gid Emporium" -d /var/lib/munge -u 1108 -g munge -s /sbin/nologin munge
#-m：这个选项告诉 useradd 命令为新用户创建一个主目录。
#-c "Munge Uid 'N' Gid Emporium"：这个选项用于设置新用户的注释字段，通常用于存储用户的全名或其他信息。在这里，它被设置为 "Munge Uid 'N' Gid Emporium"。
#-d /var/lib/munge：这个选项用于指定新用户的主目录。在这里，主目录被设置为 /var/lib/munge。
#-u 1108：这个选项用于指定新用户的用户 ID（UID） 被设置为 1108。
#-g munge：这个选项用于指定新用户的初始登录组，被设置为 munge。
#-s /sbin/nologin：这个选项用于指定新用户的登录 shell。在这里，shell 被设置为 /sbin/nologin，这意味着用户不能登录到系统。
#munge：这是新创建的用户名。
~~~

- 生成熵池

~~~sh
#管理节点上
apt install -y rng-tools
~~~

- 使用/dev/urandom来做熵源

~~~sh
#管理节点上
rngd -r /dev/urandom
tee /usr/lib/systemd/system/rngd.service <<'EOF'
[Service]
ExecStart=/sbin/rngd -f -r /dev/urandom
[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl start rngd
systemctl enable rngd
~~~

- 安装munge

~~~sh
# 安装 munge
# 管理节点
apt -y install munge
# 在管理节点执行，给计算节点安装munge
for i in `seq 1`; do ssh uc$i apt -y install munge -y; done
~~~

- 创建全局秘钥

~~~sh
#在Master Node生成全局使用的秘钥文件：/etc/munge/munge.key
dd if=/dev/urandom bs=1 count=1024 > /etc/munge/munge.key
#或者
create-munge-key
~~~

- 密钥同步到所有计算节点

~~~sh
# Master Node执行，把munge key同步到计算节点
for i in `seq 1`; do scp /etc/munge/munge.key root@uc$i:/etc/munge/ ; done
# 计算节点执行
chown munge: /etc/munge/munge.key
chmod 400 /etc/munge/munge.key
~~~

- 检查账户是否存在

~~~sh
#master node执行
for i in `seq 1`;do ssh uc$i id munge;done
#uid=1108(munge) gid=1108(munge) groups=1108(munge)
~~~

- 修改配置属主，启动所有节点

~~~sh
#master节点
chown munge: /etc/munge/munge.key
chmod 400 /etc/munge/munge.key
systemctl start munge
systemctl enable munge
systemctl status munge
~~~

~~~sh
# 设置各计算节点/etc/munge/munge.key  所有者为munge，并检查是否设置成功
for i in `seq 1`;do ssh uc$i chown munge.munge /etc/munge/munge.key;ls -l /etc/munge/munge.key;done
# 设置各节点开机自动启动munge服务
for i in `seq 1`;do ssh uc$i systemctl enable --now munge;done
# 重启并检查所有节点
for i in `seq 1`;do ssh uc$i systemctl restart munge ;done
for i in `seq 1`;do ssh uc$i ps -ef|grep munge ;done
~~~

- 测试munge服务: 每个计算节点与控制节点进行连接验证

- 本地查看凭据

```sh
munge -n
```

- 本地解码

```sh
munge -n | unmunge
```

- 验证compute node，控制节点进行连接验证

```sh
munge -n | ssh um1 unmunge
munge -n | ssh uc1 unmunge
```

- Munge凭证基准测试

```sh
remunge
```

## 配置slurm

- 创建slurm用户

~~~sh
#所有节点上
groupadd -g 1109 slurm
useradd -m -c "Slurm manager" -d /var/lib/slurm -u 1109 -g slurm -s /bin/bash slurm
~~~

- 检查slurm用户存在

~~~sh
for i in `seq 1`; do ssh uc$i id slurm; done
~~~

- 编译安装slurm - 计算和控制节点

  https://slurm.schedmd.com/quickstart_admin.html#debuild

~~~sh
wget https://download.schedmd.com/slurm/slurm-23.11.4.tar.bz2
#Install basic Debian package build requirements:
apt-get install build-essential fakeroot devscripts equivs
#Unpack the distributed tarball:
tar -xaf slurm*tar.bz2
cd slurm-23.11.4
#Install the Slurm package dependencies:
#mk-build-deps是一个用于处理Debian包构建依赖的工具。它可以创建一个虚拟的Debian包，这个虚拟的包依赖于你的源代码包的所有构建依赖。当你安装这个虚拟的包时，所有的构建依赖也会被自动安装。-i选项告诉mk-build-deps在创建虚拟的包之后，立即尝试安装它。debian/control是Debian包的控制文件，它包含了关于包的元数据，例如包的名称、版本、描述，以及构建依赖等信息。
mk-build-deps -i debian/control
#Build the Slurm packages:
#构建二进制包，但不对改变的文件和源代码包进行签名。这个命令通常在你信任源代码，并且不需要签名的情况下使用。
debuild -b -uc -us
~~~

- The packages will be in the parent directory after debuild completes.

  ~~~sh
  #um1上
  dpkg -i slurm-smd_23.11.4-1_amd64.deb
  dpkg -i slurm-smd-slurmctld_23.11.4-1_amd64.deb
  dpkg -i slurm-smd-client_23.11.4-1_amd64.deb
  dpkg -i slurm-smd-slurmdbd_23.11.4-1_amd64.deb
  #uc1上
  dpkg -i slurm-smd_23.11.4-1_amd64.deb
  dpkg -i slurm-smd-slurmd_23.11.4-1_amd64.deb
  dpkg -i slurm-smd-client_23.11.4-1_amd64.deb
  #ul1上
  dpkg -i slurm-smd_23.11.4-1_amd64.deb
  dpkg -i slurm-smd-client_23.11.4-1_amd64.deb
  ~~~

- 配置控制节点slurm

  ~~~sh
  #查看CPUs
  nproc
  #查看Sockets、CoresPerSocket、ThreadsPerCore
  lscpu
  #查看RealMemory
  free -m
  ~~~

~~~sh
#master节点上
tee /etc/slurm/slurm.conf << 'EOF'

# slurm.conf file generated by configurator.html.
# Put this file on all nodes of your cluster.
# See the slurm.conf man page for more information.
#
ClusterName=ubuntutestcluster
SlurmctldHost=um1
#SlurmctldHost=
#
#DisableRootJobs=NO
#EnforcePartLimits=NO
#Epilog=
#EpilogSlurmctld=
#FirstJobId=1
#MaxJobId=67043328
#GresTypes=
#GroupUpdateForce=0
#GroupUpdateTime=600
#JobFileAppend=0
#JobRequeue=1
#JobSubmitPlugins=lua
#KillOnBadExit=0
#LaunchType=launch/slurm
#Licenses=foo*4,bar
#MailProg=/bin/mail
#MaxJobCount=10000
#MaxStepCount=40000
#MaxTasksPerNode=512
#MpiDefault=
#MpiParams=ports=#-#
#PluginDir=
#PlugStackConfig=
#PrivateData=jobs
ProctrackType=proctrack/cgroup
#Prolog=
#PrologFlags=
#PrologSlurmctld=
#PropagatePrioProcess=0
#PropagateResourceLimits=
#PropagateResourceLimitsExcept=
#RebootProgram=
ReturnToService=1
SlurmctldPidFile=/var/run/slurmctld.pid
SlurmctldPort=6817
SlurmdPidFile=/var/run/slurmd.pid
SlurmdPort=6818
SlurmdSpoolDir=/var/spool/slurm/slurmd
SlurmUser=slurm
#SlurmdUser=root
#SrunEpilog=
#SrunProlog=
StateSaveLocation=/var/spool/slurm/slurmctld
#SwitchType=
#TaskEpilog=
TaskPlugin=task/affinity,task/cgroup
#TaskProlog=
#TopologyPlugin=topology/tree
#TmpFS=/tmp
#TrackWCKey=no
#TreeWidth=
#UnkillableStepProgram=
#UsePAM=0
#
#
# TIMERS
#BatchStartTimeout=10
#CompleteWait=0
#EpilogMsgTime=2000
#GetEnvTimeout=2
#HealthCheckInterval=0
#HealthCheckProgram=
InactiveLimit=0
KillWait=30
#MessageTimeout=10
#ResvOverRun=0
MinJobAge=300
#OverTimeLimit=0
SlurmctldTimeout=120
SlurmdTimeout=300
#UnkillableStepTimeout=60
#VSizeFactor=0
Waittime=0
#
#
# SCHEDULING
#DefMemPerCPU=0
#MaxMemPerCPU=0
#SchedulerTimeSlice=30
SchedulerType=sched/backfill
SelectType=select/cons_tres
#
#
# JOB PRIORITY
#PriorityFlags=
#PriorityType=priority/multifactor
#PriorityDecayHalfLife=
#PriorityCalcPeriod=
#PriorityFavorSmall=
#PriorityMaxAge=
#PriorityUsageResetPeriod=
#PriorityWeightAge=
#PriorityWeightFairshare=
#PriorityWeightJobSize=
#PriorityWeightPartition=
#PriorityWeightQOS=
#
#
# LOGGING AND ACCOUNTING
#AccountingStorageEnforce=0
#AccountingStorageHost=
#AccountingStoragePass=
#AccountingStoragePort=
#AccountingStorageType=
#AccountingStorageUser=
#AccountingStoreFlags=
#JobCompHost=
#JobCompLoc=
#JobCompParams=
#JobCompPass=
#JobCompPort=
JobCompType=jobcomp/none
#JobCompUser=
#JobContainerType=
JobAcctGatherFrequency=30
#JobAcctGatherType=
SlurmctldDebug=info
SlurmctldLogFile=/var/log/slurm/slurmctld.log
SlurmdDebug=info
SlurmdLogFile=/var/log/slurm/slurmd.log
#SlurmSchedLogFile=
#SlurmSchedLogLevel=
#DebugFlags=
#
#
# POWER SAVE SUPPORT FOR IDLE NODES (optional)
#SuspendProgram=
#ResumeProgram=
#SuspendTimeout=
#ResumeTimeout=
#ResumeRate=
#SuspendExcNodes=
#SuspendExcParts=
#SuspendRate=
#SuspendTime=
#
#
# COMPUTE NODES
NodeName=uc1 NodeAddr=172.16.183.131 CPUs=2 RealMemory=3969468 Sockets=2 CoresPerSocket=1 ThreadsPerCore=1 State=UNKNOWN
PartitionName=debug Nodes=ALL Default=YES MaxTime=1 State=UP
EOF
~~~

- 配置同步/权限修改

~~~sh
# 复制配置文件（Master node执行）
for i in `seq 1`;do ssh uc$i mkdir -p /etc/slurm ;done
for i in `seq 1`;do scp -p /etc/slurm/*.conf  root@uc$i:/etc/slurm/;done
# 设置文件权限，所有节点执行
#chmod 0755 /var/spool
#chown -R slurm:slurm /var/spool
mkdir -p /var/spool/slurm
chown slurm: /var/spool/slurm
mkdir -p /var/log/slurm
chown slurm: /var/log/slurm
for i in `seq 1`;do ssh uc$i mkdir -p /var/spool/slurm;done
for i in `seq 1`;do ssh uc$i chown slurm: /var/spool/slurm;done
for i in `seq 1`;do ssh uc$i mkdir -p /var/log/slurm;done
for i in `seq 1`;do ssh uc$i chown slurm: /var/log/slurm;done
~~~

## 启动服务

~~~sh
#um1上
systemctl enable slurmctld
systemctl start slurmctld
systemctl status slurmctld
#uc1上
systemctl enable slurmd
systemctl start slurmd
systemctl status slurmd
~~~

# 作业调度测试

## 查看集群状态

~~~sh
# 查看集群
sinfo
scontrol show partition
scontrol show node

# 提交作业 
srun -N1 hostname
scontrol show jobs

# 查看作业
squeue -a

#计算节点查看slurmd报错
sudo slurmd -cDvvvvv

#重启控制节点组件
systemctl daemon-reload && systemctl restart slurmctld && systemctl restart slurmdbd
systemctl status slurmctld && systemctl status slurmdbd

#重启计算节点组件
systemctl daemon-reload && systemctl restart slurmd && systemctl status slurmd

#恢复计算节点状态
#如果Compute Nodes的State=DOWN，则如下执行，将状态变成恢复
scontrol update nodename=c1 state=resume
~~~

## 交互式提交作业

~~~sh
# --mem=5M表示申请5MB内存，-c 1表示申请1个核心。
srun -p compute -w c1 --mem=5M -c 1 hostname
srun -J sample-job -p compute -N 2 -c 1 -n 1 whoami;hostname;ip a;
srun -J my-sleep -p compute -w c[1-2] -N 2 -c 1 -n 1 sleep 10
srun -p compute -w c1 sh ./a.sh
~~~

- 推荐使用squeue时指定输出格式如下

```text
squeue -o "%.5i %.10u %.2t %.10M %.6D %.4C %.7m   %R"
```

- 查看已经运行任务

```bash
sacct  -o jobid,jobname,partition,alloccpus,state,reqmem,averss,maxrss,exitcode  -j jobid
```

## sbatch提交作业

~~~sh
#!/bin/bash
#SBATCH -J test             # 作业名是 test
#SBATCH -p cpu              # 提交到 cpu分区
#SBATCH -N 1                # 使用一个节点
#SBATCH --cpus-per-task=1   # 每个进程占用一个 cpu核心
#SBATCH -t 5:00             # 任务最大运行时间是5分钟
#SBATCH -o test.out         # 将屏幕的输出结果保存到当前文件夹的test.out，问题：并未有输出
hostname                    # 执行我的hostname命令

sbatch test.sh #提交作业
~~~

- 查看作业运行信息

```bash
sacct  -o jobid,jobname,partition,alloccpus,state,reqmem,averss,maxrss,exitcode  -j job-id
```

## 示例python作业

~~~python
#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# SBATCH --output=/root/python_slurm.log
# SBATCH --partition=compute
# SBATCH -n 1 # 1 cores
import os
import sys
from threading import Thread
from time import sleep, ctime

sys.path.append(os.getcwd())


class MyClass(object):

    def func(self, name, sec):
        print('---Start---', name, 'time', ctime())
        sleep(sec)
        print('***End***', name, 'time', ctime())


def main():
    # 创建 Thread 实例
    t1 = Thread(target=MyClass().func, args=(1, 1))
    t2 = Thread(target=MyClass().func, args=(2, 2))

    # 启动线程运行
    t1.start()
    t2.start()

    # 等待所有线程执行完毕
    t1.join()  # join() 等待线程终止，要不然一直挂起
    t2.join()

    
if __name__ == "__main__":
    main()
scp thread_demo.py root@c1:/root
srun python /root/thread_demo.py 
cpu-bind=MASK - c1, task  0  0 [8685]: mask 0x1 set
('---Start---', 1, 'time', 'Thu Jun 15 19:17:46 2023')
('---Start---', 2, 'time', 'Thu Jun 15 19:17:46 2023')
('***End***', 1, 'time', 'Thu Jun 15 19:17:47 2023')
('***End***', 2, 'time', 'Thu Jun 15 19:17:48 2023')
~~~

- python提交作业

~~~python
#!/usr/bin/env python3

import subprocess
"""
#提交单个作业
#SBATCH --job-name=JOBNAME      %指定作业名称
#SBATCH --partition=debug       %指定分区
#SBATCH --nodes=2               %指定节点数量
#SBATCH --cpus-per-task=1       %指定每个进程使用核数，不指定默认为1
#SBATCH -n 32       %指定总进程数；不使用cpus-per-task，可理解为进程数即为核数
#SBATCH --ntasks-per-node=16    %指定每个节点进程数/核数,使用-n参数（优先级更高），变为每个节点最多运行的任务数
#SBATCH --nodelist=node[3,4]    %指定优先使用节点
#SBATCH --exclude=node[1,5-6]   %指定避免使用节点
#SBATCH --time=dd-hh:mm:ss      %作业最大运行时长，参考格式填写
#SBATCH --output=file_name      %指定输出文件输出
#SBATCH --error=file_name       %指定错误文件输出
#SBATCH --mail-type=ALL         %邮件提醒,可选:END,FAIL,ALL
#SBATCH --mail-user=address     %通知邮箱地址
"""
job_script = """#!/bin/bash
#SBATCH --job-name=myjob
#SBATCH --output=myjob.out
#SBATCH --ntasks=2
#SBATCH --time=00:10:00
#SBATCH --nodelist=c[2]
#SBATCH --exclude=c[1]
srun hostname
sleep 100
"""

with open('job.sh', 'w') as f:
    f.write(job_script)

subprocess.call(['sbatch', 'job.sh'])
~~~

~~~sh
#查看任务状态
sacct -j ID-number
~~~

## 分配模式salloc提交作业

~~~sh
#使用salloc命令提交。为需实时处理的作业分配资源，典型场景为分配资源并启动一个shell，然 后用此shell执行srun命令去执行并行任务。
#申请partition compute上申请一个核的资源
salloc -p compute -N1 -n1 -q low -t 2:00:00
#查看分配到的node
squeue
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
                70   compute interact     root  R       3:59      1 c1
                71   compute interact     root  R       0:10      1 c2
# 登录c2调试作业
ssh c2
# 取消作业
scancel 71
# 查看作业是否还在执行
squeue -j 71
~~~

## 常见命令

~~~sh
scontrol show nodes #显示所有计算节点
#如果Compute Nodes的State=DOWN，则如下执行，将状态变成恢复
scontrol update nodename=uc1 state=resume

# Why is a node shown in state DOWN when the node has registered for service?
# https://slurm.schedmd.com/faq.html#return_to_service
#The configuration parameter ReturnToService in slurm.conf controls how DOWN nodes are handled. Set its value to one in order for DOWN nodes to automatically be returned to service once the slurmd daemon registers with a valid node configuration. A value of zero is the default and results in a node staying DOWN until an administrator explicitly returns it to service using the command "scontrol update NodeName=whatever State=RESUME". See "man slurm.conf" and "man scontrol" for more details.

sacctmgr add cluster cluster-test
squeue #检查队列状况
scancel #结合作业ID，终止作业

#信息查看
scontrol show jobs              #显示作业数量
scontrol show job JOBID         #查看作业的详细信息
scontrol show node              #查看所有节点详细信息
scontrol show node node-name    #查看指定节点详细信息
scontrol show node | grep CPU   #查看各节点cpu状态
scontrol show node node-name | grep CPU #查看指定节点cpu状态
~~~

# slurm用户账户管理?

~~~sh
#在Slurm中，账户通常用于跟踪和控制用户对集群资源的使用。分区则定义了一组节点和作业在这些节点上的运行参数。
#查看所有的账户
sacctmgr list assoc
#查看账户和分区的关联
sacctmgr show associations
~~~



# PBS vs Slurm

![img](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402202153564.png)

[HPC调度基础：slurm集群的部署与配置-天翼云开发者社区 - 天翼云 (ctyun.cn)](https://www.ctyun.cn/developer/article/363542369067077)
