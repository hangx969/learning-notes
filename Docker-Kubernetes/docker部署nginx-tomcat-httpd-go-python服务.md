# docker部署nginx服务

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

# dockerfile构建nginx

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
docker inspect nginx
#宿主机访问nginx页面
curl 10.0.0.4:32773
```

# dockerfile构建tomcat8

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

# dockerfile构建httpd镜像

- httpd镜像可以直接从官网下载：https://httpd.apache.org/download.cgi
- 准备dockerfile

~~~sh
mkdir docker-httpd
cd docker-httpd
#上传httpd镜像

#创建启动脚本
tee run.sh <<'EOF'
#!/bin/bash
/usr/local/apache2/bin/httpd -D FOREGROUND
EOF

#创建dockerfile
tee dockerfile <<'EOF'
FROM centos:centos7.9.2009
#安装wget
RUN yum -y install epel-release.noarch 
RUN yum install -y wget
WORKDIR /usr/local/src
#下载并解压源码包
COPY httpd-2.4.54.tar.gz /usr/local/src
RUN tar -zxvf httpd-2.4.54.tar.gz
WORKDIR httpd-2.4.54
#编译安装apache
RUN yum install -y gcc gcc-c++  make  cmake apr-devel apr apr-util apr-util-devel pcre-devel
RUN ./configure --prefix=/usr/local/apache2 --enable-mods-shared=most --enable-so
RUN make
RUN make install
#修改apache配置文件
RUN sed -i 's/#ServerName www.example.com:80/ServerName localhost:80/g' /usr/local/apache2/conf/httpd.conf
#复制服务启动脚本并设置权限
COPY run.sh /usr/local/sbin/run.sh
RUN chmod 755 /usr/local/sbin/run.sh
#开放80端口
EXPOSE 80
CMD ["/usr/local/sbin/run.sh"]
EOF
~~~

- 制作镜像并运行

~~~sh
docker build -t apache:v1  .
docker run -d -p 2222:22 -p 8000:80 apache:v1
#浏览器访问机器IP:8000端口
~~~

# 基于Go代码构建镜像

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

# 基于python代码构建镜像

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

## 
