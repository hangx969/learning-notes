# 准备工作

## 配置github self-hosted runner

https://docs.github.com/en/actions/hosting-your-own-runners

- 我的K8S测试环境搭建在本地VMWare的虚拟机中，kube-api-server没有公网IP，只能在自己电脑上通过内网IP访问到。所以计划将自己电脑配置为self-hosted github action runner。
- 在Add new self-host runner中配置runner：https://github.com/hangx969/local-k8s-platform-tools/settings/actions/runners/new
- self-hosted agent安装完成之后会有配置选项：

~~~sh
√ Connected to GitHub

# Runner Registration

Enter the name of the runner group to add this runner to: [press Enter for Default] 

Enter the name of runner: [press Enter for u5cg3523gk6]        

This runner will have the following labels: 'self-hosted', 'Linux', 'X64' 
Enter any additional labels (ex. label-1,label-2): [press Enter to skip] 

√ Runner successfully added
√ Runner connection is good

# Runner settings

Enter name of work folder: [press Enter for _work] 

√ Settings Saved.
~~~

> 注意在上面“Enter name of work folder”，设定了默认的工作目录是`actions-runner/_work`，也就是说workflow中使用checkout@4，会把代码下载到这个工作目录去执行。

- 配置完成之后可以在pipeline中引用


~~~yaml
# Use this YAML in your workflow file for each job
runs-on: self-hosted
~~~

- 将self-hosted runner配置为服务


~~~sh
#安装
sudo ./svc.sh install
#启动
sudo ./svc.sh start
#检查状态
sudo ./svc.sh status
#停止
sudo ./svc.sh stop
#卸载
sudo ./svc.sh uninstall
~~~

## 安装必要工具

- kubectl
  - kubectl krew插件
  - kubectl krew install kyverno插件
- helm3
  - helm lint插件
  - helm diff插件

## 上传并使用kubeconfig

1. 把本地的kuneconfig文件转换为base64：`cat kubeconfig-local | base64 -w 0`，复制。
2. 在github repo - Settings - Security - Secrets and variables - Actions - 添加一条`Repository secret`，粘贴进去。
3. workflow中用base64解密，输出到一个临时文件中，设为环境变量以供helm和kubectl使用。

参考：https://dev.to/richicoder1/how-we-connect-to-kubernetes-pods-from-github-actions-1mg

测试用workflow的示例如下：

~~~yaml
jobs:
  build:
    runs-on: self-hosted
    env:
      KUBECONFIG: '${{ github.workspace }}/.kube/kubeconfig'
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      - name: Generate kubeconfig from secret
        run: |
          mkdir -p '${{ github.workspace }}/.kube' \
          && echo '${{ secrets.HP_LOCAL_KUBECONFIG}}' | base64 -d > $KUBECONFIG
      - name: Helm Lint Base
        run: |
          helm lint ./helm/base --values ./helm/base/values.yaml --kubeconfig $KUBECONFIG
~~~

## 存储其他secrets到github

1. Oauth2proxy的clientID、clientSecret、cookieSecret。redis password?
2. slack api token
3. Harbor username/password

## secert在workflow中的使用

参考：https://docs.github.com/en/actions/sharing-automations/reusing-workflows#using-inputs-and-secrets-in-a-reusable-workflow

### 直接在workflow文件中使用secret

用`${{ secrets.KUBECONFIG }}`格式直接引用

### 在reusable模板中传递secret

在reusable workflow的情况下，会有called workflow和calling workflow。注意到called workflow无法直接用`${{ secrets.KUBECONFIG }}`获取到repository secrets。所以这就需要一些trick来传递workflow。

在calling workflow中：

1. 要么显示指定需要传递给called workflow的secret，比如：

   ~~~yaml
   #calling workflow
   jobs:
     reusable_workflow_job:
       runs-on: ubuntu-latest
       steps:
       - uses: ./github/workflow/xxx.yml
         with:
           # 在这里显式指定要传递的这个secret
           repo-token: ${{ secrets.KUBECONFIG }}
   ~~~

   ~~~yaml
   #called workflow
   on:
     workflow_call:
       secrets:
         # 在这里定义这个secert要被使用
         personal_access_token:
           description: "xxxx"
           required: true
   #在called workflow中可以继续用${{ secrets.KUBECONFIG }}来引用这个值
   ~~~

2. 要么用`secret: inherit`字段直接隐式的把所有calling workflow环境下的所有secret传递给了called workflow，比如：

   ~~~yaml
   #calling workflow
   jobs:
     build-base:
       uses: ./.github/workflows/build-base.yml
       secrets: inherit  #注意这个字段的缩进位置，别缩进错了
   ~~~

   ~~~yaml
   #called workflow
   on:
     workflow_call:
     #不需要在这里定义任何额外字段
   #后面可以直接用${{ secrets.KUBECONFIG }}来引用这个值
   ~~~

# 编写github action workflow

> 参考文档：
>
> - 配置self-hosted runner：https://docs.github.com/zh/actions/hosting-your-own-runners/managing-self-hosted-runners/adding-self-hosted-runners
> - github workflow中的默认环境变量：https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/store-information-in-variables#default-environment-variables
>
> - 创建repo secret：https://docs.github.com/zh/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-a-repository
> - workflow的触发条件：https://docs.github.com/zh/actions/writing-workflows/choosing-when-your-workflow-runs/triggering-a-workflow
> - reusable workflow调用：https://docs.github.com/zh/actions/sharing-automations/reusing-workflows

# 卸载runner

- 按照文档方法移除runner：https://docs.github.com/en/actions/how-tos/hosting-your-own-runners/managing-self-hosted-runners/configuring-the-self-hosted-runner-application-as-a-service
- 有时候github上的runner会莫名其妙消失，这时候需要在本地暴力移除runner，直接删掉actions-runner目录即可
