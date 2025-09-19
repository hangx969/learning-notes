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
  ingress:
    configureCertmanager: false
  edition: ce

installCertmanager: false
certmanager:
  installCRDs: false

nginx-ingress: &nginx-ingress
  enabled: false

nginx-ingress-geo:
  <<: *nginx-ingress
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
helm uprade -i gitlab -n gitlab . --create-namespace -f values.yaml -f values.dev.yaml
~~~

装完之后，gitlab-sidekiq-all-in-1-v2和gitlab-webservice-default这两个deployment会莫名其妙的CrashLoopBackOff起不来。调高虚拟机内存到12G也不行。报错信息非常隐晦根本看不出问题。
