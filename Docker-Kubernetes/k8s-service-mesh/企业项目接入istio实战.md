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
  annotations:
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
        version: v1
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

~~~



