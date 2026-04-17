---
name: docker-runtime-install
description: Install Docker CE and containerd on one or more Linux hosts when the user asks to install a container runtime, Docker, or containerd on remote machines. Use for Linux-only batch installation workflows where the user provides a newline-separated host list and the agent must first verify passwordless SSH access to every host, abort immediately if any host cannot be accessed without a password, then copy a bundled script to each target host and execute it. Follow the bundled workflow strictly; do not invent extra installation steps, extra scripts, or commands outside the documented Rocky Linux 10 procedure.
---

# docker-runtime-install

Execute this skill with low freedom. Follow the workflow exactly. Do not add installation steps, optimizations, validations, package pins, cleanup logic, or helper scripts beyond what this skill already contains.

## Inputs to collect

Collect only the values needed by the workflow.

- Host list: newline-separated items such as:
  ```text
  1.1.1.1
  2.2.2.2
  server-a.example.com
  ```
- SSH login form for each host if needed by the user context, for example `root@1.1.1.1` or `rocky@1.1.1.1`.
- Optional Harbor registry hostname if the user explicitly needs the optional Harbor configuration step.

Default behavior:

- Linux only.
- If the user does not specify package versions, install the latest available versions.
- Skip steps that are explicitly optional unless the user asks for them.

## Hard rules

- Probe passwordless SSH access before doing anything else.
- Do not put the SSH probe into any bundled script; run the probe directly from the workflow.
- If any host fails the passwordless SSH probe, stop the entire task immediately.
- When SSH probing fails, tell the user to complete machine initialization first, then retry.
- Copy the bundled script to each target host with `scp`, then execute it remotely with `ssh`.
- Do not loop inside the bundled install script. Loop over hosts in the workflow only.
- Do not use example values from the original document for IPs, hostnames, local paths, or interface names unless the user provided them or you discovered them from commands.
- If a required per-host variable cannot be obtained from the user or by command inspection, pause and ask the user.
- Do not reference the external technical document from any other skill file or bundled file. Treat it as authoring-time source material only.

## Workflow

### 1. Normalize the target list

Convert the user-provided newline-separated host list into concrete SSH targets.

- If the login user is obvious from context, form targets like `user@host`.
- If the login user is not known, ask the user before probing.
- Remove blank lines.
- Preserve the user-provided order.

### 2. Probe passwordless SSH access on every host

For each target, run a direct SSH probe from the agent environment, for example:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 <target> 'true'
```

Rules:

- Run this probe for every host before any copy or installation step.
- If one host fails, stop immediately. Do not continue with the remaining hosts.
- Respond with a clear stop reason such as: a host does not support passwordless SSH yet and the machines must be initialized first.

### 3. Confirm required variables

Before execution, confirm only variables that are truly required.

- Harbor hostname is required only when the user wants the optional Harbor registry configuration.
- If the user wants that optional step but does not provide the Harbor hostname and it cannot be discovered safely, pause and ask.

### 4. Copy the install script to each host

Use the bundled script:

- `scripts/install-rocky-linux10-docker-containerd.sh`

For each host, copy it to a temporary remote path, for example:

```bash
scp scripts/install-rocky-linux10-docker-containerd.sh <target>:/tmp/install-rocky-linux10-docker-containerd.sh
```

### 5. Execute the install script on each host

Run the copied script remotely.

Without Harbor step:

```bash
ssh <target> 'bash /tmp/install-rocky-linux10-docker-containerd.sh'
```

With Harbor step:

```bash
ssh <target> 'HARBOR_HOST=<harbor-hostname> bash /tmp/install-rocky-linux10-docker-containerd.sh'
```

Execution rules:

- Execute hosts one by one.
- If one host execution fails, stop and report which host failed.
- Do not add extra remote commands before or after the bundled script except the minimal `scp` and `ssh` needed to deliver and run it.

## Bundled script

### `scripts/install-rocky-linux10-docker-containerd.sh`

Purpose:

- Run the documented Rocky Linux 10 installation steps for Docker CE and containerd on one host.
- Optionally add Harbor registry configuration only when `HARBOR_HOST` is provided.

Usage:

```bash
bash install-rocky-linux10-docker-containerd.sh
```

Optional Harbor step:

```bash
HARBOR_HOST=harbor.example.local bash install-rocky-linux10-docker-containerd.sh
```

Do not inline the script contents into this file. Use the bundled script as-is.

## Reporting back to the user

When finished:

- Report which hosts completed successfully.
- Report any host that failed and at which phase it failed: SSH probe, copy, or install.
- If optional steps were skipped, say so explicitly.
- If versions were not specified by the user, state that the latest available packages were installed.
