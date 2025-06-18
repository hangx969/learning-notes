import mysql.connector

# 插入数据
def insert_user(name, age):
    # 定义sql语句。VALUES (%s, %s) 是占位符，用于防止 SQL 注入攻击？
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
