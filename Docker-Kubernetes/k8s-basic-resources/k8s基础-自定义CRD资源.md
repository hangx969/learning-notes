# Operator

- Kubernetes Operator模式是一种自定义控制器的开发模式，它允许开发人员扩展Kubernetes的功能，以管理和自动化特定的应用程序、服务或基础设施。Operator模式利用Kubernetes的自动化、可伸缩和故障恢复功能，使应用程序可以以一种声明性的方式进行管理。
- 在Operator模式中，开发人员使用自定义控制器来监视、管理和调节应用程序的状态。控制器会根据定义的规则和策略，对资源进行创建、更新和删除操作，以确保应用程序按预期运行。为了开发Operator，通常需要使用自定义资源定义（Custom Resource Definition，CRD）来描述应用程序的自定义资源类型。

# CRD

- https://mp.weixin.qq.com/s/Ts9MxQOpQVaUtw6YbHXogw
- CRD全称是CustomResourceDefinition：
  - 在 Kubernetes 中一切都可视为资源，Kubernetes 1.7 之后增加了对 CRD 自定义资源二次开发能力来扩展 Kubernetes API，通过 CRD 我们可以向 Kubernetes API 中增加新资源类型，而不需要修改 Kubernetes 源码来创建自定义的 API server，该功能大大提高了 Kubernetes 的扩展能力。
  - 当你创建一个新的(CRD)时，Kubernetes API服务器将为你指定的每个版本创建一个新的RESTful资源路径，我们可以根据该api路径来创建一些我们自己定义的类型资源。
  - CRD可以是命名空间的，也可以是集群范围的，由CRD的作用域(scpoe)字段中所指定的，与现有的内置对象一样，删除名称空间将删除该名称空间中的所有自定义对象。CRD本身没有名称空间，所有名称空间都可以使用。

# 自定义CRD资源-crontab

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

- CRD的对象实例

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

- 可以看到对应类型资源已经创建成功；以上示例只是单纯的crd的使用示例，没有任何实质的作用

# 自定义CRD-MongoDB

- 项目地址：https://github.com/mongodb/mongodb-kubernetes-operator.git （使用0.5.0版本）
- 下载operator压缩包mongodb-kubernetes-operator-0.5.0.zip
- 创建crd

~~~sh
kubectl create ns mongodb
cd mongodb-kubernetes-operator-0.5.0
kubectl apply -f deploy/crds/mongodb.com_mongodbcommunity_crd.yaml
#查看mongodb是否创建成功
kubectl get crd/mongodbcommunity.mongodb.com
~~~

- 安装operator

~~~sh
kubectl apply -f deploy/operator/ -n mongodb
#mongodb-kubernetes-operator这个项目是将自定义控制器和自定义资源类型分开实现的；其operator只负责创建和监听对应资源类型的变化，在资源有变化时，实例化为对应资源对象，并保持对应资源对象状态吻合用户期望状态；上述四个清单中主要是创建了一个sa账户，并对对应的sa用户授权
#operator也是以pod形式运行
kubectl get pods -n mongodb
~~~

- 使用CRD创建一个mongoDB集群

~~~sh
cat deploy/crds/mongodb.com_v1_mongodbcommunity_cr.yaml
kubectl apply -f deploy/crds/mongodb.com_v1_mongodbcommunity_cr.yaml -n mongodb
kubectl get pods -n mongodb
#pod由于没有合适的PVC而创建失败，需要创建PV和PVC
kubectl get pvc -n mongodb
kubectl delete pvc --all -n mongodb
~~~

- 创建PV

~~~sh
#master节点创建nfs共享
mkdir /data/p1
mkdir /data/p2
mkdir /data/p3
tee /etc/exports <<'EOF'
/data/v1  *(rw,no_root_squash)
/data/p1  *(rw,no_root_squash)
/data/p2  *(rw,no_root_squash)
/data/p3  *(rw,no_root_squash)
exportfs -arv
~~~

~~~yaml
tee pv-demo.yaml <<'EOF'
apiVersion: v1
kind: PersistentVolume
metadata:
  name: nfs-pv-v1
  labels:
    app: example-mongodb-svc
spec:
  capacity:
    storage: 1Gi
  volumeMode: Filesystem
  accessModes: ["ReadWriteOnce","ReadWriteMany","ReadOnlyMany"]
  persistentVolumeReclaimPolicy: Retain
  mountOptions:
  - hard
  - nfsvers=4.1
  nfs:
    path: /data/p1
    server: 192.168.40.180
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: nfs-pv-v2
  labels:
    app: example-mongodb-svc
spec:
  capacity:
    storage: 1Gi
  volumeMode: Filesystem
  accessModes: ["ReadWriteOnce","ReadWriteMany","ReadOnlyMany"]
  persistentVolumeReclaimPolicy: Retain
  mountOptions:
  - hard
  - nfsvers=4.1
  nfs:
    path: /data/p2
    server: 192.168.40.180
---
 
apiVersion: v1
kind: PersistentVolume
metadata:
  name: nfs-pv-v3
  labels:
    app: example-mongodb-svc
spec:
  capacity:
    storage: 1Gi
  volumeMode: Filesystem
  accessModes: ["ReadWriteOnce","ReadWriteMany","ReadOnlyMany"]
  persistentVolumeReclaimPolicy: Retain
  mountOptions:
  - hard
  - nfsvers=4.1
  nfs:
    path: /data/p3
    server: 192.168.40.180
EOF
~~~

- 创建PVC

~~~yaml
tee pvc-demo.yaml <<'EOF' 
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data-volume-example-mongodb-0
  namespace: mongodb
spec:
  accessModes:
    - ReadWriteMany
  volumeMode: Filesystem
  resources:
    requests:
      storage: 500Mi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data-volume-example-mongodb-1
  namespace: mongodb
spec:
  accessModes:
    - ReadWriteMany
  volumeMode: Filesystem
  resources:
    requests:
      storage: 500Mi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data-volume-example-mongodb-2
  namespace: mongodb
spec:
  accessModes:
    - ReadWriteMany
  volumeMode: Filesystem
  resources:
    requests:
      storage: 500M
~~~



# 自定义CRD资源-Etcd

> Etcd是一个分布式键值存储系统，常用于存储共享配置和服务发现等场景。Etcd Operator是一个基于Operator模式开发的控制器，用于在Kubernetes上管理和运行Etcd集群。
>
> 1. 自定义资源定义（CRD）：Etcd Operator定义了一个自定义资源类型EtcdCluster，用于描述Etcd集群的配置和规模。这个CRD定义了Etcd集群的规格，包括节点数量、存储大小、版本等信息。
> 2. 控制器实现：Etcd Operator的控制器监视EtcdCluster资源的状态，并根据定义的规则执行相应的操作。例如，当创建一个新的EtcdCluster资源时，控制器会根据规格创建一个Etcd集群，并将其部署到Kubernetes集群中的适当位置。
> 3. 状态管理：Etcd Operator控制器负责监控Etcd集群的状态，并确保其符合预期。如果集群中的节点出现故障或状态不一致，控制器会自动进行故障恢复操作，例如替换故障节点或重新配置集群。
> 4. 扩展和自动化：Etcd Operator可以利用Kubernetes的自动伸缩功能，根据负载情况自动扩展Etcd集群的规模。控制器会根据指标和策略，自动增加或减少Etcd节点的数量，以适应应用程序的需求。
> 5. 通过Etcd Operator，用户可以以一种声明性的方式定义和管理Etcd集群。他们只需要创建和更新EtcdCluster资源，而不需要手动进行底层的配置和管理操作。Operator模式使Etcd集群的部署、运行和维护变得更加自动化和可靠。

1. 创建CRD

- 用于定义和管理EtcdCluster资源。这样，你可以创建、更新和删除EtcdCluster资源，并定义自定义的规格和状态字段来描述Etcd集群的配置和状态信息。

~~~sh
tee etcdcluster-crd.yaml <<'EOF'
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: etcdclusters.etcd.database.coreos.com
spec:
  group: etcd.database.coreos.com
  versions:
    - name: v1alpha1
      served: true
      storage: true
  scope: Namespaced
  names:
    plural: etcdclusters
    singular: etcdcluster
    kind: EtcdCluster
    shortNames:
      - etcd
EOF
~~~

2. 创建etcd operator控制器

- 监听EtcdCluster资源的事件，并根据事件类型执行相应的操作

~~~sh
tee etcd-operator.yaml <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: etcd-operator
spec:
  selector:
    matchLabels:
      app: etcd-operator
  replicas: 1
  template:
    metadata:
      labels:
        app: etcd-operator
    spec:
      containers:
        - name: etcd-operator
          image: your-etcd-operator-image
          # 添加你的Etcd Operator镜像信息
          args: ["--kubeconfig", "/path/to/kubeconfig"]
          # 根据需要添加额外的参数
EOF
~~~

- 镜像制作

  ~~~dockerfile
  FROM golang:1.16 as builder
  
  WORKDIR /app
  
  # 复制Etcd Operator的代码到容器中
  COPY . .
  
  # 编译Etcd Operator
  RUN go build -o etcd-operator .
  
  # 创建最终的镜像
  FROM alpine:latest
  RUN apk --no-cache add ca-certificates
  WORKDIR /root/
  COPY --from=builder /app/etcd-operator .
  CMD ["./etcd-operator"]
  ~~~

  ~~~sh
  docker build -t your-etcd-operator-image .
  ~~~

- etcd operator的代码

  ~~~go
  package main
  
  import (
  	"context"
  	"flag"
  	"fmt"
  	"log"
  	"os"
  	"path/filepath"
  	"time"
  
  	"github.com/coreos/etcd-operator/pkg/backup"
  	"github.com/coreos/etcd-operator/pkg/controller"
  	"github.com/coreos/etcd-operator/pkg/etcdapi"
  	"github.com/coreos/etcd-operator/pkg/util/constants"
  	"github.com/coreos/etcd-operator/pkg/util/k8sutil"
  	"github.com/spf13/pflag"
  	"k8s.io/apimachinery/pkg/util/wait"
  	"k8s.io/client-go/kubernetes"
  	"k8s.io/client-go/tools/clientcmd"
  )
  
  func main() {
  	kubeconfig := flag.String("kubeconfig", "", "Path to a kubeconfig file")
  	flag.Parse()
  
  	// 初始化Kubernetes客户端
  	config, err := clientcmd.BuildConfigFromFlags("", *kubeconfig)
  	if err != nil {
  		log.Fatal(err)
  	}
  	clientset, err := kubernetes.NewForConfig(config)
  	if err != nil {
  		log.Fatal(err)
  	}
  
  	// 创建EtcdOperator控制器
  	operator, err := createEtcdOperator(clientset, config)
  	if err != nil {
  		log.Fatal(err)
  	}
  
  	// 启动EtcdOperator控制器
  	err = operator.Run()
  	if err != nil {
  		log.Fatal(err)
  	}
  }
  
  func createEtcdOperator(clientset kubernetes.Interface, config *rest.Config) (*controller.Operator, error) {
  	operator := controller.NewEtcdOperator(clientset, config)
  
  	// 设置EtcdOperator的参数和配置
  	operator.Config.EtcdVolumeProvisioner = constants.DefaultEtcdVolumeProvisioner
  	operator.Config.PVProvisioner = constants.DefaultPVProvisioner
  	operator.Config.PodPolicy = constants.DefaultPodPolicy
  
  	// 设置处理EtcdCluster资源事件的回调函数
  	operator.OnAddEtcdCluster = handleEtcdClusterAdd
  	operator.OnUpdateEtcdCluster = handleEtcdClusterUpdate
  	operator.OnDeleteEtcdCluster = handleEtcdClusterDelete
  
  	return operator, nil
  }
  
  // 处理EtcdCluster资源的添加事件
  func handleEtcdClusterAdd(ctx context.Context, cluster *etcdapi.EtcdCluster) {
  	// 执行EtcdCluster资源添加事件的逻辑操作
  	fmt.Println("EtcdCluster added:", cluster.Name)
  }
  
  // 处理EtcdCluster资源的更新事件
  func handleEtcdClusterUpdate(ctx context.Context, oldCluster, newCluster *etcdapi.EtcdCluster) {
  	// 执行EtcdCluster资源更新事件的逻辑操作
  	fmt.Println("EtcdCluster updated:", newCluster.Name)
  }
  
  // 处理EtcdCluster资源的删除事件
  func handleEtcdClusterDelete(ctx context.Context, cluster *etcdapi.EtcdCluster) {
  	// 执行EtcdCluster资源删除事件的逻辑操作
  	fmt.Println("EtcdCluster deleted:", cluster.Name)
  }
  ~~~

3. 制作完前面的镜像、crd、operator后，可以创建一个EctdCluster的实例

~~~yaml
tee etcd-cluster.yaml <<'EOF'
apiVersion: etcd.database.coreos.com/v1alpha1
kind: EtcdCluster
metadata:
  name: my-etcd-cluster
spec:
  replicas: 3
  storage: 10Gi
EOF
~~~

> 注：一般而言k8s自带的api-resources够用，自定义CRD开发难度较大；一般二次开发是对coreDNS、kube-proxy做开发。