---
title: "Obsidian Vault 模板库合集：48 个 GitHub 宝藏 vault"
source: "https://mp.weixin.qq.com/s/2sPkMM4TllTjOGY7CGa6ZQ"
created: 2026-06-28
tags:
  - obsidian
  - vault-template
  - awesome-list
---

# Obsidian Vault 模板库合集

> GitHub 仓库：[obsidian-pkm-vault/awesome-obsidian-vault](https://github.com/obsidian-pkm-vault/awesome-obsidian-vault)（1.2k star，CC0 协议，维护 4 年）
>
> 48 个开箱即用的 vault 资源，按 11 大场景分类。从零搭 vault 搭了一周没头绪？clone 一个 5 分钟就有了。

## 为什么需要这个

从零搭 Obsidian vault 的三个痛点：

1. **从零开始太费时间**——配置模板 + 标签体系 + 插件 + 示例笔记，至少 1-2 周
2. **参考不足**——官方文档只教"怎么用"，不教"怎么搭"，新手连结构长什么样都没见过
3. **不同职业需求差太多**——程序员要 API 文档结构，HR 要人才盘点模板，律师要合同库

`awesome-obsidian-vault` 解决的是第三个：它给你 **48 份按真实场景分好类的 vault**，总有一份能 clone 下来就用。

## 48 个 vault 的 11 大分类

| 类别 | 数量 | 典型用途 |
|------|:----:|---------|
| 烹饪 | 10 | 食谱笔记（中文 HowToCook 也在内） |
| 计算机科学 | 6 | 编程语言学习、CS 课程笔记 |
| 数字花园 | 7 | 知识图谱、个人 wiki 模板 |
| 文档/Documentation | 9 | API 文档、知识库、Obsidian 官方 hub |
| Dev & Design | 4 | Agent Skills、Vercel skills、System Design |
| 工程 | 1 | Data Engineering Wiki |
| 知识管理 | 2 | KaaS、nikitavoloboev/knowledge（传奇个人知识库） |
| 个人网站 | 3 | oscean、100r.co、kokorobot |
| Web Directory | 2 | 资源导航站 |
| 样本/Showcases | 3 | 优秀公开 vault 案例 |
| 字典/语言资源 | 6 | 离线 wiki、词典 slob |

> ✨ 标记的 9 个是作者重点推荐的"标杆级"vault，质量最稳。

## 挑选三原则

### 原则 1：作者活跃度 > 仓库 star 数

有一堆 1k+ star 的老 vault，但 5 年没更新，Obsidian 1.5 之后的插件配置全过时。

**检查方法**：点进 vault 仓库 → 看 `Last commit` 时间 → 1 年内有提交 = 可用。

### 原则 2：场景对口 > 模板花哨

先问自己"我搭这个 vault 是要解决什么事"：
- 想做产品 wiki → 看 `Documentation` 类
- 想做学习笔记 → 看 `Computer Science` 类
- 想做个人品牌网站 → 看 `Personal Site` 类

### 原则 3：先 clone 标杆，再 clone 同类

从 ✨ 标记的开始看，再扩散到同类别其他 vault。

## 5 个推荐 vault（含踩坑）

### ① Kepano Obsidian ✨（数字花园启蒙）

**仓库**：kepano/obsidian-obsidian | **在线**：stephango.com/vault

Obsidian 官方 CEO Steph Ango **自己的 vault**。最克制、最优雅的数字花园结构。

`Homepage.md` 那套"今日焦点 + 最近修改"的设计可以直接抄到自己的 vault 里。

**适合**：想做个人 wiki / 知识花园。⏱ clone 下来 10 分钟读完 README 就能上手。

### ② Obsidian Hub ✨（Obsidian 生态地图）

**仓库**：obsidian-community/obsidian-hub | **在线**：publish.obsidian.md/hub

Obsidian 官方社区维护的**全生态索引**——插件、主题、教程、第三方 vault 全部收录。

当**插件选型词典**用——想装个新插件先去 hub 搜一下。

### ③ JavaScript Info（前端学习神器）

**仓库**：javascript-tutorial/en.javascript.info

整套 JavaScript 教程的 **Obsidian 双向链接版本**。每个章节是独立 md 文件，"相关信息"块用 wikilink 串联。

**适合**：前端工程师 / 想要个"成熟 markdown 学习笔记结构"做参考。

### ④ DevCookbook（团队 wiki 模板）

**仓库**：microsoft/DevCookbook

微软出的**团队工程实践 wiki**。包含代码评审清单、Incident 复盘模板、ADR 决策记录结构。

**适合**：项目经理 / 团队 lead / 想搭"非个人"知识库。

### ⑤ HowToCook（中文食谱 vault）

**仓库**：Anduin2017/HowToCook

**程序员写的菜谱**——按算法结构组织（"动态规划"对应"分段烹饪"），每道菜一份标准模板（主料/步骤/复杂度）。

**vault 的最大价值不是"装什么"，是"装的方式"。**

## 踩坑清单

| ❌ 避开 | 原因 |
|--------|------|
| 西班牙语 vault（Recetas Cocina） | 满屏西语 + 配图全在 instagram，国内打不开 |
| 重度依赖冷门插件的 vault（如 Obsidian Icewind） | 依赖 Dataview 模板 + Minimal 主题 + 3 个冷门插件，少一个就渲染崩 |
| 从 Hugo 静态站导出的 vault | Obsidian 打开是单向链接断的、双向链根本不存在。clone 前看一眼是不是 .md 原生 |

## 5 分钟上手流程

1. 打开仓库主页 [awesome-obsidian-vault](https://github.com/obsidian-pkm-vault/awesome-obsidian-vault)
2. 按 11 大类目找你最需要的 1-2 个
3. 点进 vault 链接 → Code → Download ZIP 或 git clone
4. 在 Obsidian 左上角 "Open another vault" → 选下载的文件夹
5. 5 分钟浏览首页 + 几个示例笔记 → 你就有了一个**结构完整的 vault 起点**
