# Azure Devops basics

![image-20241029103553828](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202410291035904.png)

## Trigger

- An agent is computing infrastructure with installed agent software that runs one job at a time.
- You can configure a pipeline to run upon a **push to a repository**, **at scheduled times**, or **upon the completion of another build**.

## Pipeline

> https://learn.microsoft.com/en-us/azure/devops/pipelines/customize-pipeline?view=azure-devops#understand-the-azure-pipelinesyml-file

- A pipeline defines the continuous integration and deployment process for your app. It's made up of one or more stages. It can be thought of as a workflow that defines how your test, build, and deployment steps are run.
- 在repo的根目录下一般会有azure-pipelines.yml，一般会定义如下内容：
  - 什么情况下触发trigger
  - pipeline在什么agent pool下运行
  - 每一个steps做什么（运行scripts或者tasks）
- pipeline分两种：
  - YAML pipeline -- 常用
  - classic pipeline


## Stage

- a logical boundary in the pipeline.
- mark separation of concerns (for example, Build, QA, and production)（有先后顺序的依赖）
- 一个stage包含多个job

## job

- 一个job包含多个steps，一个job在多个agent上运行。
- 常用于需要同时在多个环境中并行运行时：For example, you might want to build two configurations - x86 and x64. In this case, you have one stage and two jobs. One job would be for x86 and the other job would be for x64.

## Steps

- 是一个pipeline中最小的执行单元，一个step中可以执行一个task或者一个script
- 每个steps是独立的运行环境，steps之间不会共享环境变量。
- steps通过logging command来与agent通信：https://learn.microsoft.com/en-us/azure/devops/pipelines/scripts/logging-commands?view=azure-devops&tabs=bash，可以通过logging commands来产生新的环境变量，传递给下一个step

### task

- 是azure devops中预先定义好的schema，填入相关参数，组成一个task

> https://learn.microsoft.com/en-us/azure/devops/pipelines/tasks/reference/?view=azure-pipelines&viewFallbackFrom=azure-devops

### script

- 是用户自定义的command

## Run

- run是pipeline的一次运行。每次Run，将job发给agent去运行

## Approval

- define a set of validations required before a deployment runs. Manual approval is a common check performed to control deployments to production environments. 
- When checks are configured on an environment, a pipeline run pauses until all the checks are completed successfully.

## Artifact

- An artifact is a collection of files or packages published by a run.

## Agent

- 一个agent一次就运行一个job，一次运行多个job要用parallel job

# Pipeline runs

## process

For each run, Azure Pipelines:

- Processes the pipeline.
- Requests one or more agents to run jobs.
- Hands off jobs to agents and collects the results.

For each job, an agent:

- Prepares for the job.
- Runs each step in the job.
- Reports results.

## timeouts

- 每个job有timeout超时时间，未能完成就会被server cancel掉。这时就会进入到cancel timeout时间，在这个时间内，agent没能cancel完成，server直接标记job为失败。
- agent每分钟向server报告一次心跳，五次心跳没接收到，server就认为agent下线，其上的job标记为失败。

# Jobs

## 格式

https://learn.microsoft.com/en-us/azure/devops/pipelines/process/phases?view=azure-devops&tabs=yaml#define-a-single-job

- pipeline中的job不支持priority，而是通过condition和dependency来实现

# Stages

https://learn.microsoft.com/en-us/azure/devops/pipelines/process/stages?view=azure-devops&tabs=yaml

# Tasks/Scripts

https://learn.microsoft.com/en-us/azure/devops/pipelines/tasks/reference/?view=azure-pipelines&viewFallbackFrom=azure-devops

# Templates

https://learn.microsoft.com/en-us/azure/devops/pipelines/process/templates?view=azure-devops&pivots=templates-includes

# Variables

https://learn.microsoft.com/en-us/azure/devops/pipelines/process/variables?view=azure-devops&tabs=yaml%2Cbatch

# Templates

https://learn.microsoft.com/en-us/azure/devops/pipelines/process/templates?view=azure-devops&pivots=templates-includes

# Resources

https://learn.microsoft.com/en-us/azure/devops/pipelines/process/about-resources?view=azure-devops&tabs=yaml

# Self-hosted agents

> https://learn.microsoft.com/en-us/azure/devops/pipelines/agents/agents?view=azure-devops&tabs=yaml%2Cbrowser#self-hosted-agents

- azure devops在azure china不支持MS managed agents，只能是用self-hosted agents，可能会存在一些cache warm-up和拉取commit到local repo的准备时间。
- self-hosted agents提供capability，意思是上面装了什么软件。pipeline的demand会定义需要哪些软件。
  - 如果pipeline定义的demands，没有agent具备capability能满足，那么job就会失败。
  - 如果是没有空闲的agent能满足demands，job就会等待。

- azure devops - pipelines - edit - triggers - YAML - Default agent pool for YAML：可以选择默认用Azure-hosted还是private（self hosted）。yaml文件里面没定义agent pool的话，就用这个默认的。

## Agent与pipeline通信

https://learn.microsoft.com/en-us/azure/devops/pipelines/agents/agents?view=azure-devops&tabs=yaml%2Cbrowser#communication

## Agent版本

https://learn.microsoft.com/en-us/azure/devops/pipelines/agents/v3-agent?view=azure-devops

## Agent手动注册

https://learn.microsoft.com/en-us/azure/devops/pipelines/agents/linux-agent?view=azure-devops

## Agent认证

https://learn.microsoft.com/en-us/azure/devops/pipelines/agents/personal-access-token-agent-registration?view=azure-devops