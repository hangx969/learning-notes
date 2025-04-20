# 介绍

- 一个可视化查看k8s RBAC role的kubectl插件
- 官网地址：https://github.com/Ladicle/kubectl-rolesum

# 安装

- 安装krew

  - 是一个管理kubectl插件的工具：
  - https://github.com/kubernetes-sigs/krew
  - https://krew.sigs.k8s.io/docs/user-guide/quickstart/

  ~~~SH
  (
    set -x; cd "$(mktemp -d)" &&
    OS="$(uname | tr '[:upper:]' '[:lower:]')" &&
    ARCH="$(uname -m | sed -e 's/x86_64/amd64/' -e 's/\(arm\)\(64\)\?.*/\1\2/' -e 's/aarch64$/arm64/')" &&
    KREW="krew-${OS}_${ARCH}" &&
    curl -fsSLO "https://github.com/kubernetes-sigs/krew/releases/latest/download/${KREW}.tar.gz" &&
    tar zxvf "${KREW}.tar.gz" &&
    ./"${KREW}" install krew
  )
  
  tee -a ~/.bashrc <<'EOF'
  export PATH="${KREW_ROOT:-$HOME/.krew}/bin:$PATH"
  EOF
  ~~~

- 安装rolesum插件

  ~~~sh
  kubectl krew install rolesum
  ~~~

  # 使用

  ~~~sh
  kubectl rolesum <svc name>
  ~~~

  
