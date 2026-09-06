---
title: emptyDir 监控与驱逐机制实战
tags:
  - kubernetes
  - kubernetes/storage
  - kubernetes/observability
aliases:
  - Pod emptyDir 驱逐
  - emptyDir 磁盘监控
  - Kubernetes 临时存储驱逐
date: 2026-09-06
sources:
  - "[[0raw/明明每个 Pod 都没写满，为什么还是被驱逐？emptyDir 监控与驱逐机制实战]]"
source_url: "https://mp.weixin.qq.com/s?__biz=MzY5NjMxMzAxMg==&mid=2247483781&idx=1&sn=f5bf7300b4faa51c98203381d59fe4fd&chksm=f46ff45ec3187d48bc06af292f2db03dff7365b165944b0bd02c2ea4be8e51c658981e678898&cur_album_id=4534870433564983299&scene=189#wechat_redirect"
---

# emptyDir 监控与驱逐机制实战

## 一句话点透原理

`emptyDir.sizeLimit` 约束的是单个卷，不会为节点预留磁盘，也不能代替 `ephemeral-storage` 的 request/limit。即使每个 Pod 都没有超过自己的 `sizeLimit`，所有 Pod 的 `emptyDir`、容器日志和可写层仍可能共同耗尽节点磁盘并触发 `DiskPressure`；此时 kubelet 按节点压力驱逐规则选择 Pod，被驱逐的不一定是 `emptyDir` 使用量最大的 Pod。

## emptyDir 是什么

`emptyDir` 是生命周期与 Pod 绑定的临时卷：

- Pod 被调度到节点后创建，Pod 被删除时清理。
- 容器崩溃或重启不会删除该卷，只要 Pod 仍然存在，数据就还在。
- 同一 Pod 内的主容器、Sidecar 和 Init Container 可以共享该卷。
- 默认使用节点本地磁盘；设置 `medium: Memory` 时使用 tmpfs，并按内存使用量计量。
- 数据没有持久性保证，不适合保存不可丢失的数据。

~~~yaml
apiVersion: v1
kind: Pod
metadata:
  name: emptydir-demo
spec:
  containers:
    - name: app
      image: busybox
      command: ["sh", "-c", "sleep 3600"]
      volumeMounts:
        - name: cache
          mountPath: /cache
    - name: sidecar
      image: busybox
      command: ["sh", "-c", "sleep 3600"]
      volumeMounts:
        - name: cache
          mountPath: /cache
  volumes:
    - name: cache
      emptyDir: {}
~~~

适合 `emptyDir` 的数据通常具有“生命周期短、可丢失、可重建、容量可控”的特点，例如：

- 图片、下载文件、依赖包和推理中间结果的短期缓存；
- 视频转码、批处理、AI 和 ETL 任务的中间文件；
- 主容器与 Sidecar 之间交换的文件；
- 可丢失的 `/tmp`、`/work`、`/cache` 工作目录；
- 小容量、低延迟的内存临时数据。

数据不能丢、需要跨 Pod 共享、需要跨节点迁移或需要长期保留时，应使用 PVC、对象存储、数据库或分布式文件系统。

## 为什么容器内 df 看不到 sizeLimit

下面的配置把卷上限设为 100 GiB：

~~~yaml
volumes:
  - name: cache
    emptyDir:
      sizeLimit: 100Gi
~~~

`sizeLimit` 不是独立块设备或独立文件系统的容量。磁盘型 `emptyDir` 仍是节点文件系统中的目录，所以在容器里对挂载点执行 `df -h`，通常看到的是底层节点文件系统容量，而不是 100 GiB。

kubelet 通过周期性目录扫描，或在支持的文件系统上通过项目配额统计本地临时存储使用量，再依据限制决定是否驱逐。项目配额用于更准确地统计，并不等同于由文件系统直接拒绝写入。

> [!warning] 计量有前提
> kubelet 只会在受支持的本地临时存储布局中正确计量。若把额外文件系统挂到 `/var/lib/kubelet`、`/var/log` 或容器运行时目录下，计量和限制可能失效。目录扫描也无法统计“文件已删除但进程仍保持打开”的占用；项目配额可以准确记录这种空间。

## 两类驱逐必须分开理解

### 单个卷或 Pod 超限

单个 `emptyDir` 超过 `sizeLimit` 时，违规对象明确，kubelet 可以将对应 Pod 标记为驱逐候选。事件中可能看到：

~~~text
Usage of EmptyDir volume "cache" exceeds the limit "100Gi"
~~~

本地临时存储还可以通过容器级 request/limit 管理：

~~~yaml
resources:
  requests:
    ephemeral-storage: 50Gi
  limits:
    ephemeral-storage: 100Gi
~~~

Pod 的本地临时存储使用量不只包含 `emptyDir`，还包括容器可写层、Pod 日志以及 Kubernetes 为 Pod 管理的部分文件。若容器可写层与日志超过容器限制，或 Pod 内所有容器和磁盘型 `emptyDir` 的总使用量超过 Pod 聚合限制，kubelet 也会触发驱逐。

### 节点磁盘压力

假设六个 Pod 的 `emptyDir.sizeLimit` 都是 100 GiB，实际各用了 80 GiB。每个 Pod 都没有越界，但总量已经达到 480 GiB，再加上镜像、日志、容器可写层、kubelet 和系统组件占用，节点仍可能触发：

~~~text
nodefs.available below eviction threshold
~~~

这时需要解决的是节点级资源不足，而不是某个卷违反配额。kubelet 会持续回收节点资源；若镜像和容器垃圾回收不足以恢复到安全阈值，就会驱逐 Pod，直到压力解除。

## 为什么不一定驱逐写得最多的 Pod

节点压力驱逐不是按“谁最接近 `emptyDir.sizeLimit`”排序。kubelet 依次考虑：

1. Pod 对紧缺资源的实际使用量是否超过 request；
2. Pod Priority；
3. 实际使用量相对于 request 的比例。

对于 `DiskPressure`，QoS Class 不直接决定驱逐顺序；QoS 只能在某些资源压力场景中帮助估计结果。没有声明 `ephemeral-storage.requests` 的 Pod，其 request 相当于 0，只要产生了可计量的本地临时存储使用，就属于超过 request。

因此，以下现象都是可能的：

- `emptyDir` 使用量较小但没有 request、Priority 较低的 Pod 先被驱逐；
- 使用量更大但 request 合理、Priority 更高的 Pod 暂时保留；
- 驱逐一个 Pod 后仍未恢复阈值，kubelet 继续驱逐其他 Pod；
- 控制器重新创建 Pod，而调度与容量治理没有改善，形成反复驱逐。

kubelet 的目标是让节点尽快回到安全状态，并不是寻找一个“最有责任”的 Pod。

## sizeLimit 与 ephemeral-storage 的分工

| 配置 | 粒度 | 主要作用 |
| --- | --- | --- |
| `emptyDir.sizeLimit` | 单个 `emptyDir` 卷 | 控制该卷的最大使用量 |
| `requests.ephemeral-storage` | 容器，调度时汇总到 Pod | 告诉调度器预计需要的本地临时存储 |
| `limits.ephemeral-storage` | 容器，kubelet 汇总与执行 | 限制容器/Pod 的本地临时存储使用 |
| kubelet eviction threshold | 节点文件系统 | 在 `nodefs`、`imagefs` 或 `containerfs` 压力下保护节点 |

推荐同时配置：

~~~yaml
apiVersion: v1
kind: Pod
metadata:
  name: emptydir-practice
spec:
  containers:
    - name: app
      image: busybox
      command: ["sh", "-c", "sleep 3600"]
      resources:
        requests:
          cpu: 500m
          memory: 512Mi
          ephemeral-storage: 50Gi
        limits:
          cpu: "1"
          memory: 1Gi
          ephemeral-storage: 100Gi
      volumeMounts:
        - name: cache
          mountPath: /cache
  volumes:
    - name: cache
      emptyDir:
        sizeLimit: 100Gi
~~~

> [!note] Memory 类型的差异
> `medium: Memory` 的 `emptyDir` 计入容器内存使用，而不是磁盘型 local ephemeral storage。其有效容量还会受到 Pod/容器内存限制和节点可用内存影响。

## 逐 Pod、逐卷监控方案

常见 Prometheus 采集栈通常缺少可直接用于告警的“逐 `emptyDir` 卷使用量 + sizeLimit”成对指标，因此可以补充一个自定义采集器，分为控制面元数据和节点目录用量两部分。

### 1. 采集 sizeLimit 元数据

通过 Kubernetes Informer 监听 Pod 的增删改，提取每个配置了 `sizeLimit` 的 `emptyDir`：

~~~text
emptydir_size_limit_bytes{
  namespace="default",
  pod="app-0",
  node="worker-1",
  pod_uid="a74bdf6a-bb18-48ab-9462-3c92c7eb1aff",
  volume="cache"
} 107374182400
~~~

关键关联字段是 `pod_uid` 和 `volume`。Pod 名称可能复用，不能只用 `namespace + pod` 关联历史目录。

### 2. 在每个节点采集卷目录使用量

以 DaemonSet 方式在每个节点扫描 kubelet 的 Pod 目录。默认路径形态为：

~~~text
/var/lib/kubelet/pods/<pod_uid>/volumes/kubernetes.io~empty-dir/<volume_name>
~~~

暴露指标：

~~~text
emptydir_used_bytes{
  node="worker-1",
  pod_uid="a74bdf6a-bb18-48ab-9462-3c92c7eb1aff",
  volume="cache"
} 75161927680
~~~

采集器需要只读挂载 kubelet Pod 目录，并控制扫描频率和并发，避免对包含大量小文件的节点造成明显 I/O 压力。若集群修改了 kubelet `rootDir`，路径也要同步调整。

### 3. 在 Prometheus 中关联并计算使用率

两个指标应同时按 `pod_uid` 和 `volume` 关联，避免一个 Pod 有多个 `emptyDir` 时产生错误匹配：

~~~promql
emptydir_used_bytes
/
on (pod_uid, volume)
group_left(namespace, pod, node)
emptydir_size_limit_bytes
~~~

可通过 recording rule 生成 `emptydir_usage_ratio`。

推荐标签：

| 标签 | 用途 |
| --- | --- |
| `namespace`、`pod` | 定位工作负载 |
| `node` | 关联节点磁盘压力 |
| `pod_uid` | 避免 Pod 重建后的名称复用 |
| `volume` | 区分同一 Pod 的多个 emptyDir |
| `used_bytes` | 当前占用 |
| `size_limit_bytes` | 配置上限 |
| `usage_ratio` | 占上限比例 |

### 4. emptyDir 告警建议

| 级别 | 条件 | 意图 |
| --- | --- | --- |
| warning | 使用率 > 70%，持续 10 分钟 | 提前发现增长趋势 |
| critical | 使用率 > 85%，持续 5 分钟 | 需要人工介入 |
| emergency | 使用率 > 95%，持续 1 分钟 | 很可能即将触发驱逐 |

阈值需要结合采集周期和业务写入速度调整。对于突发写入任务，仅按百分比告警可能来不及，还应增加单位时间增长量或预计耗尽时间告警。

## 节点级监控

Kubernetes 可能观察以下文件系统：

| 名称 | 含义 |
| --- | --- |
| `nodefs` | kubelet、日志和部分本地数据所在文件系统 |
| `imagefs` | 镜像与容器可写层所在的独立文件系统 |
| `containerfs` | 部分运行时中单独承载容器可写层的文件系统 |

需要先确认集群实际磁盘布局，再将指标的 `mountpoint` 与 kubelet eviction signal 对齐。至少监控：

- `node_filesystem_avail_bytes` 与 `node_filesystem_size_bytes`；
- `kube_node_status_condition{condition="DiskPressure",status="true"}`；
- Pod 状态或事件中的 `Evicted`；
- kubelet 驱逐事件；
- `emptyDir` 使用量排行及增长速度；
- 节点镜像、容器日志和可写层占用。

参考告警分层：

| 级别 | 条件 | 说明 |
| --- | --- | --- |
| warning | nodefs 使用率 > 75%，持续 10 分钟 | 提前清理或扩容 |
| critical | nodefs 使用率 > 85%，持续 5 分钟 | 接近驱逐风险 |
| emergency | nodefs 使用率 > 90% 或 `DiskPressure=True` | 可能已经开始驱逐 |
| critical | 发现 Evicted Pod | 业务已经受到影响 |

最有价值的观测链路是：

~~~text
单卷 emptyDir 使用率/增长率
→ Pod ephemeral-storage 接近 request/limit
→ nodefs/imagefs/containerfs 可用空间下降
→ DiskPressure
→ Pod Evicted
~~~

## 治理建议

### 应用层

- 给缓存设置容量上限和淘汰策略。
- 定期清理临时文件，控制日志滚动。
- 中间结果完成后及时上传对象存储。
- 避免在 `emptyDir` 中长期保存大文件。
- 对“删除但仍保持打开”的文件检查进程文件描述符。

### Pod 与命名空间

- 同时配置 `emptyDir.sizeLimit` 和 `ephemeral-storage` request/limit。
- 用实际峰值和增长模型设置 request，不要把所有 Pod 的 request 留为 0。
- 使用 LimitRange 提供默认 request/limit。
- 使用 ResourceQuota 控制 namespace 的临时存储总量；要让临时存储配额生效，Pod 也需要声明相应 limit。
- 为关键服务设置合理的 PriorityClass，但不要把高优先级当作容量治理方案。

### 集群

- 为构建、批处理、转码和大模型任务使用专用节点池。
- 预留 `system-reserved`、`kube-reserved`，并合理设置 kubelet eviction threshold。
- 监控 `nodefs`、`imagefs` 和 `containerfs`，不要只监控根分区。
- 控制单节点可调度的 `ephemeral-storage.requests` 总量。
- 同时采集 emptyDir、容器日志、可写层、镜像垃圾回收和驱逐事件。

## 不适合 emptyDir 的场景

| 场景 | 更合适的方案 |
| --- | --- |
| 数据不能丢 | PVC、对象存储或数据库 |
| 单 Pod 需要数百 GiB 临时空间 | 专用节点池、Local PV 或 PVC |
| 多副本共享数据 | 共享存储或对象存储 |
| 长周期缓存 | 外部缓存或持久化卷 |
| 构建产物需要保留 | 制品库或对象存储 |
| 日志持续高速增长 | 日志采集系统与受控滚动策略 |

## 排查 Checklist

- [ ] 查看事件，区分“单卷/Pod 超限”与“节点 DiskPressure”。
- [ ] 检查 `emptyDir.sizeLimit`，不要用容器内 `df -h` 判断卷上限。
- [ ] 检查每个容器的 `ephemeral-storage.requests/limits`。
- [ ] 确认 kubelet 本地存储布局受支持，且没有额外挂载导致计量失效。
- [ ] 查看 `nodefs`、`imagefs`、`containerfs` 的实际挂载点和可用空间。
- [ ] 排查容器日志、可写层、镜像和其他 Pod，而不只看 emptyDir。
- [ ] 检查已删除但仍由进程持有的文件。
- [ ] 核对 Pod Priority，理解节点压力下的实际驱逐排序。
- [ ] 防止控制器把被驱逐 Pod 反复调度回同一类高压节点。

## 核心结论

1. `emptyDir.sizeLimit` 是卷级限制，不是节点磁盘预留，也不是调度 request。
2. 单卷或 Pod 超限时，kubelet 可以针对对应 Pod 触发驱逐。
3. 所有 Pod 都未超过各自 `sizeLimit`，总量仍可能让节点进入 `DiskPressure`。
4. 节点压力驱逐先看是否超过 request，再看 Priority 和相对 request 的使用量；不是按 emptyDir 使用绝对值排序。
5. 对磁盘压力，QoS Class 不直接决定驱逐顺序。
6. 没有声明 `ephemeral-storage.requests` 的 Pod 在驱逐排序和调度容量管理上都更脆弱。
7. 监控应覆盖单卷、Pod 和节点三层，并同时观察使用量、增长速度、压力状态和驱逐事件。
8. `medium: Memory` 的 emptyDir 按内存计量，不能套用磁盘型 emptyDir 的监控逻辑。

> [!warning] 最终原则
> `emptyDir.sizeLimit` 解决“单个卷不要越界”；`ephemeral-storage` request/limit 解决“调度和 Pod 总量要有边界”；节点容量、保留量和驱逐监控解决“不要让所有 Pod 一起打满节点”。

## 参考资料

- [Kubernetes：Local ephemeral storage](https://kubernetes.io/docs/concepts/storage/ephemeral-storage/)
- [Kubernetes：Node-pressure Eviction](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/)
- [Kubernetes：Resource Management for Pods and Containers](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
