> - 什么情况下kafka会重复消费？
> - kafka重试
> - 两个项目组或两家公司 之间进行数据交互的时候，数据少且稳定性高的时候用普通api调用就可以了，一旦数据量很大或双方有一方不稳定的时候 就会用消息队列 （rabbitmq,kafka等），如果数据量特别大达到了“大数据”的标准，这个时候现成的解决方案只剩下kafka了。spark+flink+kafka 也算是通用的大数据处理方案了。



# 介绍

- topic：通过不同的topic对消息进行分类
- partition：为了提高单个topic的并发性能，将单个topic拆分为多个partition
- 为提高扩展性，将不同partition分别部署到多个broker上。
- 为提高可用性，为partition加了多个副本（leader和follower）
- zookeeper作为分布式协调服务，与各个broker通信维护集群信息，但是zookeeper过重。在kafka 2.8.0版本中支持移除zookeeper，引入一致性算法kraft

