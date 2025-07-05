import psutil, time

# 获取CPU使用率
def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

# 获取内存使用率，已用内存GB，总内存GB
def get_mem_usage():
    mem = psutil.virtual_memory()
    return mem.percent, mem.used / (1024 ** 3), mem.total / (1024 ** 3)

# 获取交换分区使用率，已用量GB，总大小GB
def get_swap_usage():
    swap = psutil.swap_memory()
    return swap.percent, swap.used / (1024 ** 3), swap.total / (1024 ** 3)

# 获取1\5\15min的系统负载
def get_sys_load():
    return psutil.getloadavg()

# 分析系统瓶颈
def analyze_bottleneck(cpu, mem, swap, load):
    bottleneck_report = []

    # 分析各项指标
    if cpu > 80:
        bottleneck_report.append("High CPU usage")

    if mem[0] > 80:
        bottleneck_report.append(f"High memory usage. Memory used: {mem[1]: .2f} GB, used percent: {mem[0]}%.")

    if swap[0] > 80:
        bottleneck_report.append(f"High swap used. Swap used: {swap[1]: .2f} GB, used percent: {swap[0]}%.")

    if load[0] > 2 * psutil.cpu_count(): # 系统负载大于CPU核数的两倍视为负载高
        bottleneck_report.append(f"High system load: {load[0]}")