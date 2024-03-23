# Job

## 状态

- Job控制器用于管理Pod对象运行一次性任务。

  - 比方说对数据库备份，可以直接在k8s上启动一个mysqldump备份程序；也可以启动一个pod，这个pod专门用来备份用的，备份结束pod就可以终止了，不需要重启，而是将Pod对象置于"Completed"(完成)状态。

  - 若容器中的进程因错误而终止，则需要按照重启策略配置确定是否重启，Job控制器需不需要重建pod就看任务是否完成，完成就不需要重建；没有完成就需要重建pod。Job控制器的Pod对象的状态转换如下图所示：

    <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202403231953816.png" alt="image-20240323195342683" style="zoom:67%;" />



## Job使用场景

1. 非并行任务：只启一个pod，pod成功，job正常结束

2. 并行任务同时指定成功个数：.spec.completions为指定成功个数，可以指定也可以不指定.spec.parallelism（指定>1，会有多个任务并行运行）。当成功个数达到.spec.completions，任务结束。

3. 有工作队列的并行任务：.spec.completions默认为1，.spec.parallelism为大于0的整数。此时并行启动多个pod，只要有一个成功，任务结束，所有pod结束

4. 适用场景： Job不是设计用来完成通信密集型的并行程序，如科学计算领域常见的场景。它支持并行地处理一组独立但相关的work item，如发送邮件，渲染帧，转码文件和扫描NoSql数据库中的key

## 相关配置

- .spec.completions：完成该Job需要执行成功的Pod数。

- .spec.parallelism：**能够同时运行的Pod数**，意味着job会管理这里指定数目的pod。默认是1，如果是0，job就暂停。
- .spec.template.spec.restartPolicy： 如果Pod是restartPolicy为Nerver，则失败后会创建新的Pod；如果是OnFailed，则会重启Pod。对于job来说不能设置为Always。

- .spec.backoffLimit：允许执行失败的Pod数，默认值是6，0表示不允许Pod执行失败。只要Pod失败一次就计算一次，不论restartPolicy是啥。当失败的次数达到该限制时，整个Job随即结束，所有正在运行中的Pod都会被删除。

- .spec.activeDeadlineSeconds: Job的超时时间，一旦一个Job运行的时间超出该限制，。该配置指定的值必须是个正整数。不指定则不会超时。
- .spec.ttlSecondsAfterFinished： 默认情况下，job异常或者成功结束后，包括job启动的任务（pod），都不会被清理掉，因为你可以依据保存的job和pod，查看状态、日志，以及调试等。这些可以手动删除，用户手动删除job，job controller会级联删除对应的pod，除了手动删除，通过指定参数ttlSecondsAfterFinished也可以实现自动删除job，以及级联的资源如pod。如果设置为0，job会被立即删除。如果不指定，job则不会被删除。

## 示例

~~~yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: my-busybox-job
spec:
  completions: 6
  parallelism: 3 #并行跑3个，意思是一次建3个pod；再一次再建3个。
  backoffLimit: 6
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: my-container-job
          image: busybox
          imagePullPolicy: IfNotPresent
          command: ['sh', '-c']
          args: ['echo "Welcome to k8s";sleep 60; echo "Next to Meet you"']
~~~



# cronjob

## 用法

- CronJob跟Job完成的工作是一样的，只不过CronJob添加了定时任务能力可以指定时间，实现周期性运行。Job，CronJob和Deployment，DaemonSet显著区别在于不需要持续在后台运行。

- CronJob的典型用法如下：

  1、在给定的时间点调度Job运行。

  2、创建周期性运行的Job，例如数据库备份、发送邮件

## 示例

~~~yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: cj-hello
spec:
  schedule: "*/1 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
          - name: hello
            image: busybox
            imagePullPolicy: IfNotP-resent
            command:
            - /bin/sh
            - -c
            - date; echo Hello from the Kubernetes cluster
~~~

每分钟都会创建一个pod出来运行。