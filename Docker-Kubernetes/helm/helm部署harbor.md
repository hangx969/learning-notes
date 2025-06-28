# 介绍

- 基于OCI的注册中心

  - 从Helm 3开始，可以使用具有 OCI支持的容器注册中心来存储和共享chart包。从Helm v3.8.0开始，默认启用OCI支持。


  - 以下是几种chart可以使用的托管容器注册中心，都支持OCI，例如：

    - Amazon ECR

    - Azure Container Registry

    - Docker Hub

    - Google Artifact Registry

    - IBM Cloud Container Registry

    - JFrog Artifactory


  - 同样的，harbor作为是一款云原生制品仓库，可以存储和管理容器镜像、Helm Chart 等 Artifact，同样启用了OCI支持。


- 文档：https://goharbor.io/docs/main/working-with-projects/working-with-oci/working-with-helm-oci-charts/
- github release: https://github.com/goharbor/harbor-helm/releases
- artifact hub: https://artifacthub.io/packages/helm/harbor/harbor

# 下载

~~~sh
helm repo add harbor https://helm.goharbor.io
helm repo update harbor
helm pull harbor/harbor
~~~

# 配置

- 提前创建好tls证书

  ~~~yaml
  apiVersion: cert-manager.io/v1
  kind: Certificate
  metadata:
    name: cert-harbor
    namespace: harbor
  spec:
    secretName: harbor-tls-cert-secret
    privateKey:
      rotationPolicy: Always
    commonName: harbor.hanxux.local
    dnsNames:
      - harbor.hanxux.local
    usages:
      - digital signature
      - key encipherment
      - server auth
    issuerRef:
      name: selfsigned
      kind: ClusterIssuer
  ~~~

- 配置ingress，storage

~~~yaml
expose:
  # Set how to expose the service. Set the type as "ingress", "clusterIP", "nodePort" or "loadBalancer"
  # and fill the information in the corresponding section
  type: ingress
  tls:
    # Enable TLS or not.
    # Delete the "ssl-redirect" annotations in "expose.ingress.annotations" when TLS is disabled and "expose.type" is "ingress"
    # Note: if the "expose.type" is "ingress" and TLS is disabled,
    # the port must be included in the command when pulling/pushing images.
    # Refer to https://github.com/goharbor/harbor/issues/5291 for details.
    enabled: true
    # The source of the tls certificate. Set as "auto", "secret"
    # or "none" and fill the information in the corresponding section
    # 1) auto: generate the tls certificate automatically
    # 2) secret: read the tls certificate from the specified secret.
    # The tls certificate can be generated manually or by cert manager
    # 3) none: configure no tls certificate for the ingress. If the default
    # tls certificate is configured in the ingress controller, choose this option
    certSource: secret
    auto:
      # The common name used to generate the certificate, it's necessary
      # when the type isn't "ingress"
      commonName: ""
    secret:
      # The name of secret which contains keys named:
      # "tls.crt" - the certificate
      # "tls.key" - the private key
      secretName: "harbor-tls-cert-secret"
  ingress:
    hosts:
      core: harbor.hanxux.local
    # set to the type of ingress controller if it has specific requirements.
    # leave as `default` for most ingress controllers.
    # set to `gce` if using the GCE ingress controller
    # set to `ncp` if using the NCP (NSX-T Container Plugin) ingress controller
    # set to `alb` if using the ALB ingress controller
    # set to `f5-bigip` if using the F5 BIG-IP ingress controller
    controller: default
    ## Allow .Capabilities.KubeVersion.Version to be overridden while creating ingress
    kubeVersionOverride: ""
    className: "nginx-default"
    annotations:
      # note different ingress controllers may require a different ssl-redirect annotation
      # for Envoy, use ingress.kubernetes.io/force-ssl-redirect: "true" and remove the nginx lines below
      ingress.kubernetes.io/ssl-redirect: "true"
      ingress.kubernetes.io/proxy-body-size: "0"
      nginx.ingress.kubernetes.io/ssl-redirect: "true"
      nginx.ingress.kubernetes.io/proxy-body-size: "0"
      #开启oauth2proxy认证之后，helm registry login就会失败
      #nginx.ingress.kubernetes.io/auth-url: "https://oauth2proxy.hanxux.local/oauth2/auth"
      #nginx.ingress.kubernetes.io/auth-signin: "https://oauth2proxy.hanxux.local/oauth2/start?rd=https%3A%2F%2Fharbor.hanxux.local"
    # ingress-specific labels
    labels: {}
...
#这里要配置external URL，为后面helm registry login用。
#这里不配置的话，会报错：Error: Get "https://harbor.hanxux.local/v2/": Get "/service/token?account=admin&client_id=docker&offline_token=true&service=harbor-registry": unsupported protocol scheme ""
externalURL: "https://harbor.hanxux.local"
~~~

- DB和redis都配置为internal类型，harbor helm chart会自动创建相关数据库pod
- persistence中storage的accessMode都修改为ReadWriteMany，注意这个选项需要再首次安装的时候就制定好，否则PVC创建出来之后就无法通过helm upgrade去patch了。

# 安装

~~~sh
helm upgrade -i harbor -n harbor . -f values.yaml
~~~

# 使用

- `harbor.hanxux.local`访问harbor-ui
- 默认用户名密码：admin/Harbor12345

## docker推送image到harbor

- 修改docker配置文件

  ~~~sh
  vim /etc/docker/daemon.json
  #添加docker登录harbor的http设置
  "insecure-registries": ["172.16.183.100","harbor.hanxux.local"]
  # 重启docker
  systemctl daemon-reload
  systemctl restart docker.service
  ~~~

- 登录harbor

  ~~~sh
  docker login harbor.hanxux.local
  #使用默认用户名和密码登录
  ~~~

- 推送镜像

  ~~~sh
  docker tag appscode/kubed:v0.13.2_linux_amd64 harbor.hanxux.local/platform-external/appscode/kubed:v0.13.2_linux_amd64
  docker push harbor.hanxux.local/platform-external/appscode/kubed:v0.13.2_linux_amd64
  ~~~

## 推送Helm Chart到harbor

harbor版本大于等于2.8，按照下面的命令直接推送chart即可。Harbor中Charts与Image保存在相同目录下，没有单独的页面。

```sh
# 登录helm仓库
helm registry login harbor.hanxux.local --insecure
# 打包chart，需要cd到chart目录里面打包所有文件才行。否则会报错Error: Chart.yaml file is missing
helm package .
# 提前在harbor中创建好harbor项目。上传不再支持UI界面，必须使用helm push
helm push commoninfra-0.0.1.tgz oci://harbor.hanxux.local/platform-external/
#Error: failed to do request: Head "https://harbor.hanxux.local/v2/library/my-hello/blobs/sha256:0db1fb6272f773572edb9ebad8c7fb902a76166bf14d896d3790f2a82f524838": tls: failed to verify certificate: x509: certificate signed by unknown authority
# --insecure-skip-tls-verify跳过tls验证
helm push commoninfra-0.0.1.tgz oci://harbor.hanxux.local/platform-external/ --insecure-skip-tls-verify
# 下载chart执行下面命令，命令可以从harbor界面复制
helm pull oci://harbor.hanxux.local/platform-external/commoninfra --version 0.0.1 -insecure-skip-tls-verify
```

这样就实现了chart上传到harbor仓库。

## 修改第三方chart重新打包推送到harbor

- 这里演示将harbor的官方chart从官方仓库下载后，修改镜像仓库地址，重新打包上传到私有仓库harbor，方便内部后续进行部署。

```sh
# 下载harbor官方的helm chart，这里可以换成其他chart进行测试
helm repo add harbor https://helm.goharbor.io
helm repo update
helm pull harbor/harbor
tar xf harbor-1.15.0.tgz
cd harbor
# 修改value.yaml中的镜像仓库为私有harbor
sed -i 's/repository: goharbor/repository: harbor.hanxux.local\/harbor/g' values.yaml
# 重新打包chart
helm package .
```

- 将chart推送到harbor：

```sh
helm push harbor-1.15.0.tgz oci://harbor.hanxux.local/harbor --insecure-skip-tls-verify
```

- 拉取部署chart所需的容器镜像并重新打tag推送到harbor，该过程通过如下脚本进行：

```sh
# 脚本内容
cat images-pull-push-2-harbor.sh
NAMESPACE="harbor"
kubectl get pods -n $NAMESPACE -o jsonpath="{range .items[*]}{.spec.containers[*].image}{'\n'}{end}" | sort |

NAMESPACE="harbor"              # 命名空间
HARBOR_URL="harbor.hanxux.local"    # harbor访问的域名
HARBOR_PROJECT="harbor"         # 镜像项目名称

# 获取所有Pod的镜像
IMAGES=$(kubectl get pods -n $NAMESPACE -o jsonpath="{range .items[*]}{.spec.containers[*].image}{'\n'}{end}" | sort | uniq)

# 登录Harbor
docker login $HARBOR_URL -u admin -p Harbor12345

# 拉取镜像、重新tag并推送到Harbor
for IMAGE in $IMAGES; do
  IMAGE_NAME=$(echo $IMAGE | awk -F'/' '{print $NF}')
  NEW_TAG="$HARBOR_URL/$HARBOR_PROJECT/$IMAGE_NAME"

  # 拉取原镜像
  docker pull $IMAGE

  # 重新tag镜像
  docker tag $IMAGE $NEW_TAG

  # 推送到Harbor
  docker push $NEW_TAG

  # 删除本地镜像
  docker rmi $IMAGE
  docker rmi $NEW_TAG
done

# 运行脚本
sh images-pull-push-2-harbor.sh
```

最终在harbor的harbor项目下，同时存放了harbor的chart和部署所需的镜像。

## 安装harbor中的helm chart

~~~sh
helm registry login harbor.hanxux.local --insecure
helm install <release_name> oci://<harbor_address>/<project>/<chart_name> --version <version> -f values.yaml --insecure-skip-tls-verify
~~~

