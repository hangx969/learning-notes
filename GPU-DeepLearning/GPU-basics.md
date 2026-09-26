---
title: GPU 基础与环境配置
tags:
  - GPU
  - NVIDIA
  - CUDA
  - kubernetes
  - docker
aliases:
  - GPU基础
  - GPU环境配置
---

# GPU 基础与环境配置

## 延伸阅读

### GPU 入门

- [GPU 入门介绍（一）](https://mp.weixin.qq.com/s/V4mMjzQ261kk6qmyH-STUQ)
- [GPU 入门介绍（二）](https://mp.weixin.qq.com/s/nfDY6DezdsN0VHDmRbA9pw)

### GPU 型号

- [各种型号GPU介绍（一）](https://mp.weixin.qq.com/s/W--q1TZ38p83VTrSEQNqmQ)
- [各种型号GPU介绍（二）](https://mp.weixin.qq.com/s/w5vTAG8Wy13VJhH9f7xiWg)

### CUDA 环境安装

- [CUDA 环境安装（一）](https://mp.weixin.qq.com/s?__biz=MzAwMDQyOTcwOA==&mid=2247485712&idx=1&sn=0209d54687ae5f729d3a254e89f7d043&chksm=9ae852f3ad9fdbe5a8a4df3cba7cb88833635e3a908318f2f2e04fde4bd89de0b8910200df51&cur_album_id=3097728928959414276&scene=189#wechat_redirect)
- [CUDA 环境安装（二）](https://mp.weixin.qq.com/s?__biz=MzAwMDQyOTcwOA==&mid=2247485768&idx=1&sn=e1d4a6ae7dd65307f9a11e4ae278ce92&chksm=9ae852abad9fdbbdb30766aeb7a975e4ab2dea906eaaa705119aa509c5948f1f60a48fa140ef&cur_album_id=3097728928959414276&scene=189#wechat_redirect)
- [CUDA 环境安装（三）](https://mp.weixin.qq.com/s?__biz=MzAwMDQyOTcwOA==&mid=2247485778&idx=1&sn=9b69e83eb5f313e8cf25f513a9fe902f&chksm=9ae852b1ad9fdba7bd20d9ed97904121402b1e4fb34d01c30060e839a520926716d5343cfdb8&cur_album_id=3097728928959414276&scene=189#wechat_redirect)

### CUDA Hello World

- [CUDA Hello-world 示例](https://mp.weixin.qq.com/s?__biz=MzAwMDQyOTcwOA==&mid=2247485742&idx=1&sn=6babcfdbf75aa43555a3a457a4a42c69&chksm=9ae852cdad9fdbdbff41a2e8c9bf89f2100d0704524267bbee6e4536c44aaa1307142faa4e75&cur_album_id=3097728928959414276&scene=189#wechat_redirect)

### nvidia-smi

- [nvidia-smi 使用说明](https://mp.weixin.qq.com/s?__biz=MzAwMDQyOTcwOA==&mid=2247485728&idx=1&sn=d4bb3891dd1ccb855cbc94beeb55410a&chksm=9ae852c3ad9fdbd509e2496aad06e2c3aec731d5586be9d95ce85f0bbef6a1ba6127bf02565a&cur_album_id=3097728928959414276&scene=189#wechat_redirect)

## 环境配置

> [!info] 不同环境的 GPU 配置要求
> - 裸机：安装 NVIDIA GPU 驱动；需要本地编译 CUDA 程序时，再安装 CUDA Toolkit。
> - Docker：在宿主机安装 NVIDIA Container Toolkit，并配置 Docker 运行时；容器镜像可自带 CUDA Toolkit。
> - Kubernetes：安装对应的 Device Plugin，让 kubelet 上报 GPU 资源；也可用 GPU Operator 管理 NVIDIA 组件。

### 裸机：配置 NVIDIA GPU

裸机使用 GPU 时，先安装驱动；需要本地开发或编译 CUDA 程序时，再安装 CUDA Toolkit：

- **GPU Driver**：提供 GPU 驱动及 CUDA Driver API。
- **CUDA Toolkit**：包含 CUDA 编译工具、库和运行时组件。

![Image](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202408300938429.webp)

GPU 是 PCIe 设备。安装前先确认系统能识别 GPU：

```sh
lspci | grep NVIDIA
```

#### 安装驱动

从 NVIDIA 官网下载驱动：[NVIDIA 驱动下载](https://www.nvidia.cn/Download/index.aspx?lang=cn#)

以下以 `NVIDIA-Linux-x86_64-550.54.14.run` 为例：

运行安装文件：

```sh
sh NVIDIA-Linux-x86_64-550.54.14.run
```

按安装程序提示完成配置，并留意其兼容性和依赖提示。

运行 `nvidia-smi` 检查驱动是否安装成功。

==注：这里显示的 CUDA 版本表示当前驱动最大支持的 CUDA 版本。==

#### 安装 CUDA Toolkit

需要在宿主机编译 CUDA 程序时，安装 CUDA Toolkit。仅运行自带 CUDA 运行时的容器时，宿主机通常不需要安装 Toolkit。

在 NVIDIA 官网选择操作系统和安装方式：[CUDA Toolkit Archive](https://developer.nvidia.com/cuda-toolkit-archive)

以下以 CUDA 12.2 的 `.run` 安装包为例：

```sh
# 下载安装文件
wget https://developer.download.nvidia.com/compute/cuda/12.2.0/local_installers/cuda_12.2.0_535.54.03_linux.run
# 开始安装
sudo sh cuda_12.2.0_535.54.03_linux.run
# 安装后按提示配置路径
# 添加 CUDA 12.2 到 PATH
export PATH=/usr/local/cuda-12.2/bin:$PATH

# 添加 CUDA 12.2 的 lib64 到 LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/usr/local/cuda-12.2/lib64:$LD_LIBRARY_PATH
# 验证安装
nvcc -V
```

#### 测试程序

下面用一个 PyTorch 程序检查 GPU 和 CUDA 是否可用。

调用链如下：

![Image](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202408301002317.webp)

将以下代码保存为 `check_cuda_pytorch.py`：

```python
import torch

def check_cuda_with_pytorch():
    """检查 PyTorch CUDA 环境是否正常工作"""
    try:
        print("检查 PyTorch CUDA 环境:")
        if torch.cuda.is_available():
            print(f"CUDA 设备可用，当前 CUDA 版本是: {torch.version.cuda}")
            print(f"PyTorch 版本是: {torch.__version__}")
            print(f"检测到 {torch.cuda.device_count()} 个 CUDA 设备。")
            for i in range(torch.cuda.device_count()):
                print(f"设备 {i}: {torch.cuda.get_device_name(i)}")
                print(f"设备 {i} 的显存总量: {torch.cuda.get_device_properties(i).total_memory / (1024 ** 3):.2f} GB")
                print(f"设备 {i} 的显存当前使用量: {torch.cuda.memory_allocated(i) / (1024 ** 3):.2f} GB")
                print(f"设备 {i} 的显存最大使用量: {torch.cuda.memory_reserved(i) / (1024 ** 3):.2f} GB")
        else:
            print("CUDA 设备不可用。")
    except Exception as e:
        print(f"检查 PyTorch CUDA 环境时出现错误: {e}")

if __name__ == "__main__":
    check_cuda_with_pytorch()
```

```sh
# 安装 PyTorch
pip install torch
python3 check_cuda_pytorch.py
```

### Docker：配置 NVIDIA GPU

为了让 Docker 容器中也能使用 GPU，大致步骤如下：

1. 安装 NVIDIA Container Toolkit。
2. 配置 Docker 使用 NVIDIA 运行时。
3. 启动容器时使用 `--gpus` 参数。

#### 安装 NVIDIA Container Toolkit

- NVIDIA Container Toolkit 的主要作用是将 NVIDIA GPU 设备挂载到容器中。

> [!info] 兼容性
> 兼容生态系统中的任意容器运行时，docker、containerd、cri-o 等。

- NVIDIA 官方安装文档：[NVIDIA Container Toolkit Install Guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

- 对于 Ubuntu 系统，安装命令如下：

```sh
# 1. Configure the production repository
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Optionally, configure the repository to use experimental packages
sed -i -e '/experimental/ s/^#//g' /etc/apt/sources.list.d/nvidia-container-toolkit.list

# 2. Update the packages list from the repository
sudo apt-get update

# 3. Install the NVIDIA Container Toolkit packages
sudo apt-get install -y nvidia-container-toolkit
```

#### 配置 Docker

这里以 Docker 为例进行配置：

旧版本可在 `/etc/docker/daemon.json` 中加入以下 `runtimes` 字段（与已有配置合并）：

```json
{
  "runtimes": {
    "nvidia": {
      "args": [],
      "path": "nvidia-container-runtime"
    }
  }
}
```

较新版本可使用 `nvidia-ctk` 配置：

```sh
sudo nvidia-ctk runtime configure --runtime=docker
```

然后重启 Docker：

```sh
sudo systemctl daemon-reload && systemctl restart docker
```

#### 测试

安装 NVIDIA Container Toolkit 后，容器调用链如下：

调用链示意：containerd → NVIDIA Container Runtime → runc。

![Image](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202408301008014.webp)

NVIDIA Container Runtime 在创建容器时加入 GPU 相关配置。Docker 环境中的 CUDA 调用如下：

镜像可以自带 CUDA Toolkit，因此宿主机无需另行安装 Toolkit；宿主机仍需 GPU 驱动和容器工具包。

![Image](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202408301010530.webp)

最后启动容器测试，使用 `--gpus` 指定分配给容器的 GPU：

```sh
# `--gpus all` 分配所有 GPU。
# 多 GPU 场景可用 `--gpus '"device=0"'` 指定 GPU ID（通过 nvidia-smi 查看）。
# 使用包含 CUDA 运行时的镜像执行 nvidia-smi。
docker run --rm --gpus all nvidia/cuda:12.0.1-runtime-ubuntu22.04 nvidia-smi
```

### Kubernetes：手动配置 NVIDIA GPU

- **NVIDIA Device Plugin**：通常以 DaemonSet 运行，向 kubelet 报告节点上的 GPU 资源。
- **DCGM Exporter**：采集 GPU 监控指标。

![Image](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202408301019305.webp)

左图展示手动安装 Device Plugin 和监控组件；右图展示使用 GPU Operator 管理组件。

大致工作流程如下：

1. Device Plugin 向 kubelet 注册并报告可用 GPU；kubelet 将 `nvidia.com/gpu` 的容量和可分配量上报给 API Server。
2. 调度器根据 Pod 申请的 GPU 扩展资源选择满足条件的节点。
3. 节点上的 kubelet 选择具体设备，并调用 Device Plugin 的 `Allocate` 接口，获取容器运行所需的设备和配置。
4. 容器运行时根据这些配置及 NVIDIA Container Toolkit 将 GPU 暴露给容器。

Docker 使用 `--gpus` 指定 GPU；Kubernetes 通过 Pod 资源请求和 Device Plugin 分配 GPU。

#### 安装 Device Plugin

Device Plugin 通常由 GPU 厂商提供。NVIDIA 的实现见 [NVIDIA/k8s-device-plugin](https://github.com/NVIDIA/k8s-device-plugin)。以下示例安装指定版本的清单：

```sh
kubectl create -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.15.0/deployments/static/nvidia-device-plugin.yml
```

Device Plugin 向 kubelet 报告 GPU 设备后，节点资源容量中会出现 `nvidia.com/gpu`。例如：

```sh
kubectl describe node test | grep -A7 Capacity
Capacity:
  cpu:                48
  ephemeral-storage:  460364840Ki
  hugepages-1Gi:      0
  hugepages-2Mi:      0
  memory:             98260824Ki
  nvidia.com/gpu:     2
  pods:               110
```

#### 安装 GPU 监控

监控集群 GPU 使用情况时，可部署 [DCGM Exporter](https://github.com/NVIDIA/dcgm-exporter)，并由 Prometheus 抓取指标：

```sh
helm repo add gpu-helm-charts \
  https://nvidia.github.io/dcgm-exporter/helm-charts

helm repo update

helm install \
    --generate-name \
    gpu-helm-charts/dcgm-exporter
```

查看指标：

```sh
curl -sL http://127.0.0.1:8080/metrics
```

#### 测试

Pod 可通过 `resources.limits` 申请 GPU 扩展资源。下面的示例申请 1 个 GPU：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: gpu-pod
spec:
  restartPolicy: Never
  containers:
    - name: cuda-container
      image: nvcr.io/nvidia/k8s/cuda-sample:vectoradd-cuda10.2
      resources:
        limits:
          nvidia.com/gpu: 1 # requesting 1 GPU
```

`kube-scheduler` 会据此选择有足够 GPU 资源的节点。

### Kubernetes：使用 GPU Operator

手动维护多节点的 GPU 驱动、Container Toolkit 等组件较繁琐。[NVIDIA GPU Operator](https://github.com/NVIDIA/gpu-operator) 可按配置管理驱动、Container Toolkit、Device Plugin 与监控组件。

> [!tip] GPU Operator 优势
> GPU Operator 用于管理 NVIDIA GPU 软件栈，减少 Kubernetes 集群中的手动安装与配置。

#### 组件介绍

NVIDIA GPU Operator 涉及以下组件：

- **NFD（Node Feature Discovery）**：发现节点硬件和系统特征并添加标签；参见 [kubernetes-sigs/node-feature-discovery](https://github.com/kubernetes-sigs/node-feature-discovery)。
- **GFD（GPU Feature Discovery）**：将 GPU 型号、驱动版本等属性写入节点标签；参见 [NVIDIA/gpu-feature-discovery](https://github.com/NVIDIA/gpu-feature-discovery) 和 [GFD 文档](https://github.com/NVIDIA/k8s-device-plugin/tree/main/docs/gpu-feature-discovery)。
- **NVIDIA Driver Installer**：按配置在节点上安装 NVIDIA GPU 驱动。
- **NVIDIA Container Toolkit Installer**：安装并配置容器运行时所需的 NVIDIA 工具。
- **NVIDIA Device Plugin**：将 GPU 作为 Kubernetes 扩展资源提供给 Pod；参见 [NVIDIA/k8s-device-plugin](https://github.com/NVIDIA/k8s-device-plugin)。
- **DCGM Exporter**：采集温度、显存和使用率等指标，供 Prometheus 与 Grafana 使用；参见 [NVIDIA/dcgm-exporter](https://github.com/NVIDIA/dcgm-exporter)。

#### 工作原理

NFD 发现节点硬件和系统信息，GFD 提供 GPU 属性标签。Operator 根据节点标签决定各组件的部署。

1. Driver Installer 和 Container Toolkit Installer 按配置准备节点上的驱动与容器运行时。
2. Device Plugin 报告 GPU 扩展资源，供 Kubernetes 调度与分配。
3. DCGM Exporter 以 Prometheus 指标格式暴露 GPU 监控数据。

> [!tip] 自动化
> 这些组件基本就把需要手动配置的东西都自动化了。

Driver、Toolkit、Device Plugin、GFD 和 DCGM Exporter 等组件按各自依赖与节点标签部署。实际启用项和顺序取决于 Operator 版本及配置；遇到组件未就绪时，应查看对应 Pod 与 Operator 日志。

#### GFD 与 NFD

- GFD：GPU Feature Discovery
- NFD：Node Feature Discovery

NFD 和 GFD 分别发现节点特征与 GPU 信息，并将其作为节点标签提供。

NFD 标签通常以 `feature.node.kubernetes.io` 为前缀，例如：

```sh
feature.node.kubernetes.io/cpu-cpuid.ADX=true
feature.node.kubernetes.io/system-os_release.ID=ubuntu
feature.node.kubernetes.io/system-os_release.VERSION_ID.major=22
feature.node.kubernetes.io/system-os_release.VERSION_ID.minor=04
feature.node.kubernetes.io/system-os_release.VERSION_ID=22.04
```

GFD 标签主要记录 GPU 信息，例如：

```sh
nvidia.com/cuda.runtime.major=12
nvidia.com/cuda.runtime.minor=2
nvidia.com/cuda.driver.major=535
nvidia.com/cuda.driver.minor=161
nvidia.com/gpu.product=Tesla-T4
nvidia.com/gpu.memory=15360
```

#### Driver Installer

GPU Operator 可通过驱动容器在节点上安装 NVIDIA 驱动。

使用驱动容器时，架构如下：

![Image](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202408301046058.webp)

以下是某一环境中的驱动 DaemonSet 与镜像示例：

  ```sh
  kubectl get ds nvidia-driver-daemonset-5.15.0-105-generic-ubuntu22.04 -o yaml | grep image
          image: nvcr.io/nvidia/driver:535-5.15.0-105-generic-ubuntu22.04
  ```

上述名称和镜像标签包含以下信息：

  - nvidia-driver-daemonset 这部分为前缀
  - 5.15.0-105-generic 为内核版本，使用`uname -r` 命令查看
  - ubuntu22.04 操作系统版本，使用`cat /etc/os-release` 命令查看
  - 535：这个是 GPU Driver 的版本号，这里表示安装 535 版本驱动，在部署时可以指定。

  GPU Operator 会依据节点系统和内核选择或构建驱动组件。使用 Operator 的驱动容器时，应核对官方文档中的操作系统版本及驱动支持要求；DaemonSet 并不要求所有节点内核版本完全一致。

  > [!tip] 手动安装驱动的节点
  > 如果节点已预装驱动，Operator 可检测并跳过安装；仍须核对 GPU Operator、驱动和节点系统的兼容性。

#### NVIDIA Container Toolkit Installer

- 该组件用于安装 NVIDIA Container Toolkit。

手动安装的时候有两个步骤：

- 安装 NVIDIA Container Toolkit
- 修改 Runtime 配置指定使用 nvidia-runtime

在整个调用链中新增 nvidia-container-runtime，以便处理 GPU 相关操作。这个 Installer 做的操作也就是这两步：

- 将 Toolkit 的工具和库部署到 `/usr/local/nvidia/toolkit` 目录。
- 在 `/usr/local/nvidia/toolkit/.config/nvidia-container-runtime` 中创建 `config.toml`，将 `nvidia-container-cli.root` 设为 `/run/nvidia/driver`。

> 详细工作原理：[Container Toolkit 工作原理详解](https://mp.weixin.qq.com/s/vAPL48cs8pBzsqwlUi1-wA)

#### 部署要求

> [GPU Operator 安装指南](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/getting-started.html#operator-install-guide)

- 使用 Operator 的 NVIDIA 驱动容器时，按官方文档核对工作节点的操作系统版本要求；预装驱动可支持不同操作系统的节点。
- 确认容器运行时在所选 Operator 版本的支持范围内。
- 如果启用了 Pod Security Admission (PSA)，需要允许 `gpu-operator` 命名空间运行特权 Pod：

```sh
kubectl create ns gpu-operator
kubectl label --overwrite ns gpu-operator pod-security.kubernetes.io/enforce=privileged
```

- 如果集群已运行 NFD，在安装 GPU Operator 时设置 `nfd.enabled=false`，避免重复部署。以下命令检查节点是否存在 NFD 标签：

```sh
kubectl get nodes -o json | jq '.items[].metadata.labels | keys | any(startswith("feature.node.kubernetes.io"))'
```

返回 `true` 表示节点已有 NFD 特征标签；还需结合集群中的 NFD 工作负载确认标签来源。

#### Helm 部署

> [GPU Operator 安装指南](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/getting-started.html#operator-install-guide)

```sh
# 添加 nvidia helm 仓库并更新
helm repo add nvidia https://helm.ngc.nvidia.com/nvidia \
    && helm repo update
# 以默认配置安装
helm install --wait --generate-name \
    -n gpu-operator --create-namespace \
    nvidia/gpu-operator

# 如果提前手动安装了 gpu 驱动，operator 中要禁止 gpu 安装
helm install --wait --generate-name \
     -n gpu-operator --create-namespace \
     nvidia/gpu-operator \
     --set driver.enabled=false
```

安装后，Operator 会按配置部署驱动相关 Pod。对于预装驱动的节点，驱动 Pod 的初始化逻辑会检测已安装的驱动，并避免重复安装。

- 需要安装驱动的节点会启用对应的驱动组件，具体节点标签以实际 Operator 版本为准。
- 已预装驱动的节点可由驱动 Pod 的初始化逻辑检测并跳过安装；需要对整个集群禁用驱动部署时，使用 `--set driver.enabled=false`。

> 当然，并不是每个操作系统+内核版本的组合，NVIDIA 都提供了对应的镜像，可以提前在 **NVIDIA/driver tags** 查看当前 NVIDIA 提供的驱动版本。[NVIDIA Driver Tags (NGC)](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/driver/tags)

#### 测试

- 部署后检查 `gpu-operator` 命名空间中的 Pod；预期状态取决于已启用组件和工作负载类型。

- 如启用了驱动容器，可进入对应驱动 Pod 执行 `nvidia-smi` 检查驱动。

- 查看节点：`kubectl get node xxx -o yaml`，确认 `capacity` 中包含 `nvidia.com/gpu`。

- 创建一个测试 Pod，申请一个 GPU：

  ```yaml
  apiVersion: v1
  kind: Pod
  metadata:
    name: cuda-vectoradd
  spec:
    restartPolicy: OnFailure
    containers:
    - name: cuda-vectoradd
      image: "nvcr.io/nvidia/k8s/cuda-sample:vectoradd-cuda11.7.1-ubuntu20.04"
      resources:
        limits:
          nvidia.com/gpu: 1
  ```

- 成功时，测试 Pod 日志示例如下：

  ```sh
  kubectl logs pod/cuda-vectoradd
  [Vector addition of 50000 elements]
  Copy input data from the host memory to the CUDA device
  CUDA kernel launch with 196 blocks of 256 threads
  Copy output data from the CUDA device to the host memory
  Test PASSED
  Done
  ```
