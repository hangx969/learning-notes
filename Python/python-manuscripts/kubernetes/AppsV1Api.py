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

    # 处理用户输入副本数
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