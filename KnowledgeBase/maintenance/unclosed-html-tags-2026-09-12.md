---
title: 未闭合 HTML 标签扫描报告 2026-09-12
tags:
  - knowledgebase/maintenance
  - markdown/lint
date: 2026-09-12
sources:
  - "[[k8s基础-yaml-apply]]"
aliases:
  - 未闭合标签检查
---

# 未闭合 HTML 标签扫描报告（2026-09-12）

## 结论

扫描 vault 中的 Markdown 文件，排除 frontmatter、围栏代码、行内代码、HTML 注释、合法自闭合标签和允许省略结束标签的元素后，共发现 **12 个文件、33 个未闭合标签候选**。本次已修复 [[k8s基础-yaml-apply]] 中的 `<object>` 和 `<[]Object>` 类型标记，该文件不再出现在结果中。

这些候选大多是命令占位符或提示词模板参数，不是作者真正想写的 HTML。建议统一包在反引号中，例如把 `<version>` 写成行内代码形式，避免 Obsidian Live Preview 将其作为 HTML 起始标签。

## 普通文章与笔记（10 个）

| 文件 | 行号 | 未闭合标签 |
|------|------|------------|
| [[AI/ClaudeCode/Claude-Fable-5-system-prompt]] | 148、420 | `<country>`、`<company>`、`<name>` |
| [[Azure/2_AKS-basics]] | 679、680、689 | `<pdb>`、`<pdbname>`、`<pdb-name>`、`<target>` |
| [[Azure/5_Azure-Storage]] | 417、418、430 | `<client>`、`<tenant>`、`<sa>`、`<container>` |
| [[Docker-Kubernetes/k8s-UI-tools/rancher(v2.6.4)管理k8s集群]] | 99 | `<eof>` |
| [[Docker-Kubernetes/k8s-basic-resources/k8s基础-kubeadm]] | 68 | `<version>` |
| [[Docker-Kubernetes/k8s-installation-management/升级/k8s迁移容器运行时-版本升级]] | 348、417 | `<eof>`（2 处） |
| [[Docker-Kubernetes/k8s-scaling/k8s-HPA-VPA]] | 84 | `<nodename>` |
| [[Docker-Kubernetes/kubeblocks/kubeblocks部署WordPress]] | 81 | `<your-class-name>` |
| [[Linux-Shell/Linux-learning-notes]] | 1515–1518 | `<service>`（2）、`<zone>`（4）、`<port>`、`<portnumber>` |
| [[Python/python-基础/python-basics]] | 1148 | `<h1>` |

## 辅助 Markdown（2 个）

| 文件 | 行号 | 未闭合标签 |
|------|------|------------|
| [[AI/AIOps/agents身份文件/aiops/skills/k8s-install-orchestrator/SKILL]] | 162、172、183–185 | `<raw>`（3）、`<user-provided>`（2） |
| [[Python/python-运维开发/python-Linux-operation]] | 592、594 | `<module>`（2） |

> [!note]
> `Python/python-运维开发/python-Linux-operation.md` 是普通笔记，但命中内容来自 Python traceback 的 `<module>`；这里单列是因为它属于代码输出语境。未使用代码围栏时，Obsidian 仍可能按 HTML 解析。

## 扫描方法

1. 遍历 vault 中的 Markdown 文件，跳过 `.git`、`.obsidian`、`.agents`、`.codex` 和 `node_modules`。
2. 屏蔽 YAML frontmatter、代码围栏、行内代码、HTML 注释和 URL autolink。
3. 忽略 `img`、`br`、`hr` 等 void element、自闭合标签，以及 HTML 允许省略结束标签的元素。
4. 对剩余开始/结束标签执行文件内栈匹配，并记录未配对的开始标签。

## 建议修复方式

- 命令占位符：写成行内代码，例如 `kubectl get pdb <pdb-name>` 整体放入代码围栏，或至少将占位符用反引号包裹。
- 类型说明：使用 `<object>`、`<version>` 这样的行内代码。
- traceback、正则表达式和 shell heredoc：使用带语言标识的围栏代码块。
- 真正需要 HTML 的内容：补齐对应结束标签，并在阅读视图与 Live Preview 中分别验证。
