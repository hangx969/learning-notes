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
            subPath: jenkins-home
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



