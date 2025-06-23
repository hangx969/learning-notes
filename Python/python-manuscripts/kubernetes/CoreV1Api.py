from kubernetes import config, client
# 导入集群kubeconfig文件
config.load_kube_config(config_file='kubernetes/kubeconfig-local')
# 创建对象
v1 = client.CoreV1Api()

# 返回的是一个对象，包含所有ns的json属性
namespaces = v1.list_namespace()
# for ns in namespaces.items:
#     print(ns)

for ns in namespaces.items:
    # 打印每个ns的name
    print(ns.metadata.name)