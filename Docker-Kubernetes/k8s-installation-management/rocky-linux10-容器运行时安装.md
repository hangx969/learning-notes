---
title: Rocky Linux 10 容器运行时安装（Docker + containerd）
tags:
  - rocky-linux
  - docker
  - containerd
  - container-runtime
  - k8s-prereq
aliases:
  - containerd 安装
  - Docker 安装
  - 容器运行时配置
date: 2026-04-15
---

本文记录在 Rocky Linux 10 上安装和配置容器运行时的完整步骤，包括 Docker CE 和 containerd。执行本文步骤前，需先完成 [[rocky-linux10-系统初始化]] 中的所有初始化操作（尤其是第 15 步，配置 Docker CE 阿里云 repo 源）。完整安装流程见 [[安装k8s-1.35-基于rockylinux10-最新步骤]]。

# 组件安装

## Docker

> [!info]
> Docker 和 containerd 不冲突，安装 Docker 是为了能基于 Dockerfile 构建镜像。K8s 的容器运行时使用 containerd，与 Docker 无关。

```sh
# 安装最新版 Docker CE（无需像 1.33 那样固定 24.0.6 版本，
# 因为我们希望 containerd 也随之升级到最新版本）
dnf install -y docker-ce

systemctl enable docker --now

# 配置 Docker 镜像加速器（所有节点均需配置）
tee /etc/docker/daemon.json <<'EOF'
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io"
  ]
}
EOF

systemctl daemon-reload && systemctl restart docker && systemctl status docker
```

## containerd

```sh
# 从 Docker CE repo 安装最新版 containerd.io（无需固定版本号）
dnf install -y containerd.io

cd /etc/containerd
rm -rf *

# 加载必要模块
cat > /etc/modules-load.d/containerd.conf <<'EOF'
overlay
br_netfilter
EOF

modprobe overlay
modprobe br_netfilter
sysctl --system
```

配置 containerd（使用 sed 修改关键参数，兼容 containerd 1.x 和 2.x）：

```sh
mkdir -p /etc/containerd
containerd config default | tee /etc/containerd/config.toml

# 1. 启用 SystemdCgroup
sed -i 's#SystemdCgroup = false#SystemdCgroup = true#g' /etc/containerd/config.toml

# 2. 替换 sandbox (pause) 镜像为国内镜像（k8s 1.35.3 对应 pause 3.10.1）
sed -i 's#registry.k8s.io/pause#registry.cn-hangzhou.aliyuncs.com/google_containers/pause#g' /etc/containerd/config.toml

# 3. 配置 registry 镜像加速目录（containerd 1.7+ 支持此方式）
sed -i 's#config_path = ""#config_path = "/etc/containerd/certs.d"#g' /etc/containerd/config.toml
```

配置镜像加速（目录方式，兼容 containerd 1.7+ 和 2.x）：

```sh
# docker.io 镜像加速
mkdir -p /etc/containerd/certs.d/docker.io
cat > /etc/containerd/certs.d/docker.io/hosts.toml <<'EOF'
server = "https://registry-1.docker.io"

[host."https://docker.m.daocloud.io"]
  capabilities = ["pull", "resolve"]
EOF

# registry.k8s.io 镜像加速（拉取 k8s 核心组件镜像）
mkdir -p /etc/containerd/certs.d/registry.k8s.io
cat > /etc/containerd/certs.d/registry.k8s.io/hosts.toml <<'EOF'
server = "https://registry.k8s.io"

[host."https://registry.cn-hangzhou.aliyuncs.com/google_containers"]
  capabilities = ["pull", "resolve"]
EOF

# gcr.io 镜像加速
mkdir -p /etc/containerd/certs.d/gcr.io
cat > /etc/containerd/certs.d/gcr.io/hosts.toml <<'EOF'
server = "https://gcr.io"

[host."https://gcr.m.daocloud.io"]
  capabilities = ["pull", "resolve"]
EOF

# ghcr.io 镜像加速（GitHub Container Registry）
mkdir -p /etc/containerd/certs.d/ghcr.io
cat > /etc/containerd/certs.d/ghcr.io/hosts.toml <<'EOF'
server = "https://ghcr.io"

[host."https://ghcr.m.daocloud.io"]
  capabilities = ["pull", "resolve"]
EOF

# quay.io 镜像加速（Red Hat Quay）
mkdir -p /etc/containerd/certs.d/quay.io
cat > /etc/containerd/certs.d/quay.io/hosts.toml <<'EOF'
server = "https://quay.io"

[host."https://quay.m.daocloud.io"]
  capabilities = ["pull", "resolve"]
EOF

# mcr.microsoft.com 镜像加速（Microsoft Container Registry）
mkdir -p /etc/containerd/certs.d/mcr.microsoft.com
cat > /etc/containerd/certs.d/mcr.microsoft.com/hosts.toml <<'EOF'
server = "https://mcr.microsoft.com"

[host."https://mcr.m.daocloud.io"]
  capabilities = ["pull", "resolve"]
EOF
```

如果有 Harbor 私有仓库，额外添加：

```sh
mkdir -p /etc/containerd/certs.d/harbor.hanxux.local
cat > /etc/containerd/certs.d/harbor.hanxux.local/hosts.toml <<'EOF'
server = "http://harbor.hanxux.local"

[host."http://harbor.hanxux.local"]
  capabilities = ["pull", "resolve", "push"]
  skip_verify = true
EOF
```

启动并验证：

```sh
systemctl daemon-reload && systemctl start containerd && systemctl enable containerd
systemctl restart containerd

# 验证 containerd 本身（此时 crictl 尚未安装，需等 kubelet 安装后才可用）
containerd --version

# 检查关键插件状态（overlayfs 和 cri 都要是 ok）
ctr plugin ls | grep -E "overlayfs|cri"
```
