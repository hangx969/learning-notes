# 背景

## harbor

说到搭建自建 Docker 镜像仓库，业内推荐最多的是 Harbor。然而，Harbor 并没有集成高可用（HA），这使得其服务相对不那么可靠。如果开发者想要创建一个高可用 Harbor 集群，通常需要先创建和配置高可用 Redis 和 PostgreSQL 集群，但这一过程却相当麻烦。

> - Harbor 架构图: *https://goharbor.io/docs/2.1.0/install-config/harbor-ha-helm/#architecture*
>
>
> - Harbor 环境要求: *https://goharbor.io/docs/2.11.0/install-config/installation-prereqs/*

## KubeBlocks

- KubeBlocks 是一个可以管理多种数据库和有状态中间件的 K8s operator，支持管理 MySQL、PostgreSQL、Redis、MongoDB、Kafka、ClickHouse、Elasticsearch 等 30 余种数据库。其原理是定义一组通用和抽象的 API（CRDs）来描述各种引擎的共同属性，在其之上，数据库厂商和开发者可以通过插件来描述不同引擎的差异。

# 安装kbcli和KubeBlocks

> - 检查[环境要求](https://kubeblocks.io/docs/release-0.8/api_docs/installation/install-with-kbcli/install-kubeblocks-with-kbcli#environment-preparation)
> - [安装kbcli](https://kubeblocks.io/docs/preview/user_docs/installation/install-with-kbcli/install-kbcli)
> - [安装KubeBlocks](https://kubeblocks.io/docs/preview/user_docs/installation/install-with-kbcli/install-kubeblocks-with-kbcli)

1. 安装 kbcli。

   ```sh
   curl -fsSL https://kubeblocks.io/installer/install_cli.sh | bash
   ```

2. 安装 KubeBlocks。

   ```sh
   kbcli kubeblocks install
   ```

3. 检查 KubeBlocks 是否安装成功。

   ```sh
   kbcli kubeblocks status
   ```

4. 在 KubeBlocks 中开启 PostgreSQL 和 Redis 引擎。这两个引擎默认开启。您可以执行以下命令，检查引擎启用状态。如果引擎未启用，您可以参考官方文档[启用引擎](https://kubeblocks.io/docs/release-0.8/api_docs/overview/supported-addons#use-addons)。

   ```sh
   kbcli addon list
   ```

# 创建postgreSQL和redis集群

1. 创建一个名为 harbor 的独立 namespace，将集群资源独立出来。

   ```sh
   kubectl create namespace harbor
   ```

2. 创建 PostgreSQL 集群。本文中我们使用了 replication 模式，创建了主备集群，可支持自动故障转移。关于创建集群的细节，可参考[官方文档](https://kubeblocks.io/docs/preview/user_docs/kubeblocks-for-postgresql/cluster-management/create-and-connect-a-postgresql-cluster)。

   ```sh
   kbcli cluster create postgresql mypg --mode replication --namespace harbor
   ```

3. 创建 Redis 集群。本文中我们使用了 replication 模式，指定版本为 redis-7.0.6。KubeBlocks 将创建 sentinel 模式的主备集群，关于创建集群的细节，可参考[官方文档](https://kubeblocks.io/docs/preview/user_docs/kubeblocks-for-redis/cluster-management/create-and-connect-a-redis-cluster)

   ```sh
   kbcli cluster create redis myredis --mode replication --version redis-7.0.6 --namespace harbor
   ```

4. 查看已创建的集群状态，确保两个集群的状态都为 `Running`。

   ```sh
   kbcli cluster list --namespace harbor
   ```

# 连接集群

[官方文档](https://kubeblocks.io/docs/preview/api_docs/connect_database/overview-of-database-connection)根据不同的情景，提供了多种连接集群的方式。您可根据实际场景选择对应的方式。本文中我们将使用试用环境的方式来演示连接至集群。

## 连接到 PostgreSQL 集群

1. 连接至 PostgreSQL 集群。

   ```sh
   kbcli cluster connect mypg --namespace harbor
   ```

2. 在 PostgreSQL CLI 客户端中，创建新用户。

   ```sh
   create user test with password 'password';
   ```

3. 为 Harbor 创建新的数据库注册表。

   ```sh
   CREATE DATABASE registry OWNER test;
   ```

此处创建的用户和数据库将在安装 Harbor 时使用。

## 连接到redis集群

1. 连接至 Redis 集群。

   ```sh
   kbcli cluster connect myredis --namespace harbor
   ```

2. 创建用户。

   ```sh
   ACL SETUSER test on >password ~* +@all
   ```

# 安装harbor

1. 下载 Harbor Helm chart。

   ```sh
   helm repo add harbor https://helm.goharbor.io
   helm fetch harbor/harbor --untar
   cd harbor
   ```

2. 获取集群服务信息。`mypg-postgresql` 和 `myredis-redis-redis` 的集群 IP 即 Harbor 需连接的地址信息。

   ```sh
   kubectl get service -n harbor
   ```

3. 在 `values.yaml` 文件中配置 PostgreSQL 数据库。使用 KubeBlocks 提供的外部数据库，并填写必要的数据库信息。如需配置其他参数（如 `expose.type`），可参考[官方文档](https://goharbor.io/docs/2.11.0/install-config/configure-yml-file/)。

   ```sh
   database:
     type: external #修改类型为external
     ...
     external:
       host: "172.16.155.121" # clusterIP of postgresql
       port: "5432"
       username: "test"       # your username
       password: "password".  # your password
       coreDatabase: "registry" # your database name
       existingSecret: ""
       sslmode: "disable"
   ```

4. 在 `values.yaml` 文件中配置 Redis 数据库。

   ```sh
   redis:
     type: external #修改类型为external
     ...
     external:
       addr: "172.16.190.126:6379" # clusterIp of redis: port
       sentinelMasterSet: ""
       coreDatabaseIndex: "0"
       jobserviceDatabaseIndex: "1"
       registryDatabaseIndex: "2"
       trivyAdapterIndex: "5"
       username: "test"        # your username
       password: "password"    # your password
       existingSecret: ""
   ```

5. 安装 Harbor。

   ```sh
   helm install myharbor . -n harbor
   #更新yaml文件之后，update helm部署
   helm upgrade myharbor . -n harbor
   ```

6. 检查 Pod 状态，确保所有服务都处于 Running 状态。

# 访问harbor

# 高可用测试

本节将演示 KubeBlocks 创建的 Harbor 集群的高可用能力。我们将通过 PostgreSQL 集群主节点故障来模拟。

1. 查看 PostgreSQL 集群和 Pod 的初始状态。当前，`mypg-postgresql-0` 为主节点，`mypg-postgresql-1` 为备节点。

   ```sh
   kubectl -n harbor get pod -L kubeblocks.io/role
   ```

2. 向 Harbor 注册表中推送一个名为 `busybox` 的测试镜像。

   ```sh
   docker docker tag busybox harbor.domain.com/library/busybox
   docker push harbor.domain.com/library/busybox     
   ```

3. 查看 Harbor 仓库，可以看到该镜像已成功推送到 Harbor 注册表。

4. 接下来，模拟 PostgreSQL 主节点故障。

```sh
# Enter the primary pod
kubectl exec -it mypg-postgresql-0 -n harbor -- bash

# Delete the data directory of PostgreSQL to simulate an exception
root@mycluster-postgresql-0:/home/postgres# rm -fr /home/postgres/pgdata/pgroot/data
```

5. 查看集群日志，观察故障发生时节点角色变化。

```sh
# View the primary pod logs
kubectl logs mypg-postgresql-0 -n harbor
```

从日志中我们可以看到，leader lock 从主节点释放出来，触发了 HA 切换，并从备份数据中创建出新的副本。该服务几十秒便恢复正常。

```sh
 2024-06-26 08:00:51,759 INFO: no action. I am (mypg-postgresql-0), the leader with the lock
 2024-06-26 08:01:01,726 INFO: Lock owner: mypg-postgresql-0; I am mypg-postgresql-0
 2024-06-26 08:01:01,802 INFO: Leader key released
 2024-06-26 08:01:01,824 INFO: released leader key voluntarily as data dir empty and currently leader
 2024-06-26 08:01:01,825 INFO: Lock owner: mypg-postgresql-1; I am mypg-postgresql-0
 ...
 2024-06-26 08:01:04,475 INFO: replica has been created using basebackup_fast_xlog
 2024-06-26 08:01:04,475 INFO: bootstrapped from leader 'mypg-postgresql-1'
 2024-06-26 08:01:04,476 INFO: closed patroni connection to the postgresql cluster
```

```sh
# View secondary pod logs
kubectl logs mypg-postgresql-1 -n harbor
```

原来的备节点 `mypg-postgresql-1` 获得了 leader locks，成为主节点。

```sh
2024-06-26 08:02:13,638 INFO: no action. I am (mypg-postgresql-1), the leader with the lock
```

6. 再次查看 PostgreSQL 集群和 Pod 的状态。故障转移后，`mypg-posgresql-0` 变成了备节点，`mypg-postgresql-1` 变成了主节点。

```sh
kubectl -n harbor get pod -L kubeblocks.io/role
>
NAME                                   READY   STATUS    RESTARTS   AGE   ROLE
...
mypg-postgresql-0                      4/4     Running   0          89m   secondary
mypg-postgresql-1                      4/4     Running   0          26m   primary
...
```

7. 连接到 PostgreSQL 集群，查看主节点的 replication 信息。

```sh
postgres=# select * from pg_stat_replication;
```

8. 结果显示 `mypg-postgresql-0` 已被分配备节点角色。

9. 验证 Harbor 集群的服务。这里我们拉取之前推送的 `busybox` 镜像。该镜像可以成功地从 Harbor 注册表中拉取。同时，我们也推送了新镜像 `hello-world`。该镜像也能够成功推送到 Harbor 注册表。故障转移后，Harbor 集群的读写功能已恢复，证实了 KubeBlocks 提供的高可用功能的有效性。

# 集群扩容

KubeBlocks 提供了垂直和水平扩容的能力。您可以通过执行以下命令轻松扩容集群。

- 垂直扩容

  ```sh
  kbcli cluster vscale mypg \
  --components="postgresql" \
  --memory="4Gi" --cpu="2" \
  --namespace harbor
  ```

- 水平扩容

  ```sh
  kbcli cluster hscale mypg 
  --replicas 3 \
  --namespace harbor \ 
  --components postgresql
  ```
