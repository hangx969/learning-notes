import paramiko, time, smtplib
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
