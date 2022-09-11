### Linux版本

Ubuntu、RedHat、CentOS、Fedora等版本，每个版本应用的领域不同。

CentOS常被用于后台服务器的操作系统

### 入门命令行指令

- 命令提示符 [root@localhost etc]#
  - root 表示以超级管理员身份登录；localhost主机名；etc是当前目录；#表示当前用户为root用户，如果是$表示当前是普通用户

  - /root 是root用户的家目录  不管在哪个目录下，直接执行cd命令都会进入家目录

- 目录操作
  - cd 更换目录  [root@localhost ~]# cd /   从家目录更换到根目录
  - ls 列出目录下的所有文件和目录  [root@localhost /]# ls
  - pwd 显示当前目录的准确位置  [root@localhost etc]# pwd

- 文件操作
  - 新建普通文件：touch 文件名

    ```shell
    [root@localhost /]# touch 88
    ```

  - 新建目录：mkdir 目录名

    ```shell
    [root@localhost /]# mkdir test
    ```

  - 复制文件：cp 文件名 路径

    ```shell
    [root@localhost ~]# cp 88 test   //或者   
    [root@localhost /]# cp 88 /root/test
    ```
  
  - 删除文件：rm 方式 文件名
  
    ```shell
    [root@localhost /]# rm -f 88    -f //表示强制删除不会恢复
    [root@localhost /]# rm -rf test  -rf //表示强制删除目录以及里面的内容
    ```
  
- find grep  搜索 匹配

  - ```shell
    [root@localhost /]# find / -name 123   // find 路径 -name 文件名
    [root@localhost /]# grep a /root/123   // grep 字符 文件路径
    ```

- cat head tail查看文件内容

  - ```shell
    [root@localhost /]# cat 123    // cat 文件名
    ```
  
  - ```shell
    [root@localhost /]# head 123  //展示前10行   tail 展示后10行
    ```
  
- chmod 修改文件权限 （u 所有者 g 所在组 o 所有组）（r 读 w 写 x 可执行）

  - 赋予权限：

    ```shell
    chmod u=rwx, g=w, o=x  abc
    ```

  - 修改权限：

    ```shell
    chmod u+w, r+x, o-r
    ```

- 进程操作

  - 查看所有进程：

  - ```shell
    ps aux //以简单列表的形式列出进程信息；
    ```

  - ```shell
    ps -elf //(-e 显示所有进程 -f 使用完整格式)；
    ```

  - ```shell
    top //实时显示进程名 三秒刷新一次。
    ```

  - 查看特定进程：

    ```shell
    ps -ef | grep //+进程名 
    ```

- 查看日志

  - ```shell
    cat -n test.log |grep "debug"  // 查询关键字的日志(常用！~) （-n是显示行号）
    ```

  - ```shell
    tail -n 10 test.log //查询日志尾部最后10行的日志; 
    ```

    ```shell
    tail -fn 10 test.log //循环实时查看最后10行记录(最常用的)
    ```

  - head 与tail类似

  - 用more分页查看： 

    ```shell
    cat -n test.log |grep "debug" |more
    ```

      分页打印，通过空格键翻页

- 查找大于1G的文件

  - ```shell
    find \root -type f -size +800M
    ```

