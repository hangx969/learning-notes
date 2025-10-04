# 数组

## 数组声明

~~~go
package main

func main() {
	//数组声明
	//方式一：
	var balance1 = [5]float32{1.0, 2.0, 3.4, 7.0, 5.0}

	// 方式二：类型推导在声明数组的同时快速初始化数组：
	balance2 := [5]float32{1.0, 2.0, 3.4, 7.0, 5.0}

	// 方式三：如果数组长度不确定，可以使用 ... 代替数组的长度，编译器会根据元素个数自行推断数组的长度：
	var balance3 = [...]float32{1.0, 2.0, 3.4, 7.0, 5.0}
	// 或
	balance4 := [...]float32{1.0, 2.0, 3.4, 7.0, 5.0}

	// 方式四：如果设置了数组的长度，通过指定下标来初始化个别元素：
	// 将索引为 1 和 3 的元素初始化，其他没赋值的默认就是0
	balance5 := [5]float32{1: 2.0, 3: 7.0}

}
~~~

## 数组访问

用索引来访问数组元素

~~~go
var salary float32 = balance[9]
~~~

## 遍历数组

for..range遍历，这是 Go 语言一种独有的结构，可以用来遍历访问数组的元素。

~~~go
package main

import "fmt"

func main() {
	names := [3]string{"Bob", "Alice", "Tom"}
    // 遍历数组，range返回索引和值。可以用 _ 忽略i或者v
	for i, v := range names {
		fmt.Printf("Index is %d, value is %s\n", i, v)
	}
}
~~~

# 切片

Go 语言切片是对数组的抽象。Go 数组的长度不可改变，在特定场景中这样的集合就不太适用，Go 中提供了一种灵活，功能强悍的内置类型切片("动态数组")，与数组相比切片的长度是不固定的，可以追加元素，在追加时可能使切片的容量增大。比方说存放学生成绩，那学生个数是不确定的，这样就可以用切片。

切片是数组的一个引用，因此切片是引用类型，在进行传递时，遵守引用传递的机制。

切片本质是对数组的一个“轻量级封装”，包含指向底层数组的指针、长度和容量。

切片可以通过 append 动态扩容，数组不行。

## 切片定义

~~~go
package main

import "fmt"

func main() {

    intArr := [...]int{1, 11, 22, 55, 76}

    //方法1：定义一个切片，直接引用已经存在的一个数组中的某些元素
    slice := intArr[1:3]

    //方法2：make切片
    // var 切片名 []type = make([]type, len, [cap])
    // type:  切片的数据类型
    // len : 切片元素的个数
    // cap ：指定切片容量，可选， 如果你分配了 cap,则要求 cap>=len.
    var slc []float64 = make([]float64, 5, 10)
    slc[0] = 1.0
    slc[1] = 2.0
    fmt.Println("slc=", slc)

    //第3种方式：定义一个切片，直接就指定具体数组，使用原理类似make的方式
    strSlc := []string{"Bob", "Tom", "Alice"}

}
~~~

意义在于获得动态长度、灵活操作的集合类型，这和数组是不同的。Go开发中，绝大多数场景都推荐用切片而不是数组。

## 切片基本使用

~~~go
package main

import "fmt"

func main() {

    //演示切片的基本使用
    var intArr [5]int = [...]int{1, 11, 22, 55, 76}

    //声明/定义一个切片
    //1. slice 就是切片名
    //2. intArr[1:3] 表示 slice 引用到intArr这个数组
    //3. 引用intArr数组的起始下标为 1 , 最后的下标为3(但是不包含3)。所以就是索引1，索引2的元素
    slice := intArr[1:3]
    fmt.Println("intArr=", intArr)
    fmt.Println("slice 的元素 =", slice)
    fmt.Println("slice 的元素个数 =", len(slice)) // 2
    fmt.Println("slice 的容量 =", cap(slice)) // 切片的容量是可以动态变化
    fmt.Printf("intArr[1]的地址=%p\n", &intArr[1])
    fmt.Printf("slice[0]的地址=%p slice[0]==%v\n", &slice[0], slice[0])

    slice[1] = 66 //改了Slice的元素，原数组的元素也随之改变
    //添加元素
    slice = append(slice, 18)
    fmt.Println("intArr=", intArr)
    fmt.Println("slice 的元素是 =", slice) // 11 66 18

}
~~~

## 切片的遍历

~~~go
package main

import "fmt"

func main() {

    strSlc := []string{"Bob", "Tom", "Alice"}

    //索引遍历
    for i:=0; i<3; i++{
        fmt.Printf("index is %v, value is %v\n", i, strSlc[i])
    }

    // for range遍历
    for i, v := range strSlc{
        fmt.Printf("index is %v, value is %v\n", i, v)
    }
}
~~~

# 二维数组

## 二维数组定义

~~~go
package main
import (
    "fmt"
)

func main() {
    //二维数组的演示案例
    /*
    0 0 0 0 0 0
    0 0 1 0 0 0
    0 2 0 3 0 0
    0 0 0 0 0 0
    */

    //定义/声明二维数组，四行六列
    var arr [4][6]int
    //赋初值
    arr[1][2] = 1
    arr[2][1] = 2
    arr[2][3] = 3

    //遍历二维数组，按照要求输出图形
    for i := 0; i < 4; i++ {
        for j := 0; j < 6; j++ {
            fmt.Print(arr[i][j], " ")
        }
        fmt.Println()
    }
}
~~~

## 二维数组遍历

~~~go
package main
import (
    "fmt"
)
func main() {
    //演示二维数组的遍历
    var arr3 = [2][3]int{{1,2,3}, {4,5,6}}

    //for循环来遍历
    for i := 0; i < len(arr3); i++ {
        for j := 0; j < len(arr3[i]); j++ {
            fmt.Printf("%v\t", arr3[i][j])
        }
        fmt.Println()
    }

    //for-range来遍历二维数组
    for i, v := range arr3 {
        for j, v2 := range v {
            fmt.Printf("arr3[%v][%v]=%v \t",i, j, v2)
        }
        fmt.Println()   
    }
}
~~~

# 集合

Map 是一种无序的键值对的集合。Map 最重要的一点是通过 key 来快速检索数据，key 类似于索引，指向数据的值。 

Map 是一种集合，所以我们可以像迭代数组和切片那样迭代它。不过，Map 是无序的，我们无法决定它的返回顺序，这是因为 Map 是使用 hash 表来实现的。 

## 集合声明

声明：var变量名 map[keytype]valuetype

注意：声明是不会分配内存的，初始化需要 make ，分配内存后才能赋值和使用。变量名 = make(map[keytype]valuetype)

备注：如果不初始化 map，那么就会创建一个 nil map。nil map 不能用来存放键值对

~~~go
package main

import "fmt"

func main() {

	// 声明map同时make初始化
	var a map[string]string = make(map[string]string, 10)
    // 用短声明更简洁
    b := make(map[string]string, 10)
    
	a["name1"] = "Bob"
	a["name2"] = "Alice"
	a["name3"] = "Tom"
	fmt.Println(a)
}
~~~

## 集合遍历

~~~go
package main

import "fmt"

func main() {

	b := make(map[string]string, 10)

	b["name1"] = "Bob"
	b["name2"] = "Alice"
	b["name3"] = "Tom"
    // for range遍历
	for k, v := range b {
		fmt.Printf("Key is %v, value is %v\n", k, v)
	}
}
~~~

## 集合增删改查

~~~go
package main

import "fmt"

func main() {

	b := make(map[string]string, 10)

	b["name1"] = "Bob"
	b["name2"] = "Alice"
	b["name3"] = "Tom"

	// 改
	b["name1"] = "Ann"

	// 如果key不存在就是增
	b["name4"] = "Cary"

	//删
	// delete 是一个内置函数，如果 key 存在，就删除该 key-value,如果 key 不存在，不操作，但是也不会报错。
	delete(b, "name4")

	//遍历输出
	for k, v := range b {
		fmt.Printf("Key is %v, value is %v\n", k, v)
	}

	// 如果我们要删除 map 的所有 key ,没有专门的方法一次删除，可以遍历key, 逐个删除.
	// 或者 map = make(...)，make 一个新的，这样原map会被GC回收，b变成一个新的空map。
	b = make(map[string]string)
}
~~~

