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

# 查看磁盘目录使用情况

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

