---
title: "不依赖本地docker环境 从Docker Hub 下载镜像到本地 并保存为tar镜像文件"
source: "https://mp.weixin.qq.com/s/KtINb-TZxbvfuF7RwsBMVg?scene=1&click_id=458085540"
author:
  - "[[李超]]"
published:
created: 2026-09-05
description: "使用说明无需安装 Docker，直接从 Registry 拉取镜像并打包为 .tar 文件。"
tags:
  - "clippings"
---
李超 诗与远方和田野 *2026年8月13日 12:12*

#### 使用说明

无需安装 Docker，直接从 Registry 拉取镜像并打包为.tar 文件。 支持 Docker Hub、quay.io 等私有/公共 Registry。 自动处理 manifest list / OCI index，支持多架构镜像选择。 支持断点续传 + 自动重试：下载中断后再次运行，会自动跳过已完成的层， 并从断点继续未完成的层；网络波动时自动重试（最多 5 次，指数退避）。

python docker\_pull\_v2.py \[选项\] <镜像名称>

支持的选项: -h, --help 显示本帮助信息并退出 --os OS 指定目标操作系统平台 (默认: linux) --architecture ARCH 指定目标 CPU 架构 (默认: amd64) --digest DIGEST 指定具体的 manifest digest (格式: sha256:xxx) 指定后将跳过平台匹配，直接使用该 digest

使用示例:

## 1\. 拉取 Docker Hub 上的最新 ubuntu 镜像 (默认 linux/amd64)

```
python docker_pull.py ubuntu:latest
```

## 2\. 拉取指定架构的镜像 (如 ARM64)

```
python docker_pull.py quay.io/ascend/vllm-ascend:DeepSeekV4-flash-0731 --os linux --architecture arm64
```

## 3\. 拉取指定 digest 的镜像

```
python docker_pull.py quay.io/ascend/vllm-ascend:DeepSeekV4-flash-0731 --digest sha256:abc123...
```

## 4\. 查看帮助

```
python docker_pull.py -h
```

输出说明: 脚本会在当前目录生成一个.tar 文件，可直接通过 docker load 导入: docker load -i <生成的.tar文件>

断点续传说明:

- 每层下载时会生成 layer\_gzip.tar 临时文件
- 如果下载中断，再次运行脚本会自动检测并继续下载
- 已解压完成的 layer.tar 会被自动跳过，不会重复下载
- 如果 Registry 不支持 Range 请求，会从头重新下载该层

自动重试说明:

- 网络超时、连接重置、HTTP 5xx 等错误会自动重试
- 最多重试 5 次，每次间隔呈指数增长（2s, 4s, 8s...）
- 断点续传与重试结合：每次重试都从已下载的部分继续
- 如果所有重试都失败，脚本会报错退出

注意事项:

- 需要安装 Python 3 和 requests 库 (pip install requests)
- 对于需要认证的私有仓库，确保网络可达且凭证正确
- 如果目标镜像不存在指定平台，脚本会列出可用平台并默认选择第一个

欢迎大家 star 和 fork 我的代码

代码地址如下：

https://gitee.com/UchihaItachi1990128/docker\_image\_downloader

作者提示: 个人观点，仅供参考