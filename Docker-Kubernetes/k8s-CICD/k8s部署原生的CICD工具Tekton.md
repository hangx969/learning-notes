# Tekton

## 介绍

- Tekton 是一个功能强大且灵活的 Kubernetes 原生开源框架，是谷歌开源的，功能强大且灵活，开源社区也正在快速的迭代和发展壮大，主要用于创建持续集成和交付（CI/CD）系统。通过抽象底层实现细节，用户可以跨多云平台和本地系统进行构建、测试和部署。另外，基于kubernetes CRD定义的pipeline流水线也是Tekton最重要的特征。
- 它原本是 knative 项目里面一个叫做 build-pipeline 的子项目，用来作为 knative-build 的下一代引擎。然而，随着 k8s 社区里各种各样的需求涌入，这个子项目慢慢成长为一个通用的框架，能够提供灵活强大的能力去做基于 k8s 的构建发布。Tekton 其实只提供 Pipeline 这个一个功能，Pipeline 会被直接映射成 K8s Pod 等 API 资源。而比如应用发布过程的控制，灰度和上线策略，都是我们自己编写 K8s Controller来实现的，也就意味着 Tekton 不会在K8s 上盖一个”大帽子“，比如我们想看发布状态、日志等是直接通过 K8s 查看这个 Pipeline 对应的 Pod 的状态和日志，不需要再面对另外一个 API。

## 自动发布流程

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202405211038230.png" alt="image-20240521103838163" style="zoom: 67%;" />

1. 用户把需要部署的应用先按照一套标准的应用定义写成 YAML 文件（类似 Helm Chart）；
2. 用户把应用定义 YAML 推送到 Git 仓库里；
3. Tekton CD (一个 K8s Operator) 会监听到相应的改动，根据不同条件生成不同的 Tekton Pipelines；
4. Tekton CD 的操作具体分为以下几种情况：
   - 如果 Git 改动里有一个应用 YAML 且该应用不存在，那么将渲染和生成 Tekton Pipelines 用来创建应用。
   - 如果 Git 改动里有一个应用 YAML 且该应用存在，那么将渲染和生成 Tekton Pipelines 用来升级应用。这里我们会根据应用定义 YAML 里的策略来做升级，比如做金丝雀发布、灰度升级。
   - 如果 Git 改动里有一个应用 YAML 且该应用存在且标记了“被删除”，那么将渲染和生成 Tekton Pipelines 用来删除应用。确认应用被删除后，我们才从 Git 里删除这个应用的 YAML

## 术语

Tekton 为Kubernetes 提供了多种 CRD 资源对象，可用于定义我们的流水线，主要有以下几个CRD资源对象：

- Task：表示执行命令的一系列步骤，task 里可以定义一系列的 steps，例如编译代码、构建镜像、推送镜像等，每个 step 实际由一个 Pod 里的容器执行。
- TaskRun：task只是定义了一个模版，taskRun 才真正代表了一次实际的运行，当然你也可以自己手动创建一个taskRun，taskRun创建出来之后，就会自动触发task描述的构建任务。
- Pipeline：一组任务，表示一个或多个task、PipelineResource 以及各种定义参数的集合。
- PipelineRun：类似task和taskRun的关系，pipelineRun也表示某一次实际运行的 pipeline，下发一个 pipelineRun CRD 实例到 Kubernetes后，同样也会触发一次 pipeline 的构建。
- PipelineResource：表示pipeline输入资源，比如github上的源码，或者pipeline 输出资源，例如一个容器镜像或者构建生成的jar包等。

# 安装Tekton

## 准备镜像和安装文件

~~~sh
#把tekton-0-12-0.tar.gz和busybox-v-1-0.tar.gz上传到worker node机器上，手动解压：
docker load -i tekton-0-12-0.tar.gz
docker load -i busybox-v-1-0.tar.gz
vim release.yaml
~~~

~~~yaml
# Copyright 2019 The Tekton Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

apiVersion: v1
kind: Namespace
metadata:
  name: tekton-pipelines

---
# Copyright 2019 The Tekton Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: tekton-pipelines
spec:
  privileged: false
  allowPrivilegeEscalation: false
  volumes:
  - 'emptyDir'
  - 'configMap'
  - 'secret'
  hostNetwork: false
  hostIPC: false
  hostPID: false
  runAsUser:
    rule: 'RunAsAny'
  seLinux:
    rule: 'RunAsAny'
  supplementalGroups:
    rule: 'MustRunAs'
    ranges:
    - min: 1
      max: 65535
  fsGroup:
    rule: 'MustRunAs'
    ranges:
    - min: 1
      max: 65535

---
# Copyright 2020 The Tekton Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: tekton-pipelines-controller-cluster-access
rules:
- apiGroups: [""]
  # Namespace access is required because the controller timeout handling logic
  # iterates over all namespaces and times out any PipelineRuns that have expired.
  # Pod access is required because the taskrun controller wants to be updated when
  # a Pod underlying a TaskRun changes state.
  resources: ["namespaces", "pods"]
  verbs: ["list", "watch"]
  # Controller needs cluster access to all of the CRDs that it is responsible for
  # managing.
- apiGroups: ["tekton.dev"]
  resources: ["tasks", "clustertasks", "taskruns", "pipelines", "pipelineruns", "pipelineresources",
    "conditions"]
  verbs: ["get", "list", "create", "update", "delete", "patch", "watch"]
- apiGroups: ["tekton.dev"]
  resources: ["taskruns/finalizers", "pipelineruns/finalizers"]
  verbs: ["get", "list", "create", "update", "delete", "patch", "watch"]
- apiGroups: ["tekton.dev"]
  resources: ["tasks/status", "clustertasks/status", "taskruns/status", "pipelines/status",
    "pipelineruns/status", "pipelineresources/status"]
  verbs: ["get", "list", "create", "update", "delete", "patch", "watch"]
- apiGroups: ["policy"]
  resources: ["podsecuritypolicies"]
  resourceNames: ["tekton-pipelines"]
  verbs: ["use"]
---
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  # This is the access that the controller needs on a per-namespace basis.
  name: tekton-pipelines-controller-tenant-access
rules:
- apiGroups: [""]
  resources: ["pods", "pods/log", "secrets", "events", "serviceaccounts", "configmaps",
    "persistentvolumeclaims", "limitranges"]
  verbs: ["get", "list", "create", "update", "delete", "patch", "watch"]
  # Unclear if this access is actually required.  Simply a hold-over from the previous
  # incarnation of the controller's ClusterRole.
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list", "create", "update", "delete", "patch", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments/finalizers"]
  verbs: ["get", "list", "create", "update", "delete", "patch", "watch"]
---
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: tekton-pipelines-webhook-cluster-access
rules:
- # The webhook needs to be able to list and update customresourcedefinitions,
  # mainly to update the webhook certificates.
  apiGroups: ["apiextensions.k8s.io"]
  resources: ["customresourcedefinitions", "customresourcedefinitions/status"]
  verbs: ["get", "list", "update", "patch", "watch"]
- apiGroups: ["admissionregistration.k8s.io"]
  # The webhook performs a reconciliation on these two resources and continuously
  # updates configuration.
  resources: ["mutatingwebhookconfigurations", "validatingwebhookconfigurations"]
  # knative starts informers on these things, which is why we need get, list and watch.
  verbs: ["list", "watch"]
- apiGroups: ["admissionregistration.k8s.io"]
  resources: ["mutatingwebhookconfigurations"]
  # This mutating webhook is responsible for applying defaults to tekton objects
  # as they are received.
  resourceNames: ["webhook.pipeline.tekton.dev"]
  # When there are changes to the configs or secrets, knative updates the mutatingwebhook config
  # with the updated certificates or the refreshed set of rules.
  verbs: ["get", "update"]
- apiGroups: ["admissionregistration.k8s.io"]
  resources: ["validatingwebhookconfigurations"]
  # validation.webhook.pipeline.tekton.dev performs schema validation when you, for example, create TaskRuns.
  # config.webhook.pipeline.tekton.dev validates the logging configuration against knative's logging structure
  resourceNames: ["validation.webhook.pipeline.tekton.dev", "config.webhook.pipeline.tekton.dev"]
  # When there are changes to the configs or secrets, knative updates the validatingwebhook config
  # with the updated certificates or the refreshed set of rules.
  verbs: ["get", "update"]

---
# Copyright 2020 The Tekton Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: tekton-pipelines-controller
  namespace: tekton-pipelines
rules:
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["list", "watch"]
- # The controller needs access to these configmaps for logging information and runtime configuration.
  apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get"]
  resourceNames: ["config-logging", "config-observability", "config-artifact-bucket",
    "config-artifact-pvc", "feature-flags", "config-leader-election"]
---
kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: tekton-pipelines-webhook
  namespace: tekton-pipelines
rules:
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["list", "watch"]
- # The webhook needs access to these configmaps for logging information.
  apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get"]
  resourceNames: ["config-logging", "config-observability"]
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["list", "watch"]
- # The webhook daemon makes a reconciliation loop on webhook-certs. Whenever
  # the secret changes it updates the webhook configurations with the certificates
  # stored in the secret.
  apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get", "update"]
  resourceNames: ["webhook-certs"]

---
# Copyright 2019 The Tekton Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
apiVersion: v1
kind: ServiceAccount
metadata:
  name: tekton-pipelines-controller
  namespace: tekton-pipelines
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: tekton-pipelines-webhook
  namespace: tekton-pipelines

---
# Copyright 2019 The Tekton Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

apiVersion: rbac.authorization.k8s.io/v1beta1
kind: ClusterRoleBinding
metadata:
  name: tekton-pipelines-controller-cluster-access
subjects:
- kind: ServiceAccount
  name: tekton-pipelines-controller
  namespace: tekton-pipelines
roleRef:
  kind: ClusterRole
  name: tekton-pipelines-controller-cluster-access
  apiGroup: rbac.authorization.k8s.io
---
# If this ClusterRoleBinding is replaced with a RoleBinding
# then the ClusterRole would be namespaced. The access described by
# the tekton-pipelines-controller-tenant-access ClusterRole would
# be scoped to individual tenant namespaces.
apiVersion: rbac.authorization.k8s.io/v1beta1
kind: ClusterRoleBinding
metadata:
  name: tekton-pipelines-controller-tenant-access
subjects:
- kind: ServiceAccount
  name: tekton-pipelines-controller
  namespace: tekton-pipelines
roleRef:
  kind: ClusterRole
  name: tekton-pipelines-controller-tenant-access
  apiGroup: rbac.authorization.k8s.io
---
apiVersion: rbac.authorization.k8s.io/v1beta1
kind: ClusterRoleBinding
metadata:
  name: tekton-pipelines-webhook-cluster-access
subjects:
- kind: ServiceAccount
  name: tekton-pipelines-webhook
  namespace: tekton-pipelines
roleRef:
  kind: ClusterRole
  name: tekton-pipelines-webhook-cluster-access
  apiGroup: rbac.authorization.k8s.io

---
# Copyright 2020 The Tekton Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

apiVersion: rbac.authorization.k8s.io/v1beta1
kind: RoleBinding
metadata:
  name: tekton-pipelines-controller
  namespace: tekton-pipelines
subjects:
- kind: ServiceAccount
  name: tekton-pipelines-controller
  namespace: tekton-pipelines
roleRef:
  kind: Role
  name: tekton-pipelines-controller
  apiGroup: rbac.authorization.k8s.io
---
apiVersion: rbac.authorization.k8s.io/v1beta1
kind: RoleBinding
metadata:
  name: tekton-pipelines-webhook
  namespace: tekton-pipelines
subjects:
- kind: ServiceAccount
  name: tekton-pipelines-webhook
  namespace: tekton-pipelines
roleRef:
  kind: Role
  name: tekton-pipelines-webhook
  apiGroup: rbac.authorization.k8s.io

---
# Copyright 2019 The Tekton Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  name: clustertasks.tekton.dev
  labels:
    pipeline.tekton.dev/release: "devel"
    version: "devel"
spec:
  group: tekton.dev
  preserveUnknownFields: false
  validation:
    openAPIV3Schema:
      type: object
      # One can use x-kubernetes-preserve-unknown-fields: true
      # at the root of the schema (and inside any properties, additionalProperties)
      # to get the traditional CRD behaviour that nothing is pruned, despite
      # setting spec.preserveUnknownProperties: false.
      #
      # See https://kubernetes.io/blog/2019/06/20/crd-structural-schema/
      # See issue: https://github.com/knative/serving/issues/912
      x-kubernetes-preserve-unknown-fields: true
  versions:
  - name: v1alpha1
    served: true
    storage: true
  - name: v1beta1
    served: true
    storage: false
  names:
    kind: ClusterTask
    plural: clustertasks
    categories:
    - tekton
    - tekton-pipelines
  scope: Cluster
  # Opt into the status subresource so metadata.generation
  # starts to increment
  subresources:
    status: {}
  conversion:
    strategy: Webhook
    webhookClientConfig:
      service:
        name: tekton-pipelines-webhook
        namespace: tekton-pipelines

---
# Copyright 2019 The Tekton Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  name: conditions.tekton.dev
  labels:
    pipeline.tekton.dev/release: "devel"
    version: "devel"
spec:
  group: tekton.dev
  names:
    kind: Condition
    plural: conditions
    categories:
    - tekton
    - tekton-pipelines
  scope: Namespaced
  # Opt into the status subresource so metadata.generation
  # starts to increment
  subresources:
    status: {}
  version: v1alpha1

---
# Copyright 2018 The Knative Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  name: images.caching.internal.knative.dev
  labels:
    knative.dev/crd-install: "true"
spec:
  group: caching.internal.knative.dev
  version: v1alpha1
  names:
    kind: Image
    plural: images
    singular: image
    categories:
    - knative-internal
    - caching
    shortNames:
    - img
  scope: Namespaced
  subresources:
    status: {}

---
# Copyright 2019 The Tekton Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  name: pipelines.tekton.dev
  labels:
    pipeline.tekton.dev/release: "devel"
    version: "devel"
spec:
  group: tekton.dev
  preserveUnknownFields: false
  validation:
    openAPIV3Schema:
      type: object
      # One can use x-kubernetes-preserve-unknown-fields: true
      # at the root of the schema (and inside any properties, additionalProperties)
      # to get the traditional CRD behaviour that nothing is pruned, despite
      # setting spec.preserveUnknownProperties: false.
      #
      # See https://kubernetes.io/blog/2019/06/20/crd-structural-schema/
      # See issue: https://github.com/knative/serving/issues/912
      x-kubernetes-preserve-unknown-fields: true
  versions:
  - name: v1alpha1
    served: true
    storage: true
  - name: v1beta1
    served: true
    storage: false
  names:
    kind: Pipeline
    plural: pipelines
    categories:
    - tekton
    - tekton-pipelines
  scope: Namespaced
  # Opt into the status subresource so metadata.generation
  # starts to increment
  subresources:
    status: {}
  conversion:
    strategy: Webhook
    webhookClientConfig:
      service:
        name: tekton-pipelines-webhook
        namespace: tekton-pipelines

---
# Copyright 2019 The Tekton Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  name: pipelineruns.tekton.dev
  labels:
    pipeline.tekton.dev/release: "devel"
    version: "devel"
spec:
  group: tekton.dev
  preserveUnknownFields: false
  validation:
    openAPIV3Schema:
      type: object
      # One can use x-kubernetes-preserve-unknown-fields: true
      # at the root of the schema (and inside any properties, additionalProperties)
      # to get the traditional CRD behaviour that nothing is pruned, despite
      # setting spec.preserveUnknownProperties: false.
      #
      # See https://kubernetes.io/blog/2019/06/20/crd-structural-schema/
      # See issue: https://github.com/knative/serving/issues/912
      x-kubernetes-preserve-unknown-fields: true
  versions:
  - name: v1alpha1
    served: true
    storage: true
  - name: v1beta1
    served: true
    storage: false
  names:
    kind: PipelineRun
    plural: pipelineruns
    categories:
    - tekton
    - tekton-pipelines
    shortNames:
    - pr
    - prs
  scope: Namespaced
  additionalPrinterColumns:
  - name: Succeeded
    type: string
    JSONPath: ".status.conditions[?(@.type==\"Succeeded\")].status"
  - name: Reason
    type: string
    JSONPath: ".status.conditions[?(@.type==\"Succeeded\")].reason"
  - name: StartTime
    type: date
    JSONPath: .status.startTime
  - name: CompletionTime
    type: date
    JSONPath: .status.completionTime
  # Opt into the status subresource so metadata.generation
  # starts to increment
  subresources:
    status: {}
  conversion:
    strategy: Webhook
    webhookClientConfig:
      service:
        name: tekton-pipelines-webhook
        namespace: tekton-pipelines

---
# Copyright 2019 The Tekton Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  name: pipelineresources.tekton.dev
  labels:
    pipeline.tekton.dev/release: "devel"
    version: "devel"
spec:
  group: tekton.dev
  names:
    kind: PipelineResource
    plural: pipelineresources
    categories:
    - tekton
    - tekton-pipelines
  scope: Namespaced
  # Opt into the status subresource so metadata.generation
  # starts to increment
  subresources:
    status: {}
  version: v1alpha1

---
# Copyright 2019 The Tekton Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  name: tasks.tekton.dev
  labels:
    pipeline.tekton.dev/release: "devel"
    version: "devel"
spec:
  group: tekton.dev
  preserveUnknownFields: false
  validation:
    openAPIV3Schema:
      type: object
      # One can use x-kubernetes-preserve-unknown-fields: true
      # at the root of the schema (and inside any properties, additionalProperties)
      # to get the traditional CRD behaviour that nothing is pruned, despite
      # setting spec.preserveUnknownProperties: false.
      #
      # See https://kubernetes.io/blog/2019/06/20/crd-structural-schema/
      # See issue: https://github.com/knative/serving/issues/912
      x-kubernetes-preserve-unknown-fields: true
  versions:
  - name: v1alpha1
    served: true
    storage: true
  - name: v1beta1
    served: true
    storage: false
  names:
    kind: Task
    plural: tasks
    categories:
    - tekton
    - tekton-pipelines
  scope: Namespaced
  # Opt into the status subresource so metadata.generation
  # starts to increment
  subresources:
    status: {}
  conversion:
    strategy: Webhook
    webhookClientConfig:
      service:
        name: tekton-pipelines-webhook
        namespace: tekton-pipelines

---
# Copyright 2019 The Tekton Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  name: taskruns.tekton.dev
  labels:
    pipeline.tekton.dev/release: "devel"
    version: "devel"
spec:
  group: tekton.dev
  preserveUnknownFields: false
  validation:
    openAPIV3Schema:
      type: object
      # One can use x-kubernetes-preserve-unknown-fields: true
      # at the root of the schema (and inside any properties, additionalProperties)
      # to get the traditional CRD behaviour that nothing is pruned, despite
      # setting spec.preserveUnknownProperties: false.
      #
      # See https://kubernetes.io/blog/2019/06/20/crd-structural-schema/
      # See issue: https://github.com/knative/serving/issues/912
      x-kubernetes-preserve-unknown-fields: true
  versions:
  - name: v1alpha1
    served: true
    storage: true
  - name: v1beta1
    served: true
    storage: false
  names:
    kind: TaskRun
    plural: taskruns
    categories:
    - tekton
    - tekton-pipelines
    shortNames:
    - tr
    - trs
  scope: Namespaced
  additionalPrinterColumns:
  - name: Succeeded
    type: string
    JSONPath: ".status.conditions[?(@.type==\"Succeeded\")].status"
  - name: Reason
    type: string
    JSONPath: ".status.conditions[?(@.type==\"Succeeded\")].reason"
  - name: StartTime
    type: date
    JSONPath: .status.startTime
  - name: CompletionTime
    type: date
    JSONPath: .status.completionTime
  # Opt into the status subresource so metadata.generation
  # starts to increment
  subresources:
    status: {}
  conversion:
    strategy: Webhook
    webhookClientConfig:
      service:
        name: tekton-pipelines-webhook
        namespace: tekton-pipelines

---
# Copyright 2020 The Tekton Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

apiVersion: v1
kind: Secret
metadata:
  name: webhook-certs
  namespace: tekton-pipelines
  labels:
    pipeline.tekton.dev/release: devel
# The data is populated at install time.
---
apiVersion: admissionregistration.k8s.io/v1beta1
kind: ValidatingWebhookConfiguration
metadata:
  name: validation.webhook.pipeline.tekton.dev
  labels:
    pipeline.tekton.dev/release: devel
webhooks:
- admissionReviewVersions:
  - v1beta1
  clientConfig:
    service:
      name: tekton-pipelines-webhook
      namespace: tekton-pipelines
  failurePolicy: Fail
  sideEffects: None
  name: validation.webhook.pipeline.tekton.dev
---
apiVersion: admissionregistration.k8s.io/v1beta1
kind: MutatingWebhookConfiguration
metadata:
  name: webhook.pipeline.tekton.dev
  labels:
    pipeline.tekton.dev/release: devel
webhooks:
- admissionReviewVersions:
  - v1beta1
  clientConfig:
    service:
      name: tekton-pipelines-webhook
      namespace: tekton-pipelines
  failurePolicy: Fail
  sideEffects: None
  name: webhook.pipeline.tekton.dev
---
apiVersion: admissionregistration.k8s.io/v1beta1
kind: ValidatingWebhookConfiguration
metadata:
  name: config.webhook.pipeline.tekton.dev
  labels:
    pipeline.tekton.dev/release: devel
webhooks:
- admissionReviewVersions:
  - v1beta1
  clientConfig:
    service:
      name: tekton-pipelines-webhook
      namespace: tekton-pipelines
  failurePolicy: Fail
  sideEffects: None
  name: config.webhook.pipeline.tekton.dev
  namespaceSelector:
    matchExpressions:
    - key: pipeline.tekton.dev/release
      operator: Exists

---
# Copyright 2019 The Tekton Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: tekton-aggregate-edit
  labels:
    rbac.authorization.k8s.io/aggregate-to-edit: "true"
    rbac.authorization.k8s.io/aggregate-to-admin: "true"
rules:
- apiGroups:
  - tekton.dev
  resources:
  - tasks
  - taskruns
  - pipelines
  - pipelineruns
  - pipelineresources
  - conditions
  verbs:
  - create
  - delete
  - deletecollection
  - get
  - list
  - patch
  - update
  - watch

---
# Copyright 2019 The Tekton Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: tekton-aggregate-view
  labels:
    rbac.authorization.k8s.io/aggregate-to-view: "true"
rules:
- apiGroups:
  - tekton.dev
  resources:
  - tasks
  - taskruns
  - pipelines
  - pipelineruns
  - pipelineresources
  - conditions
  verbs:
  - get
  - list
  - watch

---
# Copyright 2019 The Tekton Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

apiVersion: v1
kind: ConfigMap
metadata:
  name: config-artifact-bucket
  namespace: tekton-pipelines
#  data:
#    # location of the gcs bucket to be used for artifact storage
#    location: "gs://bucket-name"
#    # name of the secret that will contain the credentials for the service account
#    # with access to the bucket
#    bucket.service.account.secret.name:
#    # The key in the secret with the required service account json
#    bucket.service.account.secret.key:

---
# Copyright 2019 The Tekton Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

apiVersion: v1
kind: ConfigMap
metadata:
  name: config-artifact-pvc
  namespace: tekton-pipelines
# data:
#   # size of the PVC volume
#   size: 5Gi
#
#   # storage class of the PVC volume
#   storageClassName: storage-class-name

---
# Copyright 2019 The Tekton Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

apiVersion: v1
kind: ConfigMap
metadata:
  name: config-defaults
  namespace: tekton-pipelines
data:
  _example: |-
    ################################
    #                              #
    #    EXAMPLE CONFIGURATION     #
    #                              #
    ################################

    # This block is not actually functional configuration,
    # but serves to illustrate the available configuration
    # options and document them in a way that is accessible
    # to users that `kubectl edit` this config map.
    #
    # These sample configuration options may be copied out of
    # this example block and unindented to be in the data block
    # to actually change the configuration.

    # default-timeout-minutes contains the default number of
    # minutes to use for TaskRun and PipelineRun, if none is specified.
    default-timeout-minutes: "60"  # 60 minutes

    # default-service-account contains the default service account name
    # to use for TaskRun and PipelineRun, if none is specified.
    default-service-account: "default"

    # default-managed-by-label-value contains the default value given to the
    # "app.kubernetes.io/managed-by" label applied to all Pods created for
    # TaskRuns. If a user's requested TaskRun specifies another value for this
    # label, the user's request supercedes.
    default-managed-by-label-value: "tekton-pipelines"

    # default-pod-template contains the default pod template to use
    # TaskRun and PipelineRun, if none is specified. If a pod template
    # is specified, the default pod template is ignored.
    # default-pod-template:

---
# Copyright 2019 The Tekton Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

apiVersion: v1
kind: ConfigMap
metadata:
  name: feature-flags
  namespace: tekton-pipelines
data:
  # Setting this flag to "true" will prevent Tekton overriding your
  # Task container's $HOME environment variable.
  #
  # The default behaviour currently is for Tekton to override the
  # $HOME environment variable but this will change in an upcoming
  # release.
  #
  # See https://github.com/tektoncd/pipeline/issues/2013 for more
  # info.
  disable-home-env-overwrite: "false"
  # Setting this flag to "true" will prevent Tekton overriding your
  # Task container's working directory.
  #
  # The default behaviour currently is for Tekton to override the
  # working directory if not set by the user but this will change
  # in an upcoming release.
  #
  # See https://github.com/tektoncd/pipeline/issues/1836 for more
  # info.
  disable-working-directory-overwrite: "false"

---
# Copyright 2020 Tekton Authors LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

apiVersion: v1
kind: ConfigMap
metadata:
  name: config-leader-election
  namespace: tekton-pipelines
data:
  # An inactive but valid configuration follows; see example.
  resourceLock: "leases"
  leaseDuration: "15s"
  renewDeadline: "10s"
  retryPeriod: "2s"

---
# Copyright 2019 Tekton Authors LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

apiVersion: v1
kind: ConfigMap
metadata:
  name: config-logging
  namespace: tekton-pipelines
data:
  # Common configuration for all knative codebase
  zap-logger-config: |
    {
      "level": "info",
      "development": false,
      "sampling": {
        "initial": 100,
        "thereafter": 100
      },
      "outputPaths": ["stdout"],
      "errorOutputPaths": ["stderr"],
      "encoding": "json",
      "encoderConfig": {
        "timeKey": "",
        "levelKey": "level",
        "nameKey": "logger",
        "callerKey": "caller",
        "messageKey": "msg",
        "stacktraceKey": "stacktrace",
        "lineEnding": "",
        "levelEncoder": "",
        "timeEncoder": "",
        "durationEncoder": "",
        "callerEncoder": ""
      }
    }
  # Log level overrides
  loglevel.controller: "info"
  loglevel.webhook: "info"

---
# Copyright 2019 The Tekton Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

apiVersion: v1
kind: ConfigMap
metadata:
  name: config-observability
  namespace: tekton-pipelines
data:
  _example: |
    ################################
    #                              #
    #    EXAMPLE CONFIGURATION     #
    #                              #
    ################################

    # This block is not actually functional configuration,
    # but serves to illustrate the available configuration
    # options and document them in a way that is accessible
    # to users that `kubectl edit` this config map.
    #
    # These sample configuration options may be copied out of
    # this example block and unindented to be in the data block
    # to actually change the configuration.

    # metrics.backend-destination field specifies the system metrics destination.
    # It supports either prometheus (the default) or stackdriver.
    # Note: Using Stackdriver will incur additional charges.
    metrics.backend-destination: prometheus

    # metrics.stackdriver-project-id field specifies the Stackdriver project ID. This
    # field is optional. When running on GCE, application default credentials will be
    # used and metrics will be sent to the cluster's project if this field is
    # not provided.
    metrics.stackdriver-project-id: "<your stackdriver project id>"

    # metrics.allow-stackdriver-custom-metrics indicates whether it is allowed
    # to send metrics to Stackdriver using "global" resource type and custom
    # metric type. Setting this flag to "true" could cause extra Stackdriver
    # charge.  If metrics.backend-destination is not Stackdriver, this is
    # ignored.
    metrics.allow-stackdriver-custom-metrics: "false"

---
# Copyright 2019 The Tekton Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

apiVersion: apps/v1
kind: Deployment
metadata:
  name: tekton-pipelines-controller
  namespace: tekton-pipelines
  labels:
    app.kubernetes.io/name: tekton-pipelines
    app.kubernetes.io/component: controller
    pipeline.tekton.dev/release: "v0.12.0"
    version: "v0.12.0"
spec:
  replicas: 1
  selector:
    matchLabels:
      app: tekton-pipelines-controller
  template:
    metadata:
      annotations:
        cluster-autoscaler.kubernetes.io/safe-to-evict: "false"
      labels:
        app: tekton-pipelines-controller
        app.kubernetes.io/name: tekton-pipelines
        app.kubernetes.io/component: controller
        # tekton.dev/release value replaced with inputs.params.versionTag in pipeline/tekton/publish.yaml
        pipeline.tekton.dev/release: "v0.12.0"
        version: "v0.12.0"
    spec:
      serviceAccountName: tekton-pipelines-controller
      containers:
      - name: tekton-pipelines-controller
        image: xianchao/tekton-controller:v0.12.0
        args: [
          # These images are built on-demand by `ko resolve` and are replaced
          # by image references by digest.
          "-kubeconfig-writer-image", "xianchao/tekton-kubeconfigwriter:v0.12.0",
          "-creds-image", "xianchao/tekton-creds-init:v0.12.0",
          "-git-image", "xianchao/tekton-git-init:v0.12.0",
          "-entrypoint-image", "xianchao/tekton-entrypoint:v0.12.0",
          "-imagedigest-exporter-image", "xianchao/tekton-imagedigestexporter:v0.12.0",
          "-pr-image", "xianchao/tekton-pullrequest-init:v0.12.0",
          "-build-gcs-fetcher-image", "xianchao/tekton-gcs-fetcher:v0.12.0",
          # These images are pulled from Dockerhub, by digest, as of April 15, 2020.
          "-nop-image", "xianchao/tianon:v1.0",
          "-shell-image", "xianchao/busybox:v1.0",
          "-gsutil-image", "google/cloud-sdk"]
        volumeMounts:
        - name: config-logging
          mountPath: /etc/config-logging
        env:
        - name: SYSTEM_NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
        - # If you are changing these names, you will also need to update
          # the controller's Role in 200-role.yaml to include the new
          # values in the "configmaps" "get" rule.
          name: CONFIG_LOGGING_NAME
          value: config-logging
        - name: CONFIG_OBSERVABILITY_NAME
          value: config-observability
        - name: CONFIG_ARTIFACT_BUCKET_NAME
          value: config-artifact-bucket
        - name: CONFIG_ARTIFACT_PVC_NAME
          value: config-artifact-pvc
        - name: CONFIG_FEATURE_FLAGS_NAME
          value: feature-flags
        - name: CONFIG_LEADERELECTION_NAME
          value: config-leader-election
        - name: METRICS_DOMAIN
          value: tekton.dev/pipeline
      volumes:
      - name: config-logging
        configMap:
          name: config-logging
---
apiVersion: v1
kind: Service
metadata:
  labels:
    app: tekton-pipelines-controller
    pipeline.tekton.dev/release: "v0.12.0"
    version: "v0.12.0"
  name: tekton-pipelines-controller
  namespace: tekton-pipelines
spec:
  ports:
  - name: http-metrics
    port: 9090
    protocol: TCP
    targetPort: 9090
  selector:
    app: tekton-pipelines-controller

---
# Copyright 2019 The Tekton Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

apiVersion: apps/v1
kind: Deployment
metadata:
  # Note: the Deployment name must be the same as the Service name specified in
  # config/400-webhook-service.yaml. If you change this name, you must also
  # change the value of WEBHOOK_SERVICE_NAME below.
  name: tekton-pipelines-webhook
  namespace: tekton-pipelines
  labels:
    app.kubernetes.io/name: tekton-pipelines
    app.kubernetes.io/component: webhook-controller
    pipeline.tekton.dev/release: "v0.12.0"
    version: "v0.12.0"
spec:
  replicas: 1
  selector:
    matchLabels:
      app: tekton-pipelines-webhook
      role: webhook
  template:
    metadata:
      annotations:
        cluster-autoscaler.kubernetes.io/safe-to-evict: "false"
      labels:
        app: tekton-pipelines-webhook
        role: webhook
        app.kubernetes.io/name: tekton-pipelines
        app.kubernetes.io/component: webhook-controller
        pipeline.tekton.dev/release: "v0.12.0"
        version: "v0.12.0"
    spec:
      serviceAccountName: tekton-pipelines-webhook
      containers:
      - name: webhook
        # This is the Go import path for the binary that is containerized
        # and substituted here.
        image:  xianchao/tekton-webhook:v0.12.0
        env:
        - name: SYSTEM_NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
        - # If you are changing these names, you will also need to update
          # the webhook's Role in 200-role.yaml to include the new
          # values in the "configmaps" "get" rule.
          name: CONFIG_LOGGING_NAME
          value: config-logging
        - name: CONFIG_OBSERVABILITY_NAME
          value: config-observability
        - name: CONFIG_LEADERELECTION_NAME
          value: config-leader-election
        - name: WEBHOOK_SERVICE_NAME
          value: tekton-pipelines-webhook
        - name: WEBHOOK_SECRET_NAME
          value: webhook-certs
        - name: METRICS_DOMAIN
          value: tekton.dev/pipeline
        securityContext:
          allowPrivilegeEscalation: false
        ports:
        - name: metrics
          containerPort: 9090
        - name: profiling
          containerPort: 8008
        - name: https-webhook
          containerPort: 8443
---
apiVersion: v1
kind: Service
metadata:
  labels:
    app: tekton-pipelines-webhook
    role: webhook
    pipeline.tekton.dev/release: v0.12.0
    version: "v0.12.0"
  name: tekton-pipelines-webhook
  namespace: tekton-pipelines
spec:
  ports:
  - # Define metrics and profiling for them to be accessible within service meshes.
    name: http-metrics
    port: 9090
    targetPort: 9090
  - name: http-profiling
    port: 8008
    targetPort: 8008
  - name: https-webhook
    port: 443
    targetPort: 8443
  selector:
    app: tekton-pipelines-webhook
    role: webhook

---
~~~

## 验证资源创建

~~~sh
kubectl get pods -n tekton-pipelines
kubectl get crd
kubectl api-versions
~~~



# 测试Tekton构建CICD流水线

- 我们测试一个简单的golang程序。应用程序代码，测试及dockerfile文件可在如下地址获取：https://github.com/luckylucky421/tekton-demo

## 创建task任务

~~~yaml
tee task-test.yaml <<'EOF' 
apiVersion: tekton.dev/v1beta1
kind: Task
metadata:
  name: test
spec:
  resources:
  #resources定义了我们的任务中定义的步骤中需要输入的内容，这里我们的步骤需要 Clone 一个 Git 仓库作为 go test 命令的输入。
  #Tekton 内置了一种 git 资源类型，它会自动将代码仓库 Clone 到 /workspace/$input_name 目录中，由于我们这里输入被命名成 repo，所以代码会被 Clone 到 /workspace/repo 目录下面。然后下面的 steps 就是来定义执行运行测试命令的步骤，这里我们直接在代码的根目录中运行 go test 命令即可，需要注意的是命令和参数需要分别定义。
    inputs:
    - name: repo
      type: git
  steps:
  - name: run-test
    image: golang:1.14-alpine
    imagePullPolicy: IfNotPresent
    workingDir: /workspace/repo
    command: ["go"]
    args: ["test"]
EOF
kubectl apply -f task-test.yaml
kubectl get Task
~~~

## 创建pipelineresource

- 通过上面步骤定义了一个 Task 任务，但是该任务并不会立即执行。必须创建一个 TaskRun 引用它并提供所有必需输入的数据才行。这里我们就需要将 git 代码库作为输入，必须先创建一个 PipelineResource 对象来定义输入信息：

~~~yaml
tee pipelineresource.yaml <<'EOF'
apiVersion: tekton.dev/v1alpha1
kind: PipelineResource
metadata:
  name: xianchao-tekton-example
spec:
  type: git
  params:
    - name: url
      value: https://github.com/luckylucky421/tekton-demo
    - name: revision
      value: master
EOF
kubectl apply -f pipelineresource.yaml
kubectl get PipelineResource
~~~

## 创建taskrun

~~~yaml
tee taskrun.yaml <<'EOF' 
apiVersion: tekton.dev/v1beta1
kind: TaskRun
metadata:
  name: testrun
spec:
  taskRef:
    name: test
  resources:
    inputs:
    - name: repo
      resourceRef:
        name: xianchao-tekton-example
#通过taskRef引用上面定义的Task和git仓库作为输入，resourceRef也是引用上面定义的PipelineResource资源对象。
EOF
kubectl apply -f taskrun.yaml
kubectl get taskrun
kubectl get pods #可以看到有一个taskrun的pod在运行，任务执行完成后，pod就变成completed状态了
#可以通过kubectl describe命令来查看任务运行的过程，通过kubectl logs查看任务执行结果
kubectl describe po testrun-pod-x9rkn
kubectl logs testrun-pod-x9rkn --all-containers
~~~

