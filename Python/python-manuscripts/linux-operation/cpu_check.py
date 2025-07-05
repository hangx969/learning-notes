"""
Linux远程服务器CPU监控脚本

功能描述：
1. 通过SSH连接远程Linux服务器，实时监控CPU使用率
2. 使用mpstat命令获取每个CPU核心的使用率统计信息
3. 识别占用CPU资源最高的进程（TOP 10）
4. 当进程CPU使用率超过设定阈值时，自动重启该进程
5. 发送邮件告警通知管理员高CPU使用率情况
6. 支持优雅退出（Ctrl+C信号处理）

依赖要求：
- 远程服务器需安装sysstat包（yum install sysstat）
- Python依赖：paramiko库用于SSH连接
"""

import paramiko, time
# 导入smtplib用于设置邮件服务器，发送邮件
import smtplib
# 导入MIMEText用于创建邮件正文
from email.mime.text import MIMEText
# 导入MIMEMultipart用于创建邮件，允许邮件包含文本、附件、图片等
from email.mime.multipart import MIMEMultipart
# 导入signal用于处理信号。比如按ctrl+C发送中断信号
import signal

# 定义全局变量
IP = "192.168.40.180"
USERNAME = "root"
PASSWD = "root"
CPU_THRESHOLD = 400
# 定义邮件变量
SMTP_SERVER = "smtp.163.com"
SMTP_FROM = "xxxxxx@163.com"
SMTP_USER = "xxxxxx@163.com"
SMTP_PASS = "xxxxx"
EMAIL_RECV = "xxx@qq.com"

# 定义控制程序退出
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

# 建立ssh连接
def ssh_connect():
    client = paramiko.SSHClient()
    # 自动添加主机密钥
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    # 连接到远程服务器
    client.connect(IP, username=USERNAME, password=PASSWD)
    return client


# 获取linux每个cpu core使用率，平均cpu使用率
def get_cpu_usage(client):
    #  "mpstat -P ALL 1 1" 是 Linux 系统中用来获取每个 CPU 核心使用率的命令：
    # -P ALL 表示显示所有 CPU 核心的信息。1 1 表示每秒采样一次，持续 1 秒。
    # 安装：yum install sysstat
    stdin, stdout, stderr = client.exec_command("mpstat -P ALL 1 1")
    # 输出的每一行保存到列表中
    output = stdout.read().decode().strip().splitlines()
    # 字典存储每个核心CPU使用率
    cpu_usage = {}
    total_usage = 0
    cpu_counts = 0

    print("\nmpstat output...")

    for line in output[4:]:
        # 把每一行按空格分割
        parts = line.split()
        # 获取每个cpu id。isdigit只能捕获纯整数字符串，0.08这种浮点数不行。所以把下半部分average给排除出去了。
        if len(parts) >= 12 and parts[2].isdigit():
            cpu_id = parts[2]

            try:
                # 获取用户态cpu使用率
                user_percent = float(parts[3])
                # 字典赋值
                cpu_usage[cpu_id] = user_percent
                # 计算所有cpu用户态使用率
                total_usage += user_percent
                # 累计cpu数量
                cpu_counts += 1

            except ValueError as e:
                print(f"Unable to get cpu {cpu_id} usage: {str(e)}")

    aver_cpu_usage = (total_usage / cpu_counts) if cpu_counts > 0 else 0
    return cpu_usage, aver_cpu_usage


# 获取占用cpu最高的进程
def get_high_cpu_process(client):
    # ps -e显示所有进程，-o自定义输出格式，comm是进程名称。-%cpu降序排列
    stdin, stdout, stderr = client.exec_command("ps -eo pid,comm,%cpu --sort=-%cpu | head -n 10")
    output = stdout.read().decode().strip().splitlines()
    processes = []
    for line in output[1:]: # 跳过表头
        parts = line.split()
        if len(parts) >= 3:
            # 获取进程pid
            pid = int(parts[0])
            # 有的进程中间带空格会被拆分，现在把这种情况的进程名拼起来
            name = ' '.join(parts[1:-1])
            cpu_usage = float(parts[-1])
            # 数据用元组打包放进列表
            processes.append((pid, name, cpu_usage))
    return processes

# 重启进程
def restart_process(pid):
    client = ssh_connect()
    try:
        client.exec_command(f"kill -9 {pid}")
        time.sleep(1)
        print(f"Prpcess {pid} has been killed, restarting.")
    except Exception as e:
        print(f"Failed to restart process {pid}: {str(e)}.")
    finally:
        client.close()


# 发送邮件
def send_email(body, subject):
    # 创建MIMEMultipart对象，表示一封可以包含多部分的邮件
    msg = MIMEMultipart()
    # 构造发送信息
    msg["From"] = SMTP_FROM
    msg["To"] = EMAIL_RECV
    msg["Subject"] = subject
    # 构造正文，并添加到邮件中
    msg.attach(MIMEText(body, 'plain'))

    try:
        # 使用smtp服务器发送邮件
        with smtplib.SMTP(SMTP_SERVER, 25) as server:
            server.login(SMTP_USER, SMTP_PASS)
            # 发送邮件
            server.sendmail(SMTP_FROM, EMAIL_RECV, msg.as_string())
    except Exception as e:
        print(f"Failed to send email: {str(e)}.")


# 监控远程服务器cpu，识别占用cpu最高的进程
def monitor_cpu_usage():
    client = ssh_connect()
    try:
        # 这里是信号真正发挥作用的地方，当按ctrl c的时候全局变量RUNNING通过信号处理函数变成FALSE，循环终止。
        while RUNNING:
            # 获取每个cpu使用率和平均cpu使用率。返回字典、数值
            cpu_usage, aver_cpu_usage = get_cpu_usage(client)
            print(f"\nCPU usage per core:")
            for id, usage in cpu_usage.items():
                print(f"CPU: {id}: {usage: .2f}%")
            print(f"Average CPU Usage: {aver_cpu_usage: .2f}%")

            # 获取占用cpu最高的前10个进程。返回列表
            processes = get_high_cpu_process(client)
            # 聚合相同进程的cpu使用率。因为有些相同进程会有多条：同样的name，不同的pid
            # 创建字典，主要是把相同name的不同pid放到一起，把相同name的usage累加
            aggre_process = {}
            for pid, name, usage in processes:
                # 如果进程重复，那就把usage累加，pid放列表里
                if name in aggre_process.keys():
                    aggre_process[name]['usage'] += usage
                    aggre_process[name]['pids'].append(pid)
                # 如果是新进程，就单开usage和pid
                else:
                    aggre_process[name] = {'usage': usage, 'pids': [pid]}

            # 存储cpu占用较高进程
            high_cpu_list = []
            for name, info in aggre_process.items():
                #获取聚合后的字典里面的所有进程、cpu使用率
                total_usage = info['usage']
                pids = info['pids']
                print(f"Process {name}, pids {','.join(map(str, pids))} total CPU usage: {total_usage: .2f}%")
                # 发现超过阈值的进程，执行重启，放到列表里
                if total_usage >= CPU_THRESHOLD:
                    for pid in pids:
                        restart_process(pid)
                    high_cpu_list.append(f"{name}, total cpu usage: {total_usage: .2f}%")
                # 字典都检测完，生成的重启列表，如果里面有元素，说明确实检测出来了，发送邮件告警。
                if high_cpu_list:
                    subject = "WARNING: Detect high cpu usage processes"
                    # 邮件正文不停的+=添加内容
                    body = f"Processes that has exceeded threshold {CPU_THRESHOLD}%:\n"
                    body += '\n'.join(high_cpu_list)

                    # 再次打印每个cpu core使用率
                    body += f"\n\nCurrent CPU usage:\n"
                    for id, usage in cpu_usage:
                        body += f"CPU {id}: {usage}"
                    # 发送邮件
                    print("Sending email...")
                    send_email(body, subject)
                else:
                    print("No high cpu process is detected.")

                time.sleep(5)

    except Exception as e:
        print(str(e))

    finally:
        client.close()

if __name__ == '__main__':
    monitor_cpu_usage()