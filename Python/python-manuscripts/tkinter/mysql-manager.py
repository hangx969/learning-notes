import tkinter as tk
from tkinter import messagebox, scrolledtext
import paramiko, pymysql

SSH_HOST = '192.168.40.80'
SSH_USERNAME = 'root'
SSH_PASSWD = '111111'
MYSQL_HOST = '192.168.40.80'
MYSQL_USER = 'root'
MYSQL_PASSWD = '111111'
MYSQL_PORT = 3306

def connect_ssh():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(SSH_HOST, username=SSH_USERNAME, password=SSH_PASSWD)
        return client
    except Exception as e:
        messagebox.showerror(f"Failed to connect ssh: {str(e)}\n")
        return None

def execute_ssh_command(command):
    client = connect_ssh()
    if client:
        try:
            stdin, stdout, stderr = client.exec_command(command)
            # 把远程命令的输出和错误放一起返回
            result = stdout.read().decode('utf-8') + stderr.read().decode('utf-8')
            return result
        finally:
            client.close()
    return None

def check_mysql_status():
    result = execute_ssh_command('systemctl status mysqld')
    if "active(running)" in str(result):
        status_label.config(text='Mysql status: running', fg='green')
    else:
        status_label.config(text='Mysql status: stopped', fg='red')
    output_text.insert(tk.END, f"Mysql status checking result:\n{result}\n")


def start_mysql():
    result = execute_ssh_command('systemctl start mysqld')
    output_text.insert(tk.END, f"Mysql start result:\n{result}\n")
    check_mysql_status()

def stop_mysql():
    result = execute_ssh_command('systemctl stop mysqld')
    output_text.insert(tk.END, f"Mysql stop result:\n{result}\n")
    check_mysql_status()

def connect_mysql():
    try:
        connection = pymysql.connect(
            host = MYSQL_HOST,
            user = MYSQL_USER,
            password = MYSQL_PASSWD,
            port = MYSQL_PORT
        )
        return connection
    except Exception as e:
        messagebox.showerror(f"Error: cannot connect to mysql: {e}\n")
        return None

def create_database():
    db_name = db_name_entry.get().strip()
    if not db_name:
        messagebox.showwarning("Warning: please input the database name!\n")
        return
    connection = connect_mysql()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute(f"CREATE DATABASE {db_name}")
            connection.commit()
            output_text.insert(tk.END, f"Database {db_name} has been created sucessfully.\n")
        except Exception as e:
            messagebox.showerror(f'Error: failed to create database: {str(e)}\n')
        finally:
            connection.close()

def create_table():
    db_name = db_name_entry.get().strip()
    table_name = table_name_entry.get().strip()
    table_definition = table_definition_entry.get().strip()
    if not db_name or not table_name or not table_definition:
        messagebox.showwarning("Warning: please input required table info!\n")
        return
    connection = connect_mysql()
    if connection:
        try:
            connection.select_db(db_name)
            cursor = connection.cursor()
            cursor.execute(f'CREATE TABLE {table_name} ({table_definition})')
            connection.commit()
            output_text.insert(tk.END, f"Table {table_name} has been created successfully\n")
        except Exception as e:
            messagebox.showerror(f'Error: failed to create table: {str(e)}')
        finally:
            connection.close()

def insert_data():
    db_name = db_name_entry.get().strip()
    table_name = table_name_entry.get().strip()
    data_values = data_values_entry.get().strip()
    if not db_name or not table_name or not data_values:
        messagebox.showerror("Warning, please input required info!")
        return
    connection = connect_mysql()
    if connection:
        try:
            connection.select_db(db_name)
            cursor = connection.cursor()
            cursor.execute(f'INSERT INTO {table_name} VALUES ({data_values})')
            connection.commit()
            output_text.insert(tk.END, f'Data has inserted into {table_name} successfully.\n')
        except Exception as e:
            messagebox.showerror(f'Failed to insert data: {str(e)}')
        finally:
            connection.close()

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Mysql Manager')

    ssh_frame = tk.LabelFrame(root, text='Mysql Management', padx=10, pady=10)
    ssh_frame.pack(padx=10, pady=10, fill='x')

    status_label = tk.Label(ssh_frame, text='Mysql Status: Unknown', fg='blue')
    status_label.pack()

    tk.Button(ssh_frame, text='Start mysql', command=start_mysql).pack(side='left', padx=5)
    tk.Button(ssh_frame, text='Stop mysql', command=stop_mysql).pack(side='left', padx=5)
    tk.Button(ssh_frame, text='Check mysql status', command=check_mysql_status).pack(side='left', padx=5)

    db_frame = tk.LabelFrame(root, text='Database operation', padx=10, pady=10)
    db_frame.pack(padx=10, pady=10, fill='x')

    tk.Label(db_frame, text='Database name').grid(row=0, column=0, sticky='w', padx=5, pady=5)
    db_name_entry = tk.Entry(db_frame)
    db_name_entry.grid(row=0, column=1, padx=5, pady=5)
    tk.Button(db_frame, text='Create database', command=create_database).grid(row=0, column=2, padx=5)

    tk.Label(db_frame, text='Table name').grid(row=1, column=0, sticky='w', padx=5, pady=5)
    table_name_entry = tk.Entry(db_frame)
    table_name_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(db_frame, text='Table definition (e.g., id INT, name VARCHAR(50), age INT):').grid(row=2, column=0, sticky='w', padx=5, pady=5)
    table_definition_entry = tk.Entry(db_frame, width=50)
    table_definition_entry.grid(row=2, column=1, padx=5, pady=5)
    tk.Button(db_frame, text='Create table', command=create_table).grid(row=3, column=0, columnspan=3, pady=5)

    tk.Label(db_frame, text="Data values (e.g., 1, 'Alice', 15):").grid(row=4, column=0, sticky='w', padx=5, pady=5)
    data_values_entry = tk.Entry(db_frame, width=50)
    data_values_entry.grid(row=4, column=1, columnspan=2, padx=5, pady=5)
    tk.Button(db_frame, text='Insert data', command=insert_data).grid(row=5, column=0, columnspan=3, pady=5)

    output_frame = tk.LabelFrame(root, text='Results', padx=10, pady=10)
    output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, height=10)
    output_text.pack(fill='both', expand=True)

    root.mainloop()