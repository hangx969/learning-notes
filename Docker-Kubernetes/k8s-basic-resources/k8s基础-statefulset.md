# 应用的状态

- 无状态和有状态应用区别

  - 无状态
    - POD都是一样的
    - 没有顺序要求
    - 不用考虑在哪个node上运行
    - 随意进行伸缩和扩展

  - 有状态
    - 上面的因素都要考虑
    - **每个pod都是独立的，保持启动顺序和唯一性**
    - 每个pod有唯一的网络标识符（有dns名称），pod名称不能随意变化
    - 持久存储的目录也不一样
    - 有序，比如mysql的主从，redis等

# sts介绍

sts是k8s的有状态资源调度器。部署有状态且需要有序启动的服务，比如mysql、zookeeper、eureka、nacos、MongoDB、ES、redis、kafka等。

sts基于headless svc给每一个pod分配一个唯一且固定的网络标识符，各pod之间通过这个标识符来通信。

# statefulSet yaml编写

```yaml
# headless service，用来定义pod网络标识，生成可解析的DNS记录
apiVersion: v1
kind: Service
metadata:
  name: svc-sts-nginx
  labels:
    app: nginx
spec:
  selector:
    app: nginx
  clusterIP: None # 这里才真正标识了svc是headless svc
  ports:
  - name: web
    port: 80
---
apiVersion: apps/v1
kind: StatefulSet
metadata: 
  name: sts-web
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  serviceName: svc-sts-nginx # sts由前端headless service管理。这个字段是sts独有的。
  volumeClaimTemplates: # sts的存储配置，自动生成pv和pvc。注意是在sts.spec字段下的
  - metadata:
      name: www
    spec:
      storageClassName: sc-nfs
      accessModes:
      - ReadWriteOnce
      resources:
        requests:
          storage: 1Gi
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx
        imagePullPolicy: IfNotPresent
        ports:
        - name: web
          containerPort: 80
        volumeMounts:
        - name: www #写volumeClaimTemplates的name
          mountPath: /usr/share/nginx/html
```

# POD主机名

- 每个pod有唯一**主机名**：**pod-name.service名称.名称空间.svc.cluster.local**
  
  例如：sts-web-0.svc-sts-nginx.default.svc.cluster.local

```bash
#查看sts pod主机名
for i in 0 1; do kubectl exec web-$i -- sh -c 'hostname';done
```

# headless service

- 不分配clusterIP怎么访问pod？

  - headless service可以通过解析service的FQDN（`<svc>.<ns>.svc.cluster.local`）, 返回所有Pod的FQDN和ip地址 (statefulSet部署的Pod才有FQDN：`<pod>.<ns>.svc.cluster.local`)

  - 普通的service, 只能通过解析service的DNS返回service的ClusterIP，再通过endpoint找到pod ip。


  ```bash
  #集群内解析headless service的FQDN ==> 直接解析出pod的IP
  nslookup svc-sts-nginx.default.svc.cluster.local
  
  Server:         10.0.0.10
  Address:        10.0.0.10:53
  
  Name:   svc-sts-nginx.default.svc.cluster.local
  Address: 10.244.1.9
  Name:   svc-sts-nginx.default.svc.cluster.local
  Address: 10.244.1.8
  ```

- 注意：

  1. sts必须要求先创建svc，但是不一定必须是headless svc，也可以是ClusterIP的svc
     - 如果是headless的svc，对这个service FQDN做dns解析，会找到它所关联的pod ip
     - 如果创建的service有ip，那对这个service做dns解析，会解析到service本身ip，通过ipvs规则再找到pod

  2. headless svc一般只用作集群内部通信。要给集群外部通信，可以再创建新的svc，NodePort类型来暴露sts的pod。


> Dig工具使用：
>
> - @来指定域名服务器
> - -t 指定要解析的类型
>
> - A 为解析类型 ，A记录：解析域名到IP
>
> ```bash
> dig -t A svc-sts-nginx.default.svc.cluster.local @10.0.0.10
> ```

# 存储模板

- 对于有状态应用都会用到持久化存储，比如mysql主从，由于主从数据库的数据是不能存放在一个目录下的，每个mysql节点都需要有自己**独立的存储空间**。

- 而在deployment中创建的存储卷是一个共享的存储卷，多个pod使用同一个存储卷，它们数据是同步的；而statefulset定义中的每一个pod都不能使用同一个存储卷，这就需要使用`volumeClainTemplate`。

- 当在使用statefulset创建pod时，`volumeClainTemplate`会自动生成一个PVC，从而请求绑定一个PV，每一个pod都有自己专用的存储卷。Pod、PVC和PV对应的关系图如下：

  ![image-20240324095254313](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202403240952473.png)

# 扩缩容

- 直接修改yaml文件扩缩容
  - 扩容：pod name从小到大开始扩。
  - 缩容：pod name从大到小依次减小。

# 滚动更新

- 定义字段

  ```bash
  kubectl explain sts.spec.updateStrategy
  ```

- yaml文件

  ```yaml
  apiVersion: apps/v1
  kind: StatefulSet
  metadata: 
    name: sts-web
  spec:
    replicas: 2
    selector:
      matchLabels:
        app: nginx
    serviceName: svc-sts-nginx #sts由前端headless service管理
    updateStrategy: 
      type: RollingUpdate #type还有OnDelete，OnDelete不会让pod自动更新，只有手动删除pod，才会自动创建新的pod
      rollingUpdate:
        maxUnavailable: 0 # 与deployment的更新策略类似，这里写0，就代表replicas规定的数量一个也不能少。
        partition: 1 # 1就代表更新的时候只更新pod序号 >= 1的
    template:
      metadata:
        labels:
          app: nginx
      spec:
        containers:
        - name: nginx
          image: nginx
          imagePullPolicy: IfNotPresent
          ports:
          - name: web
            containerPort: 80
          volumeMounts:
          - name: www # 写volumeClaimTemplates的name
            mountPath: /usr/share/nginx/html
  ```

  # 案例-部署web站点
  
  ~~~yaml
  #sts
  apiVersion: apps/v1
  kind: StatefulSet
  metadata:
    name: sts-web
    namespace: default
    labels:
      app: web
  spec:
    replicas: 2
    selector:
      matchLabels:
         app: nginx
    serviceName: svc-sts-web
    template:
      metadata:
        namespace: default
        labels:
          app: nginx
      spec:
        containers:
          name: nginx
          image: nginx
          imagePullPolicy: IfNotPresent
          ports:
          - name: www
            containerPort: 80
            protool: TCP
          volumeMounts:
          - name: storage-web
            mountPath: /usr/share/nginx/html
    volumeClaimTemplates:
    - metadata:
        name: storage-web
        namespace: default
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: sc-web
        resources:
          requests: 
            storage: 1Gi
            
  #svc
  ---
  apiVersion: v1
  kind: Service
  metadata:
    name: svc-sts-web
    namespace: default
  spec:
    clusterIP: None
    selector:
      app: nginx
    ports:
    - name: www
      port: 80
      protocol: TCP
  
  #sc
  ---
  apiVersion: storage.k8s.io/v1
  kind: StorageClass
  metadata:
    name: nfs-web
  provisioner: example.com/nfs
  ~~~
  
  