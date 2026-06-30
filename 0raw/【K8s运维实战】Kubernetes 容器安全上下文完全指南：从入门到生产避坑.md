---
title: "【K8s运维实战】Kubernetes 容器安全上下文完全指南：从入门到生产避坑"
source: "https://mp.weixin.qq.com/s/rUX0GmNlkEVbc-X6rZJ65A"
author:
  - "[[老郭a]]"
published:
created: 2026-06-30
description: "先说点实在的不知道你有没有遇到过这种情况——明明镜像里指定了非 root 用户，结果容器跑起来还是 uid=0"
tags:
  - "clippings"
---
老郭a 老郭a *2026年6月29日 08:41*

## 先说点实在的

不知道你有没有遇到过这种情况——明明镜像里指定了非 root 用户，结果容器跑起来还是 uid=0；或者某天安全扫描一跑，整个集群全是“容器以 root 运行”的高危告警。我接手过一个线上集群，30 多个微服务，没有一个配置了 `securityContext` ，所有容器全跑在 root 下。更离谱的是有个业务 Pod 开了特权模式，就因为开发说“这样省事”。直到某次节点被入侵，幸好发现得早，不然后果不堪设想。

**Security Context 不是可选项，是生产环境必选项。** 这篇文章我把这些年的踩坑经验整理出来，希望能帮你少走弯路。

## Security Context 到底是什么

Security Context 是 Kubernetes 用来定义 Pod 或容器 **运行时权限与访问控制** 的一组配置。它本质上是在告诉容器运行时：“这个进程该以什么身份、有什么权限、能调用哪些内核功能。”

它控制的东西主要包括：

- **运行身份：以哪个 UID/GID 运行**
- **Linux 权能（Capabilities）：授予部分 root 特权而非全部**
- **特权模式：是否以特权模式运行**
- **文件系统：根文件系统是否只读**
- **特权提升：是否允许获取比父进程更高的权限**
- **SELinux/AppArmor/seccomp：更细粒度的安全策略**

⚠️ **重要** ：Security Context 的这些设置最终是由 **容器运行时** （如 containerd、CRI-O）翻译成内核级别的指令来执行的。Kubernetes 本身不直接 enforce 这些设置，只是把它们传递给运行时。

## 配置格式：放在 Pod 还是 Container

`securityContext` 可以放在两个层级：

1. **Pod 级（ `spec.securityContext` ）：应用到 Pod 内 **所有** 容器**
2. **容器级（ `spec.containers[].securityContext` ）：仅应用到 **单个** 容器**

**优先级规则** ：如果 Pod 级和容器级都设置了相同字段， **容器级的配置会覆盖 Pod 级** 的。

我的建议是： **把通用的身份配置（runAsUser、runAsGroup、fsGroup）放在 Pod 级，把容器特有的配置（capabilities、allowPrivilegeEscalation）放在容器级。**

## 管理容器的运行身份（UID/GID）

这是生产环境 **最基础也最容易出错** 的部分。

### 核心字段

| 字段 | 层级 | 作用 |
| --- | --- | --- |
| `runAsUser` | Pod/Container | 指定运行进程的 UID |
| `runAsGroup` | Pod/Container | 指定主组 GID |
| `runAsNonRoot` | Pod/Container | 强制要求以非 root 运行 |
| `fsGroup` | Pod | 挂载卷的所属组 GID |
| `fsGroupChangePolicy` | Pod | 控制卷权限变更的时机 |
| `supplementalGroups` | Pod | 附加组列表 |

### 最小可行配置

```makefile
apiVersion: v1kind: Podmetadata:  name: security-context-demospec:  securityContext:                      # Pod 级配置    runAsUser: 1000                     # 所有容器以 uid 1000 运行    runAsGroup: 3000                    # 主组为 3000    fsGroup: 2000                       # 卷的所属组为 2000    supplementalGroups: [4000]          # 附加组  containers:  - name: sec-ctx-demo    image: busybox:1.36.1               # 固定具体版本，避免 latest 漂移    command: ["sh", "-c", "sleep 1h"]    volumeMounts:    - name: sec-ctx-vol      mountPath: /data/demo    securityContext:                    # 容器级配置（覆盖 Pod 级）      allowPrivilegeEscalation: false  volumes:  - name: sec-ctx-vol    emptyDir: {}
```

这个示例参考了 Kubernetes 官方文档的配置结构。配置中 `runAsUser` 指定所有容器以 UID 1000 运行， `runAsGroup` 指定主组为 3000。

### 几个关键细节

**1\. runAsNonRoot 的验证逻辑**

设置 `runAsNonRoot: true` 后，Kubelet 会在容器启动时 **验证** 容器是否以非 root 用户运行（UID!= 0）。如果容器最终以 root 运行，Pod 会启动失败。

```apache
securityContext:  runAsNonRoot: true  runAsUser: 1000    # 必须显式指定非 0 的 UID
```

**一个常见的组合错误** ：如果显式设置 `runAsUser: 0` 但同时设置了 `runAsNonRoot: true` ，Pod 会直接启动失败——Kubelet 会检测到 UID=0 并报错，这两个配置是互斥的。

**2\. runAsGroup 未设置时的行为**

`runAsGroup` 的官方定义是：“The GID to run the entrypoint of the container process. Uses runtime default if unset.”如果设置了 `runAsUser` 但 **没有设置** `runAsGroup` ，容器的主组 ID **由容器运行时决定** 。

具体来说，容器运行时会 **优先查** `/etc/passwd` 中该 UID 对应的主组；如果镜像中没有该 UID 的记录，则回退到容器运行时的默认值（通常是 `0` ，即 root 组）。这是容器运行时的行为，非 Kubernetes 直接控制。

**3\. fsGroup 的行为与 fsGroupChangePolicy**

当设置 `fsGroup` 时，Kubelet 会 **递归地** 将 Pod 挂载的 **支持 fsGroup 的卷类型** 的 ownership 改为 `fsGroup` 指定的 GID。

`fsGroupChangePolicy` 控制卷权限变更的策略，有效值为 `OnRootMismatch` 和 `Always` ：

- `Always` **（默认） ：每次 Pod 启动都递归修改卷权限**
- `OnRootMismatch：仅在卷根目录的权限与预期不匹配时才修改`

注意： `fsGroupChangePolicy` 字段 **仅适用于支持 fsGroup 的卷类型，对** `secret` **、** `configMap` **和** `emptyDir` **等临时卷类型没有影响** 。 `emptyDir` 在首次挂载时会应用 `fsGroup` 的权限设置，但由于其在 Pod 生命周期内通常只挂载一次， `fsGroupChangePolicy` 的“每次 Pod 启动时检查并修改”这一行为对它意义不大。

生产环境建议用 `OnRootMismatch` ，可以减少不必要的递归操作，提升启动速度。

**4\. supplementalGroups 的隐式合并风险**

默认情况下，Kubernetes 会把 Pod 中指定的 `supplementalGroups` 与容器镜像中 `/etc/group` 文件里定义的、属于该容器主用户的组 **合并** 到一起。这意味着即使你在 Pod 清单里只配了 `supplementalGroups: [4000]` ，容器里实际生效的附加组可能还包括镜像中定义的 50000、60000 等。

**这是一个安全隐患** ——这些隐式 GID 在 Pod 清单中看不到，无法被策略引擎检测或验证。

从 **Kubernetes v1.35** 开始， `supplementalGroupsPolicy` 字段正式 GA（从 v1.31 Alpha → v1.33 Beta → v1.35 GA）。该字段有两个取值：

- `Merge` **（默认）：合并 Pod 中指定的组与镜像 `/etc/group` 中定义的组**
- ``Strict：仅使用 Pod 中显式指定的 `fsGroup`、`supplementalGroups` 和 `runAsGroup`，忽略镜像中的组定义``

如果你在用 v1.35+，建议显式设置 `supplementalGroupsPolicy: Strict` 来消除这个安全隐患。

⚠️ **升级提醒** ：v1.33 beta 阶段引入了一些 **行为变更（breaking change）** ——kubelet 会拒绝在无法确保指定策略的节点上运行 Pod。如果你计划从 v1.32 或更早版本升级到 v1.35，请提前查阅官方升级注意事项。

**5\. runAsUser 与镜像 USER 指令的交互**

在 Pod 清单中设置的 `runAsUser` 和 `runAsGroup` **优先于** 容器镜像中的 `USER` 指令。这意味着即使 Dockerfile 里写了 `USER 1000:1000` ，Pod 的 `securityContext` 仍然可以覆盖它。

但有一个坑：如果镜像中没有 `runAsUser` 指定的 UID 对应的用户（ `/etc/passwd` 中没有记录），容器 **仍然可以运行** ——只是 `id` 命令可能显示 `uid=1000 gid=0` （如果没设 `runAsGroup` ）。这对于某些依赖用户名解析的应用可能会造成问题。

## 管理容器的内核功能（Capabilities）

Linux Capabilities 是 Security Context 里 **最精细、最灵活** 的控制手段。它把 root 的超级权限拆分成了 30 多个独立单元，你可以按需授予。

### 配置格式

```cs
securityContext:  capabilities:    drop: ["ALL"]                        # 先丢弃所有    add: ["NET_BIND_SERVICE"]            # 再按需添加
```

### 生产环境推荐配置

我一般会这样配：

```cs
securityContext:  capabilities:    drop:    - ALL                                # 丢弃所有 capabilities    add:    - NET_BIND_SERVICE                   # 只保留绑定 1024 以下端口的能力  allowPrivilegeEscalation: false  readOnlyRootFilesystem: true
```

这个组合拳的效果是：容器除了能绑定特权端口外，几乎没有任何额外的系统权限。如果应用不需要绑定 80/443 端口，连 `NET_BIND_SERVICE` 都不用加。

💡 **彩蛋** ：有些安全基准（如 CIS Benchmarks）建议“drop all capabilities then add back needed ones”。但实际生产中你可能需要保留 `SETPCAP` 或 `CHOWN` ，取决于应用的具体行为。建议先在测试环境验证，我的经验是大部分业务应用只需要 `NET_BIND_SERVICE` 就够用了。

## 特权模式容器：能不用就别用

`privileged: true` 是 Security Context 里 **最危险** 的配置，没有之一。

### 它到底做了什么

特权模式容器 **几乎拥有宿主机 root 的所有权限** ，可以：

- 访问宿主机所有设备
- 加载/卸载内核模块
- 修改宿主机网络配置
- **绕过容器的大部分隔离机制**

### 一个容易被忽略的限制

如果你给容器设置了 `privileged: true` ， **seccomp 配置文件将无法生效** 。特权容器始终以 `Unconfined` 运行，这意味着你失去了系统调用层面的防护。

### 另一个细节：allowPrivilegeEscalation

`allowPrivilegeEscalation` 控制进程能否获得比父进程更高的权限，它直接控制 `no_new_privs` 标志是否被设置。设置 `allowPrivilegeEscalation: false` 会阻止进程通过 `execve()` 获得新的权限（如 setuid 位），这是它安全价值的核心所在。

当容器以 **特权模式运行** 或具有 `CAP_SYS_ADMIN` 权能时，该字段 **始终为 true** 。也就是说，你即使显式设置了 `allowPrivilegeEscalation: false` ，只要容器是特权模式或拥有 `CAP_SYS_ADMIN` ，它仍然会被覆盖为 true。

需要留意的是，某些场景下容器可能会 **隐式获得** `CAP_SYS_ADMIN` ——比如挂载了 hostPath 或某些 CSI 卷时，容器运行时可能会赋予这个权能。这会导致你明明设置了 `allowPrivilegeEscalation: false` ，但它实际上不生效。遇到这种情况，需要检查卷挂载配置是否引入了额外的权能。

### 我的建议

- **默认禁止：在生产集群中，通过 Pod 安全标准（Pod Security Standards）的 `Baseline` 或 `Restricted` 策略禁止特权容器**
- **如果非用不可：评估是否可以用 `capabilities` 替代。比如需要操作网络时，可能只需要 `CAP_NET_ADMIN` 而不是整个特权模式**
- **绝对不用的场景：任何面向公网的服务**

## 在 Pod 上使用 sysctl 的最佳实践

sysctl 是 Linux 内核参数的配置接口。在 Kubernetes 中，你可以通过 `securityContext.sysctls` 来设置。

### 配置格式

```makefile
apiVersion: v1kind: Podmetadata:  name: sysctl-demospec:  securityContext:    sysctls:    - name: kernel.shm_rmid_forced      value: "1"    - name: net.core.somaxconn      value: "1024"    - name: kernel.msgmax      value: "65536"
```

### 安全 sysctl vs 不安全 sysctl

Kubernetes 把 sysctl 分为两类：

| 类型 | 说明 | 示例 |
| --- | --- | --- |
| **安全 sysctl** | 默认允许，无需额外配置 | `kernel.shm_rmid_forced` 、 `net.ipv4.ip_local_port_range` |
| **不安全 sysctl** | 默认禁止，需集群管理员 **在节点上单独启用** | `net.core.somaxconn` 、 `kernel.msgmax` 、 `kernel.msgmnb` |

**安全 sysctl 的完整列表** （Kubernetes v1.32，含内核版本要求）：

| sysctl | 引入版本 | 内核版本要求 |
| --- | --- | --- |
| `kernel.shm_rmid_forced` | \- | \- |
| `net.ipv4.ip_local_port_range` | \- | \- |
| `net.ipv4.tcp_syncookies` | \- | 自内核 4.6+ 支持命名空间作用域 |
| `net.ipv4.ping_group_range` | v1.18+ | \- |
| `net.ipv4.ip_unprivileged_port_start` | v1.22+ | \- |
| `net.ipv4.ip_local_reserved_ports` | v1.27+ | 内核 3.16+ |
| `net.ipv4.tcp_keepalive_time` | 自 v1.29 起加入安全列表 | 内核 4.5+ |
| `net.ipv4.tcp_fin_timeout` | 自 v1.29 起加入安全列表 | 内核 4.6+ |
| `net.ipv4.tcp_keepalive_intvl` | 自 v1.29 起加入安全列表 | 内核 4.5+ |
| `net.ipv4.tcp_keepalive_probes` | 自 v1.29 起加入安全列表 | 内核 4.5+ |
| `net.ipv4.tcp_rmem` | v1.32+ | 内核 4.15+ |
| `net.ipv4.tcp_wmem` | v1.32+ | 内核 4.15+ |
| `net.ipv4.vs.conn_reuse_mode` | \- | 内核 4.1+（用于 IPVS 代理模式） |

**注意** ： `net.ipv4.tcp_rmem` 和 `net.ipv4.tcp_wmem` 是在 **v1.32 才加入** 安全列表的。如果你的集群版本低于 v1.32，这两个参数可能仍被视为不安全 sysctl。

完整列表请以 Kubernetes 官方文档 为准。

### 启用不安全 sysctl 的步骤

1. **节点配置：集群管理员需要在 kubelet 的 `--allowed-unsafe-sysctls` 参数中指定允许的列表**
2. **Pod 配置：在 Pod 的 `securityContext.sysctls` 中设置**
3. **（OpenShift 环境）：通过 Security Context Constraints 的 `allowedUnsafeSysctls` 字段控制**

### 最佳实践

1. **优先使用安全 sysctl：能用安全的就别碰不安全的**
2. **不安全 sysctl 需要审批流程：建议建立变更审批机制**
3. **测试环境先行：sysctl 改错了可能导致节点不稳定，先在测试环境验证**
4. **明确标注：在 Pod 配置中加注释说明为什么要改这个参数**

## 配置 seccomp 配置文件

seccomp（Secure Computing Mode）是 Linux 内核的特性，用于限制进程能够发起的系统调用。Kubernetes v1.19 开始，seccomp 配置正式 GA。

### 配置方式

seccomp 配置文件通过 `securityContext.seccompProfile` 字段设置：

```makefile
apiVersion: v1kind: Podmetadata:  name: seccomp-demospec:  securityContext:    seccompProfile:      type: RuntimeDefault          # Pod 级默认配置  containers:  - name: nginx    image: nginx:latest    securityContext:      seccompProfile:        type: Localhost             # 容器级覆盖，使用本地配置文件        localhostProfile: my-profile.json
```

### 三种 Profile 类型

| 类型 | 说明 |
| --- | --- |
| `Unconfined` | 不应用任何 seccomp 限制 |
| `RuntimeDefault` | 使用容器运行时定义的默认 seccomp 配置文件 |
| `Localhost` | 使用节点上 kubelet seccomp 根目录下的自定义配置文件 |

### 优先级与继承规则

- 如果容器没有显式设置 `securityContext.seccompProfile` ，会 **继承 Pod 级** 的配置
- 如果 Pod 级和容器级都设置了， **容器级覆盖 Pod 级** ——这与 securityContext 其他字段的优先级规则一致

### Localhost 配置文件的存放路径

`localhostProfile` 指定的文件必须预先存放在节点上。在 Linux 系统中， **默认** 路径是 `/var/lib/kubelet/seccomp/` 。例如配置 `localhostProfile: my-profile.json` ，则文件需要放在 `/var/lib/kubelet/seccomp/my-profile.json` 。

如果配置文件不存在，容器创建会失败，报错类似：

`Error: setup seccomp: unable to load local profile "/var/lib/kubelet/seccomp/nginx-1.25.3.json": open /var/lib/kubelet/seccomp/nginx-1.25.3.json: no such file or directory`

具体路径可能因容器运行时（containerd vs CRI-O）和 kubelet 配置（ `--seccomp-profile-root` 参数）而异。

### 与特权模式的关系

官方文档明确指出：

“It is not possible to apply a seccomp profile to a Pod or container running with privileged: true set in the container's securityContext.”

**意思是** ：只要容器级设置了 `privileged: true` ，seccomp 配置就不会生效，容器会以 `Unconfined` 运行。这个限制无法绕过。

### 生产建议

- 大部分业务容器直接用 `RuntimeDefault` 就够了
- 只有对安全要求极高的场景才考虑自定义 `Localhost` 配置文件
- **不要同时使用** `privileged: true` **和 seccomp**
	——它们互斥

## 验证你的配置是否生效

### 1\. 检查 Pod 中的进程身份

```bash
# 进入容器kubectl exec -it security-context-demo -- sh# 查看当前用户id# 预期输出应显示 uid=1000，gid=3000
```

`groups` 部分的实际输出可能因 `supplementalGroups` 和镜像中 `/etc/group` 的合并而有所不同。如果设置了 `supplementalGroupsPolicy: Strict` ，则只会显示 Pod 中显式指定的组。

### 2\. 检查 capabilities

```bash
# 查看进程的 capabilities（位图形式）kubectl exec -it security-context-demo -- cat /proc/1/status | grep Cap
```

`CapEff` 那行会显示当前生效的 capabilities 位图。如果 drop 了 ALL，你应该看到很小的数值。如果想看更直观的输出，可以用：

```bash
kubectl exec -it security-context-demo -- capsh --print
```

### 3\. 检查 sysctl 是否生效

```bash
kubectl exec -it sysctl-demo -- cat /proc/sys/net/core/somaxconn# 预期输出：1024
```

### 4\. 检查 seccomp 是否生效

```bash
kubectl exec -it seccomp-demo -- grep Seccomp /proc/self/status# 预期输出：Seccomp: 2（2 表示启用）
```

## 常见问题与真实报错

### Q1: 设置了 runAsNonRoot: true 但容器仍以 root 运行

**现象** ：Pod 启动失败，事件中有类似报错：

`Error: container has runAsNonRoot and image will run as root`

**原因** ：容器镜像默认以 root 用户运行（大多数基础镜像都是这样），而 `runAsNonRoot: true` 要求容器必须以非 root 运行。

**解决** ：

- 方案一：设置 `runAsUser: 1000` 显式指定非 root UID
- 方案二：修改 Dockerfile，用 `USER 1000:1000` 指定非 root 用户

### Q2: 设置了 runAsUser 但容器写不了文件

**现象** ：应用报 `Permission denied` 错误。

**原因** ： `runAsUser` 改了进程的 UID，但挂载的卷可能还是 root 所有。

**解决** ：在 Pod 级设置 `fsGroup` ，Kubelet 会自动将卷的 ownership 改为该 GID。

```apache
spec:  securityContext:    runAsUser: 1000    fsGroup: 2000   # 关键：让卷可写
```

### Q3: 使用不安全 sysctl 时 Pod 无法启动

**现象** ：Pod 一直处于 `Pending` 状态，事件显示：

`forbidden sysctl: "net.core.somaxconn" not allowed in the pod's security context`

**原因** ：不安全 sysctl 需要在节点上显式启用。

**解决** ：

1. 确认该 sysctl 是否确实需要（很多场景其实不需要调）
2. 联系集群管理员在 kubelet 的 `--allowed-unsafe-sysctls` 中添加
3. 或在 Pod 安全策略/SCC 中配置 `allowedUnsafeSysctls`

### Q4: 容器需要绑定 80 端口但报错

**现象** ：应用启动失败，报 `bind: permission denied` 。

**原因** ：默认情况下容器没有 `NET_BIND_SERVICE` capability，无法绑定 1024 以下的特权端口。

**解决** ：添加 `NET_BIND_SERVICE` capability：

```sql
securityContext:  capabilities:    drop: ["ALL"]    add: ["NET_BIND_SERVICE"]
```

### Q5: readOnlyRootFilesystem: true 导致应用崩溃

**现象** ：设置了 `readOnlyRootFilesystem: true` 后，应用启动失败，报类似：

`mkdir: cannot create directory '/tmp/cache': Read-only file system`

**原因** ：应用的根文件系统被挂载为只读，但应用尝试写入 `/tmp` 或其他目录。

**解决** ：将需要写入的目录通过 `emptyDir` 卷单独挂载出来：

```bash
spec:  containers:  - name: app    image: myapp:latest    securityContext:      readOnlyRootFilesystem: true    volumeMounts:    - name: tmp      mountPath: /tmp  volumes:  - name: tmp    emptyDir: {}
```

### Q6: 容器有特权模式但 seccomp 不生效

官方文档明确指出：

“It is not possible to apply a seccomp profile to a Pod or container running with privileged: true set in the container's securityContext.”

**原因** ：这是 Kubernetes 的设计限制——特权模式会绕过 seccomp 的限制。

**解决** ：不要同时使用特权模式和 seccomp。如果确实需要特权，考虑是否可以用 capabilities 替代。

## Pod 安全标准与 Security Context 的对应关系

Kubernetes Pod 安全标准定义了三个策略级别：

| 策略 | 说明 | 对 Security Context 的要求 |
| --- | --- | --- |
| **Privileged** | 完全不受限 | 无任何限制 |
| **Baseline** | 防止已知的特权提升，面向非关键应用 | 禁止特权容器、禁止 host 命名空间、限制 capabilities |
| **Restricted** | 遵循 Pod 加固最佳实践，面向安全关键应用 | 在 Baseline 基础上额外要求： `runAsNonRoot: true` 、 `seccompProfile` 必须为 `RuntimeDefault` 或 `Localhost` |

### Baseline 策略对 Capabilities 的限制

Baseline 策略下，允许添加的 capabilities 仅限于以下列表：

`AUDIT_WRITE` 、 `CHOWN` 、 `DAC_OVERRIDE` 、 `FOWNER` 、 `FSETID` 、 `KILL` 、 `MKNOD` 、 `NET_BIND_SERVICE` 、 `SETFCAP` 、 `SETGID` 、 `SETPCAP` 、 `SETUID` 、 `SYS_CHROOT`

Restricted 策略下只允许 `NET_BIND_SERVICE` （或空列表）。

如果你在 Baseline 策略下试图添加 `CAP_SYS_ADMIN` 等不在列表中的 capability，Pod 会被拒绝。

这个列表 **可能会随 Kubernetes 版本变化** ，建议以官方文档的最新版本为准。

### 生产环境建议

- **开发/测试环境：可以用 `Baseline` ，允许一定灵活性**
- **生产环境：强烈建议用 `Restricted` ，配合合理的 securityContext 配置**
- **系统级组件（如网络插件、监控 agent）：可能需要 `Privileged` ，但应尽量缩小范围**

## 核心要点总结

1. **Security Context 是生产环境必选项，不是可选项。至少要把 `runAsNonRoot: true` 和 `allowPrivilegeEscalation: false` 配上。**
2. **容器级配置覆盖 Pod 级，利用这个特性可以做精细控制——通用身份配置放 Pod 级，特殊权限放容器级。**
3. **特权模式是万恶之源，能不用就不用。99% 的场景可以用 capabilities 替代。而且特权模式会让 seccomp 失效。**
4. **sysctl 用之前先确认是安全的还是不安全的，不安全的需要集群管理员在节点上单独启用。安全 sysctl 列表中的部分参数有内核版本要求。**
5. **readOnlyRootFilesystem 配了记得挂载可写目录，不然应用会因无法写临时文件而崩溃。**
6. **seccomp 用 RuntimeDefault 就够了，除非有特殊需求。别和特权模式一起用。**
7. **Pod 安全标准帮你兜底，生产环境用 Restricted 策略，能自动拦截大部分不安全配置。**
8. **v1.35+ 可以用** ``supplementalGroupsPolicy: Strict来消除镜像 `/etc/group` 带来的隐式组安全隐患。升级前请注意 v1.33 引入的行为变更。``
9. **本文档仅适用于 Linux 容器—— `fsGroup` 、 `runAsUser` 、 `runAsGroup` 等字段在 Windows 节点上不支持。**

---

如果觉得有用，欢迎分享给更多同行。有问题欢迎在评论区交流——你遇到过哪些 Security Context 的坑？说来听听，说不定我踩过😂

**微信扫一扫赞赏作者**

kubernetes实战 · 目录

作者提示: 个人观点，仅供参考