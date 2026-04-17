---
title: K8s Report Skills 自研技能
tags:
  - knowledgebase/source
  - ai/claude-code
  - kubernetes/monitoring
date: 2026-04-17
sources:
  - "[[AI/skills/k8s-report-skills/SKILL.md]]"
  - "[[AI/skills/k8s-report-skills/k8s_inspector.py]]"
aliases:
  - k8s-report-skills
---

# K8s Report Skills（自研 Claude Code Skill）

## 元信息
- **原始文档**：[[AI/skills/k8s-report-skills/SKILL.md]]、[[AI/skills/k8s-report-skills/k8s_inspector.py]]
- **领域**：AI × Kubernetes 运维
- **摄入日期**：2026-04-17
- **类型**：自研 Claude Code Skill

## 摘要

k8s-report-skills 是一个自研的 Claude Code Skill，使用 Python kubernetes 客户端对 K8s 集群进行全面巡检，并通过 Jinja2 渲染生成精美的 HTML 健康报告。Skill 遵循 Claude Code Skills 规范（SKILL.md frontmatter），可被 Claude Code 自动发现和触发。

## 关键知识点

1. **Skill 结构规范**：包含 SKILL.md（技能定义 + frontmatter）、Python 主脚本、Jinja2 HTML 模板、requirements.txt，遵循 Claude Code Skills 标准目录结构
2. **六大巡检维度**：集群基本信息、节点状态（CPU/内存/Pod 使用率）、Pod 异常检测（CrashLoopBackOff/Pending/高频重启）、Deployment 副本一致性、PV/PVC 存储卷状态、近 1 小时警告事件
3. **双模式连接**：支持 kubeconfig 文件（本地/远程）和 InCluster ServiceAccount（集群内 Pod 运行）两种认证方式
4. **HTML 报告特性**：带进度条的集群资源使用率仪表盘、异常资源高亮（红色/橙色状态标记）、响应式布局适合邮件发送
5. **Agent 集成设计**：提供 `run_k8s_inspection_skill()` 顶层接口返回 HTML 字符串，也暴露 `K8sReportSkill` 类的细粒度方法供 Agent 获取原始数据（JSON/Dict）
6. **依赖精简**：仅需 kubernetes（≥28.1.0）和 Jinja2（≥3.1.2）两个 Python 包，部署门槛低

## 涉及的概念与实体

- [[KnowledgeBase/entities/Claude-Code]]：宿主 Agent 框架
- [[KnowledgeBase/entities/Kubernetes]]：巡检目标平台
- [[KnowledgeBase/concepts/Observability]]：巡检属于可观测性实践
- [[KnowledgeBase/concepts/自动化运维]]：Agent 驱动的自动化巡检

## 值得注意

- 这是 **自研 Skill**，存放在 `AI/skills/` 目录下，与第三方开源 Plugin/Skills 区分
- 与 `Docker-Kubernetes/k8s-monitoring-logging/K8s全面巡检脚本-生成HTML健康报告.md` 中的 Shell 巡检脚本形成互补：Shell 版适合 CronJob 定时执行，Python Skill 版适合 Agent 按需触发
- 依赖项精简（仅 kubernetes + Jinja2），部署门槛低
