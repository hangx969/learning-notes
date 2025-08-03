import sys, io
import pandas as pd

# 将标准输出的编码设置为utf-8,这样控制台就能处理中文字符了
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 读取excel文件
data = pd.read_excel(r"E:\work\KEEP-WORKING\CS-Learning\git-repo\python-operation-scripts\python-data-ai\sales_data.xlsx")

# 统计每个产品总销量，按照Product来分组
product_sales = data.groupby('Product')['Sales'].sum().reset_index()
print(product_sales)

# 按照sales的值降序排序
product_sales_sorted = product_sales.sort_values(by='Sales',ascending=False)
# 结果去掉索引输出
print(product_sales_sorted.to_string(index=False))