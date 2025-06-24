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

# 搭建测试网站

安装django

~~~sh
pip3 install django
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple django
~~~

