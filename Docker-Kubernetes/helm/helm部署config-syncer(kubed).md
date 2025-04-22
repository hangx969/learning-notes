# 介绍

将configMap和secret同步到其他namespace的工具

- 官网地址：
  - https://github.com/config-syncer/config-syncer
  - https://config-syncer.com/docs/v0.15.2/guides/config-syncer/
  - artifact hub: https://artifacthub.io/packages/helm/appscode/kubed


# 下载helm chart

~~~sh
helm repo add --force-update appscode https://charts.appscode.com/stable
helm repo update appscode
helm pull appscode/kubed --version 0.13.2
~~~

# 构建镜像

由于在2024年2月，Appscode将config-syncer的镜像从docker.io移除了（https://github.com/bytebuilders/community/discussions/62），突然没有任何事先通知的移除dockerhub image，使得许多用户遭受了downtime。

他们仍然在Apache 2.0 Open Source license下，所以我们可以自行通过dockerfile制作镜像，推送到我们的私有仓库中以供使用。步骤如下：

~~~sh
git clone --branch 'v0.13.2' --depth 1 --verbose 'https://github.com/config-syncer/config-syncer.git' .
make 'container-linux_amd64'
docker save -o './kubed-image.tar' 'appscode/kubed:v0.13.2_linux_amd64'
~~~

> 在github上有用户提到了config-syncer的替代品：https://github.com/mittwald/kubernetes-replicator，后面可以尝试一下。

# 推送镜像到harbor

- 修改docker配置文件

  ~~~sh
  vim /etc/docker/daemon.json
  #添加docker登录harbor的http设置
  "insecure-registries": ["172.16.183.100","harbor.hanxux.local"]
  ~~~

- 登录harbor

  ~~~sh
  docker login harbor.hanxux.local 
  #使用默认用户名和密码登录
  ~~~

- 推送镜像

  ~~~sh
  docker tag appscode/kubed:v0.13.2_linux_amd64 harbor.hanxux.local/platform-tools-local/appscode/kubed:v0.13.2_linux_amd64
  docker push harbor.hanxux.local/platform-tools-local/appscode/kubed:v0.13.2_linux_amd64
  ~~~

# 配置helm chart

1. values.yaml文件中的镜像源改成先前制作完推送到harbor的镜像
2. 添加resource字段

~~~yaml
operator:
  # Docker registry used to pull Config Syncer operator image
  registry: harbor.hanxux.local
  # Config Syncer operator container image
  repository: platform-external/appscode/kubed
  # Config Syncer operator container image tag
  tag: v0.13.2_linux_amd64
  # Compute Resources required by the operator container
  resources:
    requests:
      cpu: 30m
      memory: 100Mi
    limits:
      cpu: 100m
      memory: 128Mi
config:
  additionalOptions:
    - resync-period=1m
~~~

# containerd配置从harbor拉镜像

- 编辑/etc/containerd/config.toml

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

# 安装

~~~sh
#helm template用于在不部署到集群的前提下，渲染生成yaml文件
helm template oci://$harbor_host/$harbor_project/$helm_chart_file_name -f ./external/config-syncer/values.yaml

helm upgrade -i config-syncer -n kube-system \ 
oci://$harbor_host/$harbor_project/$helm_chart_file_name \ 
--history-max 3 \ 
--version $CHART_VERSION \ 
-f ./external/config-syncer/values.yaml
~~~

# 使用

- 参考官网：https://config-syncer.com/docs/v0.15.2/guides/config-syncer/intra-cluster/#namespace-selector

- 将configMap同步到其他namespace：

  - 如果创建了一个configMap/Secret，具有annotation：**`kubed.appscode.com/sync: ""`**，config-syncer会把自动同步到其他所有namespace。
  - 如果创建了一个configMap/Secret，具有annotation：**`kubed.appscode.com/sync: "app=kubed"`**，config-syncer会把自动同步到具有标签：app=kubed的所有namespace。


> 注意：
>
> - 源secret/ConfigMap是在**annotation**中设置**`kubed.appscode.com/sync: "app=kubed"`**
> - 需要被同步的目的namespace是在**label**中设置**`app=kubed`**

- 复制出来的configMap/Secret，会被加上：
  - `kubed.appscode.com/origin`的annotation
  - `kubed.appscode.com/origin.name`，`kubed.appscode.com/origin.namespace`，`kubed.appscode.com/origin.cluster`的label
