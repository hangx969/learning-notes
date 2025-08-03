import sys, io
import pandas as pd
import matplotlib.pyplot as plt
# 用于设置图中中文字体
from matplotlib import font_manager

# 将标准输出的编码设置为utf-8,这样控制台就能处理中文字符了
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 读取excel文件
data = pd.read_excel(r"E:\work\KEEP-WORKING\CS-Learning\git-repo\python-operation-scripts\python-data-ai\sales_data.xlsx")

# 统计每个产品的总销量
product_sales = data.groupby('Product')['Sales'].sum().reset_index()
# 按照每个产品的总销量降序排序
product_sales_sorted = product_sales.sort_values(by='Sales',ascending=False)

# 绘制柱状图
# 处理字体符号显示
plt.rcParams['font.family']=['Consolas']
# 正常显示负号
plt.rcParams['axes.unicode_minus'] = False

# 创建图形窗口，设置长和宽像素
plt.figure(figsize=(10,6))

# 将product这个列设置为索引
# 谁要当横轴，就把这个值设置为索引
sales_by_product = product_sales_sorted.set_index('Product')
# print(sales_by_product)

# 绘制柱状图，索引是Product，值是Sales
sales_by_product['Sales'].plot(kind='bar', color='skyblue')

# 设置x轴和y轴坐标，和标题
plt.xlabel('Products')
plt.ylabel('Total Sales')
plt.title("Total Sales by every product")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

plt.show()