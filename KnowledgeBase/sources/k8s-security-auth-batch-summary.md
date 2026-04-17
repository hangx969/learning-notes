---
title: k8s-security-auth 来源批量摘要
tags:
  - knowledgebase/source
  - docker-kubernetes/security
date: 2026-04-17
sources:
  - "[[Docker-Kubernetes/k8s-security-auth/helm部署capsule]]"
  - "[[Docker-Kubernetes/k8s-security-auth/helm部署certmanager]]"
  - "[[Docker-Kubernetes/k8s-security-auth/helm部署external-secrets]]"
  - "[[Docker-Kubernetes/k8s-security-auth/helm部署kyverno和policy-reporter]]"
  - "[[Docker-Kubernetes/k8s-security-auth/helm部署oauth2proxy]]"
  - "[[Docker-Kubernetes/k8s-security-auth/helm部署sonarqube]]"
  - "[[Docker-Kubernetes/k8s-security-auth/helm部署trivy-operator]]"
---

## 元信息

- **原始目录**: `Docker-Kubernetes/k8s-security-auth/`
- **文档数量**: 7 篇
- **领域**: Kubernetes 安全、认证授权、证书管理、策略引擎、代码质量与镜像扫描
- **摄入日期**: 2026-04-17

## 整体概述

本目录涵盖 Kubernetes 集群安全与认证授权领域的核心工具，包括多租户管理（Capsule）、证书自动化管理（Cert-Manager）、外部密钥同步（External Secrets）、策略引擎（Kyverno）、身份认证代理（OAuth2 Proxy）、代码质量扫描（SonarQube）以及容器镜像漏洞扫描（Trivy Operator）。所有工具均通过 Helm Chart 方式部署，文档覆盖了从下载配置到企业级使用的完整流程。

## 各文档摘要

### [[Docker-Kubernetes/k8s-security-auth/helm部署capsule|Helm 部署 Capsule]]

**核心内容**: Capsule 是 K8s 多租户管理工具，通过 Tenant CRD 将一组 Namespace 逻辑分组，并对其实施 RBAC、Resource Quota、Network Policy 等策略。

- Tenant：一组 Namespace 的逻辑分组，支持权限分配与隔离
- capsuleUserGroups 配置可操作 Capsule 的用户组
- Tenant Owner 需属于 Capsule User Group（通过证书 O 字段、外部 IdP 组或 ServiceAccount 配置）
- 用户认证通过 OpenSSL 证书（CN/O 字段）+ kubeconfig 实现

### [[Docker-Kubernetes/k8s-security-auth/helm部署certmanager|Helm 部署 Cert-Manager]]

**核心内容**: Cert-Manager 是 K8s 全能证书管理工具，支持基于 ACME 协议与 Let's Encrypt 签发免费证书并自动续期。

- 证书分类：Root CA、中间 CA、终端实体证书
- 核心资源：ClusterIssuer/Issuer（证书颁发者）、Certificate（证书对象，生成 K8s Secret）
- 支持 Self-signed、ACME（Let's Encrypt）等多种 Issuer 类型
- CRDs 需设置 `crds.enabled=true` 和 `crds.keep=true`

### [[Docker-Kubernetes/k8s-security-auth/helm部署external-secrets|Helm 部署 External Secrets]]

**核心内容**: External Secrets Operator 从外部密钥提供商（如 Azure Key Vault）读取 Secrets 并同步写入 K8s Secrets。

- 核心资源：ClusterSecretStore/SecretStore（指定外部密钥源和认证方式）、ExternalSecret（定义同步映射）
- 集成 Azure Key Vault：支持 Managed Identity 和 Workload Identity 认证
- refreshInterval 控制拉取频率（如 1h）
- 支持 ChinaCloud 环境配置

### [[Docker-Kubernetes/k8s-security-auth/helm部署kyverno和policy-reporter|Helm 部署 Kyverno 和 Policy Reporter]]

**核心内容**: Kyverno 是 K8s 原生策略引擎，作为 Admission Controller 运行，用于验证和变更集群资源。Policy Reporter 提供策略执行结果的可视化界面。

- Kyverno 作为 Admission Controller 拦截 API 请求
- 支持验证（validate）、变更（mutate）、生成（generate）策略
- Policy 可按 common 和 region 分目录管理，递归应用
- Policy Reporter 提供策略执行结果的 GUI 界面

### [[Docker-Kubernetes/k8s-security-auth/helm部署oauth2proxy|Helm 部署 OAuth2 Proxy]]

**核心内容**: OAuth2 Proxy 是 K8s 应用的身份认证反向代理，支持 Middleware 模式作用于 Ingress-Nginx，集成 GitHub 等 OAuth 提供商。

- 两种工作模式：独立反向代理 / Ingress-Nginx Middleware
- sessionStorage 使用 Redis 存储用户会话状态
- 集成 GitHub OAuth App：配置 Client ID/Secret、Cookie Secret
- 架构：Nginx 路由 -> OAuth2 Proxy 认证 -> Redis 会话存储

### [[Docker-Kubernetes/k8s-security-auth/helm部署sonarqube|Helm 部署 SonarQube]]

**核心内容**: SonarQube 是开源代码质量管理系统，支持多语言（Java、C#、JavaScript、Python 等）的自动化代码质量检测。

- 检测能力：错误、漏洞、代码异味（Code Smell）
- 可集成到 CI/CD 流程中实现持续代码质量改进
- 通过 Cert-Manager 创建 HTTPS 证书
- 配置 Ingress（nginx-default）暴露服务

### [[Docker-Kubernetes/k8s-security-auth/helm部署trivy-operator|Helm 部署 Trivy Operator]]

**核心内容**: Trivy Operator 是容器镜像漏洞扫描器，以 Client-Server 模式在集群中运行，自动扫描工作负载的镜像安全漏洞。

- Client-Server 模式：trivy-operator（扫描执行）+ trivy-server（漏洞数据库）
- 报告类型：VulnerabilityReport（镜像漏洞）、ConfigAuditReport（配置安全）
- Vulnerability DB 是 OCI Image，需使用 oras 工具下载（非 docker pull）
- 支持离线环境的漏洞数据库部署

## 涉及的概念与实体

- [[KnowledgeBase/concepts/多租户]]: Capsule Tenant 实现 Namespace 级别的多租户隔离
- [[KnowledgeBase/concepts/证书管理]]: Cert-Manager 自动化 TLS 证书签发与续期
- [[KnowledgeBase/concepts/Secrets管理]]: External Secrets 外部密钥同步到 K8s
- [[KnowledgeBase/concepts/策略即代码]]: Kyverno 以 CRD 方式定义集群策略
- [[KnowledgeBase/concepts/身份认证]]: OAuth2 Proxy 统一身份认证代理
- [[KnowledgeBase/concepts/镜像安全]]: Trivy 容器镜像漏洞扫描
- [[KnowledgeBase/entities/Capsule]]: K8s 多租户管理工具
- [[KnowledgeBase/entities/Cert-Manager]]: 证书管理工具
- [[KnowledgeBase/entities/External-Secrets]]: 外部密钥同步工具
- [[KnowledgeBase/entities/Kyverno]]: K8s 策略引擎
- [[KnowledgeBase/entities/OAuth2-Proxy]]: 身份认证反向代理
- [[KnowledgeBase/entities/SonarQube]]: 代码质量管理平台
- [[KnowledgeBase/entities/Trivy]]: 镜像漏洞扫描器
- [[KnowledgeBase/entities/Azure-Key-Vault]]: 外部密钥提供商

## 交叉主题发现

1. **安全工具链协同**: Kyverno（准入控制）+ Trivy（镜像扫描）+ SonarQube（代码扫描）构成了从代码到运行时的完整安全防线。
2. **证书与 Ingress 联动**: Cert-Manager 为 SonarQube、Goldilocks 等工具生成 TLS 证书，与 `k8s-networking-service-mesh` 目录的 Ingress-Nginx 紧密配合。
3. **认证与 Ingress 集成**: OAuth2 Proxy 通过 Ingress-Nginx 的 auth-url/auth-signin annotation 实现统一认证，`k8s-scaling` 目录的 Goldilocks 也使用了同样的认证集成模式。
4. **密钥管理闭环**: External Secrets 从 Azure Key Vault 同步密钥到 K8s，CI/CD 工具（Jenkins Credentials）和应用（Helm values）均可引用这些 K8s Secrets。
5. **多租户与 RBAC**: Capsule 的多租户隔离与 K8s 原生 RBAC 配合，为企业级集群的团队协作提供了安全边界。
