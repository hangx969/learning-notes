Openclaw 可以添加很多 Skill 以提升自身的能力，skills 可以从如下地址下载：
- Openclaw 官方 hub： https://clawhub.ai/
- Openclaw 实用 skills 集合： https://github.com/VoltAgent/awesome-openclaw-skills

# skills管理工具Clawhub
教程文档： https://docs.openclaw.ai/zh-CN/tools/clawhub

Clawhub 是有 openclaw 官方提供的 skill 管理工具，可以用该工具搜索、安装、升级或卸载skill，首先安装该工具：

```sh
npm i -g clawhub

# 登录
clawhub login --token <从clawhub注册登录拿到CLI token>

# 搜索
clawhub search "pdf"

# 安装
clawhub install pdf
```

> 注意：用clawhub安装的Skills默认是装在当前Agent的工作目录中的Skills里，是局部的。想要装成全局Skills，需要手动安装到
# 手动下载Skills
- https://clawhub.ai/ 上找到想要的，下载到 openclaw 的工作目录下的 skills 目录下即可。（没有就创建一个）
- 可以在WebUI的技能中查看到安装的Skills

> 注意：第一次运行某个新skill的时候可能速度会比较慢，因为会安装一些依赖包。

# 办公Skills
下载了如下skills：
- https://clawhub.ai/ivangdavila/powerpoint-pptx
- https://clawhub.ai/awspace/pdf
- https://clawhub.ai/guohongbin-git/xlsx-cn

解压拷贝到.openclaw/skills目录下。

## 总结pdf内容
总结 PDF 时，需要给予 openclaw 具体的 pdf 路径或者文件名，否则会全盘扫描。

## 生成excel表
提供一些源数据，生成一个excel文件：
- 请帮我根据这些信息生成一个 Excel文件，需要包含图表，并存储在桌面的"xxx.xlsx"文件内

## 生成PPT
帮我生成一个 PPT，这个 PPT是关于 openclaw介绍相关的，只需要生成三页 PPT即可，注意你需要先列出来大纲，然后再生成 PPT。请注意你需要使用桌面的 openclaw.pptx 模版进行生成。

# 自我进化Skills
这个 skill 不是“多了一个命令”，而是给 agent 加了一套行为模式：

> **做事 → 复盘 → 记录纠正 → 沉淀经验 → 下次改进**
> **当 agent 出错、被纠正、完成重要任务、或发现更优方法时，让它主动复盘并把经验沉淀为长期规则。**

它的目标不是单次答对，而是**越用越会做**。

用法：
1. 用法 1：出现错误时直接触发
2. 用法 2：做完一个重要任务后让它复盘
3. 用法 3：把你的偏好沉淀进去


# 记忆插件
https://memos-claw.openmem.net/docs/index.html#quickstart

OpenClaw 自己本身也有内建 memory 机制（MEMORY.md / memory*.md + memory_search）。
而这个 `memos-local-openclaw-plugin` 是 **memory 类插件**，**本地 SQLite 存储**

部署完成后可以可视化看大存储起来的memory（127.0.0.1:18799）

# 安全审计-skill-vetter
这个skill是spclaudehome做的，下载量30000+，LobeHub评分4.96/5。它本身是一个纯文档型skill，没有任何可执行代码，说白了就是一套安全审查协议。装上之后，每次你要安装新的skill，它会引导你走四步审查流程：先查来源（作者信誉、GitHub活跃度、Star数量），然后做代码审查（扫描数据外泄模式、credential访问、eval()调用、可疑网络请求），再分析权限范围，最后给出风险评级，分LOW、MEDIUM、HIGH、EXTREME四个等级。

# 浏览器搜索和互联网平台信息抓取
Agent-browser & Agent-Reach
AI Agent最大的痛点是什么？看不到外面的世界。这两个配合起来，基本上让你的OpenClaw长出了眼睛和手。

## Agent-broswer
https://github.com/vercel-labs/agent-browser

Agent-browser是Vercel Labs用Rust写的无头浏览器自动化CLI，GitHub 19600+ stars。Agent-browser其实不算是Skill，本质上是个无头浏览器工具。

跟传统的浏览器自动化工具比（Puppeteer、Playwright），它最大的不同在于用accessibility-tree快照生成稳定的元素引用，类似@e1、@e2这种标记。传统CSS选择器在页面变动时很容易失效，但这种基于accessibility-tree的引用要稳定得多，对AI Agent来说简直是刚需。

除了基本的页面导航和元素交互，它还支持截图、PDF生成、网络请求拦截、视频录制，甚至能做像素级diff对比。

```sh
npm install -g agent-browser
agent-browser install  # 下载Chromium，linux下加上 --with-deps 安装依赖
npx skills add vercel-labs/agent-browser
```

claude code和openclaw都能用。

**场景：Web数据采集**
需要从某个网站收集一些公开信息？以前要么手动复制，要么让AI写爬虫脚本。
现在可以让AI直接用agent-browser操作：打开页面、获取元素、提取文本，整个流程在对话中就能完成。

## Agent-Reach
这个skill解决的是另一个大问题：让AI Agent免费访问各大平台的内容。Twitter/X、Reddit、YouTube、GitHub、B站、小红书，都能通过它来搜索和读取，关键是不需要任何API key。

它背后用的是xreach CLI读Twitter、yt-dlp读视频、Jina Reader读网页，这些都是成熟的开源工具。写文章做调研的时候就靠它，先跑一下 agent-reach doctor 检查哪些渠道可用，然后按需调用。

claude code和openclaw都能用：
```
帮我安装 Agent Reach：
https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md
```