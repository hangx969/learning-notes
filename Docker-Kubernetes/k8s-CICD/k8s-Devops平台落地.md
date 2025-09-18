# Devops平台建设

## 通用流程

微服务发版的自动化流水线，一般会有如下步骤：

1. 在Gitlab中创建对应的项目，项目名称与微服务名称相同即可。（建议一个微服务对应一个gitlab project）
2. 配置Jenkins集成k8s集群，后期Jenkins的Slave将为在K8s中动态创建的Slave
3. Jenkins创建对应的任务（Job），集成该项目的Git地址和K8s集群。（建议一个微服务对应一个Pipeline）
4. 开发者将代码提交到Gitlab。
5. 如果配置了Webhook，推送代码会自动触发Jenkins构建；如果没有配置Webhook，需要手动选择branch触发。
6. Jenkins控制K8s，创建Jenkins Slave pod
7. Jenkins Slave pod根据Pipeline定义的步骤执行构建，生成交付物
8. 通过Dockerfile生成镜像
9. 将镜像Push到Harbor或其他镜像仓库
10. Jenkins再次控制K8s进行最新的镜像部署
11. 流水线结束，删除Jenkins slave

基本上所有的语言都是类似的流程，可以设计一个通用模板。

## 架构设计

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202509171636477.png" alt="image-20250917163628290" style="zoom:50%;" />
