# ReplicaSet - rs

## 示例

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: rs-ft
  namespace: default
  labels:
    app: guestbook
    tier: frontend
spec:
  replicas: 3
  selector: # 在.spec.selector中定义的标签选择器必须能够匹配到spec.template.metadata.labels里定义的Pod标签
    matchLabels:
      tier1: frontend1
  template:
    metadata:
      labels:
        tier1: frontend1
    spec:
      containers:
      - name: samples-gb-frontend
        image: docker.io/yecc/gcr.io-google_samples-gb-frontend:v3
        imagePullPolicy: IfNotPresent
        ports: 
        - containerPort: 80
        startupProbe:
          initialDelaySeconds: 20
          periodSeconds: 5
          timeoutSeconds: 10
          httpGet:
            scheme: HTTP
            port: 80
            path: /
        livenessProbe:
          initialDelaySeconds: 20
          periodSeconds: 5
          timeoutSeconds: 10
          httpGet:
            scheme: HTTP
            port: 80
            path: /
        readinessProbe:
          initialDelaySeconds: 20
          periodSeconds: 5
          timeoutSeconds: 10
          httpGet:
            scheme: HTTP
            port: 80
            path: /
```

## 缺点

- 更新管理上不如deployment灵活。