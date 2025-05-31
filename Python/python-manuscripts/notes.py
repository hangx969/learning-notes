# 整型和字符串占位符
name = 'alice'
age = 12
print("Name is %s, age is %d." % (name, age))

# 输出百分号
percent = 75
print("Percentage is %d%%" % percent)

#输出浮点数的小数点后位数。%10.2f表示输出浮点数占10个字符的宽度，小数点后保留两位。数字不足将用空格填充
print('PI\'s vaule is：%10.2f' % 3.1415926)
# 仅输出小数点后两位数字
print('PI\'s vaule is：%.2f' % 3.1415926)
# 添加左对齐
print('PI\'s vaule is：%-10.2f' % 3.1415926)