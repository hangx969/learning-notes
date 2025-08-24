# 自动扩缩容工具

## HPA

Horizonal Pod Autoscaling，pod水平自动伸缩。一般是扩缩容deployment和statefulset。

### 根据什么指标

通过此功能，可以利用监控指标（cpu使用率、磁盘、自定义等）自动的扩容或缩容服务中Pod数量。

当业务需求增加时，系统将无缝地自动增加适量pod容器，提高系统稳定性。

### 指标怎么获取

基于metrics-server自动获取节点和pod的资源指标。

### 怎么实现扩缩容

- K8s的HPA controller已经实现了一套简单的自动扩缩容逻辑，默认情况下，每30s检测一次指标，只要检测到了配置HPA的目标值，则会计算出预期的工作负载的副本数，再进行扩缩容操作。
- 同时，为了避免过于频繁的扩缩容，默认在5min内没有重新扩缩容的情况下，才会触发扩缩容。
- HPA本身的算法相对比较保守，可能并不适用于很多场景。例如，一个快速的流量突发场景，如果正处在5min内的HPA稳定期，这个时候根据HPA的策略，会导致无法扩容。

> 注意：针对原生HPA
>
> 1. 必须安装metrics-server或者其他自定义metrics-server
> 2. pod必须配置requests。因为HPA就是根据requests来计算使用率的

## VPA

- Vertical Pod Autoscaler，垂直 Pod 自动扩缩容，VPA会基于Pod的资源使用情况自动为设置资源占用的request，从而让集群将Pod调度到有足够资源的最佳节点上。
- VPA也会保持最初容器定义中资源request和limit的占比。它会根据容器资源使用率自动设置pod的CPU和内存的requests的值，从而允许在节点上进行适当的调度，以便为每个 Pod 提供适当的可用的节点。
- 既可以缩小过度请求资源的容器，也可以根据其使用情况随时提升资源不足的容量。
- 不能与HPA一起使用。

> Pod 资源用其所需，所以集群节点使用效率高。Pod 会被安排到具有适当可用资源的节点上。
>
> 不必运行基准测试任务来确定 CPU 和内存请求的合适值。VPA 可以随时调整 CPU 和内存请求，无需人为操作，因此可以减少维护时间。
>
> VPA是Kubernetes比较新的功能，还没有在生产环境大规模实践过，不建议在线上环境使用自动更新模式，但是使用推荐模式你可以更好了解服务的资源使用情况。

## KPA

- Knative Pod Autoscaler：基于请求数对Pod自动扩缩容，KPA 的主要限制在于它不支持基于 CPU 的自动扩缩容。
- 支持根据并发请求数实现自动扩缩容；支持设置扩缩容上下限。可以和HPA混合使用。
- Github： https://knative.dev/docs/install/

- 安装参考：https://knative.dev/docs/install/install-serving-with-yaml/

## cluster-autoscaler

- 什么是cluster autoscaler

  - Cluster Autoscaler (CA)是一个独立程序，是用来弹性伸缩kubernetes集群的。它可以自动根据部署应用所请求的资源量来动态的伸缩集群。当集群容量不足时，它会自动去 Cloud Provider （支持 GCE、GKE 和 AWS）创建新的 Node，而在 Node 长时间资源利用率很低时自动将其删除以节省开支。

  - 项目地址：https://github.com/kubernetes/autoscaler

- 什么时候集群节点不会被 CA 删除?

  1）节点上有pod被 PodDisruptionBudget 控制器限制。
  2）节点上有命名空间是 kube-system 的pods。
  3）节点上的pod不是被控制器创建，例如不是被deployment, replica set, job, stateful set创建。
  4）节点上有pod使用了本地存储
  5）节点上pod驱逐后无处可去，即没有其他node能调度这个pod
  6）节点有注解：`"cluster-autoscaler.kubernetes.io/scale-down-disabled": "true"`(在CA 1.0.3或更高版本中受支持)

  > kubectl annotate node <nodename> cluster-autoscaler.kubernetes.io/scale-down-disabled=true

- cluster autoscaler适用的云厂商
  - GCE https://kubernetes.io/docs/concepts/cluster-administration/cluster-management/
  - GKE https://cloud.google.com/container-engine/docs/cluster-autoscaler
  - AWS（亚马逊） https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/cloudprovider/aws/README.md
  - Azure（微软） https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/cloudprovider/azure/README.md
  - Alibaba Cloud https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/cloudprovider/alicloud/README.md
  - OpenStack Magnum https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/cloudprovider/magnum/README.md
  - DigitalOcean https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/cloudprovider/digitalocean/README.md
  - CloudStack https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/cloudprovider/cloudstack/README.md
  - Exoscale https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/cloudprovider/exoscale/README.md
  - Packet https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/cloudprovider/packet/README.md
  - OVHcloud https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/cloudprovider/ovhcloud/README.md
  - Linode https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/cloudprovider/linode/README.md
  - Hetzner https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/cloudprovider/hetzner/README.md
  - Cluster API  https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/cloudprovider/clusterapi/README.md

# HPA自动扩缩容实战

## HPA基于CPU实现pod扩缩容

### HPA

- HPA由Kubernetes API资源和控制器实现。控制器会周期性的获取平均CPU利用率，并与目标值相比较后调整deployment中的副本数量。
- K8S从1.8版本开始，CPU、内存等资源的metrics信息可以通过 Metrics API来获取，用户可以直接获取这些metrics信息（例如通过执行kubect top命令），HPA使用这些metics信息来实现动态伸缩。

### 版本

- 查看当前支持的api version

~~~sh
kubectl api-versions | grep autoscal
autoscaling/v1
autoscaling/v2
autoscaling/v2beta1
autoscaling/v2beta2
~~~

- autoscaling/v2beta1支持Resource Metrics（资源指标，如pod内存）和Custom Metrics（自定义指标）的缩放
- autoscaling/v2beta2支持Resource Metrics（资源指标，如pod内存）和Custom Metrics（自定义指标）和 ExternalMetrics（额外指标）的缩放。

### 工作原理

- HPA的实现是一个控制循环，由controller manager的--horizontal-pod-autoscaler-sync-period参数指定周期（默认值为15秒）。每个周期内，controller manager根据每个HorizontalPodAutoscaler定义中指定的指标查询资源利用率。controller manager可以从resource metrics API（pod 资源指标）和custom metrics API（自定义指标）获取指标。
- 然后，通过现有pods的CPU使用率的平均值（计算方式是最近的pod使用量（最近一分钟的平均值，从metrics-server中获得）除以设定的每个Pod的CPU使用率限额）跟目标使用率进行比较。
- 计算扩容后Pod的个数：sum(最近一分钟内某个Pod的CPU使用率的平均值)/CPU使用上限的整数+1。并且在扩容时，还要遵循预先设定的副本数限制：MinReplicas <= Replicas <= MaxReplicas。

## HPA基于内存实现pod扩缩容

### kubectl创建nginx pod

~~~yaml
tee deploy-nginx.yaml <<'EOF' 
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-hpa
spec:
  selector:
    matchLabels:
      app: nginx
  replicas: 1
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.9.1
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 80
          name: http
          protocol: TCP
        resources:
          requests:
            cpu: 0.01
            memory: 25Mi
          limits:
            cpu: 0.05
            memory: 60Mi
---
apiVersion: v1
kind: Service
metadata:
  name: nginx
  labels:
    app: nginx
spec:
  selector:
    app: nginx
  type: NodePort
  ports:
  - name: http
    protocol: TCP
    port: 80
    targetPort: 80
EOF
kubectl apply -f deploy-nginx.yaml
~~~

> 注意：pod定义中必须要有memory的requests、limits，HPA才能检测得到指标从而起作用

### yaml文件创建HPA

~~~yaml
tee hpa-mem.yaml <<'EOF'
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: nginx-hpa
spec:
    maxReplicas: 10
    minReplicas: 1
    scaleTargetRef:
      apiVersion: apps/v1
      kind: Deployment
      name: nginx-hpa
    metrics:
    - type: Resource
      resource:
        name: memory
        target:
          averageUtilization: 60
          type: Utilization
EOF
kubectl apply -f hpa-mem.yaml
~~~

### 压测

~~~sh
kubectl exec -it nginx-hpa-7f5d6fbfd9-s8wbh  -- /bin/sh
#压测
dd if=/dev/zero of=/tmp/a
~~~

> 查看某个版本的hpa的字段定义
>
> ~~~sh
> kubectl get hpa.v2beta2.autoscaling -o yaml > 1.yaml
> ~~~

## 利用HPA扩缩容PHP服务

- 官网示例：[HorizontalPodAutoscaler 演练 | Kubernetes](https://kubernetes.io/zh-cn/docs/tasks/run-application/horizontal-pod-autoscale-walkthrough/)

### dockerfile构建PHP服务

- 准备镜像

~~~sh
#使用dockerfile构建一个新的镜像，在k8s的xianchaomaster1节点构建
docker load -i php.tar.gz
mkdir php && cd php/

tee dockerfile <<'EOF' 
FROM php:5-apache
ADD index.php /var/www/html/index.php
RUN chmod a+rx index.php
EOF

tee index.php <<'EOF' 
<?php
$x = 0.0001;
for ($i = 0; $i <= 1000000;$i++) {
$x += sqrt($x);
  }
 echo "OK!";
?>
EOF
#构建镜像
docker build -t k8s.gcr.io/hpa-example:v1 .
#打包镜像
docker save -o hpa-example.tar.gz k8s.gcr.io/hpa-example:v1
~~~

- 部署镜像

~~~sh
#拷贝到工作节点并解压
scp hpa-example.tar.gz node1:/root/
docker load -i hpa-example.tar.gz
~~~

~~~yaml
tee php-apache.yaml <<'EOF' 
apiVersion: apps/v1
kind: Deployment
metadata: 
  name: php-apache
spec:
  selector:
    matchLabels:
      run: php-apache
  replicas: 1
  template:
    metadata:
      labels:
        run: php-apache
    spec:
      containers:
      - name: php-apache
        image: k8s.gcr.io/hpa-example:v1
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 80
        resources:
          limits:
            cpu: 500m
          requests:
            cpu: 200m
---
apiVersion: v1
kind: Service
metadata:
    name: php-apache
    labels:
      run: php-apache
spec:
  ports:
  - port: 80
  selector:
   run: php-apache
EOF
kubectl apply -f php-apache.yaml
~~~

> 注意：pod定义中必须要有CPU的requests、limits，HPA才能检测得到指标从而起作用

### 创建HPA

~~~sh
#1）让副本数维持在1-10个之间（这里副本数指的是通过deployment部署的pod的副本数）
#2）将所有Pod的平均CPU使用率维持在50％（每个pod如果requests了200毫核，那么目标就是让平均CPU利用率为100毫核）
kubectl autoscale deployment php-apache --cpu-percent=50 --min=1 --max=10
k get hpa
#由于我们没有向服务器发送任何请求，因此当前CPU消耗为0％（TARGET列显示了由相应的deployment控制的所有Pod的平均值）。
~~~

### 压测

~~~sh
#busybox.tar.gz和nginx-1-9-1.tar.gz上传
docker load -i busybox.tar.gz 
docker load -i nginx-1-9-1.tar.gz
#启动一个容器，并将无限查询循环发送到php-apache服务
kubectl run stress-test -it --image=busybox --image-pull-policy=IfNotPresent /bin/sh
while true; do wget -q -O- http://php-apache.default.svc.cluster.local; done
~~~

# VPA实现pod垂直扩缩容

- Vertical Pod Autoscaler（VPA）：垂直Pod自动扩缩容，用户无需为其pods中的容器设置最新的资源request。配置后，它将根据使用情况自动设置request，从而允许在节点上进行适当的调度，以便为每个pod提供适当的资源量。

工作原理：

![img](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202502141048078.png)

## 安装VPA

~~~sh
docker load -i vpa-admission_0.10.0.tar.gz && docker load -i vpa-recommender_0.10.0.tar.gz && docker load -i vpa-updater_0.10.0.tar.gz #可选，这些镜像是后面的安装yaml文件里面定义的镜像
#master节点上
tar zxvf autoscaler-master.tar.gz
#升级openssl：
yum install gcc gcc-c++ -y
wget https://www.openssl.org/source/openssl-1.1.1k.tar.gz --no-check-certificate && tar zxf openssl-1.1.1k.tar.gz && cd openssl-1.1.1k
./config
make && make install
mv /usr/local/bin/openssl /usr/local/bin/openssl.bak && mv apps/openssl /usr/local/bin
rm -rf /usr/lib64/libssl.so.1.1 && ln -s /usr/local/lib64/libssl.so.1.1 /usr/lib64/libssl.so.1.1
rm -rf /usr/lib64/libcrypto.so.1.1 && ln -s /usr/local/lib64/libcrypto.so.1.1 /usr/lib64/libcrypto.so.1.1
cd /root/autoscaler-master/vertical-pod-autoscaler/hack
./vpa-up.sh
kubectl get pods -n kube-system | grep vpa
~~~

## 部署nginx

~~~sh
mkdir vpa && cd vpa/
kubectl create ns vpa
~~~

~~~yaml
tee deploy-nginx.yaml <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
  namespace: vpa
  labels:
    app: nginx
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - image: nginx
        name: nginx
        imagePullPolicy: IfNotPresent
        resources:
          requests:
            cpu: 200m
            memory: 300Mi
---
apiVersion: v1
kind: Service
metadata:
  name: nginx
  namespace: vpa
spec:
  selector:
    app: nginx
  type: NodePort
  ports:
  - port: 80
    targetPort: 80
EOF
kubectl apply -f deploy-nginx.yaml
~~~

## 创建VPA

- updateMode:”Off”模式，这种模式仅获取资源推荐值，但是不更新Pod

~~~yaml
tee vpa-nginx.yaml <<'EOF' 
apiVersion: autoscaling.k8s.io/v1beta2
kind: VerticalPodAutoscaler
metadata:
  name: nginx-vpa
  namespace: vpa
spec:
  targetRef:
    apiVersion: "apps/v1"
    kind: Deployment
    name: nginx
  updatePolicy:
    updateMode: "Off"
  resourcePolicy:
    containerPolicies:
    - containerName: "nginx"
      minAllowed: #Specifies the minimal amount of resources that will be recommended for the container. The default is no minimum.
        cpu: "500m"
        memory: "100Mi"
      maxAllowed:
        cpu: "2000m"
        memory: "2600Mi"
EOF
kubectl apply -f vpa-nginx.yaml
~~~

- 查看VPA

~~~yaml
kubectl describe vpa nginx-vpa -n vpa

Status:
  Conditions:
    Last Transition Time:  2024-05-19T09:13:42Z
    Status:                True
    Type:                  RecommendationProvided
  Recommendation:
    Container Recommendations:
      Container Name:  nginx
      #VPA去调整requests字段值的上下限和推荐值
      Lower Bound: #下限值
        Cpu:     500m
        Memory:  262144k
      Target: #推荐值
        Cpu:     500m
        Memory:  262144k #256Mi
      Uncapped Target:
        Cpu:     25m
        Memory:  262144k
      Upper Bound: #上限值
        Cpu:     576m
        Memory:  602928571
Events:          <none>
~~~

- describe的结果表示：推荐的 Pod 的 CPU 请求为 500m，推荐的内存请求为 262144k 字节（256Mi）。

## 压测nginx

~~~sh
#使用ab作为压测工具
yum -y install httpd-tools
ab -c 100 -n 10000000 http://192.168.40.180:30327/
#VPA对于requests的推荐值的变化
kubectl describe vpa nginx-vpa -n vpa
~~~

- 修改updateMode:”Auto”

~~~yaml
tee vpa-nginx.yaml <<'EOF' 
apiVersion: autoscaling.k8s.io/v1beta2
kind: VerticalPodAutoscaler
metadata:
  name: nginx-vpa
  namespace: vpa
spec:
  targetRef:
    apiVersion: "apps/v1"
    kind: Deployment
    name: nginx
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: "nginx"
      minAllowed: #Specifies the minimal amount of resources that will be recommended for the container. The default is no minimum.
        cpu: "500m"
        memory: "100Mi"
      maxAllowed:
        cpu: "2000m"
        memory: "2600Mi"
EOF
kubectl apply -f vpa-nginx.yaml
~~~

~~~yaml
tee deploy-nginx.yaml <<'EOF' 
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: nginx
  name: nginx
  namespace: vpa
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - image: nginx
        imagePullPolicy: IfNotPresent
        name: nginx
        resources:
          requests:
            cpu: 100m
            memory: 50Mi
EOF
kubectl apply -f deploy-nginx.yaml
~~~

~~~sh
ab -c 100 -n 10000000 http://192.168.40.180:30327/
#VPA对于requests的推荐值的变化
kubectl describe vpa nginx-vpa -n vpa
~~~

- 查看event的扩缩容事件

~~~sh
kubectl get event -n vpa
#vpa执行了EvictedByVPA，自动停掉了nginx，然后使用 VPA推荐的资源启动了新的nginx
#随着服务的负载的变化，VPA的推荐值也会不断变化。当目前运行的pod的资源达不到VPA的推荐值，就会执行pod驱逐，重新部署新的足够资源的服务。
~~~

# metrics-server

## Metrics-server

- metrics-server是一个集群范围内的资源数据集和工具，同样的，metrics-server也只是显示数据，并不提供数据存储服务，主要关注的是资源度量API的实现，比如CPU、文件描述符、内存、请求延时等指标，metric-server收集数据给k8s集群内使用，如kubectl,hpa,scheduler等。

- Github地址：

  https://github.com/kubernetes-sigs/metrics-server/

  https://github.com/kubernetes-sigs/metrics-server/releases/tag/v0.6.1

## 部署

~~~sh
#可选：上传镜像registry.cn-hangzhou.aliyuncs.com/google_containers/metrics-server:v0.6.1并在所有节点解压
docker load -i registry.cn-hangzhou.aliyuncs.com/google_containers/metrics-server:v0.6.1

#master节点上修改apiserver参数，允许在不修改Kubernetes核心代码的同时扩展Kubernetes API。
vim /etc/kubernetes/manifests/kube-apiserver.yaml
#增加如下内容：
- --enable-aggregator-routing=true

#使配置生效，在所有节点上
systemctl restart kubelet
#这个操作重启apiserver，会影响业务，最好在装集群的时候就配置好
~~~

> - --enable-aggregator-routing=true 是 Kubernetes API 服务器的一个配置参数。当设置为 true 时，它告诉 API 服务器通过 Kubernetes 服务 IP 路由到扩展 API 服务器，而不是直接路由到扩展 API 服务器的 Pod IP。这是在 Kubernetes 集群中使用 API 聚合层（API Aggregation Layer）时的一个重要配置。
>
> - API 聚合层允许 Kubernetes 提供更丰富和更复杂的 API，而无需将所有这些功能添加到 Kubernetes 核心 API 中。例如，服务目录 API、自定义资源定义 API 和其他扩展 API 都可以通过 API 聚合层提供。

~~~yaml
tee components.yaml <<'EOF'
apiVersion: v1
kind: ServiceAccount
metadata:
  labels:
    k8s-app: metrics-server
  name: metrics-server
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  labels:
    k8s-app: metrics-server
    rbac.authorization.k8s.io/aggregate-to-admin: "true"
    rbac.authorization.k8s.io/aggregate-to-edit: "true"
    rbac.authorization.k8s.io/aggregate-to-view: "true"
  name: system:aggregated-metrics-reader
rules:
- apiGroups:
  - metrics.k8s.io
  resources:
  - pods
  - nodes
  verbs:
  - get
  - list
  - watch
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  labels:
    k8s-app: metrics-server
  name: system:metrics-server
rules:
- apiGroups:
  - ""
  resources:
  - nodes/metrics
  verbs:
  - get
- apiGroups:
  - ""
  resources:
  - pods
  - nodes
  verbs:
  - get
  - list
  - watch
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  labels:
    k8s-app: metrics-server
  name: metrics-server-auth-reader
  namespace: kube-system
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: extension-apiserver-authentication-reader
subjects:
- kind: ServiceAccount
  name: metrics-server
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  labels:
    k8s-app: metrics-server
  name: metrics-server:system:auth-delegator
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: system:auth-delegator
subjects:
- kind: ServiceAccount
  name: metrics-server
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  labels:
    k8s-app: metrics-server
  name: system:metrics-server
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: system:metrics-server
subjects:
- kind: ServiceAccount
  name: metrics-server
  namespace: kube-system
---
apiVersion: v1
kind: Service
metadata:
  labels:
    k8s-app: metrics-server
  name: metrics-server
  namespace: kube-system
spec:
  ports:
  - name: https
    port: 443
    protocol: TCP
    targetPort: https
  selector:
    k8s-app: metrics-server
---
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    k8s-app: metrics-server
  name: metrics-server
  namespace: kube-system
spec:
  selector:
    matchLabels:
      k8s-app: metrics-server
  strategy:
    rollingUpdate:
      maxUnavailable: 0
  template:
    metadata:
      labels:
        k8s-app: metrics-server
    spec:
      containers:
      - args:
        - /metrics-server
        - --cert-dir=/tmp
        - --secure-port=4443
        - --kubelet-insecure-tls
        - --kubelet-preferred-address-types=InternalIP
        - --kubelet-use-node-status-port
        - --metric-resolution=15s
        image: registry.cn-hangzhou.aliyuncs.com/google_containers/metrics-server:v0.6.1
        imagePullPolicy: IfNotPresent
        livenessProbe:
          httpGet:
            path: /livez
            port: https
            scheme: HTTPS
          periodSeconds: 10
        name: metrics-server
        ports:
        - containerPort: 4443
          name: https
          protocol: TCP
        readinessProbe:
          httpGet:
            path: /readyz
            port: https
            scheme: HTTPS
          initialDelaySeconds: 20
          periodSeconds: 10
        resources:
          requests:
            cpu: 100m
            memory: 10Mi
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          runAsNonRoot: true
          runAsUser: 1000
        volumeMounts:
        - mountPath: /tmp
          name: tmp-dir
      nodeSelector:
        kubernetes.io/os: linux
      priorityClassName: system-cluster-critical
      serviceAccountName: metrics-server
      volumes:
      - emptyDir: {} 
        name: tmp-dir
---
apiVersion: apiregistration.k8s.io/v1
kind: APIService
metadata:
  labels:
    k8s-app: metrics-server
  name: v1beta1.metrics.k8s.io
spec:
  group: metrics.k8s.io
  groupPriorityMinimum: 100
  insecureSkipTLSVerify: true
  service:
    name: metrics-server
    namespace: kube-system
  version: v1beta1
  versionPriority: 100
EOF
~~~

~~~sh
#部署metrics-server pod
kubectl apply -f components.yaml
#测试
kubectl top nodes
kubectl top pods -n kube-system
~~~
