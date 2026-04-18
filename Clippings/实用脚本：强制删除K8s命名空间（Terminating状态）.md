---
title: "实用脚本：强制删除K8s命名空间（Terminating状态）"
source: "https://mp.weixin.qq.com/s/ERIZaE08tGUtd5fs9YvR5Q"
author:
  - "[[院长技术]]"
published:
created: 2026-04-18
description:
tags:
  - "clippings"
---
原创 院长技术 *2025年12月21日 16:12*

## 加入技术交流群

![图片](https://mmbiz.qpic.cn/mmbiz_jpg/rFHwZfd6jPIJ9cdEIibMo9TO0zuEQmScOHfuRFTvE2PgplNZDMabibNpBUTewyhjULHUFlf8FsLMaR7RiaCNqgHnQ/640?wx_fmt=jpeg&from=appmsg&watermark=1&wxfrom=5&wx_lazy=1&tp=webp#imgIndex=0)

## 前言

删除命名空间时，可能因为一些资源存在，会出现命名空间的状态一直处于Terminating状态，无论是重启K8s，还是重启所有服务器都没用。

## 首先在k8s-master节点执行开启proxy

```
[root@k8s-master ~]# kubectl proxy
Starting to serve on 127.0.0.1:8001
```

## 新开一个终端窗口创建脚本

```
[root@k8s-master ~]# vim deleteNameSpace.sh
# 脚本内容如下：

#!/bin/bash
# 获取要删除的 namespace 名称
NAMESPACE="$1"

# 如果没有传入参数，提示用户传入 namespace 名称
if [ -z "$NAMESPACE" ]
then
    echo "请传入要删除的 namespace 名称："
    read NAMESPACE
fi

# 提示用户 namespace 名称
echo "您将要删除的 namespace 名称是：$NAMESPACE"

# 使用 kubectl 命令获取 namespace 对应的 JSON 格式，再用 jq 工具修改 namespace 的 spec 属性，并将修改后的 JSON 数据保存到 temp.json 文件中
kubectl get namespace "$NAMESPACE" -o json | jq '.spec = {"finalizers":[]}' > temp.json

# 使用 curl 命令发送 PUT 请求，删除指定的 namespace
curl -k -H "Content-Type: application/json" -X PUT --data-binary @temp.json "127.0.0.1:8001/api/v1/namespaces/$NAMESPACE/finalize"

# 检查是否删除成功，输出成功或失败信息
if kubectl get namespace "$NAMESPACE" &>/dev/null
then
    echo "删除 namespace 失败：命名空间 '$NAMESPACE' 仍然存在"
    exit 1
else
    echo "删除 namespace 成功：命名空间 '$NAMESPACE' 已不存在"
    exit 0
fi
```

## 执行脚本前，查看命名空间状态

```
[root@k8s-master ~]# kubectl get ns
NAME                         STATUS        AGE
cdi                          Active        171d
default                      Active        172d
knative-eventing             Terminating   2d
kube-node-lease              Active        172d
kube-public                  Active        172d
kube-system                  Active        172d
kubevirt                     Active        171d
kubevirt-manager             Active        171d
kuboard                      Active        17h
monitoring                   Active        22h
tekton-dashboard             Active        43d
tekton-pipelines             Active        45d
tekton-pipelines-resolvers   Active        45d
```

## 执行脚本进行删除knative-eventing命名空间

```
[root@k8s-master ~]# sh deleteNameSpace.sh knative-eventing
您将要删除的 namespace 名称是：knative-eventing
{
  "kind": "Namespace",
  "apiVersion": "v1",
  "metadata": {
    "name": "knative-eventing",
    "uid": "518283c2-d470-4c59-9f10-cfcd4a1e4256",
    "resourceVersion": "12982602",
    "creationTimestamp": "2025-12-19T06:47:27Z",
    "deletionTimestamp": "2025-12-20T08:30:53Z",
    "labels": {
      "app.kubernetes.io/name": "knative-eventing",
      "app.kubernetes.io/version": "1.14.0",
      "kubernetes.io/metadata.name": "knative-eventing"
    },
    "annotations": {
      "kubectl.kubernetes.io/last-applied-configuration": "{\"apiVersion\":\"v1\",\"kind\":\"Namespace\",\"metadata\":{\"annotations\":{},\"labels\":{\"app.kubernetes.io/name\":\"knative-eventing\",\"app.kubernetes.io/version\":\"1.14.0\"},\"name\":\"knative-eventing\"}}\n"
    },
    "managedFields": [
      {
        "manager": "kubectl-client-side-apply",
        "operation": "Update",
        "apiVersion": "v1",
        "time": "2025-12-19T06:47:27Z",
        "fieldsType": "FieldsV1",
        "fieldsV1": {
          "f:metadata": {
            "f:annotations": {
              ".": {},
              "f:kubectl.kubernetes.io/last-applied-configuration": {}
            },
            "f:labels": {
              ".": {},
              "f:app.kubernetes.io/name": {},
              "f:app.kubernetes.io/version": {},
              "f:kubernetes.io/metadata.name": {}
            }
          }
        }
      },
      {
        "manager": "kube-controller-manager",
        "operation": "Update",
        "apiVersion": "v1",
        "time": "2025-12-21T06:55:20Z",
        "fieldsType": "FieldsV1",
        "fieldsV1": {
          "f:status": {
            "f:conditions": {
              ".": {},
              "k:{\"type\":\"NamespaceContentRemaining\"}": {
                ".": {},
                "f:lastTransitionTime": {},
                "f:message": {},
                "f:reason": {},
                "f:status": {},
                "f:type": {}
              },
              "k:{\"type\":\"NamespaceDeletionContentFailure\"}": {
                ".": {},
                "f:lastTransitionTime": {},
                "f:message": {},
                "f:reason": {},
                "f:status": {},
                "f:type": {}
              },
              "k:{\"type\":\"NamespaceDeletionDiscoveryFailure\"}": {
                ".": {},
                "f:lastTransitionTime": {},
                "f:message": {},
                "f:reason": {},
                "f:status": {},
                "f:type": {}
              },
              "k:{\"type\":\"NamespaceDeletionGroupVersionParsingFailure\"}": {
                ".": {},
                "f:lastTransitionTime": {},
                "f:message": {},
                "f:reason": {},
                "f:status": {},
                "f:type": {}
              },
              "k:{\"type\":\"NamespaceFinalizersRemaining\"}": {
                ".": {},
                "f:lastTransitionTime": {},
                "f:message": {},
                "f:reason": {},
                "f:status": {},
                "f:type": {}
              }
            }
          }
        },
        "subresource": "status"
      }
    ]
  },
  "spec": {},
  "status": {
    "phase": "Terminating",
    "conditions": [
      {
        "type": "NamespaceDeletionDiscoveryFailure",
        "status": "True",
        "lastTransitionTime": "2025-12-20T08:30:58Z",
        "reason": "DiscoveryFailed",
        "message": "Discovery failed for some groups, 1 failing: unable to retrieve the complete list of server APIs: cluster.core.oam.dev/v1alpha1: stale GroupVersion discovery: cluster.core.oam.dev/v1alpha1"
      },
      {
        "type": "NamespaceDeletionGroupVersionParsingFailure",
        "status": "False",
        "lastTransitionTime": "2025-12-20T08:31:00Z",
        "reason": "ParsedGroupVersions",
        "message": "All legacy kube types successfully parsed"
      },
      {
        "type": "NamespaceDeletionContentFailure",
        "status": "False",
        "lastTransitionTime": "2025-12-20T08:31:00Z",
        "reason": "ContentDeleted",
        "message": "All content successfully deleted, may be waiting on finalization"
      },
      {
        "type": "NamespaceContentRemaining",
        "status": "False",
        "lastTransitionTime": "2025-12-20T08:31:47Z",
        "reason": "ContentRemoved",
        "message": "All content successfully removed"
      },
      {
        "type": "NamespaceFinalizersRemaining",
        "status": "False",
        "lastTransitionTime": "2025-12-20T08:31:00Z",
        "reason": "ContentHasNoFinalizers",
        "message": "All content-preserving finalizers finished"
      }
    ]
  }
}删除 namespace 成功：命名空间 'knative-eventing' 已不存在
```

## 再次查看命名空间，已经被强制删除

```
[root@k8s-master ~]# kubectl get ns
NAME                         STATUS   AGE
cdi                          Active   171d
default                      Active   172d
kube-node-lease              Active   172d
kube-public                  Active   172d
kube-system                  Active   172d
kubevirt                     Active   171d
kubevirt-manager             Active   171d
kuboard                      Active   17h
monitoring                   Active   22h
tekton-dashboard             Active   43d
tekton-pipelines             Active   45d
tekton-pipelines-resolvers   Active   45d
```

## 🎉购书籍，做大牛🎉

院长书籍链接：

https://deanit.cn/DeanBooks/

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

**微信扫一扫赞赏作者**

继续滑动看下一个

院长技术

向上滑动看下一个