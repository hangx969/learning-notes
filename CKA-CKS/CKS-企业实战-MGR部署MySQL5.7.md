# MySQL高可用工具

## MGR

- MGR（MySQL Group Replication）是一种数据库集群技术，允许多个 MySQL 服务器协同工作，形成一个高可用的数据库集群。当一个mysql出现故障时，其他mysql可以继续工作，确保服务的连续性和数据的高可用性。
- MGR允许多个 MySQL 实例组成一个组，这些实例之间会自动同步数据，确保数据的一致性和高可用性。如果某个实例出现故障，其他实例会继续工作，从而保持服务的连续性。
- MGR是mysql原生带有的，不需要安装插件。MGR集群也有一些限制和要求，例如需要使用InnoDB存储引擎。

> 适用于需要高度自动化和数据一致性的场景。它提供了内置的高可用性解决方案，适合不希望依赖第三方工具的用户。

## MMM

- MMM（MySQL Multi-Master Replication Manager）是一种用于管理 MySQL 主从复制的工具。它允许你配置多个主节点和从节点，并在主节点发生故障时自动进行故障转移。MMM 可以帮助你实现读写分离，提升系统性能。

> 适用于需要复杂复制拓扑和读写分离的场景。它允许配置多个主节点和从节点，但需要手动管理和监控。

## MHA

- MHA（Master High Availability Manager and tools）MHA 是一种用于 MySQL 主从复制环境中的高可用性管理工具。它在主节点发生故障时，能够自动选举一个新的主节点，并重新配置复制关系，从而实现快速故障转移。

> 适用于需要快速故障转移和高可用性的主从复制环境。它能够自动处理主节点故障，但不支持多主复制。

# 部署MGR一主多从集群

## 环境准备

| IP             | hostname        | Port | ServerID | OS         |
| -------------- | --------------- | ---- | -------- | ---------- |
| 192.168.40.100 | xianchaomaster1 | 3306 | 63       | CentOS 7.9 |
| 192.168.40.101 | xianchaomaster2 | 3306 | 64       | CentOS 7.9 |
| 192.168.40.102 | xianchaomaster3 | 3306 | 62       | CentOS 7.9 |

## 安装mysql

- 配置三台hosts文件

~~~sh
tee -a /etc/hosts <<'EOF'
192.168.40.102    xianchaomaster3
192.168.40.100    xianchaomaster1
192.168.40.101    xianchaomaster2
EOF
~~~

- 安装mysql

~~~sh
#所有节点，上传预先准备好的压缩包：mysql-5.7.tar.gz，包括了安装mysql5.7主要的软件包
tar xvf mysql-5.7.tar.gz
yum -y install ./mysql*.rpm
systemctl start mysqld
#启动MySQL会生成临时密码。
#在MySQL的配置文件/etc/my.cnf中关闭密码强度审计插件，并重启MySQl服务。
vim /etc/my.cnf	
#修改MySQL的配置文件，在[myqld]标签处末行添加以下项：
validate-password=OFF     	#不使用密码审计插件

systemctl restart mysqld
grep 'password'  /var/log/mysqld.log #获取临时密码。
~~~

- 登录mysql修改root密码

~~~mysql
mysql -u root -p'buL.UJp!T2Od' #使用临时密码登录MySQl，注意临时密码要引号
mysql> set password for root@localhost = password('123456');		
#修改root用户密码为123456
mysql> use mysql;
mysql> update user set host = '192.168.40.%' where user = 'root';
mysql> update user set host = '%' where user = 'root';
mysql> flush privileges;
~~~

## 配置master1主节点

~~~sh
#group_name可以通过uuidgen生成
uuidgen

#服务器xianchaomaster1配置/etc/my.cnf
#参考：官网配置https://dev.mysql.com/doc/refman/5.7/en/group-replication-configuring-instances.html
vim /etc/my.cnf   
#在  [mysqld] 配置组中，增加以下红色内容：
server_id = 63 
#这个设置给当前 MySQL 服务分配了一个唯一的标识号码，用来在复制和集群中区分不同的服务。
gtid_mode = ON 
#开启全局事务标识（GTID），用于在数据库复制和高可用性方案中确保事务的唯一性和一致性。
enforce_gtid_consistency = ON       
#强制 GTID 一致性，确保所有数据库节点上执行的事务顺序和一致性。
master_info_repository = TABLE 
#将主数据库的元数据（如位置信息）保存在系统表中，以便管理和复制时使用。
relay_log_info_repository = TABLE   
#将中继日志的元数据（如位置信息）也保存在系统表中，用于复制进程的管理和监控。
binlog_checksum = NONE  		
#禁用二进制日志事件的校验，简化日志记录过程。
log_slave_updates = ON  		
#允许从服务器也记录其接收和执行的更改，支持级联复制（即从服务器再次作为主服务器向下游复制）。
log_bin = binlog 
#开启二进制日志记录，将数据库的更改以二进制格式记录下来，以便复制和恢复。
binlog_format = ROW  		
#以行的格式记录二进制日志，记录每行数据的变化，有助于准确复制数据的变更。
plugin_load_add='group_replication.so'   
#加载并启用 MySQL 的组复制插件，用于实现多个数据库实例之间的同步和协作。
transaction_write_set_extraction=XXHASH64  
#使用哈希算法将事务写入集提取为散列，有助于数据库更有效地处理和记录事务。
group_replication_group_name="ce9be252-2b71-11e6-b8f4-00212844f856"
#设置组复制的唯一标识符，确保每个参与组复制的数据库实例都能识别并加入正确的组。 
group_replication_start_on_boot=off  
#设置数据库实例不会在启动时自动加入组复制，需要手动控制启动过程。
group_replication_local_address="xianchaomaster1:33063"  
#指定本地 MySQL 实例接受其他组成员的连接的地址和端口号。
group_replication_group_seeds="xianchaomaster1:33063, xianchaomaster2:33064, xianchaomaster3:33062" 
#指定组成员的地址和端口，用于初始化组复制中的初始通信和连接。
group_replication_bootstrap_group=off 
#禁用组引导功能，避免在启动时自动创建一个新的复制组。

#重启MySQL服务
systemctl restart mysqld
~~~

> 这是一个MySQL配置文件中的一些配置参数，用于配置MySQL服务器的行为。下面是对这些参数的详细解释和通俗解释：
>
> 1. server_id = 63：
>    解释：这是MySQL服务的唯一标识号，每个MySQL服务在集群中必须具有唯一的server_id。
>    通俗解释：每个MySQL服务都像一个独特的身份证号码一样，以便在集群中识别和区分不同的服务器。
> 2. gtid_mode = ON：
>    解释：启用全局事务标识（GTID）模式，用于跟踪数据库中的事务。
>    通俗解释：开启了一个全球唯一的事务ID，可以用来标识数据库中的每个事务，有助于跟踪和管理数据库复制。
> 3. enforce_gtid_consistency = ON：
>    解释：强制GTID的一致性，确保在复制过程中每个事务都得到一致性的处理。
>    通俗解释：确保在数据库复制时，所有事务都以一致的方式被复制到其他服务器，以避免数据不一致问题。
> 4. master_info_repository = TABLE 和 relay_log_info_repository = TABLE：
>    解释：将关于主服务器和中继日志的元数据信息存储在系统表中。
>    通俗解释：将有关主服务器和中继日志的一些关键信息保存在MySQL系统表中，以便服务器能够管理和访问这些信息。
> 5. binlog_checksum = NONE：
>    解释：禁用二进制日志事件校验，不对二进制日志的内容进行校验。
>    通俗解释：关闭了对二进制日志的数据完整性检查，可能会提高性能，但要小心数据一致性问题。
> 6. log_slave_updates = ON：
>    解释：开启从服务器上的二进制日志记录，允许从服务器成为其他服务器的主服务器。
>    通俗解释：从服务器可以记录自己的二进制日志，允许其他服务器复制这个从服务器的数据。
> 7. log_bin = binlog 和 binlog_format = ROW：
>    解释：开启二进制日志记录，以行的格式记录日志。
>    通俗解释：将数据库的更改操作以二进制形式记录，以行的方式记录每个操作的详细信息。
> 8. plugin_load_add='group_replication.so'：
>    解释：加载MySQL插件，具体是group_replication.so插件，用于启用组复制。
>    通俗解释：启用一个名为group_replication.so的插件，用于启用MySQL的组复制功能。
> 9. transaction_write_set_extraction=XXHASH64：
>    解释：使用哈希算法将事务写入集提取为散列。
>    通俗解释：用一种特定的哈希算法来处理事务的写入操作。
> 10. group_replication_group_name="ce9be252-2b71-11e6-b8f4-00212844f856"：
>     解释：设置组复制集群的名称。
>     通俗解释：为组复制集群起一个唯一的名称，以便其他服务器可以加入这个集群。
> 11. group_replication_start_on_boot=off：
>     解释：禁用在启动时自动启用组复制集群。
>     通俗解释：不要在服务器启动时自动开始组复制，需要手动启用。
> 12. group_replication_local_address="xianchaomaster1:33063"：
>     解释：配置本地服务器用于接受来自组中成员的传入连接的地址和端口。
>     通俗解释：指定服务器在哪个IP地址和端口上接收其他组成员的连接请求。
> 13. group_replication_group_seeds="xianchaomaster1:33063, xianchaomaster2:33064, xianchaomaster3:33062"：
>     解释：配置组中成员访问表，以便它们可以互相发现和连接。
>     通俗解释：告诉服务器在哪些IP地址和端口上可以找到其他组成员，以便它们可以建立连接。
> 14. group_replication_bootstrap_group=off：
>     解释：禁用引导组功能，不要启动新的组。
>     通俗解释：不要启动一个新的组，而是让服务器加入一个已经存在的组。

- master1配置复制账号

~~~mysql
mysql -u root -p123456
mysql> set SQL_LOG_BIN=0;   	#停掉日志记录
mysql> grant replication slave on *.* to repl@'192.168.40.%' identified by '123456';
#创建一个用户名为 repl 的用户，并允许该用户从 192.168.40.* 范围内的任何 IP 地址以123456这个密码连接到 MySQL 服务，同时授予该用户进行数据复制所需的权限

mysql> grant replication slave on *.* to repl@'%' identified by '123456';
#创建一个用户repl，后期用于其他节点，同步数据。

mysql> flush privileges; #重新加载授权表，从而使对用户权限所做的更改立即生效
mysql> set SQL_LOG_BIN=1;  	#开启日志记录
~~~

> 注：为什么创建repl用户需要关闭二进制日志功能? 创建成功后，再开启？
>
> 因为用于同步数据的用户名repl和密码，必须在所有节点上有，且用户名和密码必须一样。所以，创建用户和密码时，先关闭二进制日志功能，这样不产生二进制日志数据。创建成功后，再开启二进制日志功能。这样repl用户信息，每台机器上都有了，而且不会在MGR同步数据时产生冲突。

~~~mysql
mysql> change master to master_user='repl',master_password='123456'  for channel 'group_replication_recovery';
~~~

> 这条 SQL 语句用于配置 MySQL 实例作为组复制的从节点，以便从主节点获取复制数据。以下是它的解释说明：
>
> CHANGE MASTER TO: 这是 MySQL 的命令，用于修改从节点的复制配置。
>
> MASTER_USER='repl': 指定连接主节点的用户名为 repl，这是一个在主节点上用于复制的已授权用户。
>
> MASTER_PASSWORD='123456': 指定连接主节点的密码，这里设置为 123456，以确保从节点能够安全地连接到主节点进行数据复制。
>
> FOR CHANNEL 'group_replication_recovery': 指定这个配置是为名为 group_replication_recovery 的复制通道进行的。在MySQL 组复制中，每个从节点都会为复制通道分配一个唯一的标识符，这里使用通道名称来区分不同的复制配置。

~~~mysql
#查看MySQL服务器xianchaomaster1上安装的group replication插件，这个组件在my.cnf配置文件中，plugin_load_add='group_replication.so'有指定。
mysql> show plugins;
#如果没有安装成功，可以执行这个命令，手动再次安装：安装插件
mysql> install PLUGIN group_replication SONAME 'group_replication.so';
#启动服务器xianchaomaster1上MySQL的group replication
#设置group_replication_bootstrap_group为ON，表示这台机器是集群中的master，以后加入集群的服务器都是salve。引导只能由一台服务器完成。
mysql> set global group_replication_bootstrap_group=ON; 
~~~

- 作为首个节点启动mgr集群

  ```sh
  mysql> start group_replication;
  mysql> set global group_replication_bootstrap_group=OFF;   #启动成功后，这台服务器已经是master了。有了master后，引导器就没有用了，就可以关闭了。
  ```

- 查看mgr的状态

  ```mysql
  #查询表performance_schema.replication_group_members
  mysql> select * from performance_schema.replication_group_members;
  ```

- 测试服务器xianchaomaster1上的MySQL

  ```mysql
  mysql> create database test;
  mysql> use test;
  mysql> create table t1 (id int primary key,name varchar(20));  #注意创建主键
  mysql> insert into t1 values (1,'man');
  mysql> select * from t1;
  mysql> show binlog events;
  ```

## 集群中添加master2主机

- 复制组添加新实例xianchaomaster2

  ```mysql
  #在master2上面，修改/etc/my.cnf 配置文件，方法和之前相同。 
  vim /etc/my.cnf   #在mysqld配置，追加以下内容
  
  server_id=64  #注意服务ID不能一样
  gtid_mode=ON
  enforce_gtid_consistency=ON
  master_info_repository=TABLE
  relay_log_info_repository=TABLE
  binlog_checksum=NONE
  log_slave_updates=ON
  log_bin=binlog
  binlog_format=ROW
  
  plugin_load_add='group_replication.so'
  transaction_write_set_extraction=XXHASH64
  group_replication_group_name="ce9be252-2b71-11e6-b8f4-00212844f856"  #这保持和master一样
  group_replication_start_on_boot=off
  group_replication_local_address="xianchaomaster2:33064"   #以本机端口33064接受来自组中成员的传入连接
  group_replication_group_seeds="xianchaomaster1:33063, xianchaomaster2:33064, xianchaomaster3:33062" #组成员列表
  group_replication_bootstrap_group=off
  ```

  ~~~sh
  systemctl restart mysqld
  ~~~

- 用户授权

~~~mysql
mysql -u root -p123456
mysql> set SQL_LOG_BIN=0;   #停掉日志记录
mysql> grant replication slave on *.* to repl@'192.168.40.%' identified by '123456';
mysql> grant replication slave on *.* to repl@'%' identified by '123456';
mysql> flush privileges;
mysql> set SQL_LOG_BIN=1;  #开启日志记录
mysql> change master to master_user='repl',master_password='123456'  for channel 'group_replication_recovery';  #构建group replication集群
~~~

- 把实例添加到之前的复制组

~~~mysql
#master2上
mysql> set global group_replication_allow_local_disjoint_gtids_join=ON;
mysql> start group_replication;
#去master1上面查看复制组状态
mysql> select * from performance_schema.replication_group_members;
#master2上可以看到数据已经同步
mysql> select * from test.t1;
~~~

## 集群中标添加master3主机

- 修改配置

~~~sh
#master3上
vim /etc/my.cnf
server_id=62  #注意服务id不一样
gtid_mode=ON
enforce_gtid_consistency=ON
master_info_repository=TABLE
relay_log_info_repository=TABLE
binlog_checksum=NONE
log_slave_updates=ON
log_bin=binlog
binlog_format=ROW

plugin_load_add='group_replication.so'
transaction_write_set_extraction=XXHASH64
group_replication_group_name="ce9be252-2b71-11e6-b8f4-00212844f856"
group_replication_start_on_boot=off
group_replication_local_address="xianchaomaster3:33062"
group_replication_group_seeds="xianchaomaster1:33063, xianchaomaster2:33064, xianchaomaster3:33062"
group_replication_bootstrap_group=off

systemctl restart mysqld
~~~

- 用户授权

~~~mysql
#用户授权
mysql -u root -p123456
mysql> set SQL_LOG_BIN=0;   #停掉日志记录
mysql> grant replication slave on *.* to repl@'192.168.40.%' identified by '123456';
mysql> grant replication slave on *.* to repl@'%' identified by '123456';
mysql> flush privileges;
mysql> set SQL_LOG_BIN=1;  #开启日志记录
mysql> change master to master_user='repl',master_password='123456'  for channel 'group_replication_recovery';  #构建group replication集群
~~~

- 添加到复制组

~~~mysql
#把实例添加到之前的复制组
mysql> set global group_replication_allow_local_disjoint_gtids_join=ON;
mysql> start group_replication;

#在xianchaomaster1上查看复制组状态
mysql> select * from performance_schema.replication_group_members;
~~~

## 测试集群读写

~~~mysql
#xianchaomaster1查看集群参数设置列表：
mysql> show variables like 'group_replication%';
#显示与组复制（Group Replication）相关的系统变量的信息。

#查看xianchaomaster1是否只读，发现xianchaomaster1 master，可读可写。
mysql> show variables like '%read_only%';
#另外两台查看，发现xianchaomaster2和xianchaomaster3，是只读的
mysql>  show variables like '%read_only%';
~~~

# Multi-primary多主模式实现多节点同时读写

## 由单主模式修改为多主模式

~~~mysql
#1、关闭xianchaomaster1单主模式，在原来单主模式的主节点执行操作如下：
mysql -u root -p123456
mysql> stop GROUP_REPLICATION;
mysql> set global group_replication_single_primary_mode=OFF;
#关闭单master模式
mysql> set global group_replication_enforce_update_everywhere_checks=ON;
#设置多主模式下各个节点严格一致性检查，启用了这个功能，MySQL 将会在执行更新操作前检查所有节点，确保更新操作在所有节点都能够成功执行，以避免数据不一致的情况发生。
mysql> SET GLOBAL group_replication_bootstrap_group=ON; #启动组复制的引导过程
mysql> START GROUP_REPLICATION; #这条命令启动了组复制。在引导过程中，此命令用于启动组复制服务，使得当前 MySQL 实例可以加入到已经存在的复制组中，或者创建一个新的复制组。
mysql> SET GLOBAL group_replication_bootstrap_group=OFF; #关闭组复制的引导模式
~~~

~~~mysql
#2、master2上
mysql -u root -p123456
mysql> stop GROUP_REPLICATION;
mysql> set global group_replication_allow_local_disjoint_gtids_join=ON; #允许本地节点加入即使 GTIDs 不完全一致，可以在某些情况下（如节点数据恢复或加入新节点时）帮助系统更灵活地进行复制管理和数据同步。
mysql> set global group_replication_single_primary_mode=OFF;
mysql> set global group_replication_enforce_update_everywhere_checks=ON;
mysql> start group_replication;
#查看是否只读的参数
mysql> show variables like '%read_only%';
~~~

~~~mysql
#3、master3上
mysql -u root -p123456
mysql> stop GROUP_REPLICATION;
mysql> set global group_replication_allow_local_disjoint_gtids_join=ON;
mysql> set global group_replication_single_primary_mode=OFF;
mysql> set global group_replication_enforce_update_everywhere_checks=ON;
mysql> start group_replication;
mysql> show variables like '%read_only%';
~~~

## 测试集群读写

~~~mysql
#查看组复制成员
mysql> select * from performance_schema.replication_group_members;
#测试 Multi-primary多主模式实现多节点同时读写
#xianchaomaster1上执行
mysql> insert into test.t1 values (2,'aa');
#xianchaomaster2上执行：
mysql> insert into test.t1 values (3,'cc');
#xianchaomaster3上执行： 
mysql> insert into test.t1 values (6,'cc');
mysql> select * from test.t1;
~~~

## 测试节点故障

~~~mysql
#测试MGR集群中一些节点坏了， 数据还可以正常读写
#xianchaomaster1
systemctl stop mysqld
#xianchaomaster3
systemctl stop mysqld
#xianchaomaster2
mysql -u root -p123456
mysql> select * from performance_schema.replication_group_members;
mysql> insert into test.t1 values (5,'ff');
mysql> select * from test.t1;

#master1\3重新加回到集群
systemctl start mysqld
mysql -u root -p123456
mysql> select * from test.t1;
mysql> stop GROUP_REPLICATION;
mysql> set global group_replication_allow_local_disjoint_gtids_join=ON;
mysql> set global group_replication_single_primary_mode=OFF;
mysql> set global group_replication_enforce_update_everywhere_checks=ON;
mysql> start group_replication;
mysql> select * from test.t1;
mysql> select * from performance_schema.replication_group_members;
~~~

# 基于nginx+keepalived实现MGR Mysql高可用

## 安装nginx主备

~~~sh
#master1\2上安装nginx
yum install epel-release -y
yum install nginx-mod-stream -y
yum install nginx keepalived -y
~~~

~~~sh
#主备修改配置文件
tee /etc/nginx/nginx.conf <<'EOF'
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /run/nginx.pid;

include /usr/share/nginx/modules/*.conf;

events {
    worker_connections 1024;
}

# 四层负载均衡，为两台Master apiserver组件提供负载均衡
stream {

    log_format  main  '$remote_addr $upstream_addr - [$time_local] $status $upstream_bytes_sent';

    access_log  /var/log/nginx/k8s-access.log  main;

    upstream mysql-server {
       server 192.168.40.100:3306 weight=5 max_fails=3 fail_timeout=30s; 
       server 192.168.40.101:3306 weight=5 max_fails=3 fail_timeout=30s;   
       server 192.168.40.102:3306 weight=5 max_fails=3 fail_timeout=30s;  
    }
    
    server {
       listen 13306; # 由于nginx与master节点复用，这个监听端口不能是3306，否则会冲突
       proxy_pass mysql-server;
    }
}

http {
    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile            on;
    tcp_nopush          on;
    tcp_nodelay         on;
    keepalive_timeout   65;
    types_hash_max_size 2048;

    include             /etc/nginx/mime.types;
    default_type        application/octet-stream;

    server {
        listen       80 default_server;
        server_name  _;

        location / {
        }
    }
}
EOF
~~~

## keepalived配置

~~~sh
#master1主keepalived
tee /etc/keepalived/keepalived.conf <<'EOF'
global_defs { 
   notification_email { 
     acassen@firewall.loc 
     failover@firewall.loc 
     sysadmin@firewall.loc 
   } 
   notification_email_from Alexandre.Cassen@firewall.loc  
   smtp_server 127.0.0.1 
   smtp_connect_timeout 30 
   router_id NGINX_MASTER
} 

vrrp_script check_nginx {
    script "/etc/keepalived/check_nginx.sh"
}

vrrp_instance VI_1 { 
    state MASTER 
    interface ens33  # 修改为实际网卡名
    virtual_router_id 51 # VRRP 路由 ID实例，每个实例是唯一的 
    priority 100    # 优先级，备服务器设置 90 
    advert_int 1    # 指定VRRP 心跳包通告间隔时间，默认1秒 
    authentication { 
        auth_type PASS      
        auth_pass 1111 
    }  
    # 虚拟IP
    virtual_ipaddress { 
        192.168.40.199/24
    } 
    track_script {
        check_nginx
    } 
}
EOF
#vrrp_script：指定检查nginx工作状态脚本（脚本返回状态码（0为工作正常，非0不正常）判断是否故障转移。）
~~~

~~~sh
#master2备keepalived
tee /etc/keepalived/keepalived.conf <<'EOF' 
global_defs { 
   notification_email { 
     acassen@firewall.loc 
     failover@firewall.loc 
     sysadmin@firewall.loc 
   } 
   notification_email_from Alexandre.Cassen@firewall.loc  
   smtp_server 127.0.0.1 
   smtp_connect_timeout 30 
   router_id NGINX_BACKUP
} 

vrrp_script check_nginx {
    script "/etc/keepalived/check_nginx.sh"
}

vrrp_instance VI_1 { 
    state BACKUP 
    interface ens33
    virtual_router_id 51 # VRRP 路由 ID实例，每个实例是唯一的 
    priority 90
    advert_int 1
    authentication { 
        auth_type PASS      
        auth_pass 1111 
    }  
    virtual_ipaddress { 
        192.168.40.199/24
    } 
    track_script {
        check_nginx
    } 
}
EOF
~~~

~~~sh
#主备添加判断nginx存活的脚本
tee /etc/keepalived/check_nginx.sh <<'EOF' 
#!/bin/bash
#1、判断Nginx是否存活
counter=`ps -C nginx --no-header | wc -l`
if [ $counter -eq 0 ]; then
    #2、如果不存活则尝试启动Nginx
    service nginx start
    sleep 2
    #3、等待2秒后再次获取一次Nginx状态
    counter=`ps -C nginx --no-header | wc -l`
    #4、再次进行判断，如Nginx还不存活则停止Keepalived，让地址进行漂移
    if [ $counter -eq 0 ]; then
        service  keepalived stop
    fi
fi 
EOF
chmod +x /etc/keepalived/check_nginx.sh
~~~

## 启动服务

~~~sh
#主备
systemctl daemon-reload
systemctl enable nginx keepalived
systemctl start nginx
systemctl start keepalived
~~~

~~~sh
#测试通过VIP访问mysql
mysql -uroot -h192.168.40.199 -P13306 -p
#输入密码：123456可以访问MySQL。
#模拟xianchaomaster1、xianchaomaster2、xianchaomaster3机器任意两个mysql被停掉，基于VIP均可访问mysql
~~~

