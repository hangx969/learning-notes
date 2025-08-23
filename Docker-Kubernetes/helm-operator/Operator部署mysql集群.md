# NDB Operator

MySQL NDB Cluster 是一个分布式、高可用的数据库系统，适用于需要高并发读写、低延迟和高可用性的应用场景。MySQL NDB Cluster基于 NDB（Network Database）存储引擎，并通过多个节点协同工作来提供数据的分布存储和故障恢复能力。

这里推荐使用ndb-operator，这是mysql官方维护的operator，可以方便启动mysql集群。

- 在Operatorhub中找到ndb-mysql的operator：https://operatorhub.io/operator/ndb-operator
- ndb-operator官网：[MySQL :: NDB Operator 8.4 Manual](https://dev.mysql.com/doc/ndb-operator/8.4/en/)
- github仓库：https://github.com/mysql/mysql-ndb-operator

# 架构组件

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202508231711571.png" alt="image-20250823171133476" style="zoom:50%;" />

组件介绍：

- 管理节点：Management Node，负责管理和配置整个 NDB Cluster。保存了NDB集群的配置信息，包括 Data Node、SQL Node。管理节点不直接参与数据存储或事务处理，主要负责集群的**管理和监控**，确保集群的正常运行。
- 数据节点：Data Node，数据节点是集群中**实际存储数据**的节点，负责存储一部分数据，并且数据会在多个Data Node之间进行分区和复制，以实现高可用性和负载均衡。
- SQL节点：SQL Node是用户与NDB Cluster交互的主要入口，提供了标准的MySQL SQL接口，允许用户通过SQL查询、插入、更新和删除数据。
- NDB API：可以直接与NDB存储引擎进行交互的接口。

# 安装NDB Operator

## 方法1：基于helm

[MySQL :: NDB Operator 8.4 Manual :: 2.3 Installing NDB Operator Using Helm](https://dev.mysql.com/doc/ndb-operator/8.4/en/installation-helm-chart.html)

~~~sh
helm repo add ndb-operator-repo https://mysql.github.io/mysql-ndb-operator/
helm repo update ndb-operator-repo
helm install --namespace=ndb-operator --create-namespace ndbop ndb-operator-repo/ndb-operator
~~~

## 方法2：基于yaml

[MySQL :: NDB Operator 8.4 Manual :: 2.4 Installing NDB Operator Using the YAML File and kubectl](https://dev.mysql.com/doc/ndb-operator/8.4/en/installation-yaml-file.html)

~~~sh
kubectl apply -f https://raw.githubusercontent.com/mysql/mysql-ndb-operator/main/deploy/manifests/ndb-operator.yaml
~~~

## 方法3：clone仓库

~~~sh
git clone https://github.com/mysql/mysql-ndb-operator.git
kubectl apply -f deploy/manifests/ndb-operator.yaml 
~~~

# 创建NDB Cluster

~~~yaml
apiVersion: mysql.oracle.com/v1 
kind: NdbCluster 
metadata: 
  name: example-ndb 
  namespace: public-service
spec: 
  redundancyLevel: 3 # 指定数据副本的数量。指的是数据要不要存储到其他节点，复制几份。生产环境大于等于2 
  dataNode: 
    nodeCount: 1 # 生产环境推荐>=2
    pvcSpec: 
      storageClassName: sc-nfs
      accessModes: ["ReadWriteOnce"] 
      resources: 
        requests: 
          storage: 1Gi 
  mysqlNode: 
    nodeCount: 1 # 生产环境推荐>=2
    pvcSpec: 
      storageClassName: sc-nfs
      accessModes: ["ReadWriteOnce"] 
      resources: 
        requests: 
          storage: 1Gi 
~~~

注：管理节点的数量是根据redundancyLevel决定的，配置成3就是3个管理节点

# 连接集群

mysqld的service是集群的入口服务，可以通过它访问集群

~~~sh
# 登录sql节点
kubectl exec -ti example-ndb-mysqld-0 -n ndb-cluster -- bash
# sql节点提供了客户端管理工具ndb-mgm，可以连接到管理节点
ndb_mgm -c example-ndb-mgmd 
SHOW 
~~~

也可以通过mysql客户端连接集群，首先查看集群的访问密码：

~~~sh
base64 -d <<<   $(kubectl -n ndb-cluster get secret example-ndb-mysqld-root-password \ 
-o jsonpath={.data.password}) 
~~~

登录mysql

~~~sh
mysql -h example-ndb-mysqld -uroot -p
show databases;
~~~

# 集群外部访问

因为mysql不涉及下一跳（与redis相比），所以直接新建一个NodePort类型的svc，后端pod指向mysqld的pod即可。

~~~yaml
apiVersion: v1 
kind: Service 
metadata: 
  name: example-ndb-mysqld-nodeport 
  namespace: public-service 
spec: 
  type: NodePort
  selector: 
    mysql.oracle.com/node-type: mysqld 
    mysql.oracle.com/v1: example-ndb 
  ports: 
  - name: mysqld-service-port-0 
    port: 3306 
    protocol: TCP 
    targetPort: 3306 
~~~

