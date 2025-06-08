# prometheus联邦集群方案

- 对于大部分监控规模而言，我们只需要在每一个数据中心 (例如：EC2可用区，Kubernetes集群)安装一个Prometheus Server实例，就可以在各个数据中心处理上千规模的集群。同时将Prometheus Server部署到不同的数据中心可以避免网络配置的复杂性

- 联邦集群简言之就是搭建多个prometheus去监控不同的数据，汇总到一个prometheus。

  ![image-20240617110353549](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202406171103712.png)

- 联邦集群的核心在于每一个Prometheus Server都包含一个用于获取当前实例中监控样本的接口/federate。对于中心Prometheus Server而言，无论是从其他的Prometheus实例还是Exporter实例中获取数据实际上并没有任何差异。

# 安装prometheus

## 环境搭建

- 192.168.40.180： 主节点，主机名: prometheusserver
- 192.168.40.181： 联邦节点1，主机名: prometheus-node1
- 192.168.40.181: 联邦节点1的目标采集服务，部署node-exporter

## 安装prometheus主节点

~~~sh
mkdir /apps
cd /apps/
tar zxvf /root/prometheus-2.32.1.linuxamd64.tar.gz
ln -sv /apps/prometheus-2.32.1.linuxamd64 /apps/prometheus
cd /apps/prometheus
# 检测配置文件、检测 metrics 数据等
./promtool check config prometheus.yml
# 创建启动脚本文件
tee /etc/systemd/system/prometheus.service <<'EOF'
[Unit]
Description=Prometheus Server
Documentation=https://prometheus.io/docs/introduction/overview/
After=network.target
[Service]
Restart=on-failure
WorkingDirectory=/apps/prometheus/
ExecStart=/apps/prometheus/prometheus --
config.file=/apps/prometheus/prometheus.yml
[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl start prometheus
systemctl enable prometheus
~~~

## 安装主节点node-exporter

~~~sh
cd /apps/
tar zxvf /root/node_exporter-1.3.1.linux-amd64.tar.gz
ln -sv /apps/node_exporter-1.3.1.linux-amd64 /apps/node_exporter
cd /apps/node_exporter

tee /etc/systemd/system/node-exporter.service <<'EOF'
[Unit]
Description=Prometheus Node Exporter
After=network.target
[Service]
ExecStart=/apps/node_exporter/node_exporter
[Install]
wantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl restart node-exporter
systemctl enable node-exporter
~~~

## 安装prometheus联邦节点

~~~sh
cd /apps/
tar zxvf /root/prometheus-2.32.1.linuxamd64.tar.gz
ln -sv /apps/prometheus-2.32.1.linuxamd64 /apps/prometheus
cd /apps/prometheus
# 检测配置文件、检测 metrics 数据等
./promtool check config prometheus.yml

tee /etc/systemd/system/prometheus.service <<'EOF'
[Unit]
Description=Prometheus Server
Documentation=https://prometheus.io/docs/introduction/overview/
After=network.target
[Service]
Restart=on-failure
WorkingDirectory=/apps/prometheus/
ExecStart=/apps/prometheus/prometheus --
config.file=/apps/prometheus/prometheus.yml
[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl restart prometheus
systemctl enable prometheus
~~~

## 安装联邦节点node-exporter

~~~sh
cd /apps/
tar zxvf /root/node_exporter-1.3.1.linuxamd64.tar.gz
ln -sv /apps/node_exporter-1.3.1.linux-amd64 /apps/node_exporter
cd /apps/node_exporter

tee /etc/systemd/system/nodeexporter.service <<'EOF'
[Unit]
Description=Prometheus Node Exporter
After=network.target
[Service]
ExecStart=/apps/node_exporter/node_exporter
[Install]
wantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl restart node-exporter
systemctl enable node-exporter
~~~

> 注：以上二进制安装包可以在prometheus官网下载

## 配置联邦节点node-exporter监控

~~~sh
vim /apps/prometheus/prometheus.yml
#追加新的job
- job_name: 'prometheus-node'
  static_configs:
    - targets: ['192.168.40.181:9100'] #9100是node_exporter1的接口

systemctl restart node-exporter
systemctl restart prometheus.service
~~~

- 访问联邦节点的prometheus 192.168.40.181:9090/targets，可以看到配置的job name：prometheus-node

## 主节点配置联邦

- 通过这个配置，Prometheus会定期从指定的目标Prometheus实例获取指标数据，并根据参数中定义的条件进行筛选。符合条件的指标数据将被保留供后续使用

~~~sh
vim /apps/prometheus/prometheus.yml
#追加新的job
- job_name: 'prometheus-federate-2.101'
  scrape_interval: 10s
  honor_labels: true
  metrics_path: '/federate'
  params:
    'match[]':
     - '{job="prometheus"}'
     - '{__name__=~"job:.*"}'
     - '{__name__=~"node.*"}'
  static_configs:
  - targets: ["192.168.40.181:9090"]
  
# 通过URL中的match[]参数指定我们可以指定需要获取的时间序列。match[]参数必须是一个瞬时向量选择器，例如up或者{job=“prometheus"}。配置多个match[]参数，用于获取多组时间序列的监控数据。
# horbor_labels配置true可以确保当采集到的监控指标冲突时，能够自动忽略冲突的监控数据。如果为false时，prometheus会自动将冲突的标签替换为”exported_“的形式。

systemctl restart prometheus
~~~

- 访问访问主节点的prometheus 192.168.40.180:9090，查看抓取到的prometheus-federate-2.101数据。在graph界面查询node_load1数据
- 后面可以接入grafana可视化展示监控数据。

