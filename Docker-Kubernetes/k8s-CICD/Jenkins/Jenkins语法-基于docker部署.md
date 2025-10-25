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

### Sections

声明式流水线中的Sections 不是一个关键字或指令，而是包含一个或多个Agent、Stages、 Post、Directives 和 Steps 的代码区域块。

#### Agent

Agent表示整个流水线或特定阶段中的步骤和命令执行的位置，该部分可以在pipeline块的顶层被定义，也可以在stage中再次定义，也可以同时在两处定义。 

- any：在任何可用的代理上执行流水线，配置语法：

  ~~~groovy
  pipeline { 
  	agent any 
  }
  ~~~

- none：表示该Pipeline脚本没有全局的agent配置。当顶层的agent配置为none时，可以为每个stage配置局部的agent。配置语法：

  ~~~groovy
  pipeline { 
  	agent none 
  	stages { 
  		stage('Stage For Build'){ 
  			agent any 
  		} 
  	} 
  }
  ~~~

- label：选择某个具体的节点执行Pipeline命令，例如：`agent { label 'my-slave-label' }`。如果这个标签的agent不存在，任务会一直处于等待agent状态。配置语法：

  ~~~groovy
  pipeline { 
  	agent none 
  	stages { 
  		stage('Stage For Build'){ 
  			agent { label 'my-slave-label' } 
  		} 
  	} 
  } 
  ~~~

- docker：agent支持直接使用镜像作为agent，这也是比较推荐的方式。直接用带基础环境的镜像，可以避免处理编译环境或者slave的版本问题。比如Java编译，可以直接使用maven镜像启动slave，之后进行打包，同时可以指定args：

  ~~~groovy
  pipeline{ 
      agent any
      stages{ 
          stage('Build'){
              agent {
                  docker {
                      image 'registry.cn-beijing.aliyuncs.com/dotbalo/maven:3.5.3'
                      args '-v /tmp:/tmp'
                  }
              }
              steps{ 
                  echo 'Hello World'
                  sh 'pwd'
                  sh 'hostname'
                  sh 'mvn -version'
              }
          }
      }
  }
  ~~~

- kubernetes：Jenkins 也支持使用Kubernetes创建Slave，也就是动态Slave。配置示例如下： 

  官网文档：https://plugins.jenkins.io/kubernetes/#plugin-content-configuration-reference 

  ~~~groovy
  agent { 
  	kubernetes { 
  		label podlabel 
  		yaml """ 
  kind: Pod 
  metadata: 
    name: jenkins-agent 
  spec: 
    containers: 
    - name: kaniko 
      image: gcr.io/kaniko-project/executor:debug 
      imagePullPolicy: Always 
      command: 
      - /busybox/cat 
      tty: true 
      volumeMounts: 
      - name: aws-secret 
        mountPath: /root/.aws/ 
      - name: docker-registry-config 
        mountPath: /kaniko/.docker 
    restartPolicy: Never 
    volumes: 
    - name: aws-secret 
      secret: 
        secretName: aws-secret 
    - name: docker-registry-config 
      configMap: 
        name: docker-registry-config 
  """ 
  } 
  ~~~

#### stages

阶段集合，包裹所有的阶段（例如：打包，部署等各个阶段）。stage: 阶段，被stages包裹，一个stages可以有多个stage

~~~groovy
pipeline { 
    agent any 
    stages {  
        stage('Example') { 
            steps { 
                echo 'Hello World' 
            } 
        } 
    } 
} 
~~~

#### steps

Steps部分在给定的stage指令中执行的一个或多个步骤，比如在steps定义执行一条shell命令：

~~~groovy 
pipeline { 
    agent any 
    stages { 
        stage('Example') { 
            steps {  
                echo 'Hello World' 
            } 
        } 
    } 
} 
~~~

也可以执行多条shell：

~~~groovy
pipeline { 
    agent any 
    stages { 
        stage('Example') { 
            steps {  
                sh """ 
                 echo 'Execute building...' 
                 mvn clean install 
                 """ 
            } 
        } 
    } 
} 
~~~

#### post

Post一般用于流水线结束之后的进一步处理，比如错误通知等。Post可以针对流水线不同的结果做出不同的处理，就像开发程序的错误处理。比如python中的try catch。Post可以定义在PIpeline或stage中。支持以下条件：

- always：无论Pipeline或stage的完成状态如何，都会执行post中定义的指令
- changed：只有当前Pipeline或stage的完成状态与他之前的运行不同时，才执行post部分
- fixed：本次Pipeline或stage成功，且上一次构建是失败或不稳定的时候，才执行post部分
- regression：当本次Pipeline或stage状态为失败、不稳定或终止，且上一次构建成功时，才执行post部分
- failure：当前pipeline或stage状态为失败，才执行post。通常失败会在web中显示为红色
- success：当前状态为成功，才执行post步骤，web中显示为蓝色或绿色。
- unstable：当前状态为不稳定，执行post步骤，通常由于测试失败或代码违规等造成，在Web界面中显示为黄色
- aborted：当前状态为终止（aborted），执行该post步骤，通常由于流水线被手动终止触发，这时在Web界面中显示为灰色
- unsuccessful：当前状态不是success时，执行该post步骤；
- cleanup：无论pipeline或stage的完成状态如何，都允许运行该post中定义的指令。和always的区别在于，cleanup会在其它执行之后执行。 

示例：一般情况下，post部分都是放在流水线的底部:

~~~groovy
// 写在pipeline里面
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                echo 'Hello World'
            }
        }
    }
    post {
        always {
            echo 'This is post message'
        }
    }
}

// 也可以写在某个stage里面
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'EXECUTE_COMMAND'
            }
            post {
                failure {
                    echo 'Pipeline failure'
                }
            }
        }
    }
}
~~~

### Directives

Directives可用于执行stage时的一些条件判断或者预处理一些数据，他也不是一个关键字或指令，而是包含了environment、options、parameters、triggers、stage、tools、input、when等配置。

#### environment

用于在流水线中配置一些环境变量，根据配置的位置决定环境变量的作用域。在pipeline中定义就作为全局环境变量，也可以配置在stage中作为该stage的环境变量。

假设需要定义一个变量名为cc的全局变量和一个局部变量，可以通过以下方式定义：

~~~groovy
pipeline {
    agent any
    environment {  
        CC = 'global' 
    }
    stages {
        stage('local env') {
            environment {
                CC2 = 'local'
            }
            steps {
                sh """
                  echo CC2: $CC2
                  echo CC: $CC
                """
            }
        }
    }
}
~~~

推荐把镜像tag作为环境变量放进去。

#### options

options指令允许在Pipeline中配置Pipeline专用选项。Pipeline本身提供了许多选项，例如buildDiscarder，但它们也可能由插件提供，例如 timestamps。

可用指令：

- `buildDiscarder`：保留多少个流水线的构建记录。例如：options { buildDiscarder(logRotator(numToKeepStr: '1')) }
- `disableConcurrentBuilds`：禁止流水线并行执行，防止并行导致的资源共享访问。例如：options { disableConcurrentBuilds() }
- `disableResume`：如果控制器重启，禁止流水线自动恢复。比如：options { disableResume() }
- `skipDefaultCheckout`：跳过默认设置的代码check out。例如：options { skipDefaultCheckout() }
- `skipStagesAfterUnstable`：一旦构建状态进入了“Unstable”状态，就跳过此stage。例如：options { skipStagesAfterUnstable() }
- `timeout`：设置Pipeline运行的超时时间，超过超时时间，job会自动被终止，例如：options { timeout(time: 1, unit: 'HOURS') }。timeout一般用于编译、代码扫描的步骤，长时间没有结果可能是卡死了，可以设置超时时间。
- `retry`：失败后，重试整个Pipeline的次数。例如：options { retry(3) }
- `timestamps`： 预定义由Pipeline生成的所有控制台输出时间。例如：options { timestamps() }

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

Option除了写在Pipeline顶层，还可以写在stage中，但是写在stage中的option仅支持retry、timeout、timestamps，或者是和stage相关的声明式选项，比如skipDefaultCheckout。

#### parameters

一般用于创建一个流水线的通用模板，应用于不同的环境，比如test、dev、prod等。

目前支持的参数类型如下：

- `string`：字符串类型的参数，例如：parameters { string(name: 'DEPLOY_ENV', defaultValue: 'staging', description: '') }，表示定义一个名为DEPLOY_ENV的字符型变量，默认值为 staging；
- `text`：文本型参数，一般用于定义多行文本内容的变量。例如parameters { text(name:  'DEPLOY_TEXT', defaultValue: 'One\nTwo\nThree\n', description: '') }，表示定义一个名 为DEPLOY_TEXT的变量，默认值是'One\nTwo\nThree\n'； 
- `booleanParam`：布尔型参数，例如: parameters { booleanParam(name: 'DEBUG_BUILD', defaultValue: true, description: '') }；
- `choice`：选择型参数，一般用于给定几个可选的值，然后选择其中一个进行赋值，例如：parameters { choice(name: 'CHOICES', choices: ['one', 'two', 'three'], description: '') }，表示定义一个名为CHOICES的变量，可选的值为one、two、three；
- `password`：密码型变量，一般用于定义敏感型变量，在Jenkins控制台会显示为*。例如：parameters { password(name: 'PASSWORD', defaultValue: 'SECRET', description: 'A secret password') }，表示定义一个名为PASSWORD的变量，其默认值为SECRET。

~~~groovy
pipeline { 
    agent any 
    parameters { 
        string(name: 'PERSON', defaultValue: 'Mr Jenkins', description: 'Who should I say hello to?') 
 
        text(name: 'BIOGRAPHY', defaultValue: '', description: 'Enter some information about the person') 
 
        booleanParam(name: 'TOGGLE', defaultValue: true, description: 'Toggle this value') 
 
        choice(name: 'CHOICE', choices: ['One', 'Two', 'Three'], description: 'Pick something') 
 
        password(name: 'PASSWORD', defaultValue: 'SECRET', description: 'Enter a password') 
    } 
    stages { 
        stage('Example') { 
            steps { 
                echo "Hello ${params.PERSON}" 
                echo "Biography: ${params.BIOGRAPHY}" 
                echo "Toggle: ${params.TOGGLE}" 
                echo "Choice: ${params.CHOICE}" 
                echo "Password: ${params.PASSWORD}" 
            } 
        } 
    } 
} 
// 构建的时候选择build with paramaters，否则识别不了parameter
~~~

除了上述内置的参数外，还可以通过插件扩展参数的能力，比如使用Git插件定义参数： 

~~~groovy
parameters { 
// 该字段会在Jenkins页面生成一个选择分支的选项，用于赋值到BRANCH参数 
    gitParameter(branch: '', branchFilter: 'origin/(.*)', defaultValue: '', description: 'Branch for build and deploy', name: 'BRANCH', quickFilterEnabled: false, selectedValue: 'NONE', sortMode: 'NONE', 
tagFilter: '*', type: 'PT_BRANCH') 
}
~~~

如何找到都支持哪些parameters？去pipeline - Configure - Pipeline - Pipeline Syntax就会进入一个语法生成器页面，在第二个‘**Declarative Directive Generator**’里面，Sample Directive - parameters: Parameters就能看到各种支持的parameter以及类型了。

#### triggers

在Pipeline中可以用Triggers实现自动触发流水线，可以通过Webhook、Cron、pollSCM、upstream等方式触发流水线。

> 注意：一般情况下triggers不会在pipeline中写，一般在界面中去配置。因为很多情况下pipeline是一个模板，针对不同的服务。一般是对每个job在ui上设置触发器。

示例：

1. cron：假如某个流水线构建的时间比较长，或者需要氢气在某个时间段执行构建，可以用cron，比如周一到周五每隔四个小时执行一次

~~~groovy
pipeline { 
    agent any 
    triggers { 
        cron('H */4 * * 1-5') // 格式是分时日月周，但是分的位置写的H意思是随机分钟。在0-59分钟之间找一个空闲分钟去执行。防止很多构建任务挤在同一个时间点执行。
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

2. pollSCM：使用cron字段可以定期执行流水线。如果希望在定时基础上，检测代码更新，只有代码更新了才触发流水线，无更新则不触发流水线，可以使用pollSCM字段

~~~groovy
pipeline { 
    agent any 
    triggers { 
        pollSCM('H */4 * * 1-5') 
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

3. Upstream：可以根据上游job的执行结果决定是否触发该流水线。比如当job1或job2执行成功时触发该流水线

~~~groovy
pipeline { 
    agent any 
    triggers { 
        upstream(upstreamProjects: 'job1,job2', threshold: hudson.model.Result.SUCCESS) 
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

目前支持的状态有SUCCESS、UNSTABLE、FAILURE、NOT_BUILT、ABORTED等。（用的比较少）

4. Webhook【用的最多】

#### input

Input字段可以实现在流水线中交互式操作。比如选择要部署的环境、是否继续执行某个阶段等。在公司没有单独的审批平台时可以使用。

支持以下选项：

- message：必须。需要用户进行input的提示信息，比如“Deploy to Prod?”
- id：可选。input的标识符，默认为 stage 名称。
- ok：可选。确认按钮的显示信息。比如：”确定“、”允许“
- submitter：可选。允许提交input操作的用户或组的名称，为空则所有登录用户皆可提交input。admin可以无视这个列表直接处理input。
- parameters：提供一个参数列表供input使用

~~~groovy
pipeline {
    agent any
    stages {
        stage('Example') {
            input {
                message "Deploy to Prod? (true/false)"
                ok "true"
                submitter ""
                parameters {
                    string(name: 'DEPLOY', defaultValue: 'false', description: 'Deploy or not?')
                }
            }
            steps {
                echo ${DEPLOY}
            }
        }
    }
}
~~~

#### when

允许流水线根据给定的条件判断是否应该执行stage，when必须包含至少一个条件。如果when包含多个条件，都返回true，stage才能执行。

比较常用的内置条件：

- `branch`：【最常用】当正在构建的分支与给定的分支匹配时，执行这个stage。例如：when { branch 'master' }。注意，branch只适用于多分支流水线
- `changelog`：匹配提交的changeLog决定是否构建。例如：when { changelog '.*^\\[DEPENDENCY\\] .+$' }；*
- `environment`：当指定的环境变量和给定的变量匹配时，执行这个stage。例如：when { environment name: 'DEPLOY_TO', value: 'production' }；
- `expression`：当指定的Groovy表达式评估为True，执行这个stage。例如：when  { expression { return params.DEBUG_BUILD } }；
- `tag`：代码提交的tag值和给定的条件匹配，执行这个stage，例如：when { tag "release-*" }；
- `not`：当嵌套条件出现错误时，执行这个stage，必须包含一个条件，例如：when { not { branch 'master' } }；
- `allOf`：当所有的嵌套条件都正确时，执行这个stage，必须包含至少一个条件，例如： when { allOf { branch 'master'; environment name: 'DEPLOY_TO', value: 'production' } }；
- `anyOf`：当至少有一个嵌套条件为True时，执行这个stage，例如：when { anyOf { branch  'master'; branch 'staging' } }。

示例：

分支是production，而且DEPLOY_TO变量的值为production 时，才执行Example Deploy：

~~~groovy
pipeline { 
    agent any 
    stages { 
        stage('Example Build') { 
            steps { 
                echo 'Hello World' 
            } 
        } 
        stage('Example Deploy') { 
            when { 
                branch 'production' 
                environment name: 'DEPLOY_TO', value: 'production' 
            } 
            steps { 
                echo 'Deploying' 
            } 
        } 
    } 
} 
~~~

#### beforeAgent

默认情况下，如果定义了某个stage的agent，在进入到该agent后，when条件才会被评估。但是有一种情况是用docker作为slave的时候，条件判断应该是在创建slave agent之前，不符合条件就不创建slave；when为true才去创建slave。这样才比较合理，用beforeAgent参数写到when里面就可以。

目前支持的前置条件如下：

- `beforeAgent`：如果beforeAgent为true，则会先评估when条件。在when条件为true时，才会进入该stage

  ~~~groovy
  pipeline { 
      agent none 
      stages { 
          stage('Example Build') { 
              steps { 
                  echo 'Hello World' 
              } 
          } 
          stage('Example Deploy') { 
              agent { 
                  label "some-label" 
              } 
              when { 
                  beforeAgent true 
                  branch 'production' 
              } 
              steps { 
                  echo 'Deploying' 
              } 
          } 
      } 
  } 
  ~~~

- `beforeInput`：如果beforeInput为true，则会先评估when条件。在when条件为true时，才会进入到input阶段

  ~~~groovy
  pipeline { 
      agent none 
      stages { 
          stage('Example Build') { 
              steps { 
                  echo 'Hello World' 
              } 
          } 
          stage('Example Deploy') { 
              when { 
                  beforeInput true 
                  branch 'production' 
              } 
              input { 
                  message "Deploy to production?" 
                  id "simple-input" 
              } 
              steps { 
                  echo 'Deploying' 
              } 
          } 
      } 
  }
  ~~~

- `beforeOptions`：如果beforeOptions为true，则会先评估when条件。在when条件为true时，才会进入到options阶段

  ~~~groovy
  pipeline { 
      agent none 
      stages { 
          stage('Example Build') { 
              steps { 
                  echo 'Hello World' 
              } 
          } 
          stage('Example Deploy') { 
              when { 
                  beforeOptions true 
                  branch 'testing' 
              } 
              options { 
                  retry(3) 
              } 
              steps { 
                  echo "Deploying to ${deployEnv}" 
              } 
          } 
      } 
  }
  ~~~

  

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

### 并行处理Parallel

当某几个stage都比较慢，并且都可以并行执行，就可以把这几个stage放到一个parallel里面并行处理，减少构建时间。

~~~groovy
pipeline { 
    agent
    {
        docker{
            image 'busybox:1.28'
        }
    }
    stages { 
        stage('Non-Parallel Stage') { 
            steps { 
                echo 'This stage will be executed first.' 
            } 
        } 
        stage('Parallel Stage') { 
            failFast true 
            parallel { 
                stage('Stage A') { 
                    steps { 
                        echo "On A" 
                    } 
                } 
                stage('Stage B') { 
                    steps { 
                        echo "On B" 
                    } 
                } 
                stage('Stage C') { 
                    steps { 
                        echo "On C" 
                    } 
 
                } 
            } 
        } 
    } 
} 
~~~

设置failFast 为true表示并行流水线中任意一个stage出现错误，其它stage也会立即终止。 也可以通过options配置在全局：

~~~groovy
pipeline { 
    agent any 
    options { 
        parallelsAlwaysFailFast() 
    } 
    stages { 
        stage('Non-Parallel Stage') { 
            steps { 
                echo 'This stage will be executed first.' 
            } 
        } 
        stage('Parallel Stage') { 
            parallel { 
                stage('Stage A') { 
                    steps { 
                        echo "On A" 
                    } 
                } 
                stage('Stage B') { 
                    steps { 
                        echo "On B" 
                    } 
                } 
                stage('Stage C') { 
                    steps { 
                        echo "On C" 
                    } 
 
                } 
            } 
        } 
    } 
} 
~~~

## Pipeline常用变量处理

### 内置环境变量

Jenkins有许多内置变量可以直接在Jenkinsfile中使用，可以通过JENKINS_URL/pipeline-syntax/globals#env获取完整列表。

目前比较常用的环境变量如下：

- `BUILD_ID`：构建ID，对于1.597及以上版本和BUILD_NUMBER一致。而对于更早版本的构建则是一个YYYY-MM-DD_hh-mm-ss格式的时间戳
- `BUILD_NUMBER`：当前构建的ID，和BUILD_ID一致
- `BUILD_TAG`：用来标识构建的版本号，格式为：`jenkins-${JOB_NAME}-${BUILD_NUMBER}`，可以对产物进行命名，比如生产的jar包名字、镜像的TAG等
- `BUILD_URL`：本次构建的完整URL，比如：http://buildserver/jenkins/job/MyJobName/17/。这个URL后面拼上`/console`就能直接看到构建的output了
- `JOB_NAME`：本次构建的项目名称
- `NODE_NAME`：当前构建节点的名称
- `JENKINS_URL`：Jenkins完整的URL，需要在System Configuration设置
- `WORKSPACE`：执行构建的工作目录。

上述内置变量都会保存在一个叫env的Map当中，可以使用`env.BUILD_ID`，`env.JENKINS_URL`这种格式引用某个内置变量：

~~~groovy
pipeline { 
    agent any 
    stages {
        stage('Show ENV') { 
            steps { 
                echo "Show all envs"
                sh """
                  env
                """
            } 
        } 
        stage('Example') { 
            steps { 
                echo "Running ${env.BUILD_ID}, tag ${env.BUILD_TAG}" 
            } 
        } 
    } 
}
~~~

### 凭证管理

#### 用户名密码

主要是在UI界面上添加：Manage Jenkins - Security - Credentials - Stores scoped to Jenkins - (global) - Add credentials。

类型选择Username with password，ID自己输入一个，比如是`HARBOR_USER_PASSWD`。接下来可以在environment中获取凭证的值：

~~~groovy
environment { 
	HARBOR_ACCOUNT = credentials('HARBOR_USER_PASSWD') 
} 
~~~

以上配置会自动生成三个环境变量：

1. HARBOR_ACCOUNT：包含一个以冒号分隔的用户名和密码，格式为 username:password
2. HARBOR_ACCOUNT_USR：仅包含用户名的附加变量
3. HARBOR_ACCOUNT_PSW：仅包含密码的附加变量

此时可以用以下方式获取变量：

~~~groovy
pipeline { 
    agent any 
    stages { 
        stage('Example stage 1') { 
        environment { 
            HARBOR_ACCOUNT = credentials('HARBOR_USER_PASSWD') 
        }
            steps { 
                 echo """ 
                      HARBOR_ACCOUNT: $HARBOR_ACCOUNT 
                      HARBOR_ACCOUNT_USR: $HARBOR_ACCOUNT_USR 
                      HARBOR_ACCOUNT_PSW: $HARBOR_ACCOUNT_PSW 
                 """ 
            } 
        } 
    } 
}
~~~

#### 加密文件

如果需要加密某个文件，可以使用credential，比如连接到k8s集群的kubeconfig文件等。

首先创建文本形式的凭证：类型选择Secret file，上传文件，设置ID。接下来可以在pipeline中引用：

~~~groovy
pipeline { 
    agent any 
    environment { 
        KUBECONFIG_LOCAL = credentials('KUBECONFIG_LOCAL') 
    } 
    stages { 
        stage('Secret File') { 
            steps { 
                sh "cat $KUBECONFIG_LOCAL" 
            } 
        } 
    } 
}
~~~

## Agent配置示例

### 基于docker slave

1. 假设有一个Java项目，需要用到mvn命令进行编译，此时可以用maven基础镜像作为agent，配置如下：

   ~~~groovy
   pipeline { 
       agent {
           docker {
               image 'registry.cn-beijing.aliyuncs.com/dotbalo/maven:3.5.3'
               args '-v /tmp:/tmp'
           }
       }
       stages{ 
           stage('Build'){
               steps{ 
                   sh 'mvn -v'
               }
           }
       }
   }
   ~~~

2. 有多个stage，需要不同的agent，就把顶层agent设为none，具体agent配置在每个stage里面：

   ~~~groovy
   pipeline{ 
       agent none
       stages{ 
           stage('Build'){
               agent {
                   docker {
                       image 'registry.cn-beijing.aliyuncs.com/dotbalo/maven:3.5.3'
                       args '-v /tmp:/tmp'
                   }
               }
               steps{ 
                   sh 'mvn -v'
               }
               stage('Test') {
                   agent {
                       docker {
                           image 'registry.cn-beijing.aliyuncs.com/dotbalo/jre:8u211-data'
                       }
                   }
                   steps {
                       sh 'java -version'
                   }
               }
           }
       }
   }
   ~~~

### 基于k8s slave

上述示例可以用K8s slave pod实现。比定义具有3个容器的pod，分别为jnlp（负责与jenkins master通信）、build（执行构建命令）、kubectl（执行k8s命令）。在steps中，可以通过containers字段，选择在某个容器内执行命令.

Kubernetes Agent详细语法：https://plugins.jenkins.io/kubernetes/#plugin-content-configuration-reference

注：dockerhub上的镜像地址：

```bash
jenkins/jnlp-agent-docker:latest
maven:3.5.3
bitnami/kubectl:latest
```

~~~groovy
pipeline{ 
    agent {
        kubernetes {
            cloud 'kubernetes-default' 
            slaveConnectTimeout 1200 
            yaml '''
apiVersion: v1 
kind: Pod 
spec: 
  containers: 
  - name: jnlp
    image: 'registry.cn-beijing.aliyuncs.com/dotbalo/jnlp-agent-docker:latest'  
    imagePullPolicy: IfNotPresent       
    args: [\'$(JENKINS_SECRET)\', \'$(JENKINS_NAME)\'] 
  - name: "build"
    image: "registry.cn-beijing.aliyuncs.com/dotbalo/maven:3.5.3" 
    imagePullPolicy: "IfNotPresent" 
    command: 
    - "cat" 
    tty: true 
  - name: "kubectl" 
    command: 
    - "cat" 
    image: "registry.cn-beijing.aliyuncs.com/dotbalo/kubectl:latest" 
    imagePullPolicy: "IfNotPresent" 
    tty: true 
'''          
        }
    }
    stages{ 
        stage('Build'){
            steps{ 
                container(name: 'build')
                sh 'mvn -v'
            }
            stage('Deploy') {
                steps {
                    container(name: 'kubectl')
                    sh 'kubectl get node'
                }
            }
        }
    }
}
~~~
