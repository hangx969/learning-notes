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
installCertmanager: false
certmanager:
  installCRDs: false

nginx-ingress: &nginx-ingress
  enabled: false

nginx-ingress-geo:
  <<: *nginx-ingress
  enabled: false

prometheus:
  install: false

gitlab-runner:
~~~

# 安装

~~~sh
helm uprade -i gitlab -n gitlab . --create-namespace -f values.yaml -f values.dev.yaml
~~~

