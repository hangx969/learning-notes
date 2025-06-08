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

## 基本日志记录器logging.basicConfig()

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

## 自定义日志记录器logging.getLogger()

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

## 案例：日志文件切割RotatingFileHandler

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

## 案例：报错信息自动发送到邮箱SMTPHandler

使用 `SMTPHandler 处理器` 发送日志信息到电子邮件。

需要预先导入：`from logging.handlers import SMTPHandler`

~~~python
import logging, os
from logging.handlers import SMTPHandler

os.chdir('/home/s0001969/Documents/learning-notes-git/Python/python-manuscripts/')

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
~~~

# paramiko模块

`Paramiko` 是一个用于实现 SSH 协议的 Python 库，它提供了 SSH、SFTP 客户端和服务器的功能。

使用前先安装paramiko：

~~~sh
pip3 install paramiko
~~~

## ssh连接

本次实验准备了一台本地VMware虚拟机，IP: **172.16.183.81**

~~~python
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
~~~

### AutoAddPolicy

在使用 SSH 协议连接远程服务器时，客户端通常会验证服务器的主机密钥（Host Key）以确保连接的安全性。主机密钥是服务器的唯一标识，用于防止中间人攻击。如果服务器的主机密钥不在客户端的已知主机密钥列表中（通常存储在 `~/.ssh/known_hosts` 中），客户端需要决定如何处理这种情况。

`set_missing_host_key_policy` 是一个方法，用于设置客户端在遇到未知主机密钥时的处理策略。它接受一个策略类（或实例）作为参数，该策略定义了如何处理未知的主机密钥。

`paramiko.AutoAddPolicy` 是 `paramiko` 提供的一个策略类，表示自动接受未知主机的密钥并将其添加到客户端的已知主机密钥列表中。这种策略的特点是：

- **自动接受**：当连接到一个未知主机时，客户端不会拒绝连接或提示警告，而是直接接受主机密钥。
- **添加到已知列表**：接受的主机密钥会被缓存，以便后续连接时进行验证。

这种策略适合开发和测试环境，因为它避免了手动管理主机密钥的麻烦。然而，在生产环境中，这种策略可能存在安全风险，因为它无法防止连接到伪造的服务器。

## sftp操作

~~~python
import paramiko, os

# 创建ssh客户端
ssh = paramiko.SSHClient()
# 设置自动接受host key
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)

# 准备本地文件路径
# 如果是windows上，local_dir可以写成'D:/'
local_dir = '/home/s0001969/Documents/learning-notes-git/Python/python-manuscripts/'
local_file = 'oop.py'
local_path = os.path.join(local_dir,local_file)

# 连接到的远程服务器
hostname = '172.16.183.81'
port = 22
username = 'root'
password = 'root'
# 远程路径必须要具体到文件名才能成功sftp put。
remote_path = '/root/oop.py'

try:
    # 创建本地目录，检查本地文件
    os.makedirs(local_dir, exist_ok=True)
    if not os.path.exists(local_path):
        with open(local_path, 'w') as f:
            f.write("test")
        print(f"File {local_path} has been created.")

    # 创建ssh客户端
    ssh.connect(hostname, port, username, password)
    print(f"Connected to {hostname}.")
    # 创建sftp客户端
    sftp = ssh.open_sftp()
    # sftp上传文件
    sftp.put(local_path, remote_path)
    print(f"File transferred from {local_path} to {remote_path}.")

    # sftp下载文件
    # sftp.get(remote_path, local_path)

except Exception as e:
    print(f"Error occurred: {e}")

finally:
    # paramiko模块需要手动关闭ssh和sftp连接
    sftp.close()
    ssh.close()
    print("Connection has closed.")
~~~

# fabric模块

Fabric和Paramiko都是用于ssh连接的Python库，但是他们之间有区别：

1. 功能定位：
- Paramiko：是一个底层库，提供了 SSH 协议的实现，可以直接用于执行远程命令、文件传输等基本操作。适合需要对 SSH 连接有更大控制的开发者。
- Fabric：建立在 Paramiko 之上，是一个高级库，旨在简化和自动化通过 SSH 进行的任务。Fabric 提供了更易于使用的 API，方便批量执行命令和文件传输，适合需要快速部署和管理服务器的用户。
2. 使用方式：
- Paramiko：需要编写更多的底层代码，例如创建 SSH 客户端、连接、处理文件传输等。
- Fabric：提供了更简单的命令接口，可以用更少的代码来实现相同的功能，同时支持任务组织和多主机操作。
3. 任务管理：
- Fabric：允许你定义可重用的任务，方便进行复杂的自动化工作流。
- paramiko：没有内置的任务管理功能，更多依赖用户自己组织代码。

**安装Fabric：**

~~~sh
pip3 install fabric --resume-retries 5 # 应对网络不好的情况，加入下载失败的重试选项
# 本次安装的版本是fabric-3.2.0
~~~

## 远程运行命令Connection.run()

命令格式：`Connection.run(command, **kwargs)`

理论： `Connection.run()` 方法封装了Paramiko的SSHCliet()用于在远程服务器上执行指定的命令。这是执行非交互式命令的主要方法。可以通过参数控制命令的输出和处理方式。

参数：

- command: 要执行的命令字符串。
- hide: 如果设置为 True，将隐藏命令的标准输出（stdout）和标准错误（stderr）。常用于不需要显示命令执行过程的情况。
- warn: 如果设置为 True，即使命令返回非零退出状态也不会引发异常，适合于非关键操作的检查。
- pty: 如果设置为 True，使用伪终端（PTY）来执行命令，适用于需要模拟终端交互的命令。

案例：获取远程服务器的系统信息

~~~python
# 从Fabric模块中导入connection这个类，就可以用这个类中的方法了
from fabric import Connection

# 实例化一个Connection对象，连接到远程主机
# connect_kwargs是一个字典，用于传递额外的连接参数。
conn = Connection(host='172.16.183.81', user='root', connect_kwargs={'password': 'root'})

# 调用Connection对象的run方法执行命令
# 隐藏命令执行的输出，避免在控制台上打印详细信息，只将结果存储在`result` 对象中
result = conn.run('uname -a', hide=True)
# 通过result.stdout获取命令结果
print(result.stdout.strip())
conn.close()
~~~

## 远程执行sudo命令Connection.sudo()

与Connection.run()方法类似，但支持需要以sudo运行的命令。需要在Connection.sudo(password=‘’)添加password参数，传入执行sudo需要的密码。

~~~python
from fabric import Connection
conn = Connection(host='172.16.183.81', user='root', connect_kwargs={'password': 'root'})
result = conn.sudo('uname -a', password='root', hide=True)
print(result.stdout.strip())
conn.close()
~~~

## 本地文件上传Connection.put()

语法：`Connection.put(local, remote)`

~~~python
from fabric import Connection

# 连接到远程主机
conn = Connection(host='172.16.183.81', user='root', connect_kwargs={'password': 'root'})

local_path = '/home/s0001969/Documents/learning-notes-git/Python/python-manuscripts/oop.py'
remote_path = '/root/oop.py'
try:
    # 上传文件
    conn.put(local_path, remote_path)
except Exception as e:
    print(f"Error occurred: {e}.")
finally:
    conn.close()
~~~

## 下载远程服务器文件Connection.get()

语法：`Connection.put(remote, local)`

~~~python
from fabric import Connection

# 连接到远程主机
conn = Connection(host='172.16.183.81', user='root', connect_kwargs={'password': 'root'})

local_path = '/home/s0001969/Documents/learning-notes-git/Python/python-manuscripts/test.py'
remote_path = '/root/test.py'

try:
    # 下载文件
    conn.get(remote_path, local_path)
except Exception as e:
    print(f"Error occurred: {e}.")
finally:
    conn.close()
~~~

## 自动关闭连接

之前的conn.run()跑完命令之后都需要手动关闭一下ssh连接`conn.close()`，这样做是为了释放资源。如果不关闭连接，ssh会话会保持到超时自动关闭，未释放的连接可能会占用系统资源。(注：`conn.open()`方法用于手动打开一个连接，但是一般不需要写，因为Connection会自动打开)

为自动关闭ssh连接，可以使用上下文管理器with，with会把Connection对象作为上下文管理器，在代码执行完毕后会自动关闭，无需显式调用conn.close()

~~~python
from fabric import Connection

# 连接到远程主机
with Connection(host='172.16.183.81', user='root', connect_kwargs={'password': 'root'}) as conn:
    result = conn.run('uname -a')
    print(result.stdout)
~~~

## 判断远程路径是否存在

核心是在远程机器上用shell命令判断路径是否存在：

~~~sh
test -e /root/oop.py && echo "exists" || echo "Not exists"
~~~

~~~python
from fabric import Connection

# 连接到远程主机
with Connection(host='172.16.183.81', user='root', connect_kwargs={'password': 'root'}) as conn:
    result = conn.run('test -e /root/oop.py && echo "exists" || echo "Not exists"', hide=True)
    print(result.stdout)
~~~

## 切换远程目录Connection.cd()

~~~python
from fabric import Connection

conn = Connection(host='172.16.183.81', user='root', connect_kwargs={'password': 'root'})
# 连接到远程主机，并指定工作目录，后面的操作都在这个目录中进行
# 退出with上下文之后会回到当前登录用户的家目录
with conn.cd('/root/'):
    result = conn.run('ls', hide=True)
    print(result.stdout)
conn.close()
~~~

# json模块

JSON 是一种轻量级数据交换格式，既易于人类阅读和编写，又便于计算机解析和生成。它在 Web 开发、API 通信和配置文件中应用广泛。

json 模块是 Python 内置的强大工具，用于在 Python 和 JSON（JavaScript Object Notation）格式之间进行高效的数据转换。Python的 json 模块提供了几种核心方法，帮助开发者实现 Python 数据结构与 JSON 格式之间的灵活转换。

序列化：将python中的数据结构转换成可存储或者传输的格式（如json格式）

核心方法：

- `json.dump()`:将python对象(比如字典、列表等)转换成json格式，并写入文件
- `json.dumps()`：将pyhton对象转换成json格式，并返回json字符串
- `json.load()`：从文件读取json数据，转换为python对象
- `json.loads()`：将json字符串转换为python对象

## 序列化到文件json.dump()

### 语法参数

`json.dump(obj, fp, *, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=None, separators=None, default=None, sort_keys=False)`

- obj:需要序列化的python对象

- fp：文件对象，表示将json写入此文件中

- skipkeys：如果为Ture，字典中不可序列化的键将被跳过。默认为False，遇到无法序列化的键会报错。

- ensure_ascii：决定非ASCII字符（比如中文、特殊符号等）怎么处理。默认是True，表示所有非ASCII字符会被转义为`\uxxx`的Unicode编码，确保json输出便于跨平台夸系统处理和传输。

  ~~~python
  # 用Unicode编码
  import json
  data = {'name': '张三'}
  json_str = json.dumps(data, ensure_ascii=True)
  print(json_str) # {"name": "\u5f20\u4e09"}
  
  # 用原始编码
  import json
  data = {'name': '张三'}
  json_str = json.dumps(data, ensure_ascii=False)
  print(json_str) # {"name": "张三"}
  ~~~

- check_circular: 默认为True，即检测对象中的循环引用，如果检测到，抛出异常并停止序列化，避免无限递归。

  ~~~python
  import json
  
  a = {}
  a['self'] = a  # 循环引用
  
  try:
      json_str = json.dumps(a)  # 默认会检查循环引用
  except ValueError as e:
      print(f"Error: {e}")  # 输出 "Error: Circular reference detected"
  ~~~

- allow_nan: 允许将特殊的浮点数，如`NaN (Not a Number), Infinity (正无穷大), -Inifity(负无穷大)`进行序列化为合法的json字符串。这些值在python中是有效的，但是由于这些值不符合json标准，序列化的时候会转变为字符串`null`。

- cls: 指定一个自定义的json编码器类，示例：

  ~~~python
  import json
  
  class CustomEncoder(json.JSONEncoder):
      def default(self, obj):
          if isinstance(obj, set):
              return list(obj)
          return super().default(obj)
  
  json_str = json.dumps({"set": {1, 2, 3}}, cls=CustomEncoder)
  print(json_str)  # 输出：{"set": [1, 2, 3]}
  ~~~

- indent：控制输出的缩进格式，为None时紧凑输出，为整数时指定缩进空格数。

- separators：用于指定键值对之间的分隔符，默认(',', ': ')

- default：自定义处理无法序列化的对象，比如类示例、日期、特殊类型等，可能不符合json标准格式，无法直接序列化。通过指定一个default函数，告诉json如何处理。

- sort_keys: 如果为 True，则字典的键会按字母顺序排序。在默认情况下，字典键的顺序是保持原来的顺序，不会进行排序。

### 示例

~~~python
import json

data = {
    'name': 'Alice',
    'age': 12,
    'city': 'Beijing',
    'skills': ['python','java','k8s']
}

with open ('python-manuscripts/data.json', 'w', encoding='utf-8') as f:
    # 把字典写入文件，缩进4个字符更具有可读性
    # 非 ASCII 字符会以原始 Unicode 字符的形式输出，这样在阅读时更直观，也便于处理和显示
    json.dump(data, f, indent=4, ensure_ascii=False)
~~~

## 序列化到字符串json.dumps()

### 语法参数

`json.dumps(obj, *, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=None, separators=None, default=None, sort_keys=False)`

与 json.dump() 参数一致，区别在于 json.dumps() 返回一个字符串，而不是写入文件。

### 示例

~~~python
import json

data = {
    'name': 'Alice',
    'age': 12,
    'city': 'Beijing',
    'skills': ['python','java','k8s']
}
# 转成字符串
json_str = json.dumps(data, indent=4, ensure_ascii=False)
print(json_str)
~~~

## 反序列化到文件json.load()

### 语法参数

`json.load(fp, *, cls=None, object_hook=None, parse_float=None, parse_int=None, parse_constant=None, object_pairs_hook=None)`

- fp: 包含 JSON 数据的文件对象。
- cls: 自定义解码类，默认为 None。
- object_hook: 解码 JSON 对象时调用的函数，常用于自定义解码逻辑。
- parse_float: 自定义解析 JSON 中浮点数的函数。
- parse_int: 自定义解析 JSON 中整数的函数。
- parse_constant: 自定义解析特殊值 NaN、Infinity 和 -Infinity 的函数。
- object_pairs_hook: 当处理 JSON 对象键值对时调用的函数。

### 示例

~~~python
import json

with open('python-manuscripts/data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    print(data)
    # 返回了一个字典： {'name': 'Alice', 'age': 12, 'city': 'Beijing', 'skills': ['python', 'java', 'k8s']}
~~~

## 反序列化到字符串json.loads()

### 语法参数

`json.loads(s, *, cls=None, object_hook=None, parse_float=None, parse_int=None, parse_constant=None, object_pairs_hook=None)`

与 json.load() 类似，但 json.loads() 接收的是 JSON 字符串，而不是文件。

### 示例

~~~python
import json

# 定义json格式字符串，用"""引起来
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
# 返回了一个字典： {'name': 'Alice', 'age': 12, 'city': 'Beijing', 'skills': ['python', 'java', 'k8s']}
~~~

## 案例：配置文件管理

~~~python
import json

# 有一个json配置文件，需要修改其中的字段：
# 1. 读取json文件
# 2. 反序列化成python对象
# 3. 修改字段
# 4. 序列化到文件中

# 读取json文件并反序列化成字典
with open('python-manuscripts/config.json', 'r') as f:
    config = json.load(f)

# 字典赋值的方法来修改字段
config['version'] = '1.0.1'
config['logging']['level'] = 'DEBUG'
config['notifications']['email']['username'] = 'test_user'

# 序列化到json文件
with open('python-manuscripts/config.json', 'w') as f:
    json.dump(config, f, indent=4)
~~~

## 案例：服务器状态监控

~~~python
import json, psutil, time
from datetime import datetime

# 使用python收集服务器状态，序列化到json文件

# 用列表来存放字典
status_data = []

# 连续收集五次数据
for _ in range(5):
    # 用字典来格式化收集的数据
    status ={
        'timestamp': datetime.now().strftime('%m-%d %H:%M:%S'),
        'cpu_usage': psutil.cpu_percent(),
        'mem_usage': psutil.virtual_memory()
    }
	# 把每一秒生成的数据（字典）添加到列表中
    status_data.append(status)
    time.sleep(1)

# 把列表序列化到json文件
with open('python-manuscripts/status.json', 'w') as f:
    json.dump(status_data, f, indent=4)
~~~

## 案例：用户权限管理

~~~python
import json

# 用一个json文件存放用户权限信息，使用python读取和更新权限信息

with open('python-manuscripts/permissions.json', 'r') as f:
    # 把json反序列化成一个字典
    user_info = json.load(f)

# 修改字段
user_info['user123']['access_level'] = 'admin'
user_info['user789']['active'] = True

# 序列化回文件中
with open('python-manuscripts/permissions.json', 'w') as f:
    json.dump(user_info, f, indent=4)
~~~

