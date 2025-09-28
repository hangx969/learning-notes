# 变量声明

## 声明变量，单独赋值

~~~go
package main
import "fmt"

func main(){
	var i int
	i = 861
	fmt.Println("i=", i)
}
~~~

## 声明变量但不赋值，使用默认值

~~~go
package main
import "fmt"

func main(){
	var i int
	fmt.Println("i=",i)
}
// i=0 是默认值
~~~

## 声明变量同时赋值

~~~go
package main
import "fmt"

func main(){
	var number int = 6
	fmt.Println("number=",number)
}
~~~

## 类型推导

有时候我们会将变量的类型省略，这个时候编译器会根据等号右边的值来推导变量的类型完成初始化。

~~~go
package main
import "fmt"

func main() {
	var number = 6
	fmt.Printf("number type is %T\n", number)
	fmt.Println("number=", number)
}
~~~

## 短变量声明

在函数内部，可以使用更简略的 := 方式声明并初始化变量。

~~~go
package main
import "fmt"

func main() {
	n := 6
	m := 8
	fmt.Println(m, n)
}
~~~

## 一次声明多个变量

~~~go
package main
import "fmt"

func main() {
	var (
		m = 5
		n = 6
		name = "string"
	)
	fmt.Println("m=", m, "n=", n, "name=", name)
}
~~~

## 匿名变量

在使用多重赋值时，如果想要忽略某个值，可以使用匿名变量（anonymous variable）。匿名变量用一个下划线_表示。

~~~go
package main
import "fmt"

func foo()(int, string){
	return 68, "test"
}

func main() {
	x, _ := foo() // 只想给x赋返回值68，另一个值忽略，不用起名字
	_, y := foo() // 只想给y赋返回值test，另一个值忽略
	fmt.Println("x=", x, "y=", y)
}
~~~

# 常量声明

相对于变量，常量是恒定不变的值，多用于定义程序运行期间不会改变的那些值。如写web程序时返回的状态码定义成常量。常量的声明和变量声明非常类似，只是把var换成了const，常量在定义的时候必须赋值。

常量的定义格式：

~~~go
const identifier [type] = value
~~~

示例：

~~~go
package main
import "fmt"

const status = 200

func main() {
	fmt.Printf("Type of status is %T\n", status)
	fmt.Println("status=", status)
}
~~~

## iota计数

iota 在 const关键字出现时将被重置为 0（ const 内部的第一行），const 中每新增一行常量声明将使 iota 计数一次(iota 可理解为 const 语句块中的行索引)。

iota 可以被用作枚举值：

~~~go
package main
import "fmt"

const (
	a = iota
	b
	c
)

func main() {
	fmt.Println("a=", a, "b=", b, "c=", c)
}
~~~

# 数据类型

