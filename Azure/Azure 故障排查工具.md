---
title: Azure 故障排查工具
tags:
  - azure/tools
  - azure/troubleshooting
  - azure/monitoring
  - azure/performance
aliases:
  - Browser Trace (HAR)
  - Fiddler
  - IO Monitor
  - PerfMon & ProcessMon
  - Postman
date: 2026-09-26
---

# Azure 故障排查工具

Azure Portal、API 和虚拟机性能问题需要采集不同层面的证据。先确定问题发生在哪一层，再选择工具；同一问题复现时尽量记录时间、操作和请求或进程，便于对照分析。

| 排查对象 | 工具 | 主要证据 |
| --- | --- | --- |
| Azure Portal 页面或浏览器请求 | Browser Trace（HAR） | 浏览器网络请求与响应 |
| HTTP/HTTPS 请求细节 | Fiddler Classic | 代理捕获的会话、URL 和进程 |
| Azure API 调用与身份验证 | Postman | 请求、响应及目标资源对应的令牌 |
| Windows 进程活动 | Process Monitor（ProcMon） | 进程事件，保存为 `.PML` |
| Windows 性能与磁盘基准 | PerfMon + Diskspd | 性能计数器、IOPS、吞吐量和延迟 |
| Linux 磁盘性能与进程 I/O | FIO、iotop | 基准测试结果和持续 I/O 记录 |

## 1. 浏览器与 HTTP 请求

### Browser Trace：采集 Azure Portal 的 HAR

浏览器网络追踪以 HAR 格式记录请求，可用于定位 Azure Portal 页面加载或操作失败时的请求。按 [Microsoft Learn 的浏览器追踪采集说明](https://learn.microsoft.com/en-us/azure/azure-portal/capture-browser-trace)操作，在开发者工具的网络面板中复现问题并导出 HAR；分析时按失败请求、状态码和时间顺序定位。

![浏览器网络追踪采集示例](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310301709430.png)

![浏览器网络追踪分析示例](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310301709684.png)

### Fiddler Classic：捕获并筛选 HTTP/HTTPS 会话

Fiddler Classic 是 HTTP 调试代理。需要检查浏览器之外的 HTTP 流量，或按进程定位请求时，可用它捕获会话。

1. 安装 **Fiddler Classic**。
2. 如需检查 HTTPS 内容，在设置中启用 HTTPS 捕获并信任其根证书。
3. 复现问题后，按目标进程过滤无关流量，再检查相关请求。

![Fiddler Classic 的 HTTPS 配置](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310301704117.png)

| 快捷键 | 用途 |
| --- | --- |
| `Ctrl+F` | 查找 |
| `Ctrl+1` | 高亮 |
| `D` | 查找相同 URL 的条目 |
| `P` | 查找 parent |
| `C` | 查找 client |

> [!warning] 敏感信息
> HAR、Fiddler 会话和令牌可能包含身份验证信息。共享前先检查并移除敏感字段；仅在需要时信任 Fiddler 根证书。

## 2. API 调试与访问令牌

Postman 用于发送 HTTP 请求并检查响应。调试 Azure API 时，应让令牌的目标资源与请求的 API 一致：Microsoft Entra ID（原 AAD）接口使用相应作用域的令牌，Azure Resource Manager（ARM）接口使用面向 ARM 的 Bearer Token。两者不能因为都叫 access token 就直接互换；还要确认调用身份对目标资源具有所需权限。

### Entra ID（AAD）请求

在 Postman 中为目标接口配置其要求的 scope，取得对应令牌后再发送请求。原文中的 scope 配置示例如下：

![Postman 中的 AAD scope 配置](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310301707977.png)

### ARM 请求

调用 ARM 资源接口时，使用面向 ARM 的 Bearer Token，并确认调用身份具备所需 RBAC 权限。排查 Portal 发出的 ARM 请求时，可在浏览器开发者工具（`F12`）中观察请求及授权信息；使用从 Portal 获取的令牌时应避免记录或传播其原值。

## 3. Windows 进程与性能数据

### Process Monitor：复现期间抓取进程事件

[下载 Process Monitor](https://learn.microsoft.com/en-us/sysinternals/downloads/procmon)并解压后：

1. 打开 Process Monitor；默认会自动开始捕获。
2. 使用工具栏的捕获按钮控制开始与停止。
3. 开始捕获后，启动 Edge 并访问出现问题的地址，复现问题。
4. 复现结束立即停止捕获，再从 **File → Save** 保存为 `.PML`。

![打开 Process Monitor](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310301726155.png)

![Process Monitor 的捕获开关](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310301726134.png)

### PerfMon：与 Diskspd 同时采集计数器

PerfMon 用于观察 Windows 性能计数器；磁盘压测时与 Diskspd 同时运行，可以把测试结果与磁盘、内存、网络和进程指标对照。原文的 PerfMon 界面示例如下：

![PerfMon 性能监视示例](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310301724780.png)

在管理员权限的 CMD 中创建并启动每 2 秒采集一次的计数器集：

```bat
Logman create counter Perf-2Second -f bincirc -max 500 -c "\LogicalDisk(*)\*" "\Memory\*" "\Network Interface(*)\*" "\Paging File(*)\*" "\PhysicalDisk(*)\*" "\Server\*" "\System\*" "\Process(*)\*" "\Processor(*)\*" "\Cache\*" -si 00:00:02 -o C:\PerfMonLogs\Perf-2Second.blg
Logman start Perf-2Second
```

压测结束后停止采集：

```bat
Logman stop Perf-2Second
```

## 4. 磁盘 I/O：基准测试与持续观察

### Windows：Diskspd 配合 PerfMon

参考 [Azure 磁盘基准测试指南](https://learn.microsoft.com/zh-cn/azure/virtual-machines/disks-benchmarks#diskspd)。在 Diskspd 的 `amd64` 目录下打开 CMD，先启动上文的 PerfMon 计数器集，再运行测试，最后停止计数器集并对照命令行输出与 `.blg` 文件。

以下是原文用于测试读取 IOPS 的示例；将 `D:` 改为实际目标磁盘盘符：

```bat
.\diskspd.exe -c200G -w0 -b8K -F16 -r -o128 -d60 -Sh D:\testfile.dat
```

原文另有两组“最大读取 IOPS”测试截图，分别保留如下；测试具体参数以各截图为准。

![Diskspd 读取 IOPS 测试示例一](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310301714709.png)

![Diskspd 读取 IOPS 测试示例二](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310301714808.png)

测试最大吞吐量时，原文提示增大 block size：

![Diskspd 吞吐量测试示例](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310301715276.png)

> [!warning] 压测影响
> Diskspd 会创建测试文件并施加磁盘负载。运行前确认目标盘符、可用空间和业务影响；示例中的 `-c200G` 会使用 200 GB 的测试文件。

#### Storage Spaces 实验：比较并发与延迟

原文实验条件为一台 Windows VM（A2_v2），挂载 4 块各 32 GiB 的 Standard SSD 数据盘，并通过 Storage Spaces 的 **Simple（striping）** 布局组成虚拟磁盘。按实验盘符执行：

```bat
diskspd.exe -c1024M -d10 -W5 -o1 -t1 -b8k -r -Sh -L f:\test.dat
diskspd.exe -c1024M -d10 -W5 -o1 -t4 -b8k -r -Sh -L f:\test.dat
```

比较两次的 IOPS 和平均延迟；再把 `-o1` 分别改为 `-o16`、`-o32`，观察队列深度变化对结果的影响。测试期间可同步采集 PerfMon 数据。

### Linux：FIO 基准测试

FIO 用于 Linux 磁盘基准测试。测试方法与参数见 [Azure 磁盘基准测试指南的 FIO 部分](https://learn.microsoft.com/en-us/azure/virtual-machines/disks-benchmarks#fio)；按实际工作负载选择测试参数。

### Linux：观察并记录进程 I/O

`top` 和 `ps` 可辅助定位活跃进程或内存占用；它们不能代替逐进程 I/O 统计。原文的辅助命令为：

```bash
top -i
ps -e -o pid,user,%mem,cmd --sort=-%mem
```

需要等待故障复现时，可使用 `iotop` 持续记录。原文给出的 cron 配置如下，创建 `/etc/cron.d/iotop` 后加入这一行：

```cron
* * * * * root /usr/sbin/iotop -botqqqk --iter=60 | grep -P "\d\d\.\d\d K/s" >>/tmp/io.log 2>&1
```

该配置表示每分钟启动一次采集；启用前应确认本机 `iotop` 的输出和选项与过滤表达式匹配，并检查定时任务不会重叠。日志会持续增长，问题结束后停止定时采集并清理日志。

## 参考资料

- [Capture a browser trace for troubleshooting - Azure portal](https://learn.microsoft.com/en-us/azure/azure-portal/capture-browser-trace)
- [Benchmark your application on Azure Disk Storage](https://learn.microsoft.com/en-us/azure/virtual-machines/disks-benchmarks)
- [Process Monitor - Sysinternals](https://learn.microsoft.com/en-us/sysinternals/downloads/procmon)
