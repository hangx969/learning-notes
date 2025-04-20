# 介绍

goldilick是一个开源工具，帮助确定资源的resource request/limit

- 官网链接：https://goldilocks.docs.fairwinds.com/#how-can-this-help-with-my-resource-settings

- github link: https://github.com/FairwindsOps/goldilocks
- release page: https://github.com/FairwindsOps/goldilocks/releases
- artifact hub: https://artifacthub.io/packages/helm/fairwinds-stable/goldilocks

# 下载

- 下载helm chart

~~~sh
helm repo add fairwinds-stable https://charts.fairwinds.com/stable
helm repo update fairwinds-stable
helm pull fairwinds-stable/goldilocks --version 9.0.1
~~~

# 配置

- values文件

~~~yaml
controller:
  flags:
    on-by-default: true
dashboard:
  flags:
    on-by-default: true

  ingress:
    enabled: true
    ingressClassName: nginx-default
    hosts:
    - host: goldilocks.hanxux.local
      paths:
      - path: /
        type: ImplementationSpecific
    tls:
      - secretName: goldilocks-tls-cert-secret
        hosts:
          - goldilocks.hanxux.local
    annotations:
      nginx.ingress.kubernetes.io/auth-url: "https://oauth2proxy.hanxux.local/oauth2/auth"
      nginx.ingress.kubernetes.io/auth-signin: "https://oauth2proxy.hanxux.local/oauth2/start?rd=https%3A%2F%2Fgoldilocks.hanxux.local"
~~~

- 配置namespace: https://goldilocks.docs.fairwinds.com/advanced/#cli-usage-not-recommended

  在goldilocks controller的配置下添加args：

  - `--on-by-default` - create VPAs in all namespaces
  - `--include-namespaces` - create VPAs in these namespaces, in addition to any that are labeled
  - `--exclude-namespaces` - when `--on-by-default` is set, exclude this comma-separated list of namespaces
  - `--ignore-controller-kind` - comma-separated list of controller kinds to ignore from automatic VPA creation. For example: `--ignore-controller-kind=Job,CronJob`

# 安装

~~~sh
helm upgrade -i goldilocks fairwinds-stable/goldilocks --namespace goldilocks \
--history-max 5 \
--values goldilocks/values.yaml \
--create-namespace \
--version $VERSION
~~~

# 使用

## UI

首先在本地hosts文件中添加goldilocks.hanxux.local的映射，浏览器访问goldilocks.hanxux.local即可看到UI

## 生成recommendation

生成recommendation的原理：goldilock从vpa的recommender读取资源值

https://goldilocks.docs.fairwinds.com/faq/#how-does-goldilocks-generate-recommendations

## 切换updateMode

默认情况下是采用off mode，可以通过给某个namespace加label来对其中的pod改用Auto模式：https://goldilocks.docs.fairwinds.com/advanced/#cli-usage-not-recommended
