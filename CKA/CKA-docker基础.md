# 实验环境搭建

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

### 进阶版

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

vscode在VM中运行docker插件

报错：

```bash
Got permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: Get "http://%2Fvar%2Frun%2Fdocker.sock/v1.24/images/json": dial unix /var/run/docker.sock: connect: permission denied
```

解决：

```bash
chmod 666 /var/run/docker.sock
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

# dockerfile基础

## dockerfile

Dockerfile是一个用于定义Docker镜像的文本文件。它包含了一系列的指令和参数，用于指示Docker在构建镜像时应该执行哪些操作，例如基于哪个基础镜像、复制哪些文件到镜像中、运行哪些命令等等。通过Dockerfile，开发人员可以将应用程序和其所有依赖项打包在一起，创建出一个可移植的Docker镜像，使得这个应用程序可以在任何Docker环境中都能够快速部署和运行。

示例

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

- COPY

  - 复制指令，从当前dockerfile上下文目录中复制文件或者目录到容器里指定路径。

  - 格式：

    ```bash
    COPY <src> <dest>
    COPY [“<src>”, “<dest>”]
    
    #[--chown=<user>:<group>]：可选参数，改变复制到容器内文件的拥有者和属组。
    COPY [--chown=<user>:<group>] <源路径1> <目标路径>
    COPY [--chown=<user>:<group>] ["<源路径1>", "<目标路径>"]
    ```

    <源路径>：源文件或者源目录，这里可以是通配符表达式，其通配符规则要满足 Go 的 filepath.Match 规则。例如：

    COPY hom\* /mydir/

    COPY hom?.txt /mydir/

    <目标路径>：容器内的指定路径，该路径不用事先建好，路径不存在的话，会自动创建。

- ADD

  ADD 指令和 COPY 的使用格式一致（同样需求下，官方推荐使用 COPY）。功能也类似，不同之处如下：

  - ADD 的优点：在执行 <源文件> 为 tar 压缩文件的话，压缩格式为 gzip, bzip2 以及 xz 的情况下，会自动复制并解压到 <目标路径>。

- VOLUME

  - 定义匿名数据卷。在启动容器时忘记挂载数据卷，会自动挂载到匿名卷。

  - 作用：

    1、避免重要的数据，因容器重启而丢失，这是非常致命的。

    2、避免容器不断变大。

  - 格式：

    VOLUME ["<路径1>", "<路径2>"...]

    VOLUME <路径>

    在启动容器 docker run 的时候，我们可以通过 -v 宿主机目录：容器目录 修改挂载点。(docker run -d -P --name volume-test -v /hangx:/data centos-volume-test)

- WORKDIR

  - 指定工作目录。用 WORKDIR 指定的工作目录，会在构建镜像的每一层中都存在。（WORKDIR 指定的工作目录，必须是提前创建好的）。

  - docker build 构建镜像过程中，每一个 RUN 命令都是新建的一层。只有通过 WORKDIR 创建的目录才会一直存在。

  - 用docker exec -it /bin/bash进去之后就是指定的工作目录路径。

  - 格式：

    WORKDIR <工作目录绝对路径>

- ENV

  - 设置环境变量

    ENV \<key\> \<value\>

    ENV \<key\>=\<value\>

  - 示例：

    以下示例设置 NODE_VERSION =6.6.6， 在后续的指令中可以通过 $NODE_VERSION 引用：

    ENV NODE_VERSION 6.6.6

    ```bash
    RUN curl -SLO "https://nodejs.org/dist/v$NODE_VERSION/node-v$NODE_VERSION-linux-x64.tar.xz" && curl -SLO "https://nodejs.org/dist/v$NODE_VERSION/SHASUMS256.txt.asc"**
    ```

- USER

  - 用于指定执行后续命令的用户和用户组，这边只是切换后续命令执行的用户（用户和用户组必须提前已经存在）。

  - 格式：

    USER <用户名>[:<用户组>]

    ```bash
    USER daemon
    USER nginx
    USER user    
    USER uid
    USER user:group 
    USER uid:gid
    USER user:gid  
    USER uid:group
    ```

- ONBUILD

  - Dockerfile 里用 ONBUILD 指定的命令，在本次构建镜像的过程中不会执行（假设镜像为 test-build）。当有新的 Dockerfile 使用了之前构建的镜像 FROM test-build ，这时执行新镜像的 Dockerfile 构建时候，会执行 test-build 的 Dockerfile 里的 ONBUILD 指定的命令。
  - 格式：ONBUILD <其它指令>

## docker构建nginx

```bash
#准备目录，将dockerfile、index和centos源都放进去
#写dockerfile
FROM centos
RUN rm -rf /etc/yum.repos.d/*
COPY Centos-vault-8.5.2111.repo /etc/yum.repos.d/
RUN yum install wget -y
RUN yum install nginx -y
COPY index.html /usr/share/nginx/html/
EXPOSE 80
ENTRYPOINT ["/usr/sbin/nginx","-g","daemon off;"]

#写index.html
<html>
<head>
        <title>page added to dockerfile</title>
</head>
<body>
        <h1>Hello world</h1>
</body>
</html>

#构建镜像：
docker build -t="nginx:v1" . --load
#查看镜像是否构建成功：
docker images | grep nginx
#基于镜像启动容器
docker run -d -p 80 --name nginx nginx:v1
#查看容器信息
docker ps | grep nginx
#宿主机访问nginx页面
curl 10.0.0.4:32773
```

## docker构建tomcat8

```bash
#把tomcat安装包和jdk包放到dockerfile目录
ls
apache-tomcat-8.0.26.tar.gz  Centos-vault-8.5.2111.repo  dockerfile  jdk-8u45-linux-x64.rpm

#写dockerfile
FROM centos
RUN rm -rf /etc/yum.repos.d/*
COPY Centos-vault-8.5.2111.repo /etc/yum.repos.d/
RUN yum install wget -y
ADD jdk-8u45-linux-x64.rpm /usr/local/
ADD apache-tomcat-8.0.26.tar.gz /usr/local/
RUN cd /usr/local && rpm -ivh jdk-8u45-linux-x64.rpm
RUN mv /usr/local/apache-tomcat-8.0.26 /usr/local/tomcat8
ENTRYPOINT /usr/local/tomcat8/bin/startup.sh && tail -F /usr/local/tomcat8/logs/catalina.out
#tomcat 的自动启动命令也可以用 ENTRYPOINT ["/usr/local/tomcat8/bin/catalina.sh", "run"]
EXPOSE 8080

#构建镜像
docker build -t="tomcat8:v1" . --load
#运行容器
docker run --name tomcat8 -d -p 8080 tomcat8:v1
```

## 基于Go代码构建镜像

```bash
#安装go
yum install -y go
#创建代码文件
vim main.go
```

```go
package main

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

func statusOKHandler(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"status": "success~welcome to study"})
}

func versionHandler(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"version": "v1.1版本"})
}

func main() {
	router := gin.New()
	router.Use(gin.Recovery())
	router.GET("/", statusOKHandler)
	router.GET("/version", versionHandler)
	router.Run(":8080")
}
```

```bash
#初始化项目
go mod init test

#因为有个包要从github下载，设置github代理
go env -w GOPROXY=https://goproxy.cn,direct
#把包下载下来
go mod tidy

#构建源码
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o k8s-demo main.go
```

```bash
#写dockerfile
FROM alpine
WORKDIR /data/app
ADD k8s-demo /data/app/
CMD ["/bin/sh","-c","./k8s-demo"]

#build镜像
docker build -t godemo:v1 . --load

#运行容器
docker run -d --name godemo -p 8080 godemo:v1
```

## 基于python代码构建镜像

```python
#获取python代码，切换到代码目录
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello from Python!"

if __name__ == "__main__":
    app.run(host='0.0.0.0')
```

```bash
#写dockerfile
FROM python:3.7 #从Docker Hub获取3.7版本的官方Python基本镜像。
RUN mkdir /app 
WORKDIR /app #将工作目录设置为新的app目录。
ADD . /app/ #将dockerfile本地目录的内容复制到该新文件夹，并将其复制到镜像中。
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install -r requirements.txt #运行pip安装程序，将需求拉入镜像中。
EXPOSE 5000 #通知Docker容器监听端口5000。
CMD ["python","/app/main.py"] #配置启动命令，使其在容器启动时使用。
```

```bash
#构建镜像
docker build -t hello-python:v1
#运行容器
docker run -d --name python -p 5000  hello-python:v1
```

# Docker数据持久化和网络模式

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

## docker数据卷容器

容器A挂载了一个volume，容器B通过volume-from参数，把A挂载的数据卷也挂载到自己里面，实现数据共享。

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

### docker数据卷的备份和还原

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

## docker容器互联

### docker0网桥

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

- 每运行一个docker容器都会生成一个veth设备对，这个veth一个接口在容器里，一个接口在物理机上。

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

### docker link网络别名

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



