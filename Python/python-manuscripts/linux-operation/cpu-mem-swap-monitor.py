"""
系统资源监控脚本

功能描述：
1. 实时监控本地系统的CPU、内存、交换分区使用率
2. 监控系统负载（1分钟、5分钟、15分钟平均负载）
3. 自动分析系统性能瓶颈并生成告警报告
4. 每10秒循环检测一次系统资源状态

瓶颈分析规则：
- CPU使用率 > 80% 视为高CPU使用率
- 内存使用率 > 80% 视为高内存使用率
- 交换分区使用率 > 80% 视为高交换分区使用率
- 1分钟平均负载 > CPU核数×2 视为高系统负载
"""

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

    # or运算符支持短路规则，前面是假（None，0，“”），就赋值后面的值
    cpu_count = psutil.cpu_count() or 1
    if load[0] > 2 * cpu_count: # 系统负载大于CPU核数的两倍视为负载高
        bottleneck_report.append(f"High system load: 1min average load: {load[0]}, higher than double CPU cores.")

    return bottleneck_report


# 监控函数
def monitor_system():
    while True:
        cpu_usage = get_cpu_usage()
        mem_usage = get_mem_usage()
        swap_usage = get_swap_usage()
        sys_load = get_sys_load()

        print(f"CPU usage percent: {cpu_usage}%.")
        print(f"Memory usage percent: {mem_usage[0]}%, memory used: {mem_usage[1]: .2f} GB, total memory: {mem_usage[2]: .2f} GB.")
        print(f"Swap usage percent: {swap_usage[0]}%, swap used: {swap_usage[1]: .2f} GB, used swap: {swap_usage[2]: .2f} GB.")
        print(f"System load in 1 minutes: {sys_load[0]}, 5 minutes: {sys_load[1]}, 15 minutes: {sys_load[2]}.")

        bottleneck_report = analyze_bottleneck(cpu_usage, mem_usage, swap_usage, sys_load)

        if bottleneck_report:
            print(f"WARNING: bottleneck report:")
            for report in bottleneck_report:
                print(f" - {report}")
        else:
            print("No bottleneck found.\n\n")
        time.sleep(10)


if __name__ == "__main__":
    monitor_system()