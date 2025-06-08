通过设置http_proxy、https_proxy，可以让终端走指定的代理。 配置脚本如下，在终端直接执行，只会临时生效。

# 编写脚本

~~~sh
tee netowkr_proxy.sh <<'EOF'
function proxy_on() {
    export http_proxy=http://127.0.0.1:7890
    export https_proxy=$http_proxy
    echo -e "终端代理已开启。"
}

function proxy_off(){
    unset http_proxy https_proxy
    echo -e "终端代理已关闭。"
}
EOF
~~~

# 脚本路径添加到bash_profile

~~~sh
tee -a ~/.bash_profile <<'EOF'
function proxy_on() {
    export http_proxy=http://127.0.0.1:7890
    export https_proxy=$http_proxy
    echo -e "终端代理已开启。"
}

function proxy_off(){
    unset http_proxy https_proxy
    echo -e "终端代理已关闭。"
}
EOF
~~~

# 执行函数

- 通过`proxy_on`启动代理，`proxy_off`关闭代理。

- 可以通过`curl cip.cc`或者`curl myip.ipip.net`查看