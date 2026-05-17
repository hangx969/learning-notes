---
title: "Claude Code 实现 CI/CD 自动化发布流程详细指南"
source: "https://mp.weixin.qq.com/s/8P4qxr2iYCC_SraW3SJxjg"
created: 2026-05-17
tags:
  - kubernetes
  - CICD
  - claude-code
  - gitlab-ci
  - kaniko
---

本篇用一个 Vue 前端项目结合 Claude Code 实现一次完整的 CI/CD 发布流程，实现的效果：从内网 GitLab 推送 → Kaniko 构建 → Harbor 推送 → Kubernetes 部署 → Istio 网关暴露，外加 Claude 自动 MR Review、Release Notes、部署失败根因分析。

完整的拓扑流程：

```
开发提交 → GitLab MR
  ↓ Claude MR Review（评论挂到 MR）
  ↓ MR 合并
开发打 tag → GitLab Pipeline
  ↓ Kaniko 构建 → Harbor
  ↓ kubectl apply → k8s（Deployment + Service + VirtualService）
  ↓ Istio Gateway → aiops-lab.eeo-inc.com
  ↓ Claude 自动写 Release Notes（写到 GitLab Release）
失败时 → Claude 拉 pod logs/events → 根因分析（写到 Job log）
```

**关键技术选型**

- 构建：Kaniko（不需要 dind，Runner 不开特权）
- 镜像仓库：内网 Harbor，机器人账号（robot account）
- 部署：原生 kubectl + 三个 yaml（Deployment / Service / VirtualService）
- 网关：复用集群里已有的 istio-system/test-gateway，挂域名
- AI 接入：LiteLLM 中转 OpenAI 兼容协议（/v1/chat/completions）

---

## CI/CD 完整 Pipeline 配置

### 变量与阶段定义

```yaml
variables:
  HARBOR_REGISTRY: "registry.xxx.com"
  HARBOR_PROJECT: "ops/aiops"
  IMAGE_NAME: "trace-analysis-app"
  IMAGE_FULL: "${HARBOR_REGISTRY}/${HARBOR_PROJECT}/${IMAGE_NAME}"
  HARBOR_USER: $CI_REGISTRY_NAME
  HARBOR_PASSWORD: $CI_REGISTRY_PASSWD
  K8S_NAMESPACE: "devops"
  K8S_APP_NAME: "trace-analysis-app"
  CLAUDE_MODEL: $ANTHROPIC_MODEL

stages:
  - review
  - build
  - deploy
  - release
  - notify
```

所有敏感参数（Harbor 账号、kubeconfig、Claude key、Bot token）都通过 GitLab CI/CD Variables 注入，不进 yaml。Settings → CI/CD → Variables，并打 Masked + Protected。

### Kaniko 构建（main 分支 / tag 触发）

```yaml
build-and-push:
  stage: build
  image:
    name: gcr.io/kaniko-project/executor:v1.23.2-debug
    entrypoint: [""]
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
    - if: '$CI_COMMIT_TAG'
  script:
    - export DOCKER_CONFIG="${CI_PROJECT_DIR}/.docker"
    - mkdir -p "${DOCKER_CONFIG}"
    - |
      AUTH=$(echo -n "${HARBOR_USER}:${HARBOR_PASSWORD}" | base64 | tr -d '\n')
      cat > "${DOCKER_CONFIG}/config.json" <<EOF
      {"auths":{"${HARBOR_REGISTRY}":{"auth":"${AUTH}"}}}
      EOF
    - BUILD_TAG="${CI_COMMIT_TAG:-${CI_COMMIT_BRANCH}-${CI_COMMIT_SHORT_SHA}}"
    - /kaniko/executor
        --context "${CI_PROJECT_DIR}"
        --dockerfile "${CI_PROJECT_DIR}/Dockerfile"
        --destination "${IMAGE_FULL}:${BUILD_TAG}"
        --destination "${IMAGE_FULL}:latest"
        --cache=true
        --cache-repo "${IMAGE_FULL}/cache"
    - echo "BUILD_TAG=${BUILD_TAG}" > build.env
  artifacts:
    reports:
      dotenv: build.env
```

### K8s 部署（tag 触发）

```yaml
deploy-k8s:
  stage: deploy
  image: alpine:3.20
  needs:
    - job: build-and-push
      artifacts: true
  rules:
    - if: '$CI_COMMIT_TAG'
  before_script:
    - apk add --no-cache curl ca-certificates
    - |
      ARCH=$(uname -m); KARCH=amd64
      [ "$ARCH" = "aarch64" ] && KARCH=arm64
      curl -fsSL -o /usr/local/bin/kubectl \
        "https://dl.k8s.io/release/v1.29.10/bin/linux/${KARCH}/kubectl"
      chmod +x /usr/local/bin/kubectl
    - export KUBECONFIG="$KUBECONFIG_FILE"
  script:
    - cd deploy/k8s
    - kubectl apply -f namespace.yaml
    - |
      kubectl create secret docker-registry harbor-pull-secret \
        --docker-server="${HARBOR_REGISTRY}" \
        --docker-username="${HARBOR_USER}" \
        --docker-password="${HARBOR_PASSWORD}" \
        --namespace="${K8S_NAMESPACE}" \
        --dry-run=client -o yaml | kubectl apply -f -
    - sed -i "s|__IMAGE_TAG__|${BUILD_TAG:-${CI_COMMIT_TAG}}|g" deployment.yaml
    - kubectl apply -f deployment.yaml -f service.yaml -f virtualservice.yaml
    - kubectl rollout status deployment/${K8S_APP_NAME} -n ${K8S_NAMESPACE} --timeout=180s
```

### Claude MR 评审（任一 MR 触发）

Claude 调用模板（复用基础镜像 + 依赖安装）：

```yaml
.claude-call:
  image: alpine:3.20
  before_script:
    - apk add --no-cache curl jq ca-certificates git
```

实际调用（拼 prompt → jq 装 JSON → curl LiteLLM → 评论挂回 MR）：

```yaml
claude-mr-review:
  stage: review
  extends: .claude-call
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
  script:
    - git fetch origin "$CI_MERGE_REQUEST_TARGET_BRANCH_NAME" --depth=200
    - DIFF=$(git diff "origin/${CI_MERGE_REQUEST_TARGET_BRANCH_NAME}...HEAD" | head -c 200000)
    - echo "$DIFF" > /tmp/diff.txt
    - |
      {
        printf '%s\n' '你是资深前端 + DevOps 工程师，正在评审 GitLab MR。请用中文输出 Markdown：'
        printf '%s\n' '## 总体评价'
        printf '%s\n' '## 必须修改 (🚫)'
        printf '%s\n' '## 建议改进 (💡)'
        printf '%s\n' '## 测试覆盖'
        printf '%s\n' '下面是 diff：'
        printf '%s\n' '\`\`\`diff'
        cat /tmp/diff.txt
        printf '%s\n' '\`\`\`'
      } > /tmp/prompt.txt
    - |
      jq -n --arg model "$ANTHROPIC_MODEL" --rawfile user /tmp/prompt.txt \
        '{model: $model, max_tokens: 2048, messages: [
          {role: "system", content: "你是严谨的代码评审者，输出简洁、可执行。"},
          {role: "user",   content: $user}
        ]}' > /tmp/body.json
    - |
      curl -fsS --max-time 120 -X POST "${ANTHROPIC_BASE_URL%/}/chat/completions" \
        -H "Authorization: Bearer ${ANTHROPIC_API_KEY}" \
        -H "Content-Type: application/json" \
        -d @/tmp/body.json > /tmp/resp.json
    - REVIEW=$(jq -r '.choices[0].message.content' /tmp/resp.json)
    - |
      jq -n --rawfile body <(echo "## 🤖 Claude Review"; echo; echo "$REVIEW") \
        '{body: $body}' > /tmp/note.json
      curl -fsS -X POST -H "PRIVATE-TOKEN: ${CLAUDE_BOT_TOKEN}" \
        -H "Content-Type: application/json" -d @/tmp/note.json \
        "${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/merge_requests/${CI_MERGE_REQUEST_IID}/notes"
  allow_failure: true
```

### 部署失败 → 自动根因分析

```yaml
deploy-failure-rca:
  stage: notify
  extends: .claude-call
  rules:
    - if: '$CI_COMMIT_TAG'
      when: on_failure
  script:
    - kubectl -n "$K8S_NAMESPACE" describe pods -l app=$K8S_APP_NAME > /tmp/diag/describe.txt
    - kubectl -n "$K8S_NAMESPACE" get events --sort-by=.lastTimestamp > /tmp/diag/events.txt
    - kubectl -n "$K8S_NAMESPACE" logs -l app=$K8S_APP_NAME --tail=200 > /tmp/diag/logs.txt
    # 拼 prompt → jq → curl → 解析返回，把 Markdown RCA 直接打印到 job 日志
```

### Tag 推送 → 自动写 Release Notes

```yaml
release-notes:
  stage: release
  extends: .claude-call
  needs: [deploy-k8s]
  rules:
    - if: '$CI_COMMIT_TAG'
  script:
    - PREV_TAG=$(git tag --sort=-creatordate | grep -v "^${CI_COMMIT_TAG}$" | head -n 1)
    - COMMITS=$(git log --pretty=format:"- %s (%h)" "${PREV_TAG}..${CI_COMMIT_TAG}")
    # → 让 Claude 按"✨新功能 / 🐛修复 / 🔧改进 / 📦CI"分类
    # → 调 GitLab Releases API 自动建 Release
```

---

## 核心要点

- 每次合 MR 自动跑 lint / build
- 打 tag 时自动构建镜像 → 推 Harbor → 部署到 K8s
- 走 Istio Gateway 用域名访问，namespace 单独隔离
- AI 自动评审代码、写 Release Notes、部署失败时自动给根因分析
- 所有敏感信息都不能写到 yaml 里，全部走 GitLab CI/CD Variables（Masked + Protected）
