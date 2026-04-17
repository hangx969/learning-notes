#!/usr/bin/env bash

HARBOR_HOST="${HARBOR_HOST:-}"

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

mkdir -p /etc/containerd
containerd config default | tee /etc/containerd/config.toml

# 1. 启用 SystemdCgroup
sed -i 's#SystemdCgroup = false#SystemdCgroup = true#g' /etc/containerd/config.toml

# 2. 替换 sandbox (pause) 镜像为国内镜像（k8s 1.35.3 对应 pause 3.10.1）
sed -i 's#registry.k8s.io/pause#registry.cn-hangzhou.aliyuncs.com/google_containers/pause#g' /etc/containerd/config.toml

# 3. 配置 registry 镜像加速目录（containerd 1.7+ 支持此方式）
sed -i 's#config_path = ""#config_path = "/etc/containerd/certs.d"#g' /etc/containerd/config.toml

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

if [ -n "$HARBOR_HOST" ]; then
mkdir -p "/etc/containerd/certs.d/${HARBOR_HOST}"
cat > "/etc/containerd/certs.d/${HARBOR_HOST}/hosts.toml" <<EOF
server = "http://${HARBOR_HOST}"

[host."http://${HARBOR_HOST}"]
  capabilities = ["pull", "resolve", "push"]
  skip_verify = true
EOF
fi

systemctl daemon-reload && systemctl start containerd && systemctl enable containerd
systemctl restart containerd

# 验证 containerd 本身（此时 crictl 尚未安装，需等 kubelet 安装后才可用）
containerd --version

# 检查关键插件状态（overlayfs 和 cri 都要是 ok）
ctr plugin ls | grep -E "overlayfs|cri"
