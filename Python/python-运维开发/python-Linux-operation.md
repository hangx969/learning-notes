# subprocess模块

`subprocess` 模块是 Python 用来管理和控制系统命令执行的工具，它可以让你从 Python 程序中运行外部的命令行命令，就像你在命令提示符或终端中手动输入命令一样。比如，你可以用它来执行 shell 命令、启动程序，或者处理子进程。

核心概念：

- 子进程：当你使用 subprocess 模块运行命令时，Python 会创建一个新进程，这个进程就是“子进程”。
- 同步与异步：你可以选择等待命令执行完成后再继续运行你的 Python 脚本（同步），或者不等待命令执行完毕直接继续运行（异步）。
- 输入、输出、错误流：通过 subprocess，你可以与子进程进行交互，比如向命令提供输入，读取命令输出的结果，或者捕获错误信息。

常见的函数：

- `subprocess.run()`：这是最常用的函数，可以运行一个命令，并等待它执行完成。你可以获取命令的输出、错误信息等
- `subprocess.Popen()`：这个函数更加灵活，适用于更复杂的场景，比如你需要与子进程进行交互。

## subprocess.run()

使用示例：

~~~python
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
~~~

自动化ping测试：

~~~python
import subprocess

result = subprocess.run(['ping','-c','6','www.baidu.com'], capture_output=True, text=True)
print(result.stdout)
~~~

### 管道与重定向shell=True

`shell=True`：如果需要执行一个包含 shell 特性（如管道或重定向）的命令，可以设置shell=True。

~~~python
import subprocess

result = subprocess.run('ls -l | grep python', shell=True)
print(result.returncode)
# returncode为0说明命令正常执行并返回结果
# returncode为1说明没有返回结果
# returncode为127说明命令执行异常
~~~

### 接收参数input

`input`参数用于向子进程提供输入数据，它特别适用于那些需要从标准输入（stdin）接收数据的命令

~~~python
import subprocess

result = subprocess.run(['grep','py'], input='python data',capture_output=True, text=True)
# 相当于echo "python data" | grep 'py'
print(result.stdout)
~~~

### 超时处理timeout

`timeout` 参数用于限制命令的执行时间。如果命令执行的时间超过了设定的超时时间，就会抛出一个 `TimeoutExpired` 异常，防止命令长时间挂起或卡住。

超时处理非常有用，特别是在你需要执行一些可能会卡住或者运行时间不确定的命令时。比如：

- 你正在执行一个远程请求，但这个请求可能因为网络问题而长时间无响应。
- 你在执行某些系统任务，但不希望因为某些原因而无限期地等待执行结果。

~~~python
import subprocess

try:
    result = subprocess.run(['sleep', '5'], timeout=3)
	print(result.stdout)
except subprocess.TimeoutExpired as e: # 在规定了超时时间时，抛出的超时错误将会是subprocess.TimeoutExpired。错误是子进程抛出来的，exception要用子进程的
    print(f"Error: {e}")
~~~

### 捕获错误与返回码check=True

在 Python 的 subprocess 模块中，subprocess.run() 用于执行系统命令。通过指定参数 `check=True`，你可以确保命令在执行时成功完成。

如果命令执行失败（即返回**非零退出状态**），会自动抛出 `CalledProcessError` 异常，而不会继续执行。这样即使命令执行失败，程序也不会崩溃，而是返回报错信息。

~~~python
import subprocess

try:
    result = subprocess.run(['ls', '/pypy'], check=True)
    print(result.stdout)

except subprocess.CalledProcessError as e: # 子进程抛出的错误要用子进程的exception
    print(f"Error: {e}")
~~~

## subprocess.Popen()

`subprocess.Popen()` 是 Python 中用于创建和管理子进程的类。它允许你与子进程进行复杂的交互。通过 stdin、stdout 和 stderr 管道,你可以将数据传递给子进程，读取子进程的输出，以及捕获子进程的错误信息。

### 子进程通信communicate

~~~python
import subprocess

process = subprocess.Popen('cat', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,text=True)

# 通过stdin向子进程发送一个数据
stdout,stderr = process.communicate(input='Hello from python')

print(f"stdout:{stdout}")
print(f"stderr:{stderr}")
~~~

这行代码创建了一个子进程来运行 cat 命令。

- `stdin=subprocess.PIPE` 表示你可以向子进程的标准输入发送数据

- `stdout=subprocess.PIPE` 表示你可以从子进程的标准输出读取数据

- `stderr=subprocess.PIPE` 表示你可以从子进程的标准错误输出读取错误信息，

- `text=True` 表示数据是以文本形式处理的（而不是字节）

- subprocess.Popen()函数会返回一个Popen对象，表示刚刚启动的子进程。

`process.communicate(input="Hello from python")：`

- communicate 方法将数据 "Hello from python" 发送到 cat 命令的`标准输入stdin`，并等待子进程完成。它返回子进程的`标准输出stdout`和`标准错误输出stderr`。

### 捕获stderr

你可以通过 `stderr=subprocess.PIPE` 捕获子进程的错误信息，用`communicate()`方法获取到stderr，便于调试或记录日志。

~~~python
import subprocess

process = subprocess.Popen(['ls','/test'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,text=True )
stdout, stderr = process.communicate()
print(f"stdout:{stdout}")
print(f"stderr:{stderr}")
~~~

### 捕获返回码wait()

`process.wait()` 用于让当前进程（即你的 Python 脚本）等待子进程完成。

当子进程结束时，`wait()` 方法会返回子进程的退出码（exit code）。退出码是一个整数，通常 0 表示子进程成功结束，非零值表示子进程在执行过程中发生了错误。

~~~python
import subprocess

process = subprocess.Popen(['sleep','2'])
exit_code = process.wait()
print(f"Exit code: {exit_code}")
~~~

### 终止子进程terminate/kill

使用 `terminate()` 或 `kill()` 可以终止子进程。

`terminate()`:

- 这个方法会发送一个 `SIGTERM` 信号到子进程。这是一个请求终止的信号，子进程可以选择优雅地处理这个信号，比如清理资源然后退出。
- 这个方法的效果是使子进程接收到一个终止请求，但是否立即终止则取决于子进程的处理逻辑。
- 如果子进程在接收到 SIGTERM 信号后没有及时退出，可能需要使用 kill() 方法。

`kill()`:

- 这个方法会发送一个 `SIGKILL` 信号到子进程。这是一个强制终止的信号，不允许子进程进行任何清理工作。
- SIGKILL 信号会立刻终止子进程，不管子进程是否正在执行某个任务，也不会给子进程任何机会去做清理工作。
- 这种方法通常在 terminate() 无效时使用。

~~~python
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
~~~

## 案例：实时监控磁盘使用情况并识别空间占用最大的目录

- 重点：
  - `splitlines()`按行分割，再`split()`按空格分割，就能把linux命令输出给拆分出来
  - 字典赋值`directory[‘key’]=value`
  - 字典排序`sorted(directory.items(), lambda x:x[1], reverse=True)`，返回的是`[(k1,v1),(k2,v2)]`
  - 遍历字典排序后的元组列表：`for k, v in sorted_directory`

~~~python
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
~~~

# psutil模块

psutil 是一个跨平台库，用于检索系统的硬件信息，如 CPU、内存、磁盘、网络等资源使用情况。它广泛应用于系统监控、性能分析和运维自动化。

安装psutil：

~~~python
pip install psutil
~~~

## 获取所有程序的PID:process_iter()

~~~python
import psutil

# psutil.process_iter()返回一个process对象，遍历系统中所有正在运行的进程。
# ['pid', 'name']参数让其返回每个进程的PID和name。
for proc in psutil.process_iter(['pid', 'name']):
    # proc.info获取到一个字典，字典的kv是process_iter()里面我们规定的参数。类似于{'pid': 2958594, 'name': 'sh'}
    print(f"PID: {proc.info['pid']}, process name: {proc.info['name']}")
~~~

## 监控磁盘分区大小:disk_usage()

~~~python
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
~~~

## 多核CPU使用率cpu_percent()

~~~python
import psutil

def get_cpu_usage():
    cpu_usage = psutil.cpu_percent(interval=1, percpu=True)
    print(f"CPU usage of every core: {cpu_usage}.")
    print(f"Overall CPU usage: {psutil.cpu_percent()}.")

if __name__ == '__main__':
    get_cpu_usage()
~~~

## 获取物理内存和交换分区统计vitrual_mamory()

~~~python
import psutil

def get_memory():
    # 物理内存使用情况
    mem_usage = psutil.virtual_memory()
    # 返回namedtuple：svmem(total=3, available=2, percent=34.2, used=1, free=1, active=1, inactive=3, buffers=5, cached=7, shared=4, slab=1)
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
~~~

## 网络流量监控get_io_counters()

~~~python
import psutil

def get_net_io():
    net_io = psutil.net_io_counters()
    # net_io_counters()返回namedtuple
    # 类似于：snetio(bytes_sent=1, bytes_recv=3, packets_sent=3, packets_recv=4, errin=0, errout=0, dropin=0, dropout=0)
    print(f"Total received byte: {net_io.bytes_recv / (2 ** 20): .2f} MiB.")
    print(f"Total sent byte: {net_io.bytes_sent / (2 ** 20): .2f} MiB.")


if __name__ == '__main__':
    get_net_io()
~~~

## 系统负载getloadavg()

~~~python
import psutil

def get_load():
    # 物理内存使用情况
    load = psutil.getloadavg()
    # 返回元组：(0.5, 0.6, 0.5)，含义是最近1min负载，最近5min负载，最近15min负载
    print(f"System load in 1 min: {load[0]: .2f}.")
    print(f"System load in 5 min: {load[1]: .2f}.")
    print(f"System load in 15 min: {load[2]: .2f}.")

if __name__ == '__main__':
    get_load()
~~~

## 案例：CPU、内存、根分区使用报告

重点：

- `datetime.datetime.now()`获取时间戳
- `psutil.cpu_percent()`获取CPU使用率
- `psutil.virtual_memory().percent`获取内存使用情况
- `shutil.disk_usage(path)`获取到某个文件系统的磁盘占用情况，返回namedtuple，类似于：usage(total=9, used=4, free=4)，可以被三个变量迭代

~~~python
import psutil, shutil, datetime

def get_system_report():
    report = []
    # 打印报告时间
    report.append(f"Report time: {datetime.datetime.now().strftime('%m-%d')}.")
    # 获取CPU memory使用情况
    report.append(f"CPU usage: {psutil.cpu_percent()}%.")
    report.append(f"Memory usage: {psutil.virtual_memory().percent}%.")
    # 获取根分区使用情况统计
    total, used, free = shutil.disk_usage("/")
    # 转换成Gib,保留一位小数
    report.append(f"Disk total: {(total / (2 ** 30)): .1f} Gib.")
    report.append(f"Disk used: {(used / (2 ** 30)): .1f} Gib.")
    report.append(f"Disk rfree: {(free / (2 ** 30)): .1f} Gib.")
	# 列表连成字符串打印
    return ('\n').join(report)

if __name__ == '__main__':
    print(get_system_report())
~~~

# os模块

os 模块是 Python 标准库中用于与操作系统进行交互的模块，主要提供对文件和目录的操作，以及对操作系统环境变量的访问和管理。通过 os 模块，我们可以执行文件系统的常见操作如文件创建、删除、目录操作，以及管理操作系统的环境变量。

## 目录操作

~~~python
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
~~~

## 文件操作

~~~python
import os

file_path = '/home/s0001969/Documents/learning-notes-git/Python/python-manuscripts/old.txt'
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
# os.stat_result(st_mode=3, st_ino=6, st_dev=6, st_nlink=1, st_uid=1, st_gid=1, st_size=1, st_atime=1, st_mtime=1, st_ctime=1)
file_info = os.stat('oop.py')
print(file_info)

# 拼接文件路径。用目录名和文件名做拼接成完成的绝对路径
full_path = os.path.join('/', 'file.txt')
~~~

## 操作环境变量

~~~python
import os

# 列出所有环境变量
# 返回一个namedtuple，元素是一个字典，包含所有环境变量
# environ({'LANGUAGE': 'en_US:en', 'LC_TIME': 'en_US.UTF-8'})
env_vars = os.environ
print(env_vars)

# 查询指定环境变量，若不存在，返回None
result = os.getenv('PATH')
print(f"env PATH is: {result}")

# 设置环境变量，和字典赋值方法一样
os.environ['MY_VAR'] = '123'
print(f"ENV 'MY_VAR' has been set to: {os.getenv('MY_VAR')}")

# 删除环境变量，相当于删除字典的某个键值对
del os.environ['MY_VAR']
print("ENV 'MY_VAR' has been deleted.")
~~~

## 路径处理

~~~python
import os

path = '/home/s0001969/Documents/learning-notes-git/Python/python-manuscripts/'
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
~~~

# logging模块

`logging` 模块是 Python 标准库中的一个模块，用于记录和跟踪程序的运行状态和事件。它提供了灵活的框架来生成和管理日志信息，便于调试和运行监控。

logging 模块使用不同的日志级别来表示日志的重要性，常用的级别有：

- DEBUG：调试信息，通常用于开发过程中获取详细信息。
- INFO：普通信息，表示程序的正常运行状态。
- WARNING：警告信息，表示可能出现问题的情况。
- ERROR：错误信息，表示发生了错误，可能影响程序的某些功能。
- CRITICAL：严重错误信息，表示非常严重的错误，可能导致程序无法继续运行。

logging模块中的三个功能：

- `日志记录器`：记录器是 logging 模块的主要接口，负责记录消息。通过名称来区分不同的记录器。

- `处理器`：处理器将记录的日志消息发送到合适的目的地，比如控制台、文件等。
- `格式化器`：格式化器定义了日志信息的输出格式。

## 基本日志记录器

~~~python
import logging

# 基本 logging 记录器
# 开启DEUBG级别信息，意思是所有等级DEBUG、INFO、WARNING、ERROR、CRITICAL）日志都记录
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s-%(levelname)s-%(message)s',
                    datefmt='%m%d_%H:%M:%S')
# format='%(asctime)s-%(levelname)s-%(message)s': 日志输出的格式字符串，定义了每条日志的显示内容：
# %(asctime)s：日志记录的时间。
# %(levelname)s：日志级别
# %(message)s：日志内容，即你记录的消息。
# datefmt='%m%d_%H:%M:%S': 格式化日期和时间的字符串
# %m%d_%H:%M:%S 会输出成 0925_14:30:00的形式

# 记录日志
logging.debug("This is debug message")
logging.info("This is info message")
logging.warning("This is warning message")
logging.error("This is error message")
logging.critical("This is critical message")
~~~

> 注意python的py文件命名最好不要与module名字重名，否则import module的时候会错误的引用到本文件。
>
> 比如这个脚本文件命名为`logging.py`,在其中`import logging`的时候，就会报错：
>
> ~~~sh
> Original exception was:
> Traceback (most recent call last):
>   File "/home/s0001969/Documents/learning-notes-git/Python/python-manuscripts/logging.py", line 1, in <module>
>     import logging
>   File "/home/s0001969/Documents/learning-notes-git/Python/python-manuscripts/logging.py", line 5, in <module>
>     logging.basicConfig(level=logging.DEBUG,
> AttributeError: partially initialized module 'logging' has no attribute 'basicConfig' (most likely due to a circular import)
> ~~~

## 自定义日志记录器

~~~python
import logging,os

os.chdir('/home/s0001969/Documents/learning-notes-git/Python/python-manuscripts/')

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
# 规定了格式：时间-记录器名称-日志级别：日志信息，时间格式：年月日_时:分:秒
# 年份格式%y是简写年（25），%Y是全称年（2025）
formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s: %(message)s', datefmt='%Y%m%d_%H:%M:%S')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# 将处理器添加到记录器
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# 记录日志
# logging.debug/info...用的是基本日志处理器
# 我们自定义了日志处理器，要用自定义的name: logger.debug/info...
logger.debug("This is a debug message.")
logger.info("This is an info message.")
logger.warning("This is a warning message.")
logger.error("This is an error message.")
logger.critical("This is a critical message.")
~~~

## 案例：日志文件切割

使用 logging 模块的 `RotatingFileHandler 处理器`来实现日志文件的切割。

需要预先导入：`from logging.handlers import RotatingFileHandler`

~~~python
import logging, os
from logging.handlers import RotatingFileHandler

os.chdir('/home/s0001969/Documents/learning-notes-git/Python/python-manuscripts/')

# 创建一个日志记录器
logger = logging.getLogger('rotating_logger')
logger.setLevel(logging.DEBUG)

# 创建日志轮替处理器
# maxBytes=2000: 当文件大小达到2000字节，触发日志轮替
# backupCount = 5 最多保留五个旧的日志文件（my_log.log1 ... my_log.log5）
# encoding = 'utf-8' 文件使用UTF-8编码，避免中文乱码
rotating_handler = RotatingFileHandler('my_log.log', maxBytes=2000,backupCount=5,encoding='utf-8')

# 创建格式化器
formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s: %(message)s', datefmt='%Y%m%d_%H:%M:%S')
# 对处理器应用这个格式
rotating_handler.setFormatter(formatter)

# 将处理器添加到记录器上
logger.addHandler(rotating_handler)

# 记录日志，观察日志轮替的生成文件的结果
for i in range(1000):
    logger.debug(f'This is number {i} message.')
~~~

## 案例：报错信息自动发送到邮箱

使用 `SMTPHandler 处理器` 发送日志信息到电子邮件。

需要预先导入：`from logging.handlers import SMTPHandler`

~~~python
~~~

