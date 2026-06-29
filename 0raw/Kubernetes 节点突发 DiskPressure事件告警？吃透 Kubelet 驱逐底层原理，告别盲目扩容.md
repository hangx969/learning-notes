---
title: "Kubernetes 节点突发 DiskPressure事件告警？吃透 Kubelet 驱逐底层原理，告别盲目扩容"
source: "https://mp.weixin.qq.com/s/qKCJ5sE79fh_m5wMF3egew"
author:
  - "[[老鹰9527]]"
published:
created: 2026-06-29
description: "绝大多数人的第一反应都是：磁盘不够了，直接扩容！但真实生产场景中，80% 的磁盘压力告警，根本不是磁盘容量耗尽，而是 Kubelet 资源驱逐机制触发了节点保护。"
tags:
  - "clippings"
---
老鹰9527 技术控杂谈 *2026年6月29日 08:30*

绝大多数人的第一反应都是：磁盘不够了，直接扩容！

但真实生产场景中， **80% 的磁盘压力告警，根本不是磁盘容量耗尽，而是 Kubelet 资源驱逐机制触发了节点保护** 。

本文穿透表象、深挖底层，完整拆解 **NodeHasDiskPressure 产生逻辑、Eviction Manager 工作机制、Pod 驱逐决策链路、镜像/容器 GC 优先级** ，让你彻底读懂 K8s 节点磁盘压力的底层逻辑，从根源解决故障，而非单纯治标扩容。

---

## 一、别被表象骗了：NodeHasDiskPressure 不是「磁盘满了」

线上告警弹出这两条日志时，运维同学基本都会瞬间紧绷：

```nginx
Warning  NodeHasDiskPressure
```

固有认知误区： **DiskPressure = 磁盘使用率 100%** 。

K8s 官方定义的 **NodeHasDiskPressure** 真实含义是：

**Kubelet 检测到节点磁盘类资源（空间/Inode）低于安全阈值，判定节点无法稳定、安全运行现有 Pod，触发节点资源保护机制** 。

重点是 **「不安全」** ，不是「磁盘满」。哪怕磁盘只用了 50%，只要剩余可用资源、Inode 数量跌破 Kubelet 预设阈值，就会立刻触发磁盘压力状态。

磁盘压力和内存压力、PID 压力本质一致，都属于 K8s \*\*节点资源压力（Resource Pressure）\*\*体系，是 Kubelet 保障集群稳定性的核心机制。

---

## 二、底层全链路：K8s 是如何发现磁盘压力的？

整个检测、判定、驱逐流程，核心由两大组件驱动： **cAdvisor + Kubelet Eviction Manager** ，全程自动轮询、实时监控，无需人工干预。

### 完整底层链路

cAdvisor 采集节点文件系统指标 → 上报至 Eviction Manager → 对比驱逐阈值 → 更新节点 DiskPressure 状态 → 调度器停止新 Pod 调度 → 优先执行镜像/容器 GC → 资源不足则驱逐存量 Pod

### 核心核心：Eviction Manager

对应的源码核心目录： `pkg/kubelet/eviction` ，是节点资源防护的核心中枢。

Eviction Manager 会持续周期性执行 `synchronize()` 方法，循环完成三件事：

1. 1.**采集指标**
1. ：获取节点磁盘、内存、PID、Inode 等实时资源数据；
2. 2.**阈值判定**
	：对比预设软硬驱逐阈值，判断资源是否超标；
3. 3.**执行动作**
	：更新节点状态、触发垃圾回收、按需驱逐 Pod。

这也是为什么磁盘压力告警、Pod 驱逐总是「突发式」出现——这是秒级轮询的自动化机制，而非磁盘瞬间爆满导致。

---

## 三、关键盲区：K8s 监控的 3 类磁盘，90% 人只看了 1 个

很多同学排查时只看根目录 `/` 磁盘使用率，这是典型的排查误区。Kubelet 会精细化监控三套独立文件系统， **任意一个触发阈值，都会触发 DiskPressure** 。

### 1\. NodeFS（节点根文件系统）

对应目录： `/`

承载核心节点数据： `/var/lib/kubelet` 、节点日志 `/var/log` 、系统配置文件等，是节点运行的基础。

### 2\. ImageFS（镜像文件系统）

对应目录：Containerd 为 `/var/lib/containerd` ，Docker 为 `/var/lib/docker`

专门存储容器镜像、镜像分层、快照数据，集群长期不清理废弃镜像，大概率会撑满 ImageFS。

### 3\. ContainerFS（容器可写层文件系统）

新版 CRI/Containerd 专属，存储容器运行时的可写分层数据、临时读写数据。

**核心结论** ：哪怕根磁盘空间充足，只要 ImageFS、ContainerFS 资源耗尽或跌破阈值，节点依然会触发磁盘压力、驱逐 Pod。

---

## 四、阈值判定真相：Kubelet 从不看「磁盘使用率」

日常我们用 `df -h` 看的是「已用空间占比」，但 **Kubelet 的驱逐判定和使用率无关，只看可用资源** 。

集群默认硬驱逐阈值参考：

```diff
--eviction-hard=memory.available<100Minodefs.available<10%imagefs.available<15%nodefs.inodesFree<5%imagefs.inodesFree<5%
```

简单解读：

■ `nodefs.available<10%` ：节点根磁盘 **剩余可用空间不足 10%** ，触发压力；

■ `inodeFree<5%` ：剩余 Inode 不足 5%，同样触发磁盘压力。

这也解释了线上最迷惑的故障场景： **磁盘空间还有富余，却依然触发 DiskPressure** 。

### 最容易被忽略的杀手：Inode 耗尽

大量微小文件会快速耗尽 Inode，却几乎不占用磁盘空间：

■ 容器疯狂打印短日志、碎片化日志文件；

■ emptyDir 临时文件、缓存碎片堆积；

■ 老旧容器残留海量小文件。

排查时务必双指令核查，缺一不可：

```bash
# 查看磁盘空间df -h# 查看 Inode 使用率（核心！）df -i
```

## 五、磁盘压力触发后，集群会发生什么？（完整连锁反应）

一旦 Eviction Manager 判定磁盘压力达标，会执行一套标准化的节点保护流程，层层递进，不可逆：

### 第一步：更新节点状态

节点 Condition 标记为 `DiskPressure=True` ，节点状态异常永久留存，直至资源恢复。

### 第二步：调度器停止新 Pod 调度

所有新创建、待调度的 Pod 会直接陷入 Pending 状态，事件日志提示「节点存在磁盘压力」，不再分配新负载。

### 第三步：优先执行垃圾回收（GC）

**K8s 不会立刻驱逐 Pod！** 这是大多数人的认知盲区。

官方优先级： **先 GC 回收资源，资源仍不足，再驱逐 Pod**

#### 1\. Image GC（镜像垃圾回收）

由 `image_gc_manager` 管控，默认每5分钟执行一次，会清理超过最小存活时长（默认2分钟）、长期未被使用的闲置镜像，释放 ImageFS 空间。同时依据镜像高低阈值百分比，控制回收粒度，避免频繁 GC 震荡。

#### 2\. Container GC（容器垃圾回收）

默认每分钟执行一次，自动清理节点上已退出、终止的残留容器，清理无效运行时碎片资源。同时会限制单 Pod 最大死亡容器数量，避免残留容器堆积。

### 第四步：资源仍不足，触发 Pod 驱逐

镜像、残留容器清理完毕后，若磁盘/Inode 资源依旧低于阈值，Eviction Manager 才会执行最终的 Pod 驱逐操作。

---

## 六、Pod 驱逐不是随机的！官方驱逐优先级细则

K8s 有严格的驱逐权重规则，最大程度保障核心业务稳定，驱逐优先级从高到低：

### 1\. 按 QoS 等级优先驱逐（核心规则）

**BestEffort（尽力服务） > Burstable（突发服务） > Guaranteed（保底服务）**

无资源配额限制的 BestEffort Pod 优先级最高，核心 Guaranteed 核心业务 Pod 最后驱逐，最大程度保护核心业务。

### 2\. 同 QoS 下的辅助判定规则

■ 优先驱逐 **磁盘资源占用更高** 的 Pod（日志、emptyDir、Overlay 可写层占用大户）；

■ 参考 `PriorityClass` 优先级，低优先级业务先被驱逐；

■ 运行时间更短、重启更频繁的 Pod 优先被清理。

简单说： **疯狂打日志、占用临时磁盘多的低优先级 Pod，永远是第一个被干掉的** 。

---

## 七、线上故障极速排查流程（直接套用）

遇到 NodeHasDiskPressure 告警，别慌着扩容，按这套标准流程排查，100% 定位根因：

### 1\. 查看节点压力状态与事件

```xml
kubectl describe node <节点名>
```

重点关注：Conditions 中的 DiskPressure 状态、节点 Event 中的驱逐与压力告警记录。

### 2\. 核查 Kubelet 底层驱逐日志

```nginx
journalctl -u kubelet -f
```

检索关键词： `eviction thresholds have been met` 、 `must evict pod` ，精准定位触发驱逐的资源类型（空间/Inode）。

### 3\. 双维度核查磁盘与 Inode

```bash
df -hdf -i
```

重点排查 Inode 耗尽、ImageFS 爆满、根磁盘剩余空间不足三类问题。

### 4\. 清理闲置镜像，排查镜像堆积

```bash
# Containerdctr images ls# 通用 CRIcrictl images
```

清理长期未使用的废弃镜像、版本残留镜像。

### 5\. 排查容器日志堆积（线上头号元凶）

核心日志目录：

■ `/var/log/containers`

■ `/var/log/pods`

生产中 60% 以上的磁盘压力故障，都是业务日志无限制打印、日志未轮转导致，而非镜像堆积。

---

## 八、生产最佳实践：彻底根治磁盘压力与 Pod 驱逐

与其故障后救火，不如提前规避，这套生产标准方案可直接落地：

■ **自定义适配驱逐阈值** ：不依赖默认阈值，根据节点磁盘容量、业务负载调优软硬驱逐阈值，避免误杀、频繁告警。

■ **强制容器日志轮转** ：为容器运行时配置日志大小、日志保留份数、自动轮转策略，杜绝日志无限膨胀。

■ **开启并优化镜像 GC** ：合理配置镜像最小保留时长、GC 高低阈值，定期自动清理闲置镜像，避免 ImageFS 堆积。

■ **新增 Inode 监控告警** ：监控面板同时接入 nodefs、imagefs 的空间使用率与 Inode 使用率，提前预警，不坐等故障爆发。

■ **限制 emptyDir 临时存储** ：为业务 emptyDir 配置 `sizeLimit` ，禁止临时数据无限制占用节点磁盘资源。

■ **前置监控预警** ：核心监控 `nodefs.available` 、 `imagefs.available` 、 `inodeFree` 三大指标，实现故障预判，而非事后补救。

---

## 九、总结

**NodeHasDiskPressure 从来不是磁盘故障，而是 K8s 节点的主动保护机制** 。

它的触发，不代表磁盘满了，只代表节点资源已经不足以安全承载现有业务，Kubelet 为了避免节点雪崩、集群失控，主动执行限流、回收、驱逐操作。

完整底层链路再复盘一遍：

**cAdvisor 指标采集 → Eviction Manager 阈值校验 → 节点 DiskPressure 状态更新 → 停止新 Pod 调度 → Image/Container 垃圾回收 → 资源不足触发 Pod 分级驱逐**

真正靠谱的集群运维，从不只会扩容磁盘。 **读懂 Eviction 底层原理、吃透资源回收机制、做好前置监控治理** ，才能彻底杜绝磁盘压力导致的业务重启、集群抖动问题。