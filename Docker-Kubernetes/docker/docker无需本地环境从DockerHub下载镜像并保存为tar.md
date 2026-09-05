---
title: "不依赖本地 Docker 环境：从 Docker Hub 下载镜像并保存为 tar 文件"
source: "https://mp.weixin.qq.com/s/KtINb-TZxbvfuF7RwsBMVg?scene=1&click_id=458085540"
author:
  - "李超"
published: 2026-08-13
created: 2026-09-05
description: "无需安装 Docker，直接从 Registry 拉取镜像并打包为 .tar 文件，支持多架构、断点续传和自动重试。"
tags:
  - docker
  - docker-kubernetes
  - container-registry
  - multi-architecture
---

# 不依赖本地 Docker 环境：从 Docker Hub 下载镜像并保存为 tar 文件

## 使用说明

无需安装 Docker，直接从 Registry 拉取镜像并打包为 `.tar` 文件。支持 Docker Hub、quay.io 等公共或私有 Registry，并自动处理 manifest list / OCI index，支持选择多架构镜像。

下载支持断点续传和自动重试：中断后再次运行会跳过已完成的层，从断点继续未完成的层；遇到网络波动时会自动重试，最多 5 次并使用指数退避。

## 命令格式

```bash
python docker_pull_v2.py [选项] <镜像名称>
```

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `-h`, `--help` | 显示帮助信息并退出 | — |
| `--os OS` | 指定目标操作系统平台 | `linux` |
| `--architecture ARCH` | 指定目标 CPU 架构 | `amd64` |
| `--digest DIGEST` | 指定具体的 manifest digest，格式为 `sha256:xxx`；指定后跳过平台匹配，直接使用该 digest | — |

> [!warning]
> 原文命令格式使用 `docker_pull_v2.py`，示例使用 `docker_pull.py`。实际执行时应以下载脚本的文件名为准。

## 使用示例

### 1. 拉取 Docker Hub 最新 Ubuntu 镜像

默认目标平台为 `linux/amd64`：

```bash
python docker_pull.py ubuntu:latest
```

### 2. 拉取指定架构的镜像

例如拉取 ARM64 镜像：

```bash
python docker_pull.py quay.io/ascend/vllm-ascend:DeepSeekV4-flash-0731 --os linux --architecture arm64
```

### 3. 拉取指定 digest 的镜像

```bash
python docker_pull.py quay.io/ascend/vllm-ascend:DeepSeekV4-flash-0731 --digest sha256:abc123...
```

### 4. 查看帮助

```bash
python docker_pull.py -h
```

脚本会在当前目录生成一个 `.tar` 文件，可在安装 Docker 的目标主机上导入：

```bash
docker load -i <生成的.tar文件>
```

## 断点续传

- 每层下载时会生成 `layer_gzip.tar` 临时文件。
- 如果下载中断，再次运行脚本会自动检测并继续下载。
- 已解压完成的 `layer.tar` 会被自动跳过，不会重复下载。
- 如果 Registry 不支持 Range 请求，则会从头重新下载该层。

## 自动重试

- 网络超时、连接重置、HTTP 5xx 等错误会触发重试。
- 最多重试 5 次，每次间隔呈指数增长，例如 `2s`、`4s`、`8s`。
- 断点续传与重试结合时，每次重试都会从已下载的部分继续。
- 如果所有重试都失败，脚本会报错退出。

## 注意事项

- 需要 Python 3 和 `requests` 库：

  ```bash
  pip install requests
  ```

- 对于需要认证的私有仓库，应确保网络可达且凭证正确。
- 如果目标镜像不存在指定平台，脚本会列出可用平台并默认选择第一个。

脚本项目地址：[docker_image_downloader](https://gitee.com/UchihaItachi1990128/docker_image_downloader)
