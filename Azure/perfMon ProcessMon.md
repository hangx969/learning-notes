---
title: PerfMon & ProcessMon
tags:
  - azure/tools
  - azure/monitoring
  - azure/performance
  - azure/disk
aliases:
  - Performance Monitor
  - Process Monitor
  - PerfMon
  - ProcMon
date: 2026-04-16
---

# PerfMon & ProcessMon

> [!summary] Windows performance monitoring and process tracing tools
> Used alongside [[Azure/IO-monitor|IO Monitor]] tools for disk benchmarking and troubleshooting on [[Azure/5_Azure-Storage|Azure Storage]].

---

## PerfMon

Download - https://docs.microsoft.com/en-us/sysinternals/downloads/procmon

![image-20231030172435694](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310301724780.png)

### Lab

> [!example] Disk Benchmarking Lab with PerfMon
> The instructor will provide the following instructions:
>
> 1. Attach ==4 Data Disks== (Standard_SSD) on a Windows VM (==A2_v2== size), 32 GiB each.
> 2. Create a ==Virtual Disk== using Storage Spaces, by combining the 4 disks with Simple (striping) layout.
> 3. Run disk benchmarking (i.e.: DiskSpd) tests with below commands:

```bash
diskspd.exe -c1024M -d10 -W5 -o1 -t1 -b8k -r -Sh -L f:\test.dat
diskspd.exe -c1024M -d10 -W5 -o1 -t4 -b8k -r -Sh -L f:\test.dat
```

> [!tip] 评估差异
> - Evaluate the differences in terms of ==IOPS== and ==avg latency==
> - Repeat the exercise by increasing the `-o` value from `-o1` to `-o16` and `-o32`: can you see the difference?

---

## ProcessMon

Process Monitor 收集方式如下：

https://docs.microsoft.com/en-us/sysinternals/downloads/procmon

解压到文件夹之后，请参考以下步骤：

1. 双击打开 Process Monitor

   ![image-20231030172616086](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310301726155.png)

2. ==默认自动抓取==，您可以通过点击该按钮进行打开抓取和关闭抓取。

   ![image-20231030172639079](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310301726134.png)

3. 开启抓取之后，启动 Edge，访问有问题的地址，复现问题。

4. 问题复现结束之后，关闭抓取

5. 从 File 中选择保存或者点击 save 进行保存。保存完格式为 ==`*.PML`== 格式。
