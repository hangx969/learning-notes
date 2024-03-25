# 部署Harbor

## 环境规划

| 主机名 | IP            | 配置          | 网络 |
| ------ | ------------- | ------------- | ---- |
| harbor | 172.16.183.74 | 4c/4G/60G硬盘 | NAT  |

## 安装准备

- 更换阿里的yum源 

```sh
mv /etc/yum.repos.d/CentOS-Base.repo  /etc/yum.repos.d/CentOS-Base.repo.backup
wget -O /etc/yum.repos.d/CentOS-Base.repo http://mirrors.aliyun.com/repo/Centos-7.repo
```

- 安装软件包

```sh
yum -y install wget net-tools nfs-utils lrzsz gcc gcc-c++ make cmake libxml2-devel openssl-devel curl curl-devel unzip sudo ntp libaio-devel wget vim ncurses-devel autoconf automake zlib-devel  python-devel epel-release openssh-server socat  ipvsadm conntrack ntpdate yum-utils device-mapper-persistent-data  lvm2
```

- 添加docker软件源 

```sh
yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
```

- 配置防火墙

```sh
systemctl stop firewalld  && systemctl  disable firewalld
```

- 时间同步

```sh
ntpdate cn.pool.ntp.org
#编辑计划任务，每分钟做一次同步
crontab -e
* */1 * * * /usr/sbin/ntpdate   cn.pool.ntp.org
```

- 重启crond服务

```sh
service crond restart
```

- 关闭selinux

```sh
sed -i  's/SELINUX=enforcing/SELINUX=disabled/g' /etc/sysconfig/selinux
sed -i  's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
reboot -f
#注：生产环境不要reboot -f，要正常关机重启
```

- 修改内核参数

```sh
modprobe br_netfilter
tee -a /etc/sysctl.d/k8s.conf <<'EOF'
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
EOF
sysctl --system
```

- 配置hosts文件

  ```sh
  tee -a /etc/hosts <<'EOF'
  172.16.183.74 harbor
  172.16.183.75 master1
  172.16.183.76 node1
  EOF
  #master1和node1添加harbor
  tee -a /etc/hosts <<'EOF'
  172.16.183.74 harbor
  EOF
  ```
  
- 主机间无密码登录

~~~sh
#master1上
cd /root && ssh-keygen -t rsa
ssh-copy-id -i .ssh/id_rsa.pub root@harbor
~~~

## 安装docker 

- 安装

```sh
yum install -y docker-ce-19.03.7-3.el7
systemctl enable docker && systemctl start docker && systemctl status docker
#修改docker配置文件
cat > /etc/docker/daemon.json <<EOF
{
"registry-mirrors":["https://rsbud4vc.mirror.aliyuncs.com","https://registry.docker-cn.com","https://docker.mirrors.ustc.edu.cn","https://dockerhub.azk8s.cn","http://hub-mirror.c.163.com","http://qtid6917.mirror.aliyuncs.com"], 
"insecure-registries":["172.16.183.74"]
}
EOF
systemctl daemon-reload && systemctl restart docker && systemctl status docker
```

- 开启机器的bridge模式

```sh
#永久生效
echo """
vm.swappiness = 0
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
net.bridge.bridge-nf-call-ip6tables = 1
""" > /etc/sysctl.conf
sysctl -p /etc/sysctl.conf
```

## Harbor安装

1. 为harbor创建自签发证书

   ```bash
   mkdir /data/ssl -p
   cd /data/ssl/
   #生成一个3072位的key，也就是私钥
   openssl genrsa -out ca.key 3072
   #生成一个数字证书ca.pem，3650表示证书的有效时间是10年。后续根据ca.pem根证书来签发信任的客户端证书
   openssl req -new -x509 -days 3650 -key ca.key -out ca.pem 
   #生成域名的证书
   #生成一个3072位的key，也就是私钥
   openssl genrsa -out harbor.key  3072
   #生成一个证书请求文件，一会签发证书时需要的。CN写主机名harbor
   openssl req -new -key harbor.key -out harbor.csr
   #签发证书：
   openssl x509 -req -in harbor.csr -CA ca.pem -CAkey ca.key -CAcreateserial -out harbor.pem -days 3650
   #验证证书有效
   openssl x509 -noout -text -in harbor.pem 
   ```

2. 安装harbor

   ```bash
   #创建安装目录
   mkdir /data/install -p
   #安装harbor
   #/data/ssl目录下有如下文件：ca.key  ca.pem  ca.srl  harbor.csr  harbor.key  harbor.pem
   cd /data/install/
   #把harbor的离线包harbor-offline-installer-v2.3.0-rc3.tgz上传到这个目录，离线包在课件里提供了
   #下载harbor离线包的地址：
   #https://github.com/goharbor/harbor
   #解压：
   tar zxvf harbor-offline-installer-v2.3.0-rc3.tgz
   cd harbor
   cp harbor.yml.tmpl harbor.yml 
   
   vim harbor.yml
   #修改配置文件：
   hostname: harbor #修改hostname，跟上面签发的证书域名保持一致
   #协议用https
   certificate: /data/ssl/harbor.pem
   private_key: /data/ssl/harbor.key
   #邮件和ldap不需要配置，在harbor的web界面可以配置，其他配置采用默认即可。
   ```
   
3. 安装docker-compose

   - docker-compose项目是Docker官方的开源项目，负责实现对Docker容器集群的快速编排。Docker-Compose的工程配置文件默认为docker-compose.yml，Docker-Compose运行目录下的必要有一个docker-compose.yml。docker-compose可以管理多个docker实例。

   ```sh
   #配置k8s源
   cat >  /etc/yum.repos.d/kubernetes.repo  <<EOF
   [kubernetes]
   name=Kubernetes
   baseurl=https://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes-el7-x86_64
   enabled=1
   gpgcheck=0
   EOF
   ```

   ```bash
   yum install docker-compose -y
   #安装harbor依赖的的离线镜像包docker-harbor-2-3-0.tar.gz上传到harbor机器解压。docker compose要用
   docker load -i docker-harbor-2-3-0.tar.gz 
   cd /data/install/harbor
   ./install.sh
   #出现✔ ----Harbor has been installed and started successfully.---- 表明安装成功。
   ```
   
4. harbor启动和停止

   ```bash
   #如何停掉harbor：
   cd /data/install/harbor
   docker-compose stop 
   #如何启动harbor：
   sudo su
   cd /data/install/harbor
   docker-compose start
   ```

   #注：harbor默认的账号密码：admin/Harbor12345

5. 图形化界面访问harbor

   - 在C:\Windows\System32\drivers\etc下修改hosts文件，添加 harbor 。浏览器访问：https://harbor/

## harbor私有仓库使用

```bash
#在k8s工作机节点上修改docker镜像源
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
docker login 172.16.183.74
#将本地镜像上传到仓库
docker load -i tomcat.tar.gz
docker tag tomcat:latest  172.16.183.74/test/tomcat:v1
docker push 172.16.183.74/test/tomcat:v1 
#从仓库拉取镜像
docker rmi -f 172.16.183.74/test/tomcat:v1
docker pull 172.16.183.74/test/tomcat:v1
```

# 部署ingress

## ingress介绍

- Ingress官网定义：Ingress可以把进入到集群内部的请求转发到集群中的一些服务上，从而可以把服务映射到集群外部。Ingress 能把集群内Service 配置成外网能够访问的 URL，流量负载均衡，提供基于域名访问的虚拟主机等。

- Ingress简单的理解就是你原来需要改Nginx配置，然后配置各种域名对应哪个 Service，现在把这个动作抽象出来，变成一个 Ingress 对象，你可以用 yaml 创建，每次不要去改Nginx 了，直接改yaml然后创建/更新就行了；那么问题来了：”Nginx 该怎么处理？”

- Ingress Controller 这东西就是解决 “Nginx 的处理方式” 的；Ingress Controller 通过与 Kubernetes API 交互，动态的去感知集群中Ingress规则变化，然后读取他，按照他自己模板生成一段 Nginx 配置，再写到 Nginx Pod 里，最后 reload 一下。

- Ingress Controller是一个七层负载均衡调度器，客户端的请求先到达这个七层负载均衡调度器，由七层负载均衡器在反向代理到后端pod，常见的七层负载均衡器有nginx、traefik。

  - 以我们熟悉的nginx为例，假如请求到达nginx，会通过upstream反向代理到后端pod应用，但是后端pod的ip地址是一直在变化的，因此在后端pod前需要加一个service，这个service只是起到分组的作用，那么我们upstream只需要填写service地址即可。

  ![image-20240325171557723](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202403251716829.png)

## 安装ingress controller

Ingress-controller官网： https://github.com/kubernetes/ingress-nginx/

```sh
#把kube-webhook-certgen-v1.1.1.tar.gz和ingress-nginx-controllerv1.1.1.tar.gz镜像上传到xianchaonode1节点，手动解压镜像：
docker load -i ingress-nginx-controllerv1.1.1.tar.gz
docker load -i kube-webhook-certgen-v1.1.1.tar.gz
```

```sh
#更新yaml文件，下面需要的yaml文件在课件，可上传到xianchaomaster1机器上：
#安装Ingress conrtroller需要的yaml所在的github地址：
#https://github.com/kubernetes/ingress-nginx/blob/main/deploy/static/provider/baremetal/deploy.yaml
kubectl apply -f deploy.yaml
kubectl create clusterrolebinding clusterrolebinding-user-3  --clusterrole=cluster-admin --user=system:serviceaccount:ingress-nginx:ingress-nginx
```

## 测试部署tomcat服务

~~~yaml
apiVersion: v1
kind: Service
metadata:
  name: tomcat
  namespace: default
spec:
  selector:
    app: tomcat
    release: canary
  ports:
  - name: http
    targetPort: 8080
    port: 8080
  - name: ajp
    targetPort: 8009
    port: 8009
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tomcat-deploy
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: tomcat
      release: canary
  template:
    metadata:
      labels:
        app: tomcat
        release: canary
    spec:
      containers:
      - name: tomcat
        image: tomcat:8.5.34-jre8-alpine   
        ports:
        - name: http
          containerPort: 8080
          name: ajp
          containerPort: 8009
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-myapp
  namespace: default
  annotations:
    kubernetes.io/ingress.class: "nginx"
spec:
  rules:  #定义后端转发的规则
  - host: tomcat.lucky.com #通过域名进行转发
    http:
      paths:
      - path: /  #配置访问路径，如果通过url进行转发，需要修改；空默认为访问的路径为"/"
        pathType:  Prefix
        backend:  #配置后端服务
         service:
           name: tomcat
           port:
            number: 8080
~~~

# 微服务介绍

- 微服务是一种软件开发架构模式，用于构建应用程序。它是一种将单个应用程序拆分为一组小型、独立的服务的方法。每个微服务都是一个独立的、可独立部署和扩展的单元，通过轻量级通信机制相互交互。
- 微服务架构的核心思想是将应用程序拆分为一组小型服务，每个服务专注于特定的业务功能。每个微服务都有自己的数据库和业务逻辑，并且可以使用不同的编程语言和技术栈进行开发。这使得团队可以独立地开发、测试、部署和扩展每个微服务，而不会对其他服务产生影响。
- 微服务通过使用轻量级的通信协议（如REST或消息队列）来进行服务之间的通信。这些服务可以在不同的服务器上部署，可以通过API进行交互。由于每个微服务都是独立的，因此可以独立进行水平扩展，以满足高负载和高可用性的需求。

![image-20240325190734586](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202403251907677.png)

## 需要考虑的问题

1. 统一的配置管理中心
   - 服务拆分以后，服务的数量非常多，如果所有的配置都以配置文件的方式放在应用本地的话，非常难以管理，可以想象当有几百上千个进程中有一个配置出现了问题，是很难将它找出来的，因而需要有统一的配置中心，来管理所有的配置，进行统一的配置下发。
   - 在微服务中，配置往往分为几类，一类是几乎不变的配置，这种配置可以直接打在容器镜像里面，第二类是启动时就会确定的配置，这种配置往往通过环境变量，在容器启动的时候传进去，第三类就是统一的配置，需要通过配置中心进行下发，例如在大促的情况下，有些功能需要降级，哪些功能可以降级，哪些功能不能降级，都可以在配置文件中统一配置。
2. 全链路监控
   1. 系统和应用的监控
      - 监控系统和服务的健康状态和性能瓶颈，当系统出现异常的时候，监控系统可以配合告警系统，及时地发现，通知，干预，从而保障系统的顺利运行。
   2. 调用关系的监控
   3. 对代码调用关系进行监控
   4. 日志收集
      - 业务层面、代码层面、系统层面

## 常见微服务框架

1. Spring Cloud：
   - Spring Cloud是基于Java的微服务框架，构建在Spring Framework之上。它提供了一系列工具和库，用于快速开发和部署微服务应用程序。Spring Cloud包括服务注册与发现、负载均衡、断路器、配置管理等功能，如Eureka、Ribbon、Hystrix、Config等。
2. Netflix OSS：
   - Netflix开源了一套用于构建可扩展、高性能微服务的工具集，被广泛应用于微服务架构中。这些工具包括服务注册与发现（Eureka）、负载均衡（Ribbon）、断路器（Hystrix）、网关（Zuul）、分布式跟踪（Zipkin）等。
3. Kubernetes：
   - Kubernetes是一个容器编排平台，也可以用于部署和管理微服务。它提供了强大的容器编排、服务发现、自动伸缩和负载均衡等功能。Kubernetes能够管理和调度微服务的容器实例，并提供故障恢复和自动扩展能力。
4. Service Mesh：
   - Service Mesh是一种用于管理微服务通信的新型架构模式。它通过在微服务之间插入一个专用的代理层，提供了诸如服务发现、负载均衡、安全认证、故障恢复等功能。常见的Service Mesh实现包括Envoy、Linkerd和Istio。

# SpringCloud

## 介绍

- 官网：https://spring.io/projects/spring-cloud/

![](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202403251916020.png)

Spring Cloud是一个开源的、用于构建分布式系统的框架。它基于Spring框架，提供了一套用于开发和管理分布式应用程序的工具和组件。

通俗地说，当我们构建一个大型的软件系统时，通常需要将系统拆分成多个独立的服务，每个服务负责完成特定的功能。这些服务可能需要在不同的计算机或服务器上运行，它们之间需要相互通信和协作。Spring Cloud就是为了简化这个分布式系统的开发和管理而设计的。

Spring Cloud提供了许多有用的功能和组件，包括服务注册与发现、负载均衡、断路器、配置管理、消息总线等。这些功能可以帮助开发人员轻松地构建具有弹性、可伸缩性和高可用性的分布式系统。

其中，服务注册与发现是Spring Cloud的核心特性之一。它允许开发人员注册和发现各个服务的实例，使得服务能够相互发现并进行通信。负载均衡则可以平衡服务之间的请求流量，提高系统的性能和可靠性。断路器模式可以防止服务之间的故障传播，提高系统的稳定性。配置管理则可以集中管理各个服务的配置信息，方便进行动态配置和更新。

开发人员使用SpringCloud的方式：

1. 服务开发：开发人员使用Spring Cloud框架构建各个微服务应用程序。他们可以使用Spring Boot来创建独立的、可运行的微服务应用，并使用Spring Cloud提供的组件和库来处理服务注册与发现、负载均衡、断路器等功能。开发人员可以使用Spring Cloud Netflix、Spring Cloud Alibaba等子项目，根据项目需求选择适合的组件。
2. 服务注册与发现：开发人员使用Spring Cloud提供的服务注册与发现组件，如Eureka或Consul，将各个微服务实例注册到注册中心，并实现服务之间的相互发现。
3. 负载均衡：开发人员可以使用Spring Cloud提供的负载均衡组件，如Ribbon，来平衡微服务实例之间的请求流量，提高系统的性能和可靠性。
4. 断路器：开发人员可以使用Spring Cloud的断路器组件，如Hystrix或Resilience4j，来实现容错和故障保护机制，防止故障的传播并提高系统的稳定性。
5. 配置管理：开发人员可以使用Spring Cloud的配置管理组件，如Spring Cloud Config，将配置信息集中管理，实现动态配置和更新。

运维人员使用Spring Cloud的方式：

1. 部署和管理：运维人员负责将开发人员开发的微服务应用程序部署到适当的环境中，如云服务器或容器平台。他们可以使用Docker、Kubernetes等工具来管理微服务的部署和运行。
2. 监控和日志：运维人员需要监控微服务的运行状态、性能指标和日志信息。Spring Cloud提供了一些监控和管理工具，如Spring Boot Actuator和Spring Cloud Sleuth，可以帮助运维人员监控和管理微服务。
3. 自动化运维：运维人员可以使用Spring Cloud提供的自动化运维工具，如Spring Cloud Data Flow，来管理和监控大规模的微服务应用程序。这些工具可以简化运维任务，提高效率。
4. 故障处理和恢复：运维人员需要处理微服务中可能出现的故障，并采取相应的措施进行恢复。他们可以借助Spring Cloud提供的断路器和容错机制，来处理和隔离故障，保证整个系统的可用性。

## 组件

### Eureka 

- 服务注册发现框架；服务提供者将自己的信息注册到注册中心，而服务消费者则从注册中心获取服务提供者的信息
- 服务提供者被称为服务实例。每个服务实例都会向注册中心注册自己的信息，包括服务名称、IP 地址、端口号等

### Zuul 

- 服务网关，网关是微服务架构中的入口点，它扮演着转发请求、认证授权、负载均衡、缓存等功能的角色。

- Zuul 提供了一个统一的入口点，客户端只需与 Zuul 进行交互，无需关心后端服务的具体地址和细节

  ![image-20240325193754333](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202403251937421.png)

### API Gateway

- Spring Cloud已经放弃Zuul了。现在Spring Cloud中引用的还是Zuul 1.x版本，而这个版本是基于过滤器的，是阻塞IO，不支持长连接，spring官网上也已经没有zuul的组件了，所以介绍SpringCloud原生的网关产品Gateway。Spring Cloud Gateway 在性能和可扩展性方面更加出色。

### SpringCloud Config

- Spring Cloud 提供的一个分布式配置管理工具，用于集中管理和提供应用程序的配置信息。它允许将配置文件存储在配置服务器中，并通过客户端将配置动态地分发给不同的服务实例。
- 组件
  1. 配置服务器（Config Server）：配置服务器是一个独立的组件，用于存储和管理配置文件。它可以从本地文件系统、Git 仓库或其他外部存储中获取配置文件，并提供 REST 接口供客户端访问。
  2. 配置文件：配置文件是应用程序的配置信息，如数据库连接、服务端口、日志级别等。Spring Cloud Config 使用约定的文件命名规则（例如 application.properties 或 application.yml）来标识不同的配置文件。
  3. 配置客户端（Config Client）：配置客户端是服务实例或应用程序，通过向配置服务器发起请求获取自身所需的配置信息。它与配置服务器进行交互，并将配置信息加载到应用程序中。
  4. 配置刷新（Refresh）：配置刷新是指在运行时更新配置信息，而无需重启应用程序。通过发送请求到配置服务器的 /actuator/refresh 端点，可以触发配置的刷新，使客户端重新加载最新的配置。

### Ribbon

- 客户端框架；服务消费者的请求分发到多个服务提供者实例之间，以实现请求的分散和负载均衡。

- 与 Nginx 的关系： Ribbon 和 Nginx 都是常用的负载均衡技术，但它们运行在不同的层级和角色上。

  - Ribbon 是运行在服务消费者端的负载均衡器，它通过在客户端进行负载均衡，在客户端经过一系列算法来均衡调用服务，将请求分发到多个服务提供者实例。

    - 它可以Ribbon 工作时分两步：
      第一步：从Eureka Server中获取服务注册信息列表，它优先选择在同一个 Zone 且负载较少的 Server。
      第二步：根据用户指定的策略，在从Server取到的服务注册列表中选择一个地址，其中Ribbon提供了多种策略，例如轮询、随机等。

    ![image-20240325193442519](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202403251934619.png)

  - Nginx 是一种独立的反向代理服务器，通常部署在服务提供者前面的服务器层。它通过在服务器端进行负载均衡，所有请求统一交给nginx，由nginx实现负载均衡请求转发。将请求转发到后端的多个服务提供者。

### Hystrix

- 服务容错组件；
- 服务雪崩
  - 假设有A、B、C三个服务，服务A --> B --> C，假设服务C因为请求量大，扛不住请求，变得不可用，这样就是积累大量的请求，服务B的请求也会阻塞，会逐渐耗尽线程资源，使得服务B变得不可用，那么服务A在调用服务B就会出现问题，导致服务A也不可用，那么整条链路的服务调用都失败了，我们称之为雪崩。
- 在微服务架构中，在高并发情况下，如果请求数量达到一定极限（可以自己设置阈值），超出了设置的阈值，Hystrix会自动开启服务保护功能，然后通过服务降级的方式返回一个友好的提示给客户端（“当前请求人数多，请稍后重试”等）。假设当10个请求中，有10%失败时，熔断器就会打开，此时再调用此服务，将会直接返回失败，不再调远程服务。直到10s之后，重新检测该触发条件，判断是否把熔断器关闭，或者继续打开。

### Archaius

- 服务配置组件；

### Servo

- Metrics组件；

### Blitz4j

- 日志组件。

### Pinpoint

- 全链路监控组件

## spring cloud与spring boot

Spring Boot用于简化Java应用程序的开发，而Spring Cloud则是在Spring Boot基础上提供了构建分布式系统所需的工具和组件。

Spring Boot为Spring Cloud提供了基础设施和开箱即用的功能，使得Spring Cloud的使用更加便捷和高效。

因此，通常在使用Spring Cloud时会使用Spring Boot作为底层框架。

# SpringCloud项目部署到K8S

## 流程

1. 把Springcloud开发的java代码做到镜像里：可以基于dockerfile文件做镜像
2. 把镜像传到镜像仓库里，比方说harbor私有镜像
3. 创建pod，可以用deployment或者statefulset创建
4. 弄个四层代理Service
5. 搭建七层代理Ingress-nginx-controller
6. 数据持久化：ceph、nfs、云存储
7. 搭建监控系统和日志收集系统：prometheus+alertmagaer+grafana、EFK+logstash+kafka
8. 链路监控：pinpoint、zipkin、skywalking

9. 完善：可以基于Jenkins+k8s构建一个自动化的CICD流水线