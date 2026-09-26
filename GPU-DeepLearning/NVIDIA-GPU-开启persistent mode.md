---
title: NVIDIA GPU 开启 Persistent Mode
tags:
  - GPU
  - NVIDIA
  - persistent-mode
aliases:
  - GPU Persistent Mode
---

# NVIDIA GPU 开启 Persistent Mode

NVIDIA 驱动提供 `nvidia-persistenced` 服务，用于在没有活动客户端时维持 GPU 驱动状态。以下示例安装其随驱动提供的 systemd 服务，并设置开机启动。安装脚本依赖 `sed`、`useradd`、`userdel` 和 `id`。示例路径来自原环境；NVIDIA 文档使用 `/usr/share/doc/NVIDIA_GLX-1.0/sample/`，请以实际驱动包中的路径为准。

## 安装服务

```sh
cd /usr/share/doc/NVIDIA_GLX-1.0/samples/
ls
#nvidia-persistenced-init.tar.bz2  systemd
tar xvf nvidia-persistenced-init.tar.bz2
ls
#nvidia-persistenced-init  nvidia-persistenced-init.tar.bz2  systemd
cd nvidia-persistenced-init/
./install.sh
```

安装成功时，输出示例如下：

```text
Checking for common requirements...
  sed found in PATH?  Yes
  useradd found in PATH?  Yes
  userdel found in PATH?  Yes
  id found in PATH?  Yes
Common installation/uninstallation supported

Creating sample System V script... done.
Creating sample systemd service file... done.
Creating sample Upstart service file... done.

Checking for systemd requirements...
  /usr/lib/systemd/system directory exists?  Yes
  systemctl found in PATH?  Yes
systemd installation/uninstallation supported

Installation parameters:
  User  : nvidia-persistenced
  Group : nvidia-persistenced
  systemd service installation path : /usr/lib/systemd/system

Adding user 'nvidia-persistenced' to group 'nvidia-persistenced'... done.
Installing sample systemd service nvidia-persistenced.service... done.
Enabling nvidia-persistenced.service... done.
Starting nvidia-persistenced.service... done.

systemd service successfully installed.
```

## 验证

检查服务状态。若要启用 GPU 的 Persistence Mode，再以管理员权限设置，并用 `nvidia-smi` 查看 Persistence-M：

```sh
systemctl status nvidia-persistenced.service
sudo nvidia-smi -pm 1
nvidia-smi
```

重启系统后，再次检查服务状态和 Persistence-M。`nvidia-smi -pm 1` 的设置本身不会跨重启保留；如果需要开机后保持 `On`，还应确认服务启动后的实际状态，并在需要时配置启动时重新设置。
