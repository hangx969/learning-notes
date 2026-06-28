---
title: "K8S 容器设计模式 - Ambassador 模式"
source: "https://mp.weixin.qq.com/s/35uKYCFWbnyqp9AaH7EyZA"
author:
  - "[[iGevin]]"
published:
created: 2026-06-28
description:
tags:
  - "clippings"
---
iGevin GevinView *2026年6月19日 09:20*

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/MNKdRa5Kr2KSGzzYvKdRNnsXPVM5HT1vfVKAHK4BsPvqyeg6Tm0Su5WtHfyfFb9nQ2cGS8oa5AdAgmiaJkxyo7xbMYtFR5etV6pdDYSwcPC4/640?wx_fmt=png&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

## 什么是容器设计模式？

容器设计模式（Container Design Patterns）是在 Kubernetes 这样的容器编排平台中，如何合理地组合和管理多个容器以实现复杂应用需求的一套方法论。它类似于软件开发中的“设计模式”，但专注于容器的组织和协作方式。

## 为什么需要容器设计模式？

单个容器通常只运行一个进程（比如一个 Web 服务），但实际应用场景往往需要多个进程协作，比如日志收集、数据预处理、服务代理等。如果把所有功能都塞进一个容器，会导致：

- • **维护困难** ：功能耦合，难以独立更新
- • **升级复杂** ：牵一发而动全身
- • **耦合度高** ：难以复用和扩展

---

## Ambassador 模式（大使模式）

本次介绍的是 Ambassador 模式，即“大使”模式。

### 🎯 核心理念

像“使者”一样，负责与外部世界沟通，为主容器提供网络代理服务。它将复杂的网络通信逻辑从主应用中解耦，让主容器专注于业务逻辑。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/MNKdRa5Kr2INyY7yOpEp4TmVJBTDribnGFAmmtVvAlWYYT8SejqibdlCxqUkIZG9bzjicLqpIykV399iadhbhXEK45A9nPDaaCys776PbPfj45I/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=1)

### 📝 典型应用场景

- • **🗄️ 数据库连接代理** ：统一管理数据库连接、连接池和故障转移
- • **🔍 服务发现与负载均衡** ：动态发现后端服务并实现负载均衡
- • **🔐 网络安全与认证** ：集中处理 TLS 加密、身份验证和授权
- • **🚪 API 网关功能** ：作为 API 网关，处理路由、限流和监控

### 💡 实际案例

主容器通过 Ambassador 容器访问外部数据库集群，Ambassador 负责处理连接池、故障转移和安全认证，让主应用无需关心这些复杂的网络细节。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/MNKdRa5Kr2InXBrJ8OTyTa8uDEiaPiahR7jafnwksJvOHAibFgeg4VNp7Jj80laXKqFR6GiaibcYxXQD0hibmk0SibITicYpXtT0z8ggibGpmS52UonE/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=2)

---

## 实战示例：数据库代理

### Deployment 配置

```
apiVersion: apps/v1
kind:Deployment
metadata:
name:app-with-db-proxy
spec:
replicas:2
selector:
    matchLabels:
      app:web-service
template:
    metadata:
      labels:
        app:web-service
    spec:
      containers:
      # 主应用容器
      -name:web-service
        image:myapp:latest
        ports:
        -containerPort:8080
        env:
        -name:DB_HOST
          value:"localhost"# 通过 Ambassador 访问
        -name:DB_PORT
          value:"5432"
      
      # Ambassador 数据库代理容器
      -name:db-proxy
        image:haproxy:2.4
        ports:
        -containerPort:5432
        volumeMounts:
        -name:haproxy-config
          mountPath:/usr/local/etc/haproxy
        command: ["haproxy", "-f", "/usr/local/etc/haproxy/haproxy.cfg"]
      
      volumes:
      -name:haproxy-config
        configMap:
          name: haproxy-config
```

### ConfigMap 配置

HAProxy 配置文件如下：

```
apiVersion: v1
kind:ConfigMap
metadata:
name:haproxy-config
data:
haproxy.cfg:|
    global
        daemon
    defaults
        mode tcp
        timeout connect 5000ms
        timeout client 50000ms
        timeout server 50000ms
    
    frontenddb_frontend
        bind*:5432
        default_backenddb_servers
    
    backenddb_servers
        balanceroundrobin
        serverdb1postgres-primary.default.svc.cluster.local:5432check
        serverdb2postgres-replica.default.svc.cluster.local:5432check backup
```

---

## What's More？

本文收录在我墨问专栏 **《 Kubernetes 学习笔记 》** ，欢迎大家订阅支持～

![图片](https://mmbiz.qpic.cn/mmbiz_jpg/MNKdRa5Kr2JA3GYGLiba051RYQEFQO207suU3pfJ7ibWwvh6b2EEkBrrEqHzVBhaAfHGZpRprzXsBO1bMrmVfPI00q3oKP92BSOliaErMHs0gk/640?wx_fmt=jpeg&from=appmsg&watermark=1#imgIndex=3)

**微信扫一扫赞赏作者**

阅读原文