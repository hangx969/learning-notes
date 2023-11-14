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
    - 每个pod有唯一的网络标识符，pod名称不能随意变化
    - 持久存储的目录也不一样
    - 有序，比如mysql的主从，redis等

# statefulSet yaml编写

```yaml
#headless service
#用来定义pod网路标识，生成可解析的DNS记录
apiVersion: v1
kind: Service
metadata:
  name: svc-sts-nginx
  labels:
    app: nginx
spec:
  selector:
    app: nginx
  clusterIP: None
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
  serviceName: svc-sts-nginx #sts由前端headless service管理
  volumeClaimTemplates: #sts的存储配置，自动生成pv和pvc。注意是在sts.spec字段下的
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

- 每个pod有唯一**主机名**；根据主机名+一定规则，生成pod唯一的FQDN：**pod-name.service名称.名称空间.svc.cluster.local**
  - 例如：sts-web-0.svc-sts-nginx.default.svc.cluster.local

```bash
#查看sts pod主机名
for i in 0 1; do kubectl exec web-$i -- sh -c 'hostname';done
```

# headless service

- 不分配clusterIP，headless service可以通过解析service的FQDN（service名称.名称空间.svc.cluster.local）, 返回所有Pod的FQDN和ip地址 (statefulSet部署的Pod才有DNS)，普通的service, 只能通过解析service的DNS返回service的ClusterIP。

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

- 注意：sts必须要求先创建svc，但是不一定必须是headless svc，也可以是ClusterIP的svc

  - 如果是headless的svc，对这个service FQDN做dns解析，会找到它所关联的pod ip
  - 如果创建的service有ip，那对这个service做dns解析，会解析到service本身ip，通过ipvs规则再找到pod

- 可以再创建新的svc，NodePort类型来暴露sts的pod。

> Dig工具使用：
>
> - @来指定域名服务器、
> - -t 指定要解析的类型
>
> - A 为解析类型 ，A记录：解析域名到IP
>
> ```bash
> dig -t A svc-sts-nginx.default.svc.cluster.local @10.0.0.10
> ```

# 扩缩容