# 获取java代码

~~~sh
yum install maven* -y
yum install git -y
git clone https://gitee.com/hanxianchao66/SpringBootDemo
cd SpringBootDemo/
~~~

# 编译代码

~~~sh
mvn clean package
cd /target
#编译成功之后一般会在target目录下生成一个jar包，本地运行的话直接java -jar xxx.jar就跑起来了
~~~

# 打包镜像

~~~sh
cd ..
vim dockerfile
~~~

~~~dockerfile
FROM java:8-jre  #基础镜像是根据代码的类型确定。如果是nginx、tomcat等开源服务，一般采用alpine，这是一个精简版几M大小的linux，但是内核和命令等是全的。

MAINTAINER hangxu

COPY target/www-0.0.1-SNAPSHOT,jar /app/www.jar
CMD ["java", "-Xmx200m", "-jar", "/app/www.jar"]

EXPOSE 8088
~~~

~~~sh
docker build -t=test/java:v1 .
#镜像可以传到某个镜像仓库中以供工作节点拉取（docker pull或者ctr -n=k8s.io pull）
~~~

# 部署deployment

~~~yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: java-web-deploy
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
  spec:
    containers:
    - name: web
      image: test/java:v1
      imagePullPolicy: Never
      ports:
      - containerPort: 8088
~~~

# 部署四层代理

~~~yaml
apiVersion: v1
kind: Service
metadata:
  name: java-web-svc
  labels:
    app: web
spec:
  type: NodePort
  selector:
    app: web
  ports:
  - name: http
    port: 8088
    targetPort: 8088
~~~

# 部署七层代理

- 首先部署好ingress-controller，再去创建ingress规则

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: in-tomcat
spec:
  ingressClassName: nginx
  rules:
  - host: java.hangxu.cn
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: java-web-svc
            port:
              number: 8088
~~~

- 创建之后，kubectl get ingress 查看域名绑定的IP地址。在内网环境，配了hosts文件建立域名和IP映射之后，内网浏览器可以直接访问java.hangxu.cn/hello

