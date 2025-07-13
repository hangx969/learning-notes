# 介绍

- 是一款对k8s应用做身份验证的反向代理。工作模式有两种：

  ![image-20241121102327853](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202411211023948.png)

  在我们的示例中，使用的是右边的middleware模式，作用于ingress-nginx。

- 官网：https://oauth2-proxy.github.io/oauth2-proxy/installation/

- github：https://github.com/oauth2-proxy/oauth2-proxy

- releases page: https://github.com/oauth2-proxy/manifests/releases

- artifact hub: https://artifacthub.io/packages/helm/oauth2-proxy/oauth2-proxy

# 下载

~~~sh
helm repo add --force-update oauth2-proxy https://oauth2-proxy.github.io/manifests
helm repo update oauth2-proxy
helm pull oauth2-proxy/oauth2-proxy --version 7.7.1
~~~

# 配置oauth2proxy

## 创建redis password

oauth的sessionStorage选择使用redis，oauth helm chart会安装redis subchart。这里需要一个redis密码，保存到secret里面

~~~sh
export REDIS_PASSWD=$( openssl rand -base64 32 | head -c 32 | base64 )
kubectl -n oauth2-proxy create secret generic oauth2-proxy-redis --from-literal=redis-password=$REDIS_PASSWD
# 需要打上标签，后续安装helm的时候会被纳入到helm管理
kubectl label secrets oauth2-proxy-redis -n oauth2-proxy "app.kubernetes.io/managed-by"="Helm"
kubectl annotate secrets oauth2-proxy-redis -n oauth2-proxy "meta.helm.sh/release-name"="oauth2-proxy"
kubectl annotate secrets oauth2-proxy-redis -n oauth2-proxy "meta.helm.sh/release-namespace"="oauth2-proxy"
~~~

## 集成github认证

1. 先去github生成一个OauthAPP：([Developer applications](https://github.com/settings/developers))，复制`client id`和`client secret`。

   - application name：`oauth2proxy-local`

   - Homepage URL：https://oauth2proxy.hanxux.local/

   - Authorization callback URL：https://oauth2proxy.hanxux.local/oauth2/callback

2. 创建一个cookie secret

  ~~~sh
  export COOKIE_SECRET=$( openssl rand -base64 32 | head -c 32 | base64 )
  ~~~

3. oauth2proxy的values.yaml里面添加github认证相关参数

   ~~~yaml
   config:
     existingSecret: oauth2-proxy-creds
   extraArgs:
     provider: github
     whitelist-domain: .hanxux.local
     cookie-domain: .hanxux.local
   ~~~

4. 传入gitub oauth app的client id和secret

### 方法1-创建secret保存

- 创建k8s secret

  ~~~sh
  export CLIENT_ID="Ov23liF0QvSRG51yPKq1"
  export CLIENT_SECRET="xxx" # 需要复制出来之后直接写入github secrets
  kubectl create namespace oauth2-proxy
  kubectl -n oauth2-proxy create secret generic oauth2-proxy-creds --from-literal=cookie-secret=$COOKIE_SECRET --from-literal=client-id=$CLIENT_ID --from-literal=client-secret=$CLIENT_SECRET
  ~~~


### 方法2-直接写入values

- 注：上面创建secret的方式oauth2proxy没有读取到。遂采取直接把cookie_secret、client_id和client_secret三个参数直接写到values.yaml里面的方式

  ~~~yaml
  config:
    # Add config annotations
    annotations: {}
    # OAuth client ID
    clientID: "Ov23liF0QvSRG51yPKq1"
    # OAuth client secret
    clientSecret: "xxx"
    # Create a new secret with the following command
    # openssl rand -base64 32 | head -c 32 | base64
    # Use an existing secret for OAuth2 credentials (see secret.yaml for required fields)
    # Example:
    #existingSecret: oauth2-proxy-creds
    cookieSecret: "xxx"
    # The name of the cookie that oauth2-proxy will create
    # If left empty, it will default to the release name
    cookieName: ""
  ~~~


### 方法3-github secrets

- 后续修改了secret加载方式，先存到github repository secrets里面，再从workflow中读取

  ~~~sh
  export helmChartVersion=${{env.oauth2proxyVersion}}
  export helmRepoName='oauth2-proxy'
  export helmChartName='oauth2-proxy'
  export REDIS_PASSWORD=$(kubectl get secret --namespace "oauth2-proxy" oauth2-proxy-redis --kubeconfig $KUBECONFIG -o jsonpath="{.data.redis-password}" | base64 -d)
  
  helm upgrade -i oauth2-proxy -n oauth2-proxy \
  oci://${{ env.harborURL }}/${{ env.harborProjectName }}/$helmRepoName/$helmChartName \
  --version $helmChartVersion \
  --history-max 5 \
  -f ./base/external/oauth2-proxy/values.yaml \
  --set config.clientID='${{ secrets.OAUTH2PROXY_CLIENT_ID}}' \
  --set config.clientSecret='${{ secrets.OAUTH2PROXY_CLIENT_SECRET}}' \
  --set config.cookieSecret='${{ secrets.OAUTH2PROXY_COOKIE_SECRET}}' \
  --set global.redis.password=$REDIS_PASSWORD \
  --insecure-skip-tls-verify \
  --kubeconfig $KUBECONFIG
  ~~~

## 配置Https

- 首先部署出certmanager --> 创建clusterissuer --> 创建给oauth2proxy ingress https的secret --> helm values.yaml的ingress.tls部分配置secret、host

- 创建oauth2proxy的tls secret

~~~yaml
tee certificate-oauth2proxy.yaml <<'EOF'
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: cert-oauth2proxy
  namespace: oauth2-proxy
spec:
  secretName: oauth2proxy-tls-cert-secret
  privateKey:
    rotationPolicy: Always
  commonName: oauth2proxy.hanxux.local
  dnsNames:
    - oauth2proxy.hanxux.local
  usages:
    - digital signature
    - key encipherment
    - server auth
  issuerRef:
    name: selfsigned
    kind: ClusterIssuer
EOF
~~~

- oauth2proxy的values配置ingress tls

~~~yaml
ingress:
  enabled: true
  ingressClassName: nginx-default
  hosts:
  - oauth2proxy.hanxux.local
  tls:
  - secretName: oauth2proxy-tls-cert-secret
    hosts:
    - oauth2proxy.hanxux.local
  path: /
  # Only used if API capabilities (networking.k8s.io/v1) allow it
  pathType: ImplementationSpecific
~~~

# 安装

~~~sh
helm upgrade -i oauth2-proxy -n oauth2-proxy --create-namespace . -f values.yaml 
~~~

- 验证安装：`oauth2proxy.hanxux.local`也要加到本机hosts文件中，https访问hostname即可看到oauthproxy的主页，有用github登录的提示。由于lab用的是自签证书，所以浏览器会报连接不安全。

# 使用oauth2proxy保护其他app

- 在其他应用的ingress中添加annotations，详细说明参考ingress官网：https://kubernetes.github.io/ingress-nginx/examples/auth/oauth-external-auth/
- 这两个annotations会将请求redirect到oauth2proxy，由oauth2proxy将请求转发到配置的3rd party认证endpoint

~~~yaml
annotations:
  nginx.ingress.kubernetes.io/auth-url: "https://oauth2proxy.hanxux.local/oauth2/auth"
  nginx.ingress.kubernetes.io/auth-signin: "https://oauth2proxy.hanxux.local/oauth2/start?rd=https%3A%2F%2F<host>.hanxux.local"
~~~
