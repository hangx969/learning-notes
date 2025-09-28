# Go背景

Go语言亦叫Golong语言，是由谷歌Google公司推出。Go语言保证了既能到达静态编译语言的安全和性能，又达到了动态语言开发速度和易维护性，有人形容Go语言：Go = C + Python , 说明Go语言既有C静态语言程序的运行速度，又能达到Python动态语言的快速开发。

2009发布并正式开源，2012年第一个正式版本Go 1.0发布。

官网地址：

- Golang 官方网站：https://golang.org
- Golang 官方标准库API：https://golang.org/pkg
- Golang 中文网官方标准库API：https://studygolang.com/pkgdoc

1. 并发编程

   Go语言天然并发，只需要关键字“go”就可以让函数并发执行，使得并发编程变得更为简单，这也是Go语言最大的优势。Go语言的并发是基于 goroutine 的，goroutine 类似于线程，但并非线程。可以将 goroutine 理解为一种虚拟线程。Go 语言运行时会参与调度 goroutine，并将 goroutine 合理地分配到每个 CPU 中，最大限度地使用CPU性能。开启一个goroutine的消耗非常小（大约2KB的内存），你可以轻松创建数百万个goroutine。

2. 性能好

   与其他现代高级语言（如Java/Python）相比，使用C，C++的最大好处是它们的性能。因为C/ C++是编译型语言而不是解释的语言。 处理器只能理解二进制文件，Java和Python这种高级语言在运行的时候需要先将人类可读的代码翻译成字节码，然后由专门的解释器再转变成处理器可以理解的二进制文件。同C,C++一样，Go语言也是编译型的语言，它直接将人类可读的代码编译成了处理器可以直接运行的二进制文件，执行效率更高，性能更好。

3. 语法简介

   Go 语言被称为“互联网时代的C语言”。Go 语言的风格类似于C语言。其语法在C语言的基础上进行了大幅的简化，去掉了不需要的表达式括号，循环也只有 for 一种表示方法，就可以实现各种遍历。

4. 开发效率高

   Go语言实现了开发效率与执行效率的完美结合，让你像写Python代码（效率）一样编写C代码（性能）。

5. 代码风格统一

   Go 语言提供了一套格式化工具——go fmt。一些 Go 语言的开发环境或者编辑器在保存时，都会使用格式化工具进行修改代码的格式化，这样就保证了不同开发者提交的代码都是统一的格式。

## Go项目结构规划

个人项目：

![image-20250928114717648](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202509281147723.png)

公司项目：

![image-20250928114732249](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202509281147306.png)

# Windows下配置Go开发环境

## 下载安装

1. 下载Go：在Go语言官网（https://golang.google.cn/dl/）下载 Windows 系统下的Go语言开发包，如下图所示。

2. 双击安装包安装

## 配环境变量

1. 把**用户变量**中的GOPATH删除。
2. 把**用户变量-PATH变量**中自带的%USERPROFILE%\go\bin删除
3. 创建go代码目录：

~~~powershell
mkdir D:\cache\gocode
cd D:\cache\gocode
mkdir src
mkdir bin
mkdir pkg
# src：存放源代码
# bin:  存放编译后的二进制文件
# pkg：存放编译后的库文件
~~~

4. 在系统变量里增加go相关的变量：

| 变量名           | 变量值                             | 作用                                                         |
| ---------------- | ---------------------------------- | ------------------------------------------------------------ |
| GOPATH           | [根据实际位置] D:\cache\gocode     | 指定存放自已编写的go代码的路径。<br />Go语言是一个编译型语言，有很多依赖包需要开发在打包过程编译进去。所以需要配置一个类似workspace的工作区，也就是定义好目录，要在这个目录下写源代码。 |
| GOROOT           | [根据实际安装位置] D:\0Software\Go | GOPATH变量：用来表明你写的go项目的存放路径（工作目录）。指定Go安装包的安装路径 |
| GO111MODULE      | auto                               | GOPATH路径最好只设置一个，所有的项目代码都放在GOPATH的src目录下。在这种模式下，Go 会表现：<br />1. 当项目路径在 GOPATH 目录外部时，设置为 GO111MODULE = on；<br />2. 当项目路径位于 GOPATH 内部时，即使存在 go.mod, 设置为 GO111MODULE = off。 |
| GOPROXY          | https://goproxy.cn                 | 配置go下载包的代理地址为七牛云的go代理地址。go依赖包默认下载地址是国外的，中国访问不了 |
| 【系统变量】PATH | D:\0Software\Go\bin                | cmd中可以运行go指令                                          |

5. 打开cmd，运行go env, go version检查是否能运行。

## 配vscode

装插件：

1. Go
2. vscode-go-syntax
3. code runner

# 测试第一个Go程序

- 创建项目目录

  ~~~sh
  mkdir gocode/src/goproject
  ~~~

- 创建源码文件main.go

  ~~~go
  package main // 在 go 中，每个文件都必须归属于一个包。必须在源文件中非注释的第一行指明这个文件属于哪个包，如：package main。表示该go文件所在的包是 main。只有main包的文件才能被go build编译。不是main包的只能被其他包引用。
  
  import "fmt" // import "fmt" 告诉 Go 编译器这个程序需要使用 fmt 包，引入该包后，就可以使用 fmt 包的函数，比如：fmt.Println
  
  func main() {
      fmt.Println("hello, world")
  }
  ~~~

- 运行代码【直接运行】

  ~~~sh
  go run ./main.go
  ~~~

- 运行代码【编译运行】

  ~~~sh
  go build ./main.go
  # 生成一个同名的exe文件，运行
  ./main.exe
  
  # 也可以指定exe文件名
  go build -o hello.exe main.go
  ~~~

# Go文件名和关键字

1. 所有的go源码都是以 ".go" 结尾。

2. 命名规则：

   1. 首字符可以是任意Unicode字符或者下划线
   2. 剩余字符可以是Unicode、数字或者下划线
   3. 字符长度不限

3. Go的关键字：25个

   brea, defaul, fun, interfac, selec, case, defer, go, map, struct, chan, else, goto, package, switch, const, fallthrough, if, range, type, continue, for, import, return, var

4. Go的保留字：37个
   - Constants：true, false, iota, nil
   - Types：int, int8, int16, int32, int64, uint, uint8, uint32, uint64, uintptr, float32, float64, complex128, complex64, bool, byte, rune, string, error
   - Functions：make, len, cap, new, append, copy, close, delete, complex, real, imag, panic, recover

# Go命令行

~~~sh
# cmd终端输入go会出现所有go命令行参数
go
~~~

- go env用于打印Go语言的环境信息。
- go run命令可以编译并运行源码文件。
- go get可以根据要求和实际情况从互联网上下载或更新指定的代码包及其依赖包，并对它们进行编译和安装。
- go build命令用于编译我们指定的源码文件或代码包以及它们的依赖包。
- go install用于编译并安装指定的代码包及它们的依赖包。
- go clean命令会删除掉执行其它命令时产生的一些文件和目录。
- go doc命令可以打印附于Go语言程序实体上的文档。我们可以通过把程序实体的标识符作为该命令的参数来达到查看其文档的目的。
- go test命令用于对Go语言编写的程序进行测试。go list命令的作用是列出指定的代码包的信息。
- go fix会把指定代码包的所有Go语言源码文件中的旧版本代码修正为新版本的代码。
- go vet是一个用于检查Go语言源码中静态错误的简单工具。
- go tool pprof命令来交互式的访问概要文件的内容。

# Go注释

1. 单行注释: //
2. 多行注释：/\* \*/

3. Golang中注释风格: Go 官方推荐使用行注释来注释整个方法和语句。

4. 代码风格：

   ~~~go
   package main
   import "fmt" 
   func main() {
   fmt.Println("hello,world!")
   }
   // 这样写是可以的，内容可以不缩进
   
   func main()
   {
   fmt.Println("hello,world!")
   }
   // 这样写不可以，{ 不能换行
   ~~~


