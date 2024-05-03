# MongoDB介绍

- MongoDB是一款为web应用程序和互联网基础设施设计的数据库管理系统。是NoSQL类型的数据库。

- MongoDB提出的是文档、集合的概念，使用BSON（类JSON）作为其数据模型结构，其结构是面向对象的而不是二维表，存储一个用户在MongoDB中是这样：

  ~~~json
  {
      username: '123',
      password: '123'
  }
  ~~~

  使用这样的数据模型，使得MongoDB能在生产环境中提供高读写的能力，吞吐量较于mysql等SQL数据库大大增强。

- 易伸缩，自动故障转移。易伸缩指的是提供了分片能力，能对数据集进行分片，数据的存储压力分摊给多台服务器。自动故障转移是副本集的概念，MongoDB能检测主节点是否存活，当失活时能自动提升从节点为主节点，达到故障转移。

- 数据模型因为是面向对象的，所以可以表示丰富的、有层级的数据结构，比如博客系统中能把“评论”直接怼到“文章“的文档中，而不必像myqsl一样创建三张表来描述这样的关系。

# MongoDB高可用方案

1. 主从

   优点：将读写分离，在不同的DB上操作，可以有效降低数据库的压力，而且还能实现数据的备份

   缺点：master节点故障的时候，不能及时的自动的切换到slaves节点，需要手动干预

2. 副本集

   优点：实现了主从模式的读写分离，没有固定的“主节点；整个副本集会选出一个节点作为“主节点”，当其挂掉后，再在剩下的从节点中选举一个节点成为新的“主节点”，在副本集中总有一个主节点(primary)和一个或多个备份节点(secondary)。

   缺点：由于数据没有shard，每个节点都是一个完整的备份，则不能使用MongoDb的分布式计算功能，当然，也可以通过程序自己来实现（成本很高），所以就有了Auto shard模式

3. 分片

   优点：可以将数据自动的分解成多个块，存储在不同的节点上，每个被差分的块都有三个副本集，这样是为了数据备份和恢复，而且数据分片以后，可以利用多台廉价的存储和CPU的计算构建一个水平可扩展的计算架构，这就是我们的分布式计算

# 部署MongoDB集群

## 创建数据目录和nfs share

~~~sh
mkdir /k8s/ -p
chmod 777 /k8s
cd /k8s
mkdir /k8s/mongo-1 -p
mkdir /k8s/mongo-1/data -p
mkdir /k8s/mongo-1/key -p
mkdir /k8s/mongo-2 -p
mkdir /k8s/mongo-2/data -p
mkdir /k8s/mongo-2/key -p

tee -a /etc/exports <<'EOF'
/k8s/ *(rw,sync,no_root_squash)
EOF

exportfs -arv
~~~

## 创建configMap

~~~yaml
tee cm-mongo.yaml <<'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: mongodb-conf
  namespace: default
data:
  mongod.conf: |-
    dbpath=/mongo/data
    #logpath=/mongo/log/mongodb.log
    pidfilepath=/mongo/key/master.pid
    directoryperdb=true
    logappend=true
    bind_ip=0.0.0.0
    port=27017
EOF
~~~

## 创建PV

~~~yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: mongo-pv-1
spec:
  accessModes:
    - ReadWriteOnce
  capacity:
    storage: 2Gi
  nfs:
    path: /k8s/mongo-1
    readOnly: false
    server: 192.168.40.180
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: mongo-pv-2
spec:
  accessModes:
    - ReadWriteOnce
  capacity:
    storage: 2Gi
  nfs:
    path: /k8s/mongo-2
    readOnly: false
    server: 192.168.40.180
~~~

## 创建statefulset

~~~sh
#解压镜像
docker load -i mongo.tar.gz
~~~

~~~yaml
#headless svc
apiVersion: v1
kind: Service
metadata:
  name: mongo-1 #需要与podname同名
  namespace: default
  labels:
    name: mongo
spec:
  clusterIP: None
  selector:
    name: mongo-1
  ports:
  - name: mongo-port
    port: 27017
---
#headless svc
apiVersion: v1
kind: Service
metadata:
  namespace: default
  name: mongo-2 #需要与podname同名
  labels:
    name: mongo
spec:
  clusterIP: None
  selector:
    name: mongo-2
  ports:
  - name: mongo-port
    port: 27017
---
apiVersion: apps/v1
kind: StatefulSet
metadata: 
  namespace: default
  name: mongo-1
spec: 
  selector: 
    matchLabels: 
      name: mongo-1
  serviceName: "mongo-1"
  replicas: 1
  podManagementPolicy: Parallel
  template: 
    metadata: 
      labels: 
        name: mongo-1
        app: mongo-cluster
    spec: 
      containers: 
      - name: mongo
        image: mongo:4.2
        imagePullPolicy: IfNotPresent
        command:  
        - mongod 
        - "-f"
        - "/etc/mongod.conf"
        - "--bind_ip_all"
        - "--replSet"
        - rs0
        ports: 
        - containerPort: 27017
        volumeMounts: 
        - name: mongo-cnf-volume
          mountPath: /etc/mongod.conf/
          subPath: mongod.conf
        - name: mongo-dir 
          mountPath: /mongo
      volumes:
        - name: mongo-cnf-volume     #映射configMap信息
          configMap:
            name: mongodb-conf
            items:
              - key: mongod.conf
                path: mongod.conf
  volumeClaimTemplates: #如果在指定了sc的情况下，会自动创建pv和pvc；这里没有sc，需要先手动创建出pv，这里自动绑定。
  - metadata:
      name: mongo-dir
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 2Gi
---
apiVersion: apps/v1
kind: StatefulSet
metadata: 
  namespace: default
  name: mongo-2
spec: 
  selector: 
    matchLabels: 
      name: mongo-2
  serviceName: "mongo-2"
  replicas: 1
  podManagementPolicy: Parallel
  template: 
    metadata: 
      labels: 
        name: mongo-2
        app: mongo-cluster
    spec: 
      containers: 
      - name: mongo
        image: mongo:4.2
        imagePullPolicy: IfNotPresent
        command:  
        - mongod 
        - "-f"
        - "/etc/mongod.conf"
        - "--bind_ip_all"
        - "--replSet"
        - rs0
        ports: 
        - containerPort: 27017
        volumeMounts: 
        - name: mongo-cnf-volume
          mountPath: /etc/mongod.conf/
          subPath: mongod.conf
        - name: mongo-dir
          mountPath: /mongo
      volumes:
        - name: mongo-cnf-volume     #映射configMap信息
          configMap:
            name: mongodb-conf
            items:
              - key: mongod.conf
                path: mongod.conf
  volumeClaimTemplates:
  - metadata:
      name: mongo-dir
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 2Gi
~~~

## 初始化MongoDB集群

~~~sh
kubectl exec -it mongo-1-0 -- /bin/bash
#连接mongo数据库
mongo    
#初始化集群
rs.initiate({  _id:"rs0", // replSet指定的名称
  members:[{    _id:0,    host:"mongo-1.default.svc.cluster.local:27017" // 主节点ip与端口,
  }]
})
#mongo-2加入集群
rs.add("mongo-2.default.svc.cluster.local:27017")// 将mongo-2加入集群
#ok为1为成功
~~~

## MongoDB服务外部访问

~~~yaml
#master nodeport service
apiVersion: v1
kind: Service
metadata:
  name: mongo-1-front-service
  namespace: default
  labels:
    name: mongo-1
spec:
  type: NodePort
  externalTrafficPolicy: Cluster
  selector:
    name: mongo-1
  ports:
    - name: mongo-http
      nodePort: 30882
      port: 27017
      protocol: TCP
      targetPort: 27017
---
#slave nodeport service
apiVersion: v1
kind: Service
metadata:
  name: mongo-2-front-service
  namespace: default
  labels:
    name: mongo-2
spec:
  selector:
    name: mongo-2
  type: NodePort
  externalTrafficPolicy: Cluster
  ports:
    - name: mongo-http
      nodePort: 30883
      port: 27017
      protocol: TCP
      targetPort: 27017
~~~

> externalTrafficPolicy: Cluster
>
> 这是默认设置。在这种模式下，如果一个请求到达了任何一个节点（无论这个节点上是否有满足 Service 选择器的 Pod），这个请求都会被 Kubernetes 路由到一个符合的Pod，请求可能会跨节点路由。这意味着所有节点都可以接收到 Service 的流量，即使它们上面没有运行任何 Pod。但是，因为源 IP 地址会被替换（因为 kube-proxy 的 DNAT），所以 Pod 无法看到真实的源 IP。

- 可以使用任一节点IP加nodeport访问服务。