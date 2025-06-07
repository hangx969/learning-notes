import json

# 用一个json文件存放用户权限信息，使用python读取和更新权限信息

with open('python-manuscripts/permissions.json', 'r') as f:
    # 把json反序列化成一个字典
    user_info = json.load(f)

user_info['user123']['access_level'] = 'admin'
user_info['user789']['active'] = True

with open('python-manuscripts/permissions.json', 'w') as f:
    json.dump(user_info, f, indent=4)