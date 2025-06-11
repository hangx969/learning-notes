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

**安装**：

`pip3 install requests`

# 发送GET请求requests.get()

get() 方法用于发送 HTTP GET 请求，用于从服务器获取资源。该方法适用于访问公开的网页、API 接口或其他 HTTP 资源。

基本语法：`response = requests.get(url, params=None, **kwargs)`

参数说明：

**url**:

类型: 字符串

描述: 请求的目标地址，是必填项，指定了需要访问的资源位置。

**params**:

类型: 字典（可选）

描述: 发送到服务器的**查询字符串**，通常以键值对的形式表示。请求会自动将这些参数编码并附加到 URL 中，生成类似 `?key=value` 的格式。

**kwargs**:

类型: 可变关键字参数（可选）

描述: 其他可选参数，包括但不限于：

- `headers`: 自定义请求头，可以模拟不同的客户端（如浏览器、移动设备等）

- `timeout`: 请求超时时间，单位为秒，用于设置请求的最大等待时间。

- `cookies`: 用于发送 cookies 到服务器

## 国内公开免费测试地址

以下是一些国内可以免费使用的测试 API 地址，适合用来测试 HTTP 请求：
1. httpbin.org（镜像）
  - 地址: http://httpbin.org/anything 或 https://httpbin.org/anything
  - 用途: 用于测试各种 HTTP 请求方法（GET、POST、PUT、DELETE、HEAD、OPTIONS 等）
2. JSONPlaceholder
  - 地址: https://jsonplaceholder.typicode.com/posts
  - 用途: 提供 RESTful API 接口，用于模拟 CRUD 操作。
3. 接口调试工具（Postman）
  - 地址: https://postman-echo.com/get
  - 用途: 适合做 GET 请求，返回请求的详细信息。这些 API 地址都是可以公开访问的，你可以使用它们进行各种 HTTP 请求的测试。

## 示例

~~~python
import requests

# 定义一个url来查询，/s是百度搜索的路径部分用于查询
url = 'https://www.baidu.com/s'

# 查询参数
params = {
    'wd': 'python'
}

# 请求头
headers = {
    'User-Agent': 'Mozilla/5.0'
}

# 发送get请求
response = requests.get(url, params=params, headers=headers)

if response.status_code == 200:
    print("Response:")
    print(response.text)
else:
    print(f'Request failed with status code {response.status_code}')
~~~

# 发送POST请求requests.post()

post() 方法用于向服务器发送 HTTP POST 请求，通常用于提交数据，比如表单数据、JSON数据或文件。该方法会返回一个响应对象，包含服务器的响应信息，如状态码、响应内容、头部信息等。

语法：`response = requests.post(url, data=None, json=None, **kwargs)`

- url：请求的目标地址（必填）。
- data：可选参数，用于提交的表单数据。可以是字典、字节对象或文件等数据格式，常用于表单提交。
- json：可选参数，发送 JSON 格式的数据。传入字典，自动将字典序列化为 JSON 字符串并发送到服务器。
- **kwargs：其他可选参数，例如：
  - headers：指定请求的头部信息，如 Content-Type。
  - timeout：请求超时时间，单位为秒。
  - cookies：指定要发送的 cookies 信息。

格式：

~~~python
response = requests.post(
'https://example.com/api',
    json = {'key':'value'},
    headers={'Content-Type':'application/json'}
)
~~~

## 示例

~~~python
import requests

response = requests.post(
    'https://httpbin.org/post',
    json = {'key': 'value'},
    headers={'Content-Type': 'application.json'}
)

# 获取状态码
print(response.status_code)
# 获取返回内容，用json格式显示
print(response.json())
~~~

# cookie
