---
title: GPU Exporter 与 Grafana 监控
tags:
  - GPU
  - NVIDIA
  - prometheus
  - grafana
  - monitoring
aliases:
  - GPU监控
  - GPU Exporter
---

# GPU Exporter 与 Grafana 监控

## 部署 NVIDIA GPU Exporter

本例在 GPU 宿主机上部署 Exporter，由 VMware 虚拟机中的 Prometheus 抓取指标。

```sh
# 下载并解压二进制包
# https://github.com/utkuozdemir/nvidia_gpu_exporter/releases/tag/v1.2.1
wget https://github.com/utkuozdemir/nvidia_gpu_exporter/releases/download/v1.2.1/nvidia_gpu_exporter_1.2.1_linux_x86_64.tar.gz
tar zxvf nvidia_gpu_exporter_1.2.1_linux_x86_64.tar.gz
# 创建 systemd 服务文件
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
# 启动 Exporter
sudo systemctl daemon-reload
sudo systemctl enable nvidia-gpu-exporter.service --now
# 检查指标
curl http://localhost:9835/metrics
```

## Prometheus 抓取数据

在 Prometheus 配置中添加以下抓取任务：

```yaml
- job_name: "gpu-exporter"
  static_configs:
    - targets:
        - '10.12.0.247:9835'
      labels:
        gpu: nvidia-rtx2000-ada
        app: gpu-exporter
```

宿主机内网 IP 会变化，而当前 Prometheus 环境无法解析其主机名。应先修复 DNS，或通过服务发现维护抓取目标。Pushgateway 主要用于短时批处理任务，不适合作为长期运行的 Exporter 的常规抓取替代方案。

## Grafana 数据展示

- [NVIDIA GPU Metrics Dashboard](https://grafana.com/grafana/dashboards/14574-nvidia-gpu-metrics/)

> [!warning] 时间同步
> 保持 Exporter、Prometheus 和 Grafana 所在主机的系统时间同步，便于正确采集和查看时间序列。
