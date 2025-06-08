# 教程文章

GPU介绍：

- https://mp.weixin.qq.com/s/V4mMjzQ261kk6qmyH-STUQ
- https://mp.weixin.qq.com/s/nfDY6DezdsN0VHDmRbA9pw

各种型号GPU：

- https://mp.weixin.qq.com/s/W--q1TZ38p83VTrSEQNqmQ
- https://mp.weixin.qq.com/s/w5vTAG8Wy13VJhH9f7xiWg

CUDA环境安装：

- https://mp.weixin.qq.com/s?__biz=MzAwMDQyOTcwOA==&mid=2247485712&idx=1&sn=0209d54687ae5f729d3a254e89f7d043&chksm=9ae852f3ad9fdbe5a8a4df3cba7cb88833635e3a908318f2f2e04fde4bd89de0b8910200df51&cur_album_id=3097728928959414276&scene=189#wechat_redirect
- https://mp.weixin.qq.com/s?__biz=MzAwMDQyOTcwOA==&mid=2247485768&idx=1&sn=e1d4a6ae7dd65307f9a11e4ae278ce92&chksm=9ae852abad9fdbbdb30766aeb7a975e4ab2dea906eaaa705119aa509c5948f1f60a48fa140ef&cur_album_id=3097728928959414276&scene=189#wechat_redirect
- https://mp.weixin.qq.com/s?__biz=MzAwMDQyOTcwOA==&mid=2247485778&idx=1&sn=9b69e83eb5f313e8cf25f513a9fe902f&chksm=9ae852b1ad9fdba7bd20d9ed97904121402b1e4fb34d01c30060e839a520926716d5343cfdb8&cur_album_id=3097728928959414276&scene=189#wechat_redirect

CUDA Hello-world

- https://mp.weixin.qq.com/s?__biz=MzAwMDQyOTcwOA==&mid=2247485742&idx=1&sn=6babcfdbf75aa43555a3a457a4a42c69&chksm=9ae852cdad9fdbdbff41a2e8c9bf89f2100d0704524267bbee6e4536c44aaa1307142faa4e75&cur_album_id=3097728928959414276&scene=189#wechat_redirect

nvidia-smi：

- https://mp.weixin.qq.com/s?__biz=MzAwMDQyOTcwOA==&mid=2247485728&idx=1&sn=d4bb3891dd1ccb855cbc94beeb55410a&chksm=9ae852c3ad9fdbd509e2496aad06e2c3aec731d5586be9d95ce85f0bbef6a1ba6127bf02565a&cur_album_id=3097728928959414276&scene=189#wechat_redirect

# 环境配置

> - 对于裸机环境，只需要安装对应的 GPU Driver 以及 CUDA Toolkit 。
>
>
> - 对应 Docker 环境，需要额外安装 nvidia-container-toolkit 并配置 docker 使用 nvidia runtime。
>
>
> - 对应 k8s 环境，需要额外安装对应的 device-plugin 使得 kubelet 能够感知到节点上的 GPU 设备，以便 k8s 能够进行 GPU 管理。注：一般在 k8s 中使用都会直接使用 gpu-operator 方式进行安装，
>

## 裸机环境配置NVIDIA GPU

裸机使用GPU需要安装：

- `GPU Driver`：GPU Driver 包括了 GPU 驱动和 CUDA 驱动

- `CUDA Toolkit`：CUDA Toolkit 则包含了 CUDA Runtime

![Image](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202408300938429.webp)

- GPU 作为一个 PCIE 设备，只要安装好之后，在系统中就可以通过 lspci 命令查看到，先确认机器上是否有 GPU：

~~~sh
lspci|grep NVIDIA
~~~

### 安装驱动

- NVIDIA官网下载驱动：*https://www.nvidia.cn/Download/index.aspx?lang=cn#*

- 最终下载得到的是一个.run 文件，例如 NVIDIA-Linux-x86_64-550.54.14.run。


- 然后直接 sh 方式运行该文件即可


```sh
sh NVIDIA-Linux-x86_64-550.54.14.run
```

- 接下来会进入图形化界面，一路选择 yes / ok 就好

- 运行以下命令检查是否安装成功：`nvidia-smi`

==注：这里显示的 CUDA 版本表示当前驱动最大支持的 CUDA 版本。==

### 安装CUDA toolkit

- 对于深度学习程序，一般都要依赖 CUDA 环境，因此需要在机器上安装 CUDA Toolkit。


- 也是到NVIDIA官网下载对应的安装包，选择操作系统和安装方式即可：*https://developer.nvidia.com/cuda-toolkit-archive*

- 也是.run文件直接安装即可

~~~sh
# 下载安装文件
wget https://developer.download.nvidia.com/compute/cuda/12.2.0/local_installers/cuda_12.2.0_535.54.03_linux.run
# 开始安装
sudo sh cuda_12.2.0_535.54.03_linux.run
#安装完成根据安装提示配置路径
# 添加 CUDA 12.2 到 PATH
export PATH=/usr/local/cuda-12.2/bin:$PATH

# 添加 CUDA 12.2 的 lib64 到 LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/usr/local/cuda-12.2/lib64:$LD_LIBRARY_PATH
#验证安装
nvcc -V
~~~

### 测试程序

- 我们使用一个简单的 Pytorch 程序来检测 GPU 和 CUDA 是否正常。

- 整个调用链大概是这样的：

  ![Image](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202408301002317.webp)

~~~sh
vim check_cuda_pytorch.py
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
~~~

~~~sh
#安装torch
pip install torch
python3 check_cuda_pytorch.py
~~~

## docker环境配置NVIDIA GPU

为了让 Docker 容器中也能使用 GPU，大致步骤如下：

1. 安装 nvidia-container-toolkit 组件
2. docker 配置使用 nvidia-runtime
3. 启动容器时增加 --gpu 参数

### **安装 nvidia-container-toolkit**

- NVIDIA Container Toolkit 的主要作用是将 NVIDIA GPU 设备挂载到容器中。

> 兼容生态系统中的任意容器运行时，docker、containerd、cri-o 等。

- NVIDIA 官方安装文档：*https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html*

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

### 配置docker

这里以 Docker 为例进行配置：

- 旧版本需要手动在 `/etc/docker/daemon.json` 中增加配置，指定使用 nvidia 的 runtime。

```json
    "runtimes": {
        "nvidia": {
            "args": [],
            "path": "nvidia-container-runtime"
        }
    }
```

- 新版 toolkit 带了一个`nvidia-ctk` 工具，执行以下命令即可一键配置：

```sh
sudo nvidia-ctk runtime configure --runtime=docker
```

- 然后重启 Docker 即可

```sh
sudo systemctl daemon-reload && systemctl restart docker
```

### 测试

- 安装nvidia-container-toolkit 后，整个调用链如下：

  - 调用链从 containerd --> runC 变成 containerd --> nvidia-container-runtime --> runC 。

  ![Image](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202408301008014.webp)

- 然后 nvidia-container-runtime 在中间拦截了容器 spec，就可以把 gpu 相关配置添加进去，再传给 runC 的 spec 里面就包含 gpu 信息了。Docker 环境中的 CUDA 调用大概是这样的：

  - 从图中可以看到，CUDA Toolkit 跑到容器里了，因此宿主机上不需要再安装 CUDA Toolkit。使用一个带 CUDA Toolkit 的镜像即可。

  ![Image](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202408301010530.webp)

- 最后我们启动一个 Docker 容器进行测试，其中命令中增加 --gpu参数来指定要分配给容器的 GPU。

~~~sh
#--gpu 参数可选值：
#--gpus all：表示将所有 GPU 都分配给该容器
#--gpus "device=<id>[,<id>...]"：对于多 GPU 场景，可以通过 id 指定分配给容器的 GPU，例如 --gpu "device=0" 表示只分配 0 号 GPU 给该容器, GPU 编号则是通过nvidia-smi 命令进行查看
#这里我们直接使用一个带 cuda 的镜像来测试，启动该容器并执行nvidia-smi 命令
docker run --rm --gpus all  nvidia/cuda:12.0.1-runtime-ubuntu22.04 nvidia-smi
#正常情况下应该是可以打印出容器中的 GPU 信息的。
~~~

## k8s配置NVIDIA GPU--手动安装

- `gpu-device-plugin` 用于管理 GPU，device-plugin 以 DaemonSet 方式运行到集群各个节点，以感知节点上的 GPU 设备，从而让 k8s 能够对节点上的 GPU 设备进行管理。
- `gpu-exporter`：用于监控 GPU

![Image](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202408301019305.webp)

左图为手动安装的场景，只需要在集群中安装 device-plugin 和 监控即可使用；右图为使用 gpu-operotar 安装场景。

大致工作流程如下：

- 每个节点的 kubelet 组件维护该节点的 GPU 设备状态（哪些已用，哪些未用）并定时报告给调度器，调度器知道每一个节点有多少张 GPU 卡可用。
- 调度器为 pod 选择节点时，从符合条件的节点中选择一个节点。
- 当 pod 调度到节点上后，kubelet 组件为 pod 分配 GPU 设备 ID，并将这些 ID 作为参数传递给 NVIDIA Device Plugin
- NVIDIA Device Plugin 将分配给该 pod 的容器的 GPU 设备 ID 写入到容器的环境变量 NVIDIA_VISIBLE_DEVICES 中，然后将信息返回给 kubelet。
- kubelet 启动容器。
- NVIDIA Container Toolkit 检测容器的 spec 中存在环境变量 NVIDIA_VISIBLE_DEVICES，然后根据环境变量的值将 GPU 设备挂载到容器中。

在 Docker 环境我们在启动容器时通过 `--gpu` 参数手动指定分配给容器的 GPU，k8s 环境则由 device-plugin 自行管理。

### 安装device-plugin

- device-plugin 一般由对应的 GPU 厂家提供，比如 NVIDIA 的：*https://github.com/NVIDIA/k8s-device-plugin*。安装其实很简单，将对应的 yaml apply 到集群即可。

```sh
kubectl create -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.15.0/deployments/static/nvidia-device-plugin.yml
```

- device-plugin 启动之后，会感知节点上的 GPU 设备并上报给 kubelet，最终由 kubelet 提交到 kube-apiserver。

  因此我们可以在 Node 可分配资源中看到 GPU，就像这样：

  ```sh
  k describe node test|grep Capacity -A7
  Capacity:
    cpu:                48
    ephemeral-storage:  460364840Ki
    hugepages-1Gi:      0
    hugepages-2Mi:      0
    memory:             98260824Ki
    nvidia.com/gpu:     2
    pods:               110
  #除了常见的 cpu、memory 之外，还有nvidia.com/gpu, 这个就是 GPU 资源
  ```

### 安装GPU监控

- 除此之外，如果你需要监控集群 GPU 资源使用情况，你可能还需要安装 **DCCM exporter**：*https://github.com/NVIDIA/dcgm-exporter* ，结合 Prometheus 输出 GPU 资源监控信息。

```sh
helm repo add gpu-helm-charts \
  https://nvidia.github.io/dcgm-exporter/helm-charts

 helm repo update

 helm install \
    --generate-name \
    gpu-helm-charts/dcgm-exporter
```

- 查看 metrics

```sh
curl -sL http://127.0.0.1:8080/metrics
```

### 测试

- 在 k8s 创建 Pod 要使用 GPU 资源很简单，和 cpu、memory 等常规资源一样，在 resource 中 申请即可。比如，下面这个 yaml 里面我们就通过 resource.limits 申请了该 Pod 要使用 1 个 GPU。

~~~yaml
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
~~~

- 这样 kueb-scheduler 在调度该 Pod 时就会考虑到这个情况，将其调度到有 GPU 资源的节点。

## k8s配置NVIDIA GPU--operator

- 需要在节点上安装 GPU Driver、Container Toolkit 等组件，当集群规模较大时还是比较麻烦的。为了解决这个问题，NVIDIA 推出了 GPU Operator，旨在简化在 Kubernetes 环境中使用 GPU 的过程，通过自动化的方式处理 GPU 驱动程序安装、Controller Toolkit、Device-Plugin 、监控等组件。*https://github.com/NVIDIA/gpu-operator*

> 基本上把需要手动安装、配置的地方全部自动化处理了，极大简化了 k8s 环境中的 GPU 使用。
>
> ps：只有 NVIDIA GPU 可以使用，其他厂家现在基本还是手动安装。

### 组件介绍

NVIDIA GPU Operator 总共包含如下的几个组件：

- **NFD(Node Feature Discovery)**：

  - 用于给节点打上某些标签，这些标签包括 cpu id、内核版本、操作系统版本、是不是 GPU 节点等，其中需要关注的标签是`nvidia.com/gpu.present=true`，如果节点存在该标签，那么说明该节点是 GPU 节点。

  - *https://github.com/kubernetes-sigs/node-feature-discovery*

- **GFD(GPU Feature Discovery)**：

  - 用于收集节点的 GPU 设备属性（GPU 驱动版本、GPU 型号等），并将这些属性以节点标签的方式透出。
  - 在 k8s 集群中以 DaemonSet 方式部署，只有节点拥有标签`nvidia.com/gpu.present=true`时，DaemonSet 控制的 Pod 才会在该节点上运行。*https://github.com/NVIDIA/gpu-feature-discovery*
  - 新版本 GFD 迁移到了 **NVIDIA/k8s-device-plugin**：*https://github.com/NVIDIA/k8s-device-plugin/tree/main/docs/gpu-feature-discovery*

- **NVIDIA Driver Installer**：

  - 基于容器的方式在节点上安装 NVIDIA GPU 驱动，在 k8s 集群中以 DaemonSet 方式部署，只有节点拥有标签`nvidia.com/gpu.present=true`时，DaemonSet 控制的 Pod 才会在该节点上运行。

- **NVIDIA Container Toolkit Installer**：

  - 能够实现在容器中使用 GPU 设备，在 k8s 集群中以 DaemonSet 方式部署，同样的，只有节点拥有标签`nvidia.com/gpu.present=true`时，DaemonSet 控制的 Pod 才会在该节点上运行。

- **NVIDIA Device Plugin**：

  - NVIDIA Device Plugin 用于实现将 GPU 设备以 Kubernetes 扩展资源的方式供用户使用，在 k8s 集群中以 DaemonSet 方式部署，只有节点拥有标签`nvidia.com/gpu.present=true`时，DaemonSet 控制的 Pod 才会在该节点上运行。
  - *https://github.com/NVIDIA/k8s-device-plugin*

- **DCGM Exporter**：

  - 周期性的收集节点 GPU 设备的状态（当前温度、总的显存、已使用显存、使用率等）并暴露 Metrics，结合 Prometheus 和 Grafana 使用。
  - 在 k8s 集群中以 DaemonSet 方式部署，只有节点拥有标签`nvidia.com/gpu.present=true`时，DaemonSet 控制的 Pod 才会在该节点上运行。
  - *https://github.com/NVIDIA/dcgm-exporter*

### 工作原理

- 首先是 GFD、NFD，二者都是用于发现 Node 上的信息，并以 label 形式添加到 k8s node 对象上，特别是 GFD 会添加`nvidia.com/gpu.present=true` 标签表示该节点有 GPU，只有携带该标签的节点才会安装后续组件。

- 然后则是 Driver Installer、Container Toolkit Installer 用于安装 GPU 驱动和 container toolkit。

- 接下来这是 device-plugin 让 k8s 能感知到 GPU 资源信息便于调度和管理。

- 最后的 exporter 则是采集 GPU 监控并以 Prometheus Metrics 格式暴露，用于做 GPU 监控。

> 这些组件基本就把需要手动配置的东西都自动化了。

NVIDIA GPU Operator 依如下的顺序部署各个组件，并且如果前一个组件部署失败，那么其后面的组件将停止部署：

- NVIDIA Driver Installer
- NVIDIA Container Toolkit Installer
- NVIDIA Device Plugin
- DCGM Exporter
- GFD

每个组件都是以 DaemonSet 方式部署，并且只有当节点存在标签 nvidia.com/gpu.present=true 时，各 DaemonSet 控制的 Pod 才会在节点上运行。

```sh
nvidia.com/gpu.deploy.driver=pre-installed
```

### **GFD & NFD**

- GFD：GPU Feature Discovery
- NFD：Node Feature Discovery

根据名称基本能猜到这两个组件的功能，发现节点信息和 GPU 信息并以 Label 形式添加到 k8s 中的 node 对象上。

其中 NFD 添加的 label 以  `feature.node.kubernetes.io` 作为前缀，比如:

```sh
feature.node.kubernetes.io/cpu-cpuid.ADX=true
feature.node.kubernetes.io/system-os_release.ID=ubuntu
feature.node.kubernetes.io/system-os_release.VERSION_ID.major=22
feature.node.kubernetes.io/system-os_release.VERSION_ID.minor=04
feature.node.kubernetes.io/system-os_release.VERSION_ID=22.04
```

对于 GFD 则主要记录 GPU 信息

```sh
nvidia.com/cuda.runtime.major=12
nvidia.com/cuda.runtime.minor=2
nvidia.com/cuda.driver.major=535
nvidia.com/cuda.driver.minor=161
nvidia.com/gpu.product=Tesla-T4
nvidia.com/gpu.memory=15360
```

### **Driver Installer**

- NVIDIA 官方提供了一种基于容器安装 NVIDIA 驱动的方式，GPU Operator 安装 nvidia 驱动也是采用的这种方式。

- 当 NVIDIA 驱动基于容器化安装后，整个架构将演变成图中描述的样子：

![Image](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202408301046058.webp)

- Driver Installer 组件对应的 DaemonSet 就是`nvidia-driver-daemonset-5.15.0-105-generic-ubuntu22.04`，对应的镜像：

  ~~~sh
  k get ds nvidia-driver-daemonset-5.15.0-105-generic-ubuntu22.04 -oyaml|grep image
          image: nvcr.io/nvidia/driver:535-5.15.0-105-generic-ubuntu22.04
  ~~~

- 其中 DaemonSet 名称/镜像由几部分组件：

  - nvidia-driver-daemonset 这部分为前缀
  - 5.15.0-105-generic 为内核版本，使用`uname -r` 命令查看
  - ubuntu22.04 操作系统版本，使用`cat /etc/os-release` 命令查看
  - 535：这个是 GPU Driver 的版本号，这里表示安装 535 版本驱动，在部署时可以指定。

  GPU Operator 会自动根据节点上的内核版本和操作系统生成 DaemonSet 镜像，因为是以 DaemonSet 方式运行的，所有节点上都是跑的同一个 Pod，**==因此要限制集群中的所有 GPU 节点操作系统和内核版本必须一致==**。

  > ps：如果提前手动在节点上安装 GPU 驱动，那么 GPU Operator 检测到之后就不会在该节点上启动 Installer Pod，这样该节点就可以不需要管操作系统和内核版本。

### NVIDIA Container Toolkit Installer

- 该组件用于安装 NVIDIA Container Toolkit。

手动安装的时候有两个步骤：

- 安装 NVIDIA Container Toolkit
- 修改 Runtime 配置指定使用 nvidia-runtime

在整个调用链中新增 nvidia-container-runtime，以便处理 GPU 相关操作。这个 Installer 做的操作也就是这两步：

- 将容器中 NVIDIA Container Toolkit 组件所涉及的命令行工具和库文件移动到/usr/local/nvidia/toolkit 目录下
- 在 /usr/local/nvidia/toolkit/.config/nvidia-container-runtime 创建 nvidia-container-runtime 的配置文件 config.toml，并设置 nvidia-container-cli.root 的值为/run/nvidia/driver。

> 详细工作原理：https://mp.weixin.qq.com/s/vAPL48cs8pBzsqwlUi1-wA

### 要求

> *https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/getting-started.html#operator-install-guide*

1. GPU 节点必须运行相同的操作系统，

- 如果提前手动在节点上安装驱动的话，该节点可以使用不同的操作系统
- CPU 节点操作系统没要求，因为 gpu-operator 只会在 GPU 节点上运行

2. GPU 节点必须配置相同容器引擎，例如都是 containerd 或者都是 docker

3. 如果使用了 Pod Security Admission (PSA) ，需要为 gpu-operator 标记特权模式

```sh
kubectl create ns gpu-operator
kubectl label --overwrite ns gpu-operator pod-security.kubernetes.io/enforce=privileged
```

4. 集群中不要安装 NFD，如果已经安装了需要再安装 gpu-operator 时禁用 NFD 部署。使用以下命令查看集群中是否部署 NFD

```sh
kubectl get nodes -o json | jq '.items[].metadata.labels | keys | any(startswith("feature.node.kubernetes.io"))'
```

- 如果返回 true 则说明集群中安装了 NFD。

### helm部署

> *https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/getting-started.html#operator-install-guide*

~~~sh
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
~~~

完成后 会启动 Pod 安装驱动，如果节点上已经安装了驱动了，那么 gpu-operaotr 就不会启动安装驱动的 Pod,通过 label 进行筛选。

- 没安装驱动的节点会打上 `nvidia.com/gpu.deploy.driver=true` ,表示需要安装驱动
- 已经手动安装过驱动的节点会打上`nvidia.com/gpu.deploy.driver=pre-install`,Daemonset 则不会在该节点上运行

> 当然，并不是每个操作系统+内核版本的组合，NVIDIA 都提供了对应的镜像，可以提前在 **NVIDIA/driver tags**查看当前 NVIDIA 提供的驱动版本。*https://catalog.ngc.nvidia.com/orgs/nvidia/containers/driver/tags*

### 测试

- 部署后，会在`gpu-operator` namespace 下启动相关 Pod，查看一下 Pod 的运行情况，除了一个 `Completed` 之外其他应该都是 Running 状态。

- 然后进入`nvidia-driver-daemonset-xxx` Pod，该 Pod 负责 GPU Driver 的安装，在exec进入该 Pod 中可以执行 `nvidia-smi`命令。

- 查看node信息`kubectl get node xxx -oyaml`，确认 capacity 是否包含 GPU,正常应该是有的

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

- 正常pod日志如下：

  ~~~sh
  kubectl logs pod/cuda-vectoradd
  [Vector addition of 50000 elements]
  Copy input data from the host memory to the CUDA device
  CUDA kernel launch with 196 blocks of 256 threads
  Copy output data from the CUDA device to the host memory
  Test PASSED
  Done
  ~~~

  
