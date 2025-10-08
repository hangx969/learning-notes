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
cd istio-1.27.0 && mv bin/istioctl /usr/local/bin/ 
istioctl version 
~~~

## 声明istioOperator资源 - 测试环境

对于istio安装，也是建议用istioctl工具安装，首先需要声明istioOperator的配置：

### 创建istio-system ns

~~~sh
kubectl create ns istio-system
~~~

### 声明istioOperator配置

创建istio-operator.yaml：

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

#### profile选项

- 使用 `istioctl` 安装 Istio 时，会根据指定的 profile 来选择使用的 Istio 配置文件。

- profile 参数是一个预定义的配置选项，用于快速设置 Istio 的安装配置。每个 profile 都对应一个特定的 YAML 配置文件，其中包含了一组预定义的配置选项。

- 在 Istio 的安装过程中，profile 参数可以指定为以下一些值：

  - demo：适用于**生产环境**，包含`istiod`、`ingressgateway`、`egressgateway`

  - default：这是一个最小配置，仅包含最基本的组件，如`istiod`和`ingressgateway` 

  - minimal：这个配置相对更加精简，只包含了必需的组件，适用于资源受限或轻量级的环境。只会安装`istiod`。

- istioctl install 本质上是根据选择的 profile 来加载对应的 YAML 配置文件，并将配置部署到 Kubernetes 集群中。

- 如果你想查看 demo 配置文件的内容，可以通过以下命令查找 Istio 的安装目录并找到对应的文件：

  ```sh
  istioctl profile dump demo
  ```

  这将打印出 demo 配置的完整内容，包括各个组件的配置选项。你也可以在 Istio 官方文档中找到各种预定义的 profile 配置选项的详细信息。

## 声明istioOperator资源 - 生产环境

测试环境安装出来的isitio和ingressgateway只有一个副本。生产环境建议两个以上的服务。

### 创建istio-system ns

~~~sh
kubectl create ns istio-system
~~~

### 声明istioOperator配置

istio组件的

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
    pilot: # istiod组件的hpa
      k8s: 
        hpaSpec: 
          minReplicas: 2  # 默认为1 
          maxReplicas: 5 # 默认为5 
        resources: 
          limits: # 生产环境建议4C4G/4C8G
            memory: 2Gi 
            cpu: "2" 
          requests: # 生产环境建议4C4G/4C8G（和limit一样，提高QoS）
            memory: 128Mi
            cpu: "100m" 
    ingressGateways: 
    - enabled: true 
      name: istio-ingressgateway 
      k8s: # ingressGateway的hpa配置
        hpaSpec: 
          minReplicas: 2  # default 1 
          maxReplicas: 5 # default 5 
        resources: 
          limits: # 生产环境建议4C4G/4C8G
            memory: 2Gi 
            cpu: "2" 
          requests: # 生产环境建议4C4G/4C8G（和limit一样，提高QoS）
            memory: 128Mi 
            cpu: "100m" 
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
vim ./istio-1.27/samples/addons/kiali.yaml

apiVersion: v1 
kind: Service 
metadata: 
  name: kiali 
  namespace: "istio-system" 
spec: 
  type: NodePort
  
# 安装
kubectl apply -f ./istio-1.27/samples/addons/kiali.yaml
# 通过NodePort高位端口访问UI界面
~~~

# 安装链路追踪jaeger

除了Kiali 之外，还可以安装一个链路追踪的工具，安装该工具可以在Kiali的Workloads页面，查看某个服务的Traces信息：

~~~yaml
cd ./istio-1.27.0/samples/addons

# 首先更改镜像地址 
vim samples/addons/jaeger.yaml 
image: "m.daocloud.io/docker.io/jaegertracing/all-in-one:1.67.0"

# 更改名称为tracing的svc为NodePort
vim samples/addons/jaeger.yaml 
apiVersion: v1
kind: Service
metadata:
  name: tracing
  namespace: istio-system
  labels:
    app: jaeger
spec:
  type: NodePort
  ports:
    - name: http-query
      port: 80
      protocol: TCP
      targetPort: 16686
    # Note: Change port name if you add '--query.grpc.tls.enabled=true'
    - name: grpc-query
      port: 16685
      protocol: TCP
      targetPort: 16685
  selector:
    app: jaeger

# 创建
kubectl create -f samples/addons/jaeger.yaml

# 通过NodePort高位端口访问UI界面
~~~

> 注意：公司如果真需要上链路追踪，建议用更专业的Skywalking。jaeger这个比较简单而且也不太好用。

# 集成prometheus+grafana

Istio 默认暴露了很多监控指标，比如请求数量统计、请求持续时间以及Service和工作负载的指标，这些指标可以使用Prometheus进行收集，Grafana进行展示。

Istio 内置了Prometheus和Grafana的安装文件，直接安装即可。

> 也可以使用外置的Prometheus和Grafana。
>
> 但是建议istio的prometheus和grafana单独安装，因为集群自己的prometheus需要监控很多集群其他指标，不建议再接入istio的指标。istio用自己独立的prometheus和grafana即可。

## 安装

~~~sh
# 同样需要修改镜像地址 
vim samples/addons/grafana.yaml 
image: "m.daocloud.io/docker.io/grafana/grafana:11.3.1" 
vim samples/addons/prometheus.yaml
image: "m.daocloud.io/docker.io/prom/prometheus:v3.2.1" 

# 修改svc为NodePort
vim samples/addons/grafana.yaml # 修改name为grafana的svc
vim samples/addons/prometheus.yaml # 修改名为prometheus的svc

# 安装
kubectl create -f samples/addons/prometheus.yaml -f samples/addons/grafana.yaml 
# 完成后通过NodePort高位端口访问grafana
~~~

## Grafana dashboard

进入到Grafana dashboard可以看到默认已经加进去了istio相关的dashboard。

进入Istio Control Plane Dashboard：

1. 有一个指标叫：“**Push Erros**”，代表当前的配置分发到数据平面有没有报错。可以着重看这个指标

进入Istio Mesh Dashboard：

1. 这是全局监控面板，如果出现性能问题，可以在其中查看相关指标。

进入Istio Performance Dashboard：

1. 这里面显示了istio的资源使用情况。出现性能问题同样可以在其中查看。

进入Istio Service Dashboard和Istio Workload Dashboard：

1. 可以看到服务间访问的链路情况。

# istio流量治理实践

istio官网提供了BookInfo项目：https://istio.io/latest/docs/examples/bookinfo/

## 部署bookinfo项目

创建ns并添加自动注入标签：

~~~sh
kubectl create ns bookinfo
kubectl label ns bookinfo istio-injection=enabled
~~~

修改项目里面的镜像地址：

~~~sh
vim samples/bookinfo/platform/kube/bookinfo.yaml
image: m.daocloud.io/docker.io/istio/examples-bookinfo-details-v1:1.20.3 
image: m.daocloud.io/docker.io/istio/examples-bookinfo-ratings-v1:1.20.3 
image: m.daocloud.io/docker.io/istio/examples-bookinfo-reviews-v1:1.20.3 
image: m.daocloud.io/docker.io/istio/examples-bookinfo-reviews-v2:1.20.3 
image: m.daocloud.io/docker.io/istio/examples-bookinfo-reviews-v3:1.20.3 
image: m.daocloud.io/docker.io/istio/examples-bookinfo-productpage-v1:1.20.3 
~~~

部署服务：

~~~sh
kubectl apply -f samples/bookinfo/platform/kube/bookinfo.yaml -n bookinfo 
~~~

## 使用域名发布服务

接下来创建Istio的Gateway和VirtualService实现域名访问Bookinfo项目。

### 创建Gateway

首先创建Gateway，假设发布的域名是`bookinfo.kubeasy.com`。Gateway配置如下所示：

~~~yaml
apiVersion: networking.istio.io/v1 
kind: Gateway 
metadata: 
  name: bookinfo-gateway 
spec:
  # The selector matches the ingress gateway pod labels.
  # If you installed Istio using Helm following the standard documentation, this would be "istio=ingress"
  selector: 
    istio: ingressgateway # 使用默认的istio ingress gateway 
  servers: 
  - port: 
      number: 80 
      name: http 
      protocol: HTTP 
    hosts: 
    - "bookinfo.kubeasy.com" # 发布域名
~~~

### 创建VirtualService

接下来创建VirtualService，实现对不同微服务的访问

~~~yaml
--- 
apiVersion: networking.istio.io/v1 
kind: VirtualService 
metadata: 
  name: bookinfo 
spec: 
  hosts: 
  - "bookinfo.kubeasy.com" 
  gateways: 
  - bookinfo-gateway 
  http: 
  - match: 
    - uri: 
        exact: /productpage 
    - uri: 
        prefix: /static 
    - uri: 
        exact: /login 
    - uri: 
        exact: /logout 
    - uri: 
        prefix: /api/v1/products 
    route: 
    - destination: 
        host: pproductpage.bookinfo.svc.cluster.local 
        port: 
          number: 9080 
~~~

部署Gateway和VS：

~~~sh
kubectl apply -f bookinfo-gateway.yaml -f bookinfo-vs.yaml -n bookinfo
~~~

### 发布域名

接下来将域名bookinfo.kubeasy.com解析至集群任意一个安装了kube-proxy的节点IP上，然后通过ingressgateway的Service的NodePort即可访问到Bookinfo：

~~~sh
kubectl get svc -n istio-system istio-ingressgateway
~~~

1. 绑定hosts后，通过bookinfo.kubeasy.com +【ingressgateway 80 端口对应的NodePort（30080）】即可访问该服务，比如本次示例：`bookinfo.kubeasy.com:30080/productpage`

(实际生产环境中有前端LB，外部用户要访问的话需要把域名解析到前端LB的IP，默认是80/443端口，就不用写端口号了。由LB再把请求转发到后端ingressgateway上面)

2. 多访问几次，可以看到Reviewer处的星星会在黑色、红色和消失之间来回替换，是因为部署了三个不同版本的reviews，每个版本具有不同的显示效果。

3. 然后去kiali - traffic graph里面看到流量链路图。

## 地址重写和重定向

Istio 同样支持访问地址的重写和重定向，这个功能一般用于新旧域名的替换和移动端、桌面端互相跳转。效果是访问某个域名的某个路径时，自动跳转到另一个域名的另一个路径。

详细配置文档：https://istio.io/latest/docs/reference/config/networking/virtual-service/#HTTPRedirect 

### 域名重定向

比如将`bookinfo.kubeasy.com/hangx`跳转到` edu.51cto.com/lecturer/11062970.html`，在VS里面配置：

~~~yaml
--- 
apiVersion: networking.istio.io/v1 
kind: VirtualService 
metadata: 
  name: bookinfo 
spec: 
  hosts: 
  - "bookinfo.kubeasy.com" 
  gateways: 
  - bookinfo-gateway 
  http: 
  - match: 
    - uri: 
        prefix: /hangx # 匹配/hangx
    redirect: 
      authority: edu.51cto.com  # 跳转的域名 
      uri: /lecturer/11062970.html  # 跳转的路径
  - match: 
    - uri: 
        exact: /productpage 
    - uri: 
        prefix: /static 
    - uri: 
        exact: /login 
    - uri: 
        exact: /logout 
    - uri: 
        prefix: /api/v1/products 
    route: 
    - destination: 
        host: productpage.bookinfo.svc.cluster.local
        port: 
          number: 9080 
~~~

~~~sh
kubectl apply -f bookinfo-vs.yaml -n bookinfo
~~~

### 地址重写

地址重写的一个典型应用场景就是：

1. 同一个域名代理了很多后端服务，比如：test.com --> a、b、b三个服务，需要通过test.com/a、test.com/b、test.com/c来路由到不同后端服务
2. 但是对于a、b、c服务的三个后端pod，开发出来对外暴露的接口都是/api。你直接访问test.com/a报404，因为pod根本没暴露这个接口，人家暴露的是/api
3. 这就需要根据域名/路径，重定向到后端服务。比如将test.com/a重写为test.com/api，route配置为a服务的svc。

我们上面bookinfo项目默认根路径是报错404的：`bookinfo.kubeasy.com:30080/`，我们可以配置根路径访问到/productpage页面。在VS中配置：

~~~yaml
--- 
apiVersion: networking.istio.io/v1 
kind: VirtualService 
metadata: 
  name: bookinfo 
spec: 
  hosts: 
  - "bookinfo.kubeasy.com" 
  gateways: 
  - bookinfo-gateway
  http: 
  - match:
    - uri:
        exact: / # 匹配根路径
    rewrite: # 地址重写为/productpage
      uri: /productpage
    route: # 指定rewrite到哪个
    - destination:
        host: productpage.bookinfo.svc.cluster.local
        port:
          number: 9080
  - match: 
    - uri: 
        exact: /productpage 
    - uri: 
        prefix: /static 
    - uri: 
        exact: /login 
    - uri: 
        exact: /logout 
    - uri: 
        prefix: /api/v1/products 
    route: 
    - destination: 
        host: productpage.bookinfo.svc.cluster.local
        port: 
          number: 9080 
~~~

~~~sh
kubectl apply -f bookinfo-vs.yaml -n bookinfo
~~~

## istio实现灰度发布

使用Istio进行细粒度的流量管理，步骤如下：

1. 创建DR划分subset
2. 创建VS将100%流量导向旧版本
3. 部署新版本
4. 使用VS逐渐切换比例流量到新版本

### 创建DR划分子集

在bookinfo项目中，有三个版本的reviews服务（pod打好了标签version=v1、v2、v3）。首先通过DestinationRule将reviews分成三个版本：

~~~yaml
apiVersion: networking.istio.io/v1 
kind: DestinationRule 
metadata: 
  name: reviews 
spec: 
  host: reviews.bookinfo.svc.cluster.local
  subsets: 
  - name: v1 
    labels: 
      version: v1 # subset v1指向具有version=v1的Pod 
  - name: v2 
    labels: 
      version: v2 # subset v2指向具有version=v2的Pod 
  - name: v3 
    labels: 
      version: v3 # subset v3指向具有version=v3的Pod 
~~~

~~~sh
kubectl apply -f bookinfo-canary-dr.yaml -n bookinfo
~~~

### 创建VS路由流量

1. 首先将所有流量路由到v1：

~~~yaml
apiVersion: networking.istio.io/v1 
kind: VirtualService 
metadata: 
  name: reviews 
spec: 
  hosts: 
  - reviews.bookinfo.svc.cluster.local 
  http: 
  - route: 
    - destination: 
        host: reviews.bookinfo.svc.cluster.local 
        subset: v1 # 将流量全部指向v1
~~~

~~~sh
kubectl apply -f vs-reviews-v1-all.yaml -n bookinfo
~~~

2. 开发了v2版本上线，现在把20%流量切到v2作为灰度发布：

~~~yaml
apiVersion: networking.istio.io/v1 
kind: VirtualService 
metadata: 
  name: reviews 
spec: 
  hosts: 
  - reviews.bookinfo.svc.cluster.local 
  http: 
  - route: 
      - weight: 80
        destination: 
          host: reviews.bookinfo.svc.cluster.local 
          subset: v1
      - weight: 20
        destination: 
          host: reviews.bookinfo.svc.cluster.local
          subset: v2    
~~~

~~~sh
kubectl apply -f vs-reviews-v1-all.yaml -n bookinfo
~~~

3. 将流量全部导向v2

~~~yaml
apiVersion: networking.istio.io/v1 
kind: VirtualService 
metadata: 
  name: reviews 
spec: 
  hosts: 
  - reviews.bookinfo.svc.cluster.local 
  http: 
  - route:
    - destination: 
        host: reviews.bookinfo.svc.cluster.local
        subset: v2
~~~

~~~sh
kubectl apply -f vs-reviews-v1-all.yaml -n bookinfo
~~~

## istio实现A/B测试

Istio也支持基于请求头、uri、schema等方式的细粒度流量管理，这种路由方式比较适用于新版本上线时的AB测试。

Istio请求头匹配介绍：https://istio.io/latest/docs/reference/config/networking/virtual-service/#HTTPMatchRequest 

假如bookinfo项目又开发了一个新版v3，此时只想要公司内部的测试组先进行测试，可以配置VirtualService指定部分用户访问新版本。 

1. 再次修改reviews的VirtualService，将jason用户指向v3，其他用户依旧使用v2版本：

~~~yaml 
apiVersion: networking.istio.io/v1 
kind: VirtualService 
metadata: 
  name: reviews 
spec: 
  hosts: 
  - reviews.bookinfo.svc.cluster.local 
  http: 
  - match: 
    - headers: # 匹配请求头 
        end-user: # 匹配请求头的key为end-user。根据实际情况填写合适的header头
          exact: jason # value 为jason，也支持prefix、regex 
    route: 
    - destination: 
        host: reviews.bookinfo.svc.cluster.local
        subset: v3 # 匹配到end-user=jason路由至v3版本
  - route: 
    - destination: 
        host: reviews.bookinfo.svc.cluster.local
        subset: v2 # 其余用户路由到v2版本
~~~

~~~sh
kubectl apply -f vs-ab-json-v3.yaml -n bookinfo
~~~

在bookinfo.kubeasy.com:30080/productpage页面上登录，user为jason，密码随便写。登录后可以发现使用的是v3版本的reviews（星星颜色为红色）

2. 当AB测试完成后，可以再接上一个灰度发布，20%到v3，80%到v2。
3. 灰度发布完成后，再完全切换流量到v3

## istio负载均衡算法

k8s原生可以调整节点级别kube-proxy ipvs的负载均衡算法，但是不支持精细化到pod级别的负载均衡算法，Istio可以。

Istio原生支持多种负载均衡算法，比如ROUND_ROBIN、LEAST_REQUEST、LEAST_CONN、RANDOM等。假如一个应用存在多个副本（Pod），可以使用上述算法对多个Pod进行定制化的负载均衡配置。

常见的负载均衡策略如下：

1. ROUND_ROBIN：轮询算法，将请求依次分配给每一个实例，不推荐使用。

   > 只要涉及到负载均衡算法，都不推荐使用轮询，已经被证实存在很多问题，比如：某个节点由于性能问题（比如cpu、内存高），导致上面pod处理请求比较慢，但是轮询是感知不到的。会导致请求不断还是会继续发送到这个节点的pod上，导致这个pod一直cpu飚高，但是其他pod空闲。

2. LEAST_REQUEST：最小链接算法，从池中随机选择两个实例pod，并将请求路由给当前活跃请求数较少的那个主机。`【生产环境建议】`

3. RANDOM：随机算法，将请求随机分配给其中一个实例。

4. PASSTHROUGH：将连接转发到调用者请求的原始 IP 地址，而不进行任何形式的负载均衡，目前不推荐使用。

5. UNSPECIFIED：未指定负载均衡算法，Istio将选择一个合适的默认算法，不推荐使用。

### 更改负载均衡算法

更改负载均衡算法需要在DR上配置，因为DR才是控制流量作用到pod上的。

~~~yaml
apiVersion: networking.istio.io/v1 
kind: DestinationRule 
metadata: 
  name: reviews 
spec: 
  trafficPolicy:  # 添加路由策略，在spec下对所有的subset生效，也可以在subset中配置
    loadBalancer: # 配置负载均衡
      simple: RANDOM # 策略为RANDOM
  host: reviews.bookinfo.svc.cluster.local
  subsets: 
  - name: v1 
    labels: 
      version: v1 # subset v1指向具有version=v1的Pod 
    trafficPolicy: # 对于v1的所有pod配置单独的负载均衡算法
      loadBalancer: # 配置负载均衡
        simple: LEAST_REQUEST # 策略为RANDOM
  - name: v2 
    labels: 
      version: v2 # subset v2指向具有version=v2的Pod 
  - name: v3 
    labels: 
      version: v3 # subset v3指向具有version=v3的Pod 
~~~

~~~sh
kubectl apply -f bookinfo-canary-dr.yaml -n bookinfo
~~~

## istio熔断配置

Istio支持熔断机制，可以实现在高并发时对服务进行过载保护。比如部署了一个大模型服务，只能同时支持100用户请求。此时来了高于100个请求，就会造成服务宕机，影响前100个正常用户的访问。这样影响太大。可以设置熔断，超过最大并发量的时候，新进来的请求返回一个“当前繁忙，请稍后再试”之类的友好提示。

假设对ratings进行熔断，希望在并发请求数超过3，并且存在1个以上的待处理请求，就触发熔断。因为熔断也是在最终实例pod上生效的，也是在DR上配置的。

### DR配置熔断

此时可以配置ratings的DestinationRule如下所示： 

~~~yaml
# vim ratings-dr.yaml  
apiVersion: networking.istio.io/v1 
kind: DestinationRule 
metadata: 
  name: ratings 
  namespace: bookinfo 
spec: 
  host: ratings.bookinfo.svc.cluster.local
  trafficPolicy: # trafficPolicy配置，也可以配置在subsets级别 
    connectionPool: # 连接池配置，可以单独使用限制程序的并发数 
      tcp: 
        maxConnections: 3 # 最大并发数为3 
      http: 
        http1MaxPendingRequests: 1 # 最大的待处理请求。
        # 假如有2个待处理请求，就触发了熔断，不让你排队了，因为排队也没有用了
    outlierDetection:  # 熔断探测配置 
      consecutive5xxErrors: 1  # 如果连续出现的5xx错误超过1次，就会被熔断 
      interval: 10s # 每10秒探测一次后端实例 
      baseEjectionTime: 3m  # 熔断的时间。某个后端pod触发熔断后，也不能一直不接受请求。3分钟之后，估算着请求应该都处理完成了，重新接受请求。
      maxEjectionPercent: 100 # 被熔断实例最大的百分比。比如10个pod，10个都能触发熔断就是100。测试用写100。实际写50就可以，太高会造成其他实例出现性能问题。
  subsets: 
  - name: v1
    labels: 
      version: v1 
~~~

### fortio压测

istio安装包提供了压测工具fortio，先部署一下：

~~~sh
# 修改镜像
vim samples/httpbin/sample-client/fortio-deploy.yaml

# 部署
kubectl apply -f samples/httpbin/sample-client/fortio-deploy.yaml -n bookinfo
~~~

获取容器ID并发送请求：

~~~sh
FORTIO_POD=$(kubectl get pod -n bookinfo | grep fortio | awk '{ print $1 }') 
echo $FORTIO_POD

kubectl exec -ti $FORTIO_POD -n bookinfo -- fortio load -curl http://ratings:9080/ratings/0
~~~

接下来更改为两个并发连接（-c 2），发送20请求（-n 20）:

~~~sh
kubectl exec -ti $FORTIO_POD -n bookinfo -- fortio load -c 2 -qps 0 -n 20 -loglevel Warning http://ratings:9080/ratings/0 | grep Code 
~~~

可以看到请求都是成功的，说明pod处理这些请求速度很快，请求没有排队待处理

提高并发量，会触发熔断：

~~~sh
kubectl exec -ti $FORTIO_POD -n bookinfo -- fortio load -c 20 -qps 0 -n 20 -loglevel Warning  http://ratings:9080/ratings/0 | grep Code

Code 200 : 5 (25.0 %)
Code 503 : 15 (75.0 %)
~~~

说明触发了熔断，pod没有直接挂掉，实现了过载保护。

## istio故障注入

### 延迟

主要用来测试链路可靠性，比如三个服务A-B-C，由于偶发网络延迟高，C服务响应变慢，是否会影响A、B服务？这是链路可靠性的问题，需要我们进行测试。

首先创建测试工具，测试访问details服务的时间：

~~~sh
kubectl create deploy -n bookinfo debug-tools --image=registry.cn-beijing.aliyuncs.com/dotbalo/debug-tools -- sleep 36000

kubectl exec -ti debug-tools-5887bf6774-598tc  -n bookinfo –- bash
time curl -I -s details:9080
~~~

不添加任何故障延迟时，0.02秒左右就会返回结果。接下来注入一个5s的延迟。由于故障注入属于service级别，所以是在vs上配置：

~~~yaml
# vim details-delay.yaml  
apiVersion: networking.istio.io/v1 
kind: VirtualService 
metadata: 
  name: details 
spec: 
  hosts: 
  - details.bookinfo.svc.cluster.local
  http: 
  - fault: # 添加一个错误 
      delay: # 添加类型为delay的故障 
        percentage: # 故障注入的百分比 
          value: 100 # 对所有请求注入故障 
        fixedDelay: 5s # 注入的延迟时间 
    route: 
    - destination: 
        host: details 
~~~

~~~sh
kubectl create -f details-delay.yaml -n bookinfo
~~~

再返回测试工具进行测试，响应时间变成了5s：

~~~sh
time curl -I -s details:9080
~~~

假设我们有A服务去访问details服务，设置的超时时间为2s，这样通过延迟故障注入，我们可以测试这个超时时间配置是否生效。

### 中断

注入中断故障，可以模拟服务返回指定的状态码（400、503等），上游服务的处理是否符合预期。（上游服务如果接收到异常状态码，也抛出异常，那就不正确了；需要配置上异常处理才算是合理的代码）

中断故障注入只需要将fault 的delay更改为abort即可： 

~~~yaml
# vim details-abort.yaml 
apiVersion: networking.istio.io/v1 
kind: VirtualService 
metadata: 
  name: details 
spec: 
  hosts: 
  - details 
  http: 
  - fault: 
      abort: # 更改为abort类型的故障 
        percentage: 
          value: 100 
        httpStatus: 400 # 故障状态码 
     route: 
     - destination: 
         host: details 
~~~

