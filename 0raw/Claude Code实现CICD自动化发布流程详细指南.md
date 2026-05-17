---
title: "Claude Code实现CICD自动化发布流程详细指南"
source: "https://mp.weixin.qq.com/s/8P4qxr2iYCC_SraW3SJxjg"
author:
  - "[[认真做自己]]"
published:
created: 2026-05-17
description: "本篇用一个vue前端项目结合Claude Code实现一次完整的CICD发布流程，实现的效果：从内网 Git"
tags:
  - "clippings"
---
认真做自己 *2026年5月16日 19:53*

本篇用一个vue前端项目结合Claude Code实现一次完整的CICD发布流程，实现的效果：从内网 GitLab 推送 → Kaniko 构建 → Harbor 推送 → Kubernetes 部署 → Istio 网关暴露，外加 Claude 自动 MR Review、Release Notes、部署失败根因分析。先看效果图：

![image.png](https://mmbiz.qpic.cn/sz_mmbiz_png/WdiaYZu25QiaicMNTZ0kPpUS5gqUibuo8zvxw1TwQB3GQ6SB2zU6tjDvZhYmpyYbGO6kFyW8Ym48HvNNehwJqc5peo68CCQUWOmufLe1avbTuI4/640?from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

- 每次合 MR 自动跑 lint / build
- 打 tag 时自动构建镜像 → 推 Harbor → 部署到 k8s
- 走 Istio Gateway 用域名访问，namespace 单独隔离
- AI 自动评审代码、写 Release Notes、部署失败时自动给根因分析
- 所有敏感信息都不能写到 yaml 里

完整的拓扑流程：

```markdown
开发提交 → GitLab MR   ↓ Claude MR Review（评论挂到 MR）   ↓ MR 合并开发打 tag → GitLab Pipeline   ↓ Kaniko 构建 → Harbor   ↓ kubectl apply → k8s（Deployment + Service + VirtualService）   ↓ Istio Gateway → aiops-lab.eeo-inc.com   ↓ Claude 自动写 Release Notes（写到 GitLab Release）失败时 → Claude 拉 pod logs/events → 根因分析（写到 Job log）
```
![image.png](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

**关键技术选型**

- 构建：Kaniko（不需要 dind，Runner 不开特权）
- 镜像仓库：内网 Harbor，机器人账号（robot account）
- 部署：原生 kubectl + 三个 yaml（Deployment / Service / VirtualService）
- 网关：复用集群里已有的 istio-system/test-gateway，挂域名
- AI 接LiteLLM 中转 OpenAI 兼容协议（/v1/chat/completions）

**CICD完整yaml**

![image.png](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

具体配置如下：

```yaml
variables:HARBOR_REGISTRY:"registry.xxx.com"HARBOR_PROJECT:"ops/aiops"IMAGE_NAME:"trace-analysis-app"IMAGE_FULL:"${HARBOR_REGISTRY}/${HARBOR_PROJECT}/${IMAGE_NAME}"HARBOR_USER:$CI_REGISTRY_NAMEHARBOR_PASSWORD:$CI_REGISTRY_PASSWDK8S_NAMESPACE:"devops"K8S_APP_NAME:"trace-analysis-app"CLAUDE_MODEL:$ANTHROPIC_MODELstages:-review-build-deploy-release-notify
```

所有敏感参数（Harbor 账号、kubeconfig、Claude key、Bot token）都通过 GitLab CI/CD Variables 注入，不进 yaml。

**Kaniko 构建（main 分支 / tag 触发）**

```yaml
build-and-push:stage:buildimage:name:gcr.io/kaniko-project/executor:v1.23.2-debugentrypoint:[""]rules:-if:'$CI_COMMIT_BRANCH=="main"'-if:'$CI_COMMIT_TAG'script:-exportDOCKER_CONFIG="${CI_PROJECT_DIR}/.docker"-mkdir-p"${DOCKER_CONFIG}"    -|      AUTH=$(echo-n"${HARBOR_USER}:${HARBOR_PASSWORD}"|base64|tr-d'\n')      cat>"${DOCKER_CONFIG}/config.json"<<EOF      {"auths":{"${HARBOR_REGISTRY}":{"auth":"${AUTH}"}}}      EOF- BUILD_TAG="${CI_COMMIT_TAG:-${CI_COMMIT_BRANCH}-${CI_COMMIT_SHORT_SHA}}"- /kaniko/executor        --context "${CI_PROJECT_DIR}"        --dockerfile "${CI_PROJECT_DIR}/Dockerfile"        --destination"${IMAGE_FULL}:${BUILD_TAG}"        --destination"${IMAGE_FULL}:latest"        --cache=true        --cache-repo"${IMAGE_FULL}/cache"-echo"BUILD_TAG=${BUILD_TAG}">build.envartifacts:reports:dotenv:build.env
```

**k8s 部署**

```yaml
deploy-k8s:stage:deployimage:alpine:3.20needs:-job:build-and-pushartifacts:truerules:-if:'$CI_COMMIT_TAG'before_script:-apkadd--no-cachecurlca-certificates    -|      ARCH=$(uname-m);KARCH=amd64      [ "$ARCH"="aarch64" ] &&KARCH=arm64      curl-fsSL-o/usr/local/bin/kubectl\        "https://dl.k8s.io/release/v1.29.10/bin/linux/${KARCH}/kubectl"      chmod+x/usr/local/bin/kubectl-exportKUBECONFIG="$KUBECONFIG_FILE"script:-cddeploy/k8s-kubectlapply-fnamespace.yaml    -|      kubectlcreatesecretdocker-registryharbor-pull-secret\        --docker-server="${HARBOR_REGISTRY}"\        --docker-username="${HARBOR_USER}"\        --docker-password="${HARBOR_PASSWORD}"\        --namespace="${K8S_NAMESPACE}"\        --dry-run=client-oyaml|kubectlapply-f--sed-i"s|__IMAGE_TAG__|${BUILD_TAG:-${CI_COMMIT_TAG}}|g"deployment.yaml-kubectlapply-fdeployment.yaml-fservice.yaml-fvirtualservice.yaml-kubectlrolloutstatusdeployment/${K8S_APP_NAME}-n${K8S_NAMESPACE}--timeout=180s
```

**Claude MR 评审（任一 MR 触发）**

**![image.png](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)**

调用模版

```yaml
.claude-call:image:alpine:3.20before_script:-apkadd--no-cachecurljqca-certificatesgit
```

实际调用（拼 prompt → jq 装 JSON → curl LiteLLM → 评论挂回 MR）：

```yaml
claude-mr-review:stage:reviewextends:.claude-callrules:-if:'$CI_PIPELINE_SOURCE=="merge_request_event"'script:- git fetch origin "$CI_MERGE_REQUEST_TARGET_BRANCH_NAME" --depth=200- DIFF=$(git diff "origin/${CI_MERGE_REQUEST_TARGET_BRANCH_NAME}...HEAD" | head -c 200000)- echo "$DIFF" > /tmp/diff.txt    -|      {        printf '%s\n''你是资深前端 + DevOps 工程师，正在评审 GitLab MR。请用中文输出 Markdown：'        printf'%s\n''## 总体评价'        printf'%s\n''## 必须修改 (🚫)'        printf'%s\n''## 建议改进 (💡)'        printf'%s\n''## 测试覆盖'        printf'%s\n''下面是 diff：'        printf'%s\n''\`\`\`diff'        cat/tmp/diff.txt        printf'%s\n''\`\`\`'      }>/tmp/prompt.txt    -|      jq-n--argmodel"$ANTHROPIC_MODEL"--rawfileuser/tmp/prompt.txt\        '{model:$model, max_tokens:2048, messages:[          {role:"system", content:"你是严谨的代码评审者，输出简洁、可执行。"},          {role:"user",   content: $user}        ]}' >/tmp/body.json    -|      curl-fsS--max-time120-XPOST"${ANTHROPIC_BASE_URL%/}/chat/completions"\        -H"Authorization: Bearer ${ANTHROPIC_API_KEY}"\        -H"Content-Type: application/json"\        -d@/tmp/body.json>/tmp/resp.json-REVIEW=$(jq-r'.choices[0].message.content'/tmp/resp.json)    -|      jq-n--rawfilebody<(echo"## 🤖 Claude Review";echo;echo"$REVIEW")'{body:$body}'>/tmp/note.json      curl-fsS-XPOST-H"PRIVATE-TOKEN: ${CLAUDE_BOT_TOKEN}"\        -H"Content-Type: application/json"-d@/tmp/note.json\        "${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/merge_requests/${CI_MERGE_REQUEST_IID}/notes"allow_failure:true
```

**部署失败 → 自动根因分析**

```yaml
deploy-failure-rca:stage:notifyextends:.claude-callrules:-if:'$CI_COMMIT_TAG'when:on_failurescript:-kubectl-n"$K8S_NAMESPACE"describepods-lapp=$K8S_APP_NAME>/tmp/diag/describe.txt-kubectl-n"$K8S_NAMESPACE"getevents--sort-by=.lastTimestamp>/tmp/diag/events.txt-kubectl-n"$K8S_NAMESPACE"logs-lapp=$K8S_APP_NAME--tail=200>/tmp/diag/logs.txt    # 拼 prompt → jq → curl → 解析返回，把 Markdown RCA 直接打印到 job 日志
```

**tag 推送 → 自动写 Release Notes**

```yaml
release-notes:stage:releaseextends:.claude-callneeds:[deploy-k8s]rules:-if:'$CI_COMMIT_TAG'script:-PREV_TAG=$(gittag--sort=-creatordate|grep-v"^${CI_COMMIT_TAG}$"|head-n1)-COMMITS=$(gitlog--pretty=format:"-%s(%h)""${PREV_TAG}..${CI_COMMIT_TAG}")    # → 让 Claude 按"✨新功能 / 🐛修复 / 🔧改进 / 📦CI"分类    # → 调 GitLab Releases API 自动建 Release
```

**敏感信息怎么放**

一行 yaml 都不写敏感字段，全部放到Settings → CI/CD → Variables，并打 Masked + Protected：

![image.png](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

**版本演进时间线**

**![image.png](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)**

**结语**

通过这套方案使用，平时测试环境发布代码方便了很多，之前需要手工操作tag、写commit等内容，完全交由AI完成，在聊天过程中就完成了整个系统的发布，很丝滑。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E "undefined")

**谷雨时节**

雨生百谷

万物生长

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

<上一篇· [从 0 到 1 搭建 Confluence 内部 Wiki RAG 知识库增强检索系统：正文、评论、附件、图片全量打通](https://mp.weixin.qq.com/s?__biz=MzkxNDczMzQ1Mw==&mid=2247484192&idx=1&sn=b9b113b06774ba07e4709b9794f4206b&scene=21#wechat_redirect)

**微信扫一扫赞赏作者**

AI运维 · 目录

作者提示: 个人观点，仅供参考

继续滑动看下一个

老甄说运维

向上滑动看下一个