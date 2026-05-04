---
title: Ubuntu 25.10 (Questing) 初始化配置指南
date: 2026-04-05
tags:
  - Linux/Ubuntu
  - DevOps/setup
  - infrastructure
aliases:
  - Ubuntu 2510 初始化
  - Ubuntu Questing 配置
---

# Ubuntu 25.10 (Questing) 初始化配置指南

适用于 ==Ubuntu 25.10 (Questing)== 的新机初始化配置,涵盖 SSH、sudo、APT 镜像源、开发工具、中文输入法及 VMware Tools。

## 1. 安装 SSH 服务

```bash
sudo apt update
sudo apt install openssh-server
```

启动并设置开机自启:

```bash
sudo systemctl enable --now ssh
```

查看状态:

```bash
sudo systemctl status ssh
```

放行防火墙:

```bash
sudo ufw allow ssh
```

> [!tip] 配置文件
> 配置文件位于 `/etc/ssh/sshd_config`,修改后需重启服务:
> ```bash
> sudo systemctl restart ssh
> ```

## 2. 配置免密 sudo

将用户 `hx-ai` 加入免密 sudo:

```bash
echo 'hx-ai ALL=(ALL) NOPASSWD:ALL' | sudo tee /etc/sudoers.d/hx-ai
```

> [!tip] 更安全的方式:`visudo`
> ```bash
> sudo visudo -f /etc/sudoers.d/hx-ai
> ```
> 添加内容:
> ```
> hx-ai ALL=(ALL) NOPASSWD:ALL
> ```

## 3. 更换 APT 国内源

Ubuntu 25.10 代号为 `questing`,使用 **DEB822 格式**,配置文件在 `/etc/apt/sources.list.d/ubuntu.sources`。

### 3.1 备份

```bash
sudo cp /etc/apt/sources.list.d/ubuntu.sources /etc/apt/sources.list.d/ubuntu.sources.bak
```

### 3.2 替换为阿里云源

```bash
sudo sed -i 's|https://cn.archive.ubuntu.com/ubuntu|https://mirrors.aliyun.com/ubuntu|g; s|http://security.ubuntu.com/ubuntu|https://mirrors.aliyun.com/ubuntu|g' /etc/apt/sources.list.d/ubuntu.sources
```

### 3.3 替换为清华 TUNA 源(可选)

```bash
sudo sed -i 's|https://cn.archive.ubuntu.com/ubuntu|https://mirrors.tuna.tsinghua.edu.cn/ubuntu|g; s|http://security.ubuntu.com/ubuntu|https://mirrors.tuna.tsinghua.edu.cn/ubuntu|g' /etc/apt/sources.list.d/ubuntu.sources
```

### 3.4 替换为中科大源(可选)

```bash
sudo sed -i 's|https://cn.archive.ubuntu.com/ubuntu|https://mirrors.ustc.edu.cn/ubuntu|g; s|http://security.ubuntu.com/ubuntu|https://mirrors.ustc.edu.cn/ubuntu|g' /etc/apt/sources.list.d/ubuntu.sources
```

### 3.5 更新缓存

```bash
sudo apt update
```

> [!info]
> 可通过 `lsb_release -cs` 查看实际系统代号。

## 4. 安装常用开发工具包

```bash
sudo apt install -y \
  thin-provisioning-tools \
  lvm2 \
  wget \
  net-tools \
  nfs-common \
  lrzsz \
  gcc \
  g++ \
  make \
  cmake \
  libxml2-dev \
  libssl-dev \
  curl \
  libcurl4-openssl-dev \
  unzip \
  sudo \
  libaio-dev \
  vim \
  libncurses-dev \
  autoconf \
  automake \
  openssh-server \
  telnet \
  coreutils \
  iputils-ping \
  iproute2 \
  ncat \
  jq \
  psmisc \
  git \
  bash-completion
```

## 5. 安装中文输入法(Fcitx5 + 拼音)

### 5.1 安装 Fcitx5 及中文输入法

```bash
sudo apt install -y fcitx5 fcitx5-chinese-addons fcitx5-frontend-gtk4 fcitx5-frontend-qt5 fcitx5-config-qt
```

### 5.2 设置为默认输入法框架

```bash
im-config -n fcitx5
```

### 5.3 设置环境变量

```bash
cat >> ~/.profile << 'EOF'

# Fcitx5
export INPUT_METHOD=fcitx5
export GTK_IM_MODULE=fcitx
export QT_IM_MODULE=fcitx
export XMODIFIERS=@im=fcitx
EOF
```

### 5.4 设置开机自启(GNOME 桌面)

```bash
mkdir -p ~/.config/autostart
cp /usr/share/applications/org.fcitx.Fcitx5.desktop ~/.config/autostart/
```

### 5.5 重启系统

```bash
reboot
```

### 5.6 重启后配置拼音

打开 Fcitx5 配置工具:

```bash
fcitx5-config-qt
```

在 **Input Method** 选项卡中,点击 `+` 搜索 `Pinyin`,添加即可。

> [!tip] 默认快捷键
> - `Ctrl + 空格` — 切换中英文
> - `Ctrl + Shift` — 切换输入法

## 6. 安装 VMware Tools

> [!note] 推荐使用 open-vm-tools
> Ubuntu 官方仓库直接提供,比 VMware 官方 Tools 更稳定。

### 6.1 安装

```bash
sudo apt install -y open-vm-tools open-vm-tools-desktop
```

| 包 | 功能 |
|---|---|
| `open-vm-tools` | 基础功能(共享文件夹、时间同步等) |
| `open-vm-tools-desktop` | ==桌面功能(复制粘贴、拖拽文件)== |

### 6.2 重启

```bash
reboot
```

### 6.3 验证

```bash
systemctl status open-vm-tools
```

### 6.4 排障

> [!warning] 如果重启后仍无法复制粘贴
> 检查 VMware 设置:**VM → Settings → Options → Guest Isolation**
> - ✅ 勾选 `Enable copy and paste`
> - ✅ 勾选 `Enable drag and drop`
