---
title: OpenClaw Channel 配置
tags:
  - AI
  - openclaw
  - channel
  - feishu
aliases:
  - OpenClaw渠道
  - OpenClaw飞书
---

# 配置 Channel

## 飞书（自带版）

这里是用的 OpenClaw 自带的飞书插件。

- 下载 app：[https://www.feishu.cn/download](https://www.feishu.cn/download)
- 参考文档：
  - [OpenClaw 飞书文档](https://docs.openclaw.ai/zh-CN/channels/feishu)
  - [飞书内容文章](https://www.feishu.cn/content/article/7613711414611463386)

### 自动安装

2026.3.8 版本的 OpenClaw 已经支持直接配置飞书插件了。可以在线安装或者选择已经下载好的本地插件文件。

> [!warning] 注意
> OpenClaw 自带飞书插件，不要选择 `npm install @openclaw/feishu`，否则后面会一直报插件重复。

```sh
openclaw channels add
# 选择Channel - Feishu/Lark (飞书)
```

### 手动安装

- 插件：[OpenClaw Extensions](https://github.com/openclaw/openclaw/tree/main/extensions)
- `git clone` 到本地，把 `feishu` 目录拷贝到 OpenClaw 的安装目录的 `extension` 目录下
- 在 `extension` 目录下手动安装：`npm install`
- 重启 OpenClaw：`openclaw restart`

### 配置飞书机器人

按照教程：[创建飞书应用](https://docs.openclaw.ai/zh-CN/channels/feishu#%E7%AC%AC%E4%B8%80%E6%AD%A5%EF%BC%9A%E5%88%9B%E5%BB%BA%E9%A3%9E%E4%B9%A6%E5%BA%94%E7%94%A8) 来配置即可。

1. 下载登录飞书
2. 创建企业应用，拿到 App Secret 和 App ID
3. 按照教程配置权限
4. 按照教程配置机器人
5. 回到 OpenClaw，配置 channel：`openclaw configure`，填入 App ID 和 App Secret
6. Connection Mode 选 ==Websocket==
7. Domain 选 ==Feishu-China==
8. Group Chat Policy 选 ==Open==
9. 选 Finished
10. DM Access Policies 选 No
11. Accounts 选 No
12. Agents 选 Yes
13. 回到飞书开放平台，按照教程配置事件与回调 → 事件配置 → 订阅方式 → 长连接
14. 添加事件：`im.message.receive_v1`（接收消息）
15. 创建版本 → 发布版本
16. 在飞书对话框中看到提示，点击打开应用，尝试第一次对话
17. 第一次对话弹出一个 pairing 命令，去 OpenClaw 那边执行一下

### Troubleshooting

#### 代理环境变量导致通信问题

开着代理，设置过 http proxy，然后安装的 OpenClaw 和飞书插件，结果关掉代理之后，从飞书机器人无法正常与 OpenClaw 通信，报错：

```
connect ECONNREFUSED 127.0.0.1:7897'
```

查看 OpenClaw 的服务文件，可以看到环境变量配置：

```yaml
Environment=http_proxy=http://127.0.0.1:7897
Environment=https_proxy=http://127.0.0.1:7897
Environment=all_proxy=socks5://127.0.0.1:7897
```

删掉即可：

```sh
sed -i '/^Environment=http_proxy=/d; /^Environment=https_proxy=/d; /^Environment=all_proxy=/d' ~/.config/systemd/user/openclaw-gateway.service

systemctl --user daemon-reload
openclaw gateway restart
```

---

## 飞书（飞书官方版）

飞书推出了一个官方开发的插件：[飞书官方插件文档](https://bytedance.larkoffice.com/docx/MFK7dDFLFoVlOGxWCv5cTXKmnMh)

一键扫码配置，很方便。

---

## QQ

腾讯出手，专门为 OpenClaw 搞了一个快捷接入通道，几步就能搞定！

- 打开 QQ 机器人 OpenClaw 接入页面，用 QQ 扫码登录：[https://q.qq.com/qqbot/openclaw/index.html](https://q.qq.com/qqbot/openclaw/index.html)
- 创建机器人，拿到接入命令，去 OpenClaw 运行一下接入即可
