# PostgreSQL介绍

PostgreSQL 是一个开源的关系型数据库管理系统（RDBMS），它遵循 SQL 标准，并且支持多种高级功能，如事务管理、外键、视图、触发器等。PostgreSQL 被广泛应用于各种场景，尤其适用于需要处理复杂查询和事务的应用程序。它的特点包括支持 JSON 数据类型、强大的查询优化器、并行查询等。

**PostgreSQL 更注重标准符合性、功能丰富性和扩展性（支持复杂类型、自定义函数等），适合复杂查询和高级应用；MySQL 更侧重简单易用、读写速度快和成熟稳定，尤其擅长高并发 OLTP 场景（如 Web 应用）。**

## 安装

~~~sh
# 1）安装基础包
yum install postgresql-server postgresql-contrib -y

# 2）初始化PostgreSQL数据库：
sudo postgresql-setup --initdb

# 3）启动并启用PostgreSQL服务：
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 4）配置PostgreSQL允许远程访问
# 编辑PostgreSQL的配置文件pg_hba.conf和postgresql.conf以允许远程访问。
sudo vim /var/lib/pgsql/data/pg_hba.conf
# 在文件最后添加如下几行，允许所有ip访问：
host    all             all             0.0.0.0/0               md5

sudo vim /var/lib/pgsql/data/postgresql.conf
#找到listen_addresses并将其修改为：
listen_addresses = '*'

#5）重启PostgreSQL服务
sudo systemctl restart postgresql

#6）创建数据库和用户
# 切换到postgres用户并创建数据库和用户：
sudo -i -u postgres
psql

#在psql中执行以下命令：
CREATE DATABASE mydatabase;
CREATE USER myuser WITH ENCRYPTED PASSWORD 'mypassword';
GRANT ALL PRIVILEGES ON DATABASE mydatabase TO myuser;
\q
#退出psql并返回普通用户：exit
~~~

## 基本增删改查

~~~sh
# 1）查看所有数据库：
\l

# 2）连接到某个数据库：
\c <数据库名>

# 3）查看当前数据库中的所有表：
\dt

# 4）查看表的结构（列名、数据类型等）：
\d <表名>

# 5）查看表中的所有数据：
SELECT * FROM <表名>;

# 6）删除表
DROP TABLE <表名>

# 1）删除数据库
DROP DATABASE <数据库名>;
~~~

# Postgresql操作

## 安装psycopg2

~~~sh
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple psycopg2
~~~

## python实现增删改查

~~~python
import psycopg2
from psycopg2 import sql

# 数据库连接参数
conn_params = {
    'dbname': 'mydatabase',
    'user': 'myuser',
    'password': 'mypassword',
    'host': '192.168.40.80',  # 替换为你的服务器IP
    'port': 5432
}

# 连接数据库
conn = psycopg2.connect(**conn_params)
cur = conn.cursor()

# 创建表
create_table_query = """
CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    position VARCHAR(100),
    salary INT
);
"""
cur.execute(create_table_query)
conn.commit()

# 插入数据
insert_query = sql.SQL("INSERT INTO employees (name, position, salary) VALUES (%s, %s, %s)")
cur.execute(insert_query, ('John Doe', 'Software Engineer', 70000))
cur.execute(insert_query, ('Jane Smith', 'Data Scientist', 80000))
conn.commit()

# 查询数据
cur.execute("SELECT * FROM employees")
rows = cur.fetchall()
print("Employees:")
for row in rows:
    print(row)

# 更新数据
update_query = sql.SQL("UPDATE employees SET salary = %s WHERE name = %s")
cur.execute(update_query, (75000, 'John Doe'))
conn.commit()

# 删除数据
delete_query = sql.SQL("DELETE FROM employees WHERE name = %s")
cur.execute(delete_query, ('Jane Smith',))
conn.commit()

# 再次查询数据
cur.execute("SELECT * FROM employees")
rows = cur.fetchall()
print("Employees after update and delete:")
for row in rows:
    print(row)

# 关闭连接
cur.close()
conn.close()
~~~

# SQLAlchemy与ORM框架操作Postgresql

SQLAlchemy 是一个 Python 的 ORM（对象关系映射）框架，它提供了简洁且强大的方式来操作关系型数据库。通过 SQLAlchemy，开发者可以使用 Python 对象来表示数据库中的表和数据，而不必直接编写 SQL 语句。

## 安装sqlalchemy

~~~python
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple sqlalchemy
~~~

## 代码

~~~python
# create_engine是sqlalchemy终的一个函数，用于创建一个数据库引擎，负责与数据库连接，并执行SQL语句
# Column、Integer、String都是SQLAlchemy终的路类型，用来定义数据库表的列和列的数据类型。
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
# sessionmaker这是sqlalchemy用来创建会话的工厂函数
from sqlalchemy.orm import sessionmaker

# 定义基类
# declarative_base是用于创建模型基类的函数。所有的ORM模型类（例如User类）都应该继承这个基类
# Base会提供一本功能，如将类与数据库表映射、生成SQL语句等
Base = declarative_base()

# 定义User模型，继承了Base，意味着这个类是SQLAlchemy ORM模型类，代表数据库中的一个表
class User(Base):
    __tablename__ = 'users'  # 对应数据库中的表名
    # 定义表结构
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    age = Column(Integer)
    # 定义了该类的字符串表示方式。可以自定义打印对象的显示格式，便于调试和输出。
    def __repr__(self):
        return f"<User(name={self.name}, age={self.age})>"

# 数据库连接URL
DATABASE_URL = 'postgresql://myuser:mypassword@192.168.40.80/aa'

# 创建数据库连接引擎
engine = create_engine(DATABASE_URL)

# 创建所有表。这个方法基于ORM模型类创建数据库表。SQL语句会自动生成。
Base.metadata.create_all(engine)

# 创建会话工厂，这是执行数据库增删改查操作的主要接口
Session = sessionmaker(bind=engine)

# 插入数据（增）
def add_user(name, age):
    session = Session() # 返回会话对象。
    new_user = User(name=name, age=age) # 创建一个User对象
    session.add(new_user) # 将新用户添加到会话中。此时还未保存到数据库。
    session.commit()  # 提交事务，实际上将User对象保存到数据库中。
    print(f"User {name} added successfully!")
    session.close() # 关闭会话连接

# 查询数据（查）
def get_user_by_name(name):
    session = Session()
    # 查询User表中的列，User是之前定义的ORM模型类。返回第一条记录。
    user = session.query(User).filter_by(name=name).first()
    if user:
        print(f"Found user: {user}")
    else:
        print(f"No user found with name {name}")
    session.close()

# 更新数据（改）
def update_user_age(name, new_age):
    session = Session()
    user = session.query(User).filter_by(name=name).first()
    if user:
        user.age = new_age
        session.commit()  # 提交事务
        print(f"User {name}'s age updated to {new_age}")
    else:
        print(f"No user found with name {name}")
    session.close()

# 删除数据（删）
def delete_user(name):
    session = Session()
    user = session.query(User).filter_by(name=name).first()
    if user:
        session.delete(user)
        session.commit()  # 提交事务
        print(f"User {name} deleted successfully!")
    else:
        print(f"No user found with name {name}")
    session.close()

# 主程序
if __name__ == "__main__":
    # 增：插入用户
    add_user('Alice', 30)
    add_user('Bob', 25)

    # 查：查询用户
    get_user_by_name('Alice')
    get_user_by_name('Charlie')  # 不存在的用户

    # 改：更新用户年龄
    update_user_age('Alice', 31)

    # 删：删除用户
    delete_user('Bob')
    delete_user('Charlie')  # 不存在的用户
~~~

