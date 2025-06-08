# 异常

异常是程序在运行过程中发生的错误。当 Python 遇到错误时，会生成一个异常对象。如果这个异常没有被处理，程序会终止并输出一个错误信息。

常见的异常类型，如 `ZeroDivisionError、ValueError、TypeError`等。

~~~python
a = 6
b = 0
result = a/b
print(result)
# ZeroDivisionError: division by zero
~~~

# 异常处理

异常处理的核心目的是即使遇到异常，程序也不会崩溃，而是返回报错信息。

## try-except

- try 块： try 块包含可能会引发异常的代码。你把容易出错的代码放在try里。如果 try 块中的代码运行时发生错误，程序会停止执行 try 块剩余部分，并跳转到相应的 except 块来处理这个错误。

- except 块：处理异常的代码。当 try 块中的代码发生指定类型的异常时，程序会进入 except 块，并执行其中的代码。通过 except 块，你可以处理各种不同的错误类型，并采取相应的行动，而不会让整个程序崩溃。

### 捕获单个异常

~~~python
a = 6
b = 0

try:
    result = a/b # ZeroDivisionError: division by zero
except ZeroDivisionError:
    print(f"Error: Denominator cannot be 0")
~~~

### 捕获多个异常

~~~python
try:
    num = int(input('Input a number:')) # 注意：用户输入一个整数必须用int(input())把输入的str转成int
    result = 10/num
    print(result)

except ValueError:
    print("Input should be int")

except ZeroDivisionError:
    print("Denominator cannot be 0")
~~~

### 捕获特定异常

~~~python
try:
    num = int(input('Input a number:'))
    result = 10/num
    print(result)

except (ValueError, ZeroDivisionError) as e:
    print(f"Error Occurred: {e}")
~~~

### 捕获所有异常

~~~python
try:
    num = int(input('Input a number:'))
    result = 10/num
    print(result)

except Exception as e: # 当你不知道会出现什么异常时，直接用Exception代表所有异常
    print(f"An unexpected error occurred: {e}")
~~~





## try-except-else

else 块中的代码只有在 try 块中没有发生异常时才会执行。

~~~python
try:
    num = int(input('Input a number:'))
    result = 10/num

except ValueError:
    print("Input should be int")

except ZeroDivisionError:
    print("Denominator cannot be 0")

else:
    print(f"the result is {result}")
~~~

## try-except-finally

finally 块无论是否发生异常，都会执行，通常用于释放资源等清理工作

~~~python
try:
    num = int(input('Input a number:'))
    result = 10/num

except ValueError:
    print("Input should be int")

except ZeroDivisionError:
    print("Denominator cannot be 0")

finally:
    print(f"This block will always run, wt./wo. exception")
~~~

# 自定义异常类

在 Python 中，标准库提供了一些内建的异常类，例如 `ValueError` 和 `TypeError`，但有时我们需要为特定的应用程序逻辑定义自己的异常类型。自定义异常类可以帮助你更好地处理程序中特定的错误情况，提高代码的可读性和维护性。

1. 创建自定义异常类：
  - 自定义异常类通常继承自python内建的 `Exception` 类或其子类。
  - 可以添加自定义的初始化方法（`__init__`），并在初始化方法中定义异常的描述信息。
2. 使用自定义异常：
  - 在程序中，通过 `raise` 语句抛出自定义异常。
  - 使用 `try...except` 语句捕获自定义异常，并处理错误情况。

~~~python
class CustomError(Exception):
    def __init__(self,message): # 这里接收一个自定义的变量message
        super().__init__(message) #调用父类(Exception)的初始化方法，确保异常的基本功能都继承过来
        self.message = message # 初始化一下自定义变量message

try:
    raise CustomError("This is a custom error") # 这里就会实例化一个CustomError类，用This...作为自定义变量

except CustomError as e: # 这里的e是一个对象
    print(f'Caught a custom error: {e.message}') # 这里需要获取到e这个对象的message属性
~~~

# 常见场景

## 文件异常处理

文件常见错误：`FileNotFoundError、PermissionError`

~~~python
try:
    with open('data.txt', 'r') as f:
        content = f.read()
        print(content)
except FileNotFoundError:
    print("Error: this file does not exist")
except PermissionError:
    print("Error: permission denied")
~~~

## 用户输入异常处理

~~~python
try:
    num = int(input("Input a number:"))
    result = 10 / num
except ValueError:
    print("Error: Invalid input, please enter a number")
except ZeroDivisionError:
    print("Error: denominator cannot be 0")
else:
    print(f"result is {result}")
finally:
    print("Execution completed")
~~~

## 网络请求异常处理

网络请求可能会遇到网络超时或者请求错误的问题

安装网络模块`pip install requests`，requests是一个用于发送HTTP请求的三方库。

~~~python
import requests

try:
    response = requests.get("http://api.test.com/data", timeout=5)
    response.raise_for_status() #检查响应的状态码。如果状态码表示请求失败（例如404、500 等），将引发HTTPError 异常。200不会触发异常
    data = response.json() # 将响应内容解析为 JSON 格式的数据
    print(data)

except requests.exceptions.HTTPError as e: # 捕获HTTPError 异常，处理 HTTP 错误（如404、500）。
    print(f"HTTP error occurred: {e}")

except requests.exceptions.RequestException as e: # 请求超时、连接错误等异常
    print(f"Error occurred: {e}")

~~~

