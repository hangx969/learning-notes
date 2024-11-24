# 介绍

- 官网地址：https://github.com/stakater/Reloader
- configMap和secret


# 下载

~~~sh
helm repo add stakater https://stakater.github.io/stakater-charts
helm repo update stakater
helm pull stakater/reloader --version 1.0.115
~~~

# 配置

- 


# 安装

~~~sh
helm upgrade -i reloader -n reloader --create-namespace . -f values.yaml
~~~
