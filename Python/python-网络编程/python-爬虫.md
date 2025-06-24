# 爬虫

爬虫（Web Scraping / Web Crawling）是一种自动化程序，按照特定规则从网络上抓取信息。

**工作原理：**

1. 发送请求：向目标网站发送HTTP请求。

2. 获取响应：接收服务器返回的HTML文档或数据。

3. 解析数据：使用解析库（如BeautifulSoup、lxml）提取所需数据。

4. 存储数据：将提取的数据存储到本地文件、数据库等。

**常用工具与库：**

- Requests：用于发送HTTP请求。
- BeautifulSoup：用于解析HTML和XML文档。
- Scrapy：功能强大的爬虫框架，支持数据抓取、存储和调度。
- Selenium：用于处理动态网页（如JavaScript生成的内容）。

## scrapy和Requests+BeautifulSoup对比

| 特性     | Scrapy                                         | Requests + BeautifulSoup     |
| -------- | ---------------------------------------------- | ---------------------------- |
| 类型     | 完整的爬虫框架，具有固定的项目结构             | 基础库组合                   |
| 抓取能力 | 支持异步处理，适合大规模抓取                   | 简单请求和解析               |
| 内置功能 | 提供内置的请求重试、用户代理管理、反爬虫机制等 | 需要手动实现                 |
| 数据存储 | 自动处理数据存储，支持多种格式                 | 需要手动实现数据存储         |
| 资源使用 | 支持多线程和多进程                             | 需要自己实现多线程，管理复杂 |

## 反爬虫

反爬虫是网站采用的一系列技术和策略，以防止爬虫抓取其数据。

常见反爬虫技术：

1. IP封禁：频繁的请求会导致 IP 被临时或永久封禁。
2. 验证码：通过图形验证码或滑动验证码阻止自动化请求。
3. User-Agent检测：网站可以通过检查请求中的 User-Agent 头部来判断请求是否来自浏览器，非浏览器的请求可能会被拒绝。
4. 请求频率限制：网站限制单位时间内的请求次数，超过限制会返回错误。
5. 动态内容加载：使用 AJAX 或其他技术动态加载内容，爬虫难以直接抓取。
6. 内容混淆：通过 JavaScript 加密或动态生成内容，爬虫难以解析。
7. Cookie 验证：网站要求用户登录后才能访问内容，爬虫需要管理和维护会话 cookie。

### IP封禁+请求速率限制

实现方法：使用 Nginx 的 `limit_req` 模块来限制请求频率，配合 `deny` 指令封禁特定 IP。

配置示例:

~~~python
http {
    # 定义请求速率
    limit_req_zone $binary_remote_addr zone=mylimit:10m rate=1r/s;
    server {
        location / {
            limit_req zone=mylimit burst=5 nodelay;  # 允许突发请求
            # 处理请求
        }
    }
}
# 封禁特定 IP
server {
    location / {
        deny 192.168.1.1;  # 封禁指定 IP
        # 处理请求
    }
}
~~~

### User-Agent检测

实现方法:使用 Nginx 的 map 指令来检测 User-Agent，并拒绝不符合条件的请求。

~~~python
http {
    map $http_user_agent $blocked {
        default 0;
        ~*bot 1;  # 匹配含有 'bot' 的 User-Agent
    }

    server {
        location / {
            if ($blocked) {
                return 403;  # 返回403状态码拒绝请求
            }
            # 处理请求
        }
    }
}
~~~

### Cookie验证

使用 Nginx 的 auth_request 模块结合后端应用进行 Cookie 验证。

~~~python
location / {
    auth_request /auth;  # 通过子请求验证 Cookie
    # 处理请求
}

location = /auth {
    internal;
    # 这里处理 Cookie 验证逻辑
    if ($http_cookie !~ "session=your_session") {
        return 403;  # Cookie 验证失败，返回403
    }
}
~~~

## 突破反爬限制

1. IP 代理池：使用代理 IP 进行请求，避免频繁使用同一 IP。可以使用免费的代理服务，或购买代理服务来确保可用性和速度。
2. 随机 User-Agent：使用多个 User-Agent 字符串，随机选择在请求中使用，模拟不同的浏览器和设备请求。
3. 请求间隔控制：添加随机延迟，控制请求的频率，以避免触发频率限制。
4. 验证码处理：使用 OCR（光学字符识别）技术来识别验证码，或者使用第三方服务进行验证码识别。对于简单验证码，可以尝试手动解决，但对于复杂的验证码，可能需要其他手段。
5. JavaScript 渲染：使用 Selenium、Playwright 或 Puppeteer 等工具来处理需要执行 JavaScript 的网页，从而抓取动态加载的内容。
6. 会话管理：使用 requests 库中的会话功能，保持登录状态并管理 cookie，以模拟正常用户的访问行为。
7. 分布式爬虫：构建分布式爬虫架构，将请求分发到不同的机器上，避免单一机器的 IP 被封。
8. API 使用：查找是否有公开的 API 可以使用。许多网站提供 RESTful API 来供用户访问数据。

### IP封禁

反爬机制：频繁的请求会导致网站暂时或永久封禁 IP 地址。

解决方案：IP 代理池：使用多个代理 IP，动态切换，避免连续使用同一 IP。

~~~python
import requests
from random import choice
proxy_list = [
    'http://proxy1:port',
    'http://proxy2:port',
    'http://proxy3:port',
]
proxy = {'http': choice(proxy_list), 'https': choice(proxy_list)}
response = requests.get('http://example.com', proxies=proxy)
~~~

### User-Agent检测

反爬机制：网站会检查请求的 User-Agent 字段，过滤掉非浏览器的请求。

解决方案：随机 User-Agent：使用 fake-useragent 库随机选择 User-Agent。

~~~python
from fake_useragent import UserAgent
ua = UserAgent()
headers = {'User-Agent': ua.random}
response = requests.get('http://example.com', headers=headers)
~~~

### 请求频率限制

反爬机制：网站限制单位时间内的请求次数，超过限制会返回错误。

解决方案：设置请求间隔：使用 time.sleep() 函数来控制请求频率。

~~~python
import time
for _ in range(10):  # 发起10次请求
    response = requests.get('http://example.com')
    print(response.status_code)
    time.sleep(5)  # 每次请求之间间隔5秒
~~~

### 动态内容加载

反爬机制：使用 AJAX 技术动态加载内容，直接请求 HTML 无法获取数据。

解决方案：使用 Selenium 模拟浏览器行为加载动态内容。

~~~python
from selenium import webdriver

driver = webdriver.Chrome()
driver.get('http://example.com')
content = driver.page_source
print(content)
driver.quit()
~~~

# 基于Requests+BeautifulSoup的爬虫案例

## 爬取测试网站html标签

### 搭建测试网站

安装django

~~~sh
pip3 install django
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple django
~~~

运行django项目，访问127.0.0.1：8000看到网页

~~~python
python ./manage.py runserver
~~~

### 爬取网页标签

安装beautifulsoup4

~~~python
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple beautifulsoup4
~~~

~~~python
import requests
from bs4 import BeautifulSoup
import csv


url = 'http://127.0.0.1:8000/'
response = requests.get(url)

if response.status_code == 200:
    # 将返回的文本内容，用解析器html.parser解析，返回一个对象赋值给soup
    soup = BeautifulSoup(response.text, 'html.parser')
    # print(response.text)
    # 查找所有li标签,li标签是HTML中的列表项。
    # 返回一个列表，元素是Tag对象。可迭代，用text方法获取文本内容
    articles = soup.find_all('li')
    data = []

    for article in articles:
        # 用text方法获取到每个标签的文本内容
        title = article.text.strip()
        # 把每个字符串变成列表，存到列表里，方便后面输出到csv
        data.append([title])
        # data = [['My First Article'], ['My Second Article'], ['hanxianchao']]

    # newline是防止写入时在每一行后额外添加空行。这是处理csv文件的推荐设置
    with open('scrape/article.csv', 'w', newline='', encoding='utf-8') as f:
        # 创建csv写入器，用于将数据写入文件
        writer = csv.writer(f)
        # 用writerow往csv写入一行数据。写入一个列表，表示csv的第一行内容，通常是表头
        # csv文件的第一行会包含一个单元格，内容为Title
        writer.writerow(['Title'])
        # 写入多行数据，传入一个列表，列表中的每个子列表作为一行写入csv
        writer.writerows(data)
        #
    print(f"Grab successfully, saved to article.csv")
else:
    print(f"Request failed, status code: {response.status_code}")
~~~

## 爬取github上的devops项目

需求：从 GitHub API 获取与“DevOps”相关的项目信息，并将这些信息输出到控制台和保存到一个名为 devops.txt 的文件中。

~~~python
import requests # 发送http请求
# import io, sys # 设置标准输出，编码是utf-8，确保处理中文字符不乱码
from bs4 import BeautifulSoup

# 设置输出内容可以处理中文字符
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# github api 查询devops相关的项目
url = "https://api.github.com/search/repositories?q=devops"

# 发送get请求
response = requests.get(url)
if response.status_code == 200:
    # 返回了一个字典对象
    data = response.json()
    # print(data)
    # get是字典方法，查找指定的key，没找到就用默认值：空列表
    # get比data['items']更安全，因为假设没有items键，后者会抛出KeyError，前者会用默认值
    repos = data.get('items', [])
    with open("scrape/github-devops.txt", 'w', encoding='utf-8') as f:
        if not repos:
            print("No projects are found.")
            f.write("No projects are found")
        else:
            for r in repos:
                # repo是一个列表，每个元素r都是字典，包含repo的详细信息。
                # 这里因为只要repo有值，‘name’和‘html_url’就有值，所以不用get方法。直接用字典键来获取值
                project_name = r['name']
                project_url = r['html_url']
                description = r['description']
                output = f"Project Name: {project_name}.\nProject URL: {project_url}.\nProject Description: {description}.\n-------\n"
                # print(output) # 控制台输出
                # 写入到文件
                f.write(output)
else:
    print(f"Request failed: {response.status_code}.\n")
~~~

## 爬取各个国家的天气

~~~python
~~~

