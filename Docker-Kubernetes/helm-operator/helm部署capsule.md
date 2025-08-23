# 介绍

- 官网：
  - https://github.com/projectcapsule/capsule/blob/main/docs/content/general/tutorial.md
  - https://capsule.clastix.io/docs/#kubernetes-multi-tenancy-made-easy
  - capsule release note：https://github.com/projectcapsule/capsule/releases/
  
- helm参数含义：https://github.com/projectcapsule/capsule/blob/main/charts/capsule/README.md#customize-the-installation
- 升级到capsule 0.7.x带来的crd管理方式改变：https://github.com/projectcapsule/capsule/blob/main/charts/capsule/README.md#upgrading-to-07x （CRDs可以随helm chart更新了）
- Tenant: capsule是管理multi tenant的工具，什么是tenant？tenant在capsule的语境下可以理解为：一组namespace，可以对其做RBAC授权、设置resource quota、network policy等。

# 下载

~~~sh
helm repo add --force-update projectcapsule https://projectcapsule.github.io/charts
helm repo update projectcapsule
helm pull projectcapsule/capsule --version 0.7.1
~~~

# 配置

- 我们ado中仅仅指定了capsuleUserGroups，用的是AAD的group
- capsuleUserGroups解释：用于配置可以访问和管理 Capsule 功能的用户组。在默认提供的 `values.yaml` 中，指定了 `capsuleUserGroups: ["capsule.clastix.io"]`，这意味着只有属于 `capsule.clastix.io` 这个用户组的用户或服务账户可以进行与 Capsule 相关的操作。
- 在后续创建tenant指定tenant owner时，tenant owner要被设置成capsule user group的一员。（user可以通过证书的O字段设置，group可以用外部idp的嵌套组，service account可以直接把capsule user group设置为system:serviceaccounts:tenant-system）

# 安装

~~~sh
helm upgrade -i capsule -n capsule-system --create-namespace . -f values.yaml
~~~

# 使用

## 创建user和group

- azure中可以直接用EntraID with Azure RBAC的模式把entraID group

- lab中：先创建一个user

  - SSL认证

    ```bash
    #生成私钥
    cd /etc/kubernetes/pki/
    umask 077
    openssl genrsa -out hangx.key 2048
    #生成证书请求，需要给tenant owner赋予capsule-user-group，默认是capsule.clastix.io
    openssl req -new -key hangx.key -out hangx.csr -subj "/CN=hangx/O=capsule.clastix.io"
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
    ```

  - 配置linux客户端的用户，让他能用hangx的config文件访问集群

    ```bash
    adduser hangx
    #config文件的拷贝：得把/root/.kube/一整个目录拷贝过去
    cp -ar /root/.kube/ /tmp/
    #修改/tmp/.kube/config文件，把kubernetes-admin相关的删除，只留hangx用户；current context切换到hangx用户
    vim /tmp/.kube/config
    #kubeconfig文件拷贝到这个用户的家目录
    cp -ar /tmp/.kube/ /home/hangx/
    #root用户下操作，修改.kube目录的属主、属组为hangx
    chown -R hangx.hangx /home/hangx/.kube
    #切换用户
    su - hangx
    #验证权限
    k get po -A
    ```


## helm创建tenant

- templates下面放tenant、role、rolebinding等

- tenant.yaml --> 创建tenant

~~~yaml
{{- range .Values.teams }}
apiVersion: capsule.clastix.io/v1beta2
kind: Tenant
metadata:
  name: team-{{- .name }}
  labels:
    team: team-{{- .name }}
spec:
  owners:
  - name: hangx
    kind: User
  namespaceOptions:                    
    quota: 100
  ingressOptions:
    hostnameCollisionScope: Cluster
    allowWildcardHostnames: false
  resourceQuotas:
    scope: Tenant                 # tenant level quota (each node -> 3860m cpu=4 cores, 16G memory)
    items:
    - hard:
        limits.cpu: "64"
        limits.memory: "128Gi"
        requests.cpu: "20"
        requests.memory: "70Gi"
        requests.storage: "100Gi"
        count/persistentvolumeclaims: 30
        count/services: 100
        count/secrets: 300 
        count/configmaps: 200
        count/ingresses.networking.k8s.io: 70
        count/alertmanagerconfigs.monitoring.coreos.com: 30
        count/serviceaccounts: 100
        count/networkpolicies.networking.k8s.io: 30
        count/issuers.cert-manager.io: 10
        count/certificates.cert-manager.io: 70
        count/daemonsets.apps: 0                     # none of the teams should be able to deploy daemonsets
        count/deployments.apps: 70
        count/replicasets.apps: 700                  # considering we keep 10 history for all deplos, daemonsets and statefulsets
        count/statefulsets.apps: 30
        count/jobs.batch: 200
        count/cronjobs.batch: 50
        count/pod: 210
  limitRanges:                    # pod and container level (nodes spec -> 3860m cpu=4 cores, 16G memory)
    items:
    - limits:
      - type: Container           # container-level
        defaultRequest:           # default request
          cpu: "100m"
          memory: "100Mi"
        default:                  # default limits
          cpu: "100m"
          memory: "100Mi"
        min:                      # min (request)
          cpu: "10m"
          memory: "20Mi"
        max:                      # max (limit)
          cpu: "4"
          memory: "15Gi"
    - limits:                     # pod-level
      - type: Pod
        min:                      # min (request) - sum of all containers
          cpu: "10m"
          memory: "20Mi"
        max:                      # max (limit) - sum of all containers
          cpu: "6"
          memory: "15Gi"
    - limits:                     # pod-level
      - type: PersistentVolumeClaim
        min:
          storage: "50Mi"
        max:
          storage: "256Gi"
  networkPolicies:                # temporary permit all in/out traffics (should be modified or removed later when users added their own netPol)                      
    items:
    - policyTypes:
      - Ingress
      - Egress
      egress:                               
      - {}
      ingress:
      - {}
      podSelector: {}
  preventDeletion: true
  additionalRoleBindings:                        # to access required CRDs
  - clusterRoleName: 'update-crds'
    subjects:
    - apiGroup: rbac.authorization.k8s.io
      kind: User
      name: hangx
      namespace: tenant-system
---
{{- end }}
~~~

- tenant_roles.yaml

~~~yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: update-crds
rules:
- apiGroups:
  - monitoring.coreos.com
  resources:
  - alertmanagerconfigs
  - alertmanagers
  - podmonitors
  - prometheusrules
  - scrapeconfigs
  - servicemonitors
  verbs:
  - create
  - get
  - list
  - watch
  - update
  - patch
  - delete
- apiGroups:
  - cert-manager.io
  resources:
  - certificates        # for custom certificates
  - issuers             # for custom issuers
  verbs:
  - create
  - get
  - list
  - watch
  - update
  - patch
  - delete
- apiGroups:
  - snapshot.storage.k8s.io
  resources:
  - volumesnapshotclasses
  - volumesnapshotcontents
  - volumesnapshots
  verbs:
  - create
  - get
  - list
  - watch
  - update
  - patch
  - delete

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: pv-creator
rules:
- apiGroups:
  - ""
  resources:
  - persistentvolumes
  verbs:
  - get
  - list
  - watch
  - create

{{- if .Values.extended_port_forward }}
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: monitoring-port-forward
  namespace: monitoring
rules:
- apiGroups:
  - ""
  resources:
  - pods/portforward
  verbs:
  - get
  - list
  - watch
  - create
{{- end }}
~~~

- tenant_role_binding.yaml

~~~yaml
{{- if .Values.extended_port_forward }}
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  labels:
    capsule-teams: "true"
  namespace: monitoring
  name: monitoring-port-forward
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: monitoring-port-forward
subjects:
{{- range .Values.teams }}
- apiGroup: rbac.authorization.k8s.io
  kind: User
  name: {{ .name }}
{{- end }}

{{- end }}
~~~

- tenant_cluster_role_bindings

~~~yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  labels:
    capsule-teams: "true"
  name: capsule-global-reader
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: view
subjects:
- apiGroup: rbac.authorization.k8s.io
  kind: Group
  name: system:authenticated
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: alertmanagerconfigs-viewer
roleRef:
  kind: ClusterRole
  name: alertmanagerconfigs-viewer
  apiGroup: rbac.authorization.k8s.io
subjects:
- apiGroup: rbac.authorization.k8s.io
  kind: Group
  name: system:authenticated
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  labels:
    capsule-teams: "true"
  name: pv-creator-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: pv-creator
subjects:
{{- range .Values.teams }}
- apiGroup: rbac.authorization.k8s.io
  kind: User
  name: {{ .name }}
{{- end }}
~~~

- additional_default_permissions.yaml --> 用来在tenant level给用户赋予默认权限，就是tenant.yaml里面的additionalRoleBindings字段

~~~yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: additional-cluster-view
rules:
- apiGroups:
  - apiextensions.k8s.io
  resources:
  # for OpenLens
  - customresourcedefinitions
  verbs:
  - get
  - list
  - watch
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  labels:
    capsule-teams: "true"
  name: additional-cluster-reader
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: additional-cluster-view
subjects:
- apiGroup: rbac.authorization.k8s.io
  kind: Group
  name: system:authenticated
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: alertmanagerconfigs-viewer
rules:
- apiGroups: ["monitoring.coreos.com"]
  resources: ["alertmanagers", "alertmanagerconfigs"]
  verbs: ["get", "list", "watch"]
~~~

- 部署

~~~sh
helm upgrade -i commoninfra-capsule-tenants -n kube-system . --values ./values/dev.chinanorth3.yaml
~~~

- 切换到hangx user，可以在tenant中创建ns

~~~sh
#检查是否有权限创建ns
kubectl auth can-i create namespaces
kubectl auth can-i delete ns -n hangx-helm-release
~~~

- 如果user是多个tenant的owner，在capsule values中开启了forceTenantPrefix选项，则根据ns的前缀匹配到tenant中；否则，需要显式在ns的label中指定tenant。不指定的话就会报错：Unable to assign namespace to tenant. Please use capsule.clastix.io/tenant label when creating a namespace

~~~yaml
kubectl apply -f - << EOF
kind: Namespace
apiVersion: v1
metadata:
  name: team-hangx-helm-release-2
  labels:
    capsule.clastix.io/tenant: team-hangx-2
EOF
~~~

## tenant层面的配置

- resource、ingress、priority class、storage class、network policies、image registries、label/annotations等等都可以在tenant层面进行配置。详见官网：https://capsule.clastix.io/docs/general/tutorial/

- 值得注意的是，PVC是namespaces-scoped的资源，但是PV不是；在一个tenant下创建的PVC只能挂载本tenant下的PV，怎么给PV指定tenant呢?

  ~~~yaml
  apiVersion: v1
  kind: PersistentVolume
  metadata:
    labels:
      capsule.clastix.io/tenant: atreides
    name: pvc-1b3aa814-3b0c-4912-9bd9-112820da38fe
  ...
  ~~~


## dashboard

- 对于已经部署好prometheus stack的集群来说，可以直接在capsule的helm中开启service monitor功能，配置prometheus抓取数据、grafana展示，详情参考：https://capsule.clastix.io/docs/guides/monitoring#quick-start

# webhook

capsule会定义两种webhook：

~~~sh
kubectl edit mutatingwebhookconfiguration capsule-mutating-webhook-configuration
kubectl edit Validatingwebhookconfigurations capsule-validating-webhook-configuration
~~~

作用如下：

1. **MutatingWebhookConfiguration**

   定义了在API请求处理过程中触发的Mutating Webhook。这些Webhook可以在资源被持久化到etcd之前修改资源的内容。例如，Capsule可能会使用Mutating Webhook来自动为命名空间添加特定的标签或注解，或者修改Pod的配置以符合多租户环境的要求。

2. **ValidatingWebhookConfiguration**

   定义了在API请求处理过程中触发的Validating Webhook。这些Webhook用于验证资源是否符合特定的规则或策略。如果资源不符合要求，Validating Webhook可以拒绝该请求。例如，Capsule可能会使用Validating Webhook来确保租户无法创建不符合Capsule策略的资源（如超出配额限制的命名空间或Pod）。

如果capsule pod删除报错或者遇到其他capsule webhook阻止的情况，可以通过上述命令修改wehbook中的failurePolicy: Fail字段为failurePolicy: Ignore

