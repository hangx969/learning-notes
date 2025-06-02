def require_permission(permission): # 装饰器工厂，可以接受参数。即需要检查的权限

    def decorator(cls): # 装饰器函数
        class Wrapped(cls): # 定义子类，继承父类cls,即被修饰的类
            def __init__(self, *args, **kwargs):
                # 装饰的核心就是在这里加上额外的逻辑。在这里是判断是否有权限
                if not self.has_permission(permission):
                    raise ValueError(f"Require {permission}")
                # 必须调用父类的构造函数以确保父类被正常初始化
                super().__init__(*args, **kwargs)

            def has_permission(self, permission) -> bool:
                #执行检查permission的逻辑。这里简单假设检查通过，返回true
                return True

        return Wrapped # 返回一个预先绑定了[permission参数]和[父类]的类
    return decorator # 返回一个预先绑定了传入参数[permission]的装饰器函数


@require_permission('admin')
class Friend:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def introduction(self):
        print(f"My name is {self.name}, age is {self.age}")

bob = Friend('Bob', 12)
print(bob.name)