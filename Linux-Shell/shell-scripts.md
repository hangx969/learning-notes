# 删除用户脚本

~~~sh
#!/bin/bash
#
# Delete_User - Automates the 4 steps to remove an account
#
#################################################################
# 
# Define Functions
#
#################################################################
function get_answer {
#
  unset ANSWER
  ASK_COUNT=0
#
  while [ -z "$ANSWER" ] # while no answer is given, keep asking
  do
    ASK_COUNT=$[ $ASK_COUNT + 1 ]
#
    case $ASK_COUNT in      # If user gives no answer in time allowed
    2)
      echo 
      echo "Please answer the question."
      echo
    ;;
    3)
      echo 
      echo "One last try... please answer the question."
      echo
    ;;
    4)
      echo 
      echo "Since you refuse to answer the question..."
      echo "exiting program."
      echo
      #
      exit
    ;;
    esac
#
    echo
#  
    if [ -n "$LINE2" ]
    then
      echo $LINE1      # Print 2 lines
      echo -e $LINE2" \c"
    else          # Print 1 line
      echo -e $LINE1" \c"
    fi
#
# Allow 60 seconds to answer before time-out
    read -t 60 ANSWER
  done
#
# Do a little variable clean-up
#
  unset LINE1
  unset LINE2
#
}    #end of get_answer function
#
#################################################################
function process_answer {
#
  case $ANSWER in
  y|Y|YES|yes|yEs|yeS|YEs|yES)
  # If user answers "yes".do nothing.
  ;;
  *)
  # If user answers anything but "yes", exit script
    echo
    echo $EXIT_LINE1
    echo $EXIT_LINE2
    echo
    exit
  ;;
  esac
  #
  # Do a little variable clean-up
  unset EXIT_LINE1
  unset EXIT_LINE2
#
} #End of process_answer function
#
################################################################
#
# End of Function Definitions
#
############### Main Script #################################
#
# Get name of User Account to check
#
echo "Step #1 - Determine User Account name to delete "
echo
LINE1="Please enter the username of the user"
LINE2="account you wish to delete from system:"
get_answer
USER_ACCOUNT=$ANSWER
#
# Double check with script user that this is the correct User Account
#
LINE1="Is $USER_ACCOUNT the user account"
LINE2="you wish to delete from the system?[ y/n ]:"
get_answer
#
############################################################
#
# Check that USER_ACCOUNT is really an account on the system
#
USER_ACCOUNT_RECORD=$(cat /etc/passwd | grep -w $USER_ACCOUNT)
#
if [ $? -eq 1 ]      # If the account is not found, exit script
then
  echo 
  echo "Account, $USER_ACCOUNT, not found."
  echo "Leaving the script..."
  echo
  exit
fi
#
echo
echo "I found this record:"
echo $USER_ACCOUNT_RECORD
echo
#
LINE1="Is this the correct User Account?[y/n]:"
get_answer
#
#
# Call process_answer function:
#  if user answers anything but "yes", exit script
#
EXIT_LINE1="Because the account, $USER_ACCOUNT, is not "
EXIT_LINE2="the one you wish to delete, we are leaving the script..."
process_anser
#
##############################################################
#
# Search for any running processes that belong to the User Account
#
echo
echo "Step #2 - Find process on system belonging to user account"
echo
echo "$USER_ACCOUNT has the following processes running: "
echo
#
ps -u $USER_ACCOUNT      #List the processes running
#
case $? in
1)      # No processes running for this User Account
  #
  echo "There are no processes for this account currently running."
  echo
;;
0)  # Processes running for this User Account.
  # Ask Script User if wants us to kill the processes.
  #
  unset ANSWER      # I think this line is not needed
  LINE1="Would you like me to kill the process(es)? [y/n]:"
  get_answer
  #
  case $ANSWER in
  y|Y|YES|yes|Yes|yEs|yeS|YEs|yES)    # if user answer "yes",
    #kill User Account processes
    #
    echo 
    #
    # Clean-up temp file upon signals
    #
    trap "rm $USER_ACCOUNT_Running_Process.rpt" SIGTERM SIGINT SIGQUIT
    #
    # List user processes running
    ps -u $USER_ACCOUNT > $USER_ACCOUNT_Running_Process.rpt
    #
    exec < $USER_ACCOUNT_Running_Process.rpt    # Make report Std Input
    #
    read USER_PROCESS_REC        # First record will be blank
    read USER_PROCESS_REC
    #
    while [ $? -eq 0 ]
    do
      # obtain PID
      USER_PID=$(echo $USER_PROCESS_REC | cut -d " " -f1 )
      kill -9 $USER_PID
      echo "Killed process $USER_PID"
      read USER_PROCESS_REC
    done
    #
    echo
    #
    rm $USER_ACCOUNT_Running_Process.rpt      # Remove temp report
  ;;
  *) # If user answers anything but "yes", do not kill.
    echo
    echo "Will not kill the process(es)."
    echo
  ;;
  esac
;;
esac
###################################################################################
#
# Create a report of all files owned by User Account
#
echo
echo "Step #3 - Find files on system belonging to user account"
echo
echo "Creating a report of all files owned by $USER_ACCOUNT."
echo
echo "It is recommended that you backup/archive these files."
echo "and then do one of two things:"
echo " 1) Delete the files"
echo " 2) Change the files' ownership to a current user account."
echo
echo "Please wait. This may take a while..."
#
REPORT_DATE=`date +%y%m%d`
REPORT_FILE=$USER_ACCOUNT"_Files_"$REPORT_DATE".rpt"
#
find / -user $USER_ACCOUNT > $REPORT_FILE 2>/dev/null
#
echo
echo "Report is complete."
echo "Name of report:  $REPORT_FILE"
echo "Location of report:     `pwd`"
echo
################################################################
#
# Remove User Account
echo
echo "Step #4 - Remove user account"
echo
#
LINE1="Do you wish to remove $USER_ACCOUNT's account from system? [y/n]:"
get_answer
#
# Cass process_answer function:
#  if user answers anything but "yes", exit script
#
EXIT_LINE1="Since you do not wish to remove the user account."
EXIT_LINE2="$USER_ACCOUNT at this time, exiting the script..."
process_answer
#
userdel $USER_ACCOUNT      # delete user account
echo
echo "User account, $USER_ACCOUNT, has been removed"
echo
~~~

# 当服务器线程数超过2500时自动dump线程数最高的java进程的内存及线程栈

~~~sh
#!/usr/bin/env bash
# 来源: https://blog.csdn.net/qianghaohao/article/details/80379118 
# 服务器线程数达到 2500 以上时 dump 线程数最多的 java 进程的线程及内存
source ~/.bashrc
cur_thread_num=`ps -efL | wc -l`
if [ $cur_thread_num -le 2500 ]; then
    exit 0
fi

cur_date=`date +"%Y-%m-%d_%H-%M-%S"`
cd ./dumpfile
# 服务器当前线程 dump 到文件:按照线程数由大到小排序显示
ps -efL --sort -nlwp > server_thread_dump_$cur_date
# dump 线程数最多的 jvm 的线程及内存
most_thread_num_pid=`cat server_thread_dump_$cur_date | sed -n '2p' | awk '{print $2}'`
nohup jstack -l $most_thread_num_pid > java_app_thread_dump_${cur_date}_pid_${most_thread_num_pid} &
nohup jmap -dump:format=b,file=java_app_mem_dump_${cur_date}_pid_${most_thread_num_pid} $most_thread_num_pid &

exit 0
~~~

# 查看磁盘目录使用并排序

~~~sh
#!/bin/bash
#
# Big_Users - find big disk space users in various directories
#############################################################
#Parameters for script
#
CHECK_DIRECTORIES="/var/log /home" #directories to check，need to modify the script to get usage for specific directory
#
######################### Main Script #######################
#
DATE=$(date '+%m%d%y')             #Date for report file
#
exec > disk_space_$DATE.rpt         #Make report file Std Output
#
echo "Top Ten Disk Space Usage"     #Report header for while report
echo "for $CHECK_DIRECTORIES Directories"
#
for DIR_CHECK in $CHECK_DIRECTORIES       #loop to du directories
do
  echo ""
  echo "The $DIR_CHECK Directory:"  #Title header for each directory
#
#  Creating a listing of top ten disk space users
  du -Sh $DIR_CHECK 2>/dev/null |
  sort -rn |
  sed '{11,$D; =}' |
  sed 'N; s/\n/ /' | 
  gawk '{printf $1 ":" "\t" $2 "\t" $3 "\n"}'
#
done                #End of for loop for du directories
~~~

# 查看某目录使用量

~~~sh
dir=${1:-/} #指定目录 作为脚本第一个参数，默认是/
depth=${2:-5} #指定深度 作为脚本第二个参数，默认是5层
exclude_dir=$(df |awk 'NR>1 {print $6}' | grep -wv ${dir} | awk '{print "--exclude="$1""}')
du -h --max-depth=${depth} ${exclude_dir} ${dir} 2>/dev/null | awk '$1~/G$/{print $0}'
~~~



# 根据PID过滤进程信息

~~~sh
#! /bin/bash
# Function: 根据用户输入的PID，过滤出该PID所有的信息
read -p "请输入要查询的PID: " P
n=`ps -aux| awk '$2~/^'$P'$/{print $11}'|wc -l`
if [ $n -eq 0 ];then
 echo "该PID不存在！！"
 exit
fi
echo "--------------------------------"
echo "进程PID: $P"
echo "进程命令：`ps -aux| awk '$2~/^'$P'$/{print $11}'`"
echo "进程所属用户: `ps -aux| awk '$2~/^'$P'$/{print $1}'`"
echo "CPU占用率：`ps -aux| awk '$2~/^'$P'$/{print $3}'`%"
echo "内存占用率：`ps -aux| awk '$2~/^'$P'$/{print $4}'`%"
echo "进程开始运行的时刻：`ps -aux| awk '$2~/^'$P'$/{print $9}'`"
echo "进程运行的时间：`ps -aux| awk '$2~/^'$P'$/{print $10}'`"
echo "进程状态：`ps -aux| awk '$2~/^'$P'$/{print $8}'`"
echo "进程虚拟内存：`ps -aux| awk '$2~/^'$P'$/{print $5}'`"
echo "进程共享内存：`ps -aux| awk '$2~/^'$P'$/{print $6}'`"
echo "--------------------------------"
~~~

# 根据进程名显示所有线程

~~~sh
#! /bin/bash
# Function: 根据输入的程序的名字过滤出所对应的PID，并显示出详细信息，如果有几个PID，则全部显示
read -p "请输入要查询的进程名：" NAME
N=`ps -aux | grep $NAME | grep -v grep | wc -l` ##统计进程总数
if [ $N -le 0 ];then
  echo "该进程名没有运行！"
fi
i=1
while [ $N -gt 0 ]
do
  echo "进程PID: `ps -aux | grep $NAME | grep -v grep | awk 'NR=='$i'{print $0}'| awk '{print $2}'`"
  echo "进程命令：`ps -aux | grep $NAME | grep -v grep | awk 'NR=='$i'{print $0}'| awk '{print $11}'`"
  echo "进程所属用户: `ps -aux | grep $NAME | grep -v grep | awk 'NR=='$i'{print $0}'| awk '{print $1}'`"
  echo "CPU占用率：`ps -aux | grep $NAME | grep -v grep | awk 'NR=='$i'{print $0}'| awk '{print $3}'`%"
  echo "内存占用率：`ps -aux | grep $NAME | grep -v grep | awk 'NR=='$i'{print $0}'| awk '{print $4}'`%"
  echo "进程开始运行的时刻：`ps -aux | grep $NAME | grep -v grep | awk 'NR=='$i'{print $0}'| awk '{print $9}'`"
  echo "进程运行的时间：` ps -aux | grep $NAME | grep -v grep | awk 'NR=='$i'{print $0}'| awk '{print $11}'`"
  echo "进程状态：`ps -aux | grep $NAME | grep -v grep | awk 'NR=='$i'{print $0}'| awk '{print $8}'`"
  echo "进程虚拟内存：`ps -aux | grep $NAME | grep -v grep | awk 'NR=='$i'{print $0}'| awk '{print $5}'`"
  echo "进程共享内存：`ps -aux | grep $NAME | grep -v grep | awk 'NR=='$i'{print $0}'| awk '{print $6}'`"
  echo "***************************************************************"
  let N-- i++
done
~~~

# 根据用户名查询用户信息

~~~sh
#! /bin/bash
# Function：根据用户名查询该用户的所有信息
read -p "请输入要查询的用户名：" A
echo "------------------------------"
n=`cat /etc/passwd | awk -F: '$1~/^'$A'$/{print}' | wc -l`
if [ $n -eq 0 ];then
echo "该用户不存在"
echo "------------------------------"
else
  echo "该用户的用户名：$A"
  echo "该用户的UID：`cat /etc/passwd | awk -F: '$1~/^'$A'$/{print}'|awk -F: '{print $3}'`"
  echo "该用户的组为：`id $A | awk {'print $3'}`"
  echo "该用户的GID为：`cat /etc/passwd | awk -F: '$1~/^'$A'$/{print}'|awk -F: '{print $4}'`"
  echo "该用户的家目录为：`cat /etc/passwd | awk -F: '$1~/^'$A'$/{print}'|awk -F: '{print $6}'`"
  Login=`cat /etc/passwd | awk -F: '$1~/^'$A'$/{print}'|awk -F: '{print $7}'`
  if [ $Login == "/bin/bash" ];then
  echo "该用户有登录系统的权限！！"
  echo "------------------------------"
  elif [ $Login == "/sbin/nologin" ];then
  echo "该用户没有登录系统的权限！！"
  echo "------------------------------"
  fi
fi
~~~

# 加固用户密码配置

~~~sh
#! /bin/bash
# Function:对账户的密码的一些加固
read -p "设置密码最多可多少天不修改：" A
read -p "设置密码修改之间最小的天数：" B
read -p "设置密码最短的长度：" C
read -p "设置密码失效前多少天通知用户：" D
sed -i '/^PASS_MAX_DAYS/c\PASS_MAX_DAYS '$A'' /etc/login.defs
sed -i '/^PASS_MIN_DAYS/c\PASS_MIN_DAYS '$B'' /etc/login.defs
sed -i '/^PASS_MIN_LEN/c\PASS_MIN_LEN '$C'' /etc/login.defs
sed -i '/^PASS_WARN_AGE/c\PASS_WARN_AGE '$D'' /etc/login.defs

echo "已对密码进行加固，新用户不得和旧密码相同，且新密码必须同时包含数字、小写字母，大写字母！！"
sed -i '/pam_pwquality.so/c\password requisite pam_pwquality.so try_first_pass local_users_only retry=3 authtok_type= difok=1 minlen=8 ucredit=-1 lcredit=-1 dcredit=-1' /etc/pam.d/system-auth

echo "已对密码进行加固，如果输入错误密码超过3次，则锁定账户！！"
n=`cat /etc/pam.d/sshd | grep "auth required pam_tally2.so "|wc -l`
if [ $n -eq 0 ];then
sed -i '/%PAM-1.0/a\auth required pam_tally2.so deny=3 unlock_time=150 even_deny_root root_unlock_time300' /etc/pam.d/sshd
fi

echo  "已设置禁止root用户远程登录！！"
sed -i '/PermitRootLogin/c\PermitRootLogin no'  /etc/ssh/sshd_config

read -p "设置历史命令保存条数：" E
read -p "设置账户自动注销时间：" F
sed -i '/^HISTSIZE/c\HISTSIZE='$E'' /etc/profile
sed -i '/^HISTSIZE/a\TMOUT='$F'' /etc/profile

echo "已设置只允许wheel组的用户可以使用su命令切换到root用户！"
sed -i '/pam_wheel.so use_uid/c\auth required pam_wheel.so use_uid ' /etc/pam.d/su
n=`cat /etc/login.defs | grep SU_WHEEL_ONLY | wc -l`
if [ $n -eq 0 ];then
echo SU_WHEEL_ONLY yes >> /etc/login.defs
fi

echo "即将对系统中的账户进行检查...."
echo "系统中有登录权限的用户有："
awk -F: '($7=="/bin/bash"){print $1}' /etc/passwd
echo "********************************************"
echo "系统中UID=0的用户有："
awk -F: '($3=="0"){print $1}' /etc/passwd
echo "********************************************"
N=`awk -F: '($2==""){print $1}' /etc/shadow|wc -l`
echo "系统中空密码用户有：$N"
if [ $N -eq 0 ];then
 echo "恭喜你，系统中无空密码用户！！"
 echo "********************************************"
else
 i=1
 while [ $N -gt 0 ]
 do
    None=`awk -F: '($2==""){print $1}' /etc/shadow|awk 'NR=='$i'{print}'`
    echo "------------------------"
    echo $None
    echo "必须为空用户设置密码！！"
    passwd $None
    let N--
 done
 M=`awk -F: '($2==""){print $1}' /etc/shadow|wc -l`
 if [ $M -eq 0 ];then
  echo "恭喜，系统中已经没有空密码用户了！"
 else
echo "系统中还存在空密码用户：$M"
 fi
fi

echo "即将对系统中重要文件进行锁定，锁定后将无法添加删除用户和组"
read -p "警告：此脚本运行后将无法添加删除用户和组！！确定输入Y，取消输入N；Y/N：" i
case $i in
      [Y,y])
            chattr +i /etc/passwd
            chattr +i /etc/shadow
            chattr +i /etc/group
            chattr +i /etc/gshadow
            echo "锁定成功！"
;;
      [N,n])
            chattr -i /etc/passwd
            chattr -i /etc/shadow
            chattr -i /etc/group
            chattr -i /etc/gshadow
            echo "取消锁定成功！！"
;;
       *)
            echo "请输入Y/y or N/n"
esac
~~~

# 列出排名前10的内存占用进程

~~~sh
ps aux | sort -rk 4,4 | head -n 10
~~~

# iptables自动屏蔽访问网站频繁的IP

- 使用场景：针对恶意访问网站情况
  - 根据访问日志（以 nginx 的 logs 中记录访问的 access.log 日志文件为例，检测短期访问大于100的IP，并使用iptables命令进行屏蔽，同时将禁用的IP放到/tmp/deny_ip.log文件中）

```sh
#!/bin/bash
DATE=$(date +%d/%b/%Y:%H:%M)
LOG_FILE=/usr/local/nginx/logs/demo2.access.log
ABNORMAL_IP=$(tail -n5000 $LOG_FILE |grep $DATE |awk '{a[$1]++}END{for(i in a)if(a[i]>100)print i}')
for IP in $ABNORMAL_IP; do
    if [ $(iptables -vnL |grep -c "$IP") -eq 0 ]; then
        iptables -I INPUT -s $IP -j DROP
        echo "$(date +'%F_%T') $IP" >> /tmp/deny_ip.log
    fi
done
```

# 自动发布 Java 项目（Tomcat）

~~~sh
#!/bin/bash
DATE=$(date +%F_%T)

TOMCAT_NAME=$1
TOMCAT_DIR=/usr/local/$TOMCAT_NAME
ROOT=$TOMCAT_DIR/webapps/ROOT

BACKUP_DIR=/data/backup
WORK_DIR=/tmp
PROJECT_NAME=tomcat-java-demo

# 拉取代码
cd $WORK_DIR
if [ ! -d $PROJECT_NAME ]; then
   git clone https://github.com/xxxx/tomcat-java-demo
   cd $PROJECT_NAME
else
   cd $PROJECT_NAME
   git pull
fi

# 构建
mvn clean package -Dmaven.test.skip=true
if [ $? -ne 0 ]; then
   echo "maven build failure!"
   exit 1
fi

# 部署
TOMCAT_PID=$(ps -ef |grep "$TOMCAT_NAME" |egrep -v "grep|$$" |awk 'NR==1{print $2}')
[ -n "$TOMCAT_PID" ] && kill -9 $TOMCAT_PID
[ -d $ROOT ] && mv $ROOT $BACKUP_DIR/${TOMCAT_NAME}_ROOT$DATE
unzip $WORK_DIR/$PROJECT_NAME/target/*.war -d $ROOT
$TOMCAT_DIR/bin/startup.sh
~~~

# Nginx日志分析

~~~sh
#!/bin/bash
# 日志格式: $remote_addr - $remote_user [$time_local] "$request" $status $body_bytes_sent "$http_referer" "$http_user_agent" "$http_x_forwarded_for"
LOG_FILE=$1
echo "统计访问最多的10个IP"
awk '{a[$1]++}END{print "UV:",length(a);for(v in a)print v,a[v]}' $LOG_FILE |sort -k2 -nr |head -10
echo "----------------------"

echo "统计时间段访问最多的IP"
awk '$4>="[01/Dec/2018:13:20:25" && $4<="[27/Nov/2018:16:20:49"{a[$1]++}END{for(v in a)print v,a[v]}' $LOG_FILE |sort -k2 -nr|head -10
echo "----------------------"

echo "统计访问最多的10个页面"
awk '{a[$7]++}END{print "PV:",length(a);for(v in a){if(a[v]>10)print v,a[v]}}' $LOG_FILE |sort -k2 -nr
echo "----------------------"

echo "统计访问页面状态码数量"
awk '{a[$7" "$9]++}END{for(v in a){if(a[v]>5)print v,a[v]}}'
~~~

# 查看网卡实时流量

~~~sh
#!/bin/bash
NIC=$1
echo -e " In ------ Out"
while true; do
    OLD_IN=$(awk '$0~"'$NIC'"{print $2}' /proc/net/dev)
    OLD_OUT=$(awk '$0~"'$NIC'"{print $10}' /proc/net/dev)
    sleep 1
    NEW_IN=$(awk  '$0~"'$NIC'"{print $2}' /proc/net/dev)
    NEW_OUT=$(awk '$0~"'$NIC'"{print $10}' /proc/net/dev)
    IN=$(printf "%.1f%s" "$((($NEW_IN-$OLD_IN)/1024))" "KB/s")
    OUT=$(printf "%.1f%s" "$((($NEW_OUT-$OLD_OUT)/1024))" "KB/s")
    echo "$IN $OUT"
    sleep 1
done
~~~

# 批量检查网站是否异常并发邮件

~~~sh
#!/bin/bash  
URL_LIST="www.baidu.com www.ctnrs.com www.der-matech.net.cn www.der-matech.com.cn www.der-matech.cn www.der-matech.top www.der-matech.org"
for URL in $URL_LIST; do
    FAIL_COUNT=0
    for ((i=1;i<=3;i++)); do
        HTTP_CODE=$(curl -o /dev/null --connect-timeout 3 -s -w "%{http_code}" $URL)
        if [ $HTTP_CODE -eq 200 ]; then
            echo "$URL OK"
            break
        else
            echo "$URL retry $FAIL_COUNT"
            let FAIL_COUNT++
        fi
    done
    if [ $FAIL_COUNT -eq 3 ]; then
        echo "Warning: $URL Access failure!"
  echo "网站$URL坏掉，请及时处理" | mail -s "$URL网站高危" xxxxx@163.com
    fi
done
~~~

# 目录入侵检测与告警

~~~sh
#!/bin/bash

MON_DIR=/opt
inotifywait -mqr --format %f -e create $MON_DIR |\
while read files; do
   #同步文件
   rsync -avz /opt /tmp/opt
  #检测文件是否被修改
   #echo "$(date +'%F %T') create $files" | mail -s "dir monitor" xxx@163.com
done
~~~

# 一键查看服务器利用率

~~~sh
#!/bin/bash
function cpu(){

 util=$(vmstat | awk '{if(NR==3)print $13+$14}')
 iowait=$(vmstat | awk '{if(NR==3)print $16}')
 echo "CPU -使用率：${util}% ,等待磁盘IO相应使用率：${iowait}:${iowait}%"

}
function memory (){

 total=`free -m |awk '{if(NR==2)printf "%.1f",$2/1024}'`
    used=`free -m |awk '{if(NR==2) printf "%.1f",($2-$NF)/1024}'`
    available=`free -m |awk '{if(NR==2) printf "%.1f",$NF/1024}'`
    echo "内存 - 总大小: ${total}G , 使用: ${used}G , 剩余: ${available}G"
}
function disk(){

 fs=$(df -h |awk '/^\/dev/{print $1}')
    for p in $fs; do
        mounted=$(df -h |awk '$1=="'$p'"{print $NF}')
        size=$(df -h |awk '$1=="'$p'"{print $2}')
        used=$(df -h |awk '$1=="'$p'"{print $3}')
        used_percent=$(df -h |awk '$1=="'$p'"{print $5}')
        echo "硬盘 - 挂载点: $mounted , 总大小: $size , 使用: $used , 使用率: $used_percent"
    done

}
function tcp_status() {
    summary=$(ss -antp |awk '{status[$1]++}END{for(i in status) printf i":"status[i]" "}')
    echo "TCP连接状态 - $summary"
}
cpu
memory
disk
tcp_status
~~~

# 以sudo运行整个shell脚本

- 将 sudo 放在 shell 脚本的首中，会以 root 身份运行整个程序。 例如自动化系统升级或包管理器包装器——不再需要用 sudo 预先准备一切

```sh
#!/usr/bin/sudo /bin/bash
```

# 将视频转换为gif动图

- 需要系统安装 ffmpeg , ubuntu 中可以通过 `sudo apt install ffmpeg` 安装。

```sh
ffmpeg -ss 00:00:03 -t 3 -i test.mov -s 640x360 -r  15  dongtu.gif
```

- `-ss 00:00:03` 表示从第 `00` 分钟 `03` 秒开始制作 GIF，如果你想从第 9 秒开始，则输入 `-ss 00:00:09`，或者 `-ss 9`，支持小数点，所以也可以输入 `-ss 00:00:11.3`，或者 `-ss 34.6` 之类的，如果不加该命令，则从 0 秒开始制作； 
- `-t 3` 表示把持续 3 秒的视频转换为 GIF，你可以把它改为其他数字，例如 1.5，7 等等，时间越长，GIF 体积越大，如果不加该命令，则把整个视频转为 GIF； 
- `-i` 表示 invert； 
- test.mov 就是你要转换的视频，名称最好不要有中文，不要留空格，支持多种视频格式； 
- `-s 640x360` 是 GIF 的分辨率，视频分辨率可能是 1080p，但你制作的 GIF 可以转为 720p 等，允许自定义，分辨率越高体积越大，如果不加该命令，则保持分辨率不变； 
- `-r “15”` 表示帧率，网上下载的视频帧率通常为 24，设为 15 效果挺好了，帧率越高体积越大，如果不加该命令，则保持帧率不变；
- dongtu.gif：就是你要输出的文件，你也可以把它命名为 hello.gif 等等。

# 批量监控服务器磁盘使用率

~~~sh
#!/bin/bash  
HOST_INFO=host.info  
  
# 遍历host.info文件中的每个IP地址  
for IP in $(awk '/^[^#]/{print $1}' $HOST_INFO); do  
    # 根据IP地址获取对应的用户名和端口号  
    USER=$(awk -v ip=$IP 'ip==$1{print $2}' $HOST_INFO)  
    PORT=$(awk -v ip=$IP 'ip==$1{print $3}' $HOST_INFO)  
    TMP_FILE=/tmp/disk.tmp  
  
    # 通过SSH远程执行df -h命令，获取磁盘使用情况并保存到临时文件中  
    ssh -p $PORT $USER@$IP 'df -h' > $TMP_FILE  
  
    # 提取每个分区的名称和使用率，并判断是否超过阈值  
    USE_RATE_LIST=$(awk 'BEGIN{OFS="="}/^\/dev/{print $NF,int($5)}' $TMP_FILE)  
    for USE_RATE in $USE_RATE_LIST; do  
        PART_NAME=${USE_RATE%=*}  # 提取分区名称  
        USE_RATE=${USE_RATE#*=}   # 提取使用率  
        if [ $USE_RATE -ge 80 ]; then  # 判断使用率是否超过80%  
            echo "Warning: $PART_NAME Partition usage $USE_RATE% on server $IP!"  
        fi  
    done  
done
~~~

~~~sh
#host.info
172.16.183.75 root 22
172.16.183.76 root 22
~~~

# 使用rsync备份目录

- https://mp.weixin.qq.com/s/k-qOKIWHgfwngNG_YlylKA

~~~sh
#!/bin/bash

# 检查是否安装了rsync
if ! command -v rsync &> /dev/null; then
    echo "rsync 未安装。正在安装..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -x "$(command -v apt-get)" ]; then
            sudo apt-get update && sudo apt-get install -y rsync
        elif [ -x "$(command -v yum)" ]; then
            sudo yum install -y rsync
        elif [ -x "$(command -v dnf)" ]; then
            sudo dnf install -y rsync
        else
            echo "无法检测到合适的包管理器，请手动安装rsync。"
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        if ! command -v brew &> /dev/null; then
            echo "Homebrew 未安装。请先安装Homebrew。"
            exit 1
        fi
        brew install rsync
    else
        echo "不支持的操作系统，请手动安装rsync。"
        exit 1
    fi
    
    echo "rsync 安装完成。"
else
    echo "rsync 已安装。"
fi

#要备份的文件目录
read -p "请输入要备份的源目录: " BACKUP_SOURCE_DIR

# 获取当前时间和昨天的日期
NOW=$(date +%Y%m%d%H%M)
YESTERDAY=$(date -d "yesterday" +%Y%m%d)

# 配置备份系统存放的目录
BACKUP_HOME="/srv/backups"
CURRENT_LINK="$BACKUP_HOME/current"
SNAPSHOT_DIR="$BACKUP_HOME/snapshots"
ARCHIVES_DIR="$BACKUP_HOME/archives"

# 创建备份文件存放目录
mkdir -p "$SNAPSHOT_DIR" "$ARCHIVES_DIR" &> /dev/null

# 使用rsync进行备份
rsync -azH --link-dest="$CURRENT_LINK" "$BACKUP_SOURCE_DIR" "$SNAPSHOT_DIR/$NOW" \
&& ln -snf "$(ls -1d "$SNAPSHOT_DIR"/* | tail -n 1)" "$CURRENT_LINK"

# 归档
# 如果快照是昨天的，将其压缩归档
if [ $(ls -d "$SNAPSHOT_DIR"/"$YESTERDAY"* 2> /dev/null | wc -l) -ne 0 ]; then
  tar -czf "$ARCHIVES_DIR/$YESTERDAY.tar.gz" "$SNAPSHOT_DIR/$YESTERDAY"* \
  && rm -rf "$SNAPSHOT_DIR/$YESTERDAY"*
fi
~~~

# 创建指定大小的单个测试文件

```sh
dd if=/dev/zero of=testfile bs=1G count=200
```

# 创建多个指定大小的测试文件

```sh
#!/bin/bash

for i in {1..100}
do
   dd if=/dev/zero of=testfile$i bs=1M count=1
done
```

# 后台运行命令

## nohup

- `nohup`命令可以让你的程序在后台静默运行，即使你退出了终端。例如：

```sh
nohup cp /path/to/source /path/to/destination &
```

- `&`符号会让命令在后台运行。

- 使用`nohup`命令运行的程序，其标准输出和标准错误默认都会被重定向到一个名为`nohup.out`的文件中。所以，你可以通过检查这个文件来查看`cp`命令是否成功完成，以及是否有任何错误信息。

- 例如，你可以使用`tail`命令来查看`nohup.out`文件的最后几行：

```sh
tail nohup.out
tail -f -n 1 nohup.out #持续监控最后一行的输出
```

- 如果`cp`命令成功完成，那么`nohup.out`文件可能不会有任何输出。如果`cp`命令遇到错误，那么错误信息将会被写入`nohup.out`文件。

## screen

另一种方法是使用`screen`命令，它可以创建一个或多个shell会话，这些会话可以在后台运行，也可以在需要时恢复。例如，你可以这样使用`screen`命令：

```sh
screen
cp /path/to/source /path/to/destination
```

然后按`Ctrl+A`然后`D`来断开`screen`会话。你可以随时使用`screen -r`命令来恢复会话。
