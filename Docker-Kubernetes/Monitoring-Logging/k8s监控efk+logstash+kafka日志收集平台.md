# 流程设计

- Filebeat采集日志 --> kafka topic保存日志 --> logstash从kafka读取日志、格式转换 --> elasticsearch --> kibana
- filebeat采集日志相比logstash更轻量化，但是格式转换不方便；所以利用logstash格式转换。kafka用作缓冲，当生产中日志量大时，加缓冲可以方式日志延迟等问题。

# zookeeper

- ZooKeeper是Apache的一个开源项目，它是一个为分布式应用提供一致性服务的中间件，可以用于构建分布式应用。它提供的功能包括：配置管理、分布式同步、命名服务和组服务等。zookeeper就是动物园管理员，他是用来管hadoop、Hive、pig、kafka消息系统的管理员， Apache Hbase 和 Apache Solr 的分布式集群都用到了 zookeeper；Zookeeper是一个分布式的、开源的程序协调服务，是 hadoop 项目下的一个子项目。

- 每个ZNode都可以存储数据，并且可以有子节点。ZooKeeper的节点主要用于存储和管理分布式系统中的元数据信息，例如配置信息、系统状态等。

- Zookeeper主要作用在于:

  1. 节点选举

     Master节点，主节点挂了之后，从节点就会接手工作，保证master节点是唯一的，这就是首脑模式，从而保证集群的高可用

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

1、kafka介绍：Kafka 是一种高吞吐量的分布式发布订阅消息系统。主要用于实时数据流的处理和分析。它可以处理大量的实时数据，并提供高吞吐量、可扩展性和容错性。

- 即使是非常普通的硬件Kafka也可以支持每秒数百万的消息。采用生产者消费者模型。

2、相关术语：

- Broker：Kafka集群包含一个或多个服务器，服务器被称为broker。Kafka的数据是分布式存储在各个Broker上的。每个Broker都会存储一部分Topic的Partition。Kafka的Broker主要用于存储和处理实时数据流。
- Topic：每条发布到Kafka集群的消息都有一个类别，这个类别被称为Topic。（物理上不同Topic的消息分开存储，逻辑上一个Topic的消息虽然保存于一个或多个broker上，但用户只需指定消息的Topic，即可生产或消费数据，而不必关心数据存于何处）
- Partition：Partition是物理上的概念，每个Topic包含一个或多个Partition。消费者从不同的partition上读取消息，避免同时读取的争抢现象。
- Producer：负责发布消息到Kafka broker
- Consumer：消息消费者，向Kafka broker读取消息的客户端。

> 消费者的偏移量：
>
> 在Kafka中，消费者的偏移量（Consumer Offset）是一个非常重要的概念。它表示消费者在特定的主题和分区中已经消费到的位置。
>
> Kafka的主题（Topic）被划分为一个或多个分区（Partition），每个分区中的消息都是有序的，并且每条消息在分区中都有一个唯一的序号，这个序号就是偏移量（Offset）。当消费者从分区中读取消息时，它会维护一个指针，这个指针指向下一条需要读取的消息的位置，这个位置就是消费者的偏移量。
>
> 消费者的偏移量是消费者消费消息的基础，通过维护每个消费者的偏移量，Kafka可以支持消息的重复消费，也就是说，消费者可以随时将偏移量回退到之前的位置，重新消费已经消费过的消息。同时，通过正确地管理消费者的偏移量，Kafka还可以实现消费者的故障恢复和负载均衡。

## 安装kafka单节点

- 准备安装包和配置文件,在zoo3上部署kafka服务

~~~sh
#zoo3上，解压压缩包
tar -xzf kafka_2.13-3.1.0.tgz
#修改配置文件
cd ./kafka_2.13-3.1.0/config
vim server.properties
listeners=PLAINTEXT://172.16.183.192:9092 #部署kafka机器的ip
zookeeper.connect=172.16.183.190:2181,172.16.183.191:2181,172.16.183.192:2181 #是指定zookeper集群地址
~~~

- 启动kafka

~~~sh
#zookeeper在kafka中的作用：管理broker、consumer，创建Broker后，向zookeeper注册新的broker信息，实现在服务器正常运行下的水平拓展。
cd /root/kafka_2.13-3.1.0/bin && ./kafka-server-start.sh -daemon ../config/server.properties
#登录zookeeper客户端，查看/brokers/ids
cd /opt/zookeeper/bin/
./zkCli.sh -server 127.0.0.1:2181  
[zk: 127.0.0.1:2181(CONNECTED) 1] ls /brokers/ids
#显示：[0]
~~~

> 在Kafka中，ZooKeeper被用作元数据的存储和协调服务。在Kafka中，ZooKeeper主要用于以下几个方面：
>
> 1. 保存和同步节点状态信息：Kafka集群中的每个节点都会在ZooKeeper中创建一个临时节点，这样就可以实时知道哪些节点是活跃的。
>
> 2. 保存消费者的偏移量：在早期的Kafka版本中，消费者的偏移量是保存在ZooKeeper中的，但在新版本中，这个功能已经被移动到了Kafka的一个内部主题中。
>
> 3. 保存主题和分区的元数据：包括主题的分区数、副本数、ISR等信息。
>
> 在Kafka 2.13版本中，ZooKeeper仍然是必需的，因为Kafka的一些核心功能依赖于ZooKeeper。但是，Kafka社区已经在计划中去除对ZooKeeper的依赖，这个计划被称为KRaft（Kafka Raft mode），在KRaft模式下，Kafka将使用自己的Raft协议来管理元数据，从而去除对ZooKeeper的依赖。

- 生产者和消费者测试

~~~sh
#（1）创建主题，主题名是 quickstart-events
cd /root/kafka_2.13-3.1.0/bin 
./kafka-topics.sh --create --topic quickstart-events --bootstrap-server 172.16.183.192:9092
#（2）查看topic
./kafka-topics.sh --describe --topic quickstart-events --bootstrap-server 172.16.183.192:9092
#（3）topic写入消息
./kafka-console-producer.sh --topic quickstart-events --bootstrap-server 172.16.183.192:9092
#>hello    
#>welcome
#（4）打开新的终端，从topic读取信息
cd /root/kafka_2.13-3.1.0/bin
./kafka-console-consumer.sh --topic quickstart-events --from-beginning --bootstrap-server 172.16.183.192:9092
#hello
#welcome
~~~

## 搭建kafka高可用集群

- 将zoo1和zoo2加入集群，唯一不同的是broker.id和listener监听的主机IP。

~~~sh
#在zoo1、zoo2上解压安装包
tar -xzf kafka_2.13-3.1.0.tgz
#修改配置文件
cd ./kafka_2.13-3.1.0/config
vim server.properties
#zoo1上
broker.id=1
listeners=PLAINTEXT://172.16.183.190:9092
zookeeper.connect=172.16.183.190:2181,172.16.183.191:2181,172.16.183.192:2181
#zoo2上
broker.id=2
listeners=PLAINTEXT://172.16.183.191:9092
zookeeper.connect=172.16.183.190:2181,172.16.183.191:2181,172.16.183.192:2181
#启动kafka
cd /root/kafka_2.13-3.1.0/bin && ./kafka-server-start.sh -daemon ../config/server.properties
#登录zookeeper客户端查看/broker/ids
cd /opt/zookeeper/bin/
./zkCli.sh -server 127.0.0.1:2181
ls /brokers/ids
#[0, 1, 2]
~~~

# 部署filebeat

filebeat是轻量级的日志收集组件。在zoo2部署nginx，利用filebeat采集nginx的日志。

- 安装nginx

~~~sh
#zoo2安装nginx
yum install nginx -y
service nginx start
#请求nginx
curl 172.16.183.191
~~~

- kafka集群创建topic，存放日志数据

~~~sh
cd /root/kafka_2.13-3.1.0/bin 
./kafka-topics.sh --create --topic test-topic --bootstrap-server 172.16.183.192:9092,172.16.183.191:9092,172.16.183.190:9092
~~~

- 安装filebeat

~~~sh
tar zxvf filebeat-7.13.1-linux-x86_64.tar.gz -C /opt/
cd /opt/filebeat-7.13.1-linux-x86_64/
./filebeat modules enable nginx
~~~

- 配置filebeat_nginx.yaml

~~~sh
#创建配置文件。记得注释kafka version，不然报错
vim filebeat_nginx.yml 
~~~

~~~yaml
filebeat.modules:
- module: nginx
  access:
    enabled: true
    var.paths: ["/var/log/nginx/access.log*"]
  error:
    enabled: true
    var.paths: ["/var/log/nginx/error.log*"]
 
#----------------------------------Kafka output--------------------------------#
output.kafka:
  enabled: true
  hosts: ['172.16.183.192:9092', '172.16.183.190:9092','172.16.183.191:9092']
  topic: 'test-topic' #kafka的topic，需要提前创建好，上面步骤已经创建过了
  required_acks: 1  #default
  compression: gzip #default
  max_message_bytes: 1000000 #default
  codec.format:
    string: '%{[message]}'
~~~

- 启动filebeat

  ```sh
  cd /opt/filebeat-7.13.1-linux-x86_64/
  nohup ./filebeat -e -c filebeat_nginx.yml &
  #请求nginx
  curl 172.16.183.191
  #查看kafka topic是否有日志数据
  cd /root/kafka_2.13-3.1.0/bin
  ./kafka-console-consumer.sh --topic test-topic --from-beginning --bootstrap-server 172.16.183.192:9092,172.16.183.190:9092,172.16.183.191:9092
  ```

# 部署logstash

- logstash用作日志采集的话，比较吃内存（约20G）。所以这里用更轻量化的filebeat采集日志，用logstash做日志格式转换。

- 安装logstash

~~~sh
#在zoo2上部署
cd /opt/
#wget https://artifacts.elastic.co/downloads/logstash/logstash-7.9.2.tar.gz
tar zxvf logstash-7.9.2.tar.gz -C /opt/
cd /opt/logstash-7.9.2/config
vim nginx.conf
~~~

~~~sh
input{
  kafka {
    bootstrap_servers => ["172.16.183.192:9092,172.16.183.190:9092 ,172.16.183.191:9092"]
    auto_offset_reset => "latest"
    consumer_threads => 3
    decorate_events => true
    topics => ["test-topic"]
    codec => "json"
  }
}
output {
    elasticsearch {
      hosts => ["172.16.183.191:9200"]
      index => "kafkalog-%{+YYYY.MM.dd}"        
    }
}

#备注
#这里定义的index就是kibana里面显示的索引名称
#bootstrap_servers => ["172.16.183.191:9092,172.16.183.192:9092,172.16.183.190:9092"]指定kafka集群地址
#hosts => ["172.16.183.191:9200"]指定es主机地址
~~~

- 启动logstash

~~~sh
cd ../bin
nohup ./logstash -f ../config/nginx.conf >> logstash.log &
~~~

# 部署ES

- elasticsearch是一个实时的，分布式的，可扩展的搜索引擎，它允许进行全文本和结构化搜索以及对日志进行分析。它通常用于索引和搜索大量日志数据，也可以用于搜索许多不同种类的文档。elasticsearch具有三大功能，搜索、分析、存储数据。

- 在zoo2上部署es

~~~sh
mkdir /es_data
chmod 777 /es_data
yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
yum install docker-ce -y
systemctl start docker && systemctl enable docker
docker load -i elasticsearch.tar.gz
docker run -p 9200:9200 -p 9330:9300 -itd -e "discovery.type=single-node" --name es -v /es_data:/usr/share/elasticsearch/data docker.elastic.co/elasticsearch/elasticsearch:7.9.2
~~~



# 部署kibana

- kibana是一个基于Web的图形界面，用于搜索、分析和可视化存储在Elasticsearch指标中的日志数据。Kibana功能众多，在“Visualize” 菜单界面可以将查询出的数据进行可视化展示，“Dev Tools” 菜单界面可以让户方便地通过浏览器直接与 Elasticsearch 进行交互，发送 RESTFUL对 Elasticsearch 数据进行增删改查。
- 在zoo2上部署kibana

~~~sh
#安装kibana服务
docker load -i kibana.tar.gz
docker run -p 5601:5601 -it -d  --link es -e ELASTICSEARCH_URL=http://172.16.183.191:9200 --name kibana kibana:7.9.2
#修改kibana配置文件：
docker exec -it kibana /bin/bash
vi config/kibana.yml
elasticsearch.hosts: [ "http://172.16.183.191:9200/" ]

docker restart kibana
~~~

- 配置kibana图形化界面

~~~sh
#配置kibana ui界面
http://172.16.183.191:5601/app/home
#选择explore on my own
#Kibana添加索引
http://172.16.183.191:5601/app/management/kibana/indexPatterns
#需要再次curl访问nginx，才能产生日志
#选择create index pattern
~~~

![image-20240426214019628](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202404262140722.png)

![image-20240426214110488](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202404262141526.png)

- 回到kibana首页，点击Discover查看日志

  ![image-20240426220309720](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202404262214829.png)
