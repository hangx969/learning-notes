# kubernetes模块

Kubernetes 模块（kubernetes）是一个 Python 客户端库，用于与 Kubernetes 集群进行交互。通过这个模块，你可以在 Python 脚本中管理 Kubernetes 资源，对各种资源进行增删改查。

Kubernetes 模块操作 k8s 集群需要了解的一些基础概念：

1. Kubernetes API
   - kubernetes 模块使用 `Kubernetes API` 来管理集群资源。Kubernetes API 提供了对集群中各种资源（如Pods、Nodes、Services 等）的 CRUD操作。
   - `kubectl api-resources`可以查看所有api资源：
     - apiVersion为`v1`的是**集群核心资源**，`apps/v1`的是**应用程序资源**

2. 集群client配置文件
   - Kubernetes 配置文件用于存储集群的连接信息。它通常位于 k8s 控制节点的~/.kube/config，你可以通过 config_file 参数指定其他位置。
   - kubectl客户端，先通过`$KUBECONFIG`环境变量查找kubeconfig文件位置，没找到的话，去`~/.kube/config/`目录下找kubeconfig文件
3. kubernetes模块核心方法
   - `CoreV1Api`: 封装了与v1 api交互的功能。主要用于管理 k8s 集群的核心资源，如 Pods、Services、Nodes 等。
   - `AppsV1Api`: 封装了与apps/v1 api交互的功能。用于管理 k8s 应用程序资源，如 Deployments、StatefulSets 等。

## 使用k8s api操作资源的优势

1. 在开发环境中，部署服务可能很简单，只需手动修改 YAML 文件。但在生产环境中，需要根据流量波动动态扩展 pod 分副本数、根据不同的名称空间更新镜像版本号，或者需要根据不同的环境（开发、测试、生产）修改 pod 副本数，编写 API 代码可以轻松实现这些自动化需求。
2. 代码可以加“如果…那么…”的判断，或者循环去做很多重复的操作。YAML 文件只是配置，不能处理这种复杂逻辑
3. 用代码调用 API 时，遇到错误可以直接捕获并处理，比如资源不可用时自动重试。而 YAML 文件出错时，需要等到执行才知道问题，调试起来慢。
4. 代码可以放进版本管理工具（比如 Git），不同版本可以灵活管理。你还可以把常用的操作写成函数，重复使用，而 YAML 文件要手动复制粘贴。

## 安装

~~~python
pip3 install kubernetes
# 清华源速度更快
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple kubernetes
~~~

## 基本配置

### 导入模块

~~~python
from kubernetes import client, config
~~~

从 Kubernetes 库中导入 client 和 config 模块。它的作用如下：
1. kubernetes：
  - 通过 kubernetes 库，你可以使用 Python 脚本与 Kubernetes API 进行交互，以便管理和操作 Kubernetes 集群中的各种资源（如 Pods、Services、Deployments 等）。
2. client：
  - client 模块包含 Kubernetes API 的具体类和方法，这些类用于与Kubernetes API 交互。
  - 例如，CoreV1Api 就是 client 模块中的一个类，通过它可以操作 Kubernetes 的核心资源（如 Pods、Services 等）。
3. config：
  - config 模块用于处理 Kubernetes 客户端的配置信息，主要是用于加载Kubernetes 集群的连接配置。它帮助你的脚本找到并连接到正确的 Kubernetes 集群。
  - 例如，`config.load_kube_config()` 用于加载本地的 kubeconfig 文件（通常位于 `~/.kube/config`），使 Python 脚本能够连接到你本地配置的 Kubernetes集群。
  - 如果是在集群内运行，你可以使用 `config.load_incluster_config()`，它会自动加载集群内部的认证信息（直接去本机器的`~/.kube/config`找）。
### 加载配置文件
1. 如果你的 config 文件放在默认位置（~/.kube/config），可以这样加载：`config.load_kube_config()`
2. 如果config文件需要指定路径：`config.load_kube_config(config_file='D:/config')`

# 常用操作

## 获取所有api资源get_api_resources()

~~~python
from kubernetes import config, client
# 导入集群kubeconfig文件
config.load_kube_config(config_file='kubernetes/kubeconfig-local')
# 创建对象
v1 = client.CoreV1Api()

# 获取所有api资源
print(v1.get_api_resources())
~~~

## 获取节点列表list_node()

~~~python
from kubernetes import config, client
# 导入集群kubeconfig文件
config.load_kube_config(config_file='kubernetes/kubeconfig-local')
# 创建对象
v1 = client.CoreV1Api()

# 获取所有节点列表
# 返回的是一个V1NodeList对象，包含所有node详细信息，metadata、statua等
nodes = v1.list_node()

# nodes.items是一个V1Node对象，包含某个node的信息
for node in nodes.items:
    # node.metadata.name获取到这个node的name属性值。层级路径和yaml文件中的层级路径一样
    print(f"Node name: {node.metadata.name}")
~~~

## pod操作

### 获取所有ns下的pod

~~~python
from kubernetes import config, client

# 导入集群kubeconfig文件
config.load_kube_config(config_file='kubernetes/kubeconfig-local')

# 创建对象
v1 = client.CoreV1Api()

pods = v1.list_pod_for_all_namespaces()
for pod in pods.items:
    print(f"Pod name: {pod.metadata.name}, ns: {pod.metadata.namespace}")
~~~

### 创建pod

~~~python
from kubernetes import config, client

# 导入集群kubeconfig文件
config.load_kube_config(config_file='kubernetes/kubeconfig-local')

# 创建client对象以获取其中的方法
v1 = client.CoreV1Api()
# 构造pod对象
pod = client.V1Pod(
    metadata = client.V1ObjectMeta(name='mypod',labels={'app':'my-app'}),
    spec = client.V1PodSpec(
        containers = [client.V1Container(
            name = 'my-container',
            image = 'busybox:latest',
            image_pull_policy = 'IfNotPresent',
            command=['sh','-c','sleep 60000']
        )]
    )
)
# 把构造好的pod对象传给方法
v1.create_namespaced_pod(namespace='default',body=pod)
~~~

### 更新和删除pod

~~~python
from kubernetes import config, client

# 导入集群kubeconfig文件
config.load_kube_config(config_file='kubernetes/kubeconfig-local')

# 创建对象
v1 = client.CoreV1Api()

# 获取到V1Pod对象
pod = v1.read_namespaced_pod(name='mypod',namespace='default')
# 修改pod对象的image字段
pod.spec.containers[0].image = 'busybox:1.28'
# 发送修改后的对象来更新pod
v1.replace_namespaced_pod(name='mypod',namespace='default',body=pod)
# 删除pod
v1.delete_namespaced_pod(name='mypod', namespace='default')
~~~

### 案例：动态获取pod信息

~~~python
from kubernetes import config, client
import time

# 导入集群kubeconfig文件
config.load_kube_config(config_file='kubernetes/kubeconfig-local')
# 创建对象
v1 = client.CoreV1Api()

while True:
    pods = v1.list_pod_for_all_namespaces()
    for pod in pods.items:
        print(f"Pod Name: {pod.metadata.name} - Status: {pod.status.phase}")
    time.sleep(60)
~~~

### 案例：批量创建多个pod

~~~python
from kubernetes import config, client
import time

# 导入集群kubeconfig文件
config.load_kube_config(config_file='kubernetes/kubeconfig-local')

# 创建对象
v1 = client.CoreV1Api()
# 用for循环创建pod
for i in range(5):
    pod = client.V1Pod(
        metadata=client.V1ObjectMeta(name=f'my-pod-{i}'),
        spec=client.V1PodSpec(
            containers=[client.V1Container(
                name=f'my-container-{i}',
                image='busybox:1.28',
                command=['sh','-c','sleep 6000']
            )]
        )
    )
    # 创建pod
    v1.create_namespaced_pod(namespace='default',body=pod)
~~~

### 案例：获取pod日志

~~~python
from kubernetes import config, client
import time

# 导入集群kubeconfig文件
config.load_kube_config(config_file='kubernetes/kubeconfig-local')

# 创建对象
v1 = client.CoreV1Api()

pod_name = 'loki-0'
namespace = 'monitoring'

pod_log = v1.read_namespaced_pod_log(name=pod_name,namespace=namespace)
print(pod_log)
~~~

## service操作

### 创建service

~~~python
from kubernetes import config, client
# 导入集群kubeconfig文件
config.load_kube_config(config_file='kubernetes/kubeconfig-local')
# 创建client对象
v1 = client.CoreV1Api()
# 创建service对象
service = client.V1Service(
    metadata = client.V1ObjectMeta(name='my-service'),
    spec = client.V1ServiceSpec(
        selector = {'app':'my-app'},
        ports = [client.V1ServicePort(port=80,target_port=80)],
        type = 'ClusterIP'
    )
)

v1.create_namespaced_service(namespace='default',body=service)
~~~

### 列出所有service

~~~python
from kubernetes import config, client
# 导入集群kubeconfig文件
config.load_kube_config(config_file='kubernetes/kubeconfig-local')
# 创建对象
v1 = client.CoreV1Api()

services = v1.list_service_for_all_namespaces()
for svc in services.items:
    print(f"service name: {svc.metadata.name} - namespace: {svc.metadata.namespace}")
~~~

## deployment操作

### 创建deployment

~~~python
from kubernetes import client, config
# 导入集群kubeconfig文件
config.load_kube_config(config_file='kubernetes/kubeconfig-local')
# 创建对象
appsv1 = client.AppsV1Api()
# 构造对象时，一般而言字符串类型是可以直接赋值的，对象或对象列表类型就需要用client.V1xxx方法来赋值
dep = client.V1Deployment(
    metadata=client.V1ObjectMeta(name='my-deployment'),
    spec=client.V1DeploymentSpec(
        replicas=1,
        selector=client.V1LabelSelector(
            match_labels={'app':'my-app-1'}
        ),
        template=client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={'app':'my-app-1'}),
            spec=client.V1PodSpec(
                containers=[client.V1Container(
                    name='my-container',
                    image='busybox:1.28',
                    image_pull_policy='IfNotPresent',
                    command=['sh','-c','sleep 6000'],
                    ports=[client.V1ContainerPort(container_port=80)]
                )]
            )
        )
    )
)

appsv1.create_namespaced_deployment(namespace='default',body=dep)
~~~

### 更新deployment

~~~python
from kubernetes import client, config
# 导入集群kubeconfig文件
config.load_kube_config(config_file='kubernetes/kubeconfig-local')
# 创建对象
appsv1 = client.AppsV1Api()

# 读取现有deployment
dep = appsv1.read_namespaced_deployment(name='my-deployment',namespace='default')
dep.spec.template.spec.containers[0].image = 'busybox:latest'
appsv1.patch_namespaced_deployment(name='my-deployment',namespace='default',body=dep)
~~~

### 删除deployment

~~~python
from kubernetes import client, config
# 导入集群kubeconfig文件
config.load_kube_config(config_file='kubernetes/kubeconfig-local')
# 创建对象
appsv1 = client.AppsV1Api()
# 删除
appsv1.delete_namespaced_deployment(name='my-deployment',namespace='default')
~~~

## statefulset操作

### 创建statefulset

~~~python
from kubernetes import client, config
# 导入集群kubeconfig文件
config.load_kube_config(config_file='kubernetes/kubeconfig-local')
# 创建对象
appsv1 = client.AppsV1Api()

# 定义sts对象
sts = client.V1StatefulSet(
    metadata=client.V1ObjectMeta(name='my-sts'),
    spec=client.V1StatefulSetSpec(
        replicas=1,
        service_name='my-svc-1',
        selector=client.V1LabelSelector(
            match_labels={'app':'my-app-2'}
        ),
        template=client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={'app':'my-app-2'}),
            spec=client.V1PodSpec(
                containers=[client.V1Container(
                    name='my-container',
                    image='busybox:1.28',
                    image_pull_policy='IfNotPresent',
                    command=['sh','-c','sleep 6000'],
                    ports=[client.V1ContainerPort(container_port=8080)]
                )]
            )
        )
    )
)

# 创建sts之前需要先创建好svc
# 创建client对象
v1 = client.CoreV1Api()
# 创建service对象
service = client.V1Service(
    metadata = client.V1ObjectMeta(name='my-svc-1'),
    spec = client.V1ServiceSpec(
        selector = {'app':'my-app-2'},
        ports = [client.V1ServicePort(port=80,target_port=80)],
        type = 'ClusterIP'
    )
)

# 创建service
v1.create_namespaced_service(namespace='default',body=service)
# 创建sts
appsv1.create_namespaced_stateful_set(namespace='default',body=sts)
~~~

### 更新statefulset

~~~python
from kubernetes import client, config
# 导入集群kubeconfig文件
config.load_kube_config(config_file='kubernetes/kubeconfig-local')
# 创建对象
appsv1 = client.AppsV1Api()
# 读取sts资源
sts = appsv1.read_namespaced_stateful_set(name='my-sts',namespace='default')
# 把sts对象的image改掉
sts.spec.template.spec.containers[0].image = 'busybox:latest'
# 把修改后的sts对象更新过去
appsv1.patch_namespaced_stateful_set(name='my-sts',namespace='default',body=sts)
~~~

### 删除statefulset

~~~python
from kubernetes import client, config
# 导入集群kubeconfig文件
config.load_kube_config(config_file='kubernetes/kubeconfig-local')
# 创建对象
appsv1 = client.AppsV1Api()
# 读取sts资源
appsv1.delete_namespaced_stateful_set(name='my-sts',namespace='default')
~~~

## configMap操作

### 创建configMap

~~~python
from kubernetes import client, config
# 导入集群kubeconfig文件
config.load_kube_config(config_file='kubernetes/kubeconfig-local')
# 创建对象
v1 = client.CoreV1Api()

cm = client.V1ConfigMap(
    metadata=client.V1ObjectMeta(name='my-cm'),
    data={'key':'value'}
)

v1.create_namespaced_config_map(namespace='default',body=cm)
# 读取configMap中的数据
config_map = v1.read_namespaced_config_map(name='my-cm',namespace='default')
print(config_map.data)
~~~

### 更新和删除configMap

~~~python
from kubernetes import client, config
# 导入集群kubeconfig文件
config.load_kube_config(config_file='kubernetes/kubeconfig-local')
# 创建对象
v1 = client.CoreV1Api()

# 读取configMap
config_map = v1.read_namespaced_config_map(name='my-cm',namespace='default')

# 更新configMap，key值不同，会自动追加一个键值对进去。
config_map.data={'key1':'value1'}
v1.patch_namespaced_config_map(name='my-cm',namespace='default',body=config_map)

# 也可以这样更新
updated_cm = client.V1ConfigMap(
    data={'key2':'value2'}
)
v1.patch_namespaced_config_map(name='my-cm',namespace='default',body=updated_cm)

# 删除configMap
v1.delete_namespaced_config_map(name='my-cm',namespace='default')
~~~



# 案例：根据不同ns更新pod副本数

假设在 k8s 集群中有三个名称空间，qatest、devlopment、production，这三个名称空间有三个 deployment 资源，叫做 my-deployment，我想要对 my-deployment 的 pod 副本数进行修改，如果对应的 my-deployment 存在，直接修改，不存在，创建新的 my-
deployment。

## 版本1

处理用户输入时，如果用户输出错误，程序退出

~~~python
from kubernetes import client, config
# 导入集群kubeconfig文件
config.load_kube_config(config_file='kubernetes/kubeconfig-local')
# 创建对象
appsv1 = client.AppsV1Api()

# 定义ns列表
valid_ns = ['qatest','development','production']

# 处理用户输入ns
ns = input(f'Please Input Namespace, options: {','.join(valid_ns)}\n')
if ns not in valid_ns:
    print(f"Invalid ns: {ns}, please re-input.")
    exit(1) # 结束程序

# 处理用户输入副本数
try:
    replicas = int(input('Please input replicas:\n'))
except ValueError:
    print("Invalid input, please input an int.")
    exit(1)

try:
    dep = appsv1.read_namespaced_deployment(name='my-deployment',namespace=ns)
    dep.spec.replicas = replicas
    appsv1.patch_namespaced_deployment(name='my-deployment',namespace=ns,body=dep)
    print(f"Deployment 'my-deployment' in namespace {ns} has been updated to new replicas {replicas}.")

except client.exceptions.ApiException as e:
    # 处理deployment在ns中不存在的情况
    if e.status == 404:
        # deployment不存在，直接创建新的deployment
        # 先构造deployment对象
        new_dep = client.V1Deployment(
            metadata=client.V1ObjectMeta(name='my-deployment'),
            spec=client.V1DeploymentSpec(
                replicas=replicas, # 这里是用户输入的副本数
                selector=client.V1LabelSelector(
                    match_labels={'app':'my-app-1'}
                ),
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(labels={'app':'my-app-1'}),
                    spec=client.V1PodSpec(
                        containers=[client.V1Container(
                            name='my-container',
                            image='busybox:1.28',
                            image_pull_policy='IfNotPresent',
                            command=['sh','-c','sleep 3600'],
                            ports=client.V1ContainerPort(container_port=8080)
                        )]
                    )
                )
            )
        )
        # 创建新的deployment
        appsv1.create_namespaced_deployment(namespace=ns,body=new_dep)
        print(f"Deployment 'my-deployment' has been created in namespace {ns}, with replicas {replicas}.")
    # 不是404说明有其他报错，直接输出报错
    else:
        print(f"Error occurred: {e.reason}")
~~~

> 注意kubernetes的client模块在处理异常时，用的是：`except client.exceptions.ApiException as e`，里面可以用`e.status`获取错误返回码，`e.reason`获取错误信息。

## 版本2

用户输入部分可以改进：

1. 循环输入: 使用 while True 实现持续的输入，直到用户输入 'exit' 结束程序。
2. 异常处理: 在副本数输入错误时，允许用户重新输入，并提供退出选项。
3. 用户体验优化: 增加了对用户主动退出的友好提示，并确保每个输入步骤有相应的反馈。

~~~python
from kubernetes import client, config
# 导入集群kubeconfig文件
config.load_kube_config(config_file='kubernetes/kubeconfig-local')
# 创建对象
appsv1 = client.AppsV1Api()

# 定义ns列表
valid_ns = ['qatest','development','production']

while True:
    # 处理用户输入ns
    ns = input(f"Please Input Namespace, options: {','.join(valid_ns)}, enter 'exit' to exit.\n")
    if ns.lower() == 'exit':
        print("Exited.\n")
        break
    if ns.lower() not in valid_ns:
        print(f"Invalid namespace {ns}, please re-enter.\n")
        continue

    # 处理用户输入副本数，有两种方案，一种用if判断，一种用try...except捕获错误
    
    # replicas = input("Please input replicas, enter 'exit' to exit\n")
    # if replicas.lower() == 'exit':
    #     print("Exited")
    #     break
    # if not replicas.isdigit():
    #     print("Replicas is not valid, please re-enter.\n")
    #     continue

    try:
        replicas = int(input("Please input replicas.\n"))
    except ValueError:
        if input("Replicas is not valid, enter 'exit' to exit, or press 'Enter' to continue.\n").lower() == 'exit':
            print("Exited.\n")
            break
        continue

    # 处理更新replicas逻辑
    try:
        dep = appsv1.read_namespaced_deployment(name='my-deployment',namespace=ns)
        dep.spec.replicas = int(replicas)
        appsv1.patch_namespaced_deployment(name='my-deployment',namespace=ns,body=dep)
        print(f"Deployment 'my-deployment' in namespace {ns} has been updated to new replicas {replicas}.")

    except client.exceptions.ApiException as e:
        # 处理deployment在ns中不存在的情况
        if e.status == 404:
            # deployment不存在，直接创建新的deployment
            # 先构造deployment对象
            new_dep = client.V1Deployment(
                metadata=client.V1ObjectMeta(name='my-deployment'),
                spec=client.V1DeploymentSpec(
                    replicas=int(replicas), # 这里是用户输入的副本数
                    selector=client.V1LabelSelector(
                        match_labels={'app':'my-app-1'}
                    ),
                    template=client.V1PodTemplateSpec(
                        metadata=client.V1ObjectMeta(labels={'app':'my-app-1'}),
                        spec=client.V1PodSpec(
                            containers=[client.V1Container(
                                name='my-container',
                                image='busybox:1.28',
                                image_pull_policy='IfNotPresent',
                                command=['sh','-c','sleep 3600'],
                                ports=client.V1ContainerPort(container_port=8080)
                            )]
                        )
                    )
                )
            )
            # 创建新的deployment
            appsv1.create_namespaced_deployment(namespace=ns,body=new_dep)
            print(f"Deployment 'my-deployment' has been created in namespace {ns}, with replicas {replicas}.")
        # 不是404说明有其他报错，直接输出报错
        else:
            print(f"Error occurred: {e.reason}")
~~~
