# 镜像准备

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
FROM centos:centos7.9.2009 #这里用alpine也可以，后面需要用apt来装软件
#安装wget
RUN yum -y install epel-release.noarch && RUN yum install -y wget
WORKDIR /usr/local/src
#下载并解压源码包
COPY httpd-2.4.54.tar.gz /usr/local/src
RUN tar -zxvf httpd-2.4.54.tar.gz && RUN rm -f httpd-2.4.54.tar.gz #上面设置了WORKDIR，这里就是在/usr/local/src路径下执行了。
WORKDIR httpd-2.4.54
#编译安装apache
RUN yum install -y gcc gcc-c++ make cmake apr-devel apr apr-util apr-util-devel pcre-devel && RUN ./configure --prefix=/usr/local/apache2 --enable-mods-shared=most --enable-so && RUN make && RUN make install
#修改apache配置文件
RUN sed -i 's/#ServerName www.example.com:80/ServerName localhost:80/g' /usr/local/apache2/conf/httpd.conf
#复制服务启动脚本并设置权限
COPY run.sh /usr/local/sbin/run.sh && RUN chmod 755 /usr/local/sbin/run.sh
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

# pod部署

~~~sh
docker save -o apache apache:v1
scp apache node1:/root/
#去工作节点解压
docker load -i apache 
#ctr -n=k8s.io images import apache
~~~

- deployment

~~~yaml
tee pod.yaml <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: apache
  labels:
     app: apache
spec:
  containers:
  - name: apache
    image: apache:v1
    imagePullPolicy: IfNotPresent
EOF
~~~

- service

~~~yaml
tee service.yaml <<'EOF'
apiVersion: v1
kind: Service
metadata:
  name: http-svc
spec:
  selector:
     app: apache
  type: NodePort
  ports:
  - port: 80
    targetPort: 80
    nodePort: 30080
EOF
~~~

