---
title: Python Linux运维模块
tags:
  - python/devops
  - python/subprocess
  - python/psutil
  - python/paramiko
  - python/fabric
  - python/json
  - python/yaml
aliases:
  - Python运维模块
  - subprocess psutil paramiko fabric
date: 2026-04-16
---

# Python Linux运维模块

本笔记涵盖 Python 运维开发中常用的核心模块:==subprocess==、==psutil==、==os==、==logging==、==paramiko==、==fabric==、==json==、==yaml==。

相关笔记: [[python-nginx]] | [[python-tomcat]] | [[python-mysql]] | [[python-elasticsearch]] | [[python-fabric高级用法]] | [[python-GUI-tkinter]]

---

## subprocess模块

`subprocess` 模块是 Python 用来管理和控制系统命令执行的工具，它可以让你从 Python 程序中运行外部的命令行命令，就像你在命令提示符或终端中手动输入命令一样。比如，你可以用它来执行 shell 命令、启动程序，或者处理子进程。

> [!summary] 核心概念
> - ==子进程==：当你使用 subprocess 模块运行命令时，Python 会创建一个新进程，这个进程就是"子进程"。
> - ==同步与异步==：你可以选择等待命令执行完成后再继续运行你的 Python 脚本（同步），或者不等待命令执行完毕直接继续运行（异步）。
> - ==输入、输出、错误流==：通过 subprocess，你可以与子进程进行交互，比如向命令提供输入，读取命令输出的结果，或者捕获错误信息。

常见的函数：

- `subprocess.run()`：这是最常用的函数，可以运行一个命令，并等待它执行完成。你可以获取命令的输出、错误信息等
- `subprocess.Popen()`：这个函数更加灵活，适用于更复杂的场景，比如你需要与子进程进行交互。

### subprocess.run()

使用示例：

```python
import subprocess

result = subprocess.run(['ls','-l'], capture_output=True, text=True)
# subprocess.run的第一个参数是列表，列表存放需要执行的命令
# capture_output=True 用于捕获命令输出，text=True 将输出以文本形式返回

print("\nAll the input:\n")
print(result)

print("\nstdout:\n")
print(result.stdout) # result.stdout 获取stdout

print("\nstderr:\n")
print(result.stderr) # result.stderr 获取stderr
```

自动化ping测试：

```python
import subprocess

result = subprocess.run(['ping','-c','6','www.baidu.com'], capture_output=True, text=True)
print(result.stdout)
```

#### 管道与重定向shell=True

`shell=True`：如果需要执行一个包含 shell 特性（如管道或重定向）的命令，可以设置shell=True。

```python
import subprocess

result = subprocess.run('ls -l | grep python', shell=True)
print(result.returncode)
# returncode为0说明命令正常执行并返回结果
# returncode为1说明没有返回结果
# returncode为127说明命令执行异常
```

#### 接收参数input

`input`参数用于向子进程提供输入数据，它特别适用于那些需要从标准输入（stdin）接收数据的命令

```python
import subprocess

result = subprocess.run(['grep','py'], input='python data',capture_output=True, text=True)
# 相当于echo "python data" | grep 'py'
print(result.stdout)
```

#### 超时处理timeout

==timeout== 参数用于限制命令的执行时间。如果命令执行的时间超过了设定的超时时间，就会抛出一个 `TimeoutExpired` 异常，防止命令长时间挂起或卡住。

```python
import subprocess

try:
    result = subprocess.run(['sleep', '5'], timeout=3)
	print(result.stdout)
except subprocess.TimeoutExpired as e: # 在规定了超时时间时，抛出的超时错误将会是subprocess.TimeoutExpired。错误是子进程抛出来的，exception要用子进程的
    print(f"Error: {e}")
```

#### 捕获错误与返回码check=True

通过指定参数 `check=True`，你可以确保命令在执行时成功完成。如果命令执行失败（即返回**非零退出状态**），会自动抛出 `CalledProcessError` 异常。

```python
import subprocess

try:
    result = subprocess.run(['ls', '/pypy'], check=True)
    print(result.stdout)

except subprocess.CalledProcessError as e: # 子进程抛出的错误要用子进程的exception
    print(f"Error: {e}")
```

---

### subprocess.Popen()

`subprocess.Popen()` 是 Python 中用于创建和管理子进程的类。它允许你与子进程进行复杂的交互。通过 stdin、stdout 和 stderr 管道,你可以将数据传递给子进程，读取子进程的输出，以及捕获子进程的错误信息。

#### 子进程通信communicate

```python
import subprocess

process = subprocess.Popen('cat', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,text=True)

# 通过stdin向子进程发送一个数据
stdout,stderr = process.communicate(input='Hello from python')

print(f"stdout:{stdout}")
print(f"stderr:{stderr}")
```

> [!note] Popen参数说明
> - `stdin=subprocess.PIPE` 表示你可以向子进程的标准输入发送数据
> - `stdout=subprocess.PIPE` 表示你可以从子进程的标准输出读取数据
> - `stderr=subprocess.PIPE` 表示你可以从子进程的标准错误输出读取错误信息
> - `text=True` 表示数据是以文本形式处理的（而不是字节）
> - subprocess.Popen()函数会返回一个Popen对象，表示刚刚启动的子进程

#### 捕获stderr

你可以通过 `stderr=subprocess.PIPE` 捕获子进程的错误信息，用`communicate()`方法获取到stderr，便于调试或记录日志。

```python
import subprocess

process = subprocess.Popen(['ls','/test'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,text=True )
stdout, stderr = process.communicate()
print(f"stdout:{stdout}")
print(f"stderr:{stderr}")
```

#### 捕获返回码wait()

`process.wait()` 用于让当前进程等待子进程完成。当子进程结束时，`wait()` 方法会返回子进程的退出码（exit code）。

```python
import subprocess

process = subprocess.Popen(['sleep','2'])
exit_code = process.wait()
print(f"Exit code: {exit_code}")
```

#### 终止子进程terminate/kill

- ==terminate()==: 发送 `SIGTERM` 信号，子进程可以选择优雅地处理
- ==kill()==: 发送 `SIGKILL` 信号，强制终止，不允许子进程进行任何清理工作

```python
import subprocess, time

process = subprocess.Popen(['sleep','30'])
time.sleep(5) # 暂停5s确保子进程已经被创建

print(f"subprocess running, PID: {process.pid}") # process.pid可以获取子进程的PID

# 使用terminate终止子进程
process.terminate()
print("SIGTERM has been sent.")
time.sleep(1) # 给点时间让子进程终止

# 使用poll检查进程状态。如果返回None说明还没终止；子进程已经终止会返回exit code
status = process.poll()
if status is None:
    print ("subprocess is still running, will kill it.")

    # 使用kill强行终止子进程
    process.kill()
    print("SIGKILL has been sent.")

else:
    print(f"subprocess has exited, exit code is {status}")
```

---

### 案例：实时监控磁盘使用情况并识别空间占用最大的目录

> [!tip] 重点
> - `splitlines()`按行分割，再`split()`按空格分割，就能把linux命令输出给拆分出来
> - 字典赋值`directory['key']=value`
> - 字典排序`sorted(directory.items(), lambda x:x[1], reverse=True)`，返回的是`[(k1,v1),(k2,v2)]`
> - 遍历字典排序后的元组列表：`for k, v in sorted_directory`

```python
import subprocess

def check_disk_usage(threshold, top_n=5):
    try:
        result = subprocess.run(['df', '-h'], capture_output=True, text=True, check=True)
        output = result.stdout

        print(f"disk usage:\n {output}")

        # 1.先检查磁盘使用率
        # splitlines按行分割，获取到每行的filesystem统计，存到列表里面
        lines = output.splitlines()
        # 从列表第二个元素开始遍历（第一行元素是输出的字段说明，不要）
        for line in lines[1:]:
            # 把每行再分割。split不写参数默认是按照空格分割
            columns = line.split()
            # 使用率去掉右边百分号，必须转成int才能比较
            percent_used = int(columns[4].rstrip('%'))

            if percent_used > threshold:
                print(f"Warning: Disk usage has exceeded threshold: {percent_used}")

        # 2. du获取目录或者文件大小。默认du只显示目录，-a显示文件，-h人类可读，-x忽略外部挂载的文件系统
        # du -ahx 获取某个目录下所有的目录和文件的磁盘占用情况
        result = subprocess.run(['du', '-ahx','/home/s0001969/Downloads/installation-packages'], capture_output=True, text=True, check=True)
        output = result.stdout
        lines = output.splitlines()

        directory_usage = {}
        # 字典赋值
        for line in lines:
            size, path = line.split(maxsplit=1)
            directory_usage[path]=size

        # 找出使用磁盘最多的文件，字典排序
        # sorted把字典键值对变成元组[('dir1','1'),('dir2',2)]
        # lamda x:x[1]指定按照字典value的值来排序
        # reverse=True从大到小排序
        sorted_dirs = sorted(directory_usage.items(), key=lambda x:x[1], reverse=True)
        print(f"Top {top_n} usage directory or file in: \n")

        #只取到列表前top_n个元素
        for path, size in sorted_dirs[:top_n]:
            print(f"Path: {path}, size: {size}")

    except subprocess.CalledProcessError as e:
        print(f"Command execution failed: {e}")
    except Exception as e:
        print(f"Exception occurred: {e}")

if __name__ == "__main__":
    # 设置磁盘使用率阈值为80%
    check_disk_usage(threshold=80, top_n=5)
```

---

## psutil模块

==psutil== 是一个跨平台库，用于检索系统的硬件信息，如 CPU、内存、磁盘、网络等资源使用情况。它广泛应用于系统监控、性能分析和运维自动化。

安装psutil：

```python
pip3 install psutil
# 清华源
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple psutil
```

### 获取所有程序的PID:process_iter()

```python
import psutil

# psutil.process_iter()返回一个process对象，遍历系统中所有正在运行的进程。
# ['pid', 'name']参数让其返回每个进程的PID和name。
for proc in psutil.process_iter(['pid', 'name']):
    # proc.info获取到一个字典，字典的kv是process_iter()里面我们规定的参数。类似于{'pid': 2958594, 'name': 'sh'}
    print(f"PID: {proc.info['pid']}, process name: {proc.info['name']}")
```

### 监控磁盘分区大小:disk_usage()

```python
import psutil

def get_disk_usage():
    # disk_partition()方法返回一个列表，里面是分区信息的元组 - namedtuple：
    # 类似于[sdiskpart(device='/dev/vg00/root', mountpoint='/', fstype='ext4', opts='rw')]
    part_usage = psutil.disk_partitions()

    # 遍历分区元组，获取其中mountpoint参数，让psutil.disk_usage计算使用情况
    for part in part_usage:
        # disk_usage方法获取到一个namedtuple，类似于：sdiskusage(total=1046, used=520, free=99, percent=5.0)
        usage = psutil.disk_usage(part.mountpoint)

        # 单位转换，字节转换为Gib，除以2的30次方（1 Gib的字节数）
        # 如果要转换为GB, 除以1024**3
        total_gb = usage.total / (2 ** 30)
        used_gb = usage.used / (2 ** 30)
        free_gb = usage.free / (2 ** 30)
        used_percentage = usage.used / usage.total * 100
        print(f"Mount point: {part.mountpoint}")
        print(f"Total: {total_gb: .2f} GiB")
        print(f"Used: {used_gb: .2f} GiB")
        print(f"Free: {free_gb: .2f} GiB")
        print(f"Used percentage: {used_percentage: .1f}%")
        print('-' * 30)

if __name__ == '__main__':
    get_disk_usage()
```

### 多核CPU使用率cpu_percent()

```python
import psutil

def get_cpu_usage():
    cpu_usage = psutil.cpu_percent(interval=1, percpu=True)
    print(f"CPU usage of every core: {cpu_usage}.")
    print(f"Overall CPU usage: {psutil.cpu_percent()}.")

if __name__ == '__main__':
    get_cpu_usage()
```

### 获取物理内存和交换分区统计vitrual_mamory()

```python
import psutil

def get_memory():
    # 物理内存使用情况
    mem_usage = psutil.virtual_memory()
    print(f"Total memory: {mem_usage.total / (2 ** 30) : .2f} GiB.")
    print(f"Used memory: {mem_usage.used / (2 ** 30) : .2f} GiB.")
    print(f"Available memory: {mem_usage.free / (2 ** 30) : .2f} GiB.")

    # 交换分区使用情况
    swap_usage = psutil.swap_memory()
    print(f"Total swap: {swap_usage.total / (2 ** 30) : .2f} GiB.")
    print(f"Used swap: {swap_usage.used / (2 ** 30) : .2f} GiB.")
    print(f"Available swap: {swap_usage.free / (2 ** 30) : .2f} GiB.")

if __name__ == '__main__':
    get_memory()
```

### 网络流量监控get_io_counters()

```python
import psutil

def get_net_io():
    net_io = psutil.net_io_counters()
    print(f"Total received byte: {net_io.bytes_recv / (2 ** 20): .2f} MiB.")
    print(f"Total sent byte: {net_io.bytes_sent / (2 ** 20): .2f} MiB.")

if __name__ == '__main__':
    get_net_io()
```

### 系统负载getloadavg()

```python
import psutil

def get_load():
    load = psutil.getloadavg()
    print(f"System load in 1 min: {load[0]: .2f}.")
    print(f"System load in 5 min: {load[1]: .2f}.")
    print(f"System load in 15 min: {load[2]: .2f}.")

if __name__ == '__main__':
    get_load()
```

### 案例：CPU、内存、根分区使用报告

```python
import psutil, shutil, datetime

def get_system_report():
    report = []
    report.append(f"Report time: {datetime.datetime.now().strftime('%m-%d')}.")
    report.append(f"CPU usage: {psutil.cpu_percent()}%.")
    report.append(f"Memory usage: {psutil.virtual_memory().percent}%.")
    total, used, free = shutil.disk_usage("/")
    report.append(f"Disk total: {(total / (2 ** 30)): .1f} Gib.")
    report.append(f"Disk used: {(used / (2 ** 30)): .1f} Gib.")
    report.append(f"Disk free: {(free / (2 ** 30)): .1f} Gib.")
	# 列表连成字符串打印
    return ('\n').join(report)

if __name__ == '__main__':
    print(get_system_report())
```

---

## os模块

==os== 模块是 Python 标准库中用于与操作系统进行交互的模块，主要提供对文件和目录的操作，以及对操作系统环境变量的访问和管理。

### 目录操作

```python
import os

# 获取当前工作目录
current_dir = os.getcwd()
print(f"current working dir: {current_dir}")

# 切换工作目录
os.chdir("/home/s0001969/Documents/learning-notes-git/Python")
current_dir = os.getcwd()
print(f"current working dir: {current_dir}")

# 列出指定目录下所有内容
contents = os.listdir('.')
print(f"Files in current dir:\n {contents}")

# 创建新目录，但是新目录已经存在时会抛异常
os.mkdir('new_dir')

# 递归创建新目录
os.makedirs('parent_dir/sub_dir')

# 删除目录，目录必须是空的，否则会报错
os.rmdir('new_dir')

# 递归删除目录，子目录必须全是空的
os.removedirs('parent_dir/sub_dir')
```

### 文件操作

```python
import os

file_path = '/path/to/python/old.txt'
os.chdir('/'.join(file_path.split('/')[:-1]))

# 判断文件是否存在
if not os.path.exists(file_path):
    with open (file_path, 'w') as f:
        f.write('test')
else:
    print(f"{file_path} exists.")

# 重命名文件
os.rename('old.txt','new.txt')
print("old.txt has been renamed to new.txt")

# 删除文件
os.remove('new.txt')
print(f"new.txt has been deleted.")

# 查看文件信息，返回元组
file_info = os.stat('oop.py')
print(file_info)

# 拼接文件路径
full_path = os.path.join('/', 'file.txt')
```

### 操作环境变量

```python
import os

# 列出所有环境变量
env_vars = os.environ
print(env_vars)

# 查询指定环境变量，若不存在，返回None
result = os.getenv('PATH')
print(f"env PATH is: {result}")

# 设置环境变量
os.environ['MY_VAR'] = '123'
print(f"ENV 'MY_VAR' has been set to: {os.getenv('MY_VAR')}")

# 删除环境变量
del os.environ['MY_VAR']
print("ENV 'MY_VAR' has been deleted.")
```

### 路径处理

```python
import os

path = '/path/to/python/'
file_name = 'oop.py'
os.chdir(path)

# 判断文件是否存在
print('File exists') if os.path.exists('oop.py') else print('File does not exists')

# 判断路径是否是文件
print("This is a file") if os.path.isfile('oop.py') else print("This is not a file")

# 判断路径是否是目录
print("This is a dir") if os.path.isdir('oop.py') else print("This is not a dir")

# 获取文件绝对路径
abs_path = os.path.abspath('ooo.py')
print(f"Absolute path: {abs_path}")

# 拆分绝对路径中的文件名和路径名
path = os.path.dirname(os.path.join(path, file_name))
file_name = os.path.basename(os.path.join(path, file_name))
print(f"path name: {path}, file name: {file_name}.")

# 拆分绝对路径成列表
dir_name, file_name =os.path.split(os.path.join(path, file_name))
print(f"path name: {dir_name}, file name: {file_name}.")

# 拆分文件名和扩展名
file_base_name, ext_name = os.path.splitext('oop.py')
print(f"file base name is: {file_base_name}, extention name is {ext_name}.")

# 获取文件大小
file_size = os.path.getsize('oop.py')
print(f"file size: {file_size} Byte")
```

---

## logging模块

==logging== 模块是 Python 标准库中的一个模块，用于记录和跟踪程序的运行状态和事件。

> [!info] 日志级别
> - ==DEBUG==：调试信息，通常用于开发过程中获取详细信息。
> - ==INFO==：普通信息，表示程序的正常运行状态。
> - ==WARNING==：警告信息，表示可能出现问题的情况。
> - ==ERROR==：错误信息，表示发生了错误，可能影响程序的某些功能。
> - ==CRITICAL==：严重错误信息，表示非常严重的错误，可能导致程序无法继续运行。

logging模块中的三个功能：

- ==日志记录器==：记录器是 logging 模块的主要接口，负责记录消息。通过名称来区分不同的记录器。
- ==处理器==：处理器将记录的日志消息发送到合适的目的地，比如控制台、文件等。
- ==格式化器==：格式化器定义了日志信息的输出格式。

### 基本日志记录器logging.basicConfig()

```python
import logging

# 基本 logging 记录器
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s-%(levelname)s-%(message)s',
                    datefmt='%m%d_%H:%M:%S')

# 记录日志
logging.debug("This is debug message")
logging.info("This is info message")
logging.warning("This is warning message")
logging.error("This is error message")
logging.critical("This is critical message")
```

> [!warning] 文件命名注意
> python的py文件命名最好不要与module名字重名，否则import module的时候会错误的引用到本文件。
>
> 比如这个脚本文件命名为`logging.py`,在其中`import logging`的时候，就会报错：
>
> ```sh
> Original exception was:
> Traceback (most recent call last):
>   File "/path/to/python/logging.py", line 1, in <module>
>     import logging
>   File "/path/to/python/logging.py", line 5, in <module>
>     logging.basicConfig(level=logging.DEBUG,
> AttributeError: partially initialized module 'logging' has no attribute 'basicConfig' (most likely due to a circular import)
> ```

### 自定义日志记录器logging.getLogger()

```python
import logging,os

os.chdir('/path/to/python/')

# getLogger()方法创建自定义记录器
logger = logging.getLogger('my_logger')
# 设定日志的记录级别
logger.setLevel(logging.DEBUG)

# 创建控制台处理器,意思是将收集到的日志通过控制台输出
# 设置控制台处理器的日志级别，意思是只有WARNING及以上的级别会被输出到控制台
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)

# 创建文件处理器,意思是将收集到的日志写入到文件中。所有级别的日志都会输出到文件
file_handler = logging.FileHandler('my_log.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

# 创建格式化器，应用到控制台处理器和文件处理器
formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s: %(message)s', datefmt='%Y%m%d_%H:%M:%S')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# 将处理器添加到记录器
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# 记录日志
logger.debug("This is a debug message.")
logger.info("This is an info message.")
logger.warning("This is a warning message.")
logger.error("This is an error message.")
logger.critical("This is a critical message.")
```

### 案例：日志文件切割RotatingFileHandler

使用 logging 模块的 ==RotatingFileHandler 处理器==来实现日志文件的切割。

```python
import logging, os
from logging.handlers import RotatingFileHandler

os.chdir('/path/to/python/')

# 创建一个日志记录器
logger = logging.getLogger('rotating_logger')
logger.setLevel(logging.DEBUG)

# 创建日志轮替处理器
# maxBytes=2000: 当文件大小达到2000字节，触发日志轮替
# backupCount = 5 最多保留五个旧的日志文件（my_log.log1 ... my_log.log5）
rotating_handler = RotatingFileHandler('my_log.log', maxBytes=2000,backupCount=5,encoding='utf-8')

# 创建格式化器
formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s: %(message)s', datefmt='%Y%m%d_%H:%M:%S')
rotating_handler.setFormatter(formatter)

# 将处理器添加到记录器上
logger.addHandler(rotating_handler)

# 记录日志，观察日志轮替的生成文件的结果
for i in range(1000):
    logger.debug(f'This is number {i} message.')
```

### 案例：报错信息自动发送到邮箱SMTPHandler

使用 ==SMTPHandler 处理器== 发送日志信息到电子邮件。

```python
import logging, os
from logging.handlers import SMTPHandler

os.chdir('/path/to/python/')

# 创建一个日志记录器
logger = logging.getLogger('smtp_logger')
logger.setLevel(logging.ERROR)

# 创建SMTP处理器,password是发件邮箱的smtp的授权码
smtp_handler = SMTPHandler(mailhost=('smtp.163.com', 25),
                           fromaddr='xxxxxx@163.com',
                           toaddrs=['xxxxx@qq.com'],
                           subject="Error log",
                           credentials=('user','password'),
                           secure=()
                           )

# 创建格式化器
formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s: %(message)s', datefmt='%Y%m%d_%H:%M:%S')
smtp_handler.setFormatter(formatter)

# 将处理器添加到记录器上
logger.addHandler(smtp_handler)

# 记录日志，每一条日志独立发送
logger.error(f'This is an error message.')
logger.critical(f'This is an critical message.')
```

---

## paramiko模块

==Paramiko== 是一个用于实现 SSH 协议的 Python 库，它提供了 SSH、SFTP 客户端和服务器的功能。

安装：

```sh
pip3 install paramiko
# 清华源
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple paramiko
```

### ssh连接

```python
import paramiko
# 创建ssh客户端
ssh = paramiko.SSHClient()
# 设置自动接受host key
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
# 连接到远程主机
ssh.connect(hostname='172.16.183.81', username='root', password='root')
# 执行命令ssh.exec_command返回一个三元可迭代: stdin, stdout, stderr
stdin, stdout, stderr = ssh.exec_command('df -h')
print(stdout.read().decode('utf-8'))
# 关闭连接
ssh.close()
```

#### AutoAddPolicy

==paramiko.AutoAddPolicy== 表示自动接受未知主机的密钥并将其添加到客户端的已知主机密钥列表中。

> [!warning] 安全提示
> 这种策略适合开发和测试环境，因为它避免了手动管理主机密钥的麻烦。然而，在生产环境中，这种策略可能存在安全风险，因为它无法防止连接到伪造的服务器。

### sftp操作

```python
import paramiko, os

# 创建ssh客户端
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)

# 准备本地文件路径
local_dir = '/path/to/python/'
local_file = 'oop.py'
local_path = os.path.join(local_dir,local_file)

# 连接到的远程服务器
hostname = '172.16.183.81'
port = 22
username = 'root'
password = 'root'
remote_path = '/root/oop.py'

try:
    os.makedirs(local_dir, exist_ok=True)
    if not os.path.exists(local_path):
        with open(local_path, 'w') as f:
            f.write("test")
        print(f"File {local_path} has been created.")

    ssh.connect(hostname, port, username, password)
    print(f"Connected to {hostname}.")
    sftp = ssh.open_sftp()
    sftp.put(local_path, remote_path)
    print(f"File transferred from {local_path} to {remote_path}.")

except Exception as e:
    print(f"Error occurred: {e}")

finally:
    sftp.close()
    ssh.close()
    print("Connection has closed.")
```

### 执行远程命令

==exec_command()== 是 paramiko SSHClient 的一个核心方法，用于在远程服务器上执行命令并获取执行结果。

#### 基本语法

```python
stdin, stdout, stderr = client.exec_command(command, bufsize=-1, timeout=None, get_pty=False, environment=None)
```

#### 参数说明

- **command**: 要执行的命令字符串
- **bufsize**: 缓冲区大小，默认 -1（系统默认）
- **timeout**: 命令执行超时时间（秒）
- **get_pty**: 是否分配伪终端，默认 False
- **environment**: 环境变量字典

#### 使用示例

1. 基本使用

```python
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.1.100', username='user', password='password')

stdin, stdout, stderr = client.exec_command('ls -la')
output = stdout.read().decode('utf-8')
error = stderr.read().decode('utf-8')

print("输出:", output)
print("错误:", error)

client.close()
```

2. 检查命令执行状态

```python
stdin, stdout, stderr = client.exec_command('ls /nonexistent')

exit_status = stdout.channel.recv_exit_status()
print(f"退出状态码: {exit_status}")

if exit_status == 0:
    print("命令执行成功")
    print(stdout.read().decode('utf-8'))
else:
    print("命令执行失败")
    print(stderr.read().decode('utf-8'))
```

3. 带超时的命令执行

```python
try:
    stdin, stdout, stderr = client.exec_command('sleep 10', timeout=5)
    output = stdout.read().decode('utf-8')
except paramiko.SSHException as e:
    print(f"命令执行超时: {e}")
```

4. 交互式命令（需要输入）

```python
stdin, stdout, stderr = client.exec_command('sudo ls', get_pty=True)
stdin.write('your_password\n')
stdin.flush()
output = stdout.read().decode('utf-8')
print(output)
```

5. 设置环境变量

```python
env = {'PATH': '/usr/local/bin:/usr/bin:/bin'}
stdin, stdout, stderr = client.exec_command('echo $PATH', environment=env)
print(stdout.read().decode('utf-8'))
```

> [!important] 注意事项
> 1. **资源管理**: 始终确保关闭连接
> 2. **错误处理**: 检查退出状态码而不仅仅是 stderr
> 3. **编码问题**: 使用 `.decode('utf-8')` 处理输出
> 4. **阻塞操作**: `exec_command` 是阻塞的，命令执行完才返回
> 5. **并发限制**: 一个 SSH 连接通常一次只能执行一个命令

### 案例：批量传输并解压镜像包

在本地下载了k8s镜像tar包，需要批量上传到多个远程主机并解压以供pod使用。

```python
"""
Kubernetes 镜像批量传输和加载工具

功能描述:
    该脚本用于自动化批量传输和加载 Kubernetes 镜像到多个远程主机。
    主要实现以下功能：
    1. 通过 SSH 连接到多个远程 Kubernetes 节点
    2. 使用 SFTP 将本地的 Docker 镜像 tar 包传输到远程主机
    3. 在远程主机上使用 containerd 的 ctr 命令导入镜像
    4. 支持批量处理多个镜像文件和多个目标主机
"""

import os, paramiko

def ssh_connect(host):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        client.connect(hostname=host, username='root', password='root')
        return client
    except Exception as e:
        print(f"Error: {str(e)}.")
        return None

def transfer_image(client, local_file, remote_file):
    try:
        sftp = client.open_sftp()
        sftp.put(local_file, remote_file)
        print(f"\n\nFiles transferred from {local_file} to {remote_file}.")
    except Exception as e:
        print(f"Error: {str(e)}.")
    finally:
        sftp.close()

def load_image(client, image_path):
    stdin, stdout, stderr = client.exec_command(f"ctr -n=k8s.io images import {image_path}")
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        print(f"{image_path} loaded")
        output = stdout.read().decode('utf-8').strip()
        if output:
            print(f"Output: {output}")
    else:
        error_msg = stderr.read().decode('utf-8').strip()
        print(f"Error loading {image_path}: {error_msg}.")

if __name__ == '__main__':

    local_path = r"D:\InstallationPackages\k8s-images"
    remote_path = "/root/"
    hosts = ['192.168.40.180','192.168.40.181','192.168.40.182']

    if not os.path.exists(local_path):
        print(f"{local_path} does not exist, creating...")
        os.makedirs(local_path)

    for host in hosts:
        client = ssh_connect(host)
        if not client:
            print(f"Error connected to {host}")
            break

        print(f"\n\nConnected to {host}")

        for image in os.listdir(local_path):
            if image.endswith(".tar"):
                local_file = os.path.join(local_path,image)
                remote_file = os.path.join(remote_path, image)
                transfer_image(client, local_file, remote_file)
                load_image(client, remote_file)

        client.close()
```

---

## fabric模块

==Fabric== 建立在 Paramiko 之上，是一个高级库，旨在简化和自动化通过 SSH 进行的任务。

> [!note] Fabric vs Paramiko
> - **Paramiko**：底层库，提供 SSH 协议实现，适合需要对 SSH 连接有更大控制的开发者
> - **Fabric**：高级库，提供更易于使用的 API，方便批量执行命令和文件传输，支持任务组织和多主机操作

安装：

```sh
pip3 install fabric --resume-retries 5
# 清华源
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple fabric
```

### 远程运行命令Connection.run()

```python
from fabric import Connection

conn = Connection(host='172.16.183.81', user='root', connect_kwargs={'password': 'root'})
result = conn.run('uname -a', hide=True)
print(result.stdout.strip())
conn.close()
```

### 远程执行sudo命令Connection.sudo()

```python
from fabric import Connection
conn = Connection(host='172.16.183.81', user='root', connect_kwargs={'password': 'root'})
result = conn.sudo('uname -a', password='root', hide=True)
print(result.stdout.strip())
conn.close()
```

### 本地文件上传Connection.put()

```python
from fabric import Connection

conn = Connection(host='172.16.183.81', user='root', connect_kwargs={'password': 'root'})
local_path = '/path/to/python/oop.py'
remote_path = '/root/oop.py'
try:
    conn.put(local_path, remote_path)
except Exception as e:
    print(f"Error occurred: {e}.")
finally:
    conn.close()
```

### 下载远程服务器文件Connection.get()

```python
from fabric import Connection

conn = Connection(host='172.16.183.81', user='root', connect_kwargs={'password': 'root'})
local_path = '/path/to/python/test.py'
remote_path = '/root/test.py'

try:
    conn.get(remote_path, local_path)
except Exception as e:
    print(f"Error occurred: {e}.")
finally:
    conn.close()
```

### 自动关闭连接

使用上下文管理器 ==with== 自动关闭ssh连接：

```python
from fabric import Connection

with Connection(host='172.16.183.81', user='root', connect_kwargs={'password': 'root'}) as conn:
    result = conn.run('uname -a')
    print(result.stdout)
```

### 判断远程路径是否存在

```python
from fabric import Connection

with Connection(host='172.16.183.81', user='root', connect_kwargs={'password': 'root'}) as conn:
    result = conn.run('test -e /root/oop.py && echo "exists" || echo "Not exists"', hide=True)
    print(result.stdout)
```

### 切换远程目录Connection.cd()

```python
from fabric import Connection

conn = Connection(host='172.16.183.81', user='root', connect_kwargs={'password': 'root'})
with conn.cd('/root/'):
    result = conn.run('ls', hide=True)
    print(result.stdout)
conn.close()
```

---

## json模块

==JSON== 是一种轻量级数据交换格式，既易于人类阅读和编写，又便于计算机解析和生成。

> [!summary] 核心方法
> - `json.dump()`：将python对象转换成json格式，并写入文件
> - `json.dumps()`：将python对象转换成json格式，并返回json字符串
> - `json.load()`：从文件读取json数据，转换为python对象
> - `json.loads()`：将json字符串转换为python对象

### 序列化到文件json.dump()

#### 语法参数

`json.dump(obj, fp, *, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=None, separators=None, default=None, sort_keys=False)`

- ==obj==：需要序列化的python对象
- ==fp==：文件对象，表示将json写入此文件中
- ==ensure_ascii==：默认True，非ASCII字符会被转义为`\uxxx`。设为False则保留原始字符
- ==indent==：控制输出的缩进格式
- ==sort_keys==：如果为True，字典键按字母顺序排序

```python
# ensure_ascii对比示例
import json
data = {'name': '张三'}
# 默认：{"name": "\u5f20\u4e09"}
json.dumps(data, ensure_ascii=True)
# 原始字符：{"name": "张三"}
json.dumps(data, ensure_ascii=False)
```

#### 示例

```python
import json

data = {
    'name': 'Alice',
    'age': 12,
    'city': 'Beijing',
    'skills': ['python','java','k8s']
}

with open ('python-manuscripts/data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)
```

### 序列化到字符串json.dumps()

与 json.dump() 参数一致，区别在于返回字符串而不是写入文件。

```python
import json

data = {
    'name': 'Alice',
    'age': 12,
    'city': 'Beijing',
    'skills': ['python','java','k8s']
}
json_str = json.dumps(data, indent=4, ensure_ascii=False)
print(json_str)
```

### 反序列化到文件json.load()

```python
import json

with open('python-manuscripts/data.json', 'r', encoding='utf-8') as f:
    data = json.load(f) # 在windows中需要用json.load(f.read())
    print(data)
    # 返回了一个字典
```

### 反序列化到字符串json.loads()

```python
import json

data = """{
    "name": "Alice",
    "age": 12,
    "city": "Beijing",
    "skills": [
        "python",
        "java",
        "k8s"
    ]
}"""

print(json.loads(data))
```

### 案例：配置文件管理

```python
import json

# 读取json文件并反序列化成字典
with open('python-manuscripts/config.json', 'r') as f:
    config = json.load(f)

# 修改字段
config['version'] = '1.0.1'
config['logging']['level'] = 'DEBUG'
config['notifications']['email']['username'] = 'test_user'

# 序列化到json文件
with open('python-manuscripts/config.json', 'w') as f:
    json.dump(config, f, indent=4)
```

### 案例：服务器状态监控

```python
import json, psutil, time
from datetime import datetime

status_data = []

for _ in range(5):
    status ={
        'timestamp': datetime.now().strftime('%m-%d %H:%M:%S'),
        'cpu_usage': psutil.cpu_percent(),
        'mem_usage': psutil.virtual_memory()
    }
	# 把每一秒生成的数据（字典）添加到列表中
    status_data.append(status)
    time.sleep(1)

with open('python-manuscripts/status.json', 'w') as f:
    json.dump(status_data, f, indent=4)
```

### 案例：用户权限管理

```python
import json

with open('python-manuscripts/permissions.json', 'r') as f:
    user_info = json.load(f)

user_info['user123']['access_level'] = 'admin'
user_info['user789']['active'] = True

with open('python-manuscripts/permissions.json', 'w') as f:
    json.dump(user_info, f, indent=4)
```

---

## PyYaml模块

==PyYAML== 是一个 Python 库，用于处理YAML格式的数据。YAML 是一种简洁、易读的文件格式，常用于配置文件。

安装：

```sh
pip3 install pyyaml
# 清华源
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple pyyaml
# 导入的是yaml模块
import yaml
```

> [!summary] 核心方法
> 1. `yaml.load()` - 解析 YAML 字符串为 Python 对象
> 2. `yaml.safe_load()` - 安全解析 YAML
> 3. `yaml.dump()` - 将 Python 对象序列化为 YAML 字符串
> 4. `yaml.safe_dump()` - 安全序列化
> 5. `yaml.load_all()` / `yaml.safe_load_all()` - 解析多个 YAML 文档
> 6. `yaml.dump_all()` / `yaml.safe_dump_all()` - 序列化多个对象

### 不安全的yaml对象

> [!warning] 安全风险
> 自定义对象或函数可能存在安全风险。恶意用户可以利用自定义标签执行任意代码：
> ```yaml
> execute: !!python/object/apply:os.system
> - rm -rf /
> ```
> 如果使用 `yaml.load()` 解析，可能会执行危险命令。推荐使用 `yaml.safe_load()`。

### 解析yaml数据yaml.load()

```python
import yaml

yaml_str = """
name: John
age: 30
languages:
- Python
- Java
"""

data = yaml.load(yaml_str, Loader=yaml.FullLoader)
print(data)
```

### 安全解析yaml数据yaml.safe_load()

```python
import yaml

yaml_str = """
name: John
age: 30
languages:
- Python
- Java
"""

data = yaml.safe_load(yaml_str)
print(data)
```

### 解析多个yaml数据yaml.load_all()

```python
import yaml

yaml_str = """
---
'name': Bob
'age': 18
---
'name': John
'age': 18
"""
documents = yaml.load_all(yaml_str, Loader=yaml.FullLoader)
for doc in documents:
    print(doc)
```

### 序列化python对象yaml.dump()

```python
import yaml
data ={
    'name': 'Bob',
    'age': 18,
    'languages':['Python', "Java"]
}
# 序列化到yaml字符串
yaml_str = yaml.dump(data, default_flow_style=False)
print(yaml_str)
# 序列化到文件
with open('python-manuscripts/status.yaml', 'w') as f:
    yaml.dump(data, f, default_flow_style=False)
```

### 序列化多个python对象yaml.dump_all()

```python
import yaml
data = [{'name':'Bob','age':18},{'name':'Joe','age':20}]
yaml_str = yaml.dump_all(data)
print(yaml_str) # 会生成yaml字符串，包含两个yaml,用 --- 隔开
```

### 案例：解析yaml配置文件

```python
import yaml

with open('python-manuscripts/deployment.yaml', 'r') as f:
    config = yaml.safe_load(f)

replicas = config['spec']['replicas']
print(replicas)

image = config['spec']['template']['spec']['containers'][0]['image']
print(image)
```

### 案例：批量更新yaml文件参数

```python
import yaml

def update_yaml(yaml_file, new_image):
    with open(yaml_file, 'r') as f:
        config = yaml.safe_load(f)
    config['spec']['template']['spec']['containers'][0]['image'] = new_image
    with open(yaml_file, 'w') as f:
        yaml.safe_dump(config, f)

if __name__ == '__main__':
    update_yaml('python-manuscripts/service1.yaml', 'janakiramm/myapp:v2')
    update_yaml('python-manuscripts/service2.yaml', 'janakiramm/myapp:v2')
```

### 案例：从yaml文件批量获取配置信息

```python
import yaml, os

def get_config(yaml_dir):
    report = []
    for file in os.listdir(yaml_dir):
        if file.endswith('.yaml'):
            with open(os.path.join(yaml_dir,file), 'r') as f:
                config = yaml.safe_load(f)
            name = config['metadata']['name']
            image = config['spec']['template']['spec']['containers'][0]['image']
            report.append(f"Service name: {name}, image version: {image}")
    return report

if __name__ == '__main__':
    os.chdir('Python/python-manuscripts')
    yaml_dir = 'configs'
    report = get_config(yaml_dir)
    for line in report:
        print(line)
```

---

## 综合案例

### 案例1：Linux CPU监控

#### 场景

1. 远程监控：实时监控linux机器所有服务的 CPU 使用率。
2. 阈值检测：定义 CPU 使用率阈值，自动重启超过阈值的进程。
3. 邮件通知：当高 CPU 占用进程被重启时，发送邮件通知运维人员。
4. 定时检查：每 5 秒检查一次 CPU 使用情况。
5. 优雅退出：通过ctrl+C允许脚本优雅退出。

#### 代码

```python
import paramiko, time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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
def sig_handler(sig, frame):
    global RUNNING
    RUNNING = False
    print("\nExiting Monitoring Program")

signal.signal(signal.SIGINT, sig_handler)

# 建立ssh连接
def ssh_connect():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    client.connect(IP, username=USERNAME, password=PASSWD)
    return client

# 获取linux每个cpu core使用率，平均cpu使用率
def get_cpu_usage(client):
    stdin, stdout, stderr = client.exec_command("mpstat -P ALL 1 1")
    output = stdout.read().decode().strip().splitlines()
    cpu_usage = {}
    total_usage = 0
    cpu_counts = 0

    print("\nmpstat output...")

    for line in output[4:]:
        parts = line.split()
        if len(parts) >= 12 and parts[2].isdigit():
            cpu_id = parts[2]
            try:
                user_percent = float(parts[3])
                cpu_usage[cpu_id] = user_percent
                total_usage += user_percent
                cpu_counts += 1
            except ValueError as e:
                print(f"Unable to get cpu {cpu_id} usage: {str(e)}")

    aver_cpu_usage = (total_usage / cpu_counts) if cpu_counts > 0 else 0
    return cpu_usage, aver_cpu_usage

# 获取占用cpu最高的进程
def get_high_cpu_process(client):
    stdin, stdout, stderr = client.exec_command("ps -eo pid,comm,%cpu --sort=-%cpu | head -n 10")
    output = stdout.read().decode().strip().splitlines()
    processes = []
    for line in output[1:]:
        parts = line.split()
        if len(parts) >= 3:
            pid = int(parts[0])
            name = ' '.join(parts[1:-1])
            cpu_usage = float(parts[-1])
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
    msg = MIMEMultipart()
    msg["From"] = SMTP_FROM
    msg["To"] = EMAIL_RECV
    msg["Subject"] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER, 25) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_FROM, EMAIL_RECV, msg.as_string())
    except Exception as e:
        print(f"Failed to send email: {str(e)}.")

# 监控远程服务器cpu
def monitor_cpu_usage():
    client = ssh_connect()
    try:
        while RUNNING:
            cpu_usage, aver_cpu_usage = get_cpu_usage(client)
            print(f"\nCPU usage per core:")
            for id, usage in cpu_usage.items():
                print(f"CPU: {id}: {usage: .2f}%")
            print(f"Average CPU Usage: {aver_cpu_usage: .2f}%")

            processes = get_high_cpu_process(client)
            aggre_process = {}
            for pid, name, usage in processes:
                if name in aggre_process.keys():
                    aggre_process[name]['usage'] += usage
                    aggre_process[name]['pids'].append(pid)
                else:
                    aggre_process[name] = {'usage': usage, 'pids': [pid]}

            high_cpu_list = []
            for name, info in aggre_process.items():
                total_usage = info['usage']
                pids = info['pids']
                print(f"Process {name}, pids {','.join(map(str, pids))} total CPU usage: {total_usage: .2f}%")
                if total_usage >= CPU_THRESHOLD:
                    for pid in pids:
                        restart_process(pid)
                    high_cpu_list.append(f"{name}, total cpu usage: {total_usage: .2f}%")
                if high_cpu_list:
                    subject = "WARNING: Detect high cpu usage processes"
                    body = f"Processes that has exceeded threshold {CPU_THRESHOLD}%:\n"
                    body += '\n'.join(high_cpu_list)
                    body += f"\n\nCurrent CPU usage:\n"
                    for id, usage in cpu_usage:
                        body += f"CPU {id}: {usage}"
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
```

> [!note] 信号处理
> - ==signal== 是 Python 用于处理信号的模块。当按下 Ctrl+C 时，操作系统会向进程发送 SIGINT 信号。
> - 通过 `signal.signal(signal.SIGINT, signal_handler)` 绑定信号处理函数，接收到 SIGINT 信号时，设置 RUNNING = False 停止主循环。

---

### 案例2：生成CPU、内存、交换分区、系统负载报告

```python
import psutil, time

# 获取CPU使用率
def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

# 获取内存使用率
def get_mem_usage():
    mem = psutil.virtual_memory()
    return mem.percent, mem.used / (1024 ** 3), mem.total / (1024 ** 3)

# 获取交换分区使用率
def get_swap_usage():
    swap = psutil.swap_memory()
    return swap.percent, swap.used / (1024 ** 3), swap.total / (1024 ** 3)

# 获取系统负载
def get_sys_load():
    return psutil.getloadavg()

# 分析系统瓶颈
def analyze_bottleneck(cpu, mem, swap, load):
    bottleneck_report = []
    if cpu > 80:
        bottleneck_report.append("High CPU usage")
    if mem[0] > 80:
        bottleneck_report.append(f"High memory usage. Memory used: {mem[1]: .2f} GB, used percent: {mem[0]}%.")
    if swap[0] > 80:
        bottleneck_report.append(f"High swap used. Swap used: {swap[1]: .2f} GB, used percent: {swap[0]}%.")
    cpu_count = psutil.cpu_count() or 1
    if load[0] > 2 * cpu_count:
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
```

---

### 案例3:定期备份目录和文件

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件和目录备份脚本
"""

import os, shutil
from datetime import datetime

# 定义源目录和目标目录
src_dir = 'path/to/source/directory'
dest_dir = 'path/to/destination/directory'

# 创建源目录和目标目录
if not os.path.exists(src_dir):
    print(f"Source directory '{src_dir}' does not exist, creating it now.")
    os.makedirs(src_dir)

if not os.path.exists(dest_dir):
    print(f"Destination directory '{dest_dir}' does not exist, creating it now.")
    os.makedirs(dest_dir)

# 创建子目录
os.makedirs(os.path.join(src_dir,'subdir1'), exist_ok=True)
os.makedirs(os.path.join(src_dir,'subdir2'), exist_ok=True)

# 创建测试文件
with open(os.path.join(src_dir, 'file1.txt'), 'w') as f:
    f.write('This is file 1.')

with open(os.path.join(src_dir, 'file2.txt'), 'w') as f:
    f.write('This is file 2.')

# 用时间戳命名备份目录
timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
backup_dir = os.path.join(dest_dir, f'backup_{timestamp}')
os.makedirs(backup_dir, exist_ok=True)

# 开始备份
for item in os.listdir(src_dir):
    src_item = os.path.join(src_dir, item)
    dest_item = os.path.join(backup_dir, item)

    if os.path.isdir(src_item):
        shutil.copytree(src_item, dest_item, dirs_exist_ok=True, copy_function=shutil.copy2)
    else:
        shutil.copy2(src_item, dest_item)

print(f"Backup completed successfully to {backup_dir}")
```

---

### 案例4：将系统指标同时输出至控制台和日志文件

```python
"""
系统资源监控与日志记录脚本
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
def sig_handler(sig, frame):
    global RUNNING
    RUNNING = False
    print("\nExiting Monitoring Program")

signal.signal(signal.SIGINT, sig_handler)

while RUNNING:
    cpu_usage = psutil.cpu_percent(interval=1)
    total_mem = psutil.virtual_memory().total / (2 ** 30)
    used_mem = psutil.virtual_memory().used / (2 ** 30)
    free_mem = psutil.virtual_memory().free / (2 ** 30)
    mem_percent = used_mem / total_mem * 100
    root_usage = psutil.disk_usage('/').used / psutil.disk_usage('/').total * 100
    net_io_sent = psutil.net_io_counters().bytes_sent / (2 ** 20)
    net_io_recv = psutil.net_io_counters().bytes_recv / (2 ** 20)

    logger.info(f"CPU usage: {cpu_usage}%")
    logger.info(f"Total memory: {total_mem: .2f}GiB")
    logger.info(f"Used memory: {used_mem: .2f}GiB")
    logger.info(f"Free memory: {free_mem: .2f}GiB")
    logger.info(f"Memory used percent: {mem_percent: .2f}%")
    logger.info(f"Root partition usage: {root_usage: .2f}%")
    logger.info(f"Network IO Sent: {net_io_sent: .2f}MiB")
    logger.info(f"Network IO Received: {net_io_recv: .2f}MiB")

    time.sleep(5)
```
