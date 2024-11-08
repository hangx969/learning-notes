# 介绍



# 下载

~~~sh
curl -LO https://github.com/kubernetes/ingress-nginx/releases/download/helm-chart-$VERSION/ingress-nginx-$VERSION.tgz

helm push ingress-nginx-$VERSION.tgz oci://crcommoninfra${{parameters.environment}}${{parameters.region}}.azurecr.io/helm

helm upgrade -i ingress-nginx -n ingress-nginx oci://crcommoninfra${{parameters.environment}}${{parameters.region}}.azurecr.io/helm/ingress-nginx --version $VERSION --history-max 3 -f $DIRECTORY/external/nginx/${{parameters.environment}}.${{parameters.region}}.yaml
~~~



# 安装

# 配置
