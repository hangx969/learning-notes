---
title: 工具地图
tags:
  - knowledgebase/map
  - knowledgebase/tools
aliases:
  - Tool Map
date: 2026-04-16
---

# 工具地图

> [!info] 按工具/平台/框架聚合知识，列出与每个工具相关的文档路径和推荐入口。

---

## AI 工具

### Claude Code
**相关文档（7 篇）：**
- [[AI/ClaudeCode/ClaudeCode基础指南]] ⭐ 推荐入口
- [[AI/ClaudeCode/MCP]] — MCP 协议配置
- [[AI/ClaudeCode/Plugin]] — 插件系统
- [[AI/ClaudeCode/Skills]] — Skills 机制
- [[AI/ClaudeCode/Slash Command]] — 斜杠命令
- [[AI/ClaudeCode/Subagents]] — 子智能体
- [[AI/ClaudeCode/obsidian-claude-搭建个人知识库]] — 搭建知识库方法论

**概念页：** [[KnowledgeBase/concepts/Claude-Code]]

---

### OpenClaw
**相关文档（7 篇）：**
- [[AI/OpenClaw/OpenClaw-基础-安装]] ⭐ 推荐入口
- [[AI/OpenClaw/OpenClaw-Channels]] — Channel 配置
- [[AI/OpenClaw/OpenClaw-Skills-插件]] — Skills 与插件
- [[AI/OpenClaw/Openclaw-AIOps]] — AIOps 场景
- [[AI/OpenClaw/Openclaw-多智能体]] — 多智能体（2974 行）
- [[AI/OpenClaw/CoPaw]] — CoPaw 工具
- [[AI/OpenClaw/Ubuntu-2510-Setup-Guide]] — Ubuntu 环境搭建

**概念页：** [[KnowledgeBase/concepts/OpenClaw]]

---

### MCP (Model Context Protocol)
**相关文档：**
- [[AI/ClaudeCode/MCP]] ⭐ 推荐入口

**概念页：** [[KnowledgeBase/concepts/MCP]]

---

### Obsidian
**相关文档：**
- [[AI/ClaudeCode/obsidian-claude-搭建个人知识库]] ⭐ 推荐入口

**概念页：** [[KnowledgeBase/concepts/Obsidian]]

---

### GitHub Copilot
**相关文档：**
- [[AI/GithubCopilot/Copilot CLI]]

---

## 容器与编排

### Docker
**相关文档（12+ 篇）：**
- [[Docker-Kubernetes/docker/docker基础]] ⭐ 推荐入口
- [[Docker-Kubernetes/docker/docker配置NVIDIA GPU]]
- [[Docker-Kubernetes/docker/docker配置代理]]
- [[Docker-Kubernetes/docker/docker部署gitlab]]
- [[Docker-Kubernetes/docker/docker部署loki]]
- [[Docker-Kubernetes/docker/docker部署prometheus-grafana-cAdvisior监控]]
- [[Docker-Kubernetes/docker/docker部署nginx-tomcat-httpd-go-python服务]]
- [[Docker-Kubernetes/docker/docker部署lnmp网站]]
- 及更多部署实战...

**概念页：** [[KnowledgeBase/concepts/Docker]]

---

### Kubernetes
**相关文档（130+ 篇）：**
- [[Docker-Kubernetes/k8s-basic-resources/k8s基础-架构-组件-资源]] ⭐ 推荐入口
- [[Docker-Kubernetes/k8s-installation-management/latest-version/安装k8s-1.35-基于rockylinux10-最新步骤]] — 最新安装
- 完整目录参见 [[KnowledgeBase/maps/kubernetes-map]]

**概念页：** [[KnowledgeBase/concepts/Kubernetes]]

---

### Helm
**相关文档（20+ 篇）：**
- [[Docker-Kubernetes/helm-operator/helmv3-安装与使用]] ⭐ 推荐入口
- [[Docker-Kubernetes/harbor/helm部署harbor]]
- [[Docker-Kubernetes/k8s-monitoring-logging/helm部署prometheus-stack全家桶]]
- [[Docker-Kubernetes/k8s-monitoring-logging/helm部署Loki-promtail-tempo-grafanaAgent全家桶]]
- [[Docker-Kubernetes/k8s-CICD/Jenkins/helm部署jenkins]]
- [[Docker-Kubernetes/k8s-networking-service-mesh/helm部署ingress-nginx]]
- [[Docker-Kubernetes/k8s-networking-service-mesh/helm安装istio]]
- [[Docker-Kubernetes/k8s-security-auth/helm部署certmanager]]
- 及更多 Helm 部署实战...

**概念页：** [[KnowledgeBase/concepts/Helm]]

---

### Istio
**相关文档（7 篇）：**
- [[Docker-Kubernetes/k8s-networking-service-mesh/k8s精细化流量管理-istio]] ⭐ 推荐入口
- [[Docker-Kubernetes/k8s-networking-service-mesh/helm安装istio]]
- [[Docker-Kubernetes/k8s-networking-service-mesh/k8s部署istio(1.13.1)]]
- [[Docker-Kubernetes/k8s-networking-service-mesh/企业项目接入istio实战]]
- [[Docker-Kubernetes/k8s-networking-service-mesh/k8s集群网络安全]]
- [[Docker-Kubernetes/k8s-networking-service-mesh/helm部署external-dns]]
- [[Docker-Kubernetes/k8s-networking-service-mesh/helm部署ingress-nginx]]

**概念页：** [[KnowledgeBase/concepts/Istio]]

---

### Harbor
**相关文档：**
- [[Docker-Kubernetes/harbor/harbor-basics]] ⭐ 推荐入口
- [[Docker-Kubernetes/harbor/helm部署harbor]]
- [[Docker-Kubernetes/kubeblocks/kubeblocks部署高可用harbor集群]]

---

## 可观测性

### Prometheus
**相关文档（10+ 篇）：**
- [[Docker-Kubernetes/k8s-monitoring-logging/Prometheus基础]] ⭐ 推荐入口
- [[Docker-Kubernetes/k8s-monitoring-logging/helm部署prometheus-stack全家桶]]
- [[Docker-Kubernetes/k8s-monitoring-logging/Prometheus监控k8s系统组件]]
- [[Docker-Kubernetes/k8s-monitoring-logging/Prometheus监控外部k8s集群]]
- [[Docker-Kubernetes/k8s-monitoring-logging/Prometheus监控非云原生应用-主机]]
- [[Docker-Kubernetes/k8s-monitoring-logging/k8s监控Prometheus(v2.33.5)+Grafana(v8.4.5)]]
- [[Docker-Kubernetes/k8s-monitoring-logging/二进制部署Prometheus(v2.32.1)联邦集群]]
- [[Docker-Kubernetes/k8s-monitoring-logging/二进制部署prometheus-grafana-nodeexporter]]
- [[Docker-Kubernetes/docker/docker部署prometheus-grafana-cAdvisior监控]]
- [[HPC/Slurm-node-exporter]]

**概念页：** [[KnowledgeBase/concepts/Prometheus]]

---

### Grafana
**相关文档：**
- [[Docker-Kubernetes/k8s-monitoring-logging/k8s部署grafana(v5.0.4)]] ⭐
- [[Docker-Kubernetes/k8s-monitoring-logging/helm部署prometheus-stack全家桶]]
- [[Docker-Kubernetes/k8s-monitoring-logging/二进制部署prometheus-grafana-nodeexporter]]
- [[GPU-DeepLearning/GPU-exporter-grafana]]

**概念页：** [[KnowledgeBase/concepts/Grafana]]

---

### Elasticsearch / EFK
**相关文档：**
- [[Docker-Kubernetes/k8s-monitoring-logging/k8s部署elasticsearch集群]] ⭐
- [[Docker-Kubernetes/k8s-monitoring-logging/k8s监控ES(7.2)+Kibana(7.2)+Fluentd(v1.4.2)]]
- [[Docker-Kubernetes/k8s-monitoring-logging/k8s监控EFK+logstash+kafka]]
- [[Docker-Kubernetes/k8s-monitoring-logging/二进制部署efk+logstash+kafka日志收集平台]]
- [[Docker-Kubernetes/k8s-monitoring-logging/基于helm+operator部署ECK日志收集平台]]
- [[Python/python-运维开发/python-elasticsearch]]

---

### Loki
**相关文档：**
- [[Docker-Kubernetes/k8s-monitoring-logging/helm部署Loki-promtail-tempo-grafanaAgent全家桶]] ⭐
- [[Docker-Kubernetes/docker/docker部署loki]]

---

## CI/CD 工具

### ArgoCD
**相关文档（4 篇）：**
- [[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD基础]] ⭐ 推荐入口
- [[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD Image Updater]]
- [[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD部署Helm应用时域名解析失败问题排查与解决]]
- [[Docker-Kubernetes/k8s-CICD/ArgoCD/学习链接]]

**概念页：** [[KnowledgeBase/concepts/ArgoCD]]

---

### Jenkins
**相关文档（7 篇）：**
- [[Docker-Kubernetes/k8s-CICD/Jenkins/k8s-Devops平台落地-基于jenkins]] ⭐ 推荐入口
- [[Docker-Kubernetes/k8s-CICD/Jenkins/Jenkins语法-基于docker部署]]
- [[Docker-Kubernetes/k8s-CICD/Jenkins/helm部署jenkins]]
- [[Docker-Kubernetes/k8s-CICD/Jenkins/docker部署jenkins]]
- [[Docker-Kubernetes/k8s-CICD/Jenkins/二进制安装Jenkins(2.319)]]
- 及 K8s 部署 Jenkins DevOps 工具链 2 篇

**概念页：** [[KnowledgeBase/concepts/Jenkins]]

---

### GitLab
**相关文档：**
- [[Docker-Kubernetes/k8s-CICD/Gitlab/二进制安装Gitlab(17.9.8)]] ⭐
- [[Docker-Kubernetes/k8s-CICD/Gitlab/helm部署gitlab]]
- [[Docker-Kubernetes/k8s-CICD/Gitlab/k8s部署Gitlab(11.8.1)-基于yaml]]
- [[Docker-Kubernetes/docker/docker部署gitlab]]

---

### Tekton
**相关文档：**
- [[Docker-Kubernetes/k8s-CICD/Tekton/基于Tekton的云原生平台落地]] ⭐
- [[Docker-Kubernetes/k8s-CICD/Tekton/k8s部署原生的CICD工具Tekton-基于yaml]]

---

## 基础设施即代码

### Terraform
**相关文档：**
- [[IaC/terraform-basics]] ⭐ 推荐入口
- [[IaC/terraform-docs]]

**概念页：** [[KnowledgeBase/concepts/Terraform]]

---

### Ansible
**相关文档：**
- [[Linux-Shell/ansible安装-rockylinux8]] ⭐

---

## 云平台

### Azure
**相关文档（21 篇）：**
- [[Azure/2_AKS-basics]] ⭐ 推荐入口（AKS）
- [[Azure/0_Azure-VM-VMSS]] — 虚拟机
- [[Azure/8_Azure-devops-basics]] — DevOps
- 完整列表参见 [[KnowledgeBase/maps/cloud-platform-map]]

**概念页：** [[KnowledgeBase/concepts/Azure]]

---

### Aliyun
**相关文档（19 篇）：**
- [[Aliyun/网络/VPC]] ⭐ 推荐入口
- [[Aliyun/计算/ECS]] — 弹性计算
- [[Aliyun/网络/负载均衡SLB]] — 负载均衡
- 完整列表参见 [[KnowledgeBase/maps/cloud-platform-map]]

**概念页：** [[KnowledgeBase/concepts/Aliyun]]

---

### AKS (Azure Kubernetes Service)
**相关文档：**
- [[Azure/2_AKS-basics]] ⭐
- [[Azure/3_AKS-workload-identity]]
- [[Azure/4_AKS-SecretProviderClass-KeyVault]]

**概念页：** [[KnowledgeBase/concepts/AKS]]

---

## 编程语言

### Python
**相关文档（27 篇）：**
- [[Python/python-基础/python-basics]] ⭐ 推荐入口
- 完整列表参见 [[KnowledgeBase/maps/python-devops-map]]

**概念页：** [[KnowledgeBase/concepts/Python运维开发]]

---

### Go
**相关文档（9 篇）：**
- [[Go/go-01-环境配置-基础]] ⭐ 推荐入口

---

## HPC 工具

### Slurm
**相关文档（5 篇）：**
- [[HPC/CentOS7-slurm23.02-二进制安装]] ⭐ 推荐入口
- [[HPC/Ubuntu2204-slurm-22.05.11-二进制安装]]
- [[HPC/Ubuntu-2204-slurm-22.05.11-binary-installation]]
- [[HPC/Ubuntu2204-slurm- 23.11-deb安装]]
- [[HPC/Slurm-node-exporter]]

**概念页：** [[KnowledgeBase/concepts/Slurm]]

---

### PBS
**相关文档：**
- [[HPC/PBS]] ⭐
- [[HPC/PBS-cases]]

---

## 消息中间件

### Kafka
- [[Middlewares/Kafka]] ⭐
- [[Docker-Kubernetes/k8s-db-middleware/helm部署strimzi-kafka]]
- [[Docker-Kubernetes/k8s-monitoring-logging/k8s监控EFK+logstash+kafka]]

### RabbitMQ
- [[Middlewares/RabbitMQ]] ⭐

### RocketMQ
- [[Middlewares/RocketMQ]] ⭐

---

## 数据库

### MySQL
- [[Database/MySQL入门]] ⭐
- [[Database/MGR部署MySQL5.7]]
- [[Docker-Kubernetes/k8s-db-middleware/helm部署mysql]]
- [[Docker-Kubernetes/k8s-db-middleware/Operator部署mysql集群]]
- [[Docker-Kubernetes/k8s-db-middleware/k8s基于yaml部署mysql主从高可用]]
- [[Python/python-运维开发/python-mysql]]

### Redis
- [[Database/源码安装redis-6.2.6-centos7]] ⭐
- [[Docker-Kubernetes/k8s-db-middleware/Operator部署Redis集群]]
- [[Docker-Kubernetes/k8s-db-middleware/k8s基于yaml部署redis集群]]

### PostgreSQL
- [[Docker-Kubernetes/k8s-db-middleware/helm部署postgreSQL]] ⭐
- [[Python/python-运维开发/python-postgresql]]

---

## GPU / NVIDIA
- [[GPU-DeepLearning/GPU-basics]] ⭐
- [[GPU-DeepLearning/GPU-exporter-grafana]]
- [[GPU-DeepLearning/NVIDIA-GPU-开启persistent mode]]
- [[Docker-Kubernetes/docker/docker配置NVIDIA GPU]]
- [[Docker-Kubernetes/k8s-ai-gpu/k8s配置NVIDIA GPU]]
