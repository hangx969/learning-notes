# 介绍

- Hashicorp发明，基于Go语言

- 脚本采用HCL语言：

  - 声明式，Infrastructure as Code，通过对比状态来实现资源的变更。

  - 脚本即文档

# Terraform 三个阶段

- terraform init
- terraform plan
- terraform apply

 

# 配置文件组成

- Provider部分：用哪家的provider	

- resource部分：创建什么资源

- variable部分：集中存储变量、参数

- output文件

# 三个基本文件

- main.tf
  - 部署的骨头架子，存放主要的代码

- variable.tf
  - 集中存储变量

- terraform.tfvars
  - 覆盖一些变量，作为变量的临时定义处