---
title: Postman
tags:
  - azure/tools
  - azure/API
  - azure/authentication
aliases:
  - Postman API Client
date: 2026-04-16
---

# Postman

> [!summary] 使用 Postman 发送 HTTP 请求，获取 Azure ==access token== 进行 API 调试。

---

## 用途

- 发送 HTTP 请求
- 主要作用：在 ==AAD== 中用 / 发 ==ARM== 请求，这两套 access token 是不一样的。

---

## AAD Token

> [!info] 在 AAD 中使用时，作用域 scope 如下：

![image-20231030170702907](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310301707977.png)

---

## ARM Token

> [!important] ARM 请求需要不同的 Bearer Token
> - Query ARM 资源，也要拿一个 ==Bearer Token==，是和 AAD 不一样的 token。只要 token 里面有 ==RBAC 的权限==就行。
> - Portal 上可以点到非 AAD 界面的地方，从 ==F12== 里面拿到 Bearer Token。
