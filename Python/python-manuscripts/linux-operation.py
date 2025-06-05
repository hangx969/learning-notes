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