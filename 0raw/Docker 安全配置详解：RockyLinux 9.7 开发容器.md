---
title: "Docker 安全配置详解：RockyLinux 9.7 开发容器"
source: "https://mp.weixin.qq.com/s/KJZlXWUS-bF6jd0OW1rmtA?scene=1&click_id=60"
author:
  - "[[院长技术]]"
published:
created: 2026-06-05
description:
tags:
  - "clippings"
---
院长技术 *2026年6月3日 10:14*

微信技术交流群

![图片](https://mmbiz.qpic.cn/mmbiz_png/icicwqjtx9YqESHicwyqUlletqYWc9JSibyE44d3urbc6IbfhC5sgT4B1HWPpiaGchHyiaicZiaSl4md49fUQhYx1VGTjGHUkbRbV5cYOdzfvw8Nams/640?wx_fmt=png&from=appmsg&watermark=1&wxfrom=5&wx_lazy=1&tp=webp#imgIndex=0)

## DeanTech云原生运维管理平台v5.0版本已更新

## 正文

本文档基于以下 `docker run` 命令，逐项解析参数含义，并深入探讨容器安全最佳实践。

```
docker run -d \
  --name rockydev \
  --cap-drop ALL \
  --cap-add CAP_NET_BIND_SERVICE \
  --cap-add CAP_SETUID \
  --cap-add CAP_SETGID \
  --cap-add CAP_CHOWN \
  --security-opt=no-new-privileges:true \
  --hostname rockydev \
  -p 20022:22 \
  --restart=always \
  swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/rockylinux/rockylinux:9.7 \
  sleep infinity
```

### 1\. 命令参数详解

| 参数 | 值 | 含义说明 |
| --- | --- | --- |
| `-d` | \- | **后台运行** （detach）。容器在后台启动，不占用当前终端。 |
| `--name` | `rockydev` | 为容器指定一个易记的名称，后续可通过 `docker start/stop/exec rockydev` 操作。 |
| `--cap-drop` | `ALL` | **放弃所有 Linux Capabilities** 。容器默认拥有约 14 项能力（如 `CAP_CHOWN`, `CAP_DAC_OVERRIDE` 等）。使用 `ALL` 剥夺全部，然后按需添加，遵循“最小权限”原则。 |
| `--cap-add` | `CAP_NET_BIND_SERVICE` | 允许进程绑定到特权端口（<1024）。SSH 服务默认监听 22 端口，需要此能力。 |
| `--cap-add` | `CAP_SETUID` | 允许改变进程的用户 ID（UID）。SSH 登录后需要切换至普通用户时用到。 |
| `--cap-add` | `CAP_SETGID` | 允许改变进程的组 ID（GID）。与 `CAP_SETUID` 配合使用。 |
| `--cap-add` | `CAP_CHOWN` | 允许更改文件或目录的所有权。SSH 服务在创建用户会话或修改 `/var/empty` 等目录时可能需要。 |
| `--security-opt` | `no-new-privileges:true` | 防止容器内的进程通过 `execve` 获得比父进程更多的权限。即使存在 `suid` 二进制文件或 `capabilities` ，也无法提升权限。这是防御提权攻击的关键配置。 |
| `--hostname` | `rockydev` | 设置容器内部的主机名。 |
| `-p` | `20022:22` | **端口映射** 。将宿主机的 `20022` 端口映射到容器的 `22` 端口。外部可通过 `宿主机IP:20022` 访问容器内的 SSH 服务。 |
| `--restart` | `always` | 容器退出时总是自动重启。适用于需要长期运行的服务。 |
| **镜像地址** | `swr.cn-north-4.../rockylinux:9.7` | 使用华为云镜像仓库提供的 Rocky Linux 9.7 官方镜像（加速国内拉取）。 |
| **启动命令** | `sleep infinity` | 使容器持续运行的前台进程。 `sleep infinity` 永不退出，保证容器不会因为无进程而自动终止。 |

## 2\. 容器安全分析

### 2.1 已实施的安全措施（⭐ 推荐）

- **移除 `--privileged`**  
	未使用特权模式，避免了容器获得宿主机 root 权限的风险。
- **最小 Capabilities 集合**  
	只添加了 SSH 服务所需的 4 项能力，其余全部丢弃。与默认的 14 项相比，攻击面大幅缩小。
- **禁止新权限** （ `no-new-privileges:true` ）  
	这是防御容器逃逸的强力开关。即使内核存在漏洞，攻击者也难以通过 `setuid` 等手段提升权限。
- **非交互式启动**  
	使用 `sleep infinity` 作为主进程，无 shell 监听，减少被入侵后的直接交互机会。

### 2.2 仍存在的风险与改进建议

| 风险点 | 说明 | 改进方案 |
| --- | --- | --- |
| **容器内以 root 运行** | 未指定 `--user` ，默认以 root 用户启动进程。容器内 root 仍拥有较高的能力（虽然 capability 受限）。 | 在 Dockerfile 中创建普通用户，并用 `USER` 指令切换。例如： `RUN useradd -m dev && USER dev` 。 |
| **文件系统可写** | 未使用 `--read-only` ，攻击者可写入恶意脚本或修改二进制文件。 | 添加 `--read-only` ，并将日志、数据目录挂载为临时卷（ `--tmpfs` 或 `-v` ）。 |
| **SSH 默认配置** | 若后续安装 sshd，默认允许 root 登录，密码认证开启。 | 在容器内配置 `/etc/ssh/sshd_config` ：   `PermitRootLogin no`   `PasswordAuthentication no`   仅使用密钥登录。 |
| **端口暴露** | 将容器 22 端口映射到宿主机 20022，可能被扫描和暴力破解。 | 使用防火墙限制访问 IP（如仅允许公司 VPN），或改用非标准端口映射（如 `-p 54321:22` ）。 |
| **内核漏洞逃逸** | 即便配置完美，仍然可能受内核漏洞（如 CVE-2024-21626）影响。 | 保持宿主机内核和 Docker 引擎更新，启用 **Seccomp** 和 **AppArmor** 配置文件。 |

## 3\. 安全加固建议（生产环境）

若要将此容器用于开发或测试环境，建议实施以下额外配置：

### 3.1 启用 User Namespace 重映射

将容器内的 root 映射为宿主机的非特权用户，即使容器被攻破，攻击者获得的也只是普通用户权限。  
修改 Docker 守护进程配置 /etc/docker/daemon.json：

```
{
  "userns-remap": "default"
}
```

重启 Docker 后生效。

### 3.2 使用只读根文件系统

```
--read-only \
--tmpfs /tmp:rw,noexec,nosuid \
--tmpfs /var/log:rw,noexec,nosuid \
--tmpfs /run:rw,noexec,nosuid
```

### 3.3 限制容器资源

防止 fork 炸弹或资源耗尽：

```
--memory=512m \
--cpus=0.5 \
--pids-limit=100
```

### 3.4 应用自定义 Seccomp/AppArmor 策略

Seccomp：默认策略已较好，可进一步收紧系统调用。

AppArmor：为容器编写专属配置文件，限制文件访问和网络操作。

### 3.5 定期扫描镜像漏洞

使用 trivy 或 docker scan 扫描基础镜像：

```
trivy image swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/rockylinux/rockylinux:9.7
```

## 4\. 验证与测试

### 4.1 验证 Capabilities 是否生效

进入容器并检查：

```
docker exec -it rockydev bash
# 安装工具
dnf install -y libcap
capsh --print
输出中应只包含已添加的 CAP_NET_BIND_SERVICE, CAP_SETUID, CAP_SETGID, CAP_CHOWN。
```

### 4.2 测试权限隔离

尝试在容器内加载内核模块（应该失败）：

```
insmod /some/module.ko
# 错误：Operation not permitted
```

### 4.3 测试 SSH 登录（需预先安装 openssh-server）

```
# 在宿主机执行
ssh -p 20022 root@localhost
如果配置了密钥登录且不允许 root，登录会被拒绝。
```

## 5\. 总结

当前命令已经遵循了“默认安全”原则，适用于大多数开发或轻量级演示场景。相比直接使用 --privileged，安全性提升了数个数量级。但在面向公网或运行不可信代码时，仍需结合 User Namespace、只读文件系统、资源限制及定期更新等手段，构建纵深防御体系。

附录：常用安全相关 Docker 参数速查

| 参数 | 作用 | 推荐值 |
| --- | --- | --- |
| `--cap-drop` | 删除能力 | `ALL` |
| `--cap-add` | 添加能力 | 仅必要项（如 `NET_ADMIN` 或 `SYS_PTRACE` 等） |
| `--security-opt=no-new-privileges:true` | 禁止权限提升 | 始终添加 |
| `--read-only` | 根文件系统只读 | 推荐 |
| `--user` | 指定运行用户 | 非 root 用户（如 `1000:1000` ） |
| `--security-opt=seccomp=path/to/profile.json` | 自定义系统调用过滤 | 生产环境定制 |
| `--security-opt=apparmor=profile-name` | AppArmor 强制访问控制 | 配合宿主机策略 |

**微信扫一扫赞赏作者**

运维必备 · 目录

继续滑动看下一个

院长技术

向上滑动看下一个