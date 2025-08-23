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
      #nginx.ingress.kubernetes.io/auth-url: "http://oauth2-proxy.oauth2-proxy.svc.cluster.local/oauth2/auth"
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

harbor版本大于等于2.8，支持OCI格式直接推送helm chart。按照下面的命令直接推送chart即可。Harbor中Charts与Image保存在相同目录下，没有单独的页面。

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
helm push commoninfra-0.0.1.tgz oci://harbor.hanxux.local/platform-external/ --plain-http # 也可以
# 下载chart：执行下面命令，命令可以从harbor界面复制
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

## containerd配置从harbor拉镜像

- containerd配置文件如下：

### 基于ip的harbor

~~~toml
disabled_plugins = []
imports = []
oom_score = 0
plugin_dir = ""
required_plugins = []
root = "/var/lib/containerd"
state = "/run/containerd"
temp = ""
version = 2

[cgroup]
  path = ""

[debug]
  address = ""
  format = ""
  gid = 0
  level = ""
  uid = 0

[grpc]
  address = "/run/containerd/containerd.sock"
  gid = 0
  max_recv_message_size = 16777216
  max_send_message_size = 16777216
  tcp_address = ""
  tcp_tls_ca = ""
  tcp_tls_cert = ""
  tcp_tls_key = ""
  uid = 0

[metrics]
  address = ""
  grpc_histogram = false

[plugins]

  [plugins."io.containerd.gc.v1.scheduler"]
    deletion_threshold = 0
    mutation_threshold = 100
    pause_threshold = 0.02
    schedule_delay = "0s"
    startup_delay = "100ms"

  [plugins."io.containerd.grpc.v1.cri"]
    device_ownership_from_security_context = false
    disable_apparmor = false
    disable_cgroup = false
    disable_hugetlb_controller = true
    disable_proc_mount = false
    disable_tcp_service = true
    enable_selinux = false
    enable_tls_streaming = false
    enable_unprivileged_icmp = false
    enable_unprivileged_ports = false
    ignore_image_defined_volumes = false
    max_concurrent_downloads = 3
    max_container_log_line_size = 16384
    netns_mounts_under_state_dir = false
    restrict_oom_score_adj = false
    sandbox_image = "registry.aliyuncs.com/google_containers/pause:3.7"
    selinux_category_range = 1024
    stats_collect_period = 10
    stream_idle_timeout = "4h0m0s"
    stream_server_address = "127.0.0.1"
    stream_server_port = "0"
    systemd_cgroup = false
    tolerate_missing_hugetlb_controller = true
    unset_seccomp_profile = ""

    [plugins."io.containerd.grpc.v1.cri".cni]
      bin_dir = "/opt/cni/bin"
      conf_dir = "/etc/cni/net.d"
      conf_template = ""
      ip_pref = ""
      max_conf_num = 1

    [plugins."io.containerd.grpc.v1.cri".containerd]
      default_runtime_name = "runc"
      disable_snapshot_annotations = true
      discard_unpacked_layers = false
      ignore_rdt_not_enabled_errors = false
      no_pivot = false
      snapshotter = "overlayfs"

      [plugins."io.containerd.grpc.v1.cri".containerd.default_runtime]
        base_runtime_spec = ""
        cni_conf_dir = ""
        cni_max_conf_num = 0
        container_annotations = []
        pod_annotations = []
        privileged_without_host_devices = false
        runtime_engine = ""
        runtime_path = ""
        runtime_root = ""
        runtime_type = ""

        [plugins."io.containerd.grpc.v1.cri".containerd.default_runtime.options]

      [plugins."io.containerd.grpc.v1.cri".containerd.runtimes]

        [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc]
          base_runtime_spec = ""
          cni_conf_dir = ""
          cni_max_conf_num = 0
          container_annotations = []
          pod_annotations = []
          privileged_without_host_devices = false
          runtime_engine = ""
          runtime_path = ""
          runtime_root = ""
          runtime_type = "io.containerd.runc.v2"

          [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
            BinaryName = ""
            CriuImagePath = ""
            CriuPath = ""
            CriuWorkPath = ""
            IoGid = 0
            IoUid = 0
            NoNewKeyring = false
            NoPivotRoot = false
            Root = ""
            ShimCgroup = ""
            SystemdCgroup = true

      [plugins."io.containerd.grpc.v1.cri".containerd.untrusted_workload_runtime]
        base_runtime_spec = ""
        cni_conf_dir = ""
        cni_max_conf_num = 0
        container_annotations = []
        pod_annotations = []
        privileged_without_host_devices = false
        runtime_engine = ""
        runtime_path = ""
        runtime_root = ""
        runtime_type = ""

        [plugins."io.containerd.grpc.v1.cri".containerd.untrusted_workload_runtime.options]

    [plugins."io.containerd.grpc.v1.cri".image_decryption]
      key_model = "node"

    [plugins."io.containerd.grpc.v1.cri".registry]
      config_path = ""

      [plugins."io.containerd.grpc.v1.cri".registry.auths]
      #=================这里是手动新加进来的 配置harbor模块=========================
      [plugins."io.containerd.grpc.v1.cri".registry.configs]
        [plugins."io.containerd.grpc.v1.cri".registry.configs."10.0.0.5".tls] #harbor server的Ip
            insecure_skip_verify = true
        [plugins."io.containerd.grpc.v1.cri".registry.configs."10.0.0.5".auth] #harbor server的Ip
            username = "admin" #配置账号密码
            password = "Harbor12345"

      [plugins."io.containerd.grpc.v1.cri".registry.headers]

      [plugins."io.containerd.grpc.v1.cri".registry.mirrors]
         [plugins."io.containerd.grpc.v1.cri".registry.mirrors."10.0.0.5"] #harbor server的Ip
            endpoint = ["https://10.0.0.5:443"] #harbor server的Ip
          [plugins."io.containerd.grpc.v1.cri".registry.mirrors."docker.io"]
             endpoint = ["https://vh3bm52y.mirror.aliyuncs.com","https://registry.docker-cn.com"]
    #==================================
    [plugins."io.containerd.grpc.v1.cri".x509_key_pair_streaming]
      tls_cert_file = ""
      tls_key_file = ""

  [plugins."io.containerd.internal.v1.opt"]
    path = "/opt/containerd"

  [plugins."io.containerd.internal.v1.restart"]
    interval = "10s"

  [plugins."io.containerd.internal.v1.tracing"]
    sampling_ratio = 1.0
    service_name = "containerd"

  [plugins."io.containerd.metadata.v1.bolt"]
    content_sharing_policy = "shared"

  [plugins."io.containerd.monitor.v1.cgroups"]
    no_prometheus = false

  [plugins."io.containerd.runtime.v1.linux"]
    no_shim = false
    runtime = "runc"
    runtime_root = ""
    shim = "containerd-shim"
    shim_debug = false

  [plugins."io.containerd.runtime.v2.task"]
    platforms = ["linux/amd64"]
    sched_core = false

  [plugins."io.containerd.service.v1.diff-service"]
    default = ["walking"]

  [plugins."io.containerd.service.v1.tasks-service"]
    rdt_config_file = ""

  [plugins."io.containerd.snapshotter.v1.aufs"]
    root_path = ""

  [plugins."io.containerd.snapshotter.v1.btrfs"]
    root_path = ""

  [plugins."io.containerd.snapshotter.v1.devmapper"]
    async_remove = false
    base_image_size = ""
    discard_blocks = false
    fs_options = ""
    fs_type = ""
    pool_name = ""
    root_path = ""

  [plugins."io.containerd.snapshotter.v1.native"]
    root_path = ""

  [plugins."io.containerd.snapshotter.v1.overlayfs"]
    root_path = ""
    upperdir_label = false

  [plugins."io.containerd.snapshotter.v1.zfs"]
    root_path = ""

  [plugins."io.containerd.tracing.processor.v1.otlp"]
    endpoint = ""
    insecure = false
    protocol = ""

[proxy_plugins]

[stream_processors]

  [stream_processors."io.containerd.ocicrypt.decoder.v1.tar"]
    accepts = ["application/vnd.oci.image.layer.v1.tar+encrypted"]
    args = ["--decryption-keys-path", "/etc/containerd/ocicrypt/keys"]
    env = ["OCICRYPT_KEYPROVIDER_CONFIG=/etc/containerd/ocicrypt/ocicrypt_keyprovider.conf"]
    path = "ctd-decoder"
    returns = "application/vnd.oci.image.layer.v1.tar"

  [stream_processors."io.containerd.ocicrypt.decoder.v1.tar.gzip"]
    accepts = ["application/vnd.oci.image.layer.v1.tar+gzip+encrypted"]
    args = ["--decryption-keys-path", "/etc/containerd/ocicrypt/keys"]
    env = ["OCICRYPT_KEYPROVIDER_CONFIG=/etc/containerd/ocicrypt/ocicrypt_keyprovider.conf"]
    path = "ctd-decoder"
    returns = "application/vnd.oci.image.layer.v1.tar+gzip"

[timeouts]
  "io.containerd.timeout.bolt.open" = "0s"
  "io.containerd.timeout.shim.cleanup" = "5s"
  "io.containerd.timeout.shim.load" = "5s"
  "io.containerd.timeout.shim.shutdown" = "3s"
  "io.containerd.timeout.task.state" = "2s"

[ttrpc]
  address = ""
  gid = 0
  uid = 0
~~~

### 基于域名的harbor

~~~toml
disabled_plugins = []
imports = []
oom_score = 0
plugin_dir = ""
required_plugins = []
root = "/var/lib/containerd"
state = "/run/containerd"
temp = ""
version = 2

[cgroup]
  path = ""

[debug]
  address = ""
  format = ""
  gid = 0
  level = ""
  uid = 0

[grpc]
  address = "/run/containerd/containerd.sock"
  gid = 0
  max_recv_message_size = 16777216
  max_send_message_size = 16777216
  tcp_address = ""
  tcp_tls_ca = ""
  tcp_tls_cert = ""
  tcp_tls_key = ""
  uid = 0

[metrics]
  address = ""
  grpc_histogram = false

[plugins]

  [plugins."io.containerd.gc.v1.scheduler"]
    deletion_threshold = 0
    mutation_threshold = 100
    pause_threshold = 0.02
    schedule_delay = "0s"
    startup_delay = "100ms"

  [plugins."io.containerd.grpc.v1.cri"]
    device_ownership_from_security_context = false
    disable_apparmor = false
    disable_cgroup = false
    disable_hugetlb_controller = true
    disable_proc_mount = false
    disable_tcp_service = true
    enable_selinux = false
    enable_tls_streaming = false
    enable_unprivileged_icmp = false
    enable_unprivileged_ports = false
    ignore_image_defined_volumes = false
    max_concurrent_downloads = 3
    max_container_log_line_size = 16384
    netns_mounts_under_state_dir = false
    restrict_oom_score_adj = false
    sandbox_image = "registry.cn-hangzhou.aliyuncs.com/google_containers/pause:3.7"
    selinux_category_range = 1024
    stats_collect_period = 10
    stream_idle_timeout = "4h0m0s"
    stream_server_address = "127.0.0.1"
    stream_server_port = "0"
    systemd_cgroup = false
    tolerate_missing_hugetlb_controller = true
    unset_seccomp_profile = ""

    [plugins."io.containerd.grpc.v1.cri".cni]
      bin_dir = "/opt/cni/bin"
      conf_dir = "/etc/cni/net.d"
      conf_template = ""
      ip_pref = ""
      max_conf_num = 1

    [plugins."io.containerd.grpc.v1.cri".containerd]
      default_runtime_name = "runc"
      disable_snapshot_annotations = true
      discard_unpacked_layers = false
      ignore_rdt_not_enabled_errors = false
      no_pivot = false
      snapshotter = "overlayfs"

      [plugins."io.containerd.grpc.v1.cri".containerd.default_runtime]
        base_runtime_spec = ""
        cni_conf_dir = ""
        cni_max_conf_num = 0
        container_annotations = []
        pod_annotations = []
        privileged_without_host_devices = false
        runtime_engine = ""
        runtime_path = ""
        runtime_root = ""
        runtime_type = ""

        [plugins."io.containerd.grpc.v1.cri".containerd.default_runtime.options]

      [plugins."io.containerd.grpc.v1.cri".containerd.runtimes]

        [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc]
          base_runtime_spec = ""
          cni_conf_dir = ""
          cni_max_conf_num = 0
          container_annotations = []
          pod_annotations = []
          privileged_without_host_devices = false
          runtime_engine = ""
          runtime_path = ""
          runtime_root = ""
          runtime_type = "io.containerd.runc.v2"

          [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
            BinaryName = ""
            CriuImagePath = ""
            CriuPath = ""
            CriuWorkPath = ""
            IoGid = 0
            IoUid = 0
            NoNewKeyring = false
            NoPivotRoot = false
            Root = ""
            ShimCgroup = ""
            SystemdCgroup = true

      [plugins."io.containerd.grpc.v1.cri".containerd.untrusted_workload_runtime]
        base_runtime_spec = ""
        cni_conf_dir = ""
        cni_max_conf_num = 0
        container_annotations = []
        pod_annotations = []
        privileged_without_host_devices = false
        runtime_engine = ""
        runtime_path = ""
        runtime_root = ""
        runtime_type = ""

        [plugins."io.containerd.grpc.v1.cri".containerd.untrusted_workload_runtime.options]

    [plugins."io.containerd.grpc.v1.cri".image_decryption]
      key_model = "node"

    [plugins."io.containerd.grpc.v1.cri".registry]
      config_path = ""
      #=================这里是手动新加进来的 配置harbor模块=========================
      [plugins."io.containerd.grpc.v1.cri".registry.auths]

      [plugins."io.containerd.grpc.v1.cri".registry.configs]
        [plugins."io.containerd.grpc.v1.cri".registry.configs."harbor.hanxux.local".tls]
            insecure_skip_verify = true
            ca_file = ""
            cert_file = ""
            key_file = ""
        [plugins."io.containerd.grpc.v1.cri".registry.configs."harbor.hanxux.local".auth]
            username = "admin"
            password = "Harbor12345"

      [plugins."io.containerd.grpc.v1.cri".registry.headers]

      [plugins."io.containerd.grpc.v1.cri".registry.mirrors]
         [plugins."io.containerd.grpc.v1.cri".registry.mirrors."harbor.hanxux.local"]
            endpoint = ["http://harbor.hanxux.local"]
          [plugins."io.containerd.grpc.v1.cri".registry.mirrors."docker.io"]
             endpoint = ["https://y8y6vosv.mirror.aliyuncs.com","https://docker.lmirror.top","https://docker.m.daocloud.io", "https://hub.uuuadc.top","https://docker.anyhub.us.kg","https://dockerhub.jobcher.com","https://dockerhub.icu","https://docker.ckyl.me","https://docker.awsl9527.cn","https://docker.laoex.link"]
#==================================
    [plugins."io.containerd.grpc.v1.cri".x509_key_pair_streaming]
      tls_cert_file = ""
      tls_key_file = ""

  [plugins."io.containerd.internal.v1.opt"]
    path = "/opt/containerd"

  [plugins."io.containerd.internal.v1.restart"]
    interval = "10s"

  [plugins."io.containerd.internal.v1.tracing"]
    sampling_ratio = 1.0
    service_name = "containerd"

  [plugins."io.containerd.metadata.v1.bolt"]
    content_sharing_policy = "shared"

  [plugins."io.containerd.monitor.v1.cgroups"]
    no_prometheus = false

  [plugins."io.containerd.runtime.v1.linux"]
    no_shim = false
    runtime = "runc"
    runtime_root = ""
    shim = "containerd-shim"
    shim_debug = false

  [plugins."io.containerd.runtime.v2.task"]
    platforms = ["linux/amd64"]
    sched_core = false

  [plugins."io.containerd.service.v1.diff-service"]
    default = ["walking"]

  [plugins."io.containerd.service.v1.tasks-service"]
    rdt_config_file = ""

  [plugins."io.containerd.snapshotter.v1.aufs"]
    root_path = ""

  [plugins."io.containerd.snapshotter.v1.btrfs"]
    root_path = ""

  [plugins."io.containerd.snapshotter.v1.devmapper"]
    async_remove = false
    base_image_size = ""
    discard_blocks = false
    fs_options = ""
    fs_type = ""
    pool_name = ""
    root_path = ""

  [plugins."io.containerd.snapshotter.v1.native"]
    root_path = ""

  [plugins."io.containerd.snapshotter.v1.overlayfs"]
    root_path = ""
    upperdir_label = false

  [plugins."io.containerd.snapshotter.v1.zfs"]
    root_path = ""

  [plugins."io.containerd.tracing.processor.v1.otlp"]
    endpoint = ""
    insecure = false
    protocol = ""

[proxy_plugins]

[stream_processors]

  [stream_processors."io.containerd.ocicrypt.decoder.v1.tar"]
    accepts = ["application/vnd.oci.image.layer.v1.tar+encrypted"]
    args = ["--decryption-keys-path", "/etc/containerd/ocicrypt/keys"]
    env = ["OCICRYPT_KEYPROVIDER_CONFIG=/etc/containerd/ocicrypt/ocicrypt_keyprovider.conf"]
    path = "ctd-decoder"
    returns = "application/vnd.oci.image.layer.v1.tar"

  [stream_processors."io.containerd.ocicrypt.decoder.v1.tar.gzip"]
    accepts = ["application/vnd.oci.image.layer.v1.tar+gzip+encrypted"]
    args = ["--decryption-keys-path", "/etc/containerd/ocicrypt/keys"]
    env = ["OCICRYPT_KEYPROVIDER_CONFIG=/etc/containerd/ocicrypt/ocicrypt_keyprovider.conf"]
    path = "ctd-decoder"
    returns = "application/vnd.oci.image.layer.v1.tar+gzip"

[timeouts]
  "io.containerd.timeout.bolt.open" = "0s"
  "io.containerd.timeout.shim.cleanup" = "5s"
  "io.containerd.timeout.shim.load" = "5s"
  "io.containerd.timeout.shim.shutdown" = "3s"
  "io.containerd.timeout.task.state" = "2s"

[ttrpc]
  address = ""
  gid = 0
  uid = 0
~~~

> 注意：所有k8s节点都需要在/etc/hosts里面加上harbor域名和node ip的映射。

##
