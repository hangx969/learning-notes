# 实验环境搭建

## 虚拟机搭建

- VM OS 版本：CentOS7

- 2G内存、2vcpu

## docker安装-centos

### 简洁版

https://docs.docker.com/engine/install/centos/

```bash
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
sudo yum install docker-ce docker-ce-cli containerd.io docker-compose-plugin
#ubuntu上apt install docker.io docker-compose
sudo systemctl start docker
```

### 进阶版

> 安装docker前可以配置docker阿里云的源：[docker-ce镜像_docker-ce下载地址_docker-ce安装教程-阿里巴巴开源镜像站](https://developer.aliyun.com/mirror/docker-ce)

```bash
#配置主机名：
hostnamectl set-hostname dockerlab && bash
#关闭防火墙
systemctl stop firewalld && systemctl disable firewalld
#安装iptables防火墙
yum install iptables-services -y
#禁用iptables
service iptables stop && systemctl disable iptables
#清空防火墙规则
iptables -F 
#关闭selinux
setenforce 0
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
#注意：修改selinux配置文件之后，重启机器，selinux才能永久生效 reboot- f
getenforce #显示Disabled表示selinux关闭成功
#配置时间同步
yum install -y ntp ntpdate
ntpdate cn.pool.ntp.org 
#编写计划任务
crontab -e 
* */1 * * * /usr/sbin/ntpdate   cn.pool.ntp.org
#重启crond服务使配置生效：
systemctl restart crond
#安装基础软件包
yum install -y wget net-tools nfs-utils lrzsz gcc gcc-c++ make cmake libxml2-devel openssl-devel curl curl-devel unzip sudo ntp libaio-devel wget vim ncurses-devel autoconf automake zlib-devel  python-devel epel-release openssh-server socat  ipvsadm conntrack 
#安装docker-ce
#配置docker-ce国内yum源（阿里云）
yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
#安装docker依赖包
yum install -y yum-utils device-mapper-persistent-data lvm2
#安装docker-ce
#注：rocky linux8中需要先yum remove containerd* runc*否则会冲突
yum install docker-ce -y
#启动docker服务
systemctl start docker && systemctl enable docker && systemctl status docker
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
tee /etc/rc.sysinit <<'EOF'
#!/bin/bash
for file in /etc/sysconfig/modules/*.modules ; do
[ -x $file ] && $file
done
EOF

#在/etc/sysconfig/modules/目录下新建文件如下
tee /etc/sysconfig/modules/br_netfilter.modules <<'EOF'
modprobe br_netfilter
EOF
#增加权限
chmod 755 /etc/sysconfig/modules/br_netfilter.modules
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
tee /etc/docker/daemon.json <<'EOF'
{
 "registry-mirrors":["https://y8y6vosv.mirror.aliyuncs.com","https://registry.docker-cn.com","https://docker.mirrors.ustc.edu.cn","https://dockerhub.azk8s.cn","http://hub-mirror.c.163.com"]
}
EOF
#让配置文件生效
systemctl daemon-reload && systemctl restart docker
```

vscode在VM中运行docker插件

报错：

```bash
Got permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: Get "http://%2Fvar%2Frun%2Fdocker.sock/v1.24/images/json": dial unix /var/run/docker.sock: connect: permission denied
```

解决：

```bash
chmod 666 /var/run/docker.sock
```

## docker安装-ubuntu

~~~sh
# Switch to root account
su ubuntu
sudo su
# install prerequisites
apt install apt-transport-https ca-certificates curl software-properties-common
# add aliyun docker source
add-apt-repository "deb [arch=amd64] http://mirrors.aliyun.com/docker-ce/linux/ubuntu $(lsb_release -cs) stable"
# import GPG keys
curl -fsSL http://mirrors.aliyun.com/docker-ce/linux/ubuntu/gpg | sudo apt-key add -
# double check apt source for docker
apt update
apt-cache policy docker-ce
# install docker community
apt-get install -y docker-ce
# check docker installation
docker -v
# start and enable docker
systemctl enable docker.service && systemctl start docker.service && systemctl status docker.service
~~~

- If docker service failed to start with error: "systemd[1]: Job docker.service/start failed with result 'dependency'.", start docker with below command:

```sh
/usr/bin/dockerd -H unix://
sytemctl status docker
```

- User permission: by default, users in group named docker will have permission to use docker-cli, follow below steps to configure:

```sh
# Check if docker group exists
cat /etc/group | grep docker
#If not, create one
groupadd docker
# Add user to docker group
gpasswd -a $USER docker 
newgrp docker
```

## docker安装-windows

1. 首先安装scoop，参考[这里](../helm/helmv3-安装与使用.md)
2. scoop安装docker和gsudo：`scoop install docker gsudo`
3. 开一个终端运行dockerd：`gsudo dockerd`
4. 开一个终端运行docker命令：`gsudo docker images`

# docker基础

## 基础架构演变

1. 物理机：宕机风险高影响大，维护、扩展困难，资源利用率差，隔离性差。
2. 虚拟机：一个物理机上创建多个虚拟机。维护扩展方便。但是多虚拟机管理不方便。
3. 云计算：由平台管理多台虚拟机，降低维护难度。但是迁移性差、环境配置复杂。
4. 容器：启动快，环境可移植，一次构建到处运行。多容器管理成为问题。
5. 容器编排/容器云：负载均衡、高可用。下一代云计算技术。
6. Serverless：函数即服务。公有云使用较多。

## docker介绍

**概念：**

容器是一种轻量级虚拟化，用于将应用程序和依赖的组件打包在一起，以便在不同的环境中进行移植和运行。

**优点：**

- 基于work on my machine的问题，Docker应运而生，由dotCloud小公司开发，2013年开源，发展壮大。基于Go语言。
- 只需要Linux核心环境，4M左右 + 其他环境。传统VM虚拟出整套硬件，运行完整操作系统，在这个系统上运行程序；而容器内的应用直接运行在宿主机的内核，没有自己的内核，不需要自己的OS和硬件，更轻便。
- 一个物理机上运行多个实例，将服务器性能压榨到极致

![image-20240725230020449](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202407252300573.png)

**工作原理：**

- docker 是一个client - server 结构的系统，docker的守护进程运行在主机上，通过socket从客户端访问server。server接到client的命令，再执行

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202407252107550.png" alt="image-20240725210736431" style="zoom:50%;" />

**docker的优点：**

- 真正的一次构建、到处运行
- 更强的一致性
- 可移植性极强
- 提升资源利用率
- 创建和启动速度快
- 更细粒度的隔离性

**docker失宠，为什么还要用：**

- docker依旧是产品交付的最佳实践
- docker依旧是本地开发和测试的首选。兼容性非常强。
- docker镜像和容器管理依旧最为灵活，构建镜像的功能非常完善，支持异构。
- 没有使用k8s的企业还是会使用docker来做容器管理。

## docker镜像原理

docker镜像：轻量级、可运行的独立软件包，包含了软件运行所需的所有内容：代码、runtime、library、环境变量、配置文件等。runtime 是一个通用抽象的术语，指的是计算机程序运行的时候所需要的一切代码库，框架，平台等。

**联合文件系统-Union File System**

- 分层、高性能、轻量级的文件系统。对文件系统的修改作为一次提交，一层一层的叠加。

![image-20240725215052857](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202407252150096.png)

- 对于一个精简OS，rootfs可以很小，只需包含基本命令，工具和库。底层用的是宿主机的kernel，自己只需要提供**rootfs**即可。docker镜像的最底层是boofts。bootfs几乎是不变的，各种镜像bootfs是通用的。
- docker镜像相当于一个只读的模板，每一次操作都在其上创建一层可写层。可写层：容器层；只读层：镜像层

### 工作原理

1. **核心概念：**

   - Docker 镜像本质上是一个**只读的、分层的文件系统**。
   - 每个镜像由**多个只读层（Layer）** 堆叠而成。
   - 这些层代表了 Dockerfile 中每条指令（`FROM`, `RUN`, `COPY`, `ADD`, `ENV` 等）所引入的文件系统变化。

2. **底层技术：联合文件系统（Union File System - UnionFS）：**

   - **关键技术：** 分层实现的核心是联合文件系统（如 AUFS, OverlayFS, Device Mapper, Btrfs, ZFS 等，现代 Docker 默认常用 Overlay2）。

   - **工作原理：** UnionFS 允许将多个不同的目录（即镜像层）透明地叠加（Union Mount）在一起，形成一个单一的、连贯的文件系统视图。

   - 特性：

     - 写时复制（Copy-on-Write - CoW）：

       这是分层和高效的关键。当一个文件需要被修改（例如，容器运行时写入）：

       - 如果该文件存在于下层（只读层），UnionFS 会先将该文件的副本复制到最上层的**可写层（容器层）**。
       - 然后修改操作只作用于这个上层的副本。
       - **下层文件始终保持不变且只读。**

     - **分层叠加：** 文件系统的最终视图是所有层按顺序叠加的结果。如果一个文件在多个层中出现，**最上层**的文件会**遮盖（Occlude）** 下层同路径的文件，用户看到的是最上层的版本。

3. **镜像构建过程与分层：**

   - 当你构建一个镜像时：
     1. Docker 读取 `Dockerfile`。
     2. 对于 `Dockerfile` 中的**每条指令**（除了少数如 `LABEL`, `MAINTAINER`, `EXPOSE` 等元数据指令），Docker 引擎会**创建一个新的只读层**。
     3. 该层包含了执行该指令后相对于前一层文件系统的**增量变化**（新增、修改、删除的文件）。
     4. 构建过程中的中间层会被缓存，加速后续构建（如果指令和上下文未变）。
     5. 最终构建出的镜像就是这一系列只读层的堆栈。

4. **容器运行时：**

   - 当基于一个镜像启动一个容器时：
     1. Docker 引擎会将该镜像的所有只读层作为容器的**基础文件系统**。
     2. 同时，在只读层之上**添加一个薄薄的可写层（Container Layer/Writable Layer）**。
     3. **容器内的所有文件修改（创建、更新、删除）都只发生在这个可写层中**，通过 CoW 机制实现。
     4. 当容器被删除时，这个可写层通常也会被丢弃（除非使用持久化卷）。

## docker常用命令

- 查看docker版本

~~~sh
docker version
Client: Docker Engine - Community
 Version:           26.1.3
 API version:       1.43 (downgraded from 1.45)
 Go version:        go1.21.10
 Git commit:        b72abbb
 Built:             Thu May 16 08:34:39 2024
 OS/Arch:           linux/amd64
 Context:           default

Server: Docker Engine - Community
 Engine:
  Version:          24.0.6
  API version:      1.43 (minimum version 1.12)
  Go version:       go1.20.7
  Git commit:       1a79695
  Built:            Mon Sep  4 12:32:10 2023
  OS/Arch:          linux/amd64
  Experimental:     false
 containerd:
  Version:          1.6.22
  GitCommit:        8165feabfdfe38c65b599c4993d227328c231fca
 runc:
  Version:          1.1.8
  GitCommit:        v1.1.8-0-g82f18fe
 docker-init:
  Version:          0.19.0
  GitCommit:        de40ad0
# OCI：Open Container Initiative的简称，由Linux基金会主导开发OCI规范和标准，目的是围绕容器格式和Runtime（运行时）制定的一个开放的工业化标准。
# Containerd： Docker为了兼容OCI标准， 将容器Runtime及其管理功能从Docker守护进程中剥离出来，用于不启动Docker也能直接通过Containerd来管理容器。
# RunC：Docker按照OCF（Open  Container  Format）开放容器格式标准制定的一个轻量级工具，可以使用RunC不通过Docker引擎即可实现容器的启动、停止和资源隔离等功能
~~~

- 查看docker详细信息

~~~sh
docker info
Client: Docker Engine - Community
 Version:    26.1.3
 Context:    default
 Debug Mode: false
 Plugins:
  buildx: Docker Buildx (Docker Inc.)
    Version:  v0.14.0
    Path:     /usr/libexec/docker/cli-plugins/docker-buildx
  compose: Docker Compose (Docker Inc.)
    Version:  v2.27.0
    Path:     /usr/libexec/docker/cli-plugins/docker-compose
# buildx支持异构镜像制作，比如在x86的机器上制作ARM的镜像
# docker client自带docker-compose插件但是我们一般不用，一般是下载一个docker-compose二进制文件去运行
Server:
 Containers: 0
  Running: 0
  Paused: 0
  Stopped: 0
 Images: 8
 Server Version: 24.0.6
 Storage Driver: overlay2 # 存储驱动，一定要是overlay2。不能是device-mapper，不建议生产环境使用。
  Backing Filesystem: xfs
  Supports d_type: true
  Using metacopy: false
  Native Overlay Diff: true
  userxattr: false
 Logging Driver: json-file # docker日志驱动。json-file是本地存储日志。
 Cgroup Driver: cgroupfs # cgroup驱动程序。新版用的是systemd
 Cgroup Version: 1
 Plugins:
  Volume: local
  Network: bridge host ipvlan macvlan null overlay
  Log: awslogs fluentd gcplogs gelf journald json-file local logentries splunk syslog
 Swarm: inactive
 Runtimes: io.containerd.runc.v2 runc
 Default Runtime: runc
 Init Binary: docker-init
 containerd version: 8165feabfdfe38c65b599c4993d227328c231fca
 runc version: v1.1.8-0-g82f18fe
 init version: de40ad0
 Security Options:
  seccomp
   Profile: builtin
 Kernel Version: 4.18.0-553.58.1.el8_10.x86_64
 Operating System: Rocky Linux 8.10 (Green Obsidian)
 OSType: linux
 Architecture: x86_64
 CPUs: 8
 Total Memory: 5.767GiB
 Name: rm1
 ID: 54d52a93-dd74-4e92-a9a8-c69f744ef67c
 Docker Root Dir: /var/lib/docker # docker数据目录
 Debug Mode: false
 Experimental: false
 Insecure Registries:
  172.16.183.100
  harbor.hanxux.local
  127.0.0.0/8
 Registry Mirrors:
  https://a88uijg4.mirror.aliyuncs.com/
  https://docker.lmirror.top/
  https://docker.m.daocloud.io/
  https://hub.uuuadc.top/
  https://docker.anyhub.us.kg/
  https://dockerhub.jobcher.com/
  https://dockerhub.icu/
  https://docker.ckyl.me/
  https://docker.awsl9527.cn/
  https://docker.laoex.link/
 Live Restore Enabled: false # true是重启docker进程的时候容器也跟着重启
~~~

- 容器相关命令

```bash
docker run --name=hello -it --rm centos /bin/bash
#docker run运行并创建容器，--name 容器的名字，-i 交互式，-t 分配伪终端，--rm 退出就删掉容器，centos: 启动docker需要的镜像，/bin/bash说明你的shell类型为bash
exit
#退出容器，退出之后容器也会停止，不会再前台运行

#以守护进程方式启动容器，-d在后台运行容器
docker run --name=hello1 -td centos 
docker ps | grep hello1
#进入容器
docker exec -it hello1 /bin/bash
#查看正在运行的容器
docker ps
#查看所有容器，包括运行和退出的容器
docker ps -a 
#停止容器
docker stop hello1
#启动已经停止的容器
docker start hello1
#进入容器
docker exec -it hello1 /bin/bash 
docker attach 容器ID   #后面不需要加 /bin/bash
##docker exec进去之后打开新的终端，所以需要加/bin/bash，exit退出不会导致容器的停止
##docker attach进入容器正在执行的终端，不会启动新的进程。exit退出会导致容器的停止。
##注意：exit退出之后，该容器停止了，但是该容器相关的资源仍然保留着，用docker ps -qa 可以看到所有容器的情况。如果不需要这些容器了，要用rm -f彻底删除掉
#删除容器
docker rm -f hello1
#删除全部镜像
docker rmi -f $(docker images -aq)
#查看镜像运行的CPU、内存等各项指标
docker stats
#查看容器进程ID
docker top <container id>
#查看容器日志
docker -tf --tail 10 <container id>
#查看容器元数据
docker inspect <container id>
#拷贝文件进容器
docker cp 容器ID:目录 源文件路径
docker cp c6b838db2e40:/home/test.py /home
#保存容器当前状态，commit，相当于保存到本地，就像快照一样。
docker commit -a="xxxx" -m="add xxx to xxx dir"  原容器ID image-name:1.0
```

## 镜像格式组成部分

`gcr.k8s.io/coreos/prometheus-adapter:0.8`为例：

- gcr.k8s.io：registry/镜像地址
- coreos：repository/Project/命名空间/镜像目录。
  - 这个目录可以有多级
- prometheus-adapter：name/镜像名称
  - 只有镜像名称没有registry和repo的时候，就默认是去`docker.io/library`去拉
- 0.8：tag/版本号

> 有些镜像如果docker.io没有，用bitnami的也行。bitnami也是比较可靠的镜像库

## docker部署服务通用步骤

1. 确认需要部署的服务
2. 了解服务运行的基础配置（配置文件、数据目录在哪里、端口号等）
3. 找到基础镜像、下载镜像
4. 确认配置启动服务并验证

# Docker数据持久化

将主机目录直接挂载到容器内目录上，容器内可以对其进行修改。源文件是在宿主机上的。

## Docker数据卷

```bash
#为容器添加数据卷
docker run -v /datavolume:/data -it centos /bin/bash
docker run --name volume -v ~/datavolume:/data -itd centos /bin/bash
#为容器添加带权限的数据卷（容器中的data目录就是只读的，宿主机目录正常读写）
docker run --name volume -v ~/datavolume1:/data:ro -itd centos /bin/bash
#dockerfile构建带数据卷的镜像
cat  dockerfile
FROM centos
VOLUME ["/datavolume3","/datavolume6"] #挂了两个volume进到容器内的挂载点 datavolume3和datavolume6
CMD /bin/bash
```

- 匿名挂载

~~~sh
# -v 容器内路径
docker run -d -P -v /etc/nginx nginx
# 查看存在的数据卷,由于只指定了容器内目录，宿主机目录会是乱码
docker volume ls
~~~

- 具名挂载

~~~sh
#可以自己给该目录起个名字，方便查找，-v 卷名:容器内路径 
docker run -d -P -v my-volume:/etc/nginx nginx
#查看相应的数据卷路径
docker volume ls
#所有docker容器内的卷，在不指定主机内目录的情况下，都是默认放在/var/lib/docker/volume/xxxx/_data
#列出悬空存储卷
docker volume ls -f dangling=true
#删除存储卷
docker volume rm volume_name1 volume_name2
~~~

- 指定路径和权限挂载

~~~sh
-v 宿主机路径:容器内路径  #指定路径挂载 
-v 卷名:容器内路径:ro （或者rw） #指定了容器对该目录的权限，如果是ro，目录内部文件只能在宿主机内改变，不能在容器内改变
~~~

## docker数据卷容器

容器A挂载了一个volume，容器B通过volume-from参数，把A挂载的数据卷也挂载到自己里面，实现数据共享。本质是软连接到宿主机上的同一个目录上。

```bash
#构建一个镜像
FROM centos
VOLUME ["/datavolume3","/datavolume6"]
CMD /bin/bash

docker build -t=volume . --load

#run一个容器A挂载volume
docker run --name volume-A -it volume
#再run一个容器B，用volume-from挂载A的数据卷
docker run --name volume-B --volumes-from volume-A -itd centos /bin/bash
docker exec -it volume-B /bin/bash #可以看到容器A挂载的目录和文件
```

## docker数据卷的备份和还原

```bash
#数据备份
docker run --volumes-from volume-B  -v  /root/backup:/backup --name volume-copy centos tar zcvf /backup/volume-B.tar.gz /datavolume3 #新建容器，挂载主容器volume-B的volume，把容器内的/backup挂载到宿主机的/root/backup，然后把主容器的/datavolume3打包到了/backup目录下，实现备份。
#这个辅助备份的容器做完复制就退出了，可以到宿主机上验证数据备份
cd /root/backup/
ls
#数据还原
docker run --volumes-from volume-B -v /root/backup/:/backup centos tar zxvf /backup/volume-B.tar.gz -C /
#运行一个辅助容器，挂载上主容器volume-B的volume，然后把宿主机的/root/backup挂载到容器内的/backup，这样备份的数据就近到容器里面了。然后把备份的datavolume3解压到自己的也就是主容器的/上，实现还原。
```

# docker容器网络

## docker0网桥

- 安装docker的时候，会生成一个docker0的虚拟网桥。

- Linux虚拟网桥的特点：可以设置ip地址，相当于拥有一个隐藏的虚拟网卡

  ```bash
  ip addr
  3: docker0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default 
      link/ether 02:42:16:a9:10:79 brd ff:ff:ff:ff:ff:ff
      inet 172.17.0.1/16 brd 172.17.255.255 scope global docker0
         valid_lft forever preferred_lft forever
      inet6 fe80::42:16ff:fea9:1079/64 scope link 
         valid_lft forever preferred_lft forever
  ```

- 每运行一个docker容器都会生成一个veth设备对，这个veth一个接口在容器里，一个接口在物理机上。访问宿主机IP：高位端口时，veth对就通过管道将请求交给要访问的容器。


```bash
7: vethb49257d@if6: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master docker0 state UP group default 
    link/ether c2:2b:1a:96:d2:2a brd ff:ff:ff:ff:ff:ff link-netnsid 0
    inet6 fe80::c02b:1aff:fe96:d22a/64 scope link 
       valid_lft forever preferred_lft forever
```

- 网桥管理工具

  ```bash
  yum install bridge-utils -y
  brctl show # 查看docker0的网桥设备，下面每个接口都表示一个启动的docker容器
  
  bridge name     bridge id               STP enabled     interfaces
  docker0         8000.024216a91079       no              vethb49257d
  ```

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202407252228993.png" alt="image-20240725222820817" style="zoom:67%;" />

## docker link网络别名

- docker link设置网络别名

  ```bash
  #dockerfile构建镜像
  FROM centos
  RUN rm -rf /etc/yum.repos.d/*
  COPY Centos-vault-8.5.2111.repo /etc/yum.repos.d/
  RUN yum install wget -y
  RUN yum install nginx -y
  EXPOSE 80
  CMD /bin/bash
  
  docker build -t="inter-image" . --load
  
  #启动一个test3容器
  docker run --name test3 -itd inter-image /bin/bash
  
  #启动一个test5容器，--link做链接，含义是在test5看来，test3容器别名为webtest。
  #test3容器就算ip变了，仍可以在test5上ping别名webtest，连接到test3
  docker run --name test5 -itd --link=test3:webtest inter-image /bin/bash
  #进入test5容器，ping webtest
  docker exec -it test5 /bin/bash
  ping webtest
  ```

## docker容器网络模式

docker run创建Docker容器时，可以用--net选项指定容器的网络模式，Docker有以下4种网络模式：

- bridge模式：--net =bridge指定，默认设置；容器启动后会通过DHCP获取一个地址。

- host模式：--net =host指定；共享宿主机网络。

- none模式：--net =none指定；创建的容器没有网络地址，只有lo网卡。

- container模式：使用--net =container:NAME or ID 指定。

  - 和已经存在的某个容器共享一个 Network Namespace。如下图所示，右方黄色新创建的container，其网卡共享左边容器。因此就不会拥有自己独立的 IP，而是共享左边容器的 IP 172.17.0.2,端口范围等网络资源，两个容器的进程通过 lo 网卡设备通信。

    ![image-20231016133450111](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310161334288.png)

```bash
###bridge模式###
docker run --name bridge -itd --privileged=true centos /bin/bash
docker exec -it net-bridge /bin/bash
ip addr
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
24: eth0@if25: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default 
    link/ether 02:42:ac:11:00:02 brd ff:ff:ff:ff:ff:ff link-netnsid 0
    inet 172.17.0.2/16 brd 172.17.255.255 scope global eth0
       valid_lft forever preferred_lft forever
###host模式###
docker run --name net-host -itd --net=host --privileged=true centos /bin/bash
docker exec -it net-host /bin/bash
ip addr #看到的是物理机的网络设备

###none模式###
docker run -itd --name net-none --net=none --privileged=true centos
docker exec -it net-none /bin/bash
ip addr
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
       
###container模式###
docker run --name net-container --net=container:net-none  -it --privileged=true centos
docker exec -it net-container /bin/bash
ip addr  #跟net-none的设置一样
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
```

# docker资源配额

Docker通过cgroup来控制容器使用的资源限制，可以对docker限制的资源包括CPU、内存、磁盘

## docker容器控制CPU

### CPU份额限制

```bash
#查看配置份额的帮助命令：
docker run --help | grep cpu-shares
# cpu配额参数：-c, --cpu-shares int 
```

- CPU shares (relative weight) 在创建容器时指定容器所使用的CPU份额值。

  - cpu-shares的值不能保证可以获得1个vcpu或者多少GHz的CPU资源，仅仅只是一个弹性的加权值。只是设置一个优先级。

  - 默认每个docker容器的cpu份额值都是1024。在同一个CPU核心上，同时运行多个容器时，容器的cpu加权的效果才能体现出来。

- 例： 两个容器A、B的cpu份额分别为1000和500，结果会怎么样？   

  - 情况1：A和B正常运行，占用同一个CPU，在cpu进行时间片分配的时候，容器A比容器B多一倍的机会获得CPU的时间片。

  - 情况2：分配的结果取决于当时其他容器的运行状态。比如容器A的进程一直是空闲的，那么容器B是可以获取比容器A更多的CPU时间片的； 比如主机上只运行了一个容器，即使它的cpu份额只有50，它也可以独占整个主机的cpu资源。

- cgroups只在多个容器同时争抢同一个cpu资源时（CPU紧张时），cpu配额才会生效。因此，无法单纯根据某个容器的cpu份额来确定有多少cpu资源分配给它，资源分配结果取决于同时运行的其他容器的cpu分配和容器中进程运行情况。

### CPU core核心限制

> 从系统架构来看，目前的商用服务器大体可以分为三类架构：
>
> 1. 即对称多处理器结构(SMP：Symmetric Multi-Processor) 例： x86 服务器，双路服务器。主板上有两个物理cpu
>
> 2. 非一致存储访问结构 (NUMA：Non-Uniform Memory Access) 例： IBM 小型机 pSeries 690
>
> 3. 海量并行处理结构 (MPP：Massive ParallelProcessing) 例： 大型机 Z14

- 对多核CPU的服务器，docker还可以控制容器运行限定使用哪些cpu内核和内存节点，即使用--cpuset-cpus和--cpuset-mems参数。
  - --cpuset可以绑定CPU core，指定容器只能在哪个CPU上运行。
  - --cpuset-mems 对具有NUMA拓扑（具有多CPU、多内存节点）的服务器尤其有用，可以对需要高性能计算的容器进行性能最优的配置。如果服务器只有一个内存节点，则--cpuset-mems的配置基本上不会有明显效果。

### Lab

> stress 压测工具参数
> -?        显示帮助信息
> -v        显示版本号
> -q       不显示运行信息
> -n       显示已完成的指令情况
> -t        --timeout  N  指定运行N秒后停止        
>           --backoff   N   等待N微秒后开始运行
> -c       产生n个进程 ：每个进程都反复不停的计算随机数的平方根，测试cpu
> -i       产生n个进程 ：每个进程反复调用sync()，sync()用于将内存上的内容写到硬盘上，测试磁盘io
> -m     --vm n 产生n个进程,每个进程不断调用内存分配malloc（）和内存释放free（）函数 ，测试内存
>           --vm-bytes B  指定malloc时内存的字节数 （默认256MB）
>           --vm-hang N   指定在free栈的秒数   
> -d    --hadd n  产生n个执行write和unlink函数的进程
>          -hadd-bytes B  指定写的字节数
>          --hadd-noclean  不unlink        
> 注：时间单位可以为秒s，分m，小时h，天d，年y，文件大小单位可以为K，M，G

```bash
#写dockerfile
FROM centos
RUN rm -rf /etc/yum.repos.d/*
COPY Centos-vault-8.5.2111.repo /etc/yum.repos.d/
RUN yum install epel-release -y
RUN yum install stress -y
CMD /bin/bash
#构建镜像
docker build -t=centos-stress . --load
#起容器
docker run -itd --name docker10 --cpuset-cpus 0 --cpu-shares 512 centos-stress /bin/bash #指定docker10只能在cpu0上运行，而且docker10的使用cpu的份额512
docker run -itd --name docker20 --cpuset-cpus 0 --cpu-shares 1024 centos-stress /bin/bash #指定docker20只能在cpu0上运行，而且docker20的使用cpu的份额1024，比dcker10多一倍

#测试1： 进入docker10，使用stress测试进程是不是只在cpu0上运行：
docker exec -it docker10 /bin/bash
stress -c 2 -v -t 10m  #运行2个进程，把两个cpu占满

#测试2： 进入docker20，使用stress测试进程是不是只在cpu0上运行：
docker exec -it docker10 /bin/bash
stress -c 2 -v -t 10m  #运行2个进程，把两个cpu占满

#物理机上运行top命令，按1快捷键，查看每个cpu使用情况：
top - 13:17:29 up 12:18,  0 users,  load average: 1.53, 0.44, 0.19
Tasks: 145 total,   5 running, 140 sleeping,   0 stopped,   0 zombie
%Cpu0  :100.0 us,  0.0 sy,  0.0 ni,  0.0 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
%Cpu1  :  2.2 us,  1.9 sy,  0.0 ni, 90.4 id,  0.0 wa,  0.0 hi,  5.4 si,  0.0 st
KiB Mem :  8173724 total,  6187612 free,   896372 used,  1089740 buff/cache
KiB Swap:        0 total,        0 free,        0 used.  6938528 avail Mem 
  PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND                    
11102 root      20   0    7960     92      0 R  33.6  0.0   0:08.04 stress                                   
11103 root      20   0    7960     92      0 R  33.2  0.0   0:08.04 stress                           
10991 root      20   0    7960     96      0 R  16.6  0.0   0:09.24 stress                               
10992 root      20   0    7960     96      0 R  16.3  0.0   0:09.23 stress    
```

## docker容器控制内存

- Docker提供参数-m, --memory=""限制容器的内存使用量。

```bash
#例：允许容器使用的内存上限为128M：
docker run -it -m 128m centos
#查看内存限制
cat /sys/fs/cgroup/memory/memory.limit_in_bytes
134217728
```

## docker容器控制IO

```bash
docker run --help | grep write-b
--device-write-bps value   Limit write rate (bytes per second) to a device (default []) #限制此设备上的写速度（bytes per second），单位可以是kb、mb或者gb。
--device-read-bps value  #限制此设备上的读速度（bytes per second），单位可以是kb、mb或者gb。 
```

情景：防止某个 Docker 容器吃光你的磁盘 I / O 资源

Lab:

```bash
#例1：限制容器实例对硬盘的最高写入速度设定为 2MB/s。
#--device参数：将主机设备添加到容器
mkdir -p /var/www/html/
docker run -itd -v /var/www/html/:/var/www/html --device /dev/sda:/dev/sda --device-write-bps /dev/sda:2mb centos  /bin/bash
```

> #用time dd测试磁盘io: time有计时作用，dd用于复制，从if读出，写到of
> 注：dd 参数：
> direct：读写数据采用直接IO方式，不走缓存。直接从内存写硬盘上。
> nonblock：读写数据采用非阻塞IO方式，优先写dd命令的数据

```bash
time dd if=/dev/sda of=/var/www/html/test.out bs=2M count=50 oflag=direct,nonblock

10+0 records out
20971520 bytes (21 MB, 20 MiB) copied, 10.0456 s, 2.1 MB/s
real    0m10.080s
user    0m0.000s
sys     0m0.018s
#注： 发现1秒写2M。限制成功。
```

## docker资源自动释放

```bash
docker run --help | grep rm
   --rm ： Automatically remove the container when it exits
   #作用：当容器命令运行结束后，自动删除容器，自动释放资源 
```

```bash
#示例
docker run -it --rm --name dockerrm centos sleep 10
#容器起来10s就自动退出了
```

# docker资源清理

- 随着时间的推移，docker containers 以及其他 Docker 资源（例如映像、卷和网络）可能会累积并消耗磁盘空间。因此，为了防止未使用或不必要的资源积累，Docker 清理有助于删除这些不需要的垃圾。此过程可以释放磁盘空间并提高系统性能。
- 我们有必要定期检查 Docker 占用的磁盘空间，以保证高效的资源管理，以及防止磁盘空间耗尽。这有助于维护系统性能并避免潜在问题，例如部署失败或容器操作速度减慢。

## 查看磁盘占用

~~~sh
#此命令提供 Docker 组件（例如镜像、容器、存储卷和构建缓存）占用的总磁盘空间。
docker system df
#有关磁盘使用情况的更详细信息，包括各个组件的大小、文件系统类型和挂载点。
docker system df -v
~~~

## 清理命令

- Docker prune 命令是 Docker 环境中的清理工具。当系统磁盘空间不足时，或者当我们想确保只有必要的 Docker 组件占用系统资源时，可以使用 Docker prune。 
- docker system prune 命令删除未使用的数据，包括：
  - 所有已停止的容器
  - 所有未使用的网络
  - 所有悬空镜像
  - 所有悬空构建缓存

~~~sh
docker system prune
~~~

## 清理悬空存储卷

~~~sh
#列出
docker volume ls -f dangling=true
#删除
docker volume rm volume_name1 volume_name2
#一次性清理未使用的存储卷的简单方法。当我们运行此命令时，Docker 会识别当前未被任何容器使用的存储卷并删除它们。
docker volume prune
~~~

## 清理网络

~~~sh
#列出
docker network ls
#删除
docker network rm name
~~~

## 清理none镜像


# dockerfile基础

## dockerfile定义

Dockerfile是一个用于定义Docker镜像的文本文件。它包含了一系列的指令和参数，用于指示Docker在构建镜像时应该执行哪些操作，例如基于哪个基础镜像、复制哪些文件到镜像中、运行哪些命令等等。通过Dockerfile，开发人员可以将应用程序和其所有依赖项打包在一起，创建出一个可移植的Docker镜像，使得这个应用程序可以在任何Docker环境中都能够快速部署和运行。

示例

```sh
FROM centos
MAINTAINER xianchao
RUN rm -rf /etc/yum.repos.d/*
COPY Centos-vault-8.5.2111.repo /etc/yum.repos.d/
RUN yum install wget -y
RUN yum install nginx -y
COPY index.html /usr/share/nginx/html/
EXPOSE 80
ENTRYPOINT ["/usr/sbin/nginx","-g","daemon off;"]
```

## dockerfile制作服务的过程

如果是二进制部署服务：

1. 先去安装操作系统
2. 更改系统的源为国内的源
3. 安装基础环境（jdk、python等）
4. 启动服务（java -jar等）

dockfile制作服务镜像：

1. 先去找到一个基础镜像（包含了服务需要的基础环境）
2. 配置系统的源为国内源
3. 创建用户并分配权限
4. 启动命令（CMD\ENTRYPOINT）

## dockerfile语法

- FROM

  - 指定基础镜像，必须是可以下载的镜像。

  - 多行FROM命令只会执行最后一行。

- RUN

  - shell模式

    ```bash
    RUN yum install -y wget
    ```

  - exec模式

    ```bash
    RUN ["/bin/bash", "-c", "yum install -y wget"]
    # -c是指定后面要运行的命令
    ```

  两种是等价的。

- EXPOSE

  仅仅只是声明端口（不声明的话，端口服务也是暴露的，只是声明出来更直观）。作用：

  1、帮助镜像使用者理解这个镜像服务的守护端口，以方便配置映射。

  2、在运行时使用随机端口映射时，也就是 docker run -P 时，会自动随机映射 EXPOSE 声明的端口。

  3、可以是一个或者多个端口，也可以指定多个EXPOSE。格式：EXPOSE 80 8080。

- CMD和ENTRYPOINT

  - CMD

    - 类似于 RUN 指令，用于设置默认的可执行命令或参数，但二者运行的时间点不同:

      1、CMD 在docker run 时运行。是容器起来之后自启动的命令。

      2、RUN 是在 docker build构建镜像时运行。

    - CMD的命令会被docker run的命令行参数给覆盖掉

    - CMD如果有多个，只有最后一行会生效。


  - ENTRYPOINT

    - 类似于 CMD 指令，但其不会被 docker run 的命令行参数指定的指令所覆盖，而且这些命令行参数会被当作参数送给 ENTRYPOINT 指令指定的程序。

    - 但是, 如果运行 docker run 时使用了 --entrypoint 选项，将覆盖docker file的entrypoint

    - 优点：在执行 docker run 的时候可以指定 ENTRYPOINT 运行所需的参数。

    - 注意：存在多个 ENTRYPOINT 指令，仅最后一个生效。

    格式：

    `ENTERYPOINT [“executable”,“param1”,“param2”]` (exec模式)

    `ENTERYPOINT command` （shell模式）

    - CMD和ENTRYPOINT配合使用举例

      - 如果dockerfile中也有CMD指令，CMD中的参数会被附加到ENTRYPOINT 指令的后面。 如果这时docker run命令带了参数，这个参数会覆盖掉CMD指令的参数，并也会附加到ENTRYPOINT 指令的后面。这样当容器启动后，会执行ENTRYPOINT 指令的参数部分。

      ```bash
      #dockerfile
      FROM nginx
      ENTRYPOINT ["nginx", "-c"] # 定参 # nginx是命令行工具，-c是指定基于哪个config文件运行
      CMD ["/etc/nginx/nginx.conf"] # 变参 #这个参数可以被docker run 命令行所覆盖
      
      #建镜像
      docker build -t nginx:test . --load
      
      #运行镜像，不传任何参数
      docker run nginx:test
      docker inspect containerid #看args字段
      #默认就跑了 ENTRYPOINT和cmd组合起来的命令：nginx -c /etc/nginx/nginx.conf
      
      #运行镜像，传递新的参数
      docker run --name nginx nginx:test /etc/nginx/new.conf
      docker inspect #看到传了新的参数进去
      ```

    > 在pod中定义command和args时的规律如下：
    >
    > 1.如果command和args均没有写，那么用Dockerfile的配置。
    >
    > 2.如果command写了，但args没有写，那么Dockerfile中的entrypoint和cmd会被忽略，执行yaml中的command
    >
    > 3.如果command没写，但args写了，那么Dockerfile中配置的ENTRYPOINT的命令行会被执行，并且将args中填写的参数追加到ENTRYPOINT中。
    >
    > 4.如果command和args都写了，那么Dockerfile的配置被忽略，执行command并追加上args参数。
    >
    > 基于以上：建议不在dockerfile中定义任何cmd和entrypoint，在pod yaml文件中去定义command和args


- COPY

  - 复制指令，从当前dockerfile上下文目录中复制文件或者目录到容器里指定路径。

  - 格式：

    ```bash
    COPY <src> <dest>
    COPY [“<src>”, “<dest>”]
    
    # [--chown=<user>:<group>]：可选参数，改变复制到容器内文件的拥有者和属组。
    COPY [--chown=<user>:<group>] <源路径1> <目标路径>
    COPY [--chown=<user>:<group>] <源路径1> <目标路径>
    ```

    <源路径>：源文件或者源目录，这里可以是通配符表达式，其通配符规则要满足 Go 的 filepath.Match 规则。例如：

    ```dockerfile
    COPY hom\* /mydir/
    COPY hom?.txt /mydir/
    ```

    <目标路径>：容器内的指定路径，该路径不用事先建好，路径不存在的话，会自动创建。

    注意：

    1. COPY不包括本机目录：比如`COPY webroot /mnt`只会把webroot目录里面的内容复制到容器内，不包括webroot目录本身。如果希望把本级目录也拷贝进去，容器路径加一级同名子目录，可以不存在，会自动创建：`COPY webroot /mnt/webroot`
    2. 如果希望在宿主机改好文件权限和属主属组再拷贝进容器，这样是不推荐的，docker的机制是执行docker build的时候用户是谁，容器内的文件权限和属主属组就是谁。所以还是得在dockerfile里面去改。
    3. 注意拷贝目录内所有内容的时候不要用\*通配符，否则子目录不会被复制。`COPY xxx/*:/mnt/` --> 错误；`COPY xxx/:/mnt/` --> 正确

- ADD

  ADD 指令和 COPY 的使用格式一致（同样需求下，官方推荐使用 COPY）。功能也类似，不同之处如下：

  - ADD 的优点：在执行 <源文件> 为 tar 压缩文件的话，压缩格式为 gzip, bzip2 以及 xz 的情况下，会自动复制并解压到 <目标路径>。

- VOLUME

  - 定义匿名数据卷。在启动容器时忘记挂载数据卷，会自动挂载到匿名卷。

  - 作用：

    1、避免重要的数据，因容器重启而丢失，这是非常致命的。

    2、避免容器不断变大。

  - 格式：

    `VOLUME ["<路径1>", "<路径2>"...]`

    `VOLUME <路径>`

    在启动容器 docker run 的时候，我们可以通过 -v 宿主机目录：容器目录 修改挂载点。(docker run -d -P --name volume-test -v /hangx:/data centos-volume-test)

- WORKDIR

  - 指定工作目录。用 WORKDIR 指定的工作目录，会在构建镜像的每一层中都存在。（WORKDIR 指定的工作目录，必须是提前创建好的）。

  - docker build 构建镜像过程中，每一个 RUN 命令都是新建的一层。只有通过 WORKDIR 创建的目录才会一直存在。

  - 用`docker exec -it /bin/bash`进去之后就是指定的**工作目录路径**。一般都使用`容器用户的家目录`作为WORKDIR。

  - 格式：

    WORKDIR <工作目录绝对路径>

- ENV

  - 设置环境变量

    `ENV \<key\> \<value\>`

    `ENV \<key\>=\<value\>`

  - 示例：

    以下示例设置 NODE_VERSION=6.6.6， 在后续的指令中可以通过 $NODE_VERSION 引用：

    ENV NODE_VERSION 6.6.6

    ```bash
    RUN curl -SLO "https://nodejs.org/dist/v$NODE_VERSION/node-v$NODE_VERSION-linux-x64.tar.xz" && curl -SLO "https://nodejs.org/dist/v$NODE_VERSION/SHASUMS256.txt.asc"**
    ```

- USER

  - 用于指定执行后续命令的用户和用户组，这边只是切换后续命令执行的用户（用户和用户组必须提前已经存在）。

  - 格式：`USER <用户名>[:<用户组>]`

    ```sh
    USER daemon
    USER nginx
    USER user    
    USER uid
    USER user:group 
    USER uid:gid
    USER user:gid  
    USER uid:group
    ```

  - 一般推荐用uid `1000`或者`1001`作为容器启动用户。指定了非root用户后，端口监听可能没有权限监听1024以下的端口，一般设置为`8080`端口来启动。

- ONBUILD

  - Dockerfile 里用 ONBUILD 指定的命令，在本次构建镜像的过程中不会执行（假设镜像为 test-build）。当有新的 Dockerfile 使用了之前构建的镜像 FROM test-build ，这时执行新镜像的 Dockerfile 构建时候，会执行 test-build 的 Dockerfile 里的 ONBUILD 指定的命令。
  - 格式：`ONBUILD <其它指令>`

- ARG，使用 ARG 和 build-arg 传入动态变量：

  ~~~sh
  # base image
  FROM registry.cn-beijing.aliyuncs.com/dotbalo/centos:7
  ARG USERNAME
  ARG DIR="defaultValue"
  RUN useradd -m $USERNAME -u 1001 && mkdir $DIR
  # 构建镜像
  docker build --build-arg USERNAME="test_arg" -t test:arg .
  ~~~

  这样可以把dockerfile做成一个框架

## dockerfile优化

### image层数优化

1. Dockerfile 的指令每执行一次都会在 docker 上新建一层。所以过多无意义的层，会造成镜像膨胀过大。

```bash
FROM centos
RUN rm -rf /etc/yum.repos.d/*
COPY Centos-vault-8.5.2111.repo /etc/yum.repos.d/
RUN yum install wget -y
RUN wget -O redis.tar.gz "http://download.redis.io/releases/redis-5.0.3.tar.gz"
RUN tar -xvf redis.tar.gz
```

- 以上执行会创建 3 层镜像。可简化为以下格式：(dockerfile支持换行符)

```bash
FROM centos
RUN rm -rf /etc/yum.repos.d/*
COPY Centos-vault-8.5.2111.repo /etc/yum.repos.d/
RUN yum install wget -y && \
wget -O redis.tar.gz "http://download.redis.io/releases/redis-5.0.3.tar.gz" && \
tar -xvf redis.tar.gz
```

2. 用安装完之后清理缓存

   ```bash
   FROM centos
   RUN rm -rf /etc/yum.repos.d/*
   COPY Centos-vault-8.5.2111.repo /etc/yum.repos.d/
   RUN yum install epel-release -y && \
   yum install -y gcc gcc-c++ make gd-devel libxml2-devel \
   libcurl-devel libjpeg-devel libpng-devel openssl-devel \
   libmcrypt-devel libxslt-devel libtidy-devel autoconf \
   iproute net-tools telnet wget curl && \
   yum clean all && \
   rm -rf /var/cache/yum/*
   ```

   `yum clean all &&` 和 `rm -rf /var/cache/yum/*` 可以清理掉yum缓存，节省image空间

3. 可以用`docker history <image id>`来看镜像每一层的大小。

### 基础镜像优化

制作业务镜像的时候，去找一个官方已经装好基础环境的镜像，比如python，jdk等。不需要基础环境的话，可以用一些精简的小镜像：

- busybox
  描述：可以将busybox理解为一个超级简化版嵌入式Linux系统。
  官网：https://www.busybox.net/
  镜像：https://hub.docker.com/_/busybox/
  包管理命令：apk, lbu
  包管理文档：https://wiki.alpinelinux.org/wiki/Alpine_Linux_package_management

- Alpine
  描述：Alpine是一个面向安全的、轻量级的Linux系统，基于musl libc和busybox。
  官网：https://www.alpinelinux.org/
  镜像：https://hub.docker.com/_/alpine/
  包管理命令：apk, lbu
  包管理文档：https://wiki.alpinelinux.org/wiki/Alpine_Linux_package_management

  ~~~sh
  # base image
  FROM registry.cn-beijing.aliyuncs.com/dotbalo/alpine:3.20
  MAINTAINER dot
  # Alpine 镜像创建用户的命令为 adduser，-D 表示不设置密码
  RUN adduser -D dot
  ~~~

### 容器外进行文件操作

如果需要将某个压缩文件拷贝到镜像，并且需要更改文件夹权限，在构建之前先更改完毕，再进行构建镜像。不要在镜像里面用RUN去跑：

~~~sh
# 这两行命令如果放到FROM后面，用RUN来跑，每一行都会增加一层镜像大小
tar xf xxx.tar.gz -C xxx
chown -R 1001.1001 xxx
FROM registry.cn-beijing.aliyuncs.com/dotbalo/alpine:3.20
MAINTAINER dot
COPY xxx /mnt/xxx
~~~

### 多阶段构建

FROM之后还能继续用FROM

以go程序为例，go build之后生成的二进制文件，不依赖与宿主机有go环境了，直接就可以运行了。

当我们打包运行一个go服务的时候，我们希望的只是运行起来这个go二进制程序。而在go编译的时候会产生很大的缓存层

~~~go
# cat hw.go 
package main
import "fmt"
func main() {
fmt.Println("Hello World!")
}
~~~

单阶段构建：产生的镜像大小300多MB

~~~sh
# build step
FROM registry.cn-beijing.aliyuncs.com/dotbalo/golang:1.22.4-alpine3.20
WORKDIR /opt
COPY hw.go /opt
RUN go build /opt/hw.go 
CMD "./hw"
~~~

多阶段构建，在第一阶段用golang的基础镜像构建出二进制文件之后，第二阶段用一个apline小镜像去运行服务即可

~~~sh
# cat Dockerfile 
# 构建过程，as builder是给第一阶段起了个名字
FROM registry.cn-beijing.aliyuncs.com/dotbalo/golang:1.22.4-alpine3.20 AS builder
WORKDIR /opt
COPY hw.go /opt
RUN go build /opt/hw.go 

# 生成应用镜像过程
FROM registry.cn-beijing.aliyuncs.com/dotbalo/alpine:3.20
# 指定了builder，从上一阶段的镜像层复制文件过来
COPY --from=builder /opt/hw . 
CMD [ "./hw" ]
~~~

Java程序也一样，第一阶段builder，先找一个maven的基础镜像，maven clean install去构建；第二阶段用一个小镜像（openjdk），把jar包拷贝过来jave -jar运行即可。

只要是需要编译 -- 运行的程序都可以拆分成两个阶段去构建镜像。

### 制作支持多操作系统的镜像

~~~sh
docker build --platform linux/amd64,windows/amd64 -t myapp .
~~~

### 使用根文件系统镜像

~~~sh
#访问 Alpine 官方网站的 下载页面，找到并下载最新版本的根文件系统 tarball。你也可以使用以下命令直接下载（这里以 3.14 版本为例）
wget https://dl-cdn.alpinelinux.org/alpine/v3.14/releases/x86_64/alpine-minirootfs-3.14.0-x86_64.tar.gz
#使用下载的 tarball 创建 Docker 镜像：
cat alpine-minirootfs-3.14.0-x86_64.tar.gz | docker import - alpine:3.14
#验证镜像是否成功创建：
docker images
#运行 Docker 容器
docker run -it alpine:3.14 /bin/sh
~~~

## dockerfile安全实践

1. 注意不要使用臃肿或者未经验证的基础镜像

- 使用大型或未验证的镜像会增加不必要的包和依赖项，从而增加攻击面。来自不可信来源的镜像可能包含恶意软件或漏洞，感染你的构建管道。

- 使用 `ubuntu:latest` 意味着每次构建时可能会拉取不同的镜像，导致环境不一致。最好是将基础镜像固定到特定的、经过验证的版本，最好是经过安全优化的版本，比如`FROM ubuntu:20.04`

2. 注意固定包的版本

- 未固定包的版本会导致不可预测性。未来的构建可能会引入未经测试或存在漏洞的依赖项版本，破坏你的应用程序或暴露安全漏洞。
- 错误示例：`RUN apt-get update && apt-get install -y curl`
- 正确示例：`RUN apt-get update && apt-get install -y curl=7.68.0-1ubuntu2.12`

3. 不要以root用户运行

- 尽早切换到非 root 用户可以最大限度地减少容器以 root 用户运行的时间。这减少了 Dockerfile 中任何命令存在漏洞时的攻击面。

  ~~~sh
  # base image
  FROM registry.cn-beijing.aliyuncs.com/dotbalo/centos:7
  RUN useradd -m nginx -u 1001
  WORKDIR /home/nginx
  USER 1001
  ~~~

- 使用非root用户操作一些文件的时候可能报权限错误，这时候推荐把产生的文件放到容器用户家目录下，肯定有权限。

- 使用非root用户启动服务监听端口的时候可能会报没有权限监听1024以下的端口。推荐用8080端口监听。

4. 使用COPY而不是ADD

- ADD 指令提供了额外的功能（例如，解压存档、从远程位置获取文件），这可能会引入意外行为或漏洞。可能出现的问题：如果攻击者攻破远程源，你的构建将包含恶意内容。存档可能会覆盖容器中的关键文件。
- 错误示例：`ADD https://example.com/app.tar.gz /app/`
- 正确示例：始终使用 `COPY` 处理本地文件。使用 `wget` 或 `curl` 进行远程下载，并结合校验和验证。

5. 定义健康检查

- 定义有意义的健康检查以确保容器始终处于运行状态。

  ```sh
  HEALTHCHECK --interval=30s --timeout=5s \
    CMD curl -f http://localhost/health || exit 1
  ```

6. 定义限制性安全配置文件

- 在没有限制性安全配置文件（如 Seccomp、AppArmor）的情况下运行容器，允许它们进行危险的系统调用，攻击者可能使用 `ptrace` 系统调用提取敏感进程数据。

- 启用 Docker 的默认 Seccomp 配置文件或为你的应用程序定义自定义配置文件。

  ```sh
  docker run --security-opt seccomp=default.json myimage
  ```

## dockerfile制作异构镜像

- docker支持异构，在AMD64上可以做ARM镜像，在ARM上可以做AMD64的镜像，这个插件叫buildx。
- 架构列表：[docker-library/official-images: Primary source of truth for the Docker "Official Images" program](https://github.com/docker-library/official-images#architectures-other-than-amd64)
- 注意：制作多架构镜像时，基础镜像也必须支持多架构，可以在dockerhub的镜像tag里面看到支持的镜像

~~~sh
# 查看所有构建器
docker builder ls
# 创建一个新的构建器：
docker buildx create --name mybuilder --use --platform linux/amd64,linux/arm64 --driver docker-container
# 查看新创建的构建器，是inactive状态
docker builder ls
# 启动新创建的构建器
docker buildx inspect --bootstrap
# 安装所有架构：
docker run --privileged --rm tonistiigi/binfmt --install all

# 如果基础镜像用的是自己私有仓库的镜像，推荐从dockerhub先拉基础镜像，用buildx构建并推送到私有镜像库来用。
# 写一个dockerfile，只包含这个基础镜像
FROM centos:7.9

# 构建多架构镜像并上传：
docker buildx build --platform linux/arm64,linux/amd64 -t registry.cnbeijing.aliyuncs.com/dotbalo/buildx:v2 --push -f ./Dockerfile .
# 只构建不推送：
docker buildx build --platform linux/arm64/v8 -t registry.cnbeijing.aliyuncs.com/dotbalo/buildx:armv2 -f ./Dockerfile . --load

# 注意构建出来的异构镜像是只有一个tag但是支持多架构的，拉取的时候根据架构不同，用--platform来
# 拉镜像指定架构
docker pull xxx:tag --platform linux/arm64
~~~

## dockerfile实战

### 制作 Vue/H5 前端镜像

代码地址：https://gitee.com/dukuan/vue-project.git

编译镜像步骤：运行包含构建环境的基础镜像，把宿主机的代码目录挂进去，进容器执行构建命令，构建结果就在宿主机上。

1. 进入容器：

~~~sh
docker run -it --rm -v `pwd`/vueproject:/mnt/ registry.cn-beijing.aliyuncs.com/citools/node:lts bash
~~~

2. 容器内执行构建命令：

~~~sh
cd /mnt
npm install --registry=https://registry.npmmirror.com/
npm run build
# 构建完宿主机工程目录会生成一个dist目录，里面有index.html和static目录。拷贝到nginx目录下就可以运行了
~~~

3. Dockerfile制作镜像：

~~~sh
# 把dockerfile放到代码工程目录
mv Dockerfile vueproject/
# 前端代码一般采用 nginx 进行部署
FROM registry.cn-beijing.aliyuncs.com/dotbalo/nginx:1.15.12
COPY dist/ /usr/share/nginx/html/
# nginx镜像自带启动命令，所以可以不写CMD
# 构建
docker build -t xxx:xxx .
~~~

### 制作 Java 后端镜像

代码地址：https://gitee.com/dukuan/spring-boot-project.git

编译镜像：registry.cn-beijing.aliyuncs.com/citools/maven:3.5.3

1. 进入容器：

~~~sh
# 对于java程序，默认有一个缓存目录/root/.m2，可以在宿主机的代码目录上创建一个m2目录挂进容器作为缓存。一些插件会缓存进去，下次构建的时候还能用。
mkdir m2
docker run -it --rm -v `pwd`/m2:/root/.m2 -v `pwd`/spring-boot-project:/mnt/ registry.cn-beijing.aliyuncs.com/citools/maven:3.5.3 bash
~~~

2. 容器内执行构建命令：

~~~sh
cd /mnt
mvn clean install -DskipTests
~~~

3. Dockerfile制作镜像：

~~~sh
# 把dockerfile放到代码工程目录
mv Dockerfile /spring-boot-project
#  基础镜像可以按需修改，可以更改为公司自有镜像
FROM registry.cn-beijing.aliyuncs.com/dotbalo/jre:8u211-data
# jar 包名称改成实际的名称，本示例为 spring-cloud-eureka-0.0.1-SNAPSHOT.jar
COPY target/spring-cloud-eureka-0.0.1-SNAPSHOT.jar ./app.jar
#  启动 Jar 包
CMD java -jar app.jar

# 构建
docker build -t xxx:xxx .
~~~

### 制作 golang 后端镜像

代码地址：https://gitee.com/dukuan/go-project.git

编译镜像：registry.cn-beijing.aliyuncs.com/citools/golang:1.15

1. 进入容器：

~~~sh
# 对于go程序，默认有一个缓存目录/go/pkg，可以在宿主机的代码目录上创建一个pkg目录挂进容器作为缓存。一些插件会缓存进去，下次构建的时候还能用。
# go代码默认放在/go/src下面
mkdir pkg
docker run -it --rm -v `pwd`/pkg:/go/pkg -v `pwd`/go-project:/go/src registry.cn-beijing.aliyuncs.com/citools/maven:3.5.3 bash
~~~

2. 容器内执行构建命令：

~~~sh
cd /go/src
export GO111MODULE=on
go env -w GOPROXY=https://goproxy.cn,direct
go build
~~~

3. Dockerfile制作镜像：

~~~sh
# 把dockerfile放到代码工程目录
mv Dockerfile /go-project

FROM registry.cn-beijing.aliyuncs.com/dotbalo/alpine-glibc:alpine-3.9
#  如果定义了单独的配置文件，可能需要拷贝到镜像中
COPY conf/ ./conf 
#  包名按照实际情况进行修改
COPY ./go-project ./ 
#  启动该应用，CMD 和 ENTRYPOINT 均可
ENTRYPOINT [ "./go-project"]   

# 构建
docker build -t xxx:xxx .
~~~

# docker-compose

## 背景

- docker建议我们每一个容器中只运行一个服务，因为docker容器本身占用资源极少，所以最好是将每个服务单独的分割开来，但是这样我们又面临了一个问题：如果需要同时部署多个服务,每个服务单独写Dockerfile、构建镜像、构建容器，繁琐。

- 所以docker官方提供了docker-compose多服务部署的工具。
  - 例如：要实现Web微服务项目，除了Web服务容器本身，还需要再加上后端mysql、redis、注册中心eureka、甚至还包括负载均衡容器等等。
  - compose允许用户通过一个单独的docker-compose.yml文件来定义一组相关联的应用容器为一个项目（project）。
  - 可以很容易地用一个配置文件定义一个多容器的应用，然后使用一条指令安装这个应用的所有依赖，完成构建。Docker-Compose 解决了容器与容器之间如何管理编排的问题。

docker-compose使用的三个步骤：

1. 编写Dockerfile定义各个微服务应用并构建出对应的镜像文件
2. 使用 docker-compose.yml 定义一个完整业务单元，安排好整体应用中的各个容器服务。
3. 最后，执行docker-compose up命令 来启动并运行整个应用程序，完成一键部署上线

## 安装

- 直接随着docker安装--是基于插件的形式安装的，不推荐

~~~sh
sudo yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
sudo yum install docker-ce docker-ce-cli containerd.io docker-compose-plugin
#docker compose version就能看到已经安装了
~~~

- github下载--自己下载二进制文件，推荐

~~~sh
#https://github.com/docker/compose/releases下载安装包
mv docker-compose-Linux-x86_64.64 /usr/bin/docker-compose
chmod +x /usr/bin/docker-compose
~~~

# 阿里云镜像仓库使用

官网：https://cr.console.aliyun.com/

1. 使用阿里云镜像仓库第一步需要创建命名空间，相当于 repository

2. 第二步需要创建一个仓库（可选，也可以不创建，直接推送也可以），注意镜像仓库的地区

3. 实例创建固定密码

4. 登录：

   ~~~sh
   docker login registry.cn-beijing.aliyuncs.com
   Username (dotbalo):  输入用户名
   Password:  输入仓库密码
   Login Succeeded
   ~~~

5. 推送镜像

   ~~~sh
   docker tag centos:8 registry.cn-beijing.aliyuncs.com/dotbalo/centos:8
   docker push registry.cn-beijing.aliyuncs.com/dotbalo/centos:8
   ~~~

# Docker私有镜像仓库harbor

## Harbor介绍

- Docker容器应用的开发和运行离不开可靠的镜像管理，虽然Docker官方也提供了公共的镜像仓库，但是从安全和效率等方面考虑，部署我们私有环境内的Registry也是非常必要的。

- Harbor是由VMware公司开源的企业级的Docker Registry管理项目，它包括权限管理(RBAC)、LDAP、日志审核、管理界面、自我注册、镜像复制和中文支持等功能。

- 官网地址：https://github.com/goharbor/harbor

## Harbor安装配置-基于docker-compose

1. 为harbor创建自签发证书

   ```bash
   #设置主机名
   hostnamectl set-hostname harbor && bash
   
   mkdir /data/ssl -p
   cd /data/ssl/
   
   #生成一个3072位的key，也就是私钥
   openssl genrsa -out ca.key 3072
   
   #生成一个数字证书ca.pem，3650表示证书的有效时间是3年。后续根据ca.pem根证书来签发信任的客户端证书
   openssl req -new -x509 -days 3650 -key ca.key -out ca.pem 
   
   #生成域名的证书
   #生成一个3072位的key，也就是私钥
   openssl genrsa -out harbor.key  3072
   #生成一个证书请求文件，一会签发证书时需要的
   openssl req -new -key harbor.key -out harbor.csr
   
   #签发证书：
   openssl x509 -req -in harbor.csr -CA ca.pem -CAkey ca.key -CAcreateserial -out harbor.pem -days 3650
   ```

2. 安装docker：前面装docker的步骤

3. 安装harbor

   ```bash
   #配置hosts文件
   vim /etc/hosts
   #添加：
   10.0.0.4 hangxdockerlab
   10.0.0.5 harbor
   
   #创建安装目录
   mkdir /data/install -p
   cd /data/install/
   #安装harbor
   #/data/ssl目录下有如下文件：ca.key  ca.pem  ca.srl  harbor.csr  harbor.key  harbor.pem
   
   cd /data/install/
   #把harbor的离线包harbor-offline-installer-v2.3.0-rc3.tgz上传到这个目录
   #下载harbor离线包的地址：
   #https://github.com/goharbor/harbor
   #解压：
   tar zxvf harbor-offline-installer-v2.3.0-rc3.tgz
   cd harbor
   cp harbor.yml.tmpl harbor.yml 
   
   vim harbor.yml
   # 修改配置文件：
   hostname:  harbor #修改hostname，跟上面签发的证书域名保持一致
   # 协议用https
   certificate: /data/ssl/harbor.pem
   private_key: /data/ssl/harbor.key
   # 邮件和ldap不需要配置，在harbor的web界面可以配置，其他配置采用默认即可。
   # 修改数据目录
   data_volume: /data/harbor
   # 注：harbor默认的账号密码：admin/Harbor12345
   ```

4. 【可选】安装docker-compose

   docker-compose项目是Docker官方的开源项目，负责实现对Docker容器集群的快速编排。Docker-Compose的工程配置文件默认为docker-compose.yml，Docker-Compose运行目录下的必要有一个docker-compose.yml。docker-compose可以管理多个docker实例。

   ```bash
   #上传docker-compose-Linux-x86_64文件到harbor机器，这是harbor的依赖
   mv docker-compose-Linux-x86_64.64 /usr/bin/docker-compose
   chmod +x /usr/bin/docker-compose
   
   #安装harbor依赖的的离线镜像包docker-harbor-2-3-0.tar.gz上传到harbor机器，通过docker load -i解压
   docker load -i docker-harbor-2-3-0.tar.gz 
   ```

   > 注：
   >
   > - docker-compose可以直接yum install docker-compose或者apt install docker-compose
   >
   > - 离线镜像包docker-harbor-2-3-0.tar.gz如果不上传，install.sh会自动拉取
   >
   > - 新版docker已经内置了docker-compose插件 docker compose就能直接用

5. 启动harbor

   ~~~sh
   # 安装harbor
   cd /data/install/harbor
   ./install.sh
   #出现✔ ----Harbor has been installed and started successfully.---- 表明安装成功。
   ~~~

6. harbor启动和停止

   ```bash
   #如何停掉harbor：
   cd /data/install/harbor
   docker-compose stop 
   #如何启动harbor：
   cd /data/install/harbor
   docker-compose start
   ```

7. 图形化界面访问harbor

   - 在harbor同一个VNET下创建了一台Windows VM，在C:\Windows\System32\drivers\etc下修改hosts文件，添加 harbor 10.0.0.5。浏览器访问：https://harbor
   - Harbor VM NSG开放443端口，直接访问公网IP就行（https://20.205.104.235）

## harbor私有镜像仓库使用

```bash
#在docker lab机器上修改docker镜像源
#修改docker配置 
vim /etc/docker/daemon.json

{  "registry-mirrors": ["https://rsbud4vc.mirror.aliyuncs.com","https://registry.docker-cn.com","https://docker.mirrors.ustc.edu.cn","https://dockerhub.azk8s.cn","http://hub-mirror.c.163.com"],
"insecure-registries": ["10.0.0.5","harbor"]
}
#注意：配置新增加了一行内容如下："insecure-registries": ["10.0.0.5","harbor"]
#上面增加的内容表示我们内网访问harbor的时候走的是http，10.0.0.5是安装harbor机器的ip

#修改配置之后使配置生效：
systemctl daemon-reload && systemctl restart docker
#查看docker是否启动成功
systemctl status docker

#登录仓库
docker login 10.0.0.5

#将本地镜像上传到仓库
docker load -i tomcat.tar.gz
docker tag tomcat:latest  10.0.0.5/test/tomcat:v1
docker push 10.0.0.5/test/tomcat:v1 

#从仓库拉取镜像
docker rmi -f 10.0.0.5/test/tomcat:v1
docker pull 10.0.0.5/test/tomcat:v1
```

## 权限管理

项目管理员、维护人员、开发者是三个最常用的角色。一般给一个维护人员就够了。

## 垃圾回收

- 每个项目需要配置策略，一般是配置保留最近推送的30个tag，每周执行。这里配置的策略仅仅是清理了tag，但是底层数据存储没有清理。
- 系统管理中需要配置清理策略：
  - 配置日志清理策略，比如每周清理日志
  - 配置垃圾清理策略，比如每周运行，用一个线程清理即可，允许回收无tag的镜像

## 复制管理

可以把其他镜像仓库的镜像复制过来or同步harbor镜像到其他镜像仓库。

