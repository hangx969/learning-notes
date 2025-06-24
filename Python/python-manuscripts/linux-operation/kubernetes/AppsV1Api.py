from kubernetes import client, config

def scale_deploy(deploy_name, new_replicas):
    # 导入集群kubeconfig文件
    config.load_kube_config(config_file='kubernetes/kubeconfig-local')
    # 创建对象
    appsv1 = client.AppsV1Api()
    # 读取deployment信息
    deployment = appsv1.read_namespaced_deployment(name=deploy_name, namespace='default')
    # 修改副本数
    deployment.spec.replicas = new_replicas
    appsv1.patch_namespaced_deployment(name=deploy_name,namespace='default',body=deployment)

if __name__ == '__main__':
    current_traffic = get_traffic() # 假设这是获取流量的函数
    if current_traffic > 100:
        scale_deploy('my-deployment', 5)
    else:
        scale_deploy('my_deployment', 2)