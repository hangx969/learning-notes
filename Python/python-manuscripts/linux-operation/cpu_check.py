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
IP = "172.16.183.80"
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
    print("\nExiting Monitoing Program")

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
    client.exec_command("mpstat -P ALL 1 1")