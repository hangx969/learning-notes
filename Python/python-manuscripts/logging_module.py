import logging,os

os.chdir('/home/s0001969/Documents/learning-notes-git/Python/python-manuscripts/')

# 创建记录器
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)

# 创建控制台处理器,意思是将收集到的日志通过控制台输出
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)

# 创建文件处理器,意思是将收集到的日志写入到文件中
file_handler = logging.FileHandler('my_log.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

# 创建格式化器，应用到控制台处理器和文件处理器
formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s: %(message)s', datefmt='%m%d_%H:%M:%S')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# 将处理器添加到记录器
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# 记录日志
# logging.debug/info用的是基本日志处理器
# 我们自定义了日志处理器，要用自定义的logger.debug/info...
logger.debug("This is a debug message.")
logger.info("This is an info message.")
logger.warning("This is a warning message.")
logger.error("This is an error message.")
logger.critical("This is a critical message.")