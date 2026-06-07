---
title: "AI 接管 Kubernetes 运维——Kubernetes MCP Server + Dify"
source: "https://mp.weixin.qq.com/s/oXn1nooZqNWfHA2s6b6iEw"
created: 2026-06-07
tags:
  - AI/AIOps
  - kubernetes
  - MCP
  - dify
---

# AI 接管 Kubernetes 运维——Kubernetes MCP Server + Dify

## 一、背景

近两年，大模型正在快速进入企业运维领域。从最开始的智能问答、知识库，到如今的 AI Agent、AI 自动化运维，整个行业正在发生巨大变化。而在云原生领域，Kubernetes 的复杂度越来越高，传统依赖人工经验的运维方式已经越来越难满足企业需求。

在这种背景下，**Dify + Kubernetes MCP Server** 的组合，正在成为 AIOps（智能运维）的热门方案。它不仅让 AI 能"看懂 Kubernetes"，更让 AI 开始真正参与故障分析、集群巡检和运维辅助决策。

### Dify 简介

LangGenius 推出的 Dify 是当前非常热门的开源 AI 应用开发平台。它集成了大模型接入、工作流编排、知识库、Agent、插件系统等能力，可以帮助企业快速构建 AI 应用。相比传统从零开发 AI 平台，Dify 最大的优势是开箱即用、可视化程度高，并且支持多种大模型（GPT、Claude、DeepSeek 等）。很多企业已经开始使用 Dify 构建内部知识助手、AI 客服、智能办公系统以及 AI 运维平台。

## 二、核心特点

- **实时读取 Kubernetes 集群数据**：通过 Kubernetes MCP Server，AI 不再依赖静态训练数据，而是能够直接访问 Kubernetes API，实时获取集群状态信息，包括 Pod、Deployment、Node、Event 和 Service 等核心资源，从而让 AI 对当前集群运行情况具备"实时感知能力"，真正实现对生产环境的动态理解与分析。

- **支持自然语言运维**：用户无需掌握复杂的 kubectl 命令或 YAML 配置，只需用自然语言提问即可完成运维操作与问题分析，例如"为什么 Pod 一直重启？"这类问题，AI 会自动关联相关资源信息并进行分析，降低 Kubernetes 使用门槛，让运维交互更加直观和高效。

- **支持 AI 自动故障分析**：系统能够自动识别 Kubernetes 中的常见故障类型，例如 CrashLoopBackOff、OOMKilled、镜像拉取失败、调度失败以及 PVC 挂载异常等问题，并结合集群实时数据进行综合分析，从而快速定位问题根因，大幅提升故障排查效率。

- **支持企业知识库**：Dify 的 RAG 能力可以将企业内部的运维文档、SOP 流程、Kubernetes 最佳实践以及内部规范统一接入 AI，使其不仅能理解集群状态，还能结合企业知识进行决策，从而形成更加贴合企业环境的智能运维能力。

## 三、使用场景

- **Pod 故障排查**：在 Pod 出现异常时，AI 可以自动分析 Pod 重启、OOMKilled、探针失败、CrashLoopBackOff 以及镜像拉取异常等情况，并结合事件与日志信息快速定位问题原因，从而减少人工排查时间，提高故障恢复效率。

- **Deployment 异常分析**：当 Deployment 出现不可用或副本异常时，AI 可以自动分析副本数量不足、Readiness 探针失败以及调度异常等问题，并结合集群状态判断根因，帮助运维人员快速恢复业务服务。

- **Kubernetes 集群巡检**：AI 可以定期对集群进行智能巡检，自动识别 Pending Pod、异常 Event、高负载 Node、资源不足以及未设置 requests/limits 等问题，从而提前发现潜在风险，提升整体集群稳定性与可用性。

- **Node 故障分析**：在 Node 出现异常时，AI 可以分析 Node NotReady、taint 污点设置不合理、资源不足以及 Pod 无法调度等问题，并结合节点状态进行综合判断，帮助快速定位节点级故障并保障集群正常运行。

## 四、架构

```
┌────────────────┐     ┌──────────────────────────┐     ┌─────────────────┐
│                │     │                          │     │                 │
│   Dify (大脑)   │────▶│  Kubernetes MCP Server   │────▶│  Kubernetes     │
│                │     │       (桥梁)              │     │   (执行层)       │
│  理解自然语言    │     │  封装 K8s API 为安全工具   │     │  管理集群资源     │
│  任务规划        │     │  实现 MCP 协议标准        │     │                 │
│  决定调用工具    │     │                          │     │                 │
└────────────────┘     └──────────────────────────┘     └─────────────────┘
```

- **Dify（大脑）**：负责理解用户的自然语言指令，进行任务规划，并决定调用哪个工具
- **Kubernetes MCP Server（桥梁）**：作为一个实现了 MCP (Model Context Protocol) 的标准工具集，它将复杂的 Kubernetes API 调用封装成简单、安全的工具，供 Dify 调用
- **Kubernetes（执行层）**：接收并执行来自 MCP Server 的指令，管理集群资源

## 五、部署 Dify

```bash
# 克隆最新版本
git clone --branch "$(curl -s https://api.github.com/repos/langgenius/dify/releases/latest | jq -r .tag_name)" https://github.com/langgenius/dify.git

cd dify/docker

# 安装 docker-compose（如未安装）
curl -SL https://github.com/docker/compose/releases/download/v2.27.0/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 启动 Dify
docker-compose up -d
```

## 六、部署 Kubernetes MCP Server

```bash
# 下载二进制文件
wget https://github.com/containers/kubernetes-mcp-server/releases/latest/download/kubernetes-mcp-server-linux-amd64

# 安装到 PATH
chmod +x kubernetes-mcp-server-linux-amd64
mv kubernetes-mcp-server-linux-amd64 /usr/local/bin/kubernetes-mcp-server
```

## 七、启动 MCP Server

```bash
nohup kubernetes-mcp-server \
  --kubeconfig=$HOME/.kube/config \
  --read-only \
  --port 8080 \
  > mcp.log 2>&1 &
```

关键参数说明：
- `--kubeconfig`：指定 K8s 集群的 kubeconfig 文件路径
- `--read-only`：只读模式，确保 AI 不会意外修改集群资源（生产环境强烈建议）
- `--port`：MCP Server 监听端口

## 八、验证服务

```bash
curl http://<MCP_SERVER_IP>:8080/sse
# 预期输出：
# event: endpoint
# data: /sse?sessionid=OQ7ZERSXEADK3265QF3C5V4CLW
```

收到 SSE 事件响应说明 MCP Server 已正常启动。

## 九、在 Dify 中添加 MCP

在 Dify 管理后台添加 MCP Server 连接：

```
服务端点 URL：http://<MCP_SERVER_IP>:8080/sse
名称和图标：k8s-mcp
服务器标识符：k8s-mcp
```

## 十、创建 Agent 应用

在 Dify 中创建空白应用，配置如下：

```
名称：K8S超级助手
描述：你不只是 kubectl 命令替代工具，更是面向云原生场景的智能运维平台。通过统一入口整合资源管理、应用发布、日志观测与故障诊断能力，实现 Kubernetes 运维的标准化与自动化，大幅提升团队交付效率与系统稳定性。
```

### Agent 提示词（完整版）

```
你是一位专业的 Kubernetes 运维专家，名叫 K8s 超级助手，能够帮助用户高效管理和运维 Kubernetes 集群。

你的核心职责：
1. **理解用户需求**：用户会用自然语言描述集群操作需求，你需要将其转化为合法、安全的 `kubectl` 命令，或提供对应的操作方案。
2. **安全优先原则**：
   - 所有命令必须是只读或安全的操作，如查询、查看日志、描述资源。
   - 任何删除、修改、重启、配置变更类的高危操作，必须先向用户明确说明风险，并得到用户的二次确认后，再提供对应的命令。
   - 绝不猜测集群权限和上下文，默认使用 `default` 命名空间，用户未指定时优先询问。
3. **输出规范**：
   - 清晰说明命令的作用、适用场景。
   - 给出完整可直接复制的 `kubectl` 命令，并附带关键参数的解释。
   - 对于复杂问题，提供分步操作指南，而不是直接执行命令。
   - 当用户输入模糊或有歧义时，主动提问确认，比如：
     - "你要查询的资源是 Pod、Deployment 还是 Service？"
     - "操作的目标命名空间是什么？"
4. **故障排查能力**：当用户描述集群异常时，主动提供排查思路和对应命令，例如：
   - Pod 异常：`kubectl describe pod`、`kubectl logs`
   - 节点问题：`kubectl describe node`、`kubectl get events`
   - 资源不足：`kubectl top nodes`、`kubectl top pods`

交流风格：专业、简洁、清晰，优先给出可执行的命令和明确的步骤，同时兼顾安全性和易用性。
```

> 工具选择对应的 MCP（k8s-mcp）

## 十一、使用流程

配置完成后的使用流程：

1. 在 Dify 中添加并选择大模型（GPT、Claude、DeepSeek 等）
2. 发布 Agent 应用
3. 通过自然语言与 K8s 超级助手对话，例如：
   - "帮我查看 default 命名空间下所有 Pod 的状态"
   - "为什么 nginx-deployment 的 Pod 一直在重启？"
   - "检查一下集群中有没有 Pending 状态的 Pod"
   - "分析一下 node-1 的资源使用情况"
