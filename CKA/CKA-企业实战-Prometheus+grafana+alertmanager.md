# Prometheus简介

## 介绍

- Prometheus是一个开源的系统监控和报警系统，现在已经加入到CNCF基金会，成为继k8s之后第二个在CNCF托管的项目。

- 在kubernetes容器管理系统中，通常会搭配prometheus进行监控，同时也支持多种exporter采集数据，还支持pushgateway进行数据上报，Prometheus性能足够支撑上万台规模的集群。
- 其他监控服务比如：Zabbix、nagios、cattio、夜莺等，在k8s中，prometheus会更原生，配置起来更简便，修改配置文件即可部署监控。

## 配置文档

- Prometheus配置：https://prometheus.io/docs/prometheus/latest/configuration/configuration/

- Prometheus监控组件对应的exporter部署地址: https://prometheus.io/docs/instrumenting/exporters/
  - 可以通过官网给出的不同的exporter来采集不同的指标（比如采集mysql、redis等软件的指标，采集GPU等硬件指标，采集node的OS指标，官网都给出了不同的exporter）

- Prometheus基于k8s服务发现参考: https://github.com/prometheus/prometheus/blob/release-2.31/documentation/examples/prometheus-kubernetes.yml

## 特点

1. 多维度数据模型

   - 每一个时间序列数据都由metric度量指标名称和它的标签labels键值对集合唯一确定：

   - 比如：http_requests_total 接收http请求的总计数，度量名称为/api/tracks的http请求，可以打上不同的标签，获取不同的操作：method=POST的标签，method=GET的标签，查看不同的操作
   - 这个查询语言在这些度量和标签列表的基础上进行过滤和聚合。改变任何度量上的任何标签值，则会形成新的时间序列图。

2. 灵活的查询语言（PromQL）
   - 可以对采集的metrics指标进行加法，乘法，连接等操作；

3. 可以直接在本地部署，不依赖其他分布式存储；

4. 通过基于HTTP的pull方式采集时序数据；

5. 可以通过中间网关pushgateway的方式把时间序列数据推送到prometheus server端；

6. 可通过服务发现或者静态配置来发现目标服务对象（targets）。

7. 有多种可视化图像界面，如Grafana等。

8. **高效的存储：每个采样数据占3.5 bytes左右。比如：300万的时间序列，30s间隔，保留60天，消耗磁盘大概200G。**

9. 做高可用，可以对数据做异地备份，联邦集群，部署多套prometheus，pushgateway上报数据：
   - 比如，自己开发的应用，官网肯定没有exporter，就可以写脚本采集相应数据，用pushgateway推送到prometheus。

## schema

- 在时间序列中的每一个点称为一个样本（sample），样本由以下三部分组成：

  - 指标（metric）：指标名称和描述当前样本特征的 labelsets；

  - 时间戳（timestamp）：一个精确到毫秒的时间戳；

  - 样本值（value）： 一个 float64 的浮点型数据表示当前样本的值。

- 表示方式：

  - 通过如下表达方式表示指定指标名称和指定标签集合的时间序列：

    `<metric name>{<label name>=<label value>, ...}`

  - 例如，指标名称为 api_http_requests_total，标签为 method="POST" 和 handler="/messages" 的时间序列可以表示为：

    `api_http_requests_total{method="POST", handler="/messages"}`

## 组件

1. Prometheus Server: 用于收集和存储时间序列数据。

2. Client Library: 客户端库，检测应用程序代码，当Prometheus抓取实例的HTTP端点时，客户端库会将所有跟踪的metrics指标的当前状态发送到prometheus server端。

3. Exporters: prometheus支持多种exporter，通过exporter可以采集metrics数据，然后发送到prometheus server端，所有向promtheus server提供监控数据的程序都可以被称为exporter

4. Alertmanager: 从 Prometheus server 端接收到 alerts 后，会进行去重，分组，并路由到相应的接收方，发出报警，常见的接收方式有：电子邮件，微信，钉钉, slack等。

5. Grafana：监控仪表盘，可视化监控数据

6. pushgateway: 各个目标主机可上报数据到pushgateway，然后prometheus server统一从pushgateway拉取数据。

![image-20240103104154211](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202401031041340.png)

## 工作流程

