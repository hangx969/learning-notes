# 第二章 实验环境搭建

## 虚拟机搭建

- VM OS 版本：CentOS 7.6 - 7.9

- 2G内存、2vcpu

## docker安装

### 简洁版

https://docs.docker.com/engine/install/centos/

```bash
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo systemctl start docker
```

进阶版

```bash
#配置主机名：
hostnamectl set-hostname dockerlab && bash

#关闭防火墙
systemctl stop firewalld && systemctl disable firewalld

#安装iptables防火墙
yum install iptables-services -y
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
yum install -y ntp ntpdate
ntpdate cn.pool.ntp.org 
#编写计划任务
crontab -e 
* */1 * * * /usr/sbin/ntpdate   cn.pool.ntp.org
#重启crond服务使配置生效：
systemctl restart crond

#安装基础软件包
yum install -y  wget net-tools nfs-utils lrzsz gcc gcc-c++ make cmake libxml2-devel openssl-devel curl curl-devel unzip sudo ntp libaio-devel wget vim ncurses-devel autoconf automake zlib-devel  python-devel epel-release openssh-server socat  ipvsadm conntrack 

#安装docker-ce
#配置docker-ce国内yum源（阿里云）
yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
#安装docker依赖包
yum install -y yum-utils device-mapper-persistent-data lvm2
#安装docker-ce
yum install docker-ce -y

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

#在/etc/sysconfig/modules/目录下新建文件如下
vim /etc/sysconfig/modules/br_netfilter.modules
modprobe br_netfilter

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
#修改/etc/docker/daemon.json，变成如下
{
 "registry-mirrors":["https://y8y6vosv.mirror.aliyuncs.com","https://registry.docker-cn.com","https://docker.mirrors.ustc.edu.cn","https://dockerhub.azk8s.cn","http://hub-mirror.c.163.com"]
}

#让配置文件生效
sudo systemctl daemon-reload
sudo systemctl restart docker
```

Docker镜像加速器：

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310141551863.png" alt="image-20231014155157774" style="zoom: 67%;" />

# docker基础

## docker常用命令

```bash
docker run --name=hello -it centos /bin/bash
#docker run运行并创建容器，--name 容器的名字，-i 交互式，-t 分配伪终端，centos: 启动docker需要的镜像，/bin/bash说明你的shell类型为bash
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
#删除容器
docker rm -f hello1
#查看docker帮助命令
docker --help
```

## docker部署nginx服务

- 用centos作为基础镜像，在里面部署并配置nginx服务

```bash
#启动一个centos基础镜像，暴露80端口，会随即映射到宿主机的高位端口
docker run --name nginx -p 80 -itd centos
#查看容器信息
docker ps | grep nginx
##在docker里面安装nginx
#进入容器
docker exec -it nginx /bin/bash

#centos默认的这个yum源已经不维护了。删掉换成阿里云的源。
rm -rf /etc/yum.repos.d/* 
curl -o /etc/yum.repos.d/CentOS-Base.repo https://mirrors.aliyun.com/repo/Centos-vault-8.5.2111.repo #从阿里云镜像地址上下载一个yum源
yum install wget -y
yum install nginx -y 
#安装文本编辑器vim
yum install vim-enhanced -y

#创建静态主页
mkdir /var/www/html -p
cd /var/www/html/
vim index.html
<html>
        <head>
                 <title>nginx in docker</title>
        </head>
        <body>
                <h1>hello,My Name is xianchao</h1>
        </body>
</html>

#修改nginx配置文件，更改主页位置
vim /etc/nginx/nginx.conf
root  /var/www/html/;

#启动nginx
/usr/sbin/nginx

#查看宿主机高位端口
docker ps | grep nginx
#查看宿主机的内网ip
ip addr
#回到宿主机，用宿主机内网IP+高位端口，访问到容器
curl http://10.0.0.4:32768

#查看容器IP
docker inspect nginx
```

- 访问链路是：

  10.0.0.4：32768 -> 172.17.0.2:80

  宿主机IP：高位端口 -> 容器IP：nginx端口

- 原理

  ```
  ip addr
  1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
      link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
      inet 127.0.0.1/8 scope host lo
         valid_lft forever preferred_lft forever
      inet6 ::1/128 scope host 
         valid_lft forever preferred_lft forever
  2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
      link/ether 00:22:48:eb:bf:f7 brd ff:ff:ff:ff:ff:ff
      inet 10.0.0.4/24 brd 10.0.0.255 scope global noprefixroute eth0
         valid_lft forever preferred_lft forever
      inet6 fe80::222:48ff:feeb:bff7/64 scope link 
         valid_lft forever preferred_lft forever
  3: docker0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default 
      link/ether 02:42:4f:5a:c7:4c brd ff:ff:ff:ff:ff:ff
      inet 172.17.0.1/16 brd 172.17.255.255 scope global docker0
         valid_lft forever preferred_lft forever
      inet6 fe80::42:4fff:fe5a:c74c/64 scope link 
         valid_lft forever preferred_lft forever
  17: veth6032358@if16: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master docker0 state UP group default 
      link/ether 66:e6:f1:b7:09:67 brd ff:ff:ff:ff:ff:ff link-netnsid 0
      inet6 fe80::64e6:f1ff:feb7:967/64 scope link 
         valid_lft forever preferred_lft forever
  ```

  - veth6032358@if16这个设备称为veth对，一端连到物理网卡上，另一端连到docker。访问宿主机IP：高位端口时，veth对就通过管道将请求交给要访问的容器。

# dockerfile构建镜像

## dockerfile

Dockerfile是一个用于定义Docker镜像的文本文件。它包含了一系列的指令和参数，用于指示Docker在构建镜像时应该执行哪些操作，例如基于哪个基础镜像、复制哪些文件到镜像中、运行哪些命令等等。通过Dockerfile，开发人员可以将应用程序和其所有依赖项打包在一起，创建出一个可移植的Docker镜像，使得这个应用程序可以在任何Docker环境中都能够快速部署和运行。

### 示例

```dockerfile
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

## dockerfile语法

- FROM

  指定基础镜像，必须是可以下载的镜像。

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

  仅仅只是声明端口。作用：

  1、帮助镜像使用者理解这个镜像服务的守护端口，以方便配置映射。

  2、在运行时使用随机端口映射时，也就是 docker run -P 时，会自动随机映射 EXPOSE 声明的端口。

  3、可以是一个或者多个端口，也可以指定多个EXPOSE。格式：EXPOSE 80 8080。

- CMD

  - 类似于 RUN 指令，用于运行程序，但二者运行的时间点不同:

    1、CMD 在docker run 时运行。这是自启动的命令，容器起来之后，

    2、RUN 是在 docker build构建镜像时运行。

  - CMD的命令会被docker run的命令行参数给覆盖掉.

  - CMD如果有多个，只有最后一行会生效。

- ENTRYPOINT

  - 类似于 CMD 指令，但其不会被 docker run 的命令行参数指定的指令所覆盖，而且这些命令行参数会被当作参数送给 ENTRYPOINT 指令指定的程序。

  - 但是, 如果运行 docker run 时使用了 --entrypoint 选项，将覆盖 entrypoint指令指定的程序。

  - 优点：在执行 docker run 的时候可以指定 ENTRYPOINT 运行所需的参数。

  - 注意：存在多个 ENTRYPOINT 指令，仅最后一个生效。

  格式：

  ENTERYPOINT \[“executable”,“param1”,“param2”\](exec模式)

  ENTERYPOINT command （shell模式）

  - CMD和ENTRYPOINT配合使用举例

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

    
