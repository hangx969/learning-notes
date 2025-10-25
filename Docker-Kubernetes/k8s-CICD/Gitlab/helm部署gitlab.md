# 介绍

- 官网：[Deploy the GitLab Helm chart | GitLab Docs](https://docs.gitlab.com/charts/installation/deployment/)
- artifacthub：[gitlab 9.3.2 · gitlab/gitlab](https://artifacthub.io/packages/helm/gitlab/gitlab)
- 源码保存在gitlab官网中：[GitLab.org / charts / GitLab Chart · GitLab](https://gitlab.com/gitlab-org/charts/gitlab)

# 下载

~~~sh
helm repo add gitlab https://charts.gitlab.io/
helm repo update gitlab
helm pull gitlab/gitlab --version 9.3.2
~~~

# 配置

~~~yaml
## NOTICE
#
# Due to the scope and complexity of this chart, all possible values are
# not documented in this file. Extensive documentation is available.
#
# Please read the docs: https://docs.gitlab.com/charts/
#
# Because properties are regularly added, updated, or relocated, it is
# _strongly suggest_ to not "copy and paste" this YAML. Please provide
# Helm only those properties you need, and allow the defaults to be
# provided by the version of this chart at the time of deployment.

## Advanced Configuration
## https://docs.gitlab.com/charts/advanced
#
# Documentation for advanced configuration, such as
# - External PostgreSQL
# - External Gitaly
# - External Redis
# - External NGINX
# - External Object Storage providers
# - PersistentVolume configuration

global:
  edition: ce

  # 主机域名配置
  hosts:
    domain: hanxux.clocal       # 主域名，所有服务将基于此域名生成子域名
    https: false             # 是否启用HTTPS（全局开关）
    # 各子组件域名配置（均继承全局HTTPS设置）
    gitlab:
      name: gitlab.hanxux.local    # GitLab核心服务域名
    minio:
      name: gitlab-minio.hanxux.local  # MinIO对象存储服务域名
    registry:
      name: gitlab-registry.hanxux.local  # 容器镜像仓库域名
    kas:
      name: gitlab-kas.hanxux.local  # Kubernetes Agent Server域名

  # Ingress全局配置
  ingress:
    enabled: true                    # 是否启用Ingress控制器
    configureCertmanager: false      # 是否自动申请TLS证书（需要预先安装Cert-Manager）
    class: nginx-default             # 指定Ingress控制器类型为nginx
    tls:
      enabled: false                 # 是否启用TLS终止（HTTPS）

  # 初始管理员密码配置（安全建议：部署后应立即修改）
  initialRootPassword:
    secret: gitlab-initial-root-password  # 存储密码的Secret名称
    key: password                         # Secret中的键名

installCertmanager: false
certmanager:
  installCRDs: false

nginx-ingress:
  enabled: false
nginx-ingress-geo:
  enabled: false

## Installation & configuration of stable/prometheus
## See dependencies in Chart.yaml for current version
prometheus:
  install: false

## Installation & configuration of gitlab/gitlab-runner
## See dependencies in Chart.yaml for current version
gitlab-runner:
  install: false

certmanager-issuer:
  # The email address to register certificates requested from Let's Encrypt.
  # Required if using Let's Encrypt.
  email: email@example.com
~~~

# 安装

~~~sh
helm upgrade -i gitlab -n gitlab . --create-namespace -f values.yaml -f values.dev.yaml
~~~

首先要检查gitlab-migrations-0dd894d-lqzmq这个job的pod状态是否是Completions，如果还是Running，那么gitlab-sidekiq-all-in-1-v2和gitlab-webservice-default这两个deployment会一直卡在CrashLoopBackOff。

部署完成后，gitlab识别不了自行创建的secret，导致一直无法用root/admin123456登录。重建redis和pgsql就会导致pgsql pod一直起不来。并且gitaly这个pod申请PVC要50G，但是values里面根本没法改。非常不方便。遂放弃这种部署方式。
