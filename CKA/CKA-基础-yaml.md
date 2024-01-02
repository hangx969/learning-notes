# yaml文件

## 语法格式

YAML：标记语言

- --- 表示新的YAML文件的开始，声明两段配置放到一个文件里也用 --- 分隔
- 以空格为缩进，表示层级关系。（不能使用Tab）开头缩进两个空格
- : 后面要加一个空格
- \# 表示注释

## 数据类型：

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

## 一级属性：

- apiVersion：k8s内部定义，用kubectl api-versions 查询
- kind：资源类型，查看：kubectl api-resources
- Metadata <object>：元数据，描述这个资源，常用的是name，namespace，labels，annotation等。
  - 用Annotation来记录的信息包括：build信息、release信息、Docker镜像信息等，例如时间戳、release id号、镜像hash值、docker registry地址等；日志库、监控库、分析库等资源库的地址信息；程序调试工具信息，例如工具名称、版本号等；团队的联系信息，例如电话号码、负责人名称、网址等。

- Spec <object>: specification，描述，是对各种资源配置的详细描述
- Status <object>: 内容无需定义，k8s自动生成

## spec子属性：

- Containers 数组：容器的详细信息

  ![image-20231026205427484](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310262054540.png)