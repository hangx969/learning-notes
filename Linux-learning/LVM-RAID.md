# Mount new data disk via fdisk

### 1. Add a new disk on Azure Portal

### 2.  Check the new disk

```shell
lsblk -f
```

### 3. Add a partition and check

```shell
fdisk /dev/sdd
m # for help
n # add a new partition
p # primary
1 # partition number, default in the following
w # save and quit
lsblk -f
```

### 4. Format the new partition and mount 

To set file format and get UUID

```shell
mkfs -t ext4 /dev/sdd1 # format
mkdir mnt/resource/newdisk2
mount /dev/sdd1 /mnt/resource/newdisk2
lsblk -f
```

### 5. Configure the mount in fstab

Mount through command line will not be kept after a reboot

So we need to maintain the mount even after a reboot through configuring the **fstab**

```shell
vim /etc/fstab  # It's important to use UUID instead of disk name in VM
```

```shell
mount -a 
```

# Difference about RAID and LVM

### RAID

- CPU Technology grew faster than disk which limit the further development.
- RAID was developed. RAID stands for Redundant Arrays of Independent Disk. It combines individual disks to a larger and faster disk array, where data is cut to sectors and stored on separate disks to gain performance.
- As for RAID0, at least two disks are combined via hardware or software approach, data was input on those disks by order, so that the IO performance improved.

### LVM

- After disk is partitioned, users may want to adjust the volume dynamically. Consequently, another disk management  technology, LVM, is developed.
- LVM add a logical layer between hardware and file system by creating volume group and logical volume.

### Difference

- RAID is a disk management technology to improve IO performance by combining several disks to one array, while LVM is another disk management technology which allow users to adjust volume of partition dynamically by creating PV, VG and LV. 

# Configure LVM for test

### 1. Prepare disk partition with type of 8e

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

### 2. Prepare Physical volume (PV)

```shell
pvcreate /dev/sde1
pvcreate /dev/sde2
pvcreate /dev/sde3
pvdisplay # check
```

### 3. Prepare volume group (VG)

```shell
vgcreate vg1 /dev/sde1 /dev/sde2 /dev/sde3  # vg1 is a name for VG
vgdisplay # check
```

### 4. Prepare logical volume (LV)

```shell
lvcreate -L 100M -n lv1 vg1 # lv1: you name it, vg1: lv1 uses the volume on vg1
lvdisplay # check
```

### 5. Format the LV and mount

```shell
mkfs -t ext4 /dev/vg1/lv1
mkdir /lvm-mount
mount /dev/vg1/lv1 /lvm-mount/
lsblk -f # check
```

### 6 [if necessary]. Expand  the volume of  LV 

```shell
umount /lvm-mount/ # unmount the point
lvresize -L 200M /dev/vg1/lv1 # resize the volume to 200M
e2fsck -f /dev/vg1/lv1 # check the error in disk
resize2fs /dev/vg1/1v1 # update
# note : order of the ubove command is IMPORTANT
lvdisplay # check
mount /dev/vg1/lv1 /lvm-mount
vim /etc/fstab  
# configure fstab to add /dev/vg1/lv1 then the mount point is kept atfer reboot
```

### 7. [if necessary] Curtail the volume of LV

```shell
umount /dev/vg1/lv1 /lvm-mount
e2fsck -f /dev/vg1/lv1 # check disk error
resize2fs /dev/vg1/lv1 50M # resize and update the file system first
lvresize -L 50M /dev/vg1/lv1 # curtail the LV volume
# the order of commands above is IMPORTANT
lvdisplay # check
```

### 8. [if necessary] Expand the VG

Add a PV to VG. Then more LV can be created on the expanded VG.

Actually, any disk partition with 8e type can be used to expand VG

Prepare a disk partition sde4 as mentioned above.

```shell
pvcreate /dev/sde4 # create Pyhsical Volume
vgextend vg1 /dev/sde4 # Expand the Voulme Group VG1
vgdisplay # check
```

### 9. Remove

```shell
umount /lvm-mount
lvremove /dev/vg1/lv1 # delete the LV
vgremove vg1 # delete the VG
pvremove /dev/sde1 # delete the PV
```



# Configure RAID0 

Get two new disks on Azure Portal

### 1. Install mdadm 

use mdadm to manage RAID configuration

```shell
yum install mdadm -y
```

### 2. Create a RAID0

```shell
mdadm -C -v /dev/md0 -l 0 -n 2 /dev/sdc /dev/sdf 
# -C create mode, -v more verbose, -l RAID level, -n disks numbers
mdadm -Ds > etc/mdadm.conf # output the configuration info to this file
mdadm -D /dev/md0 # check info about RAID
```

### 3. Add partition to raid

```shell
fdisk /dev/md0
```

### 4. Format the new partition and mount

```shell
mkfs -t ext4 /dev/md0p1  # format to ext4
mkdir /raid0 # create mount point
mount /dev/md0p1 /raid0 # mount to point 
lsblk -f # check
```

### 5. configure fstab

```shell
vim /etc/fstab
# add md0p1 to fstab to make it work after reboot
```



