# 概述

## 认证

- kubernetes主要通过API server对外提供服务，那么就需要对访问apiserver的用户做认证，如果任何人都能访问apiserver，那么就可以随意在k8s集群部署资源，这是非常危险的，也容易被黑客攻击渗透，所以需要我们对访问k8s系统的apiserver的用户进行认证，确保是合法的符合要求的用户。

## 授权

- 认证通过后仅代表它是一个被apiserver信任的用户，能访问apiserver，但是用户是否拥有删除资源的权限，需要进行授权操作，常见的授权方式有rbac授权。

## 准入控制器-admission controller

- 当用户经过认证和授权之后，最后一步就是准入控制了，k8s提供了多种准入控制机制，它有点类似"插件"，为apiserver提供了很好的"可扩展性"。请求apiserver时，通过认证、鉴权后、持久化(api对象保存到etcd)前，会经过"准入控制器"，让它可以做"变更和验证"(mutating, validating)。

- 举例：如果我们创建pod时定义了资源上下限，但不满足LimitRange规则中定义的资源上下限，此时LimitRanger就会拒绝我们创建此pod

# 访问apiserver的认证

## 客户端认证

- kubectl的认证步骤：
  - 先去找环境变量KUBECONFIG。如果用这种方式配置，需要给这个环境变量配置成KUBECONFIG=/etc/kubernetes/admin.conf
  - `echo $KUBECONFIG`看到这个环境变量是空的，下一步去找`$HOME/.kube/config`文件，根据其中的用户和集群信息去访问，可以通过`kubectl config view`来看

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

  - 首先看`current-context: kubernetes-admin@kubernetes`表示当前使用的context
  - 然后找context下面，name是`kubernetes-admin@kubernetes`的这个context中，user是kubernetes-admin，集群是kubernetes。
  - 然后网上找，在cluster里面，看到name是kubernetes的这个集群，apiserver的地址是https://192.168.40.4:6443

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

- 准入控制器限制**创建、删除、修改**对象的请求。准入控制器也可以阻止自定义动作，例如通过 API 服务器代理连接到 Pod 的请求。 准入控制器**不会**（也不能）阻止读取（**get**、**watch** 或 **list**）对象的请求。

- 在k8s上准入控制器的模块有很多，其中比较常用的有LimitRanger、ResourceQuota、ServiceAccount。（这三种是默认开启的）

- apiserver启用准入控制插件需要使用--enable-admission-plugins选项来指定，该选项可以使用多个值，用逗号隔开表示启用指定的准入控制插件；这里配置文件中显式启用了NodeRestrication这个插件；默认没有写在这上面的内置准入控制器，它也是启用了的，比如LimitRanger、ResourceQuota、ServiceAccount等等；对于不同的k8s版本，内置的准入控制器和启用与否请查看相关版本的官方文档；对于那些没有启动的准入控制器，我们可以在上面选项中直接启用，分别用逗号隔开即可。

- 用kubeadm安装的集群，如何查看apiserver开启的准入控制器？

  ~~~bash
  #kubeadm安装的集群，登录到master节点
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

  ~~~sh
  #用command查看
  kube-apiserver -h | grep enable-admission-plugins
  #在kubernetes 1.32中，默认开启的admission controller plugin如下：
  CertificateApproval, CertificateSigning, CertificateSubjectRestriction, DefaultIngressClass, DefaultStorageClass, DefaultTolerationSeconds, LimitRanger, MutatingAdmissionWebhook, NamespaceLifecycle, PersistentVolumeClaimResize, PodSecurity, Priority, ResourceQuota, RuntimeClass, ServiceAccount, StorageObjectInUseProtection, TaintNodesByCondition, ValidatingAdmissionPolicy, ValidatingAdmissionWebhook
  ~~~

- 参考文档：https://kubernetes.io/zh-cn/docs/reference/access-authn-authz/admission-controllers/

# Account

## UserAccount

- kubernetes中账户分为：UserAccounts（用户账户）和 ServiceAccounts（服务账户）两种：
  - UserAccount是给kubernetes集群外部用户使用的，如kubectl访问k8s集群要用useraccount用户，kubeadm安装的k8s，默认的useraccount用户是kubernetes-admin
  - 使用kubeadm安装的K8s，会在用户家目录下创建一个认证配置文件 .kube/config 这里面保存了客户端访问API Server的密钥相关信息，当用kubectl访问k8s时，它就会自动读取该配置文件，向API Server发起认证，然后完成操作请求。

## ServiceAccount

- ServiceAccount是Pod使用的账号，Pod容器的进程需要访问API Server时用的就是ServiceAccount账户。

- ServiceAccount仅局限它所在的namespace，每个namespace创建时都会自动创建一个default service account；创建Pod时，如果没有指定Service Account，Pod则会使用default Service Account。

- 赋予Service Account “default”的权限会让所有没有指定serviceAccountName的Pod都具有这些权限

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

### 给ns中的所有sa同时授权

- 如果希望在一个命名空间中，任何Service Account应用都具有一个角色，则可以为这一命名空间的Service Account群组进行授权 

  ```bash
  kubectl create rolebinding sa-view --clusterrole=view --group=system:serviceaccounts:my-namespace --namespace=my-namespace
  ```

### 给集群中的sa同时授权

- 为集群范围内所有Service Account都授予一个低权限角色

  ~~~bash
  kubectl create clusterrolebinding sa-view --clusterrole=view --group=system:serviceaccounts
  #system:serviceaccounts指的是集群中所有SA这个组
  ~~~



# Role和clusterRole

## Role - 定义目标资源和权限

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

## 常见的role定义

> 什么是roles定义里面的API Groups
>
> ~~~bash
> k explain roles.rules
>    apiGroups    <[]string>
>      APIGroups is the name of the APIGroup that contains the resources. If
>      multiple API groups are specified, any action requested against one of the
>      enumerated resources in any API group will be allowed. "" represents the
>      core API group and "*" represents all API groups.
> ~~~
>
> API Version是由API Group和API Version组成
>
> ```bash
> k api-versions
> admissionregistration.k8s.io/v1
> apiextensions.k8s.io/v1
> apiregistration.k8s.io/v1
> apps/v1
> authentication.k8s.io/v1
> authorization.k8s.io/v1
> autoscaling/v1
> autoscaling/v2
> autoscaling/v2beta2
> batch/v1
> certificates.k8s.io/v1
> coordination.k8s.io/v1
> crd.projectcalico.org/v1
> discovery.k8s.io/v1
> events.k8s.io/v1
> flowcontrol.apiserver.k8s.io/v1beta1
> flowcontrol.apiserver.k8s.io/v1beta2
> networking.k8s.io/v1
> node.k8s.io/v1
> policy/v1
> rbac.authorization.k8s.io/v1
> scheduling.k8s.io/v1
> storage.k8s.io/v1
> storage.k8s.io/v1beta1
> v1
> ```

- 允许读取核心API组的Pod资源

  ~~~yaml
  rules:
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get","list","watch"]
  ~~~

- 允许读写apps API组中的deployment资源

  ~~~yaml
  rules:
  - apiGroups: ["apps"]
    resources: ["deployments"]
    verbs: ["get","list","watch","create","update","patch","delete"]
  ~~~

- 允许读取Pod以及读写job信息

  ~~~YAML
  rules:
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get","list","watch"]
  - apiGroups: [""]
    resources: ["jobs"]
    verbs: ["get","list","watch","create","update","patch","delete"]
  ~~~

- 允许读取一个名为my-config的ConfigMap（必须绑定到一个RoleBinding来限制到一个Namespace下的ConfigMap）

  ~~~yaml
  rules:
  - apiGroups: [""]
    resources: ["configmaps"]
    resourceNames: ["my-configmap"]
    verbs: ["get"]
  ~~~

- 读取核心组的Node资源（Node属于集群级的资源，所以必须存在于ClusterRole中，并使用ClusterRoleBinding进行绑定）

  ~~~yaml
  rules:
  - apiGroups: [""]
    resources: ["nodes"]
    verbs: ["get","list","watch"]
  ~~~

- 允许对非资源端点“/healthz”及其所有子路径进行GET和POST操作（必须使用ClusterRole和ClusterRoleBinding）：

  ```yaml
  rules:
  - nonResourceURLs: ["/healthz","/healthz/*"]
    verbs: ["get","post"]
  ```

# RoleBinding和ClusterRoleBinding

- RoleBinding和ClusterRoleBinding用于把一个角色绑定在一个目标上，可以是User，Group，Service Account。
- 使用RoleBinding为某个命名空间授权，使用ClusterRoleBinding为集群范围内授权。

## roleBinding - 定义谁去绑定什么role

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
  
  > Kubernetes API 服务器提供 3 个 API 端点（`healthz`、`livez` 和 `readyz`）来表明 API 服务器的当前状态。 `healthz` 端点已被弃用（自 Kubernetes v1.16 起），你应该使用更为明确的 `livez` 和 `readyz` 端点。

## 常见的rolebinding示例

- 用户名alice    

  ```yaml
  subjects:
  - kind: User
    name: alice
    apiGroup: rbac.authorization.k8s.io
  ```

- 组名alice      

  ```yaml
  subjects:
  - kind: Group
    name: alice
    apiGroup: rbac.authorization.k8s.io
  ```

- kube-system命名空间中默认Service Account   

  ```yaml
  subjects:
  - kind: ServiceAccount
    name: default
    namespace: kube-system
  ```

# api接口访问k8s资源

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

- 创建一个rolebinding，给sa赋予logs-reader role

  ~~~bash
  kubectl create rolebinding rb-sa-test-logs-reader -n rbac --role=logs-reader --serviceaccount=rbac:sa-test
  ~~~

- 创建pod，把sa挂载进去

  ~~~yaml
  apiVersion: v1
  kind: Pod
  metadata:
    name: pod-sa-test
    namespace: rbac
    labels:
      app: sa
  spec:
    serviceAccountName: sa-test
    containers:
    - name:  sa-nginx
      ports:
      - containerPort: 80
      image: nginx
      imagePullPolicy: IfNotPresent
  ~~~

- 进pod模拟请求资源

  ~~~bash
  kubectl exec -it pod-sa-test -n rbac -- /bin/bash
  #这里面保存着sa挂进来的token
  cd /var/run/secrets/kubernetes.io/serviceaccount
  #看rbac名称空间下的pod
  curl --cacert ./ca.crt  -H "Authorization: Bearer $(cat ./token)" https://kubernetes.default/api/v1/namespaces/rbac/pods/ 
  #看某个pod的log
  curl --cacert ./ca.crt  -H "Authorization: Bearer $(cat ./token)" https://kubernetes.default/api/v1/namespaces/rbac/pods/pod-sa-test/log
  ~~~

# 限制kubectl用户的权限

## 限制kubectl用户仅能访问某命名空间

- SSL认证

  ```bash
  #生成私钥
  cd /etc/kubernetes/pki/
  (umask 077; openssl genrsa -out hangx.key 2048) 
  #生成证书请求
  openssl req -new -key hangx.key -out hangx.csr -subj "/CN=hangx"
  #生成证书，表明这个用户被api server信任
  openssl x509 -req -in hangx.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out hangx.crt -days 3650
  ```

- 配置k8s用户

  ```bash
  #把hangx用户添加到集群中，可以用来认证apiserver的连接
  kubectl config set-credentials hangx --client-certificate=./hangx.crt --client-key=./hangx.key --embed-certs=true
  #在kubeconfig中新增hangx账号
  kubectl config set-context hangx@kubernetes --cluster=kubernetes --user=hangx
  #切换到hangx用户
  kubectl config use-context hangx@kubernetes
  #切回cluster-admin
  kubectl config use-context kubernetes-admin@kubernetes
  #给hangx用户rolebinding授权
  kubectl create ns hangx-test
  kubectl create rolebinding hangx -n hangx-test --clusterrole=cluster-admin --user=hangx
  #切换用户，测试权限
  kubectl config use-context hangx@kubernetes
  kubectl get pods -n hangx-test
  ```

- 配置linux客户端的用户，让他能用hangx的config文件访问集群

  ```bash
  useradd hangx
  #config文件的拷贝：得把/root/.kube/一整个目录拷贝过去
  cp -ar /root/.kube/ /tmp/
  #修改/tmp/.kube/config文件，把kubernetes-admin相关的删除，只留hangx用户；current context切换到hangx用户
  #kubeconfig文件拷贝到这个用户的家目录
  cp -ar /tmp/.kube/ /home/hangx/
  #root用户下操作，修改.kube目录的属主、属组为hangx
  chown -R hangx.hangx /home/hangx/.kube
  #切换用户
  su - hangx
  #验证权限
  k get po -n hangx-test
  ```

## 授权kubectl用户查看所有pod的权限

- SSL认证

  ```bash
  #生成私钥
  cd /etc/kubernetes/pki/
  (umask 077; openssl genrsa -out hangx1.key 2048) 
  #生成证书请求
  openssl req -new -key hangx1.key -out hangx1.csr -subj "/CN=hangx1"
  #生成证书，表明这个用户被api server信任
  openssl x509 -req -in hangx1.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out hangx1.crt -days 3650
  ```

- 配置k8s用户

  ```bash
  #把hangx用户添加到集群中，可以用来认证apiserver的连接
  kubectl config set-credentials hangx --client-certificate=./hangx.crt --client-key=./hangx.key --embed-certs=true
  #在kubeconfig中新增hangx账号
  kubectl config set-context hangx@kubernetes --cluster=kubernetes --user=hangx
  #切换到hangx用户
  kubectl config use-context hangx@kubernetes
  #切回cluster-admin
  kubectl config use-context kubernetes-admin@kubernetes
  ```

- 创建role和rolebinding

  ~~~bash
  #创建clusterrole：pod-reader
  apiVersion: rbac.authorization.k8s.io/v1
  kind: ClusterRole
  metadata:
    name: cr-pod-reader
  rules:
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list", "watch"]
    
  #给hangx用户clusterrolebinding授权
  kubectl create ns hangx-test
  kubectl create clusterrolebinding rb-hangx-cr --clusteerrole=cr-pod-reader --user=hangx
  #切换用户，测试权限
  kubectl config use-context hangx@kubernetes
  kubectl get pods
  ~~~

- 配置linux客户端的用户，让他能用hangx的config文件访问集群

  ```bash
  useradd hangx
  #config文件的拷贝：得把/root/.kube/一整个目录拷贝过去
  cp -ar /root/.kube/ /tmp/
  #修改/tmp/.kube/config文件，把kubernetes-admin相关的删除，只留hangx用户；current context切换到hangx用户
  #kubeconfig文件拷贝到这个用户的家目录
  cp -ar /tmp/.kube/ /home/hangx/
  #root用户下操作，修改.kube目录的属主、属组为hangx
  chown -R hangx.hangx /home/hangx/.kube
  #切换用户
  su - hangx
  #验证权限
  k get po -n hangx-test
  ```

# resourcequota准入控制器

- ResourceQuota准入控制器是k8s上内置的准入控制器，默认该控制器是启用的状态，它主要作用是用来限制一个名称空间下的资源的使用，它能防止在一个名称空间下的pod被过多创建时，导致过多占用k8s资源。简单讲它是用来在名称空间级别限制用户的资源使用。
- resource quota也是一个资源，需要yaml定义创建。定义的规则中，只要有一个不满足，新pod就创建不出来。

## 限制CPU/memory/deploy等资源量

~~~yaml
#对ns做限制
apiVersion: v1
kind: ResourceQuota
metadata:
  name: quota-test
  namespace: quota
spec:
  hard:
    pods: "6"
    count/deployments.apps: "6"
    persistentvolumeclaims: "6"
    requests.cpu: "2"
    requests.memory: 2Gi
    limits.cpu: "4"
    limits.memory: 10Gi
~~~

~~~bash
k get quota -n quota
k get resourcequota -n quota
~~~

## 限制存储空间大小

~~~yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: quota-storage-test
  namespace: quota
spec:
  hard:
    persistentvolumeclaims: "5"
    requests.storage: "5Gi" #所有非停止的pod申请的存储不超过5Gi
    requests.ephemeral-storage: "1Gi" #限制本地临时存储
    limits.ephemeral-storage: "2Gi"
~~~

# limitRanger准入控制

- LimitRanger准入控制器是k8s上一个内置的准入控制器，LimitRange是k8s上的一个标准资源，它主要用来定义在某个名称空间下限制pod或pod里的容器对k8s上的cpu和内存资源使用；它能够定义我们在某个名称空间下创建pod时使用的cpu和内存的上限和下限以及默认cpu、内存的上下限。

- 如果我们创建pod时定义了资源上下限，但不满足LimitRange规则中定义的资源上下限，此时LimitRanger就会拒绝我们创建此pod；如果我们在LimitRange规则中定义了默认的资源上下限制，我们创建资源没有指定其资源限制，它默认会使用LimitRange规则中的默认资源限制；同样的逻辑LimitRanger可以限制一个pod使用资源的上下限，它还可以限制pod中的容器的资源上下限，比限制pod更加精准。
- 不管是针对pod还是pod里的容器，它始终只是**限制单个pod资源使用**。

~~~yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: lr-cpu-memory
  namespace: quota
spec:
  limits:
  - default: #如果创建pod不指定limit，就自动用这里default指定的值
      cpu: 1000m
      memory: 1000Mi
    defaultRequest: #如果创建pod不指定request，就自动用这里default指定的值
      cpu: 500m
      memory: 500Mi
    min: #pod的yaml里面如果自己定义request，不能少于500m cpu，500mimemory
      cpu: 500m
      memory: 500Mi
    max: #pod的yaml里面如果自己定义了limit，不能多于2000m cpu和2000mimemory
      cpu: 2000m
      memory: 2000Mi
    maxLimitRequestRatio: #定义limit/request的比值<=4。自己定义poid的limit/request比值不能高于4
      cpu: 4
      memory: 4
    type: Container
~~~

