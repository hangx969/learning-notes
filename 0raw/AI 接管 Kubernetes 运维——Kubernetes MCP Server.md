---
title: "AI 接管 Kubernetes 运维——Kubernetes MCP Server"
source: "https://mp.weixin.qq.com/s/oXn1nooZqNWfHA2s6b6iEw?scene=1"
author:
  - "[[运维大爆炸]]"
published:
created: 2026-06-05
description: "AI 接管 Kubernetes 运维——Kubernetes MCP Server"
tags:
  - "clippings"
---
运维大爆炸 *2026年5月26日 15:54*

## 1、简介

近两年，大模型正在快速进入企业运维领域。从最开始的智能问答、知识库，到如今的 AI Agent、AI 自动化运维，整个行业正在发生巨大变化。而在云原生领域，Kubernetes 的复杂度越来越高，传统依赖人工经验的运维方式已经越来越难满足企业需求。在这种背景下，Dify + Kubernetes MCP Server 的组合，正在成为 AI Ops（智能运维）的热门方案。它不仅让 AI 能“看懂 Kubernetes”，更让 AI 开始真正参与故障分析、集群巡检和运维辅助决策。

LangGenius 推出的 Dify 是当前非常热门的开源 AI 应用开发平台。它集成了大模型接入、工作流编排、知识库、Agent、插件系统等能力，可以帮助企业快速构建 AI 应用。相比传统从零开发 AI 平台，Dify 最大的优势是开箱即用、可视化程度高，并且支持多种大模型，例如 GPT、Claude、DeepSeek 等。很多企业已经开始使用 Dify 构建内部知识助手、AI 客服、智能办公系统以及 AI 运维平台。

## 2、Dify + Kubernetes MCP Server 核心特点

- **实时读取 Kubernetes 集群数据：** 通过 Kubernetes MCP Server，AI 不再依赖静态训练数据，而是能够直接访问 Kubernetes API，实时获取集群状态信息，包括 Pod、Deployment、Node、Event 和 Service 等核心资源，从而让 AI 对当前集群运行情况具备“实时感知能力”，真正实现对生产环境的动态理解与分析。
- **支持自然语言运维：** 用户无需掌握复杂的 kubectl 命令或 YAML 配置，只需用自然语言提问即可完成运维操作与问题分析，例如“为什么 Pod 一直重启？”这类问题，AI 会自动关联相关资源信息并进行分析，降低 Kubernetes 使用门槛，让运维交互更加直观和高效。
- **支持 AI 自动故障分析：** 系统能够自动识别 Kubernetes 中的常见故障类型，例如 CrashLoopBackOff、OOMKilled、镜像拉取失败、调度失败以及 PVC 挂载异常等问题，并结合集群实时数据进行综合分析，从而快速定位问题根因，大幅提升故障排查效率。
- **支持企业知识库：** Dify 的 RAG 能力可以将企业内部的运维文档、SOP 流程、Kubernetes 最佳实践以及内部规范统一接入 AI，使其不仅能理解集群状态，还能结合企业知识进行决策，从而形成更加贴合企业环境的智能运维能力。

## 3、Dify + Kubernetes MCP Server 使用场景

- **Pod 故障排查：** 在 Pod 出现异常时，AI 可以自动分析 Pod 重启、OOMKilled、探针失败、CrashLoopBackOff 以及镜像拉取异常等情况，并结合事件与日志信息快速定位问题原因，从而减少人工排查时间，提高故障恢复效率。
- **Deployment 异常分析：** 当 Deployment 出现不可用或副本异常时，AI 可以自动分析副本数量不足、Readiness 探针失败以及调度异常等问题，并结合集群状态判断根因，帮助运维人员快速恢复业务服务。
- **Kubernetes 集群巡检：** AI 可以定期对集群进行智能巡检，自动识别 Pending Pod、异常 Event、高负载 Node、资源不足以及未设置 requests/limits 等问题，从而提前发现潜在风险，提升整体集群稳定性与可用性。
- **Node 故障分析：** 在 Node 出现异常时，AI 可以分析 Node NotReady、taint 污点设置不合理、资源不足以及 Pod 无法调度等问题，并结合节点状态进行综合判断，帮助快速定位节点级故障并保障集群正常运行。

## 4、架构

![img](https://mmbiz.qpic.cn/sz_mmbiz_png/ibicibPByDZ7Zpkuzpib5mib6Xa666RbTK0LKubfdS7icRzVocLPackY7lAB4NJD6avlWbndEukuIOmGMXK7B3YOQGrI9lFicOpiaXdyFicXqxp0qp4g/640?wx_fmt=png&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

- **Dify (大脑)：** 负责理解用户的自然语言指令，进行任务规划，并决定调用哪个工具。
- **Kubernetes MCP Server (桥梁)：** 作为一个实现了 MCP (Model Context Protocol) 的标准工具集，它将复杂的 Kubernetes API 调用封装成简单、安全的工具，供 Dify 调用。
- **Kubernetes (执行层)：** 接收并执行来自 MCP Server 的指令，管理集群资源。

## 5、部署 Dify

```
[root@master ~]# git clone --branch "$(curl -s https://api.github.com/repos/langgenius/dify/releases/latest | jq -r .tag_name)" https://github.com/langgenius/dify.git

[root@master docker]# cd dify/docker

[root@master ~]# curl -SL https://github.com/docker/compose/releases/download/v2.27.0/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose

[root@master docker]# cd /usr/local/bin/
[root@master bin]# chmod +x /usr/local/bin/docker-compose

[root@master docker]# docker-compose up -d
```

## 6、部署 Kubernetes MCP Server

```
[root@master ~]# wget https://github.com/containers/kubernetes-mcp-server/releases/latest/download/kubernetes-mcp-server-linux-amd64

[root@master ~]# cd /usr/local/bin/

[root@master bin]# chmod +x kubernetes-mcp-server-linux-amd64

[root@master bin]# cp -rp kubernetes-mcp-server-linux-amd64 /usr/local/bin/

[root@master ~]# mv /usr/local/bin/kubernetes-mcp-server-linux-amd64 /usr/local/bin/kubernetes-mcp-server
```

## 7、启动 MCP

```
[root@master ~]# nohup kubernetes-mcp-server \
  --kubeconfig=$HOME/.kube/config \
  --read-only \
  --port8080 \
  > mcp.log 2>&1 &
```

## 8、验证服务

```
[root@master ~]# curl http://172.16.15.127:8080/sse
event: endpoint
data: /sse?sessionid=OQ7ZERSXEADK3265QF3C5V4CLW
```

## 9、添加map

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/ibicibPByDZ7ZpYR50Z20z3qLFkUMbhwqzicVDpSAa1K6wgb6rDPH0qWfGqr9ziaXbtPZjUgqIMLmObGN7jPDnkz0EzvEpO5kRhmKvnK7nhaMhqs/640?wx_fmt=png&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=1)

#### 配置

```
服务端点 URL：http://172.16.15.127:8080/sse
名称和图标：k8s-mcp
服务器标识符：k8s-mcp
```

## 10、添加agent

#### 创建空白应用

```
名称：K8S超级助手
描述：你不只是 kubectl 命令替代工具，更是面向云原生场景的智能运维平台。通过统一入口整合资源管理、应用发布、日志观测与故障诊断能力，实现 Kubernetes 运维的标准化与自动化，大幅提升团队交付效率与系统稳定性。
```

#### 编排与工具

```
提示词：你是一位专业的 Kubernetes 运维专家，名叫 K8s 超级助手，能够帮助用户高效管理和运维 Kubernetes 集群。

你的核心职责：
1.  **理解用户需求**：用户会用自然语言描述集群操作需求，你需要将其转化为合法、安全的 \`kubectl\` 命令，或提供对应的操作方案。
.  **安全优先原则**：

    - 所有命令必须是只读或安全的操作，如查询、查看日志、描述资源。
    - 任何删除、修改、重启、配置变更类的高危操作，必须先向用户明确说明风险，并得到用户的二次确认后，再提供对应的命令。
    - 绝不猜测集群权限和上下文，默认使用 \`default\` 命名空间，用户未指定时优先询问。
.  **输出规范**：

    - 清晰说明命令的作用、适用场景。
    - 给出完整可直接复制的 \`kubectl\` 命令，并附带关键参数的解释。
    - 对于复杂问题，提供分步操作指南，而不是直接执行命令。
    - 当用户输入模糊或有歧义时，主动提问确认，比如：
      - “你要查询的资源是 Pod、Deployment 还是 Service？”
      - “操作的目标命名空间是什么？”
.  **故障排查能力**：当用户描述集群异常时，主动提供排查思路和对应命令，例如：

    - Pod 异常：\`kubectl describe pod\`、\`kubectl logs\`
    - 节点问题：\`kubectl describe node\`、\`kubectl get events\`
    - 资源不足：\`kubectl top nodes\`、\`kubectl top pods\`

交流风格：专业、简洁、清晰，优先给出可执行的命令和明确的步骤，同时兼顾安全性和易用性。
```

<!--注：工具选择对应的mcp-->

## 11、添加模型

## 12、选择模型

## 13、实战

✨ **只写原创，不接广告，不接广告，不接广告。**

在这里，你将看到全新的技术分享、运维经验、以及最新的行业动态。我们坚信，原创内容才是最有价值的资源，所以所有文章都是独立创作，与你们一起成长。

💡 **下期想学习什么技术？**

如果你有任何学习需求或者感兴趣的技术话题，欢迎私信告诉我！我会根据大家的反馈选择下期的内容，帮助你们提升技能。

🌟 **运维知识星球**

我也创建了一个运维知识星球，专注于分享大量运维、开发和技术管理方面的原创文章、教程、工具和经验。如果你对技术有浓厚兴趣，欢迎加入我们！一起交流、一起进步！

**微信扫一扫赞赏作者**

大模型 · 目录

继续滑动看下一个

IT运维大爆炸

向上滑动看下一个