---
title: Ubuntu 22.04 Slurm 22.05.11 与 23.11.4 安装与配置指南
tags:
  - hpc/slurm
  - linux/ubuntu
  - hpc/munge
  - hpc/slurmdbd
  - hpc/gpu
aliases:
  - Ubuntu Slurm 22.05 二进制安装
  - Slurm测试环境部署
  - Ubuntu Slurm 22.05 Production
  - Slurm H800 GPU Cluster
  - Ubuntu2204-slurm-22.05.11-安装指南
  - Ubuntu2204-slurm-22.05.11-二进制安装
  - Ubuntu2204-slurm-22.05.11-binary-installation
  - Ubuntu Slurm 23.11 deb安装
  - Slurm deb包安装
  - Ubuntu2204-slurm-23.11-deb安装
date: 2026-09-26
---

# Ubuntu 22.04 Slurm 安装与配置指南

本指南汇总三套 Ubuntu 22.04 实例：Slurm 22.05.11 三节点测试环境、22.05.11 H800 生产环境，以及 Slurm 23.11.4 三节点 deb 包实验环境。先按下表选择一套拓扑，再使用对应版本的安装与配置章节；主机名、分区、目录和资源参数不可跨版本拼接。MUNGE 密钥的安全生成与分发流程共用，作业命令的参数说明集中在文末。

> [!warning] 使用前核对
> 三套配置记录的是不同集群，不能混用主机名、分区、spool 路径与资源参数。下方已用受限权限替换原记录中临时 `chmod 777` 的 MUNGE 密钥复制方式，并将数据库密码改为占位值；生产环境的资源、抢占日志和 Epilog 清理范围仍须在目标集群核对。

## 环境对照与阅读顺序

| 场景 | 控制/管理节点 | 计算节点 | 登录节点 | 配置重点 |
| --- | --- | --- | --- | --- |
| 测试环境（22.05.11 源码编译） | `m1` (`172.16.183.133`) | `c1` (`172.16.183.134`) | `l1` (`172.16.183.135`) | `hpc01` 集群、`cpu` 分区 |
| 生产环境（22.05.11 源码编译） | `CN01Z99SLU001` (`10.21.105.20`) | `cn01dl00[1-4]` (`10.21.105.11-14`) | `CN01Z99SLU002` (`10.21.105.21`) | `jade-slurm` 集群、H800 GPU 与 `zprod*` 分区 |
| deb 实验环境（23.11.4 源码构建 deb） | `um1` (`172.16.183.130`) | `uc1` (`172.16.183.131`) | `ul1` (`172.16.183.132`) | `ubuntutestcluster` 集群、`debug` 分区 |

1. 先完成所选环境的网络、账户与 MUNGE 安装及跨节点认证，再配置 Slurm；22.05.11 使用 `./configure && make && make install`，23.11.4 从源码构建 deb 包后安装。
2. 控制节点运行 `slurmctld`、计算节点运行 `slurmd`，登录节点安装客户端并保持相同的 `slurm.conf`；22.05.11 配置了 `slurmdbd`，23.11.4 实验只安装其软件包，尚未配置数据库服务。
3. 先用该环境实际存在的分区和节点验收，再参考通用作业示例。23.11.4 的 `debug` 分区仅配置 `uc1`，`MaxTime=1`。

## MUNGE 共享密钥：三种环境共用的安全流程

参与本轮分发的节点先创建相同 UID/GID 的 `munge` 用户并安装 MUNGE；控制节点**只生成一次**共享密钥。以下命令不需要开放 `/etc/munge` 的写权限；密钥在控制节点为 `munge:munge`、`0400`，远端暂存目录仅供登录用户访问。分发失败时检查并清理远端 `$HOME/.munge-transfer`。

~~~sh
# 仅在控制节点执行一次；重新生成密钥会使尚未同步的节点认证失败
sudo install -d -o munge -g munge -m 0700 /etc/munge
sudo dd if=/dev/urandom of=/etc/munge/munge.key bs=1024 count=1
sudo chown munge:munge /etc/munge/munge.key
sudo chmod 0400 /etc/munge/munge.key
~~~

在控制节点的同一个 Bash 会话中，按场景设置 `targets` 后运行分发脚本。`ubuntu@`、`test@` 来自原部署记录；若实际 SSH 用户不同，先调整列表并确认该用户可通过 `sudo` 安装密钥。测试环境在 `c1`、`l1` 安装 MUNGE 后分发；生产环境可先分发登录节点，等四台计算节点安装 MUNGE 后再运行一次分发脚本；23.11.4 环境分发到 `uc1`、`ul1`。**同一集群不要重新生成密钥**。原 23.11.4 记录使用 root SSH；若未开启，应改用可 `sudo` 的 SSH 用户。

~~~sh
# 测试环境：targets=(c1 l1)
# 生产登录节点：targets=(ubuntu@CN01Z99SLU002)
# 生产计算节点：targets=(test@cn01dl001 test@cn01dl002 test@cn01dl003 test@cn01dl004)
# 23.11.4 deb 实验：targets=(root@uc1 root@ul1)
# 运行前选择并取消注释其中一行

(
  set -euo pipefail
  umask 077
  key_tmp=$(mktemp)
  trap 'rm -f -- "$key_tmp"' EXIT
  sudo cat /etc/munge/munge.key > "$key_tmp"
  for target in "${targets[@]}"; do
    ssh -t "$target" 'mkdir -p "$HOME/.munge-transfer" && chmod 700 "$HOME/.munge-transfer"'
    scp "$key_tmp" "$target:.munge-transfer/munge.key"
    ssh -t "$target" 'sudo install -d -o munge -g munge -m 0700 /etc/munge && sudo install -o munge -g munge -m 0400 "$HOME/.munge-transfer/munge.key" /etc/munge/munge.key && rm -f "$HOME/.munge-transfer/munge.key" && rmdir "$HOME/.munge-transfer"'
  done
)
~~~

最后在每台节点上确认 `sudo stat -c '%U:%G %a' /etc/munge/munge.key` 为 `munge:munge 400`，再启动 MUNGE 并用下文的 `munge -n | ssh ... unmunge` 验证跨节点认证。

## 22.05.11 源码编译测试环境：m1 / c1 / l1

本节保留测试环境的网络准备、逐节点安装命令和完整 `slurm.conf`。实验镜像为 [Ubuntu 22.04.4 Server](https://mirrors.tuna.tsinghua.edu.cn/ubuntu-releases/22.04/ubuntu-22.04.4-live-server-amd64.iso)。原记录的实验账户信息为 `hangx hangx / root root`（历史凭据，复用前应更换）；网关和 DNS 记录见下方环境准备。测试 `slurm.conf` 只有 `cpu` 分区和一台 `c1` 计算节点。

### 环境准备

- IP配置

  - Ubuntu系统安装时,可以在网卡配置页面,将ens33设置为静态IP。
  - Gateway: 172.16.183.2
  - name servers: 8.8.8.8,114.114.114.114

- apt源设置

  - 设置主机名

~~~sh
sudo hostnamectl set-hostname m1 && bash
sudo hostnamectl set-hostname c1 && bash
sudo hostnamectl set-hostname l1 && bash
~~~

- 添加hosts

~~~sh
sudo tee -a /etc/hosts << 'EOF'
172.16.183.133 m1
172.16.183.134 c1
172.16.183.135 l1
EOF
~~~

- 配置时区

~~~sh
#查看时间同步信息
timedatectl status
#安装ntpdate命令
sudo apt install ntpdate -y
#跟网络时间做同步
ntpdate cn.pool.ntp.org
#把时间同步做成计划任务
sudo crontab -e
* */1 * * * /usr/sbin/ntpdate   cn.pool.ntp.org
#重启crond服务
sudo systemctl restart cron
~~~

- 配置ssh免登录

~~~sh
ssh-keygen
ssh-copy-id -i ~/.ssh/id_rsa.pub m1
ssh-copy-id -i ~/.ssh/id_rsa.pub c1
ssh-copy-id -i ~/.ssh/id_rsa.pub l1
~~~

---

### 配置munge

> [!important] Munge用户要确保Master Node和Compute Nodes的==UID和GID相同==,**所有节点**都需要安装Munge。

~~~sh
#所有节点上
#验证gid为1108的组不存在
getent group 1108
sudo groupadd -g 1108 munge
sudo useradd -m -c "Munge Uid 'N' Gid Emporium" -d /var/lib/munge -u 1108 -g munge -s /sbin/nologin munge
#-m:这个选项告诉 useradd 命令为新用户创建一个主目录。
#-c "Munge Uid 'N' Gid Emporium":这个选项用于设置新用户的注释字段,通常用于存储用户的全名或其他信息。在这里,它被设置为 "Munge Uid 'N' Gid Emporium"。
#-d /var/lib/munge:这个选项用于指定新用户的主目录。在这里,主目录被设置为 /var/lib/munge。
#-u 1108:这个选项用于指定新用户的用户 ID(UID) 被设置为 1108。
#-g munge:这个选项用于指定新用户的初始登录组,被设置为 munge。
#-s /sbin/nologin:这个选项用于指定新用户的登录 shell。在这里,shell 被设置为 /sbin/nologin,这意味着用户不能登录到系统。
#munge:这是新创建的用户名。
~~~

- 生成熵池

~~~sh
#管理节点上
sudo apt install -y rng-tools
~~~

- 使用/dev/urandom来做熵源

~~~sh
#管理节点上
sudo rngd -r /dev/urandom
sudo tee /usr/lib/systemd/system/rngd.service <<'EOF'
[Service]
ExecStart=/sbin/rngd -f -r /dev/urandom
[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload && sudo systemctl start rngd && sudo systemctl enable rngd
~~~

- 安装munge

~~~sh
# 安装 munge
# 所有节点
sudo apt -y install munge libmunge-dev libmunge2
~~~

- 在 `m1` 上按[[#MUNGE 共享密钥：三种环境共用的安全流程|共用密钥流程]]生成密钥，待 `c1` 和 `l1` 均安装 MUNGE 后，设置 `targets=(c1 l1)` 分发同一密钥。原记录采用的 1024 字节随机密钥和两台目标节点均保留在该流程中。

- 检查账户是否存在

~~~sh
#所有节点执行
sudo id munge
#uid=1108(munge) gid=1108(munge) groups=1108(munge)
~~~

- 修改配置属主,启动所有节点

~~~sh
# 所有节点执行
sudo chown munge: /etc/munge/munge.key
sudo chmod 400 /etc/munge/munge.key
sudo chmod 700 /etc/munge/
sudo chmod 711 /var/lib/munge/
sudo chmod 700 /var/log/munge/
sudo chmod 755 /var/run/munge/
sudo chown munge.munge /etc/munge/munge.key
sudo systemctl start munge && sudo systemctl enable --now munge && sudo systemctl status munge
ps -ef | grep munge | grep -v grep
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

- 验证compute node,控制节点进行连接验证

```sh
munge -n | ssh m1 unmunge
munge -n | ssh c1 unmunge
munge -n | ssh l1 unmunge
#如果出现unmunge: Error: Invalid credential,重启节点,报错消失
```

- Munge凭证基准测试

```sh
remunge
```

---

### 控制节点安装slurm

#### 创建slurm用户

~~~sh
getent group 1109
id 1109
sudo groupadd -g 1109 slurm
sudo useradd -m -c "Slurm manager" -d /var/lib/slurm -u 1109 -g slurm -s /bin/bash slurm
~~~

- 检查slurm用户存在

~~~sh
id slurm
~~~

#### 编译安装slurm

https://slurm.schedmd.com/quickstart_admin.html#debuild

~~~sh
wget https://download.schedmd.com/slurm/slurm-22.05.11.tar.bz2
#Install basic Debian package build requirements:
sudo apt-get install build-essential fakeroot devscripts equivs make hwloc libhwloc-dev mariadb-server libmysqlclient-dev #libmunge-dev libmunge2
#Unpack the distributed tarball:
sudo tar -xaf slurm*tar.bz2
cd slurm-22.05.11
#这里看一下Hal的配置,安装位置怎么定义的?
sudo ./configure --prefix=/usr/local --disable-debug --sysconfdir=/etc/slurm

#./configure --prefix=/usr/local --disable-dependency-tracking --disable-debug --disable-x11 --enable-really-no-cray --enable-salloc-kill-cmd --with-hdf5=no --sysconfdir=/etc/slurm --enable-pam --with-pam_dir={{ slurm_pam_lib_dir }} --with-shared-libslurm --without-rpath --with-pmix=/usr/local --with-hwloc=/opt/deepops/hwloc

sudo make -j16
sudo make install
sudo cp -r ./etc/slurm*.service /etc/systemd/system/
~~~

#### 配置数据库

以下口令是占位值，执行 SQL 前替换为专用强密码，并在 `slurmdbd.conf` 的 `StoragePass` 使用同一值。数据库由管理员创建，因此 `slurm` 用户只获得 `slurm_acct_db.*` 权限，不需要原记录的全局 `*.*` 授权或 `WITH GRANT OPTION`。已有数据库或用户需先核对，避免重复创建。

```sh
sudo systemctl enable mariadb
sudo systemctl start mariadb
sudo systemctl status mariadb
```

```sh
sudo mysql
CREATE DATABASE slurm_acct_db;
CREATE USER 'slurm'@'localhost' IDENTIFIED BY 'REPLACE_WITH_STRONG_PASSWORD';
GRANT ALL PRIVILEGES ON slurm_acct_db.* TO 'slurm'@'localhost';
exit;
```

#### slurm配置文件

##### cgroup.conf

~~~sh
#配置文件是放在--sysconfdir=/etc/slurm下
sudo mkdir /etc/slurm/
cd /etc/slurm/
~~~

~~~sh
#==============master节点===========================
sudo tee cgroup.conf <<'EOF'
###
#
# Slurm cgroup support configuration file
#
# See man slurm.conf and man cgroup.conf for further
# information on cgroup configuration parameters
#--
CgroupAutomount=yes

ConstrainCores=yes
ConstrainDevices=yes
ConstrainRAMSpace=yes
#TaskAffinity=yes
EOF
~~~

##### slurm.conf

~~~sh
#查看CPUs
nproc
#查看Sockets、CoresPerSocket、ThreadsPerCore
lscpu
#查看RealMemory
free -m
~~~

~~~sh
#先用网上的测试配置试一下
sudo tee /etc/slurm/slurm.conf << 'EOF'

#
# Example slurm.conf file. Please run configurator.html
# (in doc/html) to build a configuration file customized
# for your environment.
#
#
# slurm.conf file generated by configurator.html.
# Put this file on all nodes of your cluster.
# See the slurm.conf man page for more information.
#
ClusterName=hpc01
SlurmctldHost=m1
#SlurmctldHost=
#
MpiDefault=none
ProctrackType=proctrack/cgroup
ReturnToService=1
SlurmctldPidFile=/var/run/slurmctld.pid
SlurmctldPort=6817
SlurmdPidFile=/var/run/slurmd.pid
SlurmdPort=6818
SlurmdSpoolDir=/var/spool/slurmd
SlurmdUser=root
StateSaveLocation=/var/spool/slurmctld
SwitchType=switch/none
TaskPlugin=task/affinity

#
#
# TIMERS
InactiveLimit=0
KillWait=30
MinJobAge=300
SlurmctldTimeout=120
SlurmdTimeout=300

Waittime=0

# SCHEDULING
SchedulerType=sched/backfill
SelectType=select/cons_tres
SelectTypeParameters=CR_Core_Memory
#
#
# JOB PRIORITY
AccountingStorageEnforce=qos,limits
AccountingStorageHost=m1 #localhost?
AccountingStoragePass=/var/run/munge/munge.socket.2
AccountingStorageType=accounting_storage/slurmdbd
#AccountingStorageTRES=gres/gpu
JobCompHost=m1 #localhost?
JobCompLoc=slurm_acct_db
JobCompPass=REPLACE_WITH_STRONG_PASSWORD
JobCompType=jobcomp/none
JobCompUser=slurm
JobAcctGatherFrequency=30
JobAcctGatherType=jobacct_gather/linux
SlurmctldDebug=info
SlurmctldLogFile=/var/log/slurm/slurmctld.log
SlurmdDebug=info
SlurmdLogFile=/var/log/slurm/slurmd.log
#GresTypes=gpu
NodeName=c1  RealMemory=2500 CPUs=4 Sockets=2 CoresPerSocket=2 ThreadsPerCore=1 State=UNKNOWN
#NodeName=aiwkr2  RealMemory=1000000 Gres=gpu:8 State=UNKNOWN Sockets=2 CoresPerSocket=32 CPUs=64
#NodeName=aiwkr3  RealMemory=1000000 Gres=gpu:8 State=UNKNOWN Sockets=2 CoresPerSocket=32 CPUs=64
#PartitionName=gpu1 Nodes=aiwkr[1-3] Default=YES MaxTime=168:00:00 State=UP
#PartitionName=gpu2-8 Nodes=aiwkr[1-3] Default=YES MaxTime=168:00:00 State=UP
PartitionName=cpu Nodes=c1 Default=YES MaxTime=168:00:00 State=UP
EOF
~~~

##### gres.conf

- 控制节点/etc/slurm/下新建gres.conf,空白文件

~~~sh
sudo touch gres.conf
~~~

##### slurmdbd.conf

- 管理节点/etc/slurm/下

~~~sh
AuthType=auth/munge
AuthInfo=/var/run/munge/munge.socket.2
#
# slurmDBD info
DbdAddr=localhost #?这里的Ip所有节点都一样吗
DbdHost=localhost
#DbdPort=7031
SlurmUser=slurm
#MessageTimeout=300
DebugLevel=4
#DefaultQOS=normal,standby
LogFile=/var/log/slurm/slurmdbd.log
PidFile=/var/run/slurmdbd.pid
#PluginDir=/usr/lib/slurm
#PrivateData=accounts,users,usage,jobs
#TrackWCKey=yes
#
# Database info
StorageType=accounting_storage/mysql
StorageHost=localhost
StoragePort=3306
StoragePass=REPLACE_WITH_STRONG_PASSWORD
StorageUser=slurm
StorageLoc=slurm_acct_db
~~~

~~~sh
sudo chown slurm.slurm /etc/slurm/slurmdbd.conf
sudo chmod 600 /etc/slurm/slurmdbd.conf
sudo mkdir -p /var/log/slurm/
sudo touch /var/log/slurm/slurmdbd.log
sudo chown slurm: /var/log/slurm/slurmdbd.log
~~~

#### 配置同步/权限修改

~~~sh
sudo chmod 0755 /var/spool
sudo chown -R slurm:slurm /var/spool
sudo mkdir -p /var/spool/slurm
sudo chown slurm: /var/spool/slurm
sudo mkdir -p /var/log/slurm
sudo chown slurm: /var/log/slurm
sudo mkdir -p /var/spool/slurm
sudo chown slurm: /var/spool/slurm
sudo mkdir -p /var/log/slurm
sudo chown slurm: /var/log/slurm
~~~

#### 配置slurm环境变量

~~~sh
#给所有用户添加环境变量
su root
vim /etc/profile
#添加
# export PATH=$PATH:/usr/local/bin
# export PATH=$PATH:/usr/local/sbin
source /etc/profile
~~~

#### 启动服务

~~~sh
#m1上
sudo systemctl enable slurmdbd
sudo systemctl start slurmdbd
sudo systemctl status slurmdbd

sudo systemctl enable slurmctld
sudo systemctl start slurmctld
sudo systemctl status slurmctld
~~~

---

### 计算节点安装slurm

#### 创建slurm用户

~~~sh
getent group 1109
id 1109
sudo groupadd -g 1109 slurm
sudo useradd -m -c "Slurm manager" -d /var/lib/slurm -u 1109 -g slurm -s /bin/bash slurm
~~~

- 检查slurm用户存在

~~~sh
id slurm
~~~

#### 编译安装slurm

https://slurm.schedmd.com/quickstart_admin.html#debuild

~~~sh
wget https://download.schedmd.com/slurm/slurm-22.05.11.tar.bz2
#Install basic Debian package build requirements:
sudo apt-get install build-essential fakeroot devscripts equivs make hwloc libdbus-1-dev libhwloc-dev libmunge-dev libmunge2 mariadb-server libmysqlclient-dev libcgns-dev libcgroup-dev
#Unpack the distributed tarball:
sudo tar -xaf slurm*tar.bz2
cd slurm-22.05.11
#这里看一下Hal的配置,安装位置怎么定义的?
sudo ./configure --prefix=/usr/local --disable-debug --sysconfdir=/etc/slurm

#./configure --prefix=/usr/local --disable-dependency-tracking --disable-debug --disable-x11 --enable-really-no-cray --enable-salloc-kill-cmd --with-hdf5=no --sysconfdir=/etc/slurm --enable-pam --with-pam_dir={{ slurm_pam_lib_dir }} --with-shared-libslurm --without-rpath --with-pmix=/usr/local --with-hwloc=/opt/deepops/hwloc

sudo make -j16
sudo make install
sudo cp -r ./etc/slurm*.service /etc/systemd/system/
~~~

#### slurm配置文件

##### cgroup.conf

~~~sh
#配置文件是放在--sysconfdir=/etc/slurm下
sudo mkdir -p /etc/slurm/
cd /etc/slurm/
~~~

~~~sh
sudo tee cgroup.conf <<'EOF'
###
#
# Slurm cgroup support configuration file
#
# See man slurm.conf and man cgroup.conf for further
# information on cgroup configuration parameters
#--
CgroupAutomount=yes

ConstrainCores=no
ConstrainRAMSpace=no
EOF
~~~

##### slurm.conf

- 复制控制节点的配置文件过来

##### gres.conf

- 客户端/etc/slurm/下新建gres.conf

~~~sh
#AutoDetect=nvml
Name=gpu Type=H800 File=/dev/nvidia[0-7]
~~~

#### 配置同步/权限修改

~~~sh
sudo chmod 0755 /var/spool
sudo chown -R slurm:slurm /var/spool
sudo mkdir -p /var/spool/slurm
sudo chown slurm: /var/spool/slurm
sudo mkdir -p /var/log/slurm
sudo chown slurm: /var/log/slurm
sudo mkdir -p /var/spool/slurm
sudo chown slurm: /var/spool/slurm
sudo mkdir -p /var/log/slurm
sudo chown slurm: /var/log/slurm
sudo mkdir /var/spool/slurmd
sudo chmod 755 /var/spool/slurmd
sudo chmod 644 /var/log/slurm/slurmd.log
~~~

#### 配置slurm环境变量

~~~sh
#给所有用户添加环境变量
su root
vim /etc/profile
#添加
export PATH=$PATH:/usr/local/bin
export PATH=$PATH:/usr/local/sbin
source /etc/profile
~~~

#### 启动服务

~~~sh
sudo systemctl enable slurmd
sudo systemctl start slurmd
sudo systemctl status slurmd
~~~

---

### 登录节点安装slurm

#### 创建slurm用户

~~~sh
getent group 1109
id 1109
sudo groupadd -g 1109 slurm
sudo useradd -m -c "Slurm manager" -d /var/lib/slurm -u 1109 -g slurm -s /bin/bash slurm
~~~

- 检查slurm用户存在

~~~sh
id slurm
~~~

#### 编译安装slurm

https://slurm.schedmd.com/quickstart_admin.html#debuild

~~~sh
wget https://download.schedmd.com/slurm/slurm-22.05.11.tar.bz2
#Install basic Debian package build requirements:
sudo apt-get install build-essential fakeroot devscripts equivs make hwloc libhwloc-dev libmunge-dev libmunge2
#Unpack the distributed tarball:
sudo tar -xaf slurm*tar.bz2
cd slurm-22.05.11
#这里看一下Hal的配置,安装位置怎么定义的?
sudo ./configure --prefix=/usr/local --disable-debug --sysconfdir=/etc/slurm

#./configure --prefix=/usr/local --disable-dependency-tracking --disable-debug --disable-x11 --enable-really-no-cray --enable-salloc-kill-cmd --with-hdf5=no --sysconfdir=/etc/slurm --enable-pam --with-pam_dir={{ slurm_pam_lib_dir }} --with-shared-libslurm --without-rpath --with-pmix=/usr/local --with-hwloc=/opt/deepops/hwloc

sudo make -j16
sudo make install
sudo cp -r ./etc/slurm*.service /etc/systemd/system/
~~~

#### slurm配置文件

```sh
#配置文件是放在--sysconfdir=/etc/slurm下
sudo mkdir /etc/slurm/
cd /etc/slurm/
```

##### slurm.conf

~~~sh
#先用网上的测试配置试一下
sudo tee /etc/slurm/slurm.conf << 'EOF'

#
# Example slurm.conf file. Please run configurator.html
# (in doc/html) to build a configuration file customized
# for your environment.
#
#
# slurm.conf file generated by configurator.html.
# Put this file on all nodes of your cluster.
# See the slurm.conf man page for more information.
#
ClusterName=hpc01
SlurmctldHost=m1
#SlurmctldHost=
#
MpiDefault=none
ProctrackType=proctrack/cgroup
ReturnToService=1
SlurmctldPidFile=/var/run/slurmctld.pid
SlurmctldPort=6817
SlurmdPidFile=/var/run/slurmd.pid
SlurmdPort=6818
SlurmdSpoolDir=/var/spool/slurmd
SlurmdUser=root
StateSaveLocation=/var/spool/slurmctld
SwitchType=switch/none
TaskPlugin=task/affinity

#
#
# TIMERS
InactiveLimit=0
KillWait=30
MinJobAge=300
SlurmctldTimeout=120
SlurmdTimeout=300

Waittime=0

# SCHEDULING
SchedulerType=sched/backfill
SelectType=select/cons_tres
SelectTypeParameters=CR_Core_Memory
#
#
# JOB PRIORITY
AccountingStorageEnforce=qos,limits
AccountingStorageHost=m1 #localhost?
AccountingStoragePass=/var/run/munge/munge.socket.2
AccountingStorageType=accounting_storage/slurmdbd
#AccountingStorageTRES=gres/gpu
JobCompHost=m1 #localhost?
JobCompLoc=slurm_acct_db
JobCompPass=REPLACE_WITH_STRONG_PASSWORD
JobCompType=jobcomp/none
JobCompUser=slurm
JobAcctGatherFrequency=30
JobAcctGatherType=jobacct_gather/linux
SlurmctldDebug=info
SlurmctldLogFile=/var/log/slurm/slurmctld.log
SlurmdDebug=info
SlurmdLogFile=/var/log/slurm/slurmd.log
#GresTypes=gpu
NodeName=c1  RealMemory=2500 CPUs=4 Sockets=2 CoresPerSocket=2 ThreadsPerCore=1 State=UNKNOWN
#NodeName=aiwkr2  RealMemory=1000000 Gres=gpu:8 State=UNKNOWN Sockets=2 CoresPerSocket=32 CPUs=64
#NodeName=aiwkr3  RealMemory=1000000 Gres=gpu:8 State=UNKNOWN Sockets=2 CoresPerSocket=32 CPUs=64
#PartitionName=gpu1 Nodes=aiwkr[1-3] Default=YES MaxTime=168:00:00 State=UP
#PartitionName=gpu2-8 Nodes=aiwkr[1-3] Default=YES MaxTime=168:00:00 State=UP
PartitionName=cpu Nodes=c1 Default=YES MaxTime=168:00:00 State=UP
EOF
~~~

#### 配置同步/权限修改

~~~sh
sudo chmod 0755 /var/spool
sudo chown -R slurm:slurm /var/spool
sudo mkdir -p /var/spool/slurm
sudo chown slurm: /var/spool/slurm
sudo mkdir -p /var/log/slurm
sudo chown slurm: /var/log/slurm
sudo mkdir -p /var/spool/slurm
sudo chown slurm: /var/spool/slurm
sudo mkdir -p /var/log/slurm
sudo chown slurm: /var/log/slurm
~~~

#### 配置slurm环境变量

~~~sh
#给所有用户添加环境变量
su root
vim /etc/profile
#添加
# export PATH=$PATH:/usr/local/bin
# export PATH=$PATH:/usr/local/sbin
source /etc/profile
~~~

#### 启动服务

~~~sh
#l1上不需要启动daemon,二进制安装完,维护同样的slurm.conf就行
~~~

---

## 22.05.11 源码编译生产环境：CN01Z99SLU001 / cn01dl00[1-4] / CN01Z99SLU002

本节保留生产环境的批量 SSH 操作、H800 GPU 资源定义、分区优先级、记账配置和节点脚本。MUNGE/Slurm 用户分别使用统一 UID/GID 1108/1109；执行远程命令前需确认 `test`、`ubuntu` 或 `root` 在目标主机上的登录与提权方式。生产配置中的路径和资源数值应与实际节点核对。

### management/login node安装munge

> [!important] Munge用户要确保Master/login Nodes和Compute Nodes的==UID和GID相同==，**所有节点**都需要安装Munge。

~~~sh
#所有节点上
#验证gid为1108的组不存在
getent group 1108
id 1108
sudo groupadd -g 1108 munge
sudo useradd -m -c "Munge Uid 1108 Gid 1108" -d /var/lib/munge -u 1108 -g munge -s /sbin/nologin munge
#-m：为新用户创建一个主目录。
#-c：设置新用户的注释字段，通常用于存储用户的全名或其他信息。
#-d /var/lib/munge：指定新用户的主目录。
#-u 1108：指定UID
#-g munge：指定新用户的初始登录组
#-s /sbin/nologin：指定新用户的登录shell 被设置为 /sbin/nologin，这意味着用户不能登录到系统。
~~~

- 生成熵池

~~~sh
#master节点CN01Z99SLU001上，切换到root
apt install rng-tools
~~~

- 使用/dev/urandom来做熵源

~~~sh
#master节点CN01Z99SLU001上
sudo rngd -r /dev/urandom
sudo tee /usr/lib/systemd/system/rngd.service <<'EOF'
[Service]
ExecStart=/sbin/rngd -f -r /dev/urandom
[Install]
WantedBy=multi-user.target
EOF
#启动服务
sudo systemctl daemon-reload && sudo systemctl start rngd && sudo systemctl enable rngd && sudo systemctl status rngd
~~~

- 安装munge

~~~sh
# 所有节点安装 munge
sudo apt install munge libmunge-dev libmunge2
~~~

- 在 `CN01Z99SLU001` 上按[[#MUNGE 共享密钥：三种环境共用的安全流程|共用密钥流程]]生成密钥；登录节点安装 MUNGE 后，设置 `targets=(ubuntu@CN01Z99SLU002)` 分发。四台计算节点稍后安装 MUNGE，再分发**同一把**密钥。

- 检查账户是否存在

~~~sh
#所有节点执行，检查uid和gid是否统一
sudo id munge
#uid=1108(munge) gid=1108(munge) groups=1108(munge)
~~~

- 修改配置属主，启动所有节点

~~~sh
# 所有节点执行
sudo chown munge: /etc/munge/munge.key
sudo chown munge.munge /etc/munge/munge.key
sudo chmod 400 /etc/munge/munge.key
sudo chmod 700 /etc/munge/
sudo chmod 711 /var/lib/munge/
sudo chmod 700 /var/log/munge/
sudo chmod 755 /var/run/munge/
sudo systemctl start munge && sudo systemctl enable munge && sudo systemctl status munge
ps -ef | grep munge | grep -v grep
~~~

- 配置ssh免密登录?先不配置，后面看看munge是否可以认证成功。

- 测试munge服务: 每个计算节点与控制节点进行连接验证

- 本地查看凭据

```sh
munge -n
```

- 本地解码

```sh
munge -n | unmunge
```

- 与其他节点进行连接验证

```sh
munge -n | ssh cn01z99slu002 unmunge
#如果出现unmunge: Error: Invalid credential，重启节点，报错消失
```

- Munge凭证基准测试

```sh
remunge
```

---

### compute node安装munge

~~~sh
#ssh远程命令的语法，不需要sudo时
for i in `seq 1 4`; do
ssh test@cn01dl00$i "hostname;whoami"
done
#ssh远程命令的语法，需要sudo时，ssh -t分配伪终端，需要手动输密码
for i in `seq 1 4`; do
ssh -t test@cn01dl00$i "sudo hostname"
done
~~~

- 创建统一munge用户和组

~~~sh
for i in `seq 1 4`; do
ssh -t test@cn01dl00$i "sudo groupadd -g 1108 munge; sudo useradd -m -c \"Munge Uid 1108 Gid 1108\" -d /var/lib/munge -u 1108 -g munge -s /sbin/nologin munge";
done

for i in `seq 1 4`; do
ssh test@cn01dl00$i "id munge";
done
~~~

- 安装munge

~~~sh
#compute node上
su test
sudo su
apt install munge libmunge-dev libmunge2

# MUNGE 安装后不需要将 /etc/munge 或 munge.key 设为全员可写。
~~~

- 在管理节点设置 `targets=(test@cn01dl001 test@cn01dl002 test@cn01dl003 test@cn01dl004)`，按[[#MUNGE 共享密钥：三种环境共用的安全流程|共用密钥流程]]分发已有密钥。下面继续核对计算节点的运行目录权限。

~~~sh
#相关目录文件修改权限
for i in `seq 1 4`; do
ssh -t test@cn01dl00$i "sudo chown munge: /etc/munge/munge.key;sudo chmod 400 /etc/munge/munge.key;sudo chmod 700 /etc/munge/;sudo chmod 711 /var/lib/munge/;sudo chmod 700 /var/log/munge/;sudo chmod 755 /var/run/munge/;sudo chown munge.munge /etc/munge/munge.key;";
done
~~~

- compute node启动服务

~~~sh
for i in `seq 1 4`; do
ssh -t test@cn01dl00$i "sudo systemctl start munge && sudo systemctl enable munge && sudo systemctl status munge;ps -ef | grep munge | grep -v grep;";
done
~~~

- 服务正常启动后，检查munge凭据认证情况

~~~sh
#本地查看凭据
for i in `seq 1 4`; do
ssh test@cn01dl00$i "munge -n;";
done
#本地解码
for i in `seq 1 4`; do
ssh test@cn01dl00$i "munge -n | unmunge";
done
#生成和验证MUNGE（MUNGE Uid 'N' Gid Emporium）凭证
for i in `seq 1 4`; do
ssh test@cn01dl00$i "remunge";
done
#与其他节点进行认证
for i in `seq 1 4`; do
ssh test@cn01dl00$i "munge -n | ssh ubuntu@cn01z99slu001 unmunge";
done
~~~

---

### management node安装slurm

#### 创建slurm用户

~~~sh
getent group 1109
id 1109
sudo groupadd -g 1109 slurm
sudo useradd -m -c "Slurm manager" -d /var/lib/slurm -u 1109 -g slurm -s /bin/bash slurm
~~~

- 检查slurm用户存在

~~~sh
id slurm
~~~

#### 编译安装slurm

https://slurm.schedmd.com/quickstart_admin.html#debuild

~~~sh
#wget https://download.schedmd.com/slurm/slurm-22.05.11.tar.bz2
#自己电脑上wget下来，ftp 22端口上传上去；VM上ftp 2802端口拿出来
#Install basic Debian package build requirements:
sudo su
apt-get update
apt-get install build-essential fakeroot devscripts equivs make hwloc libhwloc-dev mariadb-server libmysqlclient-dev #libmunge-dev libmunge2
#Unpack the distributed tarball:
sudo tar -xaf slurm*tar.bz2
cd slurm-22.05.11
#这里根据Hal的配置，指定安装位置
sudo ./configure --prefix=/usr/local --disable-debug --sysconfdir=/etc/slurm

#./configure --prefix=/usr/local --disable-dependency-tracking --disable-debug --disable-x11 --enable-really-no-cray --enable-salloc-kill-cmd --with-hdf5=no --sysconfdir=/etc/slurm --enable-pam --with-pam_dir={{ slurm_pam_lib_dir }} --with-shared-libslurm --without-rpath --with-pmix=/usr/local --with-hwloc=/opt/deepops/hwloc
sudo make -j16
sudo make install
sudo cp -r ./etc/slurm*.service /etc/systemd/system/
~~~

#### 配置数据库

以下口令是占位值，执行 SQL 前替换为专用强密码，并在 `slurmdbd.conf` 的 `StoragePass` 使用同一值。数据库由管理员创建，因此 `slurm` 用户只获得 `slurm_acct_db.*` 权限，不需要原记录的全局 `*.*` 授权或 `WITH GRANT OPTION`。已有数据库或用户需先核对，避免重复创建。

```sh
sudo systemctl enable mariadb
sudo systemctl start mariadb
sudo systemctl status mariadb
```

```sh
sudo mysql
CREATE DATABASE slurm_acct_db;
CREATE USER 'slurm'@'localhost' IDENTIFIED BY 'REPLACE_WITH_STRONG_PASSWORD';
GRANT ALL PRIVILEGES ON slurm_acct_db.* TO 'slurm'@'localhost';
exit;
```

#### slurm配置文件

##### cgroup.conf

~~~sh
#配置文件是放在--sysconfdir=/etc/slurm下
sudo mkdir /etc/slurm/
cd /etc/slurm/
~~~

~~~sh
#==============master节点===========================
sudo tee cgroup.conf <<'EOF'
###
#
# Slurm cgroup support configuration file
#
# See man slurm.conf and man cgroup.conf for further
# information on cgroup configuration parameters
#--
CgroupAutomount=yes

ConstrainCores=yes
ConstrainDevices=yes
ConstrainRAMSpace=yes
#TaskAffinity=yes
EOF
~~~

##### slurm.conf

~~~sh
#查看CPUs
nproc
#查看Sockets、CoresPerSocket、ThreadsPerCore
lscpu
#查看RealMemory
free -m
#
~~~

> [!tip] slurm.conf 关键参数说明
> - ==ProctrackType=proctrack/cgroup==: 采用Linux cgroup来生成作业容器并追踪进程
> - ==ReturnToService=1==: 仅当由于无响应而将DOWN节点设置为DOWN状态时，才可以当有效配置注册后使DOWN节点恢复服务
> - ==TaskPlugin=task/affinity,task/cgroup==: affinity用于CPU亲和，cgroup用于强制采用Linux控制组分配资源
> - ==SchedulerType=sched/backfill==: 使用后填充调度器，优先运行队列中等待时间最长的作业
> - ==SelectType=select/cons_tres==: 单个的CPU核、内存、GPU及其它可追踪资源作为可消费资源

~~~sh
sudo tee /etc/slurm/slurm.conf << 'EOF'

# Define a name for the cluster
ClusterName=jade-slurm

# If you are enabling high-availability for the cluster, you should configure
# SlurmctldHost for each machine and list an external NFS location where
# both machines can mount the shared state.
#SlurmctldHost=wm-mgmt001
#SlurmctldHost=wm-mgmt002
#StateSaveLocation=/sw/slurm
#
# Otherwise, you should define a single SlurmctldHost and use the default
# StateSaveLocation
SlurmctldHost=cn01z99slu001
#StateSaveLocation=/var/spool/slurmctld
StateSaveLocation=/var/spool/slurm/ctld #后面权限配置需要注意：本级目录ctld和上级目录slurm

# Basic configuration of Slurm daemon
SlurmUser=slurm
SlurmctldPort=6817
SlurmdPort=6818
AuthType=auth/munge
SlurmdSpoolDir=/var/spool/slurm/d #注意权限
SwitchType=switch/none
SlurmctldPidFile=/var/run/slurmctld.pid
SlurmdPidFile=/var/run/slurmd.pid
ProctrackType=proctrack/cgroup ## Cgroup: 采用Linux cgroup来生成作业容器并追踪进程，需要设定/etc/slurm/cgroup.conf文件
PluginDir=/usr/local/lib/slurm

# Basic job behavior
ReturnToService=1 # 1: 仅当由于无响应而将DOWN节点设置为DOWN状态时，才可以当有效配置注册后使DOWN节点恢复服务。如节点由于任何其它原因（内存不足、意外重启等）被设置为DOWN，其状态将不会自动更改。当节点的内存、GRES、CPU计数等等于或大于slurm.conf中配置的值时，该节点才注册为有效配置。
MpiDefault=none # https://slurm.schedmd.com/mpi_guide.html
RebootProgram="/bin/systemctl reboot"
ResumeTimeout=600 # Maximum time permitted (in seconds) between when a node resume request is issued and when the node is actually available for use.  Nodes which fail to respond  in  this  time frame will be marked DOWN and the jobs scheduled on the node requeued.
PropagateResourceLimitsExcept=MEMLOCK #内存锁定（MEMLOCK）的限制不应该从提交作业的进程传播到作业的进程。这意味着作业的进程可以锁定任意量的数据在内存中，不受提交作业的进程的MEMLOCK限制的影响。
#TaskPlugin=task/affinity - test option
TaskPlugin=task/affinity,task/cgroup # affinity: CPU亲和（man srun查看其中--cpu-bind、--mem-bind和-E选项），cgroup: 强制采用Linux控制组cgroup分配资源（man group.conf查看帮助）
#SlurmdUser=slurm #no this option in hal

# Prolog/Epilog #前处理及后处理
Prolog=/etc/slurm/prolog.d/50-zen
Epilog=/etc/slurm/epilog.d/90-zen
PrologFlags=Alloc,Serial,Contain
BatchStartTimeout=120
#MailProg=/usr/bin/s-nail

# Health checking
#HealthCheckProgram=/usr/sbin/nhc
#HealthCheckInterval=300
#HealthCheckNodeState=IDLE

# TIMERS
# Increase timeout during slurm upgrade
SlurmctldTimeout=900 # 设定备份控制器在主控制器等待多少秒后成为激活的控制器
SlurmdTimeout=900 #slurm控制器等待slurmd未响应请求多少秒后将该节点状态设置为DOWN
InactiveLimit=0 #The  interval,  in  seconds,  after which a non-responsive job allocation command (e.g. srun or salloc) will result in the job being terminated.
MinJobAge=300 #Slurm控制器在等待作业结束多少秒后清理其记录
KillWait=60 #在作业到达其时间限制前等待多少秒后在发送SIGKILLL信号之前发送TERM信号以优雅地终止
Waittime=0 #在一个作业步的第一个任务结束后等待多少秒后结束所有其它任务，0表示无限长等待
UnkillableStepTimeout=300 #表示如果一个作业步骤在收到结束信号后300秒内仍然没有结束，那么它将被标记为"不可杀死"。

# SCHEDULING
SchedulerType=sched/backfill #使用后填充调度器，是先进先出（FIFO）调度器，优先运行队列中等待时间最长的作业。与普通的FIFO调度器不同，后填充调度器会尝试找到可以在不延迟当前等待时间最长的作业的情况下运行的较小作业。后填充调度器需要预测作业的运行时间。如果作业的实际运行时间超过预测的运行时间，那么可能会影响后续作业的调度。因此，你应该尽可能准确地指定作业的运行时间。
SelectType=select/cons_tres #select/cons_tres: 单个的CPU核、内存、GPU及其它可追踪资源作为可消费资源（消费及分配），建议设置
#SelectTypeParameters=CR_Core_Memory #test option
SelectTypeParameters=CR_Core_Memory,CR_CORE_DEFAULT_DIST_BLOCK,CR_ONE_TASK_PER_CORE #资源选择插件用于决定在哪些节点上运行作业。(man page里面支持的参数只有CR_Core,  CR_Core_Mem‐ory,  CR_Socket  and  CR_Socket_Memory???)
PriorityType=priority/multifactor
PriorityDecayHalfLife=2-0
PriorityFavorSmall=NO
PriorityWeightFairshare=10000
PriorityWeightAge=1000
PriorityWeightPartition=100000
PriorityWeightJobSize=1000
PriorityMaxAge=1-0
PreemptType=preempt/partition_prio
PreemptExemptTime=30:00
CompleteWait=360
SlurmSchedLogFile=/var/log/slurm/sched.log
EnforcePartLimits=ANY

# LOGGING
#SlurmctldDebug=info
SlurmctldDebug=3
SlurmctldLogFile=/var/log/slurm/slurmctld.log
#SlurmdDebug=info
SlurmdDebug=3
SlurmdLogFile=/var/log/slurm/slurmd.log
JobCompType=jobcomp/none

# ACCOUNTING
#JobAcctGatherType=jobacct_gather/linux
JobAcctGatherType=jobacct_gather/cgroup #Slurm记录每个作业消耗的资源:jobacct_gather/cgroup: 收集Linux cgroup信息;jobacct_gather/linux: 收集Linux进程表信息，建议
AccountingStorageType=accounting_storage/slurmdbd
AccountingStorageHost=cn01z99slu001 #localhost?
AccountingStorageUser=slurm
AccountingStorageTRES=gres/gpu
AccountingStoragePass=/var/run/munge/munge.socket.2
#AccountingStorageEnforce=qos,limits
AccountingStorageEnforce=limits

#GRES
# Default MPI launcher
# MpiDefault=pmix
GresTypes=gpu
#JobSubmitPlugins=lua
#Do not use this parameter because:
##slurmctld: error: Couldn't find the specified plugin name for job_submit/lua looking at all files
##slurmctld: error: cannot find job_submit plugin for job_submit/lua
##slurmctld: error: cannot create job_submit context for job_submit/lua

# zen's customization
JobFileAppend=1
JobRequeue=1
TaskPluginParam=Cores
SchedulerParameters=default_gbytes
PreemptMode=REQUEUE
AccountingStoreFlags=job_comment
JobAcctGatherFrequency=30

# JOB PRIORITY -- test option not in hal config
JobCompHost=cn01z99slu001 #localhost?
JobCompLoc=slurm_acct_db
JobCompPass=REPLACE_WITH_STRONG_PASSWORD
JobCompUser=slurm

##############################################################################################################################
# Node definitions
##############################################################################################################################
# NVIDIA H800 80GB

NodeName=cn01dl00[1-4] NodeAddr=10.21.105.[11-14] RealMemory=1031000 CPUs=128 Sockets=2 CoresPerSocket=32 ThreadsPerCore=2 Gres=gpu:H800:8 State=UNKNOWN Feature="80G"
#DOWN表示节点状态未被定义，但将在节点上启动slurmd进程后设置为BUSY或IDLE，该为默认值。
# Gres=gpu:H800:8 # 设置节点有8块H800 GPU卡，需要在GPU节点 /etc/slum/gres.conf 文件中有类似下面配置：
         #AutoDetect=nvml
         #Name=gpu Type=H800 File=/dev/nvidia[0-1] #设置资源的名称Name是gpu，类型Type为v100，名称与类型可以任意取，但需要与其它方面配置对应，File=/dev/nvidia[0-1]指明了使用的GPU设备。

##############################################################################################################################
# Partition definitions
##############################################################################################################################

# By default, we define a single partition 'batch' with all nodes
# PartitionName=batch Nodes=hal-gn[04-05] Default=YES State=UP MaxTime=24:00:00 PreemptMode=OFF

# You may wish to define a 'debug' partition to hold nodes with suspected
# issues during hardware validation
#PartitionName=debug Nodes=dgx02,dgx04 Default=NO State=UNKNOWN OverSubscribe=EXCLUSIVE MaxTime=24:00:00 PreemptMode=OFF

# You may wish to define partitions for each scalable unit to aid in hardware validation
#PartitionName=su01 Nodes=dgx[001-020] Default=NO State=UNKNOWN OverSubscribe=EXCLUSIVE MaxTime=24:00:00 PreemptMode=OFF
#PartitionName=su02 Nodes=dgx[021-040] Default=NO State=UNKNOWN OverSubscribe=EXCLUSIVE MaxTime=24:00:00 PreemptMode=OFF
#
## zen partition setup
#
PartitionName=zprodhigh Nodes=cn01dl00[1-4] DefMemPerGPU=80000 DefMemPerCPU=7812 MaxTime=INFINITE State=UP PriorityJobFactor=40000 PriorityTier=3 PreemptMode=OFF

PartitionName=zprod Nodes=cn01dl00[1-4] DefMemPerGPU=80000 DefMemPerCPU=7812 MaxTime=INFINITE State=UP PriorityJobFactor=20000 PriorityTier=2 PreemptMode=OFF #QOS=zprod

PartitionName=zprodlow Nodes=cn01dl00[1-4] DefMemPerGPU=80000 DefMemPerCPU=7812 MaxTime=INFINITE State=UP PriorityJobFactor=0 PriorityTier=1 PreemptMode=OFF

PartitionName=zprodtest Nodes=cn01dl004 DefMemPerGPU=80000 DefMemPerCPU=7812 Default=YES MaxTime=00:45:00 State=UP PriorityJobFactor=20000 PriorityTier=2 PreemptMode=OFF

PartitionName=zprodcpu Nodes=cn01dl004 DefMemPerCPU=80000 MaxTime=INFINITE State=UP PriorityTier=1 PreemptMode=OFF

#PartitionName=ztestpreemp Nodes=cn01dl00[1-4] DefMemPerGPU=64000 DefMemPerCPU=6144 MaxTime=INFINITE State=UP PriorityJobFactor=0 PriorityTier=1 PreemptMode=REQUEUE

#PriorityJobFactor=20000：定义了作业优先级的因子为20000。这个因子用于计算作业的优先级，值越大的作业优先级越高。
#PriorityTier=2：定义了分区的优先级层级为2。在同一优先级因子下，层级越高的分区优先级越高。
#PreemptMode=OFF：定义了抢占模式为OFF。这意味着在这个分区中，高优先级的作业不能抢占低优先级的作业的资源。
#QOS=zprod：定义了分区的服务质量（Quality of Service）为zprod。服务质量是一组限制和优先级，它可以用来控制作业的运行。可以使用sacctmgr命令来创建和配置QOS：sacctmgr add qos zprod set GrpTRES=cpu=10,mem=100G,gres/gpu=1 MaxWallDurationPerJob=24:00:00
EOF
~~~

##### gres.conf

- 控制节点/etc/slurm/下新建gres.conf，空白文件

~~~sh
sudo touch gres.conf
~~~

##### slurmdbd.conf

- 管理节点/etc/slurm/下

~~~sh
AuthType=auth/munge
AuthInfo=/var/run/munge/munge.socket.2
#
# slurmDBD info
DbdAddr=localhost
DbdHost=localhost
#DbdPort=7031
SlurmUser=slurm
#MessageTimeout=300
DebugLevel=4
#DefaultQOS=normal,standby
LogFile=/var/log/slurm/slurmdbd.log
PidFile=/var/run/slurmdbd.pid
#PluginDir=/usr/lib/slurm
#PrivateData=accounts,users,usage,jobs
#TrackWCKey=yes
#
# Database info
StorageType=accounting_storage/mysql
StorageHost=localhost
StoragePort=3306
StoragePass=REPLACE_WITH_STRONG_PASSWORD
StorageUser=slurm
StorageLoc=slurm_acct_db
~~~

~~~sh
sudo chown slurm:slurm /etc/slurm/slurmdbd.conf
sudo chmod 600 /etc/slurm/slurmdbd.conf
sudo mkdir -p /var/log/slurm/
sudo touch /var/log/slurm/slurmdbd.log
sudo chown slurm: /var/log/slurm/slurmdbd.log
~~~

#### 配置同步/权限修改

~~~sh
sudo mkdir -p /var/spool/slurm/ctld
#sudo chmod 0755 /var/spool
sudo chmod 0755 /var/spool/slurm
#sudo chown -R slurm:slurm /var/spool
sudo chown -R slurm:slurm /var/spool/slurm
#sudo chmod 0755 /var/spool/slurm/d
sudo chown slurm: /var/log/slurm
~~~

#### 配置slurm环境变量

~~~sh
#给所有用户添加环境变量
su root
vim /etc/profile
# 添加
# export PATH=$PATH:/usr/local/bin
# export PATH=$PATH:/usr/local/sbin
source /etc/profile
~~~

#### 启动服务

~~~sh
sudo systemctl enable slurmdbd
sudo systemctl start slurmdbd
sudo systemctl status slurmdbd

sudo systemctl enable slurmctld
sudo systemctl start slurmctld
sudo systemctl status slurmctld
~~~

---

### compute node安装slurm

#### 创建slurm用户

~~~sh
for i in `seq 1 4`; do
ssh test@cn01dl00$i "getent group 1109;id 1109";
done

for i in `seq 1 4`; do
ssh -t test@cn01dl00$i "sudo groupadd -g 1109 slurm;sudo useradd -m -c \"Slurm manager\" -d /var/lib/slurm -u 1109 -g slurm -s /bin/bash slurm";
done
~~~

#### 编译安装slurm

https://slurm.schedmd.com/quickstart_admin.html#debuild

~~~sh
#management node上
sudo su
for i in `seq 1 4`; do
scp slurm-22.05.11.tar.bz2 test@cn01dl00$i:~/;
done
#Install basic Debian package build requirements:
sudo apt install build-essential fakeroot devscripts equivs make hwloc libdbus-1-dev libhwloc-dev libcgns-dev libcgroup-dev
#Unpack the distributed tarball:
for i in `seq 1 4`; do
ssh -t test@cn01dl00$i "cd ~; sudo tar -xaf slurm*tar.bz2";
done

for i in `seq 1 4`; do
ssh -t test@cn01dl00$i "cd ~/slurm-22.05.11;sudo ./configure --prefix=/usr/local --disable-debug --sysconfdir=/etc/slurm";
done

#./configure --prefix=/usr/local --disable-dependency-tracking --disable-debug --disable-x11 --enable-really-no-cray --enable-salloc-kill-cmd --with-hdf5=no --sysconfdir=/etc/slurm --enable-pam --with-pam_dir={{ slurm_pam_lib_dir }} --with-shared-libslurm --without-rpath --with-pmix=/usr/local --with-hwloc=/opt/deepops/hwloc
for i in `seq 1 4`; do
ssh -t test@cn01dl00$i "cd ~/slurm-22.05.11;sudo make -j16";
done

for i in `seq 1 4`; do
ssh -t test@cn01dl00$i "cd ~/slurm-22.05.11;sudo make install";
done

for i in `seq 1 4`; do
ssh -t test@cn01dl00$i "cd ~/slurm-22.05.11;sudo cp -r ./etc/slurm*.service /etc/systemd/system/";
done
~~~

#### slurm配置文件

##### cgroup.conf

~~~sh
#配置文件是放在--sysconfdir=/etc/slurm下
for i in `seq 1 4`; do
ssh -t test@cn01dl00$i "sudo mkdir -p /etc/slurm/";
done
~~~

~~~sh
#compute node上
cd /etc/slurm/
sudo tee cgroup.conf <<'EOF'
###
#
# Slurm cgroup support configuration file
#
# See man slurm.conf and man cgroup.conf for further
# information on cgroup configuration parameters
#--
CgroupAutomount=yes

ConstrainCores=no
ConstrainRAMSpace=no
EOF
~~~

##### slurm.conf

- 复制控制节点的配置文件过来

~~~sh
sudo su
for i in `seq 1 4`; do
scp slurm.conf test@cn01dl00$i:/etc/slurm/;
done
~~~

##### gres.conf

- 客户端/etc/slurm/下新建gres.conf

~~~sh
#AutoDetect=nvml
Name=gpu Type=H800 File=/dev/nvidia[0-7]
~~~

#### 配置同步/权限修改

~~~sh
for i in `seq 1 4`; do
ssh -t test@cn01dl00$i "sudo mkdir -p /var/spool/slurm/d;sudo chmod 0755 /var/spool/slurm;sudo chown -R slurm:slurm /var/spool/slurm;sudo chown -R slurm:slurm /var/spool/slurm;sudo chmod 755 /var/spool/slurm/d;sudo mkdir -p /var/log/slurm;sudo touch /var/log/slurm/slurmd.log;sudo chown slurm: /var/log/slurm;sudo chmod 644 /var/log/slurm/slurmd.log";
done
~~~

#### 配置slurm环境变量

~~~sh
#给所有用户添加环境变量
su root
vim /etc/profile
#添加
export PATH=$PATH:/usr/local/bin
export PATH=$PATH:/usr/local/sbin
source /etc/profile
~~~

#### 启动服务

~~~sh
for i in `seq 1 4`; do
ssh -t test@cn01dl00$i "sudo systemctl enable slurmd;sudo systemctl start slurmd;sudo systemctl status slurmd"
done
~~~

---

### login node安装slurm

#### 创建slurm用户

~~~sh
getent group 1109
id 1109
sudo groupadd -g 1109 slurm
sudo useradd -m -c "Slurm manager" -d /var/lib/slurm -u 1109 -g slurm -s /bin/bash slurm
~~~

- 检查slurm用户存在

~~~sh
id slurm
~~~

#### 编译安装slurm

https://slurm.schedmd.com/quickstart_admin.html#debuild

~~~sh
#management node上
scp slurm-22.05.11.tar.bz2 ubuntu@CN01Z99SLU002:~/
#Install basic Debian package build requirements:
sudo apt install build-essential fakeroot devscripts equivs make hwloc libhwloc-dev libmunge-dev libmunge2
#Unpack the distributed tarball:
sudo tar -xaf slurm*tar.bz2
cd slurm-22.05.11
#这里看一下Hal的配置，安装位置怎么定义的？
sudo ./configure --prefix=/usr/local --disable-debug --sysconfdir=/etc/slurm

#./configure --prefix=/usr/local --disable-dependency-tracking --disable-debug --disable-x11 --enable-really-no-cray --enable-salloc-kill-cmd --with-hdf5=no --sysconfdir=/etc/slurm --enable-pam --with-pam_dir={{ slurm_pam_lib_dir }} --with-shared-libslurm --without-rpath --with-pmix=/usr/local --with-hwloc=/opt/deepops/hwloc

sudo make -j16
sudo make install
sudo cp -r ./etc/slurm*.service /etc/systemd/system/
~~~

#### slurm配置文件

```sh
#配置文件是放在--sysconfdir=/etc/slurm下
sudo mkdir -p /etc/slurm/
cd /etc/slurm/
```

##### slurm.conf

- 复制management node的slurm.conf

#### 配置同步/权限修改

~~~sh
sudo mkdir -p /var/spool/slurm/d
sudo chmod 0755 /var/spool/slurm
sudo chown -R slurm:slurm /var/spool/slurm
sudo chmod 755 /var/spool/slurm/d
sudo mkdir -p /var/log/slurm
sudo touch /var/log/slurm/slurmd.log
sudo chown slurm: /var/log/slurm
sudo chmod 644 /var/log/slurm/slurmd.log
~~~

#### 配置slurm环境变量

~~~sh
#给所有用户添加环境变量
sudo su
vim /etc/profile
#添加
export PATH=$PATH:/usr/local/bin
export PATH=$PATH:/usr/local/sbin
source /etc/profile
~~~

#### 启动服务

~~~sh
#login node上不需要启动daemon，二进制安装完，维护同样的slurm.conf就行
~~~

---

### 配置account和user

- 增加slurm账号

~~~sh
sudo sacctmgr create account Name=jade-slurm-user
~~~

- 关联linux user与slurm account、partition

~~~sh
sudo sacctmgr add user <username> DefaultAccount=jade-slurm-user Partition=zprodhigh,zprod,zprodlow,zprodtest,zprodcpu
#已经添加的user: ubuntu、slurm、petwan、liuwan、siyyan、svc-simulation、jinfen、hanxux、guanix,tomche
#注：ubuntu用户在dl节点不存在，但是prolog要读取提交作业的用户来在dl节点创建文件，所以用ubuntu用户提交任务的时候会报prolog失败
~~~

-  查看账户用户分区的情况

~~~sh
sacctmgr show ass format="Cluster,Account,User,Partition,QOS"
~~~

- qos配置 https://icode.pku.edu.cn/SCOW/docs/slurm

---

### 配置prolog

- 在所有计算节点上以 root 创建 Prolog 脚本；目标用户名和作业 ID 由 Slurm 提供，正式启用前确认 `/raid/localtmp` 的挂载和配额策略。

~~~sh
sudo install -d -o root -g root -m 0755 /etc/slurm/prolog.d
sudo tee /etc/slurm/prolog.d/50-zen <<'EOF'
#!/bin/bash
: "${SLURM_JOB_USER:?}" "${SLURM_JOB_ID:?}"
job_dir="/raid/localtmp/$SLURM_JOB_USER/$SLURM_JOB_ID"
if [ ! -d "$job_dir" ]; then
  mkdir -p -- "$job_dir"
  chown "$SLURM_JOB_USER" -- "$job_dir"
fi
EOF
sudo chown root:root /etc/slurm/prolog.d/50-zen
sudo chmod 0755 /etc/slurm/prolog.d/50-zen
~~~

- uncomment掉所有节点上/etc/slurm/slurm.conf上面的prolog配置

~~~sh
vim /etc/slurm/slurm.conf
# Prolog/Epilog #前处理及后处理
Prolog=/etc/slurm/prolog.d/50-zen
#Epilog=/etc/slurm/epilog.sh
PrologFlags=Alloc,Serial,Contain
BatchStartTimeout=120
#MailProg=/usr/bin/s-nail
~~~

~~~sh
#控制节点上运行：
scontrol reconfigure
~~~

---

### 配置epilog

- 在所有计算节点创建 epilog 目录和脚本。脚本保留原有“抢占时不清理运行代码”的设计，但依赖 `slurmd.log` 文本匹配；正式启用前先用普通完成、取消和抢占三种作业验证。已移除未使用的 `squeue` 调用，并为删除路径加引号与作业 ID 检查。

~~~sh
#控制节点ubuntu用户执行
for i in `seq 1 4`; do
ssh -t root@cn01dl00$i "mkdir -p /etc/slurm/epilog.d/";
done

#控制节点执行
tee ./90-zen <<'EOF'
#!/bin/bash

# 原记录通过 slurmd.log 文本识别抢占；启用前须在目标集群验证日志格式。
: "${SLURM_JOB_USER:?}" "${SLURM_JOB_ID:?}"
case "$SLURM_JOB_USER" in */*|.|.. ) exit 1 ;; esac
case "$SLURM_JOB_ID" in *[!0-9]* ) exit 1 ;; esac
RUNNING_CODE=/staging/ziit/slurm/running-code
SAVE_FOR_REQUEUE=$(grep --count --max-count=1 -E "JOB $SLURM_JOB_ID ON .* CANCELLED AT .* DUE TO PREEMPTIONS" /var/log/slurm/slurmd.log)

if [ -d "$RUNNING_CODE/$SLURM_JOB_USER/job-$SLURM_JOB_ID" ] && [ "$SAVE_FOR_REQUEUE" -eq 0 ]; then
  sudo -u "$SLURM_JOB_USER" rm -rf -- "$RUNNING_CODE/$SLURM_JOB_USER/job-$SLURM_JOB_ID"
fi

if [ -d "/raid/localtmp/$SLURM_JOB_USER/$SLURM_JOB_ID" ]; then
  rm -rf -- "/raid/localtmp/$SLURM_JOB_USER/$SLURM_JOB_ID"
fi
EOF

for i in `seq 1 4`; do
scp ./90-zen root@cn01dl00$i:/etc/slurm/epilog.d/90-zen;
done

for i in `seq 1 4`; do
ssh -t root@cn01dl00$i "chmod 755 /etc/slurm/epilog.d/90-zen;chmod 755 /etc/slurm/epilog.d/;chown root: /etc/slurm/epilog.d/;chown root: /etc/slurm/epilog.d/90-zen";
done
~~~

- uncomment掉/etc/slurm/slurm.conf上面的epilog配置，同步配置文件

~~~sh
#控制节点上
vim /etc/slurm/slurm.conf
# Prolog/Epilog #前处理及后处理
Prolog=/etc/slurm/prolog.d/50-zen
Epilog=/etc/slurm/epilog.d/90-zen
PrologFlags=Alloc,Serial,Contain
BatchStartTimeout=120
#MailProg=/usr/bin/s-nail

for i in `seq 1 4`; do
scp /etc/slurm/slurm.conf root@cn01dl00$i:/etc/slurm/slurm.conf;
done

for i in `seq 1 4`; do
scp /etc/slurm/slurm.conf root@cn01z99slu002:/etc/slurm/slurm.conf;
done
~~~

~~~sh
#控制节点执行
scontrol reconfigure
ssh -t ubuntu@cn01z99slu002 "scontrol reconfigure";

for i in `seq 1 4`; do
ssh -t root@cn01dl00$i "scontrol reconfigure";
done
~~~

---

## 23.11.4 deb 包实验环境：um1 / uc1 / ul1

原记录的 Ubuntu 22.04.4 实验机器为 2 vCPU、4 GB，用户信息为 `hangx hangx / root root`（历史凭据，不要复用），三节点分别为 `um1`、`uc1`、`ul1`。本流程先从 Slurm 23.11.4 源码构建 deb 包，再按节点角色安装；它不是直接从 Ubuntu 仓库安装 Slurm。

### 环境准备

- IP配置

  - Ubuntu系统安装时,可以在网卡配置页面,将ens33设置为静态IP。
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

  - Ubuntu系统安装时,在mirror address页面上,配置为清华镜像源: https://mirrors.tuna.tsinghua.edu.cn/help/ubuntu/

  - 设置主机名

~~~sh
sudo hostnamectl set-hostname um1 && bash
sudo hostnamectl set-hostname uc1 && bash
sudo hostnamectl set-hostname ul1 && bash
~~~

- 添加hosts

~~~sh
cat >> /etc/hosts << EOF
172.16.183.130 um1
172.16.183.131 uc1
172.16.183.132 ul1
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
ssh-copy-id -i ~/.ssh/id_rsa.pub ul1
~~~

---

### 配置 MUNGE

23.11.4 环境同样在所有节点创建 UID/GID 为 1108 的 `munge` 用户；原记录仅安装 `munge` 包（22.05.11 同时安装 `libmunge-dev`、`libmunge2`），管理节点使用 `rng-tools`/`rngd`。用户与熵源命令及 `munge -n`、`unmunge`、`remunge` 验证方法已在上方 22.05.11 测试环境的 MUNGE 章节列出，目标主机改为 `um1`、`uc1`、`ul1`。

~~~sh
# 每台节点：先核对 UID/GID 1108 未占用，再创建用户并安装 MUNGE
getent group 1108
sudo groupadd -g 1108 munge
sudo useradd -m -c "Munge Uid 'N' Gid Emporium" -d /var/lib/munge -u 1108 -g munge -s /sbin/nologin munge
sudo apt -y install munge

# 仅在 um1 生成一次共享密钥，并使用上方的受限分发流程
# targets=(root@uc1 root@ul1)；若 root SSH 不可用，改为可 sudo 的 SSH 用户
# 原记录另列 create-munge-key 作为生成命令；不要在各节点分别运行，以免密钥不同。

# 所有节点：恢复属主和权限，启动并验证服务
sudo chown munge:munge /etc/munge/munge.key
sudo chmod 0400 /etc/munge/munge.key
sudo systemctl enable --now munge
sudo systemctl status munge
munge -n | unmunge
remunge
~~~

~~~sh
# 从 um1 测试跨节点凭据；也可从计算/登录节点反向测试
munge -n | ssh uc1 unmunge
munge -n | ssh ul1 unmunge
~~~

### 配置slurm

- 创建slurm用户

~~~sh
#所有节点上
groupadd -g 1109 slurm
useradd -m -c "Slurm manager" -d /var/lib/slurm -u 1109 -g slurm -s /bin/bash slurm
~~~

- 检查slurm用户存在

~~~sh
id slurm
~~~

- 从 Slurm 23.11.4 源码构建 deb 包（原记录在所有节点执行）

  https://slurm.schedmd.com/quickstart_admin.html#debuild

~~~sh
wget https://download.schedmd.com/slurm/slurm-23.11.4.tar.bz2
#Install basic Debian package build requirements:
apt-get install build-essential fakeroot devscripts equivs
#Unpack the distributed tarball:
tar -xaf slurm*tar.bz2
cd slurm-23.11.4
#Install the Slurm package dependencies:
#mk-build-deps是一个用于处理Debian包构建依赖的工具。它可以创建一个虚拟的Debian包,这个虚拟的包依赖于你的源代码包的所有构建依赖。当你安装这个虚拟的包时,所有的构建依赖也会被自动安装。-i选项告诉mk-build-deps在创建虚拟的包之后,立即尝试安装它。debian/control是Debian包的控制文件,它包含了关于包的元数据,例如包的名称、版本、描述,以及构建依赖等信息。
mk-build-deps -i debian/control
#Build the Slurm packages:
#构建二进制包,但不对改变的文件和源代码包进行签名。这个命令通常在你信任源代码,并且不需要签名的情况下使用。
debuild -b -uc -us
~~~

> [!tip] 按节点角色安装 deb 包
> `debuild` 会将包放在源码目录的上一级。原记录使用逐个 `dpkg -i`；这里将相同的软件包组合改用 `apt install ./...deb` 安装，以便处理依赖。每台目标节点都需先获得这些包，或在节点上完成相同构建。

~~~sh
# um1（控制节点）
cd ..
sudo apt install ./slurm-smd_23.11.4-1_amd64.deb ./slurm-smd-slurmctld_23.11.4-1_amd64.deb ./slurm-smd-client_23.11.4-1_amd64.deb ./slurm-smd-slurmdbd_23.11.4-1_amd64.deb

# uc1（计算节点）
cd ..
sudo apt install ./slurm-smd_23.11.4-1_amd64.deb ./slurm-smd-slurmd_23.11.4-1_amd64.deb ./slurm-smd-client_23.11.4-1_amd64.deb

# ul1（登录节点）
cd ..
sudo apt install ./slurm-smd_23.11.4-1_amd64.deb ./slurm-smd-client_23.11.4-1_amd64.deb
~~~

- 配置控制节点 Slurm。原环境规划写 2 vCPU、4 GB 内存，但原 `slurm.conf` 写 `RealMemory=5886` MiB，二者矛盾。下面保留原值作历史记录；运行前在 `uc1` 用 `nproc`、`lscpu`、`free -m` 核对，并据实修改 `NodeName=uc1`。`MaxTime=1` 是一分钟，通用示例中的 5 分钟作业不能直接提交到 `debug`。本实验未提供 `slurmdbd.conf` 或启动 `slurmdbd` 的步骤，记账功能不能视为已配置。

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
NodeName=uc1 NodeAddr=172.16.183.131 CPUs=2 RealMemory=5886 Sockets=2 CoresPerSocket=1 ThreadsPerCore=1 State=UNKNOWN
PartitionName=debug Nodes=ALL Default=YES MaxTime=1 State=UP
EOF
~~~

- 配置同步/权限修改

~~~sh
# 复制配置文件到其他节点
#其他节点
mkdir -p /etc/slurm
#master节点
scp -p /etc/slurm/*.conf root@uc1:/etc/slurm/
scp -p /etc/slurm/*.conf root@ul1:/etc/slurm/
# 设置文件权限,所有节点执行
#chmod 0755 /var/spool
#chown -R slurm:slurm /var/spool
mkdir -p /var/spool/slurm
chown slurm: /var/spool/slurm
mkdir -p /var/log/slurm
chown slurm: /var/log/slurm
mkdir -p /var/spool/slurm
chown slurm: /var/spool/slurm
mkdir -p /var/log/slurm
chown slurm: /var/log/slurm
~~~

---

### 启动服务

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

---

### 23.11.4 环境验收与 PBS 对照

原文“常用命令”与本指南下方的作业测试章节高度重复，其中 `compute`/`c1`/`c2`、`srun -N2` 和 `low` QOS 与此环境仅有的 `debug`/`uc1` 配置不符。以下命令按此配置校正；下方通用章节仍保留交互作业、`sbatch`、Python、`salloc`、`sacct`、`squeue`、`scancel` 与节点恢复命令的参数说明。`debug` 分区的时间上限为 1 分钟，提交脚本须相应缩短。

~~~sh
sinfo
scontrol show partition
scontrol show node uc1
srun -p debug -w uc1 -N1 hostname
squeue -a
# 仅在查明并修复 DOWN 原因后恢复该节点
scontrol update nodename=uc1 state=resume
~~~

原文附带的 PBS 与 Slurm 对照图及参考文章：

![PBS vs Slurm 对照图](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202403221554549.png)

[HPC 调度基础：Slurm 集群的部署与配置](https://www.ctyun.cn/developer/article/363542369067077)

## 作业调度与故障排查

以下命令主要来自 22.05.11 测试环境。单节点示例已改为该环境存在的 `cpu` 分区；带 `c2`、`c[1-2]`、`compute`、`low` QOS 等名称的历史示例仍保留其原始意图，但**不属于上面的三节点测试拓扑**，须按实际分区、QOS 和节点改写后运行。22.05.11 生产环境应改用 `zprod*` 分区和 `cn01dl00[1-4]` 节点；23.11.4 实验环境应改用 `debug` 分区和 `uc1`，并遵守 1 分钟上限。Python/sbatch 示例保留原有参数讲解和输出记录。

### 作业调度测试

#### 查看集群状态

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
#如果Compute Nodes的State=DOWN,则如下执行,将状态变成恢复
scontrol update nodename=c1 state=resume
~~~

#### 交互式提交作业

~~~sh
# --mem=5M表示申请5MB内存,-c 1表示申请1个核心。
srun -p cpu -w c1 --mem=5M -c 1 hostname
srun -J sample-job -p cpu -w c1 -N 1 -c 1 -n 1 sh -c 'whoami; hostname; ip a'
srun -J my-sleep -p cpu -w c1 -N 1 -c 1 -n 1 sleep 10
# 历史多节点示例：只有新增 c2 并纳入 cpu 分区后才可执行
# srun -J sample-job -p cpu -N 2 -c 1 -n 1 whoami;hostname;ip a;
# srun -J my-sleep -p cpu -w c[1-2] -N 2 -c 1 -n 1 sleep 10
srun -p cpu -w c1 sh ./a.sh
~~~

- 推荐使用squeue时指定输出格式如下

```text
squeue -o "%.5i %.10u %.2t %.10M %.6D %.4C %.7m   %R"
```

- 查看已经运行任务

```bash
sacct  -o jobid,jobname,partition,alloccpus,state,reqmem,averss,maxrss,exitcode  -j jobid
```

#### sbatch提交作业

~~~sh
#!/bin/bash
#SBATCH -J test             # 作业名是 test
#SBATCH -p cpu              # 提交到 cpu分区
#SBATCH -N 1                # 使用一个节点
#SBATCH --cpus-per-task=1   # 每个进程占用一个 cpu核心
#SBATCH -t 5:00             # 任务最大运行时间是5分钟
#SBATCH -o test.out         # 将屏幕的输出结果保存到当前文件夹的test.out,问题:并未有输出
hostname                    # 执行我的hostname命令

sbatch test.sh #提交作业
~~~

- 查看作业运行信息

```bash
sacct  -o jobid,jobname,partition,alloccpus,state,reqmem,averss,maxrss,exitcode  -j job-id
```

#### 示例python作业

~~~python
#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# SBATCH --output=/root/python_slurm.log
# SBATCH --partition=cpu
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
    t1.join()  # join() 等待线程终止,要不然一直挂起
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
#SBATCH --cpus-per-task=1       %指定每个进程使用核数,不指定默认为1
#SBATCH -n 32       %指定总进程数;不使用cpus-per-task,可理解为进程数即为核数
#SBATCH --ntasks-per-node=16    %指定每个节点进程数/核数,使用-n参数(优先级更高),变为每个节点最多运行的任务数
#SBATCH --nodelist=node[3,4]    %指定优先使用节点
#SBATCH --exclude=node[1,5-6]   %指定避免使用节点
#SBATCH --time=dd-hh:mm:ss      %作业最大运行时长,参考格式填写
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

#### 分配模式salloc提交作业

~~~sh
#使用salloc命令提交。为需实时处理的作业分配资源,典型场景为分配资源并启动一个shell,然 后用此shell执行srun命令去执行并行任务。
#在 cpu 分区申请一个核；原记录的 compute 分区未在本测试配置中定义
salloc -p cpu -N1 -n1 -t 2:00:00 # 若已创建 low QOS，才添加 -q low
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

#### 常见命令

~~~sh
scontrol show nodes #显示所有计算节点
#如果Compute Nodes的State=DOWN,则如下执行,将状态变成恢复
scontrol update nodename=c1 state=resume

# Why is a node shown in state DOWN when the node has registered for service?
# https://slurm.schedmd.com/faq.html#return_to_service
#The configuration parameter ReturnToService in slurm.conf controls how DOWN nodes are handled. Set its value to one in order for DOWN nodes to automatically be returned to service once the slurmd daemon registers with a valid node configuration. A value of zero is the default and results in a node staying DOWN until an administrator explicitly returns it to service using the command "scontrol update NodeName=whatever State=RESUME". See "man slurm.conf" and "man scontrol" for more details.

sacctmgr add cluster cluster-test
squeue #检查队列状况
scancel #结合作业ID,终止作业

#信息查看
scontrol show jobs              #显示作业数量
scontrol show job JOBID         #查看作业的详细信息
scontrol show node              #查看所有节点详细信息
scontrol show node node-name    #查看指定节点详细信息
scontrol show node | grep CPU   #查看各节点cpu状态
scontrol show node node-name | grep CPU #查看指定节点cpu状态
~~~

---

## 账户与参考资料

测试环境原记录只展示了账户与分区关联的查看命令：

### slurm用户账户管理

~~~sh
#在Slurm中,账户通常用于跟踪和控制用户对集群资源的使用。分区则定义了一组节点和作业在这些节点上的运行参数。
#查看所有的账户、查看账户和分区的关联
sacctmgr list assoc
#或者sacctmgr show associations
~~~

---

## 版本差异与待核实项

- 生产 `slurm.conf` 中指向 `/etc/slurm/epilog.d/90-zen` 的第二个 `Prolog=` 已改为 `Epilog=`；这是对应作业结束脚本的配置项。
- 生产账户命令将未定义的 `ztest` 改为该文实际定义的 `zprodtest`；同步命令中的 `root@@` 改为 `root@`。
- 生产 Prolog/Epilog 脚本和目录由原记录的 `chmod 777` 改为 `chmod 755`，保留执行权限并避免所有用户可写。执行前仍需检查属主与实际安全策略。
- 测试环境的单节点提交示例使用已定义的 `cpu` 分区；原记录中的两节点、`compute` 分区及 `low` QOS 示例没有相应配置，需现场改写。
- MUNGE 密钥分发已改为受限暂存与 `munge:munge 0400` 安装；数据库示例已移除固定密码和全局授权。正式使用前须替换密码占位值，并核对目标节点资源与分区。
- 生产 Epilog 已移除未使用的 `squeue` 调用，并约束删除路径；通过 `slurmd.log` 识别抢占仍是原记录的环境假设，删除范围、日志格式和执行时序须在目标集群验证。

- 23.11.4 的 deb 包构建方法与节点角色包名已与官方指南核对；其 4 GB/`RealMemory=5886` 冲突、缺少 cgroup/记账配置，以及原文旧主机名作业示例已标明，不应照抄到目标集群。

参考：[Slurm 管理员快速入门](https://slurm.schedmd.com/quickstart_admin.html)、[认证配置](https://slurm.schedmd.com/authentication.html)、[Accounting 与数据库权限](https://slurm.schedmd.com/accounting.html)、[Prolog 与 Epilog 指南](https://slurm.schedmd.com/prolog_epilog.html)、[slurm.conf 参数](https://slurm.schedmd.com/slurm.conf.html)。以上在线文档为当前版本；22.05.11 的实际配置兼容性仍需在目标集群验证。

## 相关笔记

- [[HPC/CentOS7-slurm23.02-二进制安装]] - CentOS 7 Slurm 部署
- [[HPC/Slurm-node-exporter]] - Slurm 监控
- [[HPC/PBS]] - PBS 作业调度系统
