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
