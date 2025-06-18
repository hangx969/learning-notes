# tomcat介绍

- Apache Tomcat 是一个开源的 Web 服务器和 Servlet 容器，它由 Apache 软件基金会开发和维护。Tomcat 的主要功能是执行 Java Servlet 和 JavaServer Pages（JSP）技术，允许开发者创建动态的 Web 应用程序。

## 组件

Tomcat 主要由以下几个组件构成：

- Servlet：Servlet 是 Java 编写的程序，运行在服务器上，处理用户请求并生成响应。它们可以与数据库交互，生成动态内容。
- JSP：JavaServer Pages 是一种基于 Java 的模板引擎，允许开发者在 HTML 中嵌入Java 代码，简化动态网页的创建。
- Catalina：这是 Tomcat 的核心组件，负责处理 HTTP 请求并管理 Servlet 的生命周期。
- Coyote：这是 Tomcat 的连接器，负责处理与客户端（如浏览器）之间的 HTTP 通信。
- Host：Tomcat 可以托管多个 Web 应用程序，每个应用程序都被称为一个“虚拟主机”，Tomcat 使用 Host 来管理这些应用程序。

## 功能

Tomcat 提供了以下主要功能：

- 支持 Java EE：Tomcat 实现了 Java EE 的 Servlet 和 JSP 规范，使得开发者可以使用 Java 编写 Web 应用程序。
- 高效的处理请求：Tomcat 能够处理大量的并发请求，适合大规模的 Web 应用。
- 可扩展性：Tomcat 允许开发者通过添加自定义的 Servlet 和 JSP 来扩展其功能。
- 易于部署：开发者可以简单地将 WAR 文件（Web 应用归档）部署到 Tomcat 中，Tomcat 会自动解压和配置应用。

## 工作原理

Tomcat 的工作流程大致如下：
1. 接收请求：Tomcat 通过 Coyote 接收来自客户端（如浏览器）的 HTTP 请求。
2. 解析请求：请求被传递给 Catalina，Catalina 根据请求的 URL 确定需要调用的Servlet。
3. 执行 Servlet：对应的 Servlet 处理请求，可能会访问数据库并生成动态内容。
4. 生成响应：Servlet 生成的内容作为 HTTP 响应返回给客户端。
5. 发送响应：Tomcat 通过 Coyote 将响应发送回客户端，完成请求处理。

## 命令

Tomcat 命令

- 启动 Tomcat: `catalina.sh start`
- 停止 Tomcat: `catalina.sh stop`
- 重启 Tomcat: `catalina.sh restart`
- 查看 tomcat 状态：`ps -ef |grep tomcat`

## 安装

1. Java 安装

  打开终端并运行以下命令检查是否已安装 Java：`java -version`

  如果未安装 Java，可以使用以下命令安装 OpenJDK：

  ```sh
  yum install java-11-openjdk-devel -y
  ```

  安装完成后，重新运行 `java -version` 以确认安装。

2. 下载安装 Tomcat

  访问 [Apache Tomcat 官网](https://tomcat.apache.org/)以获取最新版本的 Tomcat 下载链接。

  ```sh
  mv apache-tomcat-10.1.30.tar.gz /opt
  cd /opt
  tar -zxvf apache-tomcat-10.1.30.tar.gz
  mv apache-tomcat-10.1.30 tomcat
  tee -a vim /etc/profile <<'EOF'
  export CATALINA_HOME=/opt/tomcat
  export PATH=$PATH:$CATALINA_HOME/bin
  EOF
  source /etc/profile
  cd /opt/tomcat/bin
  ./catalina.sh start
  # 检查是否启动tomcat
  tail -f /opt/tomcat/logs/catalina.out
  # 可以访问安装机器的8080端口查看tomcat主页
  ```

> rockylinux上启动不了：
>
> ~~~sh
> [root@rocky-1 bin]# tail -f /opt/tomcat/logs/catalina.out
> Unrecognized option: --enable-native-access=ALL-UNNAMED
> Error: Could not create the Java Virtual Machine.
> Error: A fatal exception has occurred. Program will exit.
> ~~~

# 基于subprocess启动停止tomcat

~~~python
~~~

