---
title: "K8S工具推荐：使用Argo Rollouts实现GitOps自动化测试与回滚"
source: "https://mp.weixin.qq.com/s?__biz=MzkxNzAyMzA3Nw==&mid=2247485755&idx=1&sn=50463bc31bb2610d18a843881b1515ac&scene=21&poc_token=HNo26mmjFaS-gZuoXULeSLZk_JpM6mam05HLezCp"
author:
  - "[[海笑]]"
published:
created: 2026-04-23
description:
tags:
  - "clippings"
---
海

在现代 Kubernetes 应用管理中， **GitOps** 是一种广受欢迎的方式，它通过声明式配置和自动化流程极大地提高了交付效率。然而，许多人对 GitOps 持谨慎态度，担心变更一旦推送到 Git 仓库后会直接生效，可能引发不可预知的风险。针对这一问题， **Argo Rollouts** 提供了一种安全、自动化的部署方式，支持蓝绿部署和金丝雀部署，同时具备强大的自动化测试与回滚能力。

本文将介绍如何使用 Argo Rollouts 实现自动化测试与回滚，并通过具体的代码示例来说明其使用方法。

> https://jason-umiker.medium.com/automatic-rollback-of-your-gitops-with-argo-rollouts-04f94baa2d03


---

### 什么是 Argo Rollouts？

**Argo Rollouts** 是 Argo 项目的一部分，它是一个增强型 Kubernetes 部署控制器，支持更高级的部署策略，包括：

1. 1.**蓝绿部署 (Blue/Green Deployments)** ：通过两个版本的服务并行运行，一个用于生产流量，另一个用于预览，用户可以在验证新版本无误后切换流量。
2. 2.**金丝雀部署 (Canary/Progressive Deployments)** ：逐步将生产流量切换到新版本，通过实时监控来验证新版本的稳定性。

Argo Rollouts 替代了 Kubernetes 原生的 `Deployment` 控制器，但只适用于使用 `Deployment` 的工作负载（如 Pod），不适用于 `DaemonSet` 或 `StatefulSet` 等其他控制器。

---

### 蓝绿部署的实现

以下是一个蓝绿部署的完整示例配置文件：

```
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: bluegreen-demo
  labels:
    app: bluegreen-demo
spec:
  replicas: 1
  revisionHistoryLimit: 1
  selector:
    matchLabels:
      app: bluegreen-demo
  template:
    metadata:
      labels:
        app: bluegreen-demo
    spec:
      containers:
      - name: bluegreen-demo
        image: argoproj/rollouts-demo:blue
        imagePullPolicy: Always
        ports:
        - name: http
          containerPort: 8080
          protocol: TCP
        resources:
          requests:
            memory: 32Mi
            cpu: 5m
  strategy:
    blueGreen:
      activeService: bluegreen-demo
      previewService: bluegreen-demo-preview
      prePromotionAnalysis:
        templates:
        - templateName: success-rate
          args:
          - name: url_map_name
            value: k8s2-um-1cf9hwd1-default-bluegreen-demo-preview-cn1eress
          - name: project_id
            value: project-435400
      postPromotionAnalysis:
        templates:
        - templateName: success-rate
          args:
          - name: url_map_name
            value: k8s2-um-1cf9hwd1-default-bluegreen-demo-94bd5pw1
          - name: project_id
            value: project-435400
      previewReplicaCount: 1
      autoPromotionEnabled: true
      autoPromotionSeconds: 1
      scaleDownDelaySeconds: 30
      abortScaleDownDelaySeconds: 30
```

#### 配置解析

1. 1.**`activeService` 和 `previewService`** ：
- • `activeService` 指向当前正在服务生产流量的版本。
	- • `previewService` 指向新版本，用于测试和验证。
3. 2.**`prePromotionAnalysis` 和 `postPromotionAnalysis`** ：
- • `prePromotionAnalysis` 在新版本上线前执行分析任务（如健康检查）。
	- • `postPromotionAnalysis` 在新版本上线后执行分析任务，确保新版本稳定。
5. 3.**自动化参数** ：
- • `autoPromotionEnabled` ：是否自动将新版本升级为生产版本。
	- • `scaleDownDelaySeconds` ：旧版本在切换后延迟多久缩容。

---

### 自动化测试与回滚

Argo Rollouts 支持多种方式验证部署是否成功，包括：

- • **基于监控指标** ：如 Prometheus、Datadog 等服务的请求成功率、延迟等。
- • **Kubernetes Job** ：通过自定义任务进行验证。

以下是一个基于 Prometheus 的分析模板：

```
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate
spec:
  args:
  - name: url_map_name
  - name: project_id
  metrics:
  - name: success-rate
    interval: 60s
    count: 5
    successCondition: result[0] >= 0.95
    provider:
      prometheus:
        address: http://frontend.default.svc.cluster.local:9090
        query: sum(irate(loadbalancing_googleapis_com:https_request_count{
          monitored_resource="https_lb_rule",
          url_map_name="{{args.url_map_name}}",
          project_id="{{args.project_id}}",
          response_code!="500"}[5m])) / 
          sum(irate(loadbalancing_googleapis_com:https_request_count{
          monitored_resource="https_lb_rule",
          url_map_name="{{args.url_map_name}}",
          project_id="{{args.project_id}}"}[5m]))
```

#### 配置解析

1. 1.**`successCondition`** ：定义成功的条件，此处要求请求成功率不低于 95%。
2. 2.**`provider`** ：指定分析工具，此处为 Prometheus。
3. 3.**参数化支持** ：通过 `args` 动态传参，使模板可以复用。

---

### 运行效果展示

在实际操作中，我们可以通过 Argo Rollouts 的可视化界面监控部署过程：

1. 1.**蓝绿切换** ：
- • 新版本的 Pod 被部署并绑定到 `previewService` 。
	- • 如果 `prePromotionAnalysis` 成功，则新版本被提升为生产版本， `activeService` 指向新版本。
3. 2.**失败回滚** ：
- • 如果在 `postPromotionAnalysis` 中发现错误（如响应错误率超过 5%），Argo Rollouts 会自动回滚到旧版本。

以下是一个实际的部署过程截图：

- • **切换到新版本的预览服务** ：
	Argo Rollouts Demo
- • **分析结果显示成功** ：
	Argo Rollouts Dashboard

---

### 总结

Argo Rollouts 为 Kubernetes 提供了更安全、更自动化的部署方式。通过蓝绿部署和金丝雀部署，结合自动化测试与回滚机制，它可以显著降低生产环境变更的风险，同时让平台团队能够轻松管理大规模的集群和应用。

无论您是初次接触 GitOps，还是希望提升现有部署的安全性，Argo Rollouts 都是一个值得尝试的工具。赶快试试吧！

[加](http://mp.weixin.qq.com/s?__biz=MzkxNzAyMzA3Nw==&mid=2247485016&idx=1&sn=f97eb3faad3330fd169d687fd08be53c&chksm=c147b652f6303f44718c9b6fa402033e9f7400bc08e0df64cb3c486fa8881e7ba74f0a7a1241&scene=21#wechat_redirect) [入知识星球，共同探索云原](http://mp.weixin.qq.com/s?__biz=MzkxNzAyMzA3Nw==&mid=2247485016&idx=1&sn=f97eb3faad3330fd169d687fd08be53c&chksm=c147b652f6303f44718c9b6fa402033e9f7400bc08e0df64cb3c486fa8881e7ba74f0a7a1241&scene=21#wechat_redirect) [生学习之旅！](http://mp.weixin.qq.com/s?__biz=MzkxNzAyMzA3Nw==&mid=2247485016&idx=1&sn=f97eb3faad3330fd169d687fd08be53c&chksm=c147b652f6303f44718c9b6fa402033e9f7400bc08e0df64cb3c486fa8881e7ba74f0a7a1241&scene=21#wechat_redirect)

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/Lcribm9SHtlLymvGIoIYY6oCVsx3bqduLGXbJdvvSO6TcO3qC8OKKBkTyTwjV73PuOf4SgyNSPvDVNbeWsHrZ8A/640?wx_fmt=png&from=appmsg&wxfrom=5&wx_lazy=1&wx_co=1&tp=webp#imgIndex=3)

更多云架构、K8S学习资料以及CKA、Azure考试认证资料，星球内可免费领取哦！

##### 往期回顾

[K8S工具推荐： 使用 Kubemark 进行 Kubernetes 大规模集群模拟实践](https://mp.weixin.qq.com/s?__biz=MzkxNzAyMzA3Nw==&mid=2247485727&idx=1&sn=65c3d50d36899a805c87c17ca650a010&scene=21#wechat_redirect)

[K8S工具推荐：资源编排新利器：三大云厂商联合推出 KRO](https://mp.weixin.qq.com/s?__biz=MzkxNzAyMzA3Nw==&mid=2247485719&idx=1&sn=cc7fe428cb840c21576129d48986b70e&scene=21#wechat_redirect)

[K8S工具推荐：告别复杂认证！Kubernetes登录神器kubelogin指南](https://mp.weixin.qq.com/s?__biz=MzkxNzAyMzA3Nw==&mid=2247485698&idx=1&sn=47443ce3322a407525cd6ccdffbffb29&scene=21#wechat_redirect)

[K8S工具推荐：Kubernetes资源优化神器KRR：一键诊断集群资源浪费](https://mp.weixin.qq.com/s?__biz=MzkxNzAyMzA3Nw==&mid=2247485685&idx=1&sn=6ced5d257f3c3e93383a63ef6802edaf&scene=21#wechat_redirect)

[Kubernetes工具推荐：使用 k8s-pod-restart-info-collector简化故障排查](https://mp.weixin.qq.com/s?__biz=MzkxNzAyMzA3Nw==&mid=2247485663&idx=1&sn=c0f05332e39e5b59793afd2a82326f55&scene=21#wechat_redirect)

[K8S工具推荐：动态无缝的Kubernetes多集群解决方案-Liqo](https://mp.weixin.qq.com/s?__biz=MzkxNzAyMzA3Nw==&mid=2247485739&idx=1&sn=cd7e35bbf22ca3077fbec318bb714d00&scene=21#wechat_redirect)

[K8S学习路线2025](https://mp.weixin.qq.com/s?__biz=MzkxNzAyMzA3Nw==&mid=2247485579&idx=1&sn=993a46217ed2d8190851715afb5134d0&scene=21#wechat_redirect)

[𝙺̲𝚞̲𝚋̲𝚎̲𝚛̲𝚗̲𝚎̲𝚝̲𝚎̲𝚜̲ 管理的最佳实践（2025）](https://mp.weixin.qq.com/s?__biz=MzkxNzAyMzA3Nw==&mid=2247485744&idx=1&sn=43dc3d501156461591903118b264a998&scene=21#wechat_redirect)

K8S工具 · 目录

继续滑动看下一个

云原生SRE

向上滑动看下一个