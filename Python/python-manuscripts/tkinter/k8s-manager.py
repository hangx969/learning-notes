import tkinter as tk
from tkinter import messagebox, scrolledtext
from kubernetes import client, config

# 加载k8s kubeconfig
# 注意打包成程序的时候这里最好用绝对路径
config.load_config(config_file='tkinter/kubeconfig-local')

# 创建api对象
apps_v1 = client.AppsV1Api()
core_v1 = client.CoreV1Api()

# 获取集群namespace
def get_namespace():
    # list_namespace返回对象，包含所有ns的json属性
    # .items是转成列表，可以直接遍历每一个ns的json属性
    return [ns.metadata.name for ns in core_v1.list_namespace().items]

# 获取集群deployment和statefulset
def get_resources(namespace):
    deployments = apps_v1.list_namespaced_deployment(namespace=namespace).items
    statefulsets = apps_v1.list_namespaced_stateful_set(namespace=namespace).items
    # 把deployment和其name打包成元组放进列表
    # 把statefulset和其name打包成元组放进列表
    # 两个列表 + 拼接到一起
    resources = [("Deployment", d.metadata.name) for d in deployments] + [("Statefulset", s.metadata.name) for s in statefulsets]
    return resources

# 更新资源名称下拉菜单。当用户选择了namespace后，自动列出这个namespace中的deployment或者statefulset
def update_resources_menu(*args):
    # 从namespace下拉菜单变量获取到选择好的namespace
    namespace = ns_var.get().strip()
    # 从函数里拿到所有的deployment和sts
    resources = get_resources(namespace)
    # 清空resource name下拉菜单
    resource_name_menu['menu'].delete(0, 'end')
    # 设定reosurce_name_ver的默认值显示
    if resources:
        resource_name_var.set(resources[0][1])
    else:
        # 列表为空说明对应namespace没这种资源，变量返回空值。不显示。
        resource_name_var.set('')
    # 往下拉菜单中添加所有resource name
    for type, name in resources:
        # ['menu‘]访问OptionMenu的菜单部分，add_command添加菜单元素，label指定新条目的值，setit将label的值赋值给变量
        resource_name_menu['menu'].add_command(label=name, command=tk._setit(resource_name_var, name))


# 更新副本数
def update_replicas():
    # 从下拉菜单获取值
    namespace = ns_var.get().strip()
    resource_type = resource_type_var.get().strip()
    resoruce_name = resource_name_var.get().strip()
    # 获取用户输入的replica
    replicas = replicas_entry.get().strip()
    # 验证replicas是否是整数
    try:
        replicas = int(replicas)
    except ValueError as e:
        messagebox.showerror('Error', "Replicas is not valid, please input an int")
    # 分别更新deployment和sts
    try:
        if resource_type == 'Deployment':
            deployment = apps_v1.list_namespaced_deployment(name=resoruce_name, namespace=namespace)
            deployment.spec.replicas = replicas
            apps_v1.patch_namespaced_deployment(name=resoruce_name, namespace=namespace, body=deployment)
            messagebox.showinfo('Update finished', f"Deployment {resoruce_name} in namespace {namespace} has been updated to replicas {replicas}\n")
        elif resource_type == 'Statefulset':
            statefulset = apps_v1.list_namespaced_stateful_set(name=resoruce_name, namespace=namespace)
            statefulset.spec.replicas = replicas
            apps_v1.patch_namespaced_stateful_set(name=resoruce_name, namespace=namespace, body=statefulset)
            messagebox.showinfo('Update finished', f"Statefulset {resoruce_name} in namespace {namespace} has been updated to replicas {replicas}\n")
    except client.ApiException as e:
        messagebox.showerror("Error:", f"{str(e)}")

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Kubernetes deployment and statefulset management")

    # 获取namespace列表
    valid_ns_list = get_namespace()
    # namespace下拉菜单的文本标签
    tk.Label(root, text='Namespace:').grid(row=0, column=0, padx=10, pady=10)
    # 创建一个字符串变量，是根据用户选择动态更新的
    ns_var = tk.StringVar(root)
    # 默认值为namespace列表首元素
    ns_var.set(valid_ns_list[0])
    # 定义下拉菜单，* 是解包操作符，用于将列表中的每个元素作为单独的参数传递给OptionMenu。这些选项就会在下拉菜单中以供选择
    ns_menu = tk.OptionMenu(root, ns_var, *valid_ns_list)
    ns_menu.grid(row=0, column=1, padx=10, pady=10)

    # 资源类型下拉菜单
    tk.Label(root, text='Resource Type:').grid(row=1, column=0, padx=10, pady=10)
    resource_type_var = tk.StringVar(root)
    resource_type_var.set("Deployment")
    resource_type_menu = tk.OptionMenu(root, resource_type_var, "Deployment", "Statefulset")
    resource_type_menu.grid(row=1, column=1, padx=10, pady=10)

    # 资源名称文本标签和下拉菜单标签
    tk.Label(root, text='Resource Name:').grid(row=2, column=0, padx=10, pady=10)
    resource_name_var = tk.StringVar(root)
    resource_name_menu = tk.OptionMenu(root, resource_name_var, '')
    resource_name_menu.grid(row=2, column=1, padx=10, pady=10)

    # 当ns_var变量发生写入时，调用指定的回调函数，更新资源名称下拉菜单内容
    ns_var.trace_add('write', update_resources_menu)

    # 输入副本数的窗口
    tk.Label(root, text='Replicas').grid(row=3, column=5, padx=10, pady=10)
    replicas_entry = tk.Entry(root)
    replicas_entry.grid(row=3, column=1, padx=10, pady=10)

    # 提交按钮
    submit_button = tk.Button(root, text='Submit', command=update_replicas)
    submit_button.grid(row=4, column=1, padx=10, pady=10)

    # 先根据默认显示的namespace，列出资源名称
    update_resources_menu()
    tk.mainloop()