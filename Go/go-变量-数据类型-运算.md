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

## 整型

- int
  - 64位系统占8字节
  - -2^63 ~ 2^63-1

- int8
  - 1字节
  - -128 - 127
- int16
  - 2字节
  - -2^15 ~ 2^15-1
- int32
  - 4字节
  - -2^31 ~ 2^31-1
- int64
  - 8字节
  - -2^63 ~ 2^63-1

- uint
  - 64位系统占8字节
  - 0~2^64-1

- uint8
  - 1字节
  - 0~255
- uint16
  - 2字节
  - 0~2^16-1
- uint32
  - 4字节
  - 0~2^32-1
- uint64
  - 8字节
  - 0~2^64-1
- rune：等价int32，表示一个Unicode码
- byte：等价uint8，存储字符用byte

## 字符型

Go语言的字符有以下两种：

1. 一种是 uint8 类型，或者叫 byte 型，代表了 ASCII 码的一个字符。用 1 个字节的传统 ASCII 编码的字符来说，完全没有问题，例如 `var ch byte = 'A'`，字符使用单引号括起来。

2. 另一种是 rune 类型，代表一个 UTF-8 字符，当需要处理中文、日文或者其他复合字符时，则需要用到 rune 类型。rune 类型等价于 int32 类型。

Go 语言的编码都统一成了 utf-8。非常的方便，很统一，再也没有编码乱码的困扰了

## 布尔型

一个布尔类型的值只有两种：true 或 false。if 和 for 语句的条件部分都是布尔类型的值，并且==和<等比较操作也会产生布尔型的值。

## 字符串

Go 语言的字符串的字节使用 UTF-8 编码标识 Unicode 文本。

~~~go
package main

import (
	"fmt"
)

// golang中string类型使用
func main() {
	//string的基本使用
	var str1 string = "hello world!"
	fmt.Println(str1)
	//在Go中字符串是不可变的,字符串一旦赋值了，字符串就不能修改了：

	//字符串的两种表示形式:
	//(1) 双引号, 会识别转义字符
	str2 := "abc\nabc"
	fmt.Println(str2)

	//(2) 反引号``，以字符串的原生形式输出，包括换行和特殊字符，可以实现防止攻击、输出源代码等效果
	str3 := `
    package main
    import (
        "fmt"
        "unsafe"
    )`
	fmt.Println(str3)

	//字符串拼接方式
	var str4 = "welcome " + "to"
	str4 += " China!"
	fmt.Println(str4)
	//当一个拼接的操作很长时，可以分行写
	// 但是注意，需要将+保留在上一行
	str5 := "hello " + "world" + "hello " +
		"world" + "hello " + "world" + "world" +
		"hello "
	fmt.Println(str5)
}
~~~

## 查看类型和字节数

~~~go
package main
import (
	"fmt"
	"unsafe"
)

func main(){
	var i int = 10
	fmt.Printf("Type of i: %T \n", i)
	fmt.Printf("Byte size of i: %d \n", unsafe.Sizeof(i))
}
~~~

## 各种类型的默认值

~~~go
package main
import (
	"fmt"
)

func main(){
	var a int //0
	var b float32 //0
	var c float64 //0
	var isGood bool // false
	var name string //""

	fmt.Printf("a=%v, b=%v, c=%v, isGood=%v, name=%v", a, b, c, isGood, name)
}
~~~

## 数据类型转换

1. 基本类型转string

   ~~~go
   package main
   
   import (
   	"fmt"
   )
   
   func main() {
   	var a int = 1
   	var b float64 = 8.6
   	var c byte = 'a'
   	var d bool = true
   	var str string
   
   	//使用Sprintf方法转成字符串
   	//参数的类型要和原值的类型保持一致，比如%d和a int
   	// 整型转字符串
   	str = fmt.Sprintf("%d", a)
   	fmt.Printf("Type of str is %T, str=%q \n", str, str)
   	// 浮点数转字符串
   	str = fmt.Sprintf("%f", b)
   	fmt.Printf("Type of str is %T, str=%q \n", str, str)
   	// 字符转字符串
   	str = fmt.Sprintf("%c", c)
   	fmt.Printf("Type of str is %T, str=%q \n", str, str)
   	// 布尔转字符串
   	str = fmt.Sprintf("%t", d)
   	fmt.Printf("Type of str is %T, str=%q \n", str, str)
   }
   ~~~

2. 字符串转基本数据类型

   使用strconv包。在标准官方库文档有：https://studygolang.com/static/pkgdoc/pkg/strconv.htm

   ~~~go
   package main
   
   import (
   	"fmt"
   	"strconv"
   )
   
   func main() {
   
   	// 字符串转布尔
   	// 1. strconv.ParseBool(str) 函数会返回两个值 (value bool, err error)
   	// 2. 只想获取到 value bool ,不想获取 err 所以用_忽略
   	var d bool
   	var str1 string = "true"
   	d, _ = strconv.ParseBool(str1)
   	fmt.Printf("Type of d: %T, b=%v \n", d, d)
   
   	// 字符串转整型
   	//参数str1表示数字的字符串形式
   	//参数10表示数字的字符串进制
   	//参数64表示返回结果的bit大小，如int8、int16、int32
   	var str2 string = "12"
   	var a int64
   	a, _ = strconv.ParseInt(str2, 10, 64)
   	fmt.Printf("Type of a: %T, a=%v \n", a, a)
   
   	// 整型互转
   	var a1 int
   	a1 = int(a)
   	fmt.Printf("Type of a1: %T, a1=%v \n", a1, a1)
   
   	// 字符串转浮点数
   	var b float64
   	var str3 string = "8.5"
   	b, _ = strconv.ParseFloat(str3, 64)
   	fmt.Printf("Type of b: %T, a1=%v \n", b, b)
   
   }
   
   //注意：
   //在将 String 类型转成 基本数据类型时，要确保 String 类型能够
   //转成有效的数据，比如 我们可以把 "123" , 转成一个整数，但是
   //不能把 "hello" 转成一个整数，如果这样做，Golang 直接将其转成
   //0 ， 其它类型也是一样的道理. float => 0， bool => false
   ~~~

## 指针变量

- Go语言中的函数传参都是值拷贝，当我们想要修改某个变量的时候，我们可以创建一个指向该变量地址的指针变量。传递数据使用指针，而无须拷贝数据。类型指针不能进行偏移和运算。Go语言中的指针操作非常简单，只需要记住两个符号：**&（取地址）和 *（根据地址取值）**。

- 一个指针变量可以指向任何一个值的内存地址，它所指向的值的内存地址在 32 和 64 位机器上分别占用 4 和 8 个字节，占用字节的大小与所指向的值的大小无关。

- **当一个指针被定义后没有分配到任何变量时，它的默认值为 nil**。指针变量通常缩写为 ptr。

- 每个变量在运行时都拥有一个地址，这个地址代表变量在内存中的位置。Go语言中使用在变量名前面添加&操作符（前缀）来获取变量的内存地址（取地址操作），格式如下： 

~~~go
var i int = 10
var ptr  *int = &i
// 变量 i 的地址使用变量 ptr 进行接收，ptr 的类型为 *int，称做 int 的指针类型，*代表指针。
~~~

打印变量地址：

~~~go
package main

import "fmt"

func main(){
	var i int = 3
	var name string = "bob"
	fmt.Printf("num:%p, name:%p", &i, &name)
}
// 使用 fmt.Printf 的动词%p打印 num和 str 变量的内存地址，指针的值是带有0x十六进制前缀的一组数据。
~~~

## 指针变量使用流程

1. 定义指针变量。

2. 为指针变量赋值。

3. 访问指针变量中指向地址的值。

4. 在指针类型前面加上 * 号（前缀）来获取指针所指向的内容。

~~~go
package main

import "fmt"

func main() {
	var i int = 10
	fmt.Println("var i address:", &i)

	// ip的类型是*int,赋值为&i
	var ip *int = &i
	fmt.Printf("ip=%v\n", ip)
	fmt.Printf("ip address is:%v\n", &ip)
	fmt.Printf("ip value is: %v", *ip)
}
~~~

# 运算符

## 算术运算符

1. 加+
2. 减-
3. 乘*
4. 除/
5. 取余%
6. 自增自减++ --

注意：

1. 自增自减只能当做一个单独的语句，在单独的一行里面使用
2. Golang 的++ 和 -- 只能写在变量的后面，不能写在变量的前面，即：只有 a++ a--，没有++a和--a

## 关系运算符

1. ==
2. !=
3. \>
4. \<
5. \>=
6. <=

## 逻辑运算符

1. and：&&
2. or：||
3. not：!

## 赋值运算符

1. +=
2. -=
3. *=
4. /=
5. <<= 按位左移后赋值
6. \>\>= 按位右移后赋值
7. &= 按位与后赋值 
8. |= 按位或后赋值
9. ^= 按位异或后赋值

## 位运算符

1. & 与
2. | 或
3. ^ 异或
4. << 左移
5. \>\> 右移

## 指针运算符

1. & 返回变量的地址 &a
2. \* 取地址对应的值 *ptr
