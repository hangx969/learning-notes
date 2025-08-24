# 介绍

github地址：https://github.com/bitnami/charts/tree/main/bitnami/mysql

artifactHub地址：https://artifacthub.io/packages/helm/bitnami/mysql

# 下载

~~~python
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update bitnami
helm pull bitnami/mysql --version 13.0.2 
~~~

> 注：
>
> - bitnami/mysql如果网络问题pull不下来就直接从bitnami github上clone下来源码，里面就有mysql的helm chart。
>
>   ~~~sh
>   git clone https://github.com/bitnami/charts.git
>   ~~~
>
> - 注意需要把charts/bitnami/common目录放到mysql/charts/目录里面才能组成完整的helm chart，因为common是子chart需要安装。

# 配置-单节点模式

这里简单配置，用standalone模式，只有一个statefulset会被创建。service用NodePort，暴露端口30006。

> 注意：
>
> - 生产环境中不推荐使用nfs，由于其单点无高可用、性能也有问题。如果k8s中没有配置ceph等分布式储，那就不推荐把mysql等需要持久化数据的服务部署到k8s中。
>
> - 这里学习环境可以使用nfs。

~~~yaml
global:
  defaultStorageClass: "sc-nfs"
  storageClass: "sc-nfs"

image:
  registry: docker.io
  repository: bitnami/mysql
  tag: 9.3.0-debian-12-r2
  digest: ""
  pullPolicy: IfNotPresent

architecture: standalone
auth:
  rootPassword: "111111"
  createDatabase: false
  database: "hangx"

primary:
  persistence:
    enabled: true
    storageClass: "sc-nfs"
    size: 1Gi

  service:
    type: NodePort
    ports:
      mysql: 3306
      mysqlx: 33060
    nodePorts:
      mysql: "30006"
      mysqlx: "30007"
  pdb:
    create: false

# secondary:
#   persistence:
#     enabled: true
#     storageClass: "sc-nfs"
#     size: 1Gi
#   service:
#     type: NodePort
#     nodePorts:
#       mysql: "30006"
#       mysqlx: "30007"
#   pdb:
#     create: false
~~~

# 配置-主从模式

> 注意：生产环境也不推荐主从模式，建议用集群模式（用operator安装集群模式比较方便）

~~~yaml
global:
  defaultStorageClass: "sc-nfs"
  storageClass: "sc-nfs"

image:
  registry: docker.io
  repository: bitnami/mysql
  tag: 9.3.0-debian-12-r2
  digest: ""
  pullPolicy: IfNotPresent

architecture: replication
auth:
  rootPassword: "111111"
  createDatabase: false
  database: "hangx"
  replicationUser: replicator
  replicationPassword: "111111"

primary:
  persistence:
    enabled: true
    storageClass: "sc-nfs"
    size: 1Gi

  service:
    type: NodePort
    ports:
      mysql: 3306
      mysqlx: 33060
    nodePorts:
      mysql: "30006"
      mysqlx: "30007"
  pdb:
    create: false

  secondary:
    persistence:
      enabled: true
      storageClass: "sc-nfs"
      size: 1Gi
    service:
      type: NodePort
      nodePorts:
        mysql: "30006"
        mysqlx: "30007"
    pdb:
      create: false
~~~

# 安装

~~~sh
kubectl create ns mysql
helm upgrade -i mysql -n mysql -f values.dev.yaml .
~~~

# 使用

## 连接到mysql pod

名为mysql的svc是客户端用来建立连接的。

### 通过client pod连接

Execute the following to get the administrator credentials:

```sh
echo Username: root
MYSQL_ROOT_PASSWORD=$(kubectl get secret --namespace mysql mysql -o jsonpath="{.data.mysql-root-password}" | base64 -d)
```

To connect to your database:

  1. Run a pod that you can use as a client:

      ```sh
      kubectl run mysql-client --rm --tty -i --restart='Never' --image  docker.io/bitnami/mysql:9.3.0-debian-12-r2 --namespace mysql --env MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD --command -- bash
      ```

  2. To connect to primary service (read/write):

      ```sh
      mysql -h mysql.mysql.svc.cluster.local -uroot -p"$MYSQL_ROOT_PASSWORD"
      ```

### 通过mysql client cli连接

~~~python
# Ubuntu上安装mysql client
sudo apt install mysql-client-core-8.0
# 登陆mysql
mysql -h 172.16.183.102 -P 30006 -u root -p 111111
~~~

