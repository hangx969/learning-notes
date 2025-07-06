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



# Postgresql操作

To minimize manual operations in traditional service maintenance and enhance efficiency/stability, this project developed a localized automation toolkit for operational management.

- GUI Desktop Application (Python + Tkinter)
  - Manages services: Nginx, Tomcat, MySQL, httpd, K8s
  - Features:
    - Service control (start/stop)
    - Log collection
    - Process monitoring
    - Configuration management
    - Bulk updates & auto-scaling of Kubernetes resources
- Performance Monitoring & Inspection Scripts
  - Collects Linux metrics: CPU/Memory/Disk utilization

Project Link:

https://github.com/hangx969/python-operation-scripts
