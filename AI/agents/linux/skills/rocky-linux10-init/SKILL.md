---
name: rocky-linux10-init
description: Initialize Rocky Linux 10 machines when the user mentions 初始化 Linux 机器、初始化 Rocky Linux、节点初始化、主机初始化、批量初始化主机、做 K8s 前的 Linux 初始化、给 Linux 节点做初始化，尤其是需要基于 Rocky Linux 10 按固定文档流程完成 SSH 密钥准备、免密登录配置、网络/内核/Swap/IPVS/时间同步等系统初始化时。 Use this skill aggressively for Rocky Linux 10 host initialization tasks, and do not improvise outside the documented workflow.
---

# Rocky Linux 10 初始化 Skill

使用这个 skill 时，目标非常明确：

- 初始化 **Rocky Linux 10** 主机
- 严格按既定流程执行
- 不增加额外初始化步骤
- 不增加额外命令
- 不创建额外的重复脚本
- 只在必要的可变参数上做替换

如果用户要做的是 Rocky Linux 10 的系统初始化，并且目标是为后续容器或 K8s 安装打基础，就直接使用这个 skill。

## 作用范围

只处理：

- Rocky Linux 10 主机初始化
- SSH key 检查与生成
- 远程主机免密登录配置
- 按固定初始化流程执行系统配置

不处理：

- Windows
- 非 Linux 环境
- 与本初始化流程无关的额外运维动作
- 文档之外的新增步骤

## 严格执行规则

### 1. 固定流程，不自由发挥

必须严格按照本 skill 和 `scripts/rocky_linux10_init.sh` 定义的流程执行。

禁止：

- 擅自增加新的初始化步骤
- 擅自增加新的初始化命令
- 擅自创建新的重复脚本
- 擅自修改脚本中的步骤顺序
- 擅自用示例 IP、示例主机名、示例网卡名、示例路径覆盖真实环境

### 2. 可选步骤默认跳过

以下可选内容默认先跳过，不执行：

- 释放 swap LV 空间并扩容 root / home 分区
- 系统内核优化（`k8s_better.conf` 那组可选 sysctl）

最后汇报时只需要提醒用户：

- 这些步骤本次已跳过
- 如需执行，可在下一轮明确要求

### 3. 软件包版本默认最新版

如果用户没有指定软件包版本：

- 默认安装最新版

不要自行锁版本。

### 4. 缺少关键变量时必须暂停

以下变量每台机器都可能不同：

- IP / CIDR
- 网关
- DNS
- 主机名
- 网卡名称
- `/etc/hosts` 映射内容
- 任何涉及本地路径、远程路径、仓库路径的主机相关变量

如果用户没有给出，并且你也无法通过命令查询出来，就必须暂停并向用户询问。

不要使用任何示例值直接代替真实值。

## 主机列表输入格式

用户给的主机列表没有固定格式，你需要先把它转换成统一结构，再执行。

在和用户沟通时，要求或示例化为下面几种格式之一即可：

### 推荐格式 1

```text
192.168.1.10 root password123
192.168.1.11 root password456
```

### 推荐格式 2

```text
192.168.1.10|root|password123
192.168.1.11|root|password456
```

### 推荐格式 3

```text
192.168.1.10 username=root password=password123
192.168.1.11 username=root password=password456
```

将其统一转换成你自己的标准结构即可，但不需要额外写解析脚本；直接在执行时做转换。

如果用户没有提供用户名和密码，则按下面的 root 探测规则执行。

## 执行顺序

按下面顺序执行，不要变更。

### 第一步：检查本机 SSH key

先检查当前控制机是否已经有 SSH key。

如果已经存在任意常见公钥文件，则忽略：

```bash
find ~/.ssh -maxdepth 1 -type f \( -name 'id_*.pub' -o -name '*.pub' \) | grep -q .
```

如果没有，则直接生成：

```bash
ssh-keygen -t rsa -C "1003665363@qq.com" -f ~/.ssh/id_rsa -N ""
```

### 第二步：处理远程主机免密登录

#### 情况 A：用户提供了用户名和密码

对每台主机执行免密登录配置。

优先使用现成工具完成，例如已有的 `ssh-copy-id` 配合可用的密码输入方式。

这里不要额外写循环脚本；循环逻辑直接写在执行流程里。

#### 情况 B：用户没有提供用户名密码

必须先直接探测是否可以通过 root 登录远程主机。

这个探测必须直接写在 skill 的执行流程中，不要写到任何脚本里。

对每台主机执行：

```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 -o StrictHostKeyChecking=no root@<IP> 'exit'
```

规则如下：

- 如果能登录，继续执行后续步骤
- 如果不能登录，立即中止任务，并提示用户提供该主机的 root 密码

在这种情况下，不要继续初始化，不要尝试其它账户，也不要绕过 root 探测规则。

### 第三步：收集并确认每台机器的可变参数

对每台机器，在执行脚本前确认以下参数：

- `NIC_NAME`
- `STATIC_IP_CIDR`
- `GATEWAY_IPV4`
- `DNS_SERVERS`
- `HOSTNAME_VALUE`
- `HOSTS_BLOCK_B64`（由完整 `/etc/hosts` 映射块编码得到）

如果用户没有提供，先尝试通过命令查询，例如：

```bash
ip addr
ip -o -4 addr show
ip route
hostnamectl --static
```

如果仍然无法得到可靠值，则暂停并询问用户。

关于 `DNS_SERVERS` 的默认规则：

- 如果用户明确给了 DNS，就使用用户提供的值。
- 如果用户没有给 DNS，但你能确认内网里存在**可用的递归 DNS**，优先使用那个递归 DNS。
- 如果用户没有给 DNS，且无法确认可用的内网递归 DNS，则默认优先使用国内公共 DNS：

```text
223.5.5.5 223.6.6.6
```

- 不要默认优先使用 `8.8.8.8`、`8.8.4.4` 作为第一选择。
- 只有在用户明确要求，或当前网络环境明确可以稳定访问这些 DNS 时，才使用它们。

### 第四步：上传脚本并执行

初始化脚本只负责固定安装步骤本身，不负责循环处理多台机器。

脚本路径：

- `scripts/rocky_linux10_init.sh`

使用方式：

1. 对每台机器先把脚本传上去
2. 再按该机器的变量执行脚本

示例执行方式：

```bash
scp scripts/rocky_linux10_init.sh root@<IP>:/tmp/rocky_linux10_init.sh
ssh root@<IP> "chmod +x /tmp/rocky_linux10_init.sh && NIC_NAME='<NIC_NAME>' STATIC_IP_CIDR='<STATIC_IP_CIDR>' GATEWAY_IPV4='<GATEWAY_IPV4>' DNS_SERVERS='<DNS_SERVERS>' HOSTNAME_VALUE='<HOSTNAME_VALUE>' HOSTS_BLOCK_B64='<HOSTS_BLOCK_B64>' /tmp/rocky_linux10_init.sh"
```

其中：

- `HOSTS_BLOCK_B64` 由完整 hosts 文本块进行 base64 编码得到
- `DNS_SERVERS` 如果未由用户指定，默认优先传入国内 DNS，例如：`223.5.5.5 223.6.6.6`
- DNS 校验默认优先按国内 DNS 思路处理，不要把 `8.8.8.8`、`8.8.4.4` 作为默认首选
- 不要把脚本内容重复写到这里
- 不要为循环安装再创建新的脚本
- 多台机器时，直接在 skill 执行流程里逐台处理

## 脚本职责

`scripts/rocky_linux10_init.sh` 只包含固定初始化步骤：

- 配置基础源
- 安装基础软件包
- 配置网络
- 关闭 SELinux
- 配置主机名
- 配置 `/etc/hosts`
- 关闭 Swap（仅基础关闭）
- 修改内核参数
- 关闭防火墙和 dnsmasq
- 配置时间同步
- 启用 IPVS
- 设置文件句柄数上限
- 配置 Docker CE 阿里云 repo 源

它不负责：

- 循环多主机
- 探测 root 是否可登录
- 生成本机 SSH key
- 自动修复执行失败
- 执行文档中标记为可选的步骤

## 失败处理

如果任何步骤执行失败：

- 立即停止当前主机的后续初始化
- 返回失败步骤
- 返回报错信息
- 返回修复建议
- 等待用户确认后再继续

不要在失败后擅自追加修复动作。

## 最终汇报格式

完成后按下面结构汇报：

```text
初始化结果：
- 主机 1：成功 / 失败
- 主机 2：成功 / 失败

已执行步骤：
- SSH key 检查 / 生成
- 免密登录配置
- 初始化脚本执行

失败信息（如有）：
- 哪台主机
- 哪一步失败
- 错误摘要
- 修复建议

本次跳过的可选步骤：
- swap LV 删除与分区扩容
- 系统内核优化（可选 sysctl）
```

## 注意事项

- 仅在 Rocky Linux 10 初始化场景中使用本 skill
- 看到“初始化 Linux 机器”“初始化 Rocky Linux”“初始化节点”“批量做 Linux 初始配置”等请求时，优先使用本 skill
- 不要引用外部临时文档路径
- 不要把脚本内容复制进 `SKILL.md`
- 不要额外生成重复功能脚本
- 不要自由发挥
