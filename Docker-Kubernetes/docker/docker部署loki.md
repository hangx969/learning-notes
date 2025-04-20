# Loki简介

- 最主流的 ELK 或者 EFK 比较重，再加上现阶段对于 ES 复杂的搜索功能很多都用不上。最终选择Grafana开源的Loki日志系统。

- Loki 的第一个稳定版本于 2019 年 11 月 19 日发布，是 Grafana Labs 团队最新的开源项目，是一个水平可扩展，高可用性，多租户的日志聚合系统。Loki 是专门用于聚集日志数据，重点是高可用性和可伸缩性。与竞争对手不同的是，它确实易于安装且资源效率极高。
- 项目地址：https://github.com/grafana/loki/

## 特性

与其他日志聚合系统相比，Loki 具有下面的一些特性：

- 不对日志进行全文编排索引。Loki是为每个日志处理成一组键值对，这一组键值对类似Promethues采集的指标中的Labels。这样日志内容就可以像通过Label查询Metrcis一样进行查找。类似Prometheus的查询PromQL规则一样，Loki提供了LogQL语句查询。Loki 操作起来会更简单，更省成本。
- 通过使用与 Prometheus 相同的标签记录流对日志进行索引和分组，这使得日志的扩展和操作效率更高，能对接 alertmanager。
- 特别适合储存 Kubernetes Pod 日志；诸如 Pod 标签之类的元数据会被自动删除和编入索引。
- 受 Grafana 原生支持，避免 kibana 和 grafana 来回切换。

## 优缺点

- Loki 的架构非常简单，使用了和 Prometheus 一样的标签来作为索引，通过这些标签既可以查询日志的内容也可以查询到监控的数据，不但减少了两种查询之间的切换成本，也极大地降低了日志索引的存储。
- 与 ELK 相比，消耗的成本更低，具有成本效益。
- 在日志的收集以及可视化上可以连用 Grafana，实现在日志上的筛选以及查看上下行的功能。

## 缺点

- 技术比较新颖，相对应的论坛不是非常活跃。
- 功能单一，只针对日志的查看，筛选有好的表现，对于数据的处理以及清洗没有 ELK 强大，同时与 ELK 相比，对于后期，ELK 可以连用各种技术进行日志的大数据处理，但是 loki 不行。

## 架构

![image-20241102202018889](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202411022020952.png)

Loki 的架构非常简单，使用了和 Prometheus 一样的标签来作为索引，也就是说，你通过这些标签既可以查询日志的内容也可以查询到监控的数据，不但减少了两种查询之间的切换成本，也极大地降低了日志索引的存储。Loki 将使用与 Prometheus 相同的服务发现和标签重新标记库，编写了 pormtail，在 Kubernetes 中 promtail 以 DaemonSet 方式运行在每个节点中，通过 Kubernetes API 等到日志的正确元数据，并将它们发送到 Loki。

- Loki 是主服务器，负责存储日志和处理查询。
- Promtail 是代理，负责收集日志并将其发送给 Loki 。
- Grafana 用于 UI 展示。

# docker部署loki

- 下载yaml文件

~~~yaml
wget https://raw.githubusercontent.com/grafana/loki/v2.2.0/production/docker-compose.yaml -O docker-compose-loki.yaml
version: "3"

networks:
  loki:

services:
  loki:
    image: grafana/loki:2.0.0
    ports:
      - "3100:3100"
    command: -config.file=/etc/loki/local-config.yaml
    networks:
      - loki

  promtail:
    image: grafana/promtail:2.0.0
    volumes:
      - /var/log:/var/log
    command: -config.file=/etc/promtail/config.yml
    networks:
      - loki

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    networks:
      - loki
~~~

- 启动服务

~~~sh
docker compose -f docker-compose-loki.yaml up -d
~~~

- 配置数据源
  - IP:3000端口进入grafana UI，admin/admin
  - data sources 选择loki，URL：http://172.16.183.80:3100

- 测试查询日志

  ~~~sh
  (job="varlogs")|="error"
  #查询标签为varlogs并且过滤含有error的日志
  #标签样式选job
  ~~~

## promtail配置

- promtail 容器为日志采集容器，配置文件在 promtail 容器/etc/promtail/config.yml，将该容器部署在需要采集日志的服务器上就能正常采集日志传回loki服务收集整理

~~~yaml
tee /etc/promtail/config.yml <<'EOF'
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://172.16.183.80:3100/loki/api/v1/push  #这里配置的地址为loki服务器日志收集的信息

scrape_configs:
- job_name: system
  static_configs:
  - targets:
      - localhost
    labels:
      job: varlogs                       #这里为刚才选择job下子标签
      __path__: /var/log/*log            #将采集的日志放在/var/log/*log下自动发现
EOF
~~~

## 增加一台服务器的日志采集

- 编写配置文件

~~~yaml
mkdir /root/promtail && cd /root/promtail
tee config.yml <<'EOF'
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://192.168.106.202:3100/loki/api/v1/push    

scrape_configs:
- job_name: mysql
  static_configs:
  - targets:
      - localhost
    labels:
      job: mysql                         #这里为刚才选择job下子标签
      __path__: /var/log/*log            #将采集的日志放在/var/log/*log下自动发现
EOF
~~~

- 新服务器起promail

~~~yaml
tee docker-compose-loki.yaml <<'EOF'
version: "v1"

services:
  promtail:
    image: grafana/promtail:2.0.0               #拉去镜像
    container_name: promtail-node              #镜像名称
    volumes:
      - /root/promtail/config.yml:/etc/promtail/config.yml    #挂载目录
      - /var/log:/var/log
    network_mode: 'host'
EOF

docker compose up -d
~~~

- 查询日志
  - `(job=“mysql”)|=“password”`

> 这篇doc并无法正常工作。待排查。。。
