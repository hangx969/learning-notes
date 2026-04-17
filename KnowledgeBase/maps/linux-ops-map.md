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
- [[KnowledgeBase/concepts/自动化运维|自动化运维]]
- [[KnowledgeBase/entities/Slurm|Slurm]]

---

## 📖 推荐阅读顺序

### Linux 基础
1. [[Linux-Shell/Linux-learning-notes|Linux-learning-notes]] — 全面学习笔记（2688 行）
2. [[Linux-Shell/linux环境变量管理|linux环境变量管理]] — 环境变量
3. [[Linux-Shell/系统信息查看|系统信息查看]] — 系统信息
4. [[OS/OS|OS]] — 操作系统理论
5. [[OS/OS-磁盘管理|OS-磁盘管理]] — 磁盘管理
6. [[Linux-Shell/LVM-RAID|LVM-RAID]] — LVM 与 RAID

### Shell 脚本与自动化
7. [[Linux-Shell/shell-scripts|shell-scripts]] — Shell 脚本实战
8. [[Linux-Shell/screen后台运行任务|screen后台运行任务]] — 后台任务
9. [[Linux-Shell/inotifywait监控文件变化|inotifywait监控文件变化]] — 文件监控

### 网络与安全
10. [[Linux-Shell/ssh连接|ssh连接]] — SSH 基础
11. [[Linux-Shell/ssh远程执行多个命令|ssh远程执行多个命令]] — SSH 批量执行
12. [[Linux-Shell/nmcli管理网络配置|nmcli管理网络配置]] — 网络配置
13. [[Linux-Shell/Linux终端配置proxy|Linux终端配置proxy]] — 代理配置
14. [[Linux-Shell/开源堡垒机jumpserver部署|开源堡垒机jumpserver部署]] — 堡垒机

### 自动化运维工具
15. [[Linux-Shell/ansible安装-rockylinux8|ansible安装-rockylinux8]] — Ansible
16. [[IaC/terraform-basics|terraform-basics]] — Terraform
17. [[Python/python-运维开发/python-Linux-operation|python-Linux-operation]] — Python 运维

### Ubuntu 专题
18. [[Linux-Shell/Ubuntu基础操作|Ubuntu基础操作]] — 基础操作
19. [[Linux-Shell/Ubuntu安装显卡驱动|Ubuntu安装显卡驱动]] — GPU 驱动
20. [[Linux-Shell/Ubuntu-unattended-upgrade管理|Ubuntu-unattended-upgrade管理]] — 安全补丁
21. [[Linux-Shell/Ubuntu-修改启动内核|Ubuntu-修改启动内核]] — 内核管理
22. [[Linux-Shell/Ubuntu部署vftpd|Ubuntu部署vftpd]] — FTP 服务

### 开发环境
23. [[Linux-Shell/MacBook开发环境配置|MacBook开发环境配置]] — macOS
24. [[Linux-Shell/配置zsh终端|配置zsh终端]] — zsh 终端
25. [[Linux-Shell/vscode|vscode]] — VSCode

---

## 📂 分类索引

### 系统管理
| 文章 | 主题 |
|------|------|
| [[Linux-Shell/Linux-learning-notes|Linux-learning-notes]] | Linux 全面学习笔记 |
| [[Linux-Shell/linux环境变量管理|linux环境变量管理]] | 环境变量 |
| [[Linux-Shell/系统信息查看|系统信息查看]] | 系统信息 |
| [[Linux-Shell/LVM-RAID|LVM-RAID]] | LVM 与 RAID |
| [[OS/OS|OS]] | 操作系统理论（2266 行）|
| [[OS/OS-磁盘管理|OS-磁盘管理]] | 磁盘管理与 IO |
| [[OS/计算机组成原理|计算机组成原理]] | 计算机组成原理 |

### 网络与安全
| 文章 | 主题 |
|------|------|
| [[Linux-Shell/ssh连接|ssh连接]] | SSH 连接 |
| [[Linux-Shell/ssh远程执行多个命令|ssh远程执行多个命令]] | SSH 批量执行 |
| [[Linux-Shell/nmcli管理网络配置|nmcli管理网络配置]] | NetworkManager |
| [[Linux-Shell/Linux终端配置proxy|Linux终端配置proxy]] | 代理配置 |
| [[Linux-Shell/samba文件共享服务|samba文件共享服务]] | Samba |
| [[Linux-Shell/开源堡垒机jumpserver部署|开源堡垒机jumpserver部署]] | JumpServer |
| [[Networking/计算机网络基础|计算机网络基础]] | 网络理论 |
| [[Networking/HTTP基础|HTTP基础]] | HTTP 协议 |

### 自动化
| 文章 | 主题 |
|------|------|
| [[Linux-Shell/shell-scripts|shell-scripts]] | Shell 脚本 |
| [[Linux-Shell/ansible安装-rockylinux8|ansible安装-rockylinux8]] | Ansible |
| [[Linux-Shell/inotifywait监控文件变化|inotifywait监控文件变化]] | inotifywait |
| [[Linux-Shell/screen后台运行任务|screen后台运行任务]] | screen |

### HPC 调度
| 文章 | 主题 |
|------|------|
| [[HPC/CentOS7-slurm23.02-二进制安装|CentOS7-slurm23.02-二进制安装]] | Slurm CentOS |
| [[HPC/Ubuntu2204-slurm-22.05.11-二进制安装|Ubuntu2204-slurm-22.05.11-二进制安装]] | Slurm Ubuntu |
| [[HPC/PBS|PBS]] | PBS 调度 |
| [[HPC/Slurm-node-exporter|Slurm-node-exporter]] | Slurm 监控 |

### GPU 基础设施
| 文章 | 主题 |
|------|------|
| [[GPU-DeepLearning/GPU-basics|GPU-basics]] | GPU 基础 |
| [[GPU-DeepLearning/GPU-exporter-grafana|GPU-exporter-grafana]] | GPU 监控 |
| [[GPU-DeepLearning/NVIDIA-GPU-开启persistent mode|NVIDIA-GPU-开启persistent mode]] | NVIDIA 优化 |
| [[GPU-DeepLearning/Server-basics|Server-basics]] | 服务器入门 |
| [[Linux-Shell/Ubuntu安装显卡驱动|Ubuntu安装显卡驱动]] | Ubuntu GPU 驱动 |

---

## 🔗 关联领域
- [[KnowledgeBase/maps/python-devops-map|python-devops-map]] — Python 运维自动化
- [[KnowledgeBase/maps/kubernetes-map|kubernetes-map]] — K8s 依赖 Linux 底盘
- [[KnowledgeBase/concepts/自动化运维|自动化运维]] — 自动化运维概念
