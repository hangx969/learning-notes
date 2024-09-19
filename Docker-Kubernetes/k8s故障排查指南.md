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
  
  