from kubernetes import config, client
# 导入集群kubeconfig文件
config.load_kube_config(config_file='kubernetes/kubeconfig-local')
# 创建对象
v1 = client.CoreV1Api()

services = v1.list_service_for_all_namespaces()
for svc in services.items:
    print(f"service name: {svc.metadata.name} - namespace: {svc.metadata.namespace}")