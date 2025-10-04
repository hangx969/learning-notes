# 错误处理

## 普通错误处理

Go鼓励通过返回值显式传递和处理错误，而不是依赖异常（panic/recover）。只有在不可恢复的严重错误（如数组越界、除零、程序内部bug）时才用panic。

~~~go
package main

import (
    "errors"
    "fmt"
)

func safeDivide(num1, num2 int) (int, error) {
    if num2 == 0 {
        return 0, errors.New("除数不能为0")
    }
    return num1 / num2, nil
}

func main() {
    num1 := 10
    num2 := 0
    res, err := safeDivide(num1, num2)
    if err != nil {
        fmt.Println("err=", err)
        return
    }
    fmt.Println("res=", res)
}
~~~

## 极端错误处理

只有在遇到不可恢复的致命错误时才用 panic/recover，比如程序内部不一致、严重bug等。业务逻辑错误（如除零、文件不存在）应通过 error 返回。

1. 在默认情况下，当发生错误后(panic) ，程序就会退出（崩溃）
2. 如果我们希望：当发生错误后，可以捕获到错误，并进行处理，保证程序可以继续执行。还可以在捕获到错误后，产生某些告警信息等
   这就需要对错误进行特殊处理：
   1. Go 语言追求简洁优雅，不支持传统的 try catch finally这种处理。
   2. Go 中引入的处理方式为：defer, panic, recover。简单描述：抛出一个 panic 的异常，在 defer 中通过 recover 捕获这个异常，然后正常处理。

~~~go
package main

import (
	"fmt"
)

func test() {

	//使用defer + recover 来捕获和处理异常
	defer func() { //defer注册一个延迟调用的匿名函数。
		err := recover() // recover()内置函数，没panic返回nil；有panic返回panic值
		if err != nil {  // 说明捕获到错误
			fmt.Println("err=", err)
		}
	}()

	num1 := 10
	num2 := 0
	res := num1 / num2 //这里有panic。Go 会立即中断当前函数的执行，转而执行已经注册的 defer 语句
	fmt.Println("res=", res)
}

func main() {
	test()
}
~~~

# 自定义错误

Go 程序中，也支持自定义错误， 使用 errors.New 和 panic 内置函数。

1. errors.New("错误说明"), 会返回一个 error 类型的值，表示一个错误
2. panic 内置函数，接收一个 interface{} 类型的值（也就是任何值）作为参数。可以接收 error 类型的变量，输出错误信息，并退出程序。

~~~go
package main

import (
	"fmt"
    "errors"
)

func readconf(name string) (err error) {

	// 读取init.conf配置文件，如果文件名不正确，返回自定义错误
    if name == "init.conf"{
        return nil
    }else{
        return errors.New("read file error")
    }
}

func test(){
    err := readconf("config.ini")
    if err != nil{
        panic(err)
    }
    fmt.Println("Continue")
}

func main() {
	test()
}
~~~

