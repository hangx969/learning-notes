# 背景

## KubeBlocks

- KubeBlocks 是一个可以管理多种数据库和有状态中间件的 K8s operator，支持管理 MySQL、PostgreSQL、Redis、MongoDB、Kafka、ClickHouse、Elasticsearch 等 30 余种数据库。其原理是定义一组通用和抽象的 API（CRDs）来描述各种引擎的共同属性，在其之上，数据库厂商和开发者可以通过插件来描述不同引擎的差异。

# 安装kbcli和KubeBlocks

> - 检查[环境要求](https://kubeblocks.io/docs/release-0.8/api_docs/installation/install-with-kbcli/install-kubeblocks-with-kbcli#environment-preparation)
> - [安装kbcli](https://kubeblocks.io/docs/preview/user_docs/installation/install-with-kbcli/install-kbcli)
> - [安装KubeBlocks](https://kubeblocks.io/docs/preview/user_docs/installation/install-with-kbcli/install-kubeblocks-with-kbcli)

1. 安装 kbcli。

   ```sh
   curl -fsSL https://kubeblocks.io/installer/install_cli.sh | bash
   ```

2. 安装 KubeBlocks。

   ```sh
   kbcli kubeblocks install
   ```

3. 检查 KubeBlocks 是否安装成功。

   ```sh
   kbcli kubeblocks status
   ```

4. 在 KubeBlocks 中开启 PostgreSQL 和 Redis 引擎。这两个引擎默认开启。您可以执行以下命令，检查引擎启用状态。如果引擎未启用，您可以参考官方文档[启用引擎](https://kubeblocks.io/docs/release-0.8/api_docs/overview/supported-addons#use-addons)。

   ```sh
   kbcli addon list
   ```



Harbor 架构图: *https://goharbor.io/docs/2.1.0/install-config/harbor-ha-helm/#architecture*

Harbor 环境要求: *https://goharbor.io/docs/2.11.0/install-config/installation-prereqs/*

