---
title: "K8s CGroup v2 深度解析：资源隔离原理、迁移实战与生产避坑指南"
source: "https://mp.weixin.qq.com/s/nlMP4Q6bDGJol9RogCybEA"
created: 2026-05-13
tags:
  - kubernetes
  - cgroup
  - linux
---

> 当 RHEL 9 默认启用 cgroup v2、Ubuntu 22.04 全面切换，越来越多的生产集群开始强制面对 cgroup v2。但你真的搞清楚 cgroup v2 和 v1 的区别了吗？升级之后为什么 CPU throttling 变了？内存 OOM 行为为什么不一样了？本文从内核原理到 K8s 实战，带你彻底搞懂 cgroup v2。

---

## 一、行业背景：cgroup v2 时代正式到来

2026 年，Linux 容器资源隔离领域正在经历一场静默的革命。

**RHEL 9（2022）和 RHEL 10（2025）已强制默认使用 cgroup v2**，同时完全移除了 cgroup v1 的内核挂载点。Ubuntu 22.04 LTS 起默认也是 cgroup v2。Fedora 在 v43 版本中彻底移除 cgroup v1。

这意味着：如果你还在跑基于旧 OS 镜像的生产集群，迟早要面对 cgroup v1 → v2 的迁移问题。

Kubernetes 侧的支持也早已成熟：

- v1.18：Alpha 阶段首次引入
- v1.22：Beta 阶段
- **v1.25：正式 GA（稳定支持）**

而容器运行时方面，containerd ≥ 1.6、cri-o ≥ 1.25 均已完整支持 cgroup v2。

> 问题来了：升到 cgroup v2 之后，你的应用性能为什么可能突然变差了？内存限制为什么会更严格？CPU throttling 为什么行为改变了？

---

## 二、cgroup v1 的历史局限

cgroup（Control Groups）是 Linux 内核提供的资源隔离和限制机制，是容器技术的核心基础。

### 2.1 cgroup v1 架构问题

cgroup v1 于 2008 年合入内核 2.6.24，采用 **多层次（Multiple Hierarchies）** 设计：

```
/sys/fs/cgroup/
├── cpu/           # CPU 调度
├── cpuacct/       # CPU 统计
├── memory/        # 内存限制
├── blkio/         # 块 I/O
├── devices/       # 设备访问
├── net_cls/       # 网络类别
└── pids/          # 进程数限制
```

每个子系统（subsystem）都有独立的层次树，一个进程可以同时属于多个子系统的不同 cgroup，导致：

1. **配置不一致风险高**：同一个进程可能在 cpu/ 下属于 high-priority 组，在 memory/ 下却属于 best-effort 组
2. **跨子系统协调困难**：CPU 和内存无法做联动控制，比如"内存不足时降低 CPU 配额"
3. **线程级别的问题**：v1 中同一进程的不同线程可以属于不同的 cgroup，管理混乱
4. **写入接口不统一**：各子系统的文件接口设计风格不一致

### 2.2 v1 的 CPU throttling 问题

这是影响 Kubernetes 生产环境最广的问题之一。在 v1 中：

```
# cgroup v1 CPU 限制接口
/sys/fs/cgroup/cpu/<group>/cpu.cfs_quota_us   # 配额时间 (微秒)
/sys/fs/cgroup/cpu/<group>/cpu.cfs_period_us  # 周期时间 (微秒)
```

问题：周期（period）固定为 100ms，quota 在每个 100ms 的窗口内累积，导致：

- 应用突发使用 CPU 超过配额，立即被 throttle 100ms
- 即使 CPU 整体利用率很低，仍会被频繁 throttle
- 这就是著名的 **"CPU throttling 导致 P99 延迟飙升"** 问题

---

## 三、cgroup v2：统一层次树与增强控制

### 3.1 统一层次树设计

cgroup v2 最核心的改变是采用 **单一统一层次树（Unified Hierarchy）**：

```
/sys/fs/cgroup/                  # v2 根节点
├── cgroup.controllers           # 该层级可用的控制器
├── cgroup.subtree_control       # 该层级已启用的控制器
├── system.slice/
│   ├── kubelet.service/
│   └── containerd.service/
└── kubepods.slice/
    ├── besteffort.slice/        # BestEffort QoS Pod
    ├── burstable.slice/         # Burstable QoS Pod
    └── guaranteed.slice/        # Guaranteed QoS Pod
        └── pod<uid>/
            └── <container-id>/
                ├── cpu.max      # CPU 限制（替代 cpu.cfs_quota_us）
                ├── memory.max   # 内存硬限制
                ├── memory.high  # 内存软限制（新增！）
                └── io.max       # I/O 带宽限制
```

**关键特性**：

- 每个 cgroup 只有一个父节点，层次关系清晰
- 所有控制器统一作用于同一个 cgroup
- 叶节点才能挂载进程（internal process constraint）

### 3.2 CPU 控制改进

```
# cgroup v2 的 CPU 限制接口
cat /sys/fs/cgroup/kubepods.slice/kubepods-burstable.slice/pod.../cpu.max
# 输出：50000 100000
# 含义：每 100ms (100000μs) 内最多使用 50ms (50000μs)，即 0.5 CPU

# v2 新增：CPU 权重（替代 v1 的 cpu.shares）
cat /sys/fs/cgroup/kubepods.slice/cpu.weight
# 输出：100 （默认权重，范围 1-10000）
```

v2 的 CPU Burst 特性（内核 5.14+）：

```
# cpu.max.burst：允许突发累积的时间预算
echo "50000 100000" > cpu.max        # 0.5 CPU 配额
echo "25000" > cpu.max.burst         # 可累积最多额外 25ms 突发预算
```

这解决了 v1 的 throttling 问题：空闲时段积累的预算可在突发请求时使用，**P99 延迟可降低 30%-50%**。

### 3.3 内存控制新特性

v2 内存控制引入了 **双层限制** 机制：

```
# memory.max：硬限制，超过则 OOM Kill
echo "1073741824" > memory.max   # 1GiB 硬限制

# memory.high：软限制（v2 新增）
echo "858993459" > memory.high   # 800MiB 软限制
```

**memory.high 的工作原理**：

1. 进程内存超过 `memory.high` 时，内核会 **主动回收该 cgroup 的内存**（包括 PageCache）
2. 但不会立即 OOM Kill，而是通过 throttle（减速写内存）施压
3. 只有超过 `memory.max` 才触发 OOM Kill

对 Go 服务特别重要：Go runtime 会延迟归还内存给 OS，在 v1 下经常因为 `docker stats` 看到内存正常但实际触发 OOM。v2 的 `memory.high` 可以提前回收，大幅减少 OOM 误杀。

### 3.4 I/O 控制统一

v1 中有 `blkio.throttle.read_bps_device` 等分散接口，v2 统一为：

```
# io.max：设备级别的 I/O 带宽和 IOPS 限制
# 格式：MAJ:MIN rbps=X wbps=X riops=X wiops=X
echo "8:0 rbps=104857600 wbps=104857600" > io.max  # 100MB/s 读写限速

# io.weight：I/O 权重（1-10000）
echo "100" > io.weight

# io.stat：I/O 统计（实时）
cat io.stat
# 8:0 rbytes=1073741824 wbytes=536870912 rios=1024 wios=512 dbytes=0 dios=0
```

---

## 四、Kubernetes 中的 cgroup v2 实战

### 4.1 检查集群是否使用 cgroup v2

```bash
# 方法1：检查节点 cgroup 版本
ssh node-1 "stat -fc %T /sys/fs/cgroup"
# cgroup2fs  → cgroup v2
# tmpfs      → cgroup v1

# 方法2：通过 K8s 节点信息
kubectl get node node-1 -o jsonpath='{.status.nodeInfo.osImage}'

# 方法3：检查 kubelet 配置
ssh node-1 "cat /var/lib/kubelet/config.yaml | grep -i cgroup"
# cgroupDriver: systemd  （v2 推荐使用 systemd 驱动）
# cgroupVersion: v2
```

### 4.2 kubelet 配置迁移

```yaml
# /var/lib/kubelet/config.yaml
apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration

# 关键配置：使用 systemd cgroup 驱动（v2 必须）
cgroupDriver: systemd

# v1.25+ 新增字段：显式声明 cgroup 版本（可选，kubelet 会自动检测）
# cgroupsPerQOS: true  # 开启 QoS 级别的 cgroup 层次

# 内存管理器策略（v2 支持）
memoryManagerPolicy: Static
reservedMemory:
  - numaNode: 0
    limits:
      memory: "1Gi"
```

> **重要**：必须保证 kubelet 的 `cgroupDriver` 与容器运行时的 `cgroupDriver` 一致，否则 Pod 创建失败！

```toml
# containerd 配置（/etc/containerd/config.toml）
[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
  SystemdCgroup = true  # 必须为 true
```

### 4.3 Pod QoS 与 cgroup v2 层次映射

```
/sys/fs/cgroup/kubepods.slice/
├── kubepods-besteffort.slice/      # BestEffort QoS
│   └── kubepods-besteffort-pod<uid>.slice/
│       └── <container-id>/
├── kubepods-burstable.slice/       # Burstable QoS
│   └── kubepods-burstable-pod<uid>.slice/
│       └── <container-id>/
└── kubepods-guaranteed.slice/      # Guaranteed QoS（默认，未分类）
    └── kubepods-pod<uid>.slice/
        └── <container-id>/
```

查看某 Pod 的 cgroup 路径：

```bash
# 获取 Pod UID
POD_UID=$(kubectl get pod my-pod -o jsonpath='{.metadata.uid}')

# 查看 cgroup 信息
ls /sys/fs/cgroup/kubepods.slice/kubepods-burstable.slice/kubepods-burstable-pod${POD_UID}.slice/

# 查看 CPU 限制
cat /sys/fs/cgroup/kubepods.slice/.../cpu.max
# 200000 100000  → 2 CPU (limits.cpu: "2")

# 查看内存限制
cat /sys/fs/cgroup/kubepods.slice/.../memory.max
# 1073741824     → 1Gi (limits.memory: "1Gi")

# 查看内存软限制（requests.memory 对应）
cat /sys/fs/cgroup/kubepods.slice/.../memory.high
# 858993459      → 约 820Mi
```

### 4.4 Memory QoS 特性（v1.27 Beta）

Kubernetes v1.22 引入 MemoryQoS 特性门控，v1.27 升级为 Beta 并默认开启。其核心逻辑：

```
memory.min  = requests.memory   # 内存保障：不被回收的最低内存
memory.high = requests.memory * memoryThrottlingFactor  # 软限制（触发回收）
memory.max  = limits.memory     # 硬限制（OOM Kill）
```

默认 `memoryThrottlingFactor = 0.9`，可在 kubelet 配置中调整：

```yaml
# /var/lib/kubelet/config.yaml
memoryThrottlingFactor: 0.8  # 更激进的回收策略
```

**效果**：对于内存密集型应用（如 JVM、Go 服务），提前在 80% 内存时触发回收，大幅减少 OOM Kill 事件。

---

## 五、生产环境踩坑实录

### 坑1：升级 OS 后 Pod 无法创建

**症状**：集群升级 OS 到 RHEL 9 后，新节点上的 Pod 持续报错 `failed to create containerd task`

**根因**：containerd 配置仍为 `cgroupfs` 驱动，而 RHEL 9 默认 cgroup v2 + systemd

**修复**：

```bash
# 修改 containerd 配置
sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml

# 同步修改 kubelet 配置
sed -i 's/cgroupDriver: cgroupfs/cgroupDriver: systemd/' /var/lib/kubelet/config.yaml

# 重启服务
systemctl restart containerd kubelet
```

### 坑2：CPU throttling 统计数据失效

**症状**：升级到 cgroup v2 后，Prometheus 的 `container_cpu_cfs_throttled_seconds_total` 指标持续为 0

**根因**：cgroup v2 的 CPU throttle 统计接口变更，旧版 cAdvisor (< 0.45) 不支持读取 v2 格式

**修复**：

```bash
# 升级 cAdvisor 到 0.47+
# 或升级 metrics-server / kube-state-metrics

# v2 对应的新接口
cat /sys/fs/cgroup/kubepods.slice/.../cpu.stat
# usage_usec 12345678
# user_usec 11234567
# system_usec 1111111
# nr_periods 1234       # 总调度周期数
# nr_throttled 56       # 被 throttle 的周期数
# throttled_usec 567890 # throttle 总时长
```

### 坑3：内存 OOM 行为改变导致应用闪退

**症状**：应用设置了 `resources.limits.memory: 2Gi`，但在 cgroup v2 下，内存使用到 1.8Gi 时就被 OOM Kill

**根因**：MemoryQoS 特性默认开启，`memory.high = limits.memory * 0.9 = 1.8Gi`，高于此值时内核会强制 throttle，某些不能处理慢速内存分配的应用会直接 crash

**修复方案**：

```yaml
# 方案1：给 Pod 打上注解，禁用 MemoryQoS（慎用）
annotations:
  memory.alpha.kubernetes.io/qos: "disable"

# 方案2：调大 request/limit 比例
resources:
  requests:
    memory: "1.8Gi"  # 提高 requests 以提高 memory.high 阈值
  limits:
    memory: "2Gi"

# 方案3：kubelet 全局调整 throttling factor
# /var/lib/kubelet/config.yaml
memoryThrottlingFactor: 0.95  # 宽松一些
```

### 坑4：Java 应用 OOM 误杀

**症状**：JVM 应用内存使用明显低于 limits，但仍被 OOM Kill

**根因**：JVM G1GC 在 cgroup v2 下 `memory.min`（保障内存）的感知有 Bug，会预留过多内存

**修复**：

```bash
# JVM 启动参数显式配置内存
-XX:MaxRAMPercentage=75.0           # 使用容器内存的 75%
-XX:+UseContainerSupport             # 必须开启容器内存感知
-XX:+ExitOnOutOfMemoryError          # OOM 时主动退出（优雅退出比被 Kill 好）

# Java 17+ 推荐
-XX:+UseZGC                          # ZGC 对 cgroup v2 内存压力更友好
```

### 坑5：混合集群中 v1/v2 节点共存

**症状**：同一个集群中，部分节点是 cgroup v1（旧 OS），部分是 cgroup v2（新 OS），CPU 和内存行为不一致

**最佳实践**：

```yaml
# 使用 NodeSelector 或 NodeAffinity 隔离
# 给 cgroup v2 节点打标签
kubectl label node cgroupv2-node01 node.kubernetes.io/cgroup-version=v2

# Pod 亲和性配置
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
      - matchExpressions:
        - key: node.kubernetes.io/cgroup-version
          operator: In
          values:
          - v2
```

---

## 六、cgroup v2 监控与告警

### 6.1 Prometheus 指标对比

| 指标 | cgroup v1 | cgroup v2 |
| --- | --- | --- |
| CPU 使用 | `container_cpu_usage_seconds_total` | 同（cAdvisor 适配） |
| CPU throttle | `container_cpu_cfs_throttled_seconds_total` | 需 cAdvisor ≥ 0.45 |
| 内存使用 | `container_memory_usage_bytes` | 含 PageCache（需注意） |
| 内存工作集 | `container_memory_working_set_bytes` | 同（更准确） |
| 内存 soft limit | 无 | `container_memory_high_bytes` |
| I/O 读写 | `container_fs_*` | `container_blkio_*` 更新 |

### 6.2 推荐告警规则

```yaml
groups:
- name: cgroup-v2-alerts
  rules:
  # CPU 高 throttle 率
  - alert: ContainerCPUThrottlingHigh
    expr: |
      rate(container_cpu_cfs_throttled_seconds_total[5m])
        / rate(container_cpu_usage_seconds_total[5m]) > 0.5
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "容器 CPU throttle 率超过 50%"
      description: "Pod {{ $labels.pod }} CPU 被 throttle 超过 50%，可能导致高延迟，建议提高 limits.cpu"

  # 内存接近软限制（memory.high）
  - alert: ContainerMemoryNearHighLimit
    expr: |
      container_memory_working_set_bytes
        / container_spec_memory_limit_bytes > 0.85
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "容器内存超过限制的 85%"
      description: "Pod {{ $labels.pod }} 内存使用 {{ $value | humanizePercentage }}，即将触发内核内存回收"

  # OOM Kill 事件
  - alert: ContainerOOMKilled
    expr: kube_pod_container_status_last_terminated_reason{reason="OOMKilled"} == 1
    for: 0m
    labels:
      severity: critical
    annotations:
      summary: "容器被 OOM Kill"
      description: "Pod {{ $labels.pod }} 容器 {{ $labels.container }} 因内存不足被 Kill"
```

---

## 七、总结

cgroup v2 不是简单的版本升级，而是 Linux 资源隔离架构的根本性重构：

| 维度 | cgroup v1 | cgroup v2 |
| --- | --- | --- |
| 层次结构 | 多层次树（每个控制器独立） | 统一单层次树 |
| CPU 控制 | 固定 100ms 窗口，易 throttle | 支持 CPU Burst，P99 延迟更低 |
| 内存控制 | 仅硬限制 | 硬限制 + 软限制（high），减少 OOM |
| I/O 控制 | blkio 子系统（分散） | io 控制器（统一，更精确） |
| 线程控制 | 同进程线程可在不同 cgroup | 必须在同一 cgroup（更安全） |
| K8s 支持 | v1.25 前默认 | v1.25+ GA，v1.27 MemoryQoS Beta |

**生产迁移建议**：

1. 新建集群直接使用 cgroup v2 + systemd driver
2. 存量集群：先在非核心节点验证，用 NodeAffinity 隔离，逐步扩大
3. 重点关注 Go 和 JVM 应用的内存配置，适当调高 requests/limits 比例
4. 升级 cAdvisor 到 0.47+，确保 throttle 指标正常采集
5. 配置 MemoryQoS 相关告警，提前感知内存压力

cgroup v2 是云原生基础设施现代化的必经之路，越早迁移，越早享受更精准的资源隔离和更低的延迟抖动。
