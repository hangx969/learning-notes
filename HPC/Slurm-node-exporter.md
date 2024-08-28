# 旧版exporter

## 在线部署

参考：

- https://erdong.site/prometheus-notes/chapter03-Exporter/3.24-slurm-exporter.html
- https://github.com/vpenso/prometheus-slurm-exporter
- 编译指南：https://github.com/vpenso/prometheus-slurm-exporter/blob/master/DEVELOPMENT.md

1. 下载安装包解压并复制

~~~sh
#去slurm工作节点
export VERSION=1.15 OS=linux ARCH=amd64
wget https://dl.google.com/go/go$VERSION.$OS-$ARCH.tar.gz
tar -xzvf go$VERSION.$OS-$ARCH.tar.gz
export PATH=$PWD/go/bin:$PATH

# clone the source code
git clone https://github.com/vpenso/prometheus-slurm-exporter.git
cd prometheus-slurm-exporter
make

#Slurm Exporter 部署非常简单，下载最新的安装包，然后解压，将解压好的 prometheus-slurm-exporter 文件拷贝到/usr/bin/prometheus-slurm-exporter 就完成了第一步，然后将下面的 SystemD 的启动文件 slurm-exporter.service 拷贝到指定目录就完成了。
cp prometheus-slurm-exporter/bin/prometheus-slurm-exporter /usr/bin/prometheus-slurm-exporter

tee /etc/systemd/system/slurm-exporter.service <<'EOF'
[Unit]
Description=Prometheus SLURM Exporter

[Service]
ExecStart=/usr/bin/prometheus-slurm-exporter -listen-address :9092
Restart=always
RestartSec=15

[Install]
WantedBy=multi-user.target
EOF

#启动 Slurm Exporter 
systemctl daemon-reload
systemctl enable slurm-exporter.service --now
systemctl restart slurm-exporter.service
~~~

## 离线环境部署

~~~sh
##去在线环境下载go依赖##
#下载go 1.15
export VERSION=1.15 OS=linux ARCH=amd64
wget https://dl.google.com/go/go$VERSION.$OS-$ARCH.tar.gz
tar -xzvf go$VERSION.$OS-$ARCH.tar.gz
export PATH=$PWD/go/bin:$PATH

#下载源码包
git clone https://github.com/vpenso/prometheus-slurm-exporter.git
cd prometheus-slurm-exporter
mkdir vendor
#下载依赖到vendor中
go mod download
go mod vendor
#打包整个源码包到离线环境

###离线环境中，编辑makefile###
cd prometheus-slurm-exporter
vim Makefile
#如下，注释掉go mod download和go test部分，避免联网
PROJECT_NAME = prometheus-slurm-exporter
SHELL := $(shell which bash) -eu -o pipefail

GOPATH := $(shell pwd)/go/modules
GOBIN := bin/$(PROJECT_NAME)
GOFILES := $(shell ls *.go)

.PHONY: build
build: test $(GOBIN)

$(GOBIN): go/modules/pkg/mod $(GOFILES)
        mkdir -p bin
        @echo "Building $(GOBIN)"
        go build -v -o $(GOBIN) -mod=vendor

go/modules/pkg/mod: go.mod
        #go mod download

.PHONY: test
test: go/modules/pkg/mod $(GOFILES)
        #go test -v

run: $(GOBIN)
        $(GOBIN)

clean:
        go clean -modcache
        rm -fr bin/ go/

#编译
make

#部署服务
cp prometheus-slurm-exporter/bin/prometheus-slurm-exporter /usr/bin/prometheus-slurm-exporter

tee /etc/systemd/system/slurm-exporter.service <<'EOF'
[Unit]
Description=Prometheus SLURM Exporter

[Service]
ExecStart=/usr/bin/prometheus-slurm-exporter -listen-address :9092
Restart=always
RestartSec=15

[Install]
WantedBy=multi-user.target
EOF

#启动 Slurm Exporter 
systemctl daemon-reload
systemctl enable slurm-exporter.service --now
systemctl restart slurm-exporter.service
~~~

## 可以收集的监控指标

使用 Slurm Exporter 可以收集很多的指标，包括 CPU、GPU、机器节点、提交的作业、作业分区的状态、每个账户和用户的作业信息、调度器的信息，我们大概看一下具体是什么。

### CPU 的状态

- Allocated: 已经被分配给作业的 CPU 数量。
- Idle: 没有被分配给做而已，空闲的 CPU 数量。
- Other: 暂时无法使用的 CPU 数量，不能使用的原因有多种，可能是机器坏了，也可能是被管理员设置了这些机器不能用于作业分配，一般是处于维护或者特殊用途
- Total: CPU 总数

### GPU 的状态

- Allocated: 已经被分配给作业的 GPU 数量。
- Other: GPUs which are unavailable for use at the moment.
- Total: GPU 卡的总数.
- Utilization: 集群中总的 GPU 使用率.

从0.19版本开始，GPU计费必须在命令行中添加 `-gpu-acct` 选项来显式启用，否则它将不会被激活。

### 机器节点的状态

- Allocated: 已经被分配给作业的节点。
- Completing: 与这些节点关联的所有作业都在完成过程中。a
- Down: 不能使用的节点.
- Drain: 处于这个状态的节点有 2 中不同的状态，
  - drained 状态的节点(被系统管理员都标记为不可用)
  - 处于 drained 状态的节点(当前正在执行作业，但不会分配给新的作业)。
- Fail: 这些节点预计很快就会失败，并且无法响应系统管理员的请求，也无法使用它们。
- Error: 当前处于错误状态且不能运行任何作业的节点
- Idle: 未分配给任何作业的节点，因此可供使用。
- Maint: 当前被标记为维护标志的节点。
- Mixed: 这些节点已经分配了一些cpu，而其他cpu处于空闲状态。
- Resv: 这些节点处于高级预订状态，通常不可用。

从0.18版本开始，Slurm也提取并导出了每个已知节点的以下信息:

- CPU:分配的cpu个数、空闲cpu个数、其他cpu个数和总数。
- 内存:已分配和总内存。
- 标签:主机名及其Slurm状态(例如空闲、混合、分配、耗尽等)

### 作业状态

- PENDING: 等待分配资源的作业.

- PENDING_DEPENDENCY: 由于未执行的作业依赖关系而等待的作业。

- RUNNING: 目前的已经分配资源并且正在执行的作业。

- SUSPENDED: 作业有分配，但执行已经被暂停，cpu已经被释放给其他作业。

- CANCELLED: 被用户或系统管理员明确取消的作业。

- COMPLETING: 正在完成的作业

- COMPLETED: 作业运行完成，终止了所有节点上的所有进程，退出码为0。

- CONFIGURING: 作业已经分配了资源，但正在等待它们准备好使用。

- FAILED: 作业以非零退出码或其他失败条件终止。

- TIMEOUT: 作业在达到限制的时间后就终止了。

- PREEMPTED: 由于抢占而终止作业。

- NODE_FAIL: 由于一个或多个分配的节点失败而终止作业。


### 作业分区的状态

- 每个分区运行/挂起的作业，分配给Slurm帐户和用户。

- 每个分区的总/分配/空闲CPU加上每个用户ID的已用CPU。

### 每个账户和用户的作业信息

- Running/Pending/Suspended 每个账号的作业.
- Running/Pending/Suspended 每个用户的作业

### 调度器的信息

- Server Thread count: 当前活动的slurmctld线程数。
- Queue size: scheduler queue 的长度
- DBD Agent queue size: SlurmDBD 的消息队列的长度。
- Last cycle: 上一个调度周期的时间(以微秒为单位)。
- Mean cycle:自上次重置以来调度周期的平均值。
- Cycles per minute: 每分钟调度执行的计数器。
- (Backfill) Last cycle: 最后一次回填周期的时间(以微秒计)。
- (Backfill) Mean cycle: 自上次重置以来，以微秒计的平均回填调度周期。
- (Backfill) Depth mean: 自上次重置以来的回填调度周期中已处理作业的平均值。
- (Backfill) Total Backfilled Jobs (since last slurm start): 自从上次Slurm启动以来，大量的作业得以恢复。
- (Backfill) Total Backfilled Jobs (since last stats cycle start): 自上次统计复位以来，由于回填而启动的作业数量。
- (Backfill) Total backfilled heterogeneous Job components: 自上次Slurm启动以来，由于回填，异构作业组件的数量开始增加。

## prometheus配置

添加下面的config：

~~~sh
scrape_configs:
  - job_name: 'my_slurm_exporter'
    scrape_interval:  30s
    scrape_timeout:   30s
    static_configs:
    - targets: ['172.16.183.134:9092']
~~~

## grafana配置

- 使用dashboard：https://grafana.com/grafana/dashboards/4323-slurm-dashboard/

# 新版exporter+Slurm Dashboard V2

## 部署

- 前面的slurm exporter停止维护了，现在有新的exporter：https://github.com/rivosinc/prometheus-slurm-exporter

~~~sh
#下载二进制包解压，直接有了二进制文件
tar zxvf prometheus-slurm-exporter_1.6.4_linux_amd64.tar.gz
#拷贝到bin目录
cp ./prometheus-slurm-exporter /usr/bin/prometheus-slurm-exporter

#用systemd管理服务
tee /etc/systemd/system/slurm-exporter.service <<'EOF'
[Unit]
Description=Prometheus SLURM Exporter New

[Service]
ExecStart=/usr/bin/prometheus-slurm-exporter -slurm.collect-diags -slurm.collect-licenses -slurm.collect-limits
Restart=always
RestartSec=15

[Install]
WantedBy=multi-user.target
EOF

#启动 Slurm Exporter 
systemctl enable slurm-exporter --now
~~~

> 参数说明：
>
> Usage of /usr/bin/prometheus-slurm-exporter:
>   -slurm.cli-fallback
>         drop the --json arg and revert back to standard squeue for performance reasons (default true)
>   -slurm.collect-diags
>         Collect daemon diagnostics stats from slurm
>   -slurm.collect-licenses
>         Collect license info from slurm
>   -slurm.collect-limits
>         Collect account and user limits from slurm
>   -slurm.diag-cli string
>         sdiag cli override
>   -slurm.lic-cli string
>         squeue cli override
>   -slurm.poll-limit float
>         throttle for slurmctld (default: 10s)
>   -slurm.sacctmgr-cli string
>         saactmgr cli override
>   -slurm.sinfo-cli string
>         sinfo cli override
>   -slurm.squeue-cli string
>         squeue cli override
>   -trace.enabled
>         Set up Post endpoint for collecting traces
>   -trace.path string
>         POST path to upload job proc info
>   -trace.rate uint
>         number of seconds proc info should stay in memory before being marked as stale (default 10)
>   -web.listen-address string
>         Address to listen on for telemetry "(default: :9092)"

## prometheus配置

添加下面的config：

~~~sh
scrape_configs:
  - job_name: 'slurm_exporter'
    scrape_interval:  30s
    scrape_timeout:   30s
    static_configs:
    - targets: ['172.16.183.134:9092']
    - targets: ['172.16.183.133:9092']
    - targets: ['172.16.183.135:9092']
~~~

注:这个版本不太好用，不如老的那版exporter数据多
