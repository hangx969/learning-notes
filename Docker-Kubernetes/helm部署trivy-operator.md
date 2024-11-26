# trivy

## 介绍

- 官网地址：

## 下载

~~~sh
helm repo add --force-update aqua https://aquasecurity.github.io/helm-charts
helm repo update aqua
helm pull aqua/trivy-operator --version 0.24.1
~~~

## 配置

~~~yaml
#仿照ado中的配置稍作调整
~~~

## 安装

~~~sh
echo "Extract trivy CRDs"
tar xvf trivy-operator-$VERSION.tgz trivy-operator/crds
echo "Diff trivy CRDs"
kubectl diff -f ./trivy-operator/crds/ -R
echo "Install Trivy CRDs"
kubectl apply --server-side -f trivy-operator/crds/ -R

helm upgrade -i trivy-operator -n trivy-system --create-namespace . -f values.yaml
~~~

