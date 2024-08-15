# 二进制部署prometheus

- 下载安装包
  - 官网地址：https://prometheus.io/download/，选择带有“LTS”样式的版本，这是稳定版本，推荐。


~~~sh
#以prometheus-2.45.5.linux-amd64.tar.gz为例
tar xf prometheus-2.45.5.linux-amd64.tar.gz 
mv prometheus-2.45.5.linux-amd64 prometheus
cd prometheus
~~~

~~~sh
#配置文件
tee prometheus.yml <<'EOF'
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
EOF
~~~

- systemd管理prometheus服务

~~~sh
tee prometheus.service <<'EOF'
[Unit]
Description=Prometheus service
After=network-online.target

[Service]
Type=simple
ExecStart=/usr/local/prometheus/prometheus --config.file=/usr/local/prometheus/prometheus.yml --log.level=warn --storage.tsdb.path=/usr/local/prometheus/data/
Restart=on-failure
ExecStop=/usr/bin/kill -9 MAINPID

[Install]
WantedBy=multi-user.target
EOF

mv prometheus.service /usr/lib/systemd/system/
cd ..
mv prometheus /usr/local/
cd /usr/local/prometheus/
systemctl daemon-reload
systemctl enable prometheus
systemctl start prometheus
systemctl status prometheus
~~~

~~~sh
#查看监听端口
ps -ef | grep prometheus
netstat -tunlp | grep 25427
#暴露9090端口
~~~

- 浏览器访问宿主机IP:9090端口即可

# 二进制部署grafana

- 下载安装包

~~~sh
wget https://dl.grafana.com/enterprise/release/grafana-enterprise-10.3.3.linux-amd64.tar.gz
tar -zxvf grafana-enterprise-10.3.3.linux-amd64.tar.gz
mv grafana-v10.3.3 /opt/grafana
~~~

~~~sh
tee /usr/lib/systemd/system/grafana.service <<'EOF'
[Unit]
Description=grafana
[Service]
ExecStart=/opt/grafana/bin/grafana-server -homepath=/opt/grafana
ExecReload=/bin/kill -HUP $MAINPID
KillMode=process
Restart=on-failure
[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl start grafana.service
systemctl enable grafana.service
~~~

# rpm部署grafana

~~~sh
sudo yum install -y https://dl.grafana.com/enterprise/release/grafana-enterprise-10.3.3-1.x86_64.rpm
systemctl daemon-reload
systemctl start grafana-server
systemctl enable grafana-server
~~~

# 二进制部署node_exporter

# 被监控端二进制安装node_exporter

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

# 

