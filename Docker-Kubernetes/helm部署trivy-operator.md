# 介绍

- 官网地址：https://aquasecurity.github.io/trivy-operator/v0.22.0/
- 镜像漏洞扫描器

# 下载

~~~sh
helm repo add --force-update aqua https://aquasecurity.github.io/helm-charts
helm repo update aqua
helm pull aqua/trivy-operator --version 0.24.1
~~~

# 配置

~~~yaml
#仿照ado中的配置稍作调整
~~~

# 安装

~~~sh
helm upgrade -i trivy-operator -n trivy-system --create-namespace . -f values.yaml
~~~

# 使用

- 查看漏洞报告

~~~sh
#报告主要关注的是集群中的容器镜像或其他资源是否包含已知的安全漏洞。
kubectl get vulnerabilityreports -o wide
~~~

- 查看配置审计报告

~~~sh
#报告专注于集群资源的配置安全，检查 Kubernetes 资源的配置设置是否遵守安全最佳实践。
kubectl get configauditreports -o wide
~~~

