# SpringCloud项目架构

1. 有一个SpringCloud项目需要迁移至K8s，该项目采用Eureka注册中心，采用前后端分离框架。

2. 该项目首页域名为demo.kubeasy.com：

- 域名主路径 / 转发至项目的前端
- 路径 /receiveapi 转发至网关服务
- 其他服务注册至Eureka，由网关服务进行流量转发。

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202509231042642.png" alt="image-20250923104234590" style="zoom:50%;" />

#  迁移方案

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202509231039534.png" alt="image-20250923103915421" style="zoom:50%;" />

- Eureka：通过sts部署，最好组成集群

- Receive：充当网关，负责转发，需要通过ingress暴露域名，因为需要浏览器调用

- Handler：不需要暴露对外访问，通过receive转发过去的
- UI：前端服务暴露ingress域名访问。

## 迁移Eureka集群

- 代码地址：https://gitee.com/dukuan/demo-eureka
- 构建命令：mvn clean package
- Java 版本：jdk 1.8
- 构建镜像：registry.cn-beijing.aliyuncs.com/citools/maven:3.5.3

### 构建及容器化

~~~sh
# 下载代码
git clone https://gitee.com/dukuan/demo-eureka.git 

# 执行构建，用一个maven的docker容器进去构建。
mkdir -p /data/m2 
docker run -ti --rm -v `pwd`/demo-eureka:/mnt/ -v /data/m2/:/root/.m2  registry.cn-beijing.aliyuncs.com/citools/maven:3.5.3 bash 
cd /mnt
ls
mvn clean package

# 构建完成后查看构建产物
ls target/*.jar

# 制作镜像
cd demo-eureka/

tee Dockerfile <<'EOF'  
FROM registry.cn-beijing.aliyuncs.com/dotbalo/jdk:8u211-jmap 
WORKDIR /home/tomcat
COPY target/*.jar ./ 
CMD ["java","-jar","./*.jar"]
EOF

docker build -t demo-eureka:v0.0.1 . 
~~~

### 部署至k8s

~~~yaml
apiVersion: apps/v1 
kind: StatefulSet 
metadata: 
  name: demo-eureka 
  namespace: demo 
  labels: 
    app: demo-eureka 
  annotations: 
    app: demo-eureka 
spec: 
  replicas: 3 
  selector: 
    matchLabels: 
      app: demo-eureka 
  template: 
    metadata: 
      creationTimestamp: null 
      labels: 
        app: demo-eureka 
      annotations: 
        app: demo-eureka 
    spec: 
      serviceName: "demo-eureka"
      podManagementPolicy: Parallel
      containers: 
        - name: eureka 
          image: registry.cn-beijing.aliyuncs.com/dotbalo/demo-eureka:v0.0.1 
          imagePullPolicy: IfNotPresent 
          ports: 
            - name: http-web 
              containerPort: 8761 
              protocol: TCP 
          env: 
            - name: SPRING_PROFILES_ACTIVE 
              # 这个值指定了eureka的启动文件。
              # 路径在/src/main/resources下。设置为k8s，就会在这个路径搜寻application-k8s.yaml这个文件作为启动文件
              value: k8s 
            - name: SERVER_PORT 
              value: '8761' 
            - name: EUREKA_SERVER_ADDRESS 
              value: >- 
                http://demo-eureka-0.demo-eureka:8761/eureka/,http://demo-eureka-1.demo-eureka:8761/eureka/,http://demo-eureka-2.demo-eureka:8761/eureka/ 
          resources: 
            limits:
              cpu: '1' 
              memory: 1Gi 
            requests: 
              cpu: 100m 
              memory: 128Mi 
---
# headless service
apiVersion: v1 
kind: Service 
metadata: 
  name: demo-eureka 
  namespace: demo 
  labels: 
    app: demo-eureka 
  annotations: 
    kubeasy.com/autoCreate: 'true' 
spec: 
  type: ClusterIP 
  clusterIP: None
  ports: 
  - name: http-web 
    protocol: TCP 
    port: 8761 
    targetPort: 8761 
  selector: 
    app: demo-eureka 
---
# NodePort service
apiVersion: v1 
kind: Service 
metadata: 
  name: demo-eureka-np
  namespace: demo 
spec: 
  type: NodePort
  ports: 
  - name: http-web 
    protocol: TCP 
    port: 8761 
    targetPort: 8761 
  selector: 
    app: demo-eureka 
---
apiVersion: networking.k8s.io/v1 
kind: Ingress 
metadata: 
  name: demo-receive 
  namespace: demo 
  annotations: 
    nginx.ingress.kubernetes.io/rewrite-target: /$2 
spec: 
  ingressClassName: 'nginx-default' 
  rules: 
  - host: demo.hanxux.local
    http: 
      paths: 
      - path: /receiveapi(/|$)(.*) 
        pathType: ImplementationSpecific 
        backend: 
          service: 
            name: demo-receive 
            port: 
              number: 8080 
~~~

## 迁移网关服务

代码地址：https://gitee.com/dukuan/demo-receive

构建命令：mvn clean package

Java 版本：jdk 1.8

构建镜像：registry.cn-beijing.aliyuncs.com/citools/maven:3.5.3

### 构建及容器化

~~~sh
# 下载代码
git clone https://gitee.com/dukuan/demo-receive.git

# 执行构建
mkdir -p /data/m2 
docker run -ti --rm -v `pwd`/demo-receive:/mnt/ -v /data/m2/:/root/.m2  registry.cn-beijing.aliyuncs.com/citools/maven:3.5.3 bash 
cd /mnt 
mvn clean package

# 查看构建产物
ls target/*.jar 

# 制作镜像
cd demo-receive/ 

tee Dockerfile <<'EOF'  
FROM registry.cn-beijing.aliyuncs.com/dotbalo/jdk:8u211-jmap 
WORKDIR /home/tomcat 
COPY target/*.jar ./ 
CMD ["java","-jar","./*.jar"] 
EOF

docker build -t demo-receive:v0.0.1 .
~~~

### 部署至K8s

~~~yaml
apiVersion: apps/v1 
kind: Deployment 
metadata: 
  name: demo-receive 
  namespace: demo 
  labels: 
    app: demo-receive 
  annotations: 
    app: demo-receive 
spec: 
  replicas: 1 
  selector: 
    matchLabels: 
      app: demo-receive 
  template: 
    metadata: 
      labels: 
        app: demo-receive 
      annotations: 
        app: demo-receive 
    spec: 
      restartPolicy: Always
      containers: 
        - name: receive 
          image: registry.cn-beijing.aliyuncs.com/dotbalo/demo-receive:v0.0.1 
          imagePullPolicy: IfNotPresent 
          ports: 
            - name: http-web 
              containerPort: 8080 # 推荐所有后端服务都用8080端口
              protocol: TCP 
          env: 
            - name: SPRING_PROFILES_ACTIVE 
              value: k8s 
            - name: SERVER_PORT 
              value: '8080' 
            - name: EUREKA_SERVER_ADDRESS 
              value: >- 
                http://demo-eureka-0.demo-eureka:8761/eureka/,http://demo-eureka-1.demo-eureka:8761/eureka/,http://demo-eureka-2.demo-eureka:8761/eureka/ 
          resources: 
            limits: 
              cpu: '1' 
              memory: 1Gi 
            requests: 
              cpu: 100m 
              memory: 128Mi 
---
apiVersion: v1 
kind: Service 
metadata: 
  name: demo-receive 
  namespace: demo 
  labels: 
    app: demo-receive 
  annotations: 
    kubeasy.com/autoCreate: 'true' 
spec: 
  ports: 
    - name: http-web 
      protocol: TCP 
      port: 8080 
      targetPort: 8080 
  selector: 
    app: demo-receive
---
apiVersion: networking.k8s.io/v1 
kind: Ingress 
metadata: 
  name: demo-receive 
  namespace: demo 
  annotations: 
    nginx.ingress.kubernetes.io/rewrite-target: /$2 
spec: 
  ingressClassName: 'nginx-default' 
  rules: 
  - host: demo.hanxux.local
    http: 
      paths: 
      - path: /receiveapi(/|$)(.*) 
        pathType: ImplementationSpecific 
        backend: 
          service: 
            name: demo-receive 
            port: 
              number: 8080 
~~~

## 迁移handler服务

代码地址：https://gitee.com/dukuan/demo-handler

构建命令：mvn clean package

Java 版本：jdk 1.8

构建镜像：registry.cn-beijing.aliyuncs.com/citools/maven:3.5.3

### 构建及容器化

~~~sh
# 下载代码
git clone https://gitee.com/dukuan/demo-handler.git 

#构建
mkdir -p /data/m2 
docker run -ti --rm -v `pwd`/demo-handler:/mnt/ -v /data/m2/:/root/.m2  registry.cn-beijing.aliyuncs.com/citools/maven:3.5.3 bash 
cd /mnt 
mvn clean package

# 查看构建产物
ls target/*.jar

# 制作镜像
cd demo-handler/ 

tee Dockerfile <<'EOF'  
FROM registry.cn-beijing.aliyuncs.com/dotbalo/jdk:8u211-jmap 
WORKDIR /home/tomcat 
COPY target/*.jar ./ 
CMD ["java","-jar","./*.jar"] 
EOF

docker build -t registry.cn-beijing.aliyuncs.com/dotbalo/demo-handler:v0.0.1 . 
~~~

### 部署至k8s

~~~yaml
apiVersion: apps/v1 
kind: Deployment 
metadata: 
  name: demo-handler 
  namespace: demo 
  labels: 
    app: demo-handler 
  annotations: 
    app: demo-handler 
spec: 
replicas: 1 
  selector: 
    matchLabels: 
      app: demo-handler 
  template: 
    metadata: 
      labels: 
        app: demo-handler 
      annotations: 
        app: demo-handler 
    spec: 
      restartPolicy: Always
      containers: 
        - name: handler 
          image: registry.cn-beijing.aliyuncs.com/dotbalo/demo-handler:v0.0.1 
          imagePullPolicy: Always 
          ports: 
            - name: http-web 
              containerPort: 8080 
              protocol: TCP 
          env: 
            - name: SPRING_PROFILES_ACTIVE 
              value: k8s 
            - name: SERVER_PORT 
              value: '8080' 
            - name: EUREKA_SERVER_ADDRESS 
              value: >- 
                http://demo-eureka-0.demo-eureka:8761/eureka/,http://demo-eureka-1.demo-eureka:8761/eureka/,http://demo-eureka-2.demo-eureka:8761/eureka/ 
          resources: 
            limits: 
              cpu: '1' 
              memory: 1Gi 
            requests: 
              cpu: 100m 
              memory: 128Mi 
          livenessProbe: 
            tcpSocket: 
              port: 8080 
            initialDelaySeconds: 30 
            timeoutSeconds: 2 
            periodSeconds: 30 
            successThreshold: 1 
            failureThreshold: 2 
          readinessProbe: 
            tcpSocket: 
              port: 8080 
            initialDelaySeconds: 30 
            timeoutSeconds: 2 
            periodSeconds: 30 
            successThreshold: 1 
            failureThreshold: 2
~~~

## 迁移前端服务

代码地址：https://gitee.com/dukuan/demo-ui

构建命令：npm install --registry=https://registry.npmmirror.com && npm run build

Node版本：16.17+

构建镜像：registry.cn-beijing.aliyuncs.com/dotbalo/node:16.17.0-apline-cnpm

### 构建及容器化

~~~sh
# 下载代码
git clone https://gitee.com/dukuan/demo-ui.git 

# 执行构建： 
docker run -ti --rm -v `pwd`/demo-ui:/mnt/ registry.cn-beijing.aliyuncs.com/dotbalo/node:16.17.0-apline-cnpm sh 
cd /mnt 
npm install -registry=https://registry.npmmirror.com && npm run build 

# 构建完成后，查看构建产物： 
ls dist/ 
assets      index.html  vite.svg 

# 制作镜像： 
cd demo-ui/ 
tee Dockerfile <<'EOF'  
FROM registry.cn-beijing.aliyuncs.com/dotbalo/nginx:1.22.1-alpine3.17 
COPY dist /usr/share/nginx/html
EOF

docker build -t demo-ui:v0.0.1 . 
~~~

### 部署至k8s

~~~yaml
apiVersion: apps/v1 
kind: Deployment 
metadata: 
  name: demo-ui 
  namespace: demo 
  labels: 
    app: demo-ui 
  annotations: 
    app: demo-ui 
spec: 
  replicas: 1 
  selector: 
    matchLabels: 
      app: demo-ui 
  template: 
    metadata: 
      labels: 
        app: demo-ui 
      annotations: 
        app: demo-ui 
    spec: 
      restartPolicy: Always
      containers: 
        - name: ui 
          image: registry.cn-beijing.aliyuncs.com/dotbalo/demo-ui:v0.0.1 
          imagePullPolicy: IfNotPresent 
          ports: 
            - name: http-web 
              containerPort: 80 
              protocol: TCP 
          resources: 
            limits: 
              cpu: '1' 
              memory: 1Gi 
            requests: 
              cpu: 100m 
              memory: 128Mi 
---
kind: Service 
metadata: 
  name: demo-ui 
  namespace: demo 
  labels: 
    app: demo-ui 
  annotations: 
    kubeasy.com/autoCreate: 'true' 
spec: 
  ports: 
    - name: http-web 
      protocol: TCP 
      port: 80 
      targetPort: 80 
  selector: 
    app: demo-ui 
  type: ClusterIP 
--- 
apiVersion: networking.k8s.io/v1 
kind: Ingress 
metadata: 
  name: demo-ui 
  namespace: demo 
spec: 
  ingressClassName: "nginx-default" 
  rules: 
    - host: demo.hanxux.local
      http: 
        paths: 
          - path: / 
            pathType: Prefix 
            backend: 
              service: 
                name: demo-ui 
                port: 
                  number: 80
~~~

## 迁移过程总结

1. 容器化：只要有镜像，就能部署到K8s
2. 确认部署方式（注册中心可能会需要sts部署，有headless svc可供其他pod使用来找到注册中心）
3. 确认域名配置(暴露对外访问的用ingress，服务发现用service)

# SpringCloud云原生架构升级

Eureka作为注册中心，提供的服务发现，k8s就能实现，这涉及到套娃。所以可以去掉Eureka，去中心化，基本无代码侵入。

所有微服务用svc暴露访问即可。比如handler只要创建的svc名字和当前代码中调用的地址相同，就可以无代码侵入的切换。

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202509231711078.png" alt="image-20250923171144753" style="zoom:50%;" />

~~~yaml
---
apiVersion: v1 
kind: Service 
metadata: 
  name: handler # 因为代码中调用路径就是handler，所以创建一个同名的svc即可实现暴露 
  namespace: demo 
  labels: 
    app: demo-handler 
  annotations: 
    kubeasy.com/autoCreate: 'true' 
spec: 
  ports: 
  - name: http-web 
    protocol: TCP 
    port: 8080 
    targetPort: 8080 
  selector: 
    app: demo-handler 
  type: ClusterIP
~~~

注意：在application-k8s文件里面需要把eureka的配置注释掉，然后重新做镜像部署。否则前端访问会报错。
