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
- [[KnowledgeBase/concepts/Python运维开发|Python运维开发]]
- [[KnowledgeBase/concepts/自动化运维|自动化运维]]

---

## 📖 推荐阅读顺序

### 第一阶段：语言基础
1. [python-basics](../../Python/python-基础/python-basics.md) — 数据类型与语法（1598 行）
2. [python-function](../../Python/python-基础/python-function.md) — 函数与闭包
3. [python-OOP](../../Python/python-基础/python-OOP.md) — 面向对象
4. [python-exception-handling](../../Python/python-基础/python-exception-handling.md) — 异常处理
5. [python-QA](../../Python/python-基础/python-QA.md) — 知识总结

### 第二阶段：运维核心（重点）
6. [python-Linux-operation](../../Python/python-运维开发/python-Linux-operation.md) — ==Linux 运维核心模块==（1737 行，subprocess/psutil/paramiko）
7. [python-fabric高级用法](../../Python/python-运维开发/python-fabric高级用法.md) — 批量运维
8. [python-kubernetes-module](../../Python/python-运维开发/python-kubernetes-module.md) — K8s API 自动化
9. [python-mysql](../../Python/python-运维开发/python-mysql.md) — MySQL 自动化
10. [python-postgresql](../../Python/python-运维开发/python-postgresql.md) — PostgreSQL 自动化
11. [python-elasticsearch](../../Python/python-运维开发/python-elasticsearch.md) — ES 运维
12. [python-nginx](../../Python/python-运维开发/python-nginx.md) — Nginx 自动化
13. [python-tomcat](../../Python/python-运维开发/python-tomcat.md) — Tomcat 自动化

### 第三阶段：网络编程
14. [python-request-module](../../Python/python-网络编程-前端/python-request-module.md) — HTTP 请求
15. [python-socket-module](../../Python/python-网络编程-前端/python-socket-module.md) — Socket 编程
16. [python-爬虫](../../Python/python-网络编程-前端/python-爬虫.md) — 爬虫
17. [python-Web框架Flask](../../Python/python-网络编程-前端/python-Web框架Flask.md) — Flask
18. [python-Web框架Django](../../Python/python-网络编程-前端/python-Web框架Django.md) — Django

### 第四阶段：数据与工具
19. [python-处理excel-word](../../Python/python-数据分析-AI大模型/python-处理excel-word.md) — Excel/Word
20. [python-机器学习与预测](../../Python/python-数据分析-AI大模型/python-机器学习与预测.md) — 机器学习
21. [实验室电池参数一键统计工具开发](../../Python/电池参数提取统计工具开发/实验室电池参数一键统计工具开发.md) — 实际项目

---

## 📂 分类索引

### 语言基础（8 篇）
| 文章 | 主题 |
|------|------|
| [python-basics](../../Python/python-基础/python-basics.md) | 数据类型、字符串、文件IO、正则 |
| [python-function](../../Python/python-基础/python-function.md) | 函数、闭包、装饰器 |
| [python-OOP](../../Python/python-基础/python-OOP.md) | 类、继承、多态 |
| [python-exception-handling](../../Python/python-基础/python-exception-handling.md) | try/except、自定义异常 |
| [python-QA](../../Python/python-基础/python-QA.md) | 面试题与常见问题 |
| [python包管理工具-uv](../../Python/python-基础/python包管理工具-uv.md) | uv 包管理器 |
| [rockylinux配置python开发环境](../../Python/python-基础/rockylinux配置python开发环境.md) | RockyLinux 环境 |
| [windows配置python开发环境](../../Python/python-基础/windows配置python开发环境.md) | Windows 环境 |

### 运维开发（10 篇）⭐ 核心
| 文章 | 主题 | 关键模块 |
|------|------|----------|
| [python-Linux-operation](../../Python/python-运维开发/python-Linux-operation.md) | Linux 运维 | subprocess, psutil, paramiko, fabric, json, yaml |
| [python-kubernetes-module](../../Python/python-运维开发/python-kubernetes-module.md) | K8s 自动化 | kubernetes client |
| [python-mysql](../../Python/python-运维开发/python-mysql.md) | MySQL | pymysql, SQLAlchemy |
| [python-postgresql](../../Python/python-运维开发/python-postgresql.md) | PostgreSQL | psycopg2 |
| [python-elasticsearch](../../Python/python-运维开发/python-elasticsearch.md) | ES 运维 | elasticsearch-py |
| [python-nginx](../../Python/python-运维开发/python-nginx.md) | Nginx | 配置生成、自动化 |
| [python-tomcat](../../Python/python-运维开发/python-tomcat.md) | Tomcat | 部署自动化 |
| [python-fabric高级用法](../../Python/python-运维开发/python-fabric高级用法.md) | 批量运维 | fabric2 |
| [python-GUI-tkinter](../../Python/python-运维开发/python-GUI-tkinter.md) | GUI 工具 | tkinter |
| [python-游戏开发](../../Python/python-运维开发/python-游戏开发.md) | 游戏开发 | pygame |

### 网络编程与 Web（6 篇）
| 文章 | 主题 |
|------|------|
| [python-Web开发-HTML-CSS-JS](../../Python/python-网络编程-前端/python-Web开发-HTML-CSS-JS.md) | Web 前端基础 |
| [python-Web框架Django](../../Python/python-网络编程-前端/python-Web框架Django.md) | Django |
| [python-Web框架Flask](../../Python/python-网络编程-前端/python-Web框架Flask.md) | Flask |
| [python-request-module](../../Python/python-网络编程-前端/python-request-module.md) | requests |
| [python-socket-module](../../Python/python-网络编程-前端/python-socket-module.md) | socket |
| [python-爬虫](../../Python/python-网络编程-前端/python-爬虫.md) | 爬虫 |

### 数据分析（2 篇） + 实际项目（1 篇）
| 文章 | 主题 |
|------|------|
| [python-处理excel-word](../../Python/python-数据分析-AI大模型/python-处理excel-word.md) | openpyxl, python-docx |
| [python-机器学习与预测](../../Python/python-数据分析-AI大模型/python-机器学习与预测.md) | sklearn, pandas |
| [实验室电池参数一键统计工具开发](../../Python/电池参数提取统计工具开发/实验室电池参数一键统计工具开发.md) | 完整项目案例 |

---

## 🔗 与其他领域的连接

- **K8s 方向：** [Python调用k8s-api实现资源管理](../../Docker-Kubernetes/k8s-basic-resources/Python调用k8s-api实现资源管理.md) — K8s API 调用
- **数据库方向：** [MySQL入门](../../Database/MySQL入门.md)、[源码安装redis-6.2.6-centos7](../../Database/源码安装redis-6.2.6-centos7.md) — 数据库知识基础
- **Linux 方向：** [shell-scripts](../../Linux-Shell/shell-scripts.md) — Shell vs Python 运维对比
- **CI/CD 方向：** [发布go-python-java代码到K8S环境](../../Docker-Kubernetes/k8s-CICD/发布go-python-java代码到K8S环境.md) — 代码发布

---

## 🛠️ 相关工具
- [Python运维开发](../concepts/Python运维开发.md)
- [Kubernetes](../concepts/Kubernetes.md)
- [自动化运维](../concepts/自动化运维.md)
