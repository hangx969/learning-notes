---
title: Rocky Linux 10 K8s 安装与集群初始化
tags:
  - kubernetes
  - k8s
  - kubeadm
  - calico
  - rocky-linux
  - installation
aliases:
  - K8s 集群初始化
  - kubeadm 初始化
  - k8s 1.35 安装
date: 2026-04-15
---

本文记录在 Rocky Linux 10 上安装 K8s 组件（kubeadm / kubelet / kubectl）、使用 kubeadm 初始化集群、扩容工作节点、安装 Calico 网络插件及配置 NFS 的完整步骤，并附带 homebrew / k9s / helm 等常用工具的安装方法。执行本文步骤前，需先完成 [[rocky-linux10-系统初始化]] 和 [[rocky-linux10-容器运行时安装]]。完整安装流程见 [[安装k8s-1.35-基于rockylinux10-最新步骤]]。

# 组件安装

## K8s 1.35

### 配置 Kubernetes 仓库源

```sh
# 方式一：使用阿里云镜像源（国内推荐，速度快）
cat > /etc/yum.repos.d/kubernetes.repo <<'EOF'
[kubernetes]
name=Kubernetes
baseurl=https://mirrors.aliyun.com/kubernetes-new/core/stable/v1.35/rpm/
enabled=1
gpgcheck=1
gpgkey=https://mirrors.aliyun.com/kubernetes-new/core/stable/v1.35/rpm/repodata/repomd.xml.key
EOF

dnf clean all && dnf makecache

# 方式二：使用官方源（pkgs.k8s.io，需要能访问境外网络）
cat > /etc/yum.repos.d/kubernetes.repo <<'EOF'
[kubernetes]
name=Kubernetes
baseurl=https://pkgs.k8s.io/core:/stable:/v1.35/rpm/
enabled=1
gpgcheck=1
gpgkey=https://pkgs.k8s.io/core:/stable:/v1.35/rpm/repodata/repomd.xml.key
exclude=kubelet kubeadm kubectl cri-tools kubernetes-cni
EOF

dnf clean all && dnf makecache
```

### 安装 kubeadm / kubelet / kubectl

```sh
# Rocky Linux 10 使用 DNF5，--disableexcludes 参数可能需要改为 --setopt=disable_excludes
# 安装时自动识别最新的 1.35.x 版本
dnf install -y kubelet kubeadm kubectl --disableexcludes=kubernetes

# 若使用了 DNF5（Rocky Linux 10 默认），则用以下命令：
# dnf install -y kubelet kubeadm kubectl --setopt=disable_excludes=kubernetes

# 若要安装指定小版本：
# dnf install -y kubelet-1.35.3 kubeadm-1.35.3 kubectl-1.35.3 --disableexcludes=kubernetes

# 启动 kubelet（初始化前会反复重启，属于正常现象）
systemctl enable kubelet --now

# cri-tools（含 crictl）作为 kubelet 的依赖已自动安装，现在配置 crictl
cat > /etc/crictl.yaml <<'EOF'
runtime-endpoint: unix:///run/containerd/containerd.sock
image-endpoint: unix:///run/containerd/containerd.sock
timeout: 10
debug: false
EOF

# 验证 crictl 与 containerd 的连通性
crictl info
```

> [!tip] 离线安装
> 如果无法访问在线源，可以从以下地址下载 rpm 文件手动安装：
> - https://mirrors.aliyun.com/kubernetes-new/core/stable/v1.35/rpm/x86_64/
>
> ```sh
> # 将 rpm 文件下载到 k8s-1.35 目录后：
> rpm -ivh ./*.rpm
> ```

# kubeadm 初始化 K8s 集群

> [!info] kubeadm vs 二进制安装
> - **kubeadm**：官方工具，快速部署，所有组件以 Pod 方式运行，具备故障自恢复能力，推荐自动化场景
> - **二进制**：手动安装，对 Kubernetes 理解更深，适合深度定制
> - 两者均适合生产环境

## 初始化集群

在控制节点（rm1）上执行：

```sh
# 查看默认配置模板（可用于了解所有可配置字段）
kubeadm config print init-defaults
```

创建 kubeadm 配置文件（**注意：K8s 1.35 使用 v1beta4 API**）：

```yaml
tee kubeadm.yaml <<'EOF'
apiVersion: kubeadm.k8s.io/v1beta4
kind: InitConfiguration
localAPIEndpoint:
  advertiseAddress: 192.168.164.100  # 控制节点的 IP
  bindPort: 6443
nodeRegistration:
  criSocket: unix:///run/containerd/containerd.sock  # 指定 containerd 运行时
  imagePullPolicy: IfNotPresent
  imagePullSerial: false  # v1beta4 新增：false 表示并行拉取镜像，加快初始化速度
  name: rm1  # 控制节点主机名
  taints: null
---
apiVersion: kubeadm.k8s.io/v1beta4
kind: ClusterConfiguration
certificatesDir: /etc/kubernetes/pki
clusterName: kubernetes
controllerManager: {}
dns: {}
etcd:
  local:
    dataDir: /var/lib/etcd
imageRepository: registry.cn-hangzhou.aliyuncs.com/google_containers  # 国内镜像源
kubernetesVersion: 1.35.3  # 指定 K8s 版本
networking:
  dnsDomain: cluster.local
  podSubnet: 10.244.0.0/16    # Pod 网段（与 Calico 配置保持一致）
  serviceSubnet: 10.96.0.0/12  # Service 网段
scheduler: {}
# v1beta4 新增：在初始化时就设置更长的证书有效期，避免日后频繁续签
# certificateValidityPeriod 控制非 CA 证书（apiserver、etcd 等），默认 8760h（1 年）
# caCertificateValidityPeriod 控制 CA 证书，默认 87600h（10 年）
certificateValidityPeriod: 87600h
caCertificateValidityPeriod: 175200h
---
apiVersion: kubeproxy.config.k8s.io/v1alpha1
kind: KubeProxyConfiguration
mode: ipvs
---
apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
cgroupDriver: systemd
EOF
```

> [!warning] kubeadm v1beta4 重要变更（相比 v1beta3）
> - **API 版本**：`kubeadm.k8s.io/v1beta4`（v1beta3 已废弃，1.35 不再支持）
> - **新增类型**：`ResetConfiguration`、`UpgradeConfiguration`
> - **`imagePullSerial`**：新字段，`false` = 并行拉取，加快初始化
> - **`extraArgs`**：从 Map 类型改为结构化参数，支持重复键
> - **`timeouts`**：新增超时配置块，替代 `ClusterConfiguration.timeoutForControlPlane`
> - **证书有效期**：新增 `certificateValidityPeriod`（默认 1 年）和 `caCertificateValidityPeriod`（默认 10 年）字段，在 `kubeadm init` 时即可签发长期证书，建议直接设为 10 年以上，减少后期手动续签频率（但不能完全替代续签脚本，存量集群到期后仍需手动续签）

```sh
# 【推荐】init 前先验证 DNS 和镜像仓库的可达性，避免 init 中途因网络失败
nslookup registry.cn-hangzhou.aliyuncs.com
curl -s -o /dev/null -w "%{http_code}" https://registry.cn-hangzhou.aliyuncs.com/v2/

# 【推荐】提前拉取所需镜像，拉取成功再 init，省去 init 阶段的等待和不确定性
kubeadm config images pull \
  --image-repository registry.cn-hangzhou.aliyuncs.com/google_containers \
  --kubernetes-version 1.35.3

# 初始化 master 节点（仅在第一个 master 上执行）
kubeadm init --config=kubeadm.yaml --ignore-preflight-errors=SystemVerification
```

> [!tip] IPVS 模式说明
> 相比默认的 iptables 模式，IPVS 是高性能负载均衡器，在大规模集群下有更好的性能和可靠性，支持四层/七层负载均衡，生产环境建议开启。

初始化成功后，输出的 join 命令需要保存下来，用于工作节点加入集群。

## 配置 kubeconfig

```sh
# admin.conf 是集群的访问凭证，安全起见仅在 master 节点配置
mkdir -p $HOME/.kube
cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
chown $(id -u):$(id -g) $HOME/.kube/config

# 配置 kubectl alias 和自动补全
tee -a ~/.bashrc <<'EOF'
alias k='kubectl'
source <(kubectl completion bash)
complete -o default -F __start_kubectl k
source /etc/profile
EOF

source ~/.bashrc

# 验证集群状态
kubectl get nodes
kubectl get pods -A
```

## 扩容工作节点

在控制节点（rm1）上获取 join 命令：

```sh
kubeadm token create --print-join-command
```

在工作节点（rn1、rn2）上分别执行返回的 join 命令：

```sh
# 示例（替换为实际输出的命令）
kubeadm join 192.168.164.100:6443 \
  --token <token> \
  --discovery-token-ca-cert-hash sha256:<hash> \
  --ignore-preflight-errors=SystemVerification
```

在控制节点给工作节点打角色标签：

```sh
kubectl label nodes rn1 node-role.kubernetes.io/worker=worker
kubectl label nodes rn2 node-role.kubernetes.io/worker=worker
# 验证
kubectl get nodes
```

## 安装 Calico

从官网（[https://docs.tigera.io/calico/latest](https://docs.tigera.io/calico/latest/getting-started/kubernetes/self-managed-onprem/onpremises)）获取最新版 Calico 的 manifest：

```sh
# 下载最新版 calico.yaml（以 v3.31.4 为例，请替换为实际最新版）
curl -O https://raw.githubusercontent.com/projectcalico/calico/v3.31.4/manifests/calico.yaml
```

用 shell 命令指定正确的网卡名称（防止 Calico 使用 lo 地址，导致跨节点通信失败）：

```sh
# 替换为实际网卡名（通过 ip addr 查看）
IFACE="ens160"

# 在 CLUSTER_TYPE 配置段下方插入 IP_AUTODETECTION_METHOD
# 逻辑：匹配 CLUSTER_TYPE 行 → n 跳到下一行（value: "k8s,bgp"）→ 在该行末追加两行新内容
# 加幂等检查，避免重复执行时重复插入
if ! grep -q "IP_AUTODETECTION_METHOD" calico.yaml; then
  sed -i "/- name: CLUSTER_TYPE/{n;s/\(.*\)/\1\n            - name: IP_AUTODETECTION_METHOD\n              value: \"interface=${IFACE}\"/}" calico.yaml
fi

# 验证插入结果
grep -A2 "CLUSTER_TYPE" calico.yaml

kubectl apply -f calico.yaml

# 等待 Calico pod 就绪（所有 pod 变为 Running 状态）
kubectl get pods -n kube-system -w
```

验证网络连通性：

```sh
kubectl run busybox --image busybox:1.28 \
  --image-pull-policy=IfNotPresent \
  --restart=Never --rm -it busybox -- sh
# 容器内测试：
# ping www.baidu.com
# nslookup kubernetes.default.svc.cluster.local
```

## 配置 NFS（nfs-provisioner 前置依赖）

> [!info]
> 如果需要部署 nfs-provisioner 来提供动态 PV，需要先在集群中配置 NFS 服务。PV 本质是先挂载到宿主机、再挂载到 Pod，因此所有节点都需要安装 NFS 客户端。

### 安装 NFS 服务（所有节点）

```sh
# nfs-utils 已在基础软件包中安装，如未安装则执行：
dnf install -y nfs-utils

systemctl start rpcbind && systemctl enable rpcbind
systemctl start nfs-server && systemctl enable nfs-server
```

### 配置 NFS 共享目录（仅 master 节点）

```sh
# 创建 nfs-provisioner 数据目录
mkdir -p /data/nfs_pro

# 添加 NFS 导出配置
echo "/data/nfs_pro *(rw,no_root_squash)" >> /etc/exports

# 使配置生效
exportfs -arv
```

> [!warning] 网段限制说明
> 如果需要限制可访问的网段，应填写**宿主机网段**（如 `192.168.164.0/24`）而非 Pod 网段，因为 PV 是挂载到宿主机上再挂载到 Pod 中的。

## 安装 homebrew

为了更方便的安装 k9s 等 app，宿主机上可以装一个 homebrew：

```sh
# homebrew 不让用 root 装，切换普通用户装
useradd -m hx && echo 'hx:hx' | chpasswd && echo 'hx ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/hx
su - hx
# 前置依赖
sudo dnf groupinstall -y "Development Tools"
sudo dnf install -y procps-ng curl file git
# 安装
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
# 加到 PATH
echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.bashrc
source ~/.bashrc

# 换中科大源
export HOMEBREW_API_DOMAIN="https://mirrors.ustc.edu.cn/homebrew-bottles/api"
export HOMEBREW_BOTTLE_DOMAIN="https://mirrors.ustc.edu.cn/homebrew-bottles"
export HOMEBREW_BREW_GIT_REMOTE="https://mirrors.ustc.edu.cn/brew.git"
export HOMEBREW_CORE_GIT_REMOTE="https://mirrors.ustc.edu.cn/homebrew-core.git"

# 写入 bashrc 持久化
cat >> ~/.bashrc << 'EOF'
export HOMEBREW_API_DOMAIN="https://mirrors.ustc.edu.cn/homebrew-bottles/api"
export HOMEBREW_BOTTLE_DOMAIN="https://mirrors.ustc.edu.cn/homebrew-bottles"
export HOMEBREW_BREW_GIT_REMOTE="https://mirrors.ustc.edu.cn/brew.git"
export HOMEBREW_CORE_GIT_REMOTE="https://mirrors.ustc.edu.cn/homebrew-core.git"
EOF
```

## 安装 k9s

```sh
# 方法1：webi 装。升级的话就跑一遍同样的命令
curl -sS https://webi.sh/k9s | sh

# 方法2：brew 装
brew install k9s
```

## 安装 helm

下载地址：https://github.com/helm/helm/releases

```sh
# 对于 k8s 1.23 版本，小于等于 3.11.x 版本的 helm 是支持的
wget https://get.helm.sh/helm-v3.16.2-linux-amd64.tar.gz
tar zxvf helm-v3.16.2-linux-amd64.tar.gz
cp linux-amd64/helm /bin/  # /bin/ 是默认的环境变量路径之一，所以移动后你可以在任何位置运行这个二进制文件。
# 查看 helm 版本
helm version
```
