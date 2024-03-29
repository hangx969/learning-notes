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

# 安装slurm

- 创建slurm用户

~~~sh
#所有节点上
getent group 1109
id 1109
sudo groupadd -g 1109 slurm
sudo useradd -m -c "Slurm manager" -d /var/lib/slurm -u 1109 -g slurm -s /bin/bash slurm
~~~

- 检查slurm用户存在

~~~sh
id slurm
~~~

- 编译安装slurm - 所有节点

  https://slurm.schedmd.com/quickstart_admin.html#debuild

~~~sh
wget https://download.schedmd.com/slurm/slurm-22.05.11.tar.bz2
#Install basic Debian package build requirements:
sudo apt-get install build-essential fakeroot devscripts equivs make hwloc libhwloc-dev libmunge-dev libmunge2 mariadb-server libmysqlclient-dev
#Unpack the distributed tarball:
sudo tar -xaf slurm*tar.bz2
cd slurm-22.05.11
#这里看一下Hal的配置，安装位置怎么定义的？
sudo ./configure --prefix=/usr/local --disable-debug --sysconfdir=/etc/slurm

#./configure --prefix=/usr/local --disable-dependency-tracking --disable-debug --disable-x11 --enable-really-no-cray --enable-salloc-kill-cmd --with-hdf5=no --sysconfdir=/etc/slurm --enable-pam --with-pam_dir={{ slurm_pam_lib_dir }} --with-shared-libslurm --without-rpath --with-pmix=/usr/local --with-hwloc=/opt/deepops/hwloc

sudo make -j16 
sudo make install
~~~

# 配置数据库

```sh
sudo cp -r ./etc/slurm*.service /etc/systemd/system/
sudo systemctl enable mariadb         
sudo systemctl start mariadb         
sudo systemctl status mariadb      
```

进入数据库

```sh
sudo mysql
CREATE USER 'slurm'@'localhost' IDENTIFIED BY '123456';
GRANT ALL ON *.* TO 'slurm'@'localhost';
create database slurm_acct_db;
grant all on slurm_acct_db.* to 'slurm'@'localhost' identified by '123456' with grant option;
exit;
```

# 配置控制节点slurm

- slurm服务端配置文件

  ~~~sh
  #配置文件是放在--sysconfdir=/etc/slurm下
  mkdir /etc/slurm/
  ~~~

  ~~~sh
  tee cgroup.conf <<'EOF'
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

  ~~~sh
  tee slurm.conf <<'EOF'
  ~~~

  ~~~sh
  #
  # Example slurm.conf file generated by DeepOps. 
  #
  # Slurm provides configurator.html
  # (in doc/html) to build a configuration file customized
  # for your environment.
  #
  # See the slurm.conf man page for more information.
  
  # Define a name for the cluster
  ClusterName=deepops
  
  # Configure the controllers
  SlurmctldHost=m1
  StateSaveLocation=/var/spool/slurm/ctld
  
  # Basic configuration
  SlurmUser=slurm
  SlurmctldPort=6817
  SlurmdPort=6818
  AuthType=auth/munge
  #JobCredentialPrivateKey=
  #JobCredentialPublicCertificate=
  SlurmdSpoolDir=/var/spool/slurm/d
  SwitchType=switch/none
  SlurmctldPidFile=/var/run/slurmctld.pid
  SlurmdPidFile=/var/run/slurmd.pid
  ProctrackType=proctrack/cgroup
  PluginDir=/usr/local/lib/slurm
  #FirstJobId=
  #MaxJobCount=
  #PlugStackConfig=
  #PropagatePrioProcess=
  #PropagateResourceLimits=
  #PropagateResourceLimitsExcept=
  PropagateResourceLimitsExcept=MEMLOCK
  
  # Basic job behavior
  ReturnToService=1
  RebootProgram="/bin/systemctl reboot"
  ResumeTimeout=900
  
  #% if slurm_include_pmix %}
  # Use PMIX as our default MPI configuration
  #piDefault=pmix
  #% endif %}
  
  # Prolog/epilog config
  #% if slurm_contain_ssh is defined %}
  #rologFlags=Alloc,Serial,Contain
  #% else %}
  #rologFlags=Alloc,Serial
  #% endif %}
  #% if slurm_enable_prolog_epilog %}
  #rolog={{ slurm_config_dir }}/prolog.sh
  #pilog={{ slurm_config_dir }}/epilog.sh
  #% endif %}
  #SrunProlog=
  #SrunEpilog=
  #TaskProlog=
  #TaskEpilog=
  
  #% if slurm_health_check_program is defined %}
  # Health checking
  #ealthCheckProgram={{ slurm_health_check_program }}
  #ealthCheckInterval=300
  #ealthCheckNodeState=IDLE
  #% endif %}
  
  # Mail program to use
  #ailProg=/usr/bin/s-nail
  
  TaskPlugin=affinity,cgroup
  #TrackWCKey=no
  #TreeWidth=50
  #TmpFS=
  #UsePAM=
  
  # TIMERS
  SlurmctldTimeout=120
  SlurmdTimeout=300
  InactiveLimit=0
  MinJobAge=300
  KillWait=30
  Waittime=0
  
  # SCHEDULING
  SchedulerType=sched/backfill
  #SchedulerAuth=
  SelectType=select/cons_tres
  SelectTypeParameters=CR_Core_Memory,CR_CORE_DEFAULT_DIST_BLOCK,CR_ONE_TASK_PER_CORE
  #PriorityType=priority/multifactor
  #PriorityDecayHalfLife=14-0
  #PriorityUsageResetPeriod=14-0
  #PriorityWeightFairshare=100000
  #PriorityWeightAge=1000
  #PriorityWeightPartition=10000
  #PriorityWeightJobSize=1000
  #PriorityMaxAge=1-0
  
  # LOGGING
  SlurmctldDebug=3
  SlurmctldLogFile=/var/log/slurm/slurmctld.log
  SlurmdDebug=3
  SlurmdLogFile=/var/log/slurm/slurmd.log
  JobCompType=jobcomp/none
  #JobCompLoc=
  
  # ACCOUNTING ---- 0329到这里
  JobAcctGatherType=jobacct_gather/cgroup
  #JobAcctGatherFrequency=30
  AccountingStorageTRES=gres/gpu
  #DebugFlags=CPU_Bind,gres
  AccountingStorageType=accounting_storage/slurmdbd
  AccountingStorageHost=m1
  #AccountingStorageLoc=
  #AccountingStorageEnforce=associations,limits,qos
  AccountingStorageUser=slurm
  AccountingStoragePass=/var/run/munge/munge.socket.2
  
  # COMPUTE NODES
  GresTypes=gpu
  
  {% for node_name in groups['slurm-node'] %}
  {% set memory =  hostvars[node_name]["ansible_local"]["memory"] -%}
  {% set cpu_topology =  hostvars[node_name]["ansible_local"]["topology"]["cpu_topology"] -%}
  {% set gpu_topology =  hostvars[node_name]["ansible_local"]["topology"]["gpu_topology"] -%}
      NodeName={{ node_name }}{{ " " -}}
      {% if slurm_manage_gpus %} {%- if gpu_topology|count %} Gres=gpu:{{ gpu_topology|count }} {% endif -%} {% endif %}
      CPUs={{ cpu_topology.logical_cpus|int }}{{ " " -}}
      Sockets={{ cpu_topology.sockets|int }}{{ " " -}}
      CoresPerSocket={{ cpu_topology.cores_per_socket|int }}{{ " " -}}
      ThreadsPerCore={{ cpu_topology.threads_per_core }}{{ " " -}}
      Procs={{ cpu_topology.sockets|int * cpu_topology.cores_per_socket|int }}{{ " " -}}
      RealMemory={{ memory.total_mb|int }}{{ " " -}}
      State=UNKNOWN
  {% endfor %}
  
  # hardcoding the partitions and default memory per node
  # TODO: automatically define the partitions by resource
  # TODO: set DefMemPerCPU = TotalMemory / LogicalCPUs
  {% set slurm_oversubscribe = (slurm_manage_gpus == true)|ternary('NO', 'EXCLUSIVE') %}
  PartitionName=batch Nodes=ALL Default=YES DefMemPerCPU=0 State=UP OverSubscribe={{ slurm_oversubscribe }} {%- if slurm_max_job_timelimit is defined %} MaxTime={{ slurm_max_job_timelimit }} {%- else %} MaxTime=INFINITE {% endif -%} {%- if slurm_default_job_timelimit is defined %} DefaultTime={{ slurm_default_job_timelimit }} {% endif -%}
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
SlurmctldHost=aictrl3
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
AccountingStorageHost=localhost
AccountingStoragePass=/var/run/munge/munge.socket.2
AccountingStorageType=accounting_storage/slurmdbd
AccountingStorageTRES=gres/gpu
JobCompHost=localhost
JobCompLoc=slurm_acct_db
JobCompPass=123456
JobCompType=jobcomp/none
JobCompUser=slurm
JobAcctGatherFrequency=30
JobAcctGatherType=jobacct_gather/linux
SlurmctldDebug=info
SlurmctldLogFile=/var/log/slurmctld.log
SlurmdDebug=info
SlurmdLogFile=/var/log/slurmd.log
GresTypes=gpu
NodeName=aiwkr1  RealMemory=1000000 Gres=gpu:8 State=UNKNOWN Sockets=2 CoresPerSocket=32 CPUs=64
NodeName=aiwkr2  RealMemory=1000000 Gres=gpu:8 State=UNKNOWN Sockets=2 CoresPerSocket=32 CPUs=64
NodeName=aiwkr3  RealMemory=1000000 Gres=gpu:8 State=UNKNOWN Sockets=2 CoresPerSocket=32 CPUs=64
PartitionName=gpu1 Nodes=aiwkr[1-3] Default=YES MaxTime=168:00:00 State=UP
PartitionName=gpu2-8 Nodes=aiwkr[1-3] Default=YES MaxTime=168:00:00 State=UP
PartitionName=cpu Nodes=aiwkr[1-3] Default=YES MaxTime=168:00:00 State=UP
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
sudo mkdir -p /var/spool/slurm
sudo chown slurm: /var/spool/slurm
sudo mkdir -p /var/log/slurm
sudo chown slurm: /var/log/slurm
sudo mkdir -p /var/spool/slurm
sudo chown slurm: /var/spool/slurm
sudo mkdir -p /var/log/slurm;done
sudo chown slurm: /var/log/slurm
~~~

# 启动服务

~~~sh
#um1上
sudo systemctl enable slurmctld
sudo systemctl start slurmctld
sudo systemctl status slurmctld
#uc1上
sudo systemctl enable slurmd
sudo systemctl start slurmd
sudo systemctl status slurmd
~~~



