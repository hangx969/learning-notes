# if分支控制

基本使用示例：

~~~go
package main

import "fmt"

func main() {
	// 基本使用
	var age int
	fmt.Println("Input age")
	fmt.Scanln(&age) //传入地址才能让Scanln修改age变量的值
	if age > 18 {
		fmt.Println("age older than 18")
	}

	// if里面支持直接定义变量
	if price := 20; price > 18 {
		fmt.Println("price is higher than 18")
	}

	// if else
	if age > 18 {
		fmt.Println("age older than 18")
	} else {
		fmt.Println("age younger than 18")
	}

	// if, else if, else多分支
	var score int = 80
	if score == 100 {
		fmt.Println("score 100")
	} else if score >= 80 && score <= 99 {
		fmt.Println("score 80-99")
	} else if score < 80 && score >= 60 {
		fmt.Println("score 60-80")
	} else {
		fmt.Println("score less than 60")
	}

	// 嵌套分支
	var is_enabled bool = true
	var timeout_sec int = 15
	if is_enabled {
		if timeout_sec > 10 {
			fmt.Println("feature is enabled and set timeout second longer than 10s")
		} else {
			fmt.Println("feature is enabled and set timeout second shorter then 10s")
		}
	} else {
		fmt.Println("feature is not enabled")
	}
}
~~~

# switch分支控制

switch 语句用于基于不同条件执行不同动作，每一个 case 分支都是唯一的，从上到下逐一测试，直到匹配为止。

switch 的执行的流程是：

1. 先执行表达式，得到值，然后和 case 的表达式进行比较，如果相等就匹配到，然后执行对应的 case 的语句块，然后退出 switch 控制。
2. 如果 switch 的表达式的值没有和任何的 case 的表达式匹配成功，则执行 default 的语句块。执行后退出 switch 的控制.
3. golang 的 case 后的表达式可以有多个，使用 逗号 间隔
4. golang 中的 case 语句块不需要写 break , 因为默认会有,即在默认情况下，当程序执行完 case 语句块后，就直接退出该 switch 控制结构。

switch带表达式：

~~~go
package main

import "fmt"

func main() {
	// 基本使用
	var n1 int = 10
	var n2 int = 20
	// 去比较n1的值
	switch n1 {
	case n2, 10, 5:
		fmt.Println("ok1")
	case 20:
		fmt.Println("ok2")
	default:
		fmt.Println("No matches")
	}

}
~~~

switch不带表达式：

~~~go
package main

import "fmt"

func main() {
	var age int = 10

	switch {
	case age > 18:
		fmt.Println("age is older than 18")
	case age < 10:
		fmt.Println("age is younger than 10")
	default:
		fmt.Println("age is between 10 and 18")
	}
}
~~~

用switch还是if：

1. 如果判断的具体数值不多，而且符合整数、浮点数、字符、字符串这几种类型。建议使用 swtich语句，简洁高效。
2. 对区间判断和结果为 bool 类型的判断使用 if，if 的使用范围更广。

# for循环

与多数语言不同的是，Go语言中的循环语句只支持 for 关键字，而不支持 while 和 do-while 结构，关键字 for 的基本使用方法与C语言和 C++ 中非常接近。

基本使用：在for内定义循环变量

~~~go
package main

import "fmt"

func main() {
	for i := 0; i < 10; i++ {
		fmt.Printf("it is %d time loop\n", i)
	}
}
~~~

在for外面定义循环变量：

~~~go
package main

import "fmt"

func main() {
	var i int = 0
	for i < 10 {
		fmt.Printf("it is %d time loop\n", i)
		i++
	}
}
~~~

for-range遍历字符串和数组：

~~~go
package main

import "fmt"

func main() {
	var str string = "Hello World, 欢迎"
    
	// 传统下标遍历字符串。输出中文时会乱码
	for i := 0; i < len(str); i++ {
		fmt.Printf("%c\n", str[i])
	}

	// 切片遍历字符串，可避免中文乱码，但还是不够简洁
	str2 := []rune(str)
	for i := 0; i < len(str2); i++ {
		fmt.Printf("%c\n", str2[i])
	}

	// for range遍历，最简洁
    // range会直接返回下标和对应的值，下标从0开始
	for index, val := range str{
		fmt.Printf("index is %d, value is %c \n", index, val)
	}
} 
~~~

用for实现while：

~~~go
package main

import "fmt"

func main() {
	// 使用for实现while的效果，输出10次Hello World
	var i int = 1
	for {
		if i > 10 {
			break
		}
		fmt.Println("Hello World")
		i++
	}
	fmt.Println("i=", i)
}
~~~

用for实现do while循环：就是把if break放后面

~~~go
package main

import "fmt"

func main() {
	// 使用for实现while的效果，输出10次Hello World
	var i int = 1

	for {
		fmt.Println("Hello World")
		i++
		if i > 10 {
			break
		}
	}
	fmt.Println("i=", i)
}
~~~

嵌套for循环：

~~~go
package main

import "fmt"

func main() {
	var num int = 9
	for i := 1; i<=num; i++{
		for j := 1; j<=i; j++{
			fmt.Printf("%d*%d=%d ", j, i, j*i)
		}
		fmt.Println()
	}
}
~~~

# 跳转控制语句

## break

中断for循环，或者跳出当前switch语句

~~~go
package main

import (
	"fmt"
	"math/rand"
)

func main() {
// 随机生成 1-100 的一个数，直到生成了 99 这个数，看看用了几次?
// 分析：编写一个无限循环的控制，然后不停的随机生成数，当生成了 99 时，就退出这个无限循环。

//如何随机的生成1-100整数
// n := rand.Intn(100) + 1 // [0, 100) -> [1, 100]
	var count int =0
	for {
		n := rand.Intn(100) + 1
		count += 1
		if n == 99{
			break
		}
	}
	fmt.Println("count=", count)
}
~~~

## continue

continue 语句用于结束本次循环，继续执行下一次循环。

continue 语句出现在多层嵌套的循环语句体中时，可以通过标签指明要跳过的是哪一层循环, 和前面的 break 标签的使用的规则一样.

~~~go
package main

import (
	"fmt"
)

func main() {

	label1:
	for i := 0; i < 3; i++ {
		for j := 0; j < 10; j++ {
			if j == 2 {
                continue label1 //用标签可以直接跳到外面的label1:这里，继续走外层循环。不用标签的话continue默认是继续走最近的一层循环
			}
			fmt.Println("j=", j)
		}
	}
}
~~~

## goto

Go 语言的goto语句可以无条件地转移到程序中指定的行。

~~~go
package main

import (
	"fmt"
)

func main() {

	var n int = 30
    //演示goto的使用
    fmt.Println("ok1")
    if n > 20 {
        goto label1
    }
    fmt.Println("ok2")
    fmt.Println("ok3")
    fmt.Println("ok4")
    label1:
    fmt.Println("ok5")
    fmt.Println("ok6")
    fmt.Println("ok7")
}
~~~

## return

return 使用在方法或者函数中，表示跳出所在的方法或函数

1. 如果 return 是在普通的函数，则表示跳出该函数，即不再执行函数中 return 后面代码，也可以理解成终止函数。
2. 如果 return  是在 main 函数，表示终止 main 函数，也就是说终止程序。