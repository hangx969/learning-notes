---
title: "【Kubernetes 存储扩容避坑指南】PV/PVC/StorageClass 在线扩容+缩容真相（附实战命令）"
source: "https://mp.weixin.qq.com/s/ZNw9F9-jYelsTytF7NEXiA?scene=1"
author:
  - "[[老郭]]"
published:
created: 2026-06-28
description: "一句话先告诉你核心结论PVC 可以在线扩容（大部分场景不中断业务），但缩容——K8s 原生不支持，别想了。"
tags:
  - "clippings"
---
老郭 老郭a *2026年6月8日 09:08*

### 一句话先告诉你核心结论

**PVC 可以在线扩容（大部分场景不中断业务），但缩容——K8s 原生不支持，别想了。**

我见过太多人在这上面踩坑：开发说“数据库磁盘不够了，扩一下”，运维扩完说“扩多了能不能缩回去”，结果折腾半天发现根本缩不了。这篇文档从 SRE 视角，把扩容能做的、不能做的、怎么排查、遇到扩容失败怎么办，一次说清楚。

---

### 一、什么场景下你需要扩容？

运维中最常见的几个场景：

- 监控告警：PV 使用率 > 85%，磁盘快写满了
- 业务反馈：Pod 写入文件时报 `No space left on device`
- 容量规划：历史数据显示数据每月增长 20%，需要提前扩
- 数据库扩容：MySQL/PostgreSQL 的数据目录不够用了

**什么场景不需要看这篇？**

- 你是用 hostPath 或 emptyDir（临时存储）——这种不要在生产用，挂了数据就没了
- 你的 K8s 版本低于 1.11——那会儿 PVC 扩容还是实验性功能，建议先升级集群

---

### 二、扩容前的三件必查事项

正式动手前，花 3 分钟确认这三点，能避免 90% 的坑。

**1\. 确认当前 PVC 信息**

```cs
kubectl get pvc  -n
```

看一眼 `CAPACITY` 和 `STATUS` ，确认是 `Bound` 状态。

**2\. 确认这个 PVC 用的是哪个 StorageClass**

```cs
kubectl get pvc  -n  -o jsonpath='{.spec.storageClassName}'
```

记下这个 SC 名字，下一步要用。

**3\. 确认底层存储支持扩容（非常重要）**

不是所有存储后端都支持在线扩容。我踩过的坑包括：某些 NFS 实现、旧版 vSphere CSI 的 RWX 共享卷、静态 PV（Reclaim Policy = Retain）——这些都不支持动态扩容。

---

### 三、StorageClass 配置：这是第一道坎

扩容能成功的第一步： **StorageClass 的** `allowVolumeExpansion` **必须为** `true` 。

检查当前 StorageClass：

```cs
kubectl get storageclass  -o yaml | grep -A1 allowVolumeExpansion
```

如果没输出，或者显示 `false` ，就需要改。

**修改 StorageClass：**

```nginx
kubectl edit storageclass
```

在 `parameters` 块下面添加（或修改）这一行：

```javascript
allowVolumeExpansion: true
```

完整的 StorageClass 示例（以 GCE PD 为例）：

```makefile
apiVersion: storage.k8s.io/v1kind: StorageClassmetadata:  name: standardprovisioner: kubernetes.io/gce-pdparameters:  type: pd-standardallowVolumeExpansion: true   # 这一行是关键
```

改完之后不需要重启任何东西，立即生效。

坑爹的是，有些云厂商的 CSI 驱动虽然支持 `allowVolumeExpansion` ，但实际扩容时需要离线（停 Pod）。比如 UpCloud 的 CSI 驱动就只支持离线扩容。所以最好先去云厂商文档里确认一下。

---

### 四、动手：两种扩容方式

#### 方式一：kubectl patch（推荐，最直接）

```apache
kubectl patch pvc  -n  -p '{"spec":{"resources":{"requests":{"storage":"20Gi"}}}}'
```

执行后输出 `persistentvolumeclaim/<pvc-name> patched` 表示成功。

#### 方式二：kubectl edit（适合需要同时改其他字段的场景）

```nginx
kubectl edit pvc  -n
```

找到 `.spec.resources.requests.storage` ，把值改成新的大小，保存退出。

两种方式本质一样。我习惯用 patch，一行搞定，不容易手滑。

---

### 五、扩容后的验证：别光看 PVC

扩容指令执行后， **不一定立即生效** 。整个流程分两个阶段：

1. **后端存储扩容：底层 Volume 被扩到新大小**
2. **文件系统扩容：Pod 重新挂载后，节点上的文件系统被调整**

**查看扩容进度：**

```nginx
kubectl describe pvc  -n
```

看 `Conditions` 字段。如果看到 `FileSystemResizePending` ，说明存储后端已经扩完了，但文件系统还没扩——等 Pod 重启或重新挂载后会自动完成。

**查看 PVC 容量：**

```cs
kubectl get pvc  -n
```

注意：刚执行完 patch，PVC 的 `CAPACITY` 可能还是旧值，这是正常的。等文件系统扩容完成后才会更新。

**进 Pod 确认文件系统大小（最终验证）：**

```bash
kubectl exec -it  -n  -- df -h
```

看到新的大小才算真正完成。

---

### 六、核心限制：缩容不支持 + 扩容失败怎么办

#### 缩容？不支持。

K8s 从设计上就不支持 PVC 缩容。不管是 CSI 驱动还是 in-tree 插件，都不支持对底层 Volume 做实际收缩。

如果你试着 patch 一个比当前小的值：

```apache
kubectl patch pvc my-pvc -p '{"spec":{"resources":{"requests":{"storage":"5Gi"}}}}'
```

会得到这个错误：

```cs
The persistentVolumeClaim "my-pvc" is invalid: spec.resources.requests.storage: Forbidden: field can not be less than previous value
```

这是 API 层面的校验，绕不过去。

**扩容多了怎么办？** 我的建议：

1. 接受现实，多的容量就放在那——反正存储又不贵，留着以后用
2. 如果一定要回收，只能做数据迁移：建一个新的小 PVC，把数据拷过去，切流量，删老的

#### 扩容失败怎么办？（v1.34 有救了）

扩容失败最常见的原因：拼写错误（想扩 100TB 写成了 1000TB）、存储配额用完、后端不支持那么大容量。

**K8s v1.34 之前** ：扩容失败后 PVC 会被卡住，需要管理员手动介入恢复，非常麻烦。

**K8s v1.34+** ：扩容失败后，你可以在扩容操作还未完成时，直接 patch 一个比错误值小但比原值大的新大小，Kubernetes 会自动修正。临时占用的配额也会自动归还。

示例：原来 10TB，错误地扩到 1000TB（失败），修正到 100TB：

```apache
kubectl patch pvc myclaim -p '{"spec":{"resources":{"requests":{"storage":"100TB"}}}}'
```

前提是 100TB 必须大于原值 10TB。不能缩到原值以下。

**查看扩容失败的详细状态（v1.34+ 新特性）：**

```cs
kubectl get pvc myclaim -o jsonpath='{.status.allocatedResourceStatus.storage}'
```

可能输出的状态值：

| 状态 | 含义 |
| --- | --- |
| `ControllerResizeInProgress` | 控制器正在扩容 |
| `NodeResizePending` | 等待节点扩容文件系统 |
| `ControllerResizeInfeasible` | 扩容不可行（配额/后端限制） |
| `ControllerResizeError` | 扩容出错 |

---

### 七、生产环境的扩容建议（SRE 私房经验）

1. **扩容前，先备份。**
	尤其是数据库的 PVC。虽然扩容操作本身不会丢数据，但万一后端存储出问题呢？
2. **扩容时预留缓冲。**
	别等到磁盘 99% 才扩，建议阈值设在 80%。扩容需要时间，万一扩的过程中业务写爆了就尴尬了。
3. **建立容量看板。**
	把 PVC 使用率接入 Prometheus，设置分级告警（80% 预警，90% 紧急）。
4. **扩容参数要慎重。**
	扩多大？我一般按“当前已用 × 1.5”来估算，既留够缓冲又不过度浪费。
5. **检查 CSI 驱动的文档。**
	不同厂商的驱动行为有差异：有的支持在线扩容（Pod 不用重启），有的要求离线（停 Pod），有的对文件系统类型有限制。生产环境动手前一定要确认。
6. **存储类选型建议：**
- 数据库（MySQL/PostgreSQL/Etcd）：选支持在线扩容的块存储（如 AWS EBS、GCE PD、Azure Disk），IOPS 要够
	- 大文件共享/日志：选支持 RWX 的共享存储（如 NFS、CephFS），但要确认扩容是否支持
	- 非关键数据：用普通云盘即可，便宜

---

### 八、常见问题速查表

| 现象 | 可能原因 | 解决方案 |
| --- | --- | --- |
| patch 后 PVC 没变化 | StorageClass 的 allowVolumeExpansion 不是 true | `kubectl edit storageclass` 加上 `allowVolumeExpansion: true` |
| describe 显示 `VolumeResizeFailed` | 存储后端不支持扩容，或 PV 是静态创建的 | 检查 PV 的 RECLAIM POLICY；静态 PV 需手动改 PV 容量后重建 PVC |
| `FileSystemResizePending` 一直不消失 | Pod 没有重新挂载 | 重启 Pod 或 scale down/up 触发重新挂载 |
| 想缩容 | K8s 不支持 | 建新 PVC 做数据迁移，无法原地缩 |
| 扩容时写错数值，卡住了（1.34 以下） | 扩容请求进入失败循环 | 只能手动恢复；推荐升级到 1.34+ |

---

### 九、写在最后

总结几个核心要点：

- **PVC 只能在线扩，不能缩。这是 K8s 的设计原则，别在这上面浪费时间。**
- **扩容前确认 StorageClass 的** `allowVolumeExpansion: true，这是第一道门槛。`
- **扩容后检查** `FileSystemResizePending` **状态，等 Pod 重新挂载后才算真正完成。**
- **K8s v1.34 带来了扩容失败恢复能力，写错数值不用慌，改回来就行。**
- **不同存储后端的扩容行为差异很大，生产环境动手前先读 CSI 驱动文档。**

---

你遇到过哪些扩容的坑？有什么独家排障经验？欢迎在评论区分享，一起避坑。

*如果觉得有用，欢迎分享给更多需要的朋友。*

云原生 · 目录

作者提示: 个人观点，仅供参考