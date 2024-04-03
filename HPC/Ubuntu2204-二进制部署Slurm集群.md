# 实验机器规划

- OS：[ubuntu-22.04.4-live-server-amd64.iso](https://mirrors.tuna.tsinghua.edu.cn/ubuntu-releases/22.04/ubuntu-22.04.4-live-server-amd64.iso)

- 2vcpu，4GB内存。

- User：

  - hangx hangx
  - root root

- IP地址规划

  - 172.16.183.130 um1

  - 172.16.183.131 uc1

  - 172.16.183.132 ul1

# 环境准备

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

# 配置munge

- Munge用户要确保Master Node和Compute Nodes的UID和GID相同，**所有节点**都需要安装Munge；

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
# 所有节点
apt -y install munge
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
# Master Node执行，把munge key同步到其他节点
scp /etc/munge/munge.key root@uc1:/etc/munge/ ; done
scp /etc/munge/munge.key root@ul1:/etc/munge/ ; done
~~~

- 检查账户是否存在

~~~sh
#所有节点执行
id munge
#uid=1108(munge) gid=1108(munge) groups=1108(munge)
~~~

- 修改配置属主，启动所有节点

~~~sh
# 所有节点执行
chown munge: /etc/munge/munge.key
chmod 400 /etc/munge/munge.key
chown munge.munge /etc/munge/munge.key
systemctl start munge
systemctl enable --now munge
systemctl status munge
ps -ef | grep munge ;done
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
munge -n | ssh ul1 unmunge
```

- Munge凭证基准测试

```sh
remunge
```

# 配置slurm

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

- 编译安装slurm - 所有节点

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
  cd ..
  dpkg -i slurm-smd_23.11.4-1_amd64.deb
  dpkg -i slurm-smd-slurmctld_23.11.4-1_amd64.deb
  dpkg -i slurm-smd-client_23.11.4-1_amd64.deb
  dpkg -i slurm-smd-slurmdbd_23.11.4-1_amd64.deb
  #uc1上
  cd ..
  dpkg -i slurm-smd_23.11.4-1_amd64.deb
  dpkg -i slurm-smd-slurmd_23.11.4-1_amd64.deb
  dpkg -i slurm-smd-client_23.11.4-1_amd64.deb
  #ul1上
  cd ..
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
scp -p /etc/slurm/*.conf root@uc1:/etc/slurm/;done
scp -p /etc/slurm/*.conf root@ul1:/etc/slurm/;done
# 设置文件权限，所有节点执行
#chmod 0755 /var/spool
#chown -R slurm:slurm /var/spool
mkdir -p /var/spool/slurm
chown slurm: /var/spool/slurm
mkdir -p /var/log/slurm
chown slurm: /var/log/slurm
mkdir -p /var/spool/slurm
chown slurm: /var/spool/slurm
mkdir -p /var/log/slurm;done
chown slurm: /var/log/slurm
~~~

# 启动服务

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

# 常用命令

## 查看集群状态

~~~sh
# 查看集群
sinfo
scontrol show partition
scontrol show node

# 提交作业 
srun -N2 hostname
scontrol show jobs

# 查看作业
squeue -a
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
#SBATCH -p compute          # 提交到 compute分区
#SBATCH -N 1                # 使用一个节点
#SBATCH --cpus-per-task=1   # 每个进程占用一个 cpu核心
#SBATCH -t 5:00             # 任务最大运行时间是5分钟
#SBATCH -o test.out         # 将屏幕的输出结果保存到当前文件夹的test.out，问题：并未有输出
hostname                    # 执行我的hostname命令
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

## PBS vs Slurm

![image-20240322155447470](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202403221554549.png)

[HPC调度基础：slurm集群的部署与配置-天翼云开发者社区 - 天翼云 (ctyun.cn)](https://www.ctyun.cn/developer/article/363542369067077)

