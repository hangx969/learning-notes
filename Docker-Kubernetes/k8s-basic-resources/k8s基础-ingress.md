# Ingress和 Ingress Controller概述

## OSI七层模型

![image-20231209104609983](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202312091046041.png)

## 四层代理-service

- 如何把这个动态的Pod IP暴露出去？借助 Service，Service可以以标签的形式选定一组带有指定标签的Pod，并监控和自动负载他们的Pod IP，向外暴露只暴露Service IP就行了；这就是NodePort模式：即在每个节点上开起一个端口，然后转发到内部Pod IP 上。

- 如果Service想要被k8s集群外部访问，需要用NodePort类型，但是NodePort类型的svc有如下几个问题：
  - nodeport会在物理机映射一个端口，绑定到物理机上，这样就导致每个服务都要映射一个端口，端口过多，维护困难。
  - 还有Service底层使用的是iptables或者ipvs，仅支持四层代理，无法基于https协议做代理。
  - 实际使用中，一般用域名，根据不同域名跳转到不同端口服务中。

## 四层vs七层代理

1. 四层负载：四层的负载均衡就是基于`IP+端口`的负载均衡：在三层负载均衡的基础上，通过发布三层的IP地址（VIP），然后加四层的端口号，来决定哪些流量需要做负载均衡，对需要处理的流量进行NAT处理，转发至后台服务器，并记录下这个TCP或者UDP的流量是由哪台服务器处理的，后续这个连接的所有流量都同样转发到同一台服务器处理。

2. 七层的负载均衡就是基于虚拟的URL或主机IP的负载均衡：在四层负载均衡的基础上（没有四层是绝对不可能有七层的），再考虑应用层的特征，比如同一个Web服务器的负载均衡，除了根据VIP加80端口辨别是否需要处理的流量，还可根据七层的URL、浏览器类别、语言来决定是否要进行负载均衡。举个例子，如果你的Web服务器分成两组，一组是中文语言的，一组是英文语言的，那么七层负载均衡就可以当用户来访问你的域名时，自动辨别用户语言，然后选择对应的语言服务器组进行负载均衡处理。

3. 四层负载均衡工作在传输层，七层负载均衡工作在应用层

## Ingress

- Ingress官网定义：Ingress提供了一个统一的入口，可以把进入到集群的请求转发到集群中的一些服务上，从而可以把服务映射到集群外部。Ingress 能把集群内Service 配置成外网能够访问的 URL，流量负载均衡，提供基于域名访问的虚拟主机等。
- Ingress 是k8s中的资源，主要是管理ingress-controller这个代理的配置文件。件通过它定义某个域名的请求过来之后转发到集群中指定的 Service。它可以通过 Yaml 文件定义，可以给一个或多个 Service 定义一个或多个 Ingress 规则。

![image-20240725225555680](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202407252255843.png)

## Ingress Controller

- Ingress Controller是一个七层负载均衡调度器，客户端的请求先到达这个七层负载均衡调度器，由七层负载均衡器在反向代理到后端pod，常见的七层负载均衡器有nginx、traefik、HAProxy、Istio（工作在6层）等。
  - 以我们熟悉的nginx为例，假如请求到达nginx，会通过upstream反向代理到后端pod应用，但是后端pod的ip地址是一直在变化的，因此在后端pod前需要加一个service，这个service只是起到分组的作用，那么我们upstream只需要填写service地址即可。
- 简单理解就是封装了nginx/traefik的代理。

## Ingress Controller vs ingress

- 在**ingress**里定义多个映射规则，**ingress controller**监听这些规则，转化为反向代理配置，对外提供服务。
- 核心概念：
  - Ingress：k8s中的一个对象，定义请求是如何转发到svc的规则
  - Ingress controller：具体实现反向代理和负载均衡的程序，解析ingress的规则，根据配置的规则进行转发。实现方式很多，比如可以用nginx等。nginx配置文件一改动，还需要手动reload一下才可以生效。但是如果用ingress-controller封装的nginx，在ingress维护配置，ingress创建好之后，会自动的把配置文件传到ingress-controller这个pod里，会自动进行reload，然后配置就生效了。
- ingress提供了一个统一的路由规则资源，我们只需要维护ingress的规则就行，ingress controller自动翻译成对应的代理的配置文件（比如nginx的nginx.conf）。

## Ingress代理pod的流程

### 流程

1. 部署Ingress controller，我们ingress controller使用的是nginx

2. 创建Pod应用，可以通过控制器创建pod

3. 创建Service，用来分组pod

4. 创建Ingress http，测试通过http访问应用

5. 创建Ingress https，测试通过https访问应用

### 数据流向

使用七层负载均衡调度器ingress controller时，当客户端访问kubernetes集群内部的应用时，数据包走向如下图流程所示：

![image-20231209111616791](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202312091116867.png)

> 注意：上图其实能看出来，svc只是起到了分组的作用，ingress controller里面的nginx通过label直接找到了pod，流量不经过service直接到了pod上！

# 生产环境推荐架构

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202507172346336.png" alt="image-20250717234628958" style="zoom:50%;" />

1. 在生产环境，建议找几个节点，至少2-3个，去独占部署ingress-controller。

   - 独占的node打label(ingress=true)

   - daemonset打nodeSelector：

     ~~~yaml
     nodeSelector:
       kubernetes.io/os: linux
       ingress: "true"
     ~~~

2. ingress-controller作为集群网络入口，也需要把自己暴露到集群外面：

   - 通过NodePort暴露controller是可以的，但是不推荐，因为多走一层service就多一层性能损耗。
   - 推荐的做法是通过`hostNetwork: true`，controller直接在宿主机上监听80和443端口。性能是最好的。
   - daemonset去部署controller，通过daemonset的nodeSelector去部署

3. 前端的网关（F5、阿里云SLB、LVS、HAProxy），配置IP和upstream代理到这几个节点的80和443端口即可。这些网关服务都有健康检查机制。（ingress配的域名要被解析成前端网关的IP，由前端网关转发到ingres-controller，再到pod。这里就涉及到部署external-DNS把集群内的ingress域名通过公有云dns去解析。这样用户浏览器可以直接访问域名）

4. 前端的健康检查功能已经实现，不需要再搞一个keepalived+VIP了。因为VIP同时只能绑在一个节点上，总是只有一个节点再高负载工作。不推荐这种架构。

# Ingress资源



# Ingress灰度发布

## 场景1-基于header/cookie

- 假设线上运行了一套对外提供 7 层服务的 Service A 服务，后来开发了个新版本 Service A’ 想要上线，但又不想直接替换掉原来的 Service A，希望先灰度一小部分用户，等运行一段时间足够稳定了再逐渐全量上线新版本，最后平滑下线旧版本。

- 这个时候就可以利用 Nginx Ingress 基于 Header 或 Cookie 进行流量切分的策略来发布，业务使用 Header 或 Cookie 来标识不同类型的用户，我们通过配置 Ingress 来实现让带有指定 Header 或 Cookie 的请求被转发到新版本，其它的仍然转发到旧版本，从而实现将新版本灰度给部分用户。

  <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202312281017402.png" alt="image-20231228101712175" style="zoom:50%;" />

## 场景2-按比例切分流量

- 假设线上运行了一套对外提供 7 层服务的 Service B 服务，后来修复了一些问题，需要灰度上线一个新版本 Service B’，但又不想直接替换掉原来的 Service B，而是让先切 10% 的流量到新版本，等观察一段时间稳定后再逐渐加大新版本的流量比例直至完全替换旧版本，最后再平滑下线旧版本，从而实现切一定比例的流量给新版本。

  <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202312281018356.png" alt="image-20231228101848227" style="zoom:50%;" />

## 实现方法

- 部署ingress来切分流量，在ingress的metadata.annotations字段中，定义下列annotation，实现流量控制。假设有老版本和Canry

  - nginx.ingress.kubernetes.io/canary-by-header：
    - 基于Request Header的流量切分，适用于灰度发布以及 A/B 测试。当Request Header 设置为 always时，请求将会被一直发送到 Canary 版本；当 Request Header 设置为 never时，请求不会被发送到 Canary 入口。

  - nginx.ingress.kubernetes.io/canary-by-header-value：
    - 要匹配的 Request Header 的值，用于通知 Ingress 将请求路由到 Canary Ingress 中指定的服务。当 Request Header 设置为此值时，它将被路由到 Canary 入口。

  - nginx.ingress.kubernetes.io/canary-weight：
    - 基于服务权重的流量切分，适用于蓝绿部署，权重范围 0 - 100 按百分比将请求路由到 Canary Ingress 中指定的服务。权重为 0 意味着该金丝雀规则不会向 Canary 入口的服务发送任何请求。权重为60意味着60%流量转到canary。权重为 100 意味着所有请求都将被发送到 Canary 入口。

  - nginx.ingress.kubernetes.io/canary-by-cookie：
    - 基于 Cookie 的流量切分，适用于灰度发布与 A/B 测试。用于通知 Ingress 将请求路由到 Canary Ingress 中指定的服务的cookie。当 cookie 值设置为 always时，它将被路由到 Canary 入口；当 cookie 值设置为 never时，请求不会被发送到 Canary 入口。

- 注：以上的annotations是ingress nginx所官方支持的

  [Annotations - Ingress-Nginx Controller (kubernetes.github.io)](https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/annotations/)

> A/B测试：是一种数据驱动的决策制定方式。在A/B测试中，会将用户分为两组，一组使用A版本，一组使用B版本，然后收集用户的反馈，通过数据分析来决定哪个版本更好。A/B测试可以帮助开发者理解哪些改变可以提高用户体验或者达到其他的业务目标。
>
> - 和金丝雀发布（灰度发布）的区别就是灰度发布是从小比例用户使用逐步平滑增加到大比例用户使用新版本。

## Lab

### 搭建v1和v2版本的两个服务

~~~yaml
#v1
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dep-nginx-v1
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
      version: v1
  template:
    metadata:
      labels:
        app: nginx
        version: v1
    spec:
      containers:
      - name: nginx
        image: "openresty/openresty:centos"
        imagePullPolicy: IfNotPresent
        ports:
        - name: http
          protocol: TCP
          containerPort: 80
        volumeMounts:
        - mountPath: /usr/local/openresty/nginx/conf/nginx.conf
          name: config
          subPath: nginx.conf
      volumes:
      - name: config
        configMap:
          name: cm-nginx-v1
---
apiVersion: v1
kind: ConfigMap
metadata:
  labels:
    app: nginx
    version: v1
  name: cm-nginx-v1
data:
  nginx.conf: |-
    worker_processes  1;
    events {
        accept_mutex on;
        multi_accept on;
        use epoll;
        worker_connections  1024;
    }
    http {
        ignore_invalid_headers off;
        server {
            listen 80;
            location / {
                access_by_lua '
                    local header_str = ngx.say("nginx-v1") #指定到根目录的请求返回nginx-v1
                ';
            }
        }
    }
---
apiVersion: v1
kind: Service
metadata:
  name: svc-nginx-v1
spec:
  selector:
    app: nginx
    version: v1
  type: ClusterIP
  ports:
  - port: 80
    protocol: TCP
    name: http
~~~

~~~yaml
#v2
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dep-nginx-v2
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
      version: v2
  template:
    metadata:
      labels:
        app: nginx
        version: v2
    spec:
      containers:
      - name: nginx
        image: "openresty/openresty:centos"
        imagePullPolicy: IfNotPresent
        ports:
        - name: http
          protocol: TCP
          containerPort: 80
        volumeMounts:
        - mountPath: /usr/local/openresty/nginx/conf/nginx.conf #mountPath可以是一个文件
          name: config
          subPath: nginx.conf #用于指定挂载卷中的子路径。可以将卷中的特定目录或文件，而不是整个卷挂载到 Pod 中的容器。
      volumes:
      - name: config
        configMap:
          name: cm-nginx-v2
---
apiVersion: v1
kind: ConfigMap
metadata:
  labels:
    app: nginx
    version: v2
  name: cm-nginx-v2
data:
  nginx.conf: |-
    worker_processes  1;
    events {
        accept_mutex on;
        multi_accept on;
        use epoll;
        worker_connections  1024;
    }
    http {
        ignore_invalid_headers off;
        server {
            listen 80;
            location / {
                access_by_lua '
                    local header_str = ngx.say("nginx-v2") #指定根目录的url返回nginx-2
                ';
            }
        }
    }
---
apiVersion: v1
kind: Service
metadata:
  name: svc-nginx-v2
spec:
  type: ClusterIP
  ports:
  - port: 80
    protocol: TCP
    name: http
  selector:
    app: nginx
    version: v2
~~~

### 创建ingress

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ing-nginx
spec:
  ingressClassName: nginx
  rules:
  - host: canary.example.com
    http:
      paths:
      - path: /  #配置访问路径，如果通过url进行转发，需要修改；空默认为访问的路径为"/"
        pathType:  Prefix
        backend:  #配置后端服务
         service:
           name: svc-nginx-v1
           port:
            number: 80
~~~

~~~bash
#验证ingress访问后端svc-pod
curl -H "Host: canary.example.com" http://192.168.40.6 #ingress暴露的ip
~~~

### 基于header的流量切分

- 创建 Canary Ingress，指定 v2 版本的后端服务，且加上一些 annotation，实现仅将带有名为 Region 且值为 cd 或 sz 的请求头的请求转发给当前 Canary Ingress，模拟灰度新版本给成都和深圳地域的用户。

- 需要定义新的ingress配置，指定annotation字段。

  ~~~yaml
  apiVersion: networking.k8s.io/v1
  kind: Ingress
  metadata:
    name: ing-nginx-canary
    annotations:
      nginx.ingress.kubernetes.io/canary: "true"
      nginx.ingress.kubernetes.io/canary-by-header: "Region"
      nginx.ingress.kubernetes.io/canary-by-header-pattern: "cd|sz"
  spec:
    ingressClassName: nginx
    rules:
    - host: canary.example.com
      http:
        paths:
        - path: /  #配置访问路径，如果通过url进行转发，需要修改；空默认为访问的路径为"/"
          pathType:  Prefix
          backend:  #配置后端服务
           service:
             name: svc-nginx-v2
             port:
              number: 80
  ~~~

  ~~~bash
  #测试模拟带header的请求
  curl -H "Host: canary.example.com" -H "Region: cd" http://192.168.40.6
  curl -H "Host: canary.example.com" -H "Region: sz" http://192.168.40.6
  curl -H "Host: canary.example.com" http://192.168.40.6
  #可以看到，只有header带了Region并且值为cd | sz代理到v2
  ~~~

### 基于cookie的流量切分

- 与前面 Header 类似，不过使用 Cookie 就无法自定义 value 了（带了某种cookie就会被路由到canary版本）。

- 这里以模拟灰度成都地域用户为例，仅将带有名为 user_from_cd 的 cookie 的请求转发给当前 Canary Ingress 。

- 需要定义新的ingress配置，指定annotation字段。

  ~~~yaml
  apiVersion: networking.k8s.io/v1
  kind: Ingress
  metadata:
    annotations:
      nginx.ingress.kubernetes.io/canary: "true"
      nginx.ingress.kubernetes.io/canary-by-cookie: "user_from_cd"
    name: ing-nginx-canary
  spec:
    ingressClassName: nginx
    rules:
    - host: canary.example.com
      http:
        paths:
        - path: /  #配置访问路径，如果通过url进行转发，需要修改；空默认为访问的路径为"/"
          pathType:  Prefix
          backend:  #配置后端服务
           service:
             name: svc-nginx-v2
             port:
              number: 80
  ~~~

  ~~~bash
  #测试带cookie的请求
  curl -s -H "Host: canary.example.com" --cookie "user_from_cd=always" http://192.168.40.6
  curl -s -H "Host: canary.example.com" --cookie "user_from_bj=always" http://192.168.40.6
  ~~~

### 基于服务权重的流量切分

- 直接定义需要导入的流量比例，这里以导入 10% 流量到 v2 版本为例。

- 需要定义新的ingress配置，在annotation中指定。

  ~~~yaml
  apiVersion: networking.k8s.io/v1
  kind: Ingress
  metadata:
    annotations:
      nginx.ingress.kubernetes.io/canary: "true"
      nginx.ingress.kubernetes.io/canary-weight: "10"
    name: ing-nginx-canary
  spec:
    ingressClassName: nginx
    rules:
    - host: canary.example.com
      http:
        paths:
        - path: /  #配置访问路径，如果通过url进行转发，需要修改；空默认为访问的路径为"/"
          pathType:  Prefix
          backend:  #配置后端服务
           service:
             name: svc-nginx-v2
             port:
              number: 80
  ~~~

  ~~~bash
  #测试比例
  for i in {1..20}; do curl -H "Host: canary.example.com" http://192.168.40.6; done;
  ~~~

# 集群中搭建多套ingress-controller

- ingress可以简单理解为service的service，他通过独立的ingress对象来制定请求转发的规则，把请求路由到一个或多个service中。这样就把服务与请求规则解耦了，可以从业务维度统一考虑业务的暴露，而不用为每个service单独考虑。

- 为了满足多租户场景，需要在k8s集群部署多个ingress-controller，给不同用户不同环境使用。

  主要参数设置：

  ~~~yaml
  containers:
    - name: nginx-ingress-controller
      image: registry.cn-hangzhou.aliyuncs.com/google_containers/nginx-ingress-controller:v1.1.0
      args:
      - /nginx-ingress-controller
      - --ingress-class=ngx-ds
  #注意：--ingress-class设置该Ingress Controller可监听的目标Ingress Class标识；
  #注意：同一个集群中不同套Ingress Controller监听的Ingress Class标识必须唯一，且不能设置为nginx关键字（其是集群默认Ingress Controller的监听标识）
  ~~~

- 创建ingress规则的时候，指定ingress class

  ~~~yaml
  apiVersion: networking.k8s.io/v1
  kind: Ingress
  metadata:
    name: ingress-myapp
    namespace: default
  spec:
    ingressClassName: ngx-ds
    rules:
    - host: tomcat.lucky.com
      http:
        paths:
        - path: /
          pathType:  Prefix
          backend:
           service:
             name: tomcat
             port:
              number: 8080
  ~~~

# ingress-nginx高并发优化

1. 大量请求涌入导致负载过高，影响请求的响应速度和稳定性。
2. 由于大量请求需要处理，可能会导致nginx-ingress-controller的资源（CPU、内存等）耗尽，从而导
   致服务崩溃。
3. 高并发场景下的负载均衡器需要快速且准确地将请求分配给后端服务，否则会影响响应速度和服务可用性

因此，需要对nginx-ingress-controller进行优化以提高其处理高并发请求的能力:

1. 修改ConfigMap，调整worker进程数和每个进程的最大连接数来优化性能。

~~~sh
#可以在nginx-ingress-controller的ConfigMap中增加“worker-processes”和“worker-connections”字段，分别表示worker进程数和每个进程的最大连接数。
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-ingress-controller
data:
  worker-processes: "4" # worker_processes是Nginx服务器进程的数量，通常将其设置为服务器上可用的CPU核心数量-1。
  worker-connections: "1024" # worker_connections是每个工作进程（worker process）可以同时处理的最大连接数，这个值应该根据服务器资源以及预期的并发量来设置。通常的建议是将它设置为1024或更高，但实际上需要根据实际情况进行调整。
~~~

- 例如，如果你有4个CPU核心，可以将worker_processes设置为3。如果你预计每个连接将占用2MB内存，而服务器有8GB的内存，则可以将worker_connections设置为较小的值，如1k。如果你有更多的内存可用，或者希望处理更多的并发连接，则可以将其设置为更大的值。
- 备注：如何知道每个连接占用多大内存？
  - 一般来说，HTTP/HTTPS连接使用的内存量通常较小，通常在几百字节到几千字节之间。但是，在高流量情况下，大量连接的累积内存使用量可能很大。
  - 最好的方法是使用监控和性能测试工具来实际测量您的应用程序在给定负载下的内存使用情况，并根据的观察结果来调整worker-processes和worker-connections的值
  - 常用的压测工具：JMeter、Gatling、Vegeta、ab等

2. 开启缓存

- nginx-ingress-controller可以使用缓存来缓存请求的响应，从而减少后端服务器的压力。可以通过以下两种方式开启缓存：

~~~sh
#在nginx-ingress-controller的ConfigMap中增加“proxy-cache-enabled”字段
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-ingress-controller
data:
  proxy-cache-enabled: "true"

#可以在Ingress的Annotations中增加“nginx.ingress.kubernetes.io/proxy-cache: 'on'”来开启缓存。
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: example-ingress
  annotations:
    nginx.ingress.kubernetes.io/proxy-cache: "on"
spec:
  rules:
  - host: example.com
    http:
      paths:
      - path: /test
        pathType: Prefix
        backend:
          service:
            name: test-service
            port:
              name: http
~~~

3. nginx参数优化

- 有一个业务应用部署在kubernetes中，如果将该应用以Kubernetes Service NodePort暴露出来，压测可以发现页面响应性能较高，可以达到10w多的QPS；而将这个Kubernetes用Ingress暴露出来，压测只能响应5w多的QPS了。

- 参考文档:shttps://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/configmap/

~~~sh
#upstream中的keepalive、keepalive_requests、keepalive_timeout这些配置项可以优化下
keep-alive: "100"
keep-alive-requests: "110"
upstream-keepalive-connections: "20000"
upstream-keepalive-requests: "110"
upstream-keepalive-timeout: "100"
#由于Ingress-nginx-controller配置了upstream-keepalive-connections、upstream-keepalive-requests、
#upstream-keepalive-timeout参数，这样nginx->upstream的HTTP处理是启用了Keep-Alive的，这样到Kuberentes Service的TCP连接可以高效地复用，避免了重建连接的开销。
~~~

# 基于nginx+keepalived的Ingress-Controller高可用架构【不推荐】

## 架构示意图

- Ingress Controller是集群流量的接入层，对它做高可用非常重要，可以基于keepalive实现nginx-ingress-controller高可用，具体实现如下：

  - Ingress-controller根据Deployment+ nodeSeletor+pod反亲和性方式部署在k8s指定的两个work节点

  - nginx-ingress-controller这个pod共享宿主机ip，然后通过keepalive+nginx实现nginx-ingress-controller高可用

    ![image-20231209114749417](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202312091147480.png)

## Lab - 搭建高可用架构

### 解压镜像

~~~bash
#解压课件镜像到工作节点，ctr解压
ctr -n=k8s.io images import ingress-nginx-controllerv1.1.0.tar.gz
ctr -n=k8s.io images import kube-webhook-certgen-v1.1.0.tar.gz
~~~

### 部署 ingress-controller

> 注意：k8s官方维护的叫`ingress-nginx`，nginx维护的叫`nginx-ingress`

- nginx-ingress-controller是以pod形式部署，demo的yaml文件从github下载：

  https://github.com/kubernetes/ingress-nginx/tree/main/deploy/static/provider/baremetal

  (不做高可用的话直接在这里下载apply就行)

- 但是这里为了做成高可用的nginx-ingress-controller，添加了反亲和性，对原始的yaml做了调整，yaml如下：

~~~yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ingress-nginx
  labels:
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx

---
# Source: ingress-nginx/templates/controller-serviceaccount.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  labels:
    helm.sh/chart: ingress-nginx-4.0.10
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/version: 1.1.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: controller
  name: ingress-nginx
  namespace: ingress-nginx
automountServiceAccountToken: true
---
# Source: ingress-nginx/templates/controller-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  labels:
    helm.sh/chart: ingress-nginx-4.0.10
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/version: 1.1.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: controller
  name: ingress-nginx-controller
  namespace: ingress-nginx
data:
  allow-snippet-annotations: 'true'
---
# Source: ingress-nginx/templates/clusterrole.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  labels:
    helm.sh/chart: ingress-nginx-4.0.10
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/version: 1.1.0
    app.kubernetes.io/managed-by: Helm
  name: ingress-nginx
rules:
  - apiGroups:
      - ''
    resources:
      - configmaps
      - endpoints
      - nodes
      - pods
      - secrets
      - namespaces
    verbs:
      - list
      - watch
  - apiGroups:
      - ''
    resources:
      - nodes
    verbs:
      - get
  - apiGroups:
      - ''
    resources:
      - services
    verbs:
      - get
      - list
      - watch
  - apiGroups:
      - networking.k8s.io
    resources:
      - ingresses
    verbs:
      - get
      - list
      - watch
  - apiGroups:
      - ''
    resources:
      - events
    verbs:
      - create
      - patch
  - apiGroups:
      - networking.k8s.io
    resources:
      - ingresses/status
    verbs:
      - update
  - apiGroups:
      - networking.k8s.io
    resources:
      - ingressclasses
    verbs:
      - get
      - list
      - watch
---
# Source: ingress-nginx/templates/clusterrolebinding.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  labels:
    helm.sh/chart: ingress-nginx-4.0.10
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/version: 1.1.0
    app.kubernetes.io/managed-by: Helm
  name: ingress-nginx
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: ingress-nginx
subjects:
  - kind: ServiceAccount
    name: ingress-nginx
    namespace: ingress-nginx
---
# Source: ingress-nginx/templates/controller-role.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  labels:
    helm.sh/chart: ingress-nginx-4.0.10
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/version: 1.1.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: controller
  name: ingress-nginx
  namespace: ingress-nginx
rules:
  - apiGroups:
      - ''
    resources:
      - namespaces
    verbs:
      - get
  - apiGroups:
      - ''
    resources:
      - configmaps
      - pods
      - secrets
      - endpoints
    verbs:
      - get
      - list
      - watch
  - apiGroups:
      - ''
    resources:
      - services
    verbs:
      - get
      - list
      - watch
  - apiGroups:
      - networking.k8s.io
    resources:
      - ingresses
    verbs:
      - get
      - list
      - watch
  - apiGroups:
      - networking.k8s.io
    resources:
      - ingresses/status
    verbs:
      - update
  - apiGroups:
      - networking.k8s.io
    resources:
      - ingressclasses
    verbs:
      - get
      - list
      - watch
  - apiGroups:
      - ''
    resources:
      - configmaps
    resourceNames:
      - ingress-controller-leader
    verbs:
      - get
      - update
  - apiGroups:
      - ''
    resources:
      - configmaps
    verbs:
      - create
  - apiGroups:
      - ''
    resources:
      - events
    verbs:
      - create
      - patch
---
# Source: ingress-nginx/templates/controller-rolebinding.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  labels:
    helm.sh/chart: ingress-nginx-4.0.10
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/version: 1.1.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: controller
  name: ingress-nginx
  namespace: ingress-nginx
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: ingress-nginx
subjects:
  - kind: ServiceAccount
    name: ingress-nginx
    namespace: ingress-nginx
---
# Source: ingress-nginx/templates/controller-service-webhook.yaml
apiVersion: v1
kind: Service
metadata:
  labels:
    helm.sh/chart: ingress-nginx-4.0.10
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/version: 1.1.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: controller
  name: ingress-nginx-controller-admission
  namespace: ingress-nginx
spec:
  type: ClusterIP
  ports:
    - name: https-webhook
      port: 443
      targetPort: webhook
      appProtocol: https
  selector:
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/component: controller
---
# Source: ingress-nginx/templates/controller-service.yaml
apiVersion: v1
kind: Service
metadata:
  annotations:
  labels:
    helm.sh/chart: ingress-nginx-4.0.10
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/version: 1.1.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: controller
  name: ingress-nginx-controller
  namespace: ingress-nginx
spec:
  type: NodePort
  ipFamilyPolicy: SingleStack
  ipFamilies:
    - IPv4
  ports:
    - name: http
      port: 80
      protocol: TCP
      targetPort: http
      appProtocol: http
    - name: https
      port: 443
      protocol: TCP
      targetPort: https
      appProtocol: https
  selector:
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/component: controller
---
# Source: ingress-nginx/templates/controller-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    helm.sh/chart: ingress-nginx-4.0.10
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/version: 1.1.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: controller
  name: ingress-nginx-controller
  namespace: ingress-nginx
spec:
  replicas: 2
  selector:
    matchLabels:
      app.kubernetes.io/name: ingress-nginx
      app.kubernetes.io/instance: ingress-nginx
      app.kubernetes.io/component: controller
  revisionHistoryLimit: 10
  minReadySeconds: 0
  template:
    metadata:
      labels:
        app.kubernetes.io/name: ingress-nginx
        app.kubernetes.io/instance: ingress-nginx
        app.kubernetes.io/component: controller
    spec:
      hostNetwork: true
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchLabels:
                  app.kubernetes.io/name: ingress-nginx
              topologyKey: kubernetes.io/hostname
      dnsPolicy: ClusterFirstWithHostNet
      containers:
        - name: controller
          image: registry.cn-hangzhou.aliyuncs.com/google_containers/nginx-ingress-controller:v1.1.0
          imagePullPolicy: IfNotPresent
          lifecycle:
            preStop:
              exec:
                command:
                  - /wait-shutdown
          args:
            - /nginx-ingress-controller
            - --election-id=ingress-controller-leader
            - --controller-class=k8s.io/ingress-nginx
            - --configmap=$(POD_NAMESPACE)/ingress-nginx-controller
            - --validating-webhook=:8443
            - --validating-webhook-certificate=/usr/local/certificates/cert
            - --validating-webhook-key=/usr/local/certificates/key
          securityContext:
            capabilities:
              drop:
                - ALL
              add:
                - NET_BIND_SERVICE
            runAsUser: 101
            allowPrivilegeEscalation: true
          env:
            - name: POD_NAME
              valueFrom:
                fieldRef:
                  fieldPath: metadata.name
            - name: POD_NAMESPACE
              valueFrom:
                fieldRef:
                  fieldPath: metadata.namespace
            - name: LD_PRELOAD
              value: /usr/local/lib/libmimalloc.so
          livenessProbe:
            failureThreshold: 5
            httpGet:
              path: /healthz
              port: 10254
              scheme: HTTP
            initialDelaySeconds: 10
            periodSeconds: 10
            successThreshold: 1
            timeoutSeconds: 1
          readinessProbe:
            failureThreshold: 3
            httpGet:
              path: /healthz
              port: 10254
              scheme: HTTP
            initialDelaySeconds: 10
            periodSeconds: 10
            successThreshold: 1
            timeoutSeconds: 1
          ports:
            - name: http
              containerPort: 80
              protocol: TCP
            - name: https
              containerPort: 443
              protocol: TCP
            - name: webhook
              containerPort: 8443
              protocol: TCP
          volumeMounts:
            - name: webhook-cert
              mountPath: /usr/local/certificates/
              readOnly: true
          resources:
            requests:
              cpu: 100m
              memory: 90Mi
      nodeSelector:
        kubernetes.io/os: linux
      serviceAccountName: ingress-nginx
      terminationGracePeriodSeconds: 300
      volumes:
        - name: webhook-cert
          secret:
            secretName: ingress-nginx-admission
---
# Source: ingress-nginx/templates/controller-ingressclass.yaml
# We don't support namespaced ingressClass yet
# So a ClusterRole and a ClusterRoleBinding is required
apiVersion: networking.k8s.io/v1
kind: IngressClass
metadata:
  labels:
    helm.sh/chart: ingress-nginx-4.0.10
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/version: 1.1.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: controller
  name: nginx
  namespace: ingress-nginx
spec:
  controller: k8s.io/ingress-nginx
---
# Source: ingress-nginx/templates/admission-webhooks/validating-webhook.yaml
# before changing this value, check the required kubernetes version
# https://kubernetes.io/docs/reference/access-authn-authz/extensible-admission-controllers/#prerequisites
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  labels:
    helm.sh/chart: ingress-nginx-4.0.10
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/version: 1.1.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: admission-webhook
  name: ingress-nginx-admission
webhooks:
  - name: validate.nginx.ingress.kubernetes.io
    matchPolicy: Equivalent
    rules:
      - apiGroups:
          - networking.k8s.io
        apiVersions:
          - v1
        operations:
          - CREATE
          - UPDATE
        resources:
          - ingresses
    failurePolicy: Fail
    sideEffects: None
    admissionReviewVersions:
      - v1
    clientConfig:
      service:
        namespace: ingress-nginx
        name: ingress-nginx-controller-admission
        path: /networking/v1/ingresses
---
# Source: ingress-nginx/templates/admission-webhooks/job-patch/serviceaccount.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ingress-nginx-admission
  namespace: ingress-nginx
  annotations:
    helm.sh/hook: pre-install,pre-upgrade,post-install,post-upgrade
    helm.sh/hook-delete-policy: before-hook-creation,hook-succeeded
  labels:
    helm.sh/chart: ingress-nginx-4.0.10
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/version: 1.1.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: admission-webhook
---
# Source: ingress-nginx/templates/admission-webhooks/job-patch/clusterrole.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: ingress-nginx-admission
  annotations:
    helm.sh/hook: pre-install,pre-upgrade,post-install,post-upgrade
    helm.sh/hook-delete-policy: before-hook-creation,hook-succeeded
  labels:
    helm.sh/chart: ingress-nginx-4.0.10
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/version: 1.1.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: admission-webhook
rules:
  - apiGroups:
      - admissionregistration.k8s.io
    resources:
      - validatingwebhookconfigurations
    verbs:
      - get
      - update
---
# Source: ingress-nginx/templates/admission-webhooks/job-patch/clusterrolebinding.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: ingress-nginx-admission
  annotations:
    helm.sh/hook: pre-install,pre-upgrade,post-install,post-upgrade
    helm.sh/hook-delete-policy: before-hook-creation,hook-succeeded
  labels:
    helm.sh/chart: ingress-nginx-4.0.10
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/version: 1.1.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: admission-webhook
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: ingress-nginx-admission
subjects:
  - kind: ServiceAccount
    name: ingress-nginx-admission
    namespace: ingress-nginx
---
# Source: ingress-nginx/templates/admission-webhooks/job-patch/role.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: ingress-nginx-admission
  namespace: ingress-nginx
  annotations:
    helm.sh/hook: pre-install,pre-upgrade,post-install,post-upgrade
    helm.sh/hook-delete-policy: before-hook-creation,hook-succeeded
  labels:
    helm.sh/chart: ingress-nginx-4.0.10
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/version: 1.1.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: admission-webhook
rules:
  - apiGroups:
      - ''
    resources:
      - secrets
    verbs:
      - get
      - create
---
# Source: ingress-nginx/templates/admission-webhooks/job-patch/rolebinding.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: ingress-nginx-admission
  namespace: ingress-nginx
  annotations:
    helm.sh/hook: pre-install,pre-upgrade,post-install,post-upgrade
    helm.sh/hook-delete-policy: before-hook-creation,hook-succeeded
  labels:
    helm.sh/chart: ingress-nginx-4.0.10
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/version: 1.1.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: admission-webhook
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: ingress-nginx-admission
subjects:
  - kind: ServiceAccount
    name: ingress-nginx-admission
    namespace: ingress-nginx
---
# Source: ingress-nginx/templates/admission-webhooks/job-patch/job-createSecret.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: ingress-nginx-admission-create
  namespace: ingress-nginx
  annotations:
    helm.sh/hook: pre-install,pre-upgrade
    helm.sh/hook-delete-policy: before-hook-creation,hook-succeeded
  labels:
    helm.sh/chart: ingress-nginx-4.0.10
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/version: 1.1.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: admission-webhook
spec:
  template:
    metadata:
      name: ingress-nginx-admission-create
      labels:
        helm.sh/chart: ingress-nginx-4.0.10
        app.kubernetes.io/name: ingress-nginx
        app.kubernetes.io/instance: ingress-nginx
        app.kubernetes.io/version: 1.1.0
        app.kubernetes.io/managed-by: Helm
        app.kubernetes.io/component: admission-webhook
    spec:
      containers:
        - name: create
          image: registry.cn-hangzhou.aliyuncs.com/google_containers/kube-webhook-certgen:v1.1.1
          imagePullPolicy: IfNotPresent
          args:
            - create
            - --host=ingress-nginx-controller-admission,ingress-nginx-controller-admission.$(POD_NAMESPACE).svc
            - --namespace=$(POD_NAMESPACE)
            - --secret-name=ingress-nginx-admission
          env:
            - name: POD_NAMESPACE
              valueFrom:
                fieldRef:
                  fieldPath: metadata.namespace
          securityContext:
            allowPrivilegeEscalation: false
      restartPolicy: OnFailure
      serviceAccountName: ingress-nginx-admission
      nodeSelector:
        kubernetes.io/os: linux
      securityContext:
        runAsNonRoot: true
        runAsUser: 2000
---
# Source: ingress-nginx/templates/admission-webhooks/job-patch/job-patchWebhook.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: ingress-nginx-admission-patch
  namespace: ingress-nginx
  annotations:
    helm.sh/hook: post-install,post-upgrade
    helm.sh/hook-delete-policy: before-hook-creation,hook-succeeded
  labels:
    helm.sh/chart: ingress-nginx-4.0.10
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/version: 1.1.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: admission-webhook
spec:
  template:
    metadata:
      name: ingress-nginx-admission-patch
      labels:
        helm.sh/chart: ingress-nginx-4.0.10
        app.kubernetes.io/name: ingress-nginx
        app.kubernetes.io/instance: ingress-nginx
        app.kubernetes.io/version: 1.1.0
        app.kubernetes.io/managed-by: Helm
        app.kubernetes.io/component: admission-webhook
    spec:
      containers:
        - name: patch
          image: registry.cn-hangzhou.aliyuncs.com/google_containers/kube-webhook-certgen:v1.1.1
          imagePullPolicy: IfNotPresent
          args:
            - patch
            - --webhook-name=ingress-nginx-admission
            - --namespace=$(POD_NAMESPACE)
            - --patch-mutating=false
            - --secret-name=ingress-nginx-admission
            - --patch-failure-policy=Fail
          env:
            - name: POD_NAMESPACE
              valueFrom:
                fieldRef:
                  fieldPath: metadata.namespace
          securityContext:
            allowPrivilegeEscalation: false
      restartPolicy: OnFailure
      serviceAccountName: ingress-nginx-admission
      nodeSelector:
        kubernetes.io/os: linux
      securityContext:
        runAsNonRoot: true
        runAsUser: 2000
~~~

- 部署完会在两个worker node上建出来两个pod：ingress-nginx-controller-64bdc78c96-8t25x
- ingress-nginx-admission-create-2qqzl和ingress-nginx-admission-patch-8nzwm是生成证书用的两个一次性pod

> - 如果部署完ingress，访问ingress的80端口被拒绝，原因一般是： ingress-controller的官方yaml默认注释了hostNetwork 工作方式，以防止端口的在宿主机的冲突，没有绑定到宿主机 80 端口。需要在ingress-class的deployment.spec.template.spec中加上hostNetwork: true

### 安装配置nginx和keeplived

~~~bash
#两个工作节点上安装
yum install  epel-release  nginx keepalived nginx-mod-stream  -y
~~~

~~~bash
#修改nginx配置文件，nginx监听30080端口
vim /etc/nginx/nginx.conf
chmod o+w nginx.conf #vscode加上w权限才能编辑器里面保存

user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /run/nginx.pid;

include /usr/share/nginx/modules/*.conf;

events {
    worker_connections 1024;
}

stream {

    log_format  main  '$remote_addr $upstream_addr - [$time_local] $status $upstream_bytes_sent';

    access_log  /var/log/nginx/k8s-access.log  main;

    upstream k8s-ingress-controller {
       server 192.168.40.5:80 weight=5 max_fails=3 fail_timeout=30s;   # node-01 IP:PORT
       server 192.168.40.6:80 weight=5 max_fails=3 fail_timeout=30s;  # node-02 IP:PORT
    }
    
    server {
       listen 30080; 
       proxy_pass k8s-ingress-controller;
    }
}

http {
    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile            on;
    tcp_nopush          on;
    tcp_nodelay         on;
    keepalive_timeout   65;
    types_hash_max_size 2048;

    include             /etc/nginx/mime.types;
    default_type        application/octet-stream;

}

#备注：
#server 反向服务地址和端口
#weight 权重
#max_fails 失败多少次，认为主机已挂掉，则踢出
#fail_timeout 踢出后重新探测时间
#注意：nginx监听端口变成大于30000的端口，比方说30080,这样访问域名:30080就可以了，必须是满足大于30000以上，才能代理ingress-controller
~~~

~~~bash
#主keepalived，暴露VIP 192.168.40.8
vim /etc/keepalived/keepalived.conf

global_defs { 
   notification_email { 
     acassen@firewall.loc 
     failover@firewall.loc 
     sysadmin@firewall.loc 
   } 
   notification_email_from Alexandre.Cassen@firewall.loc  
   smtp_server 127.0.0.1 
   smtp_connect_timeout 30 
   router_id NGINX_MASTER
} 

vrrp_script check_nginx {
    script "/etc/keepalived/check_nginx.sh"
}

vrrp_instance VI_1 { 
    state MASTER 
    interface eth0  # 修改为实际网卡名
    virtual_router_id 51 # VRRP 路由 ID实例，每个实例是唯一的 
    priority 100    # 优先级，备服务器设置 90 
    advert_int 1    # 指定VRRP 心跳包通告间隔时间，默认1秒 
    authentication { 
        auth_type PASS      
        auth_pass 1111 
    }  
    # 虚拟IP,要跟VM在一个网段
    virtual_ipaddress { 
        192.168.40.8/24
    } 
    track_script {
        check_nginx
    } 
}
#vrrp_script：指定检查nginx工作状态脚本（根据nginx状态判断是否故障转移）
#virtual_ipaddress：虚拟IP（VIP）
~~~

~~~bash
#备keepalived
vim /etc/keepalived/keepalived.conf

global_defs { 
   notification_email { 
     acassen@firewall.loc 
     failover@firewall.loc 
     sysadmin@firewall.loc 
   } 
   notification_email_from Alexandre.Cassen@firewall.loc  
   smtp_server 127.0.0.1 
   smtp_connect_timeout 30 
   router_id NGINX_MASTER
} 

vrrp_script check_nginx {
    script "/etc/keepalived/check_nginx.sh"
}

vrrp_instance VI_1 { 
    state BACKUP 
    interface eth0  # 修改为实际网卡名
    virtual_router_id 51 # VRRP 路由 ID实例，每个实例是唯一的 
    priority 90    # 优先级，备服务器设置 90 
    advert_int 1    # 指定VRRP 心跳包通告间隔时间，默认1秒 
    authentication { 
        auth_type PASS      
        auth_pass 1111 
    }  
    # 虚拟IP,要跟VM在一个网段
    virtual_ipaddress { 
        192.168.40.8/24
    } 
    track_script {
        check_nginx
    } 
}
#vrrp_script：指定检查nginx工作状态脚本（根据nginx状态判断是否故障转移）
#virtual_ipaddress：虚拟IP（VIP）
~~~

- 访问keepalived VIP + 30080端口 ==> 请求代理给了网卡eth0的30080端口 ==> nginx在监听 ==> 继续代理给upstream定义的两个node的80端口 ==> 两个ingress controller的nginx会监听node的80端口 ==> nginx转发给upstream的svc的8080端口 ==> svc转发给后端pod

### nginx存活脚本

- \#注：keepalived根据脚本返回状态码（0为工作正常，非0不正常）判断是否故障转移。

~~~bash
#!/bin/bash
#1、判断Nginx是否存活
counter=$(ps -ef |grep nginx | grep sbin | egrep -cv "grep|$$" )
if [ $counter -eq 0 ]; then
    #2、如果不存活则尝试启动Nginx
    service nginx start
    sleep 2
    #3、等待2秒后再次获取一次Nginx状态
    counter=$(ps -ef |grep nginx | grep sbin | egrep -cv "grep|$$" )
    #4、再次进行判断，如Nginx还不存活则停止Keepalived，让地址进行漂移
    if [ $counter -eq 0 ]; then
        service  keepalived stop
    fi
fi
~~~

~~~sh
chmod +x /etc/keepalived/check_nginx.sh
~~~

### 启动服务

~~~bash
systemctl daemon-reload
systemctl enable nginx keepalived
systemctl start nginx
systemctl start keepalived
~~~

> `systemctl daemon-reload`命令用于重新加载systemd管理器配置。这包括重新加载所有的systemd服务单元。当你修改了任何systemd服务单元的配置文件后，例如`/etc/systemd/system/`目录下的文件，你需要运行这个命令来使改动生效。

# Lab - 部署ingress

## 部署后端svc和pod

~~~yaml
apiVersion: v1
kind: Service
metadata:
  name: svc-tomcat
  namespace: default
spec:
  selector:
    app: tomcat
    release: canary
  ports:
  - name: http
    targetPort: 8080
    port: 8080 #svc暴露这个8080是给外部通信用的
  - name: ajp
    targetPort: 8009
    port: 8009 #8009是给内部通信用的
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: deploy-tomcat
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
        imagePullPolicy: IfNotPresent  
        ports:
        - name: http
          containerPort: 8080
          name: ajp
          containerPort: 8009
~~~

## 部署ingress

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-tomcat
  namespace: default
  #1.23的k8s，需要在annotations: kubernetes.io/ingress.class: "nginx"指定是关联到哪个ingress controller上面去
  #1.25以上的k8s，在spec中，ingressClassName中指定
spec:
  ingressClassName: nginx
  rules:
  - host: tomcat.hanxux.com
    http:
      paths:
      - backend:
          service:
            name: svc-tomcat
            port:
              number: 8080
        path: / #指定路由，这里是根路由
        pathType: Prefix
~~~

## 验证ingress controller配置

~~~bash
k exec -it ingress-nginx-controller-64bdc78c96-mkf2s -n ingress-nginx  -- /bin/sh
cat nginx.conf
#可以看到ingress里面定义的规则，已经定义到ingress controller的nginx规则里面了
server {
                server_name tomcat.hangx.com ;

                listen 80  ;
                listen [::]:80  ;
                listen 443  ssl http2 ;
                listen [::]:443  ssl http2 ;

                set $proxy_upstream_name "-";

                ssl_certificate_by_lua_block {
                        certificate.call()
                }

                location / {

                        set $namespace      "default";
                        set $ingress_name   "ingress-tomcat";
                        set $service_name   "svc-tomcat";
                        set $service_port   "8080";
                        set $location_path  "/";
                        set $global_rate_limit_exceeding n;
                      
~~~

## 访问入口

- Ingress Controller的暴露方式：
  - NodePort
  - HostNetwork
  - LoadBalancer
  - external name
- 如果用的是NodePort暴露的Service，就用宿主机的IP作为入口（ingress controller在node-01上，IP是192.168.40.5）
  - Node IP：ingress controller的NodePort高位端口 ==> ingress controller nginx ==> 代理给svc ==> 代理给后端pod

~~~bash
k get svc -n ingress-nginx
ingress-nginx   ingress-nginx-controller             NodePort    10.105.87.199   <none>        80:31414/TCP,443:31126/TCP   7d19h
~~~

- 示例这里用的Keepalived暴露的VIP作为入口:
  - 访问keepalived VIP + 30080端口 ==> 请求代理给了主node上网卡eth0的30080端口 ==> node上自己装的nginx在监听30080 ==> 继续代理给upstream定义的两个node IP:80端口 ==> 两个ingress controller的nginx会监听node的80端口 ==> nginx转发给upstream的svc的8080端口 ==> svc转发给后端pod
- hostnetwork模式需要显式在ingress controller的deployment上指定hostnetwork=true，然后必须配置hosts文件，让自定义的域名指向ingress的ip，然后根据设定的路由来访问。直接访问ingress的ip是不行的，nginx会报404.

# Lab - 部署ingress HTTPS代理pod

### 构建TLS站点

~~~bash
cd /root/
openssl genrsa -out tls.key 2048 #tls.key是私钥
openssl req -new -x509 -key tls.key -out tls.crt -subj /C=CN/ST=SH/L=SH/O=CKA/CN=hangx.tomcat.com #用私钥签发证书
~~~

### 生成secret

~~~bash
kubectl create secret tls secret-tomcat-ingress --cert=tls.crt --key=tls.key
~~~

### 创建基于https的ingress

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-tomcat-tls
  namespace: default
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    -  hangx.tomcat.com
    secretName: secret-tomcat-ingress
  rules:
  - host: hangx.tomcat.com
    http:
      paths:
      - path: /
        pathType:  Prefix
        backend:
         service:
           name: tomcat
           port:
            number: 8080
~~~

- 后续访问中，如果是采用上述keepalived的方案，就在hosts文件中将VIP对应ingress的hosts。如果没采用keepalived方案，就用ingress controller所在的node IP作为入口。
