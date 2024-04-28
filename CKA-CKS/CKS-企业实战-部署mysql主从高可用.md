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

## mysql

- MySQL是一种关系型数据库管理系统，关系数据库将数据保存在不同的表中，而不是将所有数据放在一个大仓库内，这样就增加了速度并提高了灵活性。MySQL所使用的 SQL 语言是用于访问数据库的最常用标准化语言。MySQL 软件采用了双授权政策，分为社区版和商业版，由于其体积小、速度快、总体拥有成本低，尤其是开放源码这一特点，一般中小型网站的开发都选择 MySQL 作为网站数据库。

- mysql高可用方案

  - MySQL高可用方案采用主从复制+读写分离，即由单一的master和多个slave所构成。
  - 客户端通过master对数据库进行写操作，通过slave端进行读操作。master出现问题后，可以将应用切换到slave端。
  - 此方案是MySQL官方提供的一种高可用解决方案，节点间的数据同步采用MySQL Replication技术。MySQL Replication从一个MySQL master的数据复制到一个或多个MySQL slave。
  - 在默认情况下，复制是异步的；slave不需要一直接收来自主机的更新。根据配置，可以复制数据库中的所有数据库、选定的数据库，或者特定的表。

  ![image-20240428092946740](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202404280931707.png)

## 部署mysql

- 创建configmap

~~~yaml
tee mysql-configmap.yaml <<'EOF' 
apiVersion: v1
kind: ConfigMap
metadata:
  name: mysql
  labels:
    app: mysql
data:
  master.cnf: |
    [mysqld]
    log-bin
    log_bin_trust_function_creators=1
    lower_case_table_names=1
  slave.cnf: |
    [mysqld]
    super-read-only
    log_bin_trust_function_creators=1
EOF
~~~

- 创建svc
