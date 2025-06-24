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
