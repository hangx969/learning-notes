---
title: GitLab
tags:
  - knowledgebase/entity
  - devops
date: 2026-04-17
sources:
  - "[[Docker-Kubernetes/k8s-CICD/Gitlab/二进制安装Gitlab(17.9.8)]]"
  - "[[Docker-Kubernetes/k8s-CICD/Gitlab/k8s部署Gitlab(11.8.1)-基于yaml]]"
  - "[[Docker-Kubernetes/k8s-CICD/Gitlab/helm部署gitlab]]"
  - "[[Docker-Kubernetes/docker/docker部署gitlab]]"
  - "[[Docker-Kubernetes/k8s-CICD/Jenkins/k8s-Devops平台落地-基于jenkins]]"
  - "[[Docker-Kubernetes/k8s-CICD/Jenkins/k8s部署基于Jenkins(2.394)的DevOps工具链-基于yaml]]"
  - "[[Docker-Kubernetes/k8s-CICD/Claude-Code实现CICD自动化发布流程]]"
  - "[[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD基础]]"
---

## 简介

GitLab 是 DevOps 全生命周期平台，提供代码仓库、CI/CD 流水线、Issue 管理、制品库等一站式功能。

## 核心功能

- **代码仓库管理**：以 Group、Project 组织代码，支持 SSH Key 认证拉取与推送，可从 GitHub、URL 等外部来源导入仓库
- **GitLab CI 流水线**：通过 variables、stages、rules、needs 定义作业；敏感参数用 CI/CD Variables（Masked + Protected）注入，不写入 yaml
- **MR 与 Release**：基于 Merge Request 评审代码，可通过 Releases API 自动创建 Release
- **Webhook 集成**：代码推送后通过 Webhook 触发 Jenkins 流水线或 ArgoCD 同步
- **Omnibus 配置与运维**：在 `/etc/gitlab/gitlab.rb` 中配置 external_url、关闭内置监控组件，用 `gitlab-ctl reconfigure` 生效，用 `gitlab-backup` 备份与恢复

## 使用场景

- 企业内部代码托管，作为 DevOps 平台的代码源（GitLab 提交 → Jenkins 构建 → Harbor 推送 → K8s 部署）
- 基于 GitLab CI 的构建发布流水线（Kaniko 构建镜像、kubectl 部署），并结合 AI 完成 MR 评审与 Release Notes
- 作为 GitOps 的 Git 仓库，通过 Webhook 触发 ArgoCD 同步
- 在实验环境中以 RPM、Docker Compose、K8s YAML 或 Helm Chart 方式部署

## 相关概念与实体

- [[KnowledgeBase/entities/Jenkins|Jenkins]]：GitLab 作为代码源，通过 SSH Key 互信与 Webhook 触发 Jenkins 流水线
- [[KnowledgeBase/entities/ArgoCD|ArgoCD]]：ArgoCD 可接收 GitLab Webhook 触发同步
- [[KnowledgeBase/concepts/CICD|CICD]]：GitLab CI 提供从构建到部署、发布的流水线能力
- [[KnowledgeBase/entities/Harbor|Harbor]]：GitLab CI 中用 Kaniko 构建的镜像推送到 Harbor
- [[KnowledgeBase/entities/NFS|NFS]]：以 YAML 部署到 K8s 时用 NFS PV 持久化 GitLab 数据
- [[KnowledgeBase/entities/Claude-Code|Claude-Code]]：结合 Claude 在 GitLab CI 中实现 MR 评审、Release Notes 与部署失败根因分析

## 在本仓库中的覆盖

- `Docker-Kubernetes/k8s-CICD/Gitlab/` 目录下有 3 篇专题笔记
- `Docker-Kubernetes/docker/` 目录中包含 GitLab 容器化部署相关内容
- [[Docker-Kubernetes/k8s-CICD/Gitlab/二进制安装Gitlab(17.9.8)|二进制安装Gitlab(17.9.8)]]：RPM 安装 GitLab CE、配置 gitlab.rb（关闭内置 Prometheus 与 exporter）、开启导入功能，以及与 Jenkins 服务器建立 SSH Key 访问
- [[Docker-Kubernetes/k8s-CICD/Gitlab/k8s部署Gitlab(11.8.1)-基于yaml|k8s部署Gitlab(11.8.1)-基于yaml]]：基于 NFS PV，用 YAML 在 K8s 中部署 PostgreSQL、Redis 与 GitLab，并通过 NodePort 暴露
- [[Docker-Kubernetes/k8s-CICD/Gitlab/helm部署gitlab|helm部署gitlab]]：GitLab Helm Chart 的域名、Ingress 与初始 root 密码配置，记录部署中遇到的问题及放弃该方式的原因
- [[Docker-Kubernetes/docker/docker部署gitlab|docker部署gitlab]]：用 docker-compose 部署 GitLab CE，关闭内置监控组件加快启动，配置 SSH Key，以及 gitlab-backup 备份与恢复
- [[Docker-Kubernetes/k8s-CICD/Jenkins/k8s-Devops平台落地-基于jenkins|k8s-Devops平台落地-基于jenkins]]：GitLab 作为 DevOps 平台代码仓库，与 Jenkins 建立 SSH 互信，流水线支持手动触发与 GitLab Webhook 触发
- [[Docker-Kubernetes/k8s-CICD/Jenkins/k8s部署基于Jenkins(2.394)的DevOps工具链-基于yaml|K8s DevOps 工具链：Jenkins 2.394]]：docker run 部署 GitLab 并配置 SSH 端口，在 Jenkins 中添加 GitLab 凭据并提交代码
- [[Docker-Kubernetes/k8s-CICD/Claude-Code实现CICD自动化发布流程|Claude Code CI/CD 自动发布指南]]：GitLab CI 流水线（Kaniko 构建、K8s 部署、Release）与 CI/CD Variables 管理敏感参数，以及 Claude 自动 MR 评审
- [[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD基础|ArgoCD基础]]：在 argocd-secret 中配置 GitLab Webhook 密钥，推送后触发 ArgoCD 同步

## 知识空白

- 仓库中尚无 GitLab Runner 的安装、注册与执行器配置
- 仓库中尚无 GitLab 版本升级与高可用部署的实践
- 仓库中尚无 GitLab 与 LDAP 等企业身份源的集成
