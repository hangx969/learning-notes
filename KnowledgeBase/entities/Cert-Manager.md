---
title: Cert-Manager
tags:
  - knowledgebase/entity
  - kubernetes/security
  - kubernetes/tls
date: 2026-09-15
sources:
  - "[[cert-manager 实战：Helm 部署、TLS 自动签发与续期]]"
  - "[[AI/企业级私有化大模型/一个 Deployment 就能跑 vLLM，为什么还需要 KServe？]]"
aliases:
  - cert-manager
---

# Cert-Manager

## 简介

Cert-Manager 是 Kubernetes 原生的证书生命周期控制器，通过 CRD 将证书签发、域名校验、Secret 写入、续期和状态跟踪声明化。它支持 ACME/Let's Encrypt、自签名、内部 CA、Vault、Venafi 等 Issuer。

## 核心功能

- 通过 Issuer 或 ClusterIssuer 定义证书颁发者与验证方式。
- 根据 Certificate 创建 CertificateRequest，并在 ACME 场景维护 Order 和 Challenge。
- 将成功签发的证书与私钥写入 `kubernetes.io/tls` Secret。
- 通过 ingress-shim 从 Ingress Annotation 自动生成 Certificate。
- 在续期窗口内更新原 Secret，并暴露资源状态用于排障与监控。
- 通过 webhook 校验/转换自定义资源，借助 cainjector 注入 CA Bundle。

## 使用场景

- 为 Kubernetes Ingress 自动签发和续期公网 TLS 证书。
- 通过 DNS01 申请通配符证书或服务于私网入口。
- 为集群内 Service/Pod 签发自签名或内部 CA 证书。
- 在 AKS 中结合 Azure DNS 与 Workload Identity 完成 DNS01。
- 作为 KServe 等 Kubernetes 平台组件的安装依赖。

## 相关概念与实体

- [[KnowledgeBase/concepts/证书管理]]：Cert-Manager 实现的核心生命周期能力。
- [[KnowledgeBase/entities/Kubernetes]]：Cert-Manager 以控制器、Webhook 和 CRD 运行。
- [[KnowledgeBase/entities/Ingress]]：引用 TLS Secret，或通过 Annotation 触发签发。
- [[KnowledgeBase/entities/Helm]]：常用安装与配置管理方式。

## 在本仓库中的覆盖

- [[cert-manager 实战：Helm 部署、TLS 自动签发与续期]]：Helm 安装、自签名、HTTP01/DNS01、Cloudflare、Azure DNS、续期与生产排障。
- [[AI/企业级私有化大模型/一个 Deployment 就能跑 vLLM，为什么还需要 KServe？]]：作为 KServe 安装链路中的依赖组件。
- [[Docker-Kubernetes/k8s-security-auth/helm部署sonarqube]]：为 Ingress 创建 HTTPS 证书。

## 知识空白

- trust-manager、CSI Driver 与 SPIFFE/SPIRE 的证书分发边界。
- Gateway API 与 cert-manager 的集成方式。
- 大规模集群的证书指标、SLO 和容量规划。
