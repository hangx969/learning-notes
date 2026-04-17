---
title: OpenClaw 多智能体定义文件导出
tags:
  - knowledgebase/source
  - ai/openclaw
  - ai/multi-agent
date: 2026-04-18
sources:
  - "[[AI/OpenClaw/Openclaw-多智能体]]"
  - "[[AI/agents/aiops/IDENTITY.md]]"
  - "[[AI/agents/k8s/IDENTITY.md]]"
  - "[[AI/agents/linux/IDENTITY.md]]"
  - "[[AI/agents/container/IDENTITY.md]]"
aliases:
  - agents-export
---

# OpenClaw 多智能体定义文件导出

## 元信息
- **原始文档**：`AI/agents/`（8 个智能体定义目录）
- **领域**：AI 多智能体架构
- **摄入日期**：2026-04-18
- **类型**：OpenClaw 多智能体实战配置文件导出

## 摘要

从 [[AI/OpenClaw/Openclaw-多智能体]] 中设计的多智能体团队导出的完整定义文件集合。包含 8 个智能体，每个由 IDENTITY.md（身份人设）、SOUL.md（核心价值观）、AGENTS.md（工作空间与行为规范）、HEARTBEAT.md（心跳配置）四大核心文件定义，部分还附带 Skills 子目录。构成一个以 aiops 为调度核心的 AIOps 多智能体团队。

## 关键知识点

### 团队架构

1. **调度核心**：aiops（AIOps 架构师）——纯路由型智能体，不亲自执行，只做任务分类、专家分发和结果汇总
2. **基础设施层**：linux（Linux 专家）、container（容器专家）、k8s（K8s 专家）——三个运维执行专家
3. **开发层**：architect（架构师）、backend-engineer（后端工程师）、frontend-engineer（前端工程师）——软件开发团队
4. **管理层**：pm（产品经理）——需求分析与任务拆解

### 核心文件规范

5. **IDENTITY.md**：定义智能体的外在人设——名称、角色、工作模式、个人宣言、行为边界
6. **SOUL.md**：定义智能体的核心价值观——核心真理、性格特征、不可逾越的边界
7. **AGENTS.md**：定义工作空间——核心身份确认、具体工作流程、可调用工具、输出格式规范
8. **HEARTBEAT.md**：心跳定时任务配置（当前均为空模板，预留周期性检查接口）

### 附带 Skills

9. **k8s-install-orchestrator**（aiops）：K8s 集群安装编排 Skill，协调 linux→container→k8s 三步部署
10. **docker-runtime-install**（container）：Docker/containerd 运行时安装 Skill，含 Rocky Linux 10 安装脚本
11. **k8s-cluster-install**（k8s）：K8s 集群安装 Skill
12. **rocky-linux10-init**（linux）：Rocky Linux 10 初始化 Skill，含系统初始化脚本

### 设计模式

13. **路由者-执行者分离**：aiops 严格不执行，只做分发——"知道答案也不抢专家的工作"
14. **Skill 优先原则**：发现可用 Skill 时必须严格按 SKILL.md 执行，不能擅自发挥
15. **角色定义三要素**：身份定义（IDENTITY）、任务边界（AGENTS）、核心价值观（SOUL）

## 涉及的概念与实体

- [[KnowledgeBase/entities/OpenClaw]]：宿主 Agent 平台
- [[KnowledgeBase/entities/Kubernetes]]：k8s 智能体的专业领域
- [[KnowledgeBase/entities/Docker]]：container 智能体的专业领域
- [[KnowledgeBase/concepts/自动化运维]]：AIOps 多智能体的核心应用场景

## 值得注意

- 这是 **实战配置文件**，不是文档——可直接用于 OpenClaw 多智能体部署
- aiops 的"克制"设计哲学值得学习：调度者绝不越界执行，即使它知道怎么做
- 与 `AI/skills/` 目录形成互补：skills 是 Claude Code 的能力扩展，agents 是 OpenClaw 的角色定义
