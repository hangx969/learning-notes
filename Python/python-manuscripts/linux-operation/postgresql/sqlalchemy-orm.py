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
