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