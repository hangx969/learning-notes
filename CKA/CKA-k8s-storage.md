# 持久化存储

- 查看支持的存储种类

  ```bash
  kubectl explain pods.spec.volumes
  ```

## emptyDir

- emptyDir类型的Volume是在Pod分配到Node上时被创建，Kubernetes会在Node上自动分配一个目录，因此无需指定宿主机Node上对应的目录文件。 这个目录的初始内容为空，当Pod从Node上移除时，emptyDir中的数据会被永久删除。emptyDir Volume主要用于某些应用程序无需永久保存的临时目录，多个容器的共享目录等。

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

- hostPath Volume使得容器可以使用宿主机的文件系统进行存储，hostpath（宿主机路径）：节点级别的存储卷，在pod被删除，这个存储卷还是存在的，不会被删除，所以只要同一个pod被调度到同一个节点上来，在pod被删除重新被调度到这个节点之后，对应的数据依然是存在的。

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

## NFS

- 搭建NFS服务

  ```bash
  #在master-01上搭建NFS作为服务端
  yum install nfs-utils -y
  mkdir /data/volumes -pv
  systemctl start nfs
  
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

## PV/PVC

### PV

- PersistentVolume（PV）是群集中的一块存储，由管理员配置或使用存储类动态配置。它是集群中的资源，是容量插件，如Volumes，其生命周期独立于使用PV的任何单个pod。
- PV供应方式：
  - 静态：集群管理员创建了许多PV。它们包含可供群集用户使用的实际存储的详细信息。它们存在于Kubernetes API中，可供使用。
  - 动态：当管理员创建的静态PV都不匹配用户的PersistentVolumeClaim时，群集可能会尝试为PVC专门动态配置卷。此配置基于StorageClasses，PVC必须请求存储类，管理员必须创建并配置该类，以便进行动态配置。

### PVC

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

- 回收策略

  - 当我们创建pod时如果使用pvc做为存储卷，那么它会和pv绑定，当删除pod，pvc和pv绑定就会解除，解除之后和pvc绑定的pv卷里的数据需要怎么处理，目前，卷可以保留，回收或删除：

    - Retain：当删除pvc的时候，pv仍然存在，处于released状态，但是它不能被其他pvc绑定使用，里面的数据还是存在的，当我们下次再使用的时候，数据还是存在的，这个是默认的回收策略

    - Recycle （不推荐使用，1.15可能被废弃了）

    - Delete：删除pvc时即会从Kubernetes中移除PV，也会从相关的外部设施中删除存储

### Lab

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

### 回收策略

pv.spec.persistentVolumeReclaimPolicy

- Retain

  - `"Retain"` means the volume will be left in its current phase (Released)
    for manual reclamation by the administrator. The default policy is Retain.
  - pvc和pv绑定，如果使用默认的回收策略retain，那么删除pvc之后，pv会处于released状态，无法重新被pvc绑定。

  - 我们想要继续使用这个pv，需要手动删除pv。删除pv，不会删除pv后端存储里的数据。再重建pv，当重新创建pvc时还会和这个最匹配的pv绑定，数据还是原来数据，不会丢失。

- Delete
  - `"Delete"` means the volume will be deleted from Kubernetes on release
    from its claim. The volume plugin must support Deletion.
