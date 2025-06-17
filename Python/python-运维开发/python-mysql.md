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

~~~sh
wget http://repo.mysql.com/mysql-community-release-el7-5.noarch.rpm
rpm -ivh mysql-community-release-el7-5.noarch.rpm
yum install mysql-server -y
chown mysql:mysql -R /var/lib/mysql
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
mysql> grant all on *.* to 'root'@'%' identified by '111111';
flush privileges;
~~~

