> 注：
>
> - 如果需要mysq对性能要求很高，建议不要在k8s中部署，还是建议直接在服务器上部署

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
EOF

kubectl apply -f sa-nfs.yaml
```

- 对sa授权


```sh
#使nfs-provisioner具有管理员权限
kubectl create clusterrolebinding rb-nfs-provisioner --clusterrole=cluster-admin --serviceaccount=default:nfs-provisioner
```

- 安装nfs服务

```sh
#master和node上都安装并启动nfs服务
yum install nfs-utils -y
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
              value: 192.168.40.180
            - name: NFS_PATH
              value: /data/nfs_pro
      volumes:
        - name: nfs-client-root
          nfs:
            server: 192.168.40.180 #nfs源路径server的IP
            path: /data/nfs_pro        
EOF
kubectgl apply -f nfs-deployment.yaml
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
kubectl apply -f sc-nfs.yaml
~~~

# sts部署mysql高可用服务

## mysql简介

- MySQL是一种关系型数据库管理系统，关系数据库将数据保存在不同的表中，而不是将所有数据放在一个大仓库内，这样就增加了速度并提高了灵活性。MySQL所使用的 SQL 语言是用于访问数据库的最常用标准化语言。MySQL 软件采用了双授权政策，分为社区版和商业版，由于其体积小、速度快、总体拥有成本低，尤其是开放源码这一特点，一般中小型网站的开发都选择 MySQL 作为网站数据库。

- mysql高可用方案

  - MySQL高可用方案采用主从复制+读写分离，即由单一的master和多个slave所构成。
  - 客户端通过master对数据库进行写操作，通过slave端进行读操作。master出现问题后，可以将应用切换到slave端。
  - 此方案是MySQL官方提供的一种高可用解决方案，节点间的数据同步采用MySQL Replication技术。MySQL Replication从一个MySQL master的数据复制到一个或多个MySQL slave。
  - 在默认情况下，复制是异步的；slave不需要一直接收来自主机的更新。根据配置，可以复制数据库中的所有数据库、选定的数据库，或者特定的表。

  ![image-20240428092946740](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202404280931707.png)

## 部署configMap

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
kubectl apply -f mysql-configmap.yaml
~~~

## 部署svc

- 创建svc，需要两个svc：mysql和mysql-read

~~~yaml
tee svc-mysql.yaml <<'EOF'
apiVersion: v1
kind: Service
metadata:
  name: mysql
  labels:
    app: mysql
spec:
  ports:
  - name: mysql
    port: 3306
  clusterIP: 'None'
  selector:
    app: mysql
---
apiVersion: v1
kind: Service
metadata:
  name: mysql-read
  labels:
    app: mysql
spec:
  ports:
  - name: mysql
    port: 3306
  selector:
    app: mysql
EOF
kubectl apply -f svc-mysql.yaml
##statefulSet下的Pod有DNS地址,通过解析Pod的DNS可以返回Pod的IP。
##用户所有写请求，必须以 DNS 记录的方式直接访问到 Master 节点，也就是 mysql-0.mysql 这条DNS记录。用户所有读请求需要访问mysql-read 这条DNS记录。
~~~

## 部署mysql sts

- 准备镜像，注意镜像要上传到工作节点

~~~sh
docker load -i mysql-5-7.tar.gz
docker load -i xtrabackup-1-0.tar.gz
~~~

- 通过sts部署mysql

~~~yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
spec:
  selector:
    matchLabels:
      app: mysql
  serviceName: mysql
  replicas: 3
  volumeClaimTemplates:
  - metadata:
      name: data
      annotations:
        volume.beta.kubernetes.io/storage-class: "nfs"
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 2Gi
  template:
    metadata:
      labels:
        app: mysql
    spec:
      initContainers:  #定义一个初始化容器
      - name: init-mysql
        image: mysql:5.7
        imagePullPolicy: IfNotPresent
        command:
        - bash
        - "-c"
        - |
          set -ex
          #从pod的序号，生成server-id
          [[ `hostname` =~ -([0-9]+)$ ]] || exit 1
          ordinal=${BASH_REMATCH[1]}
          echo [mysqld] > /mnt/conf.d/server-id.cnf
          #由于server-id不能为0，因此给id+100避开
          echo server-id=$((100 + $ordinal)) >> /mnt/conf.d/server-id.cnf
          # 如果 Pod 的序号为 0，说明它是 Master 节点，从 ConfigMap 里把 Master 的配置文件拷贝到 /mnt/conf.d 目录下
          # 否则，拷贝 ConfigMap 里的 Slave 的配置文件
          if [[ $ordinal -eq 0 ]]; then
            cp /mnt/config-map/master.cnf /mnt/conf.d/
          else
            cp /mnt/config-map/slave.cnf /mnt/conf.d/
          fi
        volumeMounts:
        - name: conf
          mountPath: /mnt/conf.d
        - name: config-map
          mountPath: /mnt/config-map
      - name: clone-mysql
        image: xtrabackup:1.0
        command:
        - bash
        - "-c"
        - |
          set -ex
          # 拷贝操作只需要在第一次启动时进行，数据已经存在则跳过
          [[ -d /var/lib/mysql/mysql ]] && exit 0
          # Master 节点（序号为 0）不需要这个操作
          [[ `hostname` =~ -([0-9]+)$ ]] || exit 1
          ordinal=${BASH_REMATCH[1]}
          [[ $ordinal -eq 0 ]] && exit 0
          #使用 ncat 指令，远程地从前一个节点拷贝数据到本地
          ncat --recv-only mysql-$(($ordinal-1)).mysql 3307 | xbstream -x -C /var/lib/mysql
          # 执行 --prepare，这样拷贝来的数据就可以用作恢复
          xtrabackup --prepare --target-dir=/var/lib/mysql
        volumeMounts:
        - name: data
          mountPath: /var/lib/mysql
          subPath: mysql
        - name: conf
          mountPath: /etc/mysql/conf.d
      containers:
      - name: mysql
        image: mysql:5.7
        imagePullPolicy: IfNotPresent
        env:
        - name: MYSQL_ALLOW_EMPTY_PASSWORD
          value: "1"
        ports:
        - name: mysql
          containerPort: 3306
        volumeMounts:
        - name: data
          mountPath: /var/lib/mysql
          subPath: mysql
        - name: conf
          mountPath: /etc/mysql/conf.d
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
        livenessProbe:
          exec:
            command: ["mysqladmin", "ping"]
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
        readinessProbe:
          exec:
            command: ["mysql", "-h", "127.0.0.1", "-e", "SELECT 1"]
          initialDelaySeconds: 5
          periodSeconds: 2
          timeoutSeconds: 1
      - name: xtrabackup
        image: xtrabackup:1.0
        imagePullPolicy: IfNotPresent
        ports:
        - name: xtrabackup
          containerPort: 3307
        command:
        - bash
        - "-c"
        - |
          set -ex
          cd /var/lib/mysql
          #从备份信息文件里读取 MASTER_LOG_FILE 和 MASTER_LOG_POS 这 2 个字段的值，用来拼装集群初始化SQL
          if [[ -f xtrabackup_slave_info ]]; then
          # 如果xtrabackup_slave_info文件存在，说明这个备份数据来自于另一个Slave节点，则XtraBackup在备份的时候，就已经在这个文件里自动生成了 "CHANGE MASTER TO" SQL 语句，所以，只需要把这个文件重命名为change_master_to.sql.in，后面直接使用即可，所以用不到xtrabackup_binlog_info 了。
            mv xtrabackup_slave_info change_master_to.sql.in
            rm -f xtrabackup_binlog_info
          elif [[ -f xtrabackup_binlog_info ]]; then
          #如果只是存在xtrabackup_binlog_info 文件，说明备份来自于 Master 节点，就需要解析这个备份信息文件，读取所需的两个字段的值
            [[ `cat xtrabackup_binlog_info` =~ ^(.*?)[[:space:]]+(.*?)$ ]] || exit 1
            rm xtrabackup_binlog_info
           # 把两个字段的值拼装成 SQL，写入 change_master_to.sql.in 文件
            echo "CHANGE MASTER TO MASTER_LOG_FILE='${BASH_REMATCH[1]}',\
                  MASTER_LOG_POS=${BASH_REMATCH[2]}" > change_master_to.sql.in
          fi
          #如果存在 change_master_to.sql.in，就意味着需要做集群初始化工作
          if [[ -f change_master_to.sql.in ]]; then
          #但一定要先等 MySQL 容器启动之后才能进行下一步连接 MySQL 的操作
            echo "Waiting for mysqld to be ready (accepting connections)"
            until mysql -h 127.0.0.1 -e "SELECT 1"; do sleep 1; done
            echo "Initializing replication from clone position"
            #将文件change_master_to.sql.in改名，防止这个 Container 重启的时候，因为又找到了 change_master_to.sql.in，从而重复执行一遍初始化流程
            mv change_master_to.sql.in change_master_to.sql.orig
            #使用 change_master_to.sql.orig 的内容，也就是前面拼装的 SQL，组成一个完整的初始化和启动 Slave 的 SQL 语句
            mysql -h 127.0.0.1 <<EOF
          $(<change_master_to.sql.orig),
            MASTER_HOST='mysql-0.mysql',
            MASTER_USER='root',
            MASTER_PASSWORD='',
            MASTER_CONNECT_RETRY=10;
          START SLAVE;
          EOF
          fi
          #使用ncat监听3307 端口。
          #它的作用是，在收到传输请求的时候，直接执行xtrabackup --backup 命令，备份 MySQL的数据并发送给请求者
          exec ncat --listen --keep-open --send-only --max-conns=1 3307 -c \
            "xtrabackup --backup --slave-info --stream=xbstream --host=127.0.0.1 --user=root"
        volumeMounts:
        - name: data
          mountPath: /var/lib/mysql
          subPath: mysql
        - name: conf
          mountPath: /etc/mysql/conf.d
        resources:
          requests:
            cpu: 100m
            memory: 100Mi
      volumes:
      - name: conf
        emptyDir: {}
      - name: config-map
        configMap:
          name: mysql
~~~

> xtrabackup容器启动命令解释：
>
> 首先通过检查备份信息文件（如 xtrabackup_slave_info 和 xtrabackup_binlog_info）来确定备份的来源，然后根据不同情况分别处理这些备份信息。
>
> 具体实现步骤如下：
>
> 1. 如果存在 xtrabackup_slave_info 文件，则将其重命名为 change_master_to.sql.in，然后删除 xtrabackup_binlog_info 文件。
> 2. 如果只存在 xtrabackup_binlog_info 文件，则解析该文件中的备份信息，并将其拼装成相应的 SQL 语句，写入 change_master_to.sql.in 文件中。
> 3. 如果存在 change_master_to.sql.in 文件，则等待 MySQL 容器启动，然后执行相应的初始化和启动 Slave 的 SQL 语句。
> 4. 最后，使用 ncat 监听 3307 端口，当接收到传输请求时，执行 xtrabackup 命令，备份 MySQL 的数据并发送给请求者。
> 5. 因此，该代码的主要功能是根据备份信息来实现集群初始化、启动 Slave，以及在接收传输请求时备份 MySQL 数据。

## 验证高可用方案

~~~sh
#上传mysql镜像到node1
docker load -i mysql-5-7.tar.gz
#运行一个临时的容器(使用mysql:5.7镜像)，使用MySQL客户端发送测试请求给MySQL master节点（主机名为mysql-0.mysql；跨命名空间的话，主机名使用mysql-0.mysql）
kubectl run mysql-client --image=mysql:5.7 -it --rm --restart=Never -- mysql -h mysql-0.mysql
#在mysql的master节点上创建demo数据库，并创建一个只有message字段的demo.messages的表，并为message字段插入hello值。
mysql> CREATE DATABASE demo;
Query OK, 1 row affected (0.01 sec)、

mysql> CREATE TABLE demo.messages (message VARCHAR(250));
Query OK, 0 rows affected (0.02 sec)

mysql> INSERT INTO demo.messages VALUES ('hello');
Query OK, 1 row affected (0.01 sec)
mysql>exit

#2）登录mysql的从数据库
kubectl run mysql-client --image=mysql:5.7 -it --rm --restart=Never -- mysql -h mysql-1.mysql
mysql> select * from demo.messages;
mysql> show slave status\G
~~~

# 搭建简单测试用mysql

~~~yaml
---
apiVersion: v1
kind: Service
metadata:
  name: mysql-cluster
spec:
  selector:
    app: mysql
  ports:
  - name: mysql
    port: 3306
    targetPort: 3306
  clusterIP: None
  type: ClusterIP
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql-cluster
spec:
  serviceName: mysql-cluster
  replicas: 3
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        ports:
        - containerPort: 3306
        env:
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: mysql-root-password
        volumeMounts:
        - name: mysql-data
          mountPath: /var/lib/mysql
        readinessProbe:
          exec:
            command:
            - sh
            - -c
            - "mysql --user=root --password=$(MYSQL_ROOT_PASSWORD) --execute='SELECT 1'"
          initialDelaySeconds: 5
          periodSeconds: 5
  volumeClaimTemplates:
  - metadata:
      name: mysql-data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 10Gi

---
apiVersion: v1
kind: Secret
metadata:
  name: mysql-secret
type: Opaque
data:
  mysql-root-password: cGFzc3dvcmQ= # password, base64 encoded
~~~

# 搭建简单oracle服务

~~~yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: oracle-pv
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: "/mnt/data"
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: oracle-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: oracle-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: oracle
  template:
    metadata:
      labels:
        app: oracle
    spec:
      containers:
      - name: oracle
        image: oracle/database:12.2.0.1-ee
        ports:
        - containerPort: 1521
        volumeMounts:
        - name: oracle-data
          mountPath: /ORCL
      volumes:
      - name: oracle-data
        persistentVolumeClaim:
          claimName: oracle-pvc
~~~

