---
title: "Obsidian vault 模板库合集：48 个 GitHub 上的宝藏 vault，下载即用"
source: "https://mp.weixin.qq.com/s/2sPkMM4TllTjOGY7CGa6ZQ?scene=1"
author:
  - "[[obsidian黑曜石]]"
published:
created: 2026-06-28
description: "通勤路上刷到一份清单：48 个 GitHub 精选 Obsidian vault，11 大场景——食谱、编程、API 文档、数字花园、即开即用。挑 vault 选了一周没头绪？我自己 clone 3 个，省一周。"
tags:
  - "clippings"
---
obsidian黑曜石 obsidian黑曜石 *2026年6月10日 19:44*

![../../运营中枢/附件/2026-06-09-awesome-obsidian-vault/首图-awesome-obsidian-vault.jpg](https://mmbiz.qpic.cn/sz_mmbiz_jpg/yib5IbOMe3l6Cyme5U3xvySPysQY2rvvibN7OiaDdBuGGIIPht1vpYE3nYT5pia7dvic0b6ib1zISOUm0UTibGUSDJEVCum5qwdu6c9nQmUo9svm2I/640?wx_fmt=jpeg&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

> 摘要：通勤路上刷到一份清单：48 个 GitHub 精选 Obsidian vault，11 大场景——食谱、编程、API 文档、数字花园、即开即用。挑 vault 选了一周没头绪？我自己 clone 3 个，省一周。（文末有我自己建的几个拿来即用的库，欢迎下载尝试）

---

3年前，我装好 Obsidian 的第一天，兴奋地新建了一个 vault。空空的，对吧——一个文件夹、一份欢迎文档、然后就愣住了。

我得自己写模板、自己配插件、自己立笔记结构。做了 3 周，最后我那个 vault 看着还是"工地状态"——几条孤零零的笔记、东一个西一个的标签、根本没成体系。

直到去年 12 月我在 GitHub 翻到一个仓库： `obsidian-pkm-vault/awesome-obsidian-vault` 。1.2k star，里面塞了 **48 个** 开箱即用的 vault 资源。

我 clone 下来 3 个——一周没搭出来的东西， **5 分钟就有了** 。

如果你也在"从零搭 vault"的坑里摔过，今天这篇文章，建议收藏。

---

## 一、你为什么需要这个

搭 Obsidian vault 的痛点，我总结了 3 个：

1.

**从零开始太费时间** — 一个像样的工作日志 vault，配置模板 + 标签体系 + 插件 + 示例笔记，至少 1-2 周。

2.

**参考不足** — 官方文档只教"怎么用"，不教"怎么搭"。新手连结构长什么样都没见过。

3.

**不同职业需求差太多** — 程序员要 API 文档结构，HR 要人才盘点模板，律师要合同库——同一份 vault 模板谁也用不上。

`awesome-obsidian-vault` 解决的就是 **第三个** ：它不只给你一份模板，它给你 **48 份按真实场景分好类的 vault** ，总有一份能 clone 下来就用。

---

## 二、这个仓库是什么

仓库作者是 obsidian-pkm-vault，维护 4 年了。它把 GitHub 上 48 个高质量的 Obsidian vault 整理成一张表，按 11 大场景分类：

| 类别 | 数量 | 典型用途 |
| --- | --- | --- |
| 烹饪 | 10 | 食谱笔记（中文 HowToCook 也在内） |
| 计算机科学 | 6 | 编程语言学习、CS 课程笔记 |
| 数字花园 | 7 | 知识图谱、个人 wiki 模板 |
| 文档/Documentation | 9 | API 文档、知识库、Obsidian 官方 hub |
| Dev & Design | 4 | Agent Skills、Vercel skills、System Design |
| 工程 | 1 | Data Engineering Wiki |
| 知识管理 | 2 | KaaS、nikitavoloboev/knowledge（传奇个人知识库） |
| 个人网站 | 3 | oscean、100r.co、kokorobot |
| Web Directory | 2 | 资源导航站（Interneto、Free Media Heck Yeah） |
| 样本/Showcases | 3 | 优秀公开 vault 案例 |
| 字典/语言资源 | 6 | 离线 wiki、词典 slob |

> ✨ 标记的 9 个是作者重点推荐的"标杆级"vault，质量最稳。

不是每个 vault 都能用——有的英语专八、有的配图全在外网、有的作者已经停更。 **关键是：怎么挑** 。

---

## 三、怎么挑？我自己的挑选框架

我把这个仓库 48 个翻了 2 遍， **真正"下载即用"不到一半** 。按"职场可用度"排个序，我提炼出 3 个挑选原则：

### 原则 1：作者活跃度 > 仓库 star 数

`awesome-obsidian-vault` 里有一堆 1k+ star 的老 vault，但 5 年没更新，Obsidian 1.5 之后的插件配置全过时。

**怎么查** ：点进 vault 仓库 → 看 `Last commit` 时间 → 1 年内有提交 = 可用。

### 原则 2：场景对口 > 模板花哨

别一上来就挑"最漂亮那个"。先问自己： **我搭这个 vault 是要解决什么事？**

•

想做产品 wiki → 看 `Documentation` 类

•

想做学习笔记 → 看 `Computer Science` 类

•

想做个人品牌网站 → 看 `Personal Site` 类

### 原则 3：先 clone 标杆，再 clone 同类

`awesome-obsidian-vault` 里的 ✨ 标，是作者认证的"最值得参考"的。从这些开始看，再扩散到同类别其他 vault，效率最高。

---

## 四、我自己 clone 的 5 个 vault（含踩坑）

按"我日常真的会打开"排序：

### ① Kepano Obsidian ✨（数字花园启蒙）

仓库：kepano/obsidian-obsidian | 在线：stephango.com/vault

Obsidian 官方 CEO Steph Ango **自己的 vault** 。 **这是我见过的最克制、最优雅的数字花园结构** 。

> 我用这个改了 3 版自己的主页。 `Homepage.md` 那套"今日焦点 + 最近修改"的设计，我抄到自己的 vault 里，到今天还在用。

适合：想做个人 wiki / 知识花园的打工人。

⏱ clone 下来 10 分钟读完 README 就能上手。

### ② Obsidian Hub ✨（Obsidian 生态地图）

仓库：obsidian-community/obsidian-hub | 在线：publish.obsidian.md/hub

Obsidian 官方社区维护的 **全生态索引** ——插件、主题、教程、第三方 vault 全部收录。

我把它当成 **插件选型词典** 用——想装个新插件？先去 hub 搜一下，看官方推荐 + 用户评价，再决定。

适合：插件选型纠结症患者 + 想知道"Obsidian 圈最近在玩什么"的人。

### ③ JavaScript Info（前端学习神器）

仓库：javascript-tutorial/en.javascript.info | 在线：javascript.info

整套 JavaScript 教程的 **Obsidian 双向链接版本** 。每个章节是独立 md 文件，"相关信息"块用 wikilink 串联。

> 我带过一个前端实习生，把这份 vault 丢给他，2 周就上手 JS 基础。比大部分培训班的笔记都强。

适合：前端工程师 / 在学 JS 的产品经理 / 想要个"成熟 markdown 学习笔记结构"做参考的人。

### ④ DevCookbook（团队 wiki 模板）

仓库：microsoft/DevCookbook | 在线：microsoft.github.io/DevCookbook

微软出的 **团队工程实践 wiki** 。包含代码评审清单、Incident 复盘模板、ADR 决策记录结构。

> 我一个朋友是某厂项目经理，团队用 DevCookbook 改造 wiki 模板，光"决策记录怎么写"这块就省了 3 天培训。

适合：项目经理 / 团队 lead / 想搭"非个人"知识库的人。

### ⑤ HowToCook（中文食谱 vault）

仓库：Anduin2017/HowToCook | 在线：cook.aiursoft.cn

**程序员写的菜谱** ——按算法结构组织（"动态规划"对应"分段烹饪"），每道菜一份标准模板（主料/步骤/复杂度）。

> 我一个不爱做饭的同事看完这个 vault，第一次正经做了顿红烧肉，从此入坑。 **vault 的最大价值不是"装什么"，是"装的方式"** 。

适合：所有想体验"vault 怎么改变生活"的人。

---

## 五、踩坑清单（先看再 clone）

我自己 clone 5 个的过程里，踩了 3 个坑：

❌ **Recetas Cocina（西班牙语食谱）** — 满屏西语 + 配图全在 instagram，国内打不开，浪费时间。

❌ **Obsidian Icewind** — 结构很美，但作者重度依赖 Dataview 模板 + Minimal 主题 + 3 个冷门插件， **少一个就渲染崩** 。纯新手别碰。

❌ **基于 Hugo 静态站生成的 vault** — README 顶部那行 NOTE 提醒了：很多 vault 是从 Hugo 静态网站导出来的， **Obsidian 打开是单向链接断的、双向链根本不存在** 。clone 前看一眼是不是.md 原生。

---

## 六、入手方式（5 分钟）

1.

打开仓库主页 github.com/obsidian-pkm-vault/awesome-obsidian-vault

2.

按上面表 1 的 11 大类目，找你最需要的 1-2 个

3.

点进 vault 链接 → Code → Download ZIP 或 git clone

4.

在 Obsidian 左上角 "Open another vault" → 选下载的文件夹

5.

5 分钟浏览首页 + 几个示例笔记 → 你就有了一个 **结构完整的 vault 起点**

⏱ 整个流程 **5 分钟** 。

---

## 七、谁适合用

✅ 刚装 Obsidian 不到 1 个月，不知道 vault 长什么样的  
✅ 搭了 vault 但结构混乱，想换思路的  
✅ 项目经理 / HR / 律师 / 设计师，想找 **非程序员场景** 的 vault 参考  
✅ 准备做"个人数字花园"或团队 wiki 的

❌ 已经搭好成熟 vault、只是想加插件的人 → 去看 awesome-obsidian（插件列表），不是这个仓库。

---

## 写在最后

写完这篇文章，我又翻了一遍 `awesome-obsidian-vault` 的提交历史。从 4 年前到今天，作者一直一个人在更新。

这件事本身就挺让我感动的—— **Obsidian 官方从不"推荐"别人的 vault** （他们的哲学是"你搭你的"），但社区里就是有人默默维护 4 年，给你整理好 48 个起点。

我自己去年 12 月 clone 下来 Kepano Obsidian 那个晚上，看着那 80 多条双向链接，第一次觉得：哦，原来 vault 不是文件夹， **是一张我自己织的网** 。

这感觉，你试试就知道。

---

**如果今天的内容对你有用：**  
🔴 **点亮「推荐❤️」** — 让更多在"搭 vault"上挣扎的朋友看到  
📌 **收藏** — 48 个 vault 链接都在里面，迟早用得上

**评论区聊聊：你 clone 下来最香的 vault 是哪个？**

把这篇文章 **转给那个"Obsidian 装了 1 个月还是空的"同事** 🤫

![IP头像-Obsidian黑曜石-v3](https://mmbiz.qpic.cn/mmbiz_jpg/yib5IbOMe3l49HctFdJWpuZKjsGUVfeQWONlmdRIwKVf1LTA142X4QyjCk9s8icKHe7REWzSnh6qeYswru5nZGwXQ9BiaPRzY8L1wtolnichnRo/640?wx_fmt=jpeg&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=1)

我是黑曜石，陪你打造第二大脑。今天推荐的是 GitHub 民间维护 4 年的宝藏清单—— **vault 早就在那里，别自己再搭一遍轮子。**

*仓库地址：https://github.com/obsidian-pkm-vault/awesome-obsidian-vault | CC0 1.0 协议（公共领域） | 列表本身不收费，clone 链接均来自原作者*

---

## 你干哪一行？对着你的职业，拿走这套Obsidian文件夹+标签模板

## TaskNotes 配置全攻略：7步把 Obsidian 变成任务中枢｜基于 PTV 示范库截图跟做

## 我搭了一个 Obsidian 工作日志库，下载就能用 | 每天 3 分钟，效率翻倍

[拿走不谢！用Obsidian搭一套从工作到生活的完整的任务管理库](https://mp.weixin.qq.com/s?__biz=MzkyODM0MzI3MA==&mid=2247484372&idx=1&sn=22a6740e2c43c12aa2d0fa9b8263b6c9&scene=21#wechat_redirect)

Obsidian模板库 · 目录