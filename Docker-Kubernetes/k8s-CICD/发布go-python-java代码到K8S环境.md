# 发布go代码到k8s-示例1

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
#设置代理，是为了下载依赖包更快一些
go env -w GOPROXY=https://goproxy.cn,direct
#拉取依赖包
go mod tidy
#构建源码
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o go-k8sdemo main.go
#直接运行程序
./go-k8sdemo
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

# 发布go代码到k8s-示例2

## 准备源码和镜像

- 准备源码

~~~sh
mkdir go-game
cd go-game
~~~

~~~go
tee main.go <<'EOF' 
package main

import (
	"fmt"
	"math/rand"
	"time"
)

const maxGuesses = 10

func main() {
	rand.Seed(time.Now().UnixNano())
	number := rand.Intn(100) + 1

	fmt.Println("I'm thinking of a number between 1 and 100.")
	fmt.Printf("You have %d guesses.\n", maxGuesses)

	for guesses := 1; guesses <= maxGuesses; guesses++ {
		fmt.Printf("Guess #%d: ", guesses)
		var guess int
		_, err := fmt.Scanln(&guess)
		if err != nil {
			fmt.Println("Invalid input. Please enter an integer.")
			continue
		}
		if guess < 1 || guess > 100 {
			fmt.Println("Invalid input. Please enter a number between 1 and 100.")
			continue
		}
		if guess < number {
			fmt.Println("Too low.")
		} else if guess > number {
			fmt.Println("Too high.")
		} else {
			fmt.Printf("Correct! You guessed the number in %d guesses.\n", guesses)
			return
		}
	}

	fmt.Printf("Sorry, you did not guess the number. It was %d.\n", number)
}
EOF
~~~

- 构建go源码

~~~sh
go mod init test
#设置代理
go env -w GOPROXY=https://goproxy.cn,direct
go mod tidy
#构建源码
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o k8s-demo main.go
~~~

- 制作镜像

~~~sh
tee dockerfile <<'EOF' 
FROM alpine
WORKDIR /app
COPY k8s-demo /app
CMD ["/bin/sh","-c","./k8s-demo"]
EOF
~~~

~~~sh
docker build -t docker.io/library/k8sgame:v1 .
docker save -o k8sgame.tar.gz docker.io/library/k8sgame:v1
#上传到工作节点并解压
~~~

## 创建pod

~~~yaml
tee deployment.yaml <<'EOF' 
apiVersion: apps/v1
kind: Deployment
metadata:
  name: guess-game
spec:
  replicas: 1
  selector:
    matchLabels:
      app: guess-game
  template:
    metadata:
      labels:
        app: guess-game
    spec:
      containers:
      - name: guess-game
        image: docker.io/library/k8sgame:v1
        imagePullPolicy: IfNotPresent
        command: ["/bin/sh","-c","sleep 3600"] #pod自己没定义前台程序，所以写一个前台保持程序
EOF

#服务没暴露，只能进入pod访问
kubectl exec -it guess-game-6c9b4df786-892ds -- /bin/sh
~~~

# 发布python代码到k8s

## 准备源码和镜像

~~~sh
tar -zxvf hello-python.tar.gz
cd /root/hello-python/app
#备注：requirements.txt文件包含main.py所需的包列表，pip将使用它来安装Flask库。
~~~

~~~python
#main.py 在页面正中央显示大字hello from python!
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return '''
    <html>
        <head>
            <style>
                body {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    font-size: 3em;
                }
            </style>
        </head>
        <body>
            <div>Hello from Python!</div>
        </body>
    </html>
    '''

if __name__ == "__main__":
    app.run(host='0.0.0.0')
~~~

~~~sh
#requirements.txt
Flask
~~~

~~~sh
#dockerfile 使用精简基础镜像，减小image体积
FROM python:3.7-slim

WORKDIR /app
COPY requirements.txt .

RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python", "main.py"]
~~~

- 构建镜像并上传到harbor

~~~sh
docker build  -t hello-python:v1 .
docker tag hello-python:v1 172.16.183.74/go-test/py-k8sdemo:v1
docker push 172.16.183.74/go-test/py-k8sdemo:v1
~~~

## yaml文件部署

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

## helm chart部署

~~~yaml
# Chart.yaml
apiVersion: v2
name: hello-python
description: Custom Helm chart for a demo python app
type: application
version: 1.0.0
appVersion: "1.0.0"
~~~

- valus.yaml可以先保持空的
- templates目录下面放上面的deployment和service文件

~~~sh
helm upgrade -i hello-python-demo -n devops-agent-management .
~~~

# 发布java代码到k8s

~~~sh
yum install maven* -y
yum install git -y
git clone https://gitee.com/hanxianchao66/SpringBootDemo
cd SpringBootDemo/
~~~

## 编译代码

~~~sh
mvn clean package
cd /target
#编译成功之后一般会在target目录下生成一个jar包，本地运行的话直接java -jar xxx.jar就跑起来了
~~~

## 打包镜像

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

## 部署deployment

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

## 部署四层代理

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

## 部署七层代理

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

