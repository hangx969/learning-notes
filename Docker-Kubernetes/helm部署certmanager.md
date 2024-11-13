# 介绍

- 使用certmanager，对cloudfare申请的域名签发证书：https://todoit.tech/k8s/cert/
- certmanager官网：https://cert-manager.io/docs/installation/helm/

- 使用 HTTPS 需要向CA申请证书，并且需要付出一定的成本，如果需求数量多，则开支也相对增加。[cert-manager](https://cert-manager.io/docs/) 是 Kubernetes 上的全能证书管理工具，支持利用 cert-manager 基于 [ACME](https://tools.ietf.org/html/rfc8555) 协议与[Let's Encrypt CA](https://letsencrypt.org/) 签发免费证书并为证书自动续期，实现永久免费使用证书。

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
  - issuer资源是让cert-manager认出证书颁发机构，比如指定letsencrypt；在issuer中也要指定dns resolver。
  - certificate资源就是绑定issuer资源和存放certificate的secret


## Issuer和certificate

- Let’s Encrypt CA 利用 ACME (Automated Certificate Management Environment，自动证书管理) 协议校验域名的归属，校验成功后可以自动颁发免费证书。免费证书有效期只有 90 天，需在到期前再校验一次实现续期。使用 cert-manager 可以自动续期，即实现永久使用免费证书。
- 校验域名归属的两种方式分别是 HTTP-01 和 DNS-01，校验原理详情可参见 [Let's Encrypt 的运作方式](https://letsencrypt.org/zh-cn/how-it-works/)

> - DNS-01检验是一种用于验证域名所有权的方法，通常用于颁发SSL/TLS证书。这个过程要求用户在其DNS设置中添加特定的TXT记录，以证明他们对该域名的控制权。在申请证书时，证书颁发机构（CA）将为用户的域名生成一个唯一的令牌，并要求用户在其域名下的DNS区域中添加该令牌对应的TXT记录。具体来说，当用户通过ACME（自动证书管理环境）客户端请求证书时，该客户端会接收到CA发送的随机令牌。用户需要在名为“_acme-challenge.<YOUR_DOMAIN>”的DNS记录中添加这个令牌。如果CA在查询该记录时找到了预期的TXT记录，就会认为用户对该域名拥有控制权，从而继续颁发证书。
> - HTTP-01检验是一种用于验证域名所有权的方式，通常在申请和续期SSL/TLS证书时使用。这种验证方式是通过将特定的令牌放置在Web服务器的指定路径下，从而向证书颁发机构（CA）证明用户对该域名的控制权。

- 使用过程：

  - 域名注册可以使用[cloudflare](https://www.cloudflare.com/zh-cn/)，拿到cloudflare的API token，放到secret里。

  - 创建ClusterIssuer时提供cloudflare的token，这样cert-manager可以自动化向域名机构添加CA要求的认证信息，完成证书申请和renew。

  - 创建certificate，指定ClusterIssuer和要保存到哪个secret，完成证书的签发。（注意Let's Encrypt 一个星期内只为同一个域名颁发 5 次证书，todoit.tech 和 whoami.todoit.tech 被视为不同的域名。）

  - 后续真正创建业务pod和ingress的时候就可以指定域名和证书，例如：

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
    ---
    apiVersion: networking.k8s.io/v1
    kind: Ingress
    metadata:
      name: whoami-ingress
      annotations:
        kubernetes.io/ingress.class: nginx
        nginx.ingress.kubernetes.io/rewrite-target: /
    spec:
      tls: #tls字段配置域名和保存证书的secret名称
        - hosts:
            - "whoami.todoit.tech"
          secretName: wildcard-letsencrypt-tls
      rules:
        - host: whoami.todoit.tech
          http:
            paths:
              - path: /
                pathType: Prefix
                backend:
                  service:
                    name: whoami
                    port:
                      number: 80
    ~~~


# 教程

- pod间TLS通信：https://www.youtube.com/watch?v=uTaXgZWwXzs&list=PLpbcUe4chE79sB7Jg7B4z3HytqUUEwcNE&index=93
- certmanager教程：https://www.youtube.com/watch?v=rOe9UpHcnKk&list=PLpbcUe4chE79sB7Jg7B4z3HytqUUEwcNE&index=96
