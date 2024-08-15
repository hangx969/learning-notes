# inotifywait

- 有时候我们常需要当文件变化的时候便触发某些脚本操作，比如说有文件更新了就同步文件到远程机器。在实现这个操作上，主要用到两个工具，一个是rsync，一个是inotifywait。inotifywait的作用是监控文件夹变化，rsync是用来同步，可同步到本机的其他目录或者远程服务器上。

> - inotify 是一个 Linux 内核提供的 API，它可以监视文件系统事件，比如文件或目录的创建、删除、修改等。
>
>
> - inotify-tools 是一套用户空间的工具，包括 inotifywait 和 inotifywatch，用于使用 inotify API。这些工具可以对文件系统事件进行监控，并生成相应的警告或日志。
>
>
> - inotifywait是一个非常实用的命令，它属于inotify-tools包，可以用来监控Linux文件系统事件。

## 安装rsync+inotifywait

~~~sh
#源码安装
wget http://rsync.samba.org/ftp/rsync/src/rsync-3.1.1.tar.gz
tar zxvf rsync-3.1.1.tar.gz 
./configure –prefix=/usr/local/rsync-3.1.1
make
make install

wget http://github.com/downloads/rvoicilas/inotify-tools/inotify-tools-3.14.tar.gz
tar zxvf inotify-tools-3.14.tar.gz
cd inotify-tools-3.14
./configure
make
make install

#直接apt安装
sudo apt install rsync
sudo apt install inotify-tools
~~~

## inotifywait基本使用

~~~sh
#监控文件的修改操作：
inotifywait -m -r -e modify /path/to/file
#监控目录或文件的属性变化：
inotifywait -m -r -e attrib /path/to/directory
#监控多个目录或文件的事件：
inotifywait -m -r -e create,delete,move /path/to/directory1 /path/to/directory2 /path/to/file1 /path/to/file2
#监控事件并执行命令：
inotifywait -m -r -e create,delete,move /path/to/directory -- /path/to/command
~~~

## 创建监控同步脚本

~~~sh
#!/bin/bash
export CNROMS_SRC=/home/ftpuser/gri/   # 同步的路径，请根据实际情况修改
inotifywait --exclude '\.(part|swp)' -r -mq -e  modify,move_self,create,delete,move,close_write $CNROMS_SRC |
  while read event;
    do
    rsync -vazu --progress  --password-file=/etc/rsyncd_rsync.secret  /home/ftpuser/gri/sla  rsync@10.208.1.1::gri ##这里执行同步的命令，可以改为其他的命令

  done
~~~

~~~sh
#后台运行脚本
chmod +x inotifywait.sh
#如果不想生成日志
nohup sh inotifywait.sh > /dev/null 2>&1
#如果想生成日志
nohup sh inotifywait.sh > output.log 2>&1
~~~

# systemd管理rsync同步任务

## 编写rsync脚本

~~~sh
#!/bin/bash

SRC_DIR="/home/s0001969/Documents/learning-notes-git"
DEST_DIR="/home/backup/"
LOGFILE="/var/log/rsync_sync.log"
DELAY=10 #增加延迟时间以减少频繁同步

while inotifywait -e modify,move_self,create,delete,move,close_write -r "$SRC_DIR"
do
    echo "Sync started at $(date)" >> "$LOGFILE"

    if rsync -avhz --delete "$SRC_DIR" "$DEST_DIR"; then
        echo "Sync successful at $(date)" >> "$LOGFILE"
    else
        echo "Sync failed at $(date)" >> "$LOGFILE"
    fi

    sleep $DELAY
done
~~~

## 创建systemd服务单元

~~~sh
tee rsync-inotifywait.service <<'EOF'
[Unit]
Description=Sync Service
After=network.target

[Service]
ExecStart=/bin/bash /home/s0001969/rsync-inotifywait.sh
Restart=Always
User=root

[Install]
WantedBy=multi-user.target
EOF

sudo cp rsync-inotifywait.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable rsync-inotifywait.service
sudo systemctl start rsync-inotifywait.service && sudo systemctl status rsync-inotifywait.service
~~~

- 查看所有service

~~~sh
sudo systemctl --type=service
#只查看active的
sudo systemctl --type=service --state=active
~~~

- 禁用service

~~~sh
sudo systemctl disable rsync-inotifywait.service
~~~

