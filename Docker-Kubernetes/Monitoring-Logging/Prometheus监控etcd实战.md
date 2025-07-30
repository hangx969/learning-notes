# etcd的metrics接口

Etcd原生提供了Metrics接口，所以无需任何服务就可以直接监控Etcd。但是访问Etcd的Metrics接口需要使用证书，如下所示：

~~~sh
curl -s --cert /etc/kubernetes/pki/etcd/server.crt --key /etc/kubernetes/pki/etcd/server.key https://192.168.40.180:2379/metrics -k | tail -1
~~~

etcd的证书路径在哪里看？

~~~sh
cat /etc/kubernetes/manifests/etcd.yaml
# command下面
#     - --cert-file=/etc/kubernetes/pki/etcd/server.crt
#     - --key-file=/etc/kubernetes/pki/etcd/server.key
# 	  - --trusted-ca-file=/etc/kubernetes/pki/etcd/ca.crt
~~~

# etcd的svc

默认没有创建etcd的svc，给他创建一个。将endpoint的IP换成etcd的pod IP

~~~yaml
apiVersion: v1 
kind: Endpoints 
metadata:
  name: etcd-prom 
  namespace: kube-system 
  labels: 
    app: etcd-prom 
subsets: 
- addresses: 
  - ip: 192.168.40.180
  ports: 
  - name: https-metrics 
    port: 2379 # etcd端口 
    protocol: TCP 
--- 
apiVersion: v1 
kind: Service 
metadata: 
  name: etcd-prom 
  namespace: kube-system
  labels: 
    app: etcd-prom 
spec: 
  type: ClusterIP
  ports: 
  - name: https-metrics 
    port: 2379 
    protocol: TCP 
    targetPort: 2379 
~~~

访问svc clusterIP测试：

~~~sh
curl -s --cert /etc/kubernetes/pki/etcd/server.crt --key /etc/kubernetes/pki/etcd/server.key https://10.104.93.132:2379/metrics -k
~~~

# 创建secret并挂载

创建Etcd证书的Secret（证书路径根据实际环境进行更改）：

~~~sh
kubectl create secret generic etcd-ssl -n monitoring --from-file=/etc/kubernetes/pki/etcd/ca.crt --from-file=/etc/kubernetes/pki/etcd/server.key --from-file=/etc/kubernetes/pki/etcd/server.crt
~~~

接下来将证书挂载至Prometheus容器（如果Prometheus是Operator部署的，所以只需要修改Prometheus资源即可；helm chart部署的，就去values里面改prometheus的挂载）：

~~~yaml
prometheus:
  ingress:
    enabled: true
    ingressClassName: nginx-default
    annotations: {}
    labels: {}
    hosts:
      - prometheus.hanxux.local
    pathType: Prefix
    paths:
      - /
    tls: []
  prometheusSpec:
    enableRemoteWriteReceiver: true
    ## If true, a nil or {} value for prometheus.prometheusSpec.ruleSelector will cause the
    ## prometheus resource to be created with selectors based on values in the helm deployment,
    ## which will also match the PrometheusRule resources created
    ##
    ruleSelectorNilUsesHelmValues: false

    ## If true, a nil or {} value for prometheus.prometheusSpec.serviceMonitorSelector will cause the
    ## prometheus resource to be created with selectors based on values in the helm deployment,
    ## which will also match the servicemonitors created
    ##
    serviceMonitorSelectorNilUsesHelmValues: false

    ## If true, a nil or {} value for prometheus.prometheusSpec.podMonitorSelector will cause the
    ## prometheus resource to be created with selectors based on values in the helm deployment,
    ## which will also match the podmonitors created
    ##
    podMonitorSelectorNilUsesHelmValues: false

    retention: 7d

    ## Enable compression of the write-ahead log using Snappy.
    ##
    walCompression: false
    storageSpec:
      volumeClaimTemplate:
        spec:
          storageClassName: sc-nfs
          accessModes: ["ReadWriteOnce"]
          resources:
            requests:
              storage: 1Gi
    ## Secrets is a list of Secrets in the same namespace as the Prometheus object, which shall be mounted into the Prometheus Pods.
    ## The Secrets are mounted into /etc/prometheus/secrets/. Secrets changes after initial creation of a Prometheus object are not
    ## reflected in the running Pods. To change the secrets mounted into the Prometheus Pods, the object must be deleted and recreated
    ## with the new list of secrets.
    ##
    secrets:
    - etcd-ssl # 挂载etcd的证书，用于获取etcd metrics数据
~~~

# 创建serviceMonitor

~~~yaml
apiVersion: monitoring.coreos.com/v1 
kind: ServiceMonitor 
metadata: 
  name: etcd 
  namespace: monitoring 
  labels: 
    app: etcd 
spec: 
  jobLabel: k8s-app 
  endpoints: 
  - interval: 30s 
    port: https-metrics # 这个port对应 Service.spec.ports.name 
    scheme: https 
    tlsConfig: 
      caFile: /etc/prometheus/secrets/etcd-ssl/ca.crt #证书路径 
      certFile: /etc/prometheus/secrets/etcd-ssl/server.crt 
      keyFile: /etc/prometheus/secrets/etcd-ssl/server.key 
      insecureSkipVerify: true # 关闭证书校验 
  selector: 
    matchLabels: 
      app: etcd-prom # 跟svc的lables保持一致 
  namespaceSelector: 
    matchNames: 
      - kube-system
~~~

