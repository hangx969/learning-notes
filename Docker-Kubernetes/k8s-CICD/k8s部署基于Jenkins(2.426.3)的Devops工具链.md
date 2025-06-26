# 部署Jenkins

## 安装nfs服务

可以在任一台机器上部署nfs服务

~~~sh
yum install nfs-utils -y
systemctl start nfs
systemctl enable nfs
yum install nfs-utils -y
systemctl start nfs
systemctl enable nfs
~~~

创建nfs共享目录

~~~sh
mkdir /data/v2 -p
tee -a /etc/exports<<'EOF'
/data/v2 *(rw,no_root_squash)
EOF
exportfs -arv
~~~

## 准备前置资源

### namespace

~~~sh
kubectl create namespace jenkins-k8s
~~~

### PV+PVC

1. PV

~~~yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: jenkins-k8s-pv
spec:
  capacity:
    storage: 1Gi
  accessModes:
  - ReadWriteMany
  nfs:
    server: 172.16.183.100
    path: /data/v2
~~~

2. PVC

~~~yaml
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: jenkins-k8s-pvc
  namespace: jenkins-k8s
spec:
  resources:
    requests:
      storage: 1Gi
  accessModes:
  - ReadWriteMany
~~~

3. service account

~~~sh
kubectl create sa jenkins-k8s-sa -n jenkins-k8s
kubectl create clusterrolebinding jenkins-k8s-sa-cluster -n jenkins-k8s  --clusterrole=cluster-admin --serviceaccount=jenkins-k8s:jenkins-k8s-sa
~~~

4. image
   - jenkins主镜像：`docker.io/jenkins/jenkins:2.426.3`
   - jenkins slave pod镜像：`docker.io/library/jenkins.agent:v2`

## 部署deployment

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
        image:  jenkins/jenkins:2.426.3
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8080
          name: web
          protocol: TCP
        - containerPort: 50000
          name: agent
          protocol: TCP
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

> 报错显示没有权限操作/var/jenkins_home/copy_reference_file.log文件:
>
> touch: cannot touch '/var/jenkins_home/copy_reference_file.log': Permission denied
>
> Can not write to /var/jenkins_home/copy_reference_file.log. Wrong volume permissions?
>
> 解决办法如下：
>
> ```sh
> kubectl delete -f jenkins-deployment.yaml
> chown -R 1000.1000 /data/v2
> kubectl apply -f jenkins-deployment.yaml
> ```

## 部署service

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

## 配置jenkins

### 登录

Nodeport暴露的jenkins服务，浏览器访问web ui:`http://172.16.183.101:30002/login?from=%2F`

在nfs服务端，PV存储里面获取到初始管理员密码：

~~~sh
cat  /data/v2/jenkins-home/secrets/initialAdminPassword
~~~

把密码输入到“解锁Jenkins”下面的“管理员密码”中。

### 初始化

1. 登录后选择“安装推荐的插件”，创建第一个管理员用户，配置管理员密码。
2. 实例配置中Jenkins URL填写http://172.16.183.101:30002
3. 保存，提示Jenkins已就绪

## 安装必要插件

Manage Jnekins-->插件管理-->可选插件

1. 搜索Kubernetes-->选择Kubernetes安装，搜索blueocean-->选择Blue Ocean安装
2. 安装之后选择重新启动jenkins--> http://172.16.183.101:30002/restart-->重启之后登陆jenkins，插件即可生效

# Jenkins连接k8s集群

1. 访问http://172.16.183.101:30002/configureClouds/，新增一个云，在下拉菜单中选择kubernetes并添加，kubernetes地址填https://172.16.183.100:6443 (master节点apiserver地址)
2. 测试jenkins是否可以通信：Kubernetes名称空间填jenkins-k8s，点击连接测试，如果显示“Connected to Kubernetes”说明jenkins与k8s可以进行通信
3. Jenkins地址填svc的地址：**http://jenkins-service.jenkins-k8s.svc.cluster.local:8080**

4. 点击保存

# 配置pod template

1. 在已保存的云中选择刚创建的kubernetes，进去点击Pod Templates --> Add a pod template

2. Pod Template Details中：

   - 命名空间填jenkins-k8s
   - 标签列表可以添加一个自定义的：testhan

3. 点击容器列表下的添加容器，选container template：

   - 名称：`jnlp` （固定值，必须谢jnlp）
   - Docker镜像：`docker.io/library/jenkins.agent:v2`
   - 工作目录：`/home/jenkins/agent`
   - 运行的命令 和 命令参数 两行清空
   - 分配伪终端：打勾

4. 给pod template添加卷：

   在卷中选择添加卷，添加5个Host Path Volume类型的卷：

   1. 主机路径：`/var/run/docker.sock`，挂载路径：`/var/run/docker.sock`
   2. 主机路径：`/root/.kube`，挂载路径：`/home/jenkins/,kube`
   3. 主机路径：`/usr/bin/docker`，挂载路径：`/usr/bin/docker`
   4. 主机路径：`/usr/bin/kubectl`，挂载路径：`/usr/bin/kubectl`
   5. 主机路径：`/etc/docker/daemon.json`，挂载路径：`/etc/docker/daemon.json`

5. 对工作节点上的docker.sock设置属主属组

~~~sh
chown 1000:1000  /var/run/docker.sock
chmod 777  /var/run/docker.sock
chmod  777 /usr/bin/docker
chown -R 1000.1000  /usr/bin/docker
~~~

6. 把控制节点的.kube目录复制到工作节点

~~~sh
scp -r /root/.kube/  node1:/root/
chown -R 1000.1000 /root/.kube/
~~~

7. 在Environment Variable --> 高级中，勾选以最高权限运行。
8. 在service account
