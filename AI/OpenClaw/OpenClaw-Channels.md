# 配置Channel

## 飞书【】
下载app： https://www.feishu.cn/download
参考文档： 
- https://docs.openclaw.ai/zh-CN/channels/feishu
- https://www.feishu.cn/content/article/7613711414611463386

### 自动安装
2026.3.8版本的openclaw已经支持直接配置飞书插件了。可以在线安装或者选择已经下载好的本地插件文件。（openclaw自带飞书插件，不要选择npm install @openclaw/feishu，否则后面会一直报插件重复）

```sh
openclaw channels add
# 选择Channel - Feishu/Lark (飞书)
```

### 手动安装
- 插件： https://github.com/openclaw/openclaw/tree/main/extensions
- git clone 到本地，把feishu目录拷贝到openclaw的安装目录的extension目录下。
- 在extension目录下手动安装：`npm install`
- 重启openclaw：`openclaw restart`

### 配置飞书机器人
按照教程： https://docs.openclaw.ai/zh-CN/channels/feishu#%E7%AC%AC%E4%B8%80%E6%AD%A5%EF%BC%9A%E5%88%9B%E5%BB%BA%E9%A3%9E%E4%B9%A6%E5%BA%94%E7%94%A8
来配置即可。

1. 下载登录飞书
2. 创建企业应用，拿到app secret和app id
3. 按照教程配置权限
4. 按照教程配置机器人
5. 回到openclaw，配置channel，`openclaw configure` ，填入app id和app secret
6. connection mode选Websocket
7. domain选Feishu-China
8. Group chat policy选Open
9. 选Finished
10. DM access policies选No
11. accounts选No
12. Agents选Yes
13. 回到飞书开放平台，按照教程配置事件与回调 - 事件配置 - 订阅方式 - 长连接
14. 添加事件：`im.message.receive_v1`（接收消息）
15. 创建版本 - 发布版本
16. 在飞书对话框中看到提示，点击打开应用，尝试第一次对话。
17. 第一次对话弹出一个pairing命令，去openclaw那边执行一下。

### troubleshooting
#### 代理环境变量导致通信问题
开着代理，设置过http proxy，然后安装的openclaw和飞书插件，结果关掉代理之后，从飞书机器人无法正常与openclaw通信，报错：

```
connect ECONNREFUSED 127.0.0.1:7897'
```

查看openclaw的服务文件，可以看到环境变量配置：

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

# QQ
腾讯出手，专门为 OpenClaw 搞了一个快捷接入通道，几步就能搞定！

- 打开 QQ 机器人 OpenClaw 接入页面，用 QQ 扫码登录： https://q.qq.com/qqbot/openclaw/index.html
- 创建机器人，拿到接入命令，去openclaw运行一下接入即可。