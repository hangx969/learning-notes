# pod状态异常

~~~sh
kubectl get po <pod name> -o yaml
kubectl describe po <pod name>
kubectl logs <pod name> -c <container name> #--all-containers
~~~

1. pending状态

   - 创建的Pod找不到可以运行它的物理节点，不能调度到相应的节点上运行。
   - 物理节点层面分析：
     - 定位是否是节点资源问题：`free -m`查看内存；`top`查看CPU；`df -h`查看磁盘利用率。
     - 查看节点污点：`kubectl describe nodes <node name>`,例如：`Taints:node-role.kubernetes.io/master:NoSchedule`,表明这个节点不允许调度pod。除非pod定义对这个污点的容忍度才行。
   - pod本身分析：
     - pod是否指定了节点调度（NodeSelector），看一下node name是否正确。
     - pod是否指定了过大的resource request，节点无法满足。
     - pod是否指定了节点亲和性，但是没有节点满足。

2. ImagePullBackOff状态

   - image的name或者tag错误
   - 镜像源无法访问，比如国内网络限制，无法访问dockerhub；或者网速过慢，拉取image超时
   - 私有仓库参数错误，比如imagePullSecret错误
   - dockerfile打包的镜像有问题

   可以手动在工作节点上docker pull看是否可以拉下镜像。

3. CrashLoopBackOff

   - 查看构建镜像用的代码是否有问题；
   - 如果代码没问题，再看环境变量是否有问题；
   - 也可能权限问题：假如pod挂载了数据目录，这个数据目录，我们需要修改属主和属组，否则pod往这个目录写数据，可能没权限

4. Evicted

   - 这个Evicted表示pod所在节点的资源不够了，pod被驱逐走了

5. Complete状态

   - 这个状态表示pod里面的任务完成了，job或者cronjob创建pod的时候，如果pod任务完成了，会出现complete状态

# pod健康探测

~~~yaml
#pod定义的存活性探测如下：
livenessProbe:
       httpGet:
         path: /
         port: 8080
~~~

- 常见错误：Killing container with id docker://xianchao:Container failed probe.. Container will be killed and recreated. Liveness
- 如果在pod启动时遇到这种情况，一般是没有设置 initialDelaySeconds导致的

~~~yaml
# 设置初始化延迟initialDelaySeconds。
livenessProbe:
       httpGet:
         path: /
         port: 8080
       initialDelaySeconds: 15 # pod启动过15s开始探测
~~~

# pod svc超时

K8S中Pod服务连接超时主要分以下几种情况：

1. Pod和Pod连接超时
2. Pod和虚拟主机上的服务连接超时
3. Pod和云主机连接超时

针对上面几种问题，排查思路可按下面方法：

- 网络插件层面：
  - 查看calico或者flannel是否是running状态，查看日志提取重要信息

- Pod层面：

  - 检查Pod网络，测试Pod是否可以ping通同网段其他pod ip

- 物理机层面：
  - 检查物理机网络，测试ping www.baidu.com，ping其他的pod ip
  - 可以抓包测试有无异常
  - 通过抓包修改内核参数

# svc代理pod出现问题

- 直接访问pod可以请求到，但是访问pod前端service，通过请求pod有问题，请求不到。
  - iptables： 重启iptables，重启iptables不可以，重启下机器
  - ipvs：重启机器

# DNS解析问题

1. 使用 `nslookup`（需容器支持）

```sh
kubectl exec <pod-name> -- nslookup google.com
```

2. 查看 DNS 配置

```sh
kubectl exec <pod-name> -- cat /etc/resolv.conf
```

预期输出示例：

```sh
nameserver 10.96.0.10    # Kubernetes DNS Service IP
search default.svc.cluster.local svc.cluster.local cluster.local
options ndots:5
```

3. 若 `nslookup` 失败，检查 CoreDNS 或 kube-dns 是否正常运行：

```sh
kubectl get pods -n kube-system -l k8s-app=kube-dns
```

4. 确认 Pod 的 DNS 策略（`dnsPolicy`）是否为 `ClusterFirst`。

# 防火墙问题

怀疑网络策略（NetworkPolicy）或云平台安全组阻止外网访问。

1. 检查 NetworkPolicy

```sh
kubectl describe networkpolicy -n <namespace>
```

重点关注是否有策略限制出站流量（`egress`）。

2. 验证云平台安全组/防火墙规则

3. 登录到 Pod 所在节点，查看 NAT 表和过滤规则：

```sh
iptables -t nat -L -n -v
iptables -L -n -v
```

# openshift中busybox无法ping

- 报错permission denied are you root

- 解决：

  - 查了下资料，发现是crio运行容器时为了安全，会把NET_RAW删除，而docker默认是启用的，可以在yaml自行手动添加
  
  ~~~yaml
  securityContext:
    capabilities:
      add:
      - NET_RAW
  ~~~
  

# 容器无shell如何测试外网连通性

在 Kubernetes 集群中，某些容器镜像（如基于 `scratch` 或 `distroless` 的镜像）为了追求极简化和安全性，移除了交互式 Shell（如 `/bin/bash` 或 `/bin/sh`）以及常见网络工具（如 `curl`、`ping`）。当这类 Pod 出现外网访问异常时，传统调试方法失效，需要更高级的技巧。

## 临时容器

适用于容器中无网络工具，，k8s版本高于1.23。临时容器会共享目标容器的 **网络命名空间**，因此两者的网络栈（IP、端口、路由等）完全一致。退出临时容器后，它会被自动销毁，不会影响原 Pod。

注意：

- 若集群版本低于 `1.23`，需启用 `EphemeralContainers` 特性门控。
- 调试镜像可能需要特权权限，需确保 Pod 的 SecurityContext 允许临时容器运行。

1. 注入临时容器

   ~~~sh
   kubectl debug -it <pod-name> --image=nicolaka/netshoot --target=<container-name>
   #nicolaka/netshoot，内置完整网络工具链
   ~~~

2. 在临时容器中测试外网

   ~~~SH
   # 测试 HTTP 访问
   curl -I https://www.google.com
   # 测试 DNS 解析
   nslookup google.com
   # 测试 ICMP（ping）
   ping 8.8.8.8
   ~~~

## 注入sidecar容器

适用于临时容器功能不可用，但是允许修改pod配置。同一 Pod 内的所有容器共享同一个网络命名空间，因此 Sidecar 可以直接访问主容器的网络环境。

注意：

- 需要重新部署pod，可能会有downtime
- 生产环境中慎用，建议仅在调试阶段添加sidecar

1. 编辑pod yaml，添加sidecar

   ~~~yaml
   apiVersion: v1
   kind: Pod
   metadata:
     name: my-pod
   spec:
     containers:
     - name: main-app
       image: my-minimal-image:latest
       # 主容器无 Shell 和网络工具...
     - name: network-debugger
       image: nicolaka/netshoot
       command: ["sleep", "infinity"]  # 保持 Sidecar 运行
       securityContext:
         runAsUser: 0  # 以 root 用户运行（可选）
   ~~~

2. 进入sidecar容器测试网络

   ~~~sh
   kubectl exec -it my-pod -c network-debugger -- curl -v https://www.google.com
   ~~~

## 跳板机pod代理测试

如果无法修改目标 Pod，也没有临时容器功能，且需要模拟相同网络环境。

1. 启动跳板机pod

   ~~~sh
   kubectl run jumpbox --image=nicolaka/netshoot --rm -it --restart=Never -- /bin/sh
   ~~~

2. 在跳板机pod中通过代理测试目标pod的网络

   假设目标 Pod 的 IP 为 `10.244.1.5`：

   ~~~sh
   # 使用 curl 的 --proxy 参数
   curl -x http://10.244.1.5:80 http://example.com
   
   # 使用 nc 测试 TCP 连通性
   nc -zv 10.244.1.5 80
   ~~~

## 调试镜像选择

| 镜像名称            | 特点                                      | 适用场景             |
| ------------------- | ----------------------------------------- | -------------------- |
| `nicolaka/netshoot` | 包含完整网络工具（curl, tcpdump, dig 等） | 通用网络调试         |
| `busybox:glibc`     | 轻量级，支持 nslookup、ping               | 基础连通性测试       |
| `alpine:latest`     | 包含 Shell 和包管理器（apk）              | 需临时安装工具的场合 |