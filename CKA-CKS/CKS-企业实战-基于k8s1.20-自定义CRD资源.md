# CRD

- https://mp.weixin.qq.com/s/Ts9MxQOpQVaUtw6YbHXogw
- CRD全称是CustomResourceDefinition：
  - 在 Kubernetes 中一切都可视为资源，Kubernetes 1.7 之后增加了对 CRD 自定义资源二次开发能力来扩展 Kubernetes API，通过 CRD 我们可以向 Kubernetes API 中增加新资源类型，而不需要修改 Kubernetes 源码来创建自定义的 API server，该功能大大提高了 Kubernetes 的扩展能力。
  - 当你创建一个新的(CRD)时，Kubernetes API服务器将为你指定的每个版本创建一个新的RESTful资源路径，我们可以根据该api路径来创建一些我们自己定义的类型资源。
  - CRD可以是命名空间的，也可以是集群范围的，由CRD的作用域(scpoe)字段中所指定的，与现有的内置对象一样，删除名称空间将删除该名称空间中的所有自定义对象。CRD本身没有名称空间，所有名称空间都可以使用。

# 自定义CRD资源

- 定义

~~~yaml
tee crontab-crd.yaml<<'EOF'
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  #metadata.name 是用户自定义资源中自己自定义的一个名字。一般我们建议使用“顶级域名.xxx.APIGroup”这样的格式，APIGroup的名称必须与下面的spec.Group字段匹配，格式为: <plural>.<group>
  name: crontabs.stable.example.com
spec:
#spec 用于指定该 CRD 的 group、version。比如在创建 Pod 或者 Deployment 时，它的 group 可能为 apps/v1 或者 apps/v1beta1 之类，这里我们也同样需要去定义 CRD 的 API group
  group: stable.example.com
  versions:
  - name: v1
    served: true #每个版本都可以通过服务标志启用/禁用
    storage: true #必须将一个且仅有一个版本标记为存储版本。
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              cronSpec:
                type: string
              image:
                type: string
              replicas:
                type: integer
  scope: Namespaced #指定crd资源作用范围在命名空间或集群
  names: 
  #names 指的是它的 kind 是什么，比如 Deployment 的 kind 就是 Deployment，Pod 的 kind 就是 Pod，这里的 kind 被定义为了CronTab
    plural: crontabs
    singular: crontab
    kind: CronTab
    shortNames:
    - ct
EOF
~~~

- 创建资源

~~~sh
kubectl apply  -f crontab-crd.yaml
kubectl get crd
kubectl get ct
~~~

# 创建CRD的对象实例

~~~yaml
tee my-crontab.yaml <<'EOF'
apiVersion: "stable.example.com/v1"
kind: CronTab
metadata:
  name: my-new-cron-object
spec:
  cronSpec: "* * * * * *"
  image: busybox
EOF
kubectl apply -f my-crobtab.yaml
kubectl get CronTab
~~~

# 基于自定义CRD创建MongoDB资源

- 项目地址：https://github.com/mongodb/mongodb-kubernetes-operator.git