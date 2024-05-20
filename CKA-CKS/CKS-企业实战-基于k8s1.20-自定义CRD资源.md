# CRD

https://mp.weixin.qq.com/s/Ts9MxQOpQVaUtw6YbHXogw

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