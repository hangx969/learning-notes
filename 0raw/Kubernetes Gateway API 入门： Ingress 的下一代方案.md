---
title: "Kubernetes Gateway API 入门： Ingress 的下一代方案"
source: "https://mp.weixin.qq.com/s/nOi89q7O9YvUo3H6NJqFKA?scene=1&click_id=147493921"
author:
  - "[[平凡小代]]"
published:
created: 2026-06-28
description:
tags:
  - "clippings"
---
平凡小代 平凡小代 *2026年6月16日 15:23*

## 一、为什么要学习 Gateway API

在 Kubernetes 里，服务暴露通常会经历下面几个阶段。

最开始，我们可能会用 `NodePort` ：

```shell
Client  -> NodeIP:NodePort  -> Service  -> Pod
```

后来为了支持域名、路径转发、HTTPS 等能力，开始使用 `Ingress` ：

```shell
Client  -> Ingress Controller  -> Ingress  -> Service  -> Pod
```

Ingress 解决了很多问题，比如：

```js
基于域名转发基于路径转发TLS 证书终止统一入口暴露多个服务
```

但是随着 Kubernetes 使用场景越来越复杂，尤其是在多团队、多命名空间、灰度发布、Header 匹配、流量权重、跨命名空间路由等场景下，Ingress 的表达能力开始显得不够。

Gateway API 就是在这个背景下出现的。可以先记住一句话：

```nginx
Gateway API 是 Kubernetes 官方定义的下一代服务网络入口和路由 API。
```

它不是某一个具体网关产品，而是一组 Kubernetes API 规范。

---

## 二、Ingress 的问题：为什么需要 Gateway API

### 2.1 Ingress 能做什么

Ingress 是 Kubernetes 中非常常见的入口资源，主要用于把集群外部的 HTTP/HTTPS 流量转发到集群内部的 Service。一个典型的 Ingress 流量链路是：

```shell
Client  -> DNS  -> Ingress Controller  -> Ingress 规则  -> Service  -> Pod
```

例如：

```javascript
http://example.com/api  -> api-servicehttp://example.com/web  -> web-service
```

Ingress 的核心价值是： **把多个 HTTP 服务统一暴露到一个入口下面** 。

---

### 2.2 Ingress 的局限

Ingress 很有用，但它的模型比较简单。对于基础的 HTTP/HTTPS 暴露来说够用，但在更复杂的生产环境中会遇到几个问题。

#### 1\. 高级能力大量依赖 annotation

很多 Ingress Controller 都会通过 annotation 扩展能力，例如：

```bash
nginx.ingress.kubernetes.io/rewrite-target: /nginx.ingress.kubernetes.io/proxy-body-size: "100m"nginx.ingress.kubernetes.io/proxy-read-timeout: "600"
```

这些 annotation 很常见，但问题是： **它们通常和具体 Ingress Controller 绑定** 。

也就是说，NGINX Ingress 的 annotation 不一定能在 Traefik 上用，Traefik 的配置方式也不一定能迁移到 Kong 或其他控制器。结果就是：

```nginx
Ingress YAML 看起来是 Kubernetes 标准资源但真正的高级能力却依赖具体控制器的私有 annotation
```

这样会导致可移植性比较差。

---

#### 2\. 资源职责不够清晰

Ingress 里通常会同时出现：

```kotlin
域名路径TLSService 后端Controller 相关配置各种 annotation
```

这些内容都堆在一个资源里，会导致运维和研发的边界不清晰。例如在一个公司里：

```js
运维希望统一管理入口网关、证书、负载均衡器、安全边界研发只希望配置自己的应用路由
```

但如果全部通过 Ingress 表达，这两个角色往往会共同操作同一个 Ingress 资源，权限边界不够自然。

---

#### 3\. 多团队、多命名空间场景管理复杂

在多团队环境里，经常会出现这种情况：

```css
平台团队维护统一入口业务 A 在 namespace-a业务 B 在 namespace-b业务 C 在 namespace-c
```

每个业务团队都想把自己的服务挂到统一入口上。如果用 Ingress，跨命名空间、统一入口、多团队权限隔离这些问题会比较难管理。Gateway API 通过 `GatewayClass` 、 `Gateway` 、 `HTTPRoute` 等资源拆分职责，更适合这种平台化场景。

---

### 2.3 Gateway API 想解决什么

Gateway API 的核心思路是：

```js
不要把所有入口配置都塞进一个 Ingress 资源里，而是把网关类型、入口监听器、路由规则、后端服务拆开定义。
```

Ingress 时代：

```shell
Ingress  -> 域名  -> 路径  -> TLS  -> Service  -> annotation
```

Gateway API 时代：

```shell
GatewayClass  -> 选择哪种网关实现Gateway  -> 定义入口、端口、协议、hostname、TLS、允许哪些 Route 绑定HTTPRoute  -> 定义 HTTP 请求如何匹配、如何转发到后端 ServiceService  -> 后端服务入口，最终转发到 Pod
```

这样拆分之后，职责会更清晰。

---

## 三、Gateway API 是什么

Gateway API 是 Kubernetes 中用于描述流量入口、监听器、路由规则和后端转发关系的一组标准 API。在实际集群中，Gateway API 资源通常以 CRD 的形式安装到 Kubernetes 集群里，然后由具体的 Gateway Controller 监听这些资源并完成真实配置下发。可以这样理解：

```java
Gateway API = Kubernetes 官方定义的服务网络入口和路由模型
```

它关注的是：

```js
外部请求怎么进入集群进入哪个 Gateway匹配哪个 listener使用哪条 Route最终转发到哪个 Service
```

Gateway API 不是只面向 HTTP。它的设计目标覆盖更广的服务网络场景，包括 L4/L7 路由、负载均衡、服务网格等。Gateway API 不是 Nginx，也不是 Envoy，也不是 Cilium，更不是 Istio。它是一组 Kubernetes API 规范。真正处理流量的是具体实现，也就是 Gateway Controller 和数据面代理。

可以这样理解：

```java
Gateway API  = 标准资源定义Gateway Controller  = 监听 Gateway API 资源，并把配置下发到数据面数据面代理  = 真正接收请求、转发请求的组件
```

例如：

```shell
Gateway API  -> Envoy Gateway Controller  -> Envoy Proxy
```

```shell
Gateway API  -> Cilium Gateway Controller  -> Cilium / Envoy 数据面
```

```shell
Gateway API  -> Istio  -> Istio Gateway / Envoy
```

也就是说，Gateway API 本身不会自动帮你转发流量。你需要安装一个支持 Gateway API 的实现，例如：

```nginx
Envoy GatewayCiliumIstioTraefikKongNGINX Gateway FabricContourGKE Gateway Controller
```

Gateway API 只是统一了 Kubernetes 侧的资源表达方式。

---

## 四、Gateway API 的核心资源模型

Gateway API 的资源比较多，但初学阶段先看这三个就够了：

```nginx
GatewayClassGatewayHTTPRoute
```

它们之间的关系是：

```shell
GatewayClass  -> Gateway      -> HTTPRoute          -> Service              -> Pod
```

也可以这样看：

```js
GatewayClass：选择哪种网关实现Gateway：定义入口HTTPRoute：定义 HTTP 路由规则Service：最终后端入口Pod：真正运行应用的实例
```

---

### 4.1 GatewayClass

`GatewayClass` 表示一类 Gateway，由某个 Gateway Controller 管理。

可以这样理解：

```ini
GatewayClass = 选择使用哪种网关实现
```

比如使用 Envoy Gateway 时，可能会有一个 GatewayClass：

```makefile
apiVersion: gateway.networking.k8s.io/v1kind: GatewayClassmetadata:  name: egspec:  controllerName: gateway.envoyproxy.io/gatewayclass-controller
```

这里最重要的是：

```bash
spec:  controllerName: gateway.envoyproxy.io/gatewayclass-controller
```

它表示：

```bash
这个 GatewayClass 由 controllerName 为 gateway.envoyproxy.io/gatewayclass-controller 的控制器管理。
```

如果后面创建 Gateway 时写：

```makefile
gatewayClassName: eg
```

就表示这个 Gateway 交给 `eg` 这个 GatewayClass 对应的控制器处理。

从运维角度看， `GatewayClass` 通常由平台团队、集群管理员或网关实现安装过程创建。普通业务开发人员一般不会频繁修改 GatewayClass。

---

### 4.2 Gateway

`Gateway` 表示一个具体的流量入口实例。

可以这样理解：

```ini
Gateway = 一个入口网关声明
```

它可以代表：

```js
一个云负载均衡器一个集群内的代理入口一个 Envoy 网关实例一个对外提供 HTTP/HTTPS 访问的入口
```

Gateway 主要定义：

```js
使用哪个 GatewayClass监听哪些端口使用什么协议接收哪些 hostnameTLS 怎么处理允许哪些 Route 绑定到这个 Gateway
```

示例：

```makefile
apiVersion: gateway.networking.k8s.io/v1kind: Gatewaymetadata:  name: app-gateway  namespace: app-demospec:  gatewayClassName: eg  listeners:    - name: http      port: 80      protocol: HTTP      hostname: "app.example.com"      allowedRoutes:        namespaces:          from: Same
```

逐字段解释：

```cpp
metadata:  name: app-gateway  namespace: app-demo
```

表示创建一个名为 `app-gateway` 的 Gateway，放在 `app-demo` 命名空间。

```makefile
spec:  gatewayClassName: eg
```

表示这个 Gateway 使用 `eg` 这个 GatewayClass。

```makefile
listeners:  - name: http
```

表示定义一个 listener，名字叫 `http` 。

listener 可以理解为：

```nginx
Gateway 上的一个逻辑监听入口。
```

```makefile
port: 80protocol: HTTP
```

表示这个 listener 监听 80 端口，并处理 HTTP 流量。

```javascript
hostname: "app.example.com"
```

表示这个 listener 只接收 Host 为 `app.example.com` 的请求。

```cs
allowedRoutes:  namespaces:    from: Same
```

表示只允许和 Gateway 同一个命名空间里的 Route 绑定到这个 listener。

由于这个 Gateway 在 `app-demo` 命名空间，所以这里表示：

```js
只有 app-demo 命名空间里的 HTTPRoute 可以挂到这个 Gateway listener 上。
```

---

### 4.3 HTTPRoute

`HTTPRoute` 表示 HTTP 请求的路由规则。

可以这样理解：

```ini
HTTPRoute = HTTP 请求怎么匹配、怎么转发
```

HTTPRoute 主要定义：

```css
这条 Route 要挂到哪个 Gateway匹配哪些 Host匹配哪些 Path匹配哪些 Header最终转发到哪个 Service
```

示例：

```makefile
apiVersion: gateway.networking.k8s.io/v1kind: HTTPRoutemetadata:  name: app-route  namespace: app-demospec:  parentRefs:    - name: app-gateway  hostnames:    - "app.example.com"  rules:    - matches:        - path:            type: PathPrefix            value: /      backendRefs:        - name: app-service          port: 8080
```

逐字段解释：

```cpp
metadata:  name: app-route  namespace: app-demo
```

表示创建一个名为 `app-route` 的 HTTPRoute，也放在 `app-demo` 命名空间。

```makefile
parentRefs:  - name: app-gateway
```

表示这条 HTTPRoute 想绑定到 `app-gateway` 这个 Gateway 上。

```makefile
hostnames:  - "app.example.com"
```

表示匹配请求中的 Host。也就是请求必须类似这样：

```javascript
curl -H "Host: app.example.com" http://<Gateway地址>/
```

或者用户通过浏览器访问：

```javascript
http://app.example.com/
```

```bash
rules:  - matches:      - path:          type: PathPrefix          value: /
```

表示匹配所有以 `/` 开头的路径。例如：

```bash
/ /api /login /v1/chat/completions
```

这些路径都能匹配。

```makefile
backendRefs:  - name: app-service    port: 8080
```

表示匹配成功后，把请求转发到 `app-service:8080` 。这里的 `app-service` 是 Kubernetes Service。

---

### 4.4 Service 在 Gateway API 中的角色

Gateway API 并没有替代 Service。最终流量仍然通常会转发到 Kubernetes Service，再由 Service 转发到后端 Pod。所以完整链路是：

```shell
Client  -> Gateway  -> HTTPRoute  -> Service  -> Pod
```

Gateway API 解决的是：

```js
外部请求怎么进入集群进入后怎么匹配路由路由命中后转发到哪个后端
```

Service 解决的是：

```js
在集群内部怎么稳定访问一组 Pod
```

这两个不是替代关系，而是协作关系。

---

## 五、一条请求在 Gateway API 中的完整流向

假设用户访问：

```javascript
http://app.example.com/
```

Gateway API 的完整请求链路可以这样表示：

```markdown
1. 用户访问 http://app.example.com/2. DNS 把 app.example.com 解析到 Gateway 的地址3. 请求到达 Gateway4. Gateway 根据端口、协议、hostname 匹配 listener5. Gateway 找到绑定在该 listener 上的 HTTPRoute6. HTTPRoute 根据 hostnames、path、headers 等规则匹配请求7. 匹配成功后，根据 backendRefs 找到后端 Service8. Service 再把请求转发到对应 Pod
```

用图表示就是：

```nginx
Client  |  |  http://app.example.com/  vGateway 地址  |  |  port: 80  |  protocol: HTTP  |  hostname: app.example.com  vGateway Listener  |  |  parentRefs 绑定  vHTTPRoute  |  |  hostnames: app.example.com  |  path: /  vService app-service:8080  |  vPod
```

这个链路里，Gateway 和 HTTPRoute 各自负责不同层面的判断。

Gateway 负责入口层面的判断：

```js
这个请求能不能进这个入口？端口对不对？协议对不对？Host 是否在 listener 允许范围内？这个 Route 是否允许绑定到这个 listener？
```

HTTPRoute 负责路由层面的判断：

```css
这个请求匹配哪个 Host？匹配哪个 Path？是否匹配某些 Header？最终要转发到哪个 Service？
```

所以可以简单记：

```nginx
Gateway 决定入口。HTTPRoute 决定转发规则。Service 决定后端 Pod。
```

---

## 六、为什么 Gateway 和 HTTPRoute 都能写 hostname

很多人刚开始看到下面两个字段会懵：

Gateway 里有：

```javascript
hostname: "app.example.com"
```

HTTPRoute 里也有：

```makefile
hostnames:  - "app.example.com"
```

看起来像重复配置，但实际上它们的作用不同。

---

### 6.1 Gateway listener.hostname 的作用

Gateway 里的 hostname 是 listener 级别的限制。示例：

```makefile
listeners:  - name: http    port: 80    protocol: HTTP    hostname: "app.example.com"
```

它的含义是：

```js
这个 Gateway 的 http listener 只接收 Host 为 app.example.com 的请求。
```

也就是说，Gateway 先在入口处判断：

```js
这个请求是不是应该由我这个 listener 接收？
```

它更偏向入口范围控制。

---

### 6.2 HTTPRoute.hostnames 的作用

HTTPRoute 里的 hostnames 是路由规则级别的匹配条件。示例：

```makefile
spec:  hostnames:    - "app.example.com"
```

它的含义是：

```js
这条 HTTPRoute 只匹配 Host 为 app.example.com 的请求。
```

也就是说，请求进入 Gateway 后，HTTPRoute 再继续判断：

```js
这个请求是不是应该命中我这条 Route？
```

它更偏向业务路由匹配。

---

### 6.3 两者需要有交集

如果 Gateway listener 和 HTTPRoute 都配置了 hostname，那么两者需要有交集。比如：

```nginx
Gateway listener.hostname = app.example.comHTTPRoute.hostnames = app.example.com
```

结果：

```js
可以匹配
```

如果：

```nginx
Gateway listener.hostname = app.example.comHTTPRoute.hostnames = api.example.com
```

结果：

```js
无法匹配
```

因为 Gateway 入口层面只允许 `app.example.com` ，但 HTTPRoute 想匹配的是 `api.example.com` ，两者没有交集。

再看一个通配符例子：

```nginx
Gateway listener.hostname = *.example.comHTTPRoute.hostnames = app.example.com
```

结果：

```js
可以匹配
```

因为 `app.example.com` 属于 `*.example.com` 的范围。

但如果：

```nginx
Gateway listener.hostname = *.example.comHTTPRoute.hostnames = example.com
```

结果：

```js
不匹配
```

因为 `*.example.com` 匹配的是 `app.example.com` 、 `api.example.com` 这类子域名，不匹配根域名 `example.com` 。

---

### 6.4 用一个类比来理解

可以把 Gateway listener.hostname 理解成小区大门的准入规则。

```js
小区大门：只允许 app.example.com 进入
```

HTTPRoute.hostnames 则像小区里面的楼栋分配规则。

```js
进入小区后，app.example.com 的请求走 app-route
```

所以：

```nginx
Gateway hostname：入口允许范围HTTPRoute hostnames：路由匹配范围
```

两者不是重复，而是分层控制。

---

## 七、parentRefs 和 sectionName 是什么

### 7.1 parentRefs

HTTPRoute 需要通过 `parentRefs` 表示自己要绑定到哪个父资源。最常见的父资源就是 Gateway。示例：

```makefile
spec:  parentRefs:    - name: app-gateway
```

含义：

```js
这条 HTTPRoute 想挂到 app-gateway 这个 Gateway 上。
```

如果 Gateway 和 HTTPRoute 在同一个 namespace，可以只写 name。

如果 Gateway 在其他 namespace，需要写 namespace：

```cpp
spec:  parentRefs:    - name: shared-gateway      namespace: gateway-system
```

这表示：

```perl
这条 HTTPRoute 想挂到 gateway-system 命名空间里的 shared-gateway 上。
```

但是要注意：跨 namespace 挂载 Route 不是随便就能成功的。Gateway 的 listener 需要通过 `allowedRoutes` 允许对应 namespace 的 Route 绑定。

---

### 7.2 sectionName

`sectionName` 用于指定 HTTPRoute 绑定到 Gateway 里的哪个 listener。

假设 Gateway 里有两个 listener：

```makefile
apiVersion: gateway.networking.k8s.io/v1kind: Gatewaymetadata:  name: app-gateway  namespace: app-demospec:  gatewayClassName: eg  listeners:    - name: http      port: 80      protocol: HTTP      hostname: "app.example.com"    - name: https      port: 443      protocol: HTTPS      hostname: "app.example.com"      tls:        mode: Terminate        certificateRefs:          - kind: Secret            name: app-example-com-tls
```

这个 Gateway 有两个 listener：

```apache
http  -> 80 端口https -> 443 端口
```

如果 HTTPRoute 写：

```makefile
parentRefs:  - name: app-gateway    sectionName: http
```

表示：

```js
这条 HTTPRoute 绑定到 app-gateway 的 http listener。
```

如果写：

```makefile
parentRefs:  - name: app-gateway    sectionName: https
```

表示：

```js
这条 HTTPRoute 绑定到 app-gateway 的 https listener。
```

---

### 7.3 什么时候需要关注 sectionName

如果 Gateway 只有一个 listener，不写 `sectionName` 也比较常见。

例如：

```makefile
listeners:  - name: http    port: 80    protocol: HTTP
```

HTTPRoute 可以简单写：

```makefile
parentRefs:  - name: app-gateway
```

但是如果 Gateway 同时有多个 listener，尤其是同时有 HTTP 和 HTTPS，建议显式写 `sectionName` 。例如：

```apache
HTTP 80 端口：只负责跳转到 HTTPSHTTPS 443 端口：负责真实业务请求
```

这时可以这样设计：

```shell
http-to-https Route  -> parentRefs.sectionName = httpapp-business Route  -> parentRefs.sectionName = https
```

这样看 YAML 的时候会非常清楚：

```js
哪条 Route 绑定 80 端口哪条 Route 绑定 443 端口
```

---

## 八、用一个完整例子串起来

假设我们希望暴露一个应用：

```makefile
域名：app.example.com入口：app-gateway后端：app-service:8080
```

### 8.1 Gateway

```makefile
apiVersion: gateway.networking.k8s.io/v1kind: Gatewaymetadata:  name: app-gateway  namespace: app-demospec:  gatewayClassName: eg  listeners:    - name: http      port: 80      protocol: HTTP      hostname: "app.example.com"      allowedRoutes:        namespaces:          from: Same
```

这个 Gateway 表示：

```cpp
创建一个 app-gateway。使用 eg 这个 GatewayClass。监听 80 端口 HTTP 流量。只接收 Host 为 app.example.com 的请求。只允许同 namespace 的 HTTPRoute 绑定。
```

---

### 8.2 HTTPRoute

```makefile
apiVersion: gateway.networking.k8s.io/v1kind: HTTPRoutemetadata:  name: app-route  namespace: app-demospec:  parentRefs:    - name: app-gateway      sectionName: http  hostnames:    - "app.example.com"  rules:    - matches:        - path:            type: PathPrefix            value: /      backendRefs:        - name: app-service          port: 8080
```

这个 HTTPRoute 表示：

```js
绑定到 app-gateway 的 http listener。匹配 Host 为 app.example.com 的请求。匹配所有以 / 开头的路径。转发到 app-service:8080。
```

---

### 8.3 请求链路

当用户访问：

```javascript
http://app.example.com/
```

完整链路是：

```shell
Client  -> DNS 解析 app.example.com  -> Gateway 地址  -> app-gateway 的 http listener  -> app-route 这条 HTTPRoute  -> app-service:8080  -> Pod
```

用一句话总结：

```nginx
Gateway 负责接住流量，HTTPRoute 负责决定流量去哪，Service 负责把流量送到 Pod。
```

---

## 九、本文小结

这篇文章主要梳理了 Gateway API 的基础概念。

可以总结成下面几句话：

```nginx
Gateway API 不是具体网关产品，而是一组 Kubernetes 网络 API 规范。Gateway API 本身不转发流量，必须配合具体 Gateway Controller 使用。GatewayClass 用来选择网关实现。Gateway 用来定义入口、listener、端口、协议、hostname、TLS 和 Route 绑定范围。HTTPRoute 用来定义 HTTP 请求如何匹配，以及最终转发到哪个 Service。Gateway listener.hostname 是入口允许范围，HTTPRoute.hostnames 是路由匹配条件，两者需要有交集。parentRefs 表示 HTTPRoute 要绑定到哪个 Gateway。sectionName 表示 HTTPRoute 要绑定到 Gateway 的哪个 listener。Service 仍然是后端入口，Gateway API 并不会替代 Service。
```

如果用一条请求来串起来，就是：

```shell
GatewayClass  -> 被 Gateway 引用，表示这个 Gateway 由哪类控制器管理Gateway  -> 定义入口地址、listener、协议、端口、hostname、TLS、allowedRoutesHTTPRoute  -> 通过 parentRefs 绑定到 Gateway 的 listenerService  -> 被 HTTPRoute 的 backendRefs 引用，作为后端服务入口Pod  -> Service 最终转发到的真实工作负载
```

收录于k8s gateway api