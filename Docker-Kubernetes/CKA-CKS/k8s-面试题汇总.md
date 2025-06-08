1. 在一个只有两个节点的集群中，一个节点有pod，另一个节点没有，新的pod会被调度到哪个节点？
   - 调度过程涉及到多个阶段，结果取决于亲和性、污点容忍度、调度插件的配置。假设是默认配置并且两个节点的资源可用性相同，NodeResourceFit插件会起到关键作用，其评分策略包括
     - LeastAllocated（默认选项，优先选择资源使用量最小的节点）
     - MostAllocated（优先选择资源使用较多的节点）
     - RequestedToCapacityRatio（平衡资源使用率）
   - 在MostAllocated模式下会调度到已有Pod的节点，其余两种模式会调度到空节点
2. 如果容器的应用程序遇到OOM，容器会重启还是整个pod会被重建？
   - 容器OOM时，通常会根据Pod的RestartPolicy来重启容器（默认是Always），这种重启，pod保持不变。
   - 但是如果在极端情况下节点的内存资源不足，Pod可能会被Evited到其他节点，这样Pod就会经历重建了。

3. 应用程序配置，如环境变量或ConfigMap更新，是否可以动态更新而无需重新创建pod？
   - 环境变量无法动态更新。
   - 但如果configMap以文件形式挂载（不使用subPath情况下），则可以实现动态更新应用。同步延时取决于：
     - kubelet的syncFrequency（默认1min）
     - 和configMapAndSecretChangeStrategy
4. 一旦创建了pod，即使用户不去人为干预，pod是否稳定？
   - pod并不保证稳定，资源短缺、网络中断等因素可能会导致pod被驱逐。
5. ClusterIP类型的Service能否确保TCP流量的负载均衡？
   - 基于ClusterIP的svc，依赖Linux内核的Netfilter机制进行负载均衡，其connection tracking机制为已建立的TCP连接保持会话持久性。这可能导致长连接分布不均。
6. 应该如何收集应用程序日志，是否存在日志丢失的风险？
   - 日志可以输出到stdout/stderr或者写入文件。对于stdout/stderr，日志保存在节点上，可以使用Fluentd或者Filebeat等日志代理采集（通常会以Daemonset部署）。
   - 但如果pod被删除，日志可能会在代理采集之前丢失。将日志写入持久化存储中的文件可以避免日志丢失。
7. 如果HTTP server pod的livenessProbe返回正常，是否可以认为应用程序没有问题？
   - 从应用程序角度看，livenessProbe正常代表应用程序存活，但不检查其功能是否正常。应用程序可能处于降级状态，仍能通过livenessProbe。
   - 从网络角度看，livenessProbe（如httpGet）是pod接收本节点kubelet的请求，这说明同节点通信是好的。这并不能保证跨节点网络可用性。
8. 应用程序如何扩展以应对流量波动？
   - pod支持水平扩展（HPA）和垂直扩展（VPA）。
   - VPA涉及到重新调整pod资源，要重建pod，这就限制了其应用场景。
   - HPA更常用，根据CPU、memory、请求速率等指标动态调整pod数量。外部系统也可以向api-server发送请求来触发扩展。
9. 当你执行kubectl exec -it是，是否登录到了pod里面
   - 并不是，kubectl exec需要指定容器。pod是隔离的Linux namespace的集合，容器共享Network、IPC和UTS namespace；而PID和Mount namespace保持独立。
   - kubectl exec在目标容器的隔离环境中启动一个新的bash进程，但并未登录到pod中。
10. pod中的容器反复崩溃重启，怎么排查？
    - 容器反复崩溃，kubectl exec就用不了了。
    - 可以检查节点和pod日志。kuebctl logs --previous
    - 可以用kubectl debug启动临时容器，以检查环境问题和依赖问题。
