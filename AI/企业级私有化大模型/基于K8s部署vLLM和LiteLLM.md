## 1.1 GPU 环境准备

### 1.1.1 GPU 机器申请

若没有 GPU 机器，可以在公有云上临时申请。

- 阿里云： https://aliyun.com/
- 腾讯云： https://cloud.tencent.com/
- 华为云： https://www.huaweicloud.com/

rockylinux9.8，24GB显存，10MB公网固定带宽，100GB磁盘

### 1.1.2 驱动安装

下载地址： https://www.nvidia.com/en-us/drivers/unix/

选择最新版下载即可（Linux x64/AMD64/EM64T 或 Linux aarch64 对应版本）。

下载完成后，把安装包上传到 GPU 服务器，之后执行如下命令即可：

```bash
# 安装依赖包
dnf install gcc make kernel-devel wget -y
# 升级系统
dnf update -y
# 重启服务器
reboot
# 禁用 Linux 驱动 nouveau
grep "blacklist nouveau" /etc/modprobe.d/blacklist.conf || echo "blacklist nouveau" >> /etc/modprobe.d/blacklist.conf
grep "options nouveau modeset=0" /etc/modprobe.d/blacklist.conf || echo "options nouveau modeset=0" >> /etc/modprobe.d/blacklist.conf
dracut --force /boot/initramfs-$(uname -r).img
dracut --force --omit-drivers nouveau
reboot
# 检查 nouveau 是否关闭
lsmod | grep nouveau # 没有结果说明已经关闭
# 安装驱动
chmod +x NVIDIA-Linux-*.run && ./NVIDIA-Linux-*.run -q -s --no-dkms --no-x-check
# 安装完成后，重启服务器
reboot
```

驱动安装完成后，执行 `nvidia-smi` 命令检查是否安装成功：

```bash
nvidia-smi
```

## 1.2 K8s 环境准备

### 1.2.1 K8s 集群部署

#### 1.2.1.1 基础配置

基本环境配置：所有节点关闭防火墙、selinux、dnsmasq、swap。服务器配置如下：

```bash
systemctl disable --now firewalld
systemctl disable --now dnsmasq
setenforce 0
sed -i 's#SELINUX=enforcing#SELINUX=disabled#g' /etc/sysconfig/selinux
sed -i 's#SELINUX=enforcing#SELINUX=disabled#g' /etc/selinux/config
# 关闭 swap 分区
swapoff -a && sysctl -w vm.swappiness=0
sed -ri '/^[^#]*swap/s/^/#/' /etc/fstab
```

配置 yum 源，安装必备工具：

```bash
sed -e 's|^mirrorlist=|#mirrorlist=|g' \
    -e 's|^#baseurl=http://dl.rockylinux.org/$contentdir|baseurl=https://mirrors.aliyun.com/rockylinux|g' \
    -i.bak \
    /etc/yum.repos.d/*.repo
dnf makecache
```

必备工具安装：

```bash
yum install wget jq psmisc vim net-tools telnet yum-utils device-mapper-persistent-data lvm2 git -y
```

#### 1.2.1.2 Runtime 安装

配置安装源：

```bash
yum-config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
```

安装 Containerd：

```bash
yum install containerd.io -y
cat <<EOF | sudo tee /etc/modules-load.d/containerd.conf
overlay
br_netfilter
EOF
sudo modprobe overlay
sudo modprobe br_netfilter

cat <<EOF | sudo tee /etc/sysctl.d/99-kubernetes-cri.conf
net.bridge.bridge-nf-call-iptables  = 1
net.ipv4.ip_forward                 = 1
net.bridge.bridge-nf-call-ip6tables = 1
EOF
sudo sysctl --system

sudo mkdir -p /etc/containerd
containerd config default | sudo tee /etc/containerd/config.toml
sed -i 's#SystemdCgroup = false#SystemdCgroup = true#g' /etc/containerd/config.toml
sed -i 's#k8s.gcr.io/pause#registry.cn-hangzhou.aliyuncs.com/google_containers/pause#g' /etc/containerd/config.toml
sed -i 's#registry.gcr.io/pause#registry.cn-hangzhou.aliyuncs.com/google_containers/pause#g' /etc/containerd/config.toml
sed -i 's#registry.k8s.io/pause#registry.cn-hangzhou.aliyuncs.com/google_containers/pause#g' /etc/containerd/config.toml
# 启动 Containerd
systemctl daemon-reload
systemctl enable --now containerd
```

#### 1.2.1.3 Kubernetes 部署

配置安装源：

```bash
cat <<EOF | tee /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://mirrors.aliyun.com/kubernetes-new/core/stable/v1.36/rpm/
enabled=1
gpgcheck=1
gpgkey=https://mirrors.aliyun.com/kubernetes-new/core/stable/v1.36/rpm/repodata/repomd.xml.key
EOF
```

安装 Kubernetes 组件：

```bash
yum install kubeadm-1.36.* kubelet-1.36.* kubectl-1.36.* -y
systemctl enable --now kubelet
kubeadm config images pull \
  --image-repository registry.cn-hangzhou.aliyuncs.com/google_containers --kubernetes-version 1.36.0
# 初始化集群
kubeadm init --apiserver-advertise-address 192.168.181.134  --image-repository registry.cn-hangzhou.aliyuncs.com/google_containers --cri-socket "unix:///var/run/containerd/containerd.sock" --kubernetes-version 1.36.0
# 加入其它节点
kubeadm join 192.168.181.134:6443 --token cg0bkg.w83qlih44rjby2jk \
    --discovery-token-ca-cert-hash sha256:4efd525d2708c60bd450b0bd3f22a850283738f49b23e04334301a4ca07a1a8f
```

配置 kubeconfig：

```bash
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

安装 Addons：

```bash
yum install git -y

git clone https://gitee.com/dukuan/k8s-ha-install.git
cd k8s-ha-install/
git checkout manual-installation-v1.36.x
cd single/
kubectl create -f .
```

解除污点：

```bash
kubectl taint node  node-role.kubernetes.io/control-plane- --all
```

查看集群状态：

```bash
kubectl top node
kubectl get node
```

### 1.2.2 GPU Operator 部署

#### 1.2.2.1 Helm 安装

官方安装文档： https://helm.sh/docs/intro/install/
Helm 安装包： https://github.com/helm/helm/releases

安装 Helm：

```bash
# 首先下载安装包
mkdir helm
cd helm
wget https://get.helm.sh/helm-v4.2.2-linux-amd64.tar.gz
ls
tar xf helm-v4.2.2-linux-amd64.tar.gz
mv linux-amd64/helm /usr/local/bin/
helm version
```

创建 Namespace：

```bash
kubectl create ns gpu-operator
```

#### 1.2.2.2 部署 GPU Operator

添加仓库：

```bash
helm repo add nvidia https://helm.ngc.nvidia.com/nvidia \
    && helm repo update
```

下载安装包：

```bash
helm pull nvidia/gpu-operator
tar xf gpu-operator-*.tgz
cd gpu-operator/
```

国内机器需要修改 values 文件中的仓库地址：

```bash
vim charts/node-feature-discovery/values.yaml

image:
  repository: m.daocloud.io/registry.k8s.io/nfd/node-feature-discovery
```

之后安装即可：

```bash
helm install gpu-operator   -n gpu-operator --create-namespace   .
```

查看 Pod 状态：

```bash
kubectl get po -n gpu-operator
```

所有 Pod 启动完成后，即可在 Kubernetes 的节点状态中，看到 GPU 资源：

```bash
kubectl get po -n gpu-operator
```

查看 GPU 资源：

```bash
kubectl describe node | grep Allocatable: -A 10
```

创建 GPU 测试服务：

```bash
tee test.yaml <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: cuda-vectoradd
spec:
  restartPolicy: OnFailure
  containers:
  - name: cuda-vectoradd
    image: "nvcr.io/nvidia/k8s/cuda-sample:vectoradd-cuda11.7.1-ubuntu20.04"
    resources:
      limits:
        nvidia.com/gpu: 1
EOF
```

```bash
kubectl create -f test.yaml
```

查看日志：

```bash
kubectl logs cuda-vectoradd
```

### 1.2.3 动态存储配置

官方文档： https://longhorn.io/docs/1.12.0/deploy/install/install-with-helm/

#### 1.2.3.1 Longhorn

添加 Longhorn Helm 仓库：

```bash
helm repo add longhorn https://charts.longhorn.io
helm repo update
helm pull longhorn/longhorn
```

安装 Longhorn：

```bash
tar xf longhorn.tar.gz
cd longhorn/
helm install longhorn . -n longhorn-system --create-namespace --version 1.12.0
```

查看服务状态：

```bash
kubectl get po -n longhorn-system
```

等待服务启动后，创建 PVC 和 Pod 测试。首先创建 PVC：

```bash
tee longhorn-pvc-test.yaml <<'EOF
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: longhorn-redis-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: longhorn
  resources:
    requests:
      storage: 1Gi
EOF
```

```bash
kubectl create -f longhorn-pvc-test.yaml
kubectl get pvc
```

创建测试 Pod：

```bash
tee longhorn-pod-test.yaml <<'EOF
apiVersion: v1
kind: Pod
metadata:
  name: volume-test
spec:
  containers:
  - name: volume-test
    image: registry.cn-beijing.aliyuncs.com/dotbalo/nginx:1.15.12
    imagePullPolicy: IfNotPresent
    volumeMounts:
    - name: volv
      mountPath: /usr/share/nginx/html
    ports:
    - containerPort: 80
  volumes:
  - name: volv
    persistentVolumeClaim:
      claimName: longhorn-redis-pvc
EOF
```

```bash
kubectl create -f longhorn-pod-test.yaml
```

写入数据测试：

```bash
kubectl get po
kubectl exec -ti volume-test -- bash
```

## 1.3 模型部署

### 1.3.1 模型文件预下载

环境准备好后，就可以通过 VLLM 部署模型。首先创建模型存储的 PVC：

```yaml
tee qwen35-4b-pvc.yaml <<'EOF'
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: qwen35-4b-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: longhorn
  resources:
    requests:
      storage: 20Gi # 根据模型大小进行调整
EOF
```

创建 PVC：

```bash
kubectl create ns models
kubectl create -f qwen35-4b-pvc.yaml -n models
```

接下来使用一个 Job，提前下载模型：

```bash
tee model-download-job.yaml <<'EOF'
apiVersion: batch/v1
kind: Job
metadata:
  name: qwen35-4b-model-downloader
spec:
  backoffLimit: 3
  template:
    spec:
      restartPolicy: OnFailure
      containers:
        - name: downloader
          image: registry.cn-beijing.aliyuncs.com/dotbalo/vllm-openai:latest
          command: ["/bin/sh", "-c"]
          args:
            - |
              echo "开始从 ModelScope 下载 Qwen/Qwen3.5-4B 模型..."
              python3 -c "
              from modelscope import snapshot_download
              model_dir = snapshot_download('Qwen/Qwen3.5-4B', cache_dir='/data/modelscope')
              print(f'模型下载完成，路径: {model_dir}')
              "
          env:
            - name: VLLM_USE_MODELSCOPE
              value: "true"
            - name: MODELSCOPE_CACHE
              value: "/data/modelscope"
            - name: TZ
              value: "Asia/Shanghai"
          volumeMounts:
            - name: model-storage
              mountPath: /data/modelscope
      volumes:
        - name: model-storage
          persistentVolumeClaim:
            claimName: qwen35-4b-pvc
EOF
```

查看 Pod：

```bash
kubectl get po -n models
```

查看下载日志：

```bash
kubectl logs -f qwen35-4b-model-downloader-7w7sg -n models
```

确认下载的文件：

```bash
kubectl exec qwen35-4b-model-downloader-7w7sg -n models -- ls /data/modelscope/Qwen/
Qwen3.5-4B
```

### 1.3.2 部署模型

模型下载完成后，即可部署模型：

```bash
kubectl get po -n models
```

创建部署文件：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: qwen3-5-4b-deployment
  labels:
    app: qwen3-5-4b
spec:
  replicas: 1
  selector:
    matchLabels:
      app: qwen3-5-4b
  template:
    metadata:
      labels:
        app: qwen3-5-4b
    spec:
      containers:
        - name: qwen3-5-4b
          image: registry.cn-beijing.aliyuncs.com/dotbalo/vllm-openai:latest
          command:
            - "--port"
            - "8080"
            - "--served-model-name"
            - "Qwen3.5-4B"
            - "--model"
            - "/data/modelscope/Qwen/Qwen3.5-4B" # 模型路径指向 PVC 挂载点下的具体模型目录
            - "--gpu_memory_utilization"
            - "0.6"
            - "--max-model-len"
            - "65536"
            - "--max_num_batched_tokens"
            - "65536"
            - "--api-key"
            - "xxxx"
          ports:
            - containerPort: 8080
          env:
            - name: TZ
              value: "Asia/Shanghai"
            - name: LANG
              value: "C.UTF-8"
            - name: LC_ALL
              value: "C.UTF-8"
            - name: CUDA_VISIBLE_DEVICES
              value: "0"
            - name: NVIDIA_VISIBLE_DEVICES
              value: "all"
            - name: VLLM_USE_MODELSCOPE
              value: "true"
            - name: MODELSCOPE_CACHE
              value: "/data/modelscope"
          resources:
            limits:
              nvidia.com/gpu: 1
            requests:
              nvidia.com/gpu: 1
          volumeMounts:
            - name: model-storage
              mountPath: /data/modelscope
            - name: dshm
              mountPath: /dev/shm
          startupProbe:
            httpGet:
              path: /health
              port: 8080
            # 给予最长 15 分钟（900 秒）的启动时间，每 10 秒探测一次
            # 如果 90 次（900/10）探测都失败，容器才会被重启
            failureThreshold: 90
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 60
            periodSeconds: 30
            timeoutSeconds: 10
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 15
            timeoutSeconds: 10
            failureThreshold: 3
      volumes:
        - name: model-storage
          persistentVolumeClaim:
            claimName: qwen35-4b-pvc
        - name: dshm
          emptyDir:
            medium: Memory
            sizeLimit: 16Gi
---
apiVersion: v1
kind: Service
metadata:
  name: qwen3-5-4b-service
spec:
  selector:
    app: qwen3-5-4b
  ports:
    - protocol: TCP
      port: 8080
      targetPort: 8080
  type: NodePort # 非必须
```

查看启动状态：

```bash
kubectl get po -n models
```

模型访问测试：

```bash
curl -H "Authorization: Bearer xxxx" -X POST http://127.0.0.1:32656/v1/chat/completions -H "Content-Type: application/json" -d '{"model": "Qwen3.5-4B","stream": true, "messages": [{"role": "user", "content": "介绍下你自己"}]}'
```

## 1.4 LiteLLM 高可用落地

### 1.4.1 高可用 Redis 部署

在 K8s 集群中安装 Redis 哨兵，用于 LiteLLM 的缓存使用：

```bash
tar xf redis.tar.gz
cd redis
helm install redis . -n litellm --create-namespace
```

查看 Redis 状态：

```bash
kubectl get po -n litellm
```

测试哨兵状态：

```bash
kubectl exec -ti redis-node-0 -n litellm -- bash
```

Redis 单节点部署：

```bash
kubectl create -f redis-single.yaml -n litellm
```

查看状态：

```bash
kubectl get po -n litellm -l app=redis-single
```

测试 Redis：

```bash
kubectl exec -ti redis-single-578d7d75f7-2mqh7 -n litellm -- bash
I have no name! [ / ]$ redis-cli -h redis-single
redis-single:6379> auth xxxx_redis
OK
redis-single:6379> set a 1
OK
redis-single:6379> get a
"1"
```

### 1.4.2 高可用 Postgresql 部署

在 Kubernetes 集群中按照高可用 PG 数据库：

```bash
tar xf postgresql-ha.tar.gz
cd postgresql-ha/
```

查看状态：

```bash
kubectl get po -n litellm
```

链接测试：

```bash
kubectl exec -ti pg-postgresql-ha-pgpool-74f76c59fd-gkgs9 -n litellm -- bash
I have no name!@pg-postgresql-ha-pgpool-74f76c59fd-gkgs9:/$ psql -U postgres -h pg-postgresql-ha-pgpool
Password for user postgres: postgres_litellm
postgres=# \l
                                  List of databases
   Name   |  Owner   | Encoding | Locale Provider |  Collate   |   Ctype    | ...
----------+----------+----------+------------------+------------+------------+-----
 litellm  | postgres | UTF8     | libc             | en_US.UTF-8 | en_US.UTF-8 |
```

### 1.4.3 部署 LiteLLM

部署 LiteLLM：

```bash
kubectl create -f litellm-deploy.yaml -n litellm
```

查看状态：

```bash
kubectl get po -n litellm
```

访问测试：

```bash
kubectl get svc -n litellm
```

登录 LiteLLM 后台后，接下来就可以添加之前部署的模型服务，和基础课程添加过程一致，将 **API Base** 填写为 K8s Service 地址（如 `http://qwen3-5-4b-service.models:8080/v1`），API Key 填写为 `xxxx`。

使用 LiteLLM 调用模型测试：

```bash
kubectl get svc -n litellm
curl -H "Authorization: Bearer sk-tvE6JKo-Q54_dkQIdXYnlg" -X POST http://127.0.0.1:31398/v1/chat/completions -H "Content-Type: application/json" -d '{"model": "Qwen3.5-4B","stream": true, "messages": [{"role": "user", "content": "介绍下你自己"}]}'
```

### 1.4.4 限流测试

LiteLLM 支持如下三种限流方案：

- **TPM**：每分钟 Token 数量限制
- **RPM**：每分钟请求数量限制
- **Max Parallel Requests**：最大并发量限制

其中 TPM 和 RPM 分为了三个限制方法：

- **Best effort**：系统会尽可能多地处理请求，不强制拦截超出限制的请求
- **Guaranteed**：系统会严格进行限制，确保不超过设定的限制值
- **Dynamic**：动态调整，系统根据实时负载、历史调用等状态，动态调整限制规则

比如限制某个 Key，每分钟最大 Token 为 2000，请求数为 3：

- **TPM Limit**：`2000`
- **TPM Rate Limit Type**：`Dynamic`
- **RPM Limit**：`3`
- **RPM Rate Limit Type**：`Guaranteed throughput`

测试每分钟请求数量限制：

```bash
curl -H "Authorization: Bearer sk-tvE6JKo-Q54_dkQIdXYnlg" -X POST http://127.0.0.1:31398/v1/chat/completions -H "Content-Type: application/json" -d '{"model": "Qwen3.5-4B","stream": true, "messages": [{"role": "user", "content": "介绍下你自己"}]}'
```

```json
{"error":{"message":"Rate limit exceeded for api_key: 7b41ef1ecb31b286fdb9815a5266c8a232edf059cc02dfdf05a1a38d85f87ab3. Limit type: requests. Current limit: 3, Remaining: 0.","type":"throttling_error","param":null,"code":"429"}}
```

由于请求数量是 Guaranteed，所以会直接拒绝，token 限制为动态的，所以不会被拒绝。调整为 Guaranteed 后会拒绝连接：

```json
{"error":{"message":"Rate limit exceeded for api_key: 7b41ef1ecb31b286fdb9815a5266c8a232edf059cc02dfdf05a1a38d85f87ab3. Limit type: tokens. Current limit: 200, Remaining: 0.","type":"throttling_error","param":null,"code":"429"}}
```

### 1.4.5 缓存命中

同一个问题，连续问会直接返回结果（命中 Redis 缓存，无需重新推理）：

```bash
curl -H "Authorization: Bearer sk-tvE6JKo-Q54_dkQIdXYnlg" -X POST http://127.0.0.1:31398/v1/chat/completions -H "Content-Type: application/json" -d '{"model": "Qwen3.5-4B","stream": true, "messages": [{"role": "user", "content": "介绍下你自己 2"}]}'
```

流式返回示例（节选）：

```
data: {"id":"chatcmpl-a1c275d854c9c722","object":"chat.completion.chunk","created":1783764514,"model":"Qwen3.5-4B","choices":[{"index":0,"delta":{"role":"assistant","content":"对于用户的问题，首先需要明确我是 Qwen3.5，是通义实验室最新推出的大语言模型。..."}}]}
data: {"id":"chatcmpl-a1c275d854c9c722","object":"chat.completion.chunk","created":1783764514,"model":"Qwen3.5-4B","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}
data: [DONE]
```

## 1.5 GPU 虚拟化

### 1.5.1 HAMI 部署

官方文档： https://project-hami.io/zh/docs/installation/prerequisites

HAMI 管理 GPU 机器，需要先给 GPU 机器添加 `gpu=on` 的标签：

```bash
kubectl label nodes {nodeid} gpu=on
```

HAMI 的安装依赖当前 K8s 的版本，所有先获取当前的 K8s 版本：

```bash
kubectl version
```

安装 HAMI：

```bash
helm repo add hami-charts https://project-hami.github.io/HAMi/
helm pull hami-charts/hami
# 解压安装包，修改镜像配置
sed -i 's#docker.io#m.daocloud.io/docker.io#g' values.yaml
helm install hami . --set scheduler.kubeScheduler.imageTag=v1.35.3 -n kube-system
```

查看启动状态：

```bash
kubectl get pods -n kube-system | grep hami
```

查看注册的 GPU 资源信息：

```bash
kubectl describe node | grep nvidia.com/gpu:
nvidia.com/gpu:     20 # 每个 GPU 卡*10
```

### 1.5.2 GPU 调度测试

创建测试 Pod：

```yaml
tee 1-gpu-test.yaml <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: hami-gpu-test
  labels:
    app: hami-gpu-test
spec:
  containers:
    - name: hami-gpu-test
      imagePullPolicy: IfNotPresent
      image: registry.cn-beijing.aliyuncs.com/dotbalo/vllm-openai:latest
      command:
        - sh
        - -c
        - nvidia-smi
  restartPolicy: OnFailure
  env:
    - name: TZ
      value: "Asia/Shanghai"
    - name: LANG
      value: "C.UTF-8"
    - name: LC_ALL
      value: "C.UTF-8"
  resources:
    limits:
      nvidia.com/gpu: 1
EOF
```

查看日志：

```bash
kubectl logs -f hami-gpu-test
```

上述分配了 1 个 vGPU，但是为指定显存和核心数，所以会独占一个显卡，和无虚拟化一致。

### 1.5.3 分配指定显存

假如需要控制每个显卡使用的显存大小，可以添加 `gpumem` 参数：

```yaml
resources:
  limits:
    nvidia.com/gpu: 2
    nvidia.com/gpumem: 3000
```

以上代表分配两个显卡，每个显卡分配 3000Mi 显存。创建后查看日志：

```
nvidia-smi
```

注意：`nvidia.com/gpu` 和 `nvidia.com/gpumem` 不能超过物理机真实显卡数量和显存大小。
显存大小也可以按照百分比分配：`nvidia.com/gpumem-percentage: 50`。

### 1.5.4 指定显卡类型调度

HAMI 支持不同显卡级别的调度，比如某个任务需要 A100，可以添加如下注释：

```yaml
metadata:
  annotations:
    nvidia.com/use-gputype: "A100,V100" # 多种类型逗号分割
    # nvidia.com/nouse-gputype: "1080,2080" # 指定黑名单
```

设备类型可以通过 `nvidia-smi` 命令查看：

```bash
nvidia-smi -L
GPU 0: NVIDIA A10 Ada Generation
GPU 1: NVIDIA A10 Ada Generation
```

### 1.5.5 VLLM 测试

修改之前的 vllm 启动文件，添加显存配置：

```yaml
resources:
  limits:
    nvidia.com/gpu: 1
    nvidia.com/gpumem: 30720
  requests:
    nvidia.com/gpu: 1
    nvidia.com/gpumem: 30720
```

修改显存使用率为 0.95：

```yaml
- "--gpu_memory_utilization"
- "0.95"
```

查看启动状态：

```bash
kubectl get po -n models -owide
```

查看显存占用：

```
| 0  NVIDIA A10 Ada Gene...   Off | 00000000:99:00.0 Off |                  0 |
| 30% 51C  P8   33W / 285W |  27117MiB / 49140MiB |      0%    Default |
|                                                                        N/A |
| 1  NVIDIA A10 Ada Gene...   Off | 00000000:BD:00.0 Off |                  0 |
| 30% 45C  P8   28W / 285W |     38MiB / 49140MiB |      0%    Default |
```