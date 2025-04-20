# GPU节点异常重启

## background

挂载了lustre的GPU计算节点在任务执行过程中 Hang 死后触发 Kdump 机 制致使系统自动重启。

系统信息：

1. 系统版本是：SUSE Linux Enterprise Server 12 SP5
2. 内核版本：Kernel-4.12.14-122.91
3. Lustre 客户端版本：2.12.6_ddn42-1

## Troubleshooting

- 根据Kdump（内核dump文件）分析原因，发现Kernel在调用Lustre模块执行 [_raw_write_lock] 操作的时候出现了空指针。DDN 技术团队做出了分析，认为此次告警问题是由于 Lustre 客户端在 lustreclient-2.12.6_ddn42-1.x86_64 版本下触发了一个已知的 bug。
- 参考：https://wiki.lustre.org/Lustre_2.15.0_Changelog

## Solution

- DDN Lustre服务端最新版本为6.3.1，建议搭配Lustre客户端2.14.0-ddn168版本，同时需要升级SFA OS、磁盘固件、Enclosure固件至新版本以获取更好的兼容性。

# cudaErrorUnknown

## background

- GPU节点上的PBS任务执行过程中异常退出，应用报错cudaErrorUnknown。

系统信息：

- 系统版本是：SUSE Linux Enterprise Server 12 SP5
- CUDA 版本 12.0
- Nvidia driver版本 525.125.06

## Troubleshooting

- 应用实际是在执行命令：`singularity run  --nv ./video_log_downsample_20240205-1600.sif <input_MF4_file> --downsample <output_zvlf_file>` ，命令本地执行也会失败，singularity一运行就退出了，没创建容器。故而判断与PBS无关。
- 这个报错会在两个GPU节点随机出现，大都是在节点重启之后一段时间有问题，过一段时间或者节点跑完GPU测试程序的话，就自动恢复了。

## Solution

- 参考singularity文档：https://docs.sylabs.io/guides/3.5/user-guide/gpu.html#cuda-error-unknown-when-everything-seems-to-be-correctly-configured，CUDA依赖一些内核模块，并不是所有的内核模块都会在系统启动后加载。在host上直接调用cuda，nvidia_uvm模块会自动加载；但是singularity --nv调用cuda，这个模块就不会自动加载，导致cudaErrorUnknown的问题。
- 建议系统启动后以root执行`modprobe nvidia_uvm`来加载模块、并且开启GPU的persistence mode。

# Timezone错误

## background

- PBS某些任务在计算节点上会报错：Timezone not found Asia/Beijing
- 系统版本是：SUSE Linux Enterprise Server 12 SP5

## Troubleshooting

- 追溯任务代码中的定义，是读取/etc/sysconfig/clock文件，以及PBS环境变量TZ来获取时区。这两个配置在节点上是Asia/Beijing，所以报错。

## Solution

- 操作系统层面，首先确保timedatectl的系统时钟设置为Asia/Shanghai

  ~~~sh
  timedatectl set-timezone Asia/Shanghai
  systemctl restart systemd-timesyncd
  ~~~

- 操作系统层面，修改硬件时钟/etc/sysconfig/clock为Asia/Shanghai

  ~~~sh
  cat /etc/sysconfig/clock
  TIMEZONE="Asia/Shanghai"
  DEFAULT_TIMEZONE="US/Eastern"
  HWCLOCK="-u"
  ~~~

- PBS层面，PBS会在安装时引用当时操作系统变量写在/var/spoolpbs/pbs_environment中，将这个文件中的时区改为Asia/Shanghai，重启PBS服务。

> - https://www.suse.com/support/kb/doc/?id=000018825 根据SUSE官网，/etc/sysconfig/clock是legacy的获取时区方式，timedatactl是modern的方式，这两种在系统中并存，长期建议是直接删掉/etc/sysconfig/clock，只用timedatectl来管理时区。
