import json

with open('Python/python-manuscripts/policy.json', 'r') as f:
    # 把json反序列化成一个字符串
    policy_info = json.loads(f.read())

print(policy_info)