# 企业内项目接入istio流程

企业内接入istio常见有两种情况：

1. 需要注入istio sidecar进行流量管理（东西流量）
2. 不需要sidecar，只需要使用ingressGateway作为网关把服务发布出去（只需要南北流量管理）

针对第一种情况，在建立服务时，最好配置version标签；第二种情况不需要特殊处理，但是也推荐打上version标签，方便后期用sidecar管理。

同时也要考虑项目是否已经部署在集群内了：

1. 新项目还未部署：按照istio的规范创建deployment和service，以及istio的核心资源
2. 已经部署在集群中的：需要修改Deployment、Service，按需转换为ingressGateway对外提供服务

# 项目接入istio实战

## 测试项目架构

有一个测试项目demo，架构如下：

![image-20250827225358494](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202508272253850.png)

- 前端有个UI服务，域名根路径指向前端服务
- 两个后端服务通过/order和/receiveapi暴露访问：
  - Receive Service（转发请求到Handler Service，返回一个随机密码）
  - Order Service（查询订单，连接Mysql）
- Handler Service不暴露对外访问。

我们把这个项目改造为istio服务网格管理。

## 部署测试项目

~~~sh
kubectl create ns demo
~~~

### mysql组件

~~~yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mysql
  namespace: demo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: mysql-data
      containers:
      - name: mysql
        image: registry.cn-beijing.aliyuncs.com/dotbalo/mysql:8.0.20
        imagePullPolicy: IfNotPresent
        env:
        - name: MYSQL_ROOT_PASSWORD
          value: password
        volumeMounts:
        - name: data
          mountPath: /var/lib/mysql
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-data
  namespace: demo
spec:
  volumeMode: Filesystem
  storageClassName: sc-nfs
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Mi
---
apiVersion: v1
kind: Service
metadata:
  name: mysql
  namespace: demo
spec:
  type: NodePort
  selector:
    app: mysql
  ports:
  - nodePort: 32541
    port: 3306
    protocol: TCP
    targetPort: 3306
~~~

~~~sh
# 部署好进入mysql配置数据库
mysql -uroot -p
create database orders; 
CREATE USER 'order'@'%' IDENTIFIED BY 'password'; 
GRANT ALL ON orders.* TO 'order'@'%'; 
~~~

### order服务

~~~yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-order
  namespace: demo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: demo-order
  template:
    metadata:
      labels:
        app: demo-order
        version: v1 # istio改造，需要加上版本标签
    spec:
      containers:
      - name: demo-order
        image: registry.cn-beijing.aliyuncs.com/dotbalo/demo-order:v1
        imagePullPolicy: IfNotPresent
        env:
        - name: MYSQL_HOST
          value: mysql
        - name: MYSQL_PORT
          value: "3306"
        - name: MYSQL_USER
          value: order
        - name: MYSQL_PASSWORD
          value: password
        - name: MYSQL_DB
          value: orders
        livenessProbe:
          failureThreshold: 2
          initialDelaySeconds: 30
          periodSeconds: 5
          successThreshold: 1
          tcpSocket:
            port: 8080
          timeoutSeconds: 2
        readinessProbe:
          failureThreshold: 2
          initialDelaySeconds: 30
          periodSeconds: 5
          successThreshold: 1
          tcpSocket:
            port: 8080
          timeoutSeconds: 2
---
apiVersion: v1
kind: Service
metadata:
  name: order
  namespace: demo
spec:
  selector:
    app: demo-order
  ports:
  # istio中端口命名的要求：如果是http端口就叫http-80或者http-web；如果是TCP的就叫tcp-3306之类的
  - name: http-web
    port: 80
    protocol: TCP
    targetPort: 8080
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: demo-order
  namespace: demo
spec:
  ingressClassName: nginx
  rules:
  - host: demo.test.com
    http:
      paths:
      - backend:
          service:
            name: order
            port:
              number: 80
        path: /orders
        pathType: ImplementationSpecific
~~~

### handler服务

~~~yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-handler
  namespace: demo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: demo-handler
  template:
    metadata:
      labels:
        app: demo-handler
        version: v1 # istio改造，加上版本标签
    spec:
      containers:
      - name: demo-handler
        env:
        - name: SPRING_PROFILES_ACTIVE
          value: k8supgrade
        - name: SERVER_PORT
          value: "8080"
        image: registry.cn-beijing.aliyuncs.com/dotbalo/demo-handler:v0.0.1-upgrade
        imagePullPolicy: IfNotPresent
        livenessProbe:
          failureThreshold: 2
          initialDelaySeconds: 30
          periodSeconds: 5
          successThreshold: 1
          tcpSocket:
            port: 8080
          timeoutSeconds: 2
        readinessProbe:
          failureThreshold: 2
          initialDelaySeconds: 30
          periodSeconds: 5
          successThreshold: 1
          tcpSocket:
            port: 8080
          timeoutSeconds: 2
---
apiVersion: v1
kind: Service
metadata:
  name: handler
  namespace: demo
spec:
  selector:
    app: demo-handler
  ports:
  - name: http-web
    port: 80
    protocol: TCP
    targetPort: 8080
~~~

### receive服务

~~~yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-receive
  namespace: demo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: demo-receive
  template:
    metadata:
      labels:
        app: demo-receive
        version: v1 # istio改造，加上版本标签
    spec:
      containers:
      - name: demo-receive
        image: registry.cn-beijing.aliyuncs.com/dotbalo/demo-receive:v0.0.1-upgrade
        imagePullPolicy: Always
        env:
        - name: SPRING_PROFILES_ACTIVE
          value: k8supgrade
        - name: SERVER_PORT
          value: "8080"
        livenessProbe:
          failureThreshold: 2
          initialDelaySeconds: 30
          periodSeconds: 5
          successThreshold: 1
          tcpSocket:
            port: 8080
          timeoutSeconds: 2
        readinessProbe:
          failureThreshold: 2
          initialDelaySeconds: 30
          periodSeconds: 5
          successThreshold: 1
          tcpSocket:
            port: 8080
          timeoutSeconds: 2
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    # 将用户请求路径重写为第二个捕获组 (.*) 的内容，去掉 /receiveapi 前缀，转发给后端demo-receive服务
    nginx.ingress.kubernetes.io/rewrite-target: /$2
  name: demo-receive
  namespace: demo
spec:
  ingressClassName: nginx-default
  rules:
  - host: demo.test.com
    http:
      paths:
      - backend:
          service:
            name: demo-receive
            port:
              number: 8080
        path: /receiveapi(/|$)(.*)
        pathType: ImplementationSpecific
---
apiVersion: v1
kind: Service
metadata:
  name: demo-receive
  namespace: demo
spec:
  selector:
    app: demo-receive
  ports:
  - name: http-web
    port: 8080
    protocol: TCP
    targetPort: 8080
~~~

### 前端UI

~~~yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-ui
  namespace: demo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: demo-ui
  template:
    metadata:
      labels:
        app: demo-ui
        version: v1 # istio项目改造，加上版本标签
    spec:
      containers:
      - name: demo-ui
        image: registry.cn-beijing.aliyuncs.com/dotbalo/demo-ui:sw
        imagePullPolicy: IfNotPresent
        livenessProbe:
          failureThreshold: 2
          initialDelaySeconds: 10
          periodSeconds: 5
          successThreshold: 1
          tcpSocket:
            port: 80
          timeoutSeconds: 2
        readinessProbe:
          failureThreshold: 2
          initialDelaySeconds: 10
          periodSeconds: 5
          successThreshold: 1
          tcpSocket:
            port: 80
          timeoutSeconds: 2
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: demo-ui
  namespace: demo
spec:
  ingressClassName: nginx-default
  rules:
  - host: demo.test.com
    http:
      paths:
      - backend:
          service:
            name: demo-ui
            port:
              number: 80
        path: /
        pathType: ImplementationSpecific
---
apiVersion: v1
kind: Service
metadata:
  labels:
    app: demo-ui
  name: demo-ui
  namespace: demo
spec:
  selector:
    app: demo-ui
  ports:
  - name: http-web
    port: 80
    protocol: TCP
    targetPort: 80
~~~

### 访问项目

宿主机添加host，通过前端UI的ingress访问：`demo.test.com`

## 接入istio南北流量改造

如果想要使用Istio管理南北流量，建议服务的入口使用IngressGateway进行管理，也就是需要把之前由其他控制器管理的Ingress改造为由Istio Gateway管理（新项目直接创建即可，无需改造）。 

### 确认待改造ingress

首先确认当前项目的ingress配置有哪些：

~~~sh
kubectl get ingress -n demo

NAME           CLASS           HOSTS           
demo-order     nginx-default   demo.test.com
demo-receive   nginx-default   demo.test.com
demo-ui        nginx-default   demo.test.com
~~~

建议先改造后端再改造前端

### 为项目创建Gateway

~~~yaml
apiVersion: networking.istio.io/v1 
kind: Gateway 
metadata: 
  name: demo-gateway
  namespace: demo
spec: 
  selector: 
    istio: ingressgateway # 使用默认的istio ingress gateway 
  servers: 
  - port: 
      number: 80 
      name: http
      protocol: HTTP 
    hosts: 
    - "demo.test.com" # 发布域名 
~~~

### 创建VirtualService

接下来需要创建VirtualService和Gateway绑定

#### order服务

看demo-order的ingress定义，把/orders路径转发到order svc，端口号是80。创建同样规则的VirtualService：

~~~yaml
--- 
apiVersion: networking.istio.io/v1 
kind: VirtualService 
metadata: 
  name: demo-order
  namespace: demo
spec: 
  hosts: 
  - "demo.test.com" 
  gateways: 
  - demo-gateway 
  http: 
  - match: 
    - uri: 
        prefix: /orders 
    route: 
    - destination:
        host: order.demo.svc.cluster.local
        port: 
          number: 80 
~~~

vs创建完成后就可以通过域名+ingressGateway端口号访问到服务了：`demo.test.com:30080/orders`

#### receive服务

看receive服务的ingress定义，里面有路径重写，将用户请求路径重写为第二个捕获组 (.*) 的内容，去掉 /receiveapi 前缀，转发给后端demo-receive服务的8080端口。

创建同样规则的VirtualService：

~~~yaml
--- 
apiVersion: networking.istio.io/v1 
kind: VirtualService 
metadata: 
  name: demo-receive
  namespace: demo
spec: 
  hosts: 
  - "demo.test.com" 
  gateways: 
  - demo-gateway 
  http: 
  - match: 
    - uri: 
        prefix: /receiveapi/ # 注意rewtire时前端路径要把最后的/写上，全部rewrite成/。这样后端服务就不会多一个/了
    rewrite: 
      uri: /
    route: 
    - destination: 
        host: demo-receive.demo.svc.cluster.local
        port: 
          number: 8080
~~~

#### 前端ui服务

~~~yaml
--- 
apiVersion: networking.istio.io/v1 
kind: VirtualService 
metadata: 
  name: demo-ui 
  namespace: demo
spec: 
  hosts: 
  - "demo.test.com" 
  gateways: 
  - demo-gateway 
  http: 
  - match: 
    - uri: 
        prefix: / 
    route: 
    - destination: 
        host: demo-ui 
        port: 
          number: 80
~~~

创建完成后，访问根路径`demo.test.com:30080/`验证。

#### 删除ingress

验证VirtualService和Gateway可以访问到发布的域名之后，就可以删掉现存的ingress了。

## 接入istio东西流量改造

如果需要istio管理东西流量，需要istio的sidecar注入，然后再通过DR和VS控制内部流量。

### ns添加istio注入标签

首先向demo命名空间添加istio标签：

~~~sh
kubectl label ns demo istio-injection=enabled
~~~

### 重建pod

rollout restart所有deployment和sts，滚动更新之后，istio sidecar会加到pod里面。

### 创建dr和vs

之后给需要管理东西流量的Service创建VirtualService和DestinationRule，方便更细力度控制流量。

比如handler服务是对内暴露的，可以进行东西流量改造。对handler服务创建VirtualService和DestinationRule：

~~~yaml
apiVersion: networking.istio.io/v1 
kind: DestinationRule 
metadata: 
  name: handler
  namespace: demo
spec: 
  host: handler.demo.svc.cluster.local
  subsets: 
  - name: v1 
    labels: 
      version: v1 
~~~

~~~yaml
apiVersion: networking.istio.io/v1 
kind: VirtualService 
metadata: 
  name: handler 
  namespace: demo 
spec: 
  hosts: 
  - handler.demo.svc.cluster.local
  http: 
  - route: 
    - destination: 
        host: handler.demo.svc.cluster.local
        port: 
          number: 80 
        subset: v1 # 流量指向v1
~~~

改造完成后可以在kiali界面查看流量图：`http://192.168.40.180:31096/kiali/console/graph/`
