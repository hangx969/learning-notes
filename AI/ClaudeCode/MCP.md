# 常用MCP
## context7
场景: 查最新框架文档(Next.js 15、React 19)、API参数和用法确认、库的最佳实践和陷阱、版本迁移指南。

https://context7.com/ 用个人github账号登录

vscode扩展：
在扩展界面搜 @mcp context7，选择安装。配置文件json中添加API Key：

```json
	"servers": {
		"io.github.upstash/context7": {
			"type": "stdio",
			"command": "npx",
			"args": [
				"@upstash/context7-mcp@1.0.30"
			],
			"env": {
				"CONTEXT7_API_KEY": ""
			},
			"gallery": "",
			"version": "1.0.30"
		}
	}
```

claude code：

```sh
claude mcp add context7 -- npx -y @upstash/context7-mcp --api-key ""
```

## atlassian
用docker方式安装。
安装完成之后，在家目录配置文件中添加进去docker命令和token，启动colima就能自动连接mcp。

```json
  "mcpServers": {
    "atlassian": {
      "type": "stdio",
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "JIRA_URL",
        "-e",
        "JIRA_USERNAME",
        "-e",
        "JIRA_PERSONAL_TOKEN",
        "-e",
        "CONFLUENCE_URL",
        "-e",
        "CONFLUENCE_USERNAME",
        "-e",
        "CONFLUENCE_PERSONAL_TOKEN",
        "ghcr.io/sooperset/mcp-atlassian:latest"
      ],
      "env": {
        "JIRA_URL": "",
        "JIRA_USERNAME": "",
        "JIRA_PERSONAL_TOKEN": "",
        "CONFLUENCE_URL": "",
        "CONFLUENCE_USERNAME": "",
        "CONFLUENCE_PERSONAL_TOKEN": ""
      }
    }
  },
```

## bitbucket
```json
    "bitbucket": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "-y",
        "@zhanglc77/bitbucket-mcp-server"
      ],
      "env": {
        "BITBUCKET_BASE_URL": "",
        "BITBUCKET_USERNAME": "",
        "BITBUCKET_TOKEN": ""
      }
    }
```

## sequential-thinking
深度思考引擎
安装：

```sh
claude mcp add mcp-sequentialthinking-tools -- npx -y mcp-sequentialthinking-tools
```

场景: 复杂技术选型(微服务 vs 单体、数据库选型)、架构设计决策(分层、模块边界、扩展性)、疑难bug根因分析(多因素交叉、隐蔽逻辑)、性能优化策略规划。

实战案例: "分析为什么我们的订单服务在高峰期会超时,考虑数据库、缓存、网络、并发锁、GC等所有可能因素"

效果: 会给出完整的推理链:假设→验证→排除→聚焦→验证→结论,而不是直接猜一个答案。

## memory
长期记忆
安装：
claude mcp add memory -- npx -y @modelcontextprotocol/server-memory

场景: 记住项目约定(命名规范、错误码、配置路径)、记住团队踩过的坑(某个库的bug、某个配置的坑)、记住重要决策(为什么选这个方案、权衡了什么)。

实战案例:
```
你:"记住:我们的错误码统一用E开头+4位数字,数据库表名用snake_case,Redis key用冒号分隔"
(一周后)你:"帮我设计一个用户登录失败的错误码"Claude自动调用记忆:"根据你们的规范,应该是E1001这样的格式..."
```

对Claude说:
```markdown
"用memory(MCP)记住我们团队的规范:  
  
代码规范:  
- 用ESLint + Prettier  
- 命名用驼峰(变量)和帕斯卡(组件)  
  
Git规范:  
- commit格式:feat/fix/docs: 描述  
- PR必须关联issue  
  
技术栈:  
- 前端:React 18 + TypeScript + Vite  
- 后端:Node.js + Express + PostgreSQL  
"
```
验证: 下次问问题时,看Claude是否会自动调用这些规范。

## playwright
浏览器自动化

```
claude mcp add playwright -- npx -y @executeautomation/playwright-mcp-server
```

场景: 竞品监控、批量截图、自动化测试、数据抓取
案例: "打开这5个竞品官网,截图首页和定价页,保存到./analysis/"

## filesystem 
本地文件操作

claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem /path/to/project

场景: 读写配置、批量处理文件、项目初始化脚本
注意: 指定允许访问的路径,避免权限过大。

## github
GitHub操作（需要官网key）
需要设置GITHUB_TOKEN环境变量

```sh
export GITHUB_PERSONAL_ACCESS_TOKEN="your_token_here"
claude mcp add github -- npx -y @modelcontextprotocol/server-github
```

## exa
智能搜索（需要官网key）: 

github: https://github.com/exa-labs/exa-mcp-server
exa api key: https://dashboard.exa.ai/home

```sh
claude mcp add exa -e EXA_API_KEY="" -- npx -y exa-mcp-server
```

场景: 需要搜索最新信息、技术博客、开源项目时，比普通搜索引擎更精准
优势：
- **语义理解更强（Neural Search）：**
    - 你可以用自然语言描述你想要的内容（例如：“找一篇关于Transformer架构的通俗易懂的教程”），它能理解“通俗易懂”和“教程”的含义，而不是只搜这两个词。
- **返回结构化数据（Clean Data）：**
    - 传统搜索引擎返回的是充满了广告、SEO 废话和复杂 HTML 的网页。
    - Exa 会清洗内容，直接返回**干净的文本**或**结构化数据**，这大大减少了 AI 处理杂乱信息的负担，减少了“幻觉”。
- **强大的过滤功能：**
    - 它允许你按**域名**（如只搜 github.com）、**日期**、**内容类型**（如 PDF、代码）进行精确过滤。
- **不仅是搜索，还能“内容相似推荐”：**
    - 你可以给它一个链接，让它找出“与这个网页内容相似的其他网页”，这对于做调研非常有用。

## deepwiki
深度文档聚合

```
claude mcp add deepwiki -- npx -y mcp-deepwiki
```

场景: 聚合某个库的完整文档站点,比context7更全面但速度慢一些

## 更多MCP
官方列表:  https://github.com/modelcontextprotocol/servers
社区精选: https://github.com/wong2/awesome-mcp-servers
(500+服务器持续更新,包括Notion、Slack、Jira、数据库等各种集成)

## 配置文件一键添加mcp

```json
{  
  "mcpServers": {  
  "mcpServers": {
    "atlassian": {
      "type": "stdio",
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "JIRA_URL",
        "-e",
        "JIRA_USERNAME",
        "-e",
        "JIRA_PERSONAL_TOKEN",
        "-e",
        "CONFLUENCE_URL",
        "-e",
        "CONFLUENCE_USERNAME",
        "-e",
        "CONFLUENCE_PERSONAL_TOKEN",
        "ghcr.io/sooperset/mcp-atlassian:latest"
      ],
      "env": {
        "JIRA_URL": "",
        "JIRA_USERNAME": "",
        "JIRA_PERSONAL_TOKEN": "",
        "CONFLUENCE_URL": "",
        "CONFLUENCE_USERNAME": "",
        "CONFLUENCE_PERSONAL_TOKEN": ""
      }
    },
    "bitbucket": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "-y",
        "@zhanglc77/bitbucket-mcp-server"
      ],
      "env": {
        "BITBUCKET_BASE_URL": "",
        "BITBUCKET_USERNAME": "",
        "BITBUCKET_TOKEN": ""
      }
    },
    "exa": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "-y",
        "exa-mcp-server"
      ],
      "env": {
        "EXA_API_KEY": "xxx"
      }
    },
    "sequential-thinking": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "-y",
        "mcp-sequential-thinking"
      ]
    },
    "context7": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "-y",
        "@upstash/context7-mcp",
        "--api-key",
        "xxx"
      ]
    },
    "memory": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-memory"
      ]
    },
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest"
      ]
    }
  },
    "filesystem": {  
      "command": "npx",  
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users"]  
    },  
    "github": {  
      "command": "npx",  
      "args": ["-y", "@modelcontextprotocol/server-github"],  
      "env": {  
        "GITHUB_PERSONAL_ACCESS_TOKEN": ""  
      }  
    }  
  }  
}
```

# 常用应用组合
日常开发: filesystem + github + memory
深度工作: sequential-thinking + context7 + memory
自动化任务: playwright + filesystem
学习新技术: context7 + deepwiki + exa (或 brave-search)

#### 典型使用场景
场景1: 深度思考
"用sequential-thinking分析:微服务 vs 单体架构,哪个更适合我们20人团队?"
(会给出完整推理过程,考虑团队规模、技术债、维护成本等多个维度。)

场景2: 查最新文档
"用context7查React 19的Server Components最新用法。"
(直接返回官方文档的相关章节和代码示例,比搜索引擎精准。)

场景3: 长期记忆
"记住:我们的数据库是PostgreSQL 15,表命名用snake_case,查询超时设置30秒。"
(下次问数据库相关问题,会自动调用这些记忆。)

场景4: 浏览器自动化
"用playwright打开5个竞品官网,截图首页,保存到./screenshots/"
(自动完成浏览器操作,省去重复手动点击。)