# 介绍

requests 模块是 Python 简单易用的 HTTP 库，主要用于发送 HTTP 请求并接收响应。与原生的 urllib 库相比，requests 提供了更加简洁直观的 API，使得网络请求的处理更加方便。

**核心功能：**

- 发送 HTTP 请求：支持常见的 GET、POST、PUT、DELETE、HEAD、OPTIONS 等请求方法。
- 处理请求参数：支持传递 URL 参数、请求体数据、文件上传等。
- 处理响应：包括响应状态码、响应头、响应内容等。
- 支持会话管理：可以通过会话对象在多次请求之间保持 Cookie 等信息。
- 简化认证：内置基本的 HTTP 认证支持，简化了身份验证的流程。
- 自动处理重定向和压缩：会自动处理 301 重定向和 GZIP 压缩。
- 支持超时和异常处理：允许设置超时并处理网络请求中的常见异常。

**核心方法**：

- `requests.get(url, params=None, **kwargs)`：发送 GET 请求。
- `requests.post(url, data=None, json=None, **kwargs)`：发送 POST 请求。
- `requests.put(url, data=None, **kwargs)`：发送 PUT 请求。
- `requests.delete(url, **kwargs)`：发送 DELETE 请求。
- `requests.head(url, **kwargs)`：发送 HEAD 请求。
- `requests.options(url, **kwargs)`：发送 OPTIONS 请求。

**常用的参数**：

- params：字典格式，用于在 URL 中添加查询参数。
- data：字典、列表或元组，表示要发送的表单数据。
- json：字典格式，表示要发送的 JSON 数据。
- headers：字典格式，指定自定义的请求头。
- timeout：设置请求的超时时间，单位为秒。
