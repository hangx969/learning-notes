# kyverno

## 介绍

- 官网：https://kyverno.io/docs/

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
