# Dashboard安装

## 镜像准备

```bash
#上传镜像和yaml文件：dashboard_2_0_0.tar.gz、metrics-scrapter-1-0-1.tar.gz、kubernetes-dashboard.yaml
docker load -i ./dashboard_2_0_0.tar.gz
docker load -i ./metrics-scrapter-1-0-1.tar.gz

#1.24版本后用ctr来解压
ctr images import dashboard_2_0_0.tar.gz
ctr images import metrics-scrapter-1-0-1.tar.gz
ctr images list
```

## 安装配置

```bash
#安装
kubectl apply -f kubernetes-dashboard.yaml
#查看
kubectl get pods -n kubernetes-dashboard
kubectl get svc -n kubernetes-dashboard

#修改svc类型到Nodeport
kubectl edit svc kubernetes-dashboard -n kubernetes-dashboard
#把type: ClusterIP变成 type: NodePort

k get svc -n kubernetes-dashboard
NAME                        TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)         AGE
dashboard-metrics-scraper   ClusterIP   10.109.123.241   <none>        8000/TCP        10m
kubernetes-dashboard        NodePort    10.109.139.152   <none>        443:30868/TCP   10m
#修改完成后，访问任何一个工作节点ip:Nodeport映射的物理机端口（30868），即可访问kubernetes dashboard。
#https://20.187.116.220:30868
```

## 解决无法访问问题

浏览器出于安全原因拒绝访问：

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310242027277.png" alt="image-20231024202732124" style="zoom:50%;" />

在google/Edge浏览器中，页面任意空白位置，直接键盘敲入：thisisunsafe，可以直接跳过安全报错进入页面。

## 登录dashboard

### token方式

- 查看安装dashboard的时候创建的SA

  ```bash
  k get sa -n kubernetes-dashboard
  
  NAME                   SECRETS   AGE
  default                0         34m
  kubernetes-dashboard   0         34m
  ```

- 给这个SA授予管理员权限

  ```bash
  kubectl create clusterrolebinding dashboard-cluster-admin --clusterrole=cluster-admin --serviceaccount=kubernetes-dashboard:kubernetes-dashboard
  ```

- 查看dashboard创建的secret

  ```bash
  kubectl get secret -n kubernetes-dashboard
  #!!!这里的问题是: 1.26版本创建role-binding之后，没有kubernetes-dashboard-token-ppc8c这样的pod被创建（需要手动创建sa和secret，手动绑定）。1.23版本重装之后是可以的。
  
  #获取token
  kubectl describe secret kubernetes-dashboard-token-ppc8c -n kubernetes-dashboard
  ```

### kubeconfig方式

```bash
#进入证书目录
cd /etc/kubernetes/pki

#创建一个k8s集群
kubectl config set-cluster kubernetes --certificate-authority=./ca.crt --server="https://192.168.40.4:6443" --embed-certs=true --kubeconfig=/root/dashboard-admin.conf

#查看这个集群的conf文件
cat /root/dashboard-admin.conf 

#创建credentials, 需要使用上面的kubernetes-dashboard-token-ppc8c对应的token信息
DEF_NS_ADMIN_TOKEN=$(kubectl get secret kubernetes-dashboard-token-ppc8c -n kubernetes-dashboard  -o jsonpath={.data.token}|base64 -d)
kubectl config set-credentials dashboard-admin --token=$DEF_NS_ADMIN_TOKEN --kubeconfig=/root/dashboard-admin.conf

#创建context
kubectl config set-context dashboard-admin@kubernetes --cluster=kubernetes --user=dashboard-admin --kubeconfig=/root/dashboard-admin.conf
#切换context的current-context是dashboard-admin@kubernetes
kubectl config use-context dashboard-admin@kubernetes --kubeconfig=/root/dashboard-admin.conf
#把刚才的kubeconfig文件dashboard-admin.conf复制到桌面,浏览器访问时使用kubeconfig认证，把刚才的dashboard-admin.conf导入到web界面，就可以登陆了.
```

