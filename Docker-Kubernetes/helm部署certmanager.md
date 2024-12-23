# 介绍

- 使用 HTTPS 需要向CA申请证书，并且需要付出一定的成本，如果需求数量多，则开支也相对增加。[cert-manager](https://cert-manager.io/docs/) 是 Kubernetes 上的全能证书管理工具，支持利用 cert-manager 基于 [ACME](https://tools.ietf.org/html/rfc8555) 协议与[Let's Encrypt CA](https://letsencrypt.org/) 签发免费证书并为证书自动续期，实现永久免费使用证书。
- certmanager官网：https://cert-manager.io/docs/installation/helm/
- pod间TLS通信：https://www.youtube.com/watch?v=uTaXgZWwXzs&list=PLpbcUe4chE79sB7Jg7B4z3HytqUUEwcNE&index=93
- certmanager教程：https://www.youtube.com/watch?v=rOe9UpHcnKk&list=PLpbcUe4chE79sB7Jg7B4z3HytqUUEwcNE&index=96

# 拉取

~~~sh
helm repo add jetstack https://charts.jetstack.io 
helm repo update jetstack
helm pull jetstack/cert-manager --version v1.16.1
~~~

# 配置

~~~yaml
#参照ado code调整
#注意：crds.enabled额外设置成true，crds.keep设置成true，因为cert-manager-cainjector需要这个crd才能正常工作
~~~

# 安装

~~~sh
helm upgrade -i cert-manager -n cert-manager . --values values.yaml --create-namespace
#可以使用下面命令检查pod是否是ready
kubectl wait --for=condition=Ready pods --all -n cert-manager
~~~

# 使用

- cert-manager服务部署好之后，可以创建issuer和certificate资源：（refer: https://todoit.tech/k8s/cert/#%E5%88%9B%E5%BB%BA-issuer）
  - issuer/clusterissuer是让cert-manager认出证书颁发机构，比如指定letsencrypt
  - certificate资源就是绑定issuer，创建存放certificate的k8s secret

## 使用Self-signed certificate

### 创建self-signed cluster issuer

- Lab为简化处理，不去连接CA机构，用自签证书代替。https://github.com/HoussemDellai/aks-course/blob/main/34_https_pod_certmanager_letsencrypt/certificate.yaml

~~~yaml
tee cluster-issuer-selfsigned <<'EOF'
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: selfsigned
spec:
  selfSigned: {}
EOF
~~~

### 创建Certificate颁发给svc

> 注意：cerfiticate和他生成的secret是一定在同一个namespace的

~~~yaml
tee certificate-app01.yaml <<'EOF'
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: app01
spec:
  secretName: app01-tls-cert-secret
  privateKey:
    rotationPolicy: Always
  commonName: app01.default.svc.cluster.local #写的是后面要部署的svc的name
  dnsNames:
    - app01.default.svc.cluster.local
  usages:
    - digital signature
    - key encipherment
    - server auth
  issuerRef:
    name: selfsigned
    kind: ClusterIssuer
EOF
~~~

~~~sh
#查看证书
k get clusterissuer,secret,certificate
NAME                                       READY   AGE
clusterissuer.cert-manager.io/selfsigned   True    5m27s

NAME                           TYPE                DATA   AGE
secret/app01-tls-cert-secret   kubernetes.io/tls   3      16s

NAME                                READY   SECRET                  AGE
certificate.cert-manager.io/app01   True    app01-tls-cert-secret   16s
~~~

### pod挂载certificate

- pod用volume挂载secret，用环境变量指定证书位置。app中需要提前配置好https 

~~~yaml
tee deploy-app01.yaml <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: app01
  name: app01
spec:
  replicas: 1
  selector:
    matchLabels:
      app: app01
  template:
    metadata:
      labels:
        app: app01
    spec:
      restartPolicy: Always
      volumes:
      - name: app01-tls
        secret:
          secretName: app01-tls-cert-secret
      containers:
      - name: app01
        image: us-docker.pkg.dev/google-samples/containers/gke/hello-app-tls:1.0
        ports:
        - containerPort: 8443
        volumeMounts:
          - name: app01-tls
            mountPath: /etc/tls
            readOnly: true
        env:
          - name: TLS_CERT
            value: /etc/tls/tls.crt
          - name: TLS_KEY
            value: /etc/tls/tls.key
---
apiVersion: v1
kind: Service
metadata:
  name: app01
  #namespace: monitoring
  labels:
    app: app01
spec:
  ports:
  - port: 443
    protocol: TCP
    targetPort: 8443
  selector:
    app: app01
  type: ClusterIP
EOF
~~~

- 创建完成之后，可以用命令行测试pod间访问：

  ~~~sh
  kubectl run nginx --image=nginx
  kubectl exec -it nginx -- curl --insecure https://app01.default.svc.cluster.local
  kubectl exec -it nginx -- curl --insecure -v https://app01.default.svc.cluster.local
  ~~~

### Certificate颁发给ingress

- 创建certificate时common name和dns name写ingress的hostname，证书保存到secret

- 创建ingress时，配置tls字段，指定secret name，例如：

  ~~~yaml
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

> 注意：pod只能挂载位于同一个namespace下的secret

## 使用Letsencrypt certificate

### 参考

- azure文档：https://learn.microsoft.com/en-us/previous-versions/azure/aks/ingress-tls?tabs=azure-cli#install-cert-manager
- 创建Issuer和ClusterIssuer可以去官网找例子：https://cert-manager.io/docs/configuration/acme/dns01/
- letsencrypt官网：https://letsencrypt.org/getting-started/

### 校验原理

Let’s Encrypt CA 利用 ACME (Automated Certificate Management Environment，自动证书管理) 协议校验域名的归属，校验成功后可以自动颁发免费证书。免费证书有效期只有 90 天，需在到期前再校验一次实现续期。使用 cert-manager 可以自动续期，即实现永久使用免费证书。

校验域名归属的两种方式分别是 HTTP-01 和 DNS-01，校验原理详情可参见 [Let's Encrypt 的运作方式](https://letsencrypt.org/zh-cn/how-it-works/)

> - 用户向clusterissuer提出申请证书请求，clusterissuer向letsencrypt机构申请证书，letsencrypt机构进行审核，假如申请的域名为www.nginxx.com,letsencrypt，机构会审核www.nginxx.com这个站点是不是你的？审核的方式有：http01和dns01。
>   - 使用http01的审核方式：letsencrypt机构会登录到www.nginxx.com，看看能不能访问成功，访问成功就证明是你的网站，我们现在测试环境为内网环境，letsencrypt访问不了；
>   - 使用dns01的审核方式：如果www.nginxx.com是你的站点，你肯定有dns服务器的操控权，在DNS服务器上生成一个api token，letsencrypt会尝试使用这个api token往DNS服务器写入内容，如果能写入成功，则说明www.nginxx.com站点是你的，就会审核通过。

### 使用cloudflare作为dns resolver

参考：https://www.cnblogs.com/renshengdezheli/p/18211540

#### 获取cloudflare的API Token

- 公网域名注册可以使用[cloudflare](https://www.cloudflare.com/zh-cn/)，拿到cloudflare的API token。

- 测试API Token：

~~~sh
curl -X GET "https://api.cloudflare.com/client/v4/user/tokens/verify" \
~~~

- letsencrypt通过我们创建的API令牌就可以往我们的cloudflare DNS服务器里写入内容，如果成功写入内容，则证明站点是我们的，则审核通过。

- 写入k8s secret

  ~~~yaml
  apiVersion: v1
  kind: Secret
  metadata:
    name: cloudflare-api-token-secret
  type: Opaque
  stringData:
    api-token: <API Token>
  ~~~

#### 创建cluster issuer

- 创建ClusterIssuer时提供cloudflare的token，这样cert-manager可以自动化向域名机构添加CA要求的认证信息，完成证书申请和renew。

~~~yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  #ClusterIssuer名字
  name: letsencrypt-dns01
spec:
  acme:
    privateKeySecretRef:
      name: letsencrypt-dns01
      #ClusterIssuer去https://acme-v02.api.letsencrypt.org/directory申请证书
    server: https://acme-v02.api.letsencrypt.org/directory
    solvers:
    - dns01:
        cloudflare:
          email: xxxxx
          #指定存储着API token的secret，secret的名字为cloudflare-api-token-secret，secret的key为api-token
          apiTokenSecretRef:
            key: api-token
            name: cloudflare-api-token-secret        
~~~

#### 申请证书

- 创建certificate，指定ClusterIssuer和要保存到哪个secret，完成证书的签发。（注意Let's Encrypt 一个星期内只为同一个域名颁发 5 次证书，todoit.tech 和 whoami.todoit.tech 被视为不同的域名。）

~~~yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  #cert-zheli-com是申请的证书名字
  name: cert-zheli-com
spec:
  dnsNames:
  #www.rengshengdezheli.xyz表示申请的证书只给www.rengshengdezheli.xyz用
  - www.rengshengdezheli.xyz
  issuerRef:
    kind: ClusterIssuer
    #name: letsencrypt-dns01表示使用哪个ClusterIssuer申请证书
    name: letsencrypt-dns01 
  #secretName: cert-zheli-com-tls表示申请到的证书放在哪个secret里面
  secretName: cert-zheli-com-tls 
~~~

- 查看相关资源

~~~sh
kubectl get certificate -o wide
kubectl get secrets -o wide
kubectl get certificaterequests.cert-manager.io -o wide
#查看challenges，challenges用来验证证书请求是否成功，当证书申请成功之后，challenges会消失，certificaterequests的READY状态变为True。
kubectl get challenges.acme.cert-manager.io -o wide
#secret由xxxx-btt2t变为xxxx-tls，现在证书就在xxxx-tls里面了。
~~~

#### 创建ingress挂载证书

- 通过ingress manifest配置secretName的方式，让ingress找到证书：

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-ingress
  annotations:
    kubernetes.io/ingress.class: "nginx"
spec:
  tls: 
  - hosts: 
    - www.rengshengdezheli.xyz
    secretName: cert-zheli-com-tls
  rules:
  - host: www.rengshengdezheli.xyz
    http:
      paths:
      #访问网址目录
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nginx1svc
            port:
              number: 80
~~~

- 创建业务pod和svc，例如：

  ~~~yaml
  # cert/whoami.yaml
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: whoami
    labels:
      app: containous
      name: whoami
  spec:
    replicas: 2
    selector:
      matchLabels:
        app: containous
        task: whoami
    template:
      metadata:
        labels:
          app: containous
          task: whoami
      spec:
        containers:
          - name: containouswhoami
            image: containous/whoami
            resources:
            ports:
              - containerPort: 80
  ---
  apiVersion: v1
  kind: Service
  metadata:
    name: whoami
  spec:
    ports:
      - name: http
        port: 80
    selector:
      app: containous
      task: whoami
    type: ClusterIP
  ~~~

#### 配置clusterissuer自动挂载证书

- 我们申请证书的步骤是创建certificate，然后clusterissuer使用certificate申请证书，最后带有certificate信息的secret和ingress一起使用。我们现在使用另外一种方法，创建ingress的时候自动让clusterissuer申请证书，不用创建certificate yaml文件。

- 添加cert-manager.io/cluster-issuer: "letsencrypt-dns01"表示使用名为letsencrypt-dns01的clusterissuer申请证书。

  当我们创建ingress规则之后，会自动使用名为letsencrypt-dns01的clusterissuer申请证书，申请的证书放在名为cert-zheli-com-tls的secret里

- 证书到期之后，clusterissuers会自动给我们续约的。

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-ingress
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt-dns01"
spec:
  tls: 
  - hosts: 
    - www.rengshengdezheli.xyz
    secretName: cert-zheli-com-tls
  rules:
  - host: www.rengshengdezheli.xyz
    http:
      paths:
      #访问网址目录
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nginx1svc
            port:
              number: 80
~~~

### 使用azure dns作为dns resolver

#### 创建cluster issuer

~~~yaml
tee cluster-issuer-letsencrypt.yaml <<'EOF'
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: 1003665363@qq.com
    privateKeySecretRef:
      name: letsencrypt
    solvers:
    - http01:
        ingress:
          class: nginx-default
          podTemplate:
            spec:
              nodeSelector:
                "kubernetes.io/os": linux
EOF
~~~

#### 创建certificate

~~~yaml
tee cert-letsencrypt-app01.yaml <<'EOF'
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: cert-letsencrypt-test
  namespace: default
spec:
  dnsNames:
  - app01.default.svc.cluster.local # 要签发证书的域名
  secretName: app01-tls-cert-secret-letsencrypt # 最终签发出来的证书会保存在这个 Secret 里面
  commonName: app01.default.svc.cluster.local
  usages:
    - digital signature
    - key encipherment
    - server auth
  privateKey:
    rotationPolicy: Always
  issuerRef:
    name: letsencrypt
    kind: ClusterIssuer
EOF
~~~

## 没有域名的情况下申请证书



# Troubleshooting

- 本地虚机中有时候操作certificate时会报错：

  ~~~sh
  Error from server (InternalError): Internal error occurred: failed calling webhook "webhook.cert-manager.io": failed to call webhook: Post "https://cert-manager-webhook.cert-manager.svc:443/validate?timeout=30s": tls: failed to verify certificate: x509: certificate has expired or is not yet valid: current time 2024-12-23T02:30:04Z is after 2024-12-20T02:19:54Z
  ~~~

  删掉cert-manager-webhook-86b8dc6c77-hczkm这个pod重建就好了

# helm管理配置文件

- cluster issuer、certificate等yaml文件都可以用helm去管理。

- 创建cert-manager-config目录，下面放Chart.yaml和values.yaml

  ~~~yaml
  tee Chart.yaml <<"EOF"
  apiVersion: v2
  name: commoninfra-cert-manager-config
  description: A Helm chart for cert manager configurations
  type: application
  version: 0.0.1
  appVersion: "0.0.1"
  EOF
  ~~~

- 创建template目录，里面放所有需要创建的yaml文件

- 安装

  ~~~sh
  helm upgrade -i commoninfra-cert-manager-config . --values ./values.yaml
  ~~~




