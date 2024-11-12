# 介绍

# 下载

~~~sh
helm repo add --force-update external-dns https://kubernetes-sigs.github.io/external-dns
helm repo update external-dns
helm pull external-dns/external-dns --version 1.14.4
~~~

# 安装

~~~sh
helm upgrade -i external-dns -n external-dns --version 1.14.4 -f values.yaml --create-namespace
~~~

