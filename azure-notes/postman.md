# postman

- 发送HTTP请求

- 主要作用：在AAD中用/发ARM请求，这两套access token是不一样的。

  - 在AAD中用，作用域scope是这个：

    ![image-20231030170702907](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310301707977.png)

- 发ARM请求：

  - query ARM资源，也要拿一个bear token，是和AAD不一样的token。只要token里面有RBAC的权限就行。

  - portal上可以点到非AAD界面的地方，从F12里面拿到bear token。