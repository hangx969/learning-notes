# 持久化数据

应用场景：

1. 用户数据（用户文件、用户头像等）
2. 文件数据（比如大模型的模型文件）
3. 配置文件
4. 共享数据（多个微服务共享一块存储数据）
5. 程序数据
6. 日志文件

# Volume

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

## 直接创建volume

直接在pod的volume字段配置各种类型的volume存储

~~~yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-volume
spec:
  containers:
  - name: container-volume
    image: nginx
    volumeMounts:
    - name: volume-nfs
      mountPath: /cache
  volumes:
  - name: volume-nfs
    nfs:
      server: 192.168.40.180
      path: /data/nfs_pro
~~~

## emptyDir

- 一个EmptyDir就是Host上的一个空目录。

- EmptyDir是在Pod被分配到Node时创建的，它的初始内容为空，并且无须指定宿主机上对应的目录文件，因为kubernetes会自动分配一个目录。

- 当Pod销毁时，EmptyDir中的数据也会被**永久删除**。

- EmptyDir用途如下：

  - 临时空间，例如应用程序运行时所需的**临时目录**，且无须永久保留


  - 一个容器需要从另一个容器中获取数据的目录（sidecar容器通过emptyDir共享数据）


<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202311141720686.png" alt="image-20231114172051513" style="zoom:50%;" />

### 容器共享数据

~~~yaml
apiVersion: apps/v1 
kind: Deployment 
metadata: 
  name: emptydir 
spec: 
  replicas: 1
  selector: 
    matchLabels: 
      app: emptydir 
  template: 
    metadata: 
      labels: 
        app: emptydir 
    spec: 
      containers: 
      - image: nginx:1.15.12 
        name: nginx 
        volumeMounts: 
        - name: share-volume # 挂载了emptyDir volume
          mountPath: /opt  
      - image: redis:7.2.5 
        name: redis 
        volumeMounts: 
        - name: share-volume # 挂载了emptyDir volume
          mountPath: /mnt      
      volumes: # 这个volume同时给两个容器用
      - name: share-volume 
        emptyDir: {} 
~~~

### 查看挂载到的宿主机路径


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
    │   └── volume-cache # 这就是pod emptydir的挂载路径
    └── kubernetes.io~projected
        └── kube-api-access-kdqtk
            ├── ca.crt -> ..data/ca.crt
            ├── namespace -> ..data/namespace
            └── token -> ..data/token
            
cd /var/lib/kubelet/pods/e948ebb2-50f2-4884-a16c-2c0dd7b3f1de/volumes/kubernetes.io~empty-dir/volume-cache
```

### 使用内存tempfs挂载

EmptyDir可以绑定主机上的硬盘和内存作为Volume，比如把 `emptyDir.medium` 字段设置为`Memory`，就可以让Kubernetes使用tmpfs（内存支持的文件系统）。

虽然tmpfs非常快，但是设置的大小会被计入到Container的内存限制当中。一些memcached、redis等服务可能会用到。其他情况用得不多。

~~~yaml
# 使用内存作为EmptyDir，只需要把medium改为Memory即可： 
    spec: 
      containers: 
      - image: nginx:1.15.12 
        name: nginx 
        volumeMounts: 
        - mountPath: /opt 
          name: share-volume
      volumes: 
      - name: share-volume 
        emptyDir: 
          medium: Memory
~~~

创建Pod，即可在Pod的容器内看到使用tmpfs挂载的/opt目录：

~~~sh
tmpfs                   tmpfs    3.5G     0  3.5G   0% /opt
~~~

### 限制大小

两种类型的EmptyDir都支持限制卷的大小，只需要添加sizeLimit字段即可。

1. 磁盘类型的emptyDir，限制大小后不会显示具体限制的大小
2. 磁盘类型的超出最大限制时，Pod将会变成Completed状态，同时将会创建一个Pod
3. 内存类型的emptyDir不会超出限制的大小，如不限制将会使用机器内存的最大值，或容器内存限制之和的最大值

~~~yaml
volumes: 
- name: share-volume 
  emptyDir: 
    medium: Memory # 可选
    sizeLimit: 10Mi
~~~

这种方式适用于某些非云原生设计的应用，他们会把日志写到本地文件，随着时间推移会把宿主机空间占满，是个定时炸弹。可以通过限制emptyDir的大小，挂载到容器内日志输出目录，这样当日志文件超过limit，pod就变成Completed状态，同时创建一个新的pod出来。

## hostPath

hostPath是指Pod挂载宿主机上的目录或文件，使得容器可以使用宿主机的文件系统进行存储。pod被删除这个存储卷还是存在的。所以只要同一个pod被调度到同一个节点上来，对应的数据依然是存在的。

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202311141722615.png" alt="image-20231114172218560" style="zoom:50%;" />

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-hostpath
spec:
  containers:
  - name: nginx-hostpath
    image: nginx
    volumeMounts:
    - name: volume-cache
      mountPath: /test-nginx
  - name: tomcat-hostpath
    image: tomcat
    volumeMounts:
    - name: volume-cache
      mountPath: /test-tomcat # 容器内目录，可以是不存在的，会自动创建
  volumes:
  - name: volume-cache
    hostPath:
      path: /data # 宿主机目录
      type: DirectoryOrCreate # type的定义：https://kubernetes.io/docs/concepts/storage/volumes/#hostpath
```

hostPath.type字段说明:

- type为空字符串：默认选项，意味着挂载hostPath卷之前不会执行任何检查。
- DirectoryOrCreate：如果给定的hostPath.path不存在任何东西，那么将根据需要创建一个权限为0755的空目录，和Kubelet具有相同的组和权限（如果kubelet是root启动的，目录属主就是root）。
- Directory：hostPath.path目录必须存在于宿主机上，否则pod起不来。
- File：文件类型，必须存在于给定路径中。如果想要挂载文件，必须指定type为File，否则如果文件不存在，就会变成自动创建文件同名的目录。
- FileOrCreate：如果给定的hostPath.path文件内容不存在，则会根据需要创建一个空文件，权限设置为0644，和Kubelet具有相同的组和所有权。 
- Socket：UNIX 套接字，如某个程序的socket文件，必须存在于给定路径中。
- CharDevice：字符设备，如串行端口、声卡、摄像头等，必须存在于给定路径中，且只有Linux 支持。
- BlockDevice：块设备，如硬盘等，必须存在于给定路径中，且只有Linux支持。

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

## NFS/NAS

HostPath可以解决数据持久化的问题，但是一旦Node节点故障了，Pod如果转移到了别的节点，又会出现问题了，此时需要准备单独的网络存储系统，比较常用的有NFS（云平台上叫NAS）、CIFS。

搭建一台NFS服务器，然后将Pod中的存储直接连接到NFS系统上，无论Pod在节点上怎么转移，只要Node跟NFS的对接没问题，数据就可以成功访问。

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202311141723114.png" alt="image-20231114172333052" style="zoom:50%;" />

### NFS访问权限

NFS的用户认证和权限控制基于RPC，在nfs3和nfs4版本中，最常用的认证机制是AUTH_UNIX。客户端上的UID/GID通过RPC传递到服务端，然后对这些ID做权限校验，这就要求客户端、服务端的UID/GID必须相同。同时，NFS支持在其文件夹上通过以下配置来设置文件夹的访问权限：

- all_squash: 将所有用户和组映射为匿名用户和组。默认为nfsnobody用户（UID：65534）、nfsnobody组（GID：65534），也可以通过`anonuid、anongid`指定。
- no_all_squash：访问用户先与本机用户通过ID匹配，能匹配上就用；匹配不上再映射为匿名用户和组。这是默认选项。
- root_squash: 将来访的root用户（UID=0）映射为匿名用户。这是默认行为。可以通过设置no_root_squash取消这种映射，保持root用户。

Lab

- 搭建NFS服务

  ```bash
  # 安装nfs服务端
  # centos\rocky
  yum install nfs-utils -y
  # ubuntu
  apt install nfs-kernel-server -y 
  
  # 创建共享目录，实际使用中建议对不同用途的nfs目录分别创建子目录分开挂载，便于管理。
  mkdir /data/volumes -pv
  
  # 启动nfs服务
  # centos\rockylinux中
  sudo systemctl enable --now rpcbind nfs-server
  # ubuntu中
  systemctl enable --now nfs-kernel-server 
  
  # 配置nfs服务端export
  vim /etc/exports
  /data/volumes *(rw,sync,no_subtree_check,no_root_squash)
  # rw 该主机对该共享目录有读写权限
  # no_root_squash 登入 NFS 主机使用分享目录的使用者，如果是 root 的话，那么对于这个分享的目录来说，他就具有 root 的权限。根用户在 NFS 客户端上拥有和服务器上相同的权限。
  
  # 加载NFS配置生效
  exportfs -arv
  ```

- 客户端挂载测试：

  不测试也需要宿主机安装nfs客户端，因为pod挂载nfs也是需要先挂载到宿主机再挂载进pod的。如果工作节点没有安装nfs客户端，就会报错：

  Output: mount: /var/lib/kubelet/pods/faae4701-1c1d-4a2d-a16efa76c64a7ae7/volumes/kubernetes.io~nfs/nfs-volume: bad option; for several filesystems (e.g. nfs, cifs) you might need a /sbin/mount. helper program. 

  ~~~sh
  # CentOS、Rocky系列 
  yum install nfs-utils -y 
  # Ubuntu系列 
  apt install nfs-common -y 
  
  mkdir /nfs-test 
  mount -t nfs 192.168.40.4:/data/volumes /nfs-test/
  df -Th  | grep nfs-test 
  # 卸载挂载
  umount /nfs-test
  ~~~

- 测试pod挂载

  ```yaml
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: dep-nfs
  spec:
    replicas: 1
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

## Downward API

元数据挂载，可以把pod的一些元数据以文件的形式，直接挂载到容器内的某个目录（比如标签、命名空间、pod IP等）。

并不推荐去使用，而是更推荐使用`env.valueFrom.fieldRef.fieldPath: status.podIP`这种方式，因为：

1. downward API配置麻烦
2. 程序读取一个文件肯定不如读取环境变量方便

## PVC

是K8s中的一类资源。用于配置不同的存储后端。

不推荐使用volume直接配置挂载持久化存储（in-tree模式），而是推荐使用PVC先绑定存储，pod再绑定PVC。

# PV/PVC

为什么引入PV/PVC，因为只用volume手动做存储，无法实现以下：

1. 当某个数据卷不再被挂载使用时，里面的数据如何处理？（生命周期管理）
2. 如果想要实现只读挂载怎么处理？
3. 如果想要只能一个pod挂载如何处理？
4. 如何只允许某个pod使用10G空间？
5. 同一个应用的不同副本如何使用不同的数据目录？（statefulset主从pod需要各自独立的存储）

从用户角度考虑，比如使用NFS volume存储，此时就要求用户会搭建NFS系统，并且会在yaml配置nfs。由于kubernetes支持的存储系统有很多，要求客户全都掌握，显然不现实。站在用户的角度，只需要提出自己需要多少存储资源，并不管关心存储的底层实现。底层由专业人员来维护即可。

从k8s开发者角度考虑，volume的配置是在k8s原生的体系当中的，每兼容一种存储，就需要增加一些volume原生代码开发，复杂度高，不符合云原生原则。

## PV

为了能够屏蔽底层存储实现的细节，方便用户使用，kubernetes引入**PV**和**PVC**两种资源对象。

![image-20231114172731738](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202311141727818.png)

PersistentVolume（PV）是对底层的共享存储的一种抽象。由管理员配置，或使用存储类动态配置，它与底层具体的共享存储技术有关，并通过**插件**完成与共享存储的对接。

它是集群中的资源，其生命周期独立于使用PV的任何单个pod。PV通过yaml文件部署；PV是node级别的，不能配namespace。

PV供应方式：
- 静态：集群管理员创建了许多PV。它们包含可供群集用户使用的实际存储的详细信息。它们存在于Kubernetes API中，可供使用。
- 动态：当管理员创建的静态PV都不匹配用户的PersistentVolumeClaim时，集群可能会尝试为PVC专门动态配置卷。此配置基于StorageClasses，PVC必须请求存储类，管理员必须创建并配置该存储类，以便进行动态配置。

## PVC

- PersistentVolumeClaim（PVC）是一个**持久化存储卷**，我们在创建pod时可以定义这个类型的存储卷。它类似于一个pod。Pod消耗节点资源，PVC消耗PV资源。Pod可以请求特定级别的资源（CPU和内存）。pvc在申请pv的时候也可以请求**特定的大小和访问模式**（例如，可以一次读写或多次只读）。

- 绑定：

  - 用户创建pvc并指定需要的资源和访问模式。在找到可用pv之前，pvc会保持未绑定状态。

  - PVC怎么找到对应的PV？通过PVC指定storageClassName为xxx，他就会找到同样有xxx这个名字的PV来绑定：

    ~~~yaml
    ---
    # PV
    apiVersion: v1
    kind: PersistentVolume
    metadata:
      name: ceph-rbd-pv
    spec:
      storageClassName: ceph-fast # 在手动绑定PV和PVC的场景下，这个字段是可以随便写的。
      accessMode:
      - ReadWriteOnce
      capacity:
        storage: 3Gi
      rbd:
        monitors:
        - 192.168.40.180:6789
        - 192.168.40.181:6789
        - 192.168.40.182:6789
        pool: rbd
        image: ceph-rnd-pv-test
        user: admin
        secretRef:
          name: ceph-secret
        fsType: ext4
        readOnly: false
    ---
    # PVC
    apiVersion: v1
    kind: PersistentVolumeClaim
    metadata:
      name: ceph-rbd-pvc
    spec:
      storageClassName: ceph-fast # 需要保证PVC的这个字段和PV一致才能被匹配
      accessMode:
      - ReadWriteOnce # 挂载模式也需要也要匹配，PVC的是PV的子集即可，
      resource:
        requests:
          storage: 3Gi # PVC的申请存储需要<=PV配置的存储大小
    ---
    # pod
    ...
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: ceph-rbd-pvc # pod和PVC的绑定是通过PVC的名称来匹配的
    ~~~

- 使用：

  a）需要找一个存储服务器，把它划分成多个存储空间；

  b）k8s管理员可以把这些存储空间定义成多个pv；

  c）在pod中使用pvc类型的存储卷之前需要先创建pvc，通过定义需要使用的pv的大小、对应的访问模式、storageClassName或者Label，找到合适的pv；

  d）pvc被创建之后，就可以当成存储卷来使用了，我们在定义pod时就可以使用这个pvc的存储卷

  e）pvc和pv它们是一一对应的关系，pv如果被pvc绑定了，就不能被其他pvc绑定了；

  f）我们在创建pvc的时候，应该确保和底下的pv能绑定，如果没有合适的pv，那么pvc就会处于pending状态。

## Lab

### HostPath PV

~~~yaml
kind: PersistentVolume 
apiVersion: v1 
metadata: 
  name: task-pv-volume 
  labels: 
    type: local 
spec: 
  storageClassName: hostpath 
  volumeMode: Filesystem # 只有未格式化的硬盘才用Block，其余都用filesystem
  capacity: 
    storage: 10Gi # HostPath和NFS目前都不支持限制存储大小
  accessModes: 
  - ReadWriteOnce 
  hostPath: 
    path: "/mnt/data" 
~~~

### NFS PV

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

- 写pvc yaml文件

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
        volumeMounts:
        - name: nginx-html
          mountPath: /usr/share/nginx/html
      volumes:
      - name: nginx-html
        persistentVolumeClaim:
          claimName: pvc-nfs-v2
```

## 访问策略

accessMode的官网解释：https://kubernetes.io/docs/concepts/storage/persistent-volumes/#access-modes

### ReadWriteOnce

the volume can be mounted as **read-write by a single node**. 单节点读写，只要pod在同一个节点上就可以读写。

ReadWriteOnce access mode still can allow multiple pods to access the volume when the pods are running on the same node.

### ReadOnlyMany

the volume can be mounted as **read-only by many nodes**. 多节点只读挂载

### ReadWriteMany

the volume can be mounted as **read-write by many nodes**. 多节点读写挂载

### ReadWriteOncePod

the volume can be mounted as **read-write by a single Pod.** 单Pod读写挂载

Use ReadWriteOncePod access mode if you want to ensure that only one pod across the whole cluster can read that PVC or write to it. 

This is only supported for CSI volumes and Kubernetes version 1.22+.

（截止1.30暂时没有ReadOnlyOncePod模式）

> 是否能用以上这几种访问模式，要取决于后端对接的存储是否支持这种模式。

## 回收策略

定义：pv.spec.persistentVolumeReclaimPolicy

当我们创建pod时如果使用pvc做为存储卷，那么它会和pv绑定，当删除pod，pvc和pv绑定就会解除，解除之后和pvc绑定的pv卷里的数据需要怎么处理，目前，卷可以保留，回收或删除：

1. Retain：【管理员手动维护的PV、生产环境 推荐使用】
  - `"Retain"` means the volume will be left in its current phase (Released) for manual reclamation by the administrator. The default policy is Retain.
  - 当删除pvc的时候，pv仍然存在，处于released状态，但是它不能被其他pvc绑定使用，里面的数据还是存在的。
  - 我们想要继续使用这个pv，需要手动删除pv。删除pv，不会删除pv后端存储里的数据。再重建pv，当重新创建pvc时还会和这个最匹配的pv绑定。
2. Delete：【动态存储建议用，因为PV不是管理员手动维护的】
  - 如果存储插件支持，删除PVC的时候，PV会一起被删除。动态存储默认为Delete。
  - 必须所有pod都没有挂载这个PVC的时候才能删掉，否则会卡住删不动。
3. Recycle：（不推荐使用，1.15可能被废弃了）

## PVC创建失败的原因

PVC一直Pending的原因：

1. PVC空间申请的大小高于PV的大小
2. PVC的storageClass名称和PV的一致
3. PVC的accessMode和PV的不一致
4. PV并不是空闲状态，已经被其他PVC绑定了

挂载PVC的pod一直处于pending：

1. PVC不存在
2. PVC和pod不在同一namespace

# 动态存储

上面介绍的PV和PVC模式都是需要先创建好PV，然后定义好PVC和pv进行一对一的绑定。但是大规模集群PVC请求成千上万，那么就需要创建成千上万的PV，对于运维人员来说维护成本很高。这时候需要动态存储自动创建PV。

动态存储依赖StorageClass和CSI实现。当创建PVC时，storageClass指定动态存储类，该类指向不同的CSI存储供应商，之后通过该CSI对接到后端存储，就可以完成PV的自动创建。

## storageClass

Kubernetes提供一种动态创建PV的机制，即创建PV的模板。k8s集群管理员通过创建storageclass可以动态生成pv供pvc使用。

每个StorageClass都包含字段provisioner，parameters和reclaimPolicy。 

具体来说，StorageClass会定义以下两部分：

1. PV的属性：比如存储的大小、类型等；
2. 创建PV用的CSI存储插件：比如Ceph、NFS等。

有了这两部分信息，Kubernetes就能够根据用户提交的PVC，找到对应的StorageClass，然后Kubernetes就会调用 StorageClass声明的存储插件，创建出需要的PV。

## CSI

CSI是一个标准化的存储接口，用于在容器环境集成外部存储系统，提供了统一的方式来集成各种存储系统，无论是云供应商的存储还是本地自检存储，都可以通过CSI对接到容器平台中。

在同一个集群中，可以同时存在多个CSI对接不同的存储平台，之后可以通过StorageClass的provisioner字段声明该clss对接哪一种存储平台。

## NFS存储类-基于nfs-subdir插件

> 安装 **nfs-subdir-external-provisioner** ，它是一个存储资源自动调配器，它可将现有的NFS服务器通过持久卷声明来支持 Kubernetes 持久卷的动态分配。
>
> 该组件是对 Kubernetes NFS-Client Provisioner 的扩展， **nfs-client-provisioner** 已经不提供更新，而且 [Github 仓库](https://cloud.tencent.com/developer/tools/blog-entry?target=https%3A%2F%2Fgithub.com%2Fkubernetes-retired%2Fexternal-storage%2Ftree%2Fmaster%2Fnfs-client&source=article&objectId=2365976) 也已经处于归档状态，已经迁移到 [nfs-subdir-external-provisioner](https://cloud.tencent.com/developer/tools/blog-entry?target=https%3A%2F%2Fgithub.com%2Fkubernetes-sigs%2Fnfs-subdir-external-provisioner&source=article&objectId=2365976) 的仓库。

使用NFS作为provisioner，用storageClass自动生成PV：

```bash
# 上传nfs-client的自动装载程序，称之为provisioner，这个程序会使用我们已经配置好的NFS服务器自动创建持久卷，也就是自动帮我们创建PV
# 所有节点需要预先安装nfs-utils
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
        volumeMounts:
        - name: nginx-html
          mountPath: /usr/share/nginx/html
      volumes:
      - name: nginx-html
        persistentVolumeClaim:
          claimName: pvc-sc-nfs
```

## NFS存储类-基于CSI

github地址：[kubernetes-csi/csi-driver-nfs: This driver allows Kubernetes to access NFS server on Linux node.](https://github.com/kubernetes-csi/csi-driver-nfs)

安装说明：[kubernetes-csi/csi-driver-nfs: This driver allows Kubernetes to access NFS server on Linux node.](https://github.com/kubernetes-csi/csi-driver-nfs?tab=readme-ov-file#install-driver-on-a-kubernetes-cluster)

这里采用local install模式：

~~~sh
cd csi-driver-nfs/ 
sed -i "s#registry.k8s.io#k8s.m.daocloud.io#g" deploy/v4.11.0/*.yaml 
./deploy/install-driver.sh v4.11.0 local 
~~~

### 创建存储类

~~~yaml
apiVersion: storage.k8s.io/v1 
kind: StorageClass 
metadata: 
  name: nfs-csi 
provisioner: nfs.csi.k8s.io 
parameters: 
  server: 192.168.40.180 
  share: /data/nfs_pro # 指定主目录，会自动在里面创建子目录作为每个PV
  # csi.storage.k8s.io/provisioner-secret is only needed for providing mountOptions in DeleteVolume 
  # csi.storage.k8s.io/provisioner-secret-name: "mount-options" 
  # csi.storage.k8s.io/provisioner-secret-namespace: "default" 
reclaimPolicy: Delete 
volumeBindingMode: Immediate 
mountOptions: 
  - nfsvers=4.1 
~~~

### 挂载测试

~~~yaml
# PVC
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-nfs-dynamic
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 10Gi
  storageClassName: nfs-csi
# pod
---
kind: Pod
apiVersion: v1
metadata:
  name: nginx-nfs
spec:
  containers:
    - image: mcr.microsoft.com/oss/nginx/nginx:1.19.5
      name: nginx-nfs
      command:
        - "/bin/bash"
        - "-c"
        - set -euo pipefail; while true; do echo $(date) >> /mnt/nfs/outfile; sleep 1; done
      volumeMounts:
        - name: persistent-storage
          mountPath: "/mnt/nfs"
          readOnly: false
  volumes:
    - name: persistent-storage
      persistentVolumeClaim:
        claimName: pvc-nfs-dynamic
~~~

> 注意：一般NFS/NAS高可用和性能不是很好，一些数据库、缓存、消息队列服务尽量不要使用NFS，生产环境中推荐使用分布式存储。如果实在没有分布式存储，那就不要部署在k8s中了。

## 默认存储类

- 默认StorageClass是指当用户创建PVC时未显式指定StorageClass的情况下，Kubernetes将自动使用该StorageClass来动态配置存储卷。这大大简化了用户的操作，并确保了一致性和可靠性。文档：

  - https://kubernetes.io/zh-cn/docs/concepts/storage/storage-classes/#default-storageclass

  - https://kubernetes.io/zh-cn/docs/tasks/administer-cluster/change-default-storage-class/

- 给一个Storage class设置为默认存储类：

  ~~~sh
  kubectl patch storageclass ceph-rbd-storage -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
  ~~~

- 取消一个存储类的默认：

  ~~~sh
  kubectl patch storageclass sc-nfs -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"false"}}}'
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

# sts的volumeClaimTemplates 

使用StatefulSet部署有状态服务时，可以使用`volumeClaimTemplates`自动为每个Pod生成 PVC，并挂载至容器中，大大降低了手动创建管理存储的难度和复杂度。

假设需要搭建一个三节点的RabbitMQ集群到K8s中，并且需要实现数据的持久化，此时可以通StatefulSet创建三个副本，并且通过volumeClaimTemplates自动绑定各自的存储。 

## sts

~~~yaml
kind: StatefulSet
apiVersion: apps/v1
metadata:
  labels:
    app: rmq-cluster
  name: rmq-cluster
  namespace: public-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: rmq-cluster
  serviceName: rmq-cluster
  template:
    metadata:
      labels:
        app: rmq-cluster
    spec:
      containers:
      - args:
        - -c
        - cp -v /etc/rabbitmq/rabbitmq.conf ${RABBITMQ_CONFIG_FILE}; exec docker-entrypoint.sh
          rabbitmq-server
        command:
        - sh
        env:
        - name: RABBITMQ_DEFAULT_USER
          valueFrom:
            secretKeyRef:
              key: username
              name: rmq-cluster-secret
        - name: RABBITMQ_DEFAULT_PASS
          valueFrom:
            secretKeyRef:
              key: password
              name: rmq-cluster-secret
        - name: RABBITMQ_ERLANG_COOKIE
          valueFrom:
            secretKeyRef:
              key: cookie
              name: rmq-cluster-secret
        - name: K8S_SERVICE_NAME
          value: rmq-cluster
        - name: POD_IP
          valueFrom:
            fieldRef:
              fieldPath: status.podIP
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: POD_NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
        - name: RABBITMQ_USE_LONGNAME
          value: "true"
        - name: RABBITMQ_NODENAME
          value: rabbit@$(POD_NAME).rmq-cluster.$(POD_NAMESPACE).svc.cluster.local
        - name: RABBITMQ_CONFIG_FILE
          value: /var/lib/rabbitmq/rabbitmq.conf
        image: registry.cn-beijing.aliyuncs.com/dotbalo/rabbitmq:3.13.6-management-alpine
        imagePullPolicy: IfNotPresent
        livenessProbe:
          exec:
            command:
            - rabbitmqctl
            - status
          initialDelaySeconds: 30
          timeoutSeconds: 10
        name: rabbitmq
        ports:
        - containerPort: 15672
          name: http
          protocol: TCP
        - containerPort: 5672
          name: amqp
          protocol: TCP
        readinessProbe:
          exec:
            command:
            - rabbitmqctl
            - status
          initialDelaySeconds: 10
          timeoutSeconds: 10
        volumeMounts:
        - mountPath: /etc/rabbitmq
          name: config-volume
          readOnly: false
        - mountPath: /var/lib/rabbitmq
          name: rabbitmq-storage
          readOnly: false
      serviceAccountName: rmq-cluster
      terminationGracePeriodSeconds: 30
      volumes:
      - configMap:
          items:
          - key: rabbitmq.conf
            path: rabbitmq.conf
          - key: enabled_plugins
            path: enabled_plugins
          name: rmq-cluster-config
        name: config-volume
    volumeClaimTemplates: # 在这里写存储模板，指定存储类
    - metadata:
        name: rabbitmq-storage
      spec:
        accessModes:
        - ReadWriteOnce
        storageClassName: "nfs-csi"
        resources:
          requests:
            storage: 4Gi
~~~

## svc-clusterIP

~~~yaml
kind: Service
apiVersion: v1
metadata:
  labels:
    app: rmq-cluster
  name: rmq-cluster
  namespace: public-service
spec:
  clusterIP: None
  ports:
  - name: amqp
    port: 5672
    targetPort: 5672
  selector:
    app: rmq-cluster
~~~

## svc-LB

~~~yaml
kind: Service
apiVersion: v1
metadata:
  labels:
    app: rmq-cluster
    type: LoadBalancer
  name: rmq-cluster-balancer
  namespace: public-service
spec:
  ports:
  - name: http
    port: 15672
    protocol: TCP
    targetPort: 15672
  - name: amqp
    port: 5672
    protocol: TCP
    targetPort: 5672
  selector:
    app: rmq-cluster
  type: NodePort
~~~

## cm

~~~yaml
kind: ConfigMap
apiVersion: v1
metadata:
  name: rmq-cluster-config
  namespace: public-service
  labels:
    addonmanager.kubernetes.io/mode: Reconcile
data:
    enabled_plugins: |
      [rabbitmq_management,rabbitmq_peer_discovery_k8s].
    rabbitmq.conf: |
      loopback_users.guest = false

      default_user = RABBITMQ_USER
      default_pass = RABBITMQ_PASS
      ## Clustering
      cluster_formation.peer_discovery_backend = rabbit_peer_discovery_k8s
      cluster_formation.k8s.host = kubernetes.default.svc.cluster.local
      cluster_formation.k8s.address_type = hostname
      #################################################
      # public-service is rabbitmq-cluster's namespace#
      #################################################
      cluster_formation.k8s.hostname_suffix = .rmq-cluster.public-service.svc.cluster.local
      cluster_formation.node_cleanup.interval = 10
      cluster_formation.node_cleanup.only_log_warning = true
      cluster_partition_handling = autoheal
      ## queue master locator
      queue_master_locator=min-masters
~~~

## secret

~~~yaml
kind: Secret
apiVersion: v1
metadata:
  name: rmq-cluster-secret
  namespace: public-service
stringData:
  cookie: ERLANG_COOKIE
  password: RABBITMQ_PASS
  url: amqp://RABBITMQ_USER:RABBITMQ_PASS@rmq-cluster-balancer
  username: RABBITMQ_USER
type: Opaque
~~~

## rbac

~~~yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: rmq-cluster
  namespace: public-service
---
kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: rmq-cluster
  namespace: public-service
rules:
  - apiGroups:
      - ""
    resources:
      - endpoints
    verbs:
      - get
---
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: rmq-cluster
  namespace: public-service
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: rmq-cluster
subjects:
- kind: ServiceAccount
  name: rmq-cluster
  namespace: public-service
~~~

