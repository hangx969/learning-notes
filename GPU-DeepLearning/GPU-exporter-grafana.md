# 部署开源gpu_exporter

- 这里在宿主机上部署exporter，在vmware虚机上的prometheus抓数据

~~~sh
#下载解压二进制包
#https://github.com/utkuozdemir/nvidia_gpu_exporter/releases/tag/v1.2.1
wget https://github.com/utkuozdemir/nvidia_gpu_exporter/releases/download/v1.2.1/nvidia_gpu_exporter_1.2.1_linux_x86_64.tar.gz
tar zxvf nvidia_gpu_exporter_1.2.1_linux_x86_64.tar.gz
#创建systemd服务启动文件
sudo cp nvidia_gpu_exporter /usr/bin/nvidia_gpu_exporter 
sudo tee /etc/systemd/system/nvidia-gpu-exporter.service <<'EOF'
[Unit]
Description=NVIDIA GPU Exporter

[Service]
ExecStart=/usr/bin/nvidia_gpu_exporter
Restart=always
RestartSec=15

[Install]
WantedBy=multi-user.target
EOF
#启动 Exporter 
systemctl daemon-reload
systemctl enable nvidia-gpu-exporter.service --now
systemctl restart nvidia-gpu-exporter.service
#检查指标
curl localhost:9835/metrics
~~~

# prometheus抓取数据

- 添加job

~~~sh
- job_name: "gpu-exporter"  
  static_configs:
  - targets: 
    - '10.12.0.247:9835'
    labels:
      gpu: nvidia-rtx2000-ada
      app: gpu-exporter
~~~

有个问题是宿主机内网IP会变，用hostname的话prometheus会报解析失败。我的思路：建一个pushgateway，宿主机推送到上面，prometheus去上面拉数据。

# grafana数据展示

- https://grafana.com/grafana/dashboards/14574-nvidia-gpu-metrics/

> 注意：prometheus抓取的数据非常依赖于系统时间准确，grafana server需要同步时间
