---
title: 全库文档盘点
tags:
  - knowledgebase/inventory
date: 2026-04-16
---

# 全库文档盘点

> [!info] 统计概览
> - **总文档数**：297 个 Markdown 文件（不含 README 和本知识库）
> - **顶层目录**：17 个主题领域
> - **有 Frontmatter**：294 个（99%）
> - **有 Wikilink 双链**：92 个（31%）
> - **扫描日期**：2026-04-16

---

## AI（26 篇）

### ClaudeCode/（5 篇）

| 文件 | 标题 | Frontmatter | 双链 |
|------|------|:-----------:|:----:|
| [[AI/ClaudeCode/ClaudeCode基础指南|ClaudeCode基础指南]] | Claude Code 使用指南 | ✅ | ✅ |
| [[AI/ClaudeCode/Claude Code 扩展体系|扩展体系]] | MCP + Skills + Slash Commands + Plugin | ✅ | ❌ |
| [[AI/ClaudeCode/多智能体协作-Subagents与Agent-Teams|多智能体协作]] | Subagents 与 Agent Teams | ✅ | ❌ |
| [[AI/ClaudeCode/obsidian-claude-搭建个人知识库|obsidian-claude-搭建个人知识库]] | Obsidian + Claude Code 搭建 AI 知识库 | ✅ | ✅ |

### skills/k8s-report-skills/（自研 Skill - Python 版，3 篇）

| 文件 | 标题 | Frontmatter | 双链 |
|------|------|:-----------:|:----:|
| [[AI/skills/k8s-report-skills/SKILL.md|SKILL.md]] | K8s Inspector Skill 定义 | ✅ | ❌ |
| [[AI/skills/k8s-report-skills/k8s_inspector.py|k8s_inspector.py]] | K8s 巡检 Python 主脚本 | — | — |
| [[AI/skills/k8s-report-skills/templates/report.html|report.html]] | Jinja2 HTML 报告模板 | — | — |

### skills/k8s-inspect-skills/（自研 Skill - Shell 版，2 篇）

| 文件 | 标题 | Frontmatter | 双链 |
|------|------|:-----------:|:----:|
| [[AI/skills/k8s-inspect-skills/SKILL.md|SKILL.md]] | K8s Inspect Skill 定义 | ✅ | ❌ |
| [[AI/skills/k8s-inspect-skills/k8s_inspect.sh|k8s_inspect.sh]] | K8s 巡检 Shell 脚本 | — | — |

### agents/（8 个智能体定义，含 4 个 Skills）

| 智能体 | 核心文件 | 附带 Skills |
|--------|---------|-------------|
| aiops | IDENTITY.md / SOUL.md / AGENTS.md / HEARTBEAT.md | k8s-install-orchestrator |
| architect | IDENTITY.md / SOUL.md / AGENTS.md / HEARTBEAT.md | — |
| backend-engineer | IDENTITY.md / SOUL.md / AGENTS.md / HEARTBEAT.md | — |
| container | IDENTITY.md / SOUL.md / AGENTS.md / HEARTBEAT.md | docker-runtime-install（含脚本） |
| frontend-engineer | IDENTITY.md / SOUL.md / AGENTS.md / HEARTBEAT.md | — |
| k8s | IDENTITY.md / SOUL.md / AGENTS.md / HEARTBEAT.md | k8s-cluster-install |
| linux | IDENTITY.md / SOUL.md / AGENTS.md / HEARTBEAT.md | rocky-linux10-init（含脚本） |
| pm | IDENTITY.md / SOUL.md / AGENTS.md / HEARTBEAT.md | — |

### GithubCopilot/（1 篇）

| 文件 | 标题 | Frontmatter | 双链 |
|------|------|:-----------:|:----:|
| [[AI/GithubCopilot/Copilot CLI|Copilot CLI]] | GitHub Copilot CLI | ✅ | ❌ |

### OpenClaw/（7 篇）

| 文件 | 标题 | Frontmatter | 双链 |
|------|------|:-----------:|:----:|
| [[AI/OpenClaw/CoPaw|CoPaw]] | CoPaw | ✅ | ❌ |
| [[AI/OpenClaw/OpenClaw-Channels|OpenClaw-Channels]] | OpenClaw Channel 配置 | ✅ | ❌ |
| [[AI/OpenClaw/OpenClaw-Skills-插件|OpenClaw-Skills-插件]] | OpenClaw Skills 与插件 | ✅ | ❌ |
| [[AI/OpenClaw/OpenClaw-基础-安装|OpenClaw-基础-安装]] | OpenClaw 基础与安装 | ✅ | ❌ |
| [[AI/OpenClaw/Openclaw-AIOps|Openclaw-AIOps]] | OpenClaw AIOps | ✅ | ❌ |
| [[AI/OpenClaw/Openclaw-多智能体|Openclaw-多智能体]] | OpenClaw 多智能体 | ✅ | ❌ |
| [[AI/OpenClaw/Ubuntu-2510-Setup-Guide|Ubuntu-2510-Setup-Guide]] | Ubuntu 25.10 初始化配置指南 | ✅ | ❌ |

### 其他（1 篇）

| 文件 | 标题 | Frontmatter | 双链 |
|------|------|:-----------:|:----:|
| [[AI/提示词|提示词]] | 提示词 | ✅ | ❌ |

---

## Aliyun（19 篇）

### 计算/（4 篇）

| 文件 | 标题 | Frontmatter | 双链 |
|------|------|:-----------:|:----:|
| [[Aliyun/计算/ECS|ECS]] | 弹性计算服务 ECS | ✅ | ✅ |
| [[Aliyun/计算/主机迁移工具SMC|主机迁移工具SMC]] | 主机迁移工具 SMC | ✅ | ✅ |
| [[Aliyun/计算/云盘-快照-镜像|云盘-快照-镜像]] | 云盘、快照与镜像 | ✅ | ✅ |
| [[Aliyun/计算/弹性伸缩ESS|弹性伸缩ESS]] | 弹性伸缩 ESS | ✅ | ✅ |

### 网络/（8 篇）

| 文件 | 标题 | Frontmatter | 双链 |
|------|------|:-----------:|:----:|
| [[Aliyun/网络/VPC|VPC]] | 专有网络 VPC | ✅ | ✅ |
| [[Aliyun/网络/CEN-TR|CEN-TR]] | 云企业网 CEN 与转发路由器 TR | ✅ | ✅ |
| [[Aliyun/网络/负载均衡SLB|负载均衡SLB]] | 负载均衡 SLB | ✅ | ✅ |
| [[Aliyun/网络/DNS-CDN-SSL|DNS-CDN-SSL]] | DNS、CDN 与 SSL 证书 | ✅ | ✅ |
| [[Aliyun/网络/WAF|WAF]] | Web 应用防火墙 WAF | ✅ | ✅ |
| [[Aliyun/网络/DDoS高防|DDoS高防]] | DDoS 防护 | ✅ | ✅ |
| [[Aliyun/网络/云安全中心-云防火墙|云安全中心-云防火墙]] | 云安全中心与云防火墙 | ✅ | ✅ |
| [[Aliyun/网络/网关-VPN-专线|网关-VPN-专线]] | 网关-VPN-专线 | ✅ | ✅ |

### 存储/（3 篇）

| 文件 | 标题 | Frontmatter | 双链 |
|------|------|:-----------:|:----:|
| [[Aliyun/存储/对象存储OSS|对象存储OSS]] | 对象存储 OSS | ✅ | ✅ |
| [[Aliyun/存储/数据湖-HDFS-POSIX|数据湖-HDFS-POSIX]] | 数据湖-HDFS-POSIX | ✅ | ✅ |
| [[Aliyun/存储/跨域共享CORS|跨域共享CORS]] | 跨域共享 CORS | ✅ | ✅ |

### 数据库/（2 篇）

| 文件 | 标题 | Frontmatter | 双链 |
|------|------|:-----------:|:----:|
| [[Aliyun/数据库/关系型数据库RDS|关系型数据库RDS]] | 关系型数据库 RDS | ✅ | ✅ |
| [[Aliyun/数据库/数据传输服务DTS|数据传输服务DTS]] | 数据传输服务 DTS | ✅ | ✅ |

### 资源管理/（1 篇） + 认证（1 篇）

| 文件 | 标题 | Frontmatter | 双链 |
|------|------|:-----------:|:----:|
| [[Aliyun/资源管理/Landing Zone|Landing Zone]] | Landing Zone | ✅ | ✅ |
| [[Aliyun/ACP考试|ACP考试]] | ACP 云计算工程师考试笔记 | ✅ | ✅ |

---

## Azure（21 篇）

| 文件 | 标题 | Frontmatter | 双链 |
|------|------|:-----------:|:----:|
| [[Azure/0_Azure-VM-VMSS|0_Azure-VM-VMSS]] | Azure VM and VMSS | ✅ | ✅ |
| [[Azure/1_Azure-Linux-VM-troubheshooting|1_Azure-Linux-VM-troubheshooting]] | Azure Linux VM Troubleshooting | ✅ | ✅ |
| [[Azure/2_AKS-basics|2_AKS-basics]] | AKS Basics | ✅ | ✅ |
| [[Azure/3_AKS-workload-identity|3_AKS-workload-identity]] | AKS Workload Identity | ✅ | ✅ |
| [[Azure/4_AKS-SecretProviderClass-KeyVault|4_AKS-SecretProviderClass-KeyVault]] | AKS SecretProviderClass with KeyVault | ✅ | ✅ |
| [[Azure/5_Azure-Storage|5_Azure-Storage]] | Azure Storage | ✅ | ✅ |
| [[Azure/6_Azure-Networking|6_Azure-Networking]] | Azure Networking | ✅ | ✅ |
| [[Azure/7_ACR-ACI|7_ACR-ACI]] | Azure Container Registry & ACI | ✅ | ✅ |
| [[Azure/8_Azure-devops-basics|8_Azure-devops-basics]] | Azure DevOps Basics | ✅ | ✅ |
| [[Azure/9_Azure-devops-self-host-agents|9_Azure-devops-self-host-agents]] | Azure DevOps Self-Hosted Agents | ✅ | ✅ |
| [[Azure/10_Azure-devops-agent-pool-management|10_Azure-devops-agent-pool-management]] | Azure DevOps Agent Pool Management | ✅ | ✅ |
| [[Azure/11_Azure-Policy|11_Azure-Policy]] | Azure Policy | ✅ | ✅ |
| [[Azure/IO-monitor|IO-monitor]] | IO Monitor | ✅ | ✅ |
| [[Azure/Jfrog-artifactory-Azure|Jfrog-artifactory-Azure]] | JFrog Artifactory on Azure | ✅ | ✅ |
| [[Azure/Kusto Query|Kusto Query]] | Kusto Query Language (KQL) | ✅ | ✅ |
| [[Azure/command-line-tools|command-line-tools]] | Command Line Tools | ✅ | ✅ |
| [[Azure/perfMon ProcessMon|perfMon ProcessMon]] | PerfMon & ProcessMon | ✅ | ✅ |
| [[Azure/Customer Support/Email Templates|Email Templates]] | Email Templates | ✅ | ❌ |
| [[Azure/browser trace|browser trace]] | Browser Trace (HAR) | ✅ | ❌ |
| [[Azure/fiddler|fiddler]] | Fiddler | ✅ | ❌ |
| [[Azure/postman|postman]] | Postman | ✅ | ❌ |

---

## Docker-Kubernetes（145 篇）

> [!note] 仓库最大领域，占全库 48.5%，覆盖 19 个子目录

### k8s-basic-resources/（20 篇）

| 文件 | 标题 | FM | 链 |
|------|------|:--:|:--:|
| [[Docker-Kubernetes/k8s-basic-resources/k8s基础-架构-组件-资源|k8s基础-架构-组件-资源]] | K8s架构-组件-资源 | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-basic-resources/k8s基础-pod|k8s基础-pod]] | K8s基础-Pod | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-basic-resources/K8s基础-pod调度-亲和力|K8s基础-pod调度-亲和力]] | Pod调度-亲和力 | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-basic-resources/k8s基础-deployment|k8s基础-deployment]] | Deployment | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-basic-resources/k8s基础-daemonset|k8s基础-daemonset]] | DaemonSet | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-basic-resources/k8s基础-statefulset|k8s基础-statefulset]] | StatefulSet | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-basic-resources/k8s基础-job-cronjob|k8s基础-job-cronjob]] | Job-CronJob | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-basic-resources/k8s基础-Service|k8s基础-Service]] | Service | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-basic-resources/k8s基础-ingress|k8s基础-ingress]] | Ingress | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-basic-resources/k8s基础-configMap-Secret|k8s基础-configMap-Secret]] | configMap-Secret | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-basic-resources/k8s基础-storage|k8s基础-storage]] | Storage | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-basic-resources/k8s基础-namespace-资源分配|k8s基础-namespace-资源分配]] | namespace-资源分配 | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-basic-resources/k8s基础-yaml|k8s基础-yaml]] | YAML | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-basic-resources/k8s基础-Calico|k8s基础-Calico]] | Calico | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-basic-resources/k8s基础-kubeadm|k8s基础-kubeadm]] | kubeadm | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-basic-resources/k8s基础-临时容器ephemeral|k8s基础-临时容器ephemeral]] | 临时容器 | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-basic-resources/k8s基础-容器运行时-containerd|k8s基础-容器运行时-containerd]] | 容器运行时-containerd | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-basic-resources/k8s基础-自定义CRD资源|k8s基础-自定义CRD资源]] | 自定义CRD | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-basic-resources/k8s基础-认证-授权-准入|k8s基础-认证-授权-准入]] | 认证-授权-准入 | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-basic-resources/Python调用k8s-api实现资源管理|Python调用k8s-api实现资源管理]] | Python调用K8s-API | ✅ | ❌ |

### k8s-monitoring-logging/（20 篇）

| 文件 | 标题 | FM | 链 |
|------|------|:--:|:--:|
| [[Docker-Kubernetes/k8s-monitoring-logging/Prometheus基础|Prometheus基础]] | Prometheus基础 | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-monitoring-logging/helm部署prometheus-stack全家桶|helm部署prometheus-stack全家桶]] | Helm部署Prometheus-Stack | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-monitoring-logging/Prometheus监控k8s系统组件|Prometheus监控k8s系统组件]] | 监控K8s系统组件 | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-monitoring-logging/Prometheus监控外部k8s集群|Prometheus监控外部k8s集群]] | 监控外部K8s集群 | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-monitoring-logging/Prometheus监控非云原生应用-主机|Prometheus监控非云原生应用-主机]] | 监控非云原生应用 | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-monitoring-logging/helm部署Loki-promtail-tempo-grafanaAgent全家桶|helm部署Loki-promtail-tempo-grafanaAgent全家桶]] | Loki+Tempo全家桶 | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-monitoring-logging/helm部署jaeger|helm部署jaeger]] | Jaeger | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-monitoring-logging/k8s日志管理|k8s日志管理]] | 日志管理 | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-monitoring-logging/k8s监控EFK+logstash+kafka|k8s监控EFK+logstash+kafka]] | EFK+Logstash+Kafka | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-monitoring-logging/k8s监控ES(7.2)+Kibana(7.2)+Fluentd(v1.4.2)|k8s监控ES(7.2)+Kibana(7.2)+Fluentd(v1.4.2)]] | ES+Kibana+Fluentd | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-monitoring-logging/k8s监控Prometheus(v2.2.1)|k8s监控Prometheus(v2.2.1)]] | Prometheus(v2.2.1) | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-monitoring-logging/k8s监控Prometheus(v2.33.5)+Grafana(v8.4.5)|k8s监控Prometheus(v2.33.5)+Grafana(v8.4.5)]] | Prometheus+Grafana | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-monitoring-logging/k8s监控alertmanager(v0.14.0)|k8s监控alertmanager(v0.14.0)]] | Alertmanager | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-monitoring-logging/k8s部署elasticsearch集群|k8s部署elasticsearch集群]] | Elasticsearch集群 | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-monitoring-logging/k8s部署grafana(v5.0.4)|k8s部署grafana(v5.0.4)]] | Grafana | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-monitoring-logging/k8s部署全链路追踪-Skywalking|k8s部署全链路追踪-Skywalking]] | Skywalking | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-monitoring-logging/二进制部署Prometheus(v2.32.1)联邦集群|二进制部署Prometheus(v2.32.1)联邦集群]] | Prometheus联邦集群 | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-monitoring-logging/二进制部署efk+logstash+kafka日志收集平台|二进制部署efk+logstash+kafka日志收集平台]] | 二进制EFK | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-monitoring-logging/二进制部署prometheus-grafana-nodeexporter|二进制部署prometheus-grafana-nodeexporter]] | 二进制Prometheus | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-monitoring-logging/基于helm+operator部署ECK日志收集平台|基于helm+operator部署ECK日志收集平台]] | ECK日志平台 | ✅ | ❌ |

### k8s-CICD/（19 篇）

| 文件 | 标题 | FM | 链 |
|------|------|:--:|:--:|
| [[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD基础|ArgoCD基础]] | ArgoCD基础 | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD Image Updater|ArgoCD Image Updater]] | ArgoCD Image Updater | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD部署Helm应用时域名解析失败问题排查与解决|ArgoCD部署Helm应用时域名解析失败问题排查与解决]] | ArgoCD域名问题排查 | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-CICD/ArgoCD/学习链接|学习链接]] | ArgoCD学习链接 | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-CICD/Jenkins/k8s-Devops平台落地-基于jenkins|k8s-Devops平台落地-基于jenkins]] | K8s DevOps平台落地 | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-CICD/Jenkins/k8s部署基于Jenkins(2.394)的DevOps工具链-基于yaml|k8s部署基于Jenkins(2.394)的DevOps工具链-基于yaml]] | Jenkins 2.394 DevOps | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-CICD/Jenkins/k8s部署基于Jenkins(2.426.3)的Devops工具链-基于yaml|k8s部署基于Jenkins(2.426.3)的Devops工具链-基于yaml]] | Jenkins 2.426.3 DevOps | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-CICD/Jenkins/Jenkins语法-基于docker部署|Jenkins语法-基于docker部署]] | Jenkins语法 | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-CICD/Jenkins/docker部署jenkins|docker部署jenkins]] | Docker部署Jenkins | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-CICD/Jenkins/helm部署jenkins|helm部署jenkins]] | Helm部署Jenkins | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-CICD/Jenkins/二进制安装Jenkins(2.319)|二进制安装Jenkins(2.319)]] | 二进制安装Jenkins | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-CICD/Gitlab/helm部署gitlab|helm部署gitlab]] | Helm部署GitLab | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-CICD/Gitlab/k8s部署Gitlab(11.8.1)-基于yaml|k8s部署Gitlab(11.8.1)-基于yaml]] | K8s部署GitLab | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-CICD/Gitlab/二进制安装Gitlab(17.9.8)|二进制安装Gitlab(17.9.8)]] | 二进制安装GitLab | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-CICD/Tekton/k8s部署原生的CICD工具Tekton-基于yaml|k8s部署原生的CICD工具Tekton-基于yaml]] | Tekton部署 | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-CICD/Tekton/基于Tekton的云原生平台落地|基于Tekton的云原生平台落地]] | Tekton云原生平台 | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-CICD/Kustomize/k8s配置定制工具-kustomize|k8s配置定制工具-kustomize]] | Kustomize | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-CICD/使用github action部署helmchart|使用github action部署helmchart]] | GitHub Action部署Helm | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-CICD/发布go-python-java代码到K8S环境|发布go-python-java代码到K8S环境]] | 发布代码到K8S | ✅ | ❌ |

### k8s-installation-management/（16 篇）

| 文件 | 标题 | FM | 链 |
|------|------|:--:|:--:|
| [[Docker-Kubernetes/k8s-installation-management/latest-version/安装k8s-1.35-基于rockylinux10-最新步骤|安装k8s-1.35-基于rockylinux10-最新步骤]] | K8s 1.35 (最新) | ✅ | ✅ |
| [[Docker-Kubernetes/k8s-installation-management/2025最新-企业级高可用集群-基于rockylinux|2025最新-企业级高可用集群-基于rockylinux]] | 企业级高可用集群 | ✅ | ✅ |
| [[Docker-Kubernetes/k8s-installation-management/二进制安装k8s高可用集群|二进制安装k8s高可用集群]] | 二进制安装高可用 | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-installation-management/etcd高可用配置以及模拟集群故障和恢复|etcd高可用配置以及模拟集群故障和恢复]] | etcd高可用 | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-installation-management/k8s两地三中心架构|k8s两地三中心架构]] | 两地三中心 | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-installation-management/k8s多集群kubeconfig管理|k8s多集群kubeconfig管理]] | kubeconfig管理 | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-installation-management/k8s故障排查指南|k8s故障排查指南]] | 故障排查 | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-installation-management/k8s生产环境优化与最佳实践|k8s生产环境优化与最佳实践]] | 生产环境优化 | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-installation-management/k8s迁移容器运行时-版本升级|k8s迁移容器运行时-版本升级]] | 运行时迁移 | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-installation-management/legacy-versions/安装k8s-1.20.6-高可用|安装k8s-1.20.6-高可用]] | K8s 1.20.6 | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-installation-management/legacy-versions/安装k8s-1.23|安装k8s-1.23]] | K8s 1.23 | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-installation-management/legacy-versions/安装k8s-1.26-1.27|安装k8s-1.26-1.27]] | K8s 1.26-1.27 | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-installation-management/legacy-versions/安装k8s-1.28|安装k8s-1.28]] | K8s 1.28 | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-installation-management/legacy-versions/安装k8s-1.30-基于rockylinux|安装k8s-1.30-基于rockylinux]] | K8s 1.30 | ✅ | ❌ |
| [[Docker-Kubernetes/k8s-installation-management/legacy-versions/安装k8s-1.32-基于rockylinux|安装k8s-1.32-基于rockylinux]] | K8s 1.32 | ✅ | ✅ |
| [[Docker-Kubernetes/k8s-installation-management/legacy-versions/安装k8s-1.33-基于rockylinux-最新步骤|安装k8s-1.33-基于rockylinux-最新步骤]] | K8s 1.33 | ✅ | ✅ |

### docker/（12 篇）

| 文件 | 标题 | FM | 链 |
|------|------|:--:|:--:|
| [[Docker-Kubernetes/docker/docker基础|docker基础]] | Docker基础 | ✅ | ❌ |
| [[Docker-Kubernetes/docker/docker部署UI工具portainer-部署redis-sentinel|docker部署UI工具portainer-部署redis-sentinel]] | Portainer+Redis | ✅ | ❌ |
| [[Docker-Kubernetes/docker/docker部署gitlab|docker部署gitlab]] | Docker部署GitLab | ✅ | ❌ |
| [[Docker-Kubernetes/docker/docker部署lnmp网站|docker部署lnmp网站]] | Docker LNMP | ✅ | ❌ |
| [[Docker-Kubernetes/docker/docker部署loki|docker部署loki]] | Docker Loki | ✅ | ❌ |
| [[Docker-Kubernetes/docker/docker部署nginx-tomcat-httpd-go-python服务|docker部署nginx-tomcat-httpd-go-python服务]] | Nginx/Tomcat/Go/Python | ✅ | ❌ |
| [[Docker-Kubernetes/docker/docker部署prometheus-grafana-cAdvisior监控|docker部署prometheus-grafana-cAdvisior监控]] | Prometheus+Grafana | ✅ | ❌ |
| [[Docker-Kubernetes/docker/docker部署仓库平台homebox|docker部署仓库平台homebox]] | Homebox | ✅ | ❌ |
| [[Docker-Kubernetes/docker/docker部署定时任务工具gocron|docker部署定时任务工具gocron]] | GoCron | ✅ | ❌ |
| [[Docker-Kubernetes/docker/docker部署路由监控工具NextTrace|docker部署路由监控工具NextTrace]] | NextTrace | ✅ | ❌ |
| [[Docker-Kubernetes/docker/docker配置NVIDIA GPU|docker配置NVIDIA GPU]] | Docker GPU | ✅ | ❌ |
| [[Docker-Kubernetes/docker/docker配置代理|docker配置代理]] | Docker代理 | ✅ | ❌ |

### 其他子目录（58 篇）

| 子目录 | 篇数 | 代表性文章 |
|--------|------|-----------|
| k8s-db-middleware/ | 10 | [[Docker-Kubernetes/k8s-db-middleware/Operator部署mysql集群|Operator部署mysql集群]]、[[Docker-Kubernetes/k8s-db-middleware/helm部署strimzi-kafka|helm部署strimzi-kafka]] |
| k8s-UI-tools/ | 8 | [[Docker-Kubernetes/k8s-UI-tools/kubectl-可视化插件k9s-stern|kubectl-可视化插件k9s-stern]]、[[Docker-Kubernetes/k8s-UI-tools/rancher(v2.6.4)管理k8s集群|rancher(v2.6.4)管理k8s集群]] |
| k8s-networking-service-mesh/ | 7 | [[Docker-Kubernetes/k8s-networking-service-mesh/k8s精细化流量管理-istio|k8s精细化流量管理-istio]]、[[Docker-Kubernetes/k8s-networking-service-mesh/helm部署ingress-nginx|helm部署ingress-nginx]] |
| k8s-security-auth/ | 7 | [[Docker-Kubernetes/k8s-security-auth/helm部署certmanager|helm部署certmanager]]、[[Docker-Kubernetes/k8s-security-auth/helm部署kyverno和policy-reporter|helm部署kyverno和policy-reporter]] |
| helm-operator/ | 6 | [[Docker-Kubernetes/helm-operator/helmv3-安装与使用|helmv3-安装与使用]] |
| k8s-scaling/ | 4 | [[Docker-Kubernetes/k8s-scaling/k8s-HPA-VPA|k8s-HPA-VPA]]、[[Docker-Kubernetes/k8s-scaling/k8s-基于KEDA的弹性能力|k8s-基于KEDA的弹性能力]] |
| k8s-storage/ | 3 | [[Docker-Kubernetes/k8s-storage/k8s-ceph部署与集成|k8s-ceph部署与集成]]、[[Docker-Kubernetes/k8s-storage/k8s-分布式存储CubeFS|k8s-分布式存储CubeFS]] |
| CKA-CKS/ | 3 | [[Docker-Kubernetes/CKA-CKS/CKA-备考|CKA-备考]]、[[Docker-Kubernetes/CKA-CKS/CKS-备考|CKS-备考]] |
| harbor/ | 2 | [[Docker-Kubernetes/harbor/harbor-basics|harbor-basics]] |
| container-platform/ | 2 | [[Docker-Kubernetes/container-platform/部署轻量级的K8S平台-K3S|部署轻量级的K8S平台-K3S]] |
| kubeblocks/ | 2 | [[Docker-Kubernetes/kubeblocks/kubeblocks部署WordPress|kubeblocks部署WordPress]] |
| k8s-springcloud/ | 1 | [[Docker-Kubernetes/k8s-springcloud/SpringCloud项目迁移到k8s实战|SpringCloud项目迁移到k8s实战]] |
| k8s-backup-dr/ | 1 | [[Docker-Kubernetes/k8s-backup-dr/k8s集群备份恢复-Velero|k8s集群备份恢复-Velero]] |
| k8s-ai-gpu/ | 1 | [[Docker-Kubernetes/k8s-ai-gpu/k8s配置NVIDIA GPU|k8s配置NVIDIA GPU]] |
| 根目录 | 1 | [[Docker-Kubernetes/简历指南|简历指南]] |

---

## Python（27 篇）

### python-基础/（8 篇）

| 文件 | 标题 | FM | 链 |
|------|------|:--:|:--:|
| [[Python/python-基础/python-basics|python-basics]] | 数据类型、运算符与基础语法 | ✅ | ✅ |
| [[Python/python-基础/python-OOP|python-OOP]] | 面向对象编程 | ✅ | ✅ |
| [[Python/python-基础/python-function|python-function]] | 函数 | ✅ | ✅ |
| [[Python/python-基础/python-exception-handling|python-exception-handling]] | 异常处理 | ✅ | ✅ |
| [[Python/python-基础/python-QA|python-QA]] | 知识总结与常见问题 | ✅ | ✅ |
| [[Python/python-基础/python包管理工具-uv|python包管理工具-uv]] | 包管理工具 uv | ✅ | ✅ |
| [[Python/python-基础/rockylinux配置python开发环境|rockylinux配置python开发环境]] | RockyLinux 环境配置 | ✅ | ✅ |
| [[Python/python-基础/windows配置python开发环境|windows配置python开发环境]] | Windows 环境配置 | ✅ | ✅ |

### python-运维开发/（10 篇）

| 文件 | 标题 | FM | 链 |
|------|------|:--:|:--:|
| [[Python/python-运维开发/python-Linux-operation|python-Linux-operation]] | Linux运维模块 | ✅ | ✅ |
| [[Python/python-运维开发/python-kubernetes-module|python-kubernetes-module]] | Kubernetes模块 | ✅ | ✅ |
| [[Python/python-运维开发/python-mysql|python-mysql]] | MySQL操作 | ✅ | ✅ |
| [[Python/python-运维开发/python-postgresql|python-postgresql]] | PostgreSQL操作 | ✅ | ✅ |
| [[Python/python-运维开发/python-elasticsearch|python-elasticsearch]] | Elasticsearch运维 | ✅ | ✅ |
| [[Python/python-运维开发/python-nginx|python-nginx]] | Nginx运维自动化 | ✅ | ✅ |
| [[Python/python-运维开发/python-tomcat|python-tomcat]] | Tomcat运维自动化 | ✅ | ✅ |
| [[Python/python-运维开发/python-fabric高级用法|python-fabric高级用法]] | Fabric高级用法 | ✅ | ✅ |
| [[Python/python-运维开发/python-GUI-tkinter|python-GUI-tkinter]] | GUI开发-Tkinter | ✅ | ✅ |
| [[Python/python-运维开发/python-游戏开发|python-游戏开发]] | 游戏开发 | ✅ | ✅ |

### python-网络编程-前端/（6 篇）

| 文件 | 标题 | FM | 链 |
|------|------|:--:|:--:|
| [[Python/python-网络编程-前端/python-Web开发-HTML-CSS-JS|python-Web开发-HTML-CSS-JS]] | Web开发基础 HTML/CSS/JS | ✅ | ✅ |
| [[Python/python-网络编程-前端/python-Web框架Django|python-Web框架Django]] | Django | ✅ | ✅ |
| [[Python/python-网络编程-前端/python-Web框架Flask|python-Web框架Flask]] | Flask | ✅ | ✅ |
| [[Python/python-网络编程-前端/python-request-module|python-request-module]] | Requests模块 | ✅ | ✅ |
| [[Python/python-网络编程-前端/python-socket-module|python-socket-module]] | Socket模块 | ✅ | ✅ |
| [[Python/python-网络编程-前端/python-爬虫|python-爬虫]] | 爬虫 | ✅ | ✅ |

### python-数据分析-AI大模型/（2 篇） + 电池参数（1 篇）

| 文件 | 标题 | FM | 链 |
|------|------|:--:|:--:|
| [[Python/python-数据分析-AI大模型/python-处理excel-word|python-处理excel-word]] | 处理Excel与Word | ✅ | ✅ |
| [[Python/python-数据分析-AI大模型/python-机器学习与预测|python-机器学习与预测]] | 机器学习与预测 | ✅ | ✅ |
| [[Python/电池参数提取统计工具开发/实验室电池参数一键统计工具开发|实验室电池参数一键统计工具开发]] | 电池参数统计工具 | ✅ | ✅ |

---

## Linux-Shell（24 篇）

| 文件 | 标题 | FM | 链 |
|------|------|:--:|:--:|
| [[Linux-Shell/Linux-learning-notes|Linux-learning-notes]] | Linux 学习笔记 | ✅ | ❌ |
| [[Linux-Shell/shell-scripts|shell-scripts]] | Shell 脚本 | ✅ | ✅ |
| [[Linux-Shell/LVM-RAID|LVM-RAID]] | LVM 与 RAID | ✅ | ❌ |
| [[Linux-Shell/ssh连接|ssh连接]] | SSH连接 | ✅ | ❌ |
| [[Linux-Shell/ssh远程执行多个命令|ssh远程执行多个命令]] | SSH远程执行 | ✅ | ❌ |
| [[Linux-Shell/linux环境变量管理|linux环境变量管理]] | 环境变量 | ✅ | ❌ |
| [[Linux-Shell/nmcli管理网络配置|nmcli管理网络配置]] | nmcli网络 | ✅ | ❌ |
| [[Linux-Shell/Linux终端配置proxy|Linux终端配置proxy]] | 终端代理 | ✅ | ❌ |
| [[Linux-Shell/ansible安装-rockylinux8|ansible安装-rockylinux8]] | Ansible安装 | ✅ | ❌ |
| [[Linux-Shell/配置zsh终端|配置zsh终端]] | zsh终端 | ✅ | ❌ |
| [[Linux-Shell/MacBook开发环境配置|MacBook开发环境配置]] | MacBook配置 | ✅ | ❌ |
| [[Linux-Shell/vscode|vscode]] | VSCode | ✅ | ❌ |
| [[Linux-Shell/screen后台运行任务|screen后台运行任务]] | screen后台 | ✅ | ❌ |
| [[Linux-Shell/inotifywait监控文件变化|inotifywait监控文件变化]] | inotifywait | ✅ | ❌ |
| [[Linux-Shell/samba文件共享服务|samba文件共享服务]] | Samba | ✅ | ❌ |
| [[Linux-Shell/开源堡垒机jumpserver部署|开源堡垒机jumpserver部署]] | JumpServer | ✅ | ❌ |
| [[Linux-Shell/系统信息查看|系统信息查看]] | 系统信息 | ✅ | ❌ |
| [[Linux-Shell/VMWare-using-notes|VMWare-using-notes]] | VMWare | ✅ | ❌ |
| [[Linux-Shell/Ubuntu基础操作|Ubuntu基础操作]] | Ubuntu基础 | ✅ | ❌ |
| [[Linux-Shell/Ubuntu安装显卡驱动|Ubuntu安装显卡驱动]] | Ubuntu显卡驱动 | ✅ | ❌ |
| [[Linux-Shell/Ubuntu安装Wechat|Ubuntu安装Wechat]] | Ubuntu Wechat | ✅ | ❌ |
| [[Linux-Shell/Ubuntu部署vftpd|Ubuntu部署vftpd]] | vsftpd | ✅ | ❌ |
| [[Linux-Shell/Ubuntu-unattended-upgrade管理|Ubuntu-unattended-upgrade管理]] | 安全补丁 | ✅ | ❌ |
| [[Linux-Shell/Ubuntu-修改启动内核|Ubuntu-修改启动内核]] | 修改内核 | ✅ | ❌ |

---

## 其他领域

### CloudComputing（7 篇）

| 文件 | 标题 | FM | 链 |
|------|------|:--:|:--:|
| [[CloudComputing/云原生|云原生]] | 云原生概念介绍 | ✅ | ❌ |
| [[CloudComputing/大话云计算|大话云计算]] | 大话云计算 | ✅ | ❌ |
| [[CloudComputing/极客时间-深入浅出云计算|极客时间-深入浅出云计算]] | 深入浅出云计算 | ✅ | ❌ |
| [[CloudComputing/图解云计算架构|图解云计算架构]] | 图解云计算架构 | ✅ | ❌ |
| [[CloudComputing/深入剖析Kubernetes|深入剖析Kubernetes]] | 深入剖析Kubernetes | ✅ | ❌ |
| [[CloudComputing/Openstack|Openstack]] | OpenStack | ✅ | ❌ |
| [[CloudComputing/Auth|Auth]] | 认证协议与SSO | ✅ | ❌ |

### Go（9 篇，全部有双链 ✅）

| 文件 | 标题 |
|------|------|
| [[Go/go-01-环境配置-基础|go-01-环境配置-基础]] | 环境配置与基础 |
| [[Go/go-变量-数据类型-运算|go-变量-数据类型-运算]] | 变量、数据类型与运算 |
| [[Go/go-分支-循环|go-分支-循环]] | 分支与循环控制 |
| [[Go/go-函数-包|go-函数-包]] | 函数与包 |
| [[Go/go-数组-切片-map|go-数组-切片-map]] | 数组、切片与Map |
| [[Go/go-面向对象|go-面向对象]] | 面向对象编程 |
| [[Go/go-错误处理|go-错误处理]] | 错误处理 |
| [[Go/go-web开发|go-web开发]] | Web开发 |
| [[Go/云原生开发-基础|云原生开发-基础]] | 云原生开发基础 |

### HPC（7 篇，全部有双链 ✅）

| 文件 | 标题 |
|------|------|
| [[HPC/CentOS7-slurm23.02-二进制安装|CentOS7-slurm23.02-二进制安装]] | CentOS7 Slurm 23.02 |
| [[HPC/Ubuntu2204-slurm-22.05.11-二进制安装|Ubuntu2204-slurm-22.05.11-二进制安装]] | Ubuntu 22.04 Slurm 22.05 |
| [[HPC/Ubuntu-2204-slurm-22.05.11-binary-installation|Ubuntu-2204-slurm-22.05.11-binary-installation]] | Slurm 22.05 (English) |
| [[HPC/Ubuntu2204-slurm- 23.11-deb安装|Ubuntu2204-slurm- 23.11-deb安装]] | Slurm 23.11 deb |
| [[HPC/PBS|PBS]] | PBS 作业调度 |
| [[HPC/PBS-cases|PBS-cases]] | PBS 实际案例 |
| [[HPC/Slurm-node-exporter|Slurm-node-exporter]] | Slurm Node Exporter |

### GPU-DeepLearning（4 篇）

| 文件 | 标题 | FM | 链 |
|------|------|:--:|:--:|
| [[GPU-DeepLearning/GPU-basics|GPU-basics]] | GPU 基础 | ✅ | ❌ |
| [[GPU-DeepLearning/GPU-exporter-grafana|GPU-exporter-grafana]] | GPU Exporter+Grafana | ✅ | ❌ |
| [[GPU-DeepLearning/NVIDIA-GPU-开启persistent mode|NVIDIA-GPU-开启persistent mode]] | NVIDIA Persistent Mode | ✅ | ❌ |
| [[GPU-DeepLearning/Server-basics|Server-basics]] | 服务器入门 | ✅ | ❌ |

### Database（3 篇，全部有双链 ✅）

| 文件 | 标题 |
|------|------|
| [[Database/MySQL入门|MySQL入门]] | MySQL入门 |
| [[Database/MGR部署MySQL5.7|MGR部署MySQL5.7]] | MGR部署MySQL5.7 |
| [[Database/源码安装redis-6.2.6-centos7|源码安装redis-6.2.6-centos7]] | 源码安装Redis |

### Middlewares（3 篇，⚠️ 无 Frontmatter）

| 文件 | 标题 | FM | 链 |
|------|------|:--:|:--:|
| [[Middlewares/Kafka|Kafka]] | Kafka | ❌ | ❌ |
| [[Middlewares/RabbitMQ|RabbitMQ]] | RabbitMQ | ❌ | ❌ |
| [[Middlewares/RocketMQ|RocketMQ]] | RocketMQ | ❌ | ❌ |

### 小型领域

| 领域 | 篇数 | 文件 |
|------|------|------|
| OS | 3 | [[OS/OS|OS]]、[[OS/OS-磁盘管理|OS-磁盘管理]]、[[OS/计算机组成原理|计算机组成原理]] |
| Networking | 2 | [[Networking/HTTP基础|HTTP基础]]、[[Networking/计算机网络基础|计算机网络基础]] |
| IaC | 2 | [[IaC/terraform-basics|terraform-basics]]、[[IaC/terraform-docs|terraform-docs]] |
| Git | 2 | [[Git/git-learning|git-learning]]、[[Git/Picgo-github图床配置|Picgo-github图床配置]] |
| SoftwareTesting | 2 | [[SoftwareTesting/软件工程基础|软件工程基础]]、[[SoftwareTesting/软件测试直播课笔记|软件测试直播课笔记]] |
| C++ | 1 | [[C++/C++LearningNotes|C++LearningNotes]] |
