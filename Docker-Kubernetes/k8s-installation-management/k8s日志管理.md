Kubernetes 容器日志的保存时长并非固定值，而是由**节点本地默认策略**、**日志输出方式**和**持久化方案**共同决定。

# 节点本地默认日志保存机制 - kubelet管控

K8s 集群中，容器标准输出（stdout/stderr）的日志默认由kubelet负责管理，遵循**大小 + 文件数**双重限制策略，而非基于固定时间周期。

## 核心限制参数（默认值）

打开 kubelet 配置：`/var/lib/kubelet/config.yaml`
- `containerLogMaxFiles: 5`，每个容器最多保留**5 个**日志文件（含当前活跃文件）
- `containerLogMaxSize: 10Mi`，单个日志文件最大**10MiB**（达到即触发轮转）

计算：每个容器默认最多占用约**50MiB**存储（10MiB×5 个文件）

## 日志存储路径

- Docker 运行时：`/var/lib/docker/containers/$CONTAINER_ID/$CONTAINER_ID-json.log`，并在`/var/log/pods`和`/var/log/containers`建立软链接
- Containerd 运行时：日志由 kubelet 直接落盘，保存至`/var/log/pods/<pod_uid>/<container_name>/0.log`等路径

## 容器日志生命周期

- 容器删除时，关联日志文件**同步删除**，kubelet 不会保留已删除容器的日志
- 日志轮转仅基于文件大小，**无默认时间限制**，高频日志可能数小时内就完成轮转覆盖，低频日志可能保存数天甚至更久

# 日志保存时长的影响因素
## 容器运行时差异
- Docker：日志驱动（默认 json-file）独立配置，可能覆盖 kubelet 限制（生产环境不推荐）
- Containerd：日志管理完全由 kubelet 控制，配置更统一稳定

## 日志输出方式
|输出方式|保存机制|保存时长特点|
|---|---|---|
|标准输出 (stdout)|kubelet 统一管控|遵循默认 50MiB 限制，容器删除即删除|
|容器内文件|应用 /sidecar（如 filebeat）自行管理|无 kubelet 限制，易导致磁盘溢出。需结合程序自行切割日志文件大小以及保留文件的份数。|
|HostPath 挂载|宿主机文件系统|脱离容器生命周期，需手动清理 / 配置 logrotate|
`logrotate` 是 Linux/Unix 系统自带的**标准日志管理工具**，核心作用是自动管理日志文件，解决日志文件无限膨胀、占用磁盘空间、难以维护的问题。

## 自定义kubelet配置
1. 通过修改 kubelet 配置可调整默认限制，适用于需要保留更多本地日志的场景。修改 kubelet 配置文件，如：
   
```yaml
containerLogMaxSize: "20Mi"  # 单个文件最大20MiB  
containerLogMaxFiles: 10     # 最多保留10个文件
```

1. 重启 kubelet 服务使配置生效：`systemctl restart kubelet`

注意：此配置仅影响**新创建**的容器，不作用于存量容器

# 持久化日志保存
节点本地日志仅作临时缓存，生产环境必须部署**集中式日志系统**实现长期保存，常见方案及保存策略如下：
- ELK/EFK等开源方案
- datadog等商业平台
- 云厂商托管等

