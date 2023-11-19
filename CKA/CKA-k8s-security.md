# 概述

## 认证

- kubernetes主要通过API server对外提供服务，那么就需要对访问apiserver的用户做认证，如果任何人都能访问apiserver，那么就可以随意在k8s集群部署资源，这是非常危险的，也容易被黑客攻击渗透，所以需要我们对访问k8s系统的apiserver的用户进行认证，确保是合法的符合要求的用户。

## 授权

- 认证通过后仅代表它是一个被apiserver信任的用户，能访问apiserver，但是用户是否拥有删除资源的权限， 需要进行授权操作，常见的授权方式有rbac授权。

## 准入控制器

- 当用户经过认证和授权之后，最后一步就是准入控制了，k8s提供了多种准入控制机制，它有点类似"插件"，为apiserver提供了很好的"可扩展性"。请求apiserver时，通过认证、鉴权后、持久化("api对象"保存到etcd)前，会经过"准入控制器"，让它可以做"变更和验证"。

- 举例：如果我们创建pod时定义了资源上下限，但不满足LimitRange规则中定义的资源上下限，此时LimitRanger就会拒绝我们创建此pod

# 访问apiserver的认证

## 客户端认证

- 也称为双向TLS认证， kubectl在访问apiserver的时候，apiserver也要认证kubectl是否是合法的，他们都会通过ca根证书来进行验证，如下图：

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202311161317269.png" alt="image-20231116131757137" style="zoom:67%;" />



## Bearertoken

- 可以理解为apiserver将一个密码通过了非对称加密的方式告诉了kubectl，然后通过该密码进行相互访问
- Kubectl访问k8s集群，要找一个kubeconfig文件（$HOME/.kube/config），基于kubeconfig文件里的用户访问apiserver。

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202311161332166.png" alt="image-20231116133231124" style="zoom:67%;" />

### kubeconfig文件

- [使用 kubeconfig 文件组织集群访问 | Kubernetes](https://kubernetes.io/zh-cn/docs/concepts/configuration/organize-cluster-access-kubeconfig/)

- 在K8S集群当中，当我们使用kubectl操作k8s资源时候，需要确定我们用哪个用户访问哪个k8s集群，kubectl操作k8s集群资源会去/root/.kube目录下找config文件，可以通过kubectl查看config文件配置，如下：

  ```bash
  kubectl config view
  ```

  ~~~yaml
  apiVersion: v1
  clusters:
  - cluster:
      certificate-authority-data: DATA+OMITTED
      server: https://192.168.40.4:6443 #apiserver的地址
    name: kubernetes #集群的名字
  contexts:
  - context:
      cluster: kubernetes
      user: kubernetes-admin 
    name: kubernetes-admin@kubernetes  #上下文的名字
  current-context: kubernetes-admin@kubernetes  #当前上下文的名字
  kind: Config
  preferences: {}
  users:
  - name: kubernetes-admin
    user:
      client-certificate-data: REDACTED
      client-key-data: REDACTED
  ~~~

  - 在上面的配置文件当中，定义了集群、上下文以及用户。其中Config也是K8S的标准资源之一，在该配置文件当中定义了一个集群列表，指定的集群可以有多个；用户列表也可以有多个，指明集群中的用户；而在上下文列表当中，是进行定义可以使用哪个用户对哪个集群进行访问，以及当前使用的上下文是什么。

## ServiceAccount

- 上面客户端证书认证和Bearertoken的两种认证方式，都是外部访问apiserver的时候使用的方式，那么我们这次说的Serviceaccount是**内部访问pod和apiserver交互**时候采用的一种方式。

- Serviceaccount包括了：namespace、token、ca，且通过目录挂载的方式给予pod，当pod运行起来的时候，就会读取到这些信息，从而使用该方式和apiserver进行通信。如下图：

  <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202311161334673.png" alt="image-20231116133424621" style="zoom:67%;" />

# 授权

- 用户通过认证之后，什么权限都没有，需要一些后续的授权操作，如对资源的增删该查等，kubernetes1.6之后开始有RBAC（基于角色的访问控制机制）授权检查机制。

- Kubernetes的授权是基于插件形成的，其常用的授权插件有以下几种：
  1. Node（节点认证）
  2. ABAC (基于属性的访问控制)
  3. RBAC（基于角色的访问控制）
  4. Webhook（基于http回调机制的访问控制）

## RBAC

- 给一个用户（Users）赋予一个角色（Role），角色拥有权限，从而让用户拥有这样的权限。随后在授权机制当中，只需要将权限授予某个角色，此时用户将获取对应角色的权限，从而实现角色的访问控制。

## Role/RoleBinding

- 在k8s的授权机制当中，采用RBAC的方式进行授权，其工作逻辑是，把对对象的操作权限定义到一个角色当中，再将用户绑定到该角色，从而使用户得到对应角色的权限。
  - 如果通过rolebinding绑定role，只能对**rolebinding所在的名称空间**的资源有权限，例如user1这个用户绑定到role1上，只对role1这个名称空间的资源有权限，对其他名称空间资源没有权限。
- 另外，k8s为此还有一种集群级别的授权机制，就是定义一个集群角色（ClusterRole），对集群内的所有资源都有可操作的权限，从而将User2通过ClusterRoleBinding到ClusterRole，从而使User2拥有集群的操作权限。

### user基于rolebinding绑定到role

- 用户基于rolebinding绑定到role：限定在rolebinding所在的名称空间。

  <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202311161359205.png" alt="image-20231116135923135" style="zoom: 67%;" />

### user基于rolebinding绑定到clusterrole

- 假如有6个名称空间，每个名称空间的用户都需要对自己的名称空间有管理员权限，那么需要定义6个role和rolebinding，然后依次绑定，如果名称空间更多，我们需要定义更多的role，这个是很麻烦的。
- 所以我们引入clusterrole，定义一个clusterrole，对clusterrole授予所有权限，然后用户通过rolebinding绑定到clusterrole，就会拥有**自己名称空间**的管理员权限了
- 注：RoleBinding仅仅对当前名称空间有对应的权限。

![image-20231116141540633](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202311161415689.png)

### user基于clusterrolebinding绑定到clusterrole

- clusterrolebinding是集群范围的，没有namespace限制。这种方案是在整个集群内生效的。

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202311161418465.png" alt="image-20231116141855404" style="zoom:67%;" />

# 准入控制

- 准入控制器限制创建、删除、修改对象的请求。 准入控制器也可以阻止自定义动作，例如通过 API 服务器代理连接到 Pod 的请求。 准入控制器**不会** （也不能）阻止读取（**get**、**watch** 或 **list**）对象的请求。

- 在k8s上准入控制器的模块有很多，其中比较常用的有LimitRanger、ResourceQuota、ServiceAccount。（这三种是默认开启的）

- 用kubeadm安装的集群，如何查看apiserver开启的准入控制器？

  ~~~bash
  #master节点
  cat /etc/kubernetes/manifests/kube-apiserver.yaml 
  
  apiVersion: v1
  kind: Pod
  metadata:
    annotations:
      kubeadm.kubernetes.io/kube-apiserver.advertise-address.endpoint: 192.168.40.4:6443
    creationTimestamp: null
    labels:
      component: kube-apiserver
      tier: control-plane
    name: kube-apiserver
    namespace: kube-system
  spec:
    containers:
    - command:
  ...
      - --enable-admission-plugins=NodeRestriction
  ...
  ~~~

- apiserver启用准入控制插件需要使用--enable-admission-plugins选项来指定，该选项可以使用多个值，用逗号隔开表示启用指定的准入控制插件；这里配置文件中显式启用了NodeRestrication这个插件；默认没有写在这上面的内置准入控制器，它也是启用了的，比如LimitRanger、ResourceQuota、ServiceAccount等等；对于不同的k8s版本，内置的准入控制器和启用与否请查看相关版本的官方文档；对于那些没有启动的准入控制器，我们可以在上面选项中直接启用，分别用逗号隔开即可。

- https://kubernetes.io/zh-cn/docs/reference/access-authn-authz/admission-controllers/

# Account

## UserAccount

- kubernetes中账户分为：UserAccounts（用户账户）和 ServiceAccounts（服务账户）两种：
  - UserAccount是给kubernetes集群外部用户使用的，如kubectl访问k8s集群要用useraccount用户，kubeadm安装的k8s，默认的useraccount用户是kubernetes-admin
  - 使用kubeadm安装的K8s，会在用户家目录下创建一个认证配置文件 .kube/config 这里面保存了客户端访问API Server的密钥相关信息，当用kubectl访问k8s时，它就会自动读取该配置文件，向API Server发起认证，然后完成操作请求。

## ServiceAccount

- ServiceAccount是Pod使用的账号，Pod容器的进程需要访问API Server时用的就是ServiceAccount账户。

- ServiceAccount仅局限它所在的namespace，每个namespace创建时都会自动创建一个default service account；创建Pod时，如果没有指定Service Account，Pod则会使用default Service Account。

  ~~~bash
  #查看默认名称空间下的
  k get sa
  #创建pod，查看sa信息
  k describe po pod-busybox -n test
  Name:             pod-busybox
  Namespace:        test
  Priority:         0
  Service Account:  default
  ~~~

- sa使用案例：创建sa，绑定到pod

  ~~~bash
  #创建sa
  k create sa sa-test
  #创建pod
  apiVersion: v1
  kind: Pod
  metadata:
    name: pod-busybox
  spec:
    serviceAccountName: sa-test
    containers:
    - name: busybox
      image: busybox:1.28
      command:
      - "/bin/sh"
      - "-c"
      - "sleep 36000"
  #进入pod
  k exec -it pod-busybox -- /bin/sh
  cd /var/run/secrets/kubernetes.io/serviceaccount/
  #手动请求apiserver接口，报403，是因为这个role还没有任何权限
  curl --cacert ./ca.crt  -H "Authorization: Bearer $(cat ./token)"  https://kubernetes/api/v1/namespaces/kube-system
  
  {
    "kind": "Status",
    "apiVersion": "v1",
    "metadata": {},
    "status": "Failure",
    "message": "namespaces \"kube-system\" is forbidden: User \"system:serviceaccount:default:sa-test\" cannot get resource \"namespaces\" in API group \"\" in the namespace \"kube-system\"",
    "reason": "Forbidden",
    "details": {
      "name": "kube-system",
      "kind": "namespaces"
    },
    "code": 403
  #给这个role通过clusterrolebinding授予cluster-admin权限
  kubectl create clusterrolebinding sa-test-admin --clusterrole=cluster-admin  --serviceaccount=default:sa-test
  #再去请求接口就成功了，请求pod信息可以看到所有namespace的信息。
  curl --cacert ./ca.crt  -H "Authorization: Bearer $(cat ./token)"  https://kubernetes/api/v1/pods
  ~~~

# Role和clusterRole

## Role

- 一组权限的集合。只能定义在**某个命名空间**中，**对命名空间内的资源**进行授权。如果是集群级别的资源，则需要使用ClusterRole。

- 举例：定义一个对pod有只读权限的role

  ~~~yaml
  apiVersion: rbac.authorization.k8s.io/v1
  kind: Role
  metadata:
    namespace: rbac
    name: pod-read
  rules:
  - apiGroups: [""]  # 支持的API组列表，例如："apiVersion: apps/v1"等
    resources: ["pods"]  # 支持的资源对象列表，例如pods、deployments、jobs
    resourceNames: []  # 指定resource的名称
    verbs: ["get","watch","list"]  # 对资源对象的操作方法列表。
  ~~~

## clusterRole

- 不指定命名空间，创建出来之后，任何命名空间内的account都可以绑定到clusterrole上去。

- 还可以用于以下特殊元素的授权：

  1、集群范围的资源，例如Node

  2、非资源型的路径，例如：/healthz

  3、包含全部命名空间的资源，例如Pods

- 举例：定义一个集群角色可让用户访问任意secrets

  ~~~yaml
  apiVersion: rbac.authorization.k8s.io/v1
  kind: ClusterRole
  metadata:
    name: secrets-clusterrole
  rules:
  - apiGroups: [""]
    resources: ["secrets"]
    verbs: ["get","watch","list"]
  ~~~

# RoleBinding和ClusterRoleBinding

- RoleBinding和ClusterRoleBinding用于把一个角色绑定在一个目标上，可以是User，Group，Service Account。
- 使用RoleBinding为某个命名空间授权，使用ClusterRoleBinding为集群范围内授权。

## roleBinding

- 给某个user在某个命名空间binding在某个role上，那就仅在这个命名空间起作用。

~~~yaml
#将在rbac命名空间中把pod-read角色授予用户es
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: pod-read-bind
  namespace: rbac
subjects:
- kind: User
  name: es
  apiGroup: rbac.authorization.k8s.io
roleRef:
- kind: Role
  name: pod-read
  apiGroup: rbac.authorizatioin.k8s.io
~~~

## ClusterRoleBinding

- 给一个user绑定一个clusterRole，就叫clusterRoleBinding。其实也是rolebinding，只是绑定到的是clusterrole。

  ~~~yaml
  #es这个user能获取到集群中所有的资源信息
  apiVersion: rbac.authorization.k8s.io/v1
  kind: RoleBinding
  metadata:
    name: es-allresource
    namespace: rbac
  subjects:
  - kind: User
    name: es
    apiGroup: rbac.authorization.k8s.io
  roleRef:
    apiGroup: rbac.authorization.k8s.io
    kind: ClusterRole
    name: cluster-admin
  ~~~

# 资源引用方式

- 多数资源可以用其名称的字符串表示，也就是Endpoint中的URL相对路径。
  - 例如pod中的日志是：GET /api/v1/namaspaces/{namespace}/pods/{podname}/log
- 如果需要在一个RBAC对象中体现上下级资源，就需要使用“/”分割资源和下级资源。

## Lab：让user同时读取pod和pod log

- 定义role，权限是读取pod和pod log

  ~~~yaml
  apiVersion: rbac.authorization.k8s.io/v1
  kind: Role
  metadata:
    name: logs-reader
    namespace: rbac
  rules:
  - apiGroups: [""]
    resources: ["pods","pods/log"]
    verbs: ["get","list","watch"]
  ~~~

- 创建一个SA

  ~~~bash
  kubectl create sa sa-test -n rbac
  ~~~

- 创建一个rolebinding，给sa赋予role

  ~~~bash
  kubectl create rolebinding rb-sa-test -n rbac --role=logs-reader --serviceaccount=rbac:sa-test
  ~~~

  


