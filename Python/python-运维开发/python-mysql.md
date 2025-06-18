# Mysql介绍

MySQL 是一种开源的关系型数据库管理系统（RDBMS），数据库就是用来存储和管理数据的地方，而 MySQL 则是一种专门用来管理这些数据的软件。

**为什么使用 MySQL？**

1. 存储数据：MySQL 能帮助我们把数据存储在一个结构化的表格中。比如，你有一个网站，可以用 MySQL 来存储用户信息、订单数据、商品信息等。
2. 数据查询：你可以用 MySQL 的查询语言（SQL）快速找到你想要的数据，比如查找某个用户的订单记录。
3. 数据安全：MySQL 提供了各种安全功能，防止未经授权的用户访问你的数据。
4. 多用户并发：MySQL 支持多个用户同时操作数据，不会互相干扰，适合企业级应用。

**MySQL 的核心概念：**

1. 数据库（Database）：这是存储数据的容器。一个数据库可以包含多个表。
2. 表（Table）：表就像一个 Excel 表格，它有行和列。每个表格中的数据都有明确的格式。
3. 行和列（Rows and Columns）：行代表一条数据记录，列则是数据的属性。例如，在用户表里，列可以是姓名、邮箱，行则是每个用户的具体信息。
4. SQL（结构化查询语言）：这是与 MySQL 互动的语言。通过 SQL，你可以进行数据的插入、删除、更新和查询。

## 安装Mysql

~~~python
wget http://repo.mysql.com/mysql-community-release-el7-5.noarch.rpm
rpm -ivh mysql-community-release-el7-5.noarch.rpm
yum install mysql-server -y
chown mysql:mysql -R /var/lib/mysql
~~~

> 注：这个教程在RockyLinux8.10上无法启动mysql。
>
> 尝试使用[helm安装mysql](../../Docker-Kubernetes/helm/helm部署mysql)

~~~sh
#初始化 MySQL
mysqld --initialize
#启动 MySQL
systemctl start mysqld
#查看 MySQL 运行状态
systemctl status mysqld
#mysql 安装成功后，默认的 root 用户密码为空，你可以使用以下命令来创建 root 用户的密码，密码设置成 111111
mysqladmin -u root password "111111"
#登陆数据库
mysql -uroot -p111111
#在 MySQL 数据库中授予用户权限
mysql> grant all on *.* to 'root'@'%' identified by '111111'; # 在mysql pod中直接用grant all on *.* to 'root'@'%'
flush privileges;
~~~

## 增删改查

~~~mysql
# 创建数据库
mysql>CREATE DATABASE shop;
# 创建用户表
mysql>USE shop;
mysql>CREATE TABLE customers (
id INT AUTO_INCREMENT PRIMARY KEY,
name VARCHAR(50) NOT NULL, 
email VARCHAR(50) NOT NULL UNIQUE 
);

# id：这是列的名称，代表每个客户的唯一标识符。
# INT：数据类型为整数，表示 id 列将存储整数值。
# AUTO_INCREMENT：自动递增，意味着每当插入新记录时，MySQL 会自动为该列生成一个唯一的、递增的整数值。这样可以确保每个客户的 id 是唯一的。
# PRIMARY KEY：将 id 列设置为主键，确保该列的值在表中是唯一的，并且不允许为空。这也使得 MySQL 可以高效地索引和查找该列的数据。
# VARCHAR(50)：数据类型为变长字符串，最大长度为 50 个字符。NOT NULL：表示该列不能为空，确保每个客户都有姓名。
# UNIQUE 确保该列的值在表中是唯一的，避免多个客户使用相同的电子邮箱

# 创建商品表
mysql>CREATE TABLE items (
id INT AUTO_INCREMENT PRIMARY KEY,
item_name VARCHAR(50) NOT NULL,
price DECIMAL(10, 2) NOT NULL
);
# DECIMAL(10, 2)：数据类型为小数，最多 10 位数字，其中 2 位用于表示小数部分。这个定义允许的价格范围是从 -99999999.99 到 99999999.99，适合用于表示价格信息。

# 插入用户数据
mysql>INSERT INTO customers (name, email) VALUES
('Alice', 'alice@example.com'),
('Bob', 'bob@example.com');
select * from customers

# 插入商品数据
mysql>INSERT INTO items (item_name, price) VALUES
('Book', 9.99),
('Pen', 1.50);
mysql> select * from items;
# 删除表
mysql> DROP TABLE shop.items;
# 删除数据库
mysql>DROP DATABASE shop;
~~~

# mysql-connector-python库

## 功能

mysql-connector-python 是一个官方提供的 Python 库，用于与 MySQL 数据库进行交互。它为 Python 应用程序提供了简单而强大的 API，使开发者能够轻松执行数据库操作，如连接数据库、执行 SQL 查询、处理结果集等。

主要功能：

1. 数据库连接: 通过该库，用户可以方便地连接到 MySQL 数据库，支持使用主机名、端口、用户名和密码等信息进行连接。
2. 执行 SQL 语句: 提供游标对象，允许用户执行各种 SQL 语句，包括 SELECT、INSERT、UPDATE 和 DELETE 等。
3. 处理结果集: 可以轻松获取查询结果并以各种方式进行处理，比如获取所有结果、逐行遍历结果集等。
4. 事务管理: 支持事务处理，用户可以通过提交或回滚操作来管理数据的一致性。
5. 错误处理: 提供详细的异常和错误处理机制，方便开发者定位问题。
6. 适用于多种平台: 该库可以在不同操作系统上使用，如 Windows、Linux 和 macOS。

## 安装

~~~sh
pip3 install mysql-connector-python
# 清华源
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple mysql-connector-python
~~~

## 使用

### 连接mysql数据库

使用 `mysql.connector.connect`() 函数可以创建一个与 MySQL 数据库的连接。需要提供以下参数：

- host: 数据库主机地址。
- user: 数据库用户名。
- password: 数据库用户的密码。
- database: 要连接的数据库名称。

### 创建cursor对象

通过连接对象创建游标 (cursor) 对象，游标用于执行 SQL 语句并获取结果。

### 执行SQL语句

使用游标的 execute() 方法可以执行 SQL 语句，例如 INSERT, UPDATE, DELETE, 和 SELECT。

### 提交更改

对于 INSERT, UPDATE, 和 DELETE 操作，必须使用连接对象的 commit() 方法来保存更改。

### 关闭连接

完成操作后，使用 close() 方法关闭游标和数据库连接，以释放资源。

## 实战案例

### 创建数据库和表

在开始编写 Python 代码之前，我们需要在 MySQL 中创建一个数据库和一个表。假设我们创建一个名为 test_db 的数据库，并在其中创建一个名为 users 的表。

~~~mysql
CREATE DATABASE test_db;
USE test_db;
CREATE TABLE users (
id INT AUTO_INCREMENT PRIMARY KEY,
name VARCHAR(100),
age INT
);
~~~

### 对表进行增删改查

~~~python
import mysql.connector

# 插入数据
def insert_user(name, age):
    # 定义sql语句。VALUES (%s, %s) 是占位符，用于防止 SQL 注入攻击
    sql = 'INSERT INTO users(name, age) VALUES(%s, %s)'
    # 将 name 和 age 打包成一个元组，作为插入 SQL 语句的参数。它会被替换为 sql 中的占位符 %s。
    val=(name, age)
    # 执行sql语句，将传入的 val 代入到占位符中，完成插入操作
    cursor.execute(sql, val)
    # 提交事务。MySQL 默认使用事务机制。commit() 方法用于提交当前事务，确保插入操作生效。
    # 如果没有调用 commit()，插入操作将不会被保存到数据库中。
    db.commit()
    # 输出插入了几条数据
    print(f'Insert {cursor.rowcount} records.')

# 查询数据
def fetch_users():
    cursor.execute("SELECT * FROM users")
    result = cursor.fetchall() # 将结果返回成一个列表，里面元素是每一行的内容，且打包成了元组
    for row in result:
        print(row)

# 更改数据
def update_user(user_id, name, age):
    sql = "UPDATE users SET name=%s, age=%s WHERE id=%s"
    val = (name, age, user_id)
    cursor.execute(sql, val)
    db.commit()
    print(f"Updated {cursor.rowcount} records.")

# 删除数据
def delete_user(user_id):
    sql = "DELETE FROM users WHERE id = %s"
    val=(user_id,) # 这里要求必须是元组类型，所以必须加一个逗号表示是元组
    cursor.execute(sql, val)
    db.commit()
    print(f"delete {cursor.rowcount} records.")

if __name__ == '__main__':

    #建立连接对象
    db = mysql.connector.connect(
        host='172.16.183.102', # 在k8s中用nodePort暴露了一个mysql服务，实验中就用这个
        port='30006', # 默认找3306端口，如果不是需要显式指定端口号
        user='root',
        password='111111',
        database='test_db',
    )

    # 创建游标对象，代表了数据库操作的上下文。允许我们用过它来执行SQL查询语句。
    # 对数据库的sql语句都是基于cursor.execute()方法实现的
    cursor = db.cursor()

    #插入数据
    insert_user('Alice', 30)
    insert_user('Bob', 25)
    fetch_users()

    #更新数据
    update_user(1, 'Smith', 12)
    fetch_users()

    #删除数据
    delete_user(2)
    fetch_users()

    # 关闭游标和连接
    cursor.close()
    db.close()
~~~

### %s占位符的作用

在 MySQL 的 Python 客户端中，`%s` 是一种占位符，用于参数化 SQL 查询。它的主要作用是将用户输入的值安全地绑定到 SQL 语句中，而不是直接拼接到 SQL 字符串中。这种机制可以有效地防止 SQL 注入攻击。

#### `%s` 的工作原理

1. 占位符的定义:
   - 在 SQL 查询中，`%s` 是一个占位符，表示一个参数的位置。
   - 它不会直接插入用户提供的值，而是作为一个标记，告诉数据库驱动程序在执行 SQL 时将参数值绑定到该位置。

2. 参数绑定:
   - 当调用 `cursor.execute(sql, val)` 时，`val` 中的参数会被安全地绑定到 SQL 语句中的 `%s`。
   - 数据库驱动程序会对参数进行转义和处理，确保它们被视为**数据**而不是**SQL 代码**。

3. 执行流程:
   - 例如，以下代码：
     ```python
     sql = "INSERT INTO users(name, age) VALUES(%s, %s)"
     val = ("Alice", 30)
     cursor.execute(sql, val)
     ```
     会被数据库驱动程序转换为类似以下的安全 SQL：
     ```sql
     INSERT INTO users(name, age) VALUES('Alice', 30)
     ```
     参数 `"Alice"` 和 `30` 被安全地插入，而不是直接拼接到 SQL 字符串中。

---

#### 为什么 `%s` 能阻止 SQL 注入攻击？

SQL 注入攻击的核心是通过恶意输入将额外的 SQL 代码插入到查询中，从而改变查询的逻辑。例如：
```sql
SELECT * FROM users WHERE name = 'Alice'; DROP TABLE users; --'
```
如果直接拼接用户输入到 SQL 中，攻击者可以通过输入类似 `"Alice'; DROP TABLE users; --"` 来破坏数据库。

使用 `%s` 占位符可以防止这种情况，原因如下：

1. 参数转义:
   - 数据库驱动程序会对参数进行转义，将特殊字符（如单引号 `'`）处理为普通数据，而不是 SQL 代码。
   - 例如，输入 `"Alice'; DROP TABLE users; --"` 会被转义为：
     ```sql
     SELECT * FROM users WHERE name = 'Alice\'; DROP TABLE users; --'
     ```
     这样，恶意代码不会被执行。

2. 分离数据与代码：
   - 参数化查询将数据与 SQL 代码分离，**用户输入的值始终被视为数据**，而不是 SQL 代码的一部分。
   - 即使用户输入了恶意字符串，也无法改变 SQL 的逻辑。

3. 防止拼接漏洞:
   
   - 如果直接拼接字符串，SQL 查询会变得不安全。例如：
     ```python
     sql = f"SELECT * FROM users WHERE name = '{name}'"
     ```
     如果 `name` 的值是 `"Alice'; DROP TABLE users; --"`，最终的 SQL 会变成：
     ```sql
     SELECT * FROM users WHERE name = 'Alice'; DROP TABLE users; --'
     ```
     而使用 `%s` 占位符时，恶意输入会被转义，无法破坏查询逻辑。

---

#### 示例对比

**不安全的拼接方式：**

```python
name = "Alice'; DROP TABLE users; --"
sql = f"SELECT * FROM users WHERE name = '{name}'"
cursor.execute(sql)
```
最终的 SQL 会执行恶意代码，导致数据库表被删除。

**安全的参数化查询：**

```python
name = "Alice'; DROP TABLE users; --"
sql = "SELECT * FROM users WHERE name = %s"
cursor.execute(sql, (name,))
```
最终的 SQL 会被安全处理为：
```sql
SELECT * FROM users WHERE name = 'Alice\'; DROP TABLE users; --'
```
恶意代码不会被执行。
