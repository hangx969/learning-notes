---
title: "从零部署 NVIDIA Device Plugin：K8s 识别 GPU 的“第一块敲门砖”"
source: "https://mp.weixin.qq.com/s/h49RmFUKpZXW1ybiltyqsg"
created: 2026-09-05
tags:
  - kubernetes
  - gpu
  - nvidia
  - device-plugin
---

# 从零部署 NVIDIA Device Plugin：K8s 识别 GPU 的“第一块敲门砖”

> K8s 节点上插着 8 张 A100，调度器却完全看不见——`kubectl describe node` 的 Capacity 里没有 `nvidia.com/gpu` 字段。

## 看不见 GPU 的 K8s

系统和硬件都正常，并不代表 Kubernetes 已经识别 GPU。没有设备插件时，GPU 对 K8s 来说就是不可调度的资源。

## Device Plugin 是那扇门

NVIDIA Device Plugin 负责把 GPU 硬件信息转换成 K8s 调度器能够识别的扩展资源。没有它，GPU 节点不会向集群上报可用的 GPU 数量。

## 一、先看整条链路：从硬件到 Pod

NVIDIA Device Plugin 位于 GPU 硬件和 Kubernetes 调度器之间，负责完成资源发现与分配请求。完整链路是：硬件和驱动提供 GPU → Device Plugin 向 Kubelet 注册资源 → Kubernetes 调度器根据扩展资源调度 Pod → 容器运行时把 GPU 设备挂载到容器。

![GPU 调度链路](https://mmbiz.qpic.cn/mmbiz_jpg/OcVbayKJuUzJAovAkweyDWHrERWJdUPwF3xDZkCYicGqX8SianpGjo1cZyOoq1jSfy0fbvgnicZN8feKTWQglZKsGre5N9PodlibmNBzNTBJ00I/640?wx_fmt=webp&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

## 二、部署之前：确保三件套已就位

在部署 Device Plugin 之前，GPU 节点上必须先准备好 NVIDIA 驱动和容器运行时。跳过这两步直接部署 Device Plugin，节点可能仍然不会上报 GPU。

### 2.1 前置条件一：NVIDIA 驱动

Device Plugin 依赖驱动暴露的 NVML（NVIDIA Management Library）接口。驱动未安装或未正常工作时，Device Plugin 无法扫描 GPU。

```bash
# 检查驱动是否正常
nvidia-smi
# 必须正常显示 GPU 列表

# 检查 NVML 是否可用
ls -l /usr/lib/x86_64-linux-gnu/libnvidia-ml.so*
```

### 2.2 前置条件二：NVIDIA Container Toolkit

容器内的应用要访问 GPU，需要容器运行时支持 GPU 设备挂载。`nvidia-container-toolkit` 提供这项能力。

```bash
# 检查 toolkit 是否安装
which nvidia-container-toolkit

# 检查 containerd 配置中是否有 nvidia runtime
cat /etc/containerd/config.toml | grep -A 5 "runtimes" | grep nvidia
```

如果配置中没有 nvidia runtime，Device Plugin 即使上报了 GPU，Pod 启动时也可能因无法挂载设备而报 `CUDA_ERROR_NO_DEVICE`。

## 三、三种部署方式对比

选择部署方式取决于集群规模和管理工具链：

![NVIDIA GPU 部署方式](https://mmbiz.qpic.cn/sz_mmbiz_jpg/OcVbayKJuUzFENnu1iaGtFVPUia4gR9XwX0fniaOl2Cur7LK1D0xZr2kIwgFzlKT5jfwuUYVkjjFnhUlibn4I8PnHNrLooldIRDYavibh5zUyJhI/640?wx_fmt=webp&from=appmsg&watermark=1#imgIndex=1)

### 方式一：Helm 部署

适用于大多数生产环境，便于版本管理和回滚：

```bash
# 添加 NVIDIA Helm 仓库
helm repo add nvidia https://helm.ngc.nvidia.com/nvidia
helm repo update

# 安装 Device Plugin
helm install nvidia-device-plugin nvidia/device-plugin \
  --namespace kube-system \
  --create-namespace
```

### 方式二：手动部署

直接 apply DaemonSet YAML，适合需要定制化配置的场景：

```bash
# 下载 DaemonSet YAML
wget https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/main/deployments/static/nvidia-device-plugin.yml

# 部署
kubectl apply -f nvidia-device-plugin.yml

# 检查 DaemonSet 状态
kubectl get daemonset -n kube-system nvidia-device-plugin
```

### 方式三：GPU Operator 一体化部署

GPU Operator 将驱动、Device Plugin、Container Toolkit、DCGM 监控等组件统一管理，适合生产环境：

```bash
helm repo add nvidia https://helm.ngc.nvidia.com/nvidia
helm repo update

helm install --wait --generate-name \
    -n gpu-operator --create-namespace \
    nvidia/gpu-operator
```

GPU Operator 可以在节点上自动安装 NVIDIA 驱动，减少手动维护驱动、运行时和监控组件的工作量。

## 四、验证部署效果

部署完成后，分三步验证：

```bash
# 第一步：检查节点资源
kubectl describe node <gpu-node> | grep nvidia.com
# 预期输出：nvidia.com/gpu: 8（或节点实际的卡数）

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

如果 `kubectl describe node` 中仍然没有 `nvidia.com/gpu`，按以下顺序排查：

| 排查顺序 | 检查项 | 命令 |
| --- | --- | --- |
| ① | 驱动是否正常 | `nvidia-smi` |
| ② | 节点是否有 GPU 硬件 | `lspci \| grep -i nvidia` |
| ③ | Device Plugin Pod 是否 Running | `kubectl get pods -n kube-system -l app=nvidia-device-plugin` |
| ④ | Device Plugin 日志是否有错误 | `kubectl logs -n kube-system -l app=nvidia-device-plugin` |
| ⑤ | Kubelet 是否重启过 | `systemctl status kubelet` |

## 五、常见报错与解法

### 报错一：`no GPU found`

这表示驱动层没有检测到 GPU。先运行 `nvidia-smi` 检查驱动；如果驱动正常但 Device Plugin 仍报错，检查 Device Plugin 容器是否以 `privileged: true` 运行，以及是否能访问宿主机的 `/dev/nvidia*` 设备文件。

### 报错二：`failed to start container: Unknown runtime specified nvidia`

这表示容器运行时未配置 nvidia runtime。检查 `/etc/containerd/config.toml` 的 `runtimes` 配置，确保包含 nvidia；补齐后重启 containerd。

### 报错三：节点上报的 GPU 数量为 0

检查 GPU 是否被其他进程占用，例如 `nvidia-persistenced` 服务；同时检查 Device Plugin 版本与驱动版本是否兼容。文章给出的示例是驱动 535.x 配合 Device Plugin v0.14.x。

## 六、Device Plugin 的运行时行为

Device Plugin 不是一次性的初始化工具，而是一个持续运行的 DaemonSet：

- **启动时**：扫描节点所有 GPU，通过 NVML 读取 UUID、型号、显存等信息
- **运行中**：监听 Kubelet 的 Allocate 请求，在 Pod 需要 GPU 时完成设备挂载
- **异常时**：如果 GPU 设备发生变化（如热插拔），需要重启 Device Plugin 才能重新扫描

默认情况下，Device Plugin 每 30 秒重新扫描一次 GPU 设备状态，可通过启动参数 `-scan-interval` 调整。GPU 设备变化频繁的环境可以改为 10 秒，普通环境保持默认值即可。

## 七、总结

- **Device Plugin 不解决调度问题**：它只解决 GPU 资源可见性问题；调度策略由 `kube-scheduler` 决定。
- **加速硬件都需要相应的 Device Plugin**：不仅 GPU 节点需要，AMD GPU、Intel FPGA 等设备也需要对应插件向 K8s 上报资源。
- **生产环境优先考虑 GPU Operator**：单独部署 Device Plugin 虽然简单，但驱动、监控和运行时升级容易碎片化；GPU Operator 可通过 Helm 统一管理和回滚。
- **避免长期使用静态 YAML**：生产环境使用 Helm 或 GPU Operator，便于版本管理，避免多份旧 YAML 混淆实际运行版本。
