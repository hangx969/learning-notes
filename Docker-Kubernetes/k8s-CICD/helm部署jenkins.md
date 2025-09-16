# 介绍

- 官网安装说明：https://www.jenkins.io/doc/book/installing/kubernetes/#install-jenkins-with-helm-v3
- github地址：https://github.com/jenkinsci/helm-charts/tree/main/charts/jenkins
- artifacthub地址：https://artifacthub.io/packages/helm/jenkinsci/jenkins

# 下载

- 下载helm chart

~~~sh
helm repo add jenkins https://charts.jenkins.io
helm repo update jenkins
helm pull jenkins/jenkins --version 5.8.68
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

  installPlugins:
    - kubernetes:4358.vcfd9c5a_0a_f51
    - workflow-aggregator:608.v67378e9d3db_1
    - git:5.7.0
    - configuration-as-code:1985.vdda_32d0c4ea_b_
  installLatestPlugins: true
  installLatestSpecifiedPlugins: true

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
    hostPath: /usr/bin/kubectl
    mountPath: /usr/bin/kubectl
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

  serviceAccount: jenkins


persistence:
  enabled: true
  storageClass: "cfs-sc"
  size: "1Gi"


~~~

配置文件里面把docker和kubectl通过host path挂进slave pod里面了，需要修改一下权限否则slave pod中会报错permission denied：

~~~sh
# 工作节点上修改属主属组和权限
chown 1000:1000  /var/run/docker.sock
chmod 777  /var/run/docker.sock
chmod 777 /usr/bin/docker
chown -R 1000.1000  /usr/bin/docker
chmod 777 /usr/bin/kubectl
chown -R 1000.1000 /usr/bin/kubectl
# 把kubeconfig复制到工作节点
# 控制节点上
scp -r /root/.kube/  rn1:/root/
# 工作节点上
chown -R 1000.1000 /root/.kube/
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

- 也可以浏览器手动重启jenkins： https://jenkins.hanxux.local/restart

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
              agent {
                  node {
                      label 'jenkins-jenkins-agent'
                  }
              }
              steps {
                  echo "Hello world!"
                  sh "cat /etc/docker/daemon.json"
              }
          }
      }
  }
  ~~~
  

## 连接harbor

1. 首先需要[安装harbor](../helm/helm部署harbor.md)
2. Jenkins中首页-->系统管理-->管理凭据-->Stores scoped to Jenkins-->全局-->添加凭据
3. 类型：Username with Password，范围：全局，用户名和密码：写harbor的用户名密码admin/Harbor12345，ID：harbork8s。
4. 点击Create

# 编写pipeline

1. harbor中新建项目`jenkins-demo`

2. 新建一个任务-->输入任务名称jenkins-harbor-->流水线-->确定-->在Pipeline script处写入脚本：

   > 注意：
   >
   > 1. `node(‘jenkins-jenkins-agent’)`是匹配标签为jenkins-jenkins-agent的pod template。
   > 2. 已经把宿主机的`/etc/docker/daemon.json`挂进slave pod中了，里面配置了harbor的insecure registry，所以在pipeline里面docker login直接登录不需要--insecure选项

   ~~~groovy
   node('jenkins-jenkins-agent') {
       stage('第1步:从gitee上下载源代码') {
           git url: "https://gitee.com/hangxu969/jenkins-sample"
           script {
               build_tag = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
           }
       }
       stage('第2步：基于dockerfile文件制作镜像') {
           withCredentials([usernamePassword(credentialsId: 'harbork8s', passwordVariable: 'harborPassword', usernameVariable: 'harborUser')]) {
               sh "docker login harbor.hanxux.local -u ${harborUser} -p ${harborPassword}"
               sh "docker build -t harbor.hanxux.local/jenkins-demo/jenkins-demo:${build_tag} ."
           }
       }
       stage('第3步：把镜像上传到harbor私有仓库') {
           withCredentials([usernamePassword(credentialsId: 'harbork8s', passwordVariable: 'harborPassword', usernameVariable: 'harborUser')]) {
               sh "docker login harbor.hanxux.local -u ${harborUser} -p ${harborPassword}"
               sh "docker push harbor.hanxux.local/jenkins-demo/jenkins-demo:${build_tag}"
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
               // sh "cd /home/jenkins/agent/workspace/jenkins-harbor"
               // sh "/root/Python-3.12.5/python qatest.py"
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
               // sh "cd /home/jenkins/agent/workspace/jenkins-harbor"
               // sh "/root/Python-3.12.5/python smtp.py"
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

# troubleshooting

1. Jenkins Pod 启动失败，`config-reload-init` 容器报告 SSL 证书验证错误：

   ~~~sh
   config-reload-init {"time": "2025-07-11T15:04:40.489716+00:00", "level": "ERROR", "msg": "MaxRetryError: HTTPSConnectionPool(host='10.96.0.1', port=443): Max retries exceeded with url: /api/v1/namespaces/jenkins/configmaps?labelSelector=jenkins-jenkins-config (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: Missing Authority Key Identifier (_ssl.c:1028)')))"
   ~~~

   jenkins helm chart从5.8.61升级到5.8.68问题自动消失。可能是旧版本的 config-reload-init 容器对证书验证要求过于严格或者无法处理缺少 Authority Key Identifier 扩展的证书。

2. 对于jenkins helm 5.8.68，init pod启动失败：

   ~~~sh
   init Plugin git:5.7.0 (via git-client:6.3.3) depends on configuration-as-code:1985.vdda_32d0c4ea_b_, but there is an older version defined on the top level
   ~~~

   在默认values.yaml中定义的是旧版本的configuration-as-code：

   ~~~yaml
   controller:
     installPlugins:
       - kubernetes:4358.vcfd9c5a_0a_f51
       - workflow-aggregator:608.v67378e9d3db_1
       - git:5.7.0
       - configuration-as-code:1971.vf9280461ea_89
   ~~~

   更改为：

   ~~~yaml
   controller:
     installPlugins:
       - kubernetes:4358.vcfd9c5a_0a_f51
       - workflow-aggregator:608.v67378e9d3db_1
       - git:5.7.0
       - configuration-as-code:1985.vdda_32d0c4ea_b_
     installLatestPlugins: true
     installLatestSpecifiedPlugins: true
   ~~~

3. 如果由于插件下载太慢导致pod startupProbe失败，可以关闭插件安装：

   ~~~yaml
   controller:
     installPlugins: false
     # installLatestPlugins: true
     # installLatestSpecifiedPlugins: true
   ~~~

   
