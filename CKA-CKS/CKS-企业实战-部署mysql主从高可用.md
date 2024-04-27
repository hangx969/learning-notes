# 部署nfs

## 安装nfs供应商

- 上传安装包

```sh
#把nfs-subdir-external-provisioner.tar.gz上传到node1上，手动解压
docker load -i nfs-subdir-external-provisioner.tar.gz
```

- 创建运行nfs-provisioner需要的sa账号

```yaml
tee sa-nfs.yaml <<'EOF' 
apiVersion: v1
kind: ServiceAccount
metadata:
  name: nfs-provisioner

EOFtee sa-nfs.yaml <<'EOF' 
apiVersion: v1
kind: ServiceAccount
metadata:
  name: nfs-provisioner

EOF
```

- 对sa授权


```sh
#使nfs-provisioner具有管理员权限
kubectl create clusterrolebinding rb-nfs-provisioner --clusterrole=cluster-admin --serviceaccount=default:nfs-provisioner
```

- 安装nfs服务

```sh
#master和node上都安装nfs服务
yum install nfs-utils -y
#启动nfs服务
systemctl start nfs && systemctl enable nfs && systemctl status nfs
```

- nfs服务器上要手动划分出共享区域，以供后面nfs供应商使用

```sh
#master1上创建nfs的共享目录，master1作为nfs server
mkdir /data/nfs_pro -p
#修改nfs配置，划分共享空间
tee -a /etc/exports << 'EOF'
/data/nfs_pro *(rw,no_root_squash)
EOF
#使共享生效
exportfs -arv
systemctl restart nfs && systemctl status nfs
```

- 部署nfs-provisioner pod

~~~yaml
tee nfs-deployment.yaml <<'EOF' 
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
              value: example.com/nfs
            - name: NFS_SERVER
              value: 172.16.183.75
            - name: NFS_PATH
              value: /data/nfs_pro
      volumes:
        - name: nfs-client-root
          nfs:
            server: 172.16.183.75 #nfs源路径server的IP
            path: /data/nfs_pro
            
EOF
~~~

- 创建存储类

~~~yaml
tee sc-nfs.yaml <<'EOF' 
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: nfs
provisioner: example.com/nfs

EOF
~~~

# sts部署mysql高可用服务

