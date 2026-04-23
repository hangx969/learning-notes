---
title: "K8S工具推荐：告别复杂认证！Kubernetes登录神器kubelogin指南"
source: "https://mp.weixin.qq.com/s?__biz=MzkxNzAyMzA3Nw==&mid=2247485698&idx=1&sn=47443ce3322a407525cd6ccdffbffb29&scene=21&poc_token=HN826mmj2PP3QFS3H1TNga-iLG8LbUSQD7GtcSv6"
author:
  - "[[海笑]]"
published:
created: 2026-04-23
description:
tags:
  - "clippings"
---


作为Kubernetes开发者，你是否还在为集群认证头疼？今天给大家介绍一款开源神器—— **kubelogin** ，让你像登录网站一样轻松访问K8s集群！



![Diagram of the credential plugin](https://mmbiz.qpic.cn/mmbiz_svg/uHwLXtyH4IWv32UlgRwr21ibraZLujAicpYFYNSsX8nUUrWcVmmunT8oUCxgBd0twApwFkzVmWJF17ARticUWujC5mPSE8cicH2a/640?wx_fmt=svg&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

Diagram of the credential plugin

### 🔑 什么是kubelogin？

kubelogin是一个基于OpenID Connect（OIDC）的kubectl插件，它实现了：

- • 浏览器一键登录（支持Google/Azure AD等）
- • 自动令牌刷新（再也不用担心token过期）
- • 多平台密钥存储（支持系统钥匙串）
- • 无缝集成kubectl工作流

### 🚀 三大核心优势

1. 1.**极简登录体验**  
	只需运行 `kubectl get pods` ，自动弹出浏览器完成OIDC认证，告别复杂的kubeconfig配置！
2. **企业级安全**
	```
	id: security
	name: 安全机制
	type: markdown
	content: |-
	  - 使用短期ID Token（默认1小时有效期）
	  - 支持Refresh Token自动续期
	  - 令牌加密存储（支持系统钥匙串）
	  - 遵循OAuth 2.0 Device Authorization Grant规范
	```
3. 3.**跨平台支持**
- • 🍎 macOS： `brew install kubelogin`
	- • 🪟 Windows： `choco install kubelogin`

### 📝 配置示例

```
id: kubeconfig
name: kubeconfig配置
type: yaml
content: |-
  users:
  - name: oidc
    user:
      exec:
        apiVersion: client.authentication.k8s.io/v1
        command: kubectl
        args:
          - oidc-login
          - get-token
          - --oidc-issuer-url=ISSUER_URL
          - --oidc-client-id=YOUR_CLIENT_ID
```

### 🛠️ 高级技巧

- • **日志调试** ：添加 `-v1` 参数查看详细日志

### 💡 适用场景

- • 需要SSO集成的企业环境
- • 多团队共享集群的场景
- • 需要审计的合规性要求
- • 开发测试环境的快速切换

目前该项目已在GitHub获得 **1.9k Stars** ，被多家云原生企业采用。立即访问项目主页体验：https://github.com/int128/kubelogin

---

**为什么选择kubelogin？**  
传统kubeconfig存在密钥泄露风险，而kubelogin通过OIDC协议实现：  
\[ \\text{安全性} \\propto \\frac{\\text{短期令牌} + \\text{自动刷新}}{\\text{长期静态凭证}} \]

无论是个人开发者还是企业团队，kubelogin都能显著提升Kubernetes认证的安全性和易用性。赶紧升级你的kubectl工作流吧！

[加入知识星球，共同探索云原生学习之旅！](http://mp.weixin.qq.com/s?__biz=MzkxNzAyMzA3Nw==&mid=2247485016&idx=1&sn=f97eb3faad3330fd169d687fd08be53c&chksm=c147b652f6303f44718c9b6fa402033e9f7400bc08e0df64cb3c486fa8881e7ba74f0a7a1241&scene=21#wechat_redirect)

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/Lcribm9SHtlLymvGIoIYY6oCVsx3bqduLGXbJdvvSO6TcO3qC8OKKBkTyTwjV73PuOf4SgyNSPvDVNbeWsHrZ8A/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=1)

更多云架构、K8S学习资料以及SRE学习手册，加入星球免费领取哦！

K8S工具 · 目录

继续滑动看下一个

云原生SRE

向上滑动看下一个