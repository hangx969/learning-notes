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