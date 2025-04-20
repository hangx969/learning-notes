# k9s

- kubectl可视化插件：https://github.com/derailed/k9s
- 安装指南：https://k9scli.io/topics/install/

# 安装

1. 方法1：via [webi](https://webinstall.dev/) (在现在ubuntu workstation上使用的方法)

   ~~~sh
   curl -sS https://webinstall.dev/k9s | bash
   ~~~

2. 方法2：在ubuntu上

   ~~~sh
   wget https://github.com/derailed/k9s/releases/download/v0.40.5/k9s_linux_amd64.deb && apt install ./k9s_linux_amd64.deb && rm k9s_linux_amd64.deb
   ~~~

3. 方法3：via snap

   ~~~sh
   snap install k9s --devmode
   ~~~

## 使用

- vim风格，在主页面上
  - ：来输入资源类型
  - /来输入filter


- 常用命令

  ~~~sh
  # List all available CLI options
  $ k9s help
  
  # To get info about K9s runtime (logs, configs, etc..)
  $ k9s info
  
  # To run K9s in a given namespace
  $ k9s -n mycoolns
  
  # Start K9s in an existing KubeConfig context
  $ k9s --context coolCtx
  
  # Start K9s in readonly mode - with all modification commands disabled
  $ k9s --readonly
  ~~~

  

## 快捷键

| 操作                                                         | 命令                          | 备注                                                         |
| ------------------------------------------------------------ | ----------------------------- | ------------------------------------------------------------ |
| 显示活跃的键盘助记符和帮助                                   | `?`                           |                                                              |
| 显示集群上所有可用的别名和资源                               | `ctrl-a` or `:alias`          |                                                              |
| 退出 K9s                                                     | `:q`, `ctrl-c`                |                                                              |
| 查看pod                                                      | `:`po⏎                        | 接受单数，复数，短名或别名如 `pod` 或 `pods`                 |
| 查看给定名称空间中的资源                                     | `:`alias namespace⏎           |                                                              |
| 过滤字段                                                     | `/`filter⏎                    | 支持 Regex2，如 ` fred                                       |
| 反向正则表达式过滤                                           | `/`! filter⏎                  | 保留所有 *不匹配* 的东西。日志未实现。                       |
| 按标签过滤资源视图                                           | `/`-l label-selector⏎         |                                                              |
| 模糊查找给定的资源                                           | `/`-f filter⏎                 |                                                              |
| 退出视图 / 命令 / 过滤模式                                   | `<esc>`                       |                                                              |
| 键映射来描述(describe)，查看(view)，编辑(edit)，查看日志(logs)，… | `d`,`v`, `e`,`l`,…            |                                                              |
| 查看并切换到另一个 Kubernetes 上下文                         | `:`ctx⏎                       |                                                              |
| 查看并切换到另一个 Kubernetes 上下文                         | `:`ctx context-name⏎          |                                                              |
| 查看namespace                                                | `:`ns⏎                        |                                                              |
| 查看所有已保存的资源                                         | `:`screendump or sd⏎          |                                                              |
| 要删除资源 (按`TAB`并输入`Enter`)                            | `ctrl-d`                      |                                                              |
| 杀死一个资源 (没有确认对话框!)                               | `ctrl-k`                      |                                                              |
| 切换宽列                                                     | `ctrl-w`                      | 等同于 `kubectl ... -o wide`                                 |
| 切换错误状态                                                 | `ctrl-z`                      | 查看有错误的资源                                             |
| 运行 pulses（脉冲）视图                                      | `:`pulses or pu⏎              |                                                              |
| 运行 XRay视图                                                | `:`xray RESOURCE [NAMESPACE]⏎ | 资源可以是以下之一：po, svc, dp, rs, sts, ds, NAMESPACE 参数可选 |
| 运行 Popeye（评估跑分） 视图                                 | `:`popeye or pop⏎             | 参阅 [https://popeyecli.io](https://popeyecli.io/)           |

## 过滤功能

- 它的过滤功能非常强大，使得你可以非常快速的定位资源，比如我想要看 traefik 的所有 CRD，操作如下：

  ~~~sh
  ctrl+a
  /traefik
  ~~~

## Pulse

- 进入监控模式，不过需要metrics-server在集群内运行

## Xray

- XRay 会提供以某个 Kubernetes 资源为维度的关联关系，像 X 光一样，透射到资源的内部。比如查看deploy资源的关联关系：

  ~~~sh
  :xray deploy
  ~~~

## popeye

> [Popeye](https://popeyecli.io/) 是 K9s 作者开发的另一个 K8s 命令行工具，现已被集成进 K9s，它可以实时扫描你的集群，并报告潜在的问题，比如：引用完整性、配置错误、资源使用等。

- 通过 `:popeye` 命令可以进入 Popeye 的总览视图，然后可以通过在给定的资源条目上按 `Enter` 键来查看更为详细的检测报告。

- Popeye 还支持一个配置文件，即 `spinach.yml`，该文件提供了自定义扫描资源的内容，并根据自己的策略设置不同的严重程度。

- 请阅读 [Popeye 文档](https://popeyecli.io/#the-spinachyaml-configuration)，了解如何自定义报告。`spinach.yml` 文件将从 K9s 的主目录`$HOME/.k9s/MY_CLUSTER_CONTEXT_NAME_spinach.yml` 中读取。

## k9s插件功能

K9s 允许你通过 [插件机制](https://github.com/derailed/k9s#plugins) 定义自己的集群命令来扩展你的命令行和工具。K9s 会查看 `$HOME/.k9s/plugin.yml` 来定位所有可用的插件。一个插件的定义如下：

- `shortCut` 快捷键选项代表用户键入激活插件的组合键。
- `confirm` 确认选项（启用时）让你看到将要执行的命令，并给你一个确认或阻止执行的选项。
- `description` 说明将被打印在 K9s 菜单中的快捷方式旁边。
- `scopes` 作用域为与插件相关联的视图定义了资源名称/简称的集合。你可以指定所有，为所有视图提供这个快捷方式。 
- `command` 代表插件在激活时运行的临时命令。 
- `background` 指定命令是否在后台运行。
- `args` 指定适用于上述命令的各种参数。

K9s 同时提供了额外的环境变量，供你自定义插件的参数。目前，可用的环境变量如下：

- `$NAMESPACE`：选定的资源命名空间 
- `$NAME`：所选资源名称 
- `$CONTAINER` ：当前容器（如果适用）
- `$FILTER`：当前的过滤器（如果有）
- `$KUBECONFIG`：KubeConfig 文件的位置 
- `$CLUSTER`：当前的集群名称 
- `$CONTEXT`：当前的上下文名称 
- `$USER`：当前用户 
- `$GROUPS`：当前的用户组 
- `$POD`：容器视图中的 Pod 

# stern

- 查看pod log的插件：https://github.com/stern/stern#installation

## 安装

If you use [Krew](https://krew.sigs.k8s.io/) which is the package manager for kubectl plugins, you can install like this:

```sh
kubectl krew install stern
```

## 使用

~~~sh
实时查看当前 Namespace 中所有 Pod 中所有容器的日志
$ stern  .

实时查看 Pod 中指定容器的日志
$ stern envvars --container gateway

实时查看指定命名空间中除指定容器外的所有容器的日志
$ stern -n staging --exclude-container istio-proxy .

实时查看指定时间范围内容器的日志，下面的例子表示是 15 分钟内
$ stern auth -t --since 15m

实时查看指定命名空间中容器的日志
$ stern kubernetes-dashboard --namespace kube-system

实时查看所有命名空间中符合指定标签容器的日志
$ stern --all-namespaces -l run=nginx
~~~

## k9s通过plugin与stern集成

[Stern](https://github.com/wercker/stern) 是一款社区知名的 K8s 集群服务日志查询工具，虽然 k9s 已然集成了部分 Stern 的功能，但操作不太直接也无法连接管道操作（ `|` ），我们可以利用插件创建一个可以查询当前命名空间下多个 Pod 的快捷命令。

```yaml
tee -a $HOME/.k9s/plugin.yml <<'EOF'
plugin:
  stern:
    shortCut: Ctrl-L
    confirm: false
    description: "Logs (Stern)"
    scopes:
      - pods
    command: /usr/local/bin/stern # NOTE! Look for the command at this location.
    background: false
    args:
     - --tail
     - 100
     - $FILTER      # NOTE! Pulls the filter out of the pod view.
     - -n
     - $NAMESPACE   # Use current namespace
     - --context
     - $CONTEXT     # Use current k8s context
EOF
```
