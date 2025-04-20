# 介绍

镜像漏洞扫描器

- 官网地址：https://aquasecurity.github.io/trivy-operator/v0.22.0/
- Helm安装指南：https://aquasecurity.github.io/trivy-operator/latest/getting-started/installation/helm/#customising-the-helm-chart
- Helm chart新版本地址：https://github.com/aquasecurity/trivy-operator/pkgs/container/helm-charts%2Ftrivy-operator
- release pages: https://github.com/aquasecurity/trivy-operator/releases
- arfifact hub: 

工作模式

https://aquasecurity.github.io/trivy-operator/v0.23.0/docs/vulnerability-scanning/trivy/#settings

operator.builtInTrivyServer: true，会设置为Client Server模式，在这个模式下会spin up两个pod：

1. `trivy-operator`: Responsible for running scans
2. `trivy-server-0`: Provides the Trivy vulnerability database to the trivy-operator

# 下载

~~~sh
helm repo add --force-update aqua https://aquasecurity.github.io/helm-charts
helm repo update aqua
helm pull aqua/trivy-operator --version 0.24.1
~~~

# 配置

~~~yaml
#仿照ado中的配置稍作调整
~~~

# 安装

~~~sh
helm upgrade -i trivy-operator -n trivy-system --create-namespace . -f values.yaml
~~~

# 使用

- 查看漏洞报告

~~~sh
#报告主要关注的是集群中的容器镜像或其他资源是否包含已知的安全漏洞。
kubectl get vulnerabilityreports -o wide
~~~

- 查看配置审计报告

~~~sh
#报告专注于集群资源的配置安全，检查 Kubernetes 资源的配置设置是否遵守安全最佳实践。
kubectl get configauditreports -o wide
~~~

## vulnerability DB

trivy会从公网镜像库下载vulnerability DB用于漏洞检测。根据[官网](https://aquasecurity.github.io/trivy-operator/v0.23.0/docs/vulnerability-scanning/trivy/#settings)，在trivy 0.23版本中，使用的镜像库默认为`mirror.gcr.io/aquasec/trivy-db`。

### 下载

Vulnerability DB是OCI image，不是container image，不能用docker pull下载。

[github文档](https://github.com/aquasecurity/trivy-db/pkgs/container/trivy-db#download-the-vulnerability-database)github提供了两种下载方式：

1. trivy-db cli
2. [oras](https://oras.land/docs/installation)（专门用来下载OCI Artifact的工具）

这里采用oras下载vlunerability DB

- 安装oras：

  ~~~sh
  #使用snap安装oras
  snap install oras --classic
  #oras v1.2.2 from Thomas Bechtold (toabctl) installed
  ~~~

- 下载db

  ~~~sh
  oras pull ghcr.io/aquasecurity/trivy-db:2 # https://github.com/aquasecurity/trivy-db/pkgs/container/trivy-db#building-the-db
  
  oras pull ghcr.io/aquasecurity/trivy-java-db:1 # https://github.com/aquasecurity/trivy-java-db
  ~~~

### 上传到ACR

参考文档：

- 使用ORAS上传到ACR：https://learn.microsoft.com/en-us/azure/container-registry/container-registry-manage-artifact
- ORAS教程：https://oras.land/docs/compatible_oci_registries#azure-container-registry-acr
- 具体的上传trivy db的命令：https://github.com/aquasecurity/trivy-db/pkgs/container/trivy-db#building-the-db
- OCI layer的格式说明：https://trivy.dev/v0.57/docs/configuration/db/
  - 对于trivy-db：application/vnd.aquasec.trivy.db.layer.v1.tar+gzip
  - 对于trivy-java-db：application/vnd.aquasec.trivy.javadb.layer.v1.tar+gzip


~~~sh
#首先确保db的tar.gz文件位于当前目录下
cd ~/Downloads
# push trivy-db
oras push cronepilot.azurecr.cn/docker.io/aquasec/trivy-db:2 \
    --artifact-type application/vnd.aquasec.trivy.config.v1+json \
    db.tar.gz:application/vnd.aquasec.trivy.db.layer.v1.tar+gzip
# push java-db
oras push cronepilot.azurecr.cn/docker.io/aquasec/trivy-java-db:1 \
    --artifact-type application/vnd.aquasec.trivy.config.v1+json \
    db.tar.gz:application/vnd.aquasec.trivy.javadb.layer.v1.tar+gzip
~~~

### [Recommended] oras cp直接复制到ACR

~~~sh
oras cp ghcr.io/aquasecurity/trivy-checks:0 cronepilot.azurecr.cn/docker.io/aquasec/trivy-checks:0 # https://github.com/aquasecurity/trivy-checks/pkgs/container/trivy-checks
oras cp ghcr.io/aquasecurity/trivy-checks:1 cronepilot.azurecr.cn/docker.io/aquasec/trivy-checks:1
oras cp ghcr.io/aquasecurity/trivy-java-db:1 cronepilot.azurecr.cn/docker.io/aquasec/trivy-java-db:1
oras cp ghcr.io/aquasecurity/trivy-db:2 cronepilot.azurecr.cn/docker.io/aquasec/trivy-db:2
~~~

### 上传到harbor

~~~sh
#首先确保db的tar.gz文件位于当前目录下
cd ~/Downloads
#login
oras login harbor.hanxux.local --insecure --username admin --password Harbor12345
# push trivy-db
oras push harbor.hanxux.local/aquasec/trivy-db:2 \
    --artifact-type application/vnd.aquasec.trivy.config.v1+json \
    db.tar.gz:application/vnd.aquasec.trivy.db.layer.v1.tar+gzip \
    --insecure
# push java-db
oras push harbor.hanxux.local/aquasec/trivy-java-db:1 \
    --artifact-type application/vnd.aquasec.trivy.config.v1+json \
    db.tar.gz:application/vnd.aquasec.trivy.javadb.layer.v1.tar+gzip \
    --insecure
~~~

### 在网络隔离环境用offline mode

https://trivy.dev/v0.57/docs/advanced/air-gap/

### troubleshooting

1. 下载vulnerability DB有时会失败，参考[troubleshooting guide](https://trivy.dev/v0.57/docs/references/troubleshooting/#db)


2. 升级版本，官网不提供自动化升级的方式，建议手动uninstall旧的helm release安装新版，注意要手动删除CRD。

   （每次升级helm chart的时候，CRD不会被自动升级，所以在pipeline中每次手动解压出CRD子目录手动kubectl Apply，如果出现conflict的情况就先手动删掉旧的CRD再安装新的）

   ~~~sh
   kubectl delete crd vulnerabilityreports.aquasecurity.github.io 
   kubectl delete crd exposedsecretreports.aquasecurity.github.io
   kubectl delete crd configauditreports.aquasecurity.github.io
   kubectl delete crd clusterconfigauditreports.aquasecurity.github.io
   kubectl delete crd rbacassessmentreports.aquasecurity.github.io
   kubectl delete crd infraassessmentreports.aquasecurity.github.io
   kubectl delete crd clusterrbacassessmentreports.aquasecurity.github.io
   kubectl delete crd clustercompliancereports.aquasecurity.github.io
   kubectl delete crd clusterinfraassessmentreports.aquasecurity.github.io
   kubectl delete crd sbomreports.aquasecurity.github.io
   kubectl delete crd clustersbomreports.aquasecurity.github.io
   kubectl delete crd clustervulnerabilityreports.aquasecurity.github.io
   ~~~

   

