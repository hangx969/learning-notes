# 环境准备

- 参考：https://www.aiwanyun.cn/archives/174

- rockylinux-8.10 (IP： 172.16.183.80)，安装docker、prometheus、grafana、node_exporter

# 被监控端安装node_exporter

- 可以从GitHub上的Prometheus项目页面下载node_exporter：https://github.com/prometheus/node_exporter/releases。
- 建议选择一个稳定但不是最新版本的node_exporter进行下载，以避免潜在的问题。下载完成后，将其上传到服务器上。

~~~sh
#amd平台
wget https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz
tar -xzf node_exporter-1.6.1.linux-amd64.tar.gz
cp node_exporter-1.6.1.linux-amd64/node_exporter /usr/local/bin/

#进程守护
cat > /etc/systemd/system/nodeexporter.service << EOF
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
systemctl start nodeexporter && systemctl enable nodeexporter && systemctl status nodeexporter
#访问宿主+9100端口既可访问Node Exporter采集的指标数据
~~~

# docker安装prometheus

- 配置文件
  - /etc/prometheus/rules主要是存放告警规则的目录
  - /prometheus-data是prometheus的数据目录
  - /etc/prometheus/prometheus.yml是prometheus主配置

~~~sh
mkdir -p /root/prometheus/data /root/prometheus/rules
#需要修改权限，否则prometheus访问不了
chmod 777 -R /root/prometheus
cd /root/prometheus/

####config文件示例###########
# 抓取规则
global:
  scrape_interval: 15s # 抓取间隔
  evaluation_interval: 15s # 评估间隔
# 触发规则
#rule_files:
#- /etc/prometheus/rules/*.rules
# alert告警服务器
#alerting:
  #alertmanagers:
  #- static_configs:
    #- targets: ['域名/服务器+端口']
# 监控客户端列表
scrape_configs:
- job_name: "测试服务器"
  static_configs:
  - targets: 
    - '域名/IP:9100'
    labels:
      name: "1号服务器"
      group: "测试服务器"
  - targets: 
    - '域名/IP:9100'
    labels:
      name: "2号服务器/编译/监控"
      group: "测试服务器"
- job_name: "应用服务器"
  static_configs:
  - targets: 
    - '域名/IP:9100'
    labels:
      name: "邮件服务器"
      group: "应用服务器"
  - targets: 
    - '域名/IP:9100'
    labels:
      name: "测试服务器"
      group: "应用服务器"
##############################################
tee /root/prometheus/prometheus.yml <<'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s
rule_files:
- /etc/prometheus/rules/*.rules
alerting:
  alertmanagers:
  - static_configs:
    - targets:
      - 172.16.183.80:9093
scrape_configs:
- job_name: "test-servers"
  static_configs:
  - targets:
    - 172.16.183.80:9100
    labels:
      name: rocky-1
      group: "test-servers"
  - targets:
    - 172.16.183.81:9100
    labels:
      name: rocky-2
      group: "test-servers"
- job_name: "docker-cAdvisior"
  static_configs:
  - targets: ["172.16.183.80:8080"]
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
#改完配置文件可以检查yaml格式：promtool check-config prometheus.yml
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
-v /root/grafana/data:/var/lib/grafana \
-p 9001:3000 \
-d grafana/grafana
#-v /root/grafana/config/grafana.ini:/etc/grafana/grafana.ini \
#9001:3000 内部端口为3000，我们映射到宿主机端口9001进行访问 访问登录页面需要输入账号密码，默认账号密码admin/admin
~~~

- 配置prometheus数据源
  - 仪表盘=>Connections=>Data sources
  - 右上角Add data source，选择第一个Prometheus作为数据源
  - 填写上刚刚部署的Prometheus的地址(http://172.16.183.80:9000)，并设置为默认数据源，然后拉到最下面保存便接入完成了。
- 导入仪表板
  - 仪表板-右上角导入仪表板-（提供三个好看的面板，分别是8919，9276，11074）
  - 点击load可以加载面板

> dashboard可以在这里查找、下载：https://grafana.com/grafana/dashboards/

# docker部署alertmanager

- 配置文件

  - /alertmanager-data 数据目录，持久化 

  - /etc/alertmanager/alertmanager.yml 是推送相关的配置

~~~yaml
mkdir -p /alertmanager/data
chmod -R 777 /alertmanager/data
tee /root/alertmanager/alertmanager.yml <<'EOF'
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

# docker部署cAdvisior容器监控

## 被控端部署cAdvisior

- 为了解决容器的监控问题，Google开发了一款容器监控工具cAdvisor（Container Advisor），它为容器用户提供了对其运行容器的资源使用和性能特征的直观展示。 它是一个运行守护程序，用于收集，聚合，处理和导出有关正在运行的容器的信息。
- cAdvisor可以对节点机器上的资源及容器进行实时监控和性能数据采集，包括CPU使用情况、内存使用情况、网络吞吐量及文件系统使用情况。cAdvisor使用go语言开发，如果想了解更多请访问其官方github：https://github.com/google/cadvisor

- cAdvisior自带一些指标监控，但不是很直观；我们这里配置prometheus抓取cAdvisior数据，并用grafana展示出来。（参考：https://mp.weixin.qq.com/s/GRexd30-oxLiwhBVjiOLew）

> Prometheus支持多种Exporter，这里我们使用Node Exporter 和 cAdvisor。其中，Node Exporter用于收集Host相关数据，cAdvisor用于收集容器相关数据

~~~sh
docker pull google/cadvisor
#docker pull lagoudocker/cadvisor:v0.37.0这个镜像拉不下来，换成google镜像了
docker run \
--volume=/:/rootfs:ro \
--volume=/var/run:/var/run:ro \
--volume=/sys:/sys:ro \
--volume=/var/lib/docker/:/var/lib/docker:ro \
--volume=/dev/disk/:/dev/disk:ro \
--publish=8080:8080 \
--detach=true \
--name=cadvisor \
--privileged \
--device=/dev/kmsg \
google/cadvisor
#访问宿主机IP:8080端口
~~~

## prometheus抓取cAdvisior数据

- 修改prometheus配置文件，添加cAdvisior内容

~~~sh
tee /root/prometheus/prometheus.yml <<'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s
rule_files:
- /etc/prometheus/rules/*.rules
alerting:
  alertmanagers:
  - static_configs:
    - targets:
      - 172.16.183.80:9093
scrape_configs:
- job_name: "test-servers"
  static_configs:
  - targets:
    - 172.16.183.80:9100
    labels:
      name: rocky1
      group: "test-servers"
- job_name: "docker-cAdvisior"
  static_configs:
  - targets: ["172.16.183.80:8080"]
  - targets: ["172.16.183.81:8080"]
EOF
~~~

- 重启prometheus容器，刷新配置文件

## grafana展示cAdvisior数据

- https://grafana.com/grafana/dashboards/13946-docker-cadvisor/，dashboard导入13946模板

> 注意：
>
> - VMWare虚机挂起的话，每次重新激活，时间同步会有问题导致prometheus抓取数据有时间偏差，从而grafana dashboard数据无法展示
>
> 解决：
>
> ~~~sh
> #rockylinux下使用chrony作为时间同步服务
> #手动强制同步
> chronyc -a makestep
> timedatectl set-ntp true
> systemctl restart chronyd.service
> #查看时间同步状态
> timedatectl status
> ~~~

