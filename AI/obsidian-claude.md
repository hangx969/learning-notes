知识库类软件
第一类，语雀、印象笔记这种。 能整理、能记录、能协作，该有的都有。但问题是，没有 AI。你存进去 100 篇笔记，想找某个东西的时候，还是得靠自己记忆和关键词搜索。知识存进去就"死"了，不会自己生长，也不能帮你产出新东西。第二类，腾讯 IMA、秘塔 AI 搜索这种。 有知识库，也有 AI，能上传文档做问答。但它更像一个内容聚合社区，产出形式比较受限——主要就是"你问我答"，想用它来做深度的知识管理和内容生产，够呛。第三类，元宝、豆包、Kimi 这种。 AI 能力确实强，写东西、总结、翻译都不在话下。但它们没有本地知识库的概念。每次用都得重新上传文件或者粘贴文字，上一次的对话上下文也留不住。知识没法真正沉淀下来。要么没脑子，要么没记忆，要么有脑子有记忆但不是你的。然后我就翻到了一个东西，叫 Obsidian。说实话，它不是新产品。在海外已经有 150 万月活用户了，开发者、研究者、写作者用得特别多。而且这家公司很有意思，完全没有接受风投，全靠用户付费活着，年收入大概 2500 万美元，续费率 90% 以上。它的核心逻辑也很简单——所有笔记就是你电脑上的 .md 文本文件，本地存储，不依赖任何云服务。你的数据从头到尾都在自己手里。笔记之间可以用双向链接互相关联，时间长了会形成一张知识网络。Obsidian 有个 Graph View，能把你所有笔记的关联关系可视化出来，哪些知识是孤立的、哪些是高频被引用的，一目了然。

但之前 Obsidian 有个问题——配置太复杂了。要装插件、要配同步、要学 Markdown 语法、要研究各种方法论（什么 Zettelkasten、PARA、MOC），光是折腾"怎么用"就能把人劝退。

但现在不一样了。Claude Code 的生态起来之后，Obsidian 的使用门槛大幅降低了。 你不需要懂那些方法论，Claude Code 替你搞定。具体来说，现在有三个关键工具把 Obsidian 和 AI 打通了：

# 1. claudian插件
这个插件直接把 Claude Code 嵌进了 Obsidian 的侧边栏。你不用再终端和笔记软件之间来回切换——打开 Obsidian，右边就是 AI 对话窗口，选中一段笔记就能让 AI 帮你总结、扩写、找关联，整个过程不离开编辑器。
claude插件； https://github.com/YishenTu/claudian
- 在release中下载main.js，manifest.json，styles.css，放到.obsidian/plugin/claudian/里面。
- 重启obsidian就能在插件页面找到claudian，设置里面配置claude code相关的环境变量。
- 侧边栏打开claudian就可以用了。

# 2. obsidian skills
skills： https://github.com/kepano/obsidian-skills

- 下载skills，放到 vault 的 .claude/ 目录下，Claude Code 就能理解 Obsidian 的格式——双向链接、标签、属性、嵌入，全都认得。

# 3. obsidian local api和claude mcp
GitHub 上的 mcp-obsidian 项目。配好之后，Claude Code 可以直接搜索、读取、创建、修改你的笔记。不用你手动复制粘贴，AI 直接操作你的知识库。

- 依赖local api： https://github.com/coddingtonbear/obsidian-local-rest-api
	- 插件市场直接搜Local REST API，下载并开启
	- 拿到api key，host，port即可
- https://github.com/MarkusPfundstein/mcp-obsidian

mcp配置，放到vault目录或者claude全局配置都可以
```json
{
  "mcpServers": {
    "mcp-obsidian": {
      "command": "uvx",
      "args": [
        "mcp-obsidian"
      ],
      "env": {
        "OBSIDIAN_API_KEY": "你的_API_KEY",
        "OBSIDIAN_HOST": "127.0.0.1",
        "OBSIDIAN_PORT": "27124",
        "OBSIDIAN_PROTOCOL": "https"
      }
    }
  }
}
```

