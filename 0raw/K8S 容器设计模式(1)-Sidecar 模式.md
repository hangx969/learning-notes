---
title: "K8S 容器设计模式(1)-Sidecar 模式"
source: "https://mp.weixin.qq.com/s/LP79kNx9QRdTH44F5s46Kw"
author:
  - "[[iGevin]]"
published:
created: 2026-06-28
description: "SideCar 核心理念：就像摩托车旁边的\x26quot;边车\x26quot;，主容器负责核心业务，边车容器负责辅助功能"
tags:
  - "clippings"
---
iGevin GevinView *2026年6月17日 21:03*

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/MNKdRa5Kr2Jpd1NB7tpNCuNcLFJtX9jDwjymoRCKFmnw9WRBUOaOtZDVs8fowHAkULFN9qPtL7UTIyjrHe8trbRiagyXXKDw1KpUIpibvoQWw/640?wx_fmt=png&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

## 🤔 什么是容器设计模式？

容器设计模式（Container Design Patterns）是在 Kubernetes 这样的容器编排平台中，如何合理地组合和管理多个容器以实现复杂应用需求的一套方法论。它类似于软件开发中的"设计模式"，但专注于容器的组织和协作方式。

## 🚀 为什么需要容器设计模式？

单个容器通常只运行一个进程（比如一个 Web 服务），但实际应用场景往往需要多个进程协作，比如日志收集、数据预处理、服务代理等。如果把所有功能都塞进一个容器，会导致：

- • **维护困难** ：功能耦合，难以独立更新
- • **升级复杂** ：牵一发而动全身
- • **耦合度高** ：组件间依赖关系复杂
- • **资源浪费** ：无法精确控制资源分配

容器设计模式帮助我们将这些功能拆分到不同的容器中，并通过 Pod 这种机制让它们协作。

## Sidecar 模式（边车模式）

**🎯 核心理念** ：就像摩托车旁边的"边车"，主容器负责核心业务，边车容器负责辅助功能。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/MNKdRa5Kr2KjiaTabfXZkecP3BmicNYkGEWic2KRQAI3QFfaWj24eRBWNoqcUkXnUEIhYuHvpegbaVe9AtJljLicr6Px5yx5qzpR5U5p31PMhRE/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=1)

**📝 应用场景** ：

- • 📋 日志收集和转发
- • ⚙️ 配置文件同步
- • 🌐 服务网格代理（如 Istio Envoy）
- • 📊 监控数据收集

**💡 实际案例** ：  
一个 Web 应用容器旁边运行一个日志收集容器（如 Fluentd），后者不断读取主容器的日志并转发到 Elasticsearch 等存储系统。

## 🛠️ 实践配置示例

Sidecar 模式示例：Web 应用 + 日志收集

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/MNKdRa5Kr2KiaRNJciaondLMhTZ2ib8Y6ytl7C3IYCQNHWQuV8EzGhm77NTOv6XSKeaxue5c2h9ibuKvnGUjzoXWwSR8uoRsLMjfQUa2VbnONek/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=2)
```
apiVersion: v1
kind:Pod
metadata:
name:web-app-with-logging
spec:
containers:
# 主容器：Web 应用
-name:web-app
    image:nginx:1.20
    ports:
    -containerPort:80
    volumeMounts:
    -name:log-volume
      mountPath:/var/log/nginx

# Sidecar 容器：日志收集
-name:log-collector
    image:fluentd:v1.14
    volumeMounts:
    -name:log-volume
      mountPath:/var/log/nginx
    -name:fluentd-config
      mountPath:/fluentd/etc

volumes:
-name:log-volume
    emptyDir: {}
-name:fluentd-config
    configMap:
      name: fluentd-config
```

---

## What's More？

本文收录在我墨问专栏 **《 Kubernetes 学习笔记 》** ，欢迎大家订阅支持～

![图片](https://mmbiz.qpic.cn/mmbiz_jpg/MNKdRa5Kr2JA3GYGLiba051RYQEFQO207suU3pfJ7ibWwvh6b2EEkBrrEqHzVBhaAfHGZpRprzXsBO1bMrmVfPI00q3oKP92BSOliaErMHs0gk/640?wx_fmt=jpeg&from=appmsg&watermark=1#imgIndex=3)

**微信扫一扫赞赏作者**