# 结构体

结构体是由一系列具有相同类型或不同类型的数据构成的数据集合。

结构体表示一项记录，比如保存图书馆的书籍记录，每本书有以下属性：

- Title：标题
- Author： 作者
- Subject：学科
- ID：书籍ID

结构体成员是由一系列的成员变量构成，这些成员变量也被称为“字段”。字段有以下特性： 

1. 字段拥有自己的类型和值。
2. 字段名必须唯一。
3. 字段的类型也可以是结构体，甚至是字段所在结构体的类型。

Golang 没有类(class)，Go 语言的结构体(struct)和其它编程语言的类(class)有同等的地位，你可以理解Golang 是基于 struct 来实现OOP（向对象编程）特性的。

## 结构体定义

~~~go
package main

import "fmt"

func main() {
    type Cat struct{
        Name string
        Age int
        Color string
    }

    cat1 := Cat{}
    cat1.Name = "Bob"
    cat1.Age = 1
    cat1.Color = "White"

    fmt.Printf("cat1 Name is %v, age is %v, color is %v", cat1.Name, cat1.Age, cat1.Color)
}
~~~

如果结构体的字段类型是: slice，和map的默认零值都是 nil ，即还没有分配空间。如果需要使用这样的字段，需要先make，才能使用：

~~~go
package main

import "fmt"

func main() {
    type Cat struct{
        Name string
        slc []string
        mp map[string]string
    }

    cat1 := Cat{}
    cat1.Name = "Bob"
    
    cat1.slc = make([]string, 0, 10) // 初始化一个空切片
    cat1.slc = append(cat1.slc, "test") // 添加一个元素
    
    cat1.mp = make(map[string]string, 10) // 初始化一个map
    cat1.mp["a"] = "yes" // 添加一个元素

    fmt.Printf("cat1 name is %v, cat1 slc is %v, cat1 mp is %v", cat1.Name, cat1.slc, cat1.mp)
}
~~~

## 结构体变量声明

~~~go
// 第一种方式：直接声明
var person Person

// 第二种方式：{}
var person Person = Person{}
// 短变量声明 person := Person{}

// 第三种方式：new
var person *Person = new (Person)

// 第四种方式
var person *Person = &Person{}
// 短变量声明 person := &Person{}
~~~

备注:

1. 第3种和第4种方式返回的是结构体指针。
2. 结构体指针访问字段的标准方式应该是：(结构体指针).字段名 ，比如 (person).Name = "jack"。但 go 做了一个简化，也支持结构体指针.字段名，比如 person.Name = "jack"。更加符合程序员使用的习惯，go 编译器底层 对 person.Name 做了转化(*person).Name。
3. 如果需要使用指针，推荐person := &Person{}这样的写法；如果不需要指针，推荐person := Person{}的写法

## 结构体方法

~~~go
package main

import "fmt"

type Calculator struct {
	Sku string
}

func (cal Calculator) get_sku() {
	fmt.Println("Sku of the cal is:", cal.Sku)
}

func (cal Calculator) get_sum(m int, n int) int {
    return m + n
}

func main() {
    cal1 := Calculator{Sku: "Cascio"} //声明结构体实例的时候，同时设置属性值
    // cal1 := &Calculator{Sku: "Cascio"}
    cal1.get_sku()
    res := cal1.get_sum(1, 2)
    fmt.Println("result is:", res)
}

~~~

(cal Calculator) 是 Go 方法的“接收者”（receiver），表示这两个函数是 Calculator 结构体的方法。含义和作用如下：

- (cal Calculator) 表示该方法属于 Calculator 类型，只有 Calculator 类型的变量才能调用这个方法。

- cal 是接收者的名字，可以在方法体内用 cal 访问结构体的字段和方法，相当于 this 或 self。

# 工厂模式

## 工厂函数

Go 中的工厂模式（Factory Pattern）是一种常用的设计模式，用于封装对象的创建过程。它通过一个工厂函数（通常以 NewXXX 命名）来创建并返回结构体实例，而不是直接在外部用结构体字面量初始化。

工厂模式的优点：

可以隐藏结构体的创建细节（如初始化默认值、做参数校验等）便于后续扩展和维护。

示例（以上面的 Calculator 为例）：

~~~go
package main

import "fmt"

type Calculator struct {
	Sku string
}

func (cal Calculator) get_sku() {
	fmt.Println("Sku of the cal is:", cal.Sku)
}

func (cal Calculator) get_sum(m int, n int) int {
    return m + n
}

func NewCalculator(sku string) *Calculator {
    return &Calculator{Sku: sku}
}

func main() {
    cal1 := NewCalculator("Cascio")
    cal1.get_sku()
    res := cal1.get_sum(1, 2)
    fmt.Println("result is:", res)
}
~~~

这样，外部只需调用 NewCalculator，无需关心结构体的具体初始化细节。这就是 Go 中的工厂模式。

## 跨包声明结构体

### 结构体名字大写

goproject/factory/model/model.go 里面定义了这样一个结构体：

~~~go
package model

type Student struct {
    Name  string
    Score float64
}
~~~

如果想在goproject/factory/main/main.go里面创建Student实例：

~~~go
package main

import(
	"fmt"
	"goproject/factory/model"
)

func main() {
	stu := model.Student{ //可以直接跨包引用结构体，因为源结构体是大写的Student，能跨包
		Name: "Bob",
		Score: 99,
	}
	fmt.Println(stu)
}
~~~

### 结构体名字小写

goproject/factory/model/model.go 里面定义了这样一个结构体。如果想在goproject/factory/main/main.go里面创建student实例，得用工厂函数实现。

goproject/factory/model/model.go：

~~~go
package model

type student struct {
	Name  string
	Score float64
}

func NewStudent(name string, score float64) *student {
	return &student{
		Name: name,
		Score: score,
	}
}
~~~

goproject/factory/main/main.go：

~~~go
package main

import(
	"fmt"
	"goproject/factory/model"
)

func main() {
	stu := model.NewStudent("Bob", 99)
	fmt.Println(stu)
	fmt.Println(*stu)
	fmt.Printf("stu name is %v, score is %v", stu.Name, stu.Score)
}
~~~

### 结构体属性也是小写

goproject/factory/model/model.go 里面定义了这样一个结构体。如果想在goproject/factory/main/main.go里面创建student实例，并且访问到里面的小写属性值，可以定义获取值的函数。

goproject/factory/model/model.go

~~~go
package model

type student struct {
	Name  string
	score float64
}

func NewStudent(name string, score float64) *student {
	return &student{
		Name: name,
		score: score,
	}
}

func (stu student) GetScore() float64{
	return stu.score
}
~~~

goproject/factory/main/main.go：

~~~go
package main

import (
	"fmt"
	"goproject/factory/model"
)

func main() {
	stu := model.NewStudent("Bob", 99) //虽然score小写了，但是可以用工厂函数初始化。
	fmt.Println(stu)
	fmt.Println(*stu)
    //fmt.Printf("stu name is %v, score is %v", stu.Name, stu.score) //这样访问score就报错不能跨包访问了
	fmt.Printf("stu name is %v, score is %v", stu.Name, stu.GetScore())
}
~~~

# 面向对象三大特性

Golang 仍然有面向对象编程的继承，封装和多态的特性，只是实现的方式和其它OOP语言不一样。

## 封装

封装(encapsulation)就是把抽象出的字段和对字段的操作封装在一起，数据被保护在内部，程序的其它包只有通过被授权的操作(方法)，才能对字段进行操作。

1. 隐藏实现细节
2. 可以对数据进行验证，保证安全合理(Age)

封装的实现步骤：

1. 将结构体、字段(属性)的首字母小写(不能导出，其它包不能使用，类似 private)

2. 给结构体所在包提供一个工厂模式的函数，首字母大写。类似一个构造函数

3. 提供一个首字母大写的 Set 方法 (类似其它语言的 public)，用于对属性判断并赋值

   - SetXxx 通常用指针接收者，以便修改原对象；若需要失败原因，可返回 error。

     ~~~go
     //示例
     func (stu *student) SetScore(score float64) error {
         if score < 0 || score > 100 {
             return fmt.Errorf("invalid score %v", score)
         }
         stu.score = score
         return nil
     }
     // 因为接收者是 *student，内部对 stu.score 的修改会反映到原始对象；如果改用 student（值接收者），修改只作用在拷贝上，调用者看不到变化。
     ~~~

4. 提供一个首字母大写的 Get 方法(类似其它语言的 public)，用于获取属性的值

   - Getter 一般用值接收者，且如果返回的是导出字段，可直接暴露字段而不是写方法。

     ~~~go
     //示例
     func (stu student) GetScore() float64 {
         return stu.score
     }
     //值接收者就是接收者不带 *，方法获得的是对象的一个拷贝。Getter 通常只读字段，不需要修改原对象，所以值接收者更简洁
     ~~~

5. 如果字段需要封装（私有化），应以小写开头并通过 SetXxx 校验赋值、GetXxx 暴露读取；若字段不需要校验，直接导出（大写开头）即可，Go 项目里往往不写显式 Getter。

示例：

goproject/factory/model/model.go：

~~~go
package model

import "fmt"

// 演示封装，创建一个Person，里面不能随意查看age和salary，并对输入的age进行验证
type person struct {
	Name string
	age  int
	sal  float64
}

//工厂函数，相当于构造函数。只初始化Name一个public参数
func NewPerson(name string) *person {
	return &person{
		Name: name,
	}
}

//为了访问age和sal，编写SetXxx和GetXxx
// SetXxx用指针接收者
func (p *person) SetAge(age int) {
	if age > 0 && age < 150 {
		p.age = age
	} else {
		fmt.Println("Please set a valid age")
	}
}

func (p *person) SetSal(sal float64) {
	if sal > 3000 && sal < 50000 {
		p.sal = sal
	} else {
		fmt.Println("Please set a valid salary")
	}
}

// GetXxx用值接收者
func (p person) GetAge() int {
	return p.age
}

func (p person) GetSal() float64 {
	return p.sal
}

~~~

goproject/factory/main/main.go：

~~~go
package main

import (
	"fmt"
	"goproject/factory/model"
)

func main() {
	bob := model.NewPerson("Bob")
	bob.SetAge(28)
	bob.SetSal(10000)
	fmt.Printf("Bob name is %v, age is %v, sal is %v", bob.Name, bob.GetAge(), bob.GetSal())
}
~~~

## 继承



## 多态

# 接口

# 类型断言