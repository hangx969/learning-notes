# Docker私有镜像仓库harbor

## Harbor介绍

- Docker容器应用的开发和运行离不开可靠的镜像管理，虽然Docker官方也提供了公共的镜像仓库，但是从安全和效率等方面考虑，部署我们私有环境内的Registry也是非常必要的。

- Harbor是由VMware公司开源的企业级的Docker Registry管理项目，它包括权限管理(RBAC)、LDAP、日志审核、管理界面、自我注册、镜像复制和中文支持等功能。

- 官网地址：https://github.com/goharbor/harbor

## Harbor安装配置

1. 创建VM。为harbor创建自签发证书

   ```bash
   #设置主机名
   hostnamectl set-hostname harbor && bash
   
   mkdir /data/ssl -p
   cd /data/ssl/
   #生成一个3072位的key，也就是私钥
   openssl genrsa -out ca.key 3072
   #生成一个数字证书ca.pem，3650表示证书的有效时间是3年。后续根据ca.pem根证书来签发信任的客户端证书
   openssl req -new -x509 -days 3650 -key ca.key -out ca.pem 
   #生成域名的证书
   #生成一个3072位的key，也就是私钥
   openssl genrsa -out harbor.key  3072
   #生成一个证书请求文件，一会签发证书时需要的
   openssl req -new -key harbor.key -out harbor.csr
   #签发证书：
   openssl x509 -req -in harbor.csr -CA ca.pem -CAkey ca.key -CAcreateserial -out harbor.pem -days 3650
   ```

2. 安装docker（harbor是基于docker的）

   安装前面装docker的步骤

3. 安装harbor

   ```bash
   #配置hosts文件
   vim /etc/hosts
   #添加：
   10.0.0.4 hangxdockerlab
   10.0.0.5 harbor
   #创建安装目录
   mkdir /data/install -p
   cd /data/install/
   #安装harbor
   #/data/ssl目录下有如下文件：ca.key  ca.pem  ca.srl  harbor.csr  harbor.key  harbor.pem
   cd /data/install/
   #把harbor的离线包harbor-offline-installer-v2.3.0-rc3.tgz上传到这个目录，离线包在课件里提供了
   
   #下载harbor离线包的地址：
   #https://github.com/goharbor/harbor
   #解压：
   tar zxvf harbor-offline-installer-v2.3.0-rc3.tgz
   cd harbor
   cp harbor.yml.tmpl harbor.yml 
   
   vim harbor.yml
   #修改配置文件：
   hostname: harbor #修改hostname，跟上面签发的证书域名保持一致
   #协议用https
   certificate: /data/ssl/harbor.pem
   private_key: /data/ssl/harbor.key
   #邮件和ldap不需要配置，在harbor的web界面可以配置，其他配置采用默认即可。
   #注：harbor默认的账号密码：admin/Harbor12345
   ```

4. 安装docker-compose

   docker-compose项目是Docker官方的开源项目，负责实现对Docker容器集群的快速编排。Docker-Compose的工程配置文件默认为docker-compose.yml，Docker-Compose运行目录下的必要有一个docker-compose.yml。docker-compose可以管理多个docker实例。

   ```bash
   #上传docker-compose-Linux-x86_64文件到harbor机器，这是harbor的依赖
   mv docker-compose-Linux-x86_64.64 /usr/bin/docker-compose
   chmod +x /usr/bin/docker-compose
   
   #安装harbor依赖的的离线镜像包docker-harbor-2-3-0.tar.gz上传到harbor机器，通过docker load -i解压
   docker load -i docker-harbor-2-3-0.tar.gz 
   cd /data/install/harbor
   ./install.sh
   #出现✔ ----Harbor has been installed and started successfully.---- 表明安装成功。
   ```

   > 注：
   >
   > - docker-compose可以直接yum install docker-compose或者apt install docker-compose
   >
   > - 离线镜像包docker-harbor-2-3-0.tar.gz如果不上传，install.sh会自动拉取
   >
   > - 安装过程中如果报错类似HTTP error chucked，执行`pip install 'urllib3<2'`

5. harbor启动和停止

   ```bash
   #如何停掉harbor：
   cd /data/install/harbor
   docker-compose stop 
   #如何启动harbor：
   sudo su
   cd /data/install/harbor
   docker-compose start
   ```

6. 图形化界面访问harbor

   - 在harbor同一个VNET下创建了一台Windows VM，在C:\Windows\System32\drivers\etc下修改hosts文件，添加 harbor 10.0.0.5。浏览器访问：https://harbor
   - Harbor VM NSG开放443端口，直接访问公网IP就行（https://20.205.104.235）

## harbor私有镜像仓库使用

```bash
#在docker lab机器上修改docker镜像源
#修改docker配置 
vim /etc/docker/daemon.json

{  "registry-mirrors": ["https://rsbud4vc.mirror.aliyuncs.com","https://registry.docker-cn.com","https://docker.mirrors.ustc.edu.cn","https://dockerhub.azk8s.cn","http://hub-mirror.c.163.com"],
"insecure-registries": ["10.0.0.5","harbor"]
}
#注意：配置新增加了一行内容如下："insecure-registries": ["10.0.0.5","harbor"]
#上面增加的内容表示我们内网访问harbor的时候走的是http，10.0.0.5是安装harbor机器的ip

#修改配置之后使配置生效：
systemctl daemon-reload && systemctl restart docker
#查看docker是否启动成功
systemctl status docker

#登录仓库
docker login 10.0.0.5

#将本地镜像上传到仓库
docker load -i tomcat.tar.gz
docker tag tomcat:latest  10.0.0.5/test/tomcat:v1
docker push 10.0.0.5/test/tomcat:v1 

#从仓库拉取镜像
docker rmi -f 10.0.0.5/test/tomcat:v1
docker pull 10.0.0.5/test/tomcat:v1
```

# k8s基于containerd从harbor拉取镜像

## 升级containerd

- 在安装1.28的k8s的时候，装的是1.6.6的containerd，还不支持harbor，需要升级containerd。

- 给虚机打个快照。

- 目前适配k8s 1.24之后的所有版本的containerd的稳定版本为：1.6.22，就装这个版本。

  ~~~sh
  yum remove containerd.io -y
  yum install containerd.io-1.6.22* -y
  cd /etc/containerd/
  rm -rf *
  #上传config.toml文件
  yum install docker-ce -y
  systemctl start docker --now
  ~~~

## containerd配置文件修改

- 修改/etc/containerd/containerd.toml配置文件里的harbor的ip地址，变成自己真实环境的harbor的ip

- 修改完之后重启containerd

  ~~~sh
  systemctl restart containerd
  ~~~

- containerd配置文件如下：

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

## 配置docker

- 在需要拉镜像的机器上配置docker登录harbor

~~~sh
vim /etc/docker/daemon.json
#添加下面一行(harbor ip，主机名)，记得在上一行末尾加上逗号。
#内网登录不用走https，走http就行。
"insecure-registries": ["10.0.0.5","harbor"]

systemctl daemon-reload
systemctl restart docker

vim /etc/hosts
#添加harbor域名
10.0.0.5 harbor

#测试docker登录推送镜像
docker login 10.0.0.5
docker pull nginx
docker tag docker.io/library/nginx:latest 10.0.0.5/test/nginx:latest #harbor IP/项目名/镜像名
docker push 10.0.0.5/test/nginx:latest
~~~

## 创建pod

- 配置为从harbor拉镜像

~~~yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-test-harbor
  namespace: default
spec:
  containers:
  - image: 10.0.0.5/test/nginx:latest
    imagePullPolicy: Always
    name: nginx-pod
    ports:
    - name: nginx-port
      containerPort: 80
      protocol: TCP
~~~

- 注：使用中发现，给containerd的config.toml配置了harbor之后，新部署的pod，即使镜像已经在本地，并且设置为IfNoePresent，containerd并不会识别到本地的镜像，反而会去镜像源拉取。将config中关于harbor的配置注释掉之后，又可以识别到本地镜像了。

# k8s基于docker从harbor拉取镜像

## 改docker配置文件

~~~sh
#修改docker配置文件，需要在k8s每个节点都修改docker配置文件。
cat > /etc/docker/daemon.json <<EOF
{
 "registry-mirrors":["https://y8y6vosv.mirror.aliyuncs.com","https://registry.docker-cn.com","https://docker.mirrors.ustc.edu.cn","https://dockerhub.azk8s.cn","http://hub-mirror.c.163.com"],
  "exec-opts": ["native.cgroupdriver=systemd"],
  "insecure-registries":["10.0.0.5","harbor"], 
}
EOF
~~~

## 配置hosts

~~~sh
#每台机器的/etc/hosts文件加上harbor地址
vim /etc/hosts
#10.0.0.5 harbor
~~~

## 创建secret

~~~sh
kubectl create secret docker-registry registry-pull-secret --docker-server=10.0.0.5 --docker-username=admin --docker-password=Harbor12345
#kubectl create secret --help可以看到，这个命令自带docker-registry参数
#kubectl create secret docker-registry --help，可以看到这个命令自带配置docker地址和用户名密码的参数
~~~

## pod挂载secret拉取镜像

~~~yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
  namespace: default
spec:
  imagePullSecrets:
  - name: registry-pull-secret
  containers:
  - name: nginx
    image: 10.0.0.5/library/nginx:latest
    imagePullPolicy: Always
~~~

