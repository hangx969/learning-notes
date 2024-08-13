# redis使用场景

- 很多大型电商网站、视频直播和游戏应用等，存在大规模数据访问，对数据查询效率要求高，且数据结构简单，不涉及太多关联查询。这种场景使用Redis，在速度上对传统磁盘数据库有很大优势，能够有效减少数据库磁盘IO，提高数据查询效率，减轻管理维护工作量，降低数据库存储成本
- Redis对传统磁盘数据库是一个重要的补充，尤其是支持高并发访问的互联网应用必不可少的基础服务。电商网站的商品类目、推荐系统以及秒杀抢购活动，适宜使用Redis缓存数据库。

应用场景举例：

1. 秒杀抢购活动，并发高，对于传统关系型数据库来说访问压力大，需要较高的硬件配置（如磁盘IO）支撑。Redis数据库，单节点QPS支撑能达到10万，轻松应对秒杀并发。实现秒杀和数据加锁的命令简单，使用SET、GET、DEL、RPUSH等命令即可。

2. （视频直播）消息弹幕：直播间的在线用户列表，礼物排行榜，弹幕消息等信息，都适合使用Redis中的SortedSet结构进行存储。例如弹幕消息，可使用ZREVRANGEBYSCORE排序返回，在Redis 5.0中，新增了zpopmax，zpopmin命令，更加方便消息处理。
3. （游戏应用）游戏排行榜：在线游戏一般涉及排行榜实时展现，比如列出当前得分最高的10个用户。使用Redis的有序集合存储用户排行榜非常合适，有序集合使用非常简单，提供多达20个操作集合的命令。
4. （社交APP）返回最新评论/回复：在web类应用中，常有“最新评论”之类的查询，如果使用关系型数据库，往往涉及到按评论时间逆排序，随着评论越来越多，排序效率越来越低，且并发频繁。使用Redis的List（链表），例如存储最新1000条评论，当请求的评论数在这个范围，就不需要访问磁盘数据库，直接从缓存中返回，减少数据库压力的同时，提升APP的响应速度。

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202408131449085.png" alt="image-20240813144924033" style="zoom:50%;" />

# 下载链接

- 查看哪个是稳定版本：https://redis.io/download/

- 下载地址：https://download.redis.io/releases/

# 源码安装redis单节点-v6.2.6

> 7.2.3版本安装步骤相同

## 安装依赖

~~~sh
yum -y install cpp binutils glibc glibc-kernheaders glibc-common glibc-devel gcc make centos-release-scl devtoolset-9-gcc devtoolset-9-c++ devtoolset-9-binutils scl enable devtoolset-9
~~~

## 编译安装redis

~~~sh
#下载稳定版本的Redis包
wget https://download.redis.io/releases/redis-6.2.6.tar.gz	
tar -zxvf  redis-6.2.6.tar.gz								
cd redis-6.2.6/												
make -j 4		
#创建一个目录，作为redis安装目录
mkdir /usr/local/redis-6.2.6						
#正式安装Redis，加PREFIX参数指定Redis安装到/usr/local/redis-6.2.6目录下，如果不加的话直接执行make install的话，默认就会生成到/usr/local/bin下。
make PREFIX=/usr/local/redis-6.2.6 install 
cd /usr/local/redis-6.2.6
#redis的/usr/local/redis-6.2.6安装目录默认只有一个bin目录，为了规范一点，我们手动创建一下目录：
#创建3个目录,etc用于存放redis的主配置文件,logs目录存放redis日志,data用于存放redis的持久化数据
mkdir etc logs data
~~~

- Redis的启动需要指定配置文件，在我们解压的源码包里就有默认配置文件，为了方便，这里把它复制一份到Redis的安装目录下：

~~~sh
cp /redis-6.2.6/redis.conf /usr/local/redis-6.2.6/etc/
~~~

## 配置redis

- 默认的Redis配置文件是以前台的方式运行Redis，这里需要修改一下配置，让Redis启动的时候在后台守护进程方式运行，以及设置登陆密码等。

~~~sh
cd /usr/local/redis-6.2.6
grep -Ev "#|$^" etc/redis.conf #过滤出所有非注释行、非空行
#修改以下参数
bind 0.0.0.0	#设置哪些IP可以连接Redis-server，4个0表示全部外部计算机都可以连接，危险
port 6379 #Redis的默认端口6379
daemonize yes	#设置Redis启动为后台守护进程
pidfile /usr/local/redis-6.2.6/logs/redis_6379.pid	#pidfile的路径
loglevel notice										#日志级别
logfile /usr/local/redis-6.2.6/logs/redis_6379.log	#日志文件的路径
dir /usr/local/redis-6.2.6/data/					#持久化数据存放的目录
databases 16		#数据库的个数，默认16个
requirepass 123456	#设置客户端登陆密码
~~~

## 配置环境变量

~~~sh
vim ~/.bashrc
alias redis-cli='/usr/local/redis-6.2.6/bin/redis-cli'
alias redis-server='/usr/local/redis-6.2.6/bin/redis-server'
source ~/.bashrc
~~~

## 启动redis服务

~~~sh
cd /usr/local/redis-6.2.6/bin/
#启动Redis服务并指定配置文件
./redis-server  /usr/local/redis-6.2.6/etc/redis.conf
#查看6379端口占用
lsof -i:6379 
~~~

## 问题排查

~~~sh
#第一次启动redis可能会看到日志报下面的3个警告：
WARNING: The TCP backlog setting of 511 cannot be enforced because /proc/sys/net/core/somaxconn is set to the lower value of 128.
WARNING: overcommit_memory is set to 0! Background save may fail under low memory condition. To fix this issue add 'vm.overcommit_memory = 1' to /etc/sysctl.conf and then reboot or run the command 'sysctl vm.overcommit_memory=1' for this to take effect.
WARNING: you have Transparent Huge Pages (THP) support enabled in your kernel. This will create latency and memory usage issues with Redis. To fix thisissue run the command ‘echo never > /sys/kernel/mm/transparent_hugepage/enabled’ as root, and add it to your /etc/rc.local in order to retain thesetting after a reboot. Redis must be restarted after THP is disabled.

#按照提示解决即可：
vim /etc/sysctl.conf          
#添加下面2行
#指定内核参数，默认值128对于负载很大的服务是不够的,改为1024或2048或者更大
net.core.somaxconn = 1024       
#内存的分配策略，设置为1表示允许内核分配所有的物理内存
vm.overcommit_memory = 1       
#修改完成后保存执行：
sysctl -p

#使用root账号执行：
echo never > /sys/kernel/mm/transparent_hugepage/enabled
#为了防止重启服务器失效，将echo never > /sys/kernel/mm/transparent_hugepage/enabled添加到/etc/rc.local开机自启中即可。
~~~

## 连通性检查

~~~sh
#DB节点连接redis节点6379端口
./redis-cli -h 192.168.1.137 -p 6379
192.168.1.137:6379> auth 123456
~~~

# redis主从复制的部署

## 背景

- Redis 主从模式是一种在分布式系统中用于提高性能、可靠性和可扩展性的架构。在这种模式中，一个 Redis 服务器（主节点）可以有多个从节点，从而形成主从复制。

基础概念：

- 主节点（Master）：
  - 主节点是负责写入和读取的节点。所有写入操作都在主节点上进行。主节点将写入的数据同步到所有从节点。

- 从节点（Slave）：
  - 从节点复制主节点的数据，起到备份的作用。从节点可以接收读请求，分担主节点的读负载。
  - 从节点可以提供故障转移（failover）支持，即当主节点宕机时，其中一个从节点可以被提升为新的主节点。

复制方式：

- 主从复制是通过异步传播数据的方式进行的，即主节点将数据变更写入到本地 RDB 快照文件，并将快照文件和增量数据发送给从节点。

主从模式应用场景：

- 读写分离：
  - 主从模式允许将读请求分发到从节点，从而减轻主节点的读取压力。这对于读多写少的应用场景非常有用，提高了整体性能和响应速度。

- 数据备份和恢复：
  - 从节点可以用于实时数据备份，即通过复制主节点的数据，实现数据的实时备份。

- 横向扩展：
  - 当系统负载逐渐增加时，可以通过添加从节点来横向扩展系统性能。
  - 新增加的从节点可以帮助分担读取负载，而主节点则继续处理写入请求。

- 容灾和故障恢复：
  - 主从模式提供了容灾机制。当主节点发生故障时，可以迅速将一个从节点升级为主节点，确保系统的持续可用性。
  - 在主从模式下，即使主节点宕机，只要有足够的从节点，系统仍然可以继续提供读服务。

- 实时数据分析：
  - 通过在从节点上进行实时数据分析，可以避免对主节点的影响。
  - 从节点可以用于执行复杂查询、分析和报告生成，而主节点则专注于处理写入请求。

## 搭建主从集群

### 安装redis

- 见上述安装部分
- master节点：*192.168.1.137*；slave节点：*192.168.1.138*

### 配置master节点

~~~sh
vim /usr/local/redis-6.2.6/etc/redis.conf
#表示监听本机哪个网卡地址，因为我们要让slave能连接master，所以让redis监听在一个外部网卡而不仅仅是127.0.0.1
bind 192.168.1.137
#设置密码
requirepass 123456
~~~

### redis中多实例配置（作为slave节点）

- 指的是在同一台服务器上运行多个redis实例，每个实例采用不同的端口和数据目录

~~~sh
vim /usr/local/redis-6.2.6/etc/redis.conf
#至少修改以下参数
port 6380
pidfile /var/run/redis_6380.pid
logfile /usr/local/redis-6.2.6/logs/redis_6380.log
dir /usr/local/redis-6.2.6/data6380
#重启redis
redis-server 6380.conf
~~~

### 配置slave节点

~~~sh
vim 6379.conf
replicaof 192.168.1.137 6379    
#找到replicaof参数，这个是配置master IP和端口的,5.0之前的版本叫slaveof
masterauth 123456          
#如果master设置了密码，还要配置master的密码，这样slave才能连的上master
replica-read-only yes        
#slave只读，默认就是只读，保持默认即可，主从模式下master读写，slave只读
~~~

## 主从读写验证测试

- 登录master插入数据

~~~sh
./redis-cli  -h 192.168.1.137 -p 6379
192.168.1.137:6379> auth 123456
OK
192.168.1.137:6379> info Replication
# Replication
role:master
connected_slaves:2
slave0:ip=192.168.1.138,port=6379,state=online,offset=3065,lag=0
slave1:ip=192.168.1.138,port=6380,state=online,offset=3065,lag=1
master_failover_state:no-failover
master_replid:cfdb7ce70d3946f3e0d51e71f4bc7b8e911b045f
master_replid2:0000000000000000000000000000000000000000
master_repl_offset:3065
second_repl_offset:-1
repl_backlog_active:1
repl_backlog_size:1048576
repl_backlog_first_byte_offset:1
repl_backlog_histlen:3065

#master上插入测试数据
192.168.1.137:6379> set time "2023"
OK
192.168.1.137:6379> get time
"2023"
~~~

- 登录slave查看

~~~sh
./redis-cli  -h 192.168.1.138 -p 6380
192.168.1.138:6380> auth 123456
OK
192.168.1.138:6380> info Replication
# Replication
role:slave
master_host:192.168.1.137
master_port:6379
master_link_status:up
master_last_io_seconds_ago:9
master_sync_in_progress:0
slave_read_repl_offset:3191
slave_repl_offset:3191
slave_priority:100
slave_read_only:1
replica_announced:1
connected_slaves:0
master_failover_state:no-failover
master_replid:cfdb7ce70d3946f3e0d51e71f4bc7b8e911b045f
master_replid2:0000000000000000000000000000000000000000
master_repl_offset:3191
second_repl_offset:-1
repl_backlog_active:1
repl_backlog_size:1048576
repl_backlog_first_byte_offset:2730
repl_backlog_histlen:462

#查看哪些键值
192.168.1.138:6380> keys *
1) "time"
2) "name"
192.168.1.138:6380> get time
"2023"

#尝试写入，发现报错，因为slave是只读的
192.168.1.138:6380> set test "1"
(error) READONLY You can't write against a read only replica.
192.168.1.138:6380>
~~~

## 主从故障迁移测试

- 模拟master宕机

~~~sh
#在master上直接关掉redis
./redis-cli  -h 127.0.0.1 -p 6379
127.0.0.1:6379> auth 123456
OK
127.0.0.1:6379> shutdown save
not connected> 
not connected> info Replication
Could not connect to Redis at 127.0.0.1:6379: Connection refused
~~~

- slave节点查看状态信息

~~~sh
#slave节点登录redis
redis-cli 
127.0.0.1:6379> auth 123456
OK
127.0.0.1:6379> not connected> info Replication
(error) ERR unknown command 'not', with args beginning with: 'connected>' 'info' 'Replication' 
127.0.0.1:6379> Could not connect to Redis at 127.0.0.1:6379: Connection refused
(error) ERR unknown command 'Could', with args beginning with: 'not' 'connect' 'to' 'Redis' 'at' '127.0.0.1:6379:' 'Connection' 'refused' 
127.0.0.1:6379> info Replication
# Replication
role:slave
master_host:192.168.1.137
master_port:6379
master_link_status:down  #master节点宕机
master_last_io_seconds_ago:-1
master_sync_in_progress:0
slave_read_repl_offset:3807
slave_repl_offset:3807
master_link_down_since_seconds:95
slave_priority:100
slave_read_only:1
replica_announced:1
connected_slaves:0
master_failover_state:no-failover
master_replid:cfdb7ce70d3946f3e0d51e71f4bc7b8e911b045f
master_replid2:0000000000000000000000000000000000000000
master_repl_offset:3807
second_repl_offset:-1
repl_backlog_active:1
repl_backlog_size:1048576
repl_backlog_first_byte_offset:15
repl_backlog_histlen:3793
127.0.0.1:6379>
~~~

- 临时手动指定slave为新的master角色继续提供服务

  ```sh
  127.0.0.1:6379>  slaveof no one
  OK
  127.0.0.1:6379>  info Replication
  # Replication
  role:master
  connected_slaves:0
  master_failover_state:no-failover
  master_replid:3682825e29c328d1775fc9e854ba6951d048be3a
  master_replid2:f53da0dbdd07f2af22f7c71bbd00e0176de98920
  master_repl_offset:4003
  second_repl_offset:4004
  repl_backlog_active:1
  repl_backlog_size:1048576
  repl_backlog_first_byte_offset:15
  repl_backlog_histlen:3989
  ```

  > 说明：将一个 Redis 服务器从其当前的主服务器角色中解除，使其变成一个独立的（非复制的）服务器。这个命令的作用是告诉当前的从服务器停止复制任何主服务器。将slave手工指定为Master。

- master恢复后，切回slave角色

~~~sh
#master节点上启动redis
redis-server  /usr/local/redis-6.2.6/etc/redis.conf
~~~

~~~sh
#连接到slave节点
127.0.0.1:6379> SLAVEOF 192.168.1.137 6379 
OK Already connected to specified master
127.0.0.1:6379> auth 123456
OK
127.0.0.1:6379>  info Replication
# Replication
role:slave
master_host:192.168.1.137
master_port:6379
master_link_status:up
master_last_io_seconds_ago:3
master_sync_in_progress:0
slave_read_repl_offset:4143
slave_repl_offset:4143
slave_priority:100
slave_read_only:1
replica_announced:1
connected_slaves:0
master_failover_state:no-failover
master_replid:1b58d039b7ec3b459e09dbbb488a98b7cb83078b
master_replid2:0000000000000000000000000000000000000000
master_repl_offset:4143
second_repl_offset:-1
repl_backlog_active:1
repl_backlog_size:1048576
repl_backlog_first_byte_offset:4116
repl_backlog_histlen:28
127.0.0.1:6379>
~~~

## Summary

- 主从模式中的主服务器仍然是单点故障的可能来源。如果主服务器发生故障，整个系统可能会受到影响。


- 在主服务器发生故障时，进行故障转移并使一个从服务器晋升为新的主服务器需要一些时间，且只能手动切换、一般不建议使用。


- 在某些情况下，可能需要考虑使用其他高可用性解决方案，如 Redis Sentinel 或 Redis Cluster。

# redis哨兵模式部署

## 背景

Redis Sentinel 是 Redis 的高可用性解决方案之一，用于监控和管理 Redis 主从复制环境。它可以检测节点的状态，并在主节点下线时自动进行故障转移。

主要特性：

- 监控： Sentinel 能够监控 Redis 主从节点的健康状况，包括网络连接、内存使用、主从同步状态等。
- 自动故障检测： Sentinel 能够检测到主节点的故障，并在必要时触发自动故障转移。
- 故障转移：在主节点故障时，Sentinel 会协调选举一个新的主节点，并将其他节点重新配置为新主节点的从节点。
- 配置提供：Sentinel 可以通过发布/订阅机制向应用程序提供有关节点状态的实时信息，使应用程序能够动态调整连接。

工作原理：

- 每个Sentinel（哨兵）进程以每秒钟一次的频率向整个集群中的Master主服务器，Slave从服务器以及其他Sentinel（哨兵）进程发送一个 PING 命令。
- 如果一个实例（instance）距离最后一次有效回复 PING 命令的时间超过 down-after-milliseconds 选项所指定的值， 则这个实例会被 Sentinel（哨兵）进程标记为主观下线（SDOWN）
- 如果一个Master主服务器被标记为主观下线（SDOWN），则正在监视这个Master主服务器的所有 Sentinel（哨兵）进程要以每秒一次的频率确认Master主服务器的确进入了主观下线状态
- 当有足够数量的 Sentinel（哨兵）进程（大于等于配置文件指定的值）在指定的时间范围内确认Master主服务器进入了主观下线状态（SDOWN）， 则Master主服务器会被标记为客观下线（ODOWN）
- 在一般情况下， 每个 Sentinel（哨兵）进程会以每 10 秒一次的频率向集群中的所有Master主服务器、Slave从服务器发送 INFO 命令。
- 当Master主服务器被 Sentinel（哨兵）进程标记为客观下线（ODOWN）时，Sentinel（哨兵）进程向下线的 Master主服务器的所有 Slave从服务器发送 INFO 命令的频率会从 10 秒一次改为每秒一次。
- 若没有足够数量的 Sentinel（哨兵）进程同意 Master主服务器下线， Master主服务器的客观下线状态就会被移除。若 Master主服务器重新向 Sentinel（哨兵）进程发送 PING 命令返回有效回复，Master主服务器的主观下线状态就会被移除。

优缺点：

- 哨兵模式是基于主从模式的，所有主从的优点，哨兵模式都具有。主从可以自动切换，系统更健壮，可用性更高。
- 难支持在线扩容，在集群容量达到上限时在线扩容会变得很复杂。

## 配置sentinel节点

- 主从两台服务器都配置：
  - 哨兵节点1:192.168.1.137；redis实例：6379（默认master）
  - 哨兵节点2：192.168.1.138；多个redis实例（6379/6380/6381/6382/6383）

- 复制redis解压目录下的sentinel配置文件

~~~sh
cp sentinel.conf /usr/local/redis-6.2.6/bin
vim sentinel.conf
protected-mode no  # 不启用保护，让其他节点都能访问这台哨兵
port 26379   #端口
daemonize yes  # 开启后台运行
pidfile "/var/run/redis-sentinel-26379.pid"  # 进程id
logfile "/usr/local/redis-6.2.6/logs/redis_26379.log" # 日志文件位置
dir "/usr/local/redis-6.2.6/sentinel"   # 工作空间目录

# 配置哨兵，mymaster是昵称可以自定义
# master内网IP master端口 
# 最后一个2代表至少有两个哨兵确认master宕机时才能认定该master失效；
# 其中的一个哨兵就可以去开始执行故障转移
sentinel monitor mymaster 192.168.10.125 6379 2
# 密码
sentinel auth-pass mymaster 123456
# master被sentinel认定为失效的间隔时间，单位：毫秒，即30秒
sentinel down-after-milliseconds mymaster 30000
# 剩余的slaves重新和新的master做同步的并行个数
sentinel parallel-syncs mymaster 1
# 主备切换的超时时间，哨兵要去做故障转移，这个时候哨兵也是一个进程，如果他没有去执行，超过这个时间后，会由其他的哨兵来处理
sentinel failover-timeout mymaster 180000
~~~

- 复制sentinel配置文件到另一台节点

~~~sh
scp sentinel.conf root@192.168.1.137:/usr/local/redis-6.2.6
~~~

## 启动哨兵模式并测试

~~~sh
#两台主机都执行
redis-sentinel sentinel.conf
#测试：停掉192.168.1.137的6379实例master
#在192.168.1.138的redis实例测试，可以发现master已经实现故障转移：
redis-cli  -h 127.0.0.1 -p 6381
127.0.0.1:6381> info Replication
# Replication
role:master
connected_slaves:4
slave0:ip=192.168.1.138,port=6382,state=online,offset=360937,lag=0
slave1:ip=192.168.1.138,port=6379,state=online,offset=361104,lag=0
slave2:ip=192.168.1.138,port=6380,state=online,offset=361104,lag=0
slave3:ip=192.168.1.138,port=6383,state=online,offset=361104,lag=0
master_failover_state:no-failover
master_replid:c9e93599ca489d8bc1ae5e203d72b7e817811583
master_replid2:f0fa1c465663eb715e7b1b66d729dd3fa4aa45f2
master_repl_offset:361104
second_repl_offset:296758
repl_backlog_active:1
repl_backlog_size:1048576
repl_backlog_first_byte_offset:38300
repl_backlog_histlen:322805
#可以通过调整sentinel down-after-milliseconds和sentinelfailover-timeout参数控制故障切换的时间长短。
~~~

## Summary

- 采用2个哨兵实现对6个redis实例的监测，并实现自动故障切换。当默认的 Redis 主节点宕掉之后，如果使用了 Redis Sentinel 进行主从切换（故障转移），Sentinel 会选择一个健康的从节点晋升为新的主节点，而不是默认的主节点恢复。

- "一主二从三哨兵"是一种常见的 Redis 高可用配置，但是否是最佳实践取决于具体的应用场景和需求。这种配置有一些优点，如提供了基本的高可用性、故障转移功能和读取负载均衡。

# redis cluster模式部署

## 背景

- Redis数据库的Cluster集群模式是一种将数据分布到多个Redis节点的解决方案，以提高数据存储和读取的可用性和扩展性。Redis Cluster是一种分布式、高可用性的Redis数据库部署模式。它将数据划分为多个槽（slot），每个节点负责处理一部分槽的数据。通过对槽的划分和分配，实现数据在多个节点之间的分布式存储和访问。Redis Cluster使用Gossip协议来进行节点间的信息传递和集群管理。
- Cluster集群模式的核心思想是将数据分片（Sharding）存储在多个Redis节点上，每个节点负责存储一部分数据。客户端与Cluster集群交互时，通过计算CRC16校验码将数据定位到具体的节点上。Cluster集群使用Gossip协议进行节点间的通信，以实现自动分片、故障转移和数据一致性。
- Redis Cluster 更适合处理读写高并发的业务，而 Sentinel 更注重保证系统的高可用性。

## 实例配置

- Redis Cluster采用无中心结构，每个节点都可以保存数据和整个集群状态，每个节点都和其他所有节点连接。Cluster一般由多个节点组成，节点数量至少为6个才能保证组成完整高可用的集群，其中三个为 主节点，三个为从节点。三个主节点会分配槽，处理客户端的命令请求，而从节点可用在主节点故障后，顶替主节点。
- 需要准备6个Redis实例：
  - 第一台服务器：192.168.1.137；6个redis实例（6371-6376）
  - 第二台服务器：192.168.1.138；6个redis实例（6371-6376）

- 创建目录

~~~sh
mkdir -p /usr/local/redis/cluster/conf /usr/local/redis/cluster/data /usr/local/redis/cluster/log
~~~

- 修改配置文件

~~~sh
vim redis-6371.conf
# 放行访问IP限制
bind 0.0.0.0
# 端口
port 6371
# 后台启动
daemonize yes
# 日志存储目录及日志文件名
logfile "/usr/local/redis/cluster/log/redis-6371.log"
# rdb数据文件名
dbfilename dump-6371.rdb
# aof模式开启和aof数据文件名
appendonly yes
appendfilename "appendonly-6371.aof"
# rdb数据文件和aof数据文件的存储目录
dir /usr/local/redis/cluster/data
# 设置密码
requirepass 123456
# 从节点访问主节点密码(必须与 requirepass 一致)
masterauth 123456
# 是否开启集群模式，默认 no
cluster-enabled yes
# 集群节点信息文件，会保存在 dir 配置对应目录下
cluster-config-file nodes-6371.conf
# 集群节点连接超时时间
cluster-node-timeout 15000
# 集群节点 IP
cluster-announce-ip 192.168.1.137
# 集群节点映射端口
cluster-announce-port 6371
# 集群节点总线端口
cluster-announce-bus-port 16371
~~~

有几个实例，就复制几份配置文件（每个配置文件修改对应的IP和端口），可以批量替换

~~~sh
:%s/6371/6372/g
批量替换conf配置文件的内容，命令如下：
find /usr/local/redis/cluster/conf -type f -name '*.conf' -exec sed -i 's/192.168.1.138/192.168.1.137/g' {} +
~~~

- 启动所有实例

~~~sh
/usr/local/redis/bin/redis-server /usr/local/redis/cluster/conf/redis-6371.conf
/usr/local/redis/bin/redis-server /usr/local/redis/cluster/conf/redis-6372.conf
/usr/local/redis/bin/redis-server /usr/local/redis/cluster/conf/redis-6373.conf
/usr/local/redis/bin/redis-server /usr/local/redis/cluster/conf/redis-6374.conf
/usr/local/redis/bin/redis-server /usr/local/redis/cluster/conf/redis-6375.conf
/usr/local/redis/bin/redis-server /usr/local/redis/cluster/conf/redis-6376.conf
~~~

## 集群配置

- 两台服务器上都配置集群

~~~sh
/usr/local/redis/bin/redis-cli -a 123456 --cluster create \
192.168.1.137:6371 192.168.1.137:6372 \
192.168.1.137:6373 192.168.1.137:6374 \
192.168.1.137:6375 192.168.1.137:6376 \
--cluster-replicas 1
#--cluster-replicas 1 表示每个主节点有一个从节点。
#这样配置完，6个redis节点被分为3主3从
~~~

- 集群检查

~~~sh
/usr/local/redis/bin/redis-cli -a 123456 --cluster check 192.168.1.137:6371
# 主节点信息
192.168.1.137:6371 (694ce7e6...) -> 0 keys | 5461 slots | 1 slaves.
192.168.1.137:6372 (bc13ea49...) -> 0 keys | 5462 slots | 1 slaves.
192.168.1.137:6373 (7a87ed79...) -> 0 keys | 5461 slots | 1 slaves.
# 主节点有多少 Key
[OK] 0 keys in 3 masters.
# 每个槽的平均分配情况
0.00 keys per slot on average.
# 集群状态检查操作由 192.168.1.137:6371执行
>>> Performing Cluster Check (using node 192.168.1.137:6371)
# 主节点信息以及附加的从节点个数
M: 694ce7e6fd614fe4da0590e56f82ac9307229835 192.168.1.137:6371
   slots:[0-5460] (5461 slots) master
   1 additional replica(s)
# 从节点信息以及复制的主节点 ID
S: 8de2b7f096636e2fa7ef66aae72e0c50ebbff0bb 192.168.1.137:6375
   slots: (0 slots) slave
   replicates 7a87ed79be4ec0023ea9a93774e4eb136dfe99c7
S: bdda13fdf3c1f39b4d9c1e6148a15028f45e8fa4 192.168.1.137:6374
   slots: (0 slots) slave
   replicates bc13ea49343fcdf80cbee55b263d5d925d46bdc7
M: bc13ea49343fcdf80cbee55b263d5d925d46bdc7 192.168.1.137:6372
   slots:[5461-10922] (5462 slots) master
   1 additional replica(s)
S: d05f960dd0f0e2688d2f2191aef1b94c2f66ba9c 192.168.1.137:6376
   slots: (0 slots) slave
   replicates 694ce7e6fd614fe4da0590e56f82ac9307229835
M: 7a87ed79be4ec0023ea9a93774e4eb136dfe99c7 192.168.1.137:6373
   slots:[10923-16383] (5461 slots) master
   1 additional replica(s)
# 所有节点都同意槽的配置情况
[OK] All nodes agree about slots configuration.
>>> Check for open slots...
>>> Check slots coverage...
# 所有 16384 个槽都包括在内
[OK] All 16384 slots covered.
~~~

- 查看主从节点日志

~~~sh
tail -f -n 1000 /usr/local/redis/cluster/log/redis-6371.log
tail -f -n 1000 /usr/local/redis/cluster/log/redis-6374.log
~~~

- 查看节点信息

~~~sh
/usr/local/redis/bin/redis-cli -c -a 123456 -h 192.168.1.137 -p 6376
cluster info   #查看集群
cluster nodes    #查看节点
~~~

## 集群验证测试

~~~sh
#连接6376节点
/usr/local/redis/bin/redis-cli -c -a 123456 -h 192.168.1.137 -p 6376

192.168.1.137:6376> set name test
-> Redirected to slot [5798] located at 192.168.1.137:6372
OK
192.168.1.137:6372> set age 18
-> Redirected to slot [741] located at 192.168.1.137:6371
OK
192.168.1.137:6371> set address xian
OK
192.168.1.137:6371> get age
"18"
192.168.1.137:6371> get name
-> Redirected to slot [5798] located at 192.168.1.137:6372
"test"
#在Redis集群中，槽（slot）是对数据进行分片的单位。每个槽都被分配给集群中的一个节点。当你执行一些操作时，如果该操作涉及的槽与当前连接的节点不匹配，Redis会返回一个"Redirected"信息，并将请求重定向到正确的节点上。
~~~

## 集群关闭与释放

- 经常出现集群创建出现错误，信息如下：

~~~sh
/usr/local/redis/bin/redis-cli -a 123456 --cluster create \
> 192.168.1.137:6371 192.168.1.137:6372 \
> 192.168.1.137:6373 192.168.1.137:6374 \
> 192.168.1.137:6375 192.168.1.137:6376 \
> --cluster-replicas 1
Warning: Using a password with '-a' or '-u' option on the command line interface may not be safe.
[ERR] Node 192.168.1.137:6371 is not empty. Either the node already knows other nodes (check with CLUSTER NODES) or contains some key in database 0.
~~~

这个错误提示表明节点 192.168.1.137:6371 不是空的，可能已经包含其他节点的信息（通过 CLUSTER NODES 命令查看）或者包含了数据库0中的某些键。在创建Redis集群时，所有的节点都必须是空的，没有包含其他节点的信息。

- 清理节点数据

~~~sh
/usr/local/redis/bin/redis-cli -a 123456 -h 192.168.1.137 -p 6371
> CLUSTER NODES   
> FLUSHALL           # 清空节点数据：
#2）清空集群data文件夹
#3）停止redis实例
pkill redis
#4）重启redis实例
/usr/local/redis/bin/redis-server /usr/local/redis/cluster/conf/redis-6371.conf
/usr/local/redis/bin/redis-server /usr/local/redis/cluster/conf/redis-6372.conf
/usr/local/redis/bin/redis-server /usr/local/redis/cluster/conf/redis-6373.conf
/usr/local/redis/bin/redis-server /usr/local/redis/cluster/conf/redis-6374.conf
/usr/local/redis/bin/redis-server /usr/local/redis/cluster/conf/redis-6375.conf
/usr/local/redis/bin/redis-server /usr/local/redis/cluster/conf/redis-6376.conf
~~~

- 重新创建redis cluster集群

~~~sh
/usr/local/redis/bin/redis-cli -a 123456 --cluster create \
192.168.1.137:6371 192.168.1.137:6372 \
192.168.1.137:6373 192.168.1.137:6374 \
192.168.1.137:6375 192.168.1.137:6376 \
--cluster-replicas 1   
#如果cluster-replicas是2，则需要至少9个实例
~~~

# redis的数据持久化

## 背景

- Redis作为一个键值对内存数据库(NoSQL)，数据都存储在内存当中，在处理客户端请求时，所有操作都在内存当中进行；当服务器关机甚至redis守护进程退出的时候，内存数据就消失了。
- 对于只把Redis当缓存来用的项目来说，数据消失或许问题不大，重新从数据源把数据加载进来就可以了，但如果直接把用户提交的业务数据存储在Redis当中，把Redis作为数据库来使用，在其放存储重要业务数据，那么Redis的内存数据丢失所造成的影响也许是毁灭性。

- 为解决数据持久化问题，Redis提供了RDB和AOF两种不同的数据持久化方式。

## RDB

RDB是一种快照存储持久化方式，具体就是将Redis某一时刻的内存数据保存到硬盘的文件当中，默认保存的文件名为dump.rdb，而在Redis服务器启动时，会重新加载dump.rdb文件的数据到内存当中恢复数据。

开启RDB：客户端可以通过向Redis服务器发送save或bgsave命令让服务器生成rdb文件，或者通过服务器配置文件指定触发RDB条件。

### save

- 当客户端向服务器发送save命令请求进行持久化时，服务器会阻塞save命令之后的其他客户端的请求，直到数据同步完成。
- 如果数据量太大，同步数据会执行很久，而这期间Redis服务器也无法接收其他请求，所以，最好不要在生产环境使用save命令。

### bgsave

- 当客户端发服务发出bgsave命令时，Redis服务器主进程会forks一个子进程来数据同步，在将数据保存到rdb文件之后，子进程会退出。
- 与save命令相比，Redis服务器在处理bgsave采用子进程进行IO写入，而主进程仍然可以接收其他请求，但forks子进程是同步的，所以forks子进程时，一样不能接收其他请求。这意味着如果forks一个子进程花费的时间太久(一般是很快的)，bgsave命令仍然有阻塞其他客户的请求的情况发生。

### 配置文件

- 除了通过客户端发送命令外，还有一种方式，就是在Redis配置文件中的save指定到达触发RDB持久化的条件，比如【多少秒内至少达到多少写操作】就开启RDB数据同步。例如我们可以在配置文件redis.conf指定如下的选项：

  ```mysql
  #900s内至少达到一条写命令
  save 900 1
  #300s内至少达至10条写命令
  save 300 10
  #60s内至少达到10000条写命令
  save 60 10000
  #启动服务器加载配置文件
  redis-server redis.conf
  ```

- 这种通过服务器配置文件触发RDB的方式，与bgsave命令类似，达到触发条件时，会forks一个子进程进行数据同步，不过最好不要通过这方式来触发RDB持久化，因为设置触发的时间太短，则容易频繁写入rdb文件，影响服务器性能，时间设置太长则会造成数据丢失。

- RDB默认生成的文件名为dump.rdb，可以通过配置文件进行更加详细配置，比如在单机下启动多个redis服务器进程时，可以通过端口号配置不同的rdb名称，如下所示：

  ```mysql
  #是否压缩rdb文件
  rdbcompression yes
  #rdb文件的名称
  dbfilename redis-6379.rdb
  #rdb文件保存目录
  dir ~/redis/
  ```

## AOF

- Append-only file: 与RDB存储某个时刻的快照不同，AOF持久化方式会记录客户端对服务器的每一次写操作命令，并将这些写操作以Redis协议追加保存到以后缀为aof文件末尾，在Redis服务器重启时，会加载并运行aof文件的命令，以达到恢复数据的目的。

- Redis默认不开启AOF持久化方式，我们可以在配置文件中开启并进行更加详细的配置，如下面的redis.conf文件：

  ```mysql
  #开启aof机制
  appendonly yes
  #aof文件名
  appendfilename "appendonly.aof"
  #写入策略,always表示每个写操作都保存到aof文件中,也可以是everysec或no
  appendfsync always
  #默认不重写aof文件
  no-appendfsync-on-rewrite no
  #保存目录
  dir ~/redis/
  ```

### 三种写入策略

在上面的配置文件中，我们可以通过appendfsync选项指定写入策略,有三个选项 

1. always： 客户端的每一个写操作都保存到aof文件当，这种策略很安全，但是每个写请注都有IO操作，所以也很慢。


2. everysec： appendfsync的默认写入策略，每秒写入一次aof文件，因此，最多可能会丢失1s的数据。

3. no： Redis服务器不负责写入aof，而是交由操作系统来处理什么时候写入aof文件。更快，但也是最不安全的选择，不推荐使用。

### AOF文件重写 

AOF将客户端的每一个写操作都追加到aof文件末尾，比如对一个key多次执行incr命令，这时候，aof保存每一次命令到aof文件中，aof文件会变得非常大。

```mysql
incr num 1
incr num 2
incr num 3
incr num 4
incr num 5
incr num 6
...
incr num 100000
```

aof文件太大，加载aof文件恢复数据时，就会非常慢，为了解决这个问题，Redis支持aof文件重写，通过重写aof，可以生成一个恢复当前数据的最少命令集，比如上面的例子中那么多条命令，可以重写为：

```mysql
set num 100000
```

aof文件是一个二进制文件，并不是像上面的例子一样，直接保存每个命令，而使用Redis自己的格式，上面只是方便演示。 

### 两种重写方式

1. 通过在redis.conf配置文件中的选项no-appendfsync-on-rewrite可以设置是否开启重写，这种方式会在每次fsync时都重写，影响服务器性以，因此默认值为no，不推荐使用。


```mysql
#默认不重写aof文件
no-appendfsync-on-rewrite no
```

2. 客户端向服务器发送bgrewriteaof命令，也可以让服务器进行AOF重写。

```sh
#让服务器异步重写追加aof文件命令
bgrewriteaof
```


AOF重写方式也是异步操作，即如果要写入aof文件，则Redis主进程会forks一个子进程来处理。

重写aof文件的好处：

1. 压缩aof文件，减少磁盘占用量。
2. 将aof的命令压缩为最小命令集，加快了数据恢复的速度。

### AOF文件损坏与修复

在写入aof日志文件时，如果Redis服务器宕机，则aof日志文件文件会出格式错误，在重启Redis服务器时，Redis服务器会拒绝载入这个aof文件，可以通过以下步骤修复aof并恢复数据。

1. 备份现在aof文件，以防万一。
2. 使用redis-check-aof命令修复aof文件，该命令格式如下：

```sh
redis-check-aof -fix file.aof
```

重启Redis服务器，加载已经修复的aof文件，恢复数据。

AOF的优点：AOF只是追加日志文件，因此对服务器性能影响较小，速度比RDB要快，消耗的内存较少。

AOF的缺点：AOF方式生成的日志文件太大，即使通过AFO重写，文件体积仍然很大。恢复数据的速度比RDB慢。

两种备份方式对比：

![image-20240813205743348](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202408132057464.png)
