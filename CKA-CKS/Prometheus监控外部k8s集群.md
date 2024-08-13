- prometheus装到单独的机器上，需要监控外部k8s集群

# 配置k8s的sa和授权

~~~sh
#新建monitor-sa的服务账号，通过clusterrolebing绑定到clusterrole上
kubectl create ns monitor-sa
kubectl create serviceaccount monitor -n monitor-sa
kubectl create clusterrolebinding monitor-clusterrolebinding  --clusterrole=cluster-admin  --serviceaccount=monitor-sa:monitor

#对user用户授权：
kubectl create clusterrolebinding anonymous-admin --clusterrole=cluster-admin --user=system:anonymous
kubectl create clusterrolebinding monitor-clusterrolebinding-2 --clusterrole=cluster-admin --user=system:serviceaccount:monitor:monitor-sa
#查看sa的secrets
kubectl get sa monitor -n monitor-sa -o yaml
##如果没有secrets，需要手动创建一个和sa绑定
tee secret-monitor-token.yaml <<'EOF'
apiVersion: v1
kind: Secret
type: kubernetes.io/service-account-token
metadata:
  name: monitor-token
  namespace: monitor-sa
  annotations:
    kubernetes.io/service-account.name: monitor
EOF
#获取token
kubectl get secret monitor-token -n monitor-sa -o jsonpath='{.data.token}' | base64 --decode
#token需要写入到安装prometheus机器的这个文件中
tee /usr/local/prometheus-2.37.6.linux-amd64/k8s_token <<'EOF'
<token>
EOF
~~~

# 安装kube-state-metrics

~~~sh
#在工作节点解压镜像
docker load -i kube-state-metrics_1_9_0.tar.gz
ctr -n=k8s.io images import kube-state-metrics_1_9_0.tar.gz
#部署
kubectl apply -f kube-state-metrics-rbac.yaml 
kubectl apply -f kube-state-metrics-deploy.yaml
kubectl apply -f kube-state-metrics-svc.yaml
~~~

# 配置prometheus

~~~sh
#在prometheus的机器上
cd /usr/local/prometheus-2.37.6.linux-amd64/
vim prometheus.yml
# my global config
global:
  scrape_interval: 15s # Set the scrape interval to every 15 seconds. Default is every 1 minute.
  evaluation_interval: 15s # Evaluate rules every 15 seconds. The default is every 1 minute.
  # scrape_timeout is set to the global default (10s).

# Alertmanager configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets:
           - 192.168.40.180:9093

# Load rules once and periodically evaluate them according to the global 'evaluation_interval'.
rule_files:
   - "/usr/local/prometheus-2.37.6.linux-amd64/rules.yml"
  # - "second_rules.yml"

# A scrape configuration containing exactly one endpoint to scrape:
# Here it's Prometheus itself.
# 指定监控哪些服务
scrape_configs:
  # The job name is added as a label `job=<job_name>` to any timeseries scraped from this config.
  - job_name: "prometheus"
    # metrics_path defaults to '/metrics'
    # scheme defaults to 'http'.
    static_configs:
      - targets: ["localhost:9090"]
  - job_name: 'xianchaonode1-node'
    static_configs:
      - targets: ['192.168.40.181:9100']
  - job_name: 'xianchaomaster1-node'
    static_configs:
      - targets: ['192.168.40.180:9100']
  - job_name: 'xianchaonode1-mysql'
    static_configs:
      - targets: ['192.168.40.181:9104']
  - job_name: 'xianchaonode1-nginx'
    static_configs:
       - targets: ['192.168.40.181:9913']
  - job_name: 'kubernetes-apiserver'
    bearer_token_file: /usr/local/prometheus-2.37.6.linux-amd64/k8s_token
    tls_config:
        ca_file: /etc/kubernetes/pki/ca.crt
        insecure_skip_verify: true
    kubernetes_sd_configs:
    - api_server: https://192.168.40.180:6443
      role: endpoints
      bearer_token_file: /usr/local/prometheus-2.37.6.linux-amd64/k8s_token
      tls_config:
        ca_file: /etc/kubernetes/pki/ca.crt
        insecure_skip_verify: true
    scheme: https
    relabel_configs:
      - source_labels: [__meta_kubernetes_namespace, __meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
        action: keep
        regex: default;kubernetes;https
  - job_name: 'kubernetes-pod-container'
    bearer_token_file: /usr/local/prometheus-2.37.6.linux-amd64/k8s_token
    tls_config:
        ca_file: /etc/kubernetes/pki/ca.crt
        insecure_skip_verify: true
    kubernetes_sd_configs:
    - api_server: https://192.168.40.180:6443
      role: endpoints
      bearer_token_file: /usr/local/prometheus-2.37.6.linux-amd64/k8s_token
      tls_config:
        ca_file: /etc/kubernetes/pki/ca.crt
        insecure_skip_verify: true
    scheme: https
    metrics_path: '/api/v1/nodes/xianchaonode1/proxy/metrics/cadvisor'
    relabel_configs:
    - source_labels: [__address__]
      regex: '(.+):.*'
      replacement: '192.168.40.180:6443'
      target_label: __address__
~~~

- 重启prometheus
- 测试是否能访问apiserver

~~~sh
#在安装prometheus机器上
curl --cacert /etc/kubernetes/pki/ca.crt --header "Authorization: Bearer $(cat /usr/local/prometheus-2.37.6.linux-amd64/k8s_token)" https://192.168.40.180:6443/metrics
~~~

- 亦可浏览器登录prometheus，看是否能访问api-server/metrics
  - Targets - kubernetes-apiserver