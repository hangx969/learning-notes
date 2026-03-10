
# 绪论
## OpenClaw是什么
OpenClaw是一个由大模型驱动的通用AI Agent平台。前身为Clawbot、Moltbot。

OpenClaw和传统对话性AI不同，不仅能理解自然语言指令，还能主动执行任务，比如操作电脑、管理文件、浏览网页、调用API，甚至操作鼠标键盘。同时可以添加Skills扩展功能使其进化。

## 应用场景
- 智慧办公：PPT生成、Excel处理、邮件处理、简历筛选、会议处理
- IT行业：代码开发、故障处理、业务巡检、跨机操作、AIOps
- 自媒体：素材收集、资讯聚合、视频剪辑、合规检查、内容分发

## 架构分层
- 入口层
	- 消息渠道：微信、钉钉、飞书
	- 客户端：CLI、WebUI、webSocket
	- 移动端：安卓、IOS的App等
- Gateway网关层
	- WebSocket维护
	- 身份认证
	- 会话绑定
	- 消息处理
- 大脑AgentRuntime
	- 上下文组装
	- 模型推理
	- 工具Skills调度
	- 记忆系统
- 原子操作
	- Shell/代码
	- 浏览器自动化
	- 文件操作
	- 接口调用
- 持久化
	- 对话日志
	- MEMORY
	- 向量数据
	- 临时文件
- 响应
	- 响应至入口

## 官网
- https://docs.openclaw.ai/
- https://github.com/openclaw/openclaw
- 安装指南： https://docs.openclaw.ai/zh-CN/install

# 大模型API准备
OpenClaw是需要接入大模型API的，如果选择免费版的大模型API，会面临限速限流问题。收费的会好一些。

## 魔塔API注册使用
由于 openclaw 需要接入模型，可以先临时选择魔塔的免费 API（每日免费调用 2000 次）。

- 首先访问 https://www.modelscope.cn/models
- 注册登录
- 新建一个长期有效的token：个人设置-访问控制-新建访问令牌
- 选择模型库-->支持体验-->推理 API
- 选择一个模型 - 查看代码实例 - api key选择刚创建的长期有效的那个 - 拿到base url和api key

## Deepseek API准备
- https://platform.deepseek.com/ 创建账户
- 创建长期有效的API key，复制保存到其他地方。
- 实名认证并充值（20RMB就够用实验了）

# Windows安装OpenClaw

## Nodejs安装
- 需要>22版本。安装包下载地址： https://nodejs.org/en/download 
- 安装，保持默认配置即可
- 配置国内阿里云npm仓库:
```powershell
npm -v
npm config get registry
npm config set registry https://registry.npmmirror.com/
npm config get registry
```

## Python安装
- 安装包下载地址： https://www.python.org/downloads/windows/
- 配置国内阿里云pip源：
```powershell
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
```

## OpenClaw安装
官网上有一键安装脚本，但是国内网络环境大概率会遇到timeout。所以用我们配置好国内源的npm来安装：
https://docs.openclaw.ai/zh-CN#%E5%BF%AB%E9%80%9F%E5%BC%80%E5%A7%8B

用管理员打开powershell：
```sh
npm install -g openclaw@latest
# 指定版本（看github release上的tag值）
npm install -g openclaw@v2026.3.2
```
由于要安装几百个依赖，所以还是需要等待一段时间。

> 也可以用docker/k8s安装，但是由于openclaw的很多组件是需要数据持久化的，如果没有配置正确存储的话，重启容器/pod，数据就丢失了。

## OpenClaw初始化引导配置

```sh
openclaw onboard 
# 需要做成守护进程就加参数 --install-daemon
```

- onboarding mode选quick start
- model选择custom provider
- 填入base url（从魔塔获取的url）
- 填入api key
- 接口协议选OpenAI
- 填入模型ID（也可以从示例代码中找到）：以deepseek-ai/DeepSeek-V3.2为示例
- 由于网络问题，先跳过Channel、Skills、Hooks配置（选Skip for now，按空格+回车选中选项）
- hatch your bot选择Open the Web UI
- 引导完成后会自动启动Gateway并且打开浏览器，概览中看到状态正常即可。

# Linux安装OpenClaw
## 安装nodejs

```sh
curl -fsSL https://rpm.nodesource.com/setup_24.x | sudo bash -
dnf install -y nodejs
npm -v
node -v

# 配置国内源
npm config get registry
npm config set registry https://registry.npmmirror.com/
npm config get registry
```

## 安装python

Linux自带python，直接配置国内源即可：
```sh
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
```

## 安装Openclaw

安装编译工具：
```sh
yum install cmake gcc* -y
```

npm安装OpenClaw：
```sh
npm install -g openclaw@latest
# 指定版本
npm install -g openclaw@v2026.3.2
```

开启工具权限：
```sh
openclaw config set tools.profile "full"
```

## OpenClaw引导配置
```sh
openclaw onboard --install-daemon
```

引导结束后，可以查看openclaw进程：
```sh
netstat -lntp | grep open
```

由于安全问题，如果需要浏览器访问，需要在Windows上通过SSH隧道访问：
```sh
ssh -N -L 18789:127.0.0.1:18789 root@IP
```
宿主机通过：http://localhost:18789/访问即可。

启停服务：
```sh
openclaw gateway stop/start
```

# OpenClaw基础使用

- 开启工具权限：（或者在webUI - 代理中打开工具权限）
```sh
openclaw config set tools.profile "full"
```

- 手动开启gateway / 重启gateway：
```sh
openclaw gateway
# 浏览器访问127.0.0.1:18789
```

- 配置gateway token
	- 概览中配置gateway token - 连接
	- gateway的token也是明文保存在openclaw.json文件下，gateway字段下。

> openclaw的所有配置都是以文件的形式保存在C盘用户家目录中的.openclaw目录下。后面的配置修改都建议修改配置文件或者用命令行修改。

- 初始角色定义：
	- “记住这个：你是xxx，我是xxx，你是我的个人助理”。（记住这个后面的内容会被自动加载到memory中）

# 添加多供应商多模型
## 手动添加(推荐)
- openclaw的所有配置都是以文件的形式保存在C盘用户家目录中的.openclaw目录下。
- 修改配置文件，添加到 models.providers
- 以deepseek为例，base url，版本等信息都可以在API文档中找到： https://api-docs.deepseek.com/zh-cn/quick_start/pricing
```json
"deepseek": {
    "baseUrl": "https://api.deepseek.com/v1",
    "apiKey": "",
    "api": "openai-completions",
    "models": [
        {
            "id": "deepseek-chat",
            "name": "deepseek-chat",
            "reasoning": false,
            "input": [
                "text"
            ],
            "cost": {
                "input": 0,
                "output": 0,
                "cacheRead": 0,
                "cacheWrite": 0
            },
            "contextWindow": 131072,
            "maxTokens": 32768
        }
    ]
},
```

需要把配置的模型添加到agents.models里面，而且更改智能体默认模型为deepseek模型。格式为provider name/model id：
```json
"agents": {
    "defaults": {
        "model": {
            "primary": "deepseek/deepseek-chat"
        },
        "models": {
            "custom-api-inference-modelscope-cn/deepseek-ai/DeepSeek-V3.2": {
                "alias": "ms-deepseek-v32"
            },
            "custom-api-inference-modelscope-cn/Qwen/Qwen3-235B-A22B-Instruct-2507": {},
            "deepseek/deepseek-chat": {}
        },
```

## 自然语言自动添加
直接让openclaw自己添加模型，输入提示词：

```
帮我新增一个模型，provider为 deepseek，模型名字和ID是 deepseek-reasoner，该模型的 base url是 https://api.deepseek.com/v1，api key是 xxxxx，该模型是openai标准协议的模型，配置时，需要限制最大 token为 32768，上下文窗口为 64k。Openclaw配置文件路径：C:\Users\xxx\.openclaw\openclaw.json
```

# 多Agent
可以创建多个Agent，每个Agent绑定的模型、配置等都可以不同。
如果创建了多个Agent，每个Agent建议保存在不同的工作目录。