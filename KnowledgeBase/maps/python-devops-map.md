---
title: Python 运维开发专题地图
tags:
  - knowledgebase/map
  - knowledgebase/python
aliases:
  - Python DevOps Map
date: 2026-04-16
---

# 🐍 Python 运维开发专题地图

> [!info] 专题范围
> 覆盖 Python/ 目录下 ==27 篇文档==，聚焦 Python 在运维自动化、Web 开发和数据分析中的应用。

---

## 核心概念
- [[KnowledgeBase/concepts/Python运维开发]]
- [[KnowledgeBase/concepts/自动化运维]]

---

## 📖 推荐阅读顺序

### 第一阶段：语言基础
1. [[Python/python-基础/python-basics]] — 数据类型与语法（1598 行）
2. [[Python/python-基础/python-function]] — 函数与闭包
3. [[Python/python-基础/python-OOP]] — 面向对象
4. [[Python/python-基础/python-exception-handling]] — 异常处理
5. [[Python/python-基础/python-QA]] — 知识总结

### 第二阶段：运维核心（重点）
6. [[Python/python-运维开发/python-Linux-operation]] — ==Linux 运维核心模块==（1737 行，subprocess/psutil/paramiko）
7. [[Python/python-运维开发/python-fabric高级用法]] — 批量运维
8. [[Python/python-运维开发/python-kubernetes-module]] — K8s API 自动化
9. [[Python/python-运维开发/python-mysql]] — MySQL 自动化
10. [[Python/python-运维开发/python-postgresql]] — PostgreSQL 自动化
11. [[Python/python-运维开发/python-elasticsearch]] — ES 运维
12. [[Python/python-运维开发/python-nginx]] — Nginx 自动化
13. [[Python/python-运维开发/python-tomcat]] — Tomcat 自动化

### 第三阶段：网络编程
14. [[Python/python-网络编程-前端/python-request-module]] — HTTP 请求
15. [[Python/python-网络编程-前端/python-socket-module]] — Socket 编程
16. [[Python/python-网络编程-前端/python-爬虫]] — 爬虫
17. [[Python/python-网络编程-前端/python-Web框架Flask]] — Flask
18. [[Python/python-网络编程-前端/python-Web框架Django]] — Django

### 第四阶段：数据与工具
19. [[Python/python-数据分析-AI大模型/python-处理excel-word]] — Excel/Word
20. [[Python/python-数据分析-AI大模型/python-机器学习与预测]] — 机器学习
21. [[Python/电池参数提取统计工具开发/实验室电池参数一键统计工具开发]] — 实际项目

---

## 📂 分类索引

### 语言基础（8 篇）
| 文章 | 主题 |
|------|------|
| [[Python/python-基础/python-basics]] | 数据类型、字符串、文件IO、正则 |
| [[Python/python-基础/python-function]] | 函数、闭包、装饰器 |
| [[Python/python-基础/python-OOP]] | 类、继承、多态 |
| [[Python/python-基础/python-exception-handling]] | try/except、自定义异常 |
| [[Python/python-基础/python-QA]] | 面试题与常见问题 |
| [[Python/python-基础/python包管理工具-uv]] | uv 包管理器 |
| [[Python/python-基础/rockylinux配置python开发环境]] | RockyLinux 环境 |
| [[Python/python-基础/windows配置python开发环境]] | Windows 环境 |

### 运维开发（10 篇）⭐ 核心
| 文章 | 主题 | 关键模块 |
|------|------|----------|
| [[Python/python-运维开发/python-Linux-operation]] | Linux 运维 | subprocess, psutil, paramiko, fabric, json, yaml |
| [[Python/python-运维开发/python-kubernetes-module]] | K8s 自动化 | kubernetes client |
| [[Python/python-运维开发/python-mysql]] | MySQL | pymysql, SQLAlchemy |
| [[Python/python-运维开发/python-postgresql]] | PostgreSQL | psycopg2 |
| [[Python/python-运维开发/python-elasticsearch]] | ES 运维 | elasticsearch-py |
| [[Python/python-运维开发/python-nginx]] | Nginx | 配置生成、自动化 |
| [[Python/python-运维开发/python-tomcat]] | Tomcat | 部署自动化 |
| [[Python/python-运维开发/python-fabric高级用法]] | 批量运维 | fabric2 |
| [[Python/python-运维开发/python-GUI-tkinter]] | GUI 工具 | tkinter |
| [[Python/python-运维开发/python-游戏开发]] | 游戏开发 | pygame |

### 网络编程与 Web（6 篇）
| 文章 | 主题 |
|------|------|
| [[Python/python-网络编程-前端/python-Web开发-HTML-CSS-JS]] | Web 前端基础 |
| [[Python/python-网络编程-前端/python-Web框架Django]] | Django |
| [[Python/python-网络编程-前端/python-Web框架Flask]] | Flask |
| [[Python/python-网络编程-前端/python-request-module]] | requests |
| [[Python/python-网络编程-前端/python-socket-module]] | socket |
| [[Python/python-网络编程-前端/python-爬虫]] | 爬虫 |

### 数据分析（2 篇） + 实际项目（1 篇）
| 文章 | 主题 |
|------|------|
| [[Python/python-数据分析-AI大模型/python-处理excel-word]] | openpyxl, python-docx |
| [[Python/python-数据分析-AI大模型/python-机器学习与预测]] | sklearn, pandas |
| [[Python/电池参数提取统计工具开发/实验室电池参数一键统计工具开发]] | 完整项目案例 |

---

## 🔗 与其他领域的连接

- **K8s 方向：** [[Docker-Kubernetes/k8s-basic-resources/Python调用k8s-api实现资源管理]] — K8s API 调用
- **数据库方向：** [[Database/MySQL入门]]、[[Database/源码安装redis-6.2.6-centos7]] — 数据库知识基础
- **Linux 方向：** [[Linux-Shell/shell-scripts]] — Shell vs Python 运维对比
- **CI/CD 方向：** [[Docker-Kubernetes/k8s-CICD/发布go-python-java代码到K8S环境]] — 代码发布

---

## 🛠️ 相关工具
- [[KnowledgeBase/concepts/Python运维开发]]
- [[KnowledgeBase/concepts/Kubernetes]]
- [[KnowledgeBase/concepts/自动化运维]]
