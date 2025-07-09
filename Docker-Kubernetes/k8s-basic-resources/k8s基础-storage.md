# 持久化存储

## Volume

- 容器的生命周期可能很短，会被频繁地创建和销毁，保存在容器中的数据也会被清除。为了持久化保存容器的数据，kubernetes引入了**Volume**的概念。 

- Volume是Pod中能够被**多个容器访问**的共享目录，它被定义在Pod上，然后被一个Pod里的多个容器挂载到容器自己的具体的文件目录下，
- kubernetes通过Volume实现同一个Pod中不同容器之间的数据共享以及数据的持久化存储。Volume的生命容器不与Pod中单个容器的生命周期相关，当容器终止或者重启时，Volume中的数据也不会丢失。

kubernetes的Volume支持多种类型，比较常见的有下面几个：

- 简单存储：EmptyDir、HostPath、NFS（本地host存储和网络共享文件） 
  - emptydir、hostpath、nfs等都是在pod的yaml文件中的volume中声明。
- 高级存储：PV、PVC
  - pvc和pv都是要用单独的yaml文件做定义，然后在pod的yaml文件中申请使用pvc
- 配置存储：ConfigMap、Secret
  - 这两个也是在单独的yaml文件中声明，在pod的yaml文件中引用使用。

- 查看所有支持的存储种类

  ```bash
  kubectl explain pods.spec.volumes
  ```

## emptyDir

- 一个EmptyDir就是Host上的一个空目录。

- EmptyDir是在Pod被分配到Node时创建的，它的初始内容为空，并且无须指定宿主机上对应的目录文件，因为kubernetes会自动分配一个目录，当Pod销毁时， EmptyDir中的数据也会被**永久删除**。 EmptyDir用途如下：

  - 临时空间，例如应用程序运行时所需的**临时目录**，且无须永久保留

  - 一个容器需要从另一个容器中获取数据的目录（**多容器共享目录**）

  <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202311141720686.png" alt="image-20231114172051513" style="zoom:50%;" />

- 测试：


```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-emptydir
spec:
  containers:
  - name: container-emptydir
    image: nginx
    imagePullPolicy: IfNotPresent
    volumeMounts:
    - name: volume-cache
      mountPath: /cache
  volumes:
  - name: volume-cache
    emptyDir: {}
```

- 怎么查看emptyDir挂载到了宿主机的哪个目录


```bash
kubectl get po pod-emptydir -o yaml | grep uid
#拿到uid，去宿主机上看挂载路径：
tree /var/lib/kubelet/pods/e948ebb2-50f2-4884-a16c-2c0dd7b3f1de

/var/lib/kubelet/pods/e948ebb2-50f2-4884-a16c-2c0dd7b3f1de
├── containers
│   └── container-emptydir
│       └── a247ebdd
├── etc-hosts
├── plugins
│   └── kubernetes.io~empty-dir
│       ├── volume-cache
│       │   └── ready
│       └── wrapped_kube-api-access-kdqtk
│           └── ready
└── volumes
    ├── kubernetes.io~empty-dir
    │   └── volume-cache #这就是pod emptydir的挂载路径
    └── kubernetes.io~projected
        └── kube-api-access-kdqtk
            ├── ca.crt -> ..data/ca.crt
            ├── namespace -> ..data/namespace
            └── token -> ..data/token
            
cd /var/lib/kubelet/pods/e948ebb2-50f2-4884-a16c-2c0dd7b3f1de/volumes/kubernetes.io~empty-dir/volume-cache
```

## hoatPath

- hostPath Volume是指Pod挂载宿主机上的目录或文件。 

- hostPath Volume使得容器可以使用宿主机的文件系统进行存储，hostpath（宿主机路径）：节点级别的存储卷，pod被删除这个存储卷还是存在的.所以只要同一个pod被调度到同一个节点上来，对应的数据依然是存在的。

  <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202311141722615.png" alt="image-20231114172218560" style="zoom:50%;" />

- 测试

  ```yaml
  apiVersion: v1
  kind: Pod
  metadata:
    name: pod-hostpath
  spec:
    containers:
    - name: nginx-hostpath
      image: nginx
      imagePullPolicy: IfNotPresent
      volumeMounts:
      - name: volume-cache
        mountPath: /test-nginx
    - name: tomcat-hostpath
      image: tomcat
      imagePullPolicy: IfNotPresent
      volumeMounts:
      - name: volume-cache
        mountPath: /test-tomcat
    volumes:
    - name: volume-cache
      hostPath:
        path: /data
        type: DirectoryOrCreate #type的定义：https://kubernetes.io/docs/concepts/storage/volumes/#hostpath
  ```

> 注：
>
> - 根据官网说明：https://kubernetes.io/docs/concepts/storage/volumes/#hostpath，hostPath方式存在安全隐患，需要小心使用。更推荐使用local类型volume

## local

- 官网链接：
  - https://kubernetes.io/docs/concepts/storage/volumes/#local
  - https://kubernetes.io/docs/concepts/storage/storage-classes/#local
- 创建local需要的sc，这个sc的作用是确保pod在创建出来后才会绑定pv和pvc

~~~yaml
#创建local存储类
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: local-storage
provisioner: kubernetes.io/no-provisioner #不需要自动创建PV
volumeBindingMode: WaitForFirstConsumer   #等到Pod运行之后才让PVC和PV绑定。因为在使用Local Persistent Volume的时候PV和对应的PVC必须要跟随Pod在同一node下面，否则会调度失败。
parameters:
  archiveOnDelete: "true" #false删除数据，true存档，即重命名路径，命名格式为oldPath前面增加archived-的前缀
reclaimPolicy: Retain #回收策略是手动回收
allowVolumeExpansion: true
~~~

- 创建PV

~~~yaml
#创建local类型的PV
apiVersion: v1
kind: PersistentVolume
metadata:
  name: local-storage-pv
  labels:
    app: local-storage-pv
spec:
  capacity:
    storage: 1Gi
  accessModes:
  - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  #与local-storageClass.yaml中name标签相同，否则不需要等待pod调用，pv创建之后就可以直接bound
  storageClassName: local-storage
  #指定的PV对应的本地磁盘的路径
  local:
    path: /var/mnt/nfs
  #并且用nodeAffinity指定这个PV必须运行在某节点上
  nodeAffinity:
    required:
      nodeSelectorTerms:
        - matchExpressions:
            - key: kubernetes.io/hostname
              operator: In
              values:
                - worker1.ocp.example.com
~~~

- 创建pvc

~~~yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: local-storage-pvc
spec:
  selector:
    matchLabels:
      app: local-storage-pv
  accessModes:
    - ReadWriteOnce
  #这边的storageClassName要与static-pv.yaml匹配，同时selector标签匹配时，才能够与pv进行绑定
  storageClassName: local-storage
  resources:
    requests:
      storage: 1Gi
~~~

- 创建pod挂载pvc

~~~yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana-deployment
spec:
  replicas: 2
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      volumes:
      - name: local-storage-volume
        persistentVolumeClaim:
    #与static-pvc.yaml中metadata-name名称一致，表示pod调用该pvc
          claimName: local-storage-pvc  
      containers:
      - name: grafana-container
        image: quay.ocp.example.com/ocp4/custom/grafana:8.2.0
        resources:
          requests:
            memory: "64Mi"
            cpu: "250m"
          limits:
            memory: "128Mi"
            cpu: "500m"
        volumeMounts:
          - mountPath: /mnt/local
            name: local-storage-volume
~~~

> github上有一个开源工具：https://github.com/kubernetes-sigs/sig-storage-local-static-provisioner/blob/master/docs/getting-started.md。自动把指定的local路径做成PV。

## NFS

- HostPath可以解决数据持久化的问题，但是一旦Node节点故障了，Pod如果转移到了别的节点，又会出现问题了，此时需要准备单独的网络存储系统，比较常用的有NFS、CIFS。

- 搭建一台NFS服务器，然后将Pod中的存储直接连接到NFS系统上，无论Pod在节点上怎么转移，只要Node跟NFS的对接没问题，数据就可以成功访问

  <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202311141723114.png" alt="image-20231114172333052" style="zoom:50%;" />

- NFS的访问权限控制：NFS的用户认证和权限控制基于RPC，在nfs3和nfs4版本中，最常用的认证机制是AUTH_UNIX。客户端上的UID/GID通过RPC传递到服务端，然后对这些ID做权限校验，这就要求客户端、服务端的UID/GID必须相同。同时，NFS支持在其文件夹上通过以下配置来设置文件夹的访问权限：
  - all_squash: 将所有用户和组映射为匿名用户和组。默认为nfsnobody用户（UID：65534）、nfsnobody组（GID：65534），也可以通过anonuid、anongid指定。
  - no_all_squash：访问用户先与本机用户通过ID匹配，能匹配上就用；匹配不上再映射为匿名用户和组。这是默认选项。
  - root_squash: 将来访的root用户（UID=0）映射为匿名用户。这是默认行为。可以通过设置no_root_squash取消这种映射，保持root用户。

Lab

- 搭建NFS服务

  ```bash
  #在master-01上搭建NFS作为服务端
  yum install nfs-utils -y
  mkdir /data/volumes -pv
  systemctl start nfs
  #rockylinux中
  sudo systemctl start rpcbind
  sudo systemctl enable rpcbind
  sudo systemctl start nfs-server
  sudo systemctl enable nfs-server
  
  #配置nfs共享服务器上的/data/volumes目录
  vim /etc/exports
  /data/volumes *(rw,no_root_squash)
  #rw 该主机对该共享目录有读写权限
  # no_root_squash 登入 NFS 主机使用分享目录的使用者，如果是 root 的话，那么对于这个分享的目录来说，他就具有 root 的权限。根用户在 NFS 客户端上拥有和服务器上相同的权限。
  
  #使NFS配置生效
  exportfs -arv
  service nfs restart
  systemctl enable nfs && systemctl status nfs
  
  #测试挂载
  mkdir /nfs-test 
  mount 192.168.40.4:/data/volumes /nfs-test/
  df -h /nfs-test/
  #卸载挂载
  umount /nfs-test
  ```

- 测试pod挂载

  ```yaml
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: dep-nfs
  spec:
    replicas: 3
    selector:
      matchLabels:
        storage: nfs
    template: 
      metadata:
        labels:
          storage: nfs
      spec:
        containers:
        - name: test-nfs
          image: nginx
          imagePullPolicy: IfNotPresent
          ports:
          - containerPort: 80
            protocol: TCP
          volumeMounts:
          - name: test-nginx-volume
            mountPath: /usr/share/nginx/html
        volumes:
        - name: test-nginx-volume
          nfs:
            server: 192.168.40.4 
            path: /data/volumes
  ```

- nfs支持多个客户端挂载，可以创建多个pod，挂载同一个nfs服务器共享出来的目录；但是nfs如果宕机了，数据也就丢失了，所以需要使用分布式存储，常见的分布式存储有glusterfs和cephfs

## PV

- 使用NFS提供存储，此时就要求用户会搭建NFS系统，并且会在yaml配置nfs。由于kubernetes支持的存储系统有很多，要求客户全都掌握，显然不现实。站在用户的角度，只需要提出自己需要多少存储资源，并不管关心存储的底层实现。底层由专业人员来维护即可。

- 为了能够屏蔽底层存储实现的细节，方便用户使用， kubernetes引入**PV**和**PVC**两种资源对象。

  ![image-20231114172731738](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202311141727818.png)

- PersistentVolume（PV）是对底层的共享存储的一种抽象。由管理员配置或使用存储类动态配置，它与底层具体的共享存储技术有关，并通过**插件**完成与共享存储的对接。
- 它是集群中的资源，其生命周期独立于使用PV的任何单个pod。PV通过yaml文件部署；PV是node级别的，不能配namespace。
- PV供应方式：
  - 静态：集群管理员创建了许多PV。它们包含可供群集用户使用的实际存储的详细信息。它们存在于Kubernetes API中，可供使用。
  - 动态：当管理员创建的静态PV都不匹配用户的PersistentVolumeClaim时，群集可能会尝试为PVC专门动态配置卷。此配置基于StorageClasses，PVC必须请求存储类，管理员必须创建并配置该类，以便进行动态配置。

## PVC

- PersistentVolumeClaim（PVC）是一个**持久化存储卷**，我们在创建pod时可以定义这个类型的存储卷。它类似于一个pod。Pod消耗节点资源，PVC消耗PV资源。Pod可以请求特定级别的资源（CPU和内存）。pvc在申请pv的时候也可以请求**特定的大小和访问模式**（例如，可以一次读写或多次只读）。

- 绑定：

  - 用户创建pvc并指定需要的资源和访问模式。在找到可用pv之前，pvc会保持未绑定状态。

- 使用：

  a）需要找一个存储服务器，把它划分成多个存储空间；

  b）k8s管理员可以把这些存储空间定义成多个pv；

  c）在pod中使用pvc类型的存储卷之前需要先创建pvc，通过定义需要使用的pv的大小和对应的访问模式，找到合适的pv；

  d）pvc被创建之后，就可以当成存储卷来使用了，我们在定义pod时就可以使用这个pvc的存储卷

  e）pvc和pv它们是一一对应的关系，pv如果被pvc绑定了，就不能被其他pvc使用了；

  f）我们在创建pvc的时候，应该确保和底下的pv能绑定，如果没有合适的pv，那么pvc就会处于pending状态。

## Lab

- 创建pod，使用pvc作为持久化存储卷

```bash
#master-01创建nfs共享目录
mkdir /data/volume_test/v{1,2,3,4,5,6,7,8,9,10} -p
#配置nfs共享宿主机上的/data/volume_test/v1..v10目录
cat /etc/exports
/data/volumes 192.168.40.0/24(rw,no_root_squash)
/data/volume_test/v1 192.168.40.0/24(rw,no_root_squash)
/data/volume_test/v2 192.168.40.0/24(rw,no_root_squash)
/data/volume_test/v3 192.168.40.0/24(rw,no_root_squash)
/data/volume_test/v4 192.168.40.0/24(rw,no_root_squash)
/data/volume_test/v5 192.168.40.0/24(rw,no_root_squash)
/data/volume_test/v6 192.168.40.0/24(rw,no_root_squash)
/data/volume_test/v7 192.168.40.0/24(rw,no_root_squash)
/data/volume_test/v8 192.168.40.0/24(rw,no_root_squash)
/data/volume_test/v9 192.168.40.0/24(rw,no_root_squash)
/data/volume_test/v10 192.168.40.0/24(rw,no_root_squash)
#vim 批量替换:把192.168.40.4替换成*
:1,$s/192.168.40.0\/24/*/g
#重新加载配置，使配置生效
exportfs -arv
```

- 写pv yaml文件

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-nfs-v1
  labels:
    app: v1
spec:
  nfs:
    server: 192.168.40.4
    path: /data/volume_test/v1
  accessModes: 
  - ReadWriteOnce #<[]string> 的字段就要这么写 
  capacity:
    storage: 1Gi
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-nfs-v2
  labels:
    app: v2
spec:
  nfs:
    server: 192.168.40.4
    path: /data/volume_test/v2
  accessModes: 
  - ReadOnlyMany 
  capacity:
    storage: 1Gi
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-nfs-v3
  labels:
    app: v3
spec:
  nfs:
    server: 192.168.40.4
    path: /data/volume_test/v3
  accessModes: 
  - ReadWriteMany 
  capacity:
    storage: 1Gi
```

> - accessMode的官网解释：https://kubernetes.io/docs/concepts/storage/persistent-volumes/#access-modes
>
> - ａｃｃｅｓｓＭｏｄｅ
>
>   ```
>   ReadWriteOnce
>   ```
>
>   the volume can be mounted as **read-write by a single node**. ReadWriteOnce access mode still can allow multiple pods to access the volume when the pods are running on the same node.
>
>   ```
>   ReadOnlyMany
>   ```
>
>   the volume can be mounted as **read-only by many nodes**.
>
>   ```
>   ReadWriteMany
>   ```
>
>   the volume can be mounted as **read-write by many nodes**.
>
>   ```
>   ReadWriteOncePod
>   ```
>
>   **FEATURE STATE:** `Kubernetes v1.27 [beta]`
>
>   the volume can be mounted as **read-write by a single Pod.** Use ReadWriteOncePod access mode if you want to ensure that only one pod across the whole cluster can read that PVC or write to it. This is only supported for CSI volumes and Kubernetes version 1.22+.

- 写ｐｖｃ　ｙａｍｌ文件

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata: 
  name: pvc-nfs-v1
spec:
  accessModes: 
  - ReadWriteOnce #跟目标PV保持一致
  selector:
    matchLabels:
      app: v1 #找到目标PV的label
  resources:
    requests: 
      storage: 1Gi 
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata: 
  name: pvc-nfs-v2
spec:
  accessModes: 
  - ReadOnlyMany  #跟目标PV保持一致
  selector:
    matchLabels:
      app: v2 #找到目标PV的label
  resources:
    requests: 
      storage: 1Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata: 
  name: pvc-nfs-v3
spec:
  accessModes: 
  - ReadWriteMany #跟目标PV保持一致
  selector:
    matchLabels:
      app: v3 #找到目标PV的label
  resources:
    requests: 
      storage: 1Gi
```

- 用pod挂载pvc：

  ```yaml
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: dep-pvc-nfs-test
  spec:
    replicas: 3
    selector:
      matchLabels:
        storage: pvc
    template: 
      metadata:
        labels:
          storage: pvc
      spec:
        containers:
        - name: test-pvc
          image: nginx
          imagePullPolicy: IfNotPresent
          ports:
          - containerPort: 80
            protocol: TCP
          volumeMounts:
          - name: nginx-html
            mountPath: /usr/share/nginx/html
        volumes:
        - name: nginx-html
          persistentVolumeClaim:
            claimName: pvc-nfs-v2
  ```

## 回收策略

- 定义：pv.spec.persistentVolumeReclaimPolicy

- 当我们创建pod时如果使用pvc做为存储卷，那么它会和pv绑定，当删除pod，pvc和pv绑定就会解除，解除之后和pvc绑定的pv卷里的数据需要怎么处理，目前，卷可以保留，回收或删除：

  - Retain：
    - `"Retain"` means the volume will be left in its current phase (Released) for manual reclamation by the administrator. The default policy is Retain.
    - 当删除pvc的时候，pv仍然存在，处于released状态，但是它不能被其他pvc绑定使用，里面的数据还是存在的。
    - 我们想要继续使用这个pv，需要手动删除pv。删除pv，不会删除pv后端存储里的数据。再重建pv，当重新创建pvc时还会和这个最匹配的pv绑定。
  - Recycle （不推荐使用，1.15可能被废弃了）
  - Delete：
    - `"Delete"` means the volume will be deleted from Kubernetes on release from its claim. The **volume plugin must support Deletion**.
    - 删除pvc时即会从Kubernetes中移除PV，也会从相关的外部设施中删除存储。当然这常见于云服务商的存储服务。

# StorageClass

## 背景

- 上面介绍的PV和PVC模式都是需要先创建好PV，然后定义好PVC和pv进行一对一的Bond，但是如果PVC请求成千上万，那么就需要创建成千上万的PV，对于运维人员来说维护成本很高。

- Kubernetes提供一种自动创建PV的机制，叫StorageClass，它的作用就是创建PV的模板。k8s集群管理员通过创建storageclass可以动态生成一个存储卷pv供k8s pvc使用。

- 每个StorageClass都包含字段provisioner，parameters和reclaimPolicy。 

  - 具体来说，StorageClass会定义以下两部分：

    1、PV的属性：比如存储的大小、类型等；

    2、创建这种PV需要使用到的存储插件：比如Ceph、NFS等

  - 有了这两部分信息，Kubernetes就能够根据用户提交的PVC，找到对应的StorageClass，然后Kubernetes就会调用 StorageClass声明的存储插件，创建出需要的PV。


## 默认存储类

- 默认StorageClass是指当用户创建PVC时未显式指定StorageClass的情况下，Kubernetes将自动使用该StorageClass来动态配置存储卷。这大大简化了用户的操作，并确保了一致性和可靠性。文档：

  - https://kubernetes.io/zh-cn/docs/concepts/storage/storage-classes/#default-storageclass

  - https://kubernetes.io/zh-cn/docs/tasks/administer-cluster/change-default-storage-class/

- 给一个Storage class设置为默认存储类：

  ~~~sh
  kubectl patch storageclass ceph-rbd-storage -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
  ~~~

- 创建pvc时无需指定sc即可

  ~~~yaml
  $ cat <<EOF | kubectl apply -f -
  apiVersion: v1
  kind: PersistentVolumeClaim
  metadata:
    name: test-default-sc
    namespace: default
  spec:
    accessModes:
    - ReadWriteOnce
    resources:
      requests:
        storage: 10Gi
  EOF
  ~~~

## Lab - NFS Storage Class

> 安装 **nfs-subdir-external-provisioner** ，它是一个存储资源自动调配器，它可将现有的 NFS 服务器通过持久卷声明来支持 Kubernetes 持久卷的动态分配。
>
> 该组件是对 Kubernetes NFS-Client Provisioner 的扩展， **nfs-client-provisioner** 已经不提供更新，而且 [Github 仓库](https://cloud.tencent.com/developer/tools/blog-entry?target=https%3A%2F%2Fgithub.com%2Fkubernetes-retired%2Fexternal-storage%2Ftree%2Fmaster%2Fnfs-client&source=article&objectId=2365976) 也已经处于归档状态，已经迁移到 [nfs-subdir-external-provisioner](https://cloud.tencent.com/developer/tools/blog-entry?target=https%3A%2F%2Fgithub.com%2Fkubernetes-sigs%2Fnfs-subdir-external-provisioner&source=article&objectId=2365976) 的仓库。

- 使用NFS作为provisioner，用storageClass自动生成PV：

  ```bash
  #上传nfs-client的自动装载程序，称之为provisioner，这个程序会使用我们已经配置好的NFS服务器自动创建持久卷，也就是自动帮我们创建PV
  ctr -n=k8s.io images import nfs-subdir-external-provisioner.tar.gz
  #所有节点需要预先安装nfs-utils
  yum install nfs-utils
  ```
  
  ```bash
  #给nfs-provisioner配置空间
  mkdir /data/nfs_pro -p
  echo "/data/nfs_pro *(rw,no_root_squash)" >> /etc/exports #注：这里如果配置可访问的网段，要写宿主机网段而非pod网段，因为pv本质是挂载到宿主机上再挂载到pod上。
  exportfs -arv
  ```
  
  ```yaml
  ---
  #创建sa，给provisioner来用
  #serviceaccount是为了方便Pod里面的进程调用Kubernetes API或其他外部服务而设计的。
  apiVersion: v1
  kind: ServiceAccount
  metadata:
    name: nfs-provisioner
    
  ---
  apiVersion: rbac.authorization.k8s.io/v1
  kind: ClusterRoleBinding
  metadata:
    name: nfs-provisioner-clusterrolebinding
  roleRef:
    apiGroup: rbac.authorization.k8s.io
    kind: ClusterRole
    name: cluster-admin
  subjects:
  - kind: ServiceAccount
    name: nfs-provisioner
    namespace: default
  
  ---
  kind: Deployment
  apiVersion: apps/v1
  metadata:
    name: nfs-provisioner
  spec:
    selector:
      matchLabels:
         app: nfs-provisioner
    replicas: 1
    strategy:
      type: Recreate
    template:
      metadata:
        labels:
          app: nfs-provisioner
      spec:
        serviceAccount: nfs-provisioner
        containers:
          - name: nfs-provisioner
            image: registry.cn-beijing.aliyuncs.com/mydlq/nfs-subdir-external-provisioner:v4.0.0
            imagePullPolicy: IfNotPresent
            volumeMounts:
              - name: nfs-client-root
                mountPath: /persistentvolumes
            env:
              - name: PROVISIONER_NAME
                value: rm1.com/nfs
              - name: NFS_SERVER
                value: 172.16.183.100
              - name: NFS_PATH
                value: /data/nfs_pro/
        volumes:
          - name: nfs-client-root
            nfs:
              server: 172.16.183.100
              path: /data/nfs_pro/
              
  ---
  apiVersion: storage.k8s.io/v1
  kind: StorageClass
  metadata: 
    name: sc-nfs
  provisioner: rm1.com/nfs
  ```
  
  ```yaml
  #创建pvc，引用sc
  kind: PersistentVolumeClaim
  apiVersion: v1
  metadata:
    name: pvc-sc-nfs
  spec:
    accessModes:
    - ReadWriteMany
    resources:
      requests:
        storage: 1Gi
    storageClassName:  sc-nfs
  
  #创建pod，挂载pvc
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: dep-pvc-nfs-test
  spec:
    replicas: 3
    selector:
      matchLabels:
        storage: pvc
    template: 
      metadata:
        labels:
          storage: pvc
      spec:
        containers:
        - name: test-pvc
          image: nginx
          imagePullPolicy: IfNotPresent
          ports:
          - containerPort: 80
            protocol: TCP
          volumeMounts:
          - name: nginx-html
            mountPath: /usr/share/nginx/html
        volumes:
        - name: nginx-html
          persistentVolumeClaim:
            claimName: pvc-sc-nfs
  ```
  

# helm部署nfs provisioner

## NFS 服务器部署

- 安装 NFS 服务端软件包

```shell
yum install nfs-utils
```

- 创建共享数据目录

执行以下命令创建共享[数据存储](https://cloud.tencent.com/product/cdcs?from_column=20065&from=20065)目录，本文以 `/data/k8s` 为例，请根据实际情况修改。

```shell
mkdir -p /data/k8s
systemctl start rpcbind
systemctl enable rpcbind
systemctl start nfs-server
systemctl enable nfs-server

# 检查用户id和组id 65534名字是啥？有可能是nobody，有可能是nfsnobody
# 如果是nfsnobody，修改权限：
chown nfsnobody:nfsnobody /data/k8s
# 如果是nobody，修改权限：
chown nobody:nobody /data/k8s
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

```shell
yum install nfs-utils
mkdir -p /data/k8s
systemctl start rpcbind
systemctl enable rpcbind
systemctl start nfs-server
systemctl enable nfs-server

tee -a /etc/exports<<'EOF'
/data/k8s *(rw,no_root_squash)
EOF

exportfs -v
```

- 添加 Helm 源

```shell
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

**（备选方案，使用配置文件设置变量参数）**，有更多定制化需求时可以选择自定义 `values.yaml` 的方式进行安装，实际使用中与命令行安装 NFS Subdir External Provisioner 的方式**二选一**即可。

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
# 主要修改内容如下
image:
  repository: registry.k8s.io/sig-storage/nfs-subdir-external-provisioner  #镜像拉取地址，默认可能拉取不下来，建议替换成本地或是其他可正常访问的仓库
  tag: v4.0.2             #镜像 tag 默认为 v4.0.2，可根据实际情况替换
nfs:
  server: 192.168.9.81    #指定 NFS 服务器的地址
  path: /data/k8s         #指定 NFS 导出的共享数据目录
storageClass:
  defaultClass: false     #是否设置为默认的 StorageClass，本示例没设置，有需要的可以设置为 true
  name: nfs-sc            #指定 storageClass 的名字
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

