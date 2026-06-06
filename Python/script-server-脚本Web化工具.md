---
title: "Script-Server：脚本 Web 化工具"
source: "https://mp.weixin.qq.com/s/WQHdokHdfqAgGdCpN-lLWA"
created: 2026-06-06
tags:
  - python
  - ops-tools
  - automation
---

# Script-Server：脚本 Web 化工具

## 简介

Script-Server 是一个 Python 脚本服务器，将 Shell/Python 脚本包装成 Web 应用。零代码改动，只需 JSON 配置，自动生成参数表单、实时输出、权限控制、审计日志。

项目地址：https://github.com/bugy/script-server

## 解决的痛点

- 非技术人员用命令行容易出错，需要可视化界面
- 脚本零散，缺少统一入口和权限管理
- 手动跑脚本缺少审计日志和执行历史
- 参数校验、输入输出需要重复造轮子

## 安装

### Docker 方式

```bash
docker pull bugy/script-server:latest
docker run -p 5000:5000 -v /path/to/conf:/opt/script-server/conf bugy/script-server
```

### Python 方式

环境要求：Python 3.7+，Tornado 5/6。

## 配置示例

`conf/runners/hello.json`：

```json
{
  "id": "say_hello",
  "title": "打个招呼",
  "script": "scripts/say_hello.sh",
  "parameters": [
    {"name": "name", "title": "你的名字", "type": "text", "default": "Tom"}
  ]
}
```

`scripts/say_hello.sh`：

```bash
#!/usr/bin/env bash
echo "Hello, $1！欢迎使用 Script-Server~"
```

启动后访问 `http://localhost:5000` 即可使用。

## 核心功能

- 支持文本、文件上传、下拉框等多种参数类型
- 实时输出、输入交互、输出文件下载
- 多种认证：LDAP、Google OAuth、htpasswd
- 审计日志、执行历史记录
- 脚本放 `conf/runners/` 目录，后台自动生成 Web 表单

## 优缺点

| 优点 | 缺点 |
|------|------|
| 零改动让脚本秒变 Web 应用 | JSON 配置需要熟悉格式 |
| 多种参数类型支持 | GUI 风格偏简单 |
| 实时输出 + 文件下载 | 老版本有 XSS/CSRF 隐患（1.17+ 已修复） |
| LDAP/OAuth 认证 + 审计日志 | 高并发场景需调优 |
