# 面向对象编程

## 概念

在面向对象编程中，任何东西都可以被看作一个“对象”，比如人、汽车、动物、书籍等。每个对象都有属性和方法。举个例子：

- 人可以是一个对象，它有属性（比如姓名、年龄、身高）也有方法（比如吃饭、走路、说话）

- 汽车也是一个对象，它有属性（品牌、型号、颜色）有方法（启动、加速、刹车）。

**对象（Object）：**

可以把对象理解为生活中的某个具体的东西。比如有一辆车，这辆车就是一个对象。在编程里，对象就是一个具体的实例。比如我们可以创建一个“汽车”的对象，它会有特定的属性，比如品牌、颜色，还有可以执行的动作，比如启动、刹车。

**类（Class）：**

类就是制造对象的“模具”或“模板”。就像你有个汽车的设计图，你可以用这个设计图制造很多不同的汽车。编程里的类就是定义了某种事物的属性和行为，比如汽车的品牌、颜色，能做的动作像启动、加速等。每次你用这个类，就像从设计图制造出一个新的汽车。

**属性（Attributes）：**

属性就是对象的特点或信息。比如汽车的品牌是红旗，颜色是白色，这些就是属性。每个对象都会有自己的属性，就像每辆汽车可以有不同的颜色和型号。方法（Methods）：方法就是对象能做的动作或功能。比如汽车能启动、加速、刹车，这些就是方法。在编程里，方法也叫做函数，就是定义在类里的“动作”，让对象可以执行某些任务。

## 示例

~~~python
# 定义一个简单的类
class Car:
    def __init__(self, make, model):
        self.make = make
        self.model = model

    def start_engine(self):
        print(f"{self.make} {self.model} starting")

    def accerlate(self):
        print(f"{self.make} {self.model} acclerating")

car1 = Car('Audi','A4')
car2 = Car('BMW', 'X7')

car1.start_engine()
car2.accerlate()
~~~

# 类和方法

## 修改类的属性

类不仅可以定义属性和方法，还可以在对象创建后动态修改这些属性。

~~~python
class Friend:
    def __init__(self, name, age, hobby):
        self.name = name
        self.age = age
        self.hobby = hobby

    def introduce(self):
        return f"I am {self.name}, {self.age} years old, I like {self.hobby}"


bob = Friend('Bob', 12, "travel")
alice = Friend('Alice', 15, 'movie')

print(bob.introduce())
print(alice.introduce())

bob.age = 13
alice.hobby = 'running'

print(bob.introduce())
print(alice.introduce())
~~~

## 带有参数的方法

类的方法可以接收参数：

~~~python 
class Friend:
    def __init__(self, name, age, hobby):
        self.name = name
        self.age = age
        self.hobby = hobby

    def introduce(self, greeting):
        return f"{greeting}. I am {self.name}, {self.age} years old, I like {self.hobby}"

    
bob = Friend('Bob', 12, "travel")
alice = Friend('Alice', 15, 'movie')

print(bob.introduce('Hi'))
print(alice.introduce('Hello'))
~~~

## 类的继承

类可以通过继承（Inheritance）机制从其他类派生出新的类。继承使得新类（子类）**能够**继承其父类的属性和方法，并可以添加新的功能或覆盖现有的功能。

- 如何标识这个子类的父类是谁？用`class SonClass(FatherClass)`。括号()里写父类的名字。
- 注意子类虽然**能够**继承父类的属性和方法：
  - 但是要完成继承父类属性：需要用`super().__init__(*args, **kargs)`实际继承过来。
  - 继承父类方法，要用`super().func()`来调用父类的方法。

~~~python
class Friend:
    def __init__(self, name, age, hobby):
        self.name = name
        self.age = age
        self.hobby = hobby

    def introduce(self, greeting):
        return f"{greeting}. I am {self.name}, {self.age} years old, I like {self.hobby}"

# 创建子类
class OldFriend(Friend):
    def __init__(self, name, age, hobby, year):
        super().__init__(name, age, hobby) # name age hobby继承父类的属性
        self.year = year # 定义子类特有的属性

    def introduce(self):
        base_info = super().introduce('Hello') # 继承父类的方法并传了个参
        return f"{base_info}, we have known for {self.year} years." # 重写了父类的方法，增加了输出

hugo = OldFriend('Hugo', 28, 'reading', 20)
print(hugo.introduce())
~~~

## 类的特殊方法

每个 Python 类都可以有一些特殊方法，这些方法的名字通常是以双下划线开头和结尾的，比如 `__init__`。这些方法允许我们为类对象定义特殊的行为，让它们的表现更像内置的数据类型。

### 构造函数：\__init__

`__init__(self)` 是类的构造函数，它在创建对象时自动被调用，用来初始化后面创建的每一个对象的属性。你可以把它想象成给对象“赋值”的地方。`self`是指当前这个对象自己。它允许你访问对象的属性和方法。make 和 model 是传入的参数。

### 对象字符串化函数：\__str__

`__str__` 是一个特殊方法，它用于定义对象被打印或转换为字符串时的输出内容。

如果你没有定义 `__str__` 方法，当你试图打印一个类的实例时，Python 会使用默认的字符串表示形式。这个默认的输出通常是对象的类型名和对象在内存中的地址，如：`__main__.Friend object at 0x10a2c1a60`，对用户而言不是很直观。

通过定义 `__str__` 方法，你可以控制当使用 `print` 函数或 `str()` 函数来打印对象时，显示的具体内容。例如：

~~~python
class Friend:
    def __init__(self, name, age, hobby):
        self.name = name
        self.age = age
        self.hobby = hobby

    def __str__(self):
        return (f"name: {self.name}, age: {self.age}, hobby: {self.hobby}") # 定义直接print对象或str()对象的时候，返回特定格式的输出

    def introduce(self, greeting):
        return f"{greeting}. I am {self.name}, {self.age} years old, I like {self.hobby}"

bob = Friend('Bob', 12, 'running')
print(bob)
print(str(bob))
~~~

### 对象比较函数：\__eq__

在 Python 中，所有的对象都可以使用 `==` 运算符进行比较。默认情况下，== 运算符比较的是对象的内存地址，也就是说，它比较的是两个对象是否是同一个对象。

如果你想让两个对象的比较更具意义（例如比较对象的内容），你需要自定义 == 运算符的行为。

~~~python
class Friend:
    def __init__(self, name, age, hobby):
        self.name = name
        self.age = age
        self.hobby = hobby

    def __str__(self) -> str:
        return (f"name: {self.name}, age: {self.age}, hobby: {self.hobby}") # 定义直接print

    def __eq__(self, other: object) -> bool: # 返回值类型提示，不影响代码运行，提高可读性和可维护性
        if isinstance(other, Friend): # 首先判断other是否属于Friend类
            # 自定义比较逻辑: 所有属性全部相同就认为对象相等
            return (self.name == other.name and
                    self.age == other.age and
                    self.hobby == other.hobby)
        else: # other不是Friend类
            return False

    def introduce(self, greeting) -> str:
        return f"{greeting}. I am {self.name}, {self.age} years old, I like {self.hobby}"

bob = Friend('Bob', 12, 'running')
alice = Friend('Alice', 12, 'reading')
bob2 = Friend('Bob', 12, 'running')

print(bob==alice)
print(bob==bob2)
~~~

## 类的访问控制

在 Python 中，类的访问控制主要依靠命名约定，来提示开发者哪些属性和方法不应该被外部代码直接访问或修改。Python 没有像其他语言（如 Java、C++）那样严格的访问控制机制，它通过单下划线（`_`）和双下划线（`__`）来实现一定程度的封装性。

### `_`: 受保护的属性和方法

- 命名方式：属性或方法的名称以单下划线 _ 开头。
- 目的：它是一种提示，告诉其他开发者这些属性和方法是类的内部实现，**不建议直接访问或修改**。
- 实际效果：这种方式**并没有真正阻止外部访问**。你仍然可以从类的外部访问和修改这些属性和方法，但这样做是不推荐的，因为它们被认为是类的内部实现部分，随时可能被修改。

~~~python
# 访问受保护的属性和方法
class Example:
    def __init__(self):
        self._protected_attr = 42

    def _protected_method(self):
        print("This is a protected method.")

obj = Example()
print(obj._protected_attr)
obj._protected_method()
~~~

### `__`: 私有的属性和方法

- 命名方式：属性或方法的名称以双下划线 __ 开头。
- 目的：双下划线的属性和方法被认为是私有的，用于更严格的封装，防止外部代码直接访问。
- 实际效果：Python 通过名称改编（name mangling）机制将以双下划线开头的属性和方法的名称改为 `_类名__属性名` 或 `_类名__方法名`，从而实现一定程度的隐藏，避免外部直接访问它们。

~~~python

 访问私有属性和方法
class Example:
    def __init__(self):
        self.__private_attr = 58

    def __private_method(self):
        print("This is a private method.")

    def public_method(self):
        print(self.__private_attr)
        self.__private_method()

obj = Example()
# print(obj._private_attr) # 不能访问
# obj._private_method() # 不能访问
obj.public_method()
~~~

### 访问器和修改器

在面向对象编程中，对象的属性（即类中的变量）通常是私有的或受保护的，这意味着外部代码不能直接访问或修改它们。这时候就需要通过访问器（getter）和修改器（setter）来控制这些属性的访问和修改。

- 访问器（getter）：这是一个用来“获取”对象属性值的方法。通过访问器，你可以从对象中读取某个属性的值，但不会直接访问该属性本身。
- 修改器（setter）：这是一个用来“设置”对象属性值的方法。通过修改器，你可以更改对象中的属性值，同时可以在设置值之前进行一些检查或处理

**为什么需要使用访问器和修改器？**

1. 数据验证：你可以在修改器中对属性值进行验证，确保设置的值是有效的。例如，年龄不能是负数或超过某个上限值。
2. 封装：访问器和修改器提供了一层抽象，隐藏了对象内部属性的实现细节。这意味着你可以随时修改属性的实现方式，而不必担心影响到使用这个类的外部代码。
3. 控制访问权限：你可以通过只提供访问器而不提供修改器来实现只读属性，或者根据需要提供修改器以允许修改属性。

示例：

~~~python
class User:
    def __init__(self, status):
        self._status = None
        # 没有直接设置属性值，而是通过修改器赋值，目的是为了控制输入的数据是否合法。
        self.set_status(status)

    # 定义访问器，用于访问受保护的属性
    def get_status(self) -> str:
        return self._status

    # 定义修改器，修改受保护的属性，增加输入验证功能
    def set_status(self, status) -> None:
        valid_value = ['active', 'inactive', 'disabled']
        if status in valid_value:
            self._status = status
        else:
            raise ValueError(f"Invalid status. Valid status are {valid_value}.")

user1 = User('active')
user2 = User('disabled')
print(user1.get_status())
print(user2.get_status())

user1.set_status('inactive')
print(user1.get_status())
user2.set_status('completed')
~~~

# 类装饰器

类装饰器是一个函数，它接收一个类作为输入，并返回一个新的类或修改后的类。使用类装饰器，我们可以在不改变原始类代码的情况下，对类的行为进行增强或改变。

示例：日志装饰器。编写一个装饰器，每次创建类的示例时，都会打印出一些日志信息。

~~~python
def log_creation(cls):
    # Warpped的父类是传入的参数cls，写到括号里
    class Warpped(cls):
        # 重写构造函数，打印一行日志
        def __init__(self, *args, **kwargs):
            print(f"Creating object: {args[0]}") # args[0]指传入的第一个参数
            # 确保父类的构造函数初始化。不写这一句就会造成name age的父类参数传递不进去
            super().__init__(*args, **kwargs)
	# 装饰器要返回装饰过的类
    return Warpped

# 使用装饰器log_creation装饰Friend类
@log_creation
class Friend:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def introduction(self):
        print(f"My name is {self.name}, age is {self.age}")

# 创建Friend类的时候，实际上是通过Wrapped类创建的，会添加上日志打印功能
bob = Friend('Bob', 12)
~~~

## 装饰器工厂

- 作用： 装饰器工厂的作用是返回一个装饰器函数。装饰器工厂使我们能够**`在装饰器中使用参数`**，从而创建更具灵活性的装饰器。

- 特点：
  - 装饰器工厂本身不会直接用于装饰类或函数，它返回一个实际的装饰器函数。
  - 装饰器工厂允许我们在装饰器中传递参数，从而改变装饰器的行为。
- 使用场景：当我们需要在装饰器中使用动态参数时，例如根据权限控制装饰器的行为，装饰器工厂非常有用。

~~~python
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
                #执行检查permission的逻辑，假设检查通过，返回true
                return True

        return Wrapped # 返回一个预先内置了[permission参数]和[父类]的类
    return decorator # 返回一个预先内置了传入参数的装饰器


@require_permission('admin')
class Friend:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def introduction(self):
        print(f"My name is {self.name}, age is {self.age}")

bob = Friend('Bob', 12)
print(bob.name)
~~~

