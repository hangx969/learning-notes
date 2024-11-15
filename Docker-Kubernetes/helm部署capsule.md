# 介绍

- 官网：https://capsule.clastix.io/docs/#kubernetes-multi-tenancy-made-easy
- Tenant: capsule是管理multi tenant的工具，什么是tenant？tenant在capsule的语境下可以理解为：一组namespace，可以对其做RBAC授权、设置resource quota、network policy等。

# 下载

~~~sh
helm repo add --force-update clastix https://clastix.github.io/charts
helm repo update clastix
helm pull clastix/capsule --version helm-v0.4.6
~~~

# 配置

- 我们ado中仅仅指定了capsuleUserGroups，用的是AAD的group
- capsuleUserGroups解释：用于配置可以访问和管理 Capsule 功能的用户组。在默认提供的 `values.yaml` 中，指定了 `capsuleUserGroups: ["capsule.clastix.io"]`，这意味着只有属于 `capsule.clastix.io` 这个用户组的用户或服务账户可以进行与 Capsule 相关的操作

# 安装

~~~sh
helm upgrade -i capsule -n capsule-system --create-namespace --skip-crds -f $DIRECTORY/external/capsule/values.yaml -f $DIRECTORY/external/capsule/${{parameters.environment}}.${{parameters.region}}.yaml

~~~

