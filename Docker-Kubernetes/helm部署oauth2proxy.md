# 介绍

- 是一款对k8s应用做身份验证的反向代理。
- 官网：https://oauth2-proxy.github.io/oauth2-proxy/installation/
- github：https://github.com/oauth2-proxy/oauth2-proxy

# 下载

~~~sh
helm repo add --force-update oauth2-proxy https://oauth2-proxy.github.io/manifests
helm repo update oauth2-proxy
helm pull oauth2-proxy/oauth2-proxy --version 7.7.1
~~~

# 安装

~~~sh
helm upgrade -i oauth2-proxy -n oauth2-proxy --create-namespace . -f values.yaml 
#--set config.clientID='$(oauth2proxy-client-id)' 
#--set config.clientSecret='$(oauth2proxy-client-secret)' 
#--set config.cookieSecret='$(oauth2proxy-cookie-secret)'
~~~

# 配置

~~~sh
~~~

