# 介绍

- 官网地址：
  - https://artifacthub.io/packages/helm/sonarqube/sonarqube#production-use-case
  - https://docs.sonarsource.com/sonarqube-server/10.5/setup-and-upgrade/deploy-on-kubernetes/sonarqube/

- SonarQube是一个开源的代码质量管理系统，用于自动化检查源代码的质量并提供报告。它支持多种编程语言，包括Java、C#、JavaScript、Python等，能够检测出代码中的错误、漏洞、代码异味等问题。SonarQube可以集成到CI/CD流程中，帮助开发团队在开发过程中持续改进代码质量。


# 下载

~~~sh
helm repo add --force-update sonarqube https://SonarSource.github.io/helm-chart-sonarqube
helm repo update sonarqube
helm pull sonarqube/sonarqube --version 10.3.0+2009
~~~

# 配置

- 创建https证书

  ~~~yaml
  kubectl create ns snoarqube
  
  tee certificate-snoarqube.yaml <<'EOF'
  apiVersion: cert-manager.io/v1
  kind: Certificate
  metadata:
    name: cert-snoarqube
    namespace: snoarqube
  spec:
    secretName: snoarqube-tls-cert-secret
    privateKey:
      rotationPolicy: Always
    commonName: snoarqube.hanxux.local
    dnsNames:
      - snoarqube.hanxux.local
    usages:
      - digital signature
      - key encipherment
      - server auth
    issuerRef:
      name: selfsigned
      kind: ClusterIssuer
  EOF
  ~~~

- ingress、tls配置

  ~~~yaml
  ingress:
    enabled: true
    # Used to create an Ingress record.
    hosts:
      - name: sonarqube.hanxux.local
        # Different clouds or configurations might need /* as the default path
        path: /
        # For additional control over serviceName and servicePort
        serviceName: sonarqube-sonarqube
        servicePort: 9000
        # the pathType can be one of the following values: Exact|Prefix|ImplementationSpecific(default)
        pathType: ImplementationSpecific
    annotations:
    # kubernetes.io/tls-acme: "true"
  
    # Set the ingressClassName on the ingress record
    ingressClassName: nginx-default
  
  # Additional labels for Ingress manifest file
    # labels:
    #  traffic-type: external
    #  traffic-type: internal
    tls:
    # Secrets must be manually created in the namespace. To generate a self-signed certificate (and private key) and then create the secret in the cluster please refer to official documentation available at https://kubernetes.github.io/ingress-nginx/user-guide/tls/#tls-secrets
    - secretName: snoarqube-tls-cert-secret
      hosts:
        - sonarqube.hanxux.local
  ~~~

  > 注意：sonarqube目前暂不支持Oauth

# 安装

~~~sh
helm upgrade -i sonarqube -n sonarqube --create-namespace . -f values.yaml
~~~

# 使用

- 与azure devops集成：https://docs.sonarsource.com/sonarqube-server/10.5/devops-platform-integration/azure-devops-integration/55
