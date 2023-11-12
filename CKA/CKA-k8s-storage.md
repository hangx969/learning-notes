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
  
  ```

  