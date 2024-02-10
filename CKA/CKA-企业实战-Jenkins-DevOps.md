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

# Jenkins语法

## jenkins pipeline介绍

# 基于Jenkins+k8s+Git+DockerHub构建DevOps平台

## 环境准备

- K8S环境：

  - VMware虚拟机，centos7.9
  - root密码为root

  | K8S集群角色 | IP             | 主机名  |
  | ----------- | -------------- | ------- |
  | 控制节点    | 192.168.40.180 | master1 |
  | 工作节点    | 192.168.40.181 | node1   |

## 部署jenkins

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

~~~sh
#http://192.168.40.180:30002/configureClouds/
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

## jenkins+k8s自动化发布Go项目

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

  ~~~sh
  node('test') { #pod模板里面指定了标签是test。
      stage('Clone') {
          echo "1.Clone Stage"
          git url: "https://github.com/hangx969/jenkins-sample.git" 
          #把韩老师的项目fork过来https://github.com/luckylucky421/jenkins-sample.git #并且注意fork过来之后，在k8s-dev/qa/prod.yaml文件中，把image的xianchao改成自己的dockerhub用户名xuhang969
          #jenkins会自动拉下来代码并解压，后面会通过dockerfile打包镜像
          script {
              build_tag = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim() #基于当前代码生成随机数，代码发生变化后，随机数变化会被检测到，从而触发后面的操作。
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
          } #检测jenkins之前配置的credentials的ID
      }
      stage('Deploy to dev') {
          echo "5. Deploy DEV"
  		sh "sed -i 's/<BUILD_TAG>/${build_tag}/' k8s-dev.yaml"
          sh "sed -i 's/<BRANCH_NAME>/${env.BRANCH_NAME}/' k8s-dev.yaml"
  //        sh "bash running-devlopment.sh"
          sh "kubectl apply -f k8s-dev.yaml  --validate=false"
  	}	
  	stage('Promote to qa') {	
  		def userInput = input( #定义函数选择是否发布到qa
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

> 上面这套方法，在开发、生产、测试环境里面用的镜像都是一样的。实际应用中，不同的环境的配置是不同的，比如要脸接到的一些IP等。这种情况可以用configmap把不同环境的配置挂到deployment里面去用。

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

# jenkins实现k8s应用按照指定版本回滚

- 更新版本之后，k8s里的deployment中会存在两个版本的replicaset，可以通过kubectl rollout来回滚

- 新建一个任务 --> 任务名称：jenkins-variable-test-deploy-rollout --> 流水线 --> 在Pipeline script处：

  ~~~sh
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

  
