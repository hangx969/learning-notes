---
title: "Docker 安全配置详解：Capabilities 与容器加固"
source: "https://mp.weixin.qq.com/s/KJZlXWUS-bF6jd0OW1rmtA"
created: 2026-06-05
tags:
  - docker
  - security
  - container
---

# Docker 安全配置详解：Capabilities 与容器加固

基于一个 RockyLinux 9.7 开发容器的 `docker run` 命令，逐项解析安全参数并深入探讨容器安全最佳实践。

## 安全基线命令

```bash
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
  rockylinux/rockylinux:9.7 \
  sleep infinity
```

## 参数详解

| 参数 | 值 | 含义 |
|------|-----|------|
| `--cap-drop` | `ALL` | **放弃所有 Linux Capabilities**（默认约 14 项），然后按需添加，遵循"最小权限"原则 |
| `--cap-add` | `CAP_NET_BIND_SERVICE` | 允许绑定特权端口（<1024），SSH 服务监听 22 端口需要 |
| `--cap-add` | `CAP_SETUID` / `CAP_SETGID` | 允许切换用户/组 ID，SSH 登录后切换至普通用户时需要 |
| `--cap-add` | `CAP_CHOWN` | 允许更改文件所有权，SSH 服务创建用户会话时需要 |
| `--security-opt` | `no-new-privileges:true` | **防止提权攻击**——即使存在 suid 二进制文件或 capabilities，也无法通过 execve 提升权限 |
| `-p` | `20022:22` | 宿主机高位端口映射到容器 SSH 端口 |
| 启动命令 | `sleep infinity` | 无 shell 监听的前台进程，减少入侵后的直接交互机会 |

## 已实施的安全措施

1. **未使用 `--privileged`**：避免容器获得宿主机 root 权限
2. **最小 Capabilities 集合**：仅保留 SSH 所需 4 项能力，攻击面大幅缩小（对比默认 14 项）
3. **禁止新权限**（`no-new-privileges:true`）：防御容器逃逸的关键开关
4. **非交互式启动**：使用 `sleep infinity` 而非 shell

## 仍存在的风险与改进

| 风险点 | 说明 | 改进方案 |
|--------|------|----------|
| **容器内以 root 运行** | 未指定 `--user`，默认 root | Dockerfile 中 `RUN useradd -m dev && USER dev` |
| **文件系统可写** | 未使用 `--read-only` | 添加 `--read-only` + `--tmpfs` 挂载临时目录 |
| **SSH 默认配置** | 默认允许 root 登录、密码认证 | `PermitRootLogin no` + `PasswordAuthentication no` |
| **端口暴露** | 可能被扫描和暴力破解 | 防火墙限制访问 IP 或改用非标准端口 |
| **内核漏洞逃逸** | 如 CVE-2024-21626 | 保持宿主机内核和 Docker 引擎更新，启用 Seccomp/AppArmor |

## 生产环境安全加固

### User Namespace 重映射

将容器内 root 映射为宿主机的非特权用户：

```json
// /etc/docker/daemon.json
{
  "userns-remap": "default"
}
```

### 只读根文件系统

```bash
--read-only \
--tmpfs /tmp:rw,noexec,nosuid \
--tmpfs /var/log:rw,noexec,nosuid \
--tmpfs /run:rw,noexec,nosuid
```

### 资源限制（防 fork 炸弹）

```bash
--memory=512m \
--cpus=0.5 \
--pids-limit=100
```

### Seccomp / AppArmor 策略

- **Seccomp**：默认策略已较好，可进一步收紧系统调用
- **AppArmor**：为容器编写专属配置文件，限制文件访问和网络操作

### 镜像漏洞扫描

```bash
trivy image rockylinux/rockylinux:9.7
```

## 验证方法

```bash
# 检查 Capabilities 是否生效
docker exec -it rockydev bash
dnf install -y libcap
capsh --print
# 输出应只包含已添加的 4 项 capability

# 测试权限隔离（应失败）
insmod /some/module.ko
# 错误：Operation not permitted
```

## 安全参数速查表

| 参数 | 作用 | 推荐值 |
|------|------|--------|
| `--cap-drop` | 删除能力 | `ALL` |
| `--cap-add` | 添加能力 | 仅必要项 |
| `--security-opt=no-new-privileges:true` | 禁止权限提升 | 始终添加 |
| `--read-only` | 根文件系统只读 | 推荐 |
| `--user` | 指定运行用户 | 非 root（如 `1000:1000`） |
| `--security-opt=seccomp=path` | 自定义系统调用过滤 | 生产环境定制 |
| `--security-opt=apparmor=profile` | AppArmor 强制访问控制 | 配合宿主机策略 |
