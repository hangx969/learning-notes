---
title: 杂项领域（Database/Middlewares/OS/Networking/IaC/Git/C++/SoftwareTesting）来源批量摘要
tags:
  - knowledgebase/source
  - misc
date: 2026-04-17
sources:
  - "[[Database/MGR部署MySQL5.7]]"
  - "[[Database/MySQL入门]]"
  - "[[Database/源码安装redis-6.2.6-centos7]]"
  - "[[Middlewares/Kafka]]"
  - "[[Middlewares/RabbitMQ]]"
  - "[[Middlewares/RocketMQ]]"
  - "[[OS/计算机组成原理]]"
  - "[[OS/OS-磁盘管理]]"
  - "[[OS/OS]]"
  - "[[Networking/计算机网络基础]]"
  - "[[Networking/HTTP基础]]"
  - "[[IaC/terraform-docs]]"
  - "[[IaC/terraform-basics]]"
  - "[[Git/git-learning]]"
  - "[[Git/Picgo-github图床配置]]"
  - "[[C++/C++LearningNotes]]"
  - "[[SoftwareTesting/软件工程基础]]"
  - "[[SoftwareTesting/软件测试直播课笔记]]"
---

## 元信息

| 项目 | 说明 |
|------|------|
| 涵盖目录 | Database、Middlewares、OS、Networking、IaC、Git、C++、SoftwareTesting（共 8 个目录） |
| 文档总数 | 18 篇 |
| 摄入日期 | 2026-04-17 |
| 内容语言 | 中文为主，部分技术术语使用英文 |

---

## 整体概述

本批次汇总了 8 个杂项技术领域的学习笔记，覆盖面广、层次分明：

- **数据库层**：涵盖 [[KnowledgeBase/entities/MySQL|MySQL]] 从入门 SQL 语法到 MGR 高可用集群部署，以及 [[KnowledgeBase/entities/Redis|Redis]] 从源码编译到哨兵/Cluster 高可用方案。
- **中间件层**：记录了三大主流消息队列 [[KnowledgeBase/entities/Kafka|Kafka]]、[[KnowledgeBase/entities/RabbitMQ|RabbitMQ]]、[[KnowledgeBase/entities/RocketMQ|RocketMQ]] 的学习资源。
- **操作系统层**：从冯诺依曼体系结构、CPU 分类讲到操作系统四大特征（并发/共享/虚拟/异步）、进程管理、内存管理、磁盘调度算法。
- **网络层**：包含 OSI/TCP-IP 分层模型、分组交换机制、HTTP 协议版本演进（1.0/1.1 持久连接/Pipeline/Cookie）。
- **基础设施即代码**：[[KnowledgeBase/entities/Terraform|Terraform]] 的三阶段工作流（init/plan/apply）、HCL 语言基础、Azure 资源部署示例，以及 terraform-docs 文档自动生成工具。
- **版本控制**：Git 基本理论（工作区/暂存区/仓库/远程）、文件状态流转，以及 PicGo + GitHub 图床配置实践。
- **编程语言**：C++ 基础知识（命名空间、内存四区、指针、存储类型）。
- **软件工程与测试**：软件生存期模型（瀑布/敏捷）、面向对象基础、测试分层（单元/集成/系统/验收）、自动化测试工具。

整体上这些笔记呈现出一条从**底层硬件与操作系统** -> **网络通信** -> **数据存储与中间件** -> **应用开发与部署** -> **质量保障**的完整技术栈学习路径。

---

## 各文档摘要

### Database

#### [[Database/MGR部署MySQL5.7|MGR部署MySQL5.7]]

MySQL Group Replication（MGR）高可用集群的完整部署指南。内容涵盖：
- MySQL 高可用方案对比：MGR（原生组复制）、MMM（多主复制管理）、MHA（主从故障自动转移）
- 三节点 CentOS 7.9 环境下 MGR 一主多从集群的逐步部署，包括 MySQL 5.7 安装、my.cnf 配置、组复制插件启用
- 结合 Keepalived + Nginx 实现读写分离和虚拟 IP 漂移的高可用架构

#### [[Database/MySQL入门|MySQL入门]]

MySQL 基础入门笔记，面向初学者：
- 关系型与非关系型数据库的概念对比，ACID 特性说明
- 数据库和数据表的创建、数据插入
- SQL 查询语法：WHERE 条件过滤（比较运算符、BETWEEN AND、IN、LIKE 通配符）、单表查询与多表查询基础

#### [[Database/源码安装redis-6.2.6-centos7|源码安装Redis-6.2.6-CentOS7]]

Redis 从源码编译到高可用部署的全面实践指南：
- Redis 典型使用场景：秒杀抢购、视频弹幕、游戏排行榜、社交 APP 最新评论
- CentOS 7 上源码编译安装 Redis 6.2.6 的详细步骤
- 配置文件参数说明（bind、daemonize、requirepass 等）
- 主从复制、Sentinel 哨兵模式、Redis Cluster 集群的部署方案

### Middlewares

#### [[Middlewares/Kafka|Kafka]]

Kafka 消息队列的核心概念笔记：
- 核心架构：Topic、Partition、Broker、Leader/Follower 副本机制
- Zookeeper 在集群协调中的角色，以及 Kafka 2.8.0 引入 KRaft 一致性算法替代 Zookeeper
- 适用场景：大数据量跨系统数据交互，与 Spark/Flink 组成通用大数据处理方案

#### [[Middlewares/RabbitMQ|RabbitMQ]]

当前仅保存了 Bilibili 视频学习链接，内容尚未展开。

#### [[Middlewares/RocketMQ|RocketMQ]]

当前仅保存了 Bilibili 视频学习链接，内容尚未展开。

### OS

#### [[OS/计算机组成原理|计算机组成原理]]

计算机体系结构基础知识：
- 计算机发展四阶段：电子管 -> 晶体管 -> 集成电路 -> 超大规模集成电路
- 冯诺依曼体系与现代计算机结构（以存储器为核心的改进）
- CPU 类型区分：x86/x64、AMD64、ARM 架构
- 计算机层次结构：硬件逻辑层 -> 微程序层 -> 操作系统层 -> 高级语言层
- 程序翻译 vs 解释：C/C++/Go（翻译）、Python/JS（解释）、Java（翻译+解释）

#### [[OS/OS-磁盘管理|OS-磁盘管理]]

操作系统磁盘管理与 I/O 专题：
- 磁盘物理结构：磁道、扇区、盘面、柱面，物理地址寻址方式
- 磁盘调度算法详解：FCFS、SSTF（最短寻道时间优先）、SCAN（电梯算法）、LOOK、C-SCAN、C-LOOK
- 减少延迟时间的优化方法

#### [[OS/OS|操作系统]]

操作系统核心概念全面笔记：
- OS 功能：CPU 管理、存储器管理、文件管理、设备管理
- 向上层提供的服务：GUI、命令接口（联机/脱机）、程序接口（系统调用）
- 库函数与系统调用的区别（用户态 vs 内核态）
- 四大特征：并发（Concurrence）、共享（Sharing，互斥共享与同时共享）、虚拟（时分/空分复用）、异步

### Networking

#### [[Networking/计算机网络基础|计算机网络基础]]

计算机网络体系化基础知识：
- 网络、互联网与因特网的关系；ISP 多层次结构
- 万维网 WWW 的诞生与 HTTP 技术
- 因特网组成：边缘部分（C/S、P2P 通信方式）与核心部分（路由器、交换机）
- 通信交换机制对比：电路交换、报文交换、分组交换（MTU 分割与重组）

#### [[Networking/HTTP基础|HTTP基础]]

基于《图解 HTTP》的协议学习笔记：
- HTTP 历史：1989 年诞生，WWW 三大核心技术（HTML/HTTP/URL）
- HTTP 1.0 非持久连接 vs HTTP 1.1 持久连接（Keep-Alive）与 Pipeline
- Cookie 工作原理（Set-Cookie、状态管理）
- HTTP 报文结构、内容编码（gzip/deflate）、分块传输、多部分对象集合、范围请求（断点续传）

### IaC

#### [[IaC/terraform-basics|Terraform基础]]

Terraform 入门与实践：
- Terraform 与 ARM Template/Bicep 的定位对比；基于 Go 语言、HCL 声明式语言
- 三阶段工作流：`terraform init`（下载 Provider）-> `plan`（计算差异）-> `apply`（执行变更）
- 核心文件结构：main.tf、variable.tf、terraform.tfvars、terraform.tfstate
- Azure 资源组创建示例（azurerm provider 配置、az login 认证流程）

#### [[IaC/terraform-docs|Terraform-docs]]

terraform-docs 文档自动生成工具：
- 用途：为 Terraform Module 自动生成 Markdown 格式的说明文档
- 安装方式（从 GitHub Release 下载）
- 配置模板详解：formatter、content 模板（Requirements/Usage/Resources/Inputs/Outputs）、output 注入模式

### Git

#### [[Git/git-learning|Git学习笔记]]

Git 版本控制基础：
- 版本控制分类：本地、集中式（SVN）、分布式（Git）
- Git 四层结构：工作目录 -> 暂存区 -> 本地仓库 -> 远程仓库
- 文件四种状态：Untracked -> Staged -> Unmodified -> Modified 的流转
- 基本工作流程：clone -> add -> commit -> push

#### [[Git/Picgo-github图床配置|PicGo-GitHub图床配置]]

利用 PicGo + GitHub 仓库实现 Markdown 图片持久化方案：
- 背景：解决 Typora 本地图片路径在换机器后失效的问题
- 三端配置：GitHub（创建公有仓库 + Access Token）、PicGo（github-plus 插件 + HTTP Server 端口）、Typora（图像上传配置）
- Obsidian 中使用 Image Auto Upload 插件实现同样功能
- 常见问题排查：repo 路径空格导致 404、时间戳命名避免文件名重复、修改 hosts 解决图片不显示

### C++

#### [[C++/C++LearningNotes|C++学习笔记]]

C++ 语言基础学习笔记：
- 命名空间 `std` 的作用
- 内存四区模型：程序代码区、全局数据区、栈区、堆区（new/delete 与 malloc/free）
- 变量存储类型：auto、register、static（静态局部/静态全局）、extern
- 指针与按址操作：地址与指针变量、取地址运算符 `&`、间接访问运算符 `*`、指向数组和字符串的指针

### SoftwareTesting

#### [[SoftwareTesting/软件工程基础|软件工程基础]]

软件工程核心概念笔记：
- 软件 = 程序 + 数据 + 文档；软件危机（1960s）催生软件工程学科
- 软件质量六大特性：功能性、可靠性、可使用性、效率、可维护性、可移植性
- 软件生存期三阶段：定义（需求分析）-> 开发（设计/编码/测试）-> 运维（DevOps）
- 生存期模型：瀑布模型、敏捷模型、极限编程
- 面向对象基础概念

#### [[SoftwareTesting/软件测试直播课笔记|软件测试直播课笔记]]

软件测试培训课程实录笔记：
- 软件研发过程：立项 -> 需求分析 -> 架构设计 -> 详细设计 -> 实现 -> 测试 -> 运维
- 测试分层：单元测试（白盒/代码审查）-> 集成测试（Smoke Test）-> 系统测试 -> 验收测试
- 开发模式对比：瀑布模型（重文档、不喜欢需求变更）vs 敏捷模型（Sprint/Story、快速迭代）
- 测试工具与环境：XAMPP 建站、Zentao 项目管理、JUnit、Selenium 自动化测试

---

## 涉及的概念与实体

### 数据库与存储
- [[KnowledgeBase/entities/MySQL|MySQL]] - 关系型数据库，涉及 SQL 语法、MGR 高可用部署
- [[KnowledgeBase/entities/Redis|Redis]] - 内存键值数据库，涉及源码安装、主从复制、Sentinel、Cluster
- [[KnowledgeBase/entities/InnoDB|InnoDB]] - MySQL 存储引擎，MGR 必须使用
- ACID 特性 - 事务的原子性、一致性、隔离性、持久性

### 消息队列中间件
- [[KnowledgeBase/entities/Kafka|Kafka]] - 分布式消息队列，Topic/Partition/Broker 架构
- [[KnowledgeBase/entities/RabbitMQ|RabbitMQ]] - 消息队列（待补充）
- [[KnowledgeBase/entities/RocketMQ|RocketMQ]] - 消息队列（待补充）
- [[KnowledgeBase/entities/Zookeeper|Zookeeper]] - 分布式协调服务，Kafka 集群管理

### 操作系统与硬件
- 冯诺依曼体系 - 现代计算机基础架构
- CPU 架构 - x86/x64/ARM 的区分与适用场景
- 磁盘调度算法 - FCFS、SSTF、SCAN、LOOK、C-SCAN、C-LOOK
- 进程管理 - 并发、共享、虚拟、异步四大特征

### 网络与协议
- [[KnowledgeBase/entities/TCP-IP|TCP/IP]] - 因特网核心协议族
- [[KnowledgeBase/entities/HTTP|HTTP]] - 超文本传输协议（1.0/1.1）
- OSI 模型 - 网络分层参考模型
- 分组交换 - 报文分割、路由转发、目的端重组

### 基础设施与工具
- [[KnowledgeBase/entities/Terraform|Terraform]] - HashiCorp 出品的 IaC 工具，HCL 声明式语言
- [[KnowledgeBase/entities/Azure|Azure]] - 云平台，Terraform azurerm Provider
- terraform-docs - Terraform Module 文档自动生成工具
- [[KnowledgeBase/entities/Git|Git]] - 分布式版本控制系统
- [[KnowledgeBase/entities/GitHub|GitHub]] - 代码托管平台，同时用作图床
- PicGo - Markdown 图片上传工具

### 编程语言
- [[KnowledgeBase/entities/CPP|C++]] - 系统级编程语言，指针与内存管理
- [[KnowledgeBase/entities/Java|Java]] - 编译+解释型语言，JVM 字节码
- [[KnowledgeBase/entities/Python|Python]] - 解释型语言

### 高可用技术
- [[KnowledgeBase/entities/Keepalived|Keepalived]] - 虚拟 IP 漂移，配合 MGR 实现高可用
- [[KnowledgeBase/entities/Nginx|Nginx]] - 反向代理/负载均衡，读写分离
- MHA / MMM - MySQL 高可用管理工具
- Redis Sentinel / Cluster - Redis 高可用方案

### 软件工程与测试
- 瀑布模型 / 敏捷模型 - 软件生存期模型
- Sprint / Story - 敏捷开发核心概念
- JUnit / Selenium - 自动化测试框架
- DevOps - 开发运维一体化

---

## 交叉主题发现

### 1. 高可用架构模式的一致性
数据库（MySQL MGR、Redis Sentinel/Cluster）和消息队列（Kafka 副本机制）都遵循相似的高可用设计模式：**多副本 + 自动故障转移 + Leader 选举**。MySQL MGR 使用组复制协议，Redis Sentinel 使用哨兵投票，Kafka 使用 ISR 副本同步机制。这些方案的核心思想是相通的。

### 2. 操作系统概念在中间件中的映射
操作系统中的并发/共享/调度概念直接映射到上层中间件：
- OS 的进程调度算法 <-> Kafka 的 Partition 分配策略
- OS 的磁盘调度算法（SCAN/C-SCAN）<-> 数据库的 I/O 优化
- OS 的内存管理（堆/栈）<-> C++ 的 new/delete 内存管理、Redis 的内存数据结构

### 3. 声明式 vs 命令式思想贯穿多个领域
- Terraform 的 HCL 是声明式语言（描述目标状态）
- SQL 也是声明式语言（描述查询意图而非过程）
- 敏捷开发中 Story 描述"做什么"而非"怎么做"
- 与之对应，C++ 是命令式编程、Shell 脚本是命令式运维

### 4. 网络分层模型在实际系统中的体现
网络基础中学习的 OSI/TCP-IP 分层模型在其他领域有直接应用：
- HTTP 协议（应用层）-> Nginx 反向代理（应用层/传输层）
- PicGo 作为 HTTP Server 监听端口上传图片（应用层协议实践）
- MySQL MGR 组通信使用专用端口（传输层）

### 5. 从开发到运维的全链路覆盖
软件测试笔记中描述的**立项 -> 开发 -> 测试 -> 运维**流程，在其他目录中都有对应的技术支撑：
- 开发阶段：C++/Java 编程、Git 版本控制
- 部署阶段：Terraform IaC 自动化部署、Redis/MySQL 集群搭建
- 测试阶段：JUnit 单元测试、Selenium 自动化测试
- 运维阶段：Keepalived/Nginx 高可用保障、Kafka 消息队列解耦

### 6. CentOS 7 作为统一实验环境
Database 和 OS 相关笔记中大量操作基于 CentOS 7.9 环境，包括 MySQL 5.7 安装、Redis 6.2.6 源码编译、yum 包管理等。这与 Linux 操作系统笔记中的理论知识形成了"理论 + 实践"的闭环。
