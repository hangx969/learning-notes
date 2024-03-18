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

