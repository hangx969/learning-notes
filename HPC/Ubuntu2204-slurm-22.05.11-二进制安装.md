# 实验机器规划

- OS：[ubuntu-22.04.4-live-server-amd64.iso](https://mirrors.tuna.tsinghua.edu.cn/ubuntu-releases/22.04/ubuntu-22.04.4-live-server-amd64.iso)
- User：

  - hangx hangx
  - root root
- IP地址规划

  - 172.16.183.133 m1

  - 172.16.183.134 c1

  - 172.16.183.135 l1

# 环境准备

- IP配置

  - Ubuntu系统安装时，可以在网卡配置页面，将ens33设置为静态IP。

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

# 配置munge

- Munge用户要确保Master Node和Compute Nodes的UID和GID相同，**所有节点**都需要安装Munge；

~~~sh
#所有节点上
#验证gid为1108的组不存在
getent group 1108
sudo groupadd -g 1108 munge
sudo useradd -m -c "Munge Uid 'N' Gid Emporium" -d /var/lib/munge -u 1108 -g munge -s /sbin/nologin munge
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

- 创建全局秘钥

~~~sh
#在Master Node生成全局使用的秘钥文件：/etc/munge/munge.key
#装好了munge之后，/etc/munge/的权限默认是700，munge:munge; /etc/munge/munge.key的权限默认是600，munge:munge
#临时提权，为了写入key
sudo chmod 777 /etc/munge
sudo chmod 777 /etc/munge/munge.key
dd if=/dev/urandom bs=1 count=1024 > /etc/munge/munge.key
~~~

- 密钥同步到所有计算节点

~~~sh
# Master Node执行，把munge key同步到其他节点
#其他节点上：
sudo chmod 777 /etc/munge
sudo chmod 777 /etc/munge/munge.key
scp /etc/munge/munge.key c1:/etc/munge/
scp /etc/munge/munge.key l1:/etc/munge/
~~~

- 检查账户是否存在

~~~sh
#所有节点执行
sudo id munge
#uid=1108(munge) gid=1108(munge) groups=1108(munge)
~~~

- 修改配置属主，启动所有节点

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

- 验证compute node，控制节点进行连接验证

```sh
munge -n | ssh m1 unmunge
munge -n | ssh c1 unmunge
munge -n | ssh l1 unmunge
#如果出现unmunge: Error: Invalid credential，重启节点，报错消失
```

- Munge凭证基准测试

```sh
remunge
```

# 控制节点安装slurm

## 创建slurm用户

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

## 编译安装slurm

https://slurm.schedmd.com/quickstart_admin.html#debuild

~~~sh
wget https://download.schedmd.com/slurm/slurm-22.05.11.tar.bz2
#Install basic Debian package build requirements:
sudo apt-get install build-essential fakeroot devscripts equivs make hwloc libhwloc-dev mariadb-server libmysqlclient-dev #libmunge-dev libmunge2
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

## 配置数据库

```sh
sudo systemctl enable mariadb        
sudo systemctl start mariadb        
sudo systemctl status mariadb
```

```sh
sudo mysql
CREATE USER 'slurm'@'localhost' IDENTIFIED BY '123456';
GRANT ALL ON *.* TO 'slurm'@'localhost';
create database slurm_acct_db;
grant all on slurm_acct_db.* to 'slurm'@'localhost' identified by '123456' with grant option;
exit;
```

## slurm配置文件

### cgroup.conf

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

### slurm.conf

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
JobCompPass=123456
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

### gres.conf

- 控制节点/etc/slurm/下新建gres.conf，空白文件

~~~sh
sudo touch gres.conf
~~~

### slurmdbd.conf

- 管理节点/etc/slurm/下

~~~sh
AuthType=auth/munge
AuthInfo=/var/run/munge/munge.socket.2
#
# slurmDBD info
DbdAddr=localhost #？这里的Ip所有节点都一样吗
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
StoragePass=123456    
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

## 配置同步/权限修改

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

## 配置slurm环境变量

~~~sh
#给所有用户添加环境变量
su root
vim /etc/profile
#添加 
# export PATH=$PATH:/usr/local/bin
# export PATH=$PATH:/usr/local/sbin
source /etc/profile
~~~

## 启动服务

~~~sh
#m1上
sudo systemctl enable slurmdbd
sudo systemctl start slurmdbd
sudo systemctl status slurmdbd

sudo systemctl enable slurmctld
sudo systemctl start slurmctld
sudo systemctl status slurmctld
~~~

# 计算节点安装slurm

## 创建slurm用户

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

## 编译安装slurm

https://slurm.schedmd.com/quickstart_admin.html#debuild

~~~sh
wget https://download.schedmd.com/slurm/slurm-22.05.11.tar.bz2
#Install basic Debian package build requirements:
sudo apt-get install build-essential fakeroot devscripts equivs make hwloc libdbus-1-dev libhwloc-dev libmunge-dev libmunge2 mariadb-server libmysqlclient-dev libcgns-dev libcgroup-dev
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

## slurm配置文件

### cgroup.conf

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

### slurm.conf

- 复制控制节点的配置文件过来

### gres.conf

- 客户端/etc/slurm/下新建gres.conf

~~~sh
#AutoDetect=nvml
Name=gpu Type=H800 File=/dev/nvidia[0-7]
~~~

## 配置同步/权限修改

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

## 配置slurm环境变量

~~~sh
#给所有用户添加环境变量
su root
vim /etc/profile
#添加 
export PATH=$PATH:/usr/local/bin
export PATH=$PATH:/usr/local/sbin
source /etc/profile
~~~

## 启动服务

~~~sh
sudo systemctl enable slurmd
sudo systemctl start slurmd
sudo systemctl status slurmd
~~~

# 登录节点安装slurm

## 创建slurm用户

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

## 编译安装slurm

https://slurm.schedmd.com/quickstart_admin.html#debuild

~~~sh
wget https://download.schedmd.com/slurm/slurm-22.05.11.tar.bz2
#Install basic Debian package build requirements:
sudo apt-get install build-essential fakeroot devscripts equivs make hwloc libhwloc-dev libmunge-dev libmunge2
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

## slurm配置文件

```sh
#配置文件是放在--sysconfdir=/etc/slurm下
sudo mkdir /etc/slurm/
cd /etc/slurm/
```

### slurm.conf

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
JobCompPass=123456
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

## 配置同步/权限修改

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

## 配置slurm环境变量

~~~sh
#给所有用户添加环境变量
su root
vim /etc/profile
#添加 
# export PATH=$PATH:/usr/local/bin
# export PATH=$PATH:/usr/local/sbin
source /etc/profile
~~~

## 启动服务

~~~sh
#l1上不需要启动daemon，二进制安装完，维护同样的slurm.conf就行
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

# slurm用户账户管理

~~~sh
#在Slurm中，账户通常用于跟踪和控制用户对集群资源的使用。分区则定义了一组节点和作业在这些节点上的运行参数。
#查看所有的账户、查看账户和分区的关联
sacctmgr list assoc
#或者sacctmgr show associations
~~~

