---
title: k8s-CICD 来源批量摘要
tags:
  - knowledgebase/source
  - docker-kubernetes/cicd
date: 2026-04-17
sources:
  - "[[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD Image Updater]]"
  - "[[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD基础]]"
  - "[[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD部署Helm应用时域名解析失败问题排查与解决]]"
  - "[[Docker-Kubernetes/k8s-CICD/ArgoCD/学习链接]]"
  - "[[Docker-Kubernetes/k8s-CICD/Gitlab/helm部署gitlab]]"
  - "[[Docker-Kubernetes/k8s-CICD/Gitlab/二进制安装Gitlab(17.9.8)]]"
  - "[[Docker-Kubernetes/k8s-CICD/Gitlab/k8s部署Gitlab(11.8.1)-基于yaml]]"
  - "[[Docker-Kubernetes/k8s-CICD/Jenkins/Jenkins语法-基于docker部署]]"
  - "[[Docker-Kubernetes/k8s-CICD/Jenkins/helm部署jenkins]]"
  - "[[Docker-Kubernetes/k8s-CICD/Jenkins/k8s-Devops平台落地-基于jenkins]]"
  - "[[Docker-Kubernetes/k8s-CICD/Jenkins/k8s部署基于Jenkins(2.394)的DevOps工具链-基于yaml]]"
  - "[[Docker-Kubernetes/k8s-CICD/Jenkins/k8s部署基于Jenkins(2.426.3)的Devops工具链-基于yaml]]"
  - "[[Docker-Kubernetes/k8s-CICD/Jenkins/docker部署jenkins]]"
  - "[[Docker-Kubernetes/k8s-CICD/Jenkins/二进制安装Jenkins(2.319)]]"
  - "[[Docker-Kubernetes/k8s-CICD/Tekton/k8s部署原生的CICD工具Tekton-基于yaml]]"
  - "[[Docker-Kubernetes/k8s-CICD/Tekton/基于Tekton的云原生平台落地]]"
  - "[[Docker-Kubernetes/k8s-CICD/Kustomize/k8s配置定制工具-kustomize]]"
  - "[[Docker-Kubernetes/k8s-CICD/使用github action部署helmchart]]"
  - "[[Docker-Kubernetes/k8s-CICD/发布go-python-java代码到K8S环境]]"
---

## 元信息

- **原始目录**: `Docker-Kubernetes/k8s-CICD/`（含子目录 ArgoCD、Gitlab、Jenkins、Kustomize、Tekton）
- **文档数量**: 19 篇
- **领域**: Kubernetes CI/CD 持续集成与持续部署
- **摄入日期**: 2026-04-17

## 整体概述

本目录系统性地覆盖了 Kubernetes 环境下主流 CI/CD 工具链的部署与使用，包括 ArgoCD（GitOps 持续交付）、Jenkins（传统 CI/CD 引擎）、Tekton（云原生 Pipeline）、GitLab（代码仓库）以及 Kustomize（配置定制）等。文档内容涵盖从工具的基础概念、多种部署方式（Helm、YAML、Docker、二进制）到企业级 DevOps 平台落地的完整实践，同时包含了 GitHub Actions 集成和多语言应用（Go/Python/Java）发布到 K8s 的实战案例。

## 各文档摘要

### [[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD Image Updater|ArgoCD Image Updater]]

**核心内容**: ArgoCD Image Updater 是自动更新 ArgoCD 管理的容器镜像版本的工具，通过 Annotation 配置跟踪镜像仓库变更并自动同步。

- 支持 semver、latest、name、digest 四种更新策略
- 通过 docker-registry secret、generic secret 或环境变量配置镜像仓库凭据
- 仅支持 Helm 或 Kustomize 渲染的应用，且镜像拉取密钥需在同集群

### [[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD基础|ArgoCD基础]]

**核心内容**: ArgoCD 是 CNCF 旗下的声明式 GitOps 持续交付工具，以 Git 仓库作为唯一事实来源，自动同步集群状态与期望状态。

- 核心组件：API Server、Repository Server、Application Controller
- CRD 资源：AppProject（逻辑分组与权限隔离）、Application（应用定义）
- 支持多集群管理、Helm/Kustomize/Jsonnet 配置来源、同步波次与钩子、RBAC 和 SSO 集成

### [[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD部署Helm应用时域名解析失败问题排查与解决|ArgoCD DNS 解析问题排查]]

**核心内容**: 排查 ArgoCD 部署 Helm 应用时的两阶段 DNS 故障：CoreDNS 上游转发失败和 Go 纯 DNS 解析器的 IPv6 缺陷。

- 阶段一根因：CoreDNS forward 插件读取宿主机 `/etc/resolv.conf` 上游 DNS 不可达
- 阶段二根因：Helm 二进制无 CGO，Go 纯 DNS 解析器优先尝试 IPv6 导致连接失败
- 涉及 CoreDNS、Calico CNI、kubeadm 集群环境的排查方法

### [[Docker-Kubernetes/k8s-CICD/ArgoCD/学习链接|ArgoCD 学习链接]]

**核心内容**: ArgoCD 学习资源汇总，包含基础、进阶、实践教程以及 Image Updater 和 Jenkins 集成的参考链接。

- 微信公众号系列教程链接
- 付费课程合集链接

### [[Docker-Kubernetes/k8s-CICD/Gitlab/helm部署gitlab|Helm 部署 GitLab]]

**核心内容**: 使用 Helm Chart（v9.3.2）在 K8s 集群中部署 GitLab CE 版，包含域名、Ingress、初始密码等详细配置。

- 全局配置：主机域名、Ingress Class（nginx-default）、TLS 开关
- 子组件域名：gitlab、minio、registry、kas 各自独立域名
- 初始管理员密码通过 Kubernetes Secret 管理

### [[Docker-Kubernetes/k8s-CICD/Gitlab/二进制安装Gitlab(17.9.8)|二进制安装 GitLab]]

**核心内容**: 在独立服务器（4C/4G/40G+）上通过 RPM 包二进制安装 GitLab CE 17.9.8，适用于 DevOps 平台的代码仓库组件。

- 使用清华大学镜像源下载 RPM 包
- 关闭自带 Prometheus 和各种 exporter 以节省资源
- 注意不能与 K8s 节点共用（80/443 端口冲突）

### [[Docker-Kubernetes/k8s-CICD/Gitlab/k8s部署Gitlab(11.8.1)-基于yaml|K8s 部署 GitLab（YAML 方式）]]

**核心内容**: 通过原生 YAML 清单在 K8s 中部署 GitLab 11.8.1，使用 NFS 作为持久化存储。

- 搭建 NFS 供应商提供 PV/PVC
- 分别为 GitLab 和 PostgreSQL 创建持久化存储
- 使用 kube-ops 命名空间部署

### [[Docker-Kubernetes/k8s-CICD/Jenkins/Jenkins语法-基于docker部署|Jenkins Pipeline 语法]]

**核心内容**: 系统性介绍 DevOps 概念、CICD 流程以及 Jenkins Pipeline 的声明式语法（pipeline、agent、stages、steps、post 等）。

- DevOps 工具链全景：代码管理、代码扫描、持续集成、持续部署、容器化、制品管理、服务编排
- Pipeline 优势：标准化、自动化、可视化、可追溯、支持并行
- 声明式语法核心元素：environment、credentials 引用

### [[Docker-Kubernetes/k8s-CICD/Jenkins/helm部署jenkins|Helm 部署 Jenkins]]

**核心内容**: 使用 Helm Chart（v5.8.68）在 K8s 中部署 Jenkins，配置 Ingress、Prometheus 监控和动态 Agent。

- Controller 以 root 用户运行，配置 Ingress（nginx-default）
- Agent 启用特权模式，使用 JNLP 方式连接
- 挂载宿主机 localtime 同步时区

### [[Docker-Kubernetes/k8s-CICD/Jenkins/k8s-Devops平台落地-基于jenkins|Jenkins DevOps 平台落地]]

**核心内容**: 基于 Jenkins 的企业级 DevOps 平台落地方案，包含 GitLab + Jenkins + Harbor + K8s 的完整工具集成。

- 通用发版流程：GitLab 代码提交 -> Jenkins 构建 -> Docker 镜像 -> Harbor 推送 -> K8s 部署
- Harbor 必须用 NodePort 暴露（因 JNLP pod 内 CoreDNS 无法解析 Ingress 域名）
- Jenkins Credentials 统一管理 Harbor 账号、GitLab 私钥、K8s 证书

### [[Docker-Kubernetes/k8s-CICD/Jenkins/k8s部署基于Jenkins(2.394)的DevOps工具链-基于yaml|Jenkins 2.394 DevOps 工具链]]

**核心内容**: 详细介绍 CI/CD/持续交付概念，以及 Jenkins Pipeline 声明式与脚本式语法，包括 environment、credentials 等高级用法。

- 持续集成 -> 持续交付 -> 持续部署的完整流程
- Pipeline 两种语法对比：Declarative vs Scripted
- agent、stages、steps、post 等核心语法元素

### [[Docker-Kubernetes/k8s-CICD/Jenkins/k8s部署基于Jenkins(2.426.3)的Devops工具链-基于yaml|Jenkins 2.426.3 DevOps 工具链]]

**核心内容**: 通过原生 YAML 在 K8s 中部署 Jenkins 2.426.3，包含 NFS 持久化存储和前置资源（PV/PVC/ServiceAccount）的创建。

- 部署 NFS 服务和共享目录
- 创建 jenkins-k8s 命名空间、PV、PVC
- Service Account 权限配置

### [[Docker-Kubernetes/k8s-CICD/Jenkins/docker部署jenkins|Docker 部署 Jenkins]]

**核心内容**: 使用 Docker 方式部署 Jenkins 主节点（bitnami 镜像 2.504.3），适用于无分布式存储的环境。

- 暴露 8080（Web UI）和 50000（JNLP）端口
- 挂载宿主机 Docker Socket 以支持 Docker Slave
- 持久化数据到 `/data/jenkins_data`

### [[Docker-Kubernetes/k8s-CICD/Jenkins/二进制安装Jenkins(2.319)|二进制安装 Jenkins]]

**核心内容**: 通过 RPM 包在服务器上二进制安装 Jenkins 2.319，配置 K8s 集群连接（通过 kubeconfig 证书认证）。

- 安装 JDK11 作为运行环境
- 离线插件安装方法（清华镜像源）
- 通过 Client P12 证书文件连接 K8s 集群

### [[Docker-Kubernetes/k8s-CICD/Tekton/k8s部署原生的CICD工具Tekton-基于yaml|Tekton YAML 部署]]

**核心内容**: 介绍 Tekton 作为 Kubernetes 原生 CI/CD 框架的核心概念（Task、TaskRun、Pipeline、PipelineRun、PipelineResource），并通过 YAML 方式部署。

- 源自 Knative build-pipeline 子项目，Pipeline 直接映射为 K8s Pod
- 所有构建任务以容器方式运行
- 安装文件中镜像需处理 SHA256 后缀问题

### [[Docker-Kubernetes/k8s-CICD/Tekton/基于Tekton的云原生平台落地|Tekton 云原生平台落地]]

**核心内容**: 基于 Tekton 构建云原生 CI/CD 平台的完整方案，包含核心资源（StepAction、Task、Pipeline、Triggers）和最佳实践。

- 核心优势：云原生、标准化（CRD）、可移植、事件驱动
- 部署三个组件：Pipeline、Triggers、Dashboard
- 最佳实践：Task 作为最小单元，一个 Task 一个 Step，workspace 统一命名

### [[Docker-Kubernetes/k8s-CICD/Kustomize/k8s配置定制工具-kustomize|Kustomize 使用指南]]

**核心内容**: Kustomize 是 K8s 原生的无模板配置定制工具，通过 Base + Overlay 分层管理实现不同环境的声明式配置定制。

- 自 K8s 1.14 起集成在 kubectl 中（`kubectl apply -k`）
- 与 Helm 模板引擎不同，直接操作原生资源文件
- 支持分层管理（Base/Overlay）和环境感知（dev/prod/qa）

### [[Docker-Kubernetes/k8s-CICD/使用github action部署helmchart|GitHub Actions 部署 Helm Chart]]

**核心内容**: 配置 GitHub Self-hosted Runner（Linux/Windows）在本地 K8s 环境中执行 GitHub Actions 工作流部署 Helm Chart。

- Self-hosted Runner 适用于无公网 IP 的本地 K8s 环境
- Runner 配置为系统服务（svc.sh）
- 支持 Linux 和 Windows 两种平台的 Runner 配置

### [[Docker-Kubernetes/k8s-CICD/发布go-python-java代码到K8S环境|K8s 应用部署示例]]

**核心内容**: 演示 Go/Python/Java 三种语言的应用从源码编译、Dockerfile 构建镜像到部署至 K8s 环境的完整流程。

- Go 应用：使用 Gin 框架，CGO_ENABLED=0 交叉编译，Alpine 基础镜像
- 包含 Dockerfile 编写、镜像构建、K8s Deployment 创建的完整步骤
- 适用于多语言微服务的标准化发布流程

## 涉及的概念与实体

- [[KnowledgeBase/concepts/GitOps]]: ArgoCD 核心理念，Git 作为唯一事实来源
- [[KnowledgeBase/concepts/CICD]]: 持续集成、持续交付、持续部署的完整流程
- [[KnowledgeBase/concepts/Pipeline]]: Jenkins/Tekton 流水线编排框架
- [[KnowledgeBase/concepts/ServiceMesh]]: 与 CI/CD 工具链的协同
- [[KnowledgeBase/entities/ArgoCD]]: GitOps 持续交付工具
- [[KnowledgeBase/entities/Jenkins]]: 传统 CI/CD 引擎
- [[KnowledgeBase/entities/Tekton]]: 云原生 CI/CD 框架
- [[KnowledgeBase/entities/GitLab]]: 代码仓库与 CI 工具
- [[KnowledgeBase/entities/Kustomize]]: K8s 配置定制工具
- [[KnowledgeBase/entities/Helm]]: K8s 包管理器
- [[KnowledgeBase/entities/Harbor]]: 容器镜像仓库
- [[KnowledgeBase/entities/GitHub-Actions]]: GitHub CI/CD 工作流
- [[KnowledgeBase/entities/CoreDNS]]: K8s 集群 DNS 服务
- [[KnowledgeBase/entities/NFS]]: 网络文件系统存储

## 交叉主题发现

1. **GitOps vs 传统 CI/CD**: ArgoCD（Pull 模式）与 Jenkins（Push 模式）代表了两种不同的部署哲学，多篇文档展示了两者的集成方案（ArgoCD+Jenkins）。
2. **部署方式多样性**: 同一工具（Jenkins、GitLab）均提供了 Helm、YAML、Docker、二进制等多种部署方式，反映了不同环境（云/本地/生产/测试）的适配需求。
3. **存储依赖**: CI/CD 工具链普遍依赖持久化存储（NFS PV/PVC），与 `k8s-storage` 目录的内容紧密关联。
4. **DNS 与网络问题**: ArgoCD DNS 排查文档揭示了 CoreDNS、IPv6、CGO 等底层网络问题对 CI/CD 流程的影响，与 `k8s-networking-service-mesh` 目录关联。
5. **安全凭据管理**: Harbor 账号、GitLab 私钥、K8s 证书的管理贯穿所有 CI/CD 工具，与 `k8s-security-auth` 目录的 External Secrets、Cert-Manager 等工具关联。
6. **云原生演进**: 从 Jenkins（VM 时代）到 Tekton（K8s 原生）再到 ArgoCD（GitOps），体现了 CI/CD 工具向云原生演进的趋势。
