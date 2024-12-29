# DevOps

## 持续集成-CI

- 持续集成强调开发人员提交了新代码之后，立刻自动的进行构建、（单元）测试。根据测试结果，我们可以确定新代码和原有代码能否正确地集成在一起。持续集成过程中很重视自动化测试验证结果，对可能出现的一些问题进行预警，以保障最终合并的代码没有问题。
- 常见的持续集成工具：Jenkins、Gitlab CI

## 持续交付

- 持续交付在持续集成的基础上，将集成后的代码部署到更贴近真实运行环境的「类生产环境」（production-like environments）中。交付给质量团队或者用户，以供评审。如果评审通过，代码就进入生产阶段。
- 如果所有的代码完成之后一起交付，会导致很多问题爆发出来，解决起来很麻烦，所以持续集成，也就是没更新一次代码，都向下交付一次，这样可以及时发现问题，及时解决，防止问题大量堆积。

## 持续部署

- 持续部署是指当交付的代码通过评审之后，自动部署到生产环境中。持续部署是持续交付的最高阶段。

- Puppet，SaltStack和Ansible是这个阶段使用的流行工具。

  ![image-20240203174605239](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402031746374.png)

# Jenkins基础

## jenkins pipeline介绍

Jenkins pipeline （流水线）是一套运行于jenkins上的工作流框架，将原本独立运行于单个或者多个节点的任务连接起来，实现单个任务难以完成的复杂流程编排与可视化。它把持续提交流水线（Continuous Delivery Pipeline）的任务集成到Jenkins中。**pipeline 是jenkins2.X 最核心的特性，帮助jenkins实现从CI到CD与DevOps的转变。**

- Jenkins Pipeline是一组插件，让Jenkins可以实现持续交付管道的落地和实施。
- 持续交付管道(CD Pipeline)是将软件从版本控制阶段到交付给用户或客户的完整过程的自动化表现。
- 软件的每一次更改（提交到源代码管理系统）都要经过一个复杂的过程才能被发布。

## jenkins语法

- pipeline支持两种语法：Declarative声明式、Scripted pipeline脚本式
  - 声明式pipeline语法，官网：https://www.jenkins.io/doc/book/pipeline/syntax/

### 声明式语法

- 包括以下核心流程：

  - pipeline : 声明其内容为一个声明式的pipeline脚本
  - agent: 连接到jenkins controller的实例，可以是VM、container等
    - node：A machine which is part of the Jenkins environment and capable of executing [Pipelines](https://www.jenkins.io/doc/book/glossary/#pipeline) or [jobs](https://www.jenkins.io/doc/book/glossary/#job). Both the [Controller](https://www.jenkins.io/doc/book/glossary/#controller) and [Agents](https://www.jenkins.io/doc/book/glossary/#agent) are considered to be Nodes. 即执行节点（job运行的slave或者master节点）
  - stages: 阶段集合，包裹所有的阶段（例如：打包，部署等各个阶段）
  - stage: 阶段，被stages包裹，一个stages可以有多个stage
  - steps: 步骤,为每个阶段的最小执行单元,被stage包裹
  - post:  执行构建后的操作，根据构建结果来执行对应的操作

  ~~~groovy
  pipeline{ //作用域，应用于全局最外层，表明该脚本为声明式pipeline
      agent any //运行在任意的可用节点上
      stages{
          stage("This is first stage"){
              steps("This is first step"){
                  echo "I am xianchao"
              }
          }
      }
      post{
          always{
              echo "The process is ending"
          }
      }
  }
  ~~~

### environment

- environment指令指定一系列键值对，这些键值对将被定义为所有step或stage-specific step的环境变量，具体取决于environment指令在Pipeline中的位置。
- 该指令支持一种特殊的方法credentials()，可以通过其在Jenkins环境中的标识符来访问预定义的凭据。
- 对于类型为“Secret Text”的凭据，该 credentials()方法将确保指定的环境变量包含Secret Text内容；对于“标准用户名和密码”类型的凭证，指定的环境变量将被设置为username:password并且将自动定义两个附加的环境变量：`MYVARNAME_USR`和`MYVARNAME_PSW`。

~~~groovy
pipeline {
    agent any
    environment {  
        CC = 'clang' 
    }
    stages {
        stage('Example') {
            steps {
                sh 'printenv'
            }
        }
    }
}
~~~

### options

- options指令允许在Pipeline本身内配置Pipeline专用选项。Pipeline本身提供了许多选项，例如buildDiscarder，但它们也可能由插件提供，例如 timestamps。

- 可用指令：

  - buildDiscarder： pipeline保持构建的最大个数。用于保存Pipeline最近几次运行的数据，例如：options { buildDiscarder(logRotator(numToKeepStr: '1')) }
  - disableConcurrentBuilds：不允许并行执行Pipeline,可用于防止同时访问共享资源等。例如：options { disableConcurrentBuilds() }
  - skipDefaultCheckout：跳过默认设置的代码check out。例如：options { skipDefaultCheckout() }
  - skipStagesAfterUnstable：一旦构建状态进入了“Unstable”状态，就跳过此stage。例如：options { skipStagesAfterUnstable() }
  - timeout：设置Pipeline运行的超时时间，超过超时时间，job会自动被终止，例如：options { timeout(time: 1, unit: 'HOURS') }
  - retry：失败后，重试整个Pipeline的次数。例如：options { retry(3) }
  - timestamps： 预定义由Pipeline生成的所有控制台输出时间。例如：options { timestamps() }

  ~~~groovy
  pipeline {
      agent any
      options {
          timeout(time: 1, unit: 'HOURS') 
      }
      stages {
          stage('Example') {
              steps {
                  echo 'Hello World'
              }
          }
      }
  }　
  ~~~

### parameters

- parameters指令提供用户在触发Pipeline时的参数列表。这些参数值通过该params对象可用于Pipeline stage中，作用域：被最外层pipeline所包裹，并且只能出现一次，参数可被全局使用

  ~~~groovy
  pipeline{
      agent any
      parameters {
          string(name: 'xianchao', defaultValue: 'my name is xianchao', description: 'My name is xiancaho')
          booleanParam(name: 'luckylucky421302', defaultValue: true, description: 'This is my wechat')
      }
      stages{
          stage("stage1"){
              steps{
                  echo "$xianchao"
                  echo "$luckylucky421302"
              }
          }
      }
  } //构建的时候选择build with paramaters，否则识别不了parameter
  ~~~

### triggers

- triggers指令定义了Pipeline自动化触发的方式。目前有三个可用的触发器：cron和pollSCM和upstream。
- 被pipeline包裹，在符合条件下自动触发pipeline

### tools

- 通过tools可自动安装工具，并放置环境变量到PATH。如果agent none，这将被忽略。
- 支持的tools：maven、jdk、gradle

~~~groovy
pipeline {
    agent any
    tools {
       //工具名称必须在Jenkins 管理Jenkins → 全局工具配置中预配置。
        maven 'apache-maven-3.0.1'
    }
    stages {
        stage('Example') {
            steps {
                sh 'mvn --version'
            }
        }
    }
}
~~~

### input

- stage 的 input 指令允许你使用 input step提示输入。
- 在应用了 options 后，进入 stage 的 agent 或评估 when 条件前，stage 将暂停。如果 input 被批准, stage 将会继续。
- 作为 input 提交的一部分的任何参数都将在环境中用于其他 stage
- 参数
  - message：必需的。 这将在用户提交 input 时呈现给用户。
  - id：input 的可选标识符， 默认为 stage 名称。
  - ok：`input`表单上的"ok" 按钮的可选文本。
  - submitter：可选的以逗号分隔的用户列表或允许提交 input 的外部组名。默认允许任何用户。admin可以无视这个列表直接处理input
  - submitterParameter：环境变量的可选名称。如果存在，用 submitter 名称设置。
  - parameters：提示提交者提供的一个可选的参数列表。

~~~groovy
pipeline {
    agent any
    stages {
        stage('Example') {
            input {
                message "Should we continue?"
                ok "Yes, we should."
                submitter "xianchao,lucky"
                parameters {
                    string(name: 'PERSON', defaultValue: 'xianchao', description: 'Who should I say hello to?')
                }
            }
            steps {
                echo "Hello, ${PERSON}, nice to meet you."
            }
        }
    }
}
~~~

### when

### parallel

### 脚本式语法

- Declarative pipeline对用户来说，语法更严格，有固定的组织结构，更容易生成代码段，使其成为用户更理想的选择。但是Scripted pipeline更加灵活，因为Groovy本身只能对结构和语法进行限制，对于更复杂的pipeline来说，用户可以根据自己的业务进行灵活的实现和扩展。



# Jenkins+k8s+Git+DockerHub构建DevOps平台

## 环境准备

- K8S环境：

  - VMware虚拟机，centos7.9
  - root密码为root

  | K8S集群角色 | IP             | 主机名  |
  | ----------- | -------------- | ------- |
  | 控制节点    | 192.168.40.180 | master1 |
  | 工作节点    | 192.168.40.181 | node1   |

## 部署jenkins--yaml文件

### 安装nfs

~~~sh
#两台节点上都安装nfs
yum install nfs-utils -y
systemctl start nfs
systemctl enable nfs
#master1上创建共享目录
mkdir /data/v1 -p
mkdir /data/v2 -p

vim /etc/exports
/data/v1 *(rw,no_root_squash)
/data/v2 *(rw,no_root_squash)

#使配置文件生效
exportfs -arv
~~~

### 安装jenkins

- 创建ns

  ~~~sh
  kubectl create namespace jenkins-k8s
  ~~~

- 创建pv

  ~~~yaml
  apiVersion: v1
  kind: PersistentVolume
  metadata:
    name: jenkins-k8s-pv
    namespace: jenkins-k8s
  spec:
    capacity:
      storage: 10Gi
    accessModes:
    - ReadWriteMany
    nfs:
      server: 192.168.40.180
      path: /data/v2
  ~~~

- 创建pvc

  ~~~yaml
  kind: PersistentVolumeClaim
  apiVersion: v1
  metadata:
    name: jenkins-k8s-pvc
    namespace: jenkins-k8s
  spec:
    resources:
      requests:
        storage: 10Gi
    accessModes:
    - ReadWriteMany
  ~~~

- 创建sa并做授权

  ~~~sh
  kubectl create sa jenkins-k8s-sa -n jenkins-k8s
  kubectl create clusterrolebinding jenkins-k8s-sa-cluster -n jenkins-k8s  --clusterrole=cluster-admin --serviceaccount=jenkins-k8s:jenkins-k8s-sa
  ~~~

- 制作jenkins镜像

  ~~~sh
  #制作jenkins镜像
  docker pull jenkins/jenkins:2.394
  docker save -o jenkins2.394.tar.gz  jenkins/jenkins:2.394
  
  #制作jenkins-slave从节点的镜像
  mkdir -p ./jenkins-slave
  cd ./jenkins-slave
  ##写dockerfile##
  cat dockerfile
  FROM jenkins/jnlp-slave:4.13.3-1-jdk11
  USER root
  ##安装Docker
  RUN apt-get update && apt-get install -y \
      docker.io
  ##将当前用户加入docker用户组
  RUN usermod -aG docker jenkins
  RUN curl -LO https://dl.k8s.io/release/stable.txt
  RUN curl -LO https://dl.k8s.io/release/$(cat stable.txt)/bin/linux/amd64/kubectl
  RUN chmod +x kubectl
  RUN mv kubectl /usr/local/bin/
  ENV DOCKER_HOST unix:///var/run/docker.sock
  
  ##打包镜像
  docker build -t=jenkins-slave-4-13:v1 .
  docker save -o jenkins-slave-4-13.tar.gz  jenkins-slave-4-13:v1
  #拷贝到所有节点上
  ~~~

- 安装jenkins

  ~~~yaml
  kind: Deployment
  apiVersion: apps/v1
  metadata:
    name: jenkins
    namespace: jenkins-k8s
  spec:
    replicas: 1
    selector:
      matchLabels:
        app: jenkins
    template:
      metadata:
        labels:
          app: jenkins
      spec:
        serviceAccount: jenkins-k8s-sa
        containers:
        - name: jenkins
          image:  jenkins/jenkins:2.394
          imagePullPolicy: IfNotPresent
          ports:
          - name: web 
            containerPort: 8080
            protocol: TCP
          - name: agent
            containerPort: 50000
            protocol: TCP
          resources:
            limits:
              cpu: 1000m
              memory: 1Gi
            requests:
              cpu: 500m
              memory: 512Mi
          livenessProbe:
            httpGet:
              path: /login
              port: 8080
            initialDelaySeconds: 60
            timeoutSeconds: 5
            failureThreshold: 12
          readinessProbe:
            httpGet:
              path: /login
              port: 8080
            initialDelaySeconds: 60
            timeoutSeconds: 5
            failureThreshold: 12
          volumeMounts:
          - name: jenkins-volume
            subPath: jenkins-home #这个subPath指的是宿主机目录里面创建一个子目录挂载
            mountPath: /var/jenkins_home
        volumes:
        - name: jenkins-volume
          persistentVolumeClaim:
            claimName: jenkins-k8s-pvc
  ~~~

  ~~~sh
  #报错
  k logs jenkins-c5c56899f-h2r4c -n jenkins-k8s
  #Can not write to /var/jenkins_home/copy_reference_file.log. Wrong volume permissions?
  #touch: cannot touch '/var/jenkins_home/copy_reference_file.log': Permission denied
  #解决
  #更改jenkins数据目录的属主。将 /data/v2 目录及其下所有文件和子目录的所有权更改为用户 ID 和组 ID 都为 1000 的用户。
  #pod挂载nfs的目录，如果没有权限，可以将属主属组改成1000.1000即可
  chown -R 1000.1000 /data/v2
  ~~~

### 暴露服务

~~~yaml
apiVersion: v1
kind: Service
metadata:
  name: jenkins-service
  namespace: jenkins-k8s
  labels:
    app: jenkins
spec:
  selector:
    app: jenkins
  type: NodePort
  ports:
  - name: web
    port: 8080
    targetPort: web
    nodePort: 30002
  - name: agent
    port: 50000
    targetPort: agent
~~~

### 配置jenkins

~~~sh
#浏览器访问192.168.40.180:30002，进到jenkins管理界面
#访问物理机的数据目录获取密码。密码文件在pod内的路径为/var/jenkins-home/secrets/initialAdminPassword
#由于pod挂载的是master节点的/data/v2，所以去master的/data/v2/jenkins-home/secrets/initialAdminPassword
cat /data/v2/jenkins-home/secrets/initialAdminPassword
#b747213415c545548308434f7b30bee7
#等他自动安装插件完，设置管理员
#用户名：admin
#密码：admin
~~~

- manage jenkins - 插件管理 - available plugins - 搜索kubernetes、blueocean - 均选择download node and install after restart

- 安装完kubernetes、blueocean之后，浏览器手动重启jenkins：

  ~~~sh
  192.168.40.180:30002/restart
  ~~~

- 弹出登录界面说明插件安装没问题，可以进行后续实验。

## jenkins对接k8s自动生成从节点

### 连接k8s集群

- 访问：http://192.168.40.180:30002/configureClouds/

~~~sh
#kubernetes地址: https://192.168.40.180:6443
#kubernetes名称空间：jenkins-k8s
#jenkins地址写jenkins svc地址：http://jenkins-service.jenkins-k8s.svc.cluster.local:8080
~~~

![image-20240207210712930](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402072107183.png)

### 配置pod template

- 配置从节点的pod模板

  - 点击添加pod模板
  - docker镜像写之前导入到node上的slave的image名称，container template名称要写jnlp。

  ![image-20240207213411537](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402072134653.png)

- 从节点的pod要调用docker去创建其他pod，所以把相关路径挂载进去。配置host path卷。

![image-20240207213709147](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402072137227.png)

- 拷贝master1的.kube到node1上。因为从节点pod挂载的是主机路径，从节点pod调度到哪个node上，node都要有/root/.kube/目录

  ~~~sh
  scp -r /root/.kube/  node1:/root/
  ~~~

- apply - save保存

### 配置dockerhub凭据

- manage credentials：


![image-20240208194828707](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402081948880.png)

- 去dockerhub注册用户名密码

- 填写credentials

  ![image-20240208195456048](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402081954137.png)

## 自动化发布Go项目

### 流程

- 开发提交代码到代码仓库gitlab --> jenkins检测到代码更新 --> 调用k8s api在k8s中创建jenkins slave pod

- slave pod拉取代码 --> maven把拉取的代码进行构建成war包/jar包 --> 上传代码到Sonarqube，静态代码扫描 --> 基于war包构建docker image --> 把镜像上传到harbor/dockerhub --> 基于镜像部署到开发/测试/生产环境

  ![image-20240208200024244](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402082000326.png)

### 创建流水线

- 创建三个测试用namespace

  ~~~sh
  kubectl create ns devlopment
  kubectl create ns production
  kubectl create ns qatest
  ~~~

- jenkins UI创建一个新任务

  - 任务名称：jenkins-variable-test-deploy
  - 创建类型为流水线

- pipeline script - 需要修改的地方见脚本注释

  ~~~groovy
  node('test') { //下面的工作都是由jenkins slave pod完成的，所以在这里定义使用标签为test的slave pod模板。
      stage('Clone') {
          echo "1.Clone Stage"
          git url: "https://github.com/hangx969/jenkins-sample.git" 
          //把韩老师的项目fork过来https://github.com/luckylucky421/jenkins-sample.git #并且注意fork过来之后，在k8s-dev/qa/prod.yaml文件中，把image的xianchao改成自己的dockerhub用户名xuhang969
          //slave自动拉代码并解压，后面通过dockerfile打包镜像
          script {
              build_tag = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim() //基于当前代码生成随机数，代码发生变化后，随机数变化会被检测到，从而触发后面的操作。
          }
      }
      stage('Test') {
        echo "2.Test Stage"
  
      }
      stage('Build') {
          echo "3.Build Docker Image Stage"
          sh "docker build -t xuhang969/jenkins-demo:${build_tag} ."
      }
      stage('Push') {
          echo "4.Push Docker Image Stage"
          withCredentials([usernamePassword(credentialsId: 'dockerhub', passwordVariable: 'dockerHubPassword', usernameVariable: 'dockerHubUser')]) {
              sh "docker login -u ${dockerHubUser} -p ${dockerHubPassword}"
              sh "docker push xuhang969/jenkins-demo:${build_tag}"
          } //检测jenkins之前配置的credentials的ID
      }
      stage('Deploy to dev') {
          echo "5. Deploy DEV"
  		sh "sed -i 's/<BUILD_TAG>/${build_tag}/' k8s-dev.yaml"
          sh "sed -i 's/<BRANCH_NAME>/${env.BRANCH_NAME}/' k8s-dev.yaml"
  //        sh "bash running-devlopment.sh"
          sh "kubectl apply -f k8s-dev.yaml  --validate=false"
  	}	
  	stage('Promote to qa') {	
  		def userInput = input( //定义函数选择是否发布到qa
              id: 'userInput',
  
              message: 'Promote to qa?',
              parameters: [
                  [
                      $class: 'ChoiceParameterDefinition',
                      choices: "YES\nNO",
                      name: 'Env'
                  ]
              ]
          )
          echo "This is a deploy step to ${userInput}"
          if (userInput == "YES") {
              sh "sed -i 's/<BUILD_TAG>/${build_tag}/' k8s-qa.yaml"
              sh "sed -i 's/<BRANCH_NAME>/${env.BRANCH_NAME}/' k8s-qa.yaml"
  //            sh "bash running-qa.sh"
              sh "kubectl apply -f k8s-qa.yaml --validate=false"
              sh "sleep 6"
              sh "kubectl get pods -n qatest"
          } else {
              //exit
          }
      }
  	stage('Promote to pro') {	
  		def userInput = input(
  
              id: 'userInput',
              message: 'Promote to pro?',
              parameters: [
                  [
                      $class: 'ChoiceParameterDefinition',
                      choices: "YES\nNO",
                      name: 'Env'
                  ]
              ]
          )
          echo "This is a deploy step to ${userInput}"
          if (userInput == "YES") {
              sh "sed -i 's/<BUILD_TAG>/${build_tag}/' k8s-prod.yaml"
              sh "sed -i 's/<BRANCH_NAME>/${env.BRANCH_NAME}/' k8s-prod.yaml"
  //            sh "bash running-production.sh"
              sh "cat k8s-prod.yaml"
              sh "kubectl apply -f k8s-prod.yaml --record --validate=false"
          }
      }
  }
  ~~~

- 应用-保存-立即构建

- 查看console output

> 上面这套方法，在开发、生产、测试环境里面用的镜像都是一样的。实际应用中，不同的环境的配置是不同的，比如要连接到的一些IP等。这种情况可以用configmap把不同环境的配置挂到deployment里面去用。

- 更改源代码之后，可以在blue ocean界面再点击重新部署来重新拉代码，部署新的pod。
  - 打开blue ocean - 重运行

### troubleshooting

- 有时候jenkins-slave pod自动创建的时候会报错：

  ```sh
  Failed to create pod sandbox: rpc error: code = Unknown desc = [failed to set up sandbox container "3787dcff86eec2020a21f0040b5225263d0df90500edcebb4e1941ee36c36ba5" network for pod "calico-kube-controllers-57c6dcfb5b-9lf78": networkPlugin cni failed to set up pod "calico-kube-controllers-57c6dcfb5b-9lf78_kube-system" network: error getting ClusterInformation: connection is unauthorized: Unauthorized, failed to clean up sandbox container "3787dcff86eec2020a21f0040b5225263d0df90500edcebb4e1941ee36c36ba5" network for pod "calico-kube-controllers-57c6dcfb5b-9lf78": networkPlugin cni failed to teardown pod "calico-kube-controllers-57c6dcfb5b-9lf78_kube-system" network: error getting ClusterInformation: connection is unauthorized: Unauthorized]
  ```

- 解决：

  参考文档：[kubernetes - After uninstalling calico, new pods are stuck in container creating state - Stack Overflow](https://stackoverflow.com/questions/61672804/after-uninstalling-calico-new-pods-are-stuck-in-container-creating-state)

  - 删掉calico

    ~~~sh
    kubectl delete -f calico.yaml 
    ~~~

  - 删掉calico的配置文件

    ```sh
    cd /etc/cni/net.d/
    rm -f ./10-calico.conflist ./calico-kubeconfig
    ```

  - 重启工作节点

  - 重新部署calico

## 按照指定版本回滚

- 更新版本之后，k8s里的deployment中会存在两个版本的replicaset，可以通过kubectl rollout来回滚

- 新建一个任务 --> 任务名称：jenkins-variable-test-deploy-rollout --> 流水线 --> 在Pipeline script处：

  ~~~groovy
  node('test') {
    stage('git clone') {
      git url: "https://github.com/luckylucky421/jenkins-rollout"
      sh "ls -al"
      sh "pwd"
  }
    stage('select env') {
      def envInput = input(
        id: 'envInput',
        message: 'Choose a deploy environment',
        parameters: [
           [
               $class: 'ChoiceParameterDefinition',
               choices: "devlopment\nqatest\nproduction",
               name: 'Env'
           ]
       ]
  )
  echo "This is a deploy step to ${envInput}"  //用户选择了env之后填写到脚本里
  sh "sed -i 's/<namespace>/${envInput}/' getVersion.sh"
  sh "sed -i 's/<namespace>/${envInput}/' rollout.sh"
  sh "bash getVersion.sh"
  // env.WORKSPACE = pwd()
  // def version = readFile "${env.WORKSPACE}/version.csv"
  // println version
  }
    stage('select version') {
       env.WORKSPACE = pwd()
    def version = readFile "${env.WORKSPACE}/version.csv"
    println version
        def userInput = input(id: 'userInput',
                                          message: '选择回滚版本',
                                          parameters: [
              [
                   $class: 'ChoiceParameterDefinition',
                   choices: "$version\n",
                   name: 'Version'
         ]
        ]
  )
         sh "sed -i 's/<version>/${userInput}/' rollout.sh"
  } //用户选了版本之后填写到脚本里
    stage('rollout deploy') {
        sh "bash rollout.sh"
  }
  }
  ~~~

- getVersion.sh

  ~~~sh
  kubectl rollout history deploy/jenkins-demo -n <namespace> | grep -v "deployment" | grep -v "REVISION" | awk '{print $1}' > version.csv
  #查询deployment的历史版本并输出到version.csv文件
  #需要替换掉namespace
  ~~~

- rollout.sh

  ~~~sh
  kubectl rollout undo deployment jenkins-demo  --to-revision=<version> -n <namespace>
  #回滚到指定版本，需要替换掉namespace和version
  ~~~

# jenkins+k8s+harbor实现DevOps

## 启动harbor

~~~sh
#在安装了harbor的机器上启动
sudo su
cd /data/install/harbor
docker-compose start
#https://20.205.104.235
#用户名密码：admin/Harbor12345
~~~

## 配置jenkins credentials

- manage credentials --> 全局凭据
  - 用户名：admin
  - 密码：Harbor12345
  - ID：dockerharbor

## 配置jenkins pipeline

- 在harbor中创建新项目：jenkins-demo

- github项目中：https://github.com/hangx969/jenkins-sample.git，把k8s-dev/qatest/prod-harbor.yaml中的image改成harbor的IP：20.205.104.235

- jenkins中创建新任务jenkins-harbor --> 流水线

  ~~~groovy
  node('test') {
      stage('Clone') {
          echo "1.Clone Stage"
          git url: "https://github.com/hangx969/jenkins-sample.git"
          script {
              build_tag = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
          }
      }
      stage('Test') {
        echo "2.Test Stage"
  
      }
      stage('Build') {
          echo "3.Build Docker Image Stage"
          sh "docker build -t 20.205.104.235/jenkins-demo/jenkins-demo:${build_tag} ."
      }
      stage('Push') {
          echo "4.Push Docker Image Stage"
          withCredentials([usernamePassword(credentialsId: 'dockerharbor', passwordVariable: 'dockerHubPassword', usernameVariable: 'dockerHubUser')]) {
              sh "docker login 20.205.104.235 -u ${dockerHubUser} -p ${dockerHubPassword}"
              sh "docker push 20.205.104.235/jenkins-demo/jenkins-demo:${build_tag}"
          }
      }
      stage('Deploy to dev') {
          echo "5. Deploy DEV"
  		sh "sed -i 's/<BUILD_TAG>/${build_tag}/' k8s-dev-harbor.yaml"
          sh "sed -i 's/<BRANCH_NAME>/${env.BRANCH_NAME}/' k8s-dev-harbor.yaml"
  //        sh "bash running-devlopment.sh"
          sh "kubectl apply -f k8s-dev-harbor.yaml  --validate=false"
  	}	
  	stage('Promote to qa') {	
  		def userInput = input(
              id: 'userInput',
  
              message: 'Promote to qa?',
              parameters: [
                  [
                      $class: 'ChoiceParameterDefinition',
                      choices: "YES\nNO",
                      name: 'Env'
                  ]
              ]
          )
          echo "This is a deploy step to ${userInput}"
          if (userInput == "YES") {
              sh "sed -i 's/<BUILD_TAG>/${build_tag}/' k8s-qa-harbor.yaml"
              sh "sed -i 's/<BRANCH_NAME>/${env.BRANCH_NAME}/' k8s-qa-harbor.yaml"
  //            sh "bash running-qa.sh"
              sh "kubectl apply -f k8s-qa-harbor.yaml --validate=false"
              sh "sleep 6"
              sh "kubectl get pods -n qatest"
          } else {
              //exit
          }
      }
  	stage('Promote to pro') {	
  		def userInput = input(
  
              id: 'userInput',
              message: 'Promote to pro?',
              parameters: [
                  [
                      $class: 'ChoiceParameterDefinition',
                      choices: "YES\nNO",
                      name: 'Env'
                  ]
              ]
          )
          echo "This is a deploy step to ${userInput}"
          if (userInput == "YES") {
              sh "sed -i 's/<BUILD_TAG>/${build_tag}/' k8s-prod-harbor.yaml"
              sh "sed -i 's/<BRANCH_NAME>/${env.BRANCH_NAME}/' k8s-prod-harbor.yaml"
  //            sh "bash running-production.sh"
              sh "cat k8s-prod-harbor.yaml"
              sh "kubectl apply -f k8s-prod-harbor.yaml --record --validate=false"
          }
      }
  }
  ~~~

- 测试了用azure VM部署的harbor，暴露公网IP给k8s使用，jenkins构建的时候会报错：

  ~~~sh
  + docker login 20.205.104.235 -u admin -p ****
  WARNING! Using --password via the CLI is insecure. Use --password-stdin.
  Error response from daemon: Get "https://20.205.104.235/v2/": tls: failed to verify certificate: x509: cannot validate certificate for 20.205.104.235 because it doesn't contain any IP SANs
  script returned exit code 1
  ~~~

  - 原因可能是证书不被信任，可以尝试这篇文章的办法，把harbor上面的证书拷贝到slave pod里面去：[搭建好harbor服务器后，从另一台机登录时遇到的问题 - 简书 (jianshu.com)](https://www.jianshu.com/p/1bc2d2b9d3fb)
  - 或者在内网中再搭建一个harbor，通过内网IP访问。

# jenkins-k8s-nexus-gitlab-harbor-sonarqube-springcloud构建devops

## jenkins接入Sonarqube

> SonarQube是一个开源的代码质量管理系统，用于自动化检查源代码的质量并提供报告。它支持多种编程语言，包括Java、C#、JavaScript、Python等，能够检测出代码中的错误、漏洞、代码异味等问题。SonarQube可以集成到CI/CD流程中，帮助开发团队在开发过程中持续改进代码质量。

- docker启动sonarqube

~~~sh
#在192.168.40.181上操作
docker run -d --name postgres10 -p 5432:5432 -e POSTGRES_USER=sonar -e POSTGRES_PASSWORD=123456 postgres

docker run -d --name sonarqube7.9 -p 9000:9000 --link postgres10 -e SONARQUBE_JDBC_URL=jdbc:postgresql://postgres10:5432/sonar -e SONARQUBE_JDBC_USERNAME=sonar -e SONARQUBE_JDBC_PASSWORD=123456 -v sonarqube_conf:/opt/sonarqube/conf -v sonarqube_extensions:/opt/sonarqube/extensions -v sonarqube_logs:/opt/sonarqube/logs -v sonarqube_data:/opt/sonarqube/data sonarqube

#启动sonarqube容器后会马上exit
docker logs containerID
#有如下报错：
#bootstrap check failure [1] of [1]: max virtual memory areas vm.max_map_count [65530] is too low, increase to at least [262144]
#解决方法
vim /etc/sysctl.conf 
#添加一行：
vm.max_map_count=262144
#刷新配置
sysctl -p
#docker rm删掉容器重新创建即可
~~~

> - `vm.max_map_count` 是一个内核参数，用于限制一个进程可以拥有的 VMA（Virtual Memory Areas）的数量。VMA 是用于描述进程虚拟内存空间的数据结构。如果进程创建大量的内存映射，但没有足够的 VMA，那么进程将无法成功映射内存，可能会导致错误。
>
> - 所以，`vm.max_map_count=262144` 这行配置的含义是，设置系统中每个进程可以拥有的最大 VMA 数量为 262144。这对于一些内存密集型的应用（如 Elasticsearch）可能是必要的，因为这些应用可能需要创建大量的内存映射。
> - `/etc/sysctl.conf` 文件是 Linux 系统中用于调整内核参数的配置文件。你可以在这个文件中添加或修改参数，然后通过 `sysctl -p` 命令使其生效，以调整系统的各种性能。

- jenkins安装sonarqube插件

  - 系统管理-插件管理-可选插件：**Sonarqube Scanner** 安装

  - 重启jenkins：`192.168.40.180:30002/restart`

- 创建sonarqube token

  - 登录sonarqube

    - 问题：docker run命令指定了用户名密码-e SONARQUBE_JDBC_USERNAME=sonar  -e SONARQUBE_JDBC_PASSWORD=123456，为何认证失败？

    ![1707654654221](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402112031991.jpg)

    - 登录：用默认的admin/admin可以登陆成功，修改密码为123456

  - 创建token：administration - security - users - tokens - generate
    - e7afc8592f0c4ec6c371417a6416e3b6018d7437

- 扫描代码

  - 课件中有示例代码**microservic-test**

    ~~~sh
    #上传到master1节点
    unzip microservic-test.zip
    cd ./microservic-test
    yum install -y maven
    mvn sonar:sonar  -Dsonar.host.url=http://192.168.40.181:9000 -Dsonar.login=e7afc8592f0c4ec6c371417a6416e3b6018d7437
    ~~~

    注：由于版本变更，当前的示例代码扫描会出错。

## 私服nexus配置

### 安装harbor

1. 为harbor创建自签发证书

   ```bash
   #在node1上
   mkdir /data/ssl -p
   cd /data/ssl/
   #生成一个3072位的key，也就是私钥
   openssl genrsa -out ca.key 3072
   #生成一个数字证书ca.pem，3650表示证书的有效时间是3年。后续根据ca.pem根证书来签发信任的客户端证书
   openssl req -new -x509 -days 3650 -key ca.key -out ca.pem 
   #生成域名的证书
   #生成一个3072位的key，也就是私钥
   openssl genrsa -out harbor.key  3072
   #生成一个证书请求文件，一会签发证书时需要的
   openssl req -new -key harbor.key -out harbor.csr
   #签发证书：
   openssl x509 -req -in harbor.csr -CA ca.pem -CAkey ca.key -CAcreateserial -out harbor.pem -days 3650
   ```

2. 安装docker（harbor是基于docker的）

3. 安装harbor

   ```bash
   #创建安装目录
   mkdir /data/install -p
   cd /data/install/
   #安装harbor
   #/data/ssl目录下有如下文件：ca.key  ca.pem  ca.srl  harbor.csr  harbor.key  harbor.pem
   #把harbor的离线包harbor-offline-installer-v2.3.0-rc3.tgz上传到这个目录，离线包在课件里提供了
   #下载harbor离线包的地址：
   #https://github.com/goharbor/harbor
   #解压：
   tar zxvf harbor-offline-installer-v2.3.0-rc3.tgz
   cd harbor
   cp harbor.yml.tmpl harbor.yml 
   
   vim harbor.yml
   #修改配置文件：
   hostname: node1 #修改hostname，跟上面签发的证书域名保持一致
   #协议用https
   certificate: /data/ssl/harbor.pem
   private_key: /data/ssl/harbor.key
   #邮件和ldap不需要配置，在harbor的web界面可以配置，其他配置采用默认即可。
   #注：harbor默认的账号密码：admin/Harbor12345
   ```

4. 安装docker-compose

   docker-compose项目是Docker官方的开源项目，负责实现对Docker容器集群的快速编排。Docker-Compose的工程配置文件默认为docker-compose.yml，Docker-Compose运行目录下的必要有一个docker-compose.yml。docker-compose可以管理多个docker实例。

   ```bash
   #上传docker-compose-Linux-x86_64文件到harbor机器，这是harbor的依赖
   mv docker-compose-Linux-x86_64.64 /usr/bin/docker-compose
   chmod +x /usr/bin/docker-compose
   
   #安装harbor依赖的的离线镜像包docker-harbor-2-3-0.tar.gz上传到harbor机器，通过docker load -i解压
   docker load -i docker-harbor-2-3-0.tar.gz 
   cd /data/install/harbor
   ./install.sh
   #出现✔ ----Harbor has been installed and started successfully.---- 表明安装成功。
   ```

5. harbor启动和停止

   ```bash
   #如何停掉harbor：
   cd /data/install/harbor
   docker-compose stop 
   #如何启动harbor：
   sudo su
   cd /data/install/harbor
   docker-compose start
   ```

### jenkins注册harbor credentials

- 系统管理-凭据管理-添加全局凭据
  - username：admin
  - password：Harbor12345
  - ID：dockerharbor

### 安装nexus

> - Nexus服务器是一个代码包管理的服务器，可以理解 Nexus 服务器是一个巨大的 Library 仓库。
>
> - Nexus 可以支持管理的工具包括 Maven ， npm 等，对于 JAVA 开发来说，只要用到 Maven 管理就可以了。
>
> - Nexus服务器作用：因为传统的中央仓库在国外，其地理位置比较远，下载速度比较缓慢。
>
> - 如果不架设一台自己的Nexus服务器，会产生大量的流量阻塞带宽，开发就会因为无法下载相关依赖包而进度停滞。
>
> - 因此在本地环境部署一台私有的Nexus服务器来缓存所有依赖包，并且将公司内部开发的私有包也部署上去，方便其他开发人员下载，是非常有必要的。因为 Nexus 有权限控制，因此外部人员是无法得到公司内部开发的项目包的。

~~~sh
docker run -d -p 8081:8081 -p 8082:8082 -p 8083:8083 -v /etc/localtime:/etc/localtime --name nexus3   sonatype/nexus3
#在docker log日志中，会看到一条消息： Started Sonatype Nexus OSS 3.20.1-01 这意味着Nexus Repository Manager可以使用了。现在转到浏览器并打开：http://192.168.0.181:8081
~~~

- 在 pom.xml 文件中声明发布的宿主仓库和 release 版本发布的仓库。

  ~~~xml
  <! -- 发布构件到Nexus -- >
      <distributionManagement>
          <repository>
              <id>releases</id>
              <name>nexus-releases</name>
              <url>http://192.168.40.181:8081/repository/maven-releases/</url>
          </repository>
          <snapshotRepository>
              <id>snapshots</id>
              <name>nexus-snapshots</name>
              <url>http://192.168.40.181:8081/repository/maven-snapshots/</url>
          </snapshotRepository>
      </distributionManagement>
  ~~~

- 由于用 Maven 分发构件到远程仓库需要认证，须要在~/.m2/settings.xml或者中加入验证信息

  ~~~xml
  <servers>  
     <server>  
             <id>public</id>  
             <username>admin</username>  
             <password>123456</password>  
         </server>  
     <server>  
             <id>releases</id>  
             <username>admin</username>  
             <password>123456</password>  
         </server>  
     <server>  
             <id>snapshots</id>  
             <username>admin</username>  
             <password>123456</password>  
         </server>  
   </servers> 
  ~~~

> `pom.xml`和`settings.xml`都是Maven项目中的配置文件。
>
> - `pom.xml`（Project Object Model）是Maven项目必备的配置文件，它是整个项目的基本单元。`pom.xml`文件定义了项目的基本信息，如项目的依赖、构建设置、插件、目标等。
>
> - `settings.xml`文件是Maven的全局配置文件，它包含了如本地仓库的位置、镜像仓库设置、代理设置等信息。这个文件通常位于Maven安装的`conf`目录下，或者在用户的`.m2`目录下。
> - settings.xml 中 server 元素下 id 的值必须与 POM 中 repository 或 snapshotRepository 下 id 的值完全一致

## 安装gitlab

- 安装

  ~~~sh
  #在192.168.40.182上安装
  docker run -d -p 443:443 -p 80:80 -p 222:22 --name gitlab --restart always -v /home/gitlab/config:/etc/gitlab -v /home/gitlab/logs:/var/log/gitlab -v /home/gitlab/data:/var/opt/gitlab gitlab/gitlab-ce
  ~~~

- 改配置

  ~~~sh
  vim /home/gitlab/config/gitlab.rb
  #增加以下3行
  external_url 'http://192.168.40.182'
  gitlab_rails['gitlab_ssh_host'] = '192.168.40.182'
  gitlab_rails['gitlab_shell_ssh_port'] = 222
  #重启容器
  docker restart gitlab
  ~~~

- 登录

  - 浏览器访问192.168.40.182即可登录：

  - 第一次登录注册账号密码之后，报错如下：

    Your account is pending approval from your GitLab administrator and hence bl 

  - 解决：

  ```sh
  docker exec -it gitlab sh
  gitlab-rails console #进入gitlab控制台
  u=User.where(id:1).first
  u.password='12345678'
  u.password_confirmation='12345678' 
  u.save!
  ```

  - 再次登录192.168.40.135

    - 用户名是root

    - 密码是12345678

- jenkins安装git插件
  - 系统管理-插件管理-可选插件-搜索git安装即可

- jenkins安装gitlab凭据
  - 系统管理-凭据管理-新建全局凭据
  - 用户名root，密码12345678，ID gitlab

### 配置gitlab

- gitlab上新建项目

  - New project - create blank project：

    <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402120840309.png" alt="image-20240212084059114" style="zoom:50%;" />

- 创建密钥对

  ~~~sh
  ssh-keygen -t rsa
  cat ~/.ssh/id_rsa.pub #查看公钥
  ~~~

- gitlab - 右上角Preferences - ssh keys - 把公钥粘贴进去 - add

### 提交本地代码到gitlab

~~~sh
yum install git -y
#上传项目microservic-test.zip
unzip microservic-test.zip
cd microservic-test
#建仓
git init
#把当前文件夹所有代码提交
git add * 
#代码提交到缓冲区
git commit -m "add microservic-test" 
#代码提交到远程仓库
git remote add origin http://192.168.40.135/root/microservic-test.git   
#最后一步push推送过去，输入账号和密码，这里的用户名和密码就是gitlab上注册的用户了
git push -u origin master
~~~

## jenkins流水线配置

- 添加新的slave pod镜像：jenkins-jnlp-v2.tar.gz这个压缩包封装的镜像带有mvn命令

  ~~~sh
  docker load -i jenkins-jnlp-v2.tar.gz
  ~~~

- 在http://192.168.40.180:30002/configureClouds/，把Container Template镜像改成jenkins-jnlp-v2.tar.gz压缩包解压之后的镜像xianchao/jenkins-jnlp:v2

- 修改gitlab上的项目中的k8s/portral.yaml文件，将image改成：192.168.40.181/microservice/jenkins-demo:v1（harbor server的地址）。同时harbor上面要创建microservice仓库。

- jenkins上面创建流水线

  - name：**mvn-gitlab-harbor-springcloud**

  - script

    ~~~groovy
    node('test') {
       stage('Clone') {
           echo "1.Clone Stage"
          git credentialsId: 'gitlab', url: 'http://192.168.40.182/root/microservic-test.git ' //gitlab地址，slave pod去拉源代码
           script {
               build_tag = sh(returnStdout: true, script: 'git rev-parse --shortHEAD').trim()
           }
        }
    
       stage('Test') {
         echo "2.Test Stage"
        }
        
       stage('mvn') {
         sh "mvn clean package -D maven.test.skip=true" //slave pod运行mvn构建java代码
        }
        
       stage('Build') {
           echo "3.Build Docker Image Stage"
           sh "cd /home/jenkins/agent/workspace/mvn-gitlab-harbor-springcloud/portal-service"
           sh "docker build --tag 192.168.40.181/microservice/jenkins-demo:v1 /home/jenkins/agent/workspace/mvn-gitlab-harbor-springcloud/portal-service/" //这里的workspace/项目名和流水线名字要一致。//写harbor地址 //slave pod把构建好的代码做成镜像push到harbor仓库
        }
        
       stage('Push') {
           echo "4.Push Docker Image Stage"
           withCredentials([usernamePassword(credentialsId: 'dockerharbor',passwordVariable: 'dockerHubPassword', usernameVariable: 'dockerHubUser')]) {
               sh "docker login 192.168.40.181 -u ${dockerHubUser} -p ${dockerHubPassword}" //harbor地址
               sh "docker push 192.168.40.181/microservice/jenkins-demo:v1" //harbor地址
           }
        }
        
         stage('Promoteto pro') {    
        sh "kubectl apply -f /home/jenkins/agent/workspace/mvn-gitlab-harbor-springcloud/k8s/portal.yaml"
          } //slave pod读取yaml文件，利用harbor的镜像部署pod
    }
    ~~~

- k8s环境创建namespace：ms

  ~~~sh
  kubectl create ns ms
  ~~~

- 流水线立即构建

  > - 构建的时候到连接harbor这一步，docker login 192.168.40.181 -u -p 命令登录harbor会报错：，报错：“tls: failed to verify certificate: x509: cannot validate certificate for 192.168.40.181 because it doesn't contain any IP SANs
  >
  > - 解决办法：
  >
  >   - Docker 客户端在尝试验证服务器的 SSL 证书时，没有找到任何 IP 主题备用名称（IP SANs）。这通常发生在使用自签名证书的情况下。
  >
  >   - 解决这个问题的一种方法是在 Docker 客户端配置中禁用对该服务器的 TLS 验证。这可以通过在 Docker 客户端的 `daemon.json` 文件中添加 `insecure-registries` 来完成。
  >
  >     ~~~sh
  >     vim /etc/docker/daemon.json
  >     #添加
  >     "insecure-registries" : ["192.168.40.181"]
  >     systemctl restart docker
  >     ~~~

- jenkins和gitlab、harbor比较吃资源，VMWare VM给3G内存容易OOM，20G磁盘容器用光。

# Jenkins插件离线安装

1. Jenkins离线插件下载地址:http://mirrors.tuna.tsinghua.edu.cn/jenkins/plugins/，可以在Jenkins官网上搜索想要下载的插件，点击“Download”按钮下载.hpi文件。

2. Jenkins离线插件安装方法：
   1. 方法一：在Jenkins管理页面点几“系统管理” -> “插件管理” -> “高级”。选择“上传插件”，并选择下载的.hpi文件。点击“上传”按钮，等待插件安装完成。
   2. 方法二：将下载的.hpi文件放到Jenkins的安装目录下的“plugins”文件夹中。重启Jenkins，等待插件安装完成。

# Jenkins版本升级

Jenkins 版本升级通常分为以下几个步骤：

1. 备份当前 Jenkins 数据在升级之前，应该备份当前 Jenkins 数据以避免数据丢失。可以通过将 Jenkins 的 JENKINS_HOME 目录复制到其他位置来备份数据。

2. 下载新版本的 Jenkins在官网下载最新版本的 Jenkins war 文件，通常可以在 https://www.jenkins.io/download/ 找到最新版本。

3. 停止当前 Jenkins 实例在进行版本升级之前，需要停止当前运行的 Jenkins 实例。

4. 启动新版本的 Jenkins将下载的新版本 Jenkins war 文件复制到 Jenkins 的安装目录下，并启动 Jenkins。在 Linux 系统中，可以使用以下命令来启动 Jenkins：`java -jar jenkins.war`
5. 升级插件在新版本的 Jenkins 中，有可能需要升级现有插件以保持兼容性。在 Jenkins 管理页面的“插件管理”中，可以检查并升级插件。
6. 验证升级启动新版本的 Jenkins 后，可以通过访问 Jenkins Web 界面来验证升级是否成功，并确保所有插件和功能正常工作。
