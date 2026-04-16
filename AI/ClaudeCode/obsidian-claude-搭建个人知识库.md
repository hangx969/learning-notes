---
title: Obsidian + Claude Code 搭建 AI 知识库
tags:
  - AI
  - obsidian
  - claude
  - knowledge-management
aliases:
  - Obsidian AI 知识库
  - Claude Code Obsidian 集成
date: 2026-04-16
---

# Obsidian + Claude Code 搭建 AI 知识库

## 知识库类软件的现状

当前市面上的知识库软件大致可以分为三类，各有不足：

| 类型 | 代表产品 | 优势 | 不足 |
| --- | --- | --- | --- |
| 传统笔记 | 语雀、印象笔记 | 整理、记录、协作齐全 | ==没有 AI==，知识存进去就"死"了 |
| AI + 知识库 | 腾讯 IMA、秘塔 AI 搜索 | 能上传文档做问答 | 更像内容聚合社区，产出形式受限 |
| 纯 AI 工具 | 元宝、豆包、Kimi | AI 能力强，写作/总结/翻译 | ==没有本地知识库==，知识无法沉淀 |

> [!summary] 核心矛盾
> 要么没脑子，要么没记忆，要么有脑子有记忆但==不是你的==。

---

## 为什么选 Obsidian？

[Obsidian](https://obsidian.md) 在海外已有 ==150 万月活用户==，开发者、研究者、写作者用得特别多。

> [!info] 关于 Obsidian 公司
> - 完全没有接受风投，全靠用户付费
> - 年收入约 **2500 万美元**，续费率 **90%+**

**核心优势：**

- **本地存储** — 所有笔记就是电脑上的 `.md` 文本文件，不依赖任何云服务，数据从头到尾在自己手里
- **双向链接** — 笔记之间用 `[[wikilink]]` 互相关联，形成知识网络
- **Graph View** — 可视化所有笔记的关联关系，哪些知识孤立、哪些高频被引用，一目了然

> [!warning] 之前的门槛
> 要装插件、配同步、学 Markdown 语法、研究方法论（Zettelkasten、PARA、MOC），光折腾"怎么用"就能把人劝退。

==但现在不一样了。== Claude Code 的生态起来之后，Obsidian 的使用门槛大幅降低——你不需要懂那些方法论，Claude Code 替你搞定。

---

## 三个关键工具：打通 Obsidian × AI

### 1. Claudian 插件

> 直接把 Claude Code 嵌进 Obsidian 侧边栏，选中笔记就能让 AI 总结、扩写、找关联，整个过程不离开编辑器。

🔗 GitHub: [YishenTu/claudian](https://github.com/YishenTu/claudian)

> [!tip] 安装步骤
> 1. 在 [Release](https://github.com/YishenTu/claudian/releases) 中下载 `main.js`、`manifest.json`、`styles.css`
> 2. 放到 `.obsidian/plugins/claudian/` 目录
> 3. 重启 Obsidian → 插件页面启用 Claudian
> 4. 在设置中配置 Claude Code 相关环境变量
> 5. 侧边栏打开 Claudian 即可使用

### 2. Obsidian Skills

> 让 Claude Code 理解 Obsidian 的格式——双向链接、标签、属性、嵌入，全都认得。

🔗 GitHub: [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills)

> [!tip] 安装步骤
> 1. 下载 Skills 文件
> 2. 放到 vault 的 `.claude/` 目录下即可

### 3. Obsidian Local API + Claude MCP

> 配好后 Claude Code 可以直接==搜索、读取、创建、修改==你的笔记，AI 直接操作知识库，无需手动复制粘贴。

**依赖项：**

- **Local REST API 插件**：[coddingtonbear/obsidian-local-rest-api](https://github.com/coddingtonbear/obsidian-local-rest-api)
  - 插件市场直接搜 `Local REST API`，下载并开启
  - 拿到 `API Key`、`Host`、`Port` 即可
- **MCP 服务端**：[MarkusPfundstein/mcp-obsidian](https://github.com/MarkusPfundstein/mcp-obsidian)

> [!example] MCP 配置
> 放到 vault 目录（`.claude/settings.json`）或 Claude 全局配置均可：
> ```json
> {
>   "mcpServers": {
>     "mcp-obsidian": {
>       "command": "uvx",
>       "args": ["mcp-obsidian"],
>       "env": {
>         "OBSIDIAN_API_KEY": "你的_API_KEY",
>         "OBSIDIAN_HOST": "127.0.0.1",
>         "OBSIDIAN_PORT": "27124",
>         "OBSIDIAN_PROTOCOL": "https"
>       }
>     }
>   }
> }
> ```
