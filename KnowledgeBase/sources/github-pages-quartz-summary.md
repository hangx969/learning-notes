---
title: GitHub Pages 构建：Quartz 4 来源摘要
tags:
  - knowledgebase/source
  - ai/obsidian
  - git/github-actions
date: 2026-10-03
sources:
  - "[[AI/Obsidian/github-pages-quartz]]"
aliases:
  - Quartz 4 发布流程摘要
  - Obsidian 笔记的 GitHub Pages 构建
---

# GitHub Pages 构建：Quartz 4 来源摘要

## 元信息

- **原始文档**：[[AI/Obsidian/github-pages-quartz|用 GitHub Actions 发布 Obsidian 笔记：Quartz 4]]
- **领域**：AI / Obsidian / 文档网站发布
- **摄入日期**：2026-10-03

## 摘要

文章记录本仓库使用 Quartz 4 构建 GitHub Pages 的流程，提供固定提交、配套文件、完整 workflow 和本地验收步骤。Python 导出器筛选 Git 已跟踪的原始笔记，保留 Git 更新时间和链接消歧规则，再由固定版本的 Quartz 构建 `_site/`。发布沿用 `main` push 与手动触发，通过 Pages artifact 部署。文章还说明旧 URL、标题锚点和 wikilink 的兼容处理，并区分已提交的基础版本、待审阅主题与实际验证范围。

## 关键知识点

1. **发布约定**：Quartz 构建沿用现有触发、权限、部署环境和 artifact 流程。`_site/` 是最终发布产物，需在上传和预览时保留，无需提交到 Git。
2. **配套文件与版本**：复现需一起取得 `tools/site/build.py`、Python 依赖、`tools/site/quartz/` 和 workflow。基础方案固定在仓库提交 `af3c83afb0616ed996ac8a9841cd713fbb44e109`，生成器使用 Quartz 4.5.2；Python 依赖为 `PyYAML~=6.0`，Node.js ≥22、npm ≥10.9.2。
3. **构建顺序**：`upstream.json` 固定生成器提交，缓存位于 `.site-cache/`。CI 先用 `--prepare` 取得上游 lockfile，再设置 npm cache、运行 `npm ci`，最后通过 `--skip-install` 构建；修改配置应写回受版本管理的文件。
4. **内容与链接**：候选笔记来自 Git 已跟踪文件，最近 15 篇按 Git 路径更新时间排序。保留重名消歧规则；`VaultLinks` 在 AST 上处理 wikilink，`LegacyUrls` 和 `LegacyAnchors` 兼容旧目录 URL、查询参数与标题锚点。
5. **主题入口**：Quartz 通过配置、布局和组件定制主页，保留原生 `Darkmode`。日夜配色在 `theme.colors` 中设置。待审阅的自定义主页需要整套组件、脚本、样式和匹配的导出器。
6. **验收边界**：本地构建、Actions 运行和 Pages 部署分别验收。构建成功还需检查中文路径、`C++`、旧锚点、资源、搜索和手机宽度；基础提交与待审阅主题的本地预览实现也需分别核对。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Obsidian|Obsidian]]：vault、wikilink 与只读导出。
- [[KnowledgeBase/concepts/CICD|CI/CD]]：从笔记到网站 artifact，再到 Pages 部署。
- [[KnowledgeBase/maps/tool-map|工具地图]]：Obsidian 的网站发布入口。
- [[KnowledgeBase/maps/ai-workflow-map|AI 工作流专题地图]]：知识库组织与发布流程。

## 值得注意

- workflow 必须使用匹配的导出器、Quartz 配置和组件；只复制 SCSS 或构建命令无法复现自定义主页。
- 复现命令与固定提交见原文。Quartz 自定义主题尚在本地审阅，克隆基础提交不会得到该主题。
- 文章移入 `AI/Obsidian/` 后成为原始来源；未纳入 Git 跟踪时，现有发布器不会收集它。知识编译层仍按原有规则排除。
