# 介绍

## 优点

Lens是一款kubectl IDE工具：

💡 **移除复杂性**：不需要学习 kubectl 命令就可以探索和导航 Kubernetes 集群。对于刚起步的开发者来说是非常棒的。

👁️ **实时可观察性**：实时查看实时统计、事件、日志流。没有转圈圈的加载，刷新或等待屏幕更新。

🔨 **定位和调试**：在仪表板上查看错误和警告，然后单击查看详细信息。再次单击以查看日志或获取命令行。

💻️ **在你的个人电脑上运行**：MacOS, Windows 和 Linux 上的独立应用程序。1 分钟安装。不需要在集群中安装任何东西。

💚 **开源免费**：Lens 基于开源平台，拥有活跃的社区，并得到 Kubernetes 和云原生生态系统先锋的支持。

⎈ **可和任何 Kubernetes 一起工作**：使用 EKS, AKS, GKE, Minikube, Rancher, k0s, k3s, OpenShift…？他们所有都可以正常运行。只需为您想要使用的集群导入 kubeconfigs。

## 功能

- Lens 有一个 **统一的目录（Catalog）**。将所有集群、服务、工作负载、工具、自动化和相关资源集中在一起，以便轻松访问。而且在 Catalog 上，可以很方便进行 **浏览和组织**。使用搜索、过滤、分类和标签来访问你需要工作的资源比以往任何时候都更容易。

- Lens 的特色是左边有一列，叫做：**Hotbar**。就是主导航，允许用户在桌面应用程序中构建适合自己的「工作流」和「自动化」。用户可以通过分配不同的标签、颜色和图标来自定义 Hotbar 中的项目，以方便回忆。

- Lens **内置的可视化**。Lens 与 Prometheus 集成，可以通过总容量、实际使用、请求和限制可视化和查看资源使用指标（包括 CPU、内存、网络和磁盘）的趋势。为每个 k8s 资源自动生成详细的可视化。

- **智能终端** 功能。Lens 智能终端自带 kubectl 和 helm，自动同步 kubectl 的版本，以匹配当前选择的 K8S 集群 API 版本。Lens 会自动分配 kubeconfig 上下文来匹配当前选择的 K8s 集群。

- 自带全量 K8S 资源模板，而且是有丰富信息的模板，直接在模板上照猫画虎就可完成各类资源的创建。
- **Helm Chart**。Lens 自带 Helm Chart 管理，允许发现和快速部署数以千计的公开可用的 Helm Chart 和管理您自己的存储库。探索已安装的 Helm Chart ，只需一次点击即可修订和升级。（这个功能不如helm dashboard做的好）

## 插件

按快捷键ctrl+shift+E进入extensions界面，可以输入extension的name或者URL来安装

### lens-certificate-info

查看含有证书信息的 Secret。

### lens-debug-tools

- 安装说明：https://github.com/pashevskii/debug-pods-lens-extension

- 可以在想要调试的 Pod 里插入带有丰富工具集的 Sidecar（为了追求 Size，一般镜像都是非常精简，导致常用命令缺失，调试困难），方便调试。还可以配置调试用的镜像，还贴心的给了 3 个推荐：

| Name                     | Description   | Link                                              |
| ------------------------ | ------------- | ------------------------------------------------- |
| busybox                  | Default value | https://hub.docker.com/_/busybox                  |
| markeijsermans/debug     |               | https://hub.docker.com/r/markeijsermans/debug     |
| praqma/network-multitool |               | https://hub.docker.com/r/praqma/network-multitool |

- 安装完成后 Pod 页面会多一个按钮：Run As Debug Pod，有两种模式：

  - 一种是「Run as debug pod」，就是在同一台 Node 上启动一个新 pod，可以用来分析调试与 Node 有关的问题。自动执行的命令示例如下：

    ~~~sh
    kubectl run loki-promtail-5d5h8-debug -n loki-stack -it --image=busybox --restart=Never  --attach  --overrides='{ \"spec\": { \"nodeName\": \"izuf656om146vu1n6pd6lpz\" } }' --labels=createdBy=lens-debug-extension --rm
    ~~~
    
  - 另一种是「Run as emepheral container」，需要启用 K8S 1.16 的新功能才能使用。直接是在要调试的 Pod 里启动一个 Debug Sidecar，就可以分析调试与 Node、Pod 有关的问题。自动执行的命令示例如下：
  
    ~~~sh
    kubectl debug -i -t -n loki-stack loki-promtail-5d5h8 --image=busybox --target promtail --attach
    ~~~

### @nevalla/kube-resource-map

- 查看资源拓扑图

# 安装

- Ubuntu系统安装Lens:[官网安装指南](https://docs.k8slens.dev/getting-started/install-lens/#install-lens-desktop-from-the-apt-repository)

- 安装完成打开desktop app后会提示注册Lens账号，注册一个即可，可以使用github账号来oauth登录。