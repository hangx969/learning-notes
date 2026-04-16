---
title: 深入剖析Kubernetes
tags:
  - cloud-computing
  - kubernetes
  - container
  - docker
  - namespace
  - cgroup
aliases:
  - K8s深入剖析
  - 深入剖析K8s
---

# 容器技术入门

## 1 从进程说开去

> [!abstract] 核心概念
> - 容器技术的兴起源于PaaS技术的普及
> - Docker公司发布的Docker项目具有里程碑式的意义，通过容器镜像，解决了应用打包的根本难题。
> - 容器技术的核心功能，就是通过约束、修改进程的动态表现，为其创造出一个”边界”。
> - 对于 Docker 等大多数 Linux 容器来说，**Cgroups** 技术是用来制造约束的主要手段，而 **Namespace** 技术则是用来修改进程视图的主要方法。

### Namespace

#### 原理

- Lab：
  - docker run -it: 告诉了 Docker 项目在启动容器后，需要给我们分配一个文本输入 / 输出环境，也就是 TTY，跟容器的标准输入相关联，这样我们就可以和这个 Docker 容器进行交互了。而 /bin/sh 就是我们要在 Docker 容器里运行的程序。
  - 容器里面执行ps，可以看到/bin/sh，就是这个容器内部的第 1 号进程（PID=1），而这个容器里一共只有两个进程在运行。这就意味着，前面执行的 /bin/sh，以及我们刚刚执行的 ps，已经被 Docker 隔离在了一个跟宿主机完全不同的世界当中。

![image-20230906213443065](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202309062134225.png)

- 解释：

  - 本来，每当我们在宿主机上运行了一个 /bin/sh 程序，操作系统都会给它分配一个进程编号，比如 PID=100。这个编号是进程的唯一标识，就像员工的工牌一样。所以 PID=100，可以粗略地理解为这个 /bin/sh 是我们公司里的第 100 号员工，而第 1 号员工就自然是比尔 · 盖茨这样统领全局的人物。
  - 而现在，我们要通过 Docker 把这个 /bin/sh 程序运行在一个容器当中。这时候，Docker就会在这个第 100 号员工入职时给他施一个“障眼法”，让他永远看不到前面的其他 99个员工，更看不到比尔 · 盖茨。这样，他就会错误地以为自己就是公司里的第 1 号员工。
  - 这种机制，其实就是对被隔离应用的进程空间做了手脚，使得这些进程只能看到重新计算过的进程编号，比如 PID=1。可实际上，他们在宿主机的操作系统里，还是原来的第 100 号进程。这种技术，就是 Linux 里面的 Namespace 机制。

- Namespace的Linux实现：

  - Namespace 的使用方式也非常有意思：它其实只是 Linux 创建新进程的一个可选参数。在 Linux 系统中创建线程的系统调用是 clone()，比如：

    ```C
    int pid = clone(main_function, stack_size, SIGCHLD, NULL);
    ```

    这个系统调用就会为我们创建一个新的进程，并且返回它的进程号 pid。

  - 而当我们用 clone() 系统调用创建一个新进程时，就可以在参数中指定 CLONE_NEWPID 参数，比如：

    ```C
    int pid = clone(main_function, stack_size, CLONE_NEWPID | SIGCHLD, NULL);
    ```

    - 这时，新创建的这个进程将会“看到”一个全新的进程空间，在这个进程空间里，它的 PID是 1。之所以说“看到”，是因为这只是一个“障眼法”，在宿主机真实的进程空间里，这个进程的 PID 还是真实的数值，比如 100。

  - 除了我们刚刚用到的 PID Namespace，Linux 操作系统还提供了 Mount、UTS、IPC、Network 和 User 这些 Namespace，用来对各种不同的进程上下文进行“障眼法”操作。
    - 比如，Mount Namespace，用于让被隔离进程只看到当前 Namespace 里的挂载点信息；Network Namespace，用于让被隔离进程看到当前 Namespace 里的网络设备和配置。

- Docker容器的本质

  - Docker 容器实际上是在创建容器进程时，指定了这个进程所需要启用的一组 Namespace 参数。这样，容器就只能“看”到当前 Namespace所限定的资源、文件、设备、状态，或者配置。而对于宿主机以及其他不相关的程序，它就完全看不到了。
  - 所以说，容器，其实是一种特殊的进程而已。跟真实存在的虚拟机不同，在使用Docker 的时候，并没有一个真正的“Docker 容器”运行在宿主机里面。Docker 项目帮助用户启动的，还是原来的应用进程，只不过在创建这些进程时，Docker 为它们加上了各种各样的 Namespace 参数。
  - 这时，这些进程就会觉得自己是各自 PID Namespace 里的第 1 号进程，只能看到各自Mount Namespace 里挂载的目录和文件，只能访问到各自 Network Namespace 里的网络设备，就仿佛运行在一个个“容器”里面，与世隔绝。

#### Namespace延伸出的容器的优势

- 与虚拟机对比的优势：
  - 在虚拟机与容器技术的对比图里，不应该把 Docker Engine 或者任何容器管理工具放在跟 Hypervisor 相同的位置，因为它们并不像 Hypervisor 那样对应用进程的隔离环境负责，也不会创建任何实体的“容器”，真正对隔离环境负责的是宿主机操作系统本身。所以，在这个对比图里，我们应该把 Docker 画在跟应用同级别并且靠边的位置。这意味着，用户运行在容器里的应用进程，跟宿主机上的其他进程一样，都由宿主机操作系统统一管理，只不过这些被隔离的进程拥有额外设置过的 Namespace 参数。而 Docker 项目在这里扮演的角色，更多的是旁路式的辅助和管理工作。
  - 这样的架构也解释了为什么 Docker 项目比虚拟机更受欢迎的原因。
    - 这是因为，使用虚拟化技术作为应用沙盒，就必须要由 Hypervisor 来负责创建虚拟机，这个虚拟机是真实存在的，并且它里面必须运行一个完整的 Guest OS 才能执行用户的应用进程。这就不可避免地带来了额外的资源消耗和占用。
    - 一个运行着 CentOS 的 KVM 虚拟机启动后，在不做优化的情况下，虚拟机自己就需要占用 100~200 MB 内存。此外，用户应用运行在虚拟机里面，它对宿主机操作系统的调用就不可避免地要经过虚拟化软件的拦截和处理，这本身又是一层性能损耗，尤其对计算资源、网络和磁盘 I/O 的损耗非常大。
    - 而相比之下，容器化后的用户应用，却依然还是一个宿主机上的普通进程，这就意味着这些因为虚拟化而带来的性能损耗都是不存在的；而另一方面，使用 Namespace 作为隔离手段的容器并不需要单独的 Guest OS，这就使得容器额外的资源占用几乎可以忽略不计。

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202309062149068.png" alt="image-20230906214926967" style="zoom:50%;" />

#### Namespace的弊端

> [!warning] 隔离不彻底
> 基于 Linux Namespace 的隔离机制相比于虚拟化技术也有很多不足之处，其中最主要的问题就是：隔离得不彻底。
> 首先，既然容器只是运行在宿主机上的一种特殊的进程，那么多个容器之间使用的就还是同一个宿主机的操作系统内核。

- 尽管你可以在容器里通过 Mount Namespace 单独挂载其他不同版本的操作系统文件，比如 CentOS 或者 Ubuntu，但这并不能改变**共享宿主机内核**的事实。
  - 这意味着，如果你要在 Windows 宿主机上运行 Linux 容器，或者在低版本的 Linux 宿主机上运行高版本的Linux 容器，都是行不通的。

> [!warning] 不能被Namespace化的资源
> 其次，在 Linux 内核中，有很多资源和对象是不能被 Namespace 化的，最典型的例子就是：时间。

- 如果你的容器中的程序使用 settimeofday(2) 系统调用修改了时间，整个宿主机的时间都会被随之修改，这显然不符合用户的预期。相比于在虚拟机里面可以随便折腾的自由度，在容器里部署应用的时候，“什么能做，什么不能做”，就是用户必须考虑的一个问题。

---

## 2 隔离与限制

### Cgroup

> [!info] Cgroups
> - Linux Cgroups 就是 Linux 内核中用来为进程设置资源限制的一个重要功能。
> - 它最主要的作用，就是限制一个进程组能够使用的资源上限，包括 CPU、内存、磁盘、网络带宽等等。
> - Cgroups 还能够对进程进行优先级设置、审计，以及将进程挂起和恢复等操作。

![image-20240725224401832](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202407252244962.png)

#### 原理

- Linux中，Cgroup给用户暴露出来的操作接口是文件系统，即以文件和目录的形式，组织在操作系统得/sys/fs/cgroup下.

  ```bash
  mount -t cgroup
  ```

  ![image-20230907205037977](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202309072050102.png)

  - /sys/fs/cgroup 下面有很多诸如 cpuset、cpu、 memory 这样的子目录，也叫子系统。这些都是我这台机器当前可以被 Cgroups 进行限制的资源种类。而在子系统对应的资源种类下，你就可以看到该类资源具体可以被限制的方法。

    ```bash
    ls /sys/fs/cgroup/cpu
    ```

    ![image-20230907211418973](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202309072114036.png)

  - 这些配置文件可以用来配置限制，如cfs_period 和 cfs_quota 这样的关键词。这两个参数需要组合使用，可以用来限制进程在长度为cfs_period 的一段时间内，只能被分配到总量为 cfs_quota 的 CPU 时间。

  - 如何使用呢，需要在子目录里面建一个目录。比如，需要进入到/sys/fs/cgroup/cpu

    ```bash
    mkdir container #这个目录就称为一个控制组
    ls container/ #操作系统自动在控制组里面生成了资源限制文件
    ```

    查看目前的CPU限制，再把对应参数写到控制文件中：

    ```bash
    cat /sys/fs/cgroup/cpu/container/cpu.cfs_quota_us
    -1
    cat /sys/fs/cgroup/cpu/container/cpu.cfs_period_us
    100000
    # container 控制组里的 CPU quota 还没有任何限制（即：-1），CPU period 则是默认的 100 ms（100000 us）
    ```

    ```bash
    echo 20000 > /sys/fs/cgroup/cpu/container/cpu.cfs_quota_us
    #cpu.cfs_period_us = 100 ms，cpu.cfs_quota_us=20 ms，每 100 ms 的时间里，被该控制组限制的进程只能使用 20 ms 的 CPU 时间，也就是说这个进程只能使用到 20% 的 CPU 带宽。
    ```

    ```bash
    echo 226 > /sys/fs/cgroup/cpu/container/tasks
    # 把被限制的进程的 PID 写入 container 组里的 tasks 文件，上面的设置就会对该进程生效了
    ```

- 对于 Docker 等 Linux 容器项目来说，它们只需要在每个子系统下面，为每个容器创建一个控制组（即创建一个新目录），然后在启动容器进程之后，
  把这个进程的 PID 填写到对应控制组的 tasks 文件中就可以了。

  - 而至于在这些控制组下面的资源文件里填上什么值，就靠用户执行 docker run 时的参数指定了，比如

    ```bash
    docker run -it --cpu-period=100000 --cpu-quota=20000 ubuntu /bin/bash
    ```

#### 容器与进程

- 由于一个容器的本质就是一个进程，用户的应用进程实际上就是容器里 PID=1 的进程，也是其他后续创建的所有进程的父进程。
- 这就意味着，在一个容器中，你没办法同时运行两个不同的应用，除非你能事先找到一个公共的 PID=1 的程序来充当两个不同应用的父进程，这也是为什么很多人都会用 systemd 或者 supervisord 这样的软件来代替应用本身作为容器的启动进程。

#### cgroup的不足

- Cgroups 对资源的限制能力也有很多不完善的地方，被提及最多的自然是 /proc 文件系统的问题：，Linux 下的 /proc 目录存储的是记录当前内核运行状态的一系列特殊文件，用户可以通过访问这些文件，查看系统以及当前正在运行的进程的信息，比如 CPU 使用情况、内存占用率等，这些文件也是top 指令查看系统信息的主要数据来源。
  - 你如果在容器里执行 top 指令，就会发现，它显示的信息居然是宿主机的 CPU 和内存数据，而不是当前容器的数据。
  - 造成这个问题的原因就是，/proc 文件系统并不知道用户通过 Cgroups 给这个容器做了什么样的资源限制，即：/proc 文件系统不了解 Cgroups限制的存在。
  - lxcfs工具的出现解决了这个问题：[lxcfs 是什么？ lxcfs 实现对容器资源视图隔离的最佳实践 - 掘金 (juejin.cn)](https://juejin.cn/post/6847902216511356936)
- cgroup只能限制上限，不能规定下限。这就是为啥需要kubernetes容器编排。

---

## 3 深入理解容器镜像

### Mount namespace

- mount namaspace创建一个完全独立的文件系统，用mount namespace挂载的进程就可以在自己的隔离目录下（比如 /tmp）下操作，完全不受到宿主机以及其他容器的影响。
- 但是mount namespace改变的是容器进程对挂载点的认知，只有在挂载操作发生之后，进程的视图才会被改变。在此之前，新容器会继承宿主机的各个挂载点。

### chroot

- chroot可以实现容器进程重新挂载整个根目录，到指定的位置。

- 假设有一个$HOME/test目录，想把他作为一个/bin/bash进程的根目录：

  ```bash
  chroot $HOME/test /bin/bash
  #告诉操作系统，使用$HOME/test，作为/bin/bash进程的根目录
  ls /
  #返回的会是$HOME/test里面的内容，而不是宿主机/的内容。
  ```

- 对于被chroot的进程来说，并不会感受到自己的根目录被修改成$HOME/test了。

- 实际上，mount namespacec就是基于chroot改良而来的。

### rootfs

- 一般会在chroot到的容器根目录上挂载一个完成测操作系统文件系统，比如Ubuntu 18.04 ISO。这样在容器启动后，执行ls / 就能看到根目录下的内容。
- 这个挂载到容器的根目录上，用来为容器进程提供隔离后执行环境的文件系统，就称为容器镜像，也就是rootfs。
- 需要明确的是，rootfs只是一个操作系统包含的文件、配置、目录；并不包含操作系统内核。
  - 在Linux中，这两部分是分开存放的，操作系统只有在开机启动时才会加载指定版本的内核镜像。
  - 所以rootfs只包含躯壳，没包含灵魂。实际上，同一台宿主机上的容器，都共享同一个宿主机的操作系统内核。

> [!tip] 容器核心三步
> 1. 启用Linux Namespace配置
> 2. 设置指定的Cgroup参数
> 3. 切换进程的根目录（chroot）
>
> Docker 项目在最后一步的切换上会优先使用pivot_root 系统调用，如果系统不支持，才会使用 chroot。这两个系统调用虽然功能类似，但是也有细微的区别。

### Union FS / Layer

> [!tip] 参考文章
> - [Union FS 教程](https://mp.weixin.qq.com/s/0enVkNjDMDh68WMNb2sEpQ)

- 容器直接打包整个操作系统作为应用的依赖库，实现了一致性。问题是：每一次打包容器，都需要重复制作rootfs吗？答案是：不需要。
- 一个base rootfs，以增量的方式做修改，制作镜像的每一步操作，都生成一个layer，也就是一个增量rootfs。所有人只需要维护基于base rootfs的增量内容即可。不同的layer通过UnionFS挂载到同一个目录。

- 以Ubuntu 1604和Docker CE 1805为例，默认使用的是AuFS这个UnionFS，可以通过docker info来查看。

  - 对于AuFS而言，核心目录结构位于 /var/lib/docker/aufs/diff/\<layer id\>中，镜像的层都放在里面。

  - 镜像会由多个layer组成，每一层都是镜像文件和目录的一部分。拉取、使用这个镜像时，docker会把这些layer联合挂载到统一的挂载点上：

    /var/lib/docker/aufs/mnt/

- 容器的rootfs由三部分组成：（以上述Ubuntu image为例）

  <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202309121652663.png" alt="image-20230912165209483" style="zoom:50%;" />

  1. 只读层（ro+wh）

     以增量的形式，保存了Ubuntu操作系统的一部分。

  2. init层（ro+wh）

     - Init 层是Docker单独生成的一个内部层，专门用来存放 /etc/hosts、/etc/resolv.conf 等信息。
     - 这些文件本来属于Ubuntu的镜像一部分，但是会被用户在启动容器时做修改；但是仅希望对当前容器生效，不希望后续被commit到dockerhub里面。用户后续的docker commit是不会包含-init层的。

  3. 可读写层（rw）

     - 写入：在没有写入文件之前，这个目录是空的；一旦在容器里面做了写操作，产生的内容就会以增量的形式出现在这个层中。
     - 如果要删除只读层的一个文件：Aufs会在rw层创建一个whiteout文件，把只读层的文件遮挡起来。（假如删除只读层的foo文件，那么会在rw层创建一个.wh.foo的文件。当联合挂载之后，foo就会被.wh.foo遮挡起来。）
     - 如果想要修改只读层的文件：需要知道相同的文件，上层会覆盖掉下层。首先会从上到下检查有没有这个文件，找到之后，就复制到可读写层里面进行修改。修改的结果就会作用到下层的文件。这就叫copy-on-write。

### Lab - 制作容器镜像并上传

- 编写python代码

  ```python
  # coding=utf-8
  from flask import Flask
  import socket
  import os
  
  app = Flask(__name__)
  
  # 如果当前环境中有 NAME 这个环境变量，就打印到Hello后；否则打印hello world。最后再打印出hostname
  @app.route('/')
  def hello():
      html = "<h3>Hello {name}!</h3>" \
             "<b>Hostname:</b> {hostname}<br/>"
      return html.format(name=os.getenv("NAME", "world"), hostname=socket.gethostname())
  
  if __name__ == "__main__":
      app.run(host='0.0.0.0', port=80)
  ```

- 编写requirments.txt

  这是应用的依赖

  ```C
  Flask
  ```

- 编写dockerfile

  ```dockerfile
  # 使用官方提供的 Python 开发镜像作为基础镜像
  FROM python:2.7-slim
  # 将工作目录切换为 /app 
  #（使用 WORKDIR 指令可以来指定工作目录（或者称为当前目录），以后各层的当前目录就被改为指定的目录，如该目录不存在，WORKDIR 会帮你建立目录。https://blog.csdn.net/qq_35423190/article/details/131471048）
  WORKDIR /app
  # 将当前目录下的所有内容复制到 /app 下
  ADD . /app
  # 使用 pip 命令安装这个应用所需要的依赖
  RUN pip install --trusted-host pypi.python.org -r requirements.txt
  # 允许外界访问容器的 80 端口
  EXPOSE 80
  # 设置环境变量
  ENV NAME HangXu
  # 设置容器进程为：python app.py，即：这个 Python 应用的启动命令。
  # 这里，app.py 的实际路径是 /app/app.py。所以，CMD [“python”, “app.py”] 等价于"docker run python app.py"。
  CMD ["python", "python-helloworld-app.py"]
  ```
  
  > [!note] Dockerfile 原语说明
  > - Dockerfile 的设计思想，是使用一些标准的原语（即大写的词语），描述我们所要构建的 Docker 镜像。并且这些原语，都是按顺序处理的。
  > - 在使用 Dockerfile 时，你可能还会看到一个叫作 ENTRYPOINT 的原语。实际上，它和 CMD 都是 Docker 容器进程启动所必需的参数，完整执行格式是：”ENTRYPOINT CMD”。
  > - 但是，默认情况下，Docker 会为你提供一个隐含的 ENTRYPOINT，即：**/bin/sh -c**。所以，在不指定 ENTRYPOINT 时，比如在我们这个例子里，实际上运行在容器里的完整进程是：/bin/sh -c “python app.py”，即 CMD 的内容就是 ENTRYPOINT 的参数。
  > - Dockerfile 里的原语并不都是指对容器内部的操作。就比如 ADD，它指的是把当前目录（即 Dockerfile 所在的目录）里的文件，复制到指定容器内的目录当中。
  
- 制作镜像

  ```bash
  docker build -t python-helloworld-app .
  ```

  - docker build 会自动加载当前目录下的 Dockerfile 文件，然后按照顺序，执行文件中的原语。
  - 而这个过程，实际上可以等同于 Docker 使用基础镜像启动了一个容器，然后在容器中依次执行Dockerfile 中的原语。
  - Dockerfile 中的每个原语执行后，都会生成一个对应的镜像层。即使原语本身并没有明显地修改文件的操作（比如，ENV 原语），它对应的层也会存在。只不过在外界看来，这个层是空的。

- 查看镜像

  ```bash
  docker images ls
  ```

- 启动镜像

  ```bash
  docker run -p 4000:80 python-helloworld-app
  #将容器内的80端口映射到宿主机4000端口上。只要访问宿主机的4000端口，就能访问到容器的返回结果。
  #不需要加启动命令，因为dockerfile中已经定义了启动命令：python app.py
  ```

- 测试镜像

  ```bash
  curl http://localhost:4000
  #<h3>Hello World!</h3><b>Hostname:</b> bb9c14f75291<br/>
  
  docker exec -it /bin/sh
  #进入到容器内部
  ```

- 上传到ACR：xhacrtest.azurecr.cn

  ```bash
  docker tag python-helloworld-app xhacrtest.azurecr.cn/python-helloworld-app:v1
  az acr login -n xhacrtest.azurecr.cn
  docker push xhacrtest.azurecr.cn/python-helloworld-app:v1
  ```

- 部署到AKS

  ```bash
  kubectl create deployment python-helloworld-app --image=xhacrtest.azurecr.cn/python-helloworld-app:v1 --port=80 --replicas=3
  
  kubectl expose deployment python-helloworld-app --port=80 --target-port=80 --type=LoadBalancer
  # pod通过lb暴露服务：
  #NAME                    TYPE           CLUSTER-IP     EXTERNAL-IP      PORT(S)        AGE
  #python-helloworld-app   LoadBalancer   10.0.166.200   52.131.217.15    80:31265/TCP   13m
  # 可以进入到node上，通过两种方式访问：
  # 访问pod ip+pod 暴露的端口：curl http://10.0.166.200:80
  # 访问node的localhost+node暴露的高位端口：curl http://localhost:31265
  # 也可以访问lb的公网IP：curl http://52.131.217.15
  ```

### docker exec的原理

- Linux Namespace 创建的隔离空间虽然看不见摸不着，但一个进程的 Namespace 信息在宿主机上是确确实实存在的，并且是以一个文件的方式存在。

- 如何查看：

  ```bash
  docker inspect --format '{{ .State.Pid }}' bb9c14f75291 #查看这个容器进程在宿主机上的pid
  #3639347
  
  ls -l /proc/3639347/ns
  #查看宿主机的 proc 文件，看到这个 25686 进程的所有 Namespace 对应的文件：
  total 0
  lrwxrwxrwx. 1 root root 0 Sep 12 21:38 cgroup -> 'cgroup:[4026531835]'
  lrwxrwxrwx. 1 root root 0 Sep 12 21:38 ipc -> 'ipc:[4026532231]'
  lrwxrwxrwx. 1 root root 0 Sep 12 20:51 mnt -> 'mnt:[4026532229]'
  lrwxrwxrwx. 1 root root 0 Sep 12 20:51 net -> 'net:[4026532308]'
  lrwxrwxrwx. 1 root root 0 Sep 12 20:51 pid -> 'pid:[4026532232]'
  lrwxrwxrwx. 1 root root 0 Sep 12 21:38 pid_for_children -> 'pid:[4026532232]'
  lrwxrwxrwx. 1 root root 0 Sep 12 20:51 user -> 'user:[4026531837]'
  lrwxrwxrwx. 1 root root 0 Sep 12 21:38 uts -> 'uts:[4026532230]'
  ```

  - 一个进程的每种 Linux Namespace，都在它对应的 /proc/[进程号]/ns 下有一个对应的虚拟文件，并且链接到一个真实的 Namespace 文件上。
  - 这也就意味着：一个进程，可以选择加入到某个进程已有的 Namespace 当中，从而达到“进入”这个进程所在容器的目的，这正是 docker exec 的实现原理。这个操作所依赖的，乃是一个名叫 setns() 的 Linux 系统调用。

### dockerinit容器进程

- Docker 创建的一个容器初始化进程(dockerinit)，而不是应用进程 (ENTRYPOINT + CMD)。
- dockerinit 会负责完成根目录的准备、挂载设备和目录、配置 hostname 等一系列需要在容器内进行的初始化操作。
- 最后，它通过 execv() 系统调用，让应用进程取代自己，成为容器里的 PID=1 的进程。

### Volume

> [!question] Volume 解决的问题
> - 容器内的文件、目录，如何让宿主机读取到？
> - 宿主机的文件、目录，如何让容器读取到？
>
> Volume 机制，允许你将宿主机上指定的目录或者文件，挂载到容器里面进行读取和修改操作。

- Docker支持两种挂载volume的方式：

  ```bash
  docker run -v /test ... 
  docker run -v /home:/test ...
  ```

  - 作用都是相同的：会将宿主机的一个目录挂载到容器内使用。
    - docker run -v /test：不指定宿主机目录，Docker 就会默认在宿主机上创建一个临时目录 /var/lib/docker/volumes/[VOLUME_ID]/_data，然后把它挂载到容器的 /test 目录上。
    - docker run -v /home:/test：Docker 就直接把宿主机的 /home 目录挂载到容器的 /test 目录上。

- 挂载的机制：
  - 当容器进程被创建之后，尽管开启了 Mount Namespace，但是在它执行 chroot（或者 pivot_root）之前，容器进程一直可以看到宿主机上的整个文件系统。
  - 而宿主机上的文件系统，也自然包括了我们要使用的容器镜像。这个镜像的各个层，保存在/var/lib/docker/aufs/diff 目录下，在容器进程启动后，它们会被联合挂载在**/var/lib/docker/aufs/mnt/**目录中，这样容器所需的 rootfs 就准备好了。
  - 只需要在 rootfs 准备好之后，在执行 chroot 之前，把 Volume 指定的宿主机目录（比如 /home 目录），挂载到指定的容器目录（比如 /test目录）**在宿主机上对应的目录**（即 /var/lib/docker/aufs/mnt/[可读写层 ID]/test）上，这个 Volume 的挂载工作就完成了。

## 4 谈谈kubernetes的本质

> 对于容器来说由两部分组成
>
> 1. 一组联合挂载在 /var/lib/docker/aufs/mnt 上的 rootfs，这一部分我们称为“容器镜像”（Container Image），是容器的静态视图。
> 2. 一个由 Namespace+Cgroups 构成的隔离环境，这一部分我们称为“容器运行时”（Container Runtime），是容器的动态视图。
>
> 作为一名开发者，并不关心容器运行时，在开发-测试=发布过程中，承载信息的是容器镜像。正因为如此，docker项目出现不久，就走向了容器编排技术的上层建筑。

### kubernetes组件简介

![image-20230916132922210](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202309161329375.png)

- 在 Kubernetes 项目中，kubelet 主要负责同容器运行时（比如 Docker 项目）打交道。而这个交互所依赖的，是一个称作 **CRI（Container Runtime Interface）的远程调用接口**，这个接口定义了容器运行时的各项核心操作。
  - 比如：启动一个容器需要的所有参数。这也是为何 Kubernetes 并不关心你部署的是什么容器运行时、使用的什么技术实现，只要你的这个容器运行时能够运行标准的容器镜像，它就可以通过实现 CRI 接入到Kubernetes当中。

- 而具体的容器运行时，比如 Docker 项目，则一般通过 OCI 这个容器运行时规范同底层的Linux 操作系统进行交互
  - 即：把 CRI 请求翻译成对 Linux 操作系统的调用（操作 Linux Namespace 和 Cgroups 等）。

- kubelet 还通过 gRPC 协议同一个叫作 Device Plugin 的插件进行交互。这个插件是 Kubernetes 项目用来管理 GPU 等宿主机物理设备的主要组件，也是基于Kubernetes 项目进行机器学习训练、高性能作业支持等工作必须关注的功能。

- kubelet 的另一个重要功能，则是调用网络插件和存储插件为容器配置网络和持久化存储。这两个插件与 kubelet 进行交互的接口，分别是 CNI Container Networking Interface）和 CSI（Container Storage Interface）。

### K8S解决的本质问题

- Kubernetes 项目要着重解决的问题，则来自于 Borg 的研究人员在论文中提到的一个非常重要的观点：
  - 运行在大规模集群中的各种任务之间，实际上存在着各种各样的关系。这些关系的处理，才是作业编排和管理系统最困难的地方。
  - 比如，一个Web 应用与数据库之间的访问关系，一个负载均衡器和它的后端服务之间的代理关系，一个门户应用与授权组件之间的调用关系。
- 在容器技术普及之前，传统虚拟机环境对这种关系的处理方法都是比较“粗粒度”的。你会经常发现很多功能并不相关的应用被一股脑儿地部署在同一台虚拟机中，只是因为它们之间偶尔会互相发起几个 HTTP 请求。
  - 更常见的情况则是，一个应用被部署在虚拟机里之后，你还得手动维护很多跟它协作的守护进程（Daemon），用来处理它的日志搜集、灾难恢复、数据备份等辅助工作。
- 容器技术普及之后，那些原先拥挤在同一个虚拟机里的各个应用、组件、守护进程，都可以被分别做成镜像，然后运行在一个个专属的容器中。它们之间互不干涉，拥有各自的资源配额，可以被调度在整个集群里的任何一台机器上。而这，正是一个 PaaS 系统最理想的工作状态，也是所谓“微服务”思想得以落地的先决条件。

### 声明式API

- 在 Kubernetes 项目中，我们所推崇的使用方法是：

  - 首先，通过一个“编排对象”，比如 Pod、Job、CronJob 等，来描述你试图管理的应用；
  - 然后，再为它定义一些“服务对象”，比如 Service、Secret、Horizontal Pod Autoscaler 等。这些对象，会负责具体的平台级功能。

  就是所谓的“声明式 API”。这种 API 对应的“编排对象”和“服务对象”，都是 Kubernetes 项目中的 API 对象（API Object）。这就是 Kubernetes 最核心的设计理念。

### 编排和调度

- 实际上，过去很多的集群管理项目（比如 Yarn、Mesos，以及 Swarm）所擅长的，都是把一个容器，按照某种规则，放置在某个最佳节点上运行起来。这种功能，我们称为“调度”。
- 而 Kubernetes 项目所擅长的，是按照用户的意愿和整个系统的规则，完全自动化地处理好容器之间的各种关系。这种功能，就是我们经常听到的一个概念：编排。

# 5 k8s集群搭建实践

## kubeadm

- 为简化pod部署，社区发起了一个独立的部署工具：kubeadm。通过kubeadm init和kubeadm join两条简单指令来完成集群部署。

### 工作原理

- k8s每一个组件都是需要被执行的单独的二进制文件。如果不用二进制文件，是否能用容器来部署k8s组件？
  - 其他的都可以，但是kubelet无法被容器化：因为kubelet负责跟容器运行时打交道，还负责配置容器网络、管理容器数据卷。即需要直接操作宿主机。
  - 如果kubelet运行在一个容器里面，直接操作宿主机就会变得很麻烦：例如比如用户在容器中挂载NFA，kubelet需要在宿主机指定目录上挂载NFS远程目录。如果kubelet运行在容器中，就无法直接操作宿主机文件系统。
- kubeadm选择了一种妥协方案：
  - 把kubelet运行在宿主机上，然后用容器来部署其他的k8s组件。所以使用kubeadm的第一步就是在机器上手动安装kubeadm、kubelet、kubectl三个二进制文件。apt-get install kubeadm即可安装打包好的安装包。

### 工作流程

1. Preflight check：预先检查前置条件
2. 生成k8s对外提供服务所需的证书和对应目录。
   - k8s对外提供服务需要通过https访问apiserver，需要配置证书。
   - 另外用户通过kubectl获取容器日志等streaming操作时，需要通过apiserver向kubelet发起请求。这个连接也需要是安全的。
   - 证书生成之后，kubeadm会为其他组件生成访问apiserver的配置文件，路径是：/etc/kubernetes/conf。这些文件里面记录的是，当前这个Master 节点的服务器地址、监听端口、证书目录等信息。这样，对应的客户端（比如 scheduler，kubelet 等），可以直接加载相应的文件，使
     用里面的信息与 kube-apiserver 建立安全连接。
3. 会为master组生成pod配置文件，apiserver、controller-manager、kube-scheduler、etcd，都会被用pod方式部署。
   - 这个时候k8s集群尚未生成，不是使用docker run来启动容器的。而是利用了特殊的容器启动机制“Static pod”，允许将需要部署的pod的yaml文件，放在一个指定的目录里，当这个节点上的kubelet启动时就会自动检查这个目录，加载所有的pod yaml文件启动他们。
   - kubeadm中，这个目录是：/etc/kubernetes/manifests
4. kubeadm为集群生成一个bootstrap token：只要持有这个token，任何一个安装了kubelet和kubeadm的节点，都可以通过kubeadm join加入到这个集群当中。（这个token会在kubeadm init结束后被打印出来）
5. token生成之后，kubeadm会将master节点的重要信息，通过configmap方式保存在etcd中，以供后续部署节点使用。这个configmap的名字是cluster-info。
6. 安装默认插件：kube-proxy和DNS必须安装。

> - kubeadm的源代码就在kubernetes/cmd/kubeadm下，其中/app/phases文件夹下面的代码就代表了以上的每一个步骤
>
>   （？在实验环境没找到）

### yaml文件与容器化应用

以下面的yaml文件为例：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  selector:
   matchLabels:
     app: nginx
replicas: 2
template: #以下都是pod的模板
  metadata:
    labels:
      app: nginx
  spec:
    containers:
    - name: nginx
      image: nginx:1.7.9
      ports:
      - containerPort: 80
```

- 一个yaml文件就是一个API对象。使用一种控制器对象（deployment）控制另一种API对象（pod）就称为控制器模式。而deployment就是controller。

- 一个 Kubernetes 的 API 对象的定义，大多可以分为 Metadata 和 Spec 两个部分。前者存放的是这个对象的元数据，对所有 API 对象来说，这一部分的字段和格式基本上是一样的；而后者存放的，则是属于这个对象独有的定义，用来描述它所要表达的功能。

  - metadata是API对象的标识。
  - 与metadata同级的字段annotation，专门用来携带k-v格式的内部信息，供k8s使用的，一般是在pod运行后加到这个API对象上。

  # 6 容器编排和作业管理

## 为什么需要pod

> - 容器的本质就是云计算系统中的进程，容器镜像就是这个系统中的.exe安装包；而k8s就是操作系统。

### pod的实现原理

- POD只是一个逻辑概念，其实是一组共享了Network namespace和volume的容器。k8s真正处理的，还是host上linux容器的namespace和cgroups，而并不存在一个pod的边界或者隔离环境。

  - 一个pod有A、B两个容器，等同于容器A共享容器B的网络和volume。但是如果真是这样，那就必须让B先启动，A才能启动。这样容器间就不是对等关系而是拓扑关系了。

  - k8s中，pod的实现需要使用一个中间容器，这个容器叫作 Infra 容器。在这个 Pod 中，Infra 容器永远都是第一个被创建的容器，而其他用户定义的容器，则通过 Join Network Namespace 的方式，与 Infra 容器关联在一起。

    <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310092139421.png" alt="image-20231009213946196" style="zoom:33%;" />
  
  - 这个 Pod 里有两个用户容器 A 和 B，还有一个 Infra 容器。在Kubernetes 项目里，Infra 容器一定要占用极少的资源，所以它使用的是一个非常特殊的镜像，叫作：k8s.gcr.io/pause。这个镜像是一个用汇编语言编写的、永远处于“暂停”状态的容器，解压后的大小也只有 100~200 KB左右。
  - 这就意味着容器A、B在network层面：
    - 可以直接使用 localhost 进行通信；
    - 它们看到的网络设备跟 Infra 容器看到的完全一样；
    - 一个 Pod 只有一个 IP 地址，也就是这个 Pod 的 Network Namespace 对应的 IP 地址；
    - 当然，其他的所有网络资源，都是一个 Pod 一份，并且被该 Pod 中的所有容器共享；
    - Pod 的生命周期只跟 Infra 容器一致，而与容器 A 和 B 无关
    - 而对于同一个 Pod 里面的所有用户容器来说，它们的进出流量，也可以认为都是通过 Infra容器完成的。这一点很重要，因为将来如果你要为 Kubernetes 开发一个网络插件时，应该重点考虑的是如何配置Infra 容器的 Network Namespace，而不是每一个用户容器如何使用你的网络配置，这是没有意义的。
  - 容器A、B在volume层面：
    - k8s只要把volume定义在pod层面即可，
    - 这样，一个 Volume 对应的宿主机目录对于 Pod 来说就只有一个，Pod 里的容器只要声明挂载这个 Volume，就一定可以共享这个 Volume 对应的宿主机目录。

### pod的意义-容器设计原理-sidecar

> Pod 这种“超亲密关系”容器的设计思想，实际上就是希望，当用户想在一个容器里跑多个功能并不相关的应用时，应该优先考虑它们是不是更应该被描述成一个 Pod 里的多个容器。

1. 一个典型例子：有一个 Java Web 应用的 WAR 包，它需要被放在 Tomcat 的 webapps 目录下运行起来。

- 如果把war包整合到tomcat镜像里，每次更新war包或者tomcat都得重做镜像，麻烦。

- 如果只发布一个tomcat，用volume的方式把war包的目录挂载进来，也需要维护一个存储服务器。

- 有了pod，就好解决了：把war包和tomcat分别做成镜像，作为同一个pod的两个容器。配置如下：

  ```yaml
  apiVersion: v1
  kind: Pod
  metadata:
    name: javaweb-2
  spec:
    initContainers:
    - image: geektime/sample:v2
      name: war
      command: ["cp", "/sample.war", "/app"]
      volumeMounts:
      - mountPath: /app
        name: app-volume
    containers:
    - image: geektime/tomcat:7.0
      name: tomcat
      command: ["sh","-c","/root/apache-tomcat-7.0.42-v2/bin/start.sh"]
      volumeMounts:
      - mountPath: /root/apache-tomcat-7.0.42-v2/webapps
        name: app-volume
      ports:
      - containerPort: 8080
        hostPort: 8001
    volumes:
    - name: app-volume
      emptyDir: {}
  ```

  - 宿主机上声明了一个name为app-volume的volume，两个容器都挂载了这个volume。
  - war包的镜像是initContainer，在 Pod 中，所有 Init Container 定义的容器，都会比 spec.containers 定义的用户容器先启动。并且，Init Container 容器会按顺序逐一启动，而直到它们都启动并且退出了，用户容器才会启动。
  - 所以，这个 Init Container 类型的 WAR 包容器启动后，执行"cp /sample.war/app"，把WAR包拷贝到/app目录下，然后退出。
  - tomcat容器同样挂载了这个volume，它的webapp目录下就一定会有war包文件。因为volume是两个容器共享的。

- 上述例子就是容器设计模式中的side-car。sidecar 指的就是我们可以在一个 Pod 中，启动一个辅助容器，来完成一些独立于主进程（主容器）之外的工作。

2. 第二个例子是容器的日志收集

- 比如有一个应用，不断地把日志文件输出到容器的 /var/log 目录中。可以把Pod里的 Volume 挂载到应用容器的 /var/log 目录上，同时在这个 Pod 里同时运行一个 sidecar 容器，它也声明挂载同一个 Volume 到自己的 /var/log 目录上。
- 接下来 sidecar 容器就只需要做一件事儿，那就是不断地从自己的 /var/log 目录里读取日志文件，转发到 MongoDB 或者 Elasticsearch 中存储起来。这样，一个最基本的日志收集工作就完成了。

3. Pod 的另一个重要特性是，它的所有容器都共享同一个 NetworkNamespace。这就使得很多与 Pod 网络相关的配置和管理，也都可以交给 sidecar 完
   成，而完全无须干涉用户容器。这里最典型的例子莫过于 Istio 这个微服务治理项目了。

### pod基本概念

> 可以把pod看作是传统环境里面的“机器”，而容器是这个机器里面的用户程序。所以，凡是调度、网络、存储、安全相关的属性，基本都是pod级别的。

- pod中的几个重要字段

  - NodeSelector

    ```yaml
    apiVersion: v1
    kind: Pod
    ...
    spec:
      nodeSelector:
        disktype: ssd
    ```

    - 供用户将pod和node进行绑定的字段，加了nodeselector就意味着pod智能调度到指定label的node上。否则会调度失败。

  - NodeName

    - 一旦pod的这个字段被赋值，k8s就认为这个pod已经被调度。这个值一般是由scheduler来负责设置。

  - HostAliases

    - 定义pod的hosts文件内容（比如/etc/hosts）

      ```yaml
      apiVersion: v1
      kind: Pod
      ...
      spec:
        hostAliases:
        - ip: "10.1.2.3"
          hostnames:
          - "foo.remote"
          - "bar.remote"
      # yaml中的 - 代表一个数组项（https://cloud.tencent.com/developer/article/1854296）
      ```

    - 如果要设置hosts文件的内容，一定要通过这种方法。如果直接修改host文件，pod被重新调度后，k8s会自动覆盖掉修改的内容。

- pod生命周期

  主要体现在POD API对象的status。这时除了Metadata、spec之外第三个重要字段。其中pod.status.phase就是pod当前的状态。

  - pending
    - pod的yaml文件已经提交给了k8s，API对象已经创建并保存在了etcd中。但是pod中有些容器因为某种原因不能被顺利创建。比如调度不成功。
  - Running
  - Succeeded
    - pod中所有容器都已经运行完毕，并且退出。这种情况在一次性任务中最常见。
  - Failed
    - pod中至少有一个容器以不正常状态（非0的返回码）退出。
  - Unknown
    - pod状态不能持续的被kubelet报告给api server。有可能是kubelet与master通信出了问题。

### pod进阶使用

> k8s中有几种特殊的volume，作用是为容器提供预先定义好的数据，又叫做Projected volume。
>
> Project Volume一共有四种:
>
> Secret、ConfigMap、Downward API、ServiceAccountToken

- Secret

  


