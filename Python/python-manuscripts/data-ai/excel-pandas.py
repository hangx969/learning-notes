import sys, io
import pandas as pd

# 将标准输出的编码设置为utf-8,这样控制台就能处理中文字符了
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 读取excel文件，路径加r保持原值原样的路径输出
data = pd.read_excel(r"E:\work\KEEP-WORKING\CS-Learning\git-repo\python-operation-scripts\python-data-ai\sales_data.xlsx")

print(data.head(10))
print(data.head(10).to_string(index=False))
