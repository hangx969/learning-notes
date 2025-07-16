# yaml文件

## 语法格式

YAML：标记语言

- --- 表示新的YAML文件的开始，声明两段配置放到一个文件里也用 --- 分隔
- 以空格为缩进，表示层级关系。（不能使用Tab）开头缩进两个空格
- : 后面要加一个空格
- \# 表示注释

## 数据类型

1. 纯量：单个值 

```yaml
c1: True
c2: ~
```

- 日期类型：ISO 8601格式

2. 数组

```yaml
address:
- Beijing
- Shenzhen
```

3. 对象：一系列属性

```yaml
heima: 
 age: 15
 address: Beijing
```

4. 对象列表

   containers  **<[]Object>** -required-
   List of containers belonging to the pod. Containers cannot currently be added or removed. There must be at least one container in a Pod. Cannot be updated.

   - 下级是一个一个的对象，以横线 - 开头，对齐containers。

   ```yaml
   containers:
   - name: tomcat-java
     image: xianchao/tomcat-8.5-jre8:v1
     imagePullPolicy: IfNotPresent
     ports: #ports也是对象列表
     - containerPort: 8080  #容器暴露的端口
   ```

5. map - 键值对

   ```yaml
   labels:
    key1: value1
    key2: value2
   ```


# POD yaml文件

> kubectl explain pod 查看pod的yaml文件写法。

## 一级属性

- apiVersion：k8s内部定义，用kubectl api-versions 查询
- kind：资源类型，查看：kubectl api-resources
- Metadata <object>：元数据，描述这个资源，常用的是name，namespace，labels，annotation等。
  - 用Annotation来记录的信息包括：build信息、release信息、Docker镜像信息等，例如时间戳、release id号、镜像hash值、docker registry地址等；日志库、监控库、分析库等资源库的地址信息；程序调试工具信息，例如工具名称、版本号等；团队的联系信息，例如电话号码、负责人名称、网址等。

- Spec <object>: specification，描述，是对各种资源配置的详细描述
- Status <object>: 内容无需定义，k8s自动生成

## spec子属性

- Containers 数组：容器的详细信息

  ![image-20231026205427484](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310262054540.png)

- imagePullPolicy:
  - Always：总是从远程仓库下载。
  - IfNotExist：本地有就用本地，否则远程仓库下载。
  - Never：只用本地镜像，本地没有就报错。
- Command：启动镜像的时候执行的命令
  - eg：busybox并不是一个程序，而是一个工具类的集合，k8s集群启动管理后，由于没有前台进程阻塞，会自动关闭，解决方法就是让其一直在运行。
  - 解决：用command写一个死循环来执行，就可以一直执行了。
  - 查看：进入容器内部看这个文件：`kubectl exec pod-command -n dev -it -c busybox /bin/sh`
- args：
  - 特别说明：通过上面发现command已经可以完成启动命令和传递参数的功能，为什么这里还要提供一个args选项，用于传递参数呢?这其实跟docker有点关系，kubernetes中的command、args两项其实是实现覆盖Dockerfile中ENTRYPOINT的功能。

 1、如果command和args均没有写，那么用Dockerfile的配置。

 2、如果command写了，但args没有写，那么Dockerfile默认的配置会被忽略，执行输入的command

 3、如果command没写，但args写了，那么Dockerfile中配置的ENTRYPOINT的命令会被执行，使用当前args的参数

 4、如果command和args都写了，那么Dockerfile的配置被忽略，执行command并追加上args参数

- Env: 设置环境变量，但是不推荐，推荐单独放到一个配置文件里面
- port：
  - containerPort：容器监听的端口
  - hostport：容器端口映射到主机上的端口，如果设置，主机上只能运行一个容器的副本（其他的副本映射过来就端口冲突了），所以一般不设置。
  - 访问程序要使用pod ip:container port （集群内部访问）
- resources：资源配额。
  - limits：限制容器运行的最大占用资源，一旦超过就会自动重启
  - requests：规定下限。下限的意思是只有占**用的资源到了下限才能启动**。否则会是pending状态
- nodeSelector 键值对：根据键值对定义的信息，将pod调度到这些label的node上

## 常用字段含义

![image-20240725224115645](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202407252241732.png)

# kubectl apply --server-side

- kubectl apply默认是client side apply和server side apply。
  - 不指定任何参数时是client-side apply，字段比较在客户端完成。
  - 可以指定`kubectl apply --server-side`使部署成为server side apply
  - 具体：https://juejin.cn/post/7173328614644006942，https://kubernetes.io/docs/reference/using-api/server-side-apply/

# kubectl create -f --dry-run=client

- 快速生成yaml文件：`kubectl create deploy nginx -n nginx --image=xxx:xxx --dry-run=client -o yaml > nginx.yaml`