import tkinter as tk
from tkinter import messagebox
import paramiko

HOST = '172.16.183.80'
USERNAME = 'root'
PASSWD = '111111'

# ssh执行命令
def run_system_command(command):
    ssh = paramiko.SSHClient()
    # 自动接受远程主机host key
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, username=USERNAME, password=PASSWD)
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        return output.strip(), error.strip()
    except Exception as e:
        return "", str(e)
    finally:
        ssh.close()

# 获取nginx服务状态
def get_nginx_status():
    output, error = run_system_command('systemctl is-active nginx')
    if error:
        return "Status unknown"
    return output.strip()

# 自动更新nginx状态的标签
def update_status_label():
    status = get_nginx_status()
    # status_label是后面定义的标签。参数怎么传进来的？
    status_label.config(text=f"Nginx Status: {status}")
    # 每5秒更新一次状态
    root.after(5000, update_status_label)

# 启动nginx服务
def start_nginx():
    output, error = run_system_command("systemctl start nginx")
    if error:
        # 定义弹窗
        messagebox.showerror("Error", f"Failed to start nginx: {error}")
    else:
        messagebox.showinfo("Success", f"Nginx has been started")
    update_status_label()

# 停止nginx服务
def stop_nginx():
    output, error = run_system_command("systemctl stop nginx")
    if error:
        messagebox.showerror("Error", f"Failed to stop nginx: {error}")
    else:
        messagebox.showinfo("Success", f"Nginx has been stopped")
    update_status_label()

# 重启nginx
def restart_nginx():
    output, error = run_system_command("systemctl restart nginx")
    if error:
        messagebox.showerror("Error", f"Failed to restart nginx: {error}")
    else:
        messagebox.showinfo("Success", f"Nginx has been restarted")
    update_status_label()

# 查看nginx日志
def view_nginx_logs():
    output, error = run_system_command("tail -fn 100 /var/log/nginx/access.log")
    if error:
        messagebox.showerror("Error", f"Failed to get nginx log: {error}")
    else:
        # 创建文本框子窗口，把日志放进去
        logs_window = tk.Toplevel(root)
        logs_window.title("Nginx Log")
        logs_text = tk.Text(logs_window, wrap='word')
        logs_text.insert(tk.END, output)
        logs_text.pack(fill='both', expand=True)


if __name__ == '__main__':
    # 创建GUI主窗口
    root = tk.Tk()
    root.title("Nginx manager")

    # 显示nginx状态的标签
    status_label = tk.Label(root, text="Nginx Status: Checking...", font=('Arial', 12))
    status_label.pack(padx=10, pady=10)

    # 创建启动按钮
    start_button = tk.Button(root, text="Start Nginx", command=start_nginx)
    start_button.pack(padx=10,pady=10)

    #创建停止按钮
    stop_button = tk.Button(root, text="Stop Nginx", command=stop_nginx)
    stop_button.pack(padx=10,pady=10)

    #创建重启按钮
    restart_button = tk.Button(root, text="Restart Nginx", command=restart_nginx)
    restart_button.pack(padx=10,pady=10)

    # 查看日志按钮
    nginx_log_button = tk.Button(root, text="Get Nginx Log", command=view_nginx_logs)
    nginx_log_button.pack(padx=10,pady=10)

    update_status_label()

    # 运行主程序，窗口持续显示
    root.mainloop()