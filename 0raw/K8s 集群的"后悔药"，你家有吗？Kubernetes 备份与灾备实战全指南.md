---
title: "K8s 集群的\"后悔药\"，你家有吗？Kubernetes 备份与灾备实战全指南"
source: "https://mp.weixin.qq.com/s/yWs0RWgEmddjOqh76rknhw?scene=1&click_id=78"
author:
  - "[[WAKEUP技术]]"
published:
created: 2026-06-05
description: "\x26quot;强哥，线上所有服务都挂了！kubectl 报 connection refused！\x26quot;"
tags:
  - "clippings"
---
WAKEUP技术 *2026年5月26日 07:46*

> 备份从来不是技术问题，而是心态问题。直到删库跑路的那一刻才想起备份，已经晚了。

## 噩梦开场：一个凌晨 3 点的 P0 事故

凌晨 3:15，手机疯狂震动。

"强哥，线上所有服务都挂了！kubectl 报 connection refused！"

你爬起来连上 VPN，踩上了一连串的屎：

```
$ kubectl get nodes
The connection to the server 192.168.1.10:6443 was refused
```

SSH 到 master 节点一看，整个人都麻了—— `etcd` 数据目录被人 `rm -rf` 了。

**没有备份。没有快照。没有 Velero。**

整个集群的状态——几十个 Namespace、上百个 Deployment、上千条 Ingress 规则、几十个 PVC 绑定信息——全部归零。

最后用了一整天时间，手动重建了所有资源。运气好的是，应用数据在外部数据库里。运气差的是， **集群配置、RBAC 规则、网络策略、Secret——这些没法从应用数据库里找回来的东西——再也回不来了** 。

从那之后，我给每个接手过的集群都配上了三层备份体系。今天这篇文章，就是要把这套方案完整地交给你。

---

## 一、Kubernetes 需要备份什么？

很多人的第一反应是："我只需要备份 etcd 就好了，它是集群的数据库。"

这话只对了一半。

### 1.1 三层备份模型

K8s 的备份不是一个动作，而是一套层次结构：

| 层级 | 备份对象 | 工具 | 恢复速度 | 粒度 |
| --- | --- | --- | --- | --- |
| **L1 集群态** | etcd 快照 | etcdctl snapshot | 分钟级 | 全集群 |
| **L2 应用态** | K8s 资源 + PV 数据 | Velero | 按需 | Namespace/Label |
| **L3 数据态** | 数据库 + 外部存储 | 应用层工具 | 按需 | 单应用 |

**L1 是保命药** ：etcd 挂了，整集群跟着挂。etcd 快照能在 10 分钟内恢复集群的状态。

**L2 是后悔药** ：有人手抖 `kubectl delete namespace production` 之后，Velero 能精确恢复那个 Namespace 里的所有资源和持久卷数据。

**L3 是终极保险** ：如果你的 MySQL 跑在 K8s 里，别只指望 Velero 的 PV 快照——数据库原生的 `mysqldump` 或 `xtrabackup` 才是数据一致性的保障。

### 1.2 etcd 快照到底存了什么？

etcd 是一个分布式的键值存储，它用 Raft 共识协议维护集群的"唯一真相来源"。 `etcdctl snapshot save` 做的事情很简单：

```
遍历 etcd 当前 MVCC 数据库中的所有键值对 → 序列化写入快照文件
```

快照里包含：

- • 所有 Namespace、Pod、Deployment、Service 等 K8s 原生资源的定义
- • 所有 CRD 自定义资源
- • RBAC 规则、ServiceAccount、Secret（ **包括 TLS 证书私钥、镜像仓库密码等敏感信息** ）
- • ConfigMap 里存的所有业务配置
- • Service 和 Endpoint 的当前状态

快照里 **不包含** ：

- • 容器的实际文件系统（那是容器运行时的活）
- • PV 里的业务数据（那是存储后端的活）
- • Node 节点的磁盘数据

这也解释了为什么需要 Velero：etcd 快照没法恢复 PV 里的数据，也做不到 Namespace 粒度的选择性恢复。

---

## 二、etcd 快照实战：从零搭建自动化备份

### 2.1 手动备份一把梭

kubeadm 部署的集群，etcd 通常以静态 Pod 运行在 master 节点上：

```
# 确认 etcd 版本和证书路径
ETCDCTL_API=3 etcdctl --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  endpoint health

# 执行快照
ETCDCTL_API=3 etcdctl snapshot save /backup/etcd-snapshot-$(date +%Y%m%d-%H%M%S).db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# 验证快照完整性
ETCDCTL_API=3 etcdctl snapshot status /backup/etcd-snapshot-$(date +%Y%m%d-%H%M%S).db --write-out=table
```

输出类似：

```
+----------+----------+------------+------------+
|   HASH   | REVISION | TOTAL KEYS | TOTAL SIZE |
+----------+----------+------------+------------+
| 2c4e9f1a |   458721 |      10234 |     256 MB |
+----------+----------+------------+------------+
```

### 2.2 自动化 CronJob 备份 + 远程上传

手动备份只适合临时操作，生产环境必须自动化。下面是一个完整的 Kubernetes CronJob，每小时执行 etcd 快照并上传到对象存储：

```
apiVersion: v1
kind: Namespace
metadata:
  name: cluster-backup
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: etcd-backup
  namespace: cluster-backup
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: etcd-backup
rules:
- apiGroups: [""]
  resources: ["nodes"]
  verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: etcd-backup
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: etcd-backup
subjects:
- kind: ServiceAccount
  name: etcd-backup
  namespace: cluster-backup
---
apiVersion: batch/v1
kind: CronJob
metadata:
  name: etcd-snapshot-backup
  namespace: cluster-backup
spec:
  schedule: "0 */6 * * *"          # 每 6 小时执行一次
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 3
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: etcd-backup
          hostNetwork: true               # 关键：必须用宿主机网络才能访问 etcd
          nodeSelector:
            node-role.kubernetes.io/control-plane: ""  # 只调度到 master 节点
          tolerations:
          - key: "node-role.kubernetes.io/control-plane"
            operator: "Exists"
            effect: "NoSchedule"
          containers:
          - name: backup
            image: bitnami/etcd:3.5.14
            command:
            - /bin/sh
            - -c
            - |
              # 生成带时间戳的快照文件名
              TIMESTAMP=$(date -u +%Y%m%d-%H%M%S)
              SNAPSHOT="/tmp/etcd-snapshot-${TIMESTAMP}.db"

              # 执行快照
              ETCDCTL_API=3 etcdctl snapshot save ${SNAPSHOT} \
                --endpoints=https://127.0.0.1:2379 \
                --cacert=/etc/kubernetes/pki/etcd/ca.crt \
                --cert=/etc/kubernetes/pki/etcd/server.crt \
                --key=/etc/kubernetes/pki/etcd/server.key

              echo "[INFO] Snapshot saved: ${SNAPSHOT}"

              # 验证快照
              ETCDCTL_API=3 etcdctl snapshot status ${SNAPSHOT} --write-out=table

              # 上传到 S3（MinIO / AWS S3 / 阿里云 OSS）
              mc alias set backup-s3 https://s3.example.com ${ACCESS_KEY} ${SECRET_KEY}
              mc cp ${SNAPSHOT} backup-s3/etcd-backups/$(hostname)/

              echo "[INFO] Snapshot uploaded to S3"

              # 清理 7 天前的旧快照
              find /tmp -name "etcd-snapshot-*.db" -mtime +7 -delete
            env:
            - name: ACCESS_KEY
              valueFrom:
                secretKeyRef:
                  name: s3-credentials
                  key: access-key
            - name: SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: s3-credentials
                  key: secret-key
            volumeMounts:
            - name: etcd-certs
              mountPath: /etc/kubernetes/pki/etcd
              readOnly: true
            - name: backup-tmp
              mountPath: /tmp
            securityContext:
              runAsUser: 0
          restartPolicy: OnFailure
          volumes:
          - name: etcd-certs
            hostPath:
              path: /etc/kubernetes/pki/etcd
              type: Directory
          - name: backup-tmp
            hostPath:
              path: /var/lib/etcd-backup
              type: DirectoryOrCreate
```

### 2.3 etcd 快照恢复：灾难演习必须练

备份的意义不在于保存，而在于 **能恢复** 。我见过太多团队的备份文件躺在 S3 桶里吃灰，真到要用的时候发现证书过期了、快照损坏了、甚至不知道怎么恢复。

**恢复核心流程：**

```
# Step 1: 停止所有 master 节点上的 kube-apiserver
mv /etc/kubernetes/manifests/kube-apiserver.yaml /tmp/

# Step 2: 在所有 master 节点上恢复 etcd 快照
ETCDCTL_API=3 etcdctl snapshot restore /backup/etcd-snapshot-20260525-060000.db \
  --name master-1 \
  --initial-cluster master-1=https://192.168.1.10:2380,master-2=https://192.168.1.11:2380,master-3=https://192.168.1.12:2380 \
  --initial-advertise-peer-urls https://192.168.1.10:2380 \
  --data-dir /var/lib/etcd-restore \
  --skip-hash-check=false  # 生产环境务必验证哈希

# Step 3: 用新数据目录替换旧目录
systemctl stop etcd  # 或 mv /etc/kubernetes/manifests/etcd.yaml /tmp/
rm -rf /var/lib/etcd/member
mv /var/lib/etcd-restore/member /var/lib/etcd/
chown -R etcd:etcd /var/lib/etcd

# Step 4: 启动 etcd，确认集群健康后再启动 apiserver
systemctl start etcd
mv /tmp/kube-apiserver.yaml /etc/kubernetes/manifests/
```

> **生产警告** ：恢复 etcd 快照会导致整个集群回到快照时刻的状态！快照时刻到恢复之间的 **所有增量数据将永久丢失** 。因此必须同时使用 Velero 做应用级备份（见下文），以便恢复 etcd 后还能捞回重要的增量变更。

---

## 三、Velero 实战：应用级备份与灾备迁移

etcd 快照是"核武器"，一次恢复全集群回滚。日常运维中，90% 的恢复场景都是 **命名空间级别** 的——有人不小心删了个 Deployment、改坏了 ConfigMap、或者需要把某个 Namespace 从旧集群迁移到新集群。

Velero（原名 Heptio Ark）就是为这些场景而生的。

### 3.1 Velero 架构原理

Velero 由两部分组成：

```
┌─────────────────────────────────────┐
│          Velero CLI (velero)        │
│  用户交互：创建备份、恢复、调度    │
└──────────────┬──────────────────────┘
               │ kubectl 风格的 API 调用
┌──────────────▼──────────────────────┐
│    Velero Server (Deployment)       │
│  ┌────────────────────────────────┐ │
│  │  Backup Controller             │ │ ← 按 Schedule 触发备份
│  │  Restore Controller            │ │ ← 执行恢复操作
│  │  BackupStorageLocation CR      │ │ ← 定义备份存储后端（S3）
│  │  VolumeSnapshotLocation CR     │ │ ← 定义卷快照后端（CSI）
│  └────────────────────────────────┘ │
└──────────────┬──────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼────┐         ┌──────▼──────┐
│  S3 /  │         │  CSI 快照   │
│  MinIO │         │  / Restic   │
│ (资源) │         │  (PV 数据)  │
└────────┘         └─────────────┘
```

**核心运作机制：**

1. 1\. **Backup 流程** ：Velero Controller 通过 K8s API 列出目标命名空间内的所有资源 → 序列化为 JSON/YAML → 压缩打包上传到对象存储（S3 兼容存储）。
2. 2\. **PV 备份** ：如果集群有 CSI 快照能力，Velero 会调用 CSI Driver 创建 VolumeSnapshot；如果没有 CSI，可以用 Restic/Kopia 做文件级备份。
3. 3\. **Restore 流程** ：从对象存储下载备份包 → 按依赖顺序重建资源（Namespace → CRD → RBAC → Deployment → Service） → 可选恢复 PV 数据。

### 3.2 Velero 安装与配置

```
# 下载 Velero CLI
wget https://github.com/vmware-tanzu/velero/releases/download/v1.14.0/velero-v1.14.0-linux-amd64.tar.gz
tar -xzf velero-v1.14.0-linux-amd64.tar.gz
sudo mv velero-v1.14.0-linux-amd64/velero /usr/local/bin/

# 安装 Velero Server（以 MinIO 为后端，无 CSI 快照时用 Restic）
velero install \
  --provider aws \
  --plugins velero/velero-plugin-for-aws:v1.9.0 \
  --bucket velero-backups \
  --secret-file ./credentials-velero \
  --use-volume-snapshots=false \
  --use-node-agent \            # 新版 Velero：用 node-agent 替代 restic
  --default-volumes-to-fs-backup \
  --backup-location-config region=minio,s3ForcePathStyle=true,s3Url=http://minio.default.svc:9000 \
  --namespace velero

# 查看安装状态
kubectl get pods -n velero
```

**credentials-velero 文件格式：**

```
[default]
aws_access_key_id = minioadmin
aws_secret_access_key = minioadmin
```

### 3.3 创建备份与恢复

```
# 备份单个 Namespace
velero backup create prod-backup-20260525 \
  --include-namespaces production \
  --wait

# 备份特定 Label 的资源（跨 Namespace）
velero backup create app-backup \
  --selector app=myapp \
  --wait

# 查看备份列表
velero backup get

# 查看备份详情
velero backup describe prod-backup-20260525

# 查看备份日志
velero backup logs prod-backup-20260525
```

**恢复操作：**

```
# 恢复到原 Namespace（会覆盖已有资源）
velero restore create --from-backup prod-backup-20260525

# 恢复到新 Namespace（推荐：安全演练/数据恢复）
velero restore create --from-backup prod-backup-20260525 \
  --namespace-mappings production:production-restored

# 只恢复特定资源类型
velero restore create --from-backup prod-backup-20260525 \
  --include-resources deployments,services,configmaps
```

### 3.4 定时备份 Schedule

```
# 也可以用 velero schedule create 命令行
velero schedule create daily-backup \
  --schedule="0 2 * * *" \              # 每天凌晨 2 点
  --include-namespaces production,staging \
  --ttl 720h0m0s \                       # 保留 30 天
  --storage-location default
```

创建后会生成一个 Schedule CR， `kubectl get schedule -n velero` 可以看到。

---

## 四、生产环境避坑指南

### 坑 1：备份不做恢复验证 = 没有备份

这是最致命的坑。2025 年 GitLab 的事故就是典型的例子：他们有备份，但从未做过恢复演练，出事后发现五六种备份策略——没一个能成功恢复。

**解决方案：** 每月至少一次的恢复演练。写一个 CronJob，在隔离的 Namespace 中执行自动恢复验证：

```
# 自动恢复测试 CronJob（验证 Velero 备份可用性）
apiVersion: batch/v1
kind: CronJob
metadata:
  name: backup-drill
  namespace: velero
spec:
  schedule: "0 8 1 * *"   # 每月 1 号早 8 点
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: velero
          containers:
          - name: drill
            image: velero/velero:v1.14.0
            command:
            - /bin/sh
            - -c
            - |
              # 获取最近一次备份
              LATEST_BACKUP=$(velero backup get -o json | jq -r '.items[0].metadata.name')
              echo "Testing restore from: ${LATEST_BACKUP}"

              # 恢复到独立命名空间
              velero restore create --from-backup ${LATEST_BACKUP} \
                --namespace-mappings production:production-drill \
                --wait

              # 验证关键 Deployment 是否 Ready
              kubectl wait --for=condition=available deployment/key-app \
                -n production-drill --timeout=300s

              echo "Restore verification PASSED"

              # 清理测试命名空间
              kubectl delete ns production-drill
          restartPolicy: OnFailure
```

### 坑 2：etcd 快照与 Velero 备份的时间差

假设 etcd 在 02:00 做了快照，Velero 在 03:00 做了备份。如果 02:30 创建了一个新的 Namespace + Deployment，那么：

- • etcd 快照（02:00）： **不包含** 新资源
- • Velero 备份（03:00）： **包含** 新资源

当你用 etcd 快照恢复集群后，必须再用 Velero 恢复快照时刻之后的增量资源。

**解决方案：** 建立对应关系。每次 Velero 备份完成后，记录当前的 etcd revision：

```
# 备份脚本中追加
ETCD_REV=$(ETCDCTL_API=3 etcdctl endpoint status --write-out=json | jq -r '.[0].Status.header.revision')
echo "etcd_revision: ${ETCD_REV}" >> /backup/velero-metadata.txt
```

### 坑 3：Secret 备份的安全性

etcd 快照包含 **所有 Secret 的明文数据** 。如果快照文件泄露，集群中所有 TLS 证书私钥、数据库密码、API Token——全部暴露。

**解决方案：**

```
# 对 etcd 快照文件进行 GPG 加密
gpg --encrypt --recipient backup-admin@company.com \
  /backup/etcd-snapshot-20260525.db

# 只上传加密后的文件
mc cp /backup/etcd-snapshot-20260525.db.gpg backup-s3/etcd-backups/

# 恢复时解密
gpg --decrypt /backup/etcd-snapshot-20260525.db.gpg > /backup/etcd-snapshot-20260525.db
```

或者直接用 S3 服务端加密（SSE-S3 / SSE-KMS），在 Velero 的 BackupStorageLocation 中配置：

```
apiVersion: velero.io/v1
kind: BackupStorageLocation
metadata:
  name: default
  namespace: velero
spec:
  provider: aws
  objectStorage:
    bucket: velero-backups
  config:
    region: us-east-1
    serverSideEncryption: AES256   # S3 服务端加密
    kmsKeyId: arn:aws:kms:...      # 可选：KMS 密钥
```

### 坑 4：etcd 磁盘空间耗尽导致快照失败

etcd 默认会每 10000 次事务创建一个快照，存储在 `--snapshot-count` 定义的路径。如果你的集群资源变更频繁，etcd 自带快照可能快速填满磁盘。

```
# 监控 etcd 数据库大小
ETCDCTL_API=3 etcdctl endpoint status --write-out=table

# 设置自动压缩，防止 DB 无限增长
ETCDCTL_API=3 etcdctl compact $(ETCDCTL_API=3 etcdctl endpoint status --write-out=json | jq -r '.[0].Status.header.revision')

# 在 etcd 配置中启用定期压缩
# /etc/kubernetes/manifests/etcd.yaml
spec:
  containers:
  - command:
    - etcd
    - --auto-compaction-mode=periodic
    - --auto-compaction-retention=24h    # 保留 24 小时的历史版本
```

### 坑 5：跨 Kubernetes 版本的 etcd 快照兼容性

etcd 快照是 **向前兼容** 的（高版本可读取低版本快照），但不是 **向后兼容** 的。

| etcd 版本 | 数据格式 | 兼容性说明 |
| --- | --- | --- |
| v3.3.x | v3 store | v3.4.x+ 可读取 |
| v3.4.x | v3 store + learner | v3.5.x+ 可读取 |
| v3.5.x | v3 store + learner + etcd v2 deprecation | 无法在 v3.4 上恢复 |

**如果你要跨版本恢复，必须先降级（恢复快照到原版本 etcd）再升级。**

### 坑 6：Velero Backup 不包含的"隐形状态"

Velero 通过 K8s API 获取资源状态，但以下"隐形状态"不在备份范围：

- • **Node 节点状态** ：节点标签、污点、容量信息。恢复后需手动重建。
- • **容器运行时状态** ：正在运行的容器状态（日志、临时文件）。
- • **外部依赖** ：外部数据库的连接串可能改变了（如 RDS 迁移后 endpoint 变了）。
- • **CRD 的 Webhook 配置** ：如果 MutatingWebhookConfiguration 指向的 Service 在 New Cluster 中不存在，恢复会阻塞。

**恢复后的检查清单：**

```
#!/bin/bash
# post-restore-check.sh
echo "=== 检查 Pod 状态 ==="
kubectl get pods -A | grep -E "Pending|Error|CrashLoopBackOff"

echo "=== 检查 PV 绑定 ==="
kubectl get pv | grep -v Bound

echo "=== 检查 Ingress 后端 ==="
kubectl get ingress -A --no-headers | while read ns name rest; do
  echo "Checking $ns/$name..."
done

echo "=== 检查 Webhook 连通性 ==="
kubectl get validatingwebhookconfigurations,mutatingwebhookconfigurations -A
```

---

## 五、综合预案：三层容灾架构落地

最后，让我把前面讲的所有内容串联成一个完整的三层容灾架构：

```
┌────────────────────────────────────────────────────┐
│                    三层容灾架构                     │
├────────────────────────────────────────────────────┤
│                                                    │
│  L1 — etcd 快照（保命）                             │
│  ├─ 频率：每 6 小时自动执行                         │
│  ├─ 存储：加密后上传到 S3 + 本地 master 保留 3 份   │
│  ├─ 恢复目标 (RTO)：< 30 分钟                       │
│  ├─ 恢复点目标 (RPO)：< 6 小时                      │
│  └─ 适用场景：etcd 损坏、集群状态丢失、全集群回滚   │
│                                                    │
│  L2 — Velero 应用备份（后悔药）                     │
│  ├─ 频率：每天凌晨全量 + 午间增量                   │
│  ├─ 存储：S3 兼容存储（MinIO/AWS S3/阿里云 OSS）    │
│  ├─ 恢复目标 (RTO)：< 10 分钟（单 Namespace）       │
│  ├─ 恢复点目标 (RPO)：< 24 小时                     │
│  └─ 适用场景：误删资源、Namespace 迁移、选择性恢复  │
│                                                    │
│  L3 — 应用数据备份（终极保险）                      │
│  ├─ 频率：数据库每小时 dump；文件存储实时同步        │
│  ├─ 存储：独立于 K8s 集群的存储后端                  │
│  ├─ 恢复目标 (RTO)：< 2 小时                        │
│  ├─ 恢复点目标 (RPO)：< 1 小时                      │
│  └─ 适用场景：数据损坏、勒索病毒、跨 Region 灾备     │
│                                                    │
└────────────────────────────────────────────────────┘
```

**Prometheus 告警规则（备份健康检查）：**

```
groups:
- name: backup-health
  rules:
  - alert: EtcdBackupFailed
    expr: time() - etcd_backup_last_success_timestamp > 86400
    for: 10m
    labels:
      severity: critical
    annotations:
      summary: "etcd 快照超过 24 小时未成功执行"

  - alert: VeleroBackupFailed
    expr: velero_backup_failure_total > 0
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Velero 备份失败：{{ $labels.schedule }}"

  - alert: BackupRestoreDrillMissed
    expr: time() - backup_drill_last_success_timestamp > 2592000
    for: 1h
    labels:
      severity: warning
    annotations:
      summary: "备份恢复演练超过 30 天未执行，请立即安排"
```

---

## 总结：备份不是成本，是保险

最后说几句掏心窝的话。

很多团队在 K8s 上跑了一年，从来没做过备份。他们的逻辑是："K8s 本身就有自愈能力，Pod 挂了会自动重建，Node 挂了 Pod 会漂移，怕什么？"

这种想法就像开车不买保险——没出事的时候确实省钱了，出事了就是家破人亡。

**衡量备份价值的公式：**

```
备份 ROI = (故障概率 × 故障导致损失) / 备份成本
```

对于任何一个生产集群：

- • 故障概率不是 0%，而是无限趋近于 100%（时间拉长到 3 年以上）
- • 故障导致损失 = 数据丢失价值 + 停机时间 × 每分钟营收损失 + 品牌信誉折损
- • 备份成本 = 存储费用 + 人力维护成本（运维人员的 10% 工时）

算完你会发现： **备份的 ROI 接近无穷大** 。

在生产环境落地时，记住三条铁律：

1. 1\. **没有做过恢复验证的备份等于没有备份** ——每月一次的恢复演练，雷打不动
2. 2\. **三层备份缺一不可** ——etcd 保命、Velero 后悔、应用数据终极保险
3. 3\. **备份文件必须加密 + 异地存储** ——同一机房的两个备份 = 一个备份

你的集群，准备好"后悔药"了吗？

---

> **作者** ：WAKE UP技术 **原文链接** ：https://blog.lweiqiang.xyz  
> 如果这篇文章对你有帮助，欢迎转发给团队里还在"裸奔"的同事。

**微信扫一扫赞赏作者**

继续滑动看下一个

WAKE UP技术

向上滑动看下一个