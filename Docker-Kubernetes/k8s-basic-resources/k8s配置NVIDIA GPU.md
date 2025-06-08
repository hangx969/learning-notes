参考：https://mp.weixin.qq.com/s/FXQRAqp8mpuWsBbEY9ZJdw

设置裸金属 Kubernetes 上的 NVIDIA RTX GPU，涵盖 Ubuntu 22.04 上的驱动程序安装、配置和故障排除。

> 译自A Practical Guide to Running NVIDIA GPUs on Kubernetes，作者  Jim Angel。

目标受众：Kubernetes运维人员、机器学习工程师、GPU爱好者

在云端探索GPU的强大性能引发了我将本地NVIDIA GPU与我的Kubernetes家用实验室集群集成的兴趣。

将GPU添加到Kubernetes使我能够运行Jupyter笔记本和AI/ML工作负载。这种方法的最大优势是可移植性；在本地运行的相同笔记本和模型可以轻松地在云端复制。

这个主题对我来说很混乱，我不得不依赖于各种供应商的信息、GitHub问题和 stackoverflow 帖子。

我旨在揭开神秘的面纱，提供一条清晰的道路，让您可以从自己的设置中立即利用GPU加速进行AI/ML工作负载。

## 范围

如果您在跟随：

- 您有一个运行Ubuntu 22.04 LTS的节点
- 您有一个连接到节点的NVIDIA GPU
- 已安装并运行Kubernetes

除非另有说明，否则所有命令都应在上述节点上运行。

## 组件概述

让我们将GPU连接路径的每个步骤分解为更大的组件（**pod/工作负载→Kubernetes→容器运行时→软件→硬件→GPU**）。

我将从上到下涵盖每个组件，然后使用“NEEDS”的反向顺序设置和验证我的GPU加速Kubernetes家用实验室。

下图显示了Kubernetes设置中的GPU连接路径：



![Image](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202403172138361.jpeg)



从**pod/工作负载**开始，容器应包含软件（如CUDA）来利用GPU硬件。我们可以假设容器自动获得带有驱动程序的GPU，但您仍然需要“在顶部”提供SDK/API。NVIDIA**容器运行时**钩子提供了容器GPU设备配置。

### Kubernetes如何知道哪些pod需要GPU？

对于我的**Kubernetes**设置，我通过`spec.runtimeClassName`（运行时类文档）、`spec.containers.resources`（资源配额文档）和`spec.nodeSelector`（nodeSelector文档）的组合在pod/工作负载中声明GPU。例如：

```yaml
spec:
  runtimeClassName: nvidia   #<--- USE THE NVIDIA CONTAINER RUNTIME
  containers:
    resources:
      limits:
        nvidia.com/gpu: 1    #<-- ASSIGN 1 GPU, IF MULTIPLE
  nodeSelector:              #<--- RUN ON GPU ${NODE_NAME}
    kubernetes.io/hostname: ${NODE_NAME}
```

在GPU节点上也经常看到`NoSchedule`taints。这是为了防止没有明确需要GPU的工作负载运行（taints和toleration文档）。要容忍`NoSchedule`taint：

```yaml
spec:
  tolerations:
  - key: nvidia.com/gpu
    operator: Exists
    effect: NoSchedule
```

上面的YAML示例指示Kubernetes在哪里/如何运行工作负载，但是GPU被视为“扩展资源”或“非Kubernetes内置资源”（文档）。必须有一些东西告诉Kubernetes，有X个节点拥有X个可用的GPU。

### Kubernetes如何知道哪些节点有GPU？

许多NVIDIA GPU功能由NVIDIA GPU Operator自动管理，包括一个device-plugin-daemonset部署，该部署通知Kubernetes有关设备容量的信息。（NVIDIA k8s-device-plugin文档）

![image-20240317214222856](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202403172143854.png)

NVIDIA GPU Operator包括：

- （可选）在主机上安装NVIDIA驱动程序的能力
- 用于GPU的Kubernetes设备插件
- （可选）在主机上配置NVIDIA容器运行时的能力
- 自动节点标记
- 基于DCGM（数据中心GPU管理器）的监控等

重要的部分是该 operator 自动为选择器标记节点并评估配额的容量。

NVIDIA设备插件是一个Daemonset，允许您自动：

- 暴露集群中每个节点上的GPU数量
- 跟踪GPU的健康状态
- 在您的Kubernetes集群中运行启用GPU的容器

到目前为止，我们的Kubernetes集群已将工作负载调度到了一个准备好的GPU节点，并提供了对容器运行时的GPU加速`nvidia`runtimeClass的指令。

### nvidia runtimeClass如何暴露GPU？

一个名为NVIDIA容器工具包（文档）的软件包提供了大部分的配置和二进制文件。

在GPU节点上，**容器运行时**（containerd）配置了一个围绕名为`nvidia-container-runtime`的`runc`的包装器（文档）。

![image-20240317214537016](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202403172145590.png)

该包装器（`nvidia-container-runtime`）使用一个预启动钩子进入containerd，通过挂载、环境变量等方式添加主机GPU。

将其想象成将GPU硬件配置注入到容器中，但您仍然需要引入软件（如CUDA）。

以下是用于让containerd使用NVIDIA runtimeClass的示例配置：

```toml
# /etc/containerd/config.toml
[plugins."io.containerd.grpc.v1.cri".containerd.runtimes]
  [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.nvidia]
    privileged_without_host_devices = false
    runtime_engine = ""
    runtime_root = ""
    runtime_type = "io.containerd.runc.v2"
    [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.nvidia.options]
      BinaryName = "/usr/bin/nvidia-container-runtime"
```

所有使用`nvidia`runtimeClass的容器使用上面的配置。

通过`nvidia-ctk`（`nvidia-container-toolkit`中一个糟糕命名的工具子集）自动配置 /etc/containerd/config.toml。稍后会详细介绍。

`nvidia-container-toolkit`和 utilities 负责配置容器运行时，但该过程假设我们已经在主机上配置了GPU。

### Ubuntu如何知道它连接了GPU？

简短的回答是**驱动程序**。驱动程序是操作系统与NVIDIA显卡通信所需的基本软件。

通过包管理器在Ubuntu上安装NVIDIA驱动程序。

NVIDIA驱动程序有两个部分，一个是硬件如何与GPU通信的部分（**硬件/内核**模块），另一个是**软件**如何与GPU通信的部分。

![image-20240317214706001](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202403172147462.png)

我在图片中包含了“CUDA stuff”，因为它可以安装在主机上，但这取决于确切的用例。对于本教程，这不是必需的，并且稍后会讨论。

### 主板如何知道连接了GPU？

这有点是个技巧性的问题。大多数（如果不是全部）消费级GPU都是通过PCIe连接的。

![image-20240317214743459](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202403172147922.png)

当我更深入地思考时，PCIe支持GPU、NVMe、网卡和许多其他外围设备。这只是一种**传输数据的方式**。

主板不需要知道它是GPU，但它确实需要知道通过PCIe插槽连接了某些东西。

> 注意: 如果使用Thunderbolt外部GPU（eGPU），它仍然被视为PCI。“Thunderbolt将PCIe和DisplayPort组合成两个串行信号，并通过单根电缆提供DC电源。”（来源）

现在我们已经了解了所有组件，我们可以按相反的顺序安装和验证本地Kubernetes集群上的GPU。

## 在Kubernetes上配置NVIDIA RTX GPU

从我们上次停下的地方开始，让我们检查物理硬件连接。

### 验证硬件连接

使用lspci，这是一个显示系统中PCI总线和连接到它们的设备信息的实用程序，查找已知的NVIDIA设备。

```sh
# list all PCI devices with the text NVIDIA
sudo lspci | grep NVIDIA
```

一切正常！输出：

```
2f:00.0 VGA compatible controller: NVIDIA Corporation GA106 [GeForce RTX 3060 Lite Hash Rate] (rev a1)
```

### NVIDIA GPU驱动程序注意事项

不仅有许多竞争性的安装相同GPU驱动程序的方法，而且您如何知道要使用哪个版本呢？

**查找正确的驱动程序版本**

使用NVIDIA驱动程序下载网站上的搜索菜单找到要安装的最新推荐版本。

例如，搜索RTX 3060返回：

|      Field       |    Value     |
| :--------------: | :----------: |
|     Version      |  535.154.05  |
|   Release Date   |  2024.1.16   |
| Operating System | Linux 64-bit |
|     Language     | English (US) |
|    File Size     |  325.86 MB   |

这意味着我正在寻找535+的nvidia驱动程序版本。

\###（关于CUDA版本的一条附言）

CUDA是一种额外的软件，可帮助应用程序在NVIDIA GPU上运行。将其视为主机GPU的API。

虽然不需要CUDA软件包进行此设置，但容器中使用的CUDA版本与驱动程序版本之间存在着一种半脆弱的关系。**如果CUDA与您的驱动程序不匹配，可能会导致事情不按预期工作！**

> 提示: 安装驱动程序后，可以运行nvidia-smi检查推荐的CUDA版本，例如nvidia-driver-535输出CUDA 12.2，即使我没有安装CUDA。
>
> 一旦主机上的CUDA版本与容器中的匹配主机驱动程序版本对齐，我的大部分问题都会消失。（CUDA下载）

此外，请注意，CUDA会向您的容器镜像添加大量资源。

如果您决心减小镜像的大小，可以有选择地rm -rf不需要的工具包，但要小心不要删除容器中的应用程序可能使用的库和工具！

### 安装NVIDIA GPU驱动程序

在Ubuntu 22.04 LTS上安装NVIDIA GPU驱动程序有几种流行的方法：

- 通过`ubuntu-drivers install`（文档）安装官方Ubuntu管理的NVIDIA驱动程序
- 通过`.run 文件`（下载）安装官方NVIDIA管理的NVIDIA驱动程序
- 通过`ppa:graphics-drivers/ppa`（文档）安装非官方PPA管理的NVIDIA驱动程序

对于此演练，我使用了最后一个选项（ppa），但请随意替换为您喜欢的方法。我选择PPA是因为它似乎最容易使用。

添加PPA存储库并安装上面找到的驱动程序。

```sh
# add ppa:graphics-driver repo to apt
sudo add-apt-repository ppa:graphics-drivers/ppa --yes
# update apt content list
sudo apt update
# install driver
sudo apt install nvidia-driver-535
```

> 警告: 我遇到了一个问题，Ubuntu的unattended-upgrades自动更新了一些GPU驱动程序依赖项，破坏了我的GPU配置。
>
> 使用sudo apt remove unattended-upgrades修复，但还有其他更不强制性的解决方案。

现在我们已经安装了驱动程序，让我们验证它们是否正常工作。一个快速测试是运行`nvidia-smi`，这是一个为NVIDIA GPU提供监控和管理功能的实用程序。

```sh
# get the driver version
nvidia-smi --query-gpu=driver_version --format=csv,noheader
```

### 验证NVIDIA GPU驱动程序

通过列出所有包（dpkg -l）来验证已安装的具有名称“nvidia”或“535”的包。

```sh
dpkg -l | grep nvidia 
# or
dpkg -l | grep 535
# expected output: non-empty list of packages
```

一切正常！

> 提示：为了防止非计划的包更改，请将它们保留以防止自动升级。

```sh
# any package with nvidia in the name should be held
dpkg-query -W --showformat='${Package} ${Status}\n' | \
grep -v deinstall | \
awk '{ print $1 }' | \
grep -E 'nvidia.*-[0-9]+$' | \
xargs -r -L 1 sudo apt-mark hold
```

输出：

```sh
#...
libnvidia-fbc1-535 set on hold.
libnvidia-gl-535 set on hold.
nvidia-compute-utils-535 set on hold.
nvidia-dkms-535 set on hold.
```

**内核模块已安装吗？驱动程序工作吗？**

模块指示内核如何与连接到它的设备交互。没有任何NVIDIA模块，操作系统不知道如何与硬件通信。

使用`lsmod`，一个列出`/proc/modules`内容的程序，显示当前加载的内核模块。

```sh
# Show the status of driver modules in the Linux Kernel
lsmod | grep nvidia
```

如果您安装了模块，它可能看起来像：

```sh
nvidia_uvm           1511424  12
nvidia_drm             77824  0
nvidia_modeset       1306624  1 nvidia_drm
nvidia              56692736  200 nvidia_uvm,nvidia_modeset
drm_kms_helper        311296  1 nvidia_drm
drm                   622592  4 drm_kms_helper,nvidia,nvidia_drm
```

> 注意: 我正在使用eGPU测试上述输出，模块未显示出来。我以为我对此的理解是错误的，但事实证明我没有插入电缆。
>
> 连接eGPU解决了我的问题，模块出现了。

检查内核驱动程序版本文件：

```sh
cat /proc/driver/nvidia/version
```

一切正常！输出：

```sh
NVRM version: NVIDIA UNIX x86_64 Kernel Module  535.154.05  Thu Dec 28 15:37:48 UTC 2023GCC version:  
gcc version 11.4.0 (Ubuntu 11.4.0-1ubuntu1~22.04)
```

检查已找到的nvidia设备的设备文件：

```sh
# any device files (I/O sys calls)
ls /dev/ | grep 'nvidia[0-9]\+'
```

一切正常！输出：

似乎我们有一个已经配置好的GPU设置的主机，接下来让我们配置containerd以支持GPU运行时。

### 安装NVIDIA容器工具包

我的家庭实验室正在运行Kubernetes v1.28.4，使用containerd。如前所述，我们需要NVIDIA容器工具包（一组实用工具）来

据我所知，这会在您的主机上安装工具，但默认情况下不会配置或更改任何东西。

来自“安装NVIDIA容器工具包”指南。

```sh
# add nvidia-container-toolkit repo to apt sources
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
&& curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
# update apt content
sudo apt update
# install container toolkit
sudo apt install -y nvidia-container-toolkit
```

### 配置 containerd

现在工具已安装好，我们需要更新 containerd 配置的运行时类。幸运的是，其中一个工具，`nvidia-ctk`可以自动化这个过程。

来自“安装NVIDIA容器工具包”指南。

```sh
# options: --dry-run
sudo nvidia-ctk runtime configure --runtime=containerd
# restart containerd
sudo systemctl restart containerd
```

> 注意：您可以通过指定运行时名称（`--nvidia-runtime-name`）、NVIDIA 运行时可执行文件的路径（`--nvidia-runtime-path`）和 NVIDIA 容器运行时钩子可执行文件的路径（`--nvidia-runtime-hook-path`）来自定义 NVIDIA 运行时配置。
>
> 还有一个选项是使用`--nvidia-set-as-default`将 NVIDIA 运行时设置为默认运行时。（来源）

如果您想更深入了解`nvidia-container-runtime`在主机上暴露 GPU 所做的工作，我强烈建议阅读他们在文档中的低级示例。

如果您对这个主题还不厌倦，NVIDIA 的名为“在容器运行时生态系统中启用 GPU”的博客非常棒。

### 验证 containerd

检查配置中是否存在 NVIDIA 运行时。

```sh
sudo cat /etc/containerd/config.toml | grep "containerd.runtimes.nvidia."
```

一切正常！输出：

```sh
[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.nvidia]   [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.nvidia.options]
```

让我们尝试在主机上直接运行一个容器（跳过 Kubernetes）。首先我们需要安装`nerdctl`，它是`docker`的替代品，允许我们使用 --gpus all 参数。

使用预编译版本安装`nerdctl`。

注意我选择的 CUDA 版本，请查看仓库网站获取最新的标签选项：docker.com/r/nvidia/cuda/tags

```sh
# `nvidia-smi` command ran with cuda 12.3
sudo nerdctl run -it --rm --gpus all nvidia/cuda:12.3.1-base-ubuntu20.04 nvidia-smi
# `nvcc -V` command ran with cuda 12.3 (the "12.3.1-base" image doesn't include nvcc)
sudo nerdctl run -it --rm --gpus all nvidia/cuda:12.3.1-devel-ubuntu20.04 nvcc -V
```

一切正常！

> 注意：如果您在一个具有多个 GPU 的机器上，您可以用`--gpus '"device=0,1"'`替换`--gpus all`来测试共享单个 GPU。

```sh
# only use device 0 and 1 out of a possible [0,1,2,3] setup
sudo nerdctl run -it --rm --gpus '"device=0,1"' nvidia/cuda:12.2.2-base-ubuntu22.04 nvidia-smi
```

到目前为止，我们有一个可以在容器运行时上工作的 GPU 节点。

### 使用 helm 安装 NVIDIA GPU Operator

最后一块拼图，我们需要让 Kubernetes 知道我们的节点上有 GPU。

NVIDIA GPU Operator在 Kubernetes 上创建/配置/管理 GPU，并通过 helm chart 安装。

按照官方说明安装 helm。如果您对 helm chart 和 value 感兴趣，这是 Github 仓库。

添加 helm 仓库：

```sh
helm repo add nvidia https://helm.ngc.nvidia.com/nvidia \  && helm repo update
```

在您的 Kubernetes 集群上安装发行版。

默认情况下，Operator 将 NVIDIA 容器工具包和 NVIDIA 驱动程序作为容器部署到系统上。因为我们已经安装了这两个组件，所以我们将这些值设置为 false。

```sh
helm install --wait gpu-operator \
-n gpu-operator --create-namespace \      
nvidia/gpu-operator \      
--set driver.enabled=false \      
--set toolkit.enabled=false
```

确保所有的 pod 都健康地启动：

```sh
# ensure nothing on kubernetes is wonky
kubectl get pods -n gpu-operator | grep -i nvidia
```

一切正常！输出：

```sh
vidia-cuda-validator-4hh2v                                  0/1     Completed   0               3d20h
nvidia-dcgm-exporter-86wcv                                   1/1     Running     5 (7d10h ago)   7d20h
nvidia-device-plugin-daemonset-cxfnc                         1/1     Running     0               26h
nvidia-operator-validator-jhz6j                              1/1     Running     0               3d20h
```

### 验证 GPU Operator

```
kubectl -n gpu-operator logs deployment/gpu-operator | grep GPU
```

这不是一个绝对可靠的测试，但你应该看到`"Number of nodes with GPU label"`,`"NodeCount": NUMBER_OF_EXPECTED_GPU_NODES`的实际值。如果它显示为 0，那么可能有一个需要调试的问题。

有用的调试命令：`kubectl get events -n gpu-operator --sort-by='.lastTimestamp'`

> 提示：当有疑问时（或者当 GPU operator pods 在单个节点上处于 init / terminating 状态，但基础设置正常时）：重新启动节点。

## 将所有内容整合在一起

最后，让我们运行一个 Kubernetes 工作负载来测试我们的集成是否端到端正常工作。

```sh
# EXPORT NODE NAME!
export NODE_NAME=node3

cat <<EOF | kubectl create -f -
apiVersion: batch/v1
kind: Job
metadata:
  name: test-job-gpu
spec:
  template:
    spec:
      runtimeClassName: nvidia
      containers:
      - name: nvidia-test
        image: nvidia/cuda:12.0.0-base-ubuntu22.04
        command: ["nvidia-smi"]
        resources:
          limits:
            nvidia.com/gpu: 1
      nodeSelector:
        kubernetes.io/hostname: ${NODE_NAME}
      restartPolicy: Never
EOF
```

通过日志检查输出：

```sh
kubectl logs job/test-job-gpu
```

期望的输出类似于：

![image-20240317215604385](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202403172156607.png)

祝贺！我们正式拥有一个本地 GPU 加速的 Kubernetes 集群！

## 结论

将 GPU 集成到 Kubernetes 中可能看起来令人望而生畏，因为涉及到复杂的技术层。我希望这个指南能为您解密将 NVIDIA GPU 与 Kubernetes 集成的过程。

总之，在 k8s 上暴露 GPU 包括以下步骤：

1. 安装 NVIDIA GPU 驱动程序（`apt install nvidia-driver-535`）
2. 配置容器运行时（`apt install -y nvidia-container-toolkit & nvidia-ctk runtime configure`）
3. 配置 Kubernetes（`helm install nvidia/gpu-operator`）
4. 更新部署 YAML 来包含 GPU 请求

在未来，我可能会考虑使用`ubuntu-driver`安装程序，并让 Kubernetes GPU Operator 管理驱动程序和容器工具包。

如果您有任何问题、见解或反馈，请随时分享！

## 清理

想要重新开始吗？安装不同的驱动程序？删除所有内容：

```sh
# drain node / remove from cluster

# remove gpu-operator deployment
helm -n gpu-operator list
helm -n gpu-operator delete HELM_RELEASE_NAME

# delete driver packages
sudo apt remove --purge '^nvidia-.*'
sudo apt remove --purge '^libnvidia-.*'

# clean up the uninstall
sudo apt autoremove

# restart containerd
```