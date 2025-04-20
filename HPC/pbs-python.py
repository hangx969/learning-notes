import os
import shutil

def create_and_copy_directory():
    # 获取用户的家目录路径
    home_dir = os.path.expanduser('~')
    # 创建新目录的完整路径
    new_dir = os.path.join(home_dir, 'hangxu-test')

    # 创建目录
    os.makedirs(new_dir, exist_ok=True)

    # 在新目录下创建文件
    file_path = os.path.join(new_dir, 'test.txt')
    with open(file_path, 'w') as file:
        file.write("Hello, this is a test file.\n")

    # 目标路径
    target_dir = '/fz1a/vccz/output/bus_decode/bus_decode_1.0.0/victor_agg2681/'

    # 确保目标目录存在，如果不存在则创建（可选）
    #if not os.path.exists(target_dir):
        #os.makedirs(target_dir, exist_ok=True)

    # 复制目录
    shutil.copytree(new_dir, os.path.join(target_dir, 'hangxu-test'), dirs_exist_ok=True)

    #print("Directory and file created and copied successfully.")

# 调用函数
create_and_copy_directory()
