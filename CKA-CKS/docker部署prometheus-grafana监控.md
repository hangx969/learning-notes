# 环境准备

- 参考：https://www.aiwanyun.cn/archives/174

- rockylinux-8.9，安装docker、prometheus、grafana、node exporter

# 被监控端安装node_exporter

~~~sh
#amd平台
wget https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz
tar -xzf node_exporter-1.6.1.linux-amd64.tar.gz
cp node_exporter-1.6.1.linux-amd64/node_exporter /usr/local/bin/

#进程守护
cat > /etc/systemd/system/notdeexporter.service << EOF
[Unit]
Description=node-exporter
After=network.target network-online.target nss-lookup.target
[Service]
Type=simple
StandardError=journal
ExecStart = /usr/local/bin/node_exporter
ExecReload=/bin/kill -HUP $MAINPID
LimitNOFILE=512000
Restart=on-failure
RestartSec=10s
[Install]
WantedBy=multi-user.target
EOF

#启动
systemctl daemon-reload
systemctl start notdeexporter
systemctl enable notdeexporter
systemctl status notdeexporter
#访问宿主+9100端口既可访问Node Exporter采集的指标数据
~~~

# docker安装prometheus

- 配置文件
  - /etc/prometheus/rules主要是存放告警规则的目录
  - /prometheus-data是prometheus的数据目录
  - /etc/prometheus/prometheus.yml是prometheus主配置

~~~sh
mkdir -p /root/prometheus/data /root/prometheus/rules
cd /root/prometheus/

tee /root/prometheus/prometheus.yml <<'EOF'
# 抓取规则
global:
  scrape_interval: 15s # 抓取间隔
  evaluation_interval: 15s # 评估间隔
# 触发规则
rule_files:
  - /etc/prometheus/rules/*.rules
# alert告警服务器
alerting:
  alertmanagers:
    - static_configs:
        - targets: ['域名/服务器+端口']
# 监控客户端列表
scrape_configs:
  - job_name: "测试服务器"
    static_configs:
      - targets: ['域名/IP:9100']
        labels:
          name: "1号服务器"
          group: "测试服务器"
      - targets: ['域名/IP:9100']
        labels:
          name: "2号服务器/编译/监控"
          group: "测试服务器"
  - job_name: "应用服务器"
    static_configs:
      - targets: ['域名/IP:9100']
        labels:
          name: "邮件服务器"
          group: "应用服务器"
      - targets: ['域名/IP:9100']
        labels:
          name: "测试服务器"
          group: "应用服务器"
EOF
~~~

~~~yaml
tee /root/prometheus/rules/hoststats-alert.rules <<'EOF'
groups:
- name: hostStatsAlert
  rules:
  - alert: CPU告警
    expr: (1 - avg(rate(node_cpu_seconds_total{vendor=~"",account=~"",mode="idle",name=~".*.*"}[5m])) by (name)) * 100 > 85
    for: 1m
    labels:
      severity: warning
    annotations:
      summary: "Instance {{ $labels.name }} CPU usgae high"
      description: "{{ $labels.name }} CPU usage above 85% (current value: {{ $value }})"
  - alert: 内存告警
    expr: (1 - (node_memory_MemAvailable_bytes{vendor=~"",account=~"",name=~".*.*"} / (node_memory_MemTotal_bytes{vendor=~"",account=~"",name=~".*.*"})))* 100 > 95
    for: 1m
    labels:
      severity: warning
    annotations:
      summary: "Instance {{ $labels.name }} MEM usgae high"
      description: "{{ $labels.name }} MEM usage above 95% (current value: {{ $value }})"
  - alert: 磁盘告警
    expr: max((node_filesystem_size_bytes{vendor=~"",account=~"",name=~".*.*",fstype=~"ext.?|xfs"}-node_filesystem_free_bytes{vendor=~"",account=~"",name=~".*.*",fstype=~"ext.?|xfs"}) *100/(node_filesystem_avail_bytes {vendor=~"",account=~"",name=~".*.*",fstype=~"ext.?|xfs"}+(node_filesystem_size_bytes{vendor=~"",account=~"",name=~".*.*",fstype=~"ext.?|xfs"}-node_filesystem_free_bytes{vendor=~"",account=~"",name=~".*.*",fstype=~"ext.?|xfs"})))by(name) > 80
    for: 1m
    labels:
      severity: warning
    annotations:
      summary: "Instance {{ $labels.name }} DISK usgae high"
      description: "{{ $labels.name }} DISK usage above 80% (current value: {{ $value }})"
  - alert: 主机宕机
    expr: up == 0
    for: 1m
    labels:
      severity: warning
    annotations:
      summary: "Instance {{ $labels.name }} 停止工作"
      description: "{{ $labels.name }} 宕机超过1分钟 (current value: {{ $value }})"
EOF
~~~

- 启动容器

~~~sh
docker stop prometheusserver
docker rm prometheusserver
docker run -i --restart=always \
--name prometheusserver \
-p 9000:9090 \
-v /root/prometheus/data:/prometheus-data \
-v /root/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml \
-v /root/prometheus/rules:/etc/prometheus/rules \
-d prom/prometheus --config.file=/etc/prometheus/prometheus.yml --storage.tsdb.path=/prometheus-data/ 
#-v <主机目录>:<容器目录>
#9090是容器内部端口，9000是外部暴露端口，可以通过服务端IP+9000端口访问
#在UI界面-Status-Rules中可以看到前面配置的alert规则
~~~

# docker安装grafana

- 配置文件

  - /etc/grafana/grafana.ini是grafana的主要配置文件，可自行启动容器拷贝一份出来进行修改，这里一般不修改 

  - /var/lib/grafana是grafana的持久化数据目录，需要从容器中映射出。提示：这里需要把映射出来的数据目录修改最高权限，否则容器启动后将会出现无法访问的情况 

    ```sh
    mkdir -p /root/grafana/data
    chmod 777 /root/grafana/data 
    ```

- 启动容器

~~~sh
docker run -i --restart=always \
--name grafanaserver \
-v /root/grafana/config/grafana.ini:/etc/grafana/grafana.ini \
-v /root/grafana/data:/var/lib/grafana \
-p 9001:3000 \
-d grafana/grafana
#9001:3000 内部端口为3000，我们映射到宿主机端口9001进行访问 访问登录页面需要输入账号密码，默认账号密码admin/admin
~~~

- 配置prometheus数据源
  - 仪表盘=>Connections=>Data sources
  - 右上角Add data source，选择第一个Prometheus作为数据源
  - 填写上刚刚部署的Prometheus的地址，并设置为默认数据源，然后拉到最下面保存便接入完成了。
- 导入仪表板
  - 仪表板-右上角导入仪表板-（提供三个好看的面板，分别是8919，9276，11074）
  - 点击load可以加载面板

> dashboard可以在这里查找、下载：https://grafana.com/grafana/dashboards/

# docker部署alertmanager

- 配置文件

  - /alertmanager-data 数据目录，持久化 

  - /etc/alertmanager/alertmanager.yml 是推送相关的配置

~~~yaml
mkdir -p /alertmanager-data
tee /etc/alertmanager/alertmanager.yml <<'EOF'
global:
  resolve_timeout: 1m
  smtp_smarthost: 'smtp.163.com:25'
  smtp_from: 'xuhang969@163.com' #指定从哪个邮箱发告警
  smtp_auth_username: 'xuhang969@163.com' #邮箱地址
  smtp_auth_password: 'xxx' #smtp授权码
  smtp_require_tls: false

route:
  group_by: ['alertname']
  group_wait: 10s       # 组告警等待时间。也就是告警产生后等待10s再发出去，10s期间如果有同组告警一起发出
  group_interval: 10s    # 上下两组发送告警的间隔时间
  repeat_interval: 30m    # 若产生重复告警，间隔多久再重发一次告警
  receiver: 'default-receiver'

receivers:
  - name: default-receiver
    email_configs:
      - to: xxxxx@qq.com #接收报警的邮箱
        send_resolved: true
EOF
~~~

- 启动容器

~~~sh
docker run -i --restart=always \
--name alertmanagerserver \
-p 9002:9093 \
-v /root/alertmanager/data:/alertmanager-data \
-v /root/alertmanager/alertmanager.yml:/etc/alertmanager/alertmanager.yml \
-d prom/alertmanager --config.file=/etc/alertmanager/alertmanager.yml --storage.path=/alertmanager-data/
#9002:9093 内部端口是9003，通过宿主机的9002进行访问或者代理访问。启动服务后，访问9002端口进行查看，如能进行访问，则部署成功。
~~~