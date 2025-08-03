import sys, io
import pandas as pd
import matplotlib.pyplot as plt
# 用于设置图中中文字体
from matplotlib import font_manager

# 将标准输出的编码设置为utf-8,这样控制台就能处理中文字符了
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# 处理字体符号显示
plt.rcParams['font.family']=['Consolas']
# 正常显示负号
plt.rcParams['axes.unicode_minus'] = False

# 读取excel文件
data = pd.read_excel(r"E:\work\KEEP-WORKING\CS-Learning\git-repo\python-operation-scripts\python-data-ai\sales_data.xlsx")

# 按照日期统计销量趋势
# 转换成pandas日期格式
data['Date'] = pd.to_datetime(data['Date'])

# 汇总每日销量
daily_sales = data.groupby('Date')['Sales'].sum().reset_index()

# 绘制折线图
# 创建图形窗口，设置长和宽像素
plt.figure(figsize=(12,6))
# 线条之间用圆点标记，蓝色线条，实线连接
plt.plot(daily_sales['Date'], daily_sales['Sales'], marker='o', color='blue', linestyle='-')
plt.xlabel("Date")
plt.ylabel('Total Sales')
plt.title("Daily Sales Trends")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()