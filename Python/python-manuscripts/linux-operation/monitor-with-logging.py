"""
系统资源监控与日志记录脚本

功能描述：
本脚本实现了对本地系统资源的实时监控和日志记录功能，通过psutil库采集系统关键性能指标，
并将监控数据同时输出到控制台和日志文件中，便于实时查看和历史数据分析。

主要功能：
1. CPU使用率监控：使用psutil.cpu_percent()获取CPU占用百分比
2. 内存信息采集：监控总内存、已用内存、可用内存和内存使用率
3. 磁盘使用率监控：采集根分区(/)的磁盘使用情况
4. 网络流量统计：监控网络IO的上行和下行流量(发送/接收字节数)
5. 双重日志输出：数据同时输出到控制台和日志文件(monitoring.log)
"""

import psutil, logging, time, signal

# 自定义日志记录器
logger = logging.getLogger('monitoring-logger')
logger.setLevel(logging.DEBUG)

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# 创建文件处理器
file_handler = logging.FileHandler('monitoring.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

# 创建格式化器
formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s: %(message)s',  datefmt='%Y%m%d_%H:%M:%S')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# 将处理器添加到记录器
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# 定义信号中断标志
RUNNING = True
# 定义信号处理函数
def sig_handler(sig, frame):
    # sig：表示信号的编号或类型，通常是一个整数（例如，SIGINT 对应的信号编号是 2）。
    # frame：表示当前执行的栈帧。这个参数对于处理信号时并不总是需要使用，但可以用来获取调用栈的信息。
    global RUNNING
    RUNNING = False
    print("\nExiting Monitoring Program")

# 将信号SIGINT与信号处理函数绑定
# signal.signal 是 signal 模块提供的一个函数，用于将信号与信号处理函数进行绑定。
# 第一个参数 signal.SIGINT 表示信号类型，即 中断信号。SIGINT 是在用户按下 Ctrl+C 时发送的信号。
# 第二个参数是信号处理函数 signal_handler，当程序接收到 SIGINT 信号时，会调用这个函数来处理信号。
signal.signal(signal.SIGINT, sig_handler)

while RUNNING:
    cpu_usage = psutil.cpu_percent(interval=1)
    total_mem = psutil.virtual_memory().total / (2 ** 30)
    used_mem = psutil.virtual_memory().used / (2 ** 30)
    free_mem = psutil.virtual_memory().free / (2 ** 30)
    mem_percent = used_mem / total_mem * 100
    root_usage = psutil.disk_usage('/').used / psutil.disk_usage('/').total * 100
    net_io_sent = psutil.net_io_counters().bytes_sent / (2 ** 20) # MiB
    net_io_recv = psutil.net_io_counters().bytes_recv / (2 ** 20) # MiB

    logger.info(f"CPU usage: {cpu_usage}%")
    logger.info(f"Total memory: {total_mem: .2f}GiB")
    logger.info(f"Used memory: {used_mem: .2f}GiB")
    logger.info(f"Free memory: {free_mem: .2f}GiB")
    logger.info(f"Memory used percent: {mem_percent: .2f}%")
    logger.info(f"Root partition usage: {root_usage: .2f}%")
    logger.info(f"Network IO Sent: {net_io_sent: .2f}MiB")
    logger.info(f"Network IO Received: {net_io_recv: .2f}MiB")

    time.sleep(5)