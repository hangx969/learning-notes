# zookeeper

- ZooKeeper是Apache的一个开源项目，它是一个为分布式应用提供一致性服务的中间件，可以用于构建分布式应用。它提供的功能包括：配置管理、分布式同步、命名服务和组服务等。zookeeper就是动物园管理员，他是用来管hadoop、Hive、pig、kafka消息系统的管理员， Apache Hbase 和 Apache Solr 的分布式集群都用到了 zookeeper；Zookeeper是一个分布式的、开源的程序协调服务，是 hadoop 项目下的一个子项目。

- Zookeeper主要作用在于:

  1. 节点选举

     Master节点，主节点挂了之后，从节点就会接手工作 ,并且，保证这个节点是唯一的，这就是首脑模式，从而保证集群的高可用

  2. 统一配置文件管理

     只需要部署一台服务器则可以把相同的配置文件同步更新到其他所有服务器，比如，修改了Hadoop,Kafka,redis统一配置等。

  3. 发布与订阅消息

     类似于消息队列,发布者把数据存在znode节点上，订阅者会读取这个数据

  4. 集群管理

     集群中保证数据的一致性

- Zookeeper的选举机制

  - 过半机制
  - 安装的台数：奇数台(否则无法过半机制)

- 一般情况下10台服务器需安装ZK3台；20台=>5台；50台=>7台；100台=>11台。多台好处在于可靠性高,但是过的话会导致通信延时长

- zookeeper角色

  - leader领导者
  - follower跟随着
  - observer观察者
  - leader：负责发起选举和决议的，更新系统状态
  - follower：接收客户端的请求，给客户端返回结果，在选主的过程参与投票
  - observe：接收客户端的连接，同步leader状态，不参与选主

# 搭建zookeeper集群

## 环境准备

- zoo1： 172.16.183.190

- zoo2： 172.16.183.191
- zoo3： 172.16.183.192

## 准备安装包和配置文件

~~~sh
#3台机器上，解压安装包，重命名
tar zxvf apache-zookeeper-3.8.0-bin.tar.gz -C /opt/
mv /opt/apache-zookeeper-3.8.0-bin/ /opt/zookeeper
#3台机器上，创建数据文件目录和日志文件目录
mkdir -p /opt/zookeeper/zkData
mkdir -p /opt/zookeeper/zkLog
#复制配置文件并修改：
cd /opt/zookeeper/conf/
cp zoo_sample.cfg zoo.cfg
vim zoo.cfg
#在原有配置基础上修改内容如下：
dataDir=/opt/zookeeper 
dataLogDir=/opt/zookeeper/zkLog
server.1=172.16.183.190:2188:3888
server.2=172.16.183.191:2188:3888
server.3=172.16.183.192:2188:3888
~~~

## 启动zookeeper

~~~sh
#3台上
yum install java -y
cd /opt/zookeeper/
echo #1 #2 #3 > myid #zoo1写1，zoo2些2，zoo3写3
cd /opt/zookeeper/bin 
nohup ./zkServer.sh start &  #要按顺序启动1-2-3
cat nohup.out #查看启动结果
~~~

## 测试zookeeper

~~~sh
#测试zookeeper：
cd /opt/zookeeper/bin/
./zkCli.sh -server 127.0.0.1:2181  #连接zookeeper
#创建节点，以及和它关联的字符串
[zk: 127.0.0.1:2181(CONNECTED) 1] create /test "hangxu"      
#获取刚才创建的节点信息
[zk: 127.0.0.1:2181(CONNECTED) 2] get /test      
#"hanxu"
#修改节点信息
[zk: 127.0.0.1:2181(CONNECTED) 4] set /test "hanxux"      
[zk: 127.0.0.1:2181(CONNECTED) 5] get /test
#"hanxux"
~~~

# 搭建kafka集群

## kafka

