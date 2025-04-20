# 背景

## WordPress

- WordPress 是全球最流行的内容管理系统（CMS），自 2003 年发布以来，已成为网站建设的首选工具。其广泛的插件和主题生态系统使用户能够轻松扩展功能和美化外观。活跃的社区提供丰富的资源和支持，进一步降低了开发和维护的难度。凭借易用性、灵活性和强大的社区支持，WordPress 已成为全球数百万用户的共同选择，在网站建设领域占据了重要地位。

## KubeBlocks

- KubeBlocks 是一个可以管理多种数据库和有状态中间件的 K8s operator，支持管理 MySQL、PostgreSQL、Redis、MongoDB、Kafka、ClickHouse、Elasticsearch 等 30 余种数据库。其原理是定义一组通用和抽象的 API（CRDs）来描述各种引擎的共同属性，在其之上，数据库厂商和开发者可以通过插件来描述不同引擎的差异。
- 使用 KubeBlocks 来部署提供 WordPress 数据库服务，可以很好解决 MariaDB 的缺陷：
  - 高可用性：可以分别为 WordPress 和数据库配置高可用方案，提高整体系统的可靠性。
  - 资源隔离：WordPress 和数据库运行在不同的 Pod 中，资源隔离性更好，避免了资源竞争。
  - 拓展性强：可以独立扩展 WordPress 和数据库的副本数，分别调整它们的资源配置。
  - 快捷管理：KubeBlocks 可以快速一键部署 WordPress 所需数据库集群，无需额外操作，且内置数据库的备份和监控功能，能提高管理效率。

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

# 一键部署高可用数据库集群

> 在部署 WordPress 之前，首先需要部署一个数据库集群用于管理 WordPress 的后台数据，可使用 [kbcli](https://kubeblocks.io/docs/preview/user_docs/kubeblocks-for-apecloud-mysql/cluster-management/create-and-connect-an-apecloud-mysql-cluster) 或者 [kubectl](https://kubeblocks.io/docs/preview/api_docs/kubeblocks-for-apecloud-mysql/cluster-management/create-and-connect-an-apecloud-mysql-cluster)部署集群。

1. 创建高可用集群

   - 这里我们使用 KubeBlocks `apecloud-mysql` addon 创建一个 MySQL 数据库作为 WordPress 的数据库。使用 kbcli 快速部署一个具有高可用多副本且达到生产环境水平的 MySQL 数据库集群。
   - 设置集群参数 replicas=3，以启用数据库 RaftGroup 模式，创建一个 MySQL 三副本集群。

   ```sh
   # 启用 addon（默认开启）
   kbcli addon install apecloud-mysql 
   
   # 部署集群 可以设置参数，如 --set replicas=3 表示三副本
   kbcli cluster create apecloud-mysql --cluster-definition=apecloud-mysql --set replicas=3
   ```

   > 如果报错：error: failed to find the default storageClass, use '--set storageClass=NAME' to set it，查看pod和pvc，发现有unbound的pvc，搭建nfs的provisioner，把nfs的sc设为默认sc，这样mysql的pvc可以自动绑定pv了
   >
   > - https://kubernetes.io/zh-cn/docs/tasks/administer-cluster/change-default-storage-class/
   >
   > ~~~sh
   > kubectl get storageclass
   > #默认 StorageClass 以 (default) 标记。
   > #标记一个 StorageClass 为默认的
   > kubectl patch storageclass <your-class-name> -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
   > ~~~

2. 查看集群状态，等待所有相关 Pod 变为 running 状态

# 部署WordPress

## 配置数据库

1. 根据实际需要，可以在数据库中创建若干用户，以便于 WordPress 进行角色管理。下面我们将创建一个 myadmin 用户作为 WordPress 安装时的主用户。

   - 使用以下命令以 root 身份连接 MySQL 数据库。

   ```sh
   kbcli cluster connect apecloud-mysql 
   ```

   - 进入数据库后，执行以下 SQL 语句创建用户并赋予权限，可根据需要设置数据库权限。

   ```mysql
   CREATE USER 'myadmin'@'%' IDENTIFIED BY 'password';
   GRANT ALL PRIVILEGES ON *.* TO 'myadmin'@'%';
   FLUSH PRIVILEGES;
   create database wordpress;
   ```

   > **注意**
   >
   > 可根据需求选择创建 secret，用于 WordPress 安装时引用，以避免明文传输密码。

2. 执行如下命令创建 `mysql-secret`，设置键 `mariadb-password=password`，安装时 WordPress 会优先将该密码键值作为数据库密码，注意密码的键名必须为 `mariadb-password`。用户名不会从该 secret 中读取。

   ```sh
   kubectl create secret generic mysql-secret --from-literal=mariadb-password=password
   ```

## 一键安装 WordPress

1. 使用 helm install 命令安装 WordPress，同时配置前面所述参数。

   ```sh
   helm install my-release oci://registry-1.docker.io/bitnamicharts/wordpress --set mariadb.enabled=false --set externalDatabase.host=apecloud-mysql-mysql.default.svc.cluster.local --set externalDatabase.database=wordpress --set externalDatabase.port=3306 --set externalDatabase.user="myadmin" --set externalDatabase.existingSecret="mysql-secret" --set replicaCount=2
   ```

   **参数说明：**

   - `mariadb.enabled`：需设置为 `false`，将禁用 MariaDB 的安装，以使用外部数据库服务。
   - `host`：我们可以使用前面的 MySQL service 地址来访问 MySQL 服务，如：`apecloud-mysql-mysql.default.svc.cluster.local`。
   - `user`, `database`, `port`：根据实际情况设置。
   - `existingSecret`：推荐使用该方式传输密码。可引用前面创建的 secret 来传输密码，以避免明文传输这些内容。注意  secret 必须包含连接密码，设置了 `existingSecret` 后，password 会被忽略。
   - `password`：可选设置。本文推荐使用 `existingSecret` 引用前面创建的 secret 来传输密码，避免明文传输。此外，设置了 `existingSecret` 后，`password` 将被忽略。
   - `replicaCount`：代表 WordPress 实例启动 Pod 数量。

   > 注：可能要从国外网站拉取镜像：registry-1.docker.io/bitnamicharts/wordpress:23.1.4。

2. 查看 Pod 运行情况 ，确保所有 Pod ready 且处于 running 状态

3. 进入 WordPress 容器，可远程连接数据库，查看 WordPress 数据库信息。

```sh
kubectl exec -it wordpress-584444f68b-sxcss  -- bash
mysql -h  apecloud-mysql-mysql.default.svc.cluster.local  -u Wordpress
```

# 数据库扩容

当出现性能瓶颈等情况，或许需要对数据库节点进行资源扩容，KubeBlocks 提供了非常方便的扩容命令，可使用 kbcli vsclae 命令轻松扩充计算资源。

```sh
kbcli cluster vscale mycluster --components=apecloud-mysql --cpu=500m --memory=500Mi
```

# 访问wordpress

~~~sh
kubectl get svc
#看到部署了一个LB的svc，暴露了nodeport 30496
my-release-wordpress            LoadBalancer   10.110.15.172   <pending>     80:30496/TCP,443:32558/TCP
~~~

- 浏览器直接访问：http://172.16.183.76:30496/wp-admin/install.php，会出现wordpress初始配置界面

- 如果没出现的话，删掉数据库再重新创建

  ~~~sh
  kbcli cluster connect apecloud-mysql 
  drop database wordpress;
  create database wordpress;
  ~~~

- 创建admin用户，密码admin

后续页面设置和各项配置再研究。。。。。。
