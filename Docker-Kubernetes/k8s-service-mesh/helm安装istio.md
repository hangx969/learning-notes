# 下载

- 官网教程：[Istio / 使用 Helm 安装](https://istio.io/latest/zh/docs/setup/install/helm/)
- github release: [istio/istio: Connect, secure, control, and observe services.](https://github.com/istio/istio)
- artifacthub: [istiod 1.27.1 · istio/istio-official](https://artifacthub.io/packages/helm/istio-official/istiod)

~~~sh
helm repo add istio https://istio-release.storage.googleapis.com/charts
helm repo update
helm pull istio/base --version 1.27.1
helm pull istio/istiod --version 1.27.1
helm pull istio/gateway --version 1.27.1
~~~

# 安装

## 安装base chart

~~~sh
helm upgrade -i istio-base -n istio-system . -f values.yaml --set defaultRevision=default --create-namespace
~~~

## 安装istiod

values.dev.yaml

~~~yaml
# "_internal_defaults_do_not_set" is a workaround for Helm limitations. Users should NOT set "._internal_defaults_do_not_set" explicitly, but rather directly set the fields internally.
# For instance, instead of `--set _internal_defaults_do_not_set.foo=bar``, just set `--set foo=bar`.
_internal_defaults_do_not_set:

  meshConfig:
    enablePrometheusMerge: true
    accessLogEncoding: JSON
    accessLogFile: /dev/stdout

  global:
    # A minimal set of requested resources to applied to all deployments so that
    # Horizontal Pod Autoscaler will be able to function (if set).
    # Each component can overwrite these default values by adding its own resources
    # block in the relevant section below and setting the desired resources values.
    defaultResources:
      requests:
        cpu: 50m
        memory: 128Mi
      # limits:
      #   cpu: 100m
      #   memory: 128Mi
    # Default hub for Istio images.
    # Releases are published to docker hub under 'istio' project.
    # Dev builds from prow are on gcr.io
    hub: m.daocloud.io/docker.io/istio
    imagePullPolicy: "IfNotPresent"
~~~

~~~sh
helm upgrade -i istiod -n istio-system . -f values.yaml -f values.dev.yaml
~~~

## 安装gateway

values.dev.yaml:

~~~yaml
_internal_defaults_do_not_set:

  service:
    type: NodePort
    ports:
    - name: status-port
      port: 15020
      protocol: TCP
      targetPort: 15020
      nodePort: 30520
    - name: http2
      port: 80
      protocol: TCP
      targetPort: 8080
      nodePort: 30080
    - name: https
      port: 443
      protocol: TCP
      targetPort: 8443
      nodePort: 30443

  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 2000m
      memory: 1024Mi

  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 5
    targetCPUUtilizationPercentage: 80
    targetMemoryUtilizationPercentage: {}
    autoscaleBehavior: {}

  imagePullPolicy: "IfNotPresent"
~~~

~~~sh
helm upgrade -i gateway -n istio-system . -f values.yaml -f values.dev.yaml
~~~

