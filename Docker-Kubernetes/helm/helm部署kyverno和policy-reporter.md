# kyverno

## 介绍

- 官网：https://kyverno.io/docs/

- release page: https://github.com/kyverno/kyverno/releases

- artifacthub: https://artifacthub.io/packages/helm/kyverno/kyverno/

- kyverno是希腊语的govern之意。是原生为K8s开发的策略引擎。

- kyverno在k8s中是作为admission controller来运行的，架构如下：

  ![image-20241122100328010](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202411221003152.png)

## 下载

~~~sh
helm repo add --force-update kyverno https://kyverno.github.io/kyverno
helm repo update kyverno
helm pull kyverno/kyverno --version 3.2.7
~~~

## 配置

~~~yaml
#仿照ado中的配置稍作调整
~~~

## 安装

~~~sh
helm upgrade -i kyverno -n kyverno --create-namespace . -f values.yaml
~~~

# kyverno policy

## 语法规则

https://mp.weixin.qq.com/s/5tANwfzp8C0O2GS8fkXErA

## 安装policy

~~~sh
export DIRECTORY="$(System.DefaultWorkingDirectory)/${{parameters.folder}}"
kubectl apply -f $DIRECTORY/external/kyverno/policies/common --recursive

if test -d "$DIRECTORY/external/kyverno/policies/${{parameters.region}}"; then
  kubectl apply -f $DIRECTORY/external/kyverno/policies/${{parameters.region}} --recursive
fi
~~~

# kyverno policy reporter

## 介绍

- kyverno自带的一个GUI界面，官网：
  - https://kyverno.io/docs/kyverno-policy-reporter/
  - https://kyverno.github.io/policy-reporter/
- release page: https://github.com/kyverno/policy-reporter/releases
- artifact hub: https://artifacthub.io/packages/helm/policy-reporter/policy-reporter

## 下载

~~~sh
helm repo add --force-update policy-reporter https://kyverno.github.io/policy-reporter
helm repo update policy-reporter
helm pull policy-reporter/policy-reporter --version 2.24.2
~~~

## 配置

- 创建policy-reporter的certificate

~~~yaml
kubectl create ns policy-reporter

tee certificate-policy-reporter.yaml <<'EOF'
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: cert-policy-reporter
  namespace: policy-reporter
spec:
  secretName: policy-reporter-tls-cert-secret
  privateKey:
    rotationPolicy: Always
  commonName: kyverno.hanxux.local
  dnsNames:
    - kyverno.hanxux.local
  usages:
    - digital signature
    - key encipherment
    - server auth
  issuerRef:
    name: selfsigned
    kind: ClusterIssuer
EOF
~~~

- 配置UI的ingress、oauth和https

~~~yaml
# Settings for the Policy Reporter UI subchart (see subchart's values.yaml)
ui:
  enabled: true
  create: true
  plugins:
    kyverno: true
  resources:
    limits:
      memory: 256Mi
      cpu: 300m
    requests:
      memory: 50Mi
      cpu: 100m
  ingress:
    enabled: true
    ingressClassName: nginx-default
    annotations:
      nginx.ingress.kubernetes.io/auth-url: "https://oauth2proxy.hanxux.local/oauth2/auth"
      nginx.ingress.kubernetes.io/auth-signin: "https://oauth2proxy.hanxux.local/oauth2/start?rd=https%3A%2F%2Fkyverno.hanxux.local"
    hosts:
    - host: kyverno.hanxux.local
      paths:
      - path: /
        pathType: Prefix
    tls:
      - secretName: policy-reporter-tls-cert-secret
        hosts:
          - kyverno.hanxux.local
~~~

## 安装

~~~sh
helm upgrade -i policy-reporter -n policy-reporter . -f values.yaml
~~~

## 配置告警

- 可以配置往loki和slack发消息：https://kyverno.github.io/policy-reporter/guide/helm-chart-core#enable-targets-notification

## 访问

https://kyverno.hanxux.local

# 实战--策略强制pod使用harbor中的镜像

安装harbor和kyverno完成后，可以定义一个Policy，使得某个namespace下的所有pod都必须使用harbor中的pod，否则请求会被拒绝。(假设harbor的URL为`registry.local.harbor`)

~~~yaml
cat disallow_any_repo.yaml <<'EOF'
apiVersion : kyverno.io/v1
kind: ClusterPolicy # 该策略的类型为ClusterPolicy，意思是在集群范围内部署
metadata:
  name: check-images
spec:
  validationFailureAction: Enforce #阻止任何不符合规则的请求。与之相对的是Audit，会将审计信息发送给审计工具，而不阻止。
  background: false
  rules:
  - name: check-registry
    match:
      any:
      - resources: #只检查app-namespace中的pod
          kinds:
          - Pod
          namespaces:
          - app-namespace

    preconditions:
      any:
      - key: "{{request.operation}}" #检查请求是否非删除操作，非删除操作的话才继续后续评估。
        operator: NotEquals
        value: DELETE
    validate:
      message: "unknown registry other than harbor"
      foreach:
      - list: "request.object.spec.initContainers"
        pattern:
          image: "registry.local.harbor/*"
      - list: "request.object.spec.containers"
        pattern:
          image: "registry.local.harbor/*"
EOF
~~~
