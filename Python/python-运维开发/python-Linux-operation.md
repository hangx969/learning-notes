# subprocess模块

`subprocess` 模块是 Python 用来管理和控制系统命令执行的工具，它可以让你从 Python 程序中运行外部的命令行命令，就像你在命令提示符或终端中手动输入命令一样。比如，你可以用它来执行 shell 命令、启动程序，或者处理子进程。

核心概念：

- 子进程：当你使用 subprocess 模块运行命令时，Python 会创建一个新进程，这个进程就是“子进程”。
- 同步与异步：你可以选择等待命令执行完成后再继续运行你的 Python 脚本（同步），或者不等待命令执行完毕直接继续运行（异步）。
- 输入、输出、错误流：通过 subprocess，你可以与子进程进行交互，比如向命令提供输入，读取命令输出的结果，或者捕获错误信息。

常见的函数：

- `subprocess.run()`：这是最常用的函数，可以运行一个命令，并等待它执行完成。你可以获取命令的输出、错误信息等
- `subprocess.Popen()`：这个函数更加灵活，适用于更复杂的场景，比如你需要与子进程进行交互。

# subprocess.run()

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

## 管道与重定向

`shell=True`：如果需要执行一个包含 shell 特性（如管道或重定向）的命令，可以设置shell=True。

~~~python
import subprocess

result = subprocess.run('ls -l | grep python', shell=True)
print(result.returncode)
# returncode为0说明命令正常执行并返回结果
# returncode为1说明没有返回结果
# returncode为127说明命令执行异常
~~~

## input接收参数

`input`参数用于向子进程提供输入数据，它特别适用于那些需要从标准输入（stdin）接收数据的命令

~~~python
import subprocess

result = subprocess.run(['grep','py'], input='python data',capture_output=True, text=True)
# 相当于echo "python data" | grep 'py'
print(result.stdout)
~~~

## timeout超时处理

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

## 捕获错误与返回码

在 Python 的 subprocess 模块中，subprocess.run() 用于执行系统命令。通过指定参数 `check=True`，你可以确保命令在执行时成功完成。

如果命令执行失败（即返回**非零退出状态**），subprocess.run() 会自动抛出 `CalledProcessError` 异常，而不会继续执行。这样即使命令执行失败，程序也不会崩溃，而是返回报错信息。

~~~python
import subprocess

try:
    result = subprocess.run(['ls', '/pypy'], check=True)
    print(result.stdout)

except subprocess.CalledProcessError as e: # 子进程抛出的错误要用子进程的exception
    print(f"Error: {e}")
~~~

# subprocess.Popen()

`subprocess.Popen()` 是 Python 中用于创建和管理子进程的类。它允许你与子进程进行复杂的交互。通过 stdin、stdout 和 stderr 管道,你可以将数据传递给子进程，读取子进程的输出，以及捕获子进程的错误信息。

## 子进程通信

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

## 捕获stderr

你可以通过 `stderr=subprocess.PIPE` 捕获子进程的错误信息，用`communicate()`方法获取到stderr，便于调试或记录日志。

~~~python
import subprocess

process = subprocess.Popen(['ls','/test'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,text=True )
stdout, stderr = process.communicate()
print(f"stdout:{stdout}")
print(f"stderr:{stderr}")
~~~

## 捕获返回码

`process.wait()` 用于让当前进程（即你的 Python 脚本）等待子进程完成。

当子进程结束时，`wait()` 方法会返回子进程的退出码（exit code）。退出码是一个整数，通常 0 表示子进程成功结束，非零值表示子进程在执行过程中发生了错误。

~~~python
import subprocess

process = subprocess.Popen(['sleep','2'])
exit_code = process.wait()
print(f"Exit code: {exit_code}")
~~~

## 终止子进程

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

