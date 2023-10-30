# Diskspd



## 教程

[在 Azure 磁盘存储上对应用程序进行基准测试 - Azure Virtual Machines | Microsoft Learn](https://learn.microsoft.com/zh-cn/azure/virtual-machines/disks-benchmarks#diskspd)

[Benchmark your application on Azure Disk Storage - Azure Virtual Machines | Microsoft Learn](https://learn.microsoft.com/en-us/azure/virtual-machines/disks-benchmarks)

## 压测

- 测试max Read IOPS

![image-20231030171446532](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310301714709.png)

- 测试max read IOPS

![image-20231030171457642](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310301714808.png)

- 测试max吞吐量
  - block size要设的大一点

![image-20231030171508132](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310301715276.png)

## 压测与perfmon配合使用

- 使用管理员权限打开CMD窗口，配置Perfmon信息：

  ```bash
  Logman create counter Perf-2Second -f bincirc -max 500 -c "\LogicalDisk(*)\*" "\Memory\*" "\Network Interface(*)\*" "\Paging File(*)\*" "\PhysicalDisk(*)\*" "\Server\*" "\System\*" "\Process(*)\*" "\Processor(*)\*" "\Cache\*" -si 00:00:02 -o C:\PerfMonLogs\Perf-2Second.blg 
  ```

- 开启Perfmon：

  ```bash
  Logman start Perf-2Second
  ```

- 在Diskspd - amd64路径下打开cmd窗口，运行以下命令，开始执行压测：

  ```bash
  .\diskspd.exe -c200G -w0 -b8K -F16 -r -o128 -d60 -Sh D:\testfile.dat
  #其中，D:\ 替换为需要测试的磁盘的盘符
  ```

- 压测结束后，命令行中会输出本次压测相关数据。此时，停止Perfmon：

  ```bash
  Logman stop Perf-2Second
  ```

# **FIO**

[Benchmark your application on Azure Disk Storage - Azure Virtual Machines | Microsoft Learn](https://learn.microsoft.com/en-us/azure/virtual-machines/disks-benchmarks#fio)

#  iotop / ps / top

## 实时查看io情况

1、top -i  

2、ps -e -o pid,user,%mem,cmd  --sort=-%mem  

## iotop脚本

- 脚本监控：使用iotop命令来监测服务器的状态，这样当问题重现时，我们可以对比发生问题的进程来进行排查。您可创建一个cron job在每分钟来收集一下I/O信息，并将其保存在日志文件中。例如：  

  - 创建/etc/cron.d/iotop文件，并添加以下内容。  

    ```bash
    vi /etc/cron.d/iotop  
    root /usr/sbin/iotop -botqqqk --iter=60 | grep -P "\d\d\.\d\d K/s"  >>/tmp/io.log 2>&1  
    #注：日志文件会不断增长，如果问题一直没有发生，请注意清理该文件。 
    ```

