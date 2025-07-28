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

3. 前端的网关（F5、阿里云SLB、LVS、HAProxy），配置IP和upstream代理到这几个节点的80和443端口即可。这些网关服务都有健康检查机制，不需要再搞一个keepalived+VIP了。因为VIP同时只能绑在一个节点上，总是只有一个节点再高负载工作。不推荐这种架构。

4. 在测试环境没有前端网关的时候，把ingress域名解析到任一个ingress-controller的节点IP即可（hosts文件手动加解析）。

5. 在生产环境，ingress配的域名要被解析成**前端网关的IP**，由前端网关转发到ingres-controller，再到pod。（这里就涉及到部署external-DNS把集群内的ingress域名通过公有云dns去解析。这样用户浏览器可以直接访问域名）

# Ingress资源

## yaml定义

~~~yaml
apiVersion: networking.k8s.io/v1 # k8s >= 1.22  必须  v1
kind: Ingress
metadata:
  name: nginx-ingress
spec:
  ingressClassName: nginx # 指定该 Ingress 被哪个 Controller 解析
  rules:  # 定义路由匹配规则，可以配置多个
  - host: nginx.test.com  # 定义域名
    http:  
      paths: # 详细的路由配置，可以配置多个
      - path: / # 指定 PATH
        pathType: ImplementationSpecific   # 指定匹配规则
        backend: # 指定该路由的后端
          service:
            name: nginx # 访问nginx.test.com/ 就会代理到这个service的80端口
            port:
              number: 80
  tls: # https配置
  - hosts:
    - nginx.test.com
    secretName: secret-nginx-test-com # 证书的secret存放
~~~

pathType：路径的匹配方式，目前有 ImplementationSpecific、Exact 和 Prefix 方式。

- Exact：精确匹配，比如配置的 path 为/bar，那么/bar/将不能被路由；
- Prefix：前缀匹配，基于以 / 分隔的URL路径。比如 path 为/abc，可以匹配到/abc/bbb等，比较常用的配置；
- ImplementationSpecific：这种类型的路由匹配根据 Ingress Controller 来实现。
  - 可以当做一个单独的类型，也可以当做 Prefix 和 Exact。这取决于controller的具体实现。大部分controller都是按照Prefix来做的。
  - ImplementationSpecific 是 1.18 版本引入 Prefix 和 Exact 的默认配置。

## 配置更改

对于ingress-nginx：

- 更改configMap是全局的ingress更改：[ConfigMap - Ingress-Nginx Controller](https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/configmap/)
- 更改某个ingress的annotations是仅对这一个ingress生效：[Annotations - Ingress-Nginx Controller](https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/annotations/)

## 特殊配置-不配域名发布服务

有些时候可能因为公司确实不支持域名或者内部dns解析，但是还是需要一个统一的入口，可以不配域名，只配path，通过controller IP+path来访问：

~~~yaml
apiVersion: networking.k8s.io/v1 # k8s >= 1.22  必须  v1
kind: Ingress
metadata:
  name: nginx-ingress-no-host
spec:
  ingressClassName: nginx # 指定该 Ingress 被哪个 Controller 解析
  rules:  # 定义路由匹配规则，可以配置多个
  - http:  
      paths: # 详细的路由配置，可以配置多个
      - path: /no-host # 指定 PATH
        pathType: ImplementationSpecific   # 指定匹配规则
        backend: # 指定该路由的后端
          service:
            name: nginx
            port:
              number: 80
~~~

只要域名到了controller，符合path /no-host，就能给转发到后端pod

## 通过https发布服务

一般情况下https证书是要绑定到前端LB网关上，后面到ingress-pod走80端口就行。有些情况下也是需要把证书绑定到ingress-controller上。

由于我们是学习环境，并没有权威证书，所以需要使用 OpenSSL 生成一个测试证书。如果是生产环境，证书为在第三方公司购买的证书，无需自行生成。

生成证书：

~~~sh
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout tls.key -out tls.crt -subj "/CN=nginx.test.com"
kubectl create secret tls ca-secret --cert=tls.crt --key=tls.key  -n study-ingress
~~~

ingress添加tls配置：

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-ingress
  namespace: study-ingress
spec:
  ingressClassName: nginx
  rules:
  - host: nginx.test.com
    http:
      paths:
      - backend:
        service:
          name: nginx
          port:
            number: 80
    path: /
    pathType: ImplementationSpecific
  tls:
    - hosts:
      - nginx.test.com
      secretName: ca-secret
~~~

## 域名添加用户名密码认证

有些开源工具本身不提供密码认证，如果暴露出去会有很大风险，对于这类工具可以使用Nginx 的 basic-auth 设置密码访问，具体方法如下，由于需要使用 htpasswd 工具，所以需要安装httpd：

~~~sh
yum install httpd -y
~~~

使用 htpasswd 创建 foo 用户的密码：

~~~sh
htpasswd -c auth foo
#New password: 
#Re-type new password: 
#Adding password for user foo
cat auth 
#foo:sssssssss
~~~

基于之前创建的密码文件创建 Secret：

~~~sh
kubectl create secret generic basic-auth --from-file=auth -n study-ingress
~~~

创建包含密码认证的 Ingress：

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-with-auth
  namespace: study-ingress
  annotations:
    nginx.ingress.kubernetes.io/auth-realm: Please Input Your Username and Password
    nginx.ingress.kubernetes.io/auth-secret: basic-auth # 在这里指定用户名密码的secret
    nginx.ingress.kubernetes.io/auth-type: basic
spec:
  ingressClassName: nginx
  rules:
  - host: auth.test.com
    path: /
    pathType: ImplementationSpecific
    http:
      paths:
      - backend:
          service:
            name: nginx 
            port:
              number: 80
~~~

## 开启会话保持

和 Nginx 一样，Ingress Nginx 也支持基于 cookie 的会话保持。

首先扩容 nginx 服务至多个副本：

~~~sh
kubectl scale deploy nginx --replicas=3 -n study-ingress
~~~

未开启会话保持，同一个主机访问可以看到流量会在三个副本中都有。

通过以下配置，即可看到流量只会进入到一个 Pod：

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-ingress
  namespace: study-ingress
  annotations:
    nginx.ingress.kubernetes.io/proxy-body-size: 16m
    nginx.ingress.kubernetes.io/affinity: "cookie"
    nginx.ingress.kubernetes.io/session-cookie-name: "route"
    # 过期时间，expires字段是为了兼容旧版浏览器
    nginx.ingress.kubernetes.io/session-cookie-expires: "172800"
    nginx.ingress.kubernetes.io/session-cookie-max-age: "172800"
    # 后端负载扩容后，是否需要重新分配流量，balanced: 重新分配，persistent: 保持粘性
    nginx.ingress.kubernetes.io/affinity-mode: persistent
spec:
  ingressClassName: nginx
  rules: 
  - host: nginx.test.com
    path: /
    pathType: ImplementationSpecific
    http:
      paths:
      - backend:
          service:
            name: nginx
            port:
              number: 80
~~~

同时浏览器的 request headers 会添加一个 Cookie 的属性。

如果需要流量重新分配，更改 `nginx.ingress.kubernetes.io/affinity-mode: balanced` 即可。再次扩容后，就会发现流量会重新分配到其他节点。（更推荐用persistent模式，）

详细的会话保持配置：[Sticky Sessions - Ingress-Nginx Controller](https://kubernetes.github.io/ingress-nginx/examples/affinity/cookie/)

## 配置流式返回 SSE（代理大模型服务）

如果后端服务需要持续的输出数据，或者需要长连接，此时需要更改请求头升级链接为长连接：

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-ingress
  namespace: study-ingress
  annotations:
    nginx.ingress.kubernetes.io/proxy-http-version: "1.1"
    nginx.ingress.kubernetes.io/proxy-buffering: "off"
    # snippet用于配置一些ingress annotation不支持或者复杂的参数，比如配置请求头，或者逻辑控制等。里面直接写nginx原生支持的参数。
    nginx.ingress.kubernetes.io/configuration-snippet: |
      proxy_set_header Updrade $http_updrade;
      proxy_set_header Connection 'upgrade';
spec:
  ingressClassName: nginx
  rules: 
  - host: nginx.test.com
    path: /
    pathType: ImplementationSpecific
    http:
      paths:
      - backend:
          service:
            name: nginx
            port:
              number: 80
~~~

## 域名重定向Redirect

在使用 Nginx 作为代理服务器时，Redirect 可用于域名的重定向，比如访问 old.com 被重定向到 new.com。Ingress 也可以实现 Redirect 功能，接下来用 nginx.redirect.com 作为旧域名，baidu.com 作为新域名进行演示：

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-ingress
  namespace: study-ingress
  annotations:
    nginx.ingress.kubernetes.io/permanent-redirect: https://www.baidu.com
    nginx.ingress.kubernetes.io/permanent-redirect-code: "308" # 301、307、308都可以，都是重定向状态码。
spec:
  ingressClassName: nginx
  rules: 
  - host: nginx.test.com
    path: /
    pathType: ImplementationSpecific
    http:
      paths:
      - backend:
          service:
            name: nginx
            port:
              number: 80
~~~

使用 curl -I nginx.redirect.com，可以看到 308

## 访问地址重写Rewrite

对于一个大的项目，前后端分离，后端微服务有很多，**共用同一个域名比如nginx.test.com**。用户访问是通过path路径去区分访问，比如/api-a到用户中心/api-b到支付中心等。但是后端去开发的时候，并不是按照/api-a、/api-b等接口去开发的，可能留的接口都是/api。这样访问怎么找到每一个微服务？

我们直接去访问/api-a肯定是不行的，因为后端服务根本没有这个名字的接口。我们可以自定义/api-a这个路径，重写为 /api (或者比如开发留的接口就是/，那就重写为/) 就能访问到后端的服务了。如下图：

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202507181955304.png" alt="image-20250718195507023" style="zoom:50%;" />

创建一个应用模拟后端服务：

~~~sh
kubectl create deploy backend-api --image=registry.cnbeijing.aliyuncs.com/dotbalo/nginx:backend-api -n study-ingress
~~~

创建 Service 暴露该应用

~~~sh
kubectl expose deploy backend-api --port 80 -n study-ingress
~~~

创建ingress

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: backend-api
  namespace: study-ingress
spec:
  ingressClassName: nginx
  rules:
  - host: nginx.rewrite.com
    http:
      paths:
      - backend:
          service:
            name: backend-api
            port:
              number: 80
    path: /api-a
    pathType: ImplementationSpecific
~~~

这个示例服务的后端接口留的是 /，而不是/api-a，现在我们直接访问/api-a，浏览器访问会报404。因为pod里面的容器根本没有/api-a接口。人家留的是/接口。

此时需要通过 Ingress Nginx 的 Rewrite 功能，将/api-a 重写为“/”，配置示例如下：

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: backend-api
  namespace: study-ingress
  annotations:
    # 告诉Ingress Controller重写请求的目标路径。
    # $2 是一个正则表达式捕获组的引用。匹配到第二个捕获组。
    nginx.ingress.kubernetes.io/rewrite-target: /$2
spec:
  ingressClassName: nginx
  rules:
  - host: nginx.rewrite.com
    http:
      paths:
      - backend:
          service:
            name: backend-api
            port:
              number: 80
    path: /api-a(/|$)(.*)
    # /api-a - 匹配以 "/api-a" 开头的路径
    # (/|$) - 第一个捕获组：匹配 "/" 或字符串结尾
	# (.*) - 第二个捕获组：匹配后面的任意字符
    pathType: ImplementationSpecific
~~~

| 原始请求路径        | 匹配结果 | 重写后路径    |
| ------------------- | -------- | ------------- |
| `/api-a/users`      | ✅ 匹配   | `/users`      |
| `/api-a/orders/123` | ✅ 匹配   | `/orders/123` |
| `/api-a`            | ✅ 匹配   | `/`           |
| `/api-b/test`       | ❌ 不匹配 | -             |

再次访问 nginx.test.com/api-a 即可访问到后端服务。

> 注：
>
> - 如果希望把/api-a重写为/api，annotation就写`nginx.ingress.kubernetes.io/rewrite-target: /api/$2`
> - 这个ingress里面配了rewrite，里面所有的host都会被重写。所以需要rewrite的不需要rewrite的ingress要分开创建ingress.yaml

## 限制访问速率

有时候可能需要限制速率以降低后端压力，或者限制单个 IP 每秒的访问速率防止攻击。此时可以使用 Nginx 的 rate limit 进行配置。

首先没有加速率限制，使用 ab 进行访问，Failed 为 0：

~~~yaml
ab -c 10 -n 100 http://auth.test.com/ | grep requests
# Complete requests: 100
# Failed requests: 0
~~~

添加速率限制，限制只能有一个连接，只需要添加 `nginx.ingress.kubernetes.io/limitconnections` 为 1 即可：

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-with-auth
  namespace: study-ingress
  annotations:
    nginx.ingress.kubernetes.io/auth-realm: Please Input Your Username and Password
    nginx.ingress.kubernetes.io/auth-secret: basic-auth
    nginx.ingress.kubernetes.io/auth-type: basic
    nginx.ingress.kubernetes.io/limit-connections: "1"
spec:
  ingressClassName: ingress-nginx
  rules:
  - host: auth.test.com
    http:
      paths:
      - backend:
          service:
            name: backend-api
            port:
              number: 80
    path: /
    pathType: ImplementationSpecific
~~~

再次使用 ab 测试，Failed 为 67:

~~~sh
ab -c 10 -n 100 http://auth.test.com/ | grep requests:
# Complete requests: 100
# Failed requests: 67
~~~

还有很多其它方面的限制，常用的配置如下：

~~~sh
# 限制每秒的连接，单个 IP：
nginx.ingress.kubernetes.io/limit-rps:
# 限制每分钟的连接，单个 IP：
nginx.ingress.kubernetes.io/limit-rpm:
# 限制客户端每秒传输的字节数，单位为 K，需要开启 proxy-buffering：
nginx.ingress.kubernetes.io/proxy-buffering: "on"
nginx.ingress.kubernetes.io/limit-rate:

# 速率限制白名单
nginx.ingress.kubernetes.io/limit-whitelist:
~~~

## 黑名单配置

**局部黑名单：**只针对这一个ingress的域名

使用 `nginx.ingress.kubernetes.io/denylist-source-range` 添加黑名单，支持 IP、网段，多个黑名单逗号分隔：

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-with-auth
  namespace: study-ingress
  annotations:
    nginx.ingress.kubernetes.io/auth-realm: Please Input Your Username and Password
    nginx.ingress.kubernetes.io/auth-secret: basic-auth
    nginx.ingress.kubernetes.io/auth-type: basic
    nginx.ingress.kubernetes.io/denylist-source-range: 192.168.181.134,10.0.0.0/24,172.10.0.1
spec:
  ingressClassName: ingress-nginx
  rules:
  - host: auth.test.com
    http:
      paths:
      - backend:
          service:
            name: backend-api
            port:
              number: 80
    path: /
    pathType: ImplementationSpecific
~~~

**全局黑名单：**所有controller代理的ingress都生效

Ingress-nginx 支持全局的黑白名单（**全局白名单慎用**），只需要在 ingress nginx 的配置文件中添加即可，添加后无需重启Controller，加一个全局黑名单：

~~~yaml
kubectl edit cm ingress-nginx-controller -n ingress-nginx
data:
  allow-snippet-annotations: "true" 
  denylist-source-range: 192.168.181.134
~~~

## 白名单配置

白名单表示只允许某个 IP 可以访问，直接在 yaml 文件中配置即可。比如这个ingress域名想要只允许192.168.181.141 访问，只需要添加一个 `nginx.ingress.kubernetes.io/whitelist-source-range` 注释即可：

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-with-auth
  namespace: study-ingress
  annotations:
    nginx.ingress.kubernetes.io/auth-realm: Please Input Your Username and Password
    nginx.ingress.kubernetes.io/auth-secret: basic-auth
    nginx.ingress.kubernetes.io/auth-type: basic
    nginx.ingress.kubernetes.io/whitelist-source-range: 192.168.181.141
spec:
  ingressClassName: ingress-nginx
  rules:
  - host: auth.test.com
    http:
      paths:
      - backend:
          service:
            name: backend-api
            port:
              number: 80
    path: /
    pathType: ImplementationSpecific
~~~

## 自定义错误页

每个项目在对外发布时，难免不了会有一些未知的错误，比如 404/502/503 等，为了给客户更加友好的提示，可以使用 default backend 自定义错误页。

需要提前部署一个自定义页面的pod来提供自定义页面：

- 官方文档提供了配置说明：[Custom Errors - Ingress-Nginx Controller](https://kubernetes.github.io/ingress-nginx/examples/customization/custom-errors/)
- yaml文件在这里：[ingress-nginx/docs/examples/customization/custom-errors/custom-default-backend.yaml at main · kubernetes/ingress-nginx](https://github.com/kubernetes/ingress-nginx/blob/main/docs/examples/customization/custom-errors/custom-default-backend.yaml)

部署default backend：

~~~sh
kubectl create -f custom-default-backend.yaml -n ingress-nginx
# service/nginx-errors created
# deployment.apps/nginx-errors created
kubectl get po -n ingress-nginx
nginx-errors-7486ff48d8-zwz6t    1/1 Running 0 6s
~~~

按照yaml文件的说明，把自定义的错误页面挂载进去：

~~~yaml
        # Mounting custom error page from configMap
        # volumeMounts:
        # - name: custom_error_pages
        #   mountPath: /www

      # Mounting custom error page from configMap
      # volumes:
      # - name: custom_error_pages
      #   configMap:
      #     name: custom_error_pages
      #     items:
      #     - key: "404"
      #       path: "404.html"
      #     - key: "503"
      #       path: "503.html"
~~~

更改 ingress-nginx 的启动参数，支持自定义错误页：

~~~sh
kubectl edit ds -n ingress-nginx
# 在 -args: 下面添加启动参数
- --default-backend-service=ingress-nginx/nginx-errors
~~~

配置 ConfigMap，定义哪些错误码被重定向到自定义错误页：

~~~sh
kubectl edit cm ingress-nginx-controller -n ingress-nginx
# custom-http-errors: "404,502,503"
~~~

更新完成以后访问一个不存在的页面，比如之前定义的 nginx.test.com。访问一个不存在的页面 123，就会返回 Error Server 中的页面。

## 根据请求头返回不同页面

比如手机端用户访问，返回手机端页面；电脑端用户访问返回电脑端页面。

需要通过snippet配置来写nginx原生语法来实现。

先创建一个移动端的ingress：

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: phone
  namespace: study-ingress
spec:
  ingressClassName: ingress-nginx
  rules:
  - host: m.test.com
    http:
      paths:
      - backend:
          service:
            name: phone
            port:
              number: 80
    path: /
    pathType: ImplementationSpecific
~~~

电脑端的ingress去检测如果是移动端发来的请求久重定向到移动端的域名：

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: laptop
  namespace: study-ingress
  annotations:
    nginx.ingress.kubernetes.io/server-snippet: |
        set $agentflag 0;
        if ($http_user_agent ~* "(Android|iPhone|WindowsPhone|UC|Kindle)" ){
            set $agentflag 1;
        }
        if ( $agentflag = 1 ) {
            return 301 http://m.test.com;
        }
spec:
  ingressClassName: ingress-nginx
  rules:
  - host: test.com
    http:
      paths:
      - backend:
          service:
            name: laptop
            port:
              number: 80
    path: /
    pathType: ImplementationSpecific
~~~

## 灰度/金丝雀/蓝绿发布

- 灰度发布：上线了新版本v2代替v1，但是不会直接把全部流量切到v2。先切10%流量到v2，验证一下；再切50%流量；再切100%到v2。

- 蓝绿发布：v2版本部署之后，直接把流量全切到v2上面去，有问题再切回v1。同时存在两个版本。

> 灰度发布里面可以通过请求头设置一部分测试用户的流量可以进来，是更加稳妥的做法。

v2的灰度版本如何设置，才能获取到一小部分比例的流量：创建 v2 版本的 Ingress 时，需要添加两个注释:

1. `nginx.ingress.kubernetes.io/canary`，表明是灰度环境，只接受部分流量

2. `nginx.ingress.kubernetes.io/canary-weight` 表明切多少流量到该环境，本示例为10%

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: canary-v2
  namespace: study-ingress
  annotations:
    nginx.ingress.kubernetes.io/canary: "true"
    nginx.ingress.kubernetes.io/canary-weight: "10"
spec:
  ingressClassName: ingress-nginx
  rules:
  - host: canary.com # 用的是和v1同一个域名，但是后端svc是v2的svc。标注了是灰度环境，仅接收部分流量。
    http:
      paths:
      - backend:
          service:
            name: canary-v2
            port:
              number: 80
    path: /
    pathType: ImplementationSpecific
~~~

此时通过 nginx.ingress.kubernetes.io/canary-weight: "10"设置的权重是 10，即 v1:v2 为 9:1。

可以用ruby脚本测试流量分布：

~~~ruby
# vim test-canary.rb 
counts = Hash.new(0)

100.times do
  output = `curl -s canary.com | grep 'Canary' | awk '{print $2}' | awk -
F"<" '{print $1}'`
  counts[output.strip.split.last] += 1

end

puts counts

# 安装 ruby 并测试，可以看到大致的比例是 9:1
yum install ruby -y
ruby test-canary.rb 
# {"v1"=>90, "v2"=>10}
ruby test-canary.rb 
# {"v1"=>92, "v2"=>8}
ruby test-canary.rb 
# {"v1"=>91, "v2"=>9}
~~~

实际使用过程中，v2流量全切过去发现没问题，有两种策略：

1. 把v1也更新上去，把流量再逐步切回v1。这样v1还是生产环境，v2还是canary环境，下次更新还是继续这样的操作。
2. v1不动，就等着下次发版发到v1上，流量再从v2灰度切回到v1。【推荐】因为第一种把流量切回去可能又会产生无法预知的问题。既然流量已经过去了就保持在v2就行了。

# 常见问题

## 404 Not Found

404表示路由不存在，通常问题：

1. ingress路径配置不正确
2. ingress的配置没有被controller解析
3. 没使用正确的域名和路径
4. 代理的服务没有该路径的接口，或者GET POST方法不对。

## 413 Request Entity Too Large

有时候需要上传一些大文件给程序，但是 nginx 默认允许的最大文件大小只有 8M，不足以满足生产最大上传需求，此时可以通过 `nginx.ingress.kubernetes.io/proxy-body-size` 参数进行更改（也可以在 ConfigMap 中全局添加）。

一般建议在annotation中给每个ingress单独配置。

## 503 Service Unavailable

503  一般是代理的服务不可用导致的，通常问题如下：
1.  Ingress 代理配置错误，比如 Service 名字或端口写错
2.  Ingress 代理的 Service 不存在
3.  Ingress 代理的 Service 后端 Pod 不正常

## 504 Gateway Timeout

504 一般是代理的服务处理请求的时间过长，导致 Nginx 等待超时，此时需要确认服务的处理时长，或者查看服务是否有问题。或者可能是网络不通（比如代理了外部的地址）。

也可以根据调整超时时间：（https://kubernetes.github.io/ingress-nginx/userguide/nginx-configuration/annotations/#custom-timeouts）

~~~yaml
annotations:
  nginx.ingress.kubernetes.io/proxy-connect-timeout: "120"
  nginx.ingress.kubernetes.io/proxy-send-timeout: "120"
  nginx.ingress.kubernetes.io/proxy-read-timeout: "120"
~~~

## CORS 跨域报错

有时候某个域名里面可能去代理了一些其他的接口，这些接口可能属于其他的第三方的域名。

如果浏览器有如下报错，说明被跨域给拦截了，可以添加跨域配置。

官方文档：https://kubernetes.github.io/ingress-nginx/user-guide/nginxconfiguration/annotations/#enable-cors

应该是去跨到别人那里的域名的ingress上添加允许跨域配置。

~~~yaml
annotations:
  # 允许跨域的请求方法
  nginx.ingress.kubernetes.io/enable-cors: "true"
  # 允许携带的请求头
  nginx.ingress.kubernetes.io/cors-allow-methods: "PUT, GET, POST, OPTIONS, DELETE"
  nginx.ingress.kubernetes.io/cors-allow-headers: "X-Forwarded-For, Xapp123-XPTO"
  # 允许跨域的域名。意思是允许哪个域名跨到你这里来
  nginx.ingress.kubernetes.io/cors-allow-origin: "*"
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

# 实战：Ingress灰度发布

## 场景1-基于header/cookie

- 假设线上运行了一套对外提供 7 层服务的 Service A 服务，后来开发了个新版本 Service A’ 想要上线，但又不想直接替换掉原来的 Service A，希望先灰度一小部分用户，等运行一段时间足够稳定了再逐渐全量上线新版本，最后平滑下线旧版本。

- 这个时候就可以利用 Nginx Ingress 基于 Header 或 Cookie 进行流量切分的策略来发布，业务使用 Header 或 Cookie 来标识不同类型的用户，我们通过配置 Ingress 来实现让带有指定 Header 或 Cookie 的请求被转发到新版本，其它的仍然转发到旧版本，从而实现将新版本灰度给部分用户。

  <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202312281017402.png" alt="image-20231228101712175" style="zoom:50%;" />

## 场景2-按比例切分流量

- 假设线上运行了一套对外提供 7 层服务的 Service B 服务，后来修复了一些问题，需要灰度上线一个新版本 Service B’，但又不想直接替换掉原来的 Service B，而是让先切 10% 的流量到新版本，等观察一段时间稳定后再逐渐加大新版本的流量比例直至完全替换旧版本，最后再平滑下线旧版本，从而实现切一定比例的流量给新版本。

  <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202312281018356.png" alt="image-20231228101848227" style="zoom:50%;" />

## 实现方法

- 部署ingress来切分流量，在ingress的metadata.annotations字段中，定义下列annotation，实现流量控制。假设有老版本和Canry

  - `nginx.ingress.kubernetes.io/canary-by-header`：
    - 基于Request Header的流量切分，适用于灰度发布以及 A/B 测试。当Request Header 设置为 always时，请求将会被一直发送到 Canary 版本；当 Request Header 设置为 never时，请求不会被发送到 Canary 入口。

  - `nginx.ingress.kubernetes.io/canary-by-header-value`：
    - 要匹配的 Request Header 的值，用于通知 Ingress 将请求路由到 Canary Ingress 中指定的服务。当 Request Header 设置为此值时，它将被路由到 Canary 入口。

  - `nginx.ingress.kubernetes.io/canary-weight`：
    - 基于服务权重的流量切分，适用于蓝绿部署，权重范围 0 - 100 按百分比将请求路由到 Canary Ingress 中指定的服务。权重为 0 意味着该金丝雀规则不会向 Canary 入口的服务发送任何请求。权重为60意味着60%流量转到canary。权重为 100 意味着所有请求都将被发送到 Canary 入口。

  - `nginx.ingress.kubernetes.io/canary-by-cookie`：
    - 基于 Cookie 的流量切分，适用于灰度发布与 A/B 测试。用于通知 Ingress 将请求路由到 Canary Ingress 中指定的服务的cookie。当 cookie 值设置为 always时，它将被路由到 Canary 入口；当 cookie 值设置为 never时，请求不会被发送到 Canary 入口。

- 注：以上的annotations是ingress nginx所官方支持的：

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

# 

# 实战：基于nginx+keepalived的Ingress-Controller高可用架构【不推荐】

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
