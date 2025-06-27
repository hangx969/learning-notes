# 介绍

- 官网安装说明：https://www.jenkins.io/doc/book/installing/kubernetes/#install-jenkins-with-helm-v3
- github地址：https://github.com/jenkinsci/helm-charts/tree/main/charts/jenkins
- artifacthub地址：https://artifacthub.io/packages/helm/jenkinsci/jenkins

# 下载

- 下载helm chart

~~~sh
helm repo add jenkins https://charts.jenkins.io
helm repo update jenkins
helm pull jenkins/jenkins --version 5.8.61
~~~

# 配置文件

~~~yaml
controller:
  admin:
    username: "admin"
    password: "admin"

  containerSecurityContext:
    runAsUser: 0
    runAsGroup: 0
    readOnlyRootFilesystem: false
    allowPrivilegeEscalation: true
  runAsUser: 0
  runAsGroup: 0

  ingress:
    enabled: true
    ingressClassName: nginx-default
    path: /
    hostName: jenkins.hanxux.local

  volumes:
  - name: local-time
    hostPath:
      path: /etc/localtime
  mounts:
  - mountPath: /etc/localtime
    name: local-time

  prometheus:
    enabled: true

agent:
  enabled: true
  namespace: "jenkins"
  privileged: true
  podName: "jnlp"
  command: ""
  args: ""

  volumes:
  - type: HostPath
    hostPath: /var/run/docker.sock
    mountPath: /var/run/docker.sock
  - type: HostPath
    hostPath: /root/.kube
    mountPath: /home/jenkins/.kube
  - type: HostPath
    hostPath: /usr/bin/docker
    mountPath: /usr/bin/docker
  - type: HostPath
    hostPath: /usr/local/bin/kubectl
    mountPath: /usr/local/bin/kubectl
  - type: HostPath
    hostPath: /etc/docker/daemon.json
    mountPath: /etc/docker/daemon.json

  TTYEnabled: true
  containerCap: 10

  # Enables garbage collection of orphan pods for this Kubernetes cloud. (beta)
  garbageCollection:
    # -- When enabled, Jenkins will periodically check for orphan pods that have not been touched for the given timeout period and delete them.
    enabled: true
    # -- Namespaces to look at for garbage collection, in addition to the default namespace defined for the cloud. One namespace per line.
    namespaces: "jenkins"

persistence:
  enabled: true
  storageClass: "sc-nfs"
  size: "1Gi"
~~~

# 安装

~~~sh
helm upgrade -i jenkins -n jenkins --create-namespace . -f values.yaml
~~~

# 后续配置

## 访问jenkins UI

- 获取初始admin密码

  ~~~sh
  kubectl exec --namespace jenkins -it svc/jenkins -c jenkins -- /bin/cat /run/secrets/additional/chart-admin-password && echo
  ~~~

- 客户端/etc/hosts添加记录

- 访问ingress URL：`http://jenkins.hanxux.local`

## 安装blue ocean插件

- manage jenkins - 插件管理 - available plugins - 搜索kubernetes、blueocean - 均选择download node and install after restart (kubernetes插件在新版jenkins helm chart中已经默认安装好了，这里仅安装blue ocean即可)

- 安装完kubernetes、blueocean之后，会自动重启jenkins

- 也可以浏览器手动重启jenkins：

  ~~~sh
  https://jenkins.hanxux.local/restart
  ~~~

- 弹出登录界面说明插件安装没问题，可以进行后续实验。

## 测试连接k8s

- 新建一个pipeline看是否可以执行任务

  ~~~groovy
  pipeline {
      agent {
          kubernetes {
              cloud 'kubernetes' 
          }
      }
   
      stages {
          stage('Hello') {
              steps {
                  echo 'Hello World'
              }
          }
      }
  }
  ~~~


## 连接harbor

1. 首先需要[安装harbor](../helm/helm部署harbor.md)
2. Jenkins中首页-->系统管理-->管理凭据-->Stores scoped to Jenkins-->全局-->添加凭据
3. 类型：Username with Password，范围：全局，用户名和密码：写harbor的用户名密码，ID：dockerharbor。
4. 点击Create

# 编写pipeline

1. harbor中新建项目`jenkins-demo`

2. 新建一个任务-->输入任务名称jenkins-harbor-->流水线-->确定-->在Pipeline script处写入脚本：

   ~~~groovy
   node('testhan') {
       stage('第1步:从gitee上下载源代码') {
           git url: "https://gitee.com/hanxianchao66/jenkins-sample"
           script {
               build_tag = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
           }
       }
       stage('第2步：基于dockerfile文件制作镜像') {
           sh "docker build -t 192.168.40.62/jenkins-demo/jenkins-demo:${build_tag} ."
       }
       stage('第3步：把镜像上传到harbor私有仓库') {
           withCredentials([usernamePassword(credentialsId: 'dockerharbor', passwordVariable: 'dockerHubPassword', usernameVariable: 'dockerHubUser')]) {
               sh "docker login 192.168.40.62 -u ${dockerHubUser} -p ${dockerHubPassword}"
               sh "docker push 192.168.40.62/jenkins-demo/jenkins-demo:${build_tag}"
           }
       }
       stage('第4步：把pod部署到开发环境') {
   		sh "sed -i 's/<BUILD_TAG>/${build_tag}/' k8s-dev-harbor.yaml"
           sh "sed -i 's/<BRANCH_NAME>/${env.BRANCH_NAME}/' k8s-dev-harbor.yaml"
   //        sh "bash running-devlopment.sh"
           sh "kubectl apply -f k8s-dev-harbor.yaml  --validate=false"
   	}	
   	stage('第5步：把pod部署到测试环境') {	
   		def userInput = input(
               id: 'userInput',
   
               message: '确定部署到测试环境吗？输入yes确定',
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
   			//sh "bash running-qa.sh"
               sh "kubectl apply -f k8s-qa-harbor.yaml --validate=false"
               sh "sleep 6"
               sh "kubectl get pods -n qatest"
               sh "cd /home/jenkins/agent/workspace/jenkins-harbor"
               sh "/root/Python-3.12.5/python qatest.py"
           } else {
               //exit
           }
       }
   	stage('第6步：pod部署到生产环境') {	
   		def userInput = input(
   
               id: 'userInput',
               message: '确定部署到生产环境吗？输入yes确定',
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
   			// sh "bash running-production.sh"
               sh "cat k8s-prod-harbor.yaml"
               sh "kubectl apply -f k8s-prod-harbor.yaml --record --validate=false"
               sh "cd /home/jenkins/agent/workspace/jenkins-harbor"
               sh "/root/Python-3.12.5/python smtp.py"
           }
       }
   }
   ~~~

3. 应用-->保存-->立即构建-->打开blue ocean可以看到流程，可以在交互式输入中手动点击确认

# 自定义agent image

## agent安装helm和docker

自己基于jenkins的inbound-agent镜像做一个装了docker、helm、kubectl的镜像：

~~~sh
FROM jenkins/inbound-agent:4.3-4

ARG VCS_REF
ARG BUILD_DATE

# Metadata
LABEL org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url="https://github.com/dtzar/jnlp-slave-helm" \
      org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.docker.dockerfile="/Dockerfile"

USER root

# Note: Latest version of kubectl may be found at:
# https://aur.archlinux.org/packages/kubectl-bin/
ENV KUBE_LATEST_VERSION="v1.18.6"
# Note: Latest version of helm may be found at:
# https://github.com/kubernetes/helm/releases
ENV HELM_VERSION="v3.3.1"
# Note: Latest version of docker may be found at:
# https://get.docker.com/builds
ENV DOCKER_VERSION="18.09.9"

RUN apt-get update && apt-get install -y --no-install-recommends \
    # Install Kubectl
    && curl -L https://storage.googleapis.com/kubernetes-release/release/${KUBE_LATEST_VERSION}/bin/linux/amd64/kubectl -o /usr/local/bin/kubectl \
    && chmod +x /usr/local/bin/kubectl \
    # Install Helm
    && curl -L https://get.helm.sh/helm-v3.3.4-linux-amd64.tar.gz -o /tmp/helm.tar.gz \
    && tar -zxvf /tmp/helm.tar.gz -C /tmp \
    && cp /tmp/linux-amd64/helm /usr/local/bin/helm \
    # Install Docker
    && curl -L https://download.docker.com/linux/static/stable/x86_64/docker-19.03.12.tgz -o /tmp/docker-19.03.12.tgz \
    && tar --strip-components=1 -xvzf /tmp/docker-19.03.12.tgz -C /usr/local/bin \
    && chmod a+x /usr/local/bin/dockerd \
    # Cleanup uncessary files
    && apt-get clean \
    && rm -rf /tmp/* ~/*.tgz
~~~

# 
