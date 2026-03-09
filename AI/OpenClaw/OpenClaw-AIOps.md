
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
- 配置国内pip源：
```powershell
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
```

## OpenClaw安装