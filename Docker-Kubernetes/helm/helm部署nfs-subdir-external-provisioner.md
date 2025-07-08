# helm部署nfs provisioner

- github release: https://github.com/kubernetes-sigs/nfs-subdir-external-provisioner
- artifacthub: https://artifacthub.io/packages/helm/nfs-subdir-external-provisioner/nfs-subdir-external-provisioner

## NFS 服务器部署

- 安装 NFS 服务端软件包

```shell
yum install nfs-utils
```

- 创建共享数据目录

执行以下命令创建共享[数据存储](https://cloud.tencent.com/product/cdcs?from_column=20065&from=20065)目录，本文以 `/data/k8s` 为例，请根据实际情况修改。

```shell
mkdir -p /data/k8s
chown nfsnobody:nfsnobody /data/k8s
# 如果没有nfsnobody用户，可以用nobody用户
```

- 编辑服务配置文件

配置 NFS 服务器数据导出目录及访问 NFS 服务器的客户端机器权限。

编辑配置文件 `vi /etc/exports`，添加如下内容

```shell
/data/k8s 192.168.9.0/24(rw,sync,all_squash,anonuid=65534,anongid=65534,no_subtree_check)
```

> **说明：**
>
> - 192.168.9.0/24：可以访问 NFS 存储的客户端 IP 地址
> - rw：读写操作，客户端机器拥有对卷的读写权限。 
> - sync：内存数据实时写入磁盘，性能会有所限制 
> - all_squash：NFS 客户端上的所有用户在使用共享目录时都会被转换为一个普通用户的权限 
> - anonuid：转换后的用户权限 ID，对应的操作系统的 nfsnobody 用户 
> - anongid：转换后的组权限 ID，对应的操作系统的 nfsnobody 组 
> - no_subtree_check：不检查客户端请求的子目录是否在共享目录的子树范围内，也就是说即使输出目录是一个子目录，NFS 服务器也不检查其父目录的权限，这样可以提高效率。

- 启动服务并设置开机自启

```shell
systemctl enable nfs-server --now
```

- 导出目录

```shell
exportfs -v
```

## 客户端挂载测试

找一台额外的机器作为客户端验证测试

- 创建测试挂载点

```shell
mkdir /mnt/nfs
```

- 安装 NFS 软件包（一定要安装，否则无法识别 nfs 类型的存储）

```shell
yum install nfs-utils
```

- 挂载 NFS 共享目录

```shell
mount -t nfs 192.168.9.81:/data/k8s /mnt/nfs/
```

- 增删改查测试

```shell
# 创建测试目录、创建测试文件、测试文件写入内容、查看写入目录和文件权限、删除目录和文件
cd /mnt/nfs/
mkdir nfs-test
touch nfs-test.txt
echo "nfs-test" > nfs-test.txt
ll
total 4
drwxr-xr-x 2 nfsnobody nfsnobody 6 Nov 29 16:56 nfs-test
-rw-r--r-- 1 nfsnobody nfsnobody 9 Nov 29 16:56 nfs-test.txt
rmdir nfs-test
rm nfs-test.txt
```

## 安装NFS Provisioner

- 想要 Kubernetes 支持 NFS 存储，我们需要安装 **nfs-subdir-external-provisioner** ，它是一个存储资源自动调配器，它可将现有的 NFS 服务器通过持久卷声明来支持 Kubernetes 持久卷的动态分配。该组件是对 Kubernetes NFS-Client Provisioner 的扩展， **nfs-client-provisioner** 已经不提供更新，而且 [Github 仓库](https://cloud.tencent.com/developer/tools/blog-entry?target=https%3A%2F%2Fgithub.com%2Fkubernetes-retired%2Fexternal-storage%2Ftree%2Fmaster%2Fnfs-client&source=article&objectId=2365976) 也已经处于归档状态，已经迁移到 [nfs-subdir-external-provisioner](https://cloud.tencent.com/developer/tools/blog-entry?target=https%3A%2F%2Fgithub.com%2Fkubernetes-sigs%2Fnfs-subdir-external-provisioner&source=article&objectId=2365976) 的仓库。

- 官方提供的安装方式有三种：

  - [With Helm](https://cloud.tencent.com/developer/tools/blog-entry?target=https%3A%2F%2Fgithub.com%2Fkubernetes-sigs%2Fnfs-subdir-external-provisioner%23with-helm&source=article&objectId=2365976)

  - [With Kustomize](https://cloud.tencent.com/developer/tools/blog-entry?target=https%3A%2F%2Fgithub.com%2Fkubernetes-sigs%2Fnfs-subdir-external-provisioner%23with-kustomize&source=article&objectId=2365976)

  - [Manually](https://cloud.tencent.com/developer/tools/blog-entry?target=https%3A%2F%2Fgithub.com%2Fkubernetes-sigs%2Fnfs-subdir-external-provisioner%23manually&source=article&objectId=2365976)

- 使用 Helm 的方式比较简单，也是现在官方推荐的、使用率最高的方式，本文仅实战演示 Helm 部署方式，其他方式请参考官方文档。

- 集群节点安装 NFS Client

  所有 Kubernetes 集群节点需要提前安装 nfs-utils，否则在部署过程中会报错.

```sh
yum install nfs-utils
```

- 添加 Helm 源

```sh
helm repo add nfs-subdir-external-provisioner https://kubernetes-sigs.github.io/nfs-subdir-external-provisioner
```

- 创建 NameSpace

**可选配置，主要是方便资源管理**。

```shell
kubectl create ns nfs-system
```

### Option1:命令行快速安装NFS Provisioner

**（首选方案，使用命令行设置变量参数）**

```shell
helm install nfs-subdir-external-provisioner nfs-subdir-external-provisioner/nfs-subdir-external-provisioner --set storageClass.name=nfs-sc --set nfs.server=192.168.9.81 --set nfs.path=/data/k8s -n nfs-system
```

> **说明：**
>
> --set storageClass.name=nfs-sc：指定 storageClass 的名字 
>
> --set nfs.server=192.168.9.81：指定 NFS 服务器的地址 
>
> --set nfs.path=/data/k8s：指定 NFS 导出的共享数据目录 
>
> --set storageClass.defaultClass=true：指定为默认的 sc，**本示例没使用** 
>
> -n nfs-system：指定命名空间

### Option2:自定义values安装 NFS Provisioner

有更多定制化需求时可以选择自定义 `values.yaml` 的方式进行安装，实际使用中与命令行安装 NFS Subdir External Provisioner 的方式**二选一**即可。

```shell
#下载解压Charts
helm pull nfs-subdir-external-provisioner/nfs-subdir-external-provisioner
tar xvf nfs-subdir-external-provisioner-4.0.18.tgz
```

```yaml
#编辑values.yaml
replicaCount: 1
strategyType: Recreate
image:
  repository: registry.k8s.io/sig-storage/nfs-subdir-external-provisioner
  tag: v4.0.2
  pullPolicy: IfNotPresent
imagePullSecrets: []
nfs:
  server:
  path: /nfs-storage
  mountOptions:
  volumeName: nfs-subdir-external-provisioner-root
  reclaimPolicy: Retain
storageClass:
  create: true
  defaultClass: false
  name: nfs-client
  allowVolumeExpansion: true
  reclaimPolicy: Delete
  archiveOnDelete: true
  onDelete:
  pathPattern:
  accessModes: ReadWriteOnce
  volumeBindingMode: Immediate
  annotations: {}
leaderElection:
  enabled: true
rbac:
  create: true
podSecurityPolicy:
  enabled: false
podAnnotations: {}
podSecurityContext: {}
securityContext: {}
serviceAccount:
  create: true
  annotations: {}
  name:
resources: {}
nodeSelector: {}
tolerations: []
affinity: {}
labels: {}
podDisruptionBudget:
  enabled: false
  maxUnavailable: 1
```

- 根据实际情况修改 `nfs-subdir-external-provisioner/values.yaml`

```yaml
replicaCount: 2

nfs:
  server: 172.16.183.100
  path: /data/nfs_pro/

storageClass:
  create: true
  defaultClass: true
  name: sc-nfs

resources:
  limits:
   cpu: 100m
   memory: 128Mi
  requests:
   cpu: 100m
   memory: 128Mi

```

- 安装 NFS Subdir External Provisioner

```shell
helm install nfs-subdir-external-provisioner nfs-subdir-external-provisioner/nfs-subdir-external-provisioner -f nfs-subdir-external-provisioner/values.yaml -n nfs-system
```

## 验证pod挂载

~~~yaml
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: test-nfs-pvc
spec:
  storageClassName: nfs-sc
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 1Gi
---
kind: Pod
apiVersion: v1
metadata:
  name: test-nfs-pod
spec:
  containers:
  - name: test-nfs-pod
    image: busybox:stable
    command:
      - "/bin/sh"
    args:
      - "-c"
      - "touch /mnt/SUCCESS && sleep 3600"
    volumeMounts:
      - name: nfs-pvc
        mountPath: "/mnt"
  restartPolicy: "Never"
  volumes:
    - name: nfs-pvc
      persistentVolumeClaim:
        claimName: test-nfs-pvc
~~~

- 进入pod查看挂载情况

~~~sh
kubectl exec test-nfs-pod -n nfs-system -- df -h
~~~

> - 在输出结果中我们可以看到挂载的 NFS 存储的可用空间是大于PVC中分配的 1G。
> - 实际测试写入2G 的数据量，已经超过了我们创建的 PVC 1G 的限制。因此，要特别注意，使用 NFS 存储时无法限制存储使用量。 
> - **PV** 名称格式是 pv+随机字符串，所以，每次只要不删除 PVC，那么 Kubernetes 中 PV 与存储绑定将不会丢失，要是删除 PVC 也就意味着删除了绑定的文件夹，下次就算重新创建相同名称的 PVC，生成的文件夹名称也不会一致，因为 **PV** 名是随机生成的字符串，而文件夹命名又跟 PV 有关，所以删除 PVC 需谨慎。
> - Kubernetes 删除 PVC 后，在 NFS 存储层并没有立即删除 PVC 对应的数据目录及已有数据，而是将原来的数据目录改名为 **archived-+原有数据目录名称**的形式。
