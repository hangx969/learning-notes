# 介绍

- 官网安装说明：https://www.jenkins.io/doc/book/installing/kubernetes/#install-jenkins-with-helm-v3

# 下载

- 下载helm chart

~~~sh
helm repo add jenkins https://charts.jenkins.io
helm repo update
helm pull jenkins/jenkins
~~~

# 配置

## 配置ingress+tls+oauth

- values文件

~~~yaml
  ingress:
    # -- Enables ingress
    enabled: true

    # Override for the default paths that map requests to the backend
    # -- Override for the default Ingress paths
    paths: []
    # - backend:
    #     serviceName: ssl-redirect
    #     servicePort: use-annotation
    # - backend:
    #     serviceName: >-
    #       {{ template "jenkins.fullname" . }}
    #     # Don't use string here, use only integer value!
    #     servicePort: 8080

    # For Kubernetes v1.14+, use 'networking.k8s.io/v1beta1'
    # For Kubernetes v1.19+, use 'networking.k8s.io/v1'
    # -- Ingress API version
    apiVersion: "extensions/v1beta1"
    # -- Ingress labels
    labels: {}
    # -- Ingress annotations
    annotations:
      nginx.ingress.kubernetes.io/auth-url: "https://oauth2proxy.hanxux.local/oauth2/auth"
      nginx.ingress.kubernetes.io/auth-signin: "https://oauth2proxy.hanxux.local/oauth2/start?rd=https%3A%2F%2Fjenkins.hanxux.local"
      # kubernetes.io/ingress.class: nginx
      # kubernetes.io/tls-acme: "true"
    # For Kubernetes >= 1.18 you should specify the ingress-controller via the field ingressClassName
    # See https://kubernetes.io/blog/2020/04/02/improvements-to-the-ingress-api-in-kubernetes-1.18/#specifying-the-class-of-an-ingress
    ingressClassName: nginx-default

    # Set this path to jenkinsUriPrefix above or use annotations to rewrite path
    # -- Ingress path
    path: /

    # configures the hostname e.g. jenkins.example.com
    # -- Ingress hostname
    hostName: jenkins.hanxux.local
    # -- Hostname to serve assets from
    resourceRootUrl:
    # -- Ingress TLS configuration
    tls:
    - secretName: jenkins-tls-cert-secret
      hosts:
        - jenkins.hanxux.local
~~~

## 配置persistence storage class name

## 挂载本地时区

~~~yaml
  # -- SubPath for jenkins-home mount
  subPath:
  # -- Additional volumes
  volumes:
  - name: local-time
    hostPath:
      path: /etc/localtime
  #  - name: nothing
  #    emptyDir: {}

  # -- Additional mounts
  mounts:
  - mountPath: /etc/localtime
    name: local-time
~~~

## 修改容器特权

> 否则会报错：/var/jenkins_config/apply_config.sh: 4: cannot create /var/jenkins_home/jenkins.install.UpgradeWizard.state: Permission denied
>
> 参考：https://github.com/jenkinsci/helm-charts/issues/210

~~~yaml
controller:
  ...
  # -- Allow controlling the securityContext for the jenkins container
  containerSecurityContext:
    runAsUser: 0
    runAsGroup: 0
    #readOnlyRootFilesystem: true
    allowPrivilegeEscalation: false
  ...
  runAsUser: 0
  runAsGroup: 0
~~~

## 配置k8s集群连接

- values.yaml

~~~yaml
kubernetesURL: "https://172.16.183.100:6443"
controller:
    cloudName: "local-platform-dev"
~~~

- jenkins UI
  - https://jenkins.hanxux.local/manage/cloud 中也可以配置

# 安装

~~~sh
helm upgrade -i jenkins -n jenkins --create-namespace . -f values.yaml
~~~

# 访问jenkins UI

- 获取初始admin密码

  ~~~sh
  kubectl exec --namespace jenkins -it svc/jenkins -c jenkins -- /bin/cat /run/secrets/additional/chart-admin-password && echo
  ~~~

- 客户端/etc/hosts添加记录

- 访问ingress URL：`https://jenkins.hanxux.local`

# 安装blue ocean插件

- manage jenkins - 插件管理 - available plugins - 搜索kubernetes、blueocean - 均选择download node and install after restart

- 安装完kubernetes、blueocean之后，浏览器手动重启jenkins：

  ~~~sh
  https://jenkins.hanxux.local/restart
  ~~~

- 弹出登录界面说明插件安装没问题，可以进行后续实验。

# 配置agent从节点

