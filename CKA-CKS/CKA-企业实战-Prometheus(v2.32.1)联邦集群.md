# prometheus联邦集群方案

- 对于大部分监控规模而言，我们只需要在每一个数据中心 (例如：EC2可用区，Kubernetes集群)安装一个Prometheus Server实例，就可以在各个数据中心处理上千规模的集群。同时将Prometheus Server部署到不同的数据中心可以避免网络配置的复杂性

- 联邦集群简言之就是搭建多个prometheus去监控不同的数据，汇总到一个prometheus。

  ![image-20240617110353549](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202406171103712.png)

- 联邦集群的核心在于每一个Prometheus Server都包含一个用于获取当前实例中监控样本的接口/federate。对于中心Prometheus Server而言，无论是从其他的Prometheus实例还是Exporter实例中获取数据实际上并没有任何差异。

~~~yaml
scrape_configs:
- job_name: 'federate'
scrape_interval: 15s
honor_labels: true
metrics_path: '/federate'
params:
'match[]':
- '{job="prometheus"}'
- '{__name__=~"job:.*"}'
- '{__name__=~"node.*"}'
static_configs:
- targets:
- '192.168.40.181:9090'
# 通过URL中的match[]参数指定我们可以指定需要获取的时间序列。match[]参数必须是一个瞬时向量选择器，例如up或者{job=“prometheus"}。配置多个match[]参数，用于获取多组时间序列的监控数据。
#horbor_labels配置true可以确保当采集到的监控指标冲突时，能够自动忽略冲突的监控数据。如果为false时，prometheus会自动将冲突的标签替换为”exported_“的形式。
~~~

# 安装prometheus

## 环境搭建

- 192.168.40.180： 主节点，主机名：prometheusserver
- 192.168.40.181： 联邦节点1，主机名prometheus-node1
- 192.168.40.181: 联邦节点1的目标采集服务，部署node-exporter

## 安装prometheus主节点

~~~sh
mkdir /apps
cd /apps/
tar zxvf /root/prometheus-2.32.1.linuxamd64.tar.gz
ln -sv /apps/prometheus-2.32.1.linuxamd64 /apps/prometheus
cd /apps/prometheus
~~~

