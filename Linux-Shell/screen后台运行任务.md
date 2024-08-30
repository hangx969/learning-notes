一些任务需要在一个终端运行，能够保留运行日志，并不随着终端的关闭而终止。这个时候，就需要screen命令来执行这样的事。

# screen命令后台运行

## 创建会话

```sh
screen -S baidudl
```

- 这样，我们就创建了一个名为baidudl的会话（session）。

- 接下来，我们执行Ctrl-A D，就可以退出并保持当面会话。

- 接下来，我们通过`screen -ls`查看系统运行了哪些screen会话。

- 可以看到刚创建的baidudl已经创建了，接下来我们通过`screen -r baidudl`重新进入刚创建的会话

## 退出会话

~~~sh
#方法一：
exit
#方法二：
screen -S 209684.baidudl -X quit
~~~

## 分离会话

- screen -r进入不了会话，报错：“There is no screen to be resumed matching”，这通常意味着该会话正在被另一个终端使用，或者没有被正确分离（Detached）。

- 如果确定会话没有被其他用户使用，可以尝试强制分离当前会话并重新附加：

```sh
screen -D -r 209652
```

## 保存日志

~~~sh
screen -L -S download //就会在当前目录创建一个screenlog.0日志
~~~

