---
title: GitHub Pages 构建：MkDocs Material 与 Quartz 来源摘要
tags:
  - knowledgebase/source
  - ai/obsidian
  - git/github-actions
date: 2026-10-03
sources:
  - "[[AI/Obsidian/github-pages-mkdocs-material-quartz]]"
aliases:
  - MkDocs Material 与 Quartz 发布流程摘要
  - Obsidian 笔记的 GitHub Pages 构建
---

# GitHub Pages 构建：MkDocs Material 与 Quartz 来源摘要

## 元信息

- **原始文档**：[[AI/Obsidian/github-pages-mkdocs-material-quartz|用 GitHub Actions 发布 Obsidian 笔记：MkDocs Material 与 Quartz 4]]
- **领域**：AI / Obsidian / 文档网站发布
- **摄入日期**：2026-10-03

## 摘要

文章记录本仓库使用 MkDocs Material 和 Quartz 4 构建 GitHub Pages 的两套流程，提供固定提交、配套文件、完整 workflow 和本地验收步骤。两套方案沿用 `main` push 与手动触发，通过 Pages artifact 发布 `_site/`，并保留原始笔记只读、发布筛选和 Git 更新时间规则。Material 通过构建 hook 和自定义 Obsidian 扩展加入虚拟页面；Quartz 先导出临时内容，再用固定的上游版本构建。文章同时说明旧 URL、标题锚点和 wikilink 的兼容处理，并区分已提交的基础版本、待审阅主题与实际验证范围。

## 关键知识点

1. **发布约定**：生成器可以替换，触发、权限、部署环境和 artifact 流程保持一致。`_site/` 是最终发布产物，需在上传和预览时保留，无需提交到 Git。
2. **Material 配套文件**：复现需一起取得 `mkdocs.yml`、构建 hook、`obsidian.py`、样式、Python 依赖和 workflow。`File.generated` 加入筛选后的笔记，`on_serve` 监听位于 `docs_dir` 之外的原始主题目录。
3. **Quartz 固定版本**：基线使用 Quartz 4.5.2、Node.js 22 和 npm ≥10.9.2。`upstream.json` 固定生成器提交，配置在 `tools/site/quartz/`，缓存位于 `.site-cache/`；CI 先 `--prepare` 取得 lockfile，再设置 npm cache、运行 `npm ci` 和构建。
4. **内容与链接**：候选笔记来自 Git 已跟踪文件，最近 15 篇按 Git 路径更新时间排序。保留重名消歧规则；`VaultLinks` 在 AST 上处理 wikilink，`LegacyUrls` 和 `LegacyAnchors` 兼容旧目录 URL、查询参数与标题锚点。
5. **主题入口**：Material 通过 palette 配置日夜切换，`repo_url` 提供 GitHub 入口；Quartz 通过配置、布局和组件定制主页，保留原生 `Darkmode`。待审阅的 Quartz 自定义主页需要整套组件、脚本、样式和匹配的导出器。
6. **验收边界**：本地构建、Actions 运行和 Pages 部署分别验收。Material strict 构建仍可能包含被设为 info 的缺失链接提示；构建成功不能代表所有历史链接有效。迁移还需检查中文路径、`C++`、旧锚点、资源、搜索和手机宽度。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Obsidian|Obsidian]]：vault、wikilink 与只读导出。
- [[KnowledgeBase/concepts/CICD|CI/CD]]：从笔记到网站 artifact，再到 Pages 部署。
- [[KnowledgeBase/maps/tool-map|工具地图]]：Obsidian 的网站发布入口。
- [[KnowledgeBase/maps/ai-workflow-map|AI 工作流专题地图]]：知识库组织与发布流程。

## 值得注意

- Material 和 Quartz 的 `tools/site/build.py` 职责不同，workflow 必须配合对应版本的适配文件，不能只替换构建命令。
- 复现命令与固定提交见原文。Quartz 自定义主题尚在本地审阅，克隆基础提交不会得到该主题。
- 文章移入 `AI/Obsidian/` 后成为原始来源；未纳入 Git 跟踪时，现有发布器不会收集它。知识编译层仍按原有规则排除。
