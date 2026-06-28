---
title: "Kubernetes Gateway API 入门：Ingress 的下一代方案"
source: "https://mp.weixin.qq.com/s/nOi89q7O9YvUo3H6NJqFKA"
created: 2026-06-28
tags:
  - kubernetes
  - gateway-api
  - networking
  - ingress
---

# Kubernetes Gateway API 入门

## 一、为什么要学习 Gateway API

在 Kubernetes 里，服务暴露通常会经历下面几个阶段。

最开始用 `NodePort`：

```
Client → NodeIP:NodePort → Service → Pod
```

后来为了支持域名、路径转发、HTTPS 等能力，开始使用 `Ingress`：

```
Client → Ingress Controller → Ingress → Service → Pod
```

Ingress 解决了很多问题（基于域名转发、基于路径转发、TLS 证书终止、统一入口暴露多个服务），但随着使用场景越来越复杂——多团队、多命名空间、灰度发布、Header 匹配、流量权重、跨命名空间路由——Ingress 的表达能力开始不够。

**Gateway API 是 Kubernetes 官方定义的下一代服务网络入口和路由 API。** 它不是某一个具体网关产品，而是一组 Kubernetes API 规范。

## 二、Ingress 的问题：为什么需要 Gateway API

### 2.1 高级能力大量依赖 annotation

很多 Ingress Controller 通过 annotation 扩展能力：

```yaml
nginx.ingress.kubernetes.io/rewrite-target: /
nginx.ingress.kubernetes.io/proxy-body-size: "100m"
nginx.ingress.kubernetes.io/proxy-read-timeout: "600"
```

问题是：**这些 annotation 通常和具体 Ingress Controller 绑定**。NGINX Ingress 的 annotation 不一定能在 Traefik 上用，Traefik 的配置方式也不一定能迁移到 Kong。可移植性差。

### 2.2 资源职责不够清晰

Ingress 里通常同时出现：域名、路径、TLS、Service 后端、Controller 相关配置、各种 annotation——全堆在一个资源里，运维和研发的边界不清晰。

- 运维希望统一管理入口网关、证书、负载均衡器、安全边界
- 研发只希望配置自己的应用路由

但全部通过 Ingress 表达时，两个角色往往共同操作同一个 Ingress 资源，权限边界不够自然。

### 2.3 多团队、多命名空间场景管理复杂

每个业务团队都想把自己的服务挂到统一入口上。用 Ingress 时，跨命名空间、统一入口、多团队权限隔离这些问题比较难管理。Gateway API 通过 `GatewayClass`、`Gateway`、`HTTPRoute` 等资源拆分职责，更适合平台化场景。

### 2.4 Gateway API 想解决什么

核心思路：**不要把所有入口配置都塞进一个 Ingress 资源里，而是把网关类型、入口监听器、路由规则、后端服务拆开定义。**

```
Ingress 时代：
Ingress → 域名 → 路径 → TLS → Service → annotation

Gateway API 时代：
GatewayClass → 选择哪种网关实现
Gateway      → 定义入口、端口、协议、hostname、TLS、允许哪些 Route 绑定
HTTPRoute    → 定义 HTTP 请求如何匹配、如何转发到后端 Service
Service      → 后端服务入口，最终转发到 Pod
```

## 三、Gateway API 是什么

Gateway API 是 Kubernetes 中用于描述流量入口、监听器、路由规则和后端转发关系的一组标准 API。以 CRD 形式安装到集群里，由具体的 Gateway Controller 监听这些资源并完成真实配置下发。

```
Gateway API      = 标准资源定义
Gateway Controller = 监听 Gateway API 资源，把配置下发到数据面
数据面代理        = 真正接收请求、转发请求的组件
```

例如：

```
Gateway API → Envoy Gateway Controller → Envoy Proxy
Gateway API → Cilium Gateway Controller → Cilium / Envoy 数据面
Gateway API → Istio → Istio Gateway / Envoy
```

支持 Gateway API 的实现：

- Envoy Gateway
- Cilium
- Istio
- Traefik
- Kong
- NGINX Gateway Fabric
- Contour
- GKE Gateway Controller

**Gateway API 只是统一了 Kubernetes 侧的资源表达方式。** 它本身不转发流量，不是 Nginx，也不是 Envoy，也不是 Cilium。

## 四、核心资源模型

初学阶段先看三个就够了：**GatewayClass → Gateway → HTTPRoute**

```
GatewayClass → Gateway → HTTPRoute → Service → Pod
```

### 4.1 GatewayClass

表示一类 Gateway，由某个 Gateway Controller 管理。

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: GatewayClass
metadata:
  name: eg
spec:
  controllerName: gateway.envoyproxy.io/gatewayclass-controller
```

`controllerName` 指定哪个控制器管理这个 GatewayClass。通常由平台团队/集群管理员创建，业务开发人员不频繁修改。

### 4.2 Gateway

表示一个具体的流量入口实例。定义：使用哪个 GatewayClass、监听哪些端口、使用什么协议、接收哪些 hostname、TLS 怎么处理、允许哪些 Route 绑定。

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: app-gateway
  namespace: app-demo
spec:
  gatewayClassName: eg
  listeners:
    - name: http
      port: 80
      protocol: HTTP
      hostname: "app.example.com"
      allowedRoutes:
        namespaces:
          from: Same    # 只允许同 namespace 的 HTTPRoute 绑定
```

**listener** 可以理解为 Gateway 上的一个逻辑监听入口。`allowedRoutes.namespaces.from: Same` 表示只有同命名空间的 Route 才能绑定到此 listener——这就是**职责分离**的体现。

### 4.3 HTTPRoute

表示 HTTP 请求的路由规则——匹配哪些 Host、Path、Header，转发到哪个 Service。

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: app-route
  namespace: app-demo
spec:
  parentRefs:
    - name: app-gateway
      sectionName: http    # 绑定到 Gateway 的哪个 listener
  hostnames:
    - "app.example.com"
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /
      backendRefs:
        - name: app-service
          port: 8080
```

- `parentRefs`：绑定到哪个 Gateway（跨 namespace 需要写 `namespace` 字段，且 Gateway 的 `allowedRoutes` 必须允许）
- `sectionName`：指定绑定到 Gateway 的哪个 listener（多 listener 时建议显式指定）
- `hostnames`：路由级别的 Host 匹配
- `backendRefs`：最终转发到哪个 Service

### 4.4 Service 在 Gateway API 中的角色

Gateway API 并没有替代 Service。最终流量仍然通过 Service 转发到 Pod：

```
Client → Gateway → HTTPRoute → Service → Pod
```

- Gateway API 解决：外部请求怎么进入集群、怎么匹配路由、路由命中后转发到哪个后端
- Service 解决：在集群内部怎么稳定访问一组 Pod

两者不是替代关系，而是协作关系。

## 五、一条请求的完整流向

用户访问 `http://app.example.com/`：

1. DNS 把 app.example.com 解析到 Gateway 的地址
2. 请求到达 Gateway
3. Gateway 根据端口、协议、hostname 匹配 listener
4. Gateway 找到绑定在该 listener 上的 HTTPRoute
5. HTTPRoute 根据 hostnames、path、headers 等规则匹配请求
6. 匹配成功后，根据 backendRefs 找到后端 Service
7. Service 再把请求转发到对应 Pod

**一句话总结**：Gateway 负责接住流量，HTTPRoute 负责决定流量去哪，Service 负责把流量送到 Pod。

## 六、Gateway 和 HTTPRoute 都能写 hostname——为什么？

### Gateway listener.hostname

入口允许范围控制——"这个请求能不能进这个入口？"

### HTTPRoute.hostnames

路由匹配条件——"进入 Gateway 后，这个请求应该命中我这条 Route 吗？"

### 两者需要有交集

```
Gateway: *.example.com  +  HTTPRoute: app.example.com → ✅ 匹配
Gateway: app.example.com + HTTPRoute: api.example.com → ❌ 无交集
Gateway: *.example.com  +  HTTPRoute: example.com    → ❌ 通配不匹配根域名
```

**类比**：Gateway hostname 是小区大门的准入规则，HTTPRoute hostnames 是小区里面的楼栋分配规则。两者不是重复，而是**分层控制**。

## 七、parentRefs 和 sectionName

### parentRefs

HTTPRoute 通过 `parentRefs` 表示绑定到哪个 Gateway：

```yaml
# 同 namespace
parentRefs:
  - name: app-gateway

# 跨 namespace
parentRefs:
  - name: shared-gateway
    namespace: gateway-system
```

跨 namespace 绑定需要 Gateway 的 `allowedRoutes` 允许。

### sectionName

指定绑定到 Gateway 的哪个 listener。Gateway 同时有 HTTP(80) 和 HTTPS(443) 两个 listener 时特别有用：

```yaml
# HTTP 跳转路由 → 绑定 80 端口 listener
parentRefs:
  - name: app-gateway
    sectionName: http

# 业务路由 → 绑定 443 端口 listener
parentRefs:
  - name: app-gateway
    sectionName: https
```

Gateway 只有一个 listener 时可以不写 sectionName。

## 八、Ingress vs Gateway API 对比

| 维度 | Ingress | Gateway API |
|------|---------|-------------|
| **定位** | 简单 HTTP/HTTPS 入口 | 通用服务网络入口和路由 API（L4/L7） |
| **资源拆分** | 单一 Ingress 资源 | GatewayClass + Gateway + HTTPRoute 职责分离 |
| **高级能力** | 依赖 Controller 私有 annotation | 标准化 API 字段（Header 匹配、流量权重等） |
| **可移植性** | annotation 绑定特定 Controller | 标准 API，跨 Controller 通用 |
| **多团队** | 同一资源混合运维/研发配置 | Gateway（平台团队）+ HTTPRoute（业务团队）权限分离 |
| **跨 namespace** | 困难 | 原生支持 `allowedRoutes` + 跨 namespace `parentRefs` |
| **协议支持** | 主要 HTTP/HTTPS | HTTP、HTTPS、gRPC、TCP、TLS |
| **状态** | GA，未来可能逐步被替代 | GA（v1.0+ 已正式发布），Kubernetes 官方推荐方向 |

## 九、总结

- Gateway API **不是**具体网关产品，而是一组 Kubernetes 网络 API 规范
- 本身不转发流量，必须配合具体 Gateway Controller 使用（Envoy Gateway / Cilium / Istio / Traefik / Kong 等）
- **GatewayClass** 选择网关实现，**Gateway** 定义入口，**HTTPRoute** 定义转发规则，**Service** 仍然是后端入口
- Gateway hostname 是入口允许范围，HTTPRoute hostnames 是路由匹配条件，两者需要有交集
- `parentRefs` 表示 HTTPRoute 绑定到哪个 Gateway，`sectionName` 表示绑定到哪个 listener
- Gateway API 是 Ingress 的下一代方案，解决了 annotation 绑定、职责混合、跨 namespace 困难等问题
