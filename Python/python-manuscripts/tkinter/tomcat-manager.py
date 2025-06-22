import tkinter as tk
from tkinter import messagebox, scrolledtext
import paramiko

HOST = '192.168.40.80'
USERNAME = 'root'
PASSWD = '111111'

TOMCAT_START_CMD = "/opt/tomcat/bin/catalina.sh start"
TOMCAT_STOP_CMD = "/opt/tomcat/bin/catalina.sh stop"
TOMCAT_STATUS_CMD = "ps -ef | grep tomcat | grep -v grep"

def connect_ssh():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOST, username=USERNAME, password=PASSWD)
        # 函数返回SSH客户端对象，以便后面用来执行命令
        return client
    except Exception as e:
        # insert方法会将信息插入到一个文本区域中（（例如ScrolledText组件））
        log_text.insert(tk.END, f"Connection failed: {str(e)}\n")
        return None

def start_tomcat():
    client = connect_ssh()
    # 检查ssh连接是否有效，连接成功才往后执行
    if client:
        try:
            stdin, stdout, stderr = client.exec_command(TOMCAT_START_CMD)
            # 从标准错误读取结果，decode解码成字符串
            error = stderr.read().decode()
            # 如果 error 不为空，表示启动过程中出现了错误，将错误信息插入到文本区域
            if error:
                log_text.insert(tk.END, f"Failed to start tomcat: {error}\n")
            else:
                log_text.insert(tk.END, "Tomcat started successfully.\n")
        finally:
            client.close()

def stop_tomcat():
    client = connect_ssh()
    if client:
        try:
            stdin, stdout, stderr = client.exec_command(TOMCAT_START_CMD)
            error = stderr.read().decode()
            if error:
                log_text.insert(tk.END, f"Failed to stop tomcat: {error}\n")
            else:
                log_text.insert(tk.END, "Tomcat stopped successfully.\n")
        finally:
            client.close()

def check_status():
    client = connect_ssh()
    if client:
        try:
            stdin, stdout, stderr = client.exec_command(TOMCAT_STATUS_CMD)
            error = stderr.read().decode()
            output = stdout.read().decode()
            if error:
                log_text.insert(tk.END, f"Failed to check tomcat status: {error}\n")
            else:
                # 如果有输出，表示tomcat正在运行
                if output.strip():
                    log_text.insert(tk.END, 'Tomcat is running\n')
                else:
                    log_text.insert(tk.END, 'Tomcat is not running\n')
            log_text.insert(tk.END, output+'\n')
        finally:
            client.close()

if __name__ == '__main__':
    # 创建一个 Tk 类的实例。
    # Tk 是 tkinter 模块中的一个类，代表一个窗口或应用程序的主窗口。通过创建这个实例，程序将显示一个新的窗口。
    window = tk.Tk()
    # 窗口标题
    window.title('Tomcat Manager')

    # 启动按钮
    # width=20表示按钮的宽度为 20 个字符单位。
    start_button = tk.Button(window, text='Start Tomcat', command=start_tomcat, width=20)
    # row=0: 指定按钮位于网格的第 0 行。
    # column=0: 指定按钮位于网格的第 0 列。
    # padx=10: 为按钮的左右两侧添加 10 像素的内边距。
    # pady=10: 为按钮的上下两侧添加 10 像素的内边距。
    start_button.grid(row=0, column=0, padx=10, pady=10)

    # 停止按钮
    stop_button = tk.Button(window, text='Stop Tomcat', command=stop_tomcat, width=20)
    stop_button.grid(row=0, column=1, padx=10, pady=10)

    # 查看状态按钮
    status_button = tk.Button(window, text='Check tomcat status', command=check_status, width=20)
    status_button.grid(row=1, column=0, padx=10, pady=10)

    # 滚动日志窗口
    # ScrolledText 是 tkinter.scrolledtext 模块中的一个类
    # 它扩展了 Text 控件，添加了滚动条功能，方便用户查看长文本内容
    # width=80: 设置文本区域的宽度为 80 个字符单位。
    # height=20: 设置文本区域的高度为 20 行文本。
    log_text = scrolledtext.ScrolledText(window, width=80, height=20)
    # columnspan=2: log_text 文本区域将占用从指定的列（column=0）开始的两个连续列。
    # 这意味着它不仅会占用第 0 列，还会占用第 1 列。
    # 通过让文本区域跨越两列，控件的宽度会变得更大，这样可以在文本区域内部显示更多的内容，减少用户需要滚动的频率。
    log_text.grid(row=2, column=0 ,columnspan=2, padx=10, pady=10)

    # 退出按钮
    exit_button = tk.Button(window, text='Exit', command=window.quit, width=20)
    exit_button.grid(row=1, column=1, padx=10, pady=10)

    window.mainloop()