# Devops平台建设

## 通用流程

微服务发版的自动化流水线，一般会有如下步骤：

1. 在Gitlab中创建对应的项目，项目名称与微服务名称相同即可。（建议一个微服务对应一个gitlab project）
2. 配置Jenkins集成k8s集群，后期Jenkins的Slave将为在K8s中动态创建的Slave
3. Jenkins创建对应的任务（Job），集成该项目的Git地址和K8s集群。（建议一个微服务对应一个Pipeline）
4. 开发者将代码提交到Gitlab。
5. 如果配置了Webhook，推送代码会自动触发Jenkins构建；如果没有配置Webhook，需要手动选择branch触发。
6. Jenkins控制K8s，创建Jenkins Slave pod
7. Jenkins Slave pod根据Pipeline定义的步骤执行构建，生成交付物
8. 通过Dockerfile生成镜像
9. 将镜像Push到Harbor或其他镜像仓库
10. Jenkins再次控制K8s进行最新的镜像部署
11. 流水线结束，删除Jenkins slave

基本上所有的语言都是类似的流程，可以设计一个通用模板。

## 架构设计

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202509171636477.png" alt="image-20250917163628290" style="zoom:50%;" />

部署这套架构需要的组件：

1. K8s
2. Gitlab（参考[二进制安装Gitlab](./二进制安装Gitlab(17.9.8).md)）
3. Jenkins（参考[docker部署Jenkins](./docker部署Jenkins)或者[helm部署Jenkins](./helm部署jenkins)）
4. Harbor（参考[helm部署harbor](../harbor/helm部署harbor)）

## 工具集成

Harbor的账号密码、Gitlab的私钥、K8s证书均使用Jenkins的Credentials管理。

### harbor用NodePort暴露

1. 如果harbor只用ingress暴露，在jnlp pod里面，kaniko容器用且仅用coreDNS解析ingress域名，导致根本解析不了harbor ingress。

2. 再加上harbor的helm chart不支持同时用ingress和nodePort暴露。
3. 尝试过helm chart用ingress暴露的同时，手动创建nodePort的svc暴露harbor-core，但是这样是不行的。因为helm chart里面用nodePort暴露，会给你创建一个harbor-nginx的pod来作为nodePort svc的后端pod，自己手动无法模拟。

4. 所以必须helm chart里面用nodePort暴露，values配置：

~~~yaml
expose:
  type: nodePort
externalURL: "http://192.168.40.180:32002"
~~~

### 配置harbor用户名密码

1. Manage Jenkins - Credentials - Stores scoped to Jenkins - (global) - Add Credentials

2. Kind选Username with password

3. Username：admin，Password：Harbor12345

4. ID：HARBOR_USER_PASSWD

5. 后面可以在pipeline中这样引用：

   ~~~groovy
   environment { 
   	HARBOR_ACCOUNT = credentials('HARBOR_USER_PASSWD') 
   }
   ~~~

   以上配置会自动生成三个环境变量：

   1. HARBOR_ACCOUNT：包含一个以冒号分隔的用户名和密码，格式为 username:password
   2. HARBOR_ACCOUNT_USR：仅包含用户名的附加变量
   3. HARBOR_ACCOUNT_PSW：仅包含密码的附加变量

### 配置k8s证书

1. 首先需要找到集群中的KUBECONFIG，一般是kubectl节点的`~/.kube/config`文件，或者是`KUBECONFIG环境变量`所指向的文件。

2. 然后把证书文放在Jenkins上的Credentials中：类型选择Secret file，上传文件，设置ID：KUBECONFIG_LOCAL。

3. 接下来可以在pipeline中引用：

~~~groovy
pipeline { 
    agent any 
    environment { 
        KUBECONFIG_LOCAL = credentials('KUBECONFIG_LOCAL') 
    } 
    stages { 
        stage('Secret File') { 
            steps { 
                sh "cat $KUBECONFIG_LOCAL" 
            } 
        } 
    } 
}
~~~

### jenkins和gitlab ssh互信

如果jenkins是docker部署在一台机器上，gitlab二进制部署在另一台机器上：

1. Jenkins机器的ssh公钥：`~/.ssh/~/id_rsa_pub`内容放到gitlab上：
   1. Gitlab进去直接搜SSH Keys，点进去：Add new key
   2. 把文件内容粘过去，点Add即可
2. Jenkins机器的ssh私钥：`~/.ssh/id_rsa`内容放到Jenkins自己的Credentials里面
   1. Jenkins - Manage Jenkins - Credentials - (Global) - Add Credentials
   2. Kind选SSH Username with private key
   3. ID: gitlab-key
   4. Username随便写一个，gitlab-key
   5. Private Key部分直接填Enter directly，把文件内容粘进去
   6. 点Create生成

如果jenkins是部署在k8s里面，gitlab二进制部署在另一台机器上：

- 找一台k8s节点，把节点上的ssh公钥放进Gitlab，私钥放进Jenkins。

### jenkins集成k8s集群

1. 通常情况下，Jenkins Agent会通过Jenkins Master的5000端口与之通信，所以需要开启Agent的5000端口：

   1. Manage Jenkins - Security - Agents - Fixed，50000。（helm部署的Jenkins默认就设置好了；docker部署的需要额外设置）

2. 实际使用时，如果不需要把整个k8s集群的节点都充当创建Jenkins Slave的节点，可以选择一个或几个节点作为创建Slave的节点：

   ~~~sh
   kubectl label node rn1 build=true
   ~~~

3. 添加集群：
   1. Manage Jenkins - Cloud - New Cloud
   2. Cloud Name随便起一个，Type选Kubernetes
   3. 如果是docker部署的jenkins，Jenkins URL填`http://<宿主机 IP>:8080/`，凭据上传已经创建过的kubeconfig credential，就能自动识别出其他k8s配置了。
   4. 如果是k8s helm部署的jenkins，已经有一个创建好的cloud叫kubernetes。

# 自动化流水线设计

## 节点打标签

如果不需要把整个k8s集群的节点都充当创建Jenkins Slave的节点，可以选择一个或几个节点作为创建Slave的节点：

~~~sh
kubectl label node rn1 build=true
~~~

## Workspace持久化

jenkins的workspace给他持久化存储起来。这个存储配置在jenkinsfile的workspaceVolume persistentVolumeClaimWorkspaceVolume字段里面。会自动挂载到jnlp里面。

~~~yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pipeline-workspace-pvc
  namespace: jenkins
spec:
  storageClassName: cfs-sc
  volumeMode: Filesystem
  accessModes:
  - ReadWriteMany
  resources:
    requests:
      storage: 10Gi
~~~

## build缓存持久存储

Jenkins在构建时，会产生一些依赖文件，这些文件最好进行持久化存储，防止重复下载。

创建一个PVC用于流水线工作目录及依赖文件的数据持久化，需要创建到和jenkins master同一个ns里面，这个PVC是jnlp template yaml里面手动挂载进去给build这个contianer用的。

~~~yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pipeline-build-cache-pvc
  namespace: jenkins
spec:
  storageClassName: cfs-sc
  volumeMode: Filesystem
  accessModes:
  - ReadWriteMany
  resources:
    requests:
      storage: 10Gi
~~~

## Kaniko配置文件

Kaniko连接harbor用的配置文件就是docker连接harbor的配置文件。

1. 在有docker客户端的机器上，配置docker连接harbor：

   ~~~sh
   # 配置docker daemon.json
   tee /etc/docker/daemon.json <<'EOF'
   {
    "registry-mirrors":["https://x6j7eqtq.mirror.aliyuncs.com","https://docker.lmirror.top","https://docker.m.daocloud.io", "https://hub.uuuadc.top","https://docker.anyhub.us.kg","https://dockerhub.jobcher.com","https://dockerhub.icu","https://docker.ckyl.me","https://docker.awsl9527.cn","https://docker.laoex.link"],
   "insecure-registries":["harbor.hanxux.local","192.168.40.180:32002"] 
   } 
   EOF
   
   systemctl daemon-reload && systemctl restart docker.service
   ~~~

2. 用docker登录一次harbor，生成一个登录harbor的配置文件：

   ~~~sh
   docker login 192.168.40.180:32002
   # admin/Harbor12345
   ~~~

3. 查看生成的配置文件：

   ~~~sh
   cat ~/.docker/config.json
   ~~~

4. 创建configMap给jnlp pod里面的Kaniko container用

   ~~~sh
   kubectl create cm docker-registry-config --from-file=config.json=/root/.docker/config.json -n jenkins
   ~~~

## 应用的imagePullSecret

k8s集群中的应用deployment需要从harbor拉取镜像，所以需要创建一个给deployment用的harbor secret，创建在应用自己的ns里面：

~~~sh
kubectl create secret docker-registry harborkey --docker-server=192.168.40.180:32002 --docker-username=admin --docker-password=Harbor12345 -n demo
~~~

## Jenkinsfile模板

~~~groovy
pipeline {
  agent {
    kubernetes {
      // 这里改成Jenkins里面配置的Cloud Name
      cloud 'kubernetes'
      slaveConnectTimeout 1200
      // 将workspace改成用PVC，用于持久化工作目录，claimName为创建的PVC名称
      workspaceVolume persistentVolumeClaimWorkspaceVolume(claimName: "pipeline-workspace-pvc", readOnly: false)
      yaml '''
apiVersion: v1
kind: Pod
spec:
  restartPolicy: "Never"
  # 可选，用打了标签的节点作为slave
  nodeSelector:
    build: "true"
  volumes:
  # 保存docker认证信息
  - name: docker-registry-config
    configMap:
      name: docker-registry-config
  - name: "localtime"
    hostPath:
      path: "/usr/share/zoneinfo/Asia/Shanghai"
  # 缓存PVC
  - name: pipeline-build-cache
    persistentVolumeClaim:
      claimName: pipeline-build-cache-pvc
      readonly: false
  containers:
  # jnlp容器,和Jenkins主节点通信
  - name: jnlp
    image: 'registry.cn-beijing.aliyuncs.com/dotbalo/jnlp-agent-docker:latest'
    imagePullPolicy: IfNotPresent
    args: [\'$(JENKINS_SECRET)\', \'$(JENKINS_NAME)\']
    volumeMounts:
    - name: "localtime"
      mountPath: "/etc/localtime"
      readOnly: false
  # build容器,包含执行构建的命令,比如Java需要mvn构建,就可以用一个maven镜像。stage名称和这个容器名称一致。
  - name: "build"
    image: "registry.cn-beijing.aliyuncs.com/dotbalo/maven:3.5.3"
    imagePullPolicy: "IfNotPresent"
    tty: true
    command:
    - "cat"
    env:
    - name: "LANGUAGE"
      value: "en_US:en"
    - name: "LC_ALL"
      value: "en_US.UTF-8"
    - name: "LANG"
      value: "en_US.UTF-8"
    volumeMounts:
    - mountPath: "/etc/localtime"
      name: "localtime"
    # Java编译会把依赖插件装到~/.m2目录下，所以把该目录缓存到PVC。其他语言用类似方式。
    - mountPath: "/root/.m2/"
      name: "pipeline-build-cache"
      readOnly: false
  # 做镜像的容器，可以用docker in docker的方式，或者用kaniko
  - name: "kaniko"
    image: "registry.cn-beijing.aliyuncs.com/dotbalo/kaniko-executor:debug"
    imagePullPolicy: "IfNotPresent"
    tty: true
    command:
    - "sleep"
    args:
    - "99d"
    env:
    - name: "LANGUAGE"
      value: "en_US:en"
    - name: "LC_ALL"
      value: "en_US.UTF-8"
    - name: "LANG"
      value: "en_US.UTF-8"
    volumeMounts:
    - name: "localtime"
      mountPath: "/etc/localtime"
      readOnly: false
    # 挂载docker配置文件，用于Kaniko连接到镜像仓库。Kaniko是自动登录镜像仓库，不用写login之类的命令
    - name: "docker-registry-config"
      mountPath: "/kaniko/.docker"
  # 发版容器，可以用kubectl或者helm的镜像
  - name: "kubectl"
    image: "registry.cn-beijing.aliyuncs.com/dotbalo/kubectl:latest"
    imagePullPolicy: "IfNotPresent"
    tty: true
    command:
    - "cat"
    env:
    - name: "LANGUAGE"
      value: "en_US:en"
    - name: "LC_ALL"
      value: "en_US.UTF-8"
    - name: "LANG"
      value: "en_US.UTF-8"
    volumeMounts:
    - name: "localtime"
      mountPath: "/etc/localtime"
      readOnly: false
'''
    }
  }
  environment {
    HARBOR_ADDRESS = "192.168.40.180:32002" // Harbor地址
    REGISTRY_DIR = "platform-tools-local" // Harbor Project名称
    IMAGE_NAME = "spring-boot-project" // 构建的镜像名称
    NAMESPACE = "demo" // 构建的应用在k8s中的名称空间
    COMMIT_ID = ""
    TAG = "" // 镜像tag，后面用BUILD_TAG+COMMIT_ID的方式生成
    GIT_URL = "git@192.168.40.183:local-k8s-platform-tools/spring-boot-project.git" // gitlab项目的ssh地址
  }
  parameters {
    // 依赖git parameter插件。该字段会在Jenkins页面上显示一个下拉列表，列出所有的分支供选择
    gitParameter(branch: '', branchFilter: 'origin/(.*)', defaultValue: '', description: 'Branch for build and deploy', name: 'BRANCH', quickFilterEnabled: false, selectedValue: 'NONE', sortMode: 'NONE',
tagFilter: '*', type: 'PT_BRANCH')
  }
  stages {
    stage('Pulling Code') {
      parallel {
      // 两个并行stage，因为要考虑到两种触发方式去选择
      // 一种是直接在Jenkins上点构建按钮，这时BRANCH参数有值
      // 另一种是通过gitlab的webhook触发，这时BRANCH参数为空，gitlabBranch环境变量有值
        stage('Pulling Code by Jenkins') {
          when {
            // 假如流水线是手动触发，则env.gitlabBranch为空。执行该stage
            expression {
              env.gitlabBranch == null
            }
          }
          steps {
            // jenkins上保存的ssh私钥credential的名字gitlab-key
            git(changelog: true, poll: true, url: "${GIT_URL}", branch: "${BRANCH}", credentialsId: 'gitlab-key')
            script {
              COMMIT_ID = sh(returnStdout: true, script: "git log -n 1 --pretty=format:'%h'").trim()
              TAG = BUILD_TAG + '-' + COMMIT_ID
              println "Current branch is ${BRANCH}, Commit ID is ${COMMIT_ID}, Image TAG is ${TAG}"
            }
          }
        }
        stage('Pulling Code by trigger') {
          // 假如流水线是被gitlab的webhook触发，env.gitlabBranch有值。执行该stage
          when {
            expression {
              env.gitlabBranch != null
            }
          }
          steps {
            // jenkins上保存的ssh私钥credential的名字gitlab-key
            git(url: "${GIT_URL}", branch: env.gitlabBranch, changelog: true, poll: true, credentialsId: 'gitlab-key')
            script {
              COMMIT_ID = sh(returnStdout: true, script: "git log -n 1 --pretty=format:'%h'").trim()
              TAG = BUILD_TAG + '-' + COMMIT_ID
              println "Current branch is ${env.gitlabBranch}, Commit ID is ${COMMIT_ID}, Image TAG is ${TAG}"
            }
          }
        }
      }
    }
    stage('Building') {
      steps {
        // 使用pod模板中定义的build container
        container(name: 'build') {
          // 编译命令，需要根据实际情况修改
            sh """
              # 检查 settings.xml 是否已存在，不存在则创建
              if [ ! -f /root/.m2/settings.xml ]; then
                echo "Creating settings.xml for Maven mirror..."
                cat <<'EOF' > /root/.m2/settings.xml
<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0 http://maven.apache.org/xsd/settings-1.0.0.xsd">
  <mirrors>
    <mirror>
      <id>aliyunmaven</id>
      <name>aliyun maven</name>
      <url>https://maven.aliyun.com/repository/public</url>
      <mirrorOf>central</mirrorOf>
    </mirror>
  </mirrors>
</settings>
EOF
              fi

              echo "Using custom settings.xml:"
              cat /root/.m2/settings.xml

              echo "Starting Maven build..."
              mvn clean install -DskipTests
              ls target/*
            """
        }
      }
    }
    stage('Build for creating image') {
      steps {
        container(name: 'kaniko') {
          // 用kaniko构建镜像并push到harbor
          sh """
            executor -d ${HARBOR_ADDRESS}/${REGISTRY_DIR}/${IMAGE_NAME}:${TAG} -c . --insecure --skip-tls-verify
          """
        }
      }
    }
    stage('Deploying to K8s') {
      environment {
        // 发布到哪个集群，就用保存好的kubeconfig的credential
        MY_KUBECONFIG = credentials('KUBECONFIG_LOCAL')
      }
      steps {
        container(name: 'kubectl'){
            sh """
            kubectl --kubeconfig $MY_KUBECONFIG set image deploy -l app=${IMAGE_NAME} ${IMAGE_NAME}=${HARBOR_ADDRESS}/${REGISTRY_DIR}/${IMAGE_NAME}:${TAG} -n $NAMESPACE
            """
        }
      }
    }
  }
}
~~~

# 自动化构建Java应用

## 创建Java测试用例

这里用一个示例项目：https://gitee.com/dukuan/spring-boot-project.git。需要导入到gitlab中

1. 找到之前创建的Gitlab Group: local-k8s-platform-tools
2. 点New Project - Import Project - Repository by URL
3. 输入gitee项目的URL，点击导入即可。

## 创建deployment

需要先把deployment创建出来，镜像随便写一个，后面流水线会替换成最新编译出来的镜像

~~~yaml
apiVersion: v1
kind: Service
metadata:
  name: spring-boot-project
  namespace: demo
  labels:
    app: spring-boot-project
spec:
  selector:
    app: spring-boot-project
  type: ClusterIP
  ports:
  - name: web
    port: 8761
    protocol: TCP
    targetPort: 8761

---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: spring-boot-project
  namespace: demo
spec:
  rules:
  - host: spring-boot-project.hanxux.local
    http:
      paths:
      - backend:
          service:
            name: spring-boot-project
            port:
              number: 8761
        path: /
        pathType: ImplementationSpecific

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: spring-boot-project
  namespace: demo
  labels: # deployment label和流水线中的set -l指定的一致
    app: spring-boot-project
spec:
  replicas: 1
  selector:
    matchLabels:
      app: spring-boot-project
  strategy:
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
    type: RollingUpdate
  template:
    metadata:
      labels:
        app: spring-boot-project
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - spring-boot-project
              topologyKey: kubernetes.io/hostname
            weight: 100
      imagePullSecrets:
      - name: harborkey # harbor仓库秘钥，需要和之前创建的secret名称保持一致
      containers:
      - name: spring-boot-project # container名称，需要和流水线中set命令指定的容器名称保持一致
        image: nginx # 一开始先用nginx占位，后续流水线构建完成后替换为实际镜像
        imagePullPolicy: IfNotPresent
        env:
        - name: TZ
          value: Asia/Shanghai
        - name: LANG
          value: C.UTF-8
        ports:
        - name: web
          containerPort: 8761
          protocol: TCP
        livenessProbe:
          failureThreshold: 2
          initialDelaySeconds: 30
          periodSeconds: 10
          successThreshold: 1
          tcpSocket:
            port: 8761
          timeoutSeconds: 2
        readinessProbe:
          failureThreshold: 2
          initialDelaySeconds: 30
          periodSeconds: 10
          successThreshold: 1
          tcpSocket:
            port: 8761
          timeoutSeconds: 2
        resources:
          limits:
            cpu: 994m
            memory: 1170Mi
          requests:
            cpu: 10m
            memory: 55Mi
~~~

创建之后pod可能无法启动，等到流水线创建完成，替换了镜像后就可以了。

## 创建Jenkinsfile

把Jenkins Pipeline文件放到代码仓库中就叫Jenkins Pipeline。

Jenkinsfile 放置于代码仓库中，有以下好处：

1. 方便对流水线上的代码进行复查/迭代；
2. 对管道进行审计跟踪；
3. 流水线真正的源代码能够被项目的多个成员查看和编辑。

在Gitlab源代码中添加一个Jenkinsfile。点击代码首页的+，选Newfile，把上面的jenkinsfile模板粘贴过来保存。注意其中的需要手动改的配置有没有写对。

## 创建Dockerfile

在执行流水线过程时，需要将代码的编译产物做成镜像。本次示例是Java项目，只需要把编译出来的Jar包放在有jre环境的镜像中，然后启动该Jar包即可：

~~~sh
#  基础镜像可以按需修改，可以更改为公司自有镜像 
FROM registry.cn-beijing.aliyuncs.com/dotbalo/jre:8u211-data 
# jar包名称改成实际的名称，本示例为spring-cloud-eureka-0.0.1-SNAPSHOT.jar 
COPY target/spring-cloud-eureka-0.0.1-SNAPSHOT.jar ./ 
# 启动Jar包 
CMD java -jar spring-cloud-eureka-0.0.1-SNAPSHOT.jar 
~~~

同样在gitlab项目中添加这个Dockerfile。注意：Dockerfile必须文件名是Dockerfile，否则Kaniko识别不出来

## 创建Jenkins Job

1. 首页在All右边的+点击创建一个List View类型的View，名称和项目名称一致。

2. 点到这个新创建的View下，左边点击创建Items，创建一个Pipeline，名称一般和Gitlab仓库名称一致，类型为Pipeline。点击ok

3. 在新页面点击Pipeline - Definition: Pipeline Script for SCM - SCM: Git

4. Repository: git@192.168.40.183:local-k8s-platform-tools/spring-boot-project.git

5. Credentials: 选之前配置过的gitlab-key，即jenkins节点服务器私钥。

   > 这一步如果有报错：Host key verification failed. 去Manage Jenkins - Security里面把Host Key Verification Strategy改成No Verification。回去重新创建Pipeline就可以了。

6. Script Path改成项目中的jenkinsfile文件地址

## 运行流水线

第一次构建，没有选择BRANCH的选项，因为第一次还没有拉取代码。第二次就会有了，需要点一下master分支。

# 自动化构建Vue/H5前端应用

其构建方式和自动化构建 Java 基本相同，重点是更改 Deployment、Jenkinsfile 和 Dockerfile 即可。

## 创建测试项目

测试项目地址在：https://gitee.com/dukuan/vue-project.git。需要导入到Gitlab的group中：New Project - Import Project

## 定义deployment

相比Java应用，只需要更改资源名称和端口号即可：

~~~yaml
apiVersion: v1
kind: Service
metadata:
  name: vue-project
  namespace: demo
  labels:
    app: vue-project
spec:
  selector:
    app: vue-project
  type: ClusterIP
  ports:
  - name: web
    port: 80
    protocol: TCP
    targetPort: 80

---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: vue-project
  namespace: demo
spec:
  rules:
  - host: vue-project.hanxux.local
    http:
      paths:
      - backend:
          service:
            name: vue-project
            port:
              number: 80
        path: /
        pathType: ImplementationSpecific

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vue-project
  namespace: demo
  labels: # deployment label和流水线中的set -l指定的一致
    app: vue-project
spec:
  replicas: 1
  selector:
    matchLabels:
      app: vue-project
  strategy:
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
    type: RollingUpdate
  template:
    metadata:
      labels:
        app: vue-project
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - vue-project
              topologyKey: kubernetes.io/hostname
            weight: 100
      imagePullSecrets:
      - name: harborkey # harbor仓库秘钥，需要和之前创建的secret名称保持一致
      containers:
      - name: vue-project # container名称，需要和流水线中set命令指定的容器名称保持一致
        image: nginx # 一开始先用nginx占位，后续流水线构建完成后替换为实际镜像
        imagePullPolicy: IfNotPresent
        env:
        - name: TZ
          value: Asia/Shanghai
        - name: LANG
          value: C.UTF-8
        ports:
        - name: web
          containerPort: 80
          protocol: TCP
        livenessProbe:
          failureThreshold: 2
          initialDelaySeconds: 30
          periodSeconds: 10
          successThreshold: 1
          tcpSocket:
            port: 80
          timeoutSeconds: 2
        readinessProbe:
          failureThreshold: 2
          initialDelaySeconds: 30
          periodSeconds: 10
          successThreshold: 1
          tcpSocket:
            port: 80
          timeoutSeconds: 2
        resources:
          limits:
            cpu: 994m
            memory: 1170Mi
          requests:
            cpu: 10m
            memory: 55Mi
~~~

## 创建Jenkinsfile

创建到仓库根目录。与Java的Jenkinsfile相比，需要更改的地方：

1. build pod的image用node基础镜像
2. 构建命令要用npm
3. 环境变量的代码地址、镜像名称

~~~groovy
pipeline {
  agent {
    kubernetes {
      // 这里改成Jenkins里面配置的Cloud Name
      cloud 'kubernetes'
      slaveConnectTimeout 1200
      // 将workspace改成用PVC，用于持久化工作目录，claimName为创建的PVC名称
      workspaceVolume persistentVolumeClaimWorkspaceVolume(claimName: "pipeline-workspace-pvc", readOnly: false)
      yaml '''
apiVersion: v1
kind: Pod
spec:
  restartPolicy: "Never"
  # 可选，用打了标签的节点作为slave
  nodeSelector:
    build: "true"
  volumes:
  # 保存docker认证信息
  - name: docker-registry-config
    configMap:
      name: docker-registry-config
  - name: "localtime"
    hostPath:
      path: "/usr/share/zoneinfo/Asia/Shanghai"
  # 缓存PVC
  - name: pipeline-build-cache
    persistentVolumeClaim:
      claimName: pipeline-build-cache-pvc
      readonly: false
  containers:
  # jnlp容器,和Jenkins主节点通信
  - name: jnlp
    image: 'registry.cn-beijing.aliyuncs.com/dotbalo/jnlp-agent-docker:latest'
    imagePullPolicy: IfNotPresent
    args: [\'$(JENKINS_SECRET)\', \'$(JENKINS_NAME)\']
    volumeMounts:
    - name: "localtime"
      mountPath: "/etc/localtime"
      readOnly: false
  # build容器,包含执行构建的命令。stage名称和这个容器名称一致。
  - name: "build"
    image: "registry.cn-beijing.aliyuncs.com/dotbalo/node:lts"
    imagePullPolicy: "IfNotPresent"
    tty: true
    command:
    - "cat"
    env:
    - name: "LANGUAGE"
      value: "en_US:en"
    - name: "LC_ALL"
      value: "en_US.UTF-8"
    - name: "LANG"
      value: "en_US.UTF-8"
    volumeMounts:
    - mountPath: "/etc/localtime"
      name: "localtime"
    # Java编译会把依赖插件装到~/.m2目录下，所以把该目录缓存到PVC。其他语言用类似方式。
    - mountPath: "/root/.m2/"
      name: "pipeline-build-cache"
      readOnly: false
  # 做镜像的容器，可以用docker in docker的方式，或者用kaniko
  - name: "kaniko"
    image: "registry.cn-beijing.aliyuncs.com/dotbalo/kaniko-executor:debug"
    imagePullPolicy: "IfNotPresent"
    tty: true
    command:
    - "sleep"
    args:
    - "99d"
    env:
    - name: "LANGUAGE"
      value: "en_US:en"
    - name: "LC_ALL"
      value: "en_US.UTF-8"
    - name: "LANG"
      value: "en_US.UTF-8"
    volumeMounts:
    - name: "localtime"
      mountPath: "/etc/localtime"
      readOnly: false
    # 挂载docker配置文件，用于Kaniko连接到镜像仓库。Kaniko是自动登录镜像仓库，不用写login之类的命令
    - name: "docker-registry-config"
      mountPath: "/kaniko/.docker"
  # 发版容器，可以用kubectl或者helm的镜像
  - name: "kubectl"
    image: "registry.cn-beijing.aliyuncs.com/dotbalo/kubectl:latest"
    imagePullPolicy: "IfNotPresent"
    tty: true
    command:
    - "cat"
    env:
    - name: "LANGUAGE"
      value: "en_US:en"
    - name: "LC_ALL"
      value: "en_US.UTF-8"
    - name: "LANG"
      value: "en_US.UTF-8"
    volumeMounts:
    - name: "localtime"
      mountPath: "/etc/localtime"
      readOnly: false
'''
    }
  }
  environment {
    HARBOR_ADDRESS = "192.168.40.180:32002" // Harbor地址
    REGISTRY_DIR = "platform-tools-local" // Harbor Project名称
    IMAGE_NAME = "vue-project" // 构建的镜像名称
    NAMESPACE = "demo" // 构建的应用在k8s中的名称空间
    COMMIT_ID = ""
    TAG = "" // 镜像tag，后面用BUILD_TAG+COMMIT_ID的方式生成
    GIT_URL = "git@192.168.40.183:local-k8s-platform-tools/vue-project.git" // gitlab项目的ssh地址
  }
  parameters {
    // 依赖git parameter插件。该字段会在Jenkins页面上显示一个下拉列表，列出所有的分支供选择
    gitParameter(branch: '', branchFilter: 'origin/(.*)', defaultValue: '', description: 'Branch for build and deploy', name: 'BRANCH', quickFilterEnabled: false, selectedValue: 'NONE', sortMode: 'NONE',
tagFilter: '*', type: 'PT_BRANCH')
  }
  stages {
    stage('Pulling Code') {
      parallel {
      // 两个并行stage，因为要考虑到两种触发方式去选择
      // 一种是直接在Jenkins上点构建按钮，这时BRANCH参数有值
      // 另一种是通过gitlab的webhook触发，这时BRANCH参数为空，gitlabBranch环境变量有值
        stage('Pulling Code by Jenkins') {
          when {
            // 假如流水线是手动触发，则env.gitlabBranch为空。执行该stage
            expression {
              env.gitlabBranch == null
            }
          }
          steps {
            // jenkins上保存的ssh私钥credential的名字gitlab-key
            git(changelog: true, poll: true, url: "${GIT_URL}", branch: "${BRANCH}", credentialsId: 'gitlab-key')
            script {
              COMMIT_ID = sh(returnStdout: true, script: "git log -n 1 --pretty=format:'%h'").trim()
              TAG = BUILD_TAG + '-' + COMMIT_ID
              println "Current branch is ${BRANCH}, Commit ID is ${COMMIT_ID}, Image TAG is ${TAG}"
            }
          }
        }
        stage('Pulling Code by trigger') {
          // 假如流水线是被gitlab的webhook触发，env.gitlabBranch有值。执行该stage
          when {
            expression {
              env.gitlabBranch != null
            }
          }
          steps {
            // jenkins上保存的ssh私钥credential的名字gitlab-key
            git(url: "${GIT_URL}", branch: env.gitlabBranch, changelog: true, poll: true, credentialsId: 'gitlab-key')
            script {
              COMMIT_ID = sh(returnStdout: true, script: "git log -n 1 --pretty=format:'%h'").trim()
              TAG = BUILD_TAG + '-' + COMMIT_ID
              println "Current branch is ${env.gitlabBranch}, Commit ID is ${COMMIT_ID}, Image TAG is ${TAG}"
            }
          }
        }
      }
    }
    stage('Building') {
      steps {
        // 使用pod模板中定义的build container
        container(name: 'build') {
          // 编译命令，需要根据实际情况修改
            sh """
              npm install --registry=https://registry.npmmirror.com/
              npm run build
            """
        }
      }
    }
    stage('Build for creating image') {
      steps {
        container(name: 'kaniko') {
          // 用kaniko构建镜像并push到harbor
          sh """
            executor -d ${HARBOR_ADDRESS}/${REGISTRY_DIR}/${IMAGE_NAME}:${TAG} -c . --insecure --skip-tls-verify
          """
        }
      }
    }
    stage('Deploying to K8s') {
      environment {
        // 发布到哪个集群，就用保存好的kubeconfig的credential
        MY_KUBECONFIG = credentials('KUBECONFIG_LOCAL')
      }
      steps {
        container(name: 'kubectl'){
            sh """
            kubectl --kubeconfig $MY_KUBECONFIG set image deploy -l app=${IMAGE_NAME} ${IMAGE_NAME}=${HARBOR_ADDRESS}/${REGISTRY_DIR}/${IMAGE_NAME}:${TAG} -n $NAMESPACE
            """
        }
      }
    }
  }
}
~~~

## 创建Dockerfile

创建到仓库根目录。前端应用构建之后一般会在dist目录下产生html文件，只需要拷贝到nginx目录下即可。编译镜像就找一个nginx镜像就行。

~~~sh
FROM registry.cn-beijing.aliyuncs.com/dotbalo/nginx:1.15.12 
COPY dist/* /usr/share/nginx/html/ 
~~~

## 创建jenkins job

直接复制之前Java的pipeline（Create New Item里面最底下Copy from填spring-boot-project即可），只需要变更名称和仓库地址即可。

pipeline创建好之后直接Build。

# 自动化构建Go应用

## 创建测试项目

测试项目地址：https://gitee.com/dukuan/go-project.git。导入到Gitlab中

## 创建deployment

~~~yaml
apiVersion: v1
kind: Service
metadata:
  name: go-project
  namespace: demo
  labels:
    app: go-project
spec:
  selector:
    app: go-project
  type: ClusterIP
  ports:
  - name: web
    port: 8080
    protocol: TCP
    targetPort: 8080

---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: go-project
  namespace: demo
spec:
  rules:
  - host: go-project.hanxux.local
    http:
      paths:
      - backend:
          service:
            name: go-project
            port:
              number: 8080
        path: /
        pathType: ImplementationSpecific

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: go-project
  namespace: demo
  labels: # deployment label和流水线中的set -l指定的一致
    app: go-project
spec:
  replicas: 1
  selector:
    matchLabels:
      app: go-project
  strategy:
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
    type: RollingUpdate
  template:
    metadata:
      labels:
        app: go-project
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - go-project
              topologyKey: kubernetes.io/hostname
            weight: 100
      imagePullSecrets:
      - name: harborkey # harbor仓库秘钥，需要和之前创建的secret名称保持一致
      containers:
      - name: go-project # container名称，需要和流水线中set命令指定的容器名称保持一致
        image: nginx # 一开始先用nginx占位，后续流水线构建完成后替换为实际镜像
        imagePullPolicy: IfNotPresent
        env:
        - name: TZ
          value: Asia/Shanghai
        - name: LANG
          value: C.UTF-8
        ports:
        - name: web
          containerPort: 8080
          protocol: TCP
        livenessProbe:
          failureThreshold: 2
          initialDelaySeconds: 30
          periodSeconds: 10
          successThreshold: 1
          tcpSocket:
            port: 8080
          timeoutSeconds: 2
        readinessProbe:
          failureThreshold: 2
          initialDelaySeconds: 30
          periodSeconds: 10
          successThreshold: 1
          tcpSocket:
            port: 8080
          timeoutSeconds: 2
        resources:
          limits:
            cpu: 994m
            memory: 1170Mi
          requests:
            cpu: 10m
            memory: 55Mi
~~~

## 创建Jenkinsfile

创建到代码仓库根目录。Go项目需要更改的内容是构建容器的镜像、缓存目录、Git地址、项目名称：

~~~groovy
pipeline {
  agent {
    kubernetes {
      // 这里改成Jenkins里面配置的Cloud Name
      cloud 'kubernetes'
      slaveConnectTimeout 1200
      // 将workspace改成用PVC，用于持久化工作目录，claimName为创建的PVC名称
      workspaceVolume persistentVolumeClaimWorkspaceVolume(claimName: "pipeline-workspace-pvc", readOnly: false)
      yaml '''
apiVersion: v1
kind: Pod
spec:
  restartPolicy: "Never"
  # 可选，用打了标签的节点作为slave
  nodeSelector:
    build: "true"
  volumes:
  # 保存docker认证信息
  - name: docker-registry-config
    configMap:
      name: docker-registry-config
  - name: "localtime"
    hostPath:
      path: "/usr/share/zoneinfo/Asia/Shanghai"
  # 缓存PVC
  - name: pipeline-build-cache
    persistentVolumeClaim:
      claimName: pipeline-build-cache-pvc
      readonly: false
  containers:
  # jnlp容器,和Jenkins主节点通信
  - name: jnlp
    image: 'registry.cn-beijing.aliyuncs.com/dotbalo/jnlp-agent-docker:latest'
    imagePullPolicy: IfNotPresent
    args: [\'$(JENKINS_SECRET)\', \'$(JENKINS_NAME)\']
    volumeMounts:
    - name: "localtime"
      mountPath: "/etc/localtime"
      readOnly: false
  # build容器,包含执行构建的命令。stage名称和这个容器名称一致。
  - name: "build"
    image: "registry.cn-beijing.aliyuncs.com/dotbalo/golang:1.15"
    imagePullPolicy: "IfNotPresent"
    tty: true
    command:
    - "cat"
    env:
    - name: "LANGUAGE"
      value: "en_US:en"
    - name: "LC_ALL"
      value: "en_US.UTF-8"
    - name: "LANG"
      value: "en_US.UTF-8"
    volumeMounts:
    - mountPath: "/etc/localtime"
      name: "localtime"
    # Go编译会把依赖装到/go/pkg目录下，所以把该目录缓存到PVC。
    - mountPath: "/go/pkg/"
      name: "pipeline-build-cache"
      readOnly: false
  # 做镜像的容器，可以用docker in docker的方式，或者用kaniko
  - name: "kaniko"
    image: "registry.cn-beijing.aliyuncs.com/dotbalo/kaniko-executor:debug"
    imagePullPolicy: "IfNotPresent"
    tty: true
    command:
    - "sleep"
    args:
    - "99d"
    env:
    - name: "LANGUAGE"
      value: "en_US:en"
    - name: "LC_ALL"
      value: "en_US.UTF-8"
    - name: "LANG"
      value: "en_US.UTF-8"
    volumeMounts:
    - name: "localtime"
      mountPath: "/etc/localtime"
      readOnly: false
    # 挂载docker配置文件，用于Kaniko连接到镜像仓库。Kaniko是自动登录镜像仓库，不用写login之类的命令
    - name: "docker-registry-config"
      mountPath: "/kaniko/.docker"
  # 发版容器，可以用kubectl或者helm的镜像
  - name: "kubectl"
    image: "registry.cn-beijing.aliyuncs.com/dotbalo/kubectl:latest"
    imagePullPolicy: "IfNotPresent"
    tty: true
    command:
    - "cat"
    env:
    - name: "LANGUAGE"
      value: "en_US:en"
    - name: "LC_ALL"
      value: "en_US.UTF-8"
    - name: "LANG"
      value: "en_US.UTF-8"
    volumeMounts:
    - name: "localtime"
      mountPath: "/etc/localtime"
      readOnly: false
'''
    }
  }
  environment {
    HARBOR_ADDRESS = "192.168.40.180:32002" // Harbor地址
    REGISTRY_DIR = "platform-tools-local" // Harbor Project名称
    IMAGE_NAME = "go-project" // 构建的镜像名称
    NAMESPACE = "demo" // 构建的应用在k8s中的名称空间
    COMMIT_ID = ""
    TAG = "" // 镜像tag，后面用BUILD_TAG+COMMIT_ID的方式生成
    GIT_URL = "git@192.168.40.183:local-k8s-platform-tools/go-project.git" // gitlab项目的ssh地址
  }
  parameters {
    // 依赖git parameter插件。该字段会在Jenkins页面上显示一个下拉列表，列出所有的分支供选择
    gitParameter(branch: '', branchFilter: 'origin/(.*)', defaultValue: '', description: 'Branch for build and deploy', name: 'BRANCH', quickFilterEnabled: false, selectedValue: 'NONE', sortMode: 'NONE',
tagFilter: '*', type: 'PT_BRANCH')
  }
  stages {
    stage('Pulling Code') {
      parallel {
      // 两个并行stage，因为要考虑到两种触发方式去选择
      // 一种是直接在Jenkins上点构建按钮，这时BRANCH参数有值
      // 另一种是通过gitlab的webhook触发，这时BRANCH参数为空，gitlabBranch环境变量有值
        stage('Pulling Code by Jenkins') {
          when {
            // 假如流水线是手动触发，则env.gitlabBranch为空。执行该stage
            expression {
              env.gitlabBranch == null
            }
          }
          steps {
            // jenkins上保存的ssh私钥credential的名字gitlab-key
            git(changelog: true, poll: true, url: "${GIT_URL}", branch: "${BRANCH}", credentialsId: 'gitlab-key')
            script {
              COMMIT_ID = sh(returnStdout: true, script: "git log -n 1 --pretty=format:'%h'").trim()
              TAG = BUILD_TAG + '-' + COMMIT_ID
              println "Current branch is ${BRANCH}, Commit ID is ${COMMIT_ID}, Image TAG is ${TAG}"
            }
          }
        }
        stage('Pulling Code by trigger') {
          // 假如流水线是被gitlab的webhook触发，env.gitlabBranch有值。执行该stage
          when {
            expression {
              env.gitlabBranch != null
            }
          }
          steps {
            // jenkins上保存的ssh私钥credential的名字gitlab-key
            git(url: "${GIT_URL}", branch: env.gitlabBranch, changelog: true, poll: true, credentialsId: 'gitlab-key')
            script {
              COMMIT_ID = sh(returnStdout: true, script: "git log -n 1 --pretty=format:'%h'").trim()
              TAG = BUILD_TAG + '-' + COMMIT_ID
              println "Current branch is ${env.gitlabBranch}, Commit ID is ${COMMIT_ID}, Image TAG is ${TAG}"
            }
          }
        }
      }
    }
    stage('Building') {
      steps {
        // 使用pod模板中定义的build container
        container(name: 'build') {
          // 编译命令，需要根据实际情况修改
            sh """
              export GO111MODULE=on
              export CGO_ENABLED=0
              go env -w GOPROXY=https://goproxy.cn,direct
              go build
            """
        }
      }
    }
    stage('Build for creating image') {
      steps {
        container(name: 'kaniko') {
          // 用kaniko构建镜像并push到harbor
          sh """
            executor -d ${HARBOR_ADDRESS}/${REGISTRY_DIR}/${IMAGE_NAME}:${TAG} -c . --insecure --skip-tls-verify
          """
        }
      }
    }
    stage('Deploying to K8s') {
      environment {
        // 发布到哪个集群，就用保存好的kubeconfig的credential
        MY_KUBECONFIG = credentials('KUBECONFIG_LOCAL')
      }
      steps {
        container(name: 'kubectl'){
            sh """
            kubectl --kubeconfig $MY_KUBECONFIG set image deploy -l app=${IMAGE_NAME} ${IMAGE_NAME}=${HARBOR_ADDRESS}/${REGISTRY_DIR}/${IMAGE_NAME}:${TAG} -n $NAMESPACE
            """
        }
      }
    }
  }
}
~~~

## 创建Dockerfile

创建到代码仓库根目录。pipeline agent拉完代码，执行go build编译后，在代码目录会生成一个二进制文件。拷贝到一个linux环境就可以直接执行，所以基础镜像用一个alpine或者其他小镜像即可。

~~~sh
FROM registry.cn-beijing.aliyuncs.com/dotbalo/alpine-glibc:alpine-3.9 

# 如果定义了单独的配置文件，可能需要拷贝到镜像中 
# COPY conf/  ./conf  

# 包名按照实际情况进行修改 
COPY ./go-project ./ 

# 启动该应用 
ENTRYPOINT [ "./go-project"] 
~~~

## 创建jenkins job

复制前面的流水线即可。修改名称和git仓库地址。

# Webhook自动触发构建

之前都是手动点击来开始构建的，比较低效。推荐按需配置自动触发构建。即提交代码之后自动触发Jenkins进行构建任务。

用上面的Go项目作为示例。

## Jenkins配置

1. 找到Go项目的Job - Configure - Triggers - Build when a change is pushed to Gitlab:
   - 只勾选Push Events
2. Advanced里面：
   - 勾选**Enable ci-skip**：非常好用的配置，建议开启。对于一些添加注释、修改文档的commit，不需要启动构建。在commit -m里面用“ci-skip”开头，就能不触发构建。比如git commit -m “ci-skip Edit README”
   - 勾选**Ignore WIP Merge Requests**：在开了PR出发构建的情况下，PR message带着WIP开头，也不会触发自动构建。
3. Allowed branches - Filter by regex - Source Branch Regex：master - Target Branch Regex：master
4. 点击Generate生成触发Token
5. 点击Save
6. 复制webhook URL:
   - Build when a change is pushed to Gitlab. GitLab webhook URL: http://jenkins.hanxux.local/project/go-project
7. 复制webhook token

## Gitlab配置

1. gitlab go-project仓库中 - Settings - Webhooks - Add new webhook
2. URL写上面复制的webhook URL，secret token写刚复制的webhook token
3. Trigger - Push Events - All Branches
4. Add webhook

### 故障解决

1。 如果添加webhook时报错invalid url token，需要在gitlab - admin - settings - network - Outbound requests里面打开允许触发外部接口：

- Allow requests to the local network from webhooks and integrations
- Allow requests to the local network from system hooks

2. 在本次实验中，jenkins部署在k8s集群中，用ingress域名暴露；gitlab部署在内网另一台机器上。需要在gitlab机器上添加jenkins域名解析。否则会报错no route to host：

   ~~~sh
   tee -a /etc/hosts <<'EOF'
   192.168.40.180 jenkins.hanxux.local
   EOF
   ~~~

## 触发构建测试

可以在gitlab webhook界面点击Test - Push Events，回到Jenkins开是否触发了构建。

# 一次构建多次部署

同一个项目在企业内一般有多个环境需要部署，而一般在dev环境构建出来的镜像，在UAT、prod等环境不需要重新编译打包，因为比较耗时。直接就用dev编译好的镜像发版就行了。

这个过程，需要Jenkins从Harbor获取到Image tag参数，以供用户选择。

## 创建Pipeline

1. 新建Job，name：go-project-uat，类型为Pipeline
2. 页面的General - This project is parameterized - Image Tag Parameter：
   - Name：IMAGE_TAG
   - Image Name填harbor项目名称/镜像名称：platform-tools-local/go-project
   - Tag Filter Pattern: .*
   - Default Tag: latest
   - Description: Choose the image to be deployed
3. 点击Advanced：
   - Registry URL填Harbor地址：http://192.168.40.180:32002
   - Registry Credential ID选添加过的Harbor用户名密码Credential
   - Verify URL取消勾选

## 创建Jenkinsfile

直接粘贴到pipeline里面Save。

由于镜像已经存在，这里只需要一个jnlp容器和jenkins master通信，一个发版容器kubectl部署到集群。

~~~groovy
pipeline {
    agent {
        kubernetes {
        cloud 'kubernetes'
        slaveConnectTimeout 1200
        yaml '''
apiVersion: v1
kind: Pod
spec:
  restartPolicy: "Never"
  containers:
  # 只需要配置jnlp和kubectl镜像即可
  - name: jnlp
    image: 'registry.cn-beijing.aliyuncs.com/dotbalo/jnlp-agent-docker:latest'
    imagePullPolicy: IfNotPresent
    args: [\'$(JENKINS_SECRET)\', \'$(JENKINS_NAME)\']
  - name: "kubectl"
    image: "registry.cn-beijing.aliyuncs.com/dotbalo/kubectl:latest"
    imagePullPolicy: "IfNotPresent"
    tty: true
    command:
    - "cat"
    env:
    - name: "LANGUAGE"
      value: "en_US:en"
    - name: "LC_ALL"
      value: "en_US.UTF-8"
    - name: "LANG"
      value: "en_US.UTF-8"
'''
        }
    }
    environment {
        HARBOR_ADDRESS = "192.168.40.180:32002"
        NAMESPACE = "demo"
        IMAGE_NAME = "go-project"
        TAG = ""
    }
    stages {
        stage('Deploy') {
            environment {
                MY_KUBECONFIG = credentials('KUBECONFIG_LOCAL')
            }
            steps {
                container(name: 'kubectl'){
                    sh """
                        echo ${IMAGE_TAG} # 该变量即为前台选择的镜像
                        kubectl --kubeconfig=${MY_KUBECONFIG} -n ${NAMESPACE} set image deployment -l app=${IMAGE_NAME} ${IMAGE_NAME}=${HARBOR_ADDRESS}/${IMAGE_TAG}
                        kubectl --kubeconfig=${MY_KUBECONFIG} get po  -l app=${IMAGE_NAME} -n ${NAMESPACE} -w
                    """
                }
            }
        }
    }
}
~~~

保存之后回到Build witr Parameters即可看到IMAGE_TAG的选择框里面可供选择的镜像。

（注意如果提示HTTP Unauthorized，回到Configure - This project is parameterized，查看harbor的image Name是不是被自动变成`- platform-tools-local/go-project -`）把前后的空格和-删掉。）

# 集成Helm发布

## 创建Helm模板

以前面的Go项目为例，改造成helm项目：

~~~sh
helm create chart-template
~~~

在template自动生成的这一套模板上稍微改改就能直接用了：

~~~yaml
# values.yaml中
imagePullSecrets:
- name: harborkey

serviceAccount:
  create: false

service:
  type: ClusterIP
  port: 8080

ingress:
  enabled: false
  className: "nginx-default"
  annotations:
  hosts:
    - host: go-project.hanxux.local
      paths:
        - path: /
          pathType: ImplementationSpecific
  tls: []

resources:
  limits:
    cpu: 200m
    memory: 128Mi
  requests:
    cpu: 100m
    memory: 64Mi
    
livenessProbe:
  tcpSocket:
    port: http
readinessProbe:
  tcpSocket:
    port: http

# Chart.yaml
apiVersion: v2
name: go-project
description: A Helm Chart for a demo Go Project
type: application
version: 0.1.0
appVersion: "0.1.0"
~~~

template里面的资源定义不用动，后面用helm upgrade的时候--set生成。

## 上传到gitlab仓库

~~~sh
# 找一台能从gitlab拉代码的机器（配置了ssh互信）
mkdir go-project-gitlab
cd go-project-gitlab
git init
git pull --rebase git@192.168.40.183:local-k8s-platform-tools/go-project.git
cp -rp ../chart/ ./
git config --global user.email "rm1@example.com"
git config --global user.name "rm1"
git remote add origin git@192.168.40.183:local-k8s-platform-tools/go-project.git
git add .
git cimmit -am "add chart"
git push origin main
~~~

## 创建Jenkinsfile

需要把发版容器的镜像改成helm镜像，把发版命令改成helm upgrade

~~~groovy
pipeline {
  agent {
    kubernetes {
      // 这里改成Jenkins里面配置的Cloud Name
      cloud 'kubernetes'
      slaveConnectTimeout 1200
      // 将workspace改成用PVC，用于持久化工作目录，claimName为创建的PVC名称
      workspaceVolume persistentVolumeClaimWorkspaceVolume(claimName: "pipeline-workspace-pvc", readOnly: false)
      yaml '''
apiVersion: v1
kind: Pod
spec:
  restartPolicy: "Never"
  # 可选，用打了标签的节点作为slave
  nodeSelector:
    build: "true"
  volumes:
  # 保存docker认证信息
  - name: docker-registry-config
    configMap:
      name: docker-registry-config
  - name: "localtime"
    hostPath:
      path: "/usr/share/zoneinfo/Asia/Shanghai"
  # 缓存PVC
  - name: pipeline-build-cache
    persistentVolumeClaim:
      claimName: pipeline-build-cache-pvc
      readonly: false
  containers:
  # jnlp容器,和Jenkins主节点通信
  - name: jnlp
    image: 'registry.cn-beijing.aliyuncs.com/dotbalo/jnlp-agent-docker:latest'
    imagePullPolicy: IfNotPresent
    args: [\'$(JENKINS_SECRET)\', \'$(JENKINS_NAME)\']
    volumeMounts:
    - name: "localtime"
      mountPath: "/etc/localtime"
      readOnly: false
  # build容器,包含执行构建的命令。stage名称和这个容器名称一致。
  - name: "build"
    image: "registry.cn-beijing.aliyuncs.com/dotbalo/golang:1.15"
    imagePullPolicy: "IfNotPresent"
    tty: true
    command:
    - "cat"
    env:
    - name: "LANGUAGE"
      value: "en_US:en"
    - name: "LC_ALL"
      value: "en_US.UTF-8"
    - name: "LANG"
      value: "en_US.UTF-8"
    volumeMounts:
    - mountPath: "/etc/localtime"
      name: "localtime"
    # Go编译会把依赖装到/go/pkg目录下，所以把该目录缓存到PVC。
    - mountPath: "/go/pkg/"
      name: "pipeline-build-cache"
      readOnly: false
  # 做镜像的容器，可以用docker in docker的方式，或者用kaniko
  - name: "kaniko"
    image: "registry.cn-beijing.aliyuncs.com/dotbalo/kaniko-executor:debug"
    imagePullPolicy: "IfNotPresent"
    tty: true
    command:
    - "sleep"
    args:
    - "99d"
    env:
    - name: "LANGUAGE"
      value: "en_US:en"
    - name: "LC_ALL"
      value: "en_US.UTF-8"
    - name: "LANG"
      value: "en_US.UTF-8"
    volumeMounts:
    - name: "localtime"
      mountPath: "/etc/localtime"
      readOnly: false
    # 挂载docker配置文件，用于Kaniko连接到镜像仓库。Kaniko是自动登录镜像仓库，不用写login之类的命令
    - name: "docker-registry-config"
      mountPath: "/kaniko/.docker"
  # 发版容器，可以用kubectl或者helm的镜像
  - name: "helm"
    image: "registry.cn-beijing.aliyuncs.com/dotbalo/helm:latest"
    imagePullPolicy: "IfNotPresent"
    tty: true
    command:
    - "cat"
    env:
    - name: "LANGUAGE"
      value: "en_US:en"
    - name: "LC_ALL"
      value: "en_US.UTF-8"
    - name: "LANG"
      value: "en_US.UTF-8"
    volumeMounts:
    - name: "localtime"
      mountPath: "/etc/localtime"
      readOnly: false
'''
    }
  }
  environment {
    HARBOR_ADDRESS = "192.168.40.180:32002" // Harbor地址
    REGISTRY_DIR = "platform-tools-local" // Harbor Project名称
    IMAGE_NAME = "go-project" // 构建的镜像名称
    NAMESPACE = "demo" // 构建的应用在k8s中的名称空间
    COMMIT_ID = ""
    TAG = "" // 镜像tag，后面用BUILD_TAG+COMMIT_ID的方式生成
    GIT_URL = "git@192.168.40.183:local-k8s-platform-tools/go-project.git" // gitlab项目的ssh地址
  }
  parameters {
    // 依赖git parameter插件。该字段会在Jenkins页面上显示一个下拉列表，列出所有的分支供选择
    gitParameter(branch: '', branchFilter: 'origin/(.*)', defaultValue: '', description: 'Branch for build and deploy', name: 'BRANCH', quickFilterEnabled: false, selectedValue: 'NONE', sortMode: 'NONE',
tagFilter: '*', type: 'PT_BRANCH')
  }
  stages {
    stage('Pulling Code') {
      parallel {
      // 两个并行stage，因为要考虑到两种触发方式去选择
      // 一种是直接在Jenkins上点构建按钮，这时BRANCH参数有值
      // 另一种是通过gitlab的webhook触发，这时BRANCH参数为空，gitlabBranch环境变量有值
        stage('Pulling Code by Jenkins') {
          when {
            // 假如流水线是手动触发，则env.gitlabBranch为空。执行该stage
            expression {
              env.gitlabBranch == null
            }
          }
          steps {
            // jenkins上保存的ssh私钥credential的名字gitlab-key
            git(changelog: true, poll: true, url: "${GIT_URL}", branch: "${BRANCH}", credentialsId: 'gitlab-key')
            script {
              COMMIT_ID = sh(returnStdout: true, script: "git log -n 1 --pretty=format:'%h'").trim()
              TAG = BUILD_TAG + '-' + COMMIT_ID
              println "Current branch is ${BRANCH}, Commit ID is ${COMMIT_ID}, Image TAG is ${TAG}"
            }
          }
        }
        stage('Pulling Code by trigger') {
          // 假如流水线是被gitlab的webhook触发，env.gitlabBranch有值。执行该stage
          when {
            expression {
              env.gitlabBranch != null
            }
          }
          steps {
            // jenkins上保存的ssh私钥credential的名字gitlab-key
            git(url: "${GIT_URL}", branch: env.gitlabBranch, changelog: true, poll: true, credentialsId: 'gitlab-key')
            script {
              COMMIT_ID = sh(returnStdout: true, script: "git log -n 1 --pretty=format:'%h'").trim()
              TAG = BUILD_TAG + '-' + COMMIT_ID
              println "Current branch is ${env.gitlabBranch}, Commit ID is ${COMMIT_ID}, Image TAG is ${TAG}"
            }
          }
        }
      }
    }
    stage('Building') {
      steps {
        // 使用pod模板中定义的build container
        container(name: 'build') {
          // 编译命令，需要根据实际情况修改
            sh """
              export GO111MODULE=on
              export CGO_ENABLED=0
              go env -w GOPROXY=https://goproxy.cn,direct
              go build
            """
        }
      }
    }
    stage('Build for creating image') {
      steps {
        container(name: 'kaniko') {
          // 用kaniko构建镜像并push到harbor
          sh """
            executor -d ${HARBOR_ADDRESS}/${REGISTRY_DIR}/${IMAGE_NAME}:${TAG} -c . --insecure --skip-tls-verify
          """
        }
      }
    }
    stage('Deploying to K8s') {
      environment {
        // 发布到哪个集群，就用保存好的kubeconfig的credential
        MY_KUBECONFIG = credentials('KUBECONFIG_LOCAL')
      }
      steps {
        container(name: 'helm'){
            sh """
                cd chart
                helm upgrade \
                --kubeconfig $MY_KUBECONFIG \
                --install $IMAGE_NAME . \
                --namespace ${NAMESPACE} \
                --create-namespace \
                --set fullnameOverride=$IMAGE_NAME \
                --set nameOverride=$IMAGE_NAME \
                --set replicaCount=1 \
                --set image.repository=${HARBOR_ADDRESS}/${REGISTRY_DIR}/${IMAGE_NAME} \
                --set image.tag=${TAG}
            """
        }
      }
    }
  }
}
~~~

