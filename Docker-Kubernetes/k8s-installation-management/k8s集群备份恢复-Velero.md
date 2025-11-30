# 方案对比
## Etcd
优点：全量备份，包含集群所有资源；备份不依赖于任何K8s API和版本，可用于灾难恢复。

缺点：全量恢复，不可恢复部分资源；不支持数据迁移，恢复时必须保持配置统一（K8s版本、各种IP、主机名都要保持一致）。

## GitOps
优点：符合GitOps规范，可以基于代码仓库进行配置控制、回滚、可审计、可重复部署

缺点：配置漂移，资源文件过多，管理复杂。

## Velero
优点：灵活性高，支持按照namespace、集群等方式备份，支持定时备份、全量备份，支持备份应用数据，支持跨集群备份恢复数据，支持细粒度恢复。

缺点：需要S3存储备份数据，备份应用数据功能有限，K8s版本依赖

关于备份应用数据：
- 不推荐使用velero备份，他是崩溃一致性。数据库应用，直接用velero备份运行中的数据库的PV数据目录不可靠，是有其他事务逻辑约束的，还原会出问题。

- 怎么备份应用数据：用数据库自己的工具，比如mysqldump、pgdump等。能保证应用一致性

> 总之，这些约束是应用层的逻辑，文件系统级的备份工具（如 Velero）无法理解和保证，所以必须使用数据库自己的备份工具（如mysqldump、pg_dump），它们从应用层理解这些约束，才能保证备份的可靠性。


# Velero介绍
专门为K8s设计的备份容灾工具，主要用于以下场景：
1. 备份、恢复、灾备K8s集群的各类资源
2. 灵活迁移K8s的数据，可以从集群A迁移到集群B，可以从ns A迁移到ns B
3. 手动及周期备份、最小范围恢复（只恢复某个ns内的某个资源）

核心组件：
- 服务端：处理备份和恢复操作，需要部署在K8s集群中，需要配置对象存储后端
- 客户端：负责与服务端交互

## 核心资源
- Backup：备份资源，用于执行一次性备份任务，可以基于Schedule规则或者自定义字段创建，备份资源可以指定需要备份或排除的空间、资源类型，同时支持备份的保留时间等。

- Schedule：周期性备份，基于Cron表达式创建的周期性备份任务，包含Backup的所有字段。

- Restore：恢复资源，用于从某个backup中恢复资源，可以指定恢复的资源类型、空间等。

- BackupStorageLocation：备份存储位置，用于指定备份文件的存储位置，比如aws、minio等。同时可以指定对象存储的bucket和prefix。

## 工作原理
### 备份过程

手动或自动备份 -- 创建backup资源 -- 服务端处理 -- 执行钩子 -- 收集资源（创建json文件和一些压缩包） -- 上传至对象存储 -- 返回结果 -- 更新bakcup状态

### 还原过程

执行还原 -- 创建Restore资源 -- 服务端处理 -- 下载备份文件 -- 创建k8s资源 -- 返回结果 -- 更新Restore状态

# 部署对象存储Minio

Velero会把备份文件上传至对象存储，可以使用公有云存储或者Minio作为存储后端。
本次实验采用docker部署Minio：

❌ 使用Bitnami镜像：（bitnami的minio的Arm64镜像无法拉取，dockerhub里面已经找不到任何tag，遂放弃）

```sh
mkdir -p /data/minio && chmod -R 777 /data/minio
docker run -d --name minio-server --restart=always \
  --env MINIO_ROOT_USER="user" \
  --env MINIO_ROOT_PASSWORD="password" \
  --env MINIO_DEFAULT_BUCKETS="velerobackup" \
  --publish 9000:9000 \
  --publish 9001:9001 \
  -v /data/minio:/bitnami/minio/data \
  bitnami/minio:latest
```

访问宿主机IP+9001可以访问Minio UI界面。

✅ 使用官方镜像：
```sh
mkdir -p /data/minio && chmod -R 777 /data/minio
docker run -d --name minio-server --restart=always -p 9000:9000 -p 9001:9001 -e MINIO_ROOT_USER="user" -e MINIO_ROOT_PASSWORD="password" -v /data/minio:/data minio/minio:latest server /data --console-address ":9001"
```

注意：
1. **`server /data --console-address ":9001"`**: 这是官方镜像必须的启动参数。如果不加 `--console-address`，Web 控制台端口可能会随机分配，导致你无法通过 9001 访问。
2. `MINIO_DEFAULT_BUCKETS` 是 Bitnami 镜像特有的环境变量。**官方镜像不支持通过环境变量自动创建 Bucket**。你需要启动后手动创建。
3. 访问宿主机IP+9001可以访问Minio UI界面，在界面左侧点击 "Buckets"，然后点击 "Create Bucket" 创建名为 `velerobackup` 的存储桶。

# 部署Velero
## 版本确认及下载

部署 Velero 之前，需要找到适合的版本和插件的版本：
- Velero 版 本 选 择 (需要下载docker image)： https://github.com/vmware-tanzu/velero?tab=readme-ov-file#velero-compatibility-matrix
- 插 件 版 本 选 择（需要下载docker image）： https://github.com/vmware-tanzu/velero-plugin-for-aws?tab=readme-ov-file#compatibility
- 接下来下载客户端工具（下载安装包）： https://github.com/vmware-tanzu/velero/releases/

K8s集群版本是1.34 -- Velero版本用1.17 -- 插件版本选1.13

## 安装客户端工具
客户端工具选：1.17.1 (release里面选择最新的patch版本下载)：
https://github.com/vmware-tanzu/velero/releases

```sh
tar xf velero-v1.17.1-linux-arm64.tar.gz
mv velero-v1.17.1-linux-arm64/velero /usr/local/bin/
chmod +x /usr/local/bin/velero
velero version
```

## 创建对象存储密码文件
```sh
cat > user-minio << EOF
[default]
aws_access_key_id=user
aws_secret_access_key=password
EOF
```

## 安装服务端
velero自动识别当前kubeconfig来往集群安装资源：

```sh
velero install \
--provider aws \
--plugins velero/velero-plugin-for-aws:v1.13.1 \
--image velero/velero:v1.17.1 \
--bucket velerobackup \
--secret-file ./user-minio \
--use-volume-snapshots=false \
--backup-location-config region=minio,s3ForcePathStyle="true",s3Url=http://172.16.35.120:9000 \
--namespace velero
```

注意：关于为什么对象存储用minio，provider却用aws：
- **因为 MinIO 是完全兼容 Amazon S3 协议的。**
- Velero 并没有专门为 MinIO 开发一个独立的插件，而是复用了 **AWS S3 的插件**。对于 Velero 来说，MinIO 就是一个“运行在你本地的 AWS S3”。
- 虽然我们用了 AWS 的插件，但我们不能让它去连接亚马逊的服务器。这就是你命令中 **`--backup-location-config`** 这一行的作用，它是“偷梁换柱”的关键：
- **`s3Url=http://192.168.181.134:9000`**:  
    这个参数告诉 AWS 插件：“**不要**去连接默认的亚马逊官网地址，**而是**去连接我指定的这个 IP 和端口”。因为 MinIO 听得懂 AWS S3 的语言，所以插件发过去的请求，MinIO 能完美处理。
- **`s3ForcePathStyle="true"`**:  
    AWS S3 现在的默认访问方式是域名形式（如 `bucketname.s3.amazonaws.com`），但本地部署的 MinIO 通常使用路径形式（如 `192.168.x.x:9000/bucketname`）。这个参数强制插件使用路径形式，否则会因为 DNS 解析不到域名而报错。
- **`region=minio`**:  
    AWS SDK 强制要求必须填一个 Region（区域）。对于本地 MinIO，这个值其实不重要（MinIO 不分区域），但为了骗过 SDK 的检查，我们通常约定俗成填 `minio` 或者 `us-east-1`。
- 因为加载的是 **AWS 插件**，该插件的代码里写死了去读取名为 `aws_access_key_id` 的变量。插件并不知道它连的是 MinIO，它只认这些标准的 AWS 变量名。所以，这里的 `user` 和 `password` 其实就是你 MinIO 的用户名和密码，只是必须套上 AWS 的“马甲”。

==扩展-S3协议==
- Amazon S3 是对象存储事实上的行业标准。几乎所有现代的对象存储软件（包括 MinIO、阿里云 OSS、腾讯云 COS、Ceph RGW 等）都实现了 **S3 API**。 这意味着：它们使用的通讯语言、认证方式、数据读写命令，和 AWS S3 是一模一样的。

安装完起了一个velero的deployment，检查pod ready，检查存储后端配置：

```sh
kubectl get BackupStorageLocation -n velero
```

# 测试备份
创建测试ns：`kubectl create ns test`

部署资源：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: busybox-test
  namespace: test
  labels:
    app: busybox-test
spec:
  replicas: 1
  selector:
    matchLabels:
      app: busybox-test
  template:
    metadata:
      labels:
        app: busybox-test
    spec:
      containers:
        - name: busybox
          image: busybox:1.28
          command:
            - "/bin/sh"
            - "-c"
            - "while true; do echo 'Hello from busybox'; sleep 10; done"
          ports:
            - containerPort: 80
          resources:
            requests:
              cpu: "50m"
              memory: "64Mi"
            limits:
              cpu: "100m"
              memory: "128Mi"
---
apiVersion: v1
kind: Service
metadata:
  name: busybox-test-svc
  namespace: test
  labels:
    app: busybox-test
spec:
  selector:
    app: busybox-test
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
  type: ClusterIP
```

备份：`velero backup create test-backup`

查看备份：`velero backup get`