---
title: Docker 安全配置与 Capabilities 加固
tags:
  - knowledgebase/source
  - docker-kubernetes/docker
  - security
date: 2026-06-05
sources:
  - "[[Docker-Kubernetes/docker/docker安全配置-Capabilities与容器加固]]"
aliases:
  - Docker安全加固摘要
---

# Docker 安全配置与 Capabilities 加固

## 元信息
- **原始文档**：[[Docker-Kubernetes/docker/docker安全配置-Capabilities与容器加固]]
- **领域**：Docker / 容器安全
- **摄入日期**：2026-06-05

## 摘要
以 RockyLinux 9.7 开发容器为例，系统讲解 Docker 容器安全配置。核心方法论是"最小权限"——先 `--cap-drop ALL` 放弃全部 Linux Capabilities，再按需逐项添加。配合 `no-new-privileges` 防提权、User Namespace 重映射、只读根文件系统、资源限制、Seccomp/AppArmor 策略等手段构建纵深防御体系。

## 关键知识点
1. **Capabilities 最小化**：`--cap-drop ALL` + 按需 `--cap-add`，将默认 14 项能力缩减到仅需的 4 项（NET_BIND_SERVICE / SETUID / SETGID / CHOWN）
2. **no-new-privileges**：`--security-opt=no-new-privileges:true` 是防御容器逃逸和 suid 提权的关键开关，应始终启用
3. **User Namespace 重映射**：`daemon.json` 中配置 `"userns-remap": "default"`，容器内 root 映射为宿主机非特权用户
4. **只读根文件系统**：`--read-only` + `--tmpfs` 挂载 /tmp、/var/log、/run（均添加 noexec,nosuid）
5. **资源限制三件套**：`--memory=512m --cpus=0.5 --pids-limit=100`，防止 fork 炸弹和资源耗尽
6. **五层仍存风险**：容器内 root 运行、文件系统可写、SSH 默认配置、端口暴露、内核漏洞逃逸——每层都有对应加固方案
7. **验证方法**：`capsh --print` 检查 capabilities 生效，`insmod` 测试权限隔离

## 涉及的概念与实体
- [[KnowledgeBase/entities/Docker]]
- [[KnowledgeBase/concepts/容器运行时]]

## 值得注意
- 本文填补了知识库中"Docker 安全加固（Seccomp、AppArmor、rootless 模式）"的知识空白
- 提供了一个完整的**安全参数速查表**，可直接作为容器启动的安全基线检查清单
- 纵深防御思路与 K8s 安全认证（Cert-Manager、Kyverno、Trivy）形成互补——Docker 层面是容器安全的第一道防线
