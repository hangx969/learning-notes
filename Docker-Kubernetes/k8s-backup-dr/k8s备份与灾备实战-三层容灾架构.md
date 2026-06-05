---
title: "K8s 备份与灾备实战：三层容灾架构"
source: "https://mp.weixin.qq.com/s/yWs0RWgEmddjOqh76rknhw"
created: 2026-06-05
tags:
  - kubernetes
  - backup
  - disaster-recovery
  - etcd
  - velero
---

# K8s 备份与灾备实战：三层容灾架构

## 一、三层备份模型

K8s 的备份不是一个动作，而是一套层次结构：

| 层级 | 备份对象 | 工具 | 恢复速度 | 粒度 |
|------|----------|------|----------|------|
| **L1 集群态** | etcd 快照 | etcdctl snapshot | 分钟级 | 全集群 |
| **L2 应用态** | K8s 资源 + PV 数据 | Velero | 按需 | Namespace/Label |
| **L3 数据态** | 数据库 + 外部存储 | 应用层工具 | 按需 | 单应用 |

- **L1 是保命药**：etcd 挂了整集群跟着挂，快照能在 10 分钟内恢复集群状态
- **L2 是后悔药**：误删 Namespace/Deployment 后，Velero 能精确恢复
- **L3 是终极保险**：数据库原生的 mysqldump/xtrabackup 才是数据一致性保障

## 二、etcd 快照实战

### etcd 快照包含与不包含

**包含**：所有 K8s 原生资源定义、CRD、RBAC 规则、ServiceAccount、Secret（含 TLS 私钥等敏感信息）、ConfigMap、Service/Endpoint 状态

**不包含**：容器实际文件系统、PV 里的业务数据、Node 节点磁盘数据

### 手动备份

```bash
ETCDCTL_API=3 etcdctl snapshot save /backup/etcd-snapshot-$(date +%Y%m%d-%H%M%S).db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# 验证快照完整性
ETCDCTL_API=3 etcdctl snapshot status /backup/etcd-snapshot-*.db --write-out=table
```

### 自动化 CronJob 备份 + 远程上传

完整的 CronJob 方案要点：
- Namespace `cluster-backup` + 专用 ServiceAccount + RBAC
- `hostNetwork: true`（必须用宿主机网络才能访问 etcd）
- `nodeSelector` 只调度到 master 节点 + 对应 tolerations
- 挂载 `/etc/kubernetes/pki/etcd` 证书目录（readOnly）
- 快照后通过 mc (MinIO Client) 上传到 S3 兼容存储
- 清理 7 天前的旧快照
- 调度频率：每 6 小时

### etcd 快照恢复核心流程

```bash
# 1. 停止所有 master 节点上的 kube-apiserver
mv /etc/kubernetes/manifests/kube-apiserver.yaml /tmp/

# 2. 在所有 master 节点上恢复 etcd 快照
ETCDCTL_API=3 etcdctl snapshot restore /backup/etcd-snapshot.db \
  --name master-1 \
  --initial-cluster master-1=https://IP1:2380,master-2=https://IP2:2380,master-3=https://IP3:2380 \
  --initial-advertise-peer-urls https://IP1:2380 \
  --data-dir /var/lib/etcd-restore \
  --skip-hash-check=false  # 生产环境务必验证哈希

# 3. 用新数据目录替换旧目录
rm -rf /var/lib/etcd/member
mv /var/lib/etcd-restore/member /var/lib/etcd/
chown -R etcd:etcd /var/lib/etcd

# 4. 启动 etcd，确认健康后再启动 apiserver
mv /tmp/kube-apiserver.yaml /etc/kubernetes/manifests/
```

> **生产警告**：恢复 etcd 快照会导致整个集群回到快照时刻的状态！快照时刻到恢复之间的所有增量数据将永久丢失。

## 三、Velero 实战

### 架构原理

Velero 由 CLI + Server（Deployment）组成：
- **Backup 流程**：Controller 通过 K8s API 列出目标资源 → 序列化为 JSON → 压缩上传到 S3
- **PV 备份**：有 CSI 快照能力时调用 CSI Driver；无 CSI 时用 Restic/Kopia 做文件级备份
- **Restore 流程**：按依赖顺序重建（Namespace → CRD → RBAC → Deployment → Service）

### 安装（以 MinIO 为后端）

```bash
velero install \
  --provider aws \
  --plugins velero/velero-plugin-for-aws:v1.9.0 \
  --bucket velero-backups \
  --secret-file ./credentials-velero \
  --use-volume-snapshots=false \
  --use-node-agent \
  --default-volumes-to-fs-backup \
  --backup-location-config region=minio,s3ForcePathStyle=true,s3Url=http://minio.default.svc:9000
```

### 备份与恢复常用命令

```bash
# 备份单个 Namespace
velero backup create prod-backup --include-namespaces production --wait

# 备份特定 Label 的资源（跨 Namespace）
velero backup create app-backup --selector app=myapp --wait

# 恢复到原 Namespace
velero restore create --from-backup prod-backup

# 恢复到新 Namespace（推荐用于安全演练）
velero restore create --from-backup prod-backup \
  --namespace-mappings production:production-restored

# 只恢复特定资源类型
velero restore create --from-backup prod-backup \
  --include-resources deployments,services,configmaps

# 定时备份 Schedule
velero schedule create daily-backup \
  --schedule="0 2 * * *" \
  --include-namespaces production,staging \
  --ttl 720h0m0s
```

## 四、生产环境六大避坑

### 坑 1：备份不做恢复验证 = 没有备份

每月至少一次恢复演练。方案：CronJob 自动恢复到隔离 Namespace → 验证关键 Deployment Ready → 清理测试 Namespace。

### 坑 2：etcd 快照与 Velero 备份的时间差

etcd 02:00 快照不含 02:30 新建的资源，但 Velero 03:00 备份包含。恢复 etcd 后必须再用 Velero 恢复增量。解决：备份时记录 etcd revision 建立对应关系。

### 坑 3：Secret 备份的安全性

etcd 快照包含**所有 Secret 明文数据**（TLS 私钥、数据库密码、API Token）。解决方案：
- GPG 加密快照文件后再上传
- 或使用 S3 服务端加密（SSE-S3 / SSE-KMS）

### 坑 4：etcd 磁盘空间耗尽

启用自动压缩防止 DB 无限增长：

```yaml
# etcd 配置
- --auto-compaction-mode=periodic
- --auto-compaction-retention=24h
```

### 坑 5：跨 K8s 版本的 etcd 快照兼容性

etcd 快照**向前兼容**（高版本可读取低版本），但**不向后兼容**。跨版本恢复必须先降级再升级。

### 坑 6：Velero 不包含的"隐形状态"

不在备份范围：Node 节点状态（标签/污点）、容器运行时状态、外部依赖（RDS endpoint 可能变了）、CRD 的 Webhook 配置。恢复后需执行检查清单。

## 五、三层容灾架构 RTO/RPO

| 层级 | 频率 | RTO | RPO | 适用场景 |
|------|------|-----|-----|----------|
| L1 etcd 快照 | 每 6 小时 | < 30 分钟 | < 6 小时 | etcd 损坏、全集群回滚 |
| L2 Velero 应用备份 | 每天全量 + 午间增量 | < 10 分钟（单 NS） | < 24 小时 | 误删资源、Namespace 迁移 |
| L3 应用数据备份 | 数据库每小时 dump | < 2 小时 | < 1 小时 | 数据损坏、勒索病毒、跨 Region |

### Prometheus 告警规则（备份健康检查）

- `EtcdBackupFailed`：etcd 快照超过 24 小时未成功执行（critical）
- `VeleroBackupFailed`：Velero 备份失败（warning）
- `BackupRestoreDrillMissed`：恢复演练超过 30 天未执行（warning）

## 三条铁律

1. **没有做过恢复验证的备份等于没有备份**——每月一次恢复演练
2. **三层备份缺一不可**——etcd 保命、Velero 后悔、应用数据终极保险
3. **备份文件必须加密 + 异地存储**——同一机房的两个备份 = 一个备份
