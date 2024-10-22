# 实验环境

| Roles           | Hostname      | IP           |
| --------------- | ------------- | ------------ |
| Management node | CN01Z99SLU001 | 10.21.105.20 |
| Login node      | CN01Z99SLU002 | 10.21.105.21 |
| Compute node    | cn01dl001     | 10.21.105.11 |
| Compute node    | cn01dl002     | 10.21.105.12 |
| Compute node    | cn01dl003     | 10.21.105.13 |
| Compute node    | cn01dl004     | 10.21.105.14 |

# management/login node安装munge

- Munge用户要确保Master/login Nodes和Compute Nodes的UID和GID相同，**所有节点**都需要安装Munge;

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

- 创建全局秘钥

~~~sh
#在master节点CN01Z99SLU001上生成全局使用的秘钥文件：/etc/munge/munge.key
#装好了munge之后，/etc/munge/的权限默认是700 munge:munge; /etc/munge/munge.key的权限默认是600，munge:munge
#临时提权，为了写入key
sudo chmod 777 /etc/munge
sudo chmod 777 /etc/munge/munge.key
dd if=/dev/urandom bs=1 count=1024 > /etc/munge/munge.key
~~~

- 密钥同步到所有计算节点

~~~sh
# master节点CN01Z99SLU001，把munge key同步到其他节点
#其他所有节点上提权：
sudo chmod 777 /etc/munge
sudo chmod 777 /etc/munge/munge.key
#master节点CN01Z99SLU001上
scp /etc/munge/munge.key CN01Z99SLU002:/etc/munge/munge.key
~~~

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

# compute node安装munge

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

#提权：
for i in `seq 1 4`; do
ssh -t test@cn01dl00$i "sudo chmod 777 /etc/munge; sudo chmod 777 /etc/munge/munge.key;";
done
~~~

- management node拷贝所有节点

~~~sh
sudo su
for i in `seq 1 4`; do
scp /etc/munge/munge.key test@cn01dl00$i:/etc/munge/munge.key;
done
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

# management node安装slurm

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
#
~~~

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
Prolog=/etc/slurm/prolog.d/50-zenseact
Prolog=/etc/slurm/epilog.d/90-zenseact
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
UnkillableStepTimeout=300 #表示如果一个作业步骤在收到结束信号后300秒内仍然没有结束，那么它将被标记为“不可杀死”。

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

# Zenseact's customization
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
JobCompPass=123456
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
## Zenseact partition setup
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
StoragePass=123456    
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

## 配置同步/权限修改

~~~sh
sudo mkdir -p /var/spool/slurm/ctld
#sudo chmod 0755 /var/spool
sudo chmod 0755 /var/spool/slurm
#sudo chown -R slurm:slurm /var/spool
sudo chown -R slurm:slurm /var/spool/slurm
#sudo chmod 0755 /var/spool/slurm/d
sudo chown slurm: /var/log/slurm
~~~

## 配置slurm环境变量

~~~sh
#给所有用户添加环境变量
su root
vim /etc/profile
# 添加 
# export PATH=$PATH:/usr/local/bin
# export PATH=$PATH:/usr/local/sbin
source /etc/profile
~~~

## 启动服务

~~~sh
sudo systemctl enable slurmdbd
sudo systemctl start slurmdbd
sudo systemctl status slurmdbd

sudo systemctl enable slurmctld
sudo systemctl start slurmctld
sudo systemctl status slurmctld
~~~

# compute node安装slurm

## 创建slurm用户

~~~sh
for i in `seq 1 4`; do
ssh test@cn01dl00$i "getent group 1109;id 1109";
done

for i in `seq 1 4`; do
ssh -t test@cn01dl00$i "sudo groupadd -g 1109 slurm;sudo useradd -m -c \"Slurm manager\" -d /var/lib/slurm -u 1109 -g slurm -s /bin/bash slurm";
done
~~~

## 编译安装slurm

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

## slurm配置文件

### cgroup.conf

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

### slurm.conf

- 复制控制节点的配置文件过来

~~~sh
sudo su
for i in `seq 1 4`; do
scp slurm.conf test@cn01dl00$i:/etc/slurm/;
done
~~~

### gres.conf

- 客户端/etc/slurm/下新建gres.conf

~~~sh
#AutoDetect=nvml
Name=gpu Type=H800 File=/dev/nvidia[0-7]
~~~

## 配置同步/权限修改

~~~sh
for i in `seq 1 4`; do
ssh -t test@cn01dl00$i "sudo mkdir -p /var/spool/slurm/d;sudo chmod 0755 /var/spool/slurm;sudo chown -R slurm:slurm /var/spool/slurm;sudo chown -R slurm:slurm /var/spool/slurm;sudo chmod 755 /var/spool/slurm/d;sudo mkdir -p /var/log/slurm;sudo touch /var/log/slurm/slurmd.log;sudo chown slurm: /var/log/slurm;sudo chmod 644 /var/log/slurm/slurmd.log";
done
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
for i in `seq 1 4`; do
ssh -t test@cn01dl00$i "sudo systemctl enable slurmd;sudo systemctl start slurmd;sudo systemctl status slurmd"
done
~~~

# login node安装slurm

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

## slurm配置文件

```sh
#配置文件是放在--sysconfdir=/etc/slurm下
sudo mkdir -p /etc/slurm/
cd /etc/slurm/
```

### slurm.conf

- 复制management node的slurm.conf

## 配置同步/权限修改

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

## 配置slurm环境变量

~~~sh
#给所有用户添加环境变量
sudo su
vim /etc/profile
#添加 
export PATH=$PATH:/usr/local/bin
export PATH=$PATH:/usr/local/sbin
source /etc/profile
~~~

## 启动服务

~~~sh
#login node上不需要启动daemon，二进制安装完，维护同样的slurm.conf就行
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

# 配置account和user

- 增加slurm账号

~~~sh
sudo sacctmgr create account Name=jade-slurm-user
~~~

- 关联linux user与slurm account、partition

~~~sh
sudo sacctmgr add user <username> DefaultAccount=jade-slurm-user Partition=zprodhigh,zprod,zprodlow,ztest,zprodcpu
#已经添加的user: ubuntu、slurm、petwan、liuwan、siyyan、svc-simulation、jinfen、hanxux、guanix,tomche
#注：ubuntu用户在dl节点不存在，但是prolog要读取提交作业的用户来在dl节点创建文件，所以用ubuntu用户提交任务的时候会报prolog失败
~~~

-  查看账户用户分区的情况

~~~sh
sacctmgr show ass format="Cluster,Account,User,Partition,QOS"
~~~

- qos配置 https://icode.pku.edu.cn/SCOW/docs/slurm

# 配置prolog

- 所有计算节点上创建prolog目录和脚本

~~~sh
mkdir -p /etc/slurm/prolog.d/
tee /etc/slurm/prolog.d/50-zenseact <<'EOF'
#!/bin/bash
if [ ! -d "/raid/localtmp/${SLURM_JOB_USER}/${SLURM_JOB_ID}" ]
then
  mkdir -p /raid/localtmp/${SLURM_JOB_USER}/${SLURM_JOB_ID}
  chown ${SLURM_JOB_USER} /raid/localtmp/${SLURM_JOB_USER}/${SLURM_JOB_ID}
fi 
EOF

chmod 777 /etc/slurm/prolog.d/
chmod 777 /etc/slurm/prolog.d/50-zenseact
~~~

- uncomment掉所有节点上/etc/slurm/slurm.conf上面的prolog配置

~~~sh
vim /etc/slurm/slurm.conf
# Prolog/Epilog #前处理及后处理
Prolog=/etc/slurm/prolog.d/50-zenseact
#Epilog=/etc/slurm/epilog.sh
PrologFlags=Alloc,Serial,Contain
BatchStartTimeout=120
#MailProg=/usr/bin/s-nail
~~~

~~~sh
#控制节点上运行：
scontrol reconfigure
~~~

# 配置epilog

- 所有节点创建epilog目录和脚本

~~~sh
#控制节点ubuntu用户执行
for i in `seq 1 4`; do
ssh -t root@cn01dl00$i "mkdir -p /etc/slurm/epilog.d/";
done

#控制节点执行
tee ./90-zenseact <<'EOF'
#!/bin/bash

THISHOST=$(hostname)
JOBLIST=$(/usr/local/bin/squeue -h -u ${SLURM_JOB_USER} -w ${THISHOST} -o "%i")
JOBSHERE=$(echo $JOBLIST|wc -w)
RUNNING_CODE=/staging/ziit/slurm/running-code

SAVE_FOR_REQUEUE=$(grep --count --max-count=1 -E "JOB $SLURM_JOB_ID ON .* CANCELLED AT .* DUE TO PREEMPTIONS" /var/log/slurm/slurmd.log)

if [ -d $RUNNING_CODE/$SLURM_JOB_USER/job-$SLURM_JOB_ID ] && [ $SAVE_FOR_REQUEUE == 0 ] 
  then
    sudo -u $SLURM_JOB_USER rm -rf $RUNNING_CODE/$SLURM_JOB_USER/job-$SLURM_JOB_ID
fi

if [ -d /raid/localtmp/${SLURM_JOB_USER}/${SLURM_JOB_ID} ]
  then
    rm -rf /raid/localtmp/${SLURM_JOB_USER}/${SLURM_JOB_ID}
fi
EOF

for i in `seq 1 4`; do
scp ./90-zenseact root@cn01dl00$i:/etc/slurm/epilog.d/90-zenseact;
done

for i in `seq 1 4`; do
ssh -t root@cn01dl00$i "chmod 777 /etc/slurm/epilog.d/90-zenseact;chmod 777 /etc/slurm/epilog.d/;chown root: /etc/slurm/epilog.d/;chown root: /etc/slurm/epilog.d/90-zenseact";
done
~~~

- uncomment掉/etc/slurm/slurm.conf上面的epilog配置，同步配置文件

~~~sh
#控制节点上
vim /etc/slurm/slurm.conf
# Prolog/Epilog #前处理及后处理
Prolog=/etc/slurm/prolog.d/50-zenseact
Epilog=/etc/slurm/epilog.d/90-zenseact
PrologFlags=Alloc,Serial,Contain
BatchStartTimeout=120
#MailProg=/usr/bin/s-nail

for i in `seq 1 4`; do
scp /etc/slurm/slurm.conf root@cn01dl00$i:/etc/slurm/slurm.conf;
done

for i in `seq 1 4`; do
scp /etc/slurm/slurm.conf root@@cn01z99slu002:/etc/slurm/slurm.conf;
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

