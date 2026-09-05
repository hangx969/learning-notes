---
title: Docker 镜像无引擎下载与 tar 导出
tags:
  - knowledgebase/source
  - docker-kubernetes/docker
date: 2026-09-05
sources:
  - "[[Docker-Kubernetes/docker/docker无需本地环境从DockerHub下载镜像并保存为tar]]"
aliases:
  - Docker 镜像离线下载摘要
---

# Docker 镜像无引擎下载与 tar 导出

## 元信息

- **原始文档**：[[Docker-Kubernetes/docker/docker无需本地环境从DockerHub下载镜像并保存为tar]]
- **原始来源**：https://mp.weixin.qq.com/s/KtINb-TZxbvfuF7RwsBMVg?scene=1&click_id=458085540
- **领域**：Docker-Kubernetes / Docker
- **摄入日期**：2026-09-05

## 摘要

文章介绍一个基于 Python 的镜像下载脚本：不依赖本地 Docker Engine，直接从 Docker Hub、quay.io 等 Registry 获取镜像层，并生成可用 `docker load` 导入的 `.tar` 文件。脚本能够处理 manifest list / OCI index，允许指定操作系统、CPU 架构或 manifest digest，并为大镜像下载提供断点续传和自动重试能力。

## 关键知识点

1. 镜像下载工具可通过 Registry 接口获取镜像，不要求下载端预先安装 Docker。
2. 多架构镜像需要根据 `--os` 和 `--architecture` 选择目标平台，也可以使用 `--digest` 绕过平台匹配。
3. 下载中断后可利用 `layer_gzip.tar` 临时文件继续未完成的层，已解压的 `layer.tar` 会被跳过。
4. 网络超时、连接重置和 HTTP 5xx 会触发最多 5 次的指数退避重试；不支持 Range 的 Registry 只能从头下载当前层。
5. 生成的 tar 文件可在另一台 Docker 主机上通过 `docker load -i` 导入，适合离线或受限网络环境的镜像转移。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Docker|Docker]]
- [[KnowledgeBase/concepts/容器运行时|容器运行时]]

## 值得注意

- 原文命令格式写作 `docker_pull_v2.py`，示例写作 `docker_pull.py`；使用时应以实际脚本文件名为准。
- 原文只给出脚本用法与行为说明，没有包含脚本源码；源码地址指向 Gitee 项目。
