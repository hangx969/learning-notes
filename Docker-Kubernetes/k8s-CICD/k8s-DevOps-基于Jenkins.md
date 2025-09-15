# DevOps

## 定义

Devops是Development和Operations的组合，一开始是为了解决开发人员和运维人员之间合作的避雷，强调跨团队协作与工具链整合。后面发展之后，不仅仅是开发运维，包含完整流程：开发、测试、运维、项目管理。

Devops核心目标：

1. 加速交付：快速迭代，频繁发布新功能
2. 提高质量：自动化任务，减少人工操作错误
3. 增强协作：开发、运维、测试等角色紧密配合

一句话总结：Devops是跨部门沟通的桥梁，利用相关工具的融合提升整个团队的工作效率。

## 工具链

| 阶段                        | 工具示例                                           |
| --------------------------- | -------------------------------------------------- |
| 代码管理                    | Gitlab(企业最常用)、Github、Gitee、Git             |
| 代码扫描                    | Sonarqube                                          |
| 持续集成（自动编译）        | Jenkins、Tekton、Gitlab CI                         |
| 持续部署                    | Jenkins、Tekton、ArgoCD                            |
| 容器化                      | Docker、Containerd、Kaniko（轻量级做镜像）、Podman |
| 制品管理（镜像或Jar包存储） | Harbor、Nexus（存Jar包比较常用）                   |
| 服务编排                    | Kubernetes                                         |

## CICD

CICD是Devops中尤为重要的一个环节，主要是通过自动化流程实现代码从开发到生产的快速和可靠交付。

CICD主要分为了三个方面：

1. 持续集成，CI，Continuous Integration

   1. 代码提交：开发者推送代码到版本控制系统
   2. 自动化构建：Jenkins自动编译并打包应用（生成镜像或产物）
   3. 自动化测试：运行单元测试、集成测试等（如Sonarqube、Jacoco，或者自己写单元测试）
   4. 任务反馈：每个环节集成通知和反馈

2. 持续交付，CD，Continuous Delivery（有些时候制品直接交付给客户，不需要部署）

   把持续集成过程中的产物，有可能是代码、镜像、包等，转变为可以随时发布到生产环境的状态，比如推送到镜像仓库。

3. 持续部署，CD，Continuous Deployment

   把产物自动发布到生产环境中。流程：

   1. 制品交付：把CI阶段的产物交付到制品仓库
   2. 制品发布：将制品自动发布到各个环境
   3. 验收测试：验证发布后的过程是否正常

## Pipeline

### 定义

一种自动化流程框架，用于定义、管理、执行一系列有序的任务。

优势：

1. 标准化流程：通过声明方式确保每个环节一致性，避免人工操作差异导致的错误。
2. 自动化执行：有多个任务组成，每个任务可以自动完成，全程无需人工操作。（自己写脚本还得写判断逻辑）
3. 流程可视化：可以看到每个环节执行过程
4. 可追溯性：每个环节都有日志，方便排查问题
5. 支持并行：可以多个任务同时运行，减少任务等待时间
6. 重复执行：支持重试，无需特殊处理
7. 灵活性高

自己写脚本处理这些事项，还得自己写失败判断逻辑、日志采集逻辑、重试逻辑，非常麻烦。

### Pipeline工具

#### Jenkins

优点：

- 长期占据CICD市场头部。社区支持强大、可扩展性、可集成性很强，插件生态系统丰富。

- 基本可以满足企业内任何场景需求。

- 可以跨平台：Win、Linux、Mac、容器、K8s等

缺点：

- 配置复杂
- 需要手动管理插件依赖、插件与Jenkins版本兼容性（升级Jenkins前要对jenkins做备份，升级之后插件用不了就要回滚）

#### Tekton

优点：

- 专门为K8s设计，以CRD方式运行，天然支持容器化和动态资源分配。（原生支持在k8s中创建pod作为slave，不用额外配置）
- Pipeline定义和底层K8s解耦（都是用CRD创建的），迁移方便，扩展性强
- 方便集成企业内部平台进行二次开发（Tekton算是一个CICD框架，方便基于此框架进行二次开发）

缺点：

- 插件支持较少
- 学习难度大，部分功能需要自行开发集成（一些CRD要自己写）
- 需要K8s底座支持 

#### Gitlab CI

优点：

- 与Gitlab仓库深度集成，无需额外配置
- 使用.gitlab-ci.yaml配置，适合中小团队快速上手

缺点：

- 高级功能需要付费
- 扩展性一般
- 需要自行维护Runner
- 无权限隔离

# Jenkins基础

## Jenkins介绍

Jenkins是一个开源的CICD工具，用于自动化构建、测试和部署软件。支持多种编程语言和版本控制系统，可以通过插件扩展功能。在CICD领域属于行业巨头。

Jenkins架构是主从架构：

- Master节点为主节点，主要用于管理任务调度、任务配置、提供web UI。
- Agent节点为从节点，主要用于执行具体的任务，可动态扩展。

## jenkins pipeline

分为声明式和脚本式。

声明式流水线采用结构化语法实现，格式固定、易读性强，并且内置错误处理机制，可以不需要掌握Groovy即可完成编写。同时可以与Blue Ocean结合实现可视化，是目前官网推荐的方式。

声明式pipeline语法，官网：https://www.jenkins.io/doc/book/pipeline/syntax/

声明式流水线和脚本式流水线比较容易区别：

~~~groovy
// 声明式以pipeline开头
pipeline{
    agent any
    stages{
        stage('Build'){
            steps{
                sh 'mvn clean package'
            }
        }
    }
}

// 脚本式以node开头，里面要写很多groovy语言
node('linux-agent'){
}
~~~

### Pipeline声明式语法

#### 结构

Pipeline定义了包含了整个流水线的所有内容和指令，也是声明式流水线的开始，包含三个层级结构：

1. Sections：包含Agent、Stages、Post、Directives和Steps的代码区域块。（即第一层缩进的字段）
2. Directives：包含一个或多个指令，用于执行stage时的条件判断或预处理。（即第二层缩进的字段）
3. Steps：用于指定具体的任务操作，比如sh命令等。（即第三层缩进的字段）

~~~groovy
pipeline{ 
    agent any //指定在哪个从节点上执行
    stages{  //定义流水线执行过程
        stage('Build'){
            steps{ //执行某阶段具体的步骤
                //
            }
        }
        stage('Test'){
            steps{
                //
            }
        }
        stage('Deploy'){
            steps{
                //
            }
        }
    }
}
~~~

- stages: 阶段集合，包裹所有的阶段（例如：打包，部署等各个阶段）
- stage: 阶段，被stages包裹，一个stages可以有多个stage
- steps: 步骤,为每个阶段的最小执行单元,被stage包裹
- post:  执行构建后的操作，根据构建结果来执行对应的操作

~~~groovy
pipeline{ //作用域，应用于全局最外层，表明该脚本为声明式pipeline
    agent any //运行在任意的可用节点上
    stages{
        stage("This is first stage"){
            steps("This is first step"){
                echo "I am xianchao"
            }
        }
    }
    post{
        always{
            echo "The process is ending"
        }
    }
}
~~~

#### environment

- environment指令指定一系列键值对，这些键值对将被定义为所有step或stage-specific step的环境变量，具体取决于environment指令在Pipeline中的位置。
- 该指令支持一种特殊的方法credentials()，可以通过其在Jenkins环境中的标识符来访问预定义的凭据。
- 对于类型为“Secret Text”的凭据，该 credentials()方法将确保指定的环境变量包含Secret Text内容；对于“标准用户名和密码”类型的凭证，指定的环境变量将被设置为username:password并且将自动定义两个附加的环境变量：`MYVARNAME_USR`和`MYVARNAME_PSW`。

~~~groovy
pipeline {
    agent any
    environment {  
        CC = 'clang' 
    }
    stages {
        stage('Example') {
            steps {
                sh 'printenv'
            }
        }
    }
}
~~~

#### options

- options指令允许在Pipeline本身内配置Pipeline专用选项。Pipeline本身提供了许多选项，例如buildDiscarder，但它们也可能由插件提供，例如 timestamps。

- 可用指令：

  - buildDiscarder：pipeline保持构建的最大个数。用于保存Pipeline最近几次运行的数据，例如：options { buildDiscarder(logRotator(numToKeepStr: '1')) }
  - disableConcurrentBuilds：不允许并行执行Pipeline,可用于防止同时访问共享资源等。例如：options { disableConcurrentBuilds() }
  - skipDefaultCheckout：跳过默认设置的代码check out。例如：options { skipDefaultCheckout() }
  - skipStagesAfterUnstable：一旦构建状态进入了“Unstable”状态，就跳过此stage。例如：options { skipStagesAfterUnstable() }
  - timeout：设置Pipeline运行的超时时间，超过超时时间，job会自动被终止，例如：options { timeout(time: 1, unit: 'HOURS') }
  - retry：失败后，重试整个Pipeline的次数。例如：options { retry(3) }
  - timestamps： 预定义由Pipeline生成的所有控制台输出时间。例如：options { timestamps() }

  ~~~groovy
  pipeline {
      agent any
      options {
          timeout(time: 1, unit: 'HOURS') 
      }
      stages {
          stage('Example') {
              steps {
                  echo 'Hello World'
              }
          }
      }
  }　
  ~~~

#### parameters

- parameters指令提供用户在触发Pipeline时的参数列表。这些参数值通过该params对象可用于Pipeline stage中，作用域：被最外层pipeline所包裹，并且只能出现一次，参数可被全局使用

  ~~~groovy
  pipeline{
      agent any
      parameters {
          string(name: 'xianchao', defaultValue: 'my name is xianchao', description: 'My name is xiancaho')
          booleanParam(name: 'luckylucky421302', defaultValue: true, description: 'This is my wechat')
      }
      stages{
          stage("stage1"){
              steps{
                  echo "$xianchao"
                  echo "$luckylucky421302"
              }
          }
      }
  } //构建的时候选择build with paramaters，否则识别不了parameter
  ~~~

#### triggers

- triggers指令定义了Pipeline自动化触发的方式。目前有三个可用的触发器：cron和pollSCM和upstream。
- 被pipeline包裹，在符合条件下自动触发pipeline

#### tools

- 通过tools可自动安装工具，并放置环境变量到PATH。如果agent none，这将被忽略。
- 支持的tools：maven、jdk、gradle

~~~groovy
pipeline {
    agent any
    tools {
       //工具名称必须在Jenkins 管理Jenkins → 全局工具配置中预配置。
        maven 'apache-maven-3.0.1'
    }
    stages {
        stage('Example') {
            steps {
                sh 'mvn --version'
            }
        }
    }
}
~~~

#### input

- stage 的 input 指令允许你使用 input step提示输入。
- 在应用了 options 后，进入 stage 的 agent 或评估 when 条件前，stage 将暂停。如果 input 被批准, stage 将会继续。
- 作为 input 提交的一部分的任何参数都将在环境中用于其他 stage
- 参数
  - message：必需的。 这将在用户提交 input 时呈现给用户。
  - id：input 的可选标识符， 默认为 stage 名称。
  - ok：`input`表单上的"ok" 按钮的可选文本。
  - submitter：可选的以逗号分隔的用户列表或允许提交 input 的外部组名。默认允许任何用户。admin可以无视这个列表直接处理input
  - submitterParameter：环境变量的可选名称。如果存在，用 submitter 名称设置。
  - parameters：提示提交者提供的一个可选的参数列表。

~~~groovy
pipeline {
    agent any
    stages {
        stage('Example') {
            input {
                message "Should we continue?"
                ok "Yes, we should."
                submitter "xianchao,lucky"
                parameters {
                    string(name: 'PERSON', defaultValue: 'xianchao', description: 'Who should I say hello to?')
                }
            }
            steps {
                echo "Hello, ${PERSON}, nice to meet you."
            }
        }
    }
}
~~~

# Jenkins部署使用

Jenkins主节点可以采用Docker、K8s或者war包进行部署。如果K8s中没有安装分布式可靠存储，建议直接采用Docker安装，slave从节点可以在k8s中部署。

## Docker安装jenkins

首先需要一个Linux服务器，配置不低于2C4G和40G硬盘。

先装Docker：

~~~sh
# 在rockylinux上：
yum install -y yum-utils device-mapper-persistent-data lvm2 
yum-config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo 
yum install docker-ce docker-ce-cli -y 
systemctl daemon-reload && systemctl enable --now docker
~~~

创建Jenkins 的数据目录，防止容器重启后数据丢失：

~~~sh
mkdir /data/jenkins_data -p
chmod -R 777 /data/jenkins_data
~~~

启动Jenkins，并配置管理员账号密码为admin/admin123：

其中8080端口为Jenkins Web界面的端口，50000是jnlp使用的端口，后期Jenkins Slave需要使用50000端口和Jenkins主节点通信。 

~~~sh
# 用的镜像是：docker.io/bitnami/jenkins:2.504.3-debian-12-r1
docker run -d \
--name=jenkins \
--restart=always \
-e JENKINS_PASSWORD=admin123 \
-e JENKINS_USERNAME=admin \
-e JENKINS_HTTP_PORT_NUMBER=8080 \
-p 8080:8080 \
-p 50000:50000 \
-v /usr/bin/docker:/usr/bin/docker \
-v /var/run/docker.sock:/var/run/docker.sock \
-v /data/jenkins_data:/bitnami/jenkins \
m.daocloud.io/docker.io/bitnami/jenkins:2.504.3-debian-12-r1 
~~~

查看jenkins日志：

~~~sh
docker logs -f  Jenkins 
# 查看到这条日志说明Jenkins已完成启动 
INFO: Jenkins is fully up and running
~~~

安装完成后可以通过Jenkins宿主机IP:8080端口访问UI界面。

## 插件安装

进入Manage Jenkins -> Manage Plugins安装需要使用的插件。

1. 首先配置国内插件源：在Advanced Settings里面将Update Site - URL改为国内源：`https://mirrors.huaweicloud.com/jenkins/updates/update-center.json`，点击submit保存

2. 在Available Plugins里面可以看到所有的可用插件，安装这些：

   ~~~sh
   Git 
   Git Parameter 
   Git Pipeline for Blue Ocean 
   GitLab 
   Credentials 
   Credentials Binding 
   Blue Ocean 
   Blue Ocean Pipeline Editor 
   Blue Ocean Core JS 
   Web for Blue Ocean 
   Pipeline SCM API for Blue Ocean 
   Dashboard for Blue Ocean 
   Build With Parameters 
   List Git Branches Parameter 
   Pipeline 
   Pipeline: Declarative 
   Kubernetes 
   Kubernetes CLI 
   Kubernetes Credentials 
   Image Tag Parameter 
   Docker 
   Docker Slaves 
   Docker Pipeline 
   Role-based Authorization Strategy 
   ~~~

   

# Jenkins插件离线安装

1. Jenkins离线插件下载地址:http://mirrors.tuna.tsinghua.edu.cn/jenkins/plugins/，可以在Jenkins官网上搜索想要下载的插件，点击“Download”按钮下载.hpi文件。

2. Jenkins离线插件安装方法：
   1. 方法一：在Jenkins管理页面点几“系统管理” -> “插件管理” -> “高级”。选择“上传插件”，并选择下载的.hpi文件。点击“上传”按钮，等待插件安装完成。
   2. 方法二：将下载的.hpi文件放到Jenkins的安装目录下的“plugins”文件夹中。重启Jenkins，等待插件安装完成。

# Jenkins版本升级

Jenkins 版本升级通常分为以下几个步骤：

1. 备份当前 Jenkins 数据在升级之前，应该备份当前 Jenkins 数据以避免数据丢失。可以通过将 Jenkins 的 JENKINS_HOME 目录复制到其他位置来备份数据。

2. 下载新版本的 Jenkins在官网下载最新版本的 Jenkins war 文件，通常可以在 https://www.jenkins.io/download/ 找到最新版本。

3. 停止当前 Jenkins 实例在进行版本升级之前，需要停止当前运行的 Jenkins 实例。

4. 启动新版本的 Jenkins将下载的新版本 Jenkins war 文件复制到 Jenkins 的安装目录下，并启动 Jenkins。在 Linux 系统中，可以使用以下命令来启动 Jenkins：`java -jar jenkins.war`
5. 升级插件在新版本的 Jenkins 中，有可能需要升级现有插件以保持兼容性。在 Jenkins 管理页面的“插件管理”中，可以检查并升级插件。
6. 验证升级启动新版本的 Jenkins 后，可以通过访问 Jenkins Web 界面来验证升级是否成功，并确保所有插件和功能正常工作。
