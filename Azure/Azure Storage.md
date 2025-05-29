# 存储类型

![image-20241214113847766](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202412141138840.png)

- 每一种存储类型的访问，都是要通过存储账户来进行

# 存储冗余

![image-20241214110808699](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202412141108871.png)

- LRS：本地冗余，单个数据中心内三份副本，读写的时候在三份里面balancing，但是数据中心故障会带来风险
- GRS：异地冗余，Region不同，主要区域存3个副本；向次要区域异步创建3个副本，但是次要区域的不能读写，除非是启动了故障转移
- RA-GRS：与GRS相比，次要区域的3个副本也是可读的
- ZRS：数据在同一个Region里面不同的Availability Zone里面进行备份，三个副本分布在三个Availability Zone里
- GZRS：在ZRS基础上，在另一个region上开启三个备份副本

# 存储账户终结点

存储帐户在 Azure 中为数据提供唯一的命名空间。 存储在 Azure 存储中的每个对象都有一个地址，其中包含唯一的帐户名称。 将帐户名称与 Azure 存储服务终结点组合在一起，即可构成适用于存储帐户的终结点。构造用于访问存储帐户中某个对象的 URL，方法是：将对象在存储帐户中的位置追加到终结点。 例如，blob 的 URL 类似于：`http://mystorageaccount.blob.core.chinacloudapi.cn/mycontainer/myblob`

# Azure Blob

- binary large object，是Azure的适用于云的对象存储解决方案，适用于存储大量二进制对象。使用场景：

  - 直接向浏览器提供图像和文档分布式访问

  - 视频音频流式处理

  - 备份 还原 灾难恢复 存档

  - Azure托管服务分析

- blob有三种类型：
  - block blob：存储文本和二进制数据
  - append blob：对追加操作进行了优化，适合存储来自虚拟机的数据
  - page blob：存储较大的随机访问文件，适合存储VHD作为VM的磁盘

## blob中的access tier

- Hot tier：适用频繁访问的数据
- Cool tier：不常使用但是要立刻访问的数据（短时备份和灾难恢复）至少存储30天
- archive access tier：离线层，对访问很少的数据进行了存储优化。要读取或修改，则要重新rehydrate到cool/hot tier。至少存储180天，否则额外收钱。

# Azure Managed Disk

- 是Azure托管，并与Azure VM一起使用的存储，类似于本地服务器中的物理磁盘，不过是虚拟化的。分为Premium SSD，standard SSD，standard HDD。

## disk功能种类

1. OS disk

预装了OS，包含启动卷

2. Data disk
3. Temporary disk

大部分VM都包含这个，它不是托管磁盘。用于存储系统分页文件（内存交换分区），是用宿主机上的disk，在Linux中通常为/dev/sdb，默认挂载点

位/mnt/resource，windows上通常会是D:\。在VM故障时，临时存储不会迁移。所以不能在临时存储中存放重要数据。

# 授权

## Access Key

- 创建存储帐户时，Azure 会生成两个 512 位存储帐户访问密钥。这些密钥可用于通过共享密钥授权来授予对你存储帐户中数据的访问权限。

- Access Keys相当于是根密码，可以获取**所有服务的所有访问权限**。

- 可以使用这两个密钥中的任何一个来访问 Azure 存储，但通常情况下，最好使用第一个密钥，并保留第二个密钥在轮换密钥时使用。

## SAS Token

- SAS可以授予对存储帐户中**container和****blob**的有限访问权限。创建 SAS 时，需要指定其约束条件，包括允许客户端访问哪些存储资源、资源具有哪些权限，以及SAS的有效期。

- SAS均使用access Keys进行签名，两种方式：

  - 使用AAD提供的keys进行签名，则称为用户委托SAS

  - 使用存储账户keys进行签名。服务SAS和账户SAS均使用存储账户签名

## management plane and data plane

- [控制平面和数据平面操作 - Azure 资源管理器|微软文档 (microsoft.com)](https://docs.microsoft.com/en-us/azure/azure-resource-manager/management/control-plane-and-data-plane)

# Logging

- 可以为blob queue和table启用分析日志，在portal -> diagnotics里面直接设置Logging，可以设置日志记录的内容，和保存时间
- 日志放在名为 $logs 的container中，可以用azcopy / explorer下载下来看
- 日志分析：

[存储分析日志格式 (REST API) - Azure 存储 | Microsoft Docs](https://docs.microsoft.com/zh-cn/rest/api/storageservices/storage-analytics-log-format)

[存储分析记录的操作和状态消息 (REST API) - Azure 存储 | Microsoft Docs](https://docs.microsoft.com/zh-cn/rest/api/storageservices/storage-analytics-logged-operations-and-status-messages)

[存储分析记录的操作和状态消息 (REST API) - Azure 存储 | Microsoft Docs](https://docs.microsoft.com/zh-cn/rest/api/storageservices/storage-analytics-logged-operations-and-status-messages)

- 使用powershell脚本将存储日志转换为

~~~powershell
$Columns = 
     (   "version-number",
         "request-start-time",
         "operation-type",
         "request-status",
         "http-status-code",
         "end-to-end-latency-in-ms",
         "server-latency-in-ms",
         "authentication-type",
         "requester-account-name",
         "owner-account-name",
         "service-type",
         "request-url",
         "requested-object-key",
         "request-id-header",
         "operation-count",
         "requester-ip-address",
         "request-version-header",
         "request-header-size",
         "request-packet-size",
         "response-header-size",
         "response-packet-size",
         "request-content-length",
         "request-md5",
         "server-md5",
         "etag-identifier",
         "last-modified-time",
         "conditions-used",
         "user-agent-header",
         "referrer-header",
         "client-request-id"
     )

$logs = Import-Csv "C:\Users\v-hangx.FAREAST\Desktop\000000.log" -Delimiter ";" -Header $Columns

$logs | Out-GridView -Title "Storage Analytic Log Parser"
~~~

# 性能分析

- 性能指标：
  - IOPS：每秒输入输出，应用程序每秒发送到存储磁盘的请求数。对于联机事务处理型（OLTP）程序，比如在线零售网站，对高并发的要求较高，是插入更新密集型数据库事务。对IOPS指标有要求。
  - 吞吐量（throughput）：应用程序在指定时间间隔内发送到磁盘的数据量。对于数据仓库应用，单次请求访问大量数据，是扫描密集型应用
  - IOPS和吞吐量之间存在如下关系：
    - IOPS * IO Size = 吞吐量

- IOPS分析工具：
  - 将 **PerfMon** 用于 Windows，将 **iostat** 用于 Linux [iostat(1) - Linux man page (die.net)](https://linux.die.net/man/1/iostat)，[性能计数器 - Win32 apps | Microsoft Docs](https://docs.microsoft.com/zh-cn/windows/win32/perfctrs/performance-counters-portal)

- 优化

  - IO请求是应用程序执行输入输出的操作单元。
    - 对于联机事务型，会产生大量随机IO；
    - 对于数仓型，产生大型顺序IO；
    - 要对应用程序结构进行设计。如果应用程序可以更改IO大小，可以降低IO size以提高IOPS：如对OLTP采用8KB的IO size；也可以提高IO size以提高吞吐量，如对数仓采用1024 KB的IO size

  - 缓存具有单独的IOPS和吞吐量，与VM size有关；随着读取时间的延长，缓存得到预热，可以为磁盘提供更多的IOPS和吞吐量。利用 Azure 高级存储的高规格 VM 使用名为 BlobCache 的多层缓存技术。Blob Cache 使用主机 RAM 和本地 SSD 的组合进行缓存。

# 缓存

缓存都是存储在物理节点宿主机上的disk，由Compute 计算资源提供，performance比较好

- ReadOnly：
  - 降低读取延迟，获得较高的IOPS和吞吐量。
  - 通过缓存执行的读取操作，发生在本地VM和本地SSD上，速度要远远快于从数据磁盘上的读取操作，后者发生在Blob上

- ReadWrite
  - OS默认开启
  - 采取适当方法将数据从缓存写入永久磁盘

- 无
  - 只有数据磁盘支持，OS磁盘不支持，若将OS盘缓存设为无，则会内部覆盖为ReadOnly

举例来说，可以通过执行以下操作将这些准则应用到在高级存储上运行的 SQL Server：

1. 在托管**数据文件**的高级存储磁盘上配置“ReadOnly”缓存。
   1.  从缓存快速读取可以缩短 SQL Server 查询时间，因为从缓存检索数据页的速度要大大快于直接从数据磁盘进行检索的速度。
   2. 从缓存进行读取意味着可以从高级数据磁盘获得更多的吞吐量。SQL Server 可以利用这额外的吞吐量来检索更多数据页和执行其他操作，例如备份/还原、批量加载以及索引重建。

2. 在托管**日志文件**的高级存储磁盘上将缓存配置为“无”。
   1. 日志文件主要是进行频繁的写入操作。因此，将缓存设置为ReadOnly 对其无用。

# 队列深度

- 队列深度和多线程处理密切相关。队列深度值表示应用程序可以实现的多线程处理的程度。如果队列深度很大，则应用程序可以并行执行更多的操作。
- 高队列深度可以让更多操作在磁盘上排队。 磁盘可以提前知道其队列中的下一个请求。 因此，磁盘可以提前计划操作，按最佳顺序对其进行处理。
- 队列深度值过高也有其缺点。如果队列深度值过高，则应用程序会尝试实现非常高的 IOPS，可能对应用程序延迟造成负面影响。以下公式显示了 IOPS、延迟和队列深度之间的关系：
  - IOPS * Latency = Queue Depth

- 条带化卷应保持足够高的队列深度，使得每个磁盘都有各自的高峰队列深度。 例如，应用程序所推送的队列深度为 2，条带中有四个磁盘。 两个 IO 请求会发送到两个磁盘中，剩下两个磁盘会处于空闲状态。 因此，将队列深度配置为让所有磁盘都能够处于繁忙状态。

# AKS上传文件到storage

## curl测试pod连接storage

~~~sh
kubectl run curl-testing --image curl:latest  --image-pull-policy=IfNotPresent --restart=Never --rm -it curl-testing -- curl "https://<sa name>.blob.core.chinacloudapi.cn/<container name>/<file name>?<sas>"
curl: (7) Failed to connect to curl-testing port 80: Connection refused
curl: (6) Could not resolve host: curl
########################################
## Testing Connection Success
########################################
~~~

## 上传文件的方案--azcopy

### VM中测试

- apt安装azcopy：https://learn.microsoft.com/zh-cn/azure/storage/common/storage-use-azcopy-v10?tabs=apt#install-azcopy-on-linux-by-using-a-package-manager

~~~sh
#curl -sSL -O https://packages.microsoft.com/config/ubuntu/22.04/packages-microsoft-prod.deb
#dpkg -i packages-microsoft-prod.deb && rm packages-microsoft-prod.deb
#apt-get update && apt-get install azcopy
wget -O azcopy_v10.tar.gz https://aka.ms/downloadazcopy-v10-linux && tar -xf azcopy_v10.tar.gz --strip-components=1
~~~

- 上传文件，不带sas -- 失败 需要认证

~~~sh
./azcopy copy 'test.log' 'https://<sa name>.blob.core.chinacloudapi.cn/<container name>/test.log'
~~~

- 上传文件，带container level的sas -- 成功

~~~sh
./azcopy copy 'test.log' 'https://<sa name>.blob.core.chinacloudapi.cn/<container name>?<sas>'
~~~

- 上传文件，用vm的system-assigned identity

  - 给identity赋予storage account的storage blob contributor

  - 直接上传文件无需sas token

    ~~~sh
    ./azcopy copy 'test.log' 'https://<sa name>.blob.core.chinacloudapi.cn/<container name>'
    ~~~

### AKS pod中测试

- 先在pod中获取到azcopy -- busybox和alpine的image下载了azcopy之后均无法运行

  ~~~sh
  kubectl run apline --image apline:latest  --image-pull-policy=IfNotPresent --restart=Never --rm -it -- sh
  ~~~

- 尝试ubuntu，容器有root -- 成功

  ~~~sh
  kubectl run ubuntu --image ubuntu:22.04  --image-pull-policy=IfNotPresent --restart=Never --rm -it -- /bin/bash
  
  ./azcopy login --identity --identity-client-id <client id>
  #这里用aks的kubelet identity，sa层面赋予Storage Blob Contributor角色
  #测试上传
  echo "tesetingfromakspod" >> test.log
  ./azcopy copy 'test.log' 'https://<sa name>.blob.core.chinacloudapi.cn/<container name>'
  ~~~

  - aks kubelet identity: https://techcommunity.microsoft.com/t5/fasttrack-for-azure/aks-review-2-1-identity-amp-access-control-cluster-operator-amp/ba-p/3716906

- pod中运行的完整命令


~~~sh
apt-get update && apt-get install -y wget
wget -O azcopy_v10.tar.gz https://aka.ms/downloadazcopy-v10-linux && tar -xf azcopy_v10.tar.gz --strip-components=1
./azcopy login --identity --identity-client-id <client-id> #--aad-endpoint https://login.partner.microsoftonline.cn
./azcopy copy '<file name>' 'https://<sa name>.blob.core.chinacloudapi.cn/<container name>'
~~~

### workload identity with azcopy

前面是用kubelet identity。尝试用workload identity登录azcopy(直接挂service account就行，不需要指定uai id)

azcopy 10.25+已经support login with workload identity： 

- https://github.com/Azure/azure-storage-azcopy/issues/2545#issuecomment-2136833573
- azcopy环境变量说明： https://learn.microsoft.com/zh-cn/azure/storage/common/storage-ref-azcopy-configuration-settings?toc=%2Fazure%2Fstorage%2Fblobs%2Ftoc.json&bc=%2Fazure%2Fstorage%2Fblobs%2Fbreadcrumb%2Ftoc.json#azcopy-v10-environment-variables

```yaml
tee pod-wi-ubuntu.yaml <<'EOF'
---
apiVersion: v1
kind: Pod
metadata:
  name: pod-test-wi
  namespace: <ns name>
  labels:
    azure.workload.identity/use: "true"
spec:
  serviceAccountName: <sa name>
  containers:
    - name: ubuntu
      image: ubuntu:22.04
      command: ["/bin/sh"]
      args: ["-c", "while true; do echo hello; sleep 10;done"]
      env:
      - name: STORAGE_ACCOUNT_NAME
        value: <sa name>
      - name: STORAGE_CONTAINER_NAME
        value: <container name>
      - name: AZCOPY_AUTO_LOGIN_TYPE
        value: WORKLOAD
EOF

##job的yaml需要添加的字段##
#1. 加一个label
  labels:
    azure.workload.identity/use: "true"
    
#2. 加环境变量
env:
- name: STORAGE_ACCOUNT_NAME
  value: <sa name>
- name: STORAGE_CONTAINER_NAME
  value: <container name>
- name: AZCOPY_AUTO_LOGIN_TYPE
  value: WORKLOAD
  
#3. job的command改成下面:
apt-get update && apt-get install -y wget
wget -O azcopy_v10.tar.gz https://aka.ms/downloadazcopy-v10-linux && tar -xf azcopy_v10.tar.gz --strip-components=1
./azcopy copy '<file name>' 'https://<sa name>.blob.core.chinacloudapi.cn/<container name>' --put-md5
```

> - azure blob的md5，对于大文件上传时需要手动指定：
>
>   https://learn.microsoft.com/en-us/answers/questions/282572/md5-hash-calculation-for-large-files
>
>   https://technet2.github.io/Wiki/blogs/windowsazurestorage/windows-azure-blob-md5-overview.html
>
>   https://azure.rvr.cloud/azcopy-sync.html

### workload identity with az login

- directly install az cli in main container (up to 700 MB will be installed, too big, the pod will crash during installation)

  https://learn.microsoft.com/zh-cn/cli/azure/install-azure-cli-linux?pivots=apt

- sidecar container

  https://learn.microsoft.com/zh-cn/cli/azure/run-azure-cli-docker

``` yaml
tee pod-sidecar.yaml <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: pod-test-wi
  namespace: mapapps
  labels:
    azure.workload.identity/use: "true"
spec:
  serviceAccountName: <sa name>
  containers:
    - name: ubuntu
      image: ubuntu:22.04
      imagePullPolicy: IfNotPresent
      command:
      - /bin/sh
      - -c
      - >
        while true; do echo hello >> /mnt/test.txt; sleep 10; done
      volumeMounts:
      - name: localstorage
        mountPath: /mnt
    - name: sidecar-azlogin
      image: azure-cli:cbl-mariner2.0
      command:
      - /bin/sh
      - -c
      - |
        az login --service-principal -u $AZURE_CLIENT_ID -t $AZURE_TENANT_ID --federated-token $AZURE_FEDERATED_TOKEN_FILE && \
        az storage blob upload --account-name <sa name> --container-name <container name> --name test.txt --file /mnt/test.txt
      volumeMounts:
      - name: localstorage
        mountPath: /mnt
  volumes:
  - name: localstorage
    emptyDir: {}
EOF
```

> - 每个pod都有wi的环境变量
>
>   ```sh
>   Environment:
>         AZURE_CLIENT_ID:             <client id>
>         AZURE_TENANT_ID:             <tenant id>
>         AZURE_FEDERATED_TOKEN_FILE:  /var/run/secrets/azure/tokens/azure-identity-token
>         AZURE_AUTHORITY_HOST:        https://login.chinacloudapi.cn
>   ```
>
> - login command
>
>   https://github.com/Azure/azure-cli/issues/24756
>
>   ```sh
>   az cloud set --name AzureChinaCloud && az login --service-principal --username "${AZURE_CLIENT_ID}" --tenant "${AZURE_TENANT_ID}" --federated-token "$(cat $AZURE_FEDERATED_TOKEN_FILE)" 
>   ```
>
> - upload command
>
>   ```sh
>   az storage blob upload --account-name <sa name> --container-name <container name> --name test.txt --file /mnt/test.txt --auth-mode login
>   ```

```yaml
#azcli pod单独测试
tee pod-azcli.yaml <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: pod-test-azcli
  namespace: <ns name>
  labels:
    azure.workload.identity/use: "true"
spec:
  serviceAccountName: <sa name>
  containers:
    - name: sidecar-azlogin
      image: azure-cli:cbl-mariner2.0
      command: ["/bin/sh"]
      args: ["-c", "while true; do echo hello; sleep 10;done"]
EOF
```

> issue: MS提供的azcli container运行az命令会直接崩溃，原因是container的cpu memory需要指定稍微大一些：request 200m cpu和500Mi memory即可运行。

## 上传文件的方案 -- pv挂载blob

- 创建secret

~~~sh
kubectl create secret generic <secret name> --from-literal sazurestorageaccountname=<sa name> --from-literal azurestorageaccountkey="<key value>" --type=Opaque
~~~

- 创建PV

~~~yaml
tee pv-download.yaml <<'EOF'
apiVersion: v1
kind: PersistentVolume
metadata:
  annotations:
    pv.kubernetes.io/provisioned-by: blob.csi.azure.com
  name: pv-blob-download
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain  # If set as "Delete" container would be removed after pvc deletion
  storageClassName: managed-blobfuse-premium-lrs
  mountOptions:
    - -o allow_other
    - --file-cache-timeout-in-seconds=120
  csi:
    driver: blob.csi.azure.com
    # volumeid has to be unique for every identical storage blob container in the cluster
    # character `#`and `/` are reserved for internal use and cannot be used in volumehandle
    volumeHandle: <handle name>
    volumeAttributes:
      containerName: <container name>
    nodeStageSecretRef:
      name: <secret name>
      namespace: default
EOF
~~~

- 创建PVC

~~~yaml
tee pvc-download.yaml <<'EOF'
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-blob-download
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 10Gi
  volumeName: pv-blob-download
  storageClassName: managed-blobfuse-premium-lrs
EOF
~~~

### workload identity with pv

- 测试简单pod挂载

~~~yaml
tee pod-wi-ubuntu.yaml <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: pod-test-wi
  namespace: <ns name>
  labels:
    azure.workload.identity/use: "true"
spec:
  serviceAccountName: <sa name>
  containers:
    - name: ubuntu
      image: ubuntu:22.04
      command: ["/bin/sh"]
      args: ["-c", "while true; do echo hello; sleep 10;done"]
EOF

k exec -it pod-test-wi -n <ns name> -- /bin/bash
#查看token
cat /run/secrets/azure/tokens/azure-identity-token
~~~

- 测试job挂载blob 

pv:

~~~yaml
tee pv-upload.yaml <<'EOF'
apiVersion: v1
kind: PersistentVolume
metadata:
  annotations:
    pv.kubernetes.io/provisioned-by: blob.csi.azure.com
  name: pv-blob-upload
  namespace: <ns name>
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain  # If set as "Delete" container would be removed after pvc deletion
  storageClassName: managed-blobfuse-premium-lrs
  mountOptions:
    - -o allow_other
    - --file-cache-timeout-in-seconds=120
  csi:
    driver: blob.csi.azure.com
    # volumeid has to be unique for every identical storage blob container in the cluster
    # character `#`and `/` are reserved for internal use and cannot be used in volumehandle
    volumeHandle: <handle name>
    volumeAttributes:
      storageAccount: <sa name>
      containerName: <container name>
      AzureStorageAuthType: MSI
      AzureStorageIdentityClientID: <client id>
      AzureStorageIdentityResourceID: <uai id>
      #MSIEndpoint: 
EOF
~~~

pvc:

~~~yaml
tee pvc-download.yaml <<'EOF'
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-blob-upload
  namespace: <ns name>
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 10Gi
  volumeName: pv-blob-upload
  storageClassName: managed-blobfuse-premium-lrs
EOF
~~~

测试动态预配pv:

~~~yaml
tee pod-wi-ubuntu.yaml <<'EOF'
---
apiVersion: v1
kind: Pod
metadata:
  name: pod-test-wi
  namespace: <ns name>
  labels:
    azure.workload.identity/use: "true"
spec:
  serviceAccountName: <sa name>
  containers:
    - name: ubuntu
      image: ubuntu:22.04
      command: ["/bin/sh"]
      args: ["-c", "while true; do echo hello; sleep 10;done"]
      volumeMounts:
        - name: storage
          mountPath: /mnt/storage
  volumes:
    - name: storage
      persistentVolumeClaim:
        claimName: pvc-blob-upload

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-blob-upload
  namespace: <ns name>
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 10Gi
  storageClassName: managed-blobfuse-premium-lrs
EOF
~~~

# 下载文件-获取md5

- 看一下container level的sas token怎么做到下载文件？

  直接url后缀加上文件名即可。需要两边同步好文件名

- 看一下blob md5的值怎么获取？

  sas url的reponse header里就带着了，”Content-MD5”字段，curl -i就能直接查看

  ![image-20241010170509800](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202410101725170.png)

~~~sh
curl -i "https://<sa name>.blob.core.chinacloudapi.cn/<container name>/values.yaml?xxxxxxxxxx"
HTTP/1.1 200 OK
Content-Length: 111
Content-Type: application/x-yaml
Content-MD5: +s1+xxxxxxxxxxxxxxxxxx
Last-Modified: Tue, 08 Oct 2024 03:25:34 GMT
Accept-Ranges: bytes
ETag: "xxx"
Server: Windows-Azure-Blob/1.0 Microsoft-HTTPAPI/2.0
x-ms-request-id: xxxx
x-ms-version: 2022-11-02
x-ms-creation-time: Fri, 27 Sep 2024 06:50:32 GMT
x-ms-lease-status: unlocked
x-ms-lease-state: available
x-ms-blob-type: BlockBlob
x-ms-server-encrypted: true
~~~

# 自动化下载blob脚本建议

相关背景说明：

1. 文件上传到azure storage account存储中，每次更新都会在同一目录下创建新的blob文件以供下载。
2. 基于此，提供一个目录级别的长期有效的SAS Token。可以用这个SAS Token来list出目录中所有文件，以及每个文件的创建时间、MD5校验值等。

使用SAS Token来list所有文件及信息的方法：

1. 提供一个格式如下的SAS URL：

~~~sh
https://<sa name>.blob.core.chinacloudapi.cn/<container name>?sp=rl&st=2024-10-11T06:04:27Z&se=2024-10-11T14:04:27Z&sip=101.95.105.42&spr=https&sv=2022-11-02&sr=c&sig=xxx
~~~

其中：

- “https://<sa name>.blob.core.chinacloudapi.cn/<container>”部分是存储目录的路径
- “sp=rl&st=2024-10-11T06:04:27Z&se=2024-10-11T14:04:27Z&sip=101.95.105.42&spr=https&sv=2022-11-02&sr=c&sig=xxx”部分是SAS Token的值。

2. 可以在目录路径和SAS Token中间添加“**restype=container&comp=list&**”参数，来获取到目录下所有文件及信息。

   - 拼接后的URL为：“https://<sa name>.blob.core.chinacloudapi.cn/<container name>?restype=container&comp=list&sp=rl&st=2024-10-11T06:04:27Z&se=2024-10-11T14:04:27Z&sip=101.95.105.42&spr=https&sv=2022-11-02&sr=c&sig=xxx”

   - 请求命令示例：

     ~~~sh
     curl -X GET “https://<sa name>.blob.core.chinacloudapi.cn/<container name>?restype=container&comp=list&sp=rl&st=2024-10-11T06:04:27Z&se=2024-10-11T14:04:27Z&sip=101.95.105.42&spr=https&sv=2022-11-02&sr=c&sig=xxx”
     ~~~

   - 返回值为xml格式，示例：

     ~~~xml
     <?xml version="1.0" encoding="utf-8"?>
     <EnumerationResults ServiceEndpoint="https://<sa name>.blob.core.chinacloudapi.cn/" ContainerName="<container name>">
         <Blobs>
             <Blob>
                 <Name>test.log</Name>
                 <Properties>
                     <Creation-Time>Tue, 08 Oct 2024 08:33:51 GMT</Creation-Time>
                     <Last-Modified>Thu, 10 Oct 2024 08:17:07 GMT</Last-Modified>
                     <Etag>xxx</Etag>
                     <Content-Length>19</Content-Length>
                     <Content-Type>text/plain</Content-Type>
                     <Content-Encoding />
                     <Content-Language />
                     <Content-CRC64 />
                     <Content-MD5>xxx</Content-MD5>
                     <Cache-Control />
                     <Content-Disposition />
                     <BlobType>BlockBlob</BlobType>
                     <AccessTier>Hot</AccessTier>
                     <AccessTierInferred>true</AccessTierInferred>
                     <LeaseStatus>unlocked</LeaseStatus>
                     <LeaseState>available</LeaseState>
                     <ServerEncrypted>true</ServerEncrypted>
                 </Properties>
                 <OrMetadata />
             </Blob>
         <NextMarker />
     </EnumerationResults>
     ~~~


   使用SAS URL来下载文件的方法：

   1. 在提供的SAS URL的container路径后面加上前一个步骤获取到的blob文件名即可，例如：     

   ```sh
   curl "https://<sa name>.blob.core.chinacloudapi.cn/<container name>/test.log?sp=rl&st=2024-10-11T06:04:27Z&se=2024-10-11T14:04:27Z&sip=101.95.105.42&spr=https&sv=2022-11-02&sr=c&sig=xxx"
   ```

   # 