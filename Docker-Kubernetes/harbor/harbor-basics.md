---
title: Harbor 部署与使用指南
tags:
  - kubernetes
  - harbor
  - docker
  - helm
  - containerd
date: 2026-09-15
aliases:
  - harbor基础
  - helm部署harbor
  - Helm 部署 Harbor
---

# Harbor 部署与使用指南

Harbor 是面向云原生制品的企业级私有 Registry，可统一存储和管理容器镜像、Helm Chart 等 OCI Artifact，并提供 RBAC、LDAP、审计、复制和 Web 管理等能力。

- 项目地址：[goharbor/harbor](https://github.com/goharbor/harbor)
- Helm Chart：[Harbor Helm Releases](https://github.com/goharbor/harbor-helm/releases)
- Artifact Hub：[Harbor](https://artifacthub.io/packages/helm/harbor/harbor)
- OCI Chart 文档：[Working with OCI Helm Charts](https://goharbor.io/docs/main/working-with-projects/working-with-oci/working-with-helm-oci-charts/)

本文按“部署 Harbor → 推拉镜像 → Kubernetes 接入 → 管理 Helm Chart → TLS 配置”的顺序整理。示例中的域名、IP、版本、StorageClass 和口令均需替换为实际环境值。

> [!warning] 示例凭据
> 文中的 `admin/Harbor12345` 是示例或旧版本默认凭据，只适合实验环境。生产环境应在首次部署时修改管理员密码，并优先使用项目级 Robot Account。

## 1. 部署方式选择

| 场景 | 推荐方式 | 说明 |
| --- | --- | --- |
| 单机实验、离线环境 | Docker Compose | 组件集中在一台主机，部署和维护简单 |
| Kubernetes 集群 | Helm | 便于通过 Ingress、PVC、cert-manager 和 values 管理 |
| 高可用生产环境 | Helm + 外部依赖 | 数据库、Redis、对象存储等需按实际 HA 设计 |

## 2. 使用 Docker Compose 部署 Harbor

以下流程来自 Harbor 2.3.x 的历史实验环境。新部署应下载目标版本对应的离线安装包，并以该版本的 `harbor.yml.tmpl` 和官方文档为准。

### 2.1 配置主机名与自签名证书

~~~bash
hostnamectl set-hostname harbor

mkdir -p /data/ssl
cd /data/ssl

# CA 私钥与根证书
openssl genrsa -out ca.key 3072
openssl req -new -x509 -days 3650 -key ca.key -out ca.pem

# Harbor 私钥、CSR 与服务端证书
openssl genrsa -out harbor.key 3072
openssl req -new -key harbor.key -out harbor.csr
openssl x509 -req -in harbor.csr \
  -CA ca.pem -CAkey ca.key -CAcreateserial \
  -out harbor.pem -days 3650
~~~

证书的 CN/SAN 必须与客户端使用的 Harbor 域名一致。客户端还需要信任签发该证书的 CA。

### 2.2 安装并配置 Harbor

先安装 Docker 和 Docker Compose，再准备主机解析和离线安装包：

~~~bash
# /etc/hosts 示例
10.0.0.4 hangxdockerlab
10.0.0.5 harbor

mkdir -p /data/install
cd /data/install
tar zxvf harbor-offline-installer-v2.3.0-rc3.tgz
cd harbor
cp harbor.yml.tmpl harbor.yml
~~~

编辑 `harbor.yml` 的关键项：

~~~yaml
hostname: harbor

https:
  port: 443
  certificate: /data/ssl/harbor.pem
  private_key: /data/ssl/harbor.key
~~~

如果 Docker Compose 未通过系统包安装，可将对应平台的二进制放入 PATH：

~~~bash
mv docker-compose-Linux-x86_64 /usr/bin/docker-compose
chmod +x /usr/bin/docker-compose
~~~

加载离线镜像并安装：

~~~bash
docker load -i docker-harbor-2-3-0.tar.gz
cd /data/install/harbor
./install.sh
~~~

未预先加载离线镜像时，安装程序会尝试在线拉取。旧环境若出现与 urllib3 版本相关的 HTTP chunked error，可检查 Python 依赖兼容性；原实验的临时处理为：

~~~bash
pip install 'urllib3<2'
~~~

### 2.3 启停与访问

~~~bash
cd /data/install/harbor
docker-compose stop
docker-compose start
~~~

客户端必须能解析 Harbor 域名，并允许访问 443 端口。例如 Windows 可在 `C:\Windows\System32\drivers\etc\hosts` 中添加 `10.0.0.5 harbor`，然后访问 `https://harbor`。

## 3. 使用 Helm 在 Kubernetes 部署 Harbor

### 3.1 下载 Chart

~~~bash
helm repo add harbor https://helm.goharbor.io
helm repo update harbor
helm pull harbor/harbor --version 1.18.0
~~~

### 3.2 使用 cert-manager 准备 TLS 证书

以下示例假定 `harbor` Namespace 和名为 `selfsigned` 的 `ClusterIssuer` 已存在：

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

### 3.3 配置 Ingress、外部 URL 与持久化

在 Chart 的 `values.yaml` 中至少确认以下配置：

~~~yaml
expose:
  type: ingress
  tls:
    enabled: true
    certSource: secret
    secret:
      secretName: harbor-tls-cert-secret
  ingress:
    hosts:
      core: harbor.hanxux.local
    controller: default
    className: nginx-default
    annotations:
      ingress.kubernetes.io/ssl-redirect: "true"
      ingress.kubernetes.io/proxy-body-size: "0"
      nginx.ingress.kubernetes.io/ssl-redirect: "true"
      nginx.ingress.kubernetes.io/proxy-body-size: "0"

externalURL: "https://harbor.hanxux.local"
~~~

`externalURL` 会参与生成 Registry 鉴权地址。如果缺失，登录时可能出现以下错误：

~~~text
Get "/service/token?...": unsupported protocol scheme ""
~~~

原实验使用 Chart 内置的 PostgreSQL 和 Redis。持久化配置需要在首次安装前规划好：如果 PVC 创建时使用了不合适的 AccessMode，后续通常无法通过 `helm upgrade` 直接修改。只有底层存储支持时才使用 `ReadWriteMany`。

> [!warning] Ingress 外部认证
> 为 Harbor Ingress 增加 oauth2-proxy 的 `auth-url` / `auth-signin` 后，可能导致 `helm registry login` 等非浏览器客户端无法完成认证。UI 单点登录与 Registry API 认证应分别设计。

### 3.4 安装或升级

~~~bash
helm upgrade --install harbor ./harbor-1.18.0.tgz \
  --namespace harbor \
  --create-namespace \
  -f values.yaml
~~~

安装后检查工作负载、Ingress、PVC 和证书状态，再通过 `https://harbor.hanxux.local` 访问 UI。

## 4. Docker 推拉镜像

### 4.1 配置客户端

如果实验环境使用 HTTP 或未受信任的自签名证书，可在 `/etc/docker/daemon.json` 配置不安全仓库：

~~~json
{
  "registry-mirrors": [
    "https://registry.docker-cn.com",
    "https://docker.mirrors.ustc.edu.cn"
  ],
  "insecure-registries": [
    "10.0.0.5",
    "harbor.hanxux.local"
  ]
}
~~~

~~~bash
systemctl daemon-reload
systemctl restart docker
systemctl status docker
~~~

> [!warning] 生产环境
> `insecure-registries` 和跳过 TLS 校验只适合受控实验环境。生产环境应向 Docker/Containerd 分发 CA，保持完整的 TLS 校验。

### 4.2 登录、推送与拉取

先在 Harbor 中创建目标项目，例如 `test` 或 `platform-external`：

~~~bash
docker login harbor.hanxux.local

docker load -i tomcat.tar.gz
docker tag tomcat:latest harbor.hanxux.local/test/tomcat:v1
docker push harbor.hanxux.local/test/tomcat:v1

docker rmi harbor.hanxux.local/test/tomcat:v1
docker pull harbor.hanxux.local/test/tomcat:v1
~~~

## 5. Kubernetes 从 Harbor 拉取镜像

### 5.1 containerd 节点配置

原 Kubernetes 1.28 实验环境把 containerd 从 1.6.6 升级到 1.6.22。该版本选择属于历史环境记录，不代表所有 Harbor 接入都必须升级；操作前应检查 Kubernetes、CRI 与 containerd 的兼容矩阵，并先备份配置或创建虚机快照。

~~~bash
yum remove containerd.io -y
yum install 'containerd.io-1.6.22*' -y
systemctl restart containerd
~~~

旧版 `config.toml` 的 Registry 配置可按 IP 或域名设置。以下只保留需要合并进 `/etc/containerd/config.toml` 的 Harbor 相关片段，其他 CRI、runtime、CNI 与 snapshotter 配置应保留环境现值。

按 IP 接入 HTTPS Harbor：

~~~toml
[plugins."io.containerd.grpc.v1.cri".registry.configs."10.0.0.5".tls]
  insecure_skip_verify = true

[plugins."io.containerd.grpc.v1.cri".registry.configs."10.0.0.5".auth]
  username = "admin"
  password = "Harbor12345"

[plugins."io.containerd.grpc.v1.cri".registry.mirrors."10.0.0.5"]
  endpoint = ["https://10.0.0.5:443"]
~~~

按域名接入 HTTP Harbor：

~~~toml
[plugins."io.containerd.grpc.v1.cri".registry.configs."harbor.hanxux.local".tls]
  insecure_skip_verify = true

[plugins."io.containerd.grpc.v1.cri".registry.configs."harbor.hanxux.local".auth]
  username = "admin"
  password = "Harbor12345"

[plugins."io.containerd.grpc.v1.cri".registry.mirrors."harbor.hanxux.local"]
  endpoint = ["http://harbor.hanxux.local"]
~~~

配置域名时，所有 Kubernetes 节点都必须能解析该域名。修改后重启并检查 containerd：

~~~bash
echo '10.0.0.5 harbor.hanxux.local' >> /etc/hosts
systemctl restart containerd
systemctl status containerd
~~~

> [!note] 原实验现象
> 某次旧版配置中，Pod 即使设置 `IfNotPresent` 且节点已有镜像，containerd 仍重新访问 Registry；注释 Harbor Registry 配置后恢复本地镜像识别。该现象应结合镜像完整引用、标签、CRI image 列表和 containerd 日志进一步定位，不宜直接归因于 Harbor。

### 5.2 使用 imagePullSecret

不建议把长期管理员密码写进每个节点的 containerd 配置。可在目标 Namespace 创建 Registry Secret，并在 Pod 或 ServiceAccount 中引用：

~~~bash
kubectl create secret docker-registry registry-pull-secret \
  --docker-server=harbor.hanxux.local \
  --docker-username=admin \
  --docker-password='Harbor12345'
~~~

~~~yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-test-harbor
  namespace: default
spec:
  imagePullSecrets:
    - name: registry-pull-secret
  containers:
    - name: nginx
      image: harbor.hanxux.local/library/nginx:latest
      imagePullPolicy: Always
      ports:
        - name: nginx-port
          containerPort: 80
          protocol: TCP
~~~

Secret 是 Namespace 级资源；多个 Namespace 使用时需分别创建，或通过对应 ServiceAccount 统一引用。

### 5.3 使用 Docker Runtime 的旧集群

如果旧 Kubernetes 集群仍使用 Docker Runtime，需要在每个节点配置 `insecure-registries`、域名解析并重启 Docker。随后同样通过 `imagePullSecrets` 提供私有仓库凭据。此流程不适用于已经迁移到 containerd/CRI-O 的节点。

## 6. 使用 Harbor 管理 Helm OCI Chart

### 6.1 版本差异

- Helm 3 支持将 Chart 存储在 OCI Registry；从 Helm 3.8.0 起 OCI 支持默认启用。
- Harbor 2.8 及以后直接将 Chart 作为 OCI Artifact 管理，与镜像显示在同一项目中，不再提供独立 Charts 页面。
- Harbor 2.8 之前可通过 ChartMuseum 使用传统 Chart Repository。安装时执行 `./install.sh --with-chartmuseum`；已有环境可运行 `./prepare --with-chartmuseum` 后再执行 `docker-compose up -d`。

### 6.2 打包、推送与拉取 Chart

先在 Harbor 创建目标项目，然后执行：

~~~bash
helm registry login harbor.hanxux.local --insecure

# 必须在包含 Chart.yaml 的目录中执行
helm package .

helm push commoninfra-0.0.1.tgz \
  oci://harbor.hanxux.local/platform-external/ \
  --insecure-skip-tls-verify

helm pull oci://harbor.hanxux.local/platform-external/commoninfra \
  --version 0.0.1 \
  --insecure-skip-tls-verify
~~~

纯 HTTP Registry 可使用 `--plain-http`。出现 `x509: certificate signed by unknown authority` 时，推荐向客户端安装 CA；`--insecure-skip-tls-verify` 仅作为实验环境的临时方案。

从 Harbor 中的 OCI Chart 安装：

~~~bash
helm install <release_name> \
  oci://<harbor_address>/<project>/<chart_name> \
  --version <version> \
  -f values.yaml \
  --insecure-skip-tls-verify
~~~

### 6.3 将第三方 Chart 和镜像同步到内网 Harbor

以 Harbor 官方 Chart 为例，先下载并把默认镜像仓库替换为私有 Harbor：

~~~bash
helm repo add harbor https://helm.goharbor.io
helm repo update
helm pull harbor/harbor --version 1.15.0
tar xf harbor-1.15.0.tgz
cd harbor

sed -i 's/repository: goharbor/repository: harbor.hanxux.local\/harbor/g' values.yaml
helm package .

helm push harbor-1.15.0.tgz \
  oci://harbor.hanxux.local/harbor \
  --insecure-skip-tls-verify
~~~

下面的脚本从已部署的 `harbor` Namespace 收集实际镜像，重新打 Tag 并推送到私有项目。运行前应确认目标项目已创建，并检查同名镜像是否可能覆盖已有 Tag。

~~~bash
#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="harbor"
HARBOR_URL="harbor.hanxux.local"
HARBOR_PROJECT="harbor"

IMAGES=$(kubectl get pods -n "$NAMESPACE" \
  -o jsonpath="{range .items[*]}{.spec.containers[*].image}{'\n'}{end}" \
  | sort -u)

docker login "$HARBOR_URL"

for IMAGE in $IMAGES; do
  IMAGE_NAME=$(echo "$IMAGE" | awk -F/ '{print $NF}')
  NEW_TAG="$HARBOR_URL/$HARBOR_PROJECT/$IMAGE_NAME"

  docker pull "$IMAGE"
  docker tag "$IMAGE" "$NEW_TAG"
  docker push "$NEW_TAG"
  docker rmi "$IMAGE" "$NEW_TAG"
done
~~~

> [!warning] 镜像命名冲突
> 该脚本只保留镜像引用的最后一段。同名镜像来自不同上游路径时可能冲突；正式迁移应保留完整仓库路径，或维护显式映射表。

验证内网 Chart：

~~~bash
helm pull oci://harbor.test.com/harbor/harbor \
  --version 1.15.0 \
  --insecure-skip-tls-verify

helm upgrade --install harbor harbor-1.15.0.tgz \
  --namespace harbor \
  --create-namespace \
  --set expose.type=ingress \
  --set expose.ingress.className=nginx \
  --set expose.ingress.hosts.core=harbor.abc.com \
  --set expose.ingress.hosts.notary=notary.abc.com \
  --set externalURL=https://harbor.abc.com \
  --set harborAdminPassword='Harbor12345' \
  --set persistence.persistentVolumeClaim.registry.storageClass=openebs-hostpath \
  --set persistence.persistentVolumeClaim.jobservice.jobLog.storageClass=openebs-hostpath \
  --set persistence.persistentVolumeClaim.database.storageClass=openebs-hostpath \
  --set persistence.persistentVolumeClaim.redis.storageClass=openebs-hostpath \
  --set persistence.persistentVolumeClaim.trivy.storageClass=openebs-hostpath
~~~

## 7. TLS 与客户端证书

### 7.1 Docker 信任自签名 CA 或使用双向 TLS

将证书放在以 Registry 主机名命名的目录中：

~~~text
/etc/docker/certs.d/rocky-2/ca.crt
/etc/docker/certs.d/rocky-2/client.cert
/etc/docker/certs.d/rocky-2/client.key
~~~

~~~bash
systemctl restart docker
~~~

### 7.2 containerd、ctr、crictl 与 nerdctl

旧版 containerd CRI 配置可指定 CA 和客户端证书：

~~~toml
[plugins."io.containerd.grpc.v1.cri".registry.configs."reg.mydomain.com".tls]
  ca_file = "/etc/containerd/certs.d/reg.mydomain.com/ca.crt"
  cert_file = "/etc/containerd/certs.d/reg.mydomain.com/client.cert"
  key_file = "/etc/containerd/certs.d/reg.mydomain.com/client.key"
~~~

`crictl` 和 `nerdctl` 使用的证书目录示例：

~~~text
/etc/containerd/certs.d/reg.mydomain.com/ca.crt
/etc/containerd/certs.d/reg.mydomain.com/client.cert
/etc/containerd/certs.d/reg.mydomain.com/client.key
~~~

~~~bash
systemctl restart containerd
~~~

## 8. 历史实验与已知问题

原文记录过“Harbor 与 Nginx 同机，由 Nginx 代理 Harbor 并要求客户端证书”的实验，环境为 Rocky Linux 8、Harbor 2.10.3、Nginx 1.14.1、Docker 26.1.3 和 containerd 1.6.22。该方案最终标记为失败，不能作为可复用部署方案。

实验中使用的证书链路包括：

~~~bash
mkdir -p /data/ca
cd /data/ca

# CA
openssl genrsa -out ca.key 2048
openssl req -new -x509 -days 365 -key ca.key -out ca.crt \
  -subj "/C=CN/ST=Beijing/L=Beijing/O=Personal/OU=Personal/CN=Registry CA"

cat > v3.ext <<'EOF'
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage=digitalSignature,nonRepudiation,keyEncipherment,dataEncipherment
extendedKeyUsage=serverAuth
subjectAltName=@alt_names

[alt_names]
DNS.1=rocky-2
EOF

# 服务端证书
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr \
  -subj "/C=CN/ST=Beijing/L=Beijing/O=Personal/OU=Personal/CN=rocky-2"
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key \
  -CAcreateserial -out server.crt -days 365 -extfile v3.ext

# 客户端证书
openssl genrsa -out client.key 2048
openssl req -new -key client.key -out client.csr \
  -subj "/C=CN/ST=Beijing/L=Beijing/O=Personal/OU=Personal/CN=Registry client"
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key \
  -CAcreateserial -out client.crt -days 365
openssl x509 -inform PEM -in client.crt -out client.cert
~~~

> [!danger] 不可直接复用
> 原 Nginx 代理配置存在问题，且 mTLS 会同时影响 Docker、containerd、Helm 和浏览器客户端。若确需双向认证，应重新设计端到端证书校验、Token Service 路由、上传大小、流式传输及客户端证书分发，并完成镜像 Push/Pull 和 Helm OCI 的联合验证。

## 9. 验证清单

- Harbor UI 可通过预期域名和 HTTPS 访问。
- Docker 登录、Push、Pull 均成功。
- Kubernetes Pod 能通过 `imagePullSecret` 拉取私有镜像。
- containerd 重启后无配置解析错误，CRI 仍正常工作。
- Helm OCI Chart 能登录、推送、拉取和安装。
- Ingress、`externalURL`、证书 SAN 与客户端访问域名一致。
- PVC 的 StorageClass、容量和 AccessMode 满足实际后端能力。
- 生产环境已移除默认管理员口令和不必要的 TLS 跳过选项。
