---
title: Jenkins
tags:
  - knowledgebase/entity
date: 2026-04-17
sources:
  - "[[KnowledgeBase/sources/k8s-CICD-batch-summary|k8s-CICD 来源批量摘要]]"
---

# Jenkins

## 定义
Jenkins 是老牌开源 CI/CD 服务器，支持 Pipeline as Code、丰富的插件生态与分布式构建。本仓库以 7 篇文章记录了 Jenkins 从二进制安装到 Kubernetes DevOps 平台落地的完整实践。

## 编译知识

### 部署方式
本仓库覆盖了 Jenkins 的四种部署方式，反映了不同环境的适配需求：
- **二进制安装**（RPM 包，JDK11 运行环境，通过 P12 证书连接 K8s 集群）
- **Docker 部署**（bitnami 镜像，挂载 Docker Socket 支持 Docker Slave）
- **Helm 部署**（Chart v5.8.68，配置 Ingress、Prometheus 监控和动态 Agent）
- **YAML 部署**（原生清单，NFS 持久化，适用于 Jenkins 2.394 和 2.426.3）

### Pipeline 语法
- 声明式语法核心元素：**pipeline、agent、stages、steps、post、environment**
- Pipeline 优势：标准化、自动化、可视化、可追溯、支持并行
- Credentials 统一管理 Harbor 账号、GitLab 私钥、K8s 证书

### 企业级 DevOps 平台落地
- 通用发版流程：GitLab 代码提交 -> Jenkins 构建 -> Docker 镜像 -> [[KnowledgeBase/entities/Harbor|Harbor]] 推送 -> K8s 部署
- Harbor 必须用 NodePort 暴露（因 JNLP Pod 内 CoreDNS 无法解析 Ingress 域名）
- K8s 中 Agent 以 JNLP 方式连接 Controller，启用特权模式

### 与 GitOps 的关系
- Jenkins 代表 **Push 模式** CI/CD，与 [[KnowledgeBase/entities/ArgoCD|ArgoCD]] 的 **Pull 模式** GitOps 可集成使用
- Jenkins 负责 CI（构建+测试），ArgoCD 负责 CD（部署同步），两者互补

## 在本仓库中的位置
主要集中在 `Docker-Kubernetes/k8s-CICD/Jenkins/` 目录。

## 相关文章
- [[Docker-Kubernetes/k8s-CICD/Jenkins/Jenkins语法-基于docker部署|Jenkins语法-基于docker部署]]
- [[Docker-Kubernetes/k8s-CICD/Jenkins/docker部署jenkins|docker部署jenkins]]
- [[Docker-Kubernetes/k8s-CICD/Jenkins/helm部署jenkins|helm部署jenkins]]
- [[Docker-Kubernetes/k8s-CICD/Jenkins/k8s-Devops平台落地-基于jenkins|k8s-Devops平台落地-基于jenkins]]
- [[Docker-Kubernetes/k8s-CICD/Jenkins/k8s部署基于Jenkins(2.394)的DevOps工具链-基于yaml|k8s部署基于Jenkins(2.394)的DevOps工具链-基于yaml]]
- [[Docker-Kubernetes/k8s-CICD/Jenkins/k8s部署基于Jenkins(2.426.3)的Devops工具链-基于yaml|k8s部署基于Jenkins(2.426.3)的Devops工具链-基于yaml]]
- [[Docker-Kubernetes/k8s-CICD/Jenkins/二进制安装Jenkins(2.319)|二进制安装Jenkins(2.319)]]

## 关联概念
- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]
- [[KnowledgeBase/entities/ArgoCD|ArgoCD]]
- [[KnowledgeBase/entities/Docker|Docker]]
- [[KnowledgeBase/entities/Helm|Helm]]

## 可延展方向
- Jenkins 向 GitOps（ArgoCD）迁移策略
- Jenkins Shared Library 最佳实践
- Jenkins 与云原生 CI 工具（Tekton）的对比
