---
title: "Script-Server：一个Python脚本服务器，帮你把脚本包成一个网页应用，扔到服务器上，任何有浏览器的人都可以看到界面"
source: "https://mp.weixin.qq.com/s/WQHdokHdfqAgGdCpN-lLWA"
author:
  - "[[小白这样学Python]]"
published:
created: 2026-06-05
description: "什么是 Script-Server？你有一堆 Shell 脚本、Python 脚本，想分享给同事或者产品小白也能随手用？"
tags:
  - "clippings"
---
小白这样学Python *2026年5月24日 19:48*

什么是 Script-Server？  
你有一堆 Shell 脚本、Python 脚本，想分享给同事或者产品小白也能随手用？Script-Server 就是干这个的。它帮你把脚本包成一个网页应用，扔到服务器上，任何有浏览器的人都可以看到界面，填几个参数，点“运行”就能出结果。零脚本改动，只要在后台配置一下，自动生成参数校验、实时输出、权限控制，界面还挺好看。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/VIupIhU5lf4ePW9PunSrsSj24otFPF0KUWWb6ib38hCKqTwmu5trlvRUDKibQRRgC56rAXZMzzUonmQVKYL4lBmQ/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

**它解决了哪些痛点？**

- • 运维小白用命令行太难，老报错，搞得你天天线上喊救命。
- • 脚本零散，没人敢随便用，临时需求还要手动跑。
- • 要搞权限、审计、输出日志，就得一堆额外工具；结果运维又要写不少代码。
- • 脚本改动多了，参数校验、输入输出都得重复造轮子……  
	用 Script-Server，你只管配置 JSON，把脚本放 `conf/runners/` 目录，后台自动给你生成表单、执行、日志、审计、下载输出文件，一条命令搞定。

**安装与简单示例**

1. 1\. 环境要求：Python 3.7+，Tornado 5/6。
2. 或者 Docker 镜像：
	```
	docker pull bugy/script-server:latest
	docker run -p 5000:5000 -v /path/to/conf:/opt/script-server/conf bugy/script-server
	```
3. 3\. 配个脚本：在 `conf/runners/hello.json`
	```
	{
	  "id":"say_hello",
	  "title":"打个招呼",
	  "script":"scripts/say_hello.sh",
	  "parameters":[
	      {"name":"name","title":"你的名字","type":"text","default":"Tom"}
	  ]
	}
	```
4. `scripts/say_hello.sh`
	```
	#!/usr/bin/env bash
	echo "Hello, $1！欢迎使用 Script-Server~"
	```

启动后，打开 `http://localhost:5000` ，界面就出来啦！

**优缺点一览**

| 优点 | 缺点 |
| --- | --- |
| 0 改动，让脚本秒变 Web 应用 | 配置 JSON 有时稍啰嗦，需要熟悉格式 |
| 支持文本、文件上传、下拉框等多种参数 | GUI 风格偏简单，不要抱太高前端期待 |
| 实时输出、输入交互、输出文件下载 | XSS/CSRF 在老版本有隐患，1.17+ 才修复 |
| 多种认证：LDAP、Google OAuth、htpasswd | 高并发场景下性能瓶颈，重度使用得调优 |
| 审计日志、执行历史一目了然 | 部分高级功能（光标定位、格式化）需要额外模块 |

**总结**  
总体来说，Script-Server 就像给运维脚本套了个小外壳，门槛低、配置灵活、上手快，适合团队集中管理各种自动化脚本。如果你的运维同事不太会命令行、或者想给业务同学用接口，又不想开发一个完整的 Web 服务，完全可以试试它。唯一要注意的是，多人协作和高并发下，得做点性能和安全的加固；还有，想要前端炫酷？那就只能自己改源码或者在外面套一层 UI。

项目地址：https/github.com/bugy/script-server

继续滑动看下一个

小白这样学Python

向上滑动看下一个