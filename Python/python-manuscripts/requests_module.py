import requests

response = requests.post(
    'https://httpbin.org/post',
    json = {'key': 'value'},
    headers={'Content-Type': 'application.json'}
)

print(response.status_code)
# 获取返回内容，用json格式显示
print(response.json())
