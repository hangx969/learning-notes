---
title: Linux 运维专题地图
tags:
  - knowledgebase/map
  - knowledgebase/linux
aliases:
  - Linux Ops Map
date: 2026-04-16
---

# 🐧 Linux 运维专题地图

> [!info] 专题范围
> 覆盖 Linux-Shell（24 篇）为主线，关联 OS（3 篇）、HPC（7 篇）、GPU（4 篇）等基础设施知识。

---

## 核心概念
- [自动化运维](../concepts/自动化运维.md)
- [Slurm](../concepts/Slurm.md)

---

## 📖 推荐阅读顺序

### Linux 基础
1. [Linux-learning-notes](../../Linux-Shell/Linux-learning-notes.md) — 全面学习笔记（2688 行）
2. [linux环境变量管理](../../Linux-Shell/linux环境变量管理.md) — 环境变量
3. [系统信息查看](../../Linux-Shell/系统信息查看.md) — 系统信息
4. [OS](../../OS/OS.md) — 操作系统理论
5. [OS-磁盘管理](../../OS/OS-磁盘管理.md) — 磁盘管理
6. [LVM-RAID](../../Linux-Shell/LVM-RAID.md) — LVM 与 RAID

### Shell 脚本与自动化
7. [shell-scripts](../../Linux-Shell/shell-scripts.md) — Shell 脚本实战
8. [screen后台运行任务](../../Linux-Shell/screen后台运行任务.md) — 后台任务
9. [inotifywait监控文件变化](../../Linux-Shell/inotifywait监控文件变化.md) — 文件监控

### 网络与安全
10. [ssh连接](../../Linux-Shell/ssh连接.md) — SSH 基础
11. [ssh远程执行多个命令](../../Linux-Shell/ssh远程执行多个命令.md) — SSH 批量执行
12. [nmcli管理网络配置](../../Linux-Shell/nmcli管理网络配置.md) — 网络配置
13. [Linux终端配置proxy](../../Linux-Shell/Linux终端配置proxy.md) — 代理配置
14. [开源堡垒机jumpserver部署](../../Linux-Shell/开源堡垒机jumpserver部署.md) — 堡垒机

### 自动化运维工具
15. [ansible安装-rockylinux8](../../Linux-Shell/ansible安装-rockylinux8.md) — Ansible
16. [terraform-basics](../../IaC/terraform-basics.md) — Terraform
17. [python-Linux-operation](../../Python/python-运维开发/python-Linux-operation.md) — Python 运维

### Ubuntu 专题
18. [Ubuntu基础操作](../../Linux-Shell/Ubuntu基础操作.md) — 基础操作
19. [Ubuntu安装显卡驱动](../../Linux-Shell/Ubuntu安装显卡驱动.md) — GPU 驱动
20. [Ubuntu-unattended-upgrade管理](../../Linux-Shell/Ubuntu-unattended-upgrade管理.md) — 安全补丁
21. [Ubuntu-修改启动内核](../../Linux-Shell/Ubuntu-修改启动内核.md) — 内核管理
22. [Ubuntu部署vftpd](../../Linux-Shell/Ubuntu部署vftpd.md) — FTP 服务

### 开发环境
23. [MacBook开发环境配置](../../Linux-Shell/MacBook开发环境配置.md) — macOS
24. [配置zsh终端](../../Linux-Shell/配置zsh终端.md) — zsh 终端
25. [vscode](../../Linux-Shell/vscode.md) — VSCode

---

## 📂 分类索引

### 系统管理
| 文章 | 主题 |
|------|------|
| [Linux-learning-notes](../../Linux-Shell/Linux-learning-notes.md) | Linux 全面学习笔记 |
| [linux环境变量管理](../../Linux-Shell/linux环境变量管理.md) | 环境变量 |
| [系统信息查看](../../Linux-Shell/系统信息查看.md) | 系统信息 |
| [LVM-RAID](../../Linux-Shell/LVM-RAID.md) | LVM 与 RAID |
| [OS](../../OS/OS.md) | 操作系统理论（2266 行）|
| [OS-磁盘管理](../../OS/OS-磁盘管理.md) | 磁盘管理与 IO |
| [计算机组成原理](../../OS/计算机组成原理.md) | 计算机组成原理 |

### 网络与安全
| 文章 | 主题 |
|------|------|
| [ssh连接](../../Linux-Shell/ssh连接.md) | SSH 连接 |
| [ssh远程执行多个命令](../../Linux-Shell/ssh远程执行多个命令.md) | SSH 批量执行 |
| [nmcli管理网络配置](../../Linux-Shell/nmcli管理网络配置.md) | NetworkManager |
| [Linux终端配置proxy](../../Linux-Shell/Linux终端配置proxy.md) | 代理配置 |
| [samba文件共享服务](../../Linux-Shell/samba文件共享服务.md) | Samba |
| [开源堡垒机jumpserver部署](../../Linux-Shell/开源堡垒机jumpserver部署.md) | JumpServer |
| [计算机网络基础](../../Networking/计算机网络基础.md) | 网络理论 |
| [HTTP基础](../../Networking/HTTP基础.md) | HTTP 协议 |

### 自动化
| 文章 | 主题 |
|------|------|
| [shell-scripts](../../Linux-Shell/shell-scripts.md) | Shell 脚本 |
| [ansible安装-rockylinux8](../../Linux-Shell/ansible安装-rockylinux8.md) | Ansible |
| [inotifywait监控文件变化](../../Linux-Shell/inotifywait监控文件变化.md) | inotifywait |
| [screen后台运行任务](../../Linux-Shell/screen后台运行任务.md) | screen |

### HPC 调度
| 文章 | 主题 |
|------|------|
| [CentOS7-slurm23.02-二进制安装](../../HPC/CentOS7-slurm23.02-二进制安装.md) | Slurm CentOS |
| [Ubuntu2204-slurm-22.05.11-二进制安装](../../HPC/Ubuntu2204-slurm-22.05.11-二进制安装.md) | Slurm Ubuntu |
| [PBS](../../HPC/PBS.md) | PBS 调度 |
| [Slurm-node-exporter](../../HPC/Slurm-node-exporter.md) | Slurm 监控 |

### GPU 基础设施
| 文章 | 主题 |
|------|------|
| [GPU-basics](../../GPU-DeepLearning/GPU-basics.md) | GPU 基础 |
| [GPU-exporter-grafana](../../GPU-DeepLearning/GPU-exporter-grafana.md) | GPU 监控 |
| [NVIDIA-GPU-开启persistent mode](../../GPU-DeepLearning/NVIDIA-GPU-开启persistent%20mode.md) | NVIDIA 优化 |
| [Server-basics](../../GPU-DeepLearning/Server-basics.md) | 服务器入门 |
| [Ubuntu安装显卡驱动](../../Linux-Shell/Ubuntu安装显卡驱动.md) | Ubuntu GPU 驱动 |

---

## 🔗 关联领域
- [python-devops-map](python-devops-map.md) — Python 运维自动化
- [kubernetes-map](kubernetes-map.md) — K8s 依赖 Linux 底盘
- [自动化运维](../concepts/自动化运维.md) — 自动化运维概念
