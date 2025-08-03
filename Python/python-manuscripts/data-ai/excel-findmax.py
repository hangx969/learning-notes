import sys, io
import pandas as pd

# 将标准输出的编码设置为utf-8,这样控制台就能处理中文字符了
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

data = pd.read_excel(r"E:\work\KEEP-WORKING\CS-Learning\git-repo\python-operation-scripts\python-data-ai\sales_data.xlsx")

# idxmax获取到Sales的最大值所在的索引
# loc方法获取到这个索引对应的Series
highest_sales = data.loc[data['Sales'].idxmax()]
print(f"Highest sales record: {highest_sales.to_string(index=False)}")

top_product = data.groupby('Product')['Sales'].sum().idxmax()
print(f"Highest product by sales: {top_product}")