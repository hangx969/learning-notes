# 介绍

- 官网地址：
  - https://github.com/config-syncer/config-syncer
  - https://config-syncer.com/docs/v0.15.2/guides/config-syncer/


# 下载

~~~sh
              helm repo add --force-update appscode https://charts.appscode.com/stable
              helm repo update appscode
              helm pull appscode/kubed --version "${CONFIG_SYNCER_VERSION#v}"
~~~

- 注意：镜像从ACR拉取

# 配置

- 

# 安装

~~~sh
helm template oci://crcommoninfra${{parameters.environment}}${{parameters.region}}.azurecr.cn/helm/kubed -f $DIRECTORY/external/config-syncer/${{parameters.environment}}.${{parameters.region}}.yaml

helm upgrade -i config-syncer -n kube-system \ oci://crcommoninfra${{parameters.environment}}${{parameters.region}}.azurecr.cn/helm/kubed \ --history-max 3 \ --version $CHART_VERSION \ -f $DIRECTORY/external/config-syncer/${{parameters.environment}}.${{parameters.region}}.yaml \ --set config.additionalOptions="{--resync-period=30s}"
~~~
