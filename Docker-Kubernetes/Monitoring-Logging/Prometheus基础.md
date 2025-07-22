# Prometheus简介

## 介绍

- Prometheus是一个开源的系统监控和报警系统，现在已经加入到CNCF基金会，成为继k8s之后第二个在CNCF托管的项目。
- 在kubernetes容器管理系统中，通常会搭配prometheus进行监控，同时也支持多种exporter采集数据，还支持pushgateway进行数据上报，Prometheus性能足够支撑上万台规模的集群。
- 其他监控服务比如：Zabbix、nagios、cattio、夜莺等，在k8s中，prometheus会更原生，配置起来更简便，修改配置文件即可部署监控。prometheus同样可以监控宿主机、windows、交换机等等，但是反过来就不一定能实现了。

- prometheus是监控平台，也是一个时序数据库，`TSDB`，专门存储大规模时间序列数据（性能指标、传感器数据、金融交易数据等），具有更高的效率和更好的性能。

## 配置文档

- Prometheus配置：https://prometheus.io/docs/prometheus/latest/configuration/configuration/

- Prometheus监控组件对应的exporter部署地址: https://prometheus.io/docs/instrumenting/exporters/
  - 可以通过官网给出的不同的exporter来采集不同的指标（比如采集mysql、redis等软件的指标，采集GPU等硬件指标，采集node的OS指标，官网都给出了不同的exporter）

- Prometheus基于k8s服务发现参考: https://github.com/prometheus/prometheus/blob/release-2.31/documentation/examples/prometheus-kubernetes.yml

## 特点

1. 多维度数据模型

   - 每一个时间序列数据，都有一个时间戳。可以通过指标名称和一大堆标签去做聚合、检索。

   - 比如：http_requests_total 接收http请求的总计数，度量名称为/api/tracks的http请求，可以打上不同的标签，获取不同的操作：method=POST的标签，method=GET的标签，查看不同的操作
   - 这个查询语言在这些度量和标签列表的基础上进行过滤和聚合。改变任何度量上的任何标签值，则会形成新的时间序列图。
2. 灵活的查询语言（PromQL）
   - 可以对采集的metrics指标进行加法，乘法，连接等操作。实现可视化、告警。
3. 存储简化：
   - 可以直接在本地部署，不依赖其他分布式存储；因为prometheus本身就是一个数据库。（zabbix等还需要单独部署mysql去存数据）
   - 部署多个prometheus实例，每个都是自治的独立的，都保存了完整的监控数据。一个挂了另外的还能独立工作。
   - **高效的存储：每个采样数据占3.5 bytes左右。比如：300万的时间序列，30s间隔，保留60天，消耗磁盘大概200G。**

4. 拉取模式：
   - prometheus服务端主动通过HTTP的pull方式采集时序数据；
   - 也有push模式，客户端push到中间网关pushgateway临时存储一下，prometheus server端再从pushgateway拉取数据；
   - 比如有一个`一次性/短生命周期的job`，运行完就退出了，pull模式不能持续的拉数据。这个时候可以让job主动把指标发到pushgateway，prometheus再从pushgateway去拉

5. 动态发现：
   - 可通过服务发现或者静态配置来发现目标服务对象（targets）。比如：
   - 基于k8s的服务发现，自动发现所有pod；基于文件的，比如某个文件写入了redis的ip和接口列表，能基于文件做服务发现；比如有很多台非K8s主机，可以部署一个consul，主机注册到consul，prometheus就能从consul上做服务发现。

6. 做高可用，可以对数据做异地备份，联邦集群，部署多套prometheus，pushgateway上报数据：
   - 比如，自己开发的应用，官网肯定没有exporter，就可以写脚本采集相应数据，用pushgateway推送到prometheus。
7. 可视化和告警支持

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

## 数据类型

### Counter

- Counter是计数器类型：
  - Counter 用于累计值，例如记录请求次数、任务完成数、错误发生次数。
  - 一直增加，不会减少。
  - 重启进程后，会被重置。

- 例如：
  - http_response_total{method="GET",endpoint="/api/tracks"} 100
  - http_response_total{method="GET",endpoint="/api/tracks"} 160

- Counter可以方便的了解事件产生的速率的变化，在PromQL内置的相关操作函数可以提供相应的分析，比如以HTTP应用请求量来进行说明：

  - 通过rate()函数获取HTTP请求量的增长率

    `rate(http_requests_total[5m])`

  - 查询当前系统中，访问量前10的HTTP地址

    `topk(10, http_requests_total)`

### Gauge

- Gauge是测量器类型：
  - Gauge是常规数值，例如温度变化、内存使用变化。
  - 可变大，可变小。
  - 重启进程后，会被重置

- 例如：
  - memory_usage_bytes{host="master-01"}  100
  - memory_usage_bytes{host="master-01"}  30
  - memory_usage_bytes{host="master-01"}  50

- 对于 Gauge 类型的监控指标，通过 PromQL 内置函数`delta()`可以获取样本在一段时间内的变化情况，例如，计算 CPU 温度在两小时内的差异：

  `dalta(cpu_temp_celsius{host="zeus"}[2h])`

- 还可以通过PromQL内置函数`predict_linear()`基于简单线性回归的方式，对样本数据的变化趋势做出预测。例如，基于 2 小时的样本数据，来预测主机可用磁盘空间在 4 个小时之后的剩余情况：`predict_linear(node_filesystem_free{job="node"}[2h], 4 \* 3600) < 0`

### histogram

- histogram是柱状图，在Prometheus系统的查询语言中，有三种作用：
  - 在一段时间范围内对数据进行采样（通常是请求持续时间或响应大小等），并将其计入可配置的存储桶（bucket）中. 后续可通过指定区间筛选样本，也可以统计样本总数，最后一般将数据展示为直方图。
  - 对每个采样点值累计和(sum)
  - 对采样点的次数累计和(count)

- 度量指标名称: `basename_`上面三类的作用度量指标名称
  - `basename_bucket{le="上边界"}`, 这个值为小于等于上边界的所有采样点数量
  - `basename_sum`
  - `basename_count`

- 为什需要用histogram柱状图？

  - 在大多数情况下人们都倾向于使用某些量化指标的平均值，例如 CPU 的平均使用率、页面的平均响应时间。这种方式的问题很明显，以系统 API 调用的平均响应时间为例：如果大多数 API 请求都维持在 100ms 的响应时间范围内，而个别请求的响应时间需要 5s，那么就会导致某些 WEB 页面的响应时间落到中位数的情况，而这种现象被称为长尾问题。

  - 为了区分是平均的慢还是长尾的慢，最简单的方式就是按照请求延迟的范围进行分组。例如，统计延迟在 0~10ms 之间的请求数有多少，而 10~20ms 之间的请求数又有多少。通过这种方式可以快速分析系统慢的原因。Histogram 和 Summary 都是为了能够解决这样问题的存在，通过 Histogram 和 Summary 类型的监控指标，我们可以快速了解监控样本的分布情况。

- 例如：

  样本的值分布在 bucket 中的数量，命名为 `basename_bucket{le="上边界"}`。这个值表示指标值小于等于上边界的所有样本数量。

  1、http 请求响应时间 <=0.005 秒 的请求次数为0

  `io_namespace_http_requests_latency_seconds_histogram_bucket{path="/",method="GET",code="200",le="0.005",} 0.0`

  2、http 请求响应时间 <=0.01 秒 的请求次数为0

  `io_namespace_http_requests_latency_seconds_histogram_bucket{path="/",method="GET",code="200",le="0.01",} 0.0`

   3、http 请求响应时间 <=0.025 秒 的请求次数为0

  `io_namespace_http_requests_latency_seconds_histogram_bucket{path="/",method="GET",code="200",le="0.025",} 0.0`

### summary

- 与 Histogram 类型类似，用于表示一段时间内的数据采样结果（通常是请求持续时间或响应大小等），但它直接存储了分位数（通过客户端计算，然后展示出来），而不是通过区间来计算。它也有三种作用：

  1、观察时间的quantiles (0~1), 显示为`basename{分位数="quantitles"}`

  2、`[basename]_sum`， 是指所有观察值的总和

  3、`[basename]_count`, 是指已观察到的事件计数值

- 例如：

  - quantiles

    - http 请求中有 50% 的请求响应时间在 3.052404983s以内 `io_namespace_http_requests_latency_seconds_summary{path="/",method="GET",code="200",quantile="0.5",} 3.052404983`

    - http 请求中有 90% 的请求响应时间是在8.003261666s以内

      `io_namespace_http_requests_latency_seconds_summary{path="/",method="GET",code="200",quantile="0.9",} 8.003261666`

  - basename_sum

    http 请求的总响应时间为 51.029495508s

    `io_namespace_http_requests_latency_seconds_summary_sum{path="/",method="GET",code="200",} 51.029495508`

  - basename_count

    当前一共发生了 12 次 http 请求

    `io_namespace_http_requests_latency_seconds_summary_count{path="/",method="GET",code="200",} 12.0`

## 组件

1. Prometheus Server: 用于收集和存储时间序列数据。
   - Retrieval负责在活跃的target主机上抓取监控指标数据
   - TSDB把采集到的数据存储到磁盘中
   - http server会将告警信息传递到alertmanager，推送到接收方

2. Client Library: 客户端库，检测应用程序代码，当Prometheus抓取实例的HTTP端点时，客户端库会将所有跟踪的metrics指标的当前状态发送到prometheus server端。

3. Exporters: 
   - 有一些服务或者非云原生的组件没有metrics接口，不能直接拉数据，就需要单独的exporter去采集数据。prometheus支持多种exporter，通过exporter可以采集metrics数据，然后发送到prometheus server端，所有向promtheus server提供监控数据的程序都可以被称为exporter

   - 大部分云原生组件是有metrics接口的，就不需要exporter了，比如etcd、api-server等。

4. Alertmanager: 从 Prometheus server 端接收到 alerts 后，会进行去重，分组，并路由到相应的接收方，发出报警，常见的接收方式有：电子邮件，微信，钉钉, slack等。

5. Grafana：监控仪表盘，可视化监控数据。安装prometheus的时候基本必装grafana。但是两者不是一个公司开发的。

6. pushgateway: 各个目标主机可上报数据到pushgateway，然后prometheus server统一从pushgateway拉取数据。

![image-20240103104154211](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202401031041340.png)

## 工作流程

1. Prometheus server可定期从活跃的（up）目标主机上（target）拉取监控指标数据，目标主机的监控数据可通过配置静态job或者服务发现的方式被prometheus server采集到，这种方式默认的pull方式拉取指标；也可通过pushgateway把采集的数据上报到prometheus server中；还可通过一些组件自带的exporter采集相应组件的数据；

2. Prometheus server把采集到的监控指标数据保存到本地磁盘或者数据库；

3. Prometheus采集的监控指标数据按时间序列存储，通过配置报警规则，把触发的报警发送到alertmanager

4. Alertmanager通过配置报警接收方，发送报警到邮件，微信或者钉钉等

5. Prometheus 自带的web ui界面提供PromQL查询语言，可查询监控数据

6. Grafana可接入prometheus数据源，把监控数据以图形化形式展示出

## 与Zabbix对比

![image-20240103111904910](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202401031119014.png)



# 安装方法

1. 二进制安装：go语言开发的，安一个go包就行
2. 容器安装
3. k8s安装：kube-prometheus-stack helm包。非常全，所有组件一键安装。推荐。

> 生产环境建议单独用一台工作节点去装prometheus

# PromQL查询语言

- PromQL（Prometheus Query Language）是 Prometheus 自己开发的表达式语言，语言表现力很丰富，内置函数也很多。使用它可以对时序数据进行筛选和聚合。

## 数据类型

PromQL 表达式计算出来的值有以下几种类型：

- 瞬时向量 (Instant vector): 一组时序，每个时序只有一个采样值

- 区间向量 (Range vector): 一组时序，每个时序包含一段时间内的多个采样值

- 标量数据 (Scalar): 一个浮点数

- 字符串 (String): 一个字符串，暂时未用 

### 瞬时向量选择器

- 瞬时向量选择器用来选择一组时序在某个采样点的采样值。最简单的情况就是指定一个度量指标，选择出所有属于该度量指标的时序的当前采样值。
- 比如下面的表达式：`apiserver_request_total`，可以通过在后面添加用大括号包围起来的一组标签键值对来对时序进行过滤。比如下面的表达式筛选出了 job 为 kubernetes-apiservers，并且 resource为 pod的时序：`apiserver_request_total{job="kubernetes-apiserver",resource="pods"}`

- 匹配标签值时可以是等于，也可以使用正则表达式。总共有下面几种匹配操作符：

  - =：完全相等

  - !=： 不相等

  - =~： 正则表达式匹配

  - !~： 正则表达式不匹配

- 下面的表达式筛选出了container是kube-scheduler或kube-proxy或kube-apiserver的时序数据:`container_processes{container=~"kube-scheduler|kube-proxy|kube-apiserver"}`

### 区间向量选择器

- 区间向量选择器类似于瞬时向量选择器，不同的是它选择的是过去一段时间的采样值。可以通过在瞬时向量选择器后面添加包含在 [] 里的时长来得到区间向量选择器。
- 比如下面的表达式选出了所有度量指标为apiserver_request_total且resource是pod的时序在过去1分钟的采样值：`apiserver_request_total{job="kubernetes-apiserver",resource="pods"}[1m]`

### 偏移向量选择器

- 偏移修饰器用来调整基准时间，使其往前偏移一段时间。偏移修饰器紧跟在选择器后面，使用 offset 来指定要偏移的量。
- 比如下面的表达式选择度量名称为apiserver_request_total的所有时序在 5 分钟前的采样值:`apiserver_request_total{job="kubernetes-apiserver",resource="pods"} offset 5m`

- 下面的表达式选择apiserver_request_total 度量指标在 1 周前的这个时间点过去 5 分钟的采样值:`apiserver_request_total{job="kubernetes-apiserver",resource="pods"} [5m] offset 1w`

## 聚合操作符

- PromQL 的聚合操作符用来将向量里的元素聚合得更少。总共有下面这些聚合操作符：

  - sum：求和

  - min：最小值

  - max：最大值

  - avg：平均值

  - stddev：标准差

  - stdvar：方差

  - count：元素个数

  - count_values：等于某值的元素个数

  - bottomk：最小的 k 个元素

  - topk：最大的 k 个元素

  - quantile：分位数

- 如：

  - 计算xianchaomaster1节点所有容器总计内存

    `sum(container_memory_usage_bytes{instance=~"xianchaomaster1"})/1024/1024/1024` 

  - 计算xianchaomaster1节点最近1m所有容器cpu使用率

    `sum (rate (container_cpu_usage_seconds_total{instance=~"xianchaomaster1"}[1m])) / sum (machine_cpu_cores{ instance =~"xianchaomaster1"}) * 100`

  - 计算最近1m所有容器cpu使用率的总和

    `sum (rate (container_cpu_usage_seconds_total{id!="/"}[1m])) by (id)`\#把id会打印出来

  > `rate()`函数用于计算时间序列数据的平均速率。这个函数通常用于处理计数器类型的指标

## 函数

- Prometheus 内置了一些函数来辅助计算，下面介绍一些典型的。

  - abs()：绝对值

  - sqrt()：平方根

  - exp()：指数计算

  - ln()：自然对数

  - ceil()：向上取整

  - floor()：向下取整

  - round()：四舍五入取整

  - delta()：计算区间向量里每一个时序第一个和最后一个的差值

  - sort()：排序
