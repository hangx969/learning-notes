# Openshift基础

## 介绍

- OpenShift 是红帽 Red Hat 公司开源的平台，是平台即服务（PaaS），是一种容器应用平台。允许开发人员构建、测试和部署应用。在 OpenShift 上可以进行开发、测试、部署、运维全流程，实现高度的自动化，满足企业中的应用持续集成和交付及部署的需求，同时也满足企业对于容器管理（Docker）、容器编排（K8S）的需求。
- Openshift 是首个支持企业级 Java 的 PaaS 平台，支持 JEE6 与 JBoss 和其 Eclipse 集成开发环境以及 Maven 和 Jenkins 自动化。

- OpenShift通常被称为容器应用平台，因为它是一个用于开发和部署容器的平台。OpenShift底层以Docker作为容器引擎驱动，以K8s作为容器编排引擎组件，并提供了开发语言，中间件，DevOps自动化流程工具和web console用户界面等元素，提供了一套完整的基于容器的应用云平台。

## 功能

- 容器引擎：docker；
- 容器编排：kubernetes；
- 应用开发框架及中间件：Java、Python、Tomcat、MySQL、PHP、Ruby、MongoDB和JBoss等中间件；
- 应用及服务目录：用户可一键部署各类应用及服务；
- 自动化流程及工具：内置自动化流程工具S2I（Source to Image），用户可完成代码编译、构建和镜像发布；
- 软件定义网络：提供 OpenVSwitch，实现跨主机共享网络及多租户隔离网络模式；
- 性能监控及日志管理：内置 Prometheus 监控功能，用户可以通过 Grafana 仪表板上实时显示应用；
- 多用户接口：提供友好的 UI、命令行工具（oc，类似于 K8S 的 kubectl 以及 RESTful API，基本与 K8S 兼容）；
- 自动化集群部署及管理：通过 Ansible 实现集群的自动化部署，为集群的自动化扩容提供接口。

## 与K8S区别

- 概念：OpenShift 是 PaaS（平台即服务），K8S 是 CaaS（容器即服务），OpenShift 内置了Kubernetes。OpenShift 底层以 Docker 作为容器引擎驱动，以 Kubernetes 作为容器编排引擎组件。
- 部署：OpenShift 可以安装在 RHEL（Red Hat Enterprise Linux）和 RHELAH（Red Hat Eneterprise Linux Atomic Host）、CentOS 和 Fedora上；K8S 最好在 Unbuntu、Fedora、centos 和 Debian上运行，可部署在任何主要的 IaaS 上，如 IBM、AWS、Azure、GCP 和阿里云等云平台上。
- 网络：OpenShift 提供了开箱即用的本机网络解决方案，即 OpenvSwitch，它提供三种不同的插件；K8S 没有本机网络解决方案，但提供可供第三方网络插件使用的接口。

## 与K8S相同点

OpenShift 集成了原生的 K8S 作为容器编排组件，提供容器集群的管理，为业务应用可以提供：

- 容器调度：根据业务的要求，快速部署容器到达指定的目标状态；
- 弹性伸缩：应用可以快速的扩缩容pod的实例数量；
- 异常修复：在容器实例发生异常时，集群可以自动发现问题、处理并恢复应用服务的状态；
- 持久化卷：为集群中的不同机器上的容器提供持久化卷的对接功能；
- 服务发现：可以提供负载均衡及服务发现功能；
- 配置管理：为业务应用提供灵活的配置管理和分发规则。

## 基础组件

在OpenShift中，Kubernetes管理容器化应用程序，并为部署、维护和应用程序扩展提供机制。Kubernetes集群由一个或多个Master节点和一组Node节点组成。

- Master节点
  - 主控节点。包括API Server、Controller Manager Server和Etcd。主控节点管理其Kubernetes集群中的Node节点，并安排pod在这些节点上运行。

- Node节点
  - Node节点为容器提供运行时环境。Kubernetes集群中的每个Node节点都有需要由Master节点管理的服务。该节点还具有运行pods所需的服务，包括容器运行时、kubelet和服务代理。

## 核心概念

- Project
  - Project是一个带有附加注释的Kubernetes名称空间，是管理普通用户访问资源的中心媒介。用户必须由管理员提供相关的权限，或者如果允许创建项目，则自动访问自己的项目。

- Namespaces
  - Kubernetes命名空间提供了一种用于划分集群中资源的机制。在OpenShift中，Project是带有附加注释的Kubernetes命名空间。

- Users
  - 与OpenShift交互的用户。OpenShift用户对象表示一个参与者，可以通过向其添加角色或向其组添加角色来授予该参与者在系统中的权限。

- Pod
  - 运行于Node节点上，若干相关容器的组合。Pod内包含的容器运行在同一宿主机上，使用相同的网络命名空间、IP地址和端口，能够通过localhost进行通信。Pod是Kurbernetes进行创建、调度和管理的最小单位，它提供了比容器更高层次的抽象，使得部署和管理更加灵活。一个Pod可以包含一个容器或者多个相关容器。

- Service
  - Service定义了Pod的逻辑集合和访问该集合的策略，是真实服务的抽象。Service提供了一个统一的服务访问入口以及服务代理和发现机制，关联多个相同Label的Pod，用户不需要了解后台Pod是如何运行。

- Router
  - Service提供了一个通往后端Pod集群的稳定入口，但是Service的IP地址只是集群内部的节点和容器可见。外部需通过Router（路由器）来转发
  - Router组件是Openshift集群中一个重要的组件，它是外界访问集群内容器应用的入口。用户可以创建Route（路由规则）对象，一个Route会与一个Service关联，并绑定一个域名。

- Persistent Storage
  - 容器默认是非持久化的，所有的修改在容器销毁时都会丢失。Docker提供了持久化卷挂载的能力，Openshift除了提供持久化卷挂载的能力，还提供了一种持久化供给模型即PV（Persistent Volume）和PVC（Persistent Volume Claim）。
  - 用户在部署应用时显示的声明对持久化的需求，创建PVC，在PVC中定义所需要的存储大小，访问方式。OpenShift集群会自动寻找符合要求的PV与PVC自动对接。

- Registry
  - Openshift内部的镜像仓库，主要用于存放内置的S2I构建流程所产生的镜像。

- S2I
  - Source to Image，负责将应用源码构建成镜像。

# 搭建OCP测试环境

## 实验环境规划

- 操作系统：centos7.9

- 节点规划：

  - master（192.168.40.180）

    - 8G/4H（cpu的虚拟化引擎选项全都打勾开启）

    - 两个硬盘80G/60G

  - node1（192.168.40.181）：

    - 4G/4H（cpu的虚拟化引擎选项全都打勾开启）

    - 两个硬盘80G/60G

  - node2（192.168.40.182）：

    - 4G/4H（cpu的虚拟化引擎选项全都打勾开启）

    - 两个硬盘80G/60G

- 网络模式：NAT

## 初始化实验环境

### 配置静态IP

~~~sh
vi /etc/sysconfig/network-scripts/ifcfg-ens33
TYPE=Ethernet
PROXY_METHOD=none
BROWSER_ONLY=no
BOOTPROTO=static
IPADDR=192.168.40.180
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
~~~

### 更新centos版本

~~~sh
yum update -y
~~~

### 安装基础软件包

~~~sh
yum install -y device-mapper-persistent-data lvm2 wget net-tools nfs-utils lrzsz gcc gcc-c++ make cmake libxml2-devel openssl-devel curl curl-devel unzip sudo ntp libaio-devel wget vim ncurses-devel autoconf automake zlib-devel  python-devel epel-release openssh-server socat  ipvsadm conntrack telnet ipvsadm
~~~

### 开启selinux

~~~sh
sed -i 's/SELINUX=enforcing/SELINUX=permissive/g' /etc/selinux/config
reboot -f
~~~

### 配置主机名和hosts文件

~~~sh
hostnamectl set-hostname master && bash 
hostnamectl set-hostname node1 && bash
hostnamectl set-hostname node2 && bash
~~~

~~~sh
vim /etc/hosts
192.168.40.180   master
192.168.40.181   node1  
192.168.40.182   node2
~~~

### 配置无密码登录

~~~sh
ssh-keygen
ssh-copy-id master
ssh-copy-id node1
ssh-copy-id node2
~~~

### 关闭交换分区

~~~sh
#临时关闭
swapoff -a
#永久关闭：注释swap挂载，给swap这行开头加一下注释
vim /etc/fstab   
#/dev/mapper/centos-swap swap      swap    defaults        0 0
~~~

### 修改机器内核参数

~~~sh
modprobe br_netfilter
cat > /etc/sysctl.d/k8s.conf <<EOF
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
EOF
sysctl -p /etc/sysctl.d/k8s.conf #sysctl -p：从指定的文件加载系统参数，如不指定即从/etc/sysctl.conf中加载
~~~

### 关闭firewalld防火墙

~~~sh
systemctl stop firewalld ; systemctl disable firewalld
~~~

### 配置阿里云repo源

~~~sh
yum install yum-utils -y
yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
~~~

### 配置时间同步

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

### 修改网卡配置文件

~~~sh
vim /etc/sysconfig/network-scripts/ifcfg-ens33
#最后追加如下内容：
NM_CONTROLLED=yes
#修改好之后重启网络
service network restart
~~~

### 停掉NetworkManager

~~~sh
#停掉NetworkManager
systemctl stop NetworkManager
systemctl disable NetworkManager
~~~

### 安装ansible

~~~sh
#把ansible-2.6.5-1.el7.ans.noarch.rpm上传到master、node1、node2上
yum install ansible-2.6.5-1.el7.ans.noarch.rpm -y
~~~

## 准备OCP部署

### 解压OCP安装包

~~~sh
#把openshift-ansible-release-3.10.zip上传到master节点，手动解压：
unzip openshift-ansible-release-3.10.zip
~~~

### 安装配置docker

~~~sh
#3台都需要配置
yum install -y docker-1.13.1

#修改docker配置文件
vim /etc/sysconfig/docker
#把之前的OPTIONS注释掉 
#OPTIONS='--selinux-enabled --log-driver=journald --signature-verification=false'
#新增如下内容：
OPTIONS='--selinux-enabled  --signature-verification=False'

#配置docker镜像加速器
systemctl start docker
vim /etc/docker/daemon.json 
{"registry-mirrors": ["http://6e9e5b27.m.daocloud.io","https://registry.docker-cn.com"],
"insecure-registries":["192.168.40.180:5000"]
}
systemctl restart docker
~~~

### 配置私有镜像仓库

~~~sh
#仅在master上配置私有镜像仓库
docker load -i registry.tar.gz
yum install httpd -y
systemctl start httpd
systemctl enable httpd
mkdir -p /opt/registry-var/auth/
docker run --entrypoint htpasswd registry:2.5 -Bbn hangxu hangxu  >> /opt/registry-var/auth/htpasswd

#设置配置文件
mkdir -p /opt/registry-var/config
vim /opt/registry-var/config/config.yml
version: "0.1"
log:
  fields:
    service: registry
storage:
  delete:
    enabled: true
  cache:
    blobdescriptor: inmemory
  filesystem:
    rootdirectory: /var/lib/registry
http:
  addr: :5000
  headers:
    X-Content-Type-Options: [nosniff]
health:
  storagedriver:
    enabled: true
    interval: 10s
threshold: 3

#启动服务
docker run -d -p 5000:5000 --restart=always  --name=registry -v /opt/registry-var/config/:/etc/docker/registry/ -v /opt/registry-var/auth/:/auth/ -e "REGISTRY_AUTH=htpasswd"  -e "REGISTRY_AUTH_HTPASSWD_REALM=Registry Realm" -e REGISTRY_AUTH_HTPASSWD_PATH=/auth/htpasswd -v /opt/registry-var/:/var/lib/registry/ registry:2.5
~~~

### 登录镜像仓库

~~~sh
#3台上都测试一下
docker login 192.168.40.180:5000
#username：hangxu
#pwd：  hangxu
~~~

### 修改docker存储

~~~sh
#设置docker开机自启动
systemctl enable docker
systemctl is-active docker
#所有节点更改/etc/sysconfig/docker-storage-setup如下：
DEVS=/dev/sdb 
VG=docker-vg
#所有Node节点执行docker-storage-setup
docker-storage-setup 
~~~

## 安装OCP

### 准备镜像

~~~sh
#master解压
docker load -i openshift_master_3_10.tar.gz
#node解压
docker load -i openshift_slave_3_10.tar.gz
docker load -i openshift_slave_3_10.tar.gz
~~~

### 配置ansible的hosts文件

~~~sh
#在master上
vim /etc/ansible/hosts 
[OSEv3:children]
masters
nodes
etcd
[OSEv3:vars]
openshift_deployment_type=origin
ansible_ssh_user=root
ansible_become=yes
openshift_repos_enable_testing=true
openshift_enable_service_catalog=false
template_service_broker_install=false
debug_level=4
openshift_clock_enabled=true
openshift_version=3.10.0 
openshift_image_tag=v3.10
openshift_disable_check=disk_availability,docker_storage,memory_availability,docker_image_availability,os_sdn_network_plugin_name=redhat/openshift-ovs-multitenant i
openshift_master_identity_providers=[{'name': 'htpasswd_auth','login': 'true', 'challenge': 'true','kind': 'HTPasswdPasswordIdentityProvider'}]
[masters]
master
[nodes]
master openshift_node_group_name='node-config-master'
node1 openshift_node_group_name='node-config-master' 
node2 openshift_node_group_name='node-config-master'
[etcd]
master
~~~

### 安装OCP

~~~sh
#安装前预配置检查，在master上执行
ansible-playbook -i /etc/ansible/hosts openshift-ansible-release-3.10/playbooks/prerequisites.yml
#显示ok 没有报错即可安装
ansible-playbook -i /etc/ansible/hosts openshift-ansible-release-3.10/playbooks/deploy_cluster.yml
~~~

> - 执行deploy时主机dns导致连外网失败（在执行上面deploy时，需要在每个节点ping www.baidu.com，如果ping不通，解决方案如下）
>
>   ```sh
>   echo nameserver 8.8.8.8 >>/etc/resolv.conf
>   ```
>
> 可以写个计划任务：
>
> ```sh
> crontab -e
> * */1 * * * /usr/sbin/ntpdate   cn.pool.ntp.org
> * * * * * /usr/bin/echo  nameserver 8.8.8.8  >>/etc/resolv.conf
> ```

### 给节点打标签

~~~sh
TASK [openshift_manage_node : Set node schedulability]
#到这个task之后执行下面部分
oc label node node1 node-role.kubernetes.io/infra=true
oc label node node2 node-role.kubernetes.io/infra=true
#显示complete表示安装成功
~~~

## 访问OCP

### 新建用户

~~~sh
#首次新建用户密码
htpasswd -cb /etc/origin/master/htpasswd admin admin
#添加用户密码
htpasswd -b /etc/origin/master/htpasswd dev dev
#以集群管理员登录
oc login -u system:admin
#给用户分配一个集群管理员角色
oc adm policy add-cluster-role-to-user cluster-admin admin
#浏览器登录openshift，配置自己电脑hosts文件，添加：
192.168.40.180 master
~~~

- 访问：https://master:8443/console/catalog，usrname：admin，passwd：admin

### 访问私有仓库

~~~sh
#Master上执行如下，获取admin密码
oc login -n openshift
#admin/admin
oc whoami -t
#eYtOZNGab9w4IO_LX2sHEHyoAZHOy1oxJ9gEsuJVMpI
#每个节点执行如下登陆openshift私有镜像仓库    
docker login docker-registry.default.svc:5000
#用户：admin
#密码：eYtOZNGab9w4IO_LX2sHEHyoAZHOy1oxJ9gEsuJVMpI
~~~

## OCP部署应用程序

> 使用OpenShift时，可以通过多种方式添加应用程序。 主要方法是：
>
> 1.通过已经存在的docker镜像部署应用程序
>
> 2.使用Source-to-Image的方式部署应用程序（Source-to-Image简称S2I:从代码仓库拉取代码，构建成镜像，基于此镜像部署应用程序）
>
> 3.在dockerfile中通过指定git仓库地址构建程序

- 登录web console：https://192.168.40.180:8443

### docker镜像部署

创建第一个项目ParkSmap，用来展示世界主要公园的地图的一个程序

- 点击右侧Create Project

  - name：myproject

  - 上面改好之后点击create即可

- Deploy image

  - 选中myproject这个项目

  - 点击Deploy image

    <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402171701124.png" alt="image-20240217170117952" style="zoom: 67%;" />

- 选create an image pull secret

  <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402171701104.png" alt="image-20240217170129000" style="zoom:67%;" />

  - Secret Name：parksmap
  - Image Registry Server Address：openshiftroadshow/parksmap-katacoda:1.0.0
  - Username：admin
  - Password：admin
  - Email：1003665363@qq.com

- 点击创建

- 再回到刚才的Deploy Image界面，选则下面的Image name，输入openshiftroadshow/parksmap-katacoda:1.0.0，然后点击搜索

  <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402171701686.png" alt="image-20240217170142597" style="zoom:67%;" />

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402171701804.png" alt="image-20240217170147717" style="zoom:67%;" />

- master节点做如下操作，给节点打标签，否则调度不成功

  ~~~sh
  oc label nodes node1 node-role.kubernetes.io/compute=true
  oc label nodes node2 node-role.kubernetes.io/compute=true
  oc label nodes node1 node-role.kubernetes.io/infra=true
  oc label nodes node2 node-role.kubernetes.io/infra=true
  ~~~

- master节点验证

  ~~~sh
  oc get pods -n myproject
  ~~~

- 上面创建好之后，在集群外部还是访问不了，需要修改service的cluster ip类型，Applications --> services --> 点击parksmap-katacoda --> 右侧Action下的Edit Yaml，修改内容如下

  ![image-20240217170416304](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402171704404.png)

  

- 改好之后点击Save, 在master节点查看

  ~~~sh
  oc get service -n myproject
  ~~~

- 访问：http://192.168.40.181:30080/index.html

### 通过S2I部署

> - Source to Image(S2I) 是一个创建 Docker 镜像的工具，也是 openshift 上面的主要构建镜像的方式之一。
>
> - S2I 会依赖一个特殊的 base 镜像，这个镜像主要包括基础的运行环境，如 Python, PHP，Nginx等。因此针对某类代码，只要提供好一个标准运行环境的基础镜像。使用的时候，先把用户的代码放到这个镜像中，生成一个新的镜像就可以。

#### 部署parksmap项目

接下来将要部署的示例应用程序是使用Python编程语言实现的。部署parksmap的后端程序，通过rest api获取世界主要公园的数据，部署方法如下：

- 项目Github代码地址：https://github.com/luckylucky421/nationalparks-katacoda，可以fork到自己的github上，或者迁移到gitee上。

- 在myproject项目下选则Add to project --> Browse Catalog --> python --> next

  <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402171707065.png" alt="image-20240217170702957" style="zoom: 67%;" />

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402171707113.png" alt="image-20240217170725012" style="zoom:67%;" />

Version：3.6

Application Name：nationalparks-katacoda

Git Repository：写自己的github/gitee项目地址

> 注：python3.5的s2i镜像: https://github.com/sclorg/s2i-python-container/blob/master/3.5/README.md

#### 部署django项目

- Github代码地址：https://github.com/openshift-instruqt/blog-django-py，可以fork到自己的github上，或者迁移到gitee上。

- myproject --> Add to project--> Browse Catalog --> python --> next

  <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402171712653.png" alt="image-20240217171224541" style="zoom:67%;" />

- 点击“Create”创建应用程序，进入如下界面。点击“Continue to the project overview”，进入查看应用程序状态。

  <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402171712760.png" alt="image-20240217171252658" style="zoom:67%;" />

- 点击箭头指示的位置，进入查看build状态

  - History：显示历史build列表
  - Configuration：显示配置信息
  - Environment：显示环境变量
  - Events：会输出重要事件

  <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402171713530.png" alt="image-20240217171314427" style="zoom:67%;" />

- 点击“#1”，进入查看该build进程的详细信息。

  ![image-20240217171342276](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402171713383.png)

- 点击“Logs”查看详细的日志信息。

  ![image-20240217171406904](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402171714021.png)

- 再次进入Overview界面，可以看见应用程序成功创建。

- 应用程序的源代码不会是静态的，因此需要在进行任何更改之后触发新构建的方法。更改源代码后，可以进入以下界面触发build。

  ![image-20240217171453968](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402171714066.png)

- 界面出现#2，代表第二次build在运行。

# OCP CICD流程

## CI/CD工具链涉及到的组件介绍

### gogs

- Gogs 是一款极易搭建的自助 Git 服务，类似于github这种代码托管系统；以最简便的方式搭建简单、稳定和可扩展的自助 Git 服务。使用 Go 语言开发使得 Gogs 能够通过独立的二进制分发，并且支持 Go 语言支持的 所有平台，包括 Linux、macOS、Windows 以及 ARM 平台。 

- 官方文档：https://gogs.io/docs/intro

- github上的中文站点：https://github.com/gogs/gogs/blob/master/README_ZH.md 

### nexus

- 为什么搭建nexus？

  有些公司都不提供外网给项目组人员，因此就不能访问maven中央仓库，或者公司内部的jar包在外网无法找到，所以很有必要在局域网里使用一台有外网权限的机器，搭建nexus私服，然后开发人员连到这台私服上，这样的话就可以通过这台搭建了nexus私服的电脑访问maven的远程仓库，或者从上面下载内部jar包，使得开发人员可以下载仓库中的内容，而且对于下载过的文件，局域网内下载会更加快速。还有一点优势在于，我们需要的jar包可能在中央仓库中没有，需要去其他地方下载，有了中央仓库，只需要一人找到jar包其他人就不用再去上网搜索jar包，十分方便。

## 创建OpenShift DevOps/CICD工作流

### 流程

1. 从gogs或者gitlab克隆代码

2. 通过maven构建war包

3. 单元测试

4. Sonarqube静态代码扫描

5. war包归档到Nexus

6. 构建docker image

7. 把镜像上传到harbor镜像仓库

8. 部署到dev环境

9. 部署到测试环境-集成测试

10. 管理员promote or abort

11. 部署到stage（生产）环境

官网地址：https://github.com/siamaksade/openshift-cd-demo/tree/origin-1.3

### OCP部署

- 依次创建三个项目

  ~~~sh
  oc new-project dev --display-name="Tasks - Dev" 
  oc new-project stage --display-name="Tasks - Stage" 
  oc new-project cicd --display-name="CI/CD"
  ~~~

- 给3个项目赋权

  ~~~sh
  oc policy add-role-to-group edit system:serviceaccounts:cicd -n dev 
  oc policy add-role-to-group edit system:serviceaccounts:cicd -n stage
  oc policy add-role-to-group view system:serviceaccounts:cicd -n dev 
  oc policy add-role-to-group view system:serviceaccounts:cicd -n stage
  ~~~

- 登陆openshift内部的私有镜像仓库

  ~~~sh
  #3个节点上都执行：
  oc login -n openshift
  #master上执行，获取密码
  oc whoami -t
  #每个节点执行如下，登录私有仓库
  docker login docker-registry.default.svc:5000
  #用户：admin
  #密码：前一步生成的密码
  ~~~

- 拉取镜像

  ~~~sh
  docker pull registry.access.redhat.com/openshift3/jenkins-agent-maven-35-rhel7
  ~~~

  > - 报错如下：
  >
  > ```sh
  > open /etc/docker/certs.d/registry.access.redhat.com/redhat-ca.crt: no such file or directory
  > ```
  >
  > - 解决办法如下：
  >
  > ```sh
  > #在每个节点操作
  > yum install *rhsm* -y
  > wget http://mirror.centos.org/centos/7/os/x86_64/Packages/python-rhsm-certificates-1.19.10-1.el7_4.x86_64.rpm
  > rpm2cpio python-rhsm-certificates-1.19.10-1.el7_4.x86_64.rpm | cpio -iv --to-stdout ./etc/rhsm/ca/redhat-uep.pem | tee /etc/rhsm/ca/redhat-uep.pem
  > ```

- 给node打标签

  ~~~sh
  oc label node node1 node-role.kubernetes.io/compute=true --overwrite
  oc label node master node-role.kubernetes.io/compute=true --overwrite
  oc label node node2 node-role.kubernetes.io/compute=true --overwrite
  ~~~

- 开始部署

  ~~~sh
  #在master上操作
  oc process -f cicd-template.yaml -n cicd | oc create -f - -n cicd
  oc get pods -n cicd
  
  #jenkins账号密码：使用openshift账号密码登陆
  #sonarqube账号密码：admin/admin
  #nexus账号密码：admin/admin123
  #gogs账号密码：需要注册，gogs/gogs
  ~~~

  