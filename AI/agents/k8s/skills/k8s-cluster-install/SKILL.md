---
name: k8s-cluster-install
description: Install a Kubernetes cluster on one or more Linux hosts when the user asks to install K8s, Kubernetes, kubeadm, a control-plane node, or worker nodes on remote machines. Use for strict Linux-only multi-host cluster installation workflows where the user provides a newline-separated hosts file plus explicit control-plane and worker-node mapping, and the agent must first verify passwordless SSH on every host, verify containerd is already installed on every host, stop immediately on any failed prerequisite, then execute only the documented Rocky Linux 10 Kubernetes installation and cluster initialization commands. Do not invent extra installation steps, scripts, retries, or repair actions.
---

# k8s-cluster-install

Execute this skill with very low freedom.

- Follow `SKILL.md` literally.
- Do not generate any scripts.
- Do not add commands or steps outside the documented procedure below.
- If installation fails, stop and report the failure. Do not attempt repair.
- Linux only.

Authoring-time source material for this skill came from `/home/hx-ai/Downloads/rocky-linux10-k8s安装与初始化.md`. Do not reference that external file during runtime. Use the instructions embedded in this `SKILL.md`.

## Required user inputs

Collect these inputs before installation.

### 1. Hosts file content

The user must provide hosts as newline-separated items. Example format:

```text
10.0.0.11
10.0.0.12
10.0.0.13
```

The agent may normalize these into concrete SSH targets such as `root@10.0.0.11` or `rocky@10.0.0.11` only after the SSH login user is known.

### 2. Node role mapping

The user must explicitly state which hosts are control-plane nodes and which hosts are worker nodes.

Example format:

```text
control-plane:
10.0.0.11

worker:
10.0.0.12
10.0.0.13
```

If the role mapping is missing or ambiguous, stop immediately and ask the user to provide it.

### 3. Optional Kubernetes version

- If the user does not specify a version, install the latest available version.
- If the user specifies a full patch version such as `1.35.5`, keep that full version for package installation and image pulling, but normalize the repository channel to `1.35`.
- If the user specifies a version that has not been released, fall back to the latest available version and say so in the final report.

## Hard stop conditions

Stop immediately in any of these cases:

1. Any host cannot be reached with passwordless SSH.
2. Any host does not already have `containerd` installed.
3. The user did not provide explicit control-plane and worker-node mapping.
4. A required per-host variable is missing and cannot be discovered safely from commands.
5. Any install or initialization command fails.

## Workflow

### 1. Normalize inputs

- Read the newline-separated hosts input.
- Remove blank lines.
- Preserve order.
- Normalize to concrete SSH targets only after the login user is known.
- If the SSH login user is not known, ask the user before probing.

### 2. Verify passwordless SSH on every host

Run this directly from the workflow, not from a script.

Example probe:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 <target> 'true'
```

Rules:

- Probe every host before any installation command.
- If one host fails, stop the entire task immediately.
- Tell the user to complete machine initialization first and retry later.

### 3. Verify `containerd` is already installed on every host

Run this directly from the workflow, not from a script.

Use `ctr plugin ls` as the required check command.

Example check:

```bash
ssh <target> 'ctr plugin ls'
```

Recommended decision rule:

- Treat the host as ready only when the command succeeds and the output shows the expected containerd plugins, especially `overlayfs` and `cri`.
- A stricter check may use:

```bash
ssh <target> 'ctr plugin ls | grep -E "overlayfs|cri"'
```

Rules:

- Check every host before any Kubernetes install step.
- If one host does not have `containerd`, stop the entire task immediately.
- Tell the user to install containerd first, then retry.
- Do not auto-install containerd from this skill.

### 4. Verify role mapping

Before any Kubernetes install step:

- Confirm at least one control-plane node exists.
- Confirm every listed worker exists in the hosts list.
- If any host is missing a role, stop and ask the user to provide a complete mapping.

### 5. Resolve version behavior

Determine two values:

- `K8S_VERSION_FULL`: the exact version to install, such as `1.35.3`.
- `K8S_VERSION_MINOR`: the repository channel, such as `1.35`.

Rules:

- If no version was provided, choose the latest available version and derive the matching `major.minor` repository channel.
- If a version was provided, normalize its repository channel to `major.minor`.
  - Example: `1.35.5` -> `K8S_VERSION_FULL=1.35.5`, `K8S_VERSION_MINOR=1.35`
- Verify that the requested version is actually released before installation.
- If the requested version is unavailable, switch to the latest available version and tell the user in the final report.

### 6. Gather required variable values from the real environment

Do not use example values from documents.

For any installation step that depends on variables such as:

- node IP addresses
- hostnames
- advertise addresses
- interface names
- local paths
- tokens
- discovery hashes
- join commands

use this rule:

- If the user provided the value, use it.
- Otherwise, discover it with commands if that is safe and unambiguous.
- If it still cannot be determined, stop and ask the user.

The following variables are required for the documented workflow:

- Control-plane advertise address
- Control-plane hostname
- Worker hostnames used for labeling
- Pod subnet
- Service subnet
- Calico interface name if Calico installation is requested

Defaults from the document may be used only when they are generic constants and not machine-specific:

- `runtime-endpoint: unix:///run/containerd/containerd.sock`
- `imageRepository: registry.cn-hangzhou.aliyuncs.com/google_containers`
- `dnsDomain: cluster.local`
- kube-proxy mode `ipvs`
- kubelet cgroup driver `systemd`

Do not blindly reuse document sample values for IP addresses, hostnames, tokens, or interface names.

## Installation procedure

Execute the following procedure only after all prerequisite checks succeed.

### A. Install Kubernetes packages on every target host

For every host, configure the Kubernetes repository.

Use the Aliyun repository form by default:

```bash
cat > /etc/yum.repos.d/kubernetes.repo <<EOF
[kubernetes]
name=Kubernetes
baseurl=https://mirrors.aliyun.com/kubernetes-new/core/stable/v${K8S_VERSION_MINOR}/rpm/
enabled=1
gpgcheck=1
gpgkey=https://mirrors.aliyun.com/kubernetes-new/core/stable/v${K8S_VERSION_MINOR}/rpm/repodata/repomd.xml.key
EOF

dnf clean all && dnf makecache
```

Alternative official source, only if the user explicitly wants it and the environment can reach it:

```bash
cat > /etc/yum.repos.d/kubernetes.repo <<EOF
[kubernetes]
name=Kubernetes
baseurl=https://pkgs.k8s.io/core:/stable:/v${K8S_VERSION_MINOR}/rpm/
enabled=1
gpgcheck=1
gpgkey=https://pkgs.k8s.io/core:/stable:/v${K8S_VERSION_MINOR}/rpm/repodata/repomd.xml.key
exclude=kubelet kubeadm kubectl cri-tools kubernetes-cni
EOF

dnf clean all && dnf makecache
```

Version handling:

- If the user wants the latest available version, install without explicit version suffix.
- If the user wants a specific released version, install `kubelet-${K8S_VERSION_FULL} kubeadm-${K8S_VERSION_FULL} kubectl-${K8S_VERSION_FULL}`.
- Rocky Linux 10 may use DNF5. Prefer the documented form first:

```bash
dnf install -y kubelet kubeadm kubectl --disableexcludes=kubernetes
```

- If DNF5 requires the documented alternative, use:

```bash
dnf install -y kubelet kubeadm kubectl --setopt=disable_excludes=kubernetes
```

- For a specific released version, use the same command form but append version suffixes to the three packages.

Then on every host:

```bash
systemctl enable kubelet --now
```

Configure `crictl` on every host:

```bash
cat > /etc/crictl.yaml <<'EOF'
runtime-endpoint: unix:///run/containerd/containerd.sock
image-endpoint: unix:///run/containerd/containerd.sock
timeout: 10
debug: false
EOF

crictl info
```

If any host fails in this phase, stop immediately.

### B. Initialize the cluster on the first control-plane node

Run the following only on the first control-plane node.

Inspect defaults first:

```bash
kubeadm config print init-defaults
```

Create `kubeadm.yaml` on the first control-plane node, replacing all machine-specific values with real values:

```yaml
tee kubeadm.yaml <<EOF
apiVersion: kubeadm.k8s.io/v1beta4
kind: InitConfiguration
localAPIEndpoint:
  advertiseAddress: ${CONTROL_PLANE_ADVERTISE_ADDRESS}
  bindPort: 6443
nodeRegistration:
  criSocket: unix:///run/containerd/containerd.sock
  imagePullPolicy: IfNotPresent
  imagePullSerial: false
  name: ${CONTROL_PLANE_HOSTNAME}
  taints: null
---
apiVersion: kubeadm.k8s.io/v1beta4
kind: ClusterConfiguration
certificatesDir: /etc/kubernetes/pki
clusterName: kubernetes
controllerManager: {}
dns: {}
etcd:
  local:
    dataDir: /var/lib/etcd
imageRepository: registry.cn-hangzhou.aliyuncs.com/google_containers
kubernetesVersion: ${K8S_VERSION_FULL}
networking:
  dnsDomain: cluster.local
  podSubnet: ${POD_SUBNET}
  serviceSubnet: ${SERVICE_SUBNET}
scheduler: {}
certificateValidityPeriod: 87600h
caCertificateValidityPeriod: 175200h
---
apiVersion: kubeproxy.config.k8s.io/v1alpha1
kind: KubeProxyConfiguration
mode: ipvs
---
apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
cgroupDriver: systemd
EOF
```

Before `kubeadm init`, run the documented reachability checks on the first control-plane node:

```bash
nslookup registry.cn-hangzhou.aliyuncs.com
curl -s -o /dev/null -w "%{http_code}" https://registry.cn-hangzhou.aliyuncs.com/v2/
```

Then pull images using the chosen full version:

```bash
kubeadm config images pull \
  --image-repository registry.cn-hangzhou.aliyuncs.com/google_containers \
  --kubernetes-version ${K8S_VERSION_FULL}
```

Initialize the first control-plane node:

```bash
kubeadm init --config=kubeadm.yaml --ignore-preflight-errors=SystemVerification
```

If this fails, stop immediately.

### C. Configure kubeconfig on the first control-plane node

Run only on the first control-plane node:

```bash
mkdir -p $HOME/.kube
cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
chown $(id -u):$(id -g) $HOME/.kube/config
```

Then configure alias and completion exactly as documented:

```bash
tee -a ~/.bashrc <<'EOF'
alias k='kubectl'
source <(kubectl completion bash)
complete -o default -F __start_kubectl k
source /etc/profile
EOF

source ~/.bashrc
```

Validate:

```bash
kubectl get nodes
kubectl get pods -A
```

### D. Join worker nodes

On the first control-plane node, obtain the join command:

```bash
kubeadm token create --print-join-command
```

This command contains the real token and discovery hash. Do not invent either value.

Run the returned join command on every worker node. The documented form is:

```bash
kubeadm join ${CONTROL_PLANE_ADVERTISE_ADDRESS}:6443 \
  --token <token> \
  --discovery-token-ca-cert-hash sha256:<hash> \
  --ignore-preflight-errors=SystemVerification
```

Use the real command produced by `kubeadm token create --print-join-command`.

If any worker join fails, stop immediately.

### E. Label worker nodes on the control-plane node

Back on the first control-plane node, apply labels using real worker hostnames:

```bash
kubectl label nodes ${WORKER_HOSTNAME_1} node-role.kubernetes.io/worker=worker
```

Repeat once per worker node, then verify:

```bash
kubectl get nodes
```

### F. Optional: install Calico

This is optional. Skip it unless the user asks for it.

If requested:

1. Download the latest Calico manifest from the official site. The document example uses v3.31.4 and explicitly says to replace it with the actual latest version.
2. Determine the correct interface name from the real host environment. Do not use the sample `ens160` unless it is truly the interface in use.

Download manifest:

```bash
curl -O https://raw.githubusercontent.com/projectcalico/calico/<actual-version>/manifests/calico.yaml
```

Set the real interface name and patch `calico.yaml` exactly as documented:

```bash
IFACE="${CALICO_INTERFACE}"

if ! grep -q "IP_AUTODETECTION_METHOD" calico.yaml; then
  sed -i "/- name: CLUSTER_TYPE/{n;s/\(.*\)/\1\n            - name: IP_AUTODETECTION_METHOD\n              value: \"interface=${IFACE}\"/}" calico.yaml
fi

grep -A2 "CLUSTER_TYPE" calico.yaml

kubectl apply -f calico.yaml
kubectl get pods -n kube-system -w
```

Optional validation:

```bash
kubectl run busybox --image busybox:1.28 \
  --image-pull-policy=IfNotPresent \
  --restart=Never --rm -it busybox -- sh
```

In the container, the documented checks are:

- `ping www.baidu.com`
- `nslookup kubernetes.default.svc.cluster.local`

### G. Optional: configure NFS

This is optional. Skip it unless the user asks for it.

If requested, run the documented NFS steps.

On all nodes:

```bash
dnf install -y nfs-utils

systemctl start rpcbind && systemctl enable rpcbind
systemctl start nfs-server && systemctl enable nfs-server
```

On the master node only:

```bash
mkdir -p /data/nfs_pro
echo "/data/nfs_pro *(rw,no_root_squash)" >> /etc/exports
exportfs -arv
```

If the user wants network restriction on exports, use the host network range, not the Pod network range.

### H. Optional: install homebrew, k9s, helm

These are optional. Skip them unless the user explicitly asks.

If requested, run only the documented commands from the source procedure.

## Version availability rule

Before installing a user-requested specific version, verify that it exists in the configured repository metadata.

Allowed approach:

- Use repository metadata or package listing commands after `dnf makecache`.
- If the requested version is not present, fall back to the latest available version.
- Report the fallback explicitly.

Do not fabricate unpublished versions.

## Reporting rules

In the final report:

- List which hosts passed SSH probing.
- List which hosts passed the `containerd` prerequisite check.
- State the control-plane and worker mapping used.
- State which Kubernetes version was installed and whether the requested version was honored or replaced by the latest available version.
- State whether Calico was installed.
- State which optional steps were skipped.
- If the task stopped, state the exact phase where it stopped: SSH probe, containerd check, package install, init, join, labeling, or optional step.
