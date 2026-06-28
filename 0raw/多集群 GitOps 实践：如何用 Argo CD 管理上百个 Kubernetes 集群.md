---
title: "多集群 GitOps 实践：如何用 Argo CD 管理上百个 Kubernetes 集群"
source: "https://mp.weixin.qq.com/s/gflLt0lXE0zkJGs1hncBtg"
author:
  - "[[AI炼丹踩坑]]"
published:
created: 2026-06-28
description: "单集群 GitOps 玩得很顺，到了多集群规模，问题会突然变成平台工程问题。Argo CD 依然是主角，但重点不再是 Sync 按钮，而是 ApplicationSet、目录模型、权限隔离和发布半径控制。"
tags:
  - "clippings"
---
每个集群内部署轻量 Argo CD、Argo CD Agent，或者类似的 GitOps Agent。集群自己去 Git 拉配置，不需要中心控制面直连 API Server。