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