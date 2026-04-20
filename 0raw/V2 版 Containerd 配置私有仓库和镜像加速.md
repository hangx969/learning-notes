---
title: "V2 版 Containerd 配置私有仓库和镜像加速"
source: "https://mp.weixin.qq.com/s/STlTvq6ORBhJbr9qztKD7w"
author:
  - "[[jxwuqingyan]]"
published:
created: 2026-04-20
description: "前几天分享过一个 containerd 配置私有仓库的配置文章如何在containerd中添加自签证书私有镜像"
tags:
  - "clippings"
---
原创 jxwuqingyan *2026年4月20日 08:08*

前几天分享过一个 containerd 配置私有仓库的配置文章

[如何在containerd中添加自签证书私有镜像仓库](https://mp.weixin.qq.com/s?__biz=MjM5MzYzMTkyOQ==&mid=2451709488&idx=1&sn=09b00ef59f11b7ea5a5059ac9442a127&scene=21#wechat_redirect)

但那个是旧版本的了，这两天在折腾 GPU节点的时候安装了新版，发现配置稍有不同了，这里再分享下新版的配置。

![图片](https://mmbiz.qpic.cn/mmbiz_png/sHoMoMNgsR2icPuICECicB9yLB6S0BYzDsibAmlAOicoP1oVo53pBtHYCRdaTDBDJycNr94sytic0zOPl1OA7DHZlJ7V6ENpllOerIzdYVcHicpib4/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

1\. 主配置文件，主要配置 `config_path =“/xx/xx”`

```shell
$ cat /etc/containerd/config.toml

[plugins]
...
    [plugins."io.containerd.cri.v1.images".registry]
      config_path = "/etc/containerd/certs.d" #默认为空

    #  [plugins."io.containerd.cri.v1.images".registry.mirrors]
    #    [plugins."io.containerd.cri.v1.images".registry.mirrors."docker.io"]
    #      endpoint = ["https://docker.m.daocloud.io", "https://registry-1.docker.io"]
```

注意当 config\_path 不为空时，不能配置 mirrors！二者互斥！

2\. 配置私有仓库,以配置https:// `hub.test.local为例`

```shell
$ mkdir /etc/containerd/certs.d/hub.test.local
$ cp ca.crt /etc/containerd/certs.d/hub.test.local/ # 自签证书的根证书
$ cd /etc/containerd/certs.d/hub.test.local/
$ cat hosts.toml
server = "https://hub.test.local"

[host."https://hub.test.local"]
    capabilities = ["pull", "resolve", "push"]
    #skip_verify = true  # 忽略证书校验
  ca="/etc/containerd/certs.d/hub.easyops.online/ca.crt" # 指定根证书
[host."https://hub.test.local".header]
  Authorization = "Basic <TOKEN>" # 填入"用户名:密码"的base64值
```

3\. 测试镜像拉取

```shell
crictl pull hub.test.local/镜像名:标签
```

4\. 配置 mirror 镜像

1）目录结构

```shell
/etc/containerd/
├── config.toml
└── certs.d/
    ├── docker.io/            # Docker 官方（配加速）
    │   └── hosts.toml
    └── hub.test.local/       # 你的私有仓库
        └── hosts.toml
```

2）hosts.toml

```shell
server = "https://registry-1.docker.io"

# 国内镜像（按顺序尝试）
[host."https://docker.m.daocloud.io"]
  capabilities = ["pull", "resolve"]

[host."https://docker.1panel.live"]
  capabilities = ["pull", "resolve"]

# 最后回源官方
[host."https://registry-1.docker.io"]
  capabilities = ["pull", "resolve"]
```

3）测试

```shell
crictl pull busybox
```

好了，今天的分享就到这里了，希望对大家有所帮助。如果觉得还不错的话，各位看官动动小手点赞加关注，点击下面的链接可以直接进入本公众号，查看历史文章，谢谢大家^\_^

**微信扫一扫赞赏作者**

继续滑动看下一个

运维小白成长之路

向上滑动看下一个