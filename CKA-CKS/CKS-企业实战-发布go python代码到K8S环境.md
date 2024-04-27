# 发布go代码到k8s

## 部署go源码和镜像

- 安装go

~~~sh
#centos7上
yum install go -y
~~~

- 创建源码

~~~sh
mkdir go-test
cd go-test/
vim main.go 
~~~

~~~go
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
~~~

- Go mod初始化项目


```sh
go mod init go-test
#设置代理
go env -w GOPROXY=https://goproxy.cn,direct
#拉取依赖包
go mod tidy
#构建源码
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o go-k8sdemo main.go
```

- 编写dockerfile文件

```dockerfile
vim Dockerfile 

FROM alpine
ADD go-k8sdemo /data/app/
WORKDIR /data/app/
CMD ["/bin/sh","-c","./go-k8sdemo"]
```

- 构建镜像


```sh
docker build -t go-test/go-k8sdemo:v1 .
```

- 打包镜像，传到harbor

```sh
docker save -o go-k8sdemo.tar.gz go-test/go-k8sdemo:v1
scp go-k8sdemo.tar.gz node1:/root/
#在xianchaonode1节点解压镜像
docker load -i go-k8sdemo.tar.gz
#上传到harbor
docker login 172.16.183.74 #harbor虚机suspend重启之后需要重新install harbor
docker tag go-test/go-k8sdemo:v1 172.16.183.74/go-test/go-k8sdemo:v1
docker push 172.16.183.74/go-test/go-k8sdemo:v1
```

## 部署pod

- 创建yaml文件

~~~yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: go-k8s-demo
  namespace: default
  labels:
    app: go-k8s-demo
spec:
  selector:
    matchLabels:
      app: go-k8s-demo
  replicas: 1
  template:
    metadata:
      labels:
        app: go-k8s-demo
    spec:
      containers:
        - image: 172.16.183.74/go-test/go-k8sdemo:v1
          imagePullPolicy: IfNotPresent
          name: go-k8s-demo
          ports:
            - containerPort: 8080
              protocol: TCP
          resources:
            limits:
              cpu: 100m
              memory: 100Mi
            requests:
              cpu: 50m
              memory: 50Mi
          livenessProbe:
            tcpSocket:
              port: 8080
            initialDelaySeconds: 10
            timeoutSeconds: 3
          readinessProbe:
            httpGet:
              path: /
              port: 8080
            initialDelaySeconds: 10
            timeoutSeconds: 2
---
apiVersion: v1
kind: Service
metadata:
  name: svc-k8s-demo
  namespace: default
  labels:
    app: go-k8s-demo
spec:
  type: NodePort
  ports:
    - name: api
      port: 8080
      protocol: TCP
      targetPort: 8080
  selector:
    app: go-k8s-demo
~~~

- 访问node物理机IP加物理机端口

~~~sh
curl 172.16.183.76:30835
#{"status":"success~welcome to study"}
~~~

# 发布python代码到k8s

- 准备源码

~~~sh
tar -zxvf hello-python.tar.gz
cd /root/hello-python/app
#备注：requirements.txt文件包含main.py所需的包列表，pip将使用它来安装Flask库。
~~~

~~~python
#main.py
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello from Python!"

if __name__ == "__main__":
    app.run(host='0.0.0.0')
    
#requirements.txt
Flask
~~~

~~~dockerfile
FROM python:3.7
RUN mkdir /app 
WORKDIR /app 
ADD . /app/ 
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python","/app/main.py"]
~~~

（1）从Docker Hub获取3.7版本的官方Python基本镜像。
（2）在镜像中，创建一个名为app的目录。
（3）将工作目录设置为新的app目录。
（4）将本地目录的内容复制到该新文件夹，并将其复制到镜像中。
（5）运行pip安装程序（就像我们前面做的那样），将需求拉入镜像中。
（6）通知Docker容器监听端口5000。
（7）配置启动命令，使其在容器启动时使用。

- 构建镜像并上传到harbor

~~~sh
docker build  -t hello-python:v1 .
docker tag hello-python:v1 172.16.183.74/go-test/py-k8sdemo:v1
docker push 172.16.183.74/go-test/py-k8sdemo:v1
~~~

- 创建yaml文件

~~~yaml
apiVersion: v1
kind: Service
metadata:
  name: svc-hello-python
spec:
  selector:
    app: hello-python
  ports:
  - protocol: "TCP"
    port: 6000
    targetPort: 5000
  type: NodePort

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hello-python
spec:
  selector:
    matchLabels:
     app: hello-python
  replicas: 1
  template:
    metadata:
      labels:
        app: hello-python
    spec:
      containers:
      - name: hello-python
        image: 172.16.183.74/go-test/py-k8sdemo:v1
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 5000
~~~

- 访问node物理机IP加物理机端口

~~~sh
curl 172.16.183.76:30608
#Hello from Python!
~~~

