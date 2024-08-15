# redis

- 参考地址：https://github.com/zuxqoj/kubernetes-redis-cluster
- Redis是一个开源的、基于内存的、高性能的key-value数据库。支持数据的持久化，可以将内存中的数据保存在磁盘中，重启的时候可以再次加载进行使用。

- Redis不仅仅支持简单的key-value类型的数据，同时还提供list，set，zset，hash等数据结构的存储。

- Redis支持数据的备份，即master-slave模式的数据备份。

## redis高可用

### 主从模式

- redis支持master-slave模式，一主多从，可以设置另外多个redis server为slave，从机同步主机的数据。配置后，读写分离，主机负责写，从机只负责读。减轻主机的压力。redis实现的是最终会一致性，具体选择强一致性还是弱一致性，取决于业务场景。

> Redis 是一个内存数据存储，通常运行在单个节点上，因此在单个节点上的操作都是强一致性的。也就是说，一旦一个写操作完成，随后的读操作就能立即看到这个写操作的结果。
>
> 然而，当我们谈论 Redis 的一致性时，我们通常是在谈论在 Redis 主从复制或集群环境中的一致性。在这些环境中，一致性的强度可能会变弱。
>
> - **弱一致性**：在 Redis 主从复制环境中，从服务器异步复制主服务器的数据。这意味着，当数据在主服务器上被修改后，可能需要一段时间才能在从服务器上看到这个修改。在这段时间内，主服务器和从服务器的数据可能会不一致，这就是所谓的弱一致性。
>
> - **强一致性**：Redis 并不直接支持强一致性模式。但是，你可以通过一些策略来实现类似强一致性的效果。例如，你可以使用 `WAIT` 命令来等待写操作被复制到指定数量的从服务器。或者，你可以使用 Redis 集群，将所有的写操作都发送到同一个主节点，这样可以保证在这个主节点上的一致性。
>
> 请注意，强一致性通常会牺牲一些性能和可用性。例如，使用 `WAIT` 命令会使写操作变慢，因为它需要等待数据被复制到从服务器。而在 Redis 集群中，如果主节点出现故障，可能需要一段时间才能选举出新的主节点，这期间可能无法处理写操作。

> 在 Redis 中，同步是指从服务器复制主服务器的数据。Redis 提供了两种类型的同步：全同步（full synchronization）和部分同步（partial synchronization）。
>
> 全同步：这是 Redis 主从复步制的默认方式，也是第一次复制时唯一的方式。在全同步中，从服务器连接到主服务器，发送 SYNC 命令。然后，主服务器开始在后台保存其数据，同时收集所有新的写命令并将它们添加到缓冲区。当数据保存完成后，主服务器将保存的数据和所有缓冲的写命令发送给从服务器。从服务器接收这些数据和命令，加载数据到内存，然后执行所有的写命令。
>
> 部分同步：这是 Redis 2.8 版本引入的一种优化的复制方式。如果一个从服务器断开连接，然后重新连接到主服务器，它可以请求只复制在它断开连接后发生的写命令，而不是所有的数据。这是通过使用一个复制偏移量和一个复制缓冲区来实现的。主服务器和从服务器都维护一个复制偏移量，表示它们已经复制了多少数据。当从服务器重新连接时，它发送自己的复制偏移量给主服务器。如果主服务器的复制缓冲区中包含从这个偏移量开始的所有写命令，那么它就将这些命令发送给从服务器，完成部分同步。否则，它将执行全同步。
>
> 请注意，全同步和部分同步都是为了实现主从复制，而不是为了实现强一致性。在同步完成后，主服务器和从服务器的数据可能仍然会有一段时间的不一致，因为从服务器需要时间来处理接收到的写命令。

### 哨兵模式

- Redis 哨兵模式是一种用于提供高可用性和故障转移能力的配置。哨兵模式使用 Redis Sentinel，这是一个分布式系统，用于监视 Redis 主服务器和从服务器的运行状况，并在主服务器出现故障时自动执行故障转移。

- 以下是 Redis 哨兵模式的主要特性和工作原理：

  - 监控：Redis Sentinel 不断检查所有 Redis 服务器（主服务器和从服务器）是否正常运行。


  - 通知：当一个 Redis 服务器出现故障时，Redis Sentinel 可以通过 API 向管理员或其他应用程序发送通知。


  - 自动故障转移：如果主服务器出现故障，Redis Sentinel 会自动从从服务器中选择一个提升为新的主服务器，并更新其余的从服务器，让它们复制新的主服务器。


  - 配置提供者：Redis Sentinel 可以作为一个配置提供者，客户端可以询问 Sentinel 哪个 Redis 服务器是当前的主服务器。


在一个典型的哨兵模式配置中，你会有一个主服务器，一个或多个从服务器，以及三个或更多的 Sentinel。三个 Sentinel 是为了在 Sentinel 自身出现故障时，仍然能够达成多数派，进行故障转移。

### Redis-Cluster模式

- Redis 集群模式是一种允许多个 Redis 节点协同工作，提供高可用性和数据分片功能的配置。在集群模式下，数据被分布在多个 Redis 节点上，每个节点负责维护数据的一部分。

- 以下是 Redis 集群模式的主要特性和工作原理：

  - 数据分片：在 Redis 集群中，数据被分为 16384 个哈希槽，每个节点负责一部分哈希槽。当一个键被存储到集群中时，Redis 使用一种哈希函数计算这个键应该被存储在哪个哈希槽，然后将数据存储到负责这个哈希槽的节点。


  - 高可用性：每个节点都可以有一个或多个复制节点，这些复制节点会复制主节点的数据。如果主节点出现故障，复制节点可以被提升为新的主节点，从而保证服务的可用性。


  - 读写分离：复制节点可以用于处理读请求，从而分担主节点的读取负载。


  - 线性扩展性：你可以通过添加更多的节点来扩展 Redis 集群的容量和性能。当你添加一个新的节点时，Redis 集群会自动将一部分哈希槽迁移到新的节点。


  请注意，尽管 Redis 集群提供了高可用性和数据分片，但它并不能保证强一致性。在主节点故障和故障转移期间，可能会丢失一些写操作。此外，Redis 集群需要至少三个主节点才能正常工作。

# 部署redis

## 部署nfs

- 创建NFS存储主要是为了给Redis提供稳定的后端存储，先要创建NFS，然后通过使用PV为Redis挂载一个NFS共享的路径。这样可以保证pod迁移或者重启，数据依然还是原来的数据，不会丢失

~~~sh
yum install nfs-utils -y
systemctl enable nfs --now
yum install nfs-utils -y
systemctl enable nfs --now
mkdir -p /data/redis/pv{1..6}
tee -a /etc/exports <<'EOF'
/data/redis/pv1 *(rw,no_root_squash)
/data/redis/pv2 *(rw,no_root_squash)
/data/redis/pv3 *(rw,no_root_squash)
/data/redis/pv4 *(rw,no_root_squash)
/data/redis/pv5 *(rw,no_root_squash)
/data/redis/pv6 *(rw,no_root_squash)
EOF
exportfs -arv
~~~

## 创建pv

- redis pod创建6个，三个master三个salve，每一个Redis Pod都需要一个独立的PV来存储自己的数据

~~~sh
apiVersion: v1
kind: PersistentVolume
metadata:
  name: redis-pv1
spec:
  capacity:
    storage: 500M
  accessModes:
    - ReadWriteMany
  nfs:
    server: 192.168.40.180
    path: "/data/redis/pv1"

---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: redis-pv2
spec:
  capacity:
    storage: 500M
  accessModes:
    - ReadWriteMany
  nfs:
    server: 192.168.40.180
    path: "/data/redis/pv2"

---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: redis-pv3
spec:
  capacity:
    storage: 500M
  accessModes:
    - ReadWriteMany
  nfs:
    server: 192.168.40.180
    path: "/data/redis/pv3"

---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: redis-pv4
spec:
  capacity:
    storage: 500M
  accessModes:
    - ReadWriteMany
  nfs:
    server: 192.168.40.180
    path: "/data/redis/pv4"

---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: redis-pv5
spec:
  capacity:
    storage: 500M
  accessModes:
    - ReadWriteMany
  nfs:
    server: 192.168.40.180
    path: "/data/redis/pv5"

---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: redis-pv6
spec:
  capacity:
    storage: 500M
  accessModes:
    - ReadWriteMany
  nfs:
    server: 192.168.40.180
    path: "/data/redis/pv6"
~~~

## 创建configMap

~~~sh
#redis的配置文件
tee redis.conf <<'EOF'
appendonly yes
cluster-enabled yes
cluster-config-file /var/lib/redis/nodes.conf
cluster-node-timeout 5000
dir /var/lib/redis
port 6379
EOF
~~~

~~~sh
kubectl create configmap redis-conf --from-file=redis.conf
~~~

## 部署redis服务

~~~sh
#上传解压redis镜像
docker load -i redis.tar.gz
~~~

~~~yaml
#headless svc
apiVersion: v1
kind: Service
metadata:
  name: redis-service
  labels:
    app: redis
spec:
  clusterIP: None
  selector:
    app: redis
    appCluster: redis-cluster
  ports:
  - name: redis-port
    port: 6379
---
#redis
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis-app
spec:
  serviceName: "redis-service"
  replicas: 6
  selector:
    matchLabels:
      app: redis
      appCluster: redis-cluster
  template:
    metadata:
      labels:
        app: redis
        appCluster: redis-cluster
    spec:
      containers:
      - name: redis
        image: docker.io/library/redis:v1
        imagePullPolicy: IfNotPresent
        command:
          - "redis-server"
        args:
          - "/etc/redis/redis.conf"
          - "--protected-mode"
          - "no"
        resources:
          requests:
            cpu: "100m"
            memory: "100Mi"
        ports:
          - name: redis
            containerPort: 6379
            protocol: "TCP"
          - name: cluster
            containerPort: 16379
            protocol: "TCP"
        volumeMounts:
          - name: "redis-conf"
            mountPath: "/etc/redis"
          - name: "redis-data"
            mountPath: "/var/lib/redis"
      volumes:
      - name: "redis-conf"
        configMap:
          name: "redis-conf"
          items:
            - key: "redis.conf" #cm的key是文件名，value是文件内容
              path: "redis.conf" #cm挂载到pod中的/redis.conf中
  volumeClaimTemplates:
  - metadata:
      name: redis-data
    spec:
      accessModes: [ "ReadWriteMany" ]
      resources:
        requests:
          storage: 500M
~~~

## 检测域名解析

~~~sh
kubectl run busybox --image busybox:1.28 --restart=Never --rm -it busybox -- sh
nslookup redis-app-0.redis-service.default.svc.cluster.local
~~~

# 初始化redis集群

- 创建好6个Redis Pod后，我们还需要利用常用的Redis-tribe工具进行集群的初始化，启动一个Ubuntu的容器，可以在该容器中安装Redis-tribe，进而初始化Redis集群。

~~~sh
docker load -i ubuntu.tar.gz
kubectl run -it ubuntu --image=ubuntu:v1 --image-pull-policy=IfNotPresent  --restart=Never /bin/bash

cat > /etc/apt/sources.list << EOF
deb http://mirrors.aliyun.com/ubuntu/ bionic main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ bionic main restricted universe multiverse

deb http://mirrors.aliyun.com/ubuntu/ bionic-security main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ bionic-security main restricted universe multiverse

deb http://mirrors.aliyun.com/ubuntu/ bionic-updates main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ bionic-updates main restricted universe multiverse

deb http://mirrors.aliyun.com/ubuntu/ bionic-proposed main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ bionic-proposed main restricted universe multiverse
 
deb http://mirrors.aliyun.com/ubuntu/ bionic-backports main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ bionic-backports main restricted universe multiverse
EOF

apt-get update
apt-get install -y vim wget python2.7 python-pip redis-tools dnsutils
pip install redis-trib==0.5.1

#创建只有master节点的redis集群
redis-trib.py create \
  `dig +short redis-app-0.redis-service.default.svc.cluster.local`:6379 \
  `dig +short redis-app-1.redis-service.default.svc.cluster.local`:6379 \
  `dig +short redis-app-2.redis-service.default.svc.cluster.local`:6379
  
#为每个Master添加Slave
redis-trib.py replicate \
  --master-addr `dig +short redis-app-0.redis-service.default.svc.cluster.local`:6379 \
  --slave-addr `dig +short redis-app-3.redis-service.default.svc.cluster.local`:6379

redis-trib.py replicate \
  --master-addr `dig +short redis-app-1.redis-service.default.svc.cluster.local`:6379 \
  --slave-addr `dig +short redis-app-4.redis-service.default.svc.cluster.local`:6379

redis-trib.py replicate \
  --master-addr `dig +short redis-app-2.redis-service.default.svc.cluster.local`:6379 \
  --slave-addr `dig +short redis-app-5.redis-service.default.svc.cluster.local`:6379
~~~

- 连接到集群测试

~~~sh
kubectl exec -it redis-app-2 -- /bin/bash
/usr/local/bin/redis-cli -c 
127.0.0.1:6379> cluster info
~~~

# 创建外部访问svc

~~~yaml
apiVersion: v1
kind: Service
metadata:
  name: redis-access-service
  labels:
    app: redis
spec:
  selector:
    app: redis
    appCluster: redis-cluster
  ports:
  - name: redis-port
    protocol: "TCP"
    port: 6379
    targetPort: 6379
#也可以加一个NodePort，从集群外部访问
~~~

# 测试集群主从切换

~~~sh
kubectl exec -it redis-app-0 -- /bin/bash
/usr/local/bin/redis-cli -c 
127.0.0.1:6379> role
~~~

~~~sh
#删掉master pod
kubectl delete pods redis-app-0 --force --grace-period=0
#重新进入新创建出来的pod
kubectl exec -it redis-app-0 -- /bin/bash
/usr/local/bin/redis-cli -c
127.0.0.1:6379> role
~~~

