# k8s安全测试工具

## kube-bench

- 这是一个开源工具，用于检查 Kubernetes 集群是否符合安全标准。它会对集群进行自动化扫描，并提供详细的安全建议。
- 安装

~~~sh
wget https://github.com/aquasecurity/kube-bench/releases/download/v0.6.5/kube-bench_0.6.5_linux_amd64.tar.gz
tar -xvf kube-bench_0.6.5_linux_amd64.tar.gz
cd kube-bench_0.6.5_linux_amd64/
#运行 Kube-bench：
sudo ./kube-bench
~~~

## kube-hunter

- 这个工具可以帮助查找集群中可能存在的安全漏洞。它会执行一些自动化测试，并生成报告，以帮助你修复可能存在的问题。
- 安装

~~~sh
docker pull aquasec/kube-hunter
docker run -it --rm --network host aquasec/kube-hunter
docker run -it --rm --network host -v /tmp/kube-hunter-report:/tmp aquasec/kube-hunter --report /tmp/report.html
#执行完成后，在 /tmp/kube-hunter-report 目录下会生成报告文件 report.html。
~~~

## kubeaudit

- 这是一个命令行工具，可用于评估Kubernetes Pod 和 Deployment 配置的安全性。它可以检查容器镜像的安全性，权限和网络配置等问题。
- 安装

~~~sh
sudo wget -O kubeaudit https://github.com/Shopify/kubeaudit/releases/download/v0.14.2/kubeaudit_0.14.2_linux_amd64
sudo chmod +x kubeaudit
#运行 kubeaudit：
sudo ./kubeaudit
~~~

## Polaris

- 这个工具可以帮助你评估集群的安全性和可靠性。它会扫描 Kubernetes 资源并提供安全建议。
- 安装

~~~sh
git clone https://github.com/FairwindsOps/polaris.git
cd polaris
kubectl apply -f deploy/polaris/
#运行 Polaris：
polaris audit
#执行完成后，会列出检查结果。
~~~

## kubescape

- 这是一个开源工具，可以帮助您评估 Kubernetes 集群是否存在安全漏洞。它会检查集群中的资源，并根据规则集提供安全性建议。
- 安装

~~~sh
wget https://github.com/armosec/kubescape/releases/download/v1.1.11/kubescape_v1.1.11_linux_x64.tar.gz
tar xvf kubescape_v1.1.11_linux_x64.tar.gz
sudo mv kubescape /usr/local/bin/
#运行 kubescape
kubescape scan framework nsa
~~~

