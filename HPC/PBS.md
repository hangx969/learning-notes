# PBS介绍

- PBS（Portable Batch System）是一个常用的作业调度系统，用于管理和调度计算集群中的作业。它允许用户提交作业并有效地利用集群资源，使得多个用户能够共享计算资源并按照优先级执行他们的作业。


- 背景：PBS最初由NASA开发，旨在管理和调度超级计算机集群中的作业。它的设计目标是提供一个可移植、灵活和可扩展的作业管理系统，使得用户可以方便地提交、管理和跟踪作业的执行。

- 作用：PBS的主要功能是管理和调度计算集群中的作业。它允许用户提交作业描述，包括作业需要的资源、执行命令、作业优先级等信息。PBS根据资源可用性、作业优先级和调度策略等因素来决定作业的执行顺序，并负责分配计算资源给作业使用。同时，PBS还提供了查询作业状态、取消作业、节点管理等功能。

## 版本分支

PBS的目前包括openPBS, PBS Pro和Torque三个主要分支. 

- 其中OpenPBS是最早的PBS系统, 目前已经没有太多后续开发。

- PBS pro是PBS的商业版本, 功能最为丰富。

- Torque是Clustering公司接过了OpenPBS, 并给与后续支持的一个开源版本。 

## 工作流程

1. 作业提交：用户使用qsub命令提交作业到PBS系统，包括作业描述和执行脚本。
2. 作业排队：提交的作业被放置在队列中等待调度执行。
3. 资源分配：PBS根据作业需求、可用资源和调度策略，选择合适的节点分配资源。
4. 作业执行：作业在分配的节点上执行，执行期间可以通过qstat查看作业状态。
5. 作业完成：作业执行完成后，输出结果被返回给用户。

# PBS命令介绍

## 查看节点情况-pbsnodes

1. `pbsnodes -a`：这个命令将显示所有节点的详细信息，包括节点的状态、空闲核数、总核数等。
2. `pbsnodes -l free`：这个命令将列出所有空闲的节点。
3. `pbsnodes -l`：这个命令将列出所有节点的状态，包括空闲节点和正在运行的节点。

## 提交作业-qsub

- qsub 命令：用于提交作业脚本

```sh
#命令格式：
$qsub -a date_time [-C directive_prefix]
      -e path -j join -l resource_list
      -M user_list -o path -q destination
      -S path_list-v variable_list
      -W additional_attributes
#参数说明：因为所采用的选项一般放在pbs 脚本中提交，所以具体见PBS 脚本选项。
```

## 提交作业-脚本

- 当使用PBS管理作业时，需要编写PBS脚本文件来描述作业的要求、资源需求以及作业的执行流程。PBS脚本是一个文本文件，通常以.pbs为扩展名。它包含了用于描述作业要求的指令、环境设置和作业执行命令。

- 脚本结构：

~~~sh
#!/bin/bash
#PBS -N job_name  # 作业名称
#PBS -l nodes=1:ppn=4  # 分配资源，1个节点，每节点4个核心
#PBS -l walltime=01:00:00  # 预计作业运行时间
#PBS -q batch  # 队列名称

# 可选的环境设置和加载模块
module load <module_name>

# 进入工作目录
cd $PBS_O_WORKDIR

# 执行命令
<command_to_execute>
~~~

- 示例1 - 运行shell命令

  ~~~sh
  #!/bin/bash
  #PBS -N myjob
  #PBS -l nodes=1:ppn=2
  #PBS -l walltime=00:01:00
  #PBS -q batch
  
  cd $PBS_O_WORKDIR
  
  echo "Hello, PBS! This is my job."
  ~~~

- 示例2 - 运行pthon脚本

  ~~~sh
  #!/bin/bash
  #PBS -N python_job
  #PBS -l nodes=1:ppn=4
  #PBS -l walltime=01:00:00
  #PBS -q batch
  
  module load python
  
  cd $PBS_O_WORKDIR
  
  python myscript.py
  ~~~

- 示例3 - 使用MPI运行并行作业

  ~~~sh
  #!/bin/bash
  #PBS -N mpi_job
  #PBS -l nodes=4:ppn=2
  #PBS -l walltime=02:00:00
  #PBS -q batch
  
  module load mpi
  
  cd $PBS_O_WORKDIR
  
  mpirun -np 8 my_mpi_program
  ~~~

qsub test.sh即可提交作业脚本

## 查看作业状态-qstat

- qstat 命令：用于查询作业状态信息

  <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202401181740885.png" alt="image-20240118174026739" style="zoom:50%;" />

  ```sh
  #状态码
  #B  只用于任务向量，表示任务向量已经开始执行 
  #E  任务在运行后退出 
  #H  任务被服务器或用户或者管理员阻塞 
  #Q  任务正在排队中，等待被调度运行 
  #R  任务正在运行 
  #S  任务被服务器挂起，由于一个更高优先级的任务需要当前任务的资源 
  #T  任务被转移到其它执行节点了 
  #U  由于服务器繁忙，任务被挂起 
  #W  任务在等待它所请求的执行时间的到来(qsub -a) 
  #X  只用于子任务，表示子任务完成
  ```

## 删除作业-qdel

- qdel 命令：用于删除已提交的作业

```shell
#命令格式：
qdel [-W 间隔时间] 作业号
# qdel -W 15 211 #15秒后删除作业号为211 的作业
qdel -W force jobid #强制删除作业
```

## 队列管理-qmgr

- qmgr 命令—用于队列管理


```sh
qmgr -c "create queue batch queue_type=execution"
qmgr -c "set queue batch started=true"
qmgr -c "set queue batch enabled=true"
qmgr -c "set queue batch resources_default.nodes=1"
qmgr -c "set queue batch resources_default.walltime=3600"
qmgr -c "set server default_queue=batch"
```

# PBS pro学习

## 组件

- Server
  - 管理job，queue；处理命令
  - 守护进程是pbs_server.bin
- Scheduler
  - 负责调度job
  - 守护进程是pbs_sched
- MoM
  - 执行job
  - 守护进程是pbs_mom

可以将3个组件全部部署在一台服务器上；更通用的方法是将Server+scheduler部署到一台管理节点，然后部署多台MoM节点。

## 工作流程

1. User submits job
2. PBS server returns a job ID (数字+head node的hostname)
3. PBS scheduler requests a list of resources from the server
4. PBS scheduler sorts all the resources and jobs
5. PBS scheduler informs PBS server which host(s) that job  can run on
6. PBS server pushes job script to execution host(s)
7. PBS MoM executes job script
8. PBS MoM periodically reports resource usage back to PBS server
9. When job is completed PBS MoM kills the job script
10. PBS server de-queues job from PBS complex

## 提交作业

- 命令行方式

  ~~~sh
  su pbsuser1
  qsub –l select=1:ncpus=1:mem=1gb –l walltime=10:00:00 -- /bin/sleep 100
  ~~~

- ctrl+d提交

  ~~~sh
  qsub
  #回车之后开始输入命令
  #ctrl+D作业就被提交了
  ~~~

- 脚本方式

  ~~~sh
  cat pbs_script.sh
  #!/bin/bash
  #PBS –l select=1:ncpus=1:mem=1gb
  #PBS –l walltime=00:01:00
  /bin/sleep 100
  ~~~

  ~~~sh
  qsub pbs_script.sh
  ~~~

- 交互式

  ~~~sh
  su pbsuser1
  qsub -I
  #会直接给一个到计算节点的终端，可以交互式输入命令。适用于debug。
  ~~~

## 作业参数设置

- 可以通过qsub参数指定 qsub -N job_name job_script

- 可以在脚本中指定

  ~~~sh
  #!/bin/bash
  #PBS –N test_run_01
  #PBS –l select=2:ncpus=2:mem=1GB 
  #PBS –l place=scatter
  #PBS -j oe
  #PBS –o /home/pbsuser1/OUTPUTS
  ## this is a comment
  /bin/sleep 60
  ~~~

  - #PBS –l select=2:ncpus=2:mem=1GB 指定需要2个chuck，每个chunk都需要2个核心，1GB内存来处理这个任务。
  - #PBS –l place=scatter 加了这个参数，倾向于把两个chunk分散到多个node去执行

### 数组作业

- 数组作业是一种特殊类型的作业，它允许你一次提交多个相似的作业。使用一个脚本来提交多个相似的作业，而不需要为每个作业都写一个单独的脚本。这对于需要运行大量相似作业的情况非常有用，例如参数扫描或蒙特卡洛模拟。

  ~~~sh
  qsub -J 1-5 -- /bin/sleep 10
  
  qstat -answ1 #只能查看数组作业的整体状态
  qstat -t #查看数组作业中每个子成员作业的状态
  qstat -J #Shows state only
  qstat -p #Shows the % completed 
  ~~~

- 数组作业的脚本示例

  - Submit 5 jobs with odd indices (1,3,5,7,9)
  
  ~~~sh
  #!/bin/sh
  #PBS -N SimOddJobs
  #PBS -J 1-10:2
  echo "Main script: index " $PBS_ARRAY_INDEX
  /opt/AppA –input /home/user01/odd/scriptlet_$PBS_ARRAY_INDEX
  ~~~
  
  - Submit 10 jobs with consecutive index numbers
  
  ~~~sh
  #!/bin/sh
  #PBS -N Simn1010Jobs
  #PBS -J 1-10
  echo "Main script: index " $PBS_ARRAY_INDEX
  /opt/AppA –input /home/pbsuser1/runcase1/scriptlet_$PBS_ARRAY_INDEX
  ~~~

### 作业环境变量

- 作业提交之后，PBS会自动指定一些环境变量，这些变量可以被利用为参数写到脚本里

  ![image-20240204160456322](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402041604385.png)

  ~~~sh
  #!/bin/bash
  #PBS -l select=8:ncpus=16:mem=32GB
  #PBS –l place=scatter,walltime=5:00:00
  #PBS –N sim_run_01
  #PBS -M user01@altair.com
  #PBS -m abe
  #PBS -e pbsworks:/scratch/${PBS_JOBNAME}.e${PBS_JOBID}
  #PBS -o pbsworks:/scratch/${PBS_JOBNAME}.o${PBS_JOBID}
  cd $PBS_TMPDIR
  mpirun –np 128 my_script.sh
  ~~~

### 作业输出

- 作业的STDOUT和STDERR可以定义，默认$PBS_O_WORKDIR。

- 有两种方式指定

  - -o \<host>:\<path>\<filename>，-e \<host>:\<path>\<filename>

  - -k

    <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402051030441.png" alt="image-20240205103046334" style="zoom:50%;" />

  - 默认的job staging目录是user的home directory

### 作业sandbox

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402051047262.png" alt="image-20240205104714155" style="zoom:50%;" />

### 作业dependency

- qsub -W depend=afterok:1.trainta01:2.trainta01  my_script
- 有dependency的job会被置于H状态

## 查看作业状态

~~~sh
qstat -answ1 #查看当前所有作业详细信息
qstat -fx jobid
qstat -f 16.pbs1 #查看某个作业详细信息
qstat -fx 16 -F json #以json格式输出历史job的详细信息
tracejob 3.pbs1 #输出中的L代表log来自scheduler，S代表来自server

source /etc/pbs.conf
$PBS_EXEC/unsupported/pbs_dtj 3.pbs1
~~~

- 作业状态码含义

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402041408776.png" alt="image-20240204140817880" style="zoom:50%;" />

E： 说明job在exit状态，可能正在复制结果回来。如果长时间卡在E说明可能server之间的passwordless  ssh或者scp有问题。

- 作业历史

  - 管理员可以开启作业历史功能，查看过去14天的job

    ~~~sh
    qmgr -c " set server job_history_enable = true "
    qstat -H #看已经删掉、移动或完成的
    qstat -x #看所有状态的
    ~~~

- 作业日志

  - accounting log存放在pbs_server守护进程所在的server上。每天生成一个log文件，只有root能看

  ~~~sh
  cd /var/spool/pbs/server_priv/accounting/
  #其中有每日的job执行记录的log。分为E记录和S记录
  ~~~

- 筛选出特定作业 - `qselect`

  ~~~sh
  qselect –u user01 #列出属于某用户的job id
  qselect –s R –l ncpus.gt.4 #在running job中找出需求cpu大于4的job
  qstat `qselect –s E` #联合使用，找出状态是E的job，列出详细信息。
  qselect -ts.gt.09251200 -ts.lt.09251500 #列出某时间段内的job
  ~~~

## 作业其他操作

- 删除作业 - `qdel`
- 重新排队一个正在运行的job - `qrerun`
- 手动hold job - `qhold`；手动release job - `qrls`
- 定时启动任务 - `qsub -a <date time>`
- 作业提交之后，其需求的资源仍可被改变 - `qalter -l select=1:ncpus=3 0.pbs1`

## 查看节点状态

~~~sh
pbsnodes -aSjv
qstat -Bf
~~~

## 查看queue

~~~sh
qstat -q
~~~

## 查看节点资源

~~~sh
pbsnodes pbs2 #指定节点名查看节点资源情况
~~~

- 提交作业的时候，通过-l参数指定对资源的要求

  ~~~sh
  qsub -l vnode=pbs3 -- /bin/sleep 100 #指定在pbs3上运行
  qsub -l host=pbs3 -- /bin/sleep 100 #指定在pbs3上运行，效果一样
  qsub -l nodes=pbs2+pbs3 -- /bin/sleep 100 #指定在2和3上执行job
  qsub -l select=2:ncpus=2:mem=1GB -- /bin/sleep 100 
  ~~~

- What are “chunks”? 

  - Set of resources that are allocated as a unit to a job

  - Smallest set of resources that are allocated to a job，For example: ncpus, mem

  - Requested in a “select” statement

    ```sh
    qsub –l select=<#>:ncpus=<#>:mem=<#>
    #举例子：如果一个job需要总计4个相同chunk，共计32核心CPU，64GB内存，那么：
    qsub –l select=4:ncpus=8:mem=16GB xxx.sh
    ```

- 提交job的位置参数，决定了不同的chunk怎么分配给job

  ![image-20240204163420516](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402041634602.png)

- 节点资源分为node-wide和job-wide两类

  - node-wide比如cpu核心数、内存、gpu数量等；job-wide比如walltime（job预计的执行时间）、cput等。

  - job-wide的资源也可以指定：

    ~~~sh
    qsub –l select=1:ncpus=1:mem=100MB –l walltime=01:00:00 #指定1h的执行时间。如果超过这个时间还没执行完，pbs会kill掉这个job
    qsub –l select=1:ncpus=1:mem=100MB –l cput=03:00:00,walltime=02:00:00
    ~~~


## troubleshooting

- 获取job为什么没能运行的相关信息。需要以root运行

  ~~~sh
  pbs_snapshot –o /tmp
  # 30 days of accounting logs
  # 5 days of daemon logs from the server host
  ~~~

- job退出码

  - 0代表成功完成
  - 1-127代表是job自己call exit()，终止了自己
  - 129-255代表UNIX signal

- job状态含义
  - Q
    - 当前资源不足以调度任务
    - queue没有启动
    - 当前用户超出了资源限额
  - W
    - job等待input文件拷贝到job执行目录，卡在这里可能是因为pbs server和MoM之间的无密码ssh/scp有问题
    - 用户没有权限拷贝文件到job执行目录
  - H
    - user在计算节点上的认证问题：有可能是home目录没挂载
    - 可能是手动qhold了这个job，或者依赖于其他job完成
  - E
    - 计算节点到pbs server的无密码ssh/scp有问题，或者权限问题，导致结果传不回来

# docker容器部署pbspro多节点

参考教程：https://blog.csdn.net/u012460749/article/details/78583063

机器配置：

- Ubuntu 2204 - s0001969，s0001969
- 通过docker容器，安装3个pbs节点，版本为pbspro 19.0.0

进环境：

~~~sh
#可能需要现将虚拟机快照还原到fresh状态
docker ps -a
docker exec -it pbs1 /bin/bash
~~~

## 配置静态IP

https://cloud.tencent.com/developer/article/1933335

~~~yaml
network:
  version: 2
  renderer: NetworkManager
  ethernets:
    ens33:
      dhcp4: no
      dhcp6: no
      addresses: 
      - 172.16.183.128/24
      routes:               
      - to: default
        via: 172.16.183.2
      nameservers:
        addresses: [8.8.8.8, 114.114.114.114] #dns
~~~

## 安装docker

~~~sh
sudo apt-get update
#安装允许 apt 通过 HTTPS 使用存储库（repository）的必要软件包：
sudo apt-get install apt-transport-https ca-certificates curl software-properties-common 
#添加 Docker 的官方 GPG 密钥：
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
#添加 Docker APT 源：
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
#最后，更新 apt 包数据库：
sudo apt-get update
~~~

~~~sh
#关闭防火墙
systemctl stop firewalld && systemctl disable firewalld
#安装iptables防火墙
apt install iptables-services -y
#禁用iptables
service iptables stop   && systemctl disable iptables
#清空防火墙规则
iptables -F 
#关闭selinux
setenforce 0
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
#注意：修改selinux配置文件之后，重启机器，selinux才能永久生效 reboot- f
getenforce #显示Disabled表示selinux关闭成功
#配置时间同步
apt install -y ntp ntpdate
ntpdate cn.pool.ntp.org 
#编写计划任务
crontab -e 
* */1 * * * /usr/sbin/ntpdate   cn.pool.ntp.org
#重启crond服务使配置生效：
systemctl restart crond
#安装基础软件包
apt install -y  wget net-tools nfs-utils lrzsz gcc gcc-c++ make cmake libxml2-devel openssl-devel curl curl-devel unzip sudo ntp libaio-devel wget vim ncurses-devel autoconf automake zlib-devel  python-devel epel-release openssh-server socat  ipvsadm conntrack 
#安装docker依赖包
apt install -y lvm2
#安装docker-ce
apt install docker-ce -y
#启动docker服务
systemctl start docker && systemctl enable docker
systemctl status docker
#查看Docker 版本信息
docker version    
#开启包转发功能和修改内核参数
#内核参数修改：br_netfilter模块用于将桥接流量转发至iptables链，br_netfilter内核参数需要开启转发。
modprobe br_netfilter
cat > /etc/sysctl.d/docker.conf <<EOF
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
EOF
#使参数生效
sysctl -p /etc/sysctl.d/docker.conf
#重启后模块失效，下面是开机自动加载模块的脚本
#在/etc/新建rc.sysinit 文件
vim /etc/rc.sysinit

#!/bin/bash
for file in /etc/sysconfig/modules/*.modules ; do
[ -x $file ] && $file
done

#在/etc/modules-load.d/br_netfilter.conf目录下新建文件如下
vim /etc/modules-load.d/br_netfilter.conf
modprobe br_netfilter
#增加权限
chmod 755 /etc/modules-load.d/br_netfilter.conf
#重启机器模块也会自动加载
lsmod |grep br_netfilter
br_netfilter 22209 0
bridge 136173 1 br_netfilter

#注：Docker 安装后出现：WARNING: bridge-nf-call-iptables is disabled 的解决办法：
#net.bridge.bridge-nf-call-ip6tables = 1
#net.bridge.bridge-nf-call-iptables = 1

#net.ipv4.ip_forward = 1：将Linux系统作为路由或者VPN服务就必须要开启IP转发功能。当linux主机有多个网卡时一个网卡收到的信息是否能够传递给其他的网卡 ，如果设置成1 的话 可以进行数据包转发，可以实现VxLAN 等功能。不开启会导致docker部署应用无法访问。
#重启docker
systemctl restart docker  
#配置docker镜像加速器: 登陆阿里云镜像仓库
#https://cr.console.aliyun.com/cn-hangzhou/instances/mirrors
#修改/etc/docker/daemon.json，变成如下
{
 "registry-mirrors":["https://y8y6vosv.mirror.aliyuncs.com","https://registry.docker-cn.com","https://docker.mirrors.ustc.edu.cn","https://dockerhub.azk8s.cn","http://hub-mirror.c.163.com"]
}
#让配置文件生效
sudo systemctl daemon-reload
sudo systemctl restart docker
~~~

## 拉取pbspro镜像

~~~sh
docker pull 
~~~

## 运行容器

| 容器名称 | 容器hostname | ip         |
| -------- | ------------ | ---------- |
| pbs1     | pbs1         | 172.19.0.3 |
| pbs2     | pbs2         | 172.19.0.4 |
| pbs3     | pbs3         | 172.19.0.5 |

~~~sh
docker network create --subnet=172.19.0.0/16 mynetwork
~~~

~~~sh
docker run -tid --name pbs1 -h pbs1 --add-host pbs1:172.19.0.3 --add-host pbs2:172.19.0.4 --add-host pbs3:172.19.0.5 --net=mynetwork --ip=172.19.0.3 pbspro/pbspro bash
docker run -tid --name pbs2 -h pbs2 --add-host pbs1:172.19.0.3 --add-host pbs2:172.19.0.4 --add-host pbs3:172.19.0.5 --net=mynetwork --ip=172.19.0.4 pbspro/pbspro bash
docker run -tid --name pbs3 -h pbs3 --add-host pbs1:172.19.0.3 --add-host pbs2:172.19.0.4 --add-host pbs3:172.19.0.5 --net=mynetwork --ip=172.19.0.5 pbspro/pbspro bash
~~~

## 配置容器间ssh互信

https://www.jianshu.com/p/fcbd57ae5d3b

~~~sh
#pbs1配置
docker exec -it pbs1 /bin/bash
#执行如下命令
yum install passwd openssl openssh-server openssh-clients net-tools vim which -y
/usr/sbin/sshd    
#报错文件不存在，执行以下命令
ssh-keygen -q -t rsa -b 2048 -f /etc/ssh/ssh_host_rsa_key -N ''
ssh-keygen -q -t ecdsa -f /etc/ssh/ssh_host_ecdsa_key -N ''
ssh-keygen -t dsa -f /etc/ssh/ssh_host_ed25519_key -N ''
#生成RSA随机图,修改 /etc/ssh/sshd_config 配置信息：
#UsePAM yes 改为 UsePAM no 
#UsePrivilegeSeparation sandbox 改为 UsePrivilegeSeparation no
#具体执行如下：
sed -i "s/#UsePrivilegeSeparation.*/UsePrivilegeSeparation no/g" /etc/ssh/sshd_config
sed -i "s/UsePAM.*/UsePAM no/g" /etc/ssh/sshd_config
#启动sshd
/usr/sbin/sshd
#查看ssh服务是否启动成功
ps -ef | grep ssh
#修改root密码
passwd 
... #root
...
#生成密码对
ssh-keygen -t rsa
#查看生成的私钥idrsa和公钥idrsa.pub
cd ~/.ssh/
#查看ssh服务是否启动成功
ps -ef | grep ssh
~~~

~~~sh
#pbs2配置
docker exec -it pbs2 /bin/bash
ssh-keygen -q -t rsa -b 2048 -f /etc/ssh/ssh_host_rsa_key -N ''
ssh-keygen -q -t ecdsa -f /etc/ssh/ssh_host_ecdsa_key -N ''
ssh-keygen -t dsa -f /etc/ssh/ssh_host_ed25519_key -N '' 
sed -i "s/#UsePrivilegeSeparation.*/UsePrivilegeSeparation no/g" /etc/ssh/sshd_config
sed -i "s/UsePAM.*/UsePAM no/g" /etc/ssh/sshd_config
/usr/sbin/sshd
ps -ef | grep ssh
passwd 
ssh-keygen -t rsa
cd ~/.ssh/
ps -ef | grep ssh
/usr/sbin/sshd
#将pbs2的公钥发送到pbs1上
scp id_rsa.pub root@pbs1:~/.ssh/id_rsa.pub.pbs2
~~~

~~~sh
#pbs3配置
docker exec -it pbs3 /bin/bash
yum install passwd openssl openssh-server openssh-clients net-tools vim which -y
ssh-keygen -q -t rsa -b 2048 -f /etc/ssh/ssh_host_rsa_key -N ''
ssh-keygen -q -t ecdsa -f /etc/ssh/ssh_host_ecdsa_key -N ''
ssh-keygen -t dsa -f /etc/ssh/ssh_host_ed25519_key -N '' 
sed -i "s/#UsePrivilegeSeparation.*/UsePrivilegeSeparation no/g" /etc/ssh/sshd_config
sed -i "s/UsePAM.*/UsePAM no/g" /etc/ssh/sshd_config
/usr/sbin/sshd
ps -ef | grep ssh
passwd #root
ssh-keygen -t rsa
cd ~/.ssh/
ps -ef | grep ssh
/usr/sbin/sshd
#将pbs2的公钥发送到pbs1上
scp id_rsa.pub root@pbs1:~/.ssh/id_rsa.pub.pbs3
~~~

~~~sh
#enter pbs1
docker exec -it pbs1 /bin/bash
cd ~/.ssh/
cat id_rsa.pub >> authorized_keys
cat id_rsa.pub.pbs2 >> authorized_keys 
cat id_rsa.pub.pbs3 >> authorized_keys
scp authorized_keys root@pbs2:~/.ssh/
scp authorized_keys root@pbs3:~/.ssh/
~~~

> note:
>
> - 容器启动的时候，需要重新开启ssh
>
>   ~~~sh
>   /usr/sbin/sshd
>   ps -ef | grep ssh
>   ~~~

## 配置管理节点

~~~sh
#登录管理节点pbs1，然后以root用户运行，修改/etc/pbs.conf
vi /etc/pbs.conf
#修改PBS_SERVER和PBS_START_MOM
PBS_SERVER=pbs1
PBS_START_MOM=1
#备注：如果是单机安装pbspro，要将PBS_START_MOM改为1

vi /var/spool/pbs/mom_priv/config
#修改clienthost为pbs1
$clienthost pbs1
~~~

> - PBS_START_MOM 参数用于控制是否启动 MOM (Message Oriented Middleware) 服务。MOM 是 PBS Pro 系统中的一个组件，它在每个计算节点上运行，负责管理和监控该节点上的作业。
>
> - 如果 PBS_START_MOM 设置为 1，那么在 PBS Pro 系统启动时，MOM 服务也会被启动(表明主节点也会承担计算任务)。如果设置为 0，那么 MOM 服务不会被启动。

## 配置计算节点

~~~sh
#分别登录计算节点pbs2和pbs3，然后以root用户运行，修改/etc/pbs.conf
vi /etc/pbs.conf
#修改PBS_SERVER和PBS_START_MOM
PBS_SERVER=pbs1
PBS_START_MOM=1
~~~

## 启动pbs

~~~sh
#3个节点上分别启动
/etc/init.d/pbs start
~~~

> ```sh
> /etc/init.d/pbs start    #启动pbs 
> /etc/init.d/pbs stop     #停止pbs 
> /etc/init.d/pbs restart  #重启pbs 
> /etc/init.d/pbs status   #查看pbs状态
> ```

## 节点扩容

~~~sh
. /etc/profile.d/pbs.sh
qmgr -c "create node pbs2"
qmgr -c "create node pbs3"
#查看添加的节点，返回state=free即为成功
pbsnodes -a
~~~

## 测试作业提交

~~~sh
#在管理节点创建user，提交作业，状态显示R为任务正在运行。同时也需要在其他计算节点也添加相同的用户，使其UID、GID一样
sudo groupadd -g 1002 pbsgroup
sudo useradd -u 1001 -g 1002 pbsuser1
#管理节点上
su pbsuser1
cd ~
qsub -- /bin/sleep 60 #qsub是提交一个作业到 PBS 集群，这个作业在被调度到集群的一个节点上运行后，会暂停10秒，然后结束。
qstat -a #查询集群中所有作业
tracejob 0.pbs1 #使用tracejob JobID查看作业的进度
~~~

> tracejob查询到结果：
>
> ```sh
> 01/18/2024 09:30:33  S    Obit received momhop:1 serverhop:1 state:4 substate:42
> ```
>
> - `Obit received` 表示作业已经结束，PBS 集群已经收到了作业结束的通知。
> - `momhop:1` 和 `serverhop:1` 是内部的计数器，用于跟踪作业在集群中的移动。通常情况下，这些值对于用户来说并不重要。
> - `state:4` 表示作业的当前状态。在 PBS 中，状态 4 通常表示作业已经完成。
> - `substate:42` 是作业的子状态，它提供了关于作业状态的更多细节。不同的 PBS 版本可能会有不同的子状态代码，你可能需要查阅你的 PBS 版本的文档来了解子状态 42 的具体含义。

# CentOS虚拟机部署torque

- 参考教程：https://www.cnblogs.com/liu-shaobo/p/13526084.html
- 3台centos机器上部署torque-6.1.3

## 环境准备

- CentOS 7 - root - root
- pbs1：172.16.183.60/24
- pbs2：172.16.183.61/24
- pbs3：172.16.183.62/24

- gateway：172.16.183.2

- DNS1: 172.16.183.2

## 部署虚拟机

- 在pbs1上配置静态IP：

  ~~~sh
  vi /etc/sysconfig/network-scripts/ifcfg-ens33
  
  TYPE=Ethernet
  PROXY_METHOD=none
  BROWSER_ONLY=no
  BOOTPROTO=static #static表示静态ip地址
  IPADDR=172.16.183.60 #ip地址，需要跟自己电脑所在网段一致
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

  - 重启，ping一下看看网络是否通了

- 克隆出pbs2和3，修改静态IP分别为172.16.183.61，172.16.183.62

- 关闭防火墙

  ~~~sh
  systemctl stop firewalld
  systemctl disable firewalld
  ~~~

- 安装epel源

  ~~~sh
  yum install -y http://mirrors.sohu.com/fedora-epel/epel-release-latest-7.noarch.rpm
  ~~~

- 安装软件包

  ~~~sh
  yum install -y device-mapper-persistent-data lvm2 wget net-tools nfs-utils lrzsz gcc gcc-c++ make cmake libxml2-devel openssl-devel curl curl-devel unzip sudo ntp libaio-devel wget vim ncurses-devel autoconf automake zlib-devel  python-devel epel-release openssh-server socat  ipvsadm conntrack telnet ipvsadm openssh-clients
  ~~~

## 配置ssh互信

~~~sh
#修改hostname
hostnamectl set-hostname pbs1 && bash
hostnamectl set-hostname pbs2 && bash
hostnamectl set-hostname pbs3 && bash
#修改hosts文件
vim /etc/hosts
172.16.183.60   pbs1  
172.16.183.61   pbs2  
172.16.183.62   pbs3
#生成、拷贝密钥
ssh-keygen
ssh-copy-id pbs2
ssh-copy-id pbs3
~~~

## 配置时间同步

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

## 修改资源限制

~~~sh
vim /etc/security/limits.conf 
* hard nofile 1000000
* soft nofile 1000000
* soft core unlimited
* soft stack 10240
* soft memlock unlimited
* hard memlock unlimited
~~~

## 配置nfs

~~~sh
#pbs1上
yum install -y nfs-utils rpcbind
mkdir /software
vim /etc/exports
/software *(rw,async,insecure,no_root_squash)

#使NFS配置生效
exportfs -arv
service nfs restart
systemctl enable nfs && systemctl status nfs
systemctl start rpcbind
systemctl enable rpcbind

#计算节点上
yum install -y nfs-utils
mkdir /software
mount pbs1:/software /software
#永久挂载
vim /etc/fstab
pbs1:/software       /software              nfs     defaults        0 0
~~~

## 部署Torque管理节点

Torque由四个服务组成：

- pbs_server ：资源管理系统的服务器，根据调度进程提供的可用节点资源清单进行作业分发和回收；
- pbs_mom  ：客户端，监视各计算节点的资源使用情况；
- trqauthd   ：用于授权pbs_mom进程与pbs_server进程之间建立互信连接；
- pbs_sched ：任务调度器；

### 安装依赖

~~~sh
yum install -y libtool openssl-devel libxml2-devel boost-devel gcc gcc-c++ hwloc hwloc-devel
~~~

### 安装torque

~~~sh
wget http://wpfilebase.s3.amazonaws.com/torque/torque-6.1.3.tar.gz
tar zxvf torque-6.1.3.tar.gz 
cd torque-6.1.3
./configure --prefix=/usr/local/torque --with-scp
#报错：
#checking whether boost is installed... configure: error: Torque needs Boost, but it was not found on your system
#This can be solved by one of the two following methods:
#1) Install the boost-devel package for your OS distribution. Note that it must be at least version 1.36.0.
#2) Run configure with --with-boost-path=<path>. This path should be the path to the directory containing the boost/ directory for your version of boost.
#解决：
#yum install -y boost-devel
make -j4
make install
~~~

- 生成计算节点需要的安装包，会生成5个可执行脚本

```sh
make packages
yum install -y libtool
libtool --finish /usr/local/torque/lib
```

### 配置torque服务端

- 添加环境变量

```sh
. /etc/profile.d/torque.sh
```

- 初始化serverdb

```sh
./torque.setup root
```

- 开启Torque服务端

```sh
qterm
systemctl enable pbs_server
systemctl start pbs_server
systemctl enable trqauthd
systemctl start trqauthd
```

## 部署torque计算节点

1、安装客户端
将torque文件夹的安装包复制到计算节点，或复制到NFS目录

```sh
#在计算节点上
./torque-package-mom-linux-x86_64.sh --install
./torque-package-clients-linux-x86_64.sh --install
```

2、配置客户端

```sh
vim /var/spool/torque/mom_priv/config
$pbsserver pbs1
$logevent 225
$loglevel 4
$usecp pbs1:/data /data
```

3、启动客户端

```sh
systemctl enable pbs_mom
systemctl start pbs_mom
systemctl enable trqauthd
systemctl start trqauthd
```

4、确保servern_name文件内容为管理节点名

```sh
cat /var/spool/torque/server_name
```

5、扩容计算节点

~~~sh
. /etc/profile.d/pbs.sh
qmgr -c "create node pbs2"
qmgr -c "create node pbs3"
#可以直接将主机名写入/var/spool/torque/server_priv/nodes
~~~

6、查看各节点状态

```sh
#查看添加的节点，返回state=free即为成功
pbsnodes -a
#或者
qnodes
#如果报错15137，可以执行：
cp contrib/init.d/{pbs_{server,sched,mom},trqauthd} /etc/init.d/
for i in pbs_server pbs_sched pbs_mom trqauthd; do chkconfig --add $i; chkconfig $ion; done
for i in pbs_server pbs_sched pbs_mom trqauthd; do service $i restart; done
#for i in pbs_mom trqauthd; do service $i start; done
```

> journalctl -xe或者message日志中如果出现如下报错：2
>
> ```sh
> PBS_Server;Svr;PBS_Server;LOG_ERROR::is_request, bad attempt to connect from  (address not trusted - check entry in server_priv/nodes
> ```
>
> - 原因是，这个节点启用了pbs_mom但在主节点的/var/spool/torque/server_priv/nodes中并没有将其归入。
>
>
> - 解决方法：如果不需要归入就什么都别改，如果需要这些节点进行运算，就在/var/spool/torque/server_priv/nodes中写入这些节点名

## **管理节点配置调度器**

1、启动调度器

```sh
cd ~/torque-6.1.3
cp contrib/systemd/pbs_sched.service /usr/lib/systemd/system/
systemctl enable pbs_sched
systemctl start pbs_sched
```

2、配置队列

```sh
qmgr -c 'create queue batch'
qmgr -c 'set server default_queue=batch'
qmgr -c 'set server query_other_jobs=true'
qmgr -c 'set queue batch queue_type=execution'
qmgr -c 'set queue batch started=true'
qmgr -c 'set queue batch enabled=true'
qmgr -c 'set queue batch resources_default.nodes=1'# qmgr -c 'set server scheduling=true'
```

## 配置节点cpu信息

~~~sh
#在管理节点上
vim /var/spool/torque/server_priv/nodes

pbs1 np=4
pbs2 np=4
pbs3 np=4

#重启服务
service pbs_mon restart
service pbs_server restart
service pbs_sched restart
~~~

## 测试作业提交

~~~sh
#在管理节点创建user，提交作业。同时也需要在其他计算节点也添加相同的用户，使其UID、GID一样。
#所有节点上
sudo groupadd -g 1002 pbsgroup
sudo useradd -u 1001 -g 1002 pbsuser1
#管理节点上
su pbsuser1
cd ~
qsub -- /bin/sleep 60 #qsub是提交一个作业到 PBS 集群，这个作业在被调度到集群的一个节点上运行后，会暂停10秒，然后结束。
echo "hello" | qsub
qstat -a #查询集群中所有作业
tracejob 0.pbs1 #使用tracejob JobID查看作业的进度
~~~



# pestat安装问题

问题：

安装了torque，里面带着pestat。

尝试安装pestat，修改了Makefile

![image-20240120175838964](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202401201758054.png)

但是无法安装，报错如图。

![2024-01-20_17-56](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202401201757319.png)





