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

# 配置

这里简单配置，用standalone模式，只有一个statefulset会被创建。service用NodePort，暴露端口30006。

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

# 安装

~~~sh
kubectl create ns mysql
helm upgrade -i mysql -n mysql -f values.dev.yaml .
~~~

# 使用

## 连接到mysql pod

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
      
      
