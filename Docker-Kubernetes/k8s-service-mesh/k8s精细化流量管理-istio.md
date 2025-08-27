# 服务网格背景

## 为什么要用服务网格

应用架构演变：单体应用 -- 微服务 -- 函数即服务

1. 单体应用发展到微服务带来的问题：
   - 服务间通信复杂：各个服务之间通过接口调用其他服务
   - 流量精细化管理很难：比如想实现金丝雀发布
   - 服务间安全通信难：双向TLS加密需要自己实现
   - 多语言环境统一治理困难：Java服务怎么自动发现python服务等
   - 跨服务间依赖管理困难：B服务挂掉，可能影响上游A服务
   - 可观测性不足：链路调用可追踪性不足
2. 为了解决上述问题，可以采用SpringCloud框架、Nacos框架等解决服务发现。但是也有问题：
   - 一是k8s已经提供了这些功能，再在k8s中用springCloud属于套娃。
   - 对于开发人员，需要手动维护微服务之间的调用、负载均衡、服务发现、熔断降级、动态路由等功能。这些都需要写代码，然而都不属于业务逻辑，严重影响开发效率。
   - springCloud和Nacos都是原生支持Java，但是对其他语言的支持性不好。这对于多语言环境很不友好。
3. 为了解决上述问题，引入了服务网格：
   - 把上述流量治理的功能下沉到了基础设施。开发人员只需要聚焦自己的业务逻辑就行了。

## 服务网格

SeriviceMesh有Buoyant公司CEO William Morgan发起，目标位解决微服务之间的复杂链路问题。

ServiceMesh将程序开发的网络功能和程序本身解耦，网络功能下沉到基础架构。

由服务网格实现服务之间的负载均衡等功能，并且除了网络功能外，也提供了其他更高级的功能，比如：全链路加密、监控、链路追踪等。

服务网格最常用的架构就是一个服务对应一个sidecar proxy。

### 核心功能

1. 负载均衡

   服务间访问可以自定义轮询、最小连接数等负载均衡算法。

2. 服务发现

   服务上下线，流量会自动做接入和切断

3. 熔断降级

   下游服务故障之后，上游服务会自动降级，避免发生微服务雪崩

4. 动态路由

   灰度、蓝绿发布

5. 故障注入

   用来测试服务韧性，模拟某个微服务的故障，测试其他服务的正常运行情况

6. 错误重试

   网络抖动时，提供重试功能。谨慎使用，避免幂等性问题。

7. 安全通信

   网格内的服务可以实现全链路加密，开箱即用

8. 语言无关

   服务网格代理与应用语言无关。

## 产品对比

### Linkerd

- Buoyant公司在2016年率先开源的高性能网络代理程序。是服务网格的鼻祖，标志着Service Mesh时代的开始。
- 配置和管理比较复杂。

### Envoy

- 高性能服务网格程序，为云原生设计。但是他并不是一款完整的服务网格产品，只是个网络代理程序。
- Istio和Kuma属于比较完整的服务网格程序，是基于Envoy开发的。

### Kuma

- 由Kong开发并提供支持，是一个通用的现代服务网格控制平面。基于Envoy构建。

### Istio

- Istio受Google、IBM、Lyft等公司的支持和推广，于2017年5月发布。底层为Envoy。
- 因为有大厂支持和背书，是现在服务网格产品的首选。
- 很多云计算大厂的k8s产品带的服务网格功能，底层也是接入的istio。

# istio功能

## 文档

官方文档：https://istio.io/docs/concepts/what-is-istio/

Github地址：[https://github.com/istio/istio/](https://github.com/istio/istio/releases)

详解文章：https://juejin.cn/post/7310878133720301604

## 核心功能

Istio是一个开源的服务网格（Service Mesh）产品，专为微服务架构设计，用于透明的管理微服务间的通信、安全、监控和流量策略。

Istio通过sidecar拦截并控制服务间的所有流量，将复杂的微服务治理从业务代码中剥离，病下沉到基础设施层，使开发者更专注于业务逻辑，以提升开发效率。

以下是Istio的一些基本特性：

1. 代理注入：Istio使用Envoy作为其数据面代理，通过注入Envoy代理到每个微服务的Pod中，实现对流量的控制和管理。这种代理注入的方式无需修改应用代码，提供了一种非侵入式的部署方式。（部署好istio，会自动在创建的pod里面注入一个sidecar envoy容器）
2. 服务发现：Istio通过在代理中集成服务注册和发现机制，实现对微服务实例的自动发现和路由。它能够动态地将流量转发到可用的服务实例，并支持多种服务发现的机制 
3. 负载均衡：Istio提供了丰富的负载均衡策略，可以根据不同的需求进行流量的分发和负载均衡，包括轮询、加权轮询、故障感知等。（Istio主要工作在六层）
4. 流量管理：Istio可以实现对流量的灵活管理和控制，支持流量切分、A/B测试、金丝雀发布等高级流量管理功能。它可以帮助开发人员更好地控制和管理微服务架构中的流量。
5. 故障恢复：Istio提供了故障恢复机制，包括超时控制、重试、断路器和熔断等。它能够自动检测和处理微服务中的故障，并提供弹性和可靠性。
6. 安全性：Istio提供了丰富的安全功能，包括双向TLS流量加密（mTLS）、身份认证和授权、访问控制（用的比较少，开发者还是更愿意在程序内部处理认证逻辑）等。它可以通过自动注入代理，对服务间的通信进行加密和验证，提供了更高层次的安全保障。
7. 集群出入口流量管理：入口流量，可以代替ingress-controller提供外部访问入口；出口流量，可以让集群出口流量固定到某一个出口出去。

### 流量管理

#### 熔断

- 熔断是一种故障保护机制，用于在服务之间的通信中防止故障扩散，并提供更好的容错能力。在微服务架构中，一个应用通常由许多小型的、相互协作的服务组成。当某个服务发生故障或变得不可用时，如果不采取措施，可能会导致连锁反应，影响到整个系统的可用性。熔断机制旨在解决这个问题，其核心思想是在服务之间设置阈值和超时时间，并对请求进行监控。当服务的错误率或响应时间超过预设的阈值时，熔断器会打开，拒绝向该服务发送更多请求，并快速失败返回错误，而不是等待超时。
- 应用场景
  1. 快速失败返回: 当目标服务不可用时，不再尝试等待请求超时，而是快速返回错误，从而避免资源浪费和潜在的长时间等待。
  2. 故障隔离: 熔断机制阻止故障扩散，使问题局限在出现故障的服务，而不会影响到整个应用程序。
  3. 恢复机制: 熔断器会定期尝试发起一些请求到目标服务，以检查其是否已经恢复。如果服务恢复正常，则熔断器会逐渐关闭，允许流量再次流向目标服务。
  4. 自动重试: 一旦目标服务恢复，熔断器会逐渐允许一部分流量通过，如果没有再次出现问题，会逐渐恢复到正常状态，否则继续保持熔断状态。
- 在高并发情况下，如果请求数量达到一定极限（可以自己设置阈值），超出了设置的阈值，断路器会自动开启服务保护功能，通过服务降级的方式返回一个友好的提示给客户端。假设当10个请求中，有10%失败时，熔断器就会打开，此时再调用此服务，将会直接返回失败，不再调远程服务。直到10s之后，重新检测该触发条件，判断是否把熔断器关闭或者继续打开。

#### 超时

- 在 Kubernetes（K8s）集群中结合 Istio，可以使用 Istio 的流量管理功能来控制服务之间的请求超时。超时是指在一定时间内，如果某个请求没有得到及时响应，就会被认为是超时。通过设置请求超时时间，可以对服务之间的通信进行控制，确保请求在合理的时间内得到响应，避免请求无限期地等待导致资源浪费或影响整体系统的响应性能。

  Istio 的超时控制允许你为每个服务之间的请求设置最大的等待时间。当某个请求在指定的超时时间内没有得到响应时，Istio 会终止该请求并返回一个错误响应给客户端。这样可以防止请求在后端服务长时间等待，从而避免请求积压，同时提高系统的稳定性和可用性。

#### 重试

- 重试机制就是如果调用服务失败，Envoy 代理尝试连接服务的最大次数。而默认情况下，Envoy 代理在失败后并不会尝试重新连接服务。

# istio架构

![image-20240212203342339](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402122033623.png)

Istio从逻辑上分为数据平面和控制平面：

- 控制平面：
  - 负责管理和配置数据平面的流量策略。由管理员创建的Istio资源会解析成相关的配置下发到数据平面
  - **istio 1.5+中使用了一个全新的部署模式，重建了控制平面，将原有的多个组件整合为一个单体结构istiod，这个组件是控制平面的核心，管理Istio的所有功能，主要包括Pilot、Mixer、Citadel等服务组件，是以三个进程运行的。**

- 数据平面：
  - 由一组以Sidecar方式部署的智能代理容器组成。这些代理承载并控制微服务之间的所有网络通信，管理入口和出口流量，类似于一线员工。
  - Sidecar 一般和业务容器运行在一个pod里，来劫持业务应用容器的流量，并接受控制面组件的控制，同时会向控制面输出日志、跟踪及监控数据。
  - 数据平面在Istio 1.22版本后，分为了Sidecar和Ambient两种模式：
    - Sidecar模式：为集群中启动的pod部署一个Envoy代理，或者为在虚拟机上运行的服务并行创建一个Envoy代理。
    - Ambient模式：在每个节点上启动四层代理，也可以在每个命名空间启动一个Envoy。出现这种模式是因为sidecar也需要占用资源，pod量上去之后，大量的sidecar也要占用很多资源。这种模式在节点上启动一个代理，这个代理故障会影响整个节点的流量。

## 工作模式对比

| 对比项   | 对比维度     | Sidecar                              | Ambient                                                      |
| -------- | ------------ | ------------------------------------ | ------------------------------------------------------------ |
| 核心架构 | 代理部署方式 | 每个pod注入一个Envoy Sidecar容器     | 分层部署：<br />L4：每个节点部署一个Ztunnel代理<br />L7：每个ns不是一个或多个Waypoint代理 |
|          | 流量管理     | 通过iptables/IPVS规则劫持pod进出流量 | 四层由Ztunnel处理，七层由Waypoint处理                        |
|          | 覆盖范围     | 所有注入Sidecar的pod                 | 默认纳入所有pod，无需添加annotation（灵活性较差）            |
|          | 故障可用性   | 只影响某个故障的pod                  | 影响当前节点或当前空间的所有服务（影响较大）                 |
| 资源开销 | 代理数量     | 每个pod一个Envoy                     | Ztunnel：每个节点一个代理<br />Wayponit：通常一个ns一个或多个 |
|          | 内存/CPU消耗 | 较高（也要看开启了多少sidecar）      | 较低（也要看实际使用量）                                     |
|          | 启动延迟     | pod启动时需要等待Sidecar就绪         | Pod启动无需等待代理，延迟更低                                |
| 性能对比 | 调用延迟     | 每个请求经过两此Envoy代理            | 四层经过Ztunnel，七层经过Waypoint。（跨ns、跨节点时，经过多跳Ztunnel和Waypoint，延迟可能更多） |

Sidecar模式官方也是推荐在生产环境中使用，非常成熟稳定，而且服务网格大部分功能都支持。

Ambient在官网一直是标成Beta版本，不推荐在生产环境中使用，有些功能不支持，比如跨集群、虚拟机服务代理等。

# istio组件

## 控制平面

### Pilot

Pilot主要用于监听API Server，动态获取集群中的svc和endpoint信息，将配置的路由规则、负载均衡策略转换为Envoy可理解的配置，下发到各个Sidecar中。

![image-20240212204831402](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402122048477.png)

###  Citadel

- Citadel负责Istio中的身份和凭据管理，提供安全相关功能。它用于为服务生成和分发TLS证书，以实现服务之间的安全通信。

- Citadel可以被视为团队中的保密专员。它负责确保团队成员之间的通信是安全的，别人无法窃听或者假冒。Citadel会为每个队员提供一个保密的通信渠道，确保他们之间的交流是私密的，就像用密码和密钥加密信息一样。

  ![image-20240212205143030](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402122051084.png)

### Galley

- Galley是Istio的配置管理组件，负责验证、转换和分发配置给其他Istio组件。它监听Kubernetes的配置更改，例如Service、Deployment等，根据规则和策略生成Istio所需的配置，并将其提供给Pilot和其他组件。
- Gallery使用Mesh Configuration Protocol和其他组件进行配置交互。
- Galley可以被看作是团队中的文件管理员。它负责管理团队中所有的文件和信息，确保每个队员都能得到正确的信息和文件。当有新的文件产生或者文件发生变化时，Galley会及时通知团队中的每个成员，确保大家都使用的是最新的文件，不会出现信息不同步的问题。

## 数据平面

### Envoy

- Envoy是Istio中的代理，pod开启了istio功能，会在pod里自动注入Envoy sidecar容器，它负责处理服务之间的所有网络通信，拦截并转发所有的HTTP、TCP和gRPC流量。Envoy提供强大的流量控制和管理功能，如路由、重试、超时和故障注入等。

- Envoy和主容器同属于一个Pod，共享网络和命名空间，Envoy代理进出Pod的流量，并将流量按照外部请求的规则作用于主容器中。

- Envoy可以看作是服务之间的守护者。它像一个中间人一样，坐在每个服务旁边（就像每个队员身边都有一个保镖一样）。它负责处理服务之间的所有信息传递，确保信息传送得又快又准确。如果有请求从一个服务发出，Envoy会帮它找到正确的目标服务并将请求送达过去。它还能处理各种不同类型的请求，就像精通各种语言的翻译一样。

  ![image-20240212205022521](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402122050589.png)

## 组件调用关系

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402131741612.png" alt="image-20240213174135452" style="zoom: 67%;" />

1. 自动注入：Kubernetes在创建Pod时调用Sidecar代理服务，自动将Sidecar代理容器（也叫做envoy容器）注入到Pod中。
2. 流量拦截：通过设置iptables规则，Envoy拦截业务容器的入口和出口流量，应用程序感知不到Sidecar代理容器的存在。上图中，流出frontend服务的流量会被 frontend服务侧的 sidecar拦截，而当流量到达forecast容器时，Inbound流量被forecast 服务侧的sidecar拦截。
3. 服务发现：服务发起方的 Envoy 调用控制面组件 Pilot 的服务发现接口获取目标服务的实例列表。上图中，frontend 服务侧的 Envoy 通过 Pilot 的服务发现接口得到forecast服务各个实例的地址。 
4. 负载均衡：服务发起方的Envoy根据配置的负载均衡策略选择服务实例，并连接对应的实例地址。上图中，数据面的各个Envoy从Pilot中获取forecast服务的负载均衡配置，并执行负载均衡动作。 
5. 流量治理：Envoy 从 Pilot 中获取配置的流量规则，在拦截到 Inbound 流量和Outbound 流量时执行治理逻辑。上图中， frontend 服务侧的 Envoy 从 Pilot 中获取流量治理规则，并根据该流量治理规则将不同特征的流量分发到forecast服务的v1或v2版本。 
6. 访问安全：在服务间访问时通过双方的Envoy进行双向认证和通道加密，并基于服务的身份进行授权管理。上图中，Pilot下发安全相关配置，在frontend服务和forecast服务的Envoy上自动加载证书和密钥来实现双向认证，其中的证书和密钥由另一个管理面组件 Citadel维护。 
7. 服务监测：在服务间通信时，通信双方的Envoy都会连接管理面组件Mixer上报访问数据，并通过Mixer将数据转发给对应的监控后端。上图中，frontend服务对forecast服务的访问监控指标、日志和调用链都可以通过这种方式收集到对应的监控后端。 
8. 策略执行：在进行服务访问时，通过Mixer连接后端服务来控制服务间的访问，判断对访问是放行还是拒绝。上图中，Mixer 后端可以对接一个限流服务对从frontend服务到forecast服务的访问进行速率控制等操作。 
9. 外部访问：在网格的入口处有一个Envoy扮演入口网关的角 色。上图中，外部服务通过Gateway访问入口服务 frontend，对 frontend服务的负载均衡和一些流量治理策略都在这个Gateway上执行。

# istio核心资源

## DestinationRule

目标规则，将服务划分为副歌版本（子集），同时可以对不同版本进行配置负载均衡和连接池等策略。

使用场景：

1. 版本划分：根据标签划分**同一个服务的不同版本**（使用灰度发布的时候会用到，v1/v2两个版本）
2. 负载均衡策略：支持配置各种负载均衡算法（如轮询、随机、最小链接数等）
3. 熔断器：支持配置最大连接数、熔断等

## VirtualService

Istio路由规则的核心，用于控制流量走向。和Ingress类似，支持HTTP、gPRC、TCP等协议。

控制南北流量：可以声明一个域名实现集群外访问。与Ingress类似。

控制东西流量：通常和DestinationRule结合实现更细粒度的流量分配。比如灰度发布。

主要应用场景：

1. 灰度发布：支持基于比例的流量分配
2. A/B测试：支持基于请求头、URI、权重等条件的流量分配
3. 重试：支持错误重试、故障注入、链接超时等策略

## Gateway

Istio集群的出入口网关，处理对外的流量。通常和VirtualService结合实现内外流量的统一治理。

主要应用场景：

1. 端口监听：可根据协议指定对外暴露的端口
2. TLS：可以根据域名证书提供HTTPS访问
3. 域名：可以根据域名进行路由转发
4. 出口管控：可以将出口的流量固定从EgressGateway的服务中代理出去

### Ingressgateway

- ingressgateway是Istio中的一个特殊网关，它作为整个网格的入口，接收外部请求，并将它们引导到内部的服务。
- 可以将它比作一个大门保安，负责接收外部人员的访问请求，然后根据配置的规则将请求分发给网格内部的服务。

### egressgateway

- egressgateway是Istio中的另一个特殊网关，它负责处理网格内部服务对集群外部服务的访问请求。
- 可以将它看作是一个网格内部的出口，负责将内部服务需要访问的外部服务请求发送到外部。

## 核心资源逻辑架构

![image-20250826154253315](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202508261542496.png)

- DestinationRule：定义服务子集和流量策略，路由的最终目标。
- VirtualService：路由规则的核心，控制流量去向。
- Gateway：管理外部流量入口和出口，与VS协同实现内外流量统一治理。（只是声明对外暴露哪些域名和端口，实际路由转发规则是VS定义的）

三者可以单独使用也可以配合使用。

以上三种资源不是实际存在的，只是一些配置，Istio拿到这些资源，翻译成Envoy认识的配置，实际本质上起作用的还是Envoy、IngressGateway。

## 核心资源定义

官网文档：[Istio / Traffic Management](https://istio.io/latest/docs/reference/config/networking/)

### DestinationRule

[Istio / Destination Rule](https://istio.io/latest/docs/reference/config/networking/destination-rule/)

~~~yaml
apiVersion: networking.istio.io/v1
kind: DestinationRule
metadata:
  name: bookinfo-ratings
spec:
  host: ratings.prod.svc.cluster.local # 路由规则的目标。客户端向服务端发送请求时用的地址。一般是写svc FQDN
  trafficPolicy: # 针对这一个svc，配置流量规则配置
    loadbalancer:
      simple: LEAST_REQUEST # 最小请求算法
  subsets: # 版本划分
  - name: v3 # 自己起一个版本名称
    labels:
      version: v3
    trafficPolicy: # 还可以对不同版本的服务做配置，这里的会覆盖掉外面的trafficPolicy
      loadbalancer:
        simple: ROUND_ROBIN # 轮询算法
~~~

### VirtualService

[Istio / Virtual Service](https://istio.io/latest/docs/reference/config/networking/virtual-service/)

~~~yaml
apiVersion: networking.istio.io/v1
kind: VirtualService
metadata:
  name: ProductPage
  namespace: nsA
spec:
  hosts:
  # 路由规则的目标，客户端向服务端发动请求时使用的地址。
  # 如果是管理南北流量，写域名；管理东西流量，写svc的FQDN
  - bookinfo.com
  gateways:
  # 管理南北流量，写当前域名绑定的gateway的名称。
  # 管理东西流量，可以不用写
  - my-gateway
  http: # 配置七层代理规则 - 某个路径路由到哪个服务
  - match:
    - url:
        prefix: /productpage/v1/
    route:
    - destination:
        host: productpage-v1.nsA.svc.cluster.local
  # 请求匹配到bookinfo.com/productpage/v1/，就走上面的svc
  # 没匹配到，就走这个默认的svc。下面的默认配置也可以不写。
  - route:
    - destination:
        host: productpage.nsA.svc.cluster.local
~~~

### Gateway

[Istio / Gateway](https://istio.io/latest/docs/reference/config/networking/gateway/)

~~~yaml
apiVersion: networking.istio.io/v1
kind: Gateway
metadata:
  name: my-gateway
  namespace: nsA
spec:
  selector: # 选择运行此网关配置的istio ingress gateway pod（一般一个集群内装一个ingress gateway）
    app:  my-gateway-controller
  servers:
  - port:
      name: http
      number: 80
      protocol: HTTP
    hosts:
    - "bookinfo.com"
~~~

推荐给每一个ns创建一个Gateway，单独管理这个ns里面的服务暴露的域名。

不推荐把所有的域名全放在一个Gateway资源里面，这样翻译出来的Envoy配置文件会变得很大。

# istio生产环境高可用架构

回顾Ingress Controller的高可用架构：ingress Controller的pod所在的宿主机暴露80/443端口，前端有个负载均衡器LB（F5、SLB、LVS、HAProxy等），购买的公网域名绑定到LB的IP上。LB配置80/443端口，解析到ingress-conrtoller的节点的80/443上，ingress-controller再把流量代理到后端svc-pod。

## istio gateway架构

对于istio也是类似的：

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202508261729606.png" alt="image-20250826172950474" style="zoom: 67%;" />

Istio Gateway和ingress-controller一样，也是有一个端口在宿主机上暴露，这个端口是内网访问的入口。

服务发布到公网，需要在前端LB上配置IP或者代理，指向后端的istio gateway的端口号，由istio gateway再代理到后端服务。

## 设备选型问题

istio gateway和ingress controller功能一样，实际使用中用哪个？

在功能层面，istio gateway完全覆盖ingress controller的功能（反之则不行）。所以建议网关直接用istio gateway。

# itsio部署

## 版本release表

官网版本支持表：[Istio / Supported Releases](https://istio.io/latest/docs/releases/supported-releases/#support-status-of-istioreleases)

github release：[Releases · istio/istio](https://github.com/istio/istio/releases)

## 安装istioctl

Istio自带istioctl工具，用来操作istio。

~~~sh
#首先下载Istio的安装包： 
wget https://github.com/istio/istio/releases/download/1.27.0/istio-1.27.0-linux-amd64.tar.gz 
#解压后，将Istio的客户端工具istioctl，移动到/usr/local/bin 目录下： 
tar xf istio-1.27.0-linux-amd64.tar.gz 
cd istio-1.27.0 
mv bin/istioctl /usr/local/bin/ 
istioctl version 
~~~

## 声明istioOperator资源 - 测试环境

对于istio安装，也是建议用istioctl工具安装，首先需要声明istioOperator的配置：

### 创建istio-system ns

~~~sh
kubectl create ns istio-system
~~~

### 声明istioOperator配置

~~~yaml
apiVersion: install.istio.io/v1alpha1 
kind: IstioOperator 
metadata: 
  name: example-istio 
  namespace: istio-system 
spec: 
  hub: m.daocloud.io/docker.io/istio # 修改镜像地址
  meshConfig: 
    accessLogEncoding: JSON 
    accessLogFile: /dev/stdout 
  # https://istio.io/latest/docs/setup/additional-setup/config-profiles/
  profile: default # 生产环境建议直接用default就行。
  components: 
    base: 
      enabled: true 
    cni: 
      enabled: false 
    egressGateways: 
    - enabled: false 
      name: istio-egressgateway 
    ingressGateways: 
    - enabled: true 
      name: istio-ingressgateway 
      k8s: # ingressgateway自己的pod端口配置
        service:      # 将Service类型改成NodePort 
          type: NodePort 
          ports: 
          - name: status-port
            port: 15020 
            nodePort: 30520  
          - name: http2 
            port: 80  # 流量入口80端口映射到NodePort的30080，之后通过节点IP+30080即可访问Istio服务 
            nodePort: 30080 
            targetPort: 8080 
          - name: https 
            port: 443 
            nodePort: 30443 
            targetPort: 8443 
~~~

### 安装istio

~~~sh
istioctl install -f istio-operator.yaml
# This will install the Istio 1.26.0 profile "default" into the cluster. 
# Proceed? (y/N) y 
~~~

## 声明istioOperator资源 - 生产环境

测试环境安装出来的isitio和ingressgateway只有一个副本。生产环境建议两个以上的服务。

### 创建istio-system ns

~~~sh
kubectl create ns istio-system
~~~

### 声明istioOperator配置

~~~yaml
apiVersion: install.istio.io/v1alpha1 
kind: IstioOperator 
metadata: 
  name: example-istio 
  namespace: istio-system 
spec: 
  hub: m.daocloud.io/docker.io/istio 
  meshConfig: 
    accessLogEncoding: JSON 
    accessLogFile: /dev/stdout
  components: 
    base: 
      enabled: true 
    cni: 
      enabled: false 
    egressGateways: 
    - enabled: false 
      name: istio-egressgateway 
    pilot: 
      k8s: 
        hpaSpec: 
          minReplicas: 2  # 默认为1 
          maxReplicas: 5 # 默认为5 
        resources: 
          limits: 
            memory: 2Gi 
            cpu: "2" 
          requests: 
            memory: 128Mi # 生产环境调整为2 Gi 
            cpu: "100m" # 生产环境调整为2 
    ingressGateways: 
    - enabled: true 
      name: istio-ingressgateway 
      k8s: 
        hpaSpec: 
          minReplicas: 2  # default 1 
          maxReplicas: 5 # default 5 
        resources: 
          limits: 
            memory: 2Gi 
            cpu: "2" 
          requests: 
            memory: 128Mi # 生产环境调整为2 Gi 
            cpu: "100m" # 生产环境调整为2 
        service:      # 将Service类型改成NodePort 
          type: NodePort 
          ports: 
          - port: 15020 
            nodePort: 30520 
            name: status-port 
          - port: 80  # 流量入口80端口映射到NodePort的30080，之后通过节点IP+30080即可访问Istio服务 
            nodePort: 30080 
            name: http2 
            targetPort: 8080 
          - port: 443 
            nodePort: 30443 
            name: https 
            targetPort: 8443
~~~

### 安装istio

~~~sh
istioctl install -f istio-operator.yaml 
# This will install the Istio 1.26.0 profile "default" into the cluster. 
# Proceed? (y/N) y 
~~~

# istio自动注入sidecar

istio自动注入sidecar的方式有两种：

1. Namespace级别：添加`istio-injection=enabled`（disabled就关闭自动注入）的标签到指定的namespace，那么该namespace下的pod1都会被自动注入一个Sidecar。
2. Pod级别：添加`sidecar.istio.io/inject=true`（false就关闭自动注入）的标签到指定的pod，那么该pod会被注入sidecar。

## 测试sidecar注入

创建测试ns：

~~~sh
kubectl create ns istio-test
kubectl label namespace istio-test istio-injection=enabled
~~~

切换目录至 istio 的安装包解压目录，里面有自带的测试用pod。然后创建测试应用，此时创建的 Pod 会被自动注入一个 istio proxy 的容器（因为这个pod创建在了开启sidecar注入的ns下面）：

~~~sh
cd istio-1.27.0/sample/sleep/
# 更改测试服务的镜像地址：
vim sleep.yaml
image: m.daocloud.io/docker.io/curlimages/curl 
# 创建测试服务：
kubectl apply -f sleep.yaml -n istio-test 
~~~

如果需要给Pod单独添加istio-proxy，可以给Pod添加sidecar.istio.io/inject=true标签即可：

~~~yaml
  template: 
    metadata: 
      labels: 
        app: sleep 
        sidecar.istio.io/inject: "true" 
~~~

## 关闭sidecar注入

如果某个服务不想被注入sidecar，可以添加`sidecar.istio.io/inject=false`的标签即可：

~~~sh
cd istio-1.27.0/samples/curl
vim curl.yaml
~~~

~~~yaml
template: 
  metadata: 
    labels: 
      app: curl 
      sidecar.istio.io/inject: "false" 
  spec: 
    terminationGracePeriodSeconds: 0 
    serviceAccountName: curl 
    containers: 
    - name: curl 
      image: m.daocloud.io/docker.io/curlimages/curl 
~~~

如果想要关闭该Namespace的自动注入，直接去除标签即可（已注入的Pod不受影响，下次重建后，不再有isito-proxy的容器）

~~~sh
kubectl label namespace istio-test istio-injection-
~~~

> 最常用的的方式：
>
> - 打开某个ns的istio sidecar注入，其中个别pod不需要sidecar，就打标签关闭注入。
> - 单独开某几个pod的情况比较少

# istio可视化工具Kiali

Kiali为Istio提供了可视化的界面，可以在Kiali上进行观测流量的走向、调用链，同时还可以使用Kiali进行配置管理。

## 安装

kiali就在istio的安装包中，service改成NodePort，直接安装即可

~~~yaml
vim istio-1.27/samples/addons/kiali.yaml

apiVersion: v1 
kind: Service 
metadata: 
  name: kiali 
  namespace: "istio-system" 
spec: 
  type: NodePort
~~~

