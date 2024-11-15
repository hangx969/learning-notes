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
helm upgrade -i capsule -n capsule-system --create-namespace . -f values.yaml #--skip-crds
~~~

# 使用

## 创建user和group

- azure中可以直接用EntraID with Azure RBAC的模式把entraID group

- lab中：先创建一个user

  - SSL认证

    ```bash
    #生成私钥
    cd /etc/kubernetes/pki/
    (umask 077; openssl genrsa -out hangx.key 2048) 
    #生成证书请求
    openssl req -new -key hangx.key -out hangx.csr -subj "/CN=hangx"
    #生成证书，表明这个用户被api server信任
    openssl x509 -req -in hangx.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out hangx.crt -days 3650
    ```

  - 配置k8s用户

    ```bash
    #把hangx用户添加到集群中，可以用来认证apiserver的连接
    kubectl config set-credentials hangx --client-certificate=./hangx.crt --client-key=./hangx.key --embed-certs=true
    #在kubeconfig中新增hangx账号
    kubectl config set-context hangx@kubernetes --cluster=kubernetes --user=hangx
    #切换到hangx用户
    kubectl config use-context hangx@kubernetes
    #切回cluster-admin
    kubectl config use-context kubernetes-admin@kubernetes
    #给hangx用户rolebinding授权
    kubectl create ns hangx-test
    kubectl create rolebinding hangx -n hangx-test --clusterrole=cluster-admin --user=hangx
    #切换用户，测试权限
    kubectl config use-context hangx@kubernetes
    kubectl get pods -n hangx-test
    ```

  - 配置linux客户端的用户，让他能用hangx的config文件访问集群

    ```bash
    useradd hangx
    #config文件的拷贝：得把/root/.kube/一整个目录拷贝过去
    cp -ar /root/.kube/ /tmp/
    #修改/tmp/.kube/config文件，把kubernetes-admin相关的删除，只留hangx用户
    #kubeconfig文件拷贝到这个用户的家目录
    cp -ar /tmp/.kube/ /home/hangx/
    #root用户下操作，修改.kube目录的属主、属组为hangx
    chown -R hangx.hangx /home/hangx/.kube
    #切换用户
    su - hangx
    #验证权限
    k get po -n hangx-test
    ```

- ## 

## helm创建tenant

~~~yaml
~~~

