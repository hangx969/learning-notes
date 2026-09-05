---
title: "从零部署 NVIDIA Device Plugin：K8s 识别 GPU 的“第一块敲门砖”"
source: "https://mp.weixin.qq.com/s/h49RmFUKpZXW1ybiltyqsg"
author:
  - "[[深栈运维]]"
published:
created: 2026-09-05
description: "K8s 节点上插着 8 张 A100，调度器却完全看不见——kubectl describe node 的 C"
tags:
  - "clippings"
---
深栈运维 深栈架构师 *2026年8月28日 07:30*

> K8s 节点上插着 8 张 A100，调度器却完全看不见——kubectl describe node 的 Capacity 里压根没有 nvidia.com/gpu 这个字段。

## 看不见 GPU 的 K8s

就像手机插了 SIM 卡却不读卡，系统完好，但“硬件不存在”。

## Device Plugin 是那扇门

它负责把 GPU 硬件信息“翻译”成 K8s 调度器能听懂的语言。没它，GPU 在 K8s 眼里就是一堆废铁。

## 一、先看整条链路：从硬件到 Pod

NVIDIA Device Plugin 在整个 GPU 调度链路里的位置非常明确——它充当了硬件和调度器之间的“翻译官”。下面这张图把完整的数据流向画出来了：

![图片](https://mmbiz.qpic.cn/mmbiz_jpg/OcVbayKJuUzJAovAkweyDWHrERWJdUPwF3xDZkCYicGqX8SianpGjo1cZyOoq1jSfy0fbvgnicZN8feKTWQglZKsGre5N9PodlibmNBzNTBJ00I/640?wx_fmt=webp&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

## 二、部署之前：确保三件套已就位

在部署 Device Plugin 之前，GPU 节点上必须先装好两样东西：NVIDIA 驱动和容器运行时。很多人跳过了这两步直接装 Device Plugin，结果发现节点死活不上报 GPU。

### 2.1 前置条件一：NVIDIA 驱动

Device Plugin 依赖驱动暴露的 NVML（NVIDIA Management Library）接口。驱动没装，Device Plugin 连 GPU 都扫描不到。

```
# 检查驱动是否正常
nvidia-smi
# 必须正常显示 GPU 列表

# 检查 NVML 是否可用
ls -l /usr/lib/x86_64-linux-gnu/libnvidia-ml.so*
```

### 2.2 前置条件二：NVIDIA Container Toolkit

容器内的应用要访问 GPU，需要容器运行时支持 GPU 设备挂载。nvidia-container-toolkit 提供这个能力。

```
# 检查 toolkit 是否安装
which nvidia-container-toolkit

# 检查 containerd 配置中是否有 nvidia runtime
cat /etc/containerd/config.toml | grep -A 5 "runtimes" | grep nvidia
```

如果配置中没有 nvidia runtime，后续 Device Plugin 上报了 GPU，Pod 启动时也会因为无法挂载设备而报 CUDA\_ERROR\_NO\_DEVICE。

## 三、三种部署方式对比

选择哪一种部署方式，取决于你的集群规模和管理工具链：

![图片](https://mmbiz.qpic.cn/sz_mmbiz_jpg/OcVbayKJuUzFENnu1iaGtFVPUia4gR9XwX0fniaOl2Cur7LK1D0xZr2kIwgFzlKT5jfwuUYVkjjFnhUlibn4I8PnHNrLooldIRDYavibh5zUyJhI/640?wx_fmt=webp&from=appmsg&watermark=1#imgIndex=1)

### 方式一：Helm 部署

适用于大多数生产环境，便于版本管理和回滚：

```
# 添加 NVIDIA Helm 仓库
helm repo add nvidia https://helm.ngc.nvidia.com/nvidia
helm repo update

# 安装 Device Plugin
helm install nvidia-device-plugin nvidia/device-plugin \
  --namespace kube-system \
  --create-namespace
```

### 方式二：手动部署（最可控）

直接 apply DaemonSet YAML，适合定制化需求：

```
# 下载 DaemonSet YAML
wget https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/main/deployments/static/nvidia-device-plugin.yml

# 部署
kubectl apply -f nvidia-device-plugin.yml

# 检查 DaemonSet 状态
kubectl get daemonset -n kube-system nvidia-device-plugin
```

### 方式三：GPU Operator 一体化部署（推荐生产）

GPU Operator 把驱动、Device Plugin、Container Toolkit、DCGM 监控全部打包管理：

```
helm repo add nvidia https://helm.ngc.nvidia.com/nvidia
helm repo update

helm install --wait --generate-name \
    -n gpu-operator --create-namespace \
    nvidia/gpu-operator
```

GPU Operator 会在节点上自动安装 NVIDIA 驱动，省去手动装驱动的步骤。真正“从零部署”，连驱动都不用自己装。

## 四、验证部署效果

部署完成后，分三步验证是否生效：

```
# 第一步：检查节点资源
kubectl describe node <gpu-node> | grep nvidia.com
# 预期输出：nvidia.com/gpu: 8（或你节点实际的卡数）

# 第二步：查看 Device Plugin 日志
kubectl logs -n kube-system -l app=nvidia-device-plugin
# 预期输出：Starting FS watcher... 和 Detected X GPU(s)

# 第三步：提交测试 Pod
kubectl run gpu-test --image=nvidia/cuda:12.4.1-base-ubuntu22.04 \
  --restart=Never \
  --overrides='{"spec": {"containers": [{"name": "cuda-test", "image": "nvidia/cuda:12.4.1-base-ubuntu22.04", "args": ["nvidia-smi"], "resources": {"limits": {"nvidia.com/gpu": 1}}}]}}'

kubectl logs gpu-test
# 预期输出：nvidia-smi 正常显示 GPU 信息
```

如果 kubectl describe node 中仍然没有 nvidia.com/gpu，按这个顺序排查：

| 排查顺序 | 检查项 | 命令 |
| --- | --- | --- |
| ① | 驱动是否正常 | `nvidia-smi` |
| ② | 节点是否有 GPU 硬件 | `lspci \| grep -i nvidia` |
| ③ | Device Plugin Pod 是否 Running | `kubectl get pods -n kube-system -l app=nvidia-device-plugin` |
| ④ | Device Plugin 日志是否有错误 | `kubectl logs -n kube-system -l app=nvidia-device-plugin` |
| ⑤ | Kubelet 是否重启过 | `systemctl status kubelet` |

## 五、常见报错与解法

### 报错一：no GPU found

Device Plugin 日志输出这个，表示驱动层没检测到 GPU。跑 nvidia-smi 看驱动是否正常。如果驱动正常但 Device Plugin 报错，检查 Device Plugin 的容器是否以 privileged: true 运行——它需要访问宿主机的 /dev/nvidia\* 设备文件。

### 报错二：failed to start container: Unknown runtime specified nvidia

Pod 启动后报这个错，表示容器运行时未配置 nvidia runtime。检查 /etc/containerd/config.toml 中的 runtimes 配置，确保包含 nvidia。没有就补上，然后重启 containerd。

### 报错三：节点上报的 GPU 数量为 0

检查 GPU 是否被其他进程占用（如 nvidia-persistenced 服务）。或者 Device Plugin 版本与驱动版本不兼容——NVIDIA 推荐 Device Plugin 版本匹配驱动大版本（如驱动 535.x 配合 Device Plugin v0.14.x）。

## 六、Device Plugin 的运行时行为

Device Plugin 不是一次性的初始化工具，而是一个持续运行的 DaemonSet：

- **启动时** ：扫描节点所有 GPU，通过 NVML 读取 UUID、型号、显存等信息
- **运行中** ：监听 Kubelet 的 Allocate 请求，在 Pod 需要 GPU 时完成设备挂载
- **异常时** ：如果 GPU 设备发生变化（如热插拔），Device Plugin 需要重启才能重新扫描

默认情况下，Device Plugin 每 30 秒重新扫描一次 GPU 设备状态，但这个间隔可以通过启动参数 -scan-interval 调整。频繁变化 GPU 设备的环境建议改到 10 秒，普通环境保持默认即可。

## 七、总结

部署 NVIDIA Device Plugin 这件事本身不难，难的是理解它为什么需要，以及它卡住时怎么救。记住三句经验之谈：

- **Device Plugin 不解决调度问题** ，它只解决“资源可见性”问题。调度策略由 kube-scheduler 决定，Device Plugin 只管上报。
- **不是只有 GPU 节点才需要 Device Plugin** 。所有需要上报加速硬件的节点都需要对应的 Device Plugin（如 AMD GPU、Intel FPGA 等）。
- **尽量用 GPU Operator，而不是单独装 Device Plugin** 。单个 Device Plugin 部署简单，但后续管理驱动、监控、运行时升级时，碎片化组件容易遗漏。GPU Operator 把这些打包在一起，Helm 升级一次搞定所有组件。

**生产环境不要用静态 YAML 部署 Device Plugin** 。用 Helm 或 GPU Operator，版本管理和回滚都方便——老版本 YAML 堆积在 /tmp/ 目录里，最后自己都分不清哪个在跑，出问题了才后悔。

---

欢迎加w一起交流：19067272547

**微信扫一扫赞赏作者**

GPU文章 · 目录