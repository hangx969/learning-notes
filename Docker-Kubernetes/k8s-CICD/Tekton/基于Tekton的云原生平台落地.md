# Tekton介绍

Tekton是一个云原生的CICD解决方案，是CNCF很流行的开源项目之一。Tekton以K8s CRD资源的形式部署在集群上。

Tekton的核心资源包括StepAction、Task、TaskRun、Pipeline、PipelineRun等。可以使用Kubectl直接管理Tekton资源，配置和执行流水线。

核心功能：

1. 云原生：完全基于K8s云原生，不依赖其他组件，所有任务均以容器运行，按需创建和销毁
2. 标准化：所有资源均以CRD定义，符合IaC标准
3. 可移植性：基于标准CRD资源构建，可以一键式跨集群迁移
4. 可扩展性：随集群扩展，无需修改即可增加工作负载
5. 事件驱动：可以接收外部webhook事件触发流水线
6. 社区生态：具备社区和Task Hub，可以用现成的Task

## 核心资源

- StepAction: 最小的工作单元。定义可以复用的工作单元的资源，一般用于定义具体的执行步骤，比如构建、扫描等。可以被task调用
- Task: 用于定义一系列有序的步骤，每个步骤用于调用特定的工具处理特定的任务，可以指定具体的命令，也可以绑定StepActions
- Tekton Pipeline: 集成多个Task，按顺序执行。
- Tekton Triggers: Tekton事件触发组件，可以用于接收外部系统的事件，之后进行流水线的执行
- Tekton CLI: Tekton提供的客户端工具，可以使用tkn与Tekton交互。（推荐kubectl来管理，不用这个）
- Tekton Dashboard: Tekton提供的基于Web的图形界面
- TaskRun: 用于实例化特定任务(Task)，相当于真正执行Task
- PipelineRun: 用于实例化特定流水线(Pipeline)，相当于执行Pipeline中定义的任务

## 工作模式

- 先定义好Pipeline，集成了多个Task：Task A --> Task B | Task C --> Task D

- 再创建TaskRun实例化Pipeline

这样定义的原因是：Pipeline是一个通用模板，里面不定义真实的命令；PipelineRun中传入实际的参数。

## 最佳实践

1. 推荐把Task作为最小单元就行了，不要再定义StepAction作为最小单元了，因为一层一层参数传递实在是太麻烦了。
2. 推荐一个Task就定义一个Step就行了。
3. workspace都写一个名字就行了免得搞混 

# 部署Tekton

- Tekton官网：https://tekton.dev/

要部署三个组件：

1. Tekton Pipeline：https://tekton.dev/docs/installation/pipelines/
2. Tekton Triggers：https://tekton.dev/docs/installation/triggers/#installation
3. Tekton Dashboard：https://tekton.dev/docs/dashboard/install/#installing-tekton-dashboard-on-kubernetes