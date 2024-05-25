# 1 AppArmor

## AppArmor介绍

- k8s文档：https://kubernetes.io/docs/tutorials/security/apparmor/
- AppArmor官网：https://wiki.ubuntu.com/AppArmor/
- AppArmor（Application Armor）是一种在Linux环境中用于增强系统安全的软件。它通过使用Linux内核的安全模块（LSM）来限制程序的能力，防止系统受到恶意软件或者非授权操作的影响。AppArmor通过定义一套简单的配置文件来指定程序能够访问哪些文件和功能。这种机制被称为强制访问控制（MAC），它与传统的基于用户权限的访问控制（DAC）不同，可以更精细地控制应用程序的行为，提高系统的安全性。与SELinux相比，AppArmor的策略更加简洁易懂，易于配置和管理。
- AppArmor的策略通常定义在 /etc/apparmor.d/ 目录下，每个策略文件对应一个程序，通过规定哪些文件路径可以访问以及可执行哪些操作（如读取、写入、执行、打开网络端口等）来控制程序的行为。目前Apparmor已经整合到了Linux 2.6内核中，Ubuntu系统自带Apparmor。
- Apparmor两种工作模式：
  - Enforcement：配置文件中列出的限制条件会被执行，并对于违反条件的程序进行日志记录
  - Complain：只监控行为并记录到日志中，并不会实际阻止程序的执行。

- 配置文件位置：/etc/apparmor.d目录下
- 访问控制：
  - r(read) \ w(write) \ a(append) \ k(file locking mode) \ l(link mode)
  - 在配置文件中的写法：`/tmp r` 表示对/tmp下的文件可以读取。（没在配置文件中列出的文件，程序是不能访问的）
- 资源限制
  - `set rlimit as<=1M` (限制使用的虚拟内存)
- 网络限制
  - network `\[\[domain]\[type]\[protocol]]`
  - 允许对所有网络进行操作：`network,`
  - 允许在IPv4下使用TCP协议：`network inet tcp.`


## Task

- 在cluster的工作节点上，实施位于/etc/apparmor.d/nginx_apparmor的现有的apparmor配置文件。编辑位于/home/candidate/KSSH00401/nginx-deploy.yaml的现有清单文件以应用AppArmor配置文件。最后，应用清单文件并创建其中指定的Pod。

~~~sh
kubectl config use-context KSSH00401
#先去工作节点，查看apparmor配置文件
sudo kubectl get nodes
ssh kssh00401-worker1
sudo -i
sudo apparmor_parser -q /etc/apparmor.d/nginx_apparmor 
#加载apparmor配置文件
sudo apparmor_status
#exit退出工作节点，回到控制节点部署pod
kubectl config use-context KSSH00401
sudo vim /home/candidate/KSSH00401/nginx-deploy.yaml 
#新增annotqation：
annotations:
  container.apparmor.security.beta.kubernetes.io/hello: localhost/nginx-profile
  ##hello是pod里container的名称，nginx-profile是apparmor_status解析出来的结果

sudo kubectl apply -f /home/candidate/KSSH00401/nginx-deploy.yaml
~~~

# 2 kube-bench基准测试

## kube-bench介绍

- 

## Task

~~~sh
~~~

# 3

## 介绍

- 

## Task

~~~sh

~~~

# 4

## 介绍

- 

## Task

~~~sh

~~~

# 5

## 介绍

- 

## Task

~~~sh

~~~

# 6

## 介绍

- 

## Task

~~~sh

~~~

# 7

## 介绍

- 

## Task

~~~sh

~~~

# 8

## 介绍

- 

## Task

~~~sh

~~~

# 9

## 介绍

- 

## Task

~~~sh

~~~

# 10

## 介绍

- 

## Task

~~~sh

~~~

# 11

## 介绍

- 

## Task

~~~sh

~~~

# 12

## 介绍

- 

## Task

~~~sh

~~~

