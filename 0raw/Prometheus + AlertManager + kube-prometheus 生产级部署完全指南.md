---
title: "Prometheus + AlertManager + kube-prometheus 生产级部署完全指南"
source: "https://mp.weixin.qq.com/s/VCQ81Mn0rgP9qPKnXzFM6w"
author:
  - "[[院长技术]]"
published:
created: 2026-06-05
description:
tags:
  - "clippings"
---
院长技术 *2026年5月26日 09:11*

## DeanTech企业级运维管理平台正在全新改版，修复Bug。

> **适用版本**: Kubernetes 1.35+  
> **存储方案**: NFS + StorageClass  
> **部署方式**: kube-prometheus-stack (Helm)  
> **最后更新**: 2025-05-26

---

## 目录

1. 1\. Prometheus 与 AlertManager 核心概念 <sup>[1]</sup>
2. 2\. 架构设计与组件说明 <sup>[2]</sup>
3. 3\. 环境准备与前置条件 <sup>[3]</sup>
4. 4\. NFS 存储与 StorageClass 配置 <sup>[4]</sup>
5. 5\. kube-prometheus-stack 生产级部署 <sup>[5]</sup>
6. 6\. 核心组件配置详解 <sup>[6]</sup>
7. 7\. 告警规则配置大全 <sup>[7]</sup>
8. 8\. ServiceMonitor 服务监控配置 <sup>[8]</sup>
9. 9\. AlertManager 告警路由配置 <sup>[9]</sup>
10. 10\. 参数优化与性能调优 <sup>[10]</sup>
11. 11\. 高可用与扩展方案 <sup>[11]</sup>
12. 12\. 故障排查与常见问题 <sup>[12]</sup>

---

## 一、Prometheus 与 AlertManager 核心概念

### 1.1 Prometheus 简介

**Prometheus** 是由 SoundCloud 开源的监控和告警工具包，现已成为云原生监控领域的事实标准，也是 CNCF 的毕业项目。

#### 核心特性

| 特性 | 说明 |
| --- | --- |
| **多维数据模型** | 时间序列数据由指标名称和键值对标签标识 |
| **灵活的查询语言 PromQL** | 强大的数据查询和聚合能力 |
| **不依赖分布式存储** | 单个服务器节点自治，易于运维 |
| **HTTP 拉取模型** | 通过 HTTP 协议主动拉取（pull）指标数据 |
| **支持推送网关** | 用于批处理作业和短生命周期服务的推送（push）模式 |
| **多种可视化方案** | 内置表达式浏览器，完美支持 Grafana |
| **高效存储** | 自定义的时序数据库，支持压缩和分块 |

#### 数据模型

```
指标名称{标签1="值1", 标签2="值2"} 数值 时间戳

示例：
http_requests_total{method="POST", handler="/api/users", status="200"} 1027 1699123456000
```

#### 四种核心指标类型

| 类型 | 说明 | 示例 |
| --- | --- | --- |
| **Counter（计数器）** | 只增不减的累加值 | `http_requests_total` |
| **Gauge（仪表盘）** | 可增可减的瞬时值 | `node_memory_MemAvailable_bytes` |
| **Histogram（直方图）** | 数据分布统计（分位数） | `http_request_duration_seconds` |
| **Summary（摘要）** | 客户端计算的分位数 | `rpc_duration_seconds` |

### 1.2 AlertManager 简介

**AlertManager** 是 Prometheus 生态中的告警管理组件，负责处理 Prometheus 服务器发送的告警，进行分组、抑制、静默和路由，最终通过多种渠道通知接收者。

#### 核心功能

| 功能 | 描述 |
| --- | --- |
| **分组 (Grouping)** | 将相似告警聚合为单一通知，减少告警风暴 |
| **抑制 (Inhibition)** | 当高优先级告警触发时，抑制低优先级相关告警 |
| **静默 (Silencing)** | 在维护窗口期间临时静默特定告警 |
| **路由 (Routing)** | 基于标签将告警路由到不同的接收器 |
| **去重 (Deduplication)** | 消除重复告警通知 |

#### 告警生命周期

```
Inactive → Pending → Firing → Resolved
  ↑          ↑          ↑          ↑
未触发    条件满足    持续满足    条件恢复
         但未超时    超过阈值    告警解除
```
- • **Inactive**: 告警条件未满足
- • **Pending**: 条件已满足但未超过 `for` 指定的持续时间
- • **Firing**: 条件持续满足超过 `for` 时间，告警触发
- • **Resolved**: 条件不再满足，告警恢复

### 1.3 kube-prometheus 项目

**kube-prometheus** 是一个完整的 Kubernetes 监控解决方案，通过 Prometheus Operator 以声明式方式部署和管理 Prometheus 生态系统。

#### 包含组件

```
┌─────────────────────────────────────────────────────────────┐
│                    kube-prometheus-stack                    │
├─────────────────────────────────────────────────────────────┤
│  Prometheus Operator    │  Prometheus CRD 控制器            │
│  Prometheus Server      │  时序数据库与采集引擎              │
│  AlertManager           │  告警管理与通知路由               │
│  Grafana                │  可视化仪表盘                     │
│  Node Exporter          │  节点级系统指标采集               │
│  kube-state-metrics     │  K8s 资源状态指标                 │
│  Prometheus Adapter     │  K8s Metrics API 适配器           │
│  Blackbox Exporter      │  黑盒探测与端点监控               │
└─────────────────────────────────────────────────────────────┘
```

#### 核心 CRD 说明

| CRD | 作用 |
| --- | --- |
| `Prometheus` | 定义 Prometheus 服务器实例 |
| `Alertmanager` | 定义 AlertManager 实例 |
| `ServiceMonitor` | 基于 Service 的服务发现与监控 |
| `PodMonitor` | 基于 Pod 的服务发现与监控 |
| `PrometheusRule` | 定义告警规则和记录规则 |
| `ThanosRuler` | 定义 Thanos Ruler 实例 |

---

## 二、架构设计与组件说明

### 2.1 整体架构图

```
┌─────────────────┐
                              │   User/Admin    │
                              └────────┬────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
           ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
           │   Grafana   │    │  Prometheus │    │ AlertManager│
           │   :3000     │    │   :9090     │    │   :9093     │
           └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
                  │                  │                  │
                  │    ┌─────────────┴─────────────┐    │
                  │    │                           │    │
                  └────┤    Prometheus Operator    ├────┘
                       │                           │
                       └─────────────┬─────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         │                           │                           │
         ▼                           ▼                           ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  ServiceMonitor │      │  PodMonitor     │      │ PrometheusRule  │
│  (服务发现)      │      │  (Pod发现)      │      │  (告警规则)      │
└────────┬────────┘      └────────┬────────┘      └─────────────────┘
         │                        │
         ▼                        ▼
┌─────────────────┐      ┌─────────────────┐
│  Target Apps    │      │  Node Exporter  │
│  (业务应用)      │      │  (节点指标)      │
└─────────────────┘      └─────────────────┘
```

### 2.2 核心组件详解

#### Prometheus Operator

- • **作用**: 通过 Kubernetes CRD 管理 Prometheus 实例
- • **核心能力**: 自动生成 Prometheus 配置、管理 StatefulSet、处理服务发现
- • **自动发现机制**: 监听 ServiceMonitor/PodMonitor/PrometheusRule 资源变化

#### Prometheus Server

- • **存储引擎**: TSDB (Time Series Database)
- • **采集方式**: Pull 模式（HTTP），默认 30s 间隔
- • **服务发现**: Kubernetes SD、DNS SD、File SD、Consul SD 等
- • **查询语言**: PromQL (Prometheus Query Language)

#### AlertManager

- • **高可用**: 支持集群模式（Gossip 协议）
- • **通知渠道**: Email、Slack、PagerDuty、Webhook、钉钉、企业微信等
- • **配置热加载**: 支持 SIGHUP 或 HTTP POST `/-/reload` 重新加载配置

#### Grafana

- • **可视化**: 丰富的图表类型和 Dashboard 模板
- • **数据源**: 支持 Prometheus、InfluxDB、Elasticsearch 等
- • **告警集成**: 内置告警规则（也可使用 Prometheus 告警）

### 2.3 数据流说明

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Target      │────▶│  Prometheus  │────▶│ AlertManager │────▶│  Receiver    │
│  (被监控端)   │Pull │  (采集存储)   │Alert│  (告警管理)   │Notify│  (通知渠道)   │
└──────────────┘     └──────┬───────┘     └──────────────┘     └──────────────┘
                            │
                            │Query
                            ▼
                     ┌──────────────┐
                     │   Grafana    │
                     │  (可视化)     │
                     └──────────────┘
```
1. 1\. **数据采集**: Prometheus 通过 HTTP Pull 模式从 Target 拉取指标
2. 2\. **规则评估**: Prometheus 定期评估告警规则，触发告警发送给 AlertManager
3. 3\. **告警处理**: AlertManager 对告警进行分组、去重、抑制、路由
4. 4\. **通知发送**: AlertManager 将告警发送到配置的接收器（邮件、Slack 等）
5. 5\. **数据查询**: Grafana 通过 PromQL 查询 Prometheus 数据进行可视化

---

## 三、环境准备与前置条件

### 3.1 系统要求

#### 最低配置

| 组件 | CPU | 内存 | 磁盘 | 说明 |
| --- | --- | --- | --- | --- |
| Prometheus | 2核 | 4GB | 100GB | 单实例 |
| AlertManager | 1核 | 512MB | 10GB | 单实例 |
| Grafana | 1核 | 512MB | 10GB | 单实例 |
| Node Exporter | 100m | 128MB | \- | 每节点 |

#### 推荐配置（生产环境）

| 组件 | CPU | 内存 | 磁盘 | 说明 |
| --- | --- | --- | --- | --- |
| Prometheus | 4核 | 16GB | 500GB+ SSD | 高可用双实例 |
| AlertManager | 2核 | 2GB | 20GB | 高可用三实例 |
| Grafana | 2核 | 4GB | 20GB | 单实例 |

### 3.2 Kubernetes 集群要求

#### 版本兼容性

| kube-prometheus 版本 | Kubernetes 版本 | 推荐 Helm Chart 版本 |
| --- | --- | --- |
| v0.14.x | 1.30 - 1.32 | 62.x |
| v0.15.x | 1.32 - 1.34 | 70.x |
| v0.16.x | 1.33 - 1.35 | 75.x |
| v0.17.x | 1.35+ | 76.x+ |

#### Kubelet 配置检查

```
# 检查所有节点的 kubelet 配置
kubectl get --raw /api/v1/nodes/<node-name>/proxy/configz | jq '.kubeletconfig | {authentication: .authentication.webhook.enabled, authorization: .authorization.mode}'

# 预期输出
{
  "authentication": true,
  "authorization": "Webhook"
}
```

> **注意**: 如果 `authentication.webhook.enabled` 为 `false` 或 `authorization.mode` 不是 `Webhook` ，需要修改 kubelet 配置并重启。

#### 控制平面组件配置

确保以下组件绑定到 `0.0.0.0` ，允许 Prometheus 采集指标：

```
# 修改 controller-manager
sudo sed -i 's/--bind-address=127.0.0.1/--bind-address=0.0.0.0/' /etc/kubernetes/manifests/kube-controller-manager.yaml

# 修改 scheduler
sudo sed -i 's/--bind-address=127.0.0.1/--bind-address=0.0.0.0/' /etc/kubernetes/manifests/kube-scheduler.yaml

# 重启组件（自动）
kubectl delete pod -n kube-system -l component=kube-controller-manager
kubectl delete pod -n kube-system -l component=kube-scheduler
```

### 3.3 工具安装

```
# 安装 Helm (v3.13+)
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# 验证安装
helm version

# 添加 Prometheus Community Helm 仓库
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# 查看可用版本
helm search repo kube-prometheus-stack --versions | head -20
```

### 3.4 命名空间创建

```
# 创建监控专用命名空间
kubectl create namespace monitoring

# 设置默认上下文（可选）
kubectl config set-context --current --namespace=monitoring
```

---

## 四、NFS 存储与 StorageClass 配置

### 4.1 NFS 服务器部署

#### 安装 NFS 服务

```
# Ubuntu/Debian
sudo apt update
sudo apt install -y nfs-kernel-server

# CentOS/RHEL
sudo yum install -y nfs-utils

# 创建共享目录
sudo mkdir -p /data/k8s/nfs/prometheus
sudo mkdir -p /data/k8s/nfs/grafana
sudo mkdir -p /data/k8s/nfs/alertmanager

# 设置权限
sudo chown -R nobody:nogroup /data/k8s/nfs
sudo chmod -R 777 /data/k8s/nfs
```

#### 配置 NFS 导出

```
# 编辑 /etc/exports
sudo tee /etc/exports << 'EOF'
# Prometheus 数据存储
/data/k8s/nfs/prometheus 192.168.0.0/16(rw,sync,no_subtree_check,no_root_squash)

# Grafana 数据存储
/data/k8s/nfs/grafana 192.168.0.0/16(rw,sync,no_subtree_check,no_root_squash)

# AlertManager 数据存储
/data/k8s/nfs/alertmanager 192.168.0.0/16(rw,sync,no_subtree_check,no_root_squash)
EOF

# 参数说明：
# rw: 读写权限
# sync: 同步写入磁盘
# no_subtree_check: 禁用子树检查，提升性能
# no_root_squash: 允许 root 用户保留权限（容器内可能需要）

# 生效配置
sudo exportfs -ra

# 启动服务
sudo systemctl enable nfs-server
sudo systemctl restart nfs-server

# 验证
sudo exportfs -v
sudo showmount -e localhost
```

#### 防火墙配置

```
# Ubuntu (UFW)
sudo ufw allow from 192.168.0.0/16 to any port nfs
sudo ufw allow 2049/tcp
sudo ufw allow 111/tcp
sudo ufw allow 111/udp

# CentOS (firewalld)
sudo firewall-cmd --permanent --add-service=nfs
sudo firewall-cmd --permanent --add-service=rpc-bind
sudo firewall-cmd --permanent --add-service=mountd
sudo firewall-cmd --reload
```

### 4.2 Kubernetes 节点配置

```
# 在所有 K8s 节点上安装 NFS 客户端

# Ubuntu/Debian
sudo apt install -y nfs-common

# CentOS/RHEL
sudo yum install -y nfs-utils

# 测试挂载
sudo mkdir -p /mnt/test-nfs
sudo mount -t nfs <nfs-server-ip>:/data/k8s/nfs/prometheus /mnt/test-nfs
echo "test" | sudo tee /mnt/test-nfs/test.txt
cat /mnt/test-nfs/test.txt
sudo umount /mnt/test-nfs
```

### 4.3 NFS 动态存储供应配置

#### 方法一：使用 nfs-subdir-external-provisioner（推荐）

```
# 添加 Helm 仓库
helm repo add nfs-subdir-external-provisioner https://kubernetes-sigs.github.io/nfs-subdir-external-provisioner/
helm repo update

# 安装 provisioner
helm install nfs-provisioner nfs-subdir-external-provisioner/nfs-subdir-external-provisioner \
  --namespace kube-system \
  --set nfs.server=<nfs-server-ip> \
  --set nfs.path=/data/k8s/nfs \
  --set storageClass.name=nfs-client \
  --set storageClass.defaultClass=true \
  --set storageClass.reclaimPolicy=Retain

# 查看安装状态
kubectl get pods -n kube-system -l app=nfs-subdir-external-provisioner
kubectl get storageclass
```

#### 方法二：使用 NFS CSI Driver

```
# 克隆仓库
git clone https://github.com/kubernetes-csi/csi-driver-nfs.git
cd csi-driver-nfs

# 修改镜像地址为国内镜像（可选）
sed -i "s#registry.k8s.io#k8s.m.daocloud.io#g" deploy/v4.12.0/*.yaml

# 安装 NFS-CSI
./deploy/install-driver.sh v4.12.0 local

# 验证安装
kubectl get pod -l app=csi-nfs-node -n kube-system
kubectl get csidriver
```

#### 创建 StorageClass

```
# nfs-storageclass.yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: nfs-client
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: kubernetes.io/no-provisioner  # 如果用 nfs-subdir-external-provisioner
# provisioner: nfs.csi.k8s.io              # 如果用 NFS CSI Driver
parameters:
  archiveOnDelete: "true"    # 删除 PVC 时归档而非直接删除
reclaimPolicy: Retain
volumeBindingMode: Immediate
mountOptions:
  - nfsvers=4.1
  - hard
  - intr
  - rsize=1048576
  - wsize=1048576
  - noatime
  - nodiratime
```
```
kubectl apply -f nfs-storageclass.yaml
kubectl get storageclass
```

### 4.4 存储验证

```
# 创建测试 PVC
kubectl apply -f - << 'EOF'
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: test-nfs-pvc
  namespace: monitoring
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: nfs-client
  resources:
    requests:
      storage: 1Gi
EOF

# 查看 PVC 状态
kubectl get pvc -n monitoring

# 预期输出：STATUS 为 Bound
# NAME           STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
# test-nfs-pvc   Bound    pvc-xxxxx   1Gi        RWO            nfs-client     10s

# 清理测试资源
kubectl delete pvc test-nfs-pvc -n monitoring
```

---

## 五、kube-prometheus-stack 生产级部署

### 5.1 获取默认配置

```
# 创建配置目录
mkdir -p ~/kube-prometheus-config
cd ~/kube-prometheus-config

# 导出默认 values.yaml
helm show values prometheus-community/kube-prometheus-stack > values-default.yaml

# 查看当前最新版本
helm search repo kube-prometheus-stack --versions | head -5
```

### 5.2 生产级 values.yaml 配置

```
# values-production.yaml
# ============================================
# kube-prometheus-stack 生产级配置
# 适用于 Kubernetes 1.35+
# 存储: NFS + StorageClass
# ============================================

# --------------------------------------------
# 全局配置
# --------------------------------------------
global:
  rbac:
    create: true

# --------------------------------------------
# Prometheus Operator 配置
# --------------------------------------------
prometheusOperator:
  enabled: true
  resources:
    limits:
      cpu: 1000m
      memory: 512Mi
    requests:
      cpu: 100m
      memory: 128Mi
  replicas: 1
  admissionWebhooks:
    enabled: true
    patch:
      enabled: true
      image:
        repository: registry.aliyuncs.com/google_containers/kube-webhook-certgen
        tag: v1.5.2
        pullPolicy: IfNotPresent
  image:
    repository: quay.io/prometheus-operator/prometheus-operator
    tag: v0.76.0
    pullPolicy: IfNotPresent
  prometheusConfigReloader:
    image:
      repository: quay.io/prometheus-operator/prometheus-config-reloader
      tag: v0.76.0
    resources:
      limits:
        cpu: 200m
        memory: 128Mi
      requests:
        cpu: 50m
        memory: 32Mi

# --------------------------------------------
# Prometheus 配置
# --------------------------------------------
prometheus:
  enabled: true
  prometheusSpec:
    image:
      repository: quay.io/prometheus/prometheus
      tag: v2.55.0
    replicas: 2
    shards: 1
    resources:
      limits:
        cpu: 4000m
        memory: 16Gi
      requests:
        cpu: 1000m
        memory: 4Gi

    # 存储配置（使用 NFS StorageClass）
    storageSpec:
      volumeClaimTemplate:
        spec:
          storageClassName: nfs-client
          accessModes: ["ReadWriteOnce"]
          resources:
            requests:
              storage: 500Gi

    # 数据保留策略
    retention: 30d
    retentionSize: 450GB

    # 查询配置
    query:
      maxSamples: 50000000
      timeout: 2m
      maxConcurrency: 20

    # 抓取配置
    scrapeInterval: 30s
    evaluationInterval: 30s

    # 服务发现配置（允许发现所有命名空间的资源）
    serviceMonitorSelectorNilUsesHelmValues: false
    serviceMonitorSelector: {}
    serviceMonitorNamespaceSelector: {}
    podMonitorSelectorNilUsesHelmValues: false
    podMonitorSelector: {}
    podMonitorNamespaceSelector: {}
    ruleSelectorNilUsesHelmValues: false
    ruleSelector: {}
    ruleNamespaceSelector: {}

    # 启用特性
    enableFeatures:
      - exemplar-storage
      - memory-snapshot-on-shutdown
      - new-service-discovery-manager

    # 安全上下文
    securityContext:
      runAsUser: 1000
      runAsNonRoot: true
      fsGroup: 2000

    # 额外参数
    additionalArgs:
      - name: storage.tsdb.min-block-duration
        value: 2h
      - name: storage.tsdb.max-block-duration
        value: 2h

    # 告警管理配置
    alerting:
      alertmanagers:
        - namespace: monitoring
          name: alertmanager-operated
          port: web
          apiVersion: v2

    additionalScrapeConfigs: []

  service:
    type: ClusterIP
    port: 9090
    targetPort: 9090

  ingress:
    enabled: true
    ingressClassName: nginx
    hosts:
      - prometheus.example.com
    paths:
      - /
    pathType: Prefix
    tls:
      - secretName: prometheus-tls
        hosts:
          - prometheus.example.com

# --------------------------------------------
# AlertManager 配置
# --------------------------------------------
alertmanager:
  enabled: true
  alertmanagerSpec:
    image:
      repository: quay.io/prometheus/alertmanager
      tag: v0.27.0
    replicas: 3
    resources:
      limits:
        cpu: 1000m
        memory: 1Gi
      requests:
        cpu: 100m
        memory: 256Mi

    # 存储配置
    storage:
      volumeClaimTemplate:
        spec:
          storageClassName: nfs-client
          accessModes: ["ReadWriteOnce"]
          resources:
            requests:
              storage: 50Gi

    retention: 720h  # 30天
    logLevel: info
    clusterAdvertiseAddress: $(POD_IP)

    securityContext:
      runAsUser: 1000
      runAsNonRoot: true
      fsGroup: 2000

  service:
    type: ClusterIP
    port: 9093
    targetPort: 9093

  ingress:
    enabled: true
    ingressClassName: nginx
    hosts:
      - alertmanager.example.com
    paths:
      - /
    pathType: Prefix
    tls:
      - secretName: alertmanager-tls
        hosts:
          - alertmanager.example.com

# --------------------------------------------
# Grafana 配置
# --------------------------------------------
grafana:
  enabled: true
  adminUser: admin
  adminPassword: admin123  # 生产环境请修改！

  image:
    repository: grafana/grafana
    tag: 11.1.0
    pullPolicy: IfNotPresent

  resources:
    limits:
      cpu: 1000m
      memory: 1Gi
    requests:
      cpu: 250m
      memory: 512Mi

  # 持久化配置
  persistence:
    enabled: true
    type: pvc
    storageClassName: nfs-client
    accessModes:
      - ReadWriteOnce
    size: 50Gi
    finalizers:
      - kubernetes.io/pvc-protection

  service:
    type: ClusterIP
    port: 80
    targetPort: 3000

  ingress:
    enabled: true
    ingressClassName: nginx
    hosts:
      - grafana.example.com
    paths:
      - /
    pathType: Prefix
    tls:
      - secretName: grafana-tls
        hosts:
          - grafana.example.com

  # 数据源配置
  datasources:
    datasources.yaml:
      apiVersion: 1
      datasources:
        - name: Prometheus
          type: prometheus
          url: http://prometheus-kube-prometheus-prometheus:9090
          access: proxy
          isDefault: true
          jsonData:
            timeInterval: "5s"
            httpMethod: POST
            manageAlerts: true
            prometheusType: Prometheus
            prometheusVersion: "2.55.0"

  # 预装仪表盘
  dashboards:
    default:
      kubernetes-cluster:
        gnetId: 7249
        revision: 1
        datasource: Prometheus
      kubernetes-pods:
        gnetId: 747
        revision: 1
        datasource: Prometheus
      node-exporter:
        gnetId: 1860
        revision: 27
        datasource: Prometheus

  plugins:
    - grafana-piechart-panel
    - grafana-clock-panel

  env:
    GF_SERVER_ROOT_URL: "https://grafana.example.com"
    GF_SECURITY_CSRF_ADDITIONAL_HEADERS: "X-Forwarded-Host"
    GF_SECURITY_CSRF_TRUSTED_ORIGINS: "https://grafana.example.com"
    GF_AUTH_ANONYMOUS_ENABLED: "false"
    GF_AUTH_BASIC_ENABLED: "true"
    GF_SECURITY_DISABLE_GRAVATAR: "true"
    GF_SECURITY_ANGULAR_SUPPORT_ENABLED: "false"
    GF_ANALYTICS_REPORTING_ENABLED: "false"
    GF_ANALYTICS_CHECK_FOR_UPDATES: "false"

# --------------------------------------------
# Node Exporter 配置
# --------------------------------------------
prometheus-node-exporter:
  enabled: true
  image:
    repository: quay.io/prometheus/node-exporter
    tag: v1.8.2
    pullPolicy: IfNotPresent
  resources:
    limits:
      cpu: 250m
      memory: 256Mi
    requests:
      cpu: 50m
      memory: 64Mi
  extraArgs:
    - --path.procfs=/host/proc
    - --path.sysfs=/host/sys
    - --path.rootfs=/host/root
    - --collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)
    - --collector.systemd
    - --collector.tcpstat
    - --collector.processes
  tolerations:
    - operator: Exists

# --------------------------------------------
# kube-state-metrics 配置
# --------------------------------------------
kube-state-metrics:
  enabled: true
  image:
    repository: registry.k8s.io/kube-state-metrics/kube-state-metrics
    tag: v2.13.0
    pullPolicy: IfNotPresent
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 100m
      memory: 128Mi

# --------------------------------------------
# Prometheus Adapter 配置
# --------------------------------------------
prometheusAdapter:
  enabled: true
  image:
    repository: registry.k8s.io/prometheus-adapter/prometheus-adapter
    tag: v0.12.0
    pullPolicy: IfNotPresent
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 100m
      memory: 128Mi
  replicas: 2

# --------------------------------------------
# Blackbox Exporter 配置
# --------------------------------------------
prometheus-blackbox-exporter:
  enabled: true
  image:
    repository: quay.io/prometheus/blackbox-exporter
    tag: v0.25.0
  resources:
    limits:
      cpu: 200m
      memory: 256Mi
    requests:
      cpu: 50m
      memory: 64Mi
  config:
    modules:
      http_2xx:
        prober: http
        timeout: 5s
        http:
          valid_http_versions: ["HTTP/1.1", "HTTP/2.0"]
          valid_status_codes: [200, 301, 302]
          method: GET
          follow_redirects: true
          fail_if_ssl: false
          tls_config:
            insecure_skip_verify: true
      http_post_2xx:
        prober: http
        timeout: 5s
        http:
          method: POST
          valid_status_codes: [200]
      tcp_connect:
        prober: tcp
        timeout: 5s
      icmp:
        prober: icmp
        timeout: 5s
        icmp:
          preferred_ip_protocol: ip4

# --------------------------------------------
# 默认规则配置
# --------------------------------------------
defaultRules:
  create: true
  rules:
    alertmanager: true
    etcd: true
    configReloaders: true
    general: true
    k8s: true
    kubeApiserverAvailability: true
    kubeApiserverBurnrate: true
    kubeApiserverHistogram: true
    kubeApiserverSlos: true
    kubeControllerManager: true
    kubelet: true
    kubeProxy: true
    kubePrometheusGeneral: true
    kubePrometheusNodeRecording: true
    kubernetesApps: true
    kubernetesResources: true
    kubernetesStorage: true
    kubernetesSystem: true
    kubeSchedulerAlerting: true
    kubeSchedulerRecording: true
    kubeStateMetrics: true
    network: true
    node: true
    nodeExporterAlerting: true
    nodeExporterRecording: true
    prometheus: true
    prometheusOperator: true

# --------------------------------------------
# 网络策略（生产环境建议启用）
# --------------------------------------------
networkPolicy:
  enabled: false

# --------------------------------------------
# Pod 安全标准
# --------------------------------------------
podSecurityStandard:
  enabled: true
  enforce: "baseline"
  audit: "restricted"
  warn: "restricted"
```

### 5.3 部署执行

```
# 创建命名空间
kubectl create namespace monitoring

# 部署 kube-prometheus-stack
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --values values-production.yaml \
  --version 76.0.0 \
  --timeout 600s \
  --wait
```

> **注意**: 如果网络拉取镜像困难，请修改 `values-production.yaml` 中的镜像地址为国内镜像源（如 `registry.aliyuncs.com` 、 `k8s.m.daocloud.io` 等）。

### 5.4 部署验证

```
# 检查所有 Pod 状态
kubectl get pods -n monitoring -o wide

# 预期输出：
# NAME                                                     READY   STATUS    RESTARTS   AGE
# alertmanager-kube-prometheus-stack-alertmanager-0        2/2     Running   0          5m
# alertmanager-kube-prometheus-stack-alertmanager-1        2/2     Running   0          5m
# alertmanager-kube-prometheus-stack-alertmanager-2        2/2     Running   0          5m
# kube-prometheus-stack-grafana-7c466d88c5-xxxxx          3/3     Running   0          5m
# kube-prometheus-stack-kube-state-metrics-77d5757f57-xxx  1/1     Running   0          5m
# kube-prometheus-stack-operator-67b84b5d9b-xxxxx         1/1     Running   0          5m
# kube-prometheus-stack-prometheus-node-exporter-xxxxx    1/1     Running   0          5m
# prometheus-adapter-xxxxx                                1/1     Running   0          5m
# prometheus-kube-prometheus-stack-prometheus-0           2/2     Running   0          5m
# prometheus-kube-prometheus-stack-prometheus-1           2/2     Running   0          5m

# 检查服务
kubectl get svc -n monitoring

# 检查 Ingress
kubectl get ingress -n monitoring

# 检查 PVC 绑定状态
kubectl get pvc -n monitoring

# 检查 StorageClass
kubectl get storageclass
```

### 5.5 访问验证

```
# 方式1：Port-forward（临时访问）
# Prometheus
kubectl port-forward svc/kube-prometheus-stack-prometheus 9090:9090 -n monitoring

# Grafana
kubectl port-forward svc/kube-prometheus-stack-grafana 3000:80 -n monitoring

# AlertManager
kubectl port-forward svc/kube-prometheus-stack-alertmanager 9093:9093 -n monitoring

# 方式2：通过 Ingress 访问（配置 DNS 后）
# https://prometheus.example.com
# https://grafana.example.com
# https://alertmanager.example.com

# 获取 Grafana 管理员密码
kubectl get secret kube-prometheus-stack-grafana -n monitoring \
  -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
```

### 5.6 卸载（如需）

```
helm uninstall kube-prometheus-stack -n monitoring

# 如果需要清理 NFS 上的数据，手动删除 NFS 服务器上的对应目录
```

---

## 六、核心组件配置详解

### 6.1 Prometheus CRD 配置

```
# prometheus-custom.yaml
apiVersion: monitoring.coreos.com/v1
kind: Prometheus
metadata:
  name: k8s
  namespace: monitoring
  labels:
    prometheus: k8s
spec:
  version: v2.55.0
  replicas: 2

  resources:
    requests:
      cpu: 1000m
      memory: 4Gi
    limits:
      cpu: 4000m
      memory: 16Gi

  # 存储配置
  storage:
    volumeClaimTemplate:
      spec:
        storageClassName: nfs-client
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 500Gi

  # 数据保留
  retention: 30d
  retentionSize: 450GB

  # 查询配置
  query:
    maxSamples: 50000000
    timeout: 2m
    maxConcurrency: 20

  # 抓取配置
  scrapeInterval: 30s
  evaluationInterval: 30s

  # 服务发现
  serviceMonitorSelector:
    matchExpressions:
      - key: app
        operator: Exists
  serviceMonitorNamespaceSelector: {}
  podMonitorSelector:
    matchExpressions:
      - key: app
        operator: Exists
  podMonitorNamespaceSelector: {}
  ruleSelector:
    matchLabels:
      role: alert-rules
      prometheus: k8s
  ruleNamespaceSelector: {}

  # 告警配置
  alerting:
    alertmanagers:
      - namespace: monitoring
        name: alertmanager-operated
        port: web
        apiVersion: v2

  # 安全上下文
  securityContext:
    runAsUser: 1000
    runAsNonRoot: true
    fsGroup: 2000

  # 启用特性
  enableFeatures:
    - exemplar-storage
    - memory-snapshot-on-shutdown
    - new-service-discovery-manager

  # 额外参数
  additionalArgs:
    - name: storage.tsdb.min-block-duration
      value: 2h
    - name: storage.tsdb.max-block-duration
      value: 2h
    - name: query.max-samples
      value: "50000000"

  # 亲和性配置（Pod 分散到不同节点）
  affinity:
    podAntiAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
        - weight: 100
          podAffinityTerm:
            labelSelector:
              matchExpressions:
                - key: app.kubernetes.io/name
                  operator: In
                  values:
                    - prometheus
            topologyKey: kubernetes.io/hostname

  # 容忍配置
  tolerations:
    - key: "monitoring"
      operator: "Equal"
      value: "true"
      effect: "NoSchedule"
```

### 6.2 AlertManager CRD 配置

```
# alertmanager-custom.yaml
apiVersion: monitoring.coreos.com/v1
kind: Alertmanager
metadata:
  name: main
  namespace: monitoring
  labels:
    alertmanager: main
spec:
  version: v0.27.0
  replicas: 3

  resources:
    requests:
      cpu: 100m
      memory: 256Mi
    limits:
      cpu: 1000m
      memory: 1Gi

  # 存储配置
  storage:
    volumeClaimTemplate:
      spec:
        storageClassName: nfs-client
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 50Gi

  retention: 720h  # 30天
  logLevel: info
  clusterAdvertiseAddress: $(POD_IP)

  securityContext:
    runAsUser: 1000
    runAsNonRoot: true
    fsGroup: 2000

  # 亲和性配置（Pod 分散到不同节点）
  affinity:
    podAntiAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        - labelSelector:
            matchExpressions:
              - key: app.kubernetes.io/name
                operator: In
                values:
                  - alertmanager
          topologyKey: kubernetes.io/hostname

  tolerations:
    - key: "monitoring"
      operator: "Equal"
      value: "true"
      effect: "NoSchedule"
```

### 6.3 配置热更新

```
# Prometheus 配置重载
kubectl exec -it prometheus-k8s-0 -n monitoring -c prometheus -- kill -HUP 1

# 或者使用 API
curl -X POST http://prometheus:9090/-/reload

# AlertManager 配置重载
kubectl exec -it alertmanager-main-0 -n monitoring -c alertmanager -- kill -HUP 1

# 或者使用 API
curl -X POST http://alertmanager:9093/-/reload
```

### 6.4 Helm 升级与回滚

```
# 升级
helm upgrade kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --values values-production.yaml \
  --version 76.1.0

# 回滚到上一版本
helm rollback kube-prometheus-stack -n monitoring

# 查看历史版本
helm history kube-prometheus-stack -n monitoring
```

---

## 七、告警规则配置大全

### 7.1 告警规则概述

Prometheus 使用 `PrometheusRule` CRD 定义告警规则。每个规则包含：

- • **告警名称**: 唯一标识告警
- • **表达式**: PromQL 查询，触发条件
- • **持续时间**: 条件持续多久后触发
- • **标签**: 用于路由和分组
- • **注解**: 告警描述和详情

### 7.2 节点与基础设施告警

```
# rules/node-alerts.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: node-alerts
  namespace: monitoring
  labels:
    prometheus: k8s
    role: alert-rules
spec:
  groups:
    # ============================================
    # 节点状态告警
    # ============================================
    - name: node.status
      interval: 30s
      rules:
        - alert: NodeDown
          expr: up{job="node-exporter"} == 0
          for: 5m
          labels:
            severity: critical
            team: ops
          annotations:
            summary: "节点 {{ $labels.instance }} 宕机"
            description: "节点 {{ $labels.instance }} 已宕机超过 5 分钟"
            runbook_url: "https://wiki.example.com/runbooks/node-down"

        - alert: NodeNotReady
          expr: kube_node_status_condition{condition="Ready",status="false"} == 1
          for: 5m
          labels:
            severity: critical
            team: ops
          annotations:
            summary: "节点 {{ $labels.node }} 状态为 NotReady"
            description: "节点 {{ $labels.node }} 状态为 NotReady 超过 5 分钟"

        - alert: NodeDiskPressure
          expr: kube_node_status_condition{condition="DiskPressure",status="true"} == 1
          for: 2m
          labels:
            severity: warning
            team: ops
          annotations:
            summary: "节点 {{ $labels.node }} 磁盘压力过高"
            description: "节点 {{ $labels.node }} 存在磁盘压力"

        - alert: NodeMemoryPressure
          expr: kube_node_status_condition{condition="MemoryPressure",status="true"} == 1
          for: 2m
          labels:
            severity: warning
            team: ops
          annotations:
            summary: "节点 {{ $labels.node }} 内存压力过高"
            description: "节点 {{ $labels.node }} 存在内存压力"

        - alert: NodePIDPressure
          expr: kube_node_status_condition{condition="PIDPressure",status="true"} == 1
          for: 2m
          labels:
            severity: warning
            team: ops
          annotations:
            summary: "节点 {{ $labels.node }} PID 压力过高"
            description: "节点 {{ $labels.node }} 存在 PID 压力"

    # ============================================
    # 节点资源告警
    # ============================================
    - name: node.resources
      interval: 30s
      rules:
        - alert: HighCPUUsage
          expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
          for: 5m
          labels:
            severity: warning
            team: ops
          annotations:
            summary: "节点 {{ $labels.instance }} CPU 使用率过高"
            description: "节点 {{ $labels.instance }} CPU 使用率超过 80%，当前值: {{ $value }}%"

        - alert: CriticalCPUUsage
          expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 95
          for: 2m
          labels:
            severity: critical
            team: ops
          annotations:
            summary: "节点 {{ $labels.instance }} CPU 使用率严重过高"
            description: "节点 {{ $labels.instance }} CPU 使用率超过 95%，当前值: {{ $value }}%"

        - alert: HighMemoryUsage
          expr: |
            (
              node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes
            ) / node_memory_MemTotal_bytes * 100 > 85
          for: 5m
          labels:
            severity: warning
            team: ops
          annotations:
            summary: "节点 {{ $labels.instance }} 内存使用率过高"
            description: "节点 {{ $labels.instance }} 内存使用率超过 85%，当前值: {{ $value }}%"

        - alert: CriticalMemoryUsage
          expr: |
            (
              node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes
            ) / node_memory_MemTotal_bytes * 100 > 95
          for: 2m
          labels:
            severity: critical
            team: ops
          annotations:
            summary: "节点 {{ $labels.instance }} 内存使用率严重过高"
            description: "节点 {{ $labels.instance }} 内存使用率超过 95%，当前值: {{ $value }}%"

        - alert: HighDiskUsage
          expr: |
            (
              node_filesystem_size_bytes{mountpoint="/"} - node_filesystem_avail_bytes{mountpoint="/"}
            ) / node_filesystem_size_bytes{mountpoint="/"} * 100 > 80
          for: 5m
          labels:
            severity: warning
            team: ops
          annotations:
            summary: "节点 {{ $labels.instance }} 磁盘使用率过高"
            description: "节点 {{ $labels.instance }} 根分区使用率超过 80%，当前值: {{ $value }}%"

        - alert: CriticalDiskUsage
          expr: |
            (
              node_filesystem_size_bytes{mountpoint="/"} - node_filesystem_avail_bytes{mountpoint="/"}
            ) / node_filesystem_size_bytes{mountpoint="/"} * 100 > 90
          for: 2m
          labels:
            severity: critical
            team: ops
          annotations:
            summary: "节点 {{ $labels.instance }} 磁盘使用率严重过高"
            description: "节点 {{ $labels.instance }} 根分区使用率超过 90%，当前值: {{ $value }}%"

        - alert: DiskWillFillIn4Hours
          expr: |
            predict_linear(
              node_filesystem_avail_bytes{mountpoint="/"}[1h], 4 * 3600
            ) < 0
          for: 5m
          labels:
            severity: warning
            team: ops
          annotations:
            summary: "节点 {{ $labels.instance }} 磁盘将在 4 小时内写满"
            description: "根据当前写入速度，节点 {{ $labels.instance }} 根分区将在 4 小时内写满"

        - alert: HighLoadAverage
          expr: node_load1 / count by(instance) (node_cpu_seconds_total{mode="idle"}) > 2
          for: 5m
          labels:
            severity: warning
            team: ops
          annotations:
            summary: "节点 {{ $labels.instance }} 负载过高"
            description: "节点 {{ $labels.instance }} 1 分钟负载平均值超过 CPU 核心数的 2 倍"

        - alert: HighSwapUsage
          expr: |
            (
              node_memory_SwapTotal_bytes - node_memory_SwapFree_bytes
            ) / node_memory_SwapTotal_bytes * 100 > 80
          for: 5m
          labels:
            severity: warning
            team: ops
          annotations:
            summary: "节点 {{ $labels.instance }} Swap 使用率过高"
            description: "节点 {{ $labels.instance }} Swap 使用率超过 80%"

    # ============================================
    # 网络告警
    # ============================================
    - name: node.network
      interval: 30s
      rules:
        - alert: NetworkReceiveErrors
          expr: rate(node_network_receive_errs_total[5m]) / rate(node_network_receive_packets_total[5m]) > 0.01
          for: 5m
          labels:
            severity: warning
            team: ops
          annotations:
            summary: "节点 {{ $labels.instance }} 网卡 {{ $labels.device }} 接收错误率过高"
            description: "接收错误率超过 1%"

        - alert: NetworkTransmitErrors
          expr: rate(node_network_transmit_errs_total[5m]) / rate(node_network_transmit_packets_total[5m]) > 0.01
          for: 5m
          labels:
            severity: warning
            team: ops
          annotations:
            summary: "节点 {{ $labels.instance }} 网卡 {{ $labels.device }} 发送错误率过高"
            description: "发送错误率超过 1%"

    # ============================================
    # 文件描述符告警
    # ============================================
    - name: node.fd
      interval: 30s
      rules:
        - alert: FileDescriptorUsageHigh
          expr: node_filefd_allocated / node_filefd_maximum * 100 > 80
          for: 5m
          labels:
            severity: warning
            team: ops
          annotations:
            summary: "节点 {{ $labels.instance }} 文件描述符使用率过高"
            description: "文件描述符使用率超过 80%"

        - alert: FileDescriptorUsageCritical
          expr: node_filefd_allocated / node_filefd_maximum * 100 > 95
          for: 2m
          labels:
            severity: critical
            team: ops
          annotations:
            summary: "节点 {{ $labels.instance }} 文件描述符使用率严重过高"
            description: "文件描述符使用率超过 95%"
```

### 7.3 Kubernetes 集群告警

```
# rules/k8s-alerts.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: k8s-alerts
  namespace: monitoring
  labels:
    prometheus: k8s
    role: alert-rules
spec:
  groups:
    # ============================================
    # K8s 控制平面告警
    # ============================================
    - name: k8s.control-plane
      interval: 30s
      rules:
        - alert: KubeAPIServerDown
          expr: up{job="kube-apiserver"} == 0
          for: 5m
          labels:
            severity: critical
            team: k8s
          annotations:
            summary: "Kube API Server 宕机"
            description: "Kube API Server {{ $labels.instance }} 已宕机超过 5 分钟"

        - alert: KubeControllerManagerDown
          expr: up{job="kube-controller-manager"} == 0
          for: 5m
          labels:
            severity: critical
            team: k8s
          annotations:
            summary: "Kube Controller Manager 宕机"
            description: "Kube Controller Manager {{ $labels.instance }} 已宕机超过 5 分钟"

        - alert: KubeSchedulerDown
          expr: up{job="kube-scheduler"} == 0
          for: 5m
          labels:
            severity: critical
            team: k8s
          annotations:
            summary: "Kube Scheduler 宕机"
            description: "Kube Scheduler {{ $labels.instance }} 已宕机超过 5 分钟"

        - alert: KubeEtcdDown
          expr: up{job="kube-etcd"} == 0
          for: 5m
          labels:
            severity: critical
            team: k8s
          annotations:
            summary: "ETCD 宕机"
            description: "ETCD {{ $labels.instance }} 已宕机超过 5 分钟"

        - alert: KubeAPIErrorBudgetBurn
          expr: |
            sum(rate(apiserver_request_total{job="kube-apiserver",code=~"5.."}[5m]))
            /
            sum(rate(apiserver_request_total{job="kube-apiserver"}[5m])) > 0.01
          for: 5m
          labels:
            severity: warning
            team: k8s
          annotations:
            summary: "Kube API Server 错误率过高"
            description: "API Server 5xx 错误率超过 1%"

        - alert: KubeAPIHighLatency
          expr: |
            histogram_quantile(0.99,
              sum(rate(apiserver_request_duration_seconds_bucket{job="kube-apiserver"}[5m])) by (le, verb)
            ) > 1
          for: 5m
          labels:
            severity: warning
            team: k8s
          annotations:
            summary: "Kube API Server 延迟过高"
            description: "API Server P99 延迟超过 1 秒"

    # ============================================
    # K8s 节点告警
    # ============================================
    - name: k8s.nodes
      interval: 30s
      rules:
        - alert: KubeNodeNotReady
          expr: kube_node_status_condition{condition="Ready",status="true"} == 0
          for: 15m
          labels:
            severity: critical
            team: k8s
          annotations:
            summary: "K8s 节点 {{ $labels.node }} 未就绪"
            description: "节点 {{ $labels.node }} 未就绪状态超过 15 分钟"

        - alert: KubeNodeUnreachable
          expr: kube_node_spec_taint{key="node.kubernetes.io/unreachable"} == 1
          for: 5m
          labels:
            severity: critical
            team: k8s
          annotations:
            summary: "K8s 节点 {{ $labels.node }} 不可达"
            description: "节点 {{ $labels.node }} 被标记为不可达"

    # ============================================
    # K8s Pod 告警
    # ============================================
    - name: k8s.pods
      interval: 30s
      rules:
        - alert: KubePodCrashLooping
          expr: rate(kube_pod_container_status_restarts_total[15m]) > 0
          for: 5m
          labels:
            severity: warning
            team: k8s
          annotations:
            summary: "Pod {{ $labels.namespace }}/{{ $labels.pod }} 处于 CrashLoopBackOff"
            description: "Pod 在 15 分钟内存在重启"

        - alert: KubePodNotReady
          expr: |
            sum by(namespace, pod) (
              kube_pod_status_phase{phase=~"Pending|Unknown|Failed"}
            ) > 0
          for: 15m
          labels:
            severity: warning
            team: k8s
          annotations:
            summary: "Pod {{ $labels.namespace }}/{{ $labels.pod }} 未就绪"
            description: "Pod 处于非 Running 状态超过 15 分钟"

        - alert: KubeContainerWaiting
          expr: kube_pod_container_status_waiting_reason{reason!="ContainerCreating"} == 1
          for: 1h
          labels:
            severity: warning
            team: k8s
          annotations:
            summary: "容器 {{ $labels.container }} 处于等待状态"
            description: "容器处于 {{ $labels.reason }} 状态超过 1 小时"

        - alert: KubeDaemonSetNotScheduled
          expr: |
            kube_daemonset_status_desired_number_scheduled
            - kube_daemonset_status_current_number_scheduled > 0
          for: 10m
          labels:
            severity: warning
            team: k8s
          annotations:
            summary: "DaemonSet {{ $labels.namespace }}/{{ $labels.daemonset }} 有 Pod 未调度"
            description: "部分 Pod 未被调度到节点"

        - alert: KubeDeploymentReplicasMismatch
          expr: |
            kube_deployment_spec_replicas
            != kube_deployment_status_replicas_available
          for: 15m
          labels:
            severity: warning
            team: k8s
          annotations:
            summary: "Deployment {{ $labels.namespace }}/{{ $labels.deployment }} 副本数不匹配"
            description: "期望副本数与实际可用副本数不一致"

        - alert: KubeStatefulSetReplicasMismatch
          expr: |
            kube_statefulset_status_replicas_ready
            != kube_statefulset_status_replicas
          for: 15m
          labels:
            severity: warning
            team: k8s
          annotations:
            summary: "StatefulSet {{ $labels.namespace }}/{{ $labels.statefulset }} 副本数不匹配"
            description: "期望副本数与就绪副本数不一致"

        - alert: KubeHpaMaxedOut
          expr: kube_horizontalpodautoscaler_status_current_replicas >= kube_horizontalpodautoscaler_spec_max_replicas
          for: 15m
          labels:
            severity: warning
            team: k8s
          annotations:
            summary: "HPA {{ $labels.namespace }}/{{ $labels.horizontalpodautoscaler }} 已达到最大副本数"
            description: "HPA 已达到最大副本数限制，可能需要扩容"

        - alert: KubeJobFailed
          expr: kube_job_status_failed{job_name!~".*-cronjob-.*"} == 1
          for: 0m
          labels:
            severity: warning
            team: k8s
          annotations:
            summary: "Job {{ $labels.namespace }}/{{ $labels.job_name }} 失败"
            description: "Job 执行失败"

        - alert: KubeCronJobRunning
          expr: time() - kube_cronjob_next_schedule_time > 3600
          for: 0m
          labels:
            severity: warning
            team: k8s
          annotations:
            summary: "CronJob {{ $labels.namespace }}/{{ $labels.cronjob }} 可能卡住"
            description: "CronJob 超过 1 小时未执行"

    # ============================================
    # K8s 资源配额告警
    # ============================================
    - name: k8s.resources
      interval: 30s
      rules:
        - alert: KubeQuotaExceeded
          expr: |
            kube_resourcequota{resource="requests.cpu",type="used"}
            / ignoring(type)
            kube_resourcequota{resource="requests.cpu",type="hard"} > 0.85
          for: 15m
          labels:
            severity: warning
            team: k8s
          annotations:
            summary: "命名空间 {{ $labels.namespace }} CPU 配额即将用完"
            description: "CPU 配额使用率超过 85%"

        - alert: KubePersistentVolumeFillingUp
          expr: |
            kubelet_volume_stats_available_bytes
            / kubelet_volume_stats_capacity_bytes < 0.15
          for: 1m
          labels:
            severity: warning
            team: k8s
          annotations:
            summary: "PV {{ $labels.persistentvolumeclaim }} 空间不足"
            description: "PV 可用空间小于 15%"

        - alert: KubePersistentVolumeFullInFourDays
          expr: |
            predict_linear(
              kubelet_volume_stats_available_bytes[6h], 4 * 24 * 3600
            ) < 0
          for: 1h
          labels:
            severity: warning
            team: k8s
          annotations:
            summary: "PV {{ $labels.persistentvolumeclaim }} 将在 4 天内写满"
            description: "根据当前写入速度，PV 将在 4 天内写满"
```

### 7.4 应用与业务告警

```
# rules/application-alerts.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: application-alerts
  namespace: monitoring
  labels:
    prometheus: k8s
    role: alert-rules
spec:
  groups:
    # ============================================
    # HTTP 应用告警
    # ============================================
    - name: application.http
      interval: 30s
      rules:
        - alert: HighErrorRate
          expr: |
            sum(rate(http_requests_total{status=~"5.."}[5m]))
            /
            sum(rate(http_requests_total[5m])) > 0.05
          for: 5m
          labels:
            severity: critical
            team: dev
          annotations:
            summary: "应用 {{ $labels.job }} 错误率过高"
            description: "5xx 错误率超过 5%，当前值: {{ $value }}%"

        - alert: HighLatency
          expr: |
            histogram_quantile(0.95,
              sum(rate(http_request_duration_seconds_bucket[5m])) by (le, job)
            ) > 0.5
          for: 5m
          labels:
            severity: warning
            team: dev
          annotations:
            summary: "应用 {{ $labels.job }} P95 延迟过高"
            description: "P95 延迟超过 500ms，当前值: {{ $value }}s"

        - alert: HighLatencyCritical
          expr: |
            histogram_quantile(0.99,
              sum(rate(http_request_duration_seconds_bucket[5m])) by (le, job)
            ) > 1
          for: 5m
          labels:
            severity: critical
            team: dev
          annotations:
            summary: "应用 {{ $labels.job }} P99 延迟严重过高"
            description: "P99 延迟超过 1s，当前值: {{ $value }}s"

        - alert: NoTraffic
          expr: sum(rate(http_requests_total[5m])) by (job) == 0
          for: 5m
          labels:
            severity: warning
            team: dev
          annotations:
            summary: "应用 {{ $labels.job }} 无流量"
            description: "应用在过去 5 分钟内无请求"

    # ============================================
    # JVM 应用告警
    # ============================================
    - name: application.jvm
      interval: 30s
      rules:
        - alert: JvmHeapUsageHigh
          expr: |
            jvm_memory_used_bytes{area="heap"}
            / jvm_memory_max_bytes{area="heap"} * 100 > 80
          for: 5m
          labels:
            severity: warning
            team: dev
          annotations:
            summary: "应用 {{ $labels.job }} JVM 堆内存使用率过高"
            description: "堆内存使用率超过 80%，当前值: {{ $value }}%"

        - alert: JvmHeapUsageCritical
          expr: |
            jvm_memory_used_bytes{area="heap"}
            / jvm_memory_max_bytes{area="heap"} * 100 > 95
          for: 2m
          labels:
            severity: critical
            team: dev
          annotations:
            summary: "应用 {{ $labels.job }} JVM 堆内存使用率严重过高"
            description: "堆内存使用率超过 95%，当前值: {{ $value }}%"

        - alert: JvmGcPauseHigh
          expr: |
            increase(jvm_gc_pause_seconds_sum[5m])
            / increase(jvm_gc_pause_seconds_count[5m]) > 0.5
          for: 5m
          labels:
            severity: warning
            team: dev
          annotations:
            summary: "应用 {{ $labels.job }} GC 停顿时间过长"
            description: "平均 GC 停顿时间超过 500ms"

        - alert: JvmThreadCountHigh
          expr: jvm_threads_live_threads > 500
          for: 5m
          labels:
            severity: warning
            team: dev
          annotations:
            summary: "应用 {{ $labels.job }} 线程数过高"
            description: "活动线程数超过 500，当前值: {{ $value }}"

    # ============================================
    # 数据库告警
    # ============================================
    - name: application.database
      interval: 30s
      rules:
        - alert: MysqlConnectionsHigh
          expr: mysql_global_status_threads_connected / mysql_global_variables_max_connections * 100 > 80
          for: 5m
          labels:
            severity: warning
            team: dba
          annotations:
            summary: "MySQL 连接数使用率过高"
            description: "连接数使用率超过 80%，当前值: {{ $value }}%"

        - alert: MysqlSlowQueries
          expr: rate(mysql_global_status_slow_queries[5m]) > 1
          for: 5m
          labels:
            severity: warning
            team: dba
          annotations:
            summary: "MySQL 慢查询过多"
            description: "慢查询率超过 1/s，当前值: {{ $value }}/s"

        - alert: RedisMemoryHigh
          expr: redis_memory_used_bytes / redis_memory_max_bytes * 100 > 80
          for: 5m
          labels:
            severity: warning
            team: dba
          annotations:
            summary: "Redis 内存使用率过高"
            description: "内存使用率超过 80%，当前值: {{ $value }}%"

        - alert: RedisRejectedConnections
          expr: rate(redis_connections_rejected_total[5m]) > 0
          for: 5m
          labels:
            severity: critical
            team: dba
          annotations:
            summary: "Redis 拒绝连接"
            description: "存在被拒绝的连接请求"

    # ============================================
    # 消息队列告警
    # ============================================
    - name: application.messaging
      interval: 30s
      rules:
        - alert: KafkaConsumerLagHigh
          expr: kafka_consumer_group_lag > 1000
          for: 5m
          labels:
            severity: warning
            team: dev
          annotations:
            summary: "Kafka 消费者组 {{ $labels.group }} 积压过高"
            description: "消费延迟超过 1000 条消息"

        - alert: RabbitMQQueueDepthHigh
          expr: rabbitmq_queue_messages > 1000
          for: 5m
          labels:
            severity: warning
            team: dev
          annotations:
            summary: "RabbitMQ 队列 {{ $labels.queue }} 深度过高"
            description: "队列消息数超过 1000"

        - alert: RabbitMQNodeMemoryHigh
          expr: rabbitmq_node_mem_used / rabbitmq_node_mem_limit * 100 > 80
          for: 5m
          labels:
            severity: warning
            team: dev
          annotations:
            summary: "RabbitMQ 节点内存使用率过高"
            description: "内存使用率超过 80%"
```

### 7.5 Prometheus 自身告警

```
# rules/prometheus-alerts.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: prometheus-alerts
  namespace: monitoring
  labels:
    prometheus: k8s
    role: alert-rules
spec:
  groups:
    - name: prometheus.service
      interval: 30s
      rules:
        - alert: PrometheusTargetDown
          expr: up == 0
          for: 5m
          labels:
            severity: warning
            team: ops
          annotations:
            summary: "Prometheus 目标 {{ $labels.job }} 不可达"
            description: "目标 {{ $labels.instance }} 已宕机超过 5 分钟"

        - alert: PrometheusConfigurationReloadFailure
          expr: prometheus_config_last_reload_successful != 1
          for: 0m
          labels:
            severity: critical
            team: ops
          annotations:
            summary: "Prometheus 配置重载失败"
            description: "Prometheus 配置重载失败，请检查配置"

        - alert: PrometheusNotConnectedToAlertmanagers
          expr: prometheus_notifications_alertmanagers_discovered < 1
          for: 5m
          labels:
            severity: critical
            team: ops
          annotations:
            summary: "Prometheus 未连接到 AlertManager"
            description: "Prometheus 无法连接到任何 AlertManager 实例"

    - name: prometheus.performance
      interval: 30s
      rules:
        - alert: PrometheusRuleEvaluationFailures
          expr: rate(prometheus_rule_evaluation_failures_total[5m]) > 0
          for: 5m
          labels:
            severity: warning
            team: ops
          annotations:
            summary: "Prometheus 规则评估失败"
            description: "存在规则评估失败的情况"

        - alert: PrometheusRuleEvaluationSlow
          expr: |
            prometheus_rule_group_last_duration_seconds
            / prometheus_rule_group_interval_seconds > 0.5
          for: 5m
          labels:
            severity: warning
            team: ops
          annotations:
            summary: "Prometheus 规则评估缓慢"
            description: "规则评估时间超过间隔的 50%"

        - alert: PrometheusTSDBWALCorruptions
          expr: tsdb_wal_corruptions_total > 0
          for: 0m
          labels:
            severity: critical
            team: ops
          annotations:
            summary: "Prometheus TSDB WAL 损坏"
            description: "检测到 WAL 文件损坏"

        - alert: PrometheusNotIngestingSamples
          expr: rate(prometheus_tsdb_head_samples_appended_total[5m]) <= 0
          for: 10m
          labels:
            severity: critical
            team: ops
          annotations:
            summary: "Prometheus 未写入样本"
            description: "过去 10 分钟未写入任何样本"

        - alert: PrometheusQueryErrors
          expr: |
            rate(prometheus_http_requests_total{handler="/api/v1/query",code=~"5.."}[5m])
            /
            rate(prometheus_http_requests_total{handler="/api/v1/query"}[5m]) > 0.05
          for: 5m
          labels:
            severity: warning
            team: ops
          annotations:
            summary: "Prometheus 查询错误率过高"
            description: "查询 API 5xx 错误率超过 5%"

    - name: prometheus.storage
      interval: 30s
      rules:
        - alert: PrometheusStorageRunningOut
          expr: |
            (
              prometheus_tsdb_retention_limit_bytes
              - prometheus_tsdb_storage_blocks_bytes
            ) / prometheus_tsdb_retention_limit_bytes < 0.1
          for: 5m
          labels:
            severity: warning
            team: ops
          annotations:
            summary: "Prometheus 存储空间不足"
            description: "存储空间剩余不足 10%"
```

### 7.6 应用告警规则

```
# 应用所有告警规则
kubectl apply -f rules/node-alerts.yaml
kubectl apply -f rules/k8s-alerts.yaml
kubectl apply -f rules/application-alerts.yaml
kubectl apply -f rules/prometheus-alerts.yaml

# 查看告警规则
kubectl get prometheusrules -n monitoring

# 验证规则是否被 Prometheus 加载
# 访问 Prometheus UI -> Status -> Rules
```

---

## 八、ServiceMonitor 服务监控配置

### 8.1 ServiceMonitor 概述

`ServiceMonitor` 是 Prometheus Operator 引入的 CRD，用于声明式地定义服务发现规则，自动发现并监控 Kubernetes Service。

### 8.2 基础 ServiceMonitor 模板

```
# servicemonitor-template.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: <app-name>
  namespace: monitoring
  labels:
    app: <app-name>
    release: kube-prometheus-stack
spec:
  # 选择要监控的 Service
  selector:
    matchLabels:
      app: <app-name>

  # 命名空间选择器
  namespaceSelector:
    matchNames:
      - <app-namespace>
    # 或者监控所有命名空间
    # any: true

  # 端点配置
  endpoints:
    - port: metrics          # Service 中定义的端口名称
      path: /metrics         # 指标端点路径
      interval: 30s          # 抓取间隔
      scrapeTimeout: 10s     # 抓取超时
      honorLabels: true      # 保留原始标签
      honorTimestamps: true  # 保留原始时间戳

      # 标签配置
      relabelings:
        - sourceLabels: [__meta_kubernetes_pod_node_name]
          targetLabel: node
          action: replace
        - sourceLabels: [__meta_kubernetes_namespace]
          targetLabel: namespace
          action: replace

      # 指标过滤
      metricRelabelings:
        - sourceLabels: [__name__]
          regex: 'go_.*'
          action: drop
```

### 8.3 常见应用监控配置

#### Nginx Ingress Controller

```
# servicemonitors/nginx-ingress.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: nginx-ingress
  namespace: monitoring
  labels:
    app: nginx-ingress
    release: kube-prometheus-stack
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: ingress-nginx
      app.kubernetes.io/component: controller
  namespaceSelector:
    matchNames:
      - ingress-nginx
  endpoints:
    - port: metrics
      path: /metrics
      interval: 30s
      scrapeTimeout: 10s
      relabelings:
        - sourceLabels: [__meta_kubernetes_pod_node_name]
          targetLabel: node
        - sourceLabels: [__meta_kubernetes_pod_name]
          targetLabel: pod
```

#### MySQL Exporter

```
# servicemonitors/mysql-exporter.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: mysql-exporter
  namespace: monitoring
  labels:
    app: mysql-exporter
    release: kube-prometheus-stack
spec:
  selector:
    matchLabels:
      app: mysql-exporter
  namespaceSelector:
    matchNames:
      - database
  endpoints:
    - port: metrics
      path: /metrics
      interval: 30s
      scrapeTimeout: 10s
      relabelings:
        - sourceLabels: [__meta_kubernetes_pod_node_name]
          targetLabel: node
        - sourceLabels: [__meta_kubernetes_pod_name]
          targetLabel: instance
      metricRelabelings:
        - sourceLabels: [__name__]
          regex: '(mysql_global_status_.*|mysql_up|mysql_global_variables_.*)'
          action: keep
---
# MySQL Exporter Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mysql-exporter
  namespace: database
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mysql-exporter
  template:
    metadata:
      labels:
        app: mysql-exporter
    spec:
      containers:
        - name: mysql-exporter
          image: prom/mysqld-exporter:v0.15.1
          env:
            - name: DATA_SOURCE_NAME
              value: "user:password@(mysql:3306)/"
          ports:
            - name: metrics
              containerPort: 9104
---
apiVersion: v1
kind: Service
metadata:
  name: mysql-exporter
  namespace: database
  labels:
    app: mysql-exporter
spec:
  selector:
    app: mysql-exporter
  ports:
    - name: metrics
      port: 9104
      targetPort: 9104
```

#### Redis Exporter

```
# servicemonitors/redis-exporter.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: redis-exporter
  namespace: monitoring
  labels:
    app: redis-exporter
    release: kube-prometheus-stack
spec:
  selector:
    matchLabels:
      app: redis-exporter
  namespaceSelector:
    matchNames:
      - database
  endpoints:
    - port: metrics
      path: /metrics
      interval: 30s
      scrapeTimeout: 10s
---
# Redis Exporter Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis-exporter
  namespace: database
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis-exporter
  template:
    metadata:
      labels:
        app: redis-exporter
    spec:
      containers:
        - name: redis-exporter
          image: oliver006/redis_exporter:v1.55.0
          env:
            - name: REDIS_ADDR
              value: "redis:6379"
            - name: REDIS_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: redis-secret
                  key: password
          ports:
            - name: metrics
              containerPort: 9121
---
apiVersion: v1
kind: Service
metadata:
  name: redis-exporter
  namespace: database
  labels:
    app: redis-exporter
spec:
  selector:
    app: redis-exporter
  ports:
    - name: metrics
      port: 9121
      targetPort: 9121
```

#### Kafka Exporter

```
# servicemonitors/kafka-exporter.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: kafka-exporter
  namespace: monitoring
  labels:
    app: kafka-exporter
    release: kube-prometheus-stack
spec:
  selector:
    matchLabels:
      app: kafka-exporter
  namespaceSelector:
    matchNames:
      - messaging
  endpoints:
    - port: metrics
      path: /metrics
      interval: 30s
---
# Kafka Exporter Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kafka-exporter
  namespace: messaging
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kafka-exporter
  template:
    metadata:
      labels:
        app: kafka-exporter
    spec:
      containers:
        - name: kafka-exporter
          image: danielqsj/kafka-exporter:v1.7.0
          args:
            - --kafka.server=kafka:9092
          ports:
            - name: metrics
              containerPort: 9308
---
apiVersion: v1
kind: Service
metadata:
  name: kafka-exporter
  namespace: messaging
  labels:
    app: kafka-exporter
spec:
  selector:
    app: kafka-exporter
  ports:
    - name: metrics
      port: 9308
      targetPort: 9308
```

#### Elasticsearch Exporter

```
# servicemonitors/elasticsearch-exporter.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: elasticsearch-exporter
  namespace: monitoring
  labels:
    app: elasticsearch-exporter
    release: kube-prometheus-stack
spec:
  selector:
    matchLabels:
      app: elasticsearch-exporter
  namespaceSelector:
    matchNames:
      - logging
  endpoints:
    - port: metrics
      path: /metrics
      interval: 30s
---
# Elasticsearch Exporter Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: elasticsearch-exporter
  namespace: logging
spec:
  replicas: 1
  selector:
    matchLabels:
      app: elasticsearch-exporter
  template:
    metadata:
      labels:
        app: elasticsearch-exporter
    spec:
      containers:
        - name: elasticsearch-exporter
          image: quay.io/prometheuscommunity/elasticsearch-exporter:v1.7.0
          args:
            - --es.uri=http://elasticsearch:9200
            - --es.all
            - --es.indices
            - --es.cluster_settings
          ports:
            - name: metrics
              containerPort: 9114
---
apiVersion: v1
kind: Service
metadata:
  name: elasticsearch-exporter
  namespace: logging
  labels:
    app: elasticsearch-exporter
spec:
  selector:
    app: elasticsearch-exporter
  ports:
    - name: metrics
      port: 9114
      targetPort: 9114
```

#### PostgreSQL Exporter

```
# servicemonitors/postgres-exporter.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: postgres-exporter
  namespace: monitoring
  labels:
    app: postgres-exporter
    release: kube-prometheus-stack
spec:
  selector:
    matchLabels:
      app: postgres-exporter
  namespaceSelector:
    matchNames:
      - database
  endpoints:
    - port: metrics
      path: /metrics
      interval: 30s
---
# PostgreSQL Exporter Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres-exporter
  namespace: database
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres-exporter
  template:
    metadata:
      labels:
        app: postgres-exporter
    spec:
      containers:
        - name: postgres-exporter
          image: quay.io/prometheuscommunity/postgres-exporter:v0.15.0
          env:
            - name: DATA_SOURCE_NAME
              value: "postgresql://user:password@postgres:5432/postgres?sslmode=disable"
          ports:
            - name: metrics
              containerPort: 9187
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-exporter
  namespace: database
  labels:
    app: postgres-exporter
spec:
  selector:
    app: postgres-exporter
  ports:
    - name: metrics
      port: 9187
      targetPort: 9187
```

### 8.4 应用自定义监控

```
# servicemonitors/custom-app.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: my-application
  namespace: monitoring
  labels:
    app: my-application
    release: kube-prometheus-stack
spec:
  selector:
    matchLabels:
      app: my-application
  namespaceSelector:
    matchNames:
      - production
  endpoints:
    - port: http-metrics
      path: /actuator/prometheus
      interval: 30s
      scrapeTimeout: 10s
      honorLabels: true

      # 基本认证
      basicAuth:
        username:
          name: my-app-metrics-secret
          key: username
        password:
          name: my-app-metrics-secret
          key: password

      # TLS 配置
      tlsConfig:
        insecureSkipVerify: true

      # 标签重写
      relabelings:
        - sourceLabels: [__meta_kubernetes_pod_node_name]
          targetLabel: node
        - sourceLabels: [__meta_kubernetes_namespace]
          targetLabel: namespace
        - sourceLabels: [__meta_kubernetes_pod_name]
          targetLabel: pod
        - regex: __meta_kubernetes_pod_label_(.+)
          action: labelmap

      # 指标过滤
      metricRelabelings:
        - sourceLabels: [__name__]
          regex: 'go_.*'
          action: drop
        - sourceLabels: [__name__]
          regex: 'process_.*'
          action: drop
        - sourceLabels: [__name__]
          regex: '(app_|http_|jvm_|system_).*'
          action: keep
---
apiVersion: v1
kind: Secret
metadata:
  name: my-app-metrics-secret
  namespace: monitoring
type: Opaque
stringData:
  username: admin
  password: secretpassword
```

### 8.5 PodMonitor 配置

对于没有 Service 的 Pod（如 DaemonSet），使用 PodMonitor：

```
# podmonitors/fluentd.yaml
apiVersion: monitoring.coreos.com/v1
kind: PodMonitor
metadata:
  name: fluentd
  namespace: monitoring
  labels:
    app: fluentd
    release: kube-prometheus-stack
spec:
  selector:
    matchLabels:
      app: fluentd
  namespaceSelector:
    matchNames:
      - logging
  podMetricsEndpoints:
    - port: metrics
      path: /metrics
      interval: 30s
      scrapeTimeout: 10s
      relabelings:
        - sourceLabels: [__meta_kubernetes_pod_node_name]
          targetLabel: node
        - sourceLabels: [__meta_kubernetes_namespace]
          targetLabel: namespace
```

### 8.6 应用监控配置

```
# 创建目录
mkdir -p servicemonitors podmonitors

# 应用所有 ServiceMonitor
kubectl apply -f servicemonitors/

# 应用所有 PodMonitor
kubectl apply -f podmonitors/

# 查看已配置的监控
kubectl get servicemonitors -n monitoring
kubectl get podmonitors -n monitoring

# 验证 Prometheus 是否发现目标
# 访问 Prometheus UI -> Status -> Targets
```

---

## 九、AlertManager 告警路由配置

### 9.1 AlertManager 配置概述

AlertManager 使用 YAML 配置文件定义告警路由、接收器和抑制规则。配置通过 Secret 挂载到 AlertManager Pod。

### 9.2 完整配置示例

```
# alertmanager-config.yaml
apiVersion: v1
kind: Secret
metadata:
  name: alertmanager-kube-prometheus-stack-alertmanager
  namespace: monitoring
type: Opaque
stringData:
  alertmanager.yaml: |
    global:
      # SMTP 配置（邮件通知）
      smtp_smarthost: 'smtp.example.com:587'
      smtp_from: 'alertmanager@example.com'
      smtp_auth_username: 'alertmanager@example.com'
      smtp_auth_password: 'your-email-password'
      smtp_require_tls: true
      
      # Slack API
      slack_api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
      
      # 告警超时
      resolve_timeout: 5m
      
      # 消息模板
      templates:
        - '/etc/alertmanager/templates/*.tmpl'
    
    # 抑制规则：高级别告警抑制低级别相关告警
    inhibit_rules:
      # 节点宕机抑制该节点上的其他告警
      - source_match:
          severity: 'critical'
          alertname: 'NodeDown'
        target_match_re:
          severity: 'warning|info'
        equal:
          - instance
      
      # 严重磁盘使用抑制警告级别磁盘告警
      - source_match:
          severity: 'critical'
          alertname: 'CriticalDiskUsage'
        target_match:
          severity: 'warning'
          alertname: 'HighDiskUsage'
        equal:
          - instance
      
      # K8s 命名空间级别抑制
      - source_match:
          severity: 'critical'
        target_match_re:
          severity: 'warning|info'
        equal:
          - namespace
          - pod
    
    # 路由树
    route:
      # 根路由配置
      group_by: ['alertname', 'cluster', 'service', 'severity']
      group_wait: 30s
      group_interval: 5m
      repeat_interval: 4h
      receiver: 'default-receiver'
      
      # 子路由
      routes:
        # 严重级别告警立即发送
        - match:
            severity: critical
          receiver: 'critical-receiver'
          group_wait: 0s
          group_interval: 1m
          repeat_interval: 30m
          continue: true
        
        # 警告级别告警
        - match:
            severity: warning
          receiver: 'warning-receiver'
          group_wait: 1m
          group_interval: 5m
          repeat_interval: 2h
          continue: true
        
        # 按团队路由
        - match_re:
            team: ops|operations
          receiver: 'ops-team'
          routes:
            - match:
                severity: critical
              receiver: 'ops-critical'
        
        - match_re:
            team: dev|development
          receiver: 'dev-team'
          routes:
            - match:
                severity: critical
              receiver: 'dev-critical'
        
        - match:
            team: dba
          receiver: 'dba-team'
        
        # 按服务路由
        - match_re:
            service: mysql|postgres|redis|elasticsearch
          receiver: 'database-alerts'
          group_by: ['alertname', 'service', 'instance']
        
        - match_re:
            service: kafka|rabbitmq
          receiver: 'messaging-alerts'
        
        # K8s 特定路由
        - match:
            job: kube-state-metrics
          receiver: 'k8s-alerts'
          group_by: ['alertname', 'namespace', 'pod']
        
        # 黑盒探测告警
        - match:
            job: blackbox-exporter
          receiver: 'blackbox-alerts'
          group_by: ['alertname', 'instance']
        
        # 静默测试告警
        - match:
            test: 'true'
          receiver: 'null'
    
    # 接收器配置
    receivers:
      # 默认接收器
      - name: 'default-receiver'
        email_configs:
          - to: 'ops@example.com'
            send_resolved: true
            headers:
              Subject: '[Prometheus] {{ .GroupLabels.alertname }}'
            html: |
              {{ range .Alerts }}
              <h3>{{ .Annotations.summary }}</h3>
              <p><strong>描述:</strong> {{ .Annotations.description }}</p>
              <p><strong>严重级别:</strong> {{ .Labels.severity }}</p>
              <p><strong>开始时间:</strong> {{ .StartsAt }}</p>
              <hr>
              {{ end }}
      
      # 严重告警接收器
      - name: 'critical-receiver'
        email_configs:
          - to: 'oncall@example.com'
            send_resolved: true
        slack_configs:
          - channel: '#critical-alerts'
            send_resolved: true
            title: ':fire: Critical Alert'
            text: |
              {{ range .Alerts }}
              *{{ .Annotations.summary }}*
              {{ .Annotations.description }}
              {{ end }}
        pagerduty_configs:
          - service_key: 'your-pagerduty-key'
            severity: critical
            description: '{{ .GroupLabels.alertname }}'
      
      # 警告告警接收器
      - name: 'warning-receiver'
        email_configs:
          - to: 'ops@example.com'
            send_resolved: true
        slack_configs:
          - channel: '#alerts'
            send_resolved: true
            title: ':warning: Warning'
            text: |
              {{ range .Alerts }}
              *{{ .Annotations.summary }}*
              {{ .Annotations.description }}
              {{ end }}
      
      # Ops 团队
      - name: 'ops-team'
        slack_configs:
          - channel: '#ops-alerts'
            send_resolved: true
      
      - name: 'ops-critical'
        slack_configs:
          - channel: '#ops-critical'
            send_resolved: true
        pagerduty_configs:
          - service_key: 'ops-pagerduty-key'
      
      # Dev 团队
      - name: 'dev-team'
        slack_configs:
          - channel: '#dev-alerts'
            send_resolved: true
      
      - name: 'dev-critical'
        slack_configs:
          - channel: '#dev-critical'
            send_resolved: true
        pagerduty_configs:
          - service_key: 'dev-pagerduty-key'
      
      # DBA 团队
      - name: 'dba-team'
        email_configs:
          - to: 'dba@example.com'
            send_resolved: true
        slack_configs:
          - channel: '#dba-alerts'
            send_resolved: true
      
      # 数据库告警
      - name: 'database-alerts'
        email_configs:
          - to: 'dba@example.com'
            send_resolved: true
        slack_configs:
          - channel: '#database-alerts'
            send_resolved: true
            title: ':database: Database Alert'
      
      # 消息队列告警
      - name: 'messaging-alerts'
        slack_configs:
          - channel: '#messaging-alerts'
            send_resolved: true
      
      # K8s 告警
      - name: 'k8s-alerts'
        slack_configs:
          - channel: '#k8s-alerts'
            send_resolved: true
            title: ':k8s: Kubernetes Alert'
            text: |
              {{ range .Alerts }}
              Namespace: {{ .Labels.namespace }}
              Pod: {{ .Labels.pod }}
              {{ .Annotations.summary }}
              {{ end }}
      
      # 黑盒告警
      - name: 'blackbox-alerts'
        slack_configs:
          - channel: '#uptime-alerts'
            send_resolved: true
            title: ':globe_with_meridians: Endpoint Alert'
      
      # 空接收器（用于静默）
      - name: 'null'

---
# 应用配置
kubectl apply -f alertmanager-config.yaml

# 重载 AlertManager 配置
kubectl exec -it alertmanager-main-0 -n monitoring -c alertmanager -- kill -HUP 1
```

### 9.3 企业微信告警配置

```
# 在 receivers 中添加
- name: 'wechat-alerts'
  wechat_configs:
    - corp_id: 'your-corp-id'
      to_party: '2'  # 部门ID
      agent_id: '1000002'
      api_secret: 'your-api-secret'
      send_resolved: true
      message: |
        {{ range .Alerts }}
        【{{ .Status | toUpper }}】{{ .Annotations.summary }}
        
        描述: {{ .Annotations.description }}
        严重级别: {{ .Labels.severity }}
        时间: {{ .StartsAt.Format "2006-01-02 15:04:05" }}
        {{ end }}
```

### 9.4 钉钉告警配置

```
# 使用 webhook 方式
- name: 'dingtalk-alerts'
  webhook_configs:
    - url: 'http://dingtalk-webhook.monitoring.svc.cluster.local:8060/dingtalk/webhook1/send'
      send_resolved: true
```
```
# dingtalk-webhook.yaml - DingTalk Webhook 适配器
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dingtalk-webhook
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: dingtalk-webhook
  template:
    metadata:
      labels:
        app: dingtalk-webhook
    spec:
      containers:
        - name: dingtalk-webhook
          image: timonwong/prometheus-webhook-dingtalk:v2.1.0
          args:
            - --web.listen-address=:8060
            - --web.enable-ui
            - --config.file=/etc/dingtalk/config.yml
          ports:
            - containerPort: 8060
          volumeMounts:
            - name: config
              mountPath: /etc/dingtalk
          resources:
            limits:
              cpu: 200m
              memory: 256Mi
            requests:
              cpu: 50m
              memory: 64Mi
      volumes:
        - name: config
          configMap:
            name: dingtalk-config
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: dingtalk-config
  namespace: monitoring
data:
  config.yml: |
    targets:
      webhook1:
        url: https://oapi.dingtalk.com/robot/send?access_token=your-token
        secret: your-secret
        message:
          title: '{{ template "dingtalk.default.title" . }}'
          text: '{{ template "dingtalk.default.content" . }}'
---
apiVersion: v1
kind: Service
metadata:
  name: dingtalk-webhook
  namespace: monitoring
spec:
  selector:
    app: dingtalk-webhook
  ports:
    - port: 8060
      targetPort: 8060
```

### 9.5 告警模板自定义

```
# alertmanager-templates.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: alertmanager-templates
  namespace: monitoring
data:
  default.tmpl: |
    {{ define "slack.default.title" }}{{ .GroupLabels.alertname }}{{ end }}
    
    {{ define "slack.default.text" }}
    {{ range .Alerts }}
    *Alert:* {{ .Annotations.summary }}
    *Description:* {{ .Annotations.description }}
    *Severity:* {{ .Labels.severity }}
    *Started:* {{ .StartsAt.Format "2006-01-02 15:04:05" }}
    {{ end }}
    {{ end }}
    
    {{ define "email.default.subject" }}[{{ .Status | toUpper }}] {{ .GroupLabels.alertname }}{{ end }}
    
    {{ define "email.default.html" }}
    <html>
    <body>
    <h2>{{ .GroupLabels.alertname }}</h2>
    <p>Status: {{ .Status }}</p>
    <hr>
    {{ range .Alerts }}
    <h3>{{ .Annotations.summary }}</h3>
    <p><strong>Description:</strong> {{ .Annotations.description }}</p>
    <p><strong>Labels:</strong></p>
    <ul>
    {{ range .Labels.SortedPairs }}
      <li>{{ .Name }}: {{ .Value }}</li>
    {{ end }}
    </ul>
    <p><strong>Started:</strong> {{ .StartsAt.Format "2006-01-02 15:04:05" }}</p>
    <hr>
    {{ end }}
    </body>
    </html>
    {{ end }}
    
    {{ define "dingtalk.default.title" }}
    [{{ .Status | toUpper }}] {{ .GroupLabels.alertname }}
    {{ end }}
    
    {{ define "dingtalk.default.content" }}
    {{ range .Alerts }}
    【{{ .Annotations.summary }}】
    描述: {{ .Annotations.description }}
    严重级别: {{ .Labels.severity }}
    时间: {{ .StartsAt.Format "2006-01-02 15:04:05" }}
    {{ end }}
    {{ end }}
```

---

## 十、参数优化与性能调优

### 10.1 Prometheus 性能优化

#### 资源规划建议

| 指标数量 | 抓取目标数 | CPU | 内存 | 磁盘 | 抓取间隔 |
| --- | --- | --- | --- | --- | --- |
| < 100K | < 100 | 2核 | 8GB | 100GB | 30s |
| 100K-500K | 100-500 | 4核 | 16GB | 500GB | 30s |
| 500K-1M | 500-1000 | 8核 | 32GB | 1TB | 15s |
| \> 1M | \> 1000 | 16核+ | 64GB+ | 2TB+ | 15s |

#### TSDB 优化参数

```
# values-production.yaml 中的 prometheusSpec 部分
prometheusSpec:
  # 数据保留策略
  retention: 30d                    # 保留时间
  retentionSize: 450GB              # 保留大小（优先触发）
  
  # TSDB 配置
  tsdb:
    # 乱序时间窗口（允许写入过去的数据）
    outOfOrderTimeWindow: 0s
  
  # 额外参数
  additionalArgs:
    # 最小/最大块持续时间
    - name: storage.tsdb.min-block-duration
      value: 2h
    - name: storage.tsdb.max-block-duration
      value: 2h
    
    # WAL 压缩
    - name: storage.tsdb.wal-compression
      value: "true"
    
    # 内存映射的最大块数
    - name: storage.tsdb.max-block-chunk-segment-size
      value: "512MB"
    
    # 查询优化
    - name: query.max-samples
      value: "50000000"
    - name: query.max-concurrency
      value: "20"
    - name: query.timeout
      value: "2m"
    
    # 抓取优化
    - name: storage.remote.flush-deadline
      value: "1m"
    - name: rules.alert.for-outage-tolerance
      value: "1h"
    - name: rules.alert.for-grace-period
      value: "10m"
    - name: rules.alert.resend-delay
      value: "1m"
```

#### 抓取配置优化

```
prometheusSpec:
  # 全局抓取间隔
  scrapeInterval: 30s
  evaluationInterval: 30s
  
  # 抓取超时
  scrapeTimeout: 10s
  
  # 外部标签
  externalLabels:
    cluster: production
    replica: '{{.ExternalURL}}'
  
  # 启用特性
  enableFeatures:
    - exemplar-storage          # 示例存储
    - memory-snapshot-on-shutdown  # 关机时内存快照
    - new-service-discovery-manager  # 新服务发现管理器
    - remote-write-receiver     # 远程写入接收器
```

### 10.2 AlertManager 优化

```
alertmanager:
  alertmanagerSpec:
    # 资源限制
    resources:
      limits:
        cpu: 1000m
        memory: 1Gi
      requests:
        cpu: 100m
        memory: 256Mi
    
    # 高可用配置
    replicas: 3
    
    # 集群配置
    clusterAdvertiseAddress: $(POD_IP)
    
    # 额外参数
    additionalArgs:
      # 集群 gossip 间隔
      - name: cluster.gossip-interval
        value: "200ms"
      # 推送超时
      - name: cluster.pushpull-interval
        value: "1m0s"
      # 静默限制
      - name: silences.max-silences
        value: "10000"
      - name: silences.max-silence-size-bytes
        value: "10485760"  # 10MB
```

### 10.3 Grafana 优化

```
grafana:
  resources:
    limits:
      cpu: 1000m
      memory: 1Gi
    requests:
      cpu: 250m
      memory: 512Mi
  
  # 环境变量优化
  env:
    # 数据库连接池
    GF_DATABASE_MAX_OPEN_CONN: "100"
    GF_DATABASE_MAX_IDLE_CONN: "100"
    
    # 会话配置
    GF_SESSION_PROVIDER: "memory"
    GF_SESSION_PROVIDER_CONFIG: ""
    
    # 缓存配置
    GF_CACHE_ENABLED: "true"
    
    # 渲染超时
    GF_RENDERING_CALLBACK_URL: "http://grafana:3000/"
    GF_RENDERING_SERVER_URL: "http://grafana-image-renderer:8081/render"
    
    # 日志级别
    GF_LOG_LEVEL: "warn"
    
    # 匿名访问禁用
    GF_AUTH_ANONYMOUS_ENABLED: "false"
    
    # CSRF 保护
    GF_SECURITY_CSRF_ADDITIONAL_HEADERS: "X-Forwarded-Host"
    GF_SECURITY_CSRF_TRUSTED_ORIGINS: "https://grafana.example.com"
    
    # 安全头
    GF_SECURITY_STRICT_TRANSPORT_SECURITY: "true"
    GF_SECURITY_STRICT_TRANSPORT_SECURITY_MAX_AGE_SECONDS: "86400"
    GF_SECURITY_X_CONTENT_TYPE_OPTIONS: "true"
    GF_SECURITY_X_XSS_PROTECTION: "true"
```

### 10.4 查询优化

#### PromQL 最佳实践

```
# 1. 使用 rate() 而不是 increase() 计算速率
# 推荐
rate(http_requests_total[5m])

# 不推荐
increase(http_requests_total[5m]) / 300

# 2. 使用 irate() 用于快速变化的计数器
irate(http_requests_total[5m])

# 3. 避免高基数查询
# 不推荐 - 可能导致内存问题
topk(10000, http_requests_total)

# 推荐 - 限制结果数量
topk(10, sum by(handler) (rate(http_requests_total[5m])))

# 4. 使用 recording rules 预计算复杂查询
# rules/recording-rules.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: recording-rules
  namespace: monitoring
spec:
  groups:
    - name: http_requests
      interval: 30s
      rules:
        - record: job:http_requests_total:rate5m
          expr: sum by(job) (rate(http_requests_total[5m]))
        
        - record: job:http_request_duration_seconds:p95
          expr: |
            histogram_quantile(0.95,
              sum by(job, le) (rate(http_request_duration_seconds_bucket[5m]))
            )
```

### 10.5 存储优化

#### NFS 挂载选项优化

```
# StorageClass 优化
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: nfs-optimized
provisioner: nfs.csi.k8s.io
parameters:
  server: <nfs-server-ip>
  share: /data/k8s/nfs
mountOptions:
  - nfsvers=4.1      # 使用 NFSv4.1
  - nconnect=16      # 多连接（Linux 5.3+）
  - hard             # 硬挂载
  - intr             # 允许中断
  - rsize=1048576    # 读块大小 1MB
  - wsize=1048576    # 写块大小 1MB
  - noatime          # 不更新访问时间
  - nodiratime       # 不更新目录访问时间
reclaimPolicy: Retain
volumeBindingMode: WaitForFirstConsumer
```

#### 本地缓存方案

```
# 使用本地 SSD 作为 WAL 目录
prometheusSpec:
  storageSpec:
    volumeClaimTemplate:
      spec:
        storageClassName: nfs-client
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 500Gi
  
  # 额外挂载本地 SSD 用于 WAL
  volumes:
    - name: wal-volume
      emptyDir:
        medium: Memory  # 或使用 hostPath 挂载本地 SSD
  
  volumeMounts:
    - name: wal-volume
      mountPath: /prometheus/wal
```

### 10.6 网络优化

```
# 启用 HTTP/2 和压缩
prometheusSpec:
  additionalArgs:
    - name: web.enable-http2
      value: "true"
    - name: web.enable-gzip
      value: "true"
    - name: web.max-connections
      value: "512"
    - name: web.read-timeout
      value: "5m"
    - name: web.write-timeout
      value: "5m"
```

---

## 十一、高可用与扩展方案

### 11.1 Prometheus 高可用架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     Load Balancer (Ingress)                     │
└─────────────────────────────┬───────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ Prometheus-0  │    │ Prometheus-1  │    │ Prometheus-2  │
│ (Shard 0)     │    │ (Shard 1)     │    │ (Shard 2)     │
└───────┬───────┘    └───────┬───────┘    └───────┬───────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Thanos Query   │
                    │  (全局查询视图)  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   Thanos Store  │
                    │   (长期存储)     │
                    └─────────────────┘
```

### 11.2 Thanos 集成配置

```
# values-production.yaml - Thanos 配置
thanosSidecar:
  enabled: true
  image: quay.io/thanos/thanos:v0.35.0
  objectStorageConfig:
    type: s3
    config:
      bucket: "thanos-bucket"
      endpoint: "s3.amazonaws.com"
      access_key: "your-access-key"
      secret_key: "your-secret-key"
      insecure: false
      signature_version2: false
      put_user_metadata: {}
      http_config:
        idle_conn_timeout: 90s
        response_header_timeout: 2m
        insecure_skip_verify: false
  resources:
    limits:
      cpu: 1000m
      memory: 1Gi
    requests:
      cpu: 100m
      memory: 256Mi
```

### 11.3 联邦集群配置

```
# 全局 Prometheus 配置
apiVersion: monitoring.coreos.com/v1
kind: Prometheus
metadata:
  name: global
  namespace: monitoring
spec:
  replicas: 2
  
  # 联邦抓取配置
  additionalScrapeConfigs:
    - job_name: 'federate'
      scrape_interval: 30s
      honor_labels: true
      metrics_path: '/federate'
      params:
        'match[]':
          - '{job="prometheus"}'
          - '{__name__=~"job:.*"}'
          - '{__name__=~"node_.*"}'
      static_configs:
        - targets:
            - 'prometheus-dc1:9090'
            - 'prometheus-dc2:9090'
            - 'prometheus-dc3:9090'
```

### 11.4 AlertManager 高可用

```
alertmanager:
  alertmanagerSpec:
    replicas: 3
    
    # 集群配置
    clusterAdvertiseAddress: $(POD_IP)
    
    # 亲和性配置 - 分散到不同节点
    affinity:
      podAntiAffinity:
        requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
                - key: app.kubernetes.io/name
                  operator: In
                  values:
                    - alertmanager
            topologyKey: kubernetes.io/hostname
    
    # 容忍配置
    tolerations:
      - key: "monitoring"
        operator: "Equal"
        value: "true"
        effect: "NoSchedule"
```

### 11.5 多集群监控

```
# cluster-monitoring.yaml
apiVersion: monitoring.coreos.com/v1
kind: Prometheus
metadata:
  name: cluster-prometheus
  namespace: monitoring
  labels:
    cluster: cluster-1
spec:
  externalLabels:
    cluster: cluster-1
    region: beijing
    datacenter: dc1
  
  # 远程写入到中心 Prometheus
  remoteWrite:
    - url: "http://central-prometheus:9090/api/v1/write"
      queueConfig:
        maxSamplesPerSend: 1000
        maxShards: 200
        capacity: 2500
      writeRelabelConfigs:
        - sourceLabels: [__name__]
          regex: 'up|node_.*|container_.*|kube_.*'
          action: keep
```

---

## 十二、故障排查与常见问题

### 12.1 常用排查命令

```
# 查看 Prometheus Pod 状态
kubectl get pods -n monitoring -l app.kubernetes.io/name=prometheus

# 查看 Prometheus 日志
kubectl logs -f prometheus-k8s-0 -n monitoring -c prometheus

# 进入 Prometheus 容器
kubectl exec -it prometheus-k8s-0 -n monitoring -c prometheus -- sh

# 查看配置
kubectl get secret prometheus-k8s -n monitoring -o jsonpath='{.data.prometheus\.yaml\.gz}' | base64 -d | gunzip

# 查看 targets
kubectl port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090 -n monitoring
# 访问 http://localhost:9090/targets

# 查看 AlertManager 状态
kubectl logs -f alertmanager-main-0 -n monitoring -c alertmanager

# 查看 Grafana 日志
kubectl logs -f deployment/kube-prometheus-stack-grafana -n monitoring

# 检查 PVC 状态
kubectl get pvc -n monitoring
kubectl describe pvc <pvc-name> -n monitoring

# 检查 PV
kubectl get pv
kubectl describe pv <pv-name>

# 检查 StorageClass
kubectl get storageclass
kubectl describe storageclass <sc-name>
```

### 12.2 常见问题解决

#### 问题1：Prometheus 无法发现目标

```
# 症状：Targets 页面显示为空或 down

# 排查步骤：
# 1. 检查 ServiceMonitor 标签
kubectl get servicemonitor -n monitoring --show-labels

# 2. 检查 Prometheus 的 serviceMonitorSelector
kubectl get prometheus k8s -n monitoring -o yaml | grep -A 5 serviceMonitorSelector

# 3. 确保 ServiceMonitor 标签匹配
# 如果 Prometheus 配置了 serviceMonitorSelector: {app: monitoring}
# 则 ServiceMonitor 必须有 label: app: monitoring

# 4. 检查 Service 标签
kubectl get svc -n <namespace> --show-labels

# 5. 检查 endpoints
kubectl get endpoints -n <namespace>
```

#### 问题2：告警不触发

```
# 症状：告警规则已配置但不触发

# 排查步骤：
# 1. 检查告警规则是否加载
kubectl port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090 -n monitoring
# 访问 http://localhost:9090/rules

# 2. 测试告警表达式
# 在 Prometheus UI 的 Graph 页面执行告警表达式

# 3. 检查告警状态
# 访问 http://localhost:9090/alerts

# 4. 检查 AlertManager 连接
# 访问 http://localhost:9090/status
# 查看 Alertmanager 部分
```

#### 问题3：NFS 挂载失败

```
# 症状：Pod 处于 Pending 状态，PVC 无法绑定

# 排查步骤：
# 1. 检查 NFS 服务器
showmount -e <nfs-server-ip>

# 2. 检查 NFS provisioner 日志
kubectl logs -f deployment/nfs-provisioner -n kube-system

# 3. 检查 StorageClass
kubectl describe storageclass nfs-client

# 4. 检查 PVC 事件
kubectl describe pvc <pvc-name> -n monitoring

# 5. 手动测试挂载
kubectl run test-nfs --rm -it --image=busybox -- /bin/sh
# 在容器中：
mount -t nfs <nfs-server-ip>:/data/k8s/nfs /mnt
```

#### 问题4：Prometheus OOMKilled

```
# 症状：Prometheus Pod 被 OOMKilled

# 解决方案：
# 1. 增加内存限制
kubectl patch prometheus k8s -n monitoring --type merge -p '
{
  "spec": {
    "resources": {
      "limits": {
        "memory": "32Gi"
      }
    }
  }
}'

# 2. 减少抓取目标
# 调整 ServiceMonitor 的 namespaceSelector

# 3. 增加抓取间隔
# 修改 scrapeInterval 为 60s 或更长

# 4. 减少保留时间
# 修改 retention 为 15d
```

#### 问题5：镜像拉取失败

```
# 症状：ImagePullBackOff

# 解决方案：
# 1. 检查镜像地址
kubectl describe pod <pod-name> -n monitoring

# 2. 使用国内镜像源
# 修改 values.yaml 中的镜像地址：
# prometheus:
#   prometheusSpec:
#     image:
#       repository: registry.aliyuncs.com/prometheus/prometheus

# 3. 配置镜像拉取密钥
# kubectl create secret docker-registry regcred \
#   --docker-server=your-registry.com \
#   --docker-username=username \
#   --docker-password=password
```

### 12.3 性能调优检查清单

```
# 1. 检查 Prometheus 内存使用
kubectl top pod -n monitoring -l app.kubernetes.io/name=prometheus

# 2. 检查 TSDB 状态
kubectl exec -it prometheus-k8s-0 -n monitoring -c prometheus -- wget -qO- http://localhost:9090/api/v1/status/tsdb

# 3. 检查目标数量
kubectl exec -it prometheus-k8s-0 -n monitoring -c prometheus -- wget -qO- http://localhost:9090/api/v1/targets | jq '.data.activeTargets | length'

# 4. 检查序列数量
# 在 Prometheus UI 执行：prometheus_tsdb_head_series

# 5. 检查查询性能
# 在 Prometheus UI 执行慢查询并分析
```

### 12.4 备份与恢复

```
# 备份 Prometheus 数据
# 方法1：使用 velero
velero backup create prometheus-backup --include-namespaces monitoring

# 方法2：手动备份
kubectl exec -it prometheus-k8s-0 -n monitoring -c prometheus -- tar czf /tmp/prometheus-backup.tar.gz /prometheus
kubectl cp monitoring/prometheus-k8s-0:/tmp/prometheus-backup.tar.gz ./prometheus-backup.tar.gz

# 方法3：使用 NFS 快照（如果存储支持）

# 恢复数据
# 1. 停止 Prometheus
kubectl scale sts prometheus-k8s --replicas=0 -n monitoring

# 2. 恢复数据到 PVC
# 3. 启动 Prometheus
kubectl scale sts prometheus-k8s --replicas=2 -n monitoring
```

### 12.5 监控检查清单

```
# 生产环境部署检查清单

# [ ] 1. 存储配置
#   - [ ] NFS 服务器可用
#   - [ ] StorageClass 配置正确
#   - [ ] PVC 绑定成功
#   - [ ] 数据持久化验证

# [ ] 2. 高可用配置
#   - [ ] Prometheus 多副本
#   - [ ] AlertManager 多副本
#   - [ ] 反亲和性配置
#   - [ ] 容忍污点配置

# [ ] 3. 告警配置
#   - [ ] 告警规则已加载
#   - [ ] AlertManager 路由配置
#   - [ ] 通知渠道测试
#   - [ ] 抑制规则验证

# [ ] 4. 安全配置
#   - [ ] Ingress TLS 配置
#   - [ ] Grafana 认证配置
#   - [ ] 网络策略配置
#   - [ ] RBAC 配置

# [ ] 5. 性能优化
#   - [ ] 资源限制配置
#   - [ ] TSDB 参数优化
#   - [ ] 抓取间隔优化
#   - [ ] 查询性能优化

# [ ] 6. 备份配置
#   - [ ] 数据备份策略
#   - [ ] 配置备份
#   - [ ] 恢复测试

# [ ] 7. 文档与运维
#   - [ ] 运维手册
#   - [ ] 告警响应流程
#   - [ ] 升级流程
#   - [ ] 故障处理流程
```

---

## 附录

### A. 常用 PromQL 查询

```
# 节点 CPU 使用率
100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# 节点内存使用率
(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100

# 节点磁盘使用率
(node_filesystem_size_bytes{mountpoint="/"} - node_filesystem_avail_bytes{mountpoint="/"}) / node_filesystem_size_bytes{mountpoint="/"} * 100

# Pod CPU 使用率
rate(container_cpu_usage_seconds_total{container!=""}[5m])

# Pod 内存使用
container_memory_usage_bytes{container!=""}

# HTTP 请求速率
rate(http_requests_total[5m])

# HTTP 错误率
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])

# P95 延迟
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))

# K8s Pod 重启次数
increase(kube_pod_container_status_restarts_total[1h])

# 预测磁盘将在 4 小时内写满
predict_linear(node_filesystem_avail_bytes{mountpoint="/"}[1h], 4 * 3600) < 0
```

### B. 参考资源

- • Prometheus 官方文档 <sup>[13]</sup>
- • AlertManager 配置 <sup>[14]</sup>
- • kube-prometheus-stack GitHub <sup>[15]</sup>
- • Prometheus Operator <sup>[16]</sup>
- • Grafana Dashboards <sup>[17]</sup>

### C. 版本信息

| 组件 | 版本 |
| --- | --- |
| Kubernetes | 1.35+ |
| kube-prometheus-stack | 76.0.0+ |
| Prometheus | v2.55.0+ |
| AlertManager | v0.27.0+ |
| Grafana | 11.1.0+ |
| Node Exporter | v1.8.2+ |
| kube-state-metrics | v2.13.0+ |

**微信扫一扫赞赏作者**

k8s · 目录

继续滑动看下一个

院长技术

向上滑动看下一个