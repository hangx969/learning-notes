---
title: CICD
tags:
  - knowledgebase/concept
date: 2026-04-16
---

# CICD

## 定义
持续集成（Continuous Integration）与持续交付/部署（Continuous Delivery/Deployment）是 DevOps 实践的核心，通过自动化构建、测试和部署流程，实现代码从提交到上线的快速、可靠交付。本仓库涵盖 Jenkins、ArgoCD、GitLab CI、Tekton、Kustomize、GitHub Actions 等主流 CI/CD 工具链。

## 在本仓库中的位置
主要集中在 `Docker-Kubernetes/k8s-CICD/` 目录下，按工具分为 Jenkins、ArgoCD、Gitlab、Tekton、Kustomize 等子目录，共 19 篇文章。

## 相关文章
- [k8s-Devops平台落地-基于jenkins](../../Docker-Kubernetes/k8s-CICD/Jenkins/k8s-Devops平台落地-基于jenkins.md)
- [k8s部署基于Jenkins(2.426.3)的Devops工具链-基于yaml](../../Docker-Kubernetes/k8s-CICD/Jenkins/k8s部署基于Jenkins(2.426.3.md)的Devops工具链-基于yaml)
- [k8s部署基于Jenkins(2.394)的DevOps工具链-基于yaml](../../Docker-Kubernetes/k8s-CICD/Jenkins/k8s部署基于Jenkins(2.394.md)的DevOps工具链-基于yaml)
- [helm部署jenkins](../../Docker-Kubernetes/k8s-CICD/Jenkins/helm部署jenkins.md)
- [docker部署jenkins](../../Docker-Kubernetes/k8s-CICD/Jenkins/docker部署jenkins.md)
- [二进制安装Jenkins(2.319)](../../Docker-Kubernetes/k8s-CICD/Jenkins/二进制安装Jenkins(2.319.md))
- [Jenkins语法-基于docker部署](../../Docker-Kubernetes/k8s-CICD/Jenkins/Jenkins语法-基于docker部署.md)
- [ArgoCD基础](../../Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD基础.md)
- [ArgoCD Image Updater](../../Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD%20Image%20Updater.md)
- [ArgoCD部署Helm应用时域名解析失败问题排查与解决](../../Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD部署Helm应用时域名解析失败问题排查与解决.md)
- [helm部署gitlab](../../Docker-Kubernetes/k8s-CICD/Gitlab/helm部署gitlab.md)
- [k8s部署Gitlab(11.8.1)-基于yaml](../../Docker-Kubernetes/k8s-CICD/Gitlab/k8s部署Gitlab(11.8.1.md)-基于yaml)
- [二进制安装Gitlab(17.9.8)](../../Docker-Kubernetes/k8s-CICD/Gitlab/二进制安装Gitlab(17.9.8.md))
- [k8s部署原生的CICD工具Tekton-基于yaml](../../Docker-Kubernetes/k8s-CICD/Tekton/k8s部署原生的CICD工具Tekton-基于yaml.md)
- [基于Tekton的云原生平台落地](../../Docker-Kubernetes/k8s-CICD/Tekton/基于Tekton的云原生平台落地.md)
- [k8s配置定制工具-kustomize](../../Docker-Kubernetes/k8s-CICD/Kustomize/k8s配置定制工具-kustomize.md)
- [使用github action部署helmchart](../../Docker-Kubernetes/k8s-CICD/使用github%20action部署helmchart.md)
- [发布go-python-java代码到K8S环境](../../Docker-Kubernetes/k8s-CICD/发布go-python-java代码到K8S环境.md)

## 关联概念
- [Azure](Azure.md)
- [AKS](AKS.md)
- [Observability](Observability.md)
- [服务网格](服务网格.md)
- [容器运行时](容器运行时.md)

## 可延展方向
- GitOps 工作流最佳实践（ArgoCD + Kustomize / Helm）
- CI/CD 安全（镜像签名、SBOM、Supply Chain Security）
- 多集群 CD 部署策略（蓝绿、金丝雀、渐进式发布）
- Pipeline as Code 规范与模板化
- Azure DevOps Pipeline 与 GitHub Actions 对比
