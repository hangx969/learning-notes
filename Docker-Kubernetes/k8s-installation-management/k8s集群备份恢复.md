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
- Velero 版 本 选 择 ： https://github.com/vmware-tanzu/velero?tab=readme-ov-file#velero-compatibility-matrix
- 插 件 版 本 选 择 ： https://github.com/vmware-tanzu/velero-plugin-for-aws?tab=readme-ov-file#compatibility
- 接下来下载客户端工具： https://github.com/vmware-tanzu/velero/releases/

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

```sh
velero install \
--provider aws \
--plugins velero/velero-plugin-for-aws:v1.13.1 \
--image velero/velero:v1.17.1 \
--bucket velerobackup \
--secret-file ./user-minio \
--use-volume-snapshots=false \
--backup-location-config region=minio,s3ForcePathStyle="true",s3Url=http://192.168.181.134:9000 \
--namespace velero
```