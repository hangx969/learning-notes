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


