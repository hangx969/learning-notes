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

# 国内公开免费测试地址

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

# requests模块主要功能

## 发送GET请求requests.get()

get() 方法用于发送 HTTP GET 请求，用于从服务器获取资源。该方法适用于访问公开的网页、API 接口或其他 HTTP 资源。

基本语法：`response = requests.get(url, params=None, **kwargs)`

参数说明：

- **url**:
  - 类型: 字符串
  - 描述: 请求的目标地址，是必填项，指定了需要访问的资源位置。

- **params**:

  - 类型: 字典（可选）


  - 描述: 发送到服务器的**查询字符串**，通常以键值对的形式表示。请求会自动将这些参数编码并附加到 URL 中，生成类似 `?key=value` 的格式。


- **kwargs**:

  - 类型: 可变关键字参数（可选）


  - 描述: 其他可选参数，包括但不限于：

    - `headers`: 自定义请求头，可以模拟不同的客户端（如浏览器、移动设备等）


    - `timeout`: 请求超时时间，单位为秒，用于设置请求的最大等待时间。


    - `cookies`: 用于发送 cookies 到服务器


返回值response是一个对象:

- `response.status_code`获取状态码
- `response.text`获取文本格式返回内容
- `response.json()`获取返回文本的json格式内容

### 示例

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

## 发送POST请求requests.post()

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

### 示例

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

## 发送PUT请求requests.put()

put() 方法用于发送 HTTP PUT 请求，通常用于更新服务器上的资源。

语法：`response = requests.put(url, data=None, **kwargs)`

参数：

1. url: (必填)

  目标资源的 URL 地址，表示你希望更新的服务器资源的路径。

2. data: (可选)

  发送到服务器的更新数据，通常是**字典格式**的内容。该数据会在请求的 body 中传输，用于替换目标资源的当前数据。

3. **kwargs: (可选)

  其他可选参数，类似于请求头（headers）、超时时间（timeout）、认证信息（auth）等。

### 示例

~~~python
import requests

response = requests.put(
    'https://httpbin.org/put',
    json={'name':'new_name'} # 这里传入要修改的参数，例如把name修改成new_name
)

if response.status_code == 200:
    print("Update successfully.")
    print(response.json())
else:
    print(f"Update failed: {response.status_code}")
~~~

## 发送DELETE请求requests.delete()

delete() 方法在 requests 库中用于发送 HTTP DELETE 请求，以删除服务器上的特定资源。在 RESTful API 中，DELETE 方法被用于删除指定的资源。

语法：`response = requests.delete(url, **kwargs)`

参数：

1. url: (必填)

  目标资源的 URL 地址，指向你希望删除的服务器资源。

2. **kwargs: (可选)

  其他可选参数，可以包括请求头（headers）、超时时间（timeout）、认证信息（auth）等。

响应状态码: `response.status_code`：用于检查服务器返回的状态码。

- **204**：表示删除操作成功，服务器没有返回任何内容。
- 404：表示尝试删除的资源不存在。s
- 其他状态码：可能表示请求失败，需进一步处理。

### 示例

~~~python
import requests

response = requests.delete(
    'https://example.com/delete' # 没用那个httpbin的免费接口，因为不支持delete这个方法
)

if response.status_code == 204:
    print("Update successfully.")
elif response.status_code == 404:
    print("Resource not found.")
else:
    print(f"Update failed: {response.status_code}")
~~~

## 发送HEAD请求requests.head()

head() 方法在 requests 库中用于发送 HTTP HEAD 请求，功能类似于 GET 请求，但**只请求响应头而不下载响应体**。该方法通常用于获取关于特定资源的信息，例如检查资源是否存在、获取内容类型、获取缓存信息等，而不需要下载整个内容。

用途:

- 检查资源存在性：可以通过检查返回的状态码（如 200 或 404）来确定资源是否存在。

- 获取资源信息：获取有关资源的元数据而不下载实际内容，适用于了解响应的内容类型和大小等信息。

语法：`response = requests.head(url, **kwargs)`

参数：

1. url: (必填)

  请求的目标地址，指向你希望获取响应头的资源。

2. **kwargs: (可选)

  其他可选参数，例如请求头（headers）、超时时间（timeout）、认证信息（auth）等。

响应头信息可能包括：

- `Content-Type`：资源的内容类型（如 text/html）。
- `Content-Length`：响应体的长度（字节数），虽然 HEAD 请求不会返回响应体，但可以获取该信息。
- `Last-Modified`：资源最后修改的时间。
- `Cache-Control`：缓存相关的指令。

状态码：与 GET 请求类似，HEAD 请求也返回状态码，常见状态码包括：

- 200：请求成功，资源存在。
- 404：请求的资源不存在。
- 301/302：资源已被移动，返回重定向信息。

效率：由于不下载响应体，HEAD 请求比 GET 请求更高效，适用于需要快速检查资源信息的场景。

### 示例

~~~python
import requests

response = requests.head(
    'https://httpbin.org/headers'
)
print(response.headers)
# 返回 {'Date': 'Wed, 11 Jun 2025 12:30:40 GMT', 'Content-Type': 'application/json', 'Content-Length': '225', 'Connection': 'keep-alive', 'Server': 'gunicorn/19.9.0', 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Credentials': 'true'}
~~~

## 发送OPTIONS请求requests.options()

options() 方法在 requests 库中用于发送 HTTP OPTIONS 请求，目的是查看服务器支持的请求方法。通过使用该方法，可以获取到服务器允许的 HTTP 方法列表，这对于了解 API 的功能和限制非常有用。

语法：`response = requests.options(url, **kwargs)`

参数：

1. url: (必填)

  请求的目标地址，指向你希望查询支持请求方法的资源。

2. **kwargs: (可选)

  其他可选参数，例如请求头（headers）、超时时间（timeout）、认证信息（auth）等。

响应：

- 请求后返回的 Response 对象，其中包含了服务器返回的信息。可以通过访问 `response.headers` 获取响应头。

用途:

- API 调试：在开发或调试阶段，可以通过 OPTIONS 请求了解服务器的功能。
- CORS 处理：在跨域资源共享（CORS）中，OPTIONS 请求用于检查特定资源的访问权限。

### 示例

~~~python
import requests

response = requests.options(
    'https://httpbin.org/anything'
)
print(response.headers)
# 返回的字典中的‘Allow’这个KEY表示支持的方法
print(response.headers['Allow'])
~~~

# requests模块其他功能

## 超时设置

使用 timeout 参数可以设置请求的最大等待时间，以防止请求无限期挂起。超过此时间就会与抛出Timeout异常。

~~~python
import requests
try:
    url = 'https://jsonplaceholder.typicode.com/posts'
    response = requests.get(url, timeout=5)
    print(f"Request success: {response.status_code}")
except requests.Timeout as e:
    print(f"Error: {e}")
~~~

## 身份验证

requests 支持基本的 HTTP 身份验证，可以通过 auth 参数提供用户名和密码。提供 (username, password) 元组进行基本身份验证。

~~~python
import requests

url = 'https://httpbin.org/basic-auth/user/pass' # 这里传进去的user和pass就是用户名密码
# url = 'https://httpbin.org/basic-auth/user/pass1' 就会报401
response = requests.get(url, auth=('user', 'pass')) # 在这里匹配上面的user,pass
if response.status_code == 200:
    print(f"Request success: {response.status_code}")
else:
    print(f"Request failed: {response.status_code}")
~~~

## 文件上传

可以使用 files 参数进行文件上传。files: 上传的文件字典，键为表单字段名，值为文件对象。

~~~python
import requests

# b是以二进制模式读取文件内容。处理非文本文件时可以避免字符编码问题
with open('config.json','rb') as f:
    files = {'file': f}
    url = 'https://httpbin.org/post'
    response = requests.post(url, files=files) # 这个要写到with里面，确保文件对象没被关闭。

if response.status_code == 200:
    print(f"Request success: {response.status_code}")
else:
    print(f"Request failed: {response.status_code}")
~~~

## cookie处理

cookie 是指存储在用户浏览器中的一小段数据，它用于记录和保存用户的状态信息。服务器通过 cookie 可以在用户访问网站的过程中，保持用户会话信息，或用于跟踪用户的访问行为。

cookie 的常见用途：

1. 会话管理：用于记录用户的登录状态、购物车信息等，当用户再次访问时，可以保持用户的登录状态或其他信息。
2. 个性化设置：网站可以通过 cookie 保存用户的偏好设置，如语言、主题、显示风格等。
3. 追踪与分析：广告商或分析工具可以通过 cookie 追踪用户的浏览行为，了解用户的喜好，以提供定制化广告或优化网站体验。

cookie 的组成：

1. 键值对：每个 cookie 都是一个键值对，例如 session_id=abc123。
2. 有效期：cookie 可以设置有效期，决定它会在浏览器中存储多长时间。如果不设置有效期，cookie 会在浏览器关闭时删除，称为**会话 cookie**。
3. 域和路径：cookie 只会对特定的域名和路径生效。例如，example.com 设置的 cookie 只能被 example.com 使用。
4. 安全性设置：cookie 可以设置为仅在 HTTPS 协议下发送（Secure），或者只有在 HTTP 请求中发送，避免 JavaScript 访问（HttpOnly）。

~~~python
import requests

# 定义cookie，是一个字典包含多个键值对
cookies = {'session_id': 'abc123', 'user': 'bob'}
# post可以添加爱cookie参数
response = requests.post(
    'https://httpbin.org/post',
    cookies= cookies
)
print(response.text) # 返回值中带着cookie信息
~~~

## 重定向与历史

当你发送一个 HTTP 请求到服务器时，服务器可能会返回一个重定向状态码，比如 301 或 302。这意味着请求的资源已经被移动到一个新的 URL。

举个例子：你请求的 URL 是 A（比如 http://example.com/page1），服务器回应一个状态码 302，并告诉你新的 URL 是 B（比如http://example.com/page2）

默认行为：requests 模块的默认行为是自动处理这些重定向。当你发送请求时，如果服务器返回了重定向状态码，requests 会自动向新的 URL 发送请求，直到最终返回目标资源的内容。

禁用重定向： 如果你希望手动处理重定向，可以通过设置 allow_redirects 参数为 False 来禁用自动重定向。这意味着如果请求返回了重定向状态码，requests 不会自动跟随，而是直接返回重定向响应。

~~~python
import requests

url = 'https://httpbin.org/redirect/1'
# 禁用自动重定向
response = requests.get(url, allow_redirects=False)
print(f"Status code: {response.status_code}.") # 返回302
print(f"Redirect URL: {response.headers.get('Location')}") # 获取重定向链接
print(response.content) # 获取的内容是原本的url的内容，没有自动重定向到新url

# 默认开启自动重定向
response = requests.get(url)
print(f"Status code: {response.status_code}.") # 返回200
print(f"Redirect URL: {response.headers.get('Location')}") # 返回None
print(response.content) # 直接重定向到了新url
~~~

