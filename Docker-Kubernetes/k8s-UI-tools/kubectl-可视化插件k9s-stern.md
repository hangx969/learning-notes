# k9s

- kubectl可视化插件：https://github.com/derailed/k9s
- 安装指南：https://k9scli.io/topics/install/

# 在线安装

1. 方法1：via [webi](https://webinstall.dev/) (在现在rockylinux vm上使用的方法)

   ~~~sh
   curl -sS https://webinstall.dev/k9s | bash
   ~~~

2. 方法2：在ubuntu上

   ~~~sh
   wget https://github.com/derailed/k9s/releases/download/v0.40.5/k9s_linux_amd64.deb && apt install ./k9s_linux_amd64.deb && rm k9s_linux_amd64.deb
   ~~~

3. 方法3：via snap

   ~~~sh
   snap install k9s --devmode
   ~~~

## 使用

- vim风格，在主页面上
  - ：来输入资源类型
  - /来输入filter


- 常用命令

  ~~~sh
  # List all available CLI options
  $ k9s help
  
  # To get info about K9s runtime (logs, configs, etc..)
  $ k9s info
  
  # To run K9s in a given namespace
  $ k9s -n mycoolns
  
  # Start K9s in an existing KubeConfig context
  $ k9s --context coolCtx
  
  # Start K9s in readonly mode - with all modification commands disabled
  $ k9s --readonly
  ~~~

  

## 快捷键

| 操作                                                         | 命令                          | 备注                                                         |
| ------------------------------------------------------------ | ----------------------------- | ------------------------------------------------------------ |
| 显示活跃的键盘助记符和帮助                                   | `?`                           |                                                              |
| 显示集群上所有可用的别名和资源                               | `ctrl-a` or `:alias`          |                                                              |
| 退出 K9s                                                     | `:q`, `ctrl-c`                |                                                              |
| 查看pod                                                      | `:`po⏎                        | 接受单数，复数，短名或别名如 `pod` 或 `pods`                 |
| 查看给定名称空间中的资源                                     | `:`alias namespace⏎           |                                                              |
| 过滤字段                                                     | `/`filter⏎                    | 支持 Regex2，如 ` fred                                       |
| 反向正则表达式过滤                                           | `/`! filter⏎                  | 保留所有 *不匹配* 的东西。日志未实现。                       |
| 按标签过滤资源视图                                           | `/`-l label-selector⏎         |                                                              |
| 模糊查找给定的资源                                           | `/`-f filter⏎                 |                                                              |
| 退出视图 / 命令 / 过滤模式                                   | `<esc>`                       |                                                              |
| 键映射来描述(describe)，查看(view)，编辑(edit)，查看日志(logs)，… | `d`,`v`, `e`,`l`,…            |                                                              |
| 查看并切换到另一个 Kubernetes 上下文                         | `:`ctx⏎                       |                                                              |
| 查看并切换到另一个 Kubernetes 上下文                         | `:`ctx context-name⏎          |                                                              |
| 查看namespace                                                | `:`ns⏎                        |                                                              |
| 查看所有已保存的资源                                         | `:`screendump or sd⏎          |                                                              |
| 要删除资源 (按`TAB`并输入`Enter`)                            | `ctrl-d`                      |                                                              |
| 杀死一个资源 (没有确认对话框!)                               | `ctrl-k`                      |                                                              |
| 切换宽列                                                     | `ctrl-w`                      | 等同于 `kubectl ... -o wide`                                 |
| 切换错误状态                                                 | `ctrl-z`                      | 查看有错误的资源                                             |
| 运行 pulses（脉冲）视图                                      | `:`pulses or pu⏎              |                                                              |
| 运行 XRay视图                                                | `:`xray RESOURCE [NAMESPACE]⏎ | 资源可以是以下之一：po, svc, dp, rs, sts, ds, NAMESPACE 参数可选 |
| 运行 Popeye（评估跑分） 视图                                 | `:`popeye or pop⏎             | 参阅 [https://popeyecli.io](https://popeyecli.io/)           |

## 过滤功能

- 它的过滤功能非常强大，使得你可以非常快速的定位资源，比如我想要看 traefik 的所有 CRD，操作如下：

  ~~~sh
  ctrl+a
  /traefik
  ~~~

## Pulse

- 进入监控模式，不过需要metrics-server在集群内运行

## Xray

- XRay 会提供以某个 Kubernetes 资源为维度的关联关系，像 X 光一样，透射到资源的内部。比如查看deploy资源的关联关系：

  ~~~sh
  :xray deploy
  ~~~

## popeye

> [Popeye](https://popeyecli.io/) 是 K9s 作者开发的另一个 K8s 命令行工具，现已被集成进 K9s，它可以实时扫描你的集群，并报告潜在的问题，比如：引用完整性、配置错误、资源使用等。

- 通过 `:popeye` 命令可以进入 Popeye 的总览视图，然后可以通过在给定的资源条目上按 `Enter` 键来查看更为详细的检测报告。

- Popeye 还支持一个配置文件，即 `spinach.yml`，该文件提供了自定义扫描资源的内容，并根据自己的策略设置不同的严重程度。

- 请阅读 [Popeye 文档](https://popeyecli.io/#the-spinachyaml-configuration)，了解如何自定义报告。`spinach.yml` 文件将从 K9s 的主目录`$HOME/.k9s/MY_CLUSTER_CONTEXT_NAME_spinach.yml` 中读取。

## k9s插件功能

K9s 允许你通过 [插件机制](https://github.com/derailed/k9s#plugins) 定义自己的集群命令来扩展你的命令行和工具。K9s 会查看 `$HOME/.k9s/plugin.yml` 来定位所有可用的插件。一个插件的定义如下：

- `shortCut` 快捷键选项代表用户键入激活插件的组合键。
- `confirm` 确认选项（启用时）让你看到将要执行的命令，并给你一个确认或阻止执行的选项。
- `description` 说明将被打印在 K9s 菜单中的快捷方式旁边。
- `scopes` 作用域为与插件相关联的视图定义了资源名称/简称的集合。你可以指定所有，为所有视图提供这个快捷方式。 
- `command` 代表插件在激活时运行的临时命令。 
- `background` 指定命令是否在后台运行。
- `args` 指定适用于上述命令的各种参数。

K9s 同时提供了额外的环境变量，供你自定义插件的参数。目前，可用的环境变量如下：

- `$NAMESPACE`：选定的资源命名空间 
- `$NAME`：所选资源名称 
- `$CONTAINER` ：当前容器（如果适用）
- `$FILTER`：当前的过滤器（如果有）
- `$KUBECONFIG`：KubeConfig 文件的位置 
- `$CLUSTER`：当前的集群名称 
- `$CONTEXT`：当前的上下文名称 
- `$USER`：当前用户 
- `$GROUPS`：当前的用户组 
- `$POD`：容器视图中的 Pod 

# stern

- 查看pod log的插件：https://github.com/stern/stern#installation

## 安装

If you use [Krew](https://krew.sigs.k8s.io/) which is the package manager for kubectl plugins, you can install like this:

```sh
kubectl krew install stern
```

## 使用

~~~sh
实时查看当前 Namespace 中所有 Pod 中所有容器的日志
$ stern  .

实时查看 Pod 中指定容器的日志
$ stern envvars --container gateway

实时查看指定命名空间中除指定容器外的所有容器的日志
$ stern -n staging --exclude-container istio-proxy .

实时查看指定时间范围内容器的日志，下面的例子表示是 15 分钟内
$ stern auth -t --since 15m

实时查看指定命名空间中容器的日志
$ stern kubernetes-dashboard --namespace kube-system

实时查看所有命名空间中符合指定标签容器的日志
$ stern --all-namespaces -l run=nginx
~~~

## k9s通过plugin与stern集成

[Stern](https://github.com/wercker/stern) 是一款社区知名的 K8s 集群服务日志查询工具，虽然 k9s 已然集成了部分 Stern 的功能，但操作不太直接也无法连接管道操作（ `|` ），我们可以利用插件创建一个可以查询当前命名空间下多个 Pod 的快捷命令。

```yaml
tee -a $HOME/.k9s/plugin.yml <<'EOF'
plugin:
  stern:
    shortCut: Ctrl-L
    confirm: false
    description: "Logs (Stern)"
    scopes:
      - pods
    command: /usr/local/bin/stern # NOTE! Look for the command at this location.
    background: false
    args:
     - --tail
     - 100
     - $FILTER      # NOTE! Pulls the filter out of the pod view.
     - -n
     - $NAMESPACE   # Use current namespace
     - --context
     - $CONTEXT     # Use current k8s context
EOF
```

# 离线安装k9s

## 下载安装包

先从github下载amd64版本安装包：[Releases · derailed/k9s](https://github.com/derailed/k9s/releases)

安装包放到/root/下

## 本地安装脚本

~~~sh
#!/bin/bash

############################################################
# K9s Local Installation Script
# Modified to install from local tar.gz file instead of downloading
############################################################

# Configuration for local installation
K9S_LOCAL_ARCHIVE="/root/k9s_Linux_amd64.tar.gz"
INSTALL_DIR="$HOME/.local/bin"

# Check if local archive exists, if so use local installation
if [ -f "$K9S_LOCAL_ARCHIVE" ]; then
    echo "Found local k9s archive, installing from: $K9S_LOCAL_ARCHIVE"

    # Create installation directory
    mkdir -p "$INSTALL_DIR"

    # Create temporary directory for extraction
    TEMP_DIR=$(mktemp -d)

    # Extract and install
    echo "Extracting k9s from local archive..."
    tar -xzf "$K9S_LOCAL_ARCHIVE" -C "$TEMP_DIR"

    if [ -f "$TEMP_DIR/k9s" ]; then
        echo "Installing k9s to $INSTALL_DIR/k9s"
        cp "$TEMP_DIR/k9s" "$INSTALL_DIR/k9s"
        chmod +x "$INSTALL_DIR/k9s"

        # Clean up
        rm -rf "$TEMP_DIR"

        echo "k9s installed successfully to $INSTALL_DIR/k9s"
        echo "Make sure $INSTALL_DIR is in your PATH to use k9s command"
        exit 0
    else
        echo "Error: k9s binary not found in archive"
        rm -rf "$TEMP_DIR"
        exit 1
    fi
fi

# Fallback to original webi installation if local archive not found
echo "Local archive not found at $K9S_LOCAL_ARCHIVE, falling back to webi installation..."

export WEBI_PKG='k9s@stable'
export WEBI_HOST='https://webi.sh'
export WEBI_CHECKSUM='adad246e'

#########################################
#                                       #
# Display Debug Info in Case of Failure #
#                                       #
#########################################

fn_show_welcome() { (
    echo ""
    echo ""
    # invert t_task and t_pkg for top-level welcome message
    printf -- ">>> %s %s  <<<\n" \
        "$(t_pkg 'Welcome to') $(t_task 'Webi')$(t_pkg '!')" \
        "$(t_dim "- modern tools, instant installs.")"
    echo "    We expect your experience to be $(t_em 'absolutely perfect')!"
    echo ""
    echo "    $(t_attn 'Success')? Star it!   $(t_url 'https://github.com/webinstall/webi-installers')"
    echo "    $(t_attn 'Problem')? Report it: $(t_url 'https://github.com/webinstall/webi-installers/issues')"
    echo "                        $(t_dim "(your system is") $(t_host "$(fn_get_os)")/$(t_host "$(uname -m)") $(t_dim "with") $(t_host "$(fn_get_libc)") $(t_dim "&") $(t_host "$(fn_get_http_client_name)")$(t_dim ")")"

    sleep 0.2
); }

fn_get_os() { (
    # Ex:
    #     GNU/Linux
    #     Android
    #     Linux (often Alpine, musl)
    #     Darwin
    b_os="$(uname -o 2> /dev/null || echo '')"
    b_sys="$(uname -s)"
    if test -z "${b_os}" || test "${b_os}" = "${b_sys}"; then
        # ex: 'Darwin' (and plain, non-GNU 'Linux')
        echo "${b_sys}"
        return 0
    fi

    if echo "${b_os}" | grep -q "${b_sys}"; then
        # ex: 'GNU/Linux'
        echo "${b_os}"
        return 0
    fi

    # ex: 'Android/Linux'
    echo "${b_os}/${b_sys}"
); }

fn_get_libc() { (
    # Ex:
    #     musl
    #     libc
    if ldd /bin/ls 2> /dev/null | grep -q 'musl' 2> /dev/null; then
        echo 'musl'
    elif fn_get_os | grep -q 'GNU|Linux'; then
        echo 'gnu'
    else
        echo 'libc'
    fi
); }

fn_get_http_client_name() { (
    # Ex:
    #     curl
    #     curl+wget
    b_client=""
    if command -v curl > /dev/null; then
        b_client="curl"
    fi
    if command -v wget > /dev/null; then
        if test -z "${b_client}"; then
            b_client="wget"
        else
            b_client="curl+wget"
        fi
    fi

    echo "${b_client}"
); }

#########################################
#                                       #
#      For Making the Display Nice      #
#                                       #
#########################################

# Term Types
t_cmd() { (fn_printf '\e[2m\e[35m%s\e[39m\e[22m' "${1}"); }
t_host() { (fn_printf '\e[2m\e[33m%s\e[39m\e[22m' "${1}"); }
t_link() { (fn_printf '\e[1m\e[36m%s\e[39m\e[22m' "${1}"); }
t_path() { (fn_printf '\e[2m\e[32m%s\e[39m\e[22m' "${1}"); }
t_pkg() { (fn_printf '\e[1m\e[32m%s\e[39m\e[22m' "${1}"); }
t_task() { (fn_printf '\e[36m%s\e[39m' "${1}"); }
t_url() { (fn_printf '\e[2m%s\e[22m' "${1}"); }

# Levels
t_info() { (fn_printf '\e[1m\e[36m%s\e[39m\e[22m' "${1}"); }
t_attn() { (fn_printf '\e[1m\e[33m%s\e[39m\e[22m' "${1}"); }
t_warn() { (fn_printf '\e[1m\e[33m%s\e[39m\e[22m' "${1}"); }
t_err() { (fn_printf '\e[31m%s\e[39m' "${1}"); }

# Styles
t_bold() { (fn_printf '\e[1m%s\e[22m' "${1}"); }
t_dim() { (fn_printf '\e[2m%s\e[22m' "${1}"); }
t_em() { (fn_printf '\e[3m%s\e[23m' "${1}"); }
t_under() { (fn_printf '\e[4m%s\e[24m' "${1}"); }

# FG Colors
t_cyan() { (fn_printf '\e[36m%s\e[39m' "${1}"); }
t_green() { (fn_printf '\e[32m%s\e[39m' "${1}"); }
t_magenta() { (fn_printf '\e[35m%s\e[39m' "${1}"); }
t_yellow() { (fn_printf '\e[33m%s\e[39m' "${1}"); }

fn_printf() { (
    a_style="${1}"
    a_text="${2}"
    if fn_is_tty; then
        #shellcheck disable=SC2059
        printf -- "${a_style}" "${a_text}"
    else
        printf -- '%s' "${a_text}"
    fi
); }

fn_sub_home() { (
    my_rel=${HOME}
    my_abs=${1}
    echo "${my_abs}" | sed "s:^${my_rel}:~:"
); }

###################################
#                                 #
#       Detect HTTP Client        #
#                                 #
###################################

fn_wget() { (
    # Doc:
    #     Downloads the file at the given url to the given path
    a_url="${1}"
    a_path="${2}"

    cmd_wget="wget -c -q --user-agent"
    if fn_is_tty; then
        cmd_wget="wget -c -q --show-progress --user-agent"
    fi
    # busybox wget doesn't support --show-progress
    # See
    if readlink "$(command -v wget)" | grep -q busybox; then
        cmd_wget="wget --user-agent"
    fi

    b_triple_ua="$(fn_get_target_triple_user_agent)"
    b_agent="webi/wget ${b_triple_ua}"
    if command -v curl > /dev/null; then
        b_agent="webi/wget+curl ${b_triple_ua}"
    fi

    if ! $cmd_wget "${b_agent}" "${a_url}" -O "${a_path}"; then
        echo >&2 "    $(t_err "failed to download (wget)") '$(t_url "${a_url}")'"
        echo >&2 "    $cmd_wget '${b_agent}' '${a_url}' -O '${a_path}'"
        echo >&2 "    $(wget -V)"
        return 1
    fi
); }

fn_curl() { (
    # Doc:
    #     Downloads the file at the given url to the given path
    a_url="${1}"
    a_path="${2}"

    cmd_curl="curl -f -sSL -#"
    if fn_is_tty; then
        cmd_curl="curl -f -sSL"
    fi

    b_triple_ua="$(fn_get_target_triple_user_agent)"
    b_agent="webi/curl ${b_triple_ua}"
    if command -v wget > /dev/null; then
        b_agent="webi/curl+wget ${b_triple_ua}"
    fi

    if ! $cmd_curl -A "${b_agent}" "${a_url}" -o "${a_path}"; then
        echo >&2 "    $(t_err "failed to download (curl)") '$(t_url "${a_url}")'"
        echo >&2 "    $cmd_curl -A '${b_agent}' '${a_url}' -o '${a_path}'"
        echo >&2 "    $(curl -V)"
        return 1
    fi
); }

fn_get_target_triple_user_agent() { (
    # Ex:
    #     x86_64/unknown GNU/Linux/5.15.107-2-pve gnu
    #     arm64/unknown Darwin/22.6.0 libc
    echo "$(uname -m)/unknown $(fn_get_os)/$(uname -r) $(fn_get_libc)"
); }

fn_download_to_path() { (
    a_url="${1}"
    a_path="${2}"

    mkdir -p "$(dirname "${a_path}")"
    if command -v curl > /dev/null; then
        fn_curl "${a_url}" "${a_path}.part"
    elif command -v wget > /dev/null; then
        fn_wget "${a_url}" "${a_path}.part"
    else
        echo >&2 "    $(t_err "failed to detect HTTP client (curl, wget)")"
        return 1
    fi
    mv "${a_path}.part" "${a_path}"
); }

##############################################
#                                            #
# Install or Update Webi and Install Package #
#                                            #
##############################################

webi_bootstrap() { (
    a_path="${1}"

    echo ""
    echo "$(t_task 'Bootstrapping') $(t_pkg 'Webi')"

    b_path_rel="$(fn_sub_home "${a_path}")"
    b_checksum=""
    if test -r "${a_path}"; then
        b_checksum="$(fn_checksum "${a_path}")"
    fi
    if test "$b_checksum" = "${WEBI_CHECKSUM}"; then
        echo "    $(t_dim 'Found') $(t_path "${b_path_rel}")"
        sleep 0.1
        return 0
    fi

    b_webi_file_url="${WEBI_HOST}/packages/webi/webi.sh"
    b_tmp=''
    if test -r "${a_path}"; then
        b_ts="$(date -u '+%s')"
        b_tmp="${a_path}.${b_ts}.bak"
        mv "${a_path}" "${b_tmp}"
        echo "    Updating $(t_path "${b_path_rel}")"
    fi

    echo "    Downloading $(t_url "${b_webi_file_url}")"
    echo "        to $(t_path "${b_path_rel}")"
    fn_download_to_path "${b_webi_file_url}" "${a_path}"
    chmod u+x "${a_path}"

    if test -r "${b_tmp}"; then
        rm -f "${b_tmp}"
    fi
); }

fn_checksum() {
    a_filepath="${1}"

    if command -v sha1sum > /dev/null; then
        sha1sum "${a_filepath}" | cut -d' ' -f1 | cut -c 1-8
        return 0
    fi

    if command -v shasum > /dev/null; then
        shasum "${a_filepath}" | cut -d' ' -f1 | cut -c 1-8
        return 0
    fi

    if command -v sha1 > /dev/null; then
        sha1 "${a_filepath}" | cut -d'=' -f2 | cut -c 2-9
        return 0
    fi

    echo >&2 "    warn: no sha1 sum program"
    date '+%F %H:%M'
}

##############################################
#                                            #
#          Detect TTY and run main           #
#                                            #
##############################################

fn_is_tty() {
    if test "${WEBI_TTY}" = 'tty'; then
        return 0
    fi
    return 1
}

fn_detect_tty() { (
    # stdin will NOT be a tty if it's being piped
    # stdout & stderr WILL be a tty even when piped
    # they are not a tty if being captured or redirected
    # 'set -i' is NOT available in sh
    if test -t 1 && test -t 2; then
        return 0
    fi

    return 1
); }

main() { (
    set -e
    set -u

    WEBI_TTY="${WEBI_TTY:-}"
    if test -z "${WEBI_TTY}"; then
        if fn_detect_tty; then
            WEBI_TTY="tty"
        fi
        export WEBI_TTY
    fi

    if test -z "${WEBI_WELCOME:-}"; then
        fn_show_welcome
    fi
    export WEBI_WELCOME='shown'

    # note: we may support custom locations in the future
    export WEBI_HOME="${HOME}/.local"
    b_home="$(fn_sub_home "${WEBI_HOME}")"
    b_webi_path="${WEBI_HOME}/bin/webi"
    b_webi_path_rel="${b_home}/bin/webi"

    WEBI_CURRENT="${WEBI_CURRENT:-}"
    if test "${WEBI_CURRENT}" != "${WEBI_CHECKSUM}"; then
        webi_bootstrap "${b_webi_path}"
        export WEBI_CURRENT="${WEBI_CHECKSUM}"
    fi

    echo "    Running $(t_cmd "${b_webi_path_rel} ${WEBI_PKG}")"
    echo ""

    "${b_webi_path}" "${WEBI_PKG}"
); }

main
~~~

## 安装

~~~sh
chmod +x k9s-local-install.sh
./k9s0local-install.sh

echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
~~~

再新开一个terminal就可以运行K9s了
