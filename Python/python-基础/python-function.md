# 函数传参

## 位置参数

传递给函数的参数，按照定义的顺序匹配

~~~python
def add(a, b):
    return a+b
add(2, 3)
~~~

## 默认参数

定义函数时提供默认值，调用时不传参就用默认值

~~~python
def func(name='guest'):
    print(f'Hello {name}')
func()
func('Bob')
~~~

## 关键字参数

通过参数名称来传递参数值，这样可以在调用时更清晰地指定参数

~~~python
def func(name, age):
    print(f'name is {name}, age is {age}')
func(age=10, name='Bob')
~~~

## 不定长参数

用于接收可变数量的位置参数或关键字参数。

### *args

`*args`接收任意数量的位置参数，作为一个元组

~~~python
def joinargs(*args):
    # args接收到的参数形成一个元组
    return ' '.join(args)
print(joinargs('hello', 'world'))
~~~

### **kwargs

`**kwargs`会将传递的关键字参数收集成一个字典，可以接收任意数量的参数。

在函数中，`kwargs.items()` 方法返回字典中的键值对，并允许我们遍历每一个键值对。

~~~python
def func(**kargs):
    for k, v in kargs.items():
        print(f"{k}:{v}")
func({name:'alice',age:'10'})
~~~

> - 传参的时候，args要在kargs前面，否则会报错。

# 函数嵌套和作用域

## 嵌套

函数可以在其他函数内部定义，这叫做嵌套函数。内部函数可以访问外部函数的变量，但外部函数不能直接访问内部函数。

~~~python
def outerfunc(x):
    def innerfunc(y):
        return y*2
    return innerfunc(x) + 5
print(outerfunc(3)) # 11
~~~

## 作用域

Python 的变量作用域有局部作用域（Local Scope）和全局作用域（Global Scope）：

- 在函数内部定义的变量默认是局部的，只能在函数内部使用。
- 在所有函数外部定义的变量是全局变量，可以被程序中的任何函数访问和修改。

~~~python
x = 10
def modify_global():
    global x
    x = 20
# 在函数里把x变量转成全局变量了
modify_global(x)
print(x)
~~~

# 高阶函数

## 函数作为参数

高阶函数的一个关键特点是它们可以接受其他函数作为参数。通过将函数作为参数传递，你可以在不同的场景下复用代码，并使代码更具灵活性。

~~~python
def apply_function(func, value):
    return func(value)

def square(x):
    return x*x

result = apply_function(square, 5)
print(result)
~~~

## 返回函数（闭包）

高阶函数的另一个特点是它们可以返回函数。这使得你可以通过`函数嵌套`和`参数绑定`创建“定制化”的函数：

~~~python
def make_multiplier(multiplier):
    def multiplier_func(value):
        return value * multiplier
    return multiplier_func

double = make_multiplier(2) # double是返回的multiplier_func函数，这个函数预先被绑定了2，所以double传入几，结果就是几乘2
triple = make_multiplier(3) # triple是返回的multiplier_func函数，这个函数预先被传了3，所以triple传入几，结果就是几乘3

print(double(5)) # Output: 10
print(triple(5)) # Output: 15
~~~

这种方式也称为`闭包`，闭包的特性是：内部函数可以引用并记住外部函数的变量，即使外部函数已经执行完毕。在这个示例中，每次调用`make_multiplier`都生成了一个新的`multiplier_func`实例，并`multiplier`的参数值绑定到该实例上。

## 闭包使用场景

闭包是一种强大的编程工具，适用于以下场景或情况：

### 1.需要保存函数的上下文状态
闭包可以“记住”外部函数的变量，即使外部函数已经执行完毕。这在需要保存某些状态或上下文信息时非常有用。例如：
- **任务调度器**：根据不同的策略生成特定的任务函数，并在后续调用时执行。示例：

~~~python
def make_command_executor(server_name):
    def command_executor(command):
        # 这里演示假装执行命令，返回结果
        return f"Executing {command} in {server_name}"
    return command_executor

server1_executor = make_command_executor('server1') # 传入了server1，返回了预先绑定server1参数的command_executor函数，后面传参command，相当于调用了command_executor(command)函数
server2_executor = make_command_executor('server2')

# server1 检查磁盘空间
result1 = server1_executor('df -h')
print(result1)

# server2重启服务
result2 = server2_executor('systemctl restart nginx')
print(result2)
~~~

- **计数器**：实现一个计数器函数，每次调用时返回递增的值。示例：

```python
def make_counter():
    count = 0
    def counter():
        nonlocal count # 声明这里的count是外层函数的变量，方便后续修改
        count += 1
        return count
    return counter

counter = make_counter() # 此时已经实例化了一个内部函数counter，count从0开始自增了
print(counter())  # 输出 1
print(counter())  # 输出 2
```

---

### 2.需要动态生成函数
当需要根据不同的输入动态生成具有特定行为的函数时，闭包是一个很好的选择。例如：
- **策略模式**：根据不同的策略生成对应的处理函数。
- **命令生成器**：动态生成带有特定参数的命令执行函数。示例：

```python
def make_multiplier(factor):
    def multiplier(x):
        return x * factor
    return multiplier

double = make_multiplier(2)
triple = make_multiplier(3)
print(double(5))  # 输出 10
print(triple(5))  # 输出 15
```

---

### 3.避免全局变量
闭包可以通过外部函数的局部变量保存状态，从而避免使用全局变量，减少命名冲突和副作用。示例：

```python
def logger(prefix):
    def log(message):
        print(f"{prefix}: {message}")
    return log

info_logger = logger("INFO") # logger被调用时，INFO被传入了内部函数log，即使logger在这里调用结束并退出，返回出来的log函数仍然保留了传进去的INFO参数
error_logger = logger("ERROR")

info_logger("This is an info message.")  # 输出 INFO: This is an info message.
error_logger("This is an error message.")  # 输出 ERROR: This is an error message.
```

---

### 4.**实现装饰器**

闭包是实现装饰器的基础，用于在不修改原函数的情况下扩展其功能。

示例：
```python
def decorator(func):
    def wrapper(*args, **kwargs):
        print("Before function call")
        result = func(*args, **kwargs)
        print("After function call")
        return result
    return wrapper

@decorator 
# 装饰器相当于在原函数执行之前先执行：
# say_hello=decortor(say_hello)
def say_hello():
    print("Hello!")

say_hello()
# 输出：
# Before function call
# Hello!
# After function call
```

~~~python
# 对一个计数程序 增加统计时间功能
import time    
def count_time_wrapper(func):
	def improved_func(*args, **kwargs):
        start_time = time.clock()
        ret = func(*args, **kwargs)
        end_time = time.clock()
        print("takes {} s".format(end_time - start_time))
        return ret
    return improved_func

@count_time_wrapper
def odds(lim):
    for i in range(0,lim,2):
        print(i)

if __name__ == '__main__':
    # 装饰器等价于在函数调用之前执行如下语句： odds = count_time_wrapper(odds)
    odds(100)
~~~



---

### 5.需要延迟执行的逻辑
闭包可以将某些逻辑封装起来，延迟到特定条件满足时再执行。例如：
- **事件处理**：为不同的事件生成对应的处理函数。
- **回调函数**：在异步操作完成后执行特定逻辑。

---

## 闭包的工作机制

闭包的工作机制是通过内部函数对外部函数局部变量的引用实现的。即使外部函数已经执行完毕，内部函数依然可以访问这些变量。

在 Python 中，闭包会将外部函数的局部变量存储在内部函数的 `__closure__` 属性中。例如：

```python
def logger(prefix):
    def log(message):
        print(f"{prefix}: {message}")
    return log

info_logger = logger("INFO") 
print(info_logger.__closure__[0].cell_contents) # 输出 "INFO"
```

这里，`info_logger.__closure__` 存储了闭包中捕获的变量，`cell_contents` 是变量的值。

# 案例实战

## 1.不同服务器自动匹配执行的任务

创建一个高阶函数，根据服务器主机名和不同的命令生成不同的执行器，然后用这些执行器来控制在哪个主机上执行哪个命令。

~~~python
def make_command_executor(server_name):
    def command_executor(command):
        # 这里演示假装执行命令，返回结果
        return f"Executing {command} in {server_name}"
    return command_executor

server1_executor = make_command_executor('server1') # 传入了server1，返回了预先绑定server1参数的command_executor函数，后面传参command，相当于调用了command_executor(command)函数
server2_executor = make_command_executor('server2')

# server1 检查磁盘空间
result1 = server1_executor('df -h')
print(result1)

# server2重启服务
result2 = server2_executor('systemctl restart nginx')
print(result2)
~~~

## 2.自动化任务调度

对不同服务器执行相似的任务，如备份数据库、清理临时文件等。我们可以使用高阶函数来创建动态的任务调度器，根据不同服务器的配置来定制执行任务的策略。

~~~python
def make_task_scheduler(strategy):
    
    def daily_backup():
        print("Performing daily backup")
    
    def weekly_cleanup():
        print("Performing weekly cleanup")
    
    def monthly_report():
        print("Generating monthly report")
    
    if strategy == 'daily':
        return daily_backup
    elif strategy == 'weekly':
        return weekly_cleanup
    elif strategy == 'monthly':
        return monthly_report
    else:
        raise ValueError('Unknown strategy')
    
daily_task = make_task_scheduler(daily)
weekly_task = make_task_scheduler(weekly)
monthly_task = make_task_scheduler(monthly)

daily_task()
weekly_task()
monthly_task()
~~~

## 3.动态配置生成器

~~~python
def make_config_generator(env):
    def dev_config():
        return {
            'db': 'dev_db',
            'host': 'localhost',
            'debug': True
        }

    def prod_config():
        return {
            'db': 'prod_db',
            'host': 'prod.server.com',
            'debug': False
        }

    if env == 'dev':
        return dev_config
    elif env == 'prod':
        return prod_config
    else:
        raise ValueError('Unknown env')

dev_config = make_config_generator('dev')
prod_config = make_config_generator('prod')

print(dev_config())
print(prod_config())
~~~

## 4.自定义告警规则

~~~python
def make_alert_ruler(service_name):
    def cpu_usage_alert(threshold):
        print(f"Alert: {service_name} CPU usage exceeded {threshold}%")
    def mem_usage_alert(threshold):
        print(f"Alert: {service_name} Memory usage exceeded {threshold} MB")

    if service_name == 'web_server':
        return cpu_usage_alert
    elif service_name == 'db_server':
        return mem_usage_alert
    else:
        raise ValueError('Unknown service name')

web_server_alert = make_alert_ruler('web_server')
db_server_alert = make_alert_ruler('db_server')

web_server_alert(80)
db_server_alert(1024)
~~~

## 5.分析nginx日志

### 背景

1. 需求

   设计一个通用的日志解析器，用于解析不同类型服务的日志（如 Nginx 日志和系统 messages 日志）

2. 编写动态解析器生成函数

   编写一个 make_log_parser 函数，该函数可以根据传入的服务名动态返回一个专门用于该服务的解析器。

   这样设计的目的是为了实现代码复用和简化扩展：未来如果你需要添加新的日志类型，只需要在这个函数内扩展即可。

3. 实现具体的解析逻辑

   每种日志格式都需要各自的解析逻辑，因此为 Nginx 和 messages 分别编写解析函数。

4. Nginx 日志解析逻辑

   - 利用字符串的 split()方法将日志行按空格拆分成多个部分。
   - 根据日志中各个字段的顺序提取出对应的IP、日期、请求方法、状态码、返回值大小、用户代理等信息。
   - 注意处理带有括号的字段，如日期中的[]。

5. Messages 日志解析逻辑

   - 使用 split()分割日志行，提取出日期、时间、主机名等信息。
   - 使用正则表达式提取服务名（包括方括号内的进程 ID）
   - 按照服务名: 消息内容的格式分割剩余部分。

6. 日志示例：

   ~~~sh
   nginx_log = '192.168.40.80 - - [30/Aug/2030:11:27:18 +0800] "GET / HTTP/1.1" 200 3429 "-" "curl/7.61.1" "-"'
   messages_log = 'Aug 30 18:08 myhost sshd[1234]: Accepted password for user from 192.168.1.2 port 22 ssh2'
   ~~~

### 代码实现

~~~python
import re

def make_log_praser(service_name):

    def nginx_praser(line):
    # IP、日期、请求方法、状态码、返回值大小、用户代理
        parts = line.split(' ')
        # ['192.168.40.80', '-', '-', '[30/Aug/2030:11:27:18', '+0800]', '"GET', '/', 'HTTP/1.1"', '200', '3429', '"-"', '"curl/7.61.1"', '"-"']

        # 直接用字符串切片获取对应的值
        return {
            'IP': parts[0],
            'date': parts[3][1:] + ' ' + parts[4][:-1],
            'request': ' '.join(parts[5:8]),
            'status': parts[8],
            'size': parts[9],
            'referer': parts[10],
            'user_agent': parts[11][1:-1]
        }


    def messages_praser(line):
        # 日期、时间、主机名、服务信息、日志消息
        #['Aug', '30', '18:08', 'myhost sshd[1234]: Accepted password for user from 192.168.1.2 port 22 ssh2']
        parts = line.split(' ', 3) # 只分割前三个空格，拿出来日期时间

        if len(parts) < 4:
            raise ValueError('Log line is too short to parse')

        date = parts[0] + ' ' + parts[1]
        time = parts[2]

        # 提取主机名部分
        rest = parts[3]
        host_part = re.match(r'(\S+)', rest) # 匹配剩余部分开头的主机名部分
        if host_part:
            hostname = host_part.group(1) # 提取正则表达式中的第一个捕获组
            rest = rest[len(hostname):].lstrip()
            # 从左边开始切片，去掉hostname部分
            # 'sshd[1234]: Accepted password for user from 192.168.1.2 port 22 ssh2'
        else:
            raise ValueError('Log line is malformed')

        # 获取 sshd 部分，去掉[1234]
        service_message_split = rest.split(':', 1) # 剩余部分用冒号分割一次，分割成两部分 ['sshd[1234]', 'Accepted......']
        if len(service_message_split) < 2:
            return ValueError('Log line is malformed')
        service_message = service_message_split[0].strip()
        # 去掉[1234]
        service_message = re.match(r'(\S+)(?:\[\d+\])', service_message)
        if service_message:
            # 匹配到就取出第1个捕获组的值
            service = service_message.group(1)
        else:
            # 没匹配到说明没有[1234]部分，service就是它本身？（有没有可能是没有前面的部分？）
            service = service_message

        # 获取 Accepted password ... 部分
        message = service_message_split[1].strip()

        # 返回字典结果
        return {
            'date': date,
            'time': time,
            'hostname': hostname,
            'service': service,
            'message': message
        }

    if service_name == 'nginx':
        return nginx_praser
    elif service_name == 'messages':
        return messages_praser
    else:
        raise ValueError('Unknown service name')

if __name__=='__main__':
    nginx_log_praser = make_log_praser('nginx')
    messages_log_praser = make_log_praser('messages')

    nginx_log = '192.168.40.80 - - [30/Aug/2030:11:27:18 +0800] "GET / HTTP/1.1" 200 3429 "-" "curl/7.61.1" "-"'
    messages_log = 'Aug 30 18:08 myhost sshd[1234]: Accepted password for user from 192.168.1.2 port 22 ssh2'

    print(nginx_log_praser(nginx_log))
    print(messages_log_praser(messages_log))
~~~

