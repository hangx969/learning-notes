# 部署Jenkins

## 安装nfs服务

可以在任一台机器上部署nfs服务

~~~sh
yum install nfs-utils -y
systemctl start nfs
systemctl enable nfs
yum install nfs-utils -y
systemctl start nfs
systemctl enable nfs
~~~

创建nfs共享目录

~~~sh
mkdir /data/v2 -p
tee -a /etc/exports<<'EOF'
/data/v2 *(rw,no_root_squash)
EOF
exportfs -arv
~~~

## 准备前置资源

### namespace

~~~sh
kubectl create namespace jenkins-k8s
~~~

### PV+PVC

1. PV

~~~yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: jenkins-k8s-pv
spec:
  capacity:
    storage: 1Gi
  accessModes:
  - ReadWriteMany
  nfs:
    server: 172.16.183.100
    path: /data/v2
~~~

2. PVC

~~~yaml
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: jenkins-k8s-pvc
  namespace: jenkins-k8s
spec:
  resources:
    requests:
      storage: 1Gi
  accessModes:
  - ReadWriteMany
~~~

3. service account

~~~sh
kubectl create sa jenkins-k8s-sa -n jenkins-k8s
kubectl create clusterrolebinding jenkins-k8s-sa-cluster -n jenkins-k8s  --clusterrole=cluster-admin --serviceaccount=jenkins-k8s:jenkins-k8s-sa

~~~

