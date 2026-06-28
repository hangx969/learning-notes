---
title: "K8S 容器设计模式 - Adapter 模式"
source: "https://mp.weixin.qq.com/s/MaNQDfrLlcZNaWffSQYF0Q"
author:
  - "[[iGevin]]"
published:
created: 2026-06-28
description:
tags:
  - "clippings"
---
iGevin GevinView *2026年6月22日 12:05*

![图片](https://mmbiz.qpic.cn/mmbiz_png/MNKdRa5Kr2LPYrIibnrDicd7ic1gQ7pj8A1f2D3FZcXRQ5JmUSoT06iaCRXhCdSth5ic1vr7JcustUzn0gorcLwEbYG6o6Zff0CnGjmbac6X3iasg/640?wx_fmt=png&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

接前文：

[K8S 容器设计模式 - Ambassador 模式](https://mp.weixin.qq.com/s?__biz=MzIzNjQyMzc0Mw==&mid=2247486931&idx=1&sn=1c25babe2a19d778825a5762371b256d&scene=21#wechat_redirect)

继续介绍 k8s 的常用容器设计模式。

**🎯 核心理念** ：

Adapter 模式（适配器模式）如同一个"转换器"，主要负责数据格式转换和协议适配，使原本不兼容的系统能够顺利协作。

![图片](https://mmbiz.qpic.cn/mmbiz_png/MNKdRa5Kr2IrCKLZuIhg4CVXvu2u1xlKQ2tqaF4AFUzLWPRRFzcYUtibYhQBickZhwe4vfKLwLzJAmcXQsLr6l4e8MQ4aEoMKjS4tDwluicibjs/640?wx_fmt=png&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=1)

**📝 应用场景** ：

**• 📋 日志格式标准化** ：将不同格式的日志统一转换为标准格式

**• 📊 监控指标转换** ：将各种监控指标转换为统一的数据格式

**• 🔄 协议转换** ：实现不同协议间的转换，如 HTTP 到 gRPC

**• 🔧 数据格式适配** ：调整数据格式以满足不同系统的需求

**💡 实际案例** ：

主容器输出原始日志，Adapter 容器负责将日志转换为 JSON 格式，并添加必要的元数据，然后将处理后的数据发送到 Prometheus 监控系统。

**实践：监控数据转换**

Deployment:

```
apiVersion: apps/v1
kind:Deployment
metadata:
name:legacy-app-with-adapter
spec:
replicas:1
selector:
    matchLabels:
      app:legacy-service
template:
    metadata:
      labels:
        app:legacy-service
    spec:
      containers:
      # 主应用容器（遗留系统）
      -name:legacy-app
        image:legacy-service:1.0
        ports:
        -containerPort:8080
        volumeMounts:
        -name:metrics-volume
          mountPath:/var/metrics
      
      # Adapter 监控适配器容器
      -name:metrics-adapter
        image:prometheus/node-exporter:latest
        ports:
        -containerPort:9100
        volumeMounts:
        -name:metrics-volume
          mountPath:/host/metrics
        -name:adapter-script
          mountPath:/scripts
        command: ["/scripts/convert-metrics.sh"]
        env:
        -name:LEGACY_METRICS_PATH
          value:"/host/metrics"
        -name:PROMETHEUS_PORT
          value:"9100"
      
      volumes:
      -name:metrics-volume
        emptyDir: {}
      -name:adapter-script
        configMap:
          name:metrics-adapter-script
          defaultMode: 0755
```

Configmap:

```
apiVersion: v1
kind:ConfigMap
metadata:
name:metrics-adapter-script
data:
convert-metrics.sh:|
    #!/bin/bash
    # 转换遗留系统的监控数据格式为 Prometheus 格式
    while true; do
      # 读取遗留系统的监控文件
      if [ -f "$LEGACY_METRICS_PATH/app.metrics" ]; then
        # 转换格式并输出到 Prometheus 格式
        awk '{
          if ($1 == "cpu_usage") {
            print "legacy_cpu_usage_percent " $2
          }
          if ($1 == "memory_used") {
            print "legacy_memory_used_bytes " $2
          }
          if ($1 == "requests_total") {
            print "legacy_http_requests_total " $2
          }
        }' "$LEGACY_METRICS_PATH/app.metrics" > /tmp/prometheus_metrics.prom
        
        # 启动简单的 HTTP 服务器提供 metrics
        python3 -c "
importhttp.server
importsocketserver
importos

class MetricsHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        ifself.path=='/metrics':
            self.send_response(200)
            self.send_header('Content-type','text/plain')
            self.end_headers()
            try:
                withopen('/tmp/prometheus_metrics.prom','r')as f:
                    self.wfile.write(f.read().encode())
            except FileNotFoundError:
                self.wfile.write(b'#Nometricsavailable\n')
        else:
            self.send_response(404)
            self.end_headers()

withsocketserver.TCPServer(('',$PROMETHEUS_PORT),MetricsHandler) as httpd:
    httpd.serve_forever()
" &
      fi
      sleep 30
    done
```

---

## What's More？

本文收录在我墨问专栏 **《 Kubernetes 学习笔记 》** ，欢迎大家订阅支持～

![图片](https://mmbiz.qpic.cn/mmbiz_jpg/MNKdRa5Kr2JA3GYGLiba051RYQEFQO207suU3pfJ7ibWwvh6b2EEkBrrEqHzVBhaAfHGZpRprzXsBO1bMrmVfPI00q3oKP92BSOliaErMHs0gk/640?wx_fmt=jpeg&from=appmsg&watermark=1#imgIndex=2)

**微信扫一扫赞赏作者**

阅读原文