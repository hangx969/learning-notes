# 前置条件

- 安装python（pycharm）

- 安装kubernetes包

  ~~~sh
  python -m pip install --upgrade pip
  pip install ignore-installed kubernetes
  ~~~

- 将master节点上的/root/.kube/config下载到本地

- 部署pod的yaml文件

  ~~~yaml
  apiVersion: v1
  kind: Pod
  metadata:
    name: po-nginx
    namespace: default
  spec:
    containers:
    - name: nginx
      image: nginx
      imagePullPolicy: IfNotPresent
  ~~~

- 部署deploy的yam文件

  ~~~yaml
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: dep-nginx
  spec:
    replicas: 2
    selector:
      matchLabels:
        app: myapp
        version: v1
    template:
      metadata:
        labels:
          app: myapp
          version: v1
      spec:
        containers:
        - name: nginx
          image: nginx
          imagePullPolicy: IfNotPresent
          ports:
          - containerPort: 80
  ~~~

# 查看资源

~~~python
import kubernetes
from kubernetes import client, config

config.kube_config.load_kube_config(config_file='E:\work\KEEP-WORKING\CS-Learning\python\python-k8s\config')

# 获取CoreV1API版本对象，是client.CoreV1Api()的实例，可以操作k8s中的资源对象。
v1 = client.CoreV1Api()

# 列出k8s中的所有名称空间
print("All ns:\n")
for namespace in v1.list_namespace().items:
    print(namespace.metadata.name)

# 列举所有名称空间下的所有service
print("all svc\n")
services = v1.list_service_for_all_namespaces()
for svc in services.items:
    print('%s \t%s \t%s \t%s \n' % (svc.metadata.namespace, svc.metadata.name, svc.spec.cluster_ip, svc.spec.ports))

# 列举所有名称空间下的pod资源
print("all pods:\n")
pods = v1.list_pod_for_all_namespaces()
for i in pods.items:
    print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

# client.AppsV1Api对象可以操作跟k8s中控制器相关资源对象，下面演示的是列举所有名称空间的deployment
v1_deploy = client.AppsV1Api()
deploys = v1_deploy.list_deployment_for_all_namespaces()
print("print deploy\n")
for i in deploys.items:
    print("%s\t%s\t%s" % (i.metadata.name, i.metadata.namespace, i.spec.replicas))

# 读取pod指定的属性
print("read pod:\n")
resp = v1.read_namespaced_pod(namespace='default', name='po-nginx')
print('read pod')
# print(resp)
print(resp.spec.containers[0])
print(resp.spec.containers[0].image)
~~~

# 创建deploy

~~~python
from os import path
import yaml
from kubernetes import client,config

def main():
    #读入集群信息
    config.load_kube_config(config_file='E:\work\KEEP-WORKING\CS-Learning\python\python-k8s\config')
    with open(path.join(path.dirname(__file__),"nginx-py.yaml")) as f:
        dep = yaml.safe_load(f)
        k8s_apps_v1 = client.AppsV1Api()
        resp = k8s_apps_v1.create_namespaced_deployment(body=dep, namespace='default')
        print('deployment created,name=%s'%(resp.metadata.name))

if __name__ == '__main__':
      main()
~~~

# 修改资源

~~~python
from os import path
import yaml
from kubernetes import client,config
def main():
    config.load_kube_config(config_file='E:\work\KEEP-WORKING\CS-Learning\python\python-k8s\config')
    k8s_core_v1=client.CoreV1Api()
    #原image为nginx
    old_resp=k8s_core_v1.read_namespaced_pod(namespace='default',name='po-nginx')
    #修改镜像为busybox
    old_resp.spec.containers[0].image='busybox'
    #patch pod
    new_resp=k8s_core_v1.patch_namespaced_pod(namespace='default',name='po-nginx',body=old_resp)
    print(new_resp.spec.containers[0].image)
        
if __name__=='__main__':
    main()
~~~

# 删除资源

~~~python
from os import path
import yaml
from kubernetes import client,config

def main():
    config.load_kube_config(config_file='E:\work\KEEP-WORKING\CS-Learning\python\python-k8s\config')
    k8s_core_v1=client.CoreV1Api()
    resp=k8s_core_v1.delete_namespaced_pod(namespace='default',name='po-nginx')
    print('delete pod')
    
if __name__=='__main__':
    main()
~~~



