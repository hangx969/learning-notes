> 

# LVM基本概念

> - 在 GNU/Linux 环境中，LVM（Logical Volume Management）或逻辑卷管理是一种通过虚拟块轻松管理块设备的解决方案。Linux 环境中使用 LVM 的磁盘管理提供了系统上存在的磁盘结构的高级视图，为应用程序和用户分配存储提供了更大的灵活性。使用 LVM 创建的卷几乎可以随意调整大小和移动，使得存储空间的管理变得更加简便和高效。
>
> - LVM 的三个重要元素：物理卷（PV）、卷组（VG）和逻辑卷（LV）。

## 物理卷（Physical Volume）

物理卷是 LVM 中的基本单元，它可以是硬盘的整个分区或者未分区的硬盘空间。物理卷是 LVM 中存储数据的实际载体，它们通常是硬盘、SSD 或 NVMe 等块设备。

创建物理卷的步骤通常包括使用 `pvcreate` 命令将磁盘或磁盘分区标记为物理卷，以供后续使用。

```sh
pvcreate /dev/sdb
```

## 卷组（Volume Group）

卷组是由一个或多个物理卷组成的逻辑存储池，它为逻辑卷提供了抽象和灵活性。在卷组中，物理卷的存储空间汇总在一起，以供后续使用。

创建卷组的步骤包括使用 `vgcreate` 命令创建一个卷组，并将一个或多个物理卷添加到卷组中。

```sh
vgcreate vg_data /dev/sdb
```

## 逻辑卷（Logical Volume）

逻辑卷是从卷组中划分出的逻辑存储空间，它可以看作是虚拟的硬盘分区。逻辑卷是用户实际上用来存储数据的部分，它们可以根据需要动态调整大小，并且可以跨越多个物理卷。

创建逻辑卷的步骤包括使用 `lvcreate` 命令在指定的卷组上创建逻辑卷，并指定逻辑卷的大小。

```sh
lvcreate -L 100G -n lv_data vg_data
```

## LVM 架构示意图

```sh
物理卷 (PV)       卷组 (VG)        逻辑卷 (LV)
   |                 |                |
   |                 |                |
   +-----------------+----------------+
            |                  |
            +------------------+
                   |
                   |
            文件系统（/、/var、/home 等）
```

- 在 LVM 架构中，物理卷被组织成卷组，而卷组上创建逻辑卷以供文件系统使用。这种层次结构使得管理和扩展存储空间变得更加灵活和方便。
- 遵循创建顺序，首先创建物理卷，然后将它们分组为一个或多个卷组，最后在卷组上创建逻辑卷。这种顺序保证了逻辑卷可以充分利用物理卷和卷组的灵活性和可用性。

# 线性逻辑卷和条带逻辑卷

在 LVM 中，您可以选择使用线性逻辑卷（Linear LV）或条带逻辑卷（Striped LV）来管理存储空间。这两种方式在磁盘资源的利用和性能方面有所不同。

![img](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202408151423674.webp)

## 线性逻辑卷（Linear LV）

线性逻辑卷是 LVM 中的一种基本形式，它将物理卷上的数据按照线性顺序进行存储。换句话说，数据从一个物理卷的末尾延伸到下一个物理卷的开始，依次类推，直到所有物理卷都被使用完毕。

特点：

- 数据按照线性顺序存储，从一个物理卷延伸到下一个物理卷。
- 简单直观，易于管理。
- 适用于小型环境或者对数据读取顺序要求不高的情况。

## 条带逻辑卷（Striped LV）

条带逻辑卷是一种高级形式的逻辑卷，它将数据分布在多个物理卷之间，以提高读写性能和并发能力。数据被分成固定大小的条带（或块），依次存储在不同的物理卷上。

特点：

- 数据被分割成条带，并分布在多个物理卷上，增加了读写并发能力和性能。
- 更好地利用了磁盘资源，提高了 IOP（每秒输入/输出操作数）。
- 适用于对性能要求较高、需要大量并发读写操作的情况，如数据库、视频编辑等应用场景。

假设我们有两个 1 TiB 的物理卷，分别为 `/dev/sdb` 和 `/dev/sdc`。我们可以创建一个线性逻辑卷和一个条带逻辑卷，以比较它们之间的不同。

## 创建线性逻辑卷

```sh
lvcreate -l 100%FREE -n linear_lv vg_data /dev/sdb /dev/sdc
```

## 创建条带逻辑卷

```sh
lvcreate -i2 -I64 -l 100%FREE -n striped_lv vg_data /dev/sdb /dev/sdc
```

在上面的示例中，`-i2` 表示使用两个物理卷进行条带化，`-I64` 表示条带大小为 64KB。您可以根据实际需求调整条带数量和大小。

# 文件系统管理与挂载

一旦我们创建了逻辑卷，接下来就是将其格式化为文件系统，并挂载到系统中的目录上，以便用户可以访问和使用该存储空间。

## 格式化逻辑卷

在创建逻辑卷后，需要使用适当的文件系统格式化它，以便在其上创建文件并存储数据。常见的文件系统格式包括 ext4、XFS、NTFS 等。

例如，要将 `lv_data` 逻辑卷格式化为 ext4 文件系统，可以执行以下命令：

```sh
mkfs.ext4 /dev/vg_data/lv_data
```

## 挂载逻辑卷

格式化完成后，需要将逻辑卷挂载到文件系统的目录上，以便用户可以访问其中的数据。

```sh
# 创建挂载点（如果不存在）
mkdir /mnt/data

# 将逻辑卷挂载到挂载点上
mount /dev/vg_data/lv_data /mnt/data
```

现在，逻辑卷 `lv_data` 已经成功挂载到 `/mnt/data` 目录上，用户可以通过该目录来访问和管理存储在其中的数据。

# LVM 的扩展与管理

LVM 不仅可以帮助我们管理已有的存储空间，还可以在需要时进行扩展和调整，以满足不断增长的存储需求。

## 添加物理卷到卷组

如果卷组中的存储空间不足，可以通过添加更多的物理卷来扩展其容量。

```sh
# 创建新的物理卷
pvcreate /dev/sdc1

# 将新的物理卷添加到卷组
vgextend vg_data /dev/sdc1
```

## 扩展逻辑卷

当系统中的存储空间不足时，可以通过扩展现有的逻辑卷来增加可用空间。

```sh
# 扩展逻辑卷
lvextend -L +50G /dev/vg_data/lv_data

# 调整文件系统大小
resize2fs /dev/vg_data/lv_data
```

## 移除物理卷或逻辑卷

在一些情况下，可能需要移除不再需要的物理卷或逻辑卷，以释放存储空间或进行系统优化。

```sh
# 移除物理卷
vgreduce vg_data /dev/sdb1

# 移除逻辑卷
lvremove /dev/vg_data/lv_data
```

## 扩容基于LVM的文件系统-实验

- 实验环境：
  - Ubuntu 2204
- 实验目标：
  - 原始配置了20GB的LVM，挂载到根分区。
  - 对磁盘进行扩容，如何扩容到根分区。

- 查看现有LVM配置

~~~sh
root@ubuntu-test:~# df -h
Filesystem                         Size  Used Avail Use% Mounted on
tmpfs                              791M  1.6M  789M   1% /run
/dev/mapper/ubuntu--vg-ubuntu--lv  9.8G  3.1G  6.3G  33% /
tmpfs                              3.9G     0  3.9G   0% /dev/shm
tmpfs                              5.0M     0  5.0M   0% /run/lock
/dev/sda2                          1.8G  130M  1.5G   8% /boot
tmpfs                              791M  4.0K  791M   1% /run/user/0

root@ubuntu-test:~# lsblk
sda                         8:0    0    20G  0 disk 
├─sda1                      8:1    0     1M  0 part 
├─sda2                      8:2    0   1.8G  0 part /boot
└─sda3                      8:3    0  18.2G  0 part 
  └─ubuntu--vg-ubuntu--lv 253:0    0    10G  0 lvm  /
~~~

- 扩容磁盘到25G

- 更新磁盘容量

~~~SH
#刷新SCSI
for i in $(ls /sys/class/scsi_host/); do echo "- - -" > /sys/class/scsi_host/$i/scan; done
#查看磁盘容量
sda                         8:0    0    25G  0 disk 
├─sda1                      8:1    0     1M  0 part 
├─sda2                      8:2    0   1.8G  0 part /boot
└─sda3                      8:3    0  18.2G  0 part 
  └─ubuntu--vg-ubuntu--lv 253:0    0    10G  0 lvm  /
~~~

~~~sh
#gdisk新建磁盘分区
sudo gdisk /dev/sda
p #查看已有分区
n #创建新分区
5 #输入分区编号。
enter #默认起始点
+100G #按照结束点设置分区大小 +5G。
8e00 #更改分区类型为LVM。
w #保存并退出 fdisk。
#更新分区表
partprobe /dev/sda
#扩容lvm
pvs/pvdisplay
pvcreate /dev/sda5
vgs/vgdisplay
vgextend ubuntu-vg /dev/sda5
lvs
lvextend -L +100%FREE /dev/ubuntu-vg/ubuntu-lv
lvs/lvdisplay
#扩容ext4文件系统 -- 指定的是lvdisplay中的LV Path
resize2fs /dev/ubuntu-vg/ubuntu-lv
#扩容xfs文件系统 -- 指定的是挂载点而非逻辑卷路径
xfs_growfs /
df -h
lsblk
~~~

## 数据备份与恢复

- LVM 的快照功能可以用于创建存储卷的快照，以便进行数据备份、测试或者回滚操作，而无需中断服务。
- 在数据库升级之前，我们可以先创建一个逻辑卷的快照，以便在升级失败时快速回滚。

```sh
# 创建快照
lvcreate -L 20G -s -n lv_data_snapshot /dev/vg_data/lv_data
# 在快照上进行操作（如升级数据库）
# ...
# 恢复快照
lvconvert --merge /dev/vg_data/lv_data_snapshot
```

## 磁盘故障恢复

- LVM 支持 RAID 技术，可以在物理卷之间创建镜像或条带，以提高数据的容错性和可用性，同时在硬盘故障时实现数据自动恢复。
- 在卷组中创建一个镜像卷，以保证数据在一块硬盘故障时的可靠性。

```sh
# 创建镜像卷
lvcreate -L 100G -m1 -n lv_data_mirror vg_data /dev/sdd1
```

# Difference about RAID and LVM

## RAID

- CPU Technology grew faster than disk which limit the further development.
- RAID was developed. RAID stands for Redundant Arrays of Independent Disk. It combines individual disks to a larger and faster disk array, where data is cut to sectors and stored on separate disks to gain performance.
- As for RAID0, at least two disks are combined via hardware or software approach, data was input on those disks by order, so that the IO performance improved.

## LVM

- After disk is partitioned, users may want to adjust the volume dynamically. Consequently, another disk management  technology, LVM, is developed.
- LVM add a logical layer between hardware and file system by creating volume group and logical volume.

## Difference

- RAID is a disk management technology to improve IO performance by combining several disks to one array, while LVM is another disk management technology which allow users to adjust volume of partition dynamically by creating PV, VG and LV. 

# How to add a disk on Azure VM

- Mount new data disk via fdisk

- Add a new disk on Azure Portal
- Check the new disk

```shell
lsblk -f
```

- Add a partition and check

```shell
fdisk /dev/sdd
m # for help
n # add a new partition
p # primary
1 # partition number, default in the following
w # save and quit
lsblk -f
```

- Format the new partition and mount 
  - To set file format and get UUID

```shell
mkfs -t ext4 /dev/sdd1 # format
mkdir mnt/resource/newdisk2
mount /dev/sdd1 /mnt/resource/newdisk2
lsblk -f
```

- Configure the mount in fstab
  - Mount through command line will not be kept after a reboot
  - So we need to maintain the mount even after a reboot through configuring the **fstab**

```shell
vim /etc/fstab  # It's important to use UUID instead of disk name in VM
```

```shell
mount -a 
```

# Configure LVM in centos

1. Prepare disk partition with type of 8e

```shell
fdisk /dev/sde
p # primary
1 # partition num
default # first sector
+1G # last sector
t # change partition type
8e # hex code for LVM
fdisk -l # check
```

2. Prepare Physical volume (PV)

```shell
pvcreate /dev/sde1
pvcreate /dev/sde2
pvcreate /dev/sde3
pvdisplay # check
```

3. Prepare volume group (VG)

```shell
vgcreate vg1 /dev/sde1 /dev/sde2 /dev/sde3  # vg1 is a name for VG
vgdisplay # check
```

4. Prepare logical volume (LV)

```shell
lvcreate -L 100M -n lv1 vg1 # lv1: you name it, vg1: lv1 uses the volume on vg1
lvdisplay # check
```

5. Format the LV and mount

```shell
mkfs -t ext4 /dev/vg1/lv1
mkdir /lvm-mount
mount /dev/vg1/lv1 /lvm-mount/
lsblk -f # check
```

6 [if necessary]. Expand the volume of LV 

```shell
umount /lvm-mount/ # unmount the point
lvresize -L 200M /dev/vg1/lv1 # resize the volume to 200M
e2fsck -f /dev/vg1/lv1 # check the error in disk
resize2fs /dev/vg1/1v1 # update
#xfs_growfs /
# note : order of the ubove command is IMPORTANT
lvdisplay # check
mount /dev/vg1/lv1 /lvm-mount
vim /etc/fstab  
# configure fstab to add /dev/vg1/lv1 then the mount point is kept atfer reboot
```

7. [if necessary] Curtail the volume of LV

```shell
umount /dev/vg1/lv1 /lvm-mount
e2fsck -f /dev/vg1/lv1 # check disk error
resize2fs /dev/vg1/lv1 50M # resize and update the file system first
lvresize -L 50M /dev/vg1/lv1 # curtail the LV volume
# the order of commands above is IMPORTANT
lvdisplay # check
```

8. [if necessary] Expand the VG

Add a PV to VG. Then more LV can be created on the expanded VG.

Actually, any disk partition with 8e type can be used to expand VG

Prepare a disk partition sde4 as mentioned above.

```shell
pvcreate /dev/sde4 # create Pyhsical Volume
vgextend vg1 /dev/sde4 # Expand the Voulme Group VG1
vgdisplay # check
```

9. Remove

```shell
umount /lvm-mount
lvremove /dev/vg1/lv1 # delete the LV
vgremove vg1 # delete the VG
pvremove /dev/sde1 # delete the PV
```

# Configure RAID0 

Get two new disks on Azure Portal

## 1. Install mdadm

use mdadm to manage RAID configuration

```shell
yum install mdadm -y
```

## 2. Create a RAID0

```shell
mdadm -C -v /dev/md0 -l 0 -n 2 /dev/sdc /dev/sdf 
# -C create mode, -v more verbose, -l RAID level, -n disks numbers
mdadm -Ds > etc/mdadm.conf # output the configuration info to this file
mdadm -D /dev/md0 # check info about RAID
```

## 3. Add partition to raid

```shell
fdisk /dev/md0
```

## 4. Format the new partition and mount

```shell
mkfs -t ext4 /dev/md0p1  # format to ext4
mkdir /raid0 # create mount point
mount /dev/md0p1 /raid0 # mount to point 
lsblk -f # check
```

## 5. configure fstab

```shell
vim /etc/fstab
# add md0p1 to fstab to make it work after reboot
```

