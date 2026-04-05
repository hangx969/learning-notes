
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
- 获取base url： https://api-docs.deepseek.com/zh-cn/
- 获取model id：deepseek-chat

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

## OpenClaw引导配置

```sh
openclaw onboard 
# 需要做成守护进程就加参数 --install-daemon
```

以魔塔免费API为例：
- onboarding mode选quick start
- model选择custom provider
- 填入base url（从魔塔获取的url）
- 填入api key
- 接口协议选OpenAI
- 填入模型ID（也可以从示例代码中找到）：deepseek-ai/DeepSeek-V3.2
- 由于网络问题，先跳过Channel、Skills、Hooks配置（选Skip for now，按空格+回车选中选项）
- hatch your bot选择Open the Web UI
- 引导完成后会自动启动Gateway并且打开浏览器。初次访问会显示unauthorized。
- 配置gateway token：
	- gateway的token也是明文保存在openclaw.json文件下，gateway.token字段下。
	- 填进去，连接，看到状态正常即可。

# Linux安装OpenClaw
## 安装nodejs

```sh
# RPM版
curl -fsSL https://rpm.nodesource.com/setup_24.x | sudo bash -
dnf install -y nodejs
# DEB版
sudo apt install -y nodejs
sudo corepack enable npm

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
apt install -y pip
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
```

## 安装Openclaw

安装编译工具：
```sh
yum install cmake gcc* -y
# ubuntu下直接装gcc*，包太多了放不下
sudo apt install -y cmake gcc g++ make build-essential
```

npm安装OpenClaw：
```sh
npm install -g openclaw@latest
# 指定版本
npm install -g openclaw@v2026.3.2
```

注：2026.03.10，用`npm install -g openclaw@latest` 安装的时候会报错：
````
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.
````
这是一个已知问题，某个依赖包被强制使用ssh连接github地址了，而非https。
github上有issue和PR，PR还没Merge。
- https://github.com/openclaw/openclaw/issues/40684
- https://github.com/openclaw/openclaw/pull/40721
所以暂时用这个命令修复：
```sh
git config --global url."https://github.com/".insteadOf "ssh://git@github.com/"
git config --global url."https://github.com/".insteadOf "git+ssh://git@github.com/"
git config --global url."https://github.com/".insteadOf "git+ssh://git@github.com:"
```

开启工具权限：
```sh
openclaw config set tools.profile "full"
```

## OpenClaw引导配置
```sh
openclaw onboard --install-daemon
```

以deepweek-chat为例
- onboarding mode选quick start
- model选择custom provider
- 填入base url： https://api.deepseek.com/v1
- 填入api key
- 接口协议选OpenAI
- 填入模型ID：deepseek-chat
- 由于网络问题，先跳过Channel、Skills、Hooks配置（选Skip for now，按空格+回车选中选项）
- hatch your bot选择Open the Web UI
- 引导完成后会自动启动Gateway并且打开浏览器，概览中看到状态正常即可。

引导结束后，可以查看openclaw进程：
```sh
netstat -lntp | grep open
```

## 浏览器访问
如果linux是虚拟机安装在windows宿主机上。由于安全问题，openclaw监听的是127.0.0.1，直接用虚拟机IP:18789端口是访问不通的。

如果需要宿主机上的浏览器访问，需要在Windows上z执行一下命令，通过SSH隧道访问：
```sh
ssh -N -L 18789:127.0.0.1:18789 root@<虚拟机-IP>
```
没有返回说明连接成功，然后宿主机通过：127.0.0.1:18789 访问。

初次访问，进去会看到unauthorized报错，需要去openclaw配置文件中拿gateway token：`/root/.openclaw/openclaw.json` 中的 `"gateway"."token"` 字段。
填入概览-网关令牌中，点击连接，看到状态是正常的即可。

# OpenClaw基础使用

- 开启工具权限：（或者在webUI - 代理中打开工具权限）
```sh
openclaw config set tools.profile "full"
```

- 手动开启gateway / 重启gateway：
```sh
openclaw gateway
```

- 启停服务：
```sh
openclaw gateway stop/start
```

- CLI修改配置
```sh
openclaw configure
```

> openclaw的所有配置都是以文件的形式保存在C盘用户家目录中的.openclaw目录下。后面的配置修改都建议修改配置文件或者用命令行修改。

- 初始角色定义：
	- “记住这个：你是xxx，我是xxx，你是我的个人助理”。（记住这个后面的内容会被自动加载到memory中）

- 升级
```sh
npm i -g openclaw@2026.3.11
openclaw doctor
openclaw gateway restart
```

- 开启一段新对话：`/new`
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

## 添加github copilot订阅

GitHub Copilot（包括 Enterprise 版）**不提供独立的 API Key**。它的认证方式是通过 GitHub OAuth 令牌交换实现的。但好消息是，**OpenClaw 内置了对 GitHub Copilot 的原生支持**，会自动处理整个令牌交换和刷新流程。

 1. 登录 GitHub Copilot
在你安装好 OpenClaw 的 Rocky Linux 服务器上执行：

```bash
openclaw models auth login-github-copilot
```

该命令会启动 GitHub 设备授权流程：
- 终端会显示一个 **URL** 和一个 **一次性验证码**
- 在浏览器中打开该 URL，输入验证码，授权 OpenClaw 使用你的 GitHub 账户
- 保持终端打开直到授权完成

2. 设置默认模型

登录成功后，设置你想用的模型：

```bash
# 设置默认模型（根据你的 Enterprise 订阅可用的模型选择）
openclaw models set github-copilot/claude-sonnet-4.6

# 或者使用 GPT 系列
openclaw models set github-copilot/gpt-4.1
```

3. 可选：指定认证配置文件 ID

```bash
openclaw models auth login-github-copilot --profile-id github-copilot:enterprise
```

## 多Agent
可以创建多个Agent，每个Agent绑定的模型、配置等都可以不同。
如果创建了多个Agent，每个Agent建议保存在不同的工作目录。

# 卸载
一行命令即可卸载：
```sh
openclaw uninstall
openclaw uninstall --all --yes --non-interactive
```
但是要注意观察执行命令后的输出结果，有些内容可能不会自动删除。

完全干净卸载：
- Mac / Linux 用户：
```sh
openclaw gateway stop  
openclaw gateway uninstall  
rm -rf "${OPENCLAW_STATE_DIR:-$HOME/.openclaw}"  
npm rm -g openclaw || pnpm remove -g openclaw  
rm -rf /Applications/OpenClaw.app
```

- Windows 用户（在 PowerShell 中执行）：
```sh
openclaw gateway stop  
openclaw gateway uninstall  
schtasks /Delete /F /TN "OpenClaw Gateway"  
Remove-Item -Recurse -Force "$env:USERPROFILE\.openclaw"  
Remove-Item -Force "$env:USERPROFILE\.openclaw\gateway.cmd" -ErrorAction SilentlyContinue  
npm rm -g openclaw  
# 如果你是用 pnpm 安装的，改为执行：pnpm remove -g openclaw
```

