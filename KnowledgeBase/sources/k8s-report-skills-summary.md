---
title: K8s 巡检自研 Skills
tags:
  - knowledgebase/source
  - ai/claude-code
  - kubernetes/monitoring
date: 2026-04-17
sources:
  - "[[AI/skills/k8s-report-skills/SKILL.md]]"
  - "[[AI/skills/k8s-report-skills/k8s_inspector.py]]"
  - "[[AI/skills/k8s-inspect-skills/SKILL.md]]"
  - "[[AI/skills/k8s-inspect-skills/k8s_inspect.sh]]"
aliases:
  - k8s-report-skills
  - k8s-inspect-skills
---

# K8s 巡检自研 Skills

## 元信息
- **原始文档**：`AI/skills/k8s-report-skills/`、`AI/skills/k8s-inspect-skills/`
- **领域**：AI × Kubernetes 运维
- **摄入日期**：2026-04-17
- **类型**：自研 Claude Code Skill（2 个）

## 摘要

两个互补的自研 K8s 巡检 Skill，分别基于 Python 和 Shell 实现，均可被 Claude Code 自动发现和触发，对 Kubernetes 集群进行全面健康检查并生成 HTML 报告。

## 关键知识点

### k8s-report-skills（Python 版）

1. **技术栈**：Python kubernetes 客户端 + Jinja2 模板引擎
2. **六大巡检维度**：集群基本信息、节点状态（CPU/内存/Pod 使用率）、Pod 异常检测、Deployment 副本一致性、PV/PVC 存储卷状态、近 1 小时警告事件
3. **双模式连接**：kubeconfig 文件（本地/远程）和 InCluster ServiceAccount
4. **报告风格**：浅色专业主题，带进度条的资源使用率仪表盘
5. **Agent 集成**：`run_k8s_inspection_skill()` 返回 HTML 字符串，`K8sReportSkill` 类暴露细粒度方法获取原始 JSON 数据
6. **依赖**：kubernetes（≥28.1.0）+ Jinja2（≥3.1.2）

### k8s-inspect-skills（Shell 版）

7. **技术栈**：Bash + kubectl CLI，零 Python 依赖
8. **七大巡检模块**：节点健康、Pod 状态、资源配额与 PVC、证书到期（kubeadm + TLS）、网络组件（CoreDNS/CNI）、警告事件
9. **报告风格**：深色仪表盘主题（dark dashboard），顶部 4 统计卡片 + 分模块表格
10. **Agent 结构化输出**：脚本末尾输出 `INSPECTION SUMMARY` 文本块，便于 Agent 解析关键指标
11. **跨平台兼容**：macOS（BSD date）和 Linux（GNU date）证书日期解析自适应
12. **来源**：改造自 [[Docker-Kubernetes/k8s-monitoring-logging/K8s全面巡检脚本-生成HTML健康报告]] 的 Shell 脚本

### 共同特性

13. **Skill 结构规范**：SKILL.md（含 frontmatter name/description/compatibility）+ 主脚本 + 支撑文件
14. **只读操作**：仅执行 get/list/describe，不修改集群状态
15. **kubeconfig 参数化**：支持 `--kubeconfig` 指定路径，适配多集群场景

## 涉及的概念与实体

- [[KnowledgeBase/entities/Claude-Code]]：宿主 Agent 框架
- [[KnowledgeBase/entities/Kubernetes]]：巡检目标平台
- [[KnowledgeBase/concepts/Observability]]：巡检属于可观测性实践
- [[KnowledgeBase/concepts/自动化运维]]：Agent 驱动的自动化巡检

## 值得注意

- 两个 Skill 形成 **互补组合**：Python 版适合 Agent API 集成和获取结构化数据，Shell 版适合 CronJob 定时执行和运维工程师直接使用
- Shell 版比 Python 版多了 **证书到期检查** 和 **网络组件检查**，覆盖更全面
- Python 版的优势是 **细粒度数据访问**（可单独调用各检查方法获取 Dict/JSON）
- 均已通过 v1.35.3 集群（3 节点、43 Pod、13 Namespace）实测验证
