# 函数

基本使用：

~~~go
package main

import (
	"fmt"
)

func cal_result (m float64, n float64, cal_method byte) float64 {
	var result float64

	switch cal_method {
	case '+':
		result = m + n
	case '-':
		result = m - n
	case '*':
		result = m * n
	case '/':
		result = m / n
	default:
		fmt.Println("Input correct method")
	}
	return result
}

func main() {
	var m float64
	var n float64
	var cal_method byte
	var result float64

	fmt.Println("Input 1st number:")
	fmt.Scanln(&m)
	fmt.Println("Input 2nd number:")
	fmt.Scanln(&n)
	fmt.Println("Input cal method (+ - * /):")
	fmt.Scanf("%c", &cal_method) //接受字符输入

	result = cal_result(m, n, cal_method)
	fmt.Println("Result is:", result)
}
~~~

## 函数包调用

1. 在实际的开发中，我们往往需要在不同的文件中，去调用其它文件定义的函数，比如 main.go 中，去使用 utils.go  文件中的函数，如何实现？ 通过包实现
2. 现在有两个程序员共同开发一个 Go 项目，程序员A希望定义函数 Cal，程序员B也想定义函数也叫 Cal。怎么办? 通过包实现

包的基本介绍：

包的本质实际上就是创建不同的文件夹，来存放程序文件。go 的每一个文件都是属于一个包的，也就是说 go 是以包的形式来管理文件和项目目录结构的。

### 包的基本使用

~~~sh
# 在项目目录下创建子目录
mkdir -p goproject/functiondemo/main
mkdir -p goproject/functiondemo/utils
cd goproject/functiondemo/utils
# 创建程序文件
touch goproject/functiondemo/utils/utils.go
~~~

~~~go
package utils

import "fmt"

var Num1 int = 300 //大写开头变量名允许跨包访问

func Cal (m float64, n float64, operator byte) float64 { // 函数名大写，可以跨包调用

	var res float64

	switch operator{
	case '+':
		res = m + n
	case '-':
		res = m - n
	case '*':
		res = m * n
	case '/':
		res = m / n
	default:
		fmt.Println("Input corrent operator")
	}

	return res
}
~~~

在别的地方调用：

~~~sh
touch goproject/functiondemo/main/main.go
~~~

~~~go
package main

import(
	"fmt"
	"goproject/functiondemo/utils" // 定义好了GOPATH之后，引用包的路径就从src的下级目录开始写。而且是以目录的形式。utils是目录名，可以引用到目录下的所有包
)

func main(){
	fmt.Println("utils.go Num1 is:", utils.Num1)

	var m float64 = 6.4
	var n float64 = 5.7
	var operator byte = '+'

	fmt.Printf("result=%f", utils.Cal(m, n, operator))
}
~~~

## 函数return

Go的函数可以返回多个值。在调用函数接收返回值时，希望忽略某个返回值，则使用下划线表示占位忽略。

~~~go
package main

import (
	"fmt"
)

func cal(m float64, n float64) (float64, float64) {
    return m + n, m - n
}

func main() {
    var sum float64
    sum, _ = cal(10, 6)
	fmt.Println("Sum is:", sum)
}
~~~

## init函数

每一个源文件都可以包含一个 init 函数，该函数会在 main 函数执行前，被 Go 运行框架调用，也就是说 init 会在 main 函数前被调用

~~~go
package main

import (
	"fmt"
)

func init() {
    fmt.Println("init function is doing initializing...")
}

func main() {
	fmt.Println("Main func")
}
~~~

## 匿名函数

Go 支持匿名函数，匿名函数就是没有名字的函数，如果我们某个函数只是希望使用一次，可以考虑使用匿名函数，匿名函数也可以实现多次调用。

~~~go
package main
import (
    "fmt"
)

var (
    //如果将匿名函数赋给一个全局变量，就成为一个全局匿名函数，在整个程序有效
    Fun1 = func (n1 int, n2 int) int {
        return n1 * n2
    }
)

func main() {
    //在定义匿名函数时就直接调用，这种方式匿名函数只能调用一次
    //求两个数的和，使用匿名函数的方式完成
    res1 := func (n1 int, n2 int) int {
        return n1 + n2
    }(10, 20)

    fmt.Println("res1=", res1)

    //将匿名函数func (n1 int, n2 int) int赋给 a变量
    //则a的数据类型就是函数类型。此时可以通过a调用
    a := func (n1 int, n2 int) int {
        return n1 - n2
    }
    
    res2 := a(50, 60)
    fmt.Println("res2=", res2)
    
    res3 := a(90, 60)
    fmt.Println("res3=", res3)
    
    //全局匿名函数的使用
    res4 := Fun1(6, 9)
    fmt.Println("res4=", res4)
}
~~~

## 闭包

闭包就是一个函数和与其相关的引用环境组合的一个整体

~~~go
package main

import (
	"fmt"
)

// 累加器 返回值是一个匿名函数
func AddUpper() func(int) int {
	var n int = 10
	return func(x int) int {
		n += x
		return n
	}
}

func main() {
	f := AddUpper()
	fmt.Println(f(1))
	fmt.Println(f(1))
	fmt.Println(f(1))
    // 函数里面的n每次调用都会累加
}
~~~

~~~go
package main

import (
	"fmt"
	"strings"
)

// 1)编写一个函数 makeSuffix(suffix string)  可以接收一个文件后缀名(比如.jpg)，并返回一个闭包
// 2)调用闭包，可以传入一个文件名，如果该文件名没有指定的后缀(比如.jpg) ,则返回 文件名.jpg , 如果已经有.jpg后缀，则返回原文件名。

func makeSuffix(suffix string) func(string) string {

	return func(name string) string {
		if !strings.HasSuffix(name, suffix) {
			return name + suffix
		}
		return name
	}
}

func main() {
	f := makeSuffix(".jpg")
	fmt.Println("After Handling file name:", f("test"))
	fmt.Println("After Handling file name:", f("demo.jpg"))
}
// 闭包的好处，如果使用传统的函数，也可以轻松实现这个功能，但是传统方法需要每次都传入后缀名
// 而闭包因为可以保留上次引用的某个值，所以我们传入一次就可以反复使用。
~~~

# defer机制

在函数中，程序员经常需要创建资源(比如：数据库连接、文件句柄、锁等) ，为了在函数执行完毕后，及时的释放资源，Go 的设计者提供 defer (延时机制)。

1. 当 go 执行到一个 defer 时，不会立即执行 defer 后的语句，而是将 defer 后的语句压入到一个栈中, 然后继续执行函数下一个语句。
2. 当函数执行完毕后，在从 defer 栈中，依次从栈顶取出语句执行 (注：遵守栈先入后出的机制)

基本使用：

~~~go
package main
import (
    "fmt"
)
func sum(n1 int, n2 int) int {

    //当执行到defer时，暂时不执行，会将defer后面的语句压入到独立的栈(defer栈)
    //当函数执行完毕后，再从defer栈，按照先入后出的方式出栈，执行
    defer fmt.Println("ok1 n1=", n1) //defer 3. ok1 n1 = 10
    defer fmt.Println("ok2 n2=", n2) //defer 2. ok2 n2 = 20

    n1++
    n2++
    res := n1 + n2
    fmt.Println("ok3 res=", res) // 1. ok3 res= 32
    return res
}

func main() {
    result := sum(10, 20)
    fmt.Println("result=", result)  // 4. result= 32
}
~~~

最佳实践：

defer 最主要的价值是，当函数执行完毕后，可以及时的释放函数创建的资源。

在 golang 编程中的通常做法是：

1. 创建资源后，比如打开了文件，获取了数据库的链接，或者是锁资源，可以执行 defer file.Close() defer connect.Close()
2. 在 defer 后，可以继续使用创建资源
3. 当函数完毕后，系统会依次从 defer 栈中，取出语句，关闭资源
4. 这种机制，非常简洁，程序员不用再为在什么时机关闭资源而烦心

~~~go
func test(){
    file = openfile("filename")
    defer file.close
}

func dbconn(){
    connect = openDatabase()
    defer connect.close()
}
~~~