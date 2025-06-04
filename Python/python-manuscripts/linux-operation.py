dic = {
    'k1': 100,
    'k2': 50,
    'k3': 200
}
# 常用sorted函数进行排序
# 默认是从小到大排序
sorted_list = sorted(dic.items(), key=lambda x:x[1])
# 加了reverse=True是从大到小
sorted_list = sorted(dic.items(), key=lambda x:x[1], reverse=True)

print(sorted_list)
# sorted会返回一个列表，元素是k-v组成的元组，例如：
# [('k3', 200), ('k1', 100), ('k2', 50)]
# 迭代这个元组：
print("top 2 is:\n")
for k, v in sorted_list[:2]:
    print(f"{k}:{v}")