## Troubleshooting
创建完applicationset之后，无法创建application，去看k describe applicationset appset-helm -n argocd的时候看到网络连接问题：Client.Timeout exceeded while awaiting headers。
解决：删掉当前appset，换个名字再重新创建一个。

  

