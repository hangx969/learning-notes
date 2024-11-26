# 介绍

- 官网地址：
  - https://github.com/config-syncer/config-syncer
  - https://config-syncer.com/docs/v0.15.2/guides/config-syncer/


# 下载

~~~sh
helm repo add --force-update appscode https://charts.appscode.com/stable
helm repo update appscode
helm pull appscode/kubed --version "${CONFIG_SYNCER_VERSION#v}" #0.13.2
~~~

# 配置

# 安装

~~~sh
helm template oci://crcommoninfra${{parameters.environment}}${{parameters.region}}.azurecr.cn/helm/kubed -f $DIRECTORY/external/config-syncer/${{parameters.environment}}.${{parameters.region}}.yaml

helm upgrade -i config-syncer -n kube-system \ oci://crcommoninfra${{parameters.environment}}${{parameters.region}}.azurecr.cn/helm/kubed \ --history-max 3 \ --version $CHART_VERSION \ -f $DIRECTORY/external/config-syncer/${{parameters.environment}}.${{parameters.region}}.yaml \ --set config.additionalOptions="{--resync-period=30s}"
~~~

> - 由于当前镜像存在ACR中暂时获取不到，自己build直接报错。先暂停测试。后面可以尝试用官网提供的license方法来部署。

# 使用

- 参考官网：https://config-syncer.com/docs/v0.15.2/guides/config-syncer/intra-cluster/#namespace-selector

- 将configMap同步到其他namespace：

  - 如果创建了一个configMap/Secret，具有annotation：**`kubed.appscode.com/sync: ""`**，config-syncer会把自动同步到其他所有namespace。
  - 如果创建了一个configMap/Secret，具有annotation：**`kubed.appscode.com/sync: "app=kubed"`**，config-syncer会把自动同步到具有标签：app=kubed的所有namespace。


> 注意：
>
> - 源secret/ConfigMap是在**annotation**中设置**`kubed.appscode.com/sync: "app=kubed"`**
> - 需要被同步的目的namespace是在**label**中设置**`app=kubed`**

