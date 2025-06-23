import tkinter as tk
from tkinter import messagebox, scrolledtext
import paramiko

HOST = '192.168.40.80'
USERNAME = 'root'
PASSWD = '111111'
HTTPD_SERVICE = 'httpd'
LOG_PATH = '/var/log/httpd/access.log'

def create_ssh_client():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOST, username=USERNAME, password=PASSWD)
        return client
    except Exception as e:
        messagebox.showerror('Error', f"Failed to connect SSH: {str(e)}\n")
        return None

def check_status():
    client = create_ssh_client()
    if client:
        stdin, stdout, stderr = client.exec_command(f'systemctl status {HTTPD_SERVICE}')
        output = stdout.read().decode()
        if "running" in str(output):
            status_text.delete(1.0, tk.END)
            status_text.insert(tk.END, 'Running')
        else:
            status_text.delete(1.0, tk.END)
            status_text.insert(tk.END, 'Not Running')
        client.close()

def start_service():
    client = create_ssh_client()
    if client:
        try:
            stdin, stdout, stderr = client.exec_command(f'systemctl start {HTTPD_SERVICE}')
            error = stderr.read().decode()
            if error:
                messagebox.showerror("Error", f"Failed to start httpd: {error}\n")
            else:
                messagebox.showinfo('Info', 'Httpd has been started\n')
        finally:
            client.close()

def stop_service():
    client = create_ssh_client()
    if client:
        try:
            stdin, stdout, stderr = client.exec_command(f'systemctl stop {HTTPD_SERVICE}')
            error = stderr.read().decode()
            if error:
                messagebox.showerror("Error", f"Failed to stop httpd: {error}\n")
            else:
                messagebox.showinfo('Info', 'Httpd has been stopped\n')
        finally:
            client.close()

def view_log():
    client = create_ssh_client()
    if client:
        stdin, stdout, stderr = client.exec_command(f'cat {LOG_PATH}')
        error = stderr.read().decode()
        if error:
            messagebox.showerror("Error", f"Failed to get httpd log: {error}\n")
        else:
            log_content = stdout.read().decode()
            log_window = tk.Toplevel(root)
            log_window.title('Httpd logs')
            log_text = scrolledtext.ScrolledText(log_window, height=20, width=80)
            log_text.pack()
            log_text.insert(tk.END, log_content)
        client.close()


if __name__ == '__main__':
    root = tk.Tk()
    root.title("Httpd service management")

    status_label = tk.Label(root, text='httpd service status:')
    status_label.pack()
    status_text = tk.Text(root, height=1, width=30)
    status_text.pack()

    check_status_button = tk.Button(root, text='Check status', command=check_status)
    check_status_button.pack()

    start_button = tk.Button(root, text='start service', command=start_service)
    start_button.pack()

    stop_button = tk.Button(root, text='stop service', command=stop_service)
    stop_button.pack()

    log_button = tk.Button(root, text='check logs', command=view_log)
    log_button.pack()

    root.mainloop()
