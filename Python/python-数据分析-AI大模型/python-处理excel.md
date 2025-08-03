# excel表格操作

## 安装

需要安装pandas和openpyxl

~~~sh
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple pandas
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple openpyxl
~~~

## dataframe和series

**Series 是 pandas 中的一维数据结构，类似于带标签的数组或字典。**

特点：

- 一维数据：只有一列数据
- 带索引：每个元素都有一个标签（索引）
- 同类型数据：通常包含相同数据类型的元素
- 类似列表和字典的结合体

作用：

- 存储单列数据（如一列数字、字符串、日期等）
- 支持快速的数据访问和操作
- 可以进行数学运算、统计分析等

**DataFrame 是 pandas 中的二维数据结构，可以理解为多个 Series 的集合。**

特点：

- 二维数据：有行和列的表格结构
- 多列数据：每列可以是不同的数据类型
- 带标签：行索引和列索引都有标签
- 类似 Excel 表格或 SQL 表

作用：

- 存储和操作结构化数据
- 数据清洗、转换、分析
- 数据可视化的基础
- 与各种数据源（Excel、CSV、数据库等）交互

## 读取excel数据

~~~python
import sys, io
import pandas as pd
# 将标准输出的编码设置为utf-8,这样控制台就能处理中文字符了
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 读取excel文件，路径加r保持原值原样的路径输出
data = pd.read_excel(r"E:\work\KEEP-WORKING\CS-Learning\git-repo\python-operation-scripts\python-data-ai\sales_data.xlsx")
# 带索引输出表格数据前10行
print(data.head(10))
# 不带索引输出表格数据前10行
print(data.head(10).to_string(index=False))
~~~

## 分析表格数据

~~~python
import sys, io
import pandas as pd

# 将标准输出的编码设置为utf-8,这样控制台就能处理中文字符了
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 读取excel文件
data = pd.read_excel(r"E:\work\KEEP-WORKING\CS-Learning\git-repo\python-operation-scripts\python-data-ai\sales_data.xlsx")

# 统计每个产品总销量，按照Product来分组。
# ['Sales'].sum() 分组之后的sum聚合操作，只应用在Sales这一列。
# reset_index() 结果重新转换为新的索引，不按照原来的索引
product_sales = data.groupby('Product')['Sales'].sum().reset_index()
print(product_sales)

# 按照sales的值降序排序
product_sales_sorted = product_sales.sort_values(by='Sales',ascending=False)
# 结果去掉索引输出
print(product_sales_sorted.to_string(index=False))

# 获取表格中的单日Sales最大值和Sales最大的产品
# idxmax获取到Sales的最大值所在的索引
# loc方法获取到这个索引对应的Series
highest_sales = data.loc[data['Sales'].idxmax()]
print(f"Highest sales record: {highest_sales.to_string(index=False)}")

top_product = data.groupby('Product')['Sales'].sum().idxmax()
print(f"Highest product by sales: {top_product}")
~~~

# 绘图操作

## 绘制柱状图

### 安装

~~~sh
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple matplotlib
~~~

### 绘图

~~~python
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
~~~

## 绘制折线图

~~~python
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

# 汇总每日销量，按照日期聚合，聚合操作是把Sales相加
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
~~~

# word文件处理

## 安装

~~~sh
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple python-docx
~~~

## 生成word报告

~~~python

