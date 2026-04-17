---
title: ArgoCD
tags:
  - knowledgebase/entity
date: 2026-04-16
---

# ArgoCD

## 定义
ArgoCD 是基于 GitOps 理念的 Kubernetes 持续交付（CD）工具，通过监听 Git 仓库变更自动同步应用到集群。本仓库记录了 ArgoCD 基础使用、Image Updater 自动更新镜像、Helm 应用部署及问题排查。

## 在本仓库中的位置
主要集中在 `Docker-Kubernetes/k8s-CICD/ArgoCD/` 目录，共 4 篇文章。

## 相关文章
- [[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD基础|ArgoCD基础]]
- [[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD Image Updater|ArgoCD Image Updater]]
- [[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD部署Helm应用时域名解析失败问题排查与解决|ArgoCD部署Helm应用时域名解析失败问题排查与解决]]
- [[Docker-Kubernetes/k8s-CICD/ArgoCD/学习链接|学习链接]]

## 关联概念
- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]
- [[KnowledgeBase/entities/Helm|Helm]]
- [[KnowledgeBase/entities/Jenkins|Jenkins]]
- [[KnowledgeBase/entities/Docker|Docker]]

## 可延展方向
- ArgoCD ApplicationSet 多环境管理
- ArgoCD 与 Kustomize 的结合使用
- ArgoCD RBAC 与多租户配置
