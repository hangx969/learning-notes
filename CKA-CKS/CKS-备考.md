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

## Answer

- 文档:kubernetes.io --> documentation --> 搜apparmor

~~~sh
kubectl config use-context KSSH00401
#先去工作节点，查看apparmor配置文件
sudo kubectl get nodes
ssh kssh00401-worker1
sudo -i
cat /etc/apparmor.d/nginx_apparmor 
#...
profile nginx-profile  flags=(attach_disconnected) {
#... profile后面的nginx-profile是这个配置的名称，
#后面apparmor_status | grep nginx-profile 要用到
#yaml文件的annotations也要用到

#安静模式（不输出信息）加载或更新名为 nginx_apparmor 的 AppArmor 配置文件
apparmor_parser -q /etc/apparmor.d/nginx_apparmor 
#查看apparmor配置文件是否生效(profile的名字是在nginx_apparmor文件里面定义的)
apparmor_status
#exit退出工作节点，回到控制节点部署pod

kubectl config use-context KSSH00401
sudo vim /home/candidate/KSSH00401/nginx-deploy.yaml 
#新增deploy.spec.template.metadata.annotqations。
annotations:
  container.apparmor.security.beta.kubernetes.io/hello: localhost/nginx-profile
  ##hello是pod里container的名称，nginx-profile是apparmor_status解析出来的结果

sudo kubectl apply -f /home/candidate/KSSH00401/nginx-deploy.yaml
~~~

> 注意：
>
> - cat /etc/apparmor.d/nginx_apparmor配置文件中查看profile的名称
> - yaml文件中的deployments.spec.template.metadata.annotations中写annotation
> - annotation中的container name记得要改

# 2 kube-bench基准测试

## kube-bench介绍

- kube-Bench是一款针对Kubernetes的安全检测工具

## Task

- context：针对kubeadm创建的cluster运行CIS基准测试工具时，发现了多个必须解决的问题。


- task：通过配置修复所有问题并重新启动受影响的组件以确保新设置生效。

- 修复针对kubelet发现的所有以下违规行为

  - Ensure  that the  anonymous-auth argument  is set to false  

  - Ensure  that the  -authorization-mode argument  is  not set to AlwaysAllow 

- 尽可能使用Webhook 身份验证/授权

- 修复针对etcd发现的以下违规行为：

  - Ensure  that the  --client-cert-auth argument  is set to true

## Answer

- 官网搜索：authorization

~~~sh
#切换到指定集群节点
kubectl config use-context KSSH00201
sudo kubectl get nodes
ssh kscs00201-master
sudo -i
~~~

- 修改master节点kubelet文件

~~~sh
#master节点上，编辑kubelet文件来配置以上参数
vim /var/lib/kubelet/config.yaml 
~~~

- 原始文件如下：

~~~yaml
#原始文件内容如下：
apiVersion: kubelet.config.k8s.io/v1beta1
authentication:
  anonymous:
    enabled: true
  webhook:
    cacheTTL: 0s
    enabled: false
  x509:
    clientCAFile: /etc/kubernetes/pki/ca.crt
authorization:
  mode: AlwaysAllow
  webhook:
    cacheAuthorizedTTL: 0s
    cacheUnauthorizedTTL: 0s
cgroupDriver: systemd
#.........
~~~

- 修改后内容如下：

~~~yaml
apiVersion: kubelet.config.k8s.io/v1beta1
authentication:
  anonymous:
    enabled: false #改为false
  webhook:
    cacheTTL: 0s
    enabled: true #改为true
  x509:
    clientCAFile: /etc/kubernetes/pki/ca.crt
authorization:
  mode: Webhook #改为Webhook
#......
~~~

~~~sh
#修改完重启kubelet
systemctl restart kubelet
~~~

- 修改工作节点kubelet文件，修改内容同master节点。

~~~sh
#修改完重启kubelet
systemctl restart kubelet
~~~

- 修改master节点etcd

~~~sh
ssh kscs00201-master
sudo -i
vim /etc/kubernetes/manifests/etcd.yaml
#containers.command下面新增以下参数
- --client-cert-auth=true
~~~

- 修改完重启kubelet

~~~sh
systemctl restart kubelet
kubectl get nodes
#这个过程比较慢，估计需要几分钟才可以启动
~~~

> 注意：
>
> - 这个字段可能默认没有，需要自己添加，考试的时候自己注意下
>
> ~~~yaml
> webhook:
>   cacheTTL: 0s
>   enabled: true
> ~~~
>
> - 背过kubelet和etcd配置文件的路径：
>   - kubelet：/var/lib/kubelet/config.yaml 
>   - etcd: /etc/kubernetes/manifests/etcd.yaml

# 3 Trivy镜像扫描

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

