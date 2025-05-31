# Python数据类型、运算符

## 数据类型

- 整型（int）

- 浮点数（float）

- 字符串（str）

  - 多行字符串

    ~~~python
    # 在给变量赋值的时候，三引号是用作多行字符串
    a = """This is a
    multi-line string
    """
    ~~~

  - 伪注释

    ~~~python
    # 不是赋值的情况就是“伪注释”
    """
    multi-line commtns
    """
    ~~~

- 布尔值（bool）

## 运算符

- 算术运算：+，-，*，/，%（取模）

- 比较运算符：==，!=,>=,<=

- 逻辑运算符：and（&&）, or（|）, not（!）

  > 短路逻辑：在多个and or连接的判断语句中，前面的判断只要是能确定了整个句子的true false，就不会继续去算后面的逻辑。

## 索引操作/切片

- 列表索引

  ~~~python
  time = ["2028", "08", "08", "T10:00:00", "Z"]
  time[3] # T10:00:00
  ~~~

- 字符串索引

  ~~~python
  time = "T10:00:00"
  #可以用索引来取到字符串的某个字符
  time[0] # T
  ~~~

- 嵌套索引

  当列表元素为字符串的时候，可以用嵌套索引来获取某个字符串元素的某一部分

  ~~~python
  time = ["2028", "08", "08", "T10:00:00", "Z"]
  time[3][1:] # 10:00:00
  ~~~

# 列表、元组、字典、集合

## 列表（List）

列表是有序的，索引从0开始，可以随时修改。

### 列表操作

~~~python
# 获取元素个数
len(list)
# 获取最大最小值
max(list) / min(list)
# 数组求和
sum(list)
~~~

### 列表方法

~~~python
# 添加元素
list.append("xxx")
# 删除元素
list.remove("xxx")
# 排序数值数组。
list.sort()
# 获取元素索引
list.index("元素值")
# 反转列表
list.reverse()
~~~

> - 中文排序是按照每个字符的unicode编码，从小到大排序。Unicode 对应的汉字编码是一种国际标准，用于为每个汉字分配一个唯一的编码值。由于汉字数量庞大，这些编码值范围从较低的数值到较高的数值。常见汉字的 Unicode 编码大多集中在 U+4E00 到 U+9FFF 之间
> - 查看unicode编码：访问 https://www.unicode.org/charts/，找到 CJK Unified Ideographs (Han)

### 列表嵌套访问

~~~python
nested=[[1,2,3],[4,5,6],[7,8,9]]
nested[1] # [1,2,3]
nested[1,1] # [5]
~~~

### 列表拼接

- join() 是一个字符串方法，它用于将一个可迭代的对象（如列表、元组等，**元素必须是字符串**）中的元素用某个连接符连接成一个字符串。
- 语法：separator.join(iterable)，其中 separator 是连接各元素的分隔符，iterable 是要被拼接的元素（如列表）

~~~ python
words = ["a", "b", "c"]
"".join(words) # "abc"
" ".join(words) # "a b c"
"-".join(words) # "a-b-c"
~~~

- 案例：处理时间戳

~~~python
time_stamps=['2028','08','08','T10:00:00','Z']
# 提取日期和时间部分分别提取出来，拼接成新的字符串，日期部分为‘2028-08-08’，时间部分为‘10:00:00 Z‘
date = '-'.join(time_stamps[:3])
time = time_stamps[3][1:]+ ' ' + time_stamps[-1]
# ' '.join(time_stamps[3:])).lstrip('T')也行
~~~

## 元组（Tuple）

元组是一个有序、不可变的元素集合。一旦创建，元组中的元素不能被修改。这种特性使得元组适用于存储那些不希望被改变的数据。

### 元组赋值

~~~python
product = ('1123','abc',10)
# 直接用元组名字给变量赋值
id, name, price = product
print (f"id is {id}")
print (f"name is {name}")
print (f"price is {price}")
# print中可以用f"{variable}"，在双引号中格式化变量的值
~~~

## 字典(Dict)

字典是一种无序的、键值对形式的容器。

~~~python
phont_book = {
    'Alice': '123-456-7890',
    'Bob': '987-654-3210',
    'Charlie': '555-555-5555'
}
# 通过key的值，获取到对应的value
print (phone_book['Alice'])
~~~

嵌套字典

~~~python
library_books = {
    '978-3-16-148410-0': {
        'title': 'The Great Gatsby',
        'author': 'F. Scott Fitzgerald',
        'year': 1925,
        'available': True
    },
    '978-1-56619-909-4': {
        'title': 'To Kill a Mockingbird',
        'author': 'Harper Lee',
        'year': 1960,
        'available': False
    }
}

isbn = '978-3-16-148410-0'
print (library_books[isbn]['available'])
~~~

### 字典方法

## 集合(Set)

集合是一个无序、不重复的元素集合。它有点像数学中的集合概念，特别适合用于去重或检查某个元素是否在集合中。

~~~python
email_list = [
"alice@example.com",
"bob@example.com",
"carol@example.com",
"alice@example.com", # 重复的邮箱
"dave@example.com",
"bob@example.com" # 重复的邮箱
]
# 去重
unique_list=set(email_list)

# 检查元素是否在其中
email_check = "alice@example.com"
is_in = email_check in unique_list
~~~

### 集合方法

~~~python
seta = {"a","b","c"}
setb = {"c","d","e"}
# 求两个集合的交集
seta.intersection(setb)
~~~

# 条件判断语句

## if

~~~python
# 语法格式
if x > 5：
   print("x>5")
elif x < 5：
   print("x<5")
else：
   print("x=5")

# if的三元表达式
result = "x>5" if x>5 else "x<=5"
~~~

案例：验证用户信息

~~~python
# phone number validation
phone = input ("Enter your phone number: ")

if len(phone) == 11 and phone.isdigit():
    print("Valid phone number")
else:
    print("Invalid phone number. Please enter an 11-digit number.")

# name validation
name = input("Enter your name: ")

if len(name)>=2 and len(name)<=20 and all ('/u4e00' <= char <= '/u9fa5' for char in name):
    print("Valid name")
else:
    print("Invalid name. Please enter a name with 2 to 20 characters, using Chinese characters only.")

# id validation
# 15位或者18位，18位的最后一位可以是X
id_number = input("Enter your ID number: ")

if (len(id_number) == 15 and id_number.isdigit()) or (len(id_number)==17 and id_number[:17].isdigit() and (id_number[-1].isdigit() or id_number[-1]=='X')):
    print("Valid ID number")
else:
    print("Invalid ID number. Please enter a 15-digit or 18-digit ID number, with the last character being a digit or 'X'.")
~~~

# 循环语句for/while

for: 用于已知循环次数。while：用于循环次数未知，但是知道终止条件，循环到终止条件被满足。

### 案例1：批量数据备份与恢复

`os.listdir`, `os.path.join`的使用

~~~python
import os
import shutil

config_dir ='~/scripts/config'
backup_dir = '~/scripts/backup'

# os.llistdir(path) 获取目录下的所有文件名称列表
for file_name in os.listdir(config_dir):
    if file_name.endswith('.conf'):
        # 把文件名和当前路径拼接成文件的绝对路径
        file_path = os.path.join(config_dir, file_name)
        backup_path = os.path.join(backup_dir, file_name)
        # 复制文件
        shutil.copy(file_path, backup_path)
        print(f"Backup of {file_path} completed to {backup_path}")
~~~

### 案例2：旧日志数据管理与清理

`os.path.join`, `os.path.getmtime`的使用

~~~sh
# 用touch -d来模拟历史文件
touch -d '60 days ago' /path/to/logs/log1.log
~~~

~~~python
# 删除修改时间为30天之前的日志
import os
import time

log_dir = "~/scripts/logs"
retention_days = 30
# 获取当前时间（距离1970/01/01过去的秒数）
current_time = time.time()

for file_name in os.listdir(log_dir):
    if file_name.endswith(".log"):
        file_path = os.path.join(log_dir, file_name)
        # getmtime() returns the time of last modification of the file in seconds since the Unix epoch （1970/01/01）
        file_age = current_time - os.path.getmtime(file_path)
        # Check if the file is older than the retention period（seconds）
        if file_age > retention_days * 86400:
            try:
                os.remove(file_path)
                print(f"Deleted old log file: {file_path}")
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")
~~~

### 案例3：服务器运行状态定期检查

`subprocess.run([],)`的使用:

subprocess.run 是一个用于执行外部命令的函数。

- []内放需要执行的命令和参数
- capture_output=True，捕获命令执行时的标准输出（stdout）和标准错误输出（stderr）。不使用 capture_output=True，标准输出和标准错误输出会直接显示在你的终端或命令行界面上。使用 capture_output=True 后，这些输出会被捕获并存储在 result 对象的属性中，供后续使用。
- text=True 指示 subprocess.run 将捕获到的输出解码为文本字符串，而不是默认的字节对象。
  - 默认情况下，subprocess.run 会返回字节对象（bytes），对于处理文本输出来说不够方便。如`b'PING google.com (172.217.14.206): 56 data bytes'`
  - 使用 text=True 后，输出会自动解码为字符串（str），这使得处理和操作输出更为直观和方便，如`PING google.com (172.217.14.206): 56 data bytes'`

~~~python
import time
# 可以执行ping, ls等操作
import subprocess

servers = ["192.168.1.1","192.168.1.2","192.168.1.3"]
while True:
    for server in servers:
        result = subprocess.run(["ping", "-c", "1", server], capture_output=True, text=True)
        print(f"Checking {server}...")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        print(f"returncode: {result.returncode}")

        if result.returncode == 0:
            print(f"{server} is reachable.")
        else:
            print(f"{server} is not reachable.")
    time.sleep(86400)  # 等待86400秒，即24小时
    print("Waiting for the next check...\n")
~~~

### 案例4：根分区空间监控

`shutil.disk_usage`的使用

~~~python
import shutil, time
check_interval = 60  # seconds
while True:
    # shutil.diskusage()返回某个目录的使用情况，直接返回了一个字典，包含了总空间、已用空间和可用空间
    total,used,free=shutil.disk_usage('/')
    usage_percent = used/total * 100
    # 结果保留两位小数
    print(f"Root partition usage: {usage_percent:.2f}%")
    time.sleep(check_interval)
~~~

### 案例5：服务状态监控

`os.system`的使用

~~~python
import os, time
SERVICES = ['docker.service']
CHECK_INT = 10

while True:
    for service in SERVICES:
        status = os.system(f'systemctl is-active --quiet {service}')
        if status != 0:
            os.system(f"systemctl start {service}")
            print(f"service {service} is not running and has been started")
        time.sleep(CHECK_INT)
~~~

### 案例6：多台服务器上执行命令

`os.system()`的使用

~~~python
import os
servers = ["192.168.1.1","192.168.1.2","192.168.1.3"]
command = ['df -h']

for server in servers:
    print (f"Connecting to {server} and run command")
    os.system(f"ssh root@{server} '{command}'")
~~~

# 字符串操作

## 访问/修改/切片

### 访问

可以通过索引下标来访问到字符串的某个元素。

### 修改

字符串创建之后就不支持修改，但是可以通过切片重新分配来修改字符串

~~~python
var1 = 'hello'
var1 = var1[:] + ' ' + 'world'
~~~

### 切片

是索引的扩展形式，语法[start​​\:end\:step]，用于从序列中提取一个子集

- start:切片的起始索引，包含在结果中，如果省略，默认从 0 开始
- end：切片的结束索引，不包含在结果中，如果省略，则一直切到序列末尾 （左闭右开）
- step：切片的步长，默认是 1，如果设置成了负数，表示从右向左取元素。-1表示最后一个元素

~~~python
text="Hello,world!"
text[:-1] # Hello,world 表示去掉最后一个字符

numbers=[1,2,3,4,5]
numbers[:-1] # [1,2,3,4] 表示去掉最后一个元素 
~~~

## 运算符

~~~python
a = 'Hello'
b = 'world'

# 字符串相加等于拼接
a + b # 'Hello world'

# 字符串乘以数字等于重复
a * 2 # 'HelloHello'

# 用in来判断某元素是否在字符串中
a = 'Hello'
print (f"H is in {a}") if 'H' in a

#获取长度
len(a)
~~~

## 转义字符

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202505311736560.png" style="zoom:67%;" />

取消转义用r，`print(r"\n")`

## 格式化

字符串中%用于定义占位符，后面跟着一个格式化字符，用于指定变量的类型。例如：

- `%s` 表示插入一个字符串。
- `%d` 表示插入一个整数。
- `%f` 表示插入一个浮点数。
- `%%` 表示插入一个百分号符号本身。

~~~python
# 整型和字符串占位符
name = 'alice'
age = 12
print("Name is %s, age is %d." % (name, age))

# 输出百分号
percent = 75
print("Percentage is %d%%" % percent)

#输出浮点数的小数点后位数。%10.2f表示输出浮点数占10个字符的宽度，小数点后保留两位。数字不足将用空格填充
print('PI\'s vaule is：%10.2f' % 3.1415926)
# 仅输出小数点后两位数字
print('PI\'s vaule is：%.2f' % 3.1415926)
# 添加左对齐
print('PI\'s vaule is：%-10.2f' % 3.1415926)
~~~

## 字符串方法

~~~python
text = "Hello, world!"

# 首字母大写
text.capitalize()
# 首字母每个标点符号后面的小写都变大写
text.title()
# 所有字母转换为大写
text.upper()
# 所有字母转换成小写
text.lower()
# 大小写反转
text.swapcase()
# 字符串居中，变量表示一共多宽，用什么符号做占位符
text.center(40，'-')

# 按符号分开
words = text.split(" ")
# 统计词频，Counter方法会以字典的形式输出单词和词频
from collections import Counter
word_count = Counter(words)

#查找元素或子串，查不到就返回-1
text.find('Hello') # 会返回H的索引，0。

# 连接字符串，用于将序列用某种连接符连接成新的字符串
seq=['a','b','c']
'-'.join(seq) # a-b-c
''.join(seq) # abc

# 子串/元素替换
text.replace(","," ") # 把,替换为空格

#分割字符串，返回列表
str = "abc def"
str.split() # ['abc','def'] 默认用空白作为分割符
str.split('c') # ['ab','def']
str.split(' ', 2) # 指定分割次数：最多从前到后分割两次，后面的原封不动
"".split() # 空格分割空字符串，返回空列表

# 去除首尾字符
text = "\t abc \t"
# 去掉首尾空白字符
text.strip()
# 去掉首尾指定字符
text.strip('!')
# 对开头字符去除
text.lstrip()
# 对末尾字符去除
text.rstrip()
~~~
