import psutil

def get_disk_usage():
    # 返回一个列表，里面是分区信息的元组
    # 类似于[sdiskpart(device='/dev/vg00/root', mountpoint='/', fstype='ext4', opts='rw')]
    part_usage = psutil.disk_partitions()

    # 遍历分区元组，获取其中mountpoint参数，让psutil.disk_usage计算使用情况
    for part in part_usage:
        usage = psutil.disk_usage(part.mountpoint)
        # 获取到类似于：sdiskusage(total=1046, used=520, free=99, percent=5.0)
        total_gb = usage.total / (2 ** 30)
        used_gb = usage.used / (2 ** 30)
        free_gb = usage.free / (2 ** 30)
        used_percentage = usage.used / usage.total * 100
        print(f"Mount point: {part.mountpoint}")
        print(f"Total: {total_gb: .2f} GiB")
        print(f"Used: {used_gb: .2f} GiB")
        print(f"Free: {free_gb: .2f} GiB")
        print(f"Used percentage: {used_percentage: .1f}%")
        print('-' * 30)

if __name__ == '__main__':
    get_disk_usage()