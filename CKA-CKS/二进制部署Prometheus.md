# 下载安装包

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

# systemd管理prometheus服务

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
