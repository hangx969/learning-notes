try:
    # 输入被除数
    dividend = int(input("Please input the dividend:"))
    # 输入除数
    divider = int(input("Please input the divider:"))
    # 计算除法结果
    result = dividend / divider

# 输入不是数字
except ValueError:
    print("Error: input is not a number.")

# 除数是0
except ZeroDivisionError:
    print("Error: divider cannot be 0")

# 输入正常，打印结果
else:
    print(f"The result of {dividend}/{divider} is: {result}.")