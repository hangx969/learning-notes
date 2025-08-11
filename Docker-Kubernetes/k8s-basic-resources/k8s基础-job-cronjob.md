# Job

## 状态

Job控制器用于管理Pod对象运行一次性任务。对于每次任务，job控制器创建一个或多个pod执行相关指令，并确保成功的个数达到预期才会把job标记为成功，否则标记为失败。

比方说对数据库备份，可以直接在k8s上启动一个mysqldump备份程序；也可以启动一个job pod，这个job pod专门用来备份用的，备份结束就可以终止了，不需要重启，而是将job Pod对象置于"Completed"(完成)状态。

若容器中的进程因错误而终止，则需要按照重启策略配置确定是否重启，Job控制器需不需要重建pod，就看任务是否完成，完成就不需要重建；没有完成就需要重建pod。Job控制器的Pod对象的状态转换如下图所示：

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202403231953816.png" alt="image-20240323195342683" style="zoom:67%;" />

## 优点

相比较在linux上启动一个docker或者shell去做job，k8s的job有什么优点？

1. 环境隔离：可以使用不同的镜像执行任务，无需考虑版本冲突。（比如有不同版本的mysql，就需要不同版本的mysqldump，直接用包含不同版本的mysqldump的镜像启动job即可）
2. 状态追踪：job控制器追踪所有pod运行情况，一旦达到指定的成功次数，job才会被标记为完成
3. 失败重试：任务执行失败，可以按需重新执行
4. 并行执行：同一个任务可以拆分成不同的pod并行执行2，提高执行速度

## Job使用场景

1. 非并行任务：只启一个pod，pod成功，job正常结束。

2. 并行任务同时指定成功个数：.spec.completions为指定成功个数，可以指定也可以不指定.spec.parallelism（指定>1，会有多个任务并行运行）。当成功个数达到.spec.completions，任务结束。

3. 有工作队列的并行任务：.spec.completions默认为1，.spec.parallelism为大于0的整数。此时并行启动多个pod，只要有一个成功，任务结束，所有pod结束

4. 适用场景： Job不是设计用来完成通信密集型的并行程序，如科学计算领域常见的场景。它支持并行地处理一组独立但相关的work item，如发送邮件，渲染帧，转码文件和扫描NoSql数据库中的key

## 相关配置

- .spec.completions：完成该Job需要执行成功的Pod数。

- .spec.parallelism：**能够同时运行的Pod数**，意味着job会管理这里指定数目的pod。默认是1，如果是0，job就暂停。
- .spec.template.spec.restartPolicy： 如果Pod是restartPolicy为Nerver，则失败后会创建新的Pod；如果是OnFailed，则会重启Pod。对于job来说不能设置为Always。

- .spec.backoffLimit：允许执行失败的Pod数，默认值是6。0表示不允许Pod执行失败。只要Pod失败一次就计算一次，不论restartPolicy是啥。当失败的次数达到该限制时，整个Job随即结束，所有正在运行中的Pod都会被删除。

- .spec.activeDeadlineSeconds: Job的超时时间，一旦一个Job运行的时间超出该限制，。该配置指定的值必须是个正整数。不指定则不会超时。
- .spec.ttlSecondsAfterFinished：默认情况下，job异常或者成功结束后，包括job启动的任务（pod），都不会被清理掉，因为你可以依据保存的job和pod，查看状态、日志，以及调试等。这些可以手动删除，用户手动删除job，job controller会级联删除对应的pod，除了手动删除，通过指定参数ttlSecondsAfterFinished也可以实现自动删除job，以及级联的资源如pod。如果设置为0，job会被立即删除。如果不指定，job则不会被删除。

## 示例

~~~yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: my-busybox-job
spec:
  parallelism: 3 # 并行跑3个，意思是一次建3个pod；再一次再建3个。但是如果completions大于parallelism，那么一次只会创建未完成数量的pod。比如现有配置，第一次建3个pod，第二次只创建1个pod。
  completions: 4 # 多少个pod执行成功，认为job成功。默认等于parallelism。
  backoffLimit: 2 # 每个pod最大允许重启的次数。默认是6。生产环境限制成2就够了。搭配restartPolicy为OnFailure。
  ttlSecondsAfterFinished: 100 # job执行结束之后多久自动清理。为0是立即清理。不设置就不清理。
  # 下面是job管理的pod模板字段
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: my-container-job
          image: busybox:1.28
          imagePullPolicy: IfNotPresent
          command: ['sh', '-c']
          args: ['echo "Welcome to k8s";sleep 60; echo "Next to Meet you"']
~~~

# cronjob

## 用法

CronJob跟Job完成的工作是一样的，只不过CronJob添加了定时任务能力可以指定时间，实现周期性运行。Job，CronJob和Deployment显著区别在于不需要持续在后台运行。cronjob具有多种并发策略；调用job更灵活，并且可以保留多个成功或失败的案例，方便追踪。

CronJob的典型用法如下：

1、在给定的时间点调度Job运行。

2、创建周期性运行的Job，例如数据库备份、发送邮件

Cronjob执行时先创建job，再由job创建pod去执行。

## 示例

~~~yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: cj-hello
spec:
  schedule: "*/1 * * * *" # 分时日月周
  concurrencyPolicy: Allow 
  suspend: false # 改成true相当于把计划任务关了
  successfulJobsHistoryLimit: 3 # 保留多少个成功任务
  failedJobHistoryLimit: 3 # 保留多少个失败任务
  jobTemplate:
    spec:
      backoffLimit: 2
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

## 并发策略

cronjob支持三种并发策略，在`cronjob.spec.concurrencyPolicy`中配置：

1. Allow：允许同时运行多个任务，新job可以和旧job同时执行。（默认值）
2. Forbid：不允许并发运行，如果之前的任务尚未完成，新的任务不会被创建。（适用于不能同时运行的情况）
3. Replace：如果之前的任务尚未完成，新的任务会替换之前的任务。

## 执行记录

CronJob默认的执行记录保留方式如下：

1. 成功记录：默认为3次，可以通过.spec.successfulJobsHistoryLimit字段更改
2. 失败记录：默认为1次，可以通过.spec.failedJobsHistoryLimit字段更改 

## 调度时区

如果采用具体的时间调度任务，需要注意调度的时区问题。

如果CronJob未标注调度时区，Kubernetes会以kube-controller-manager组件的时区进行调度，如果该组件运行的时区和本地时区不一样，会导致无法按照规定时间进行调度。

比如创建一个每天凌晨一点开始执行的任务，此时配置的调度表达式可能如下：`schedule: '00 01 * * *'`。但是如果未指定时区，当kube-controller-manager组件的时区和本地时区有差别时，可能会在北京时间每天的九点进行调度（本地时区为Shanghai时区，kube-controller-manager采用UTC时间）

在Kubernetes 1.25 版本时，CronJob 增加了`.spec.timeZone`的字段用于配置CronJob的调度时区。在1.27版本达到稳定，可以直接使用。

> 1.25~1.27（不包括1.27）版本之间需要打开`kube-apiserver`的featuregates特性，比如：`--feature-gates=CronJobTimeZone=true` ，1.27及1.27之后不用打开直接用就行。

~~~yaml
apiVersion: batch/v1 
kind: CronJob 
metadata: 
  name: example-cronjob
spec: 
  schedule: "*/5 02 * * *" 
  timeZone: "Asia/Shanghai"
~~~

## 手动运行cronjob

已经创建了cronjob的情况下，时间还没到，但是希望手动执行先测试一下：

~~~sh
kubectl create job mysql-backup-test --from=cronjob/mysql-backup -n cronjob
~~~

# 实战

## 定期备份mysql

~~~yaml
--- 
apiVersion: v1 
kind: PersistentVolumeClaim 
metadata: 
  name: mysql-backup-data 
  namespace: cronjob
spec: 
  accessModes: 
    - ReadWriteMany 
  resources: 
    requests: 
      storage: 10Gi 
  storageClassName: nfs-csi 
  
---
apiVersion: batch/v1 
kind: CronJob 
metadata: 
  name: mysql-backup 
  namespace: cronjob
spec: 
  schedule: '01 16 * * *' 
  failedJobsHistoryLimit: 5 
  successfulJobsHistoryLimit: 5 
  jobTemplate: 
    spec: 
      template: 
        spec: 
          volumes: 
          - name: data 
            persistentVolumeClaim: 
              claimName: mysql-backup-data 
          restartPolicy: Never 
          containers: 
          - name: backup
            image: registry.cn-beijing.aliyuncs.com/dotbalo/mysql:8.0.20 # 这个镜像已经包含mysqldump的命令
            command: 
            - sh 
            - -c 
            - | 
              mysqldump -hmysql.default -P3306 -uroot -p'password_123' -
all-databases > /mnt/all-`date +%Y%m%d-%H%M%S`.sql; 
              ls /mnt/ 
            volumeMounts: 
            - name: data 
              mountPath: /mnt
~~~

## 定时重启k8s服务

有时候需要定期重启K8s中的服务，也可以使用CronJob实现。

~~~sh
kubectl create clusterrole deployment-restart --verb=get,update,patch --resource=deployments.apps 
# 给cronjob的ns的default service account授权
kubectl create clusterrolebinding deployment-restart-binding -clusterrole=deployment-restart --serviceaccount=cronjob:default 
~~~

创建cronjob：

~~~yaml
apiVersion: batch/v1 
kind: CronJob 
metadata: 
  name: default-restart 
  namespace: cronjob 
spec: 
  schedule: 01 18 * * 5 
  concurrencyPolicy: Allow 
  suspend: false 
  successfulJobsHistoryLimit: 3 
  failedJobsHistoryLimit: 3 
  jobTemplate: 
    spec: 
      template: 
        spec: 
          restartPolicy: Never 
          containers: 
          - name: restart 
            image: registry.cn-beijing.aliyuncs.com/dotbalo/kubectl:latest 
            command: 
            - /bin/bash - '-c' - >- kubectl rollout restart deploy mysql -n default 
~~~

