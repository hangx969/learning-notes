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

