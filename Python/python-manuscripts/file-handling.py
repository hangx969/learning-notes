import re
pattern = r'\d{3}-\d{3,8}'
text = 'My phone 123-1234567, and 987-6543210'
result = re.findall(pattern, text) # result返回列表，直接print就行，不用group()方法
print(f"Match well {result}") if result else print("Match failed")