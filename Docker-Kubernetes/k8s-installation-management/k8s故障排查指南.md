---
title: k8s故障排查指南
tags:
  - kubernetes
  - k8s-installation
  - 故障排查
aliases:
  - k8s troubleshooting
  - pod故障排查
---

# pod状态异常

~~~sh
kubectl get po <pod name> -o yaml
kubectl describe po <pod name>
kubectl logs <pod name> -c <container name> #--all-containers
~~~

1. pending状态

   - 创建的Pod找不到可以运行它的物理节点，不能调度到相应的节点上运行。
   - 物理节点层面分析：
     - 定位是否是节点资源问题：`free -m`查看内存；`top`查看CPU；`df -h`查看磁盘利用率。
     - 查看节点污点：`kubectl describe nodes <node name>`,例如：`Taints:node-role.kubernetes.io/master:NoSchedule`,表明这个节点不允许调度pod。除非pod定义对这个污点的容忍度才行。
   - pod本身分析：
     - pod是否指定了节点调度（NodeSelector），看一下node name是否正确。
     - pod是否指定了过大的resource request，节点无法满足。
     - pod是否指定了节点亲和性，但是没有节点满足。

2. ImagePullBackOff状态

   - image的name或者tag错误
   - 镜像源无法访问，比如国内网络限制，无法访问dockerhub；或者网速过慢，拉取image超时
   - 私有仓库参数错误，比如imagePullSecret错误
   - dockerfile打包的镜像有问题

   可以手动在工作节点上docker pull看是否可以拉下镜像。

3. CrashLoopBackOff

   - 查看构建镜像用的代码是否有问题；
   - 如果代码没问题，再看环境变量是否有问题；
   - 也可能权限问题：假如pod挂载了数据目录，这个数据目录，我们需要修改属主和属组，否则pod往这个目录写数据，可能没权限

4. Evicted

   - 这个Evicted表示pod所在节点的资源不够了，pod被驱逐走了

5. Complete状态

   - 这个状态表示pod里面的任务完成了，job或者cronjob创建pod的时候，如果pod任务完成了，会出现complete状态

# pod健康探测

~~~yaml
#pod定义的存活性探测如下：
livenessProbe:
       httpGet:
         path: /
         port: 8080
~~~

- 常见错误：Killing container with id docker://xianchao:Container failed probe.. Container will be killed and recreated. Liveness
- 如果在pod启动时遇到这种情况，一般是没有设置 initialDelaySeconds导致的

~~~yaml
# 设置初始化延迟initialDelaySeconds。
livenessProbe:
       httpGet:
         path: /
         port: 8080
       initialDelaySeconds: 15 # pod启动过15s开始探测
~~~

# pod svc超时

K8S中Pod服务连接超时主要分以下几种情况：

1. Pod和Pod连接超时
2. Pod和虚拟主机上的服务连接超时
3. Pod和云主机连接超时

针对上面几种问题，排查思路可按下面方法：

- 网络插件层面：
  - 查看calico或者flannel是否是running状态，查看日志提取重要信息

- Pod层面：

  - 检查Pod网络，测试Pod是否可以ping通同网段其他pod ip

- 物理机层面：
  - 检查物理机网络，测试ping www.baidu.com，ping其他的pod ip
  - 可以抓包测试有无异常
  - 通过抓包修改内核参数

# svc代理pod出现问题

- 直接访问pod可以请求到，但是访问pod前端service，通过请求pod有问题，请求不到。
  - iptables： 重启iptables，重启iptables不可以，重启下机器
  - ipvs：重启机器

# DNS解析问题

1. 使用 `nslookup`（需容器支持）

```sh
kubectl exec <pod-name> -- nslookup google.com
```

2. 查看 DNS 配置

```sh
kubectl exec <pod-name> -- cat /etc/resolv.conf
```

预期输出示例：

```sh
nameserver 10.96.0.10    # Kubernetes DNS Service IP
search default.svc.cluster.local svc.cluster.local cluster.local
options ndots:5
```

3. 若 `nslookup` 失败，检查 CoreDNS 或 kube-dns 是否正常运行：

```sh
kubectl get pods -n kube-system -l k8s-app=kube-dns
```

4. 确认 Pod 的 DNS 策略（`dnsPolicy`）是否为 `ClusterFirst`。

# 防火墙问题

怀疑网络策略（NetworkPolicy）或云平台安全组阻止外网访问。

1. 检查 NetworkPolicy

```sh
kubectl describe networkpolicy -n <namespace>
```

重点关注是否有策略限制出站流量（`egress`）。

2. 验证云平台安全组/防火墙规则

3. 登录到 Pod 所在节点，查看 NAT 表和过滤规则：

```sh
iptables -t nat -L -n -v
iptables -L -n -v
```

# openshift中busybox无法ping

- 报错permission denied are you root

- 解决：

  - 查了下资料，发现是crio运行容器时为了安全，会把NET_RAW删除，而docker默认是启用的，可以在yaml自行手动添加
  
  ~~~yaml
  securityContext:
    capabilities:
      add:
      - NET_RAW
  ~~~
  

# 容器无shell如何测试外网连通性

在 Kubernetes 集群中，某些容器镜像（如基于 `scratch` 或 `distroless` 的镜像）为了追求极简化和安全性，移除了交互式 Shell（如 `/bin/bash` 或 `/bin/sh`）以及常见网络工具（如 `curl`、`ping`）。当这类 Pod 出现外网访问异常时，传统调试方法失效，需要更高级的技巧。

## 临时容器

适用于容器中无网络工具，，k8s版本高于1.23。临时容器会共享目标容器的 **网络命名空间**，因此两者的网络栈（IP、端口、路由等）完全一致。退出临时容器后，它会被自动销毁，不会影响原 Pod。

注意：

- 若集群版本低于 `1.23`，需启用 `EphemeralContainers` 特性门控。
- 调试镜像可能需要特权权限，需确保 Pod 的 SecurityContext 允许临时容器运行。

1. 注入临时容器

   ~~~sh
   kubectl debug -it <pod-name> --image=nicolaka/netshoot --target=<container-name>
   #nicolaka/netshoot，内置完整网络工具链
   ~~~

2. 在临时容器中测试外网

   ~~~sh
   # 测试 HTTP 访问
   curl -I https://www.google.com
   # 测试 DNS 解析
   nslookup google.com
   # 测试 ICMP（ping）
   ping 8.8.8.8
   ~~~

## 注入sidecar容器

适用于临时容器功能不可用，但是允许修改pod配置。同一 Pod 内的所有容器共享同一个网络命名空间，因此 Sidecar 可以直接访问主容器的网络环境。

注意：

- 需要重新部署pod，可能会有downtime
- 生产环境中慎用，建议仅在调试阶段添加sidecar

1. 编辑pod yaml，添加sidecar

   ~~~yaml
   apiVersion: v1
   kind: Pod
   metadata:
     name: my-pod
   spec:
     containers:
     - name: main-app
       image: my-minimal-image:latest
       # 主容器无 Shell 和网络工具...
     - name: network-debugger
       image: nicolaka/netshoot
       command: ["sleep", "infinity"]  # 保持 Sidecar 运行
       securityContext:
         runAsUser: 0  # 以 root 用户运行（可选）
   ~~~

2. 进入sidecar容器测试网络

   ~~~sh
   kubectl exec -it my-pod -c network-debugger -- curl -v https://www.google.com
   ~~~

## 跳板机pod代理测试

如果无法修改目标 Pod，也没有临时容器功能，且需要模拟相同网络环境。

1. 启动跳板机pod

   ~~~sh
   kubectl run jumpbox --image=nicolaka/netshoot --rm -it --restart=Never -- /bin/sh
   ~~~

2. 在跳板机pod中通过代理测试目标pod的网络

   假设目标 Pod 的 IP 为 `10.244.1.5`：

   ~~~sh
   # 使用 curl 的 --proxy 参数
   curl -x http://10.244.1.5:80 http://example.com
   
   # 使用 nc 测试 TCP 连通性
   nc -zv 10.244.1.5 80
   ~~~

## 调试镜像选择

| 镜像名称            | 特点                                      | 适用场景             |
| ------------------- | ----------------------------------------- | -------------------- |
| `nicolaka/netshoot` | 包含完整网络工具（curl, tcpdump, dig 等） | 通用网络调试         |
| `busybox:glibc`     | 轻量级，支持 nslookup、ping               | 基础连通性测试       |
| `alpine:latest`     | 包含 Shell 和包管理器（apk）              | 需临时安装工具的场合 |


---

# 节点 DiskPressure 与 Kubelet 驱逐机制

> 80% 的磁盘压力告警，根本不是磁盘容量耗尽，而是 Kubelet 资源驱逐机制触发了节点保护。别急着扩容——先搞懂底层原理。

## NodeHasDiskPressure 不是"磁盘满了"

K8s 官方定义的 NodeHasDiskPressure 真实含义：**Kubelet 检测到节点磁盘类资源（空间/Inode）低于安全阈值，判定节点无法稳定、安全运行现有 Pod，触发节点资源保护机制。**

重点是"不安全"，不是"磁盘满"。哪怕磁盘只用了 50%，只要剩余可用资源、Inode 数量跌破 Kubelet 预设阈值，就会立即触发磁盘压力状态。

## 底层全链路：Kubelet 如何发现磁盘压力

```
cAdvisor 采集节点文件系统指标
  → 上报至 Eviction Manager
    → 对比驱逐阈值
      → 更新节点 DiskPressure 状态
        → 调度器停止新 Pod 调度
          → 优先执行镜像/容器 GC
            → 资源仍不足则驱逐存量 Pod
```

### Eviction Manager 核心循环

对应源码：`pkg/kubelet/eviction`。持续周期性执行 `synchronize()` 方法，循环完成三件事：

1. **采集指标**：获取节点磁盘、内存、PID、Inode 等实时资源数据
2. **阈值判定**：对比预设软硬驱逐阈值，判断资源是否超标
3. **执行动作**：更新节点状态、触发垃圾回收、按需驱逐 Pod

## Kubelet 监控的 3 类磁盘（90% 的人只看了 1 个）

**任意一个触发阈值，都会触发 DiskPressure**：

| 磁盘类型 | 对应目录 | 承载内容 |
|---------|---------|---------|
| **NodeFS**（节点根文件系统） | `/` | `/var/lib/kubelet`、节点日志 `/var/log`、系统配置 |
| **ImageFS**（镜像文件系统） | Containerd: `/var/lib/containerd`<br>Docker: `/var/lib/docker` | 容器镜像、镜像分层、快照数据 |
| **ContainerFS**（容器可写层） | 新版 CRI/Containerd 专属 | 容器运行时的可写分层数据、临时读写数据 |

**核心结论**：哪怕根磁盘空间充足，只要 ImageFS、ContainerFS 资源耗尽或跌破阈值，节点依然会触发磁盘压力、驱逐 Pod。

## 阈值判定：Kubelet 看的是可用资源，不是使用率

日常用 `df -h` 看的是"已用空间占比"，但 **Kubelet 的驱逐判定和使用率无关，只看可用资源**。

### 默认硬驱逐阈值

```
--eviction-hard=
  memory.available<100Mi
  nodefs.available<10%
  imagefs.available<15%
  nodefs.inodesFree<5%
  imagefs.inodesFree<5%
```

- `nodefs.available<10%`：节点根磁盘剩余可用空间不足 10%，触发压力
- `inodeFree<5%`：剩余 Inode 不足 5%，同样触发磁盘压力

### 最容易被忽略的杀手：Inode 耗尽

大量微小文件会快速耗尽 Inode，却几乎不占用磁盘空间：

- 容器疯狂打印短日志、碎片化日志文件
- emptyDir 临时文件、缓存碎片堆积
- 老旧容器残留海量小文件

**排查时务必双指令核查，缺一不可**：

```bash
df -h    # 查看磁盘空间
df -i    # 查看 Inode 使用率（核心！）
```

## 触发后的完整连锁反应

### 第一步：更新节点状态

节点 Condition 标记为 `DiskPressure=True`，直至资源恢复。

### 第二步：调度器停止新 Pod 调度

所有新创建、待调度的 Pod 直接陷入 Pending 状态。

### 第三步：优先执行垃圾回收（不是立即驱逐！）

**K8s 不会立即驱逐 Pod！** 这是大多数人的认知盲区。

官方优先级：**先 GC 回收资源，资源仍不足，再驱逐 Pod。**

- **Image GC**：由 `image_gc_manager` 管控，默认每 5 分钟执行，清理超过最小存活时长（默认 2 分钟）、长期未被使用的闲置镜像
- **Container GC**：默认每分钟执行，清理节点上已退出、终止的残留容器和无效运行时碎片资源

### 第四步：资源仍不足，触发 Pod 驱逐

镜像、残留容器清理完毕后，若磁盘/Inode 资源依旧低于阈值，Eviction Manager 才执行最终的 Pod 驱逐。

## Pod 驱逐优先级（不是随机的）

### 按 QoS 等级优先驱逐（核心规则）

**BestEffort（先驱逐）> Burstable > Guaranteed（最后驱逐）**

无资源配额限制的 BestEffort Pod 优先级最高（最先被驱逐），核心 Guaranteed 业务 Pod 最后驱逐。

### 同 QoS 下的辅助判定

- 优先驱逐**磁盘资源占用更高**的 Pod（日志、emptyDir、Overlay 可写层占用大户）
- 参考 `PriorityClass` 优先级，低优先级业务先被驱逐
- 运行时间更短、重启更频繁的 Pod 优先被清理

> **疯狂打日志、占用临时磁盘多的低优先级 Pod，永远是第一个被干掉的。**

## 线上故障极速排查流程

遇到 NodeHasDiskPressure 告警，别慌着扩容，按这套流程走：

### 1. 查看节点压力状态与事件

```bash
kubectl describe node <节点名>
# 重点关注：Conditions 中的 DiskPressure 状态、Event 中的驱逐与压力告警记录
```

### 2. 核查 Kubelet 底层驱逐日志

```bash
journalctl -u kubelet -f
# 检索关键词：eviction thresholds have been met、must evict pod
```

### 3. 双维度核查磁盘与 Inode

```bash
df -h    # 磁盘空间
df -i    # Inode 使用率
# 重点排查：Inode 耗尽、ImageFS 爆满、根磁盘剩余空间不足
```

### 4. 清理闲置镜像

```bash
# Containerd
ctr images ls
# 通用 CRI
crictl images
# 清理未使用的镜像
crictl rmi --prune
```

### 5. 排查容器日志堆积（线上头号元凶）

```bash
# 核心日志目录
du -sh /var/log/containers/
du -sh /var/log/pods/
# 找到最大的日志文件
find /var/log/containers/ -size +100M -exec ls -lh {} \;
```

**生产中 60% 以上的磁盘压力故障，都是业务日志无限制打印、日志未轮转导致，而非镜像堆积。**

## 生产最佳实践

| 措施 | 说明 |
|------|------|
| **自定义驱逐阈值** | 根据节点磁盘容量和业务负载调优软硬驱逐阈值，避免误杀和频繁告警 |
| **强制容器日志轮转** | 配置日志大小、保留份数、自动轮转策略，杜绝日志无限膨胀 |
| **开启并优化镜像 GC** | 合理配置镜像最小保留时长、GC 高低阈值，定期自动清理闲置镜像 |
| **新增 Inode 监控告警** | 监控面板同时接入 nodefs、imagefs 的空间使用率**与 Inode 使用率** |
| **限制 emptyDir 临时存储** | 为业务 emptyDir 配置 `sizeLimit`，禁止临时数据无限制占用节点磁盘 |
| **前置监控预警** | 核心监控 `nodefs.available`、`imagefs.available`、`inodeFree` 三大指标 |

## 总结

**NodeHasDiskPressure 从来不是磁盘故障，而是 K8s 节点的主动保护机制。**

完整底层链路：

```
cAdvisor 指标采集 → Eviction Manager 阈值校验 → 节点 DiskPressure 状态更新
→ 停止新 Pod 调度 → Image/Container 垃圾回收 → 资源不足触发 Pod 分级驱逐
```

真正靠谱的集群运维，从不只会扩容磁盘。**读懂 Eviction 底层原理、吃透资源回收机制、做好前置监控治理**，才能彻底杜绝磁盘压力导致的业务重启、集群抖动问题。
