---
title: Script-Server 脚本 Web 化工具
tags:
  - knowledgebase/source
  - python/ops-tools
date: 2026-06-06
sources:
  - "[[Python/script-server-脚本Web化工具]]"
aliases:
  - Script-Server摘要
---

# Script-Server 脚本 Web 化工具

## 元信息
- **原始文档**：[[Python/script-server-脚本Web化工具]]
- **领域**：Python / 运维工具
- **摄入日期**：2026-06-06

## 摘要
Script-Server 是一个 Python 开源工具，可将 Shell/Python 脚本零改动包装成 Web 应用。通过 JSON 配置自动生成参数表单、实时输出、权限控制和审计日志，适合团队集中管理自动化脚本，让非技术人员也能通过浏览器执行运维操作。

## 关键知识点
1. **核心定位**：给运维脚本套 Web 外壳，零代码改动，JSON 配置即可
2. **部署方式**：Docker 一行命令（`bugy/script-server:latest`）或 Python 3.7+ 直接运行
3. **配置模式**：脚本放 `conf/runners/` 目录，JSON 定义参数（支持文本/文件上传/下拉框）
4. **企业特性**：LDAP/Google OAuth/htpasswd 认证 + 审计日志 + 执行历史
5. **局限性**：GUI 偏简单、高并发需调优、老版本（<1.17）有 XSS/CSRF 隐患

## 涉及的概念与实体
- [[KnowledgeBase/concepts/Python运维开发]]
- [[KnowledgeBase/concepts/自动化运维]]

## 值得注意
- 适合"脚本多但没有统一管理平台"的团队，门槛极低
- 与知识库中的 GoCron（定时任务 Web 化）思路类似，但 Script-Server 侧重"按需执行 + 参数化"
