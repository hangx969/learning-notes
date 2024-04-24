# 后台运行命令nohup

- `nohup`命令可以让你的程序在后台静默运行，即使你退出了终端。例如：

```sh
nohup cp /path/to/source /path/to/destination &
```

- `&`符号会让命令在后台运行。

- 使用`nohup`命令运行的程序，其标准输出和标准错误默认都会被重定向到一个名为`nohup.out`的文件中。所以，你可以通过检查这个文件来查看`cp`命令是否成功完成，以及是否有任何错误信息。

- 例如，你可以使用`tail`命令来查看`nohup.out`文件的最后几行：

```sh
tail nohup.out
```

- 如果`cp`命令成功完成，那么`nohup.out`文件可能不会有任何输出。如果`cp`命令遇到错误，那么错误信息将会被写入`nohup.out`文件。

# screen

另一种方法是使用`screen`命令，它可以创建一个或多个shell会话，这些会话可以在后台运行，也可以在需要时恢复。例如，你可以这样使用`screen`命令：

```sh
screen
cp /path/to/source /path/to/destination
```

然后按`Ctrl+A`然后`D`来断开`screen`会话。你可以随时使用`screen -r`命令来恢复会话。
