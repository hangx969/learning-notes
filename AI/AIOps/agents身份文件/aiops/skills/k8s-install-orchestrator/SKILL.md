---
name: k8s-install-orchestrator
description: Orchestrate a Kubernetes cluster installation across specialist agents when the user asks AIOps to install K8s, Kubernetes, or a K8s cluster on one or more Linux machines. Use for serial multi-agent task routing where AIOps must take the user-provided machine list as-is, send it first to the linux specialist for machine initialization, then to the container specialist for container runtime installation, then to the k8s specialist for cluster installation and initialization, and only proceed to the next stage after the previous stage explicitly completes successfully. Do not execute shell commands, do not generate scripts, and do not perform installation directly.
---

# k8s-install-orchestrator

Execute this skill with very low freedom.

- This skill is for orchestration only.
- Do not execute shell commands.
- Do not generate scripts.
- Do not perform Linux initialization, container runtime installation, or Kubernetes installation directly.
- Do not merge stages.
- Run stages strictly in order.
- If any stage fails or pauses for missing information, stop the workflow and report back to the user.

## Purpose

Take the user-provided machine list and installation intent, then route the work to the correct specialist agents in this exact order:

1. `linux` specialist: machine initialization
2. `container` specialist: Docker and containerd installation
3. `k8s` specialist: Kubernetes cluster installation and initialization

AIOps is the coordinator only. It must not replace or bypass any specialist.

## Input handling

Accept the machine list exactly as the user provides it.

The input format can be flexible, including forms such as:

- IP only
- hostname only
- `IP USERNAME PASSWORD`
- mixed lines with additional notes
- any other raw machine list format provided by the user

Rules:

- Do not normalize, rewrite, or simplify the machine list unless the receiving specialist explicitly needs clarification.
- Forward the machine list to downstream specialists essentially as provided by the user.
- Preserve any role mapping, version requirement, or extra notes supplied by the user.
- If the user did not provide required machine-specific values and a downstream specialist cannot determine them from commands, stop and ask the user.

## Global rules

- Linux only. Do not consider Windows.
- Serial only. Never run stages in parallel.
- Only continue when the previous specialist explicitly reports successful completion.
- If a specialist reports failure, stop immediately and report the failure.
- If a specialist asks for missing data, stop immediately and relay the question to the user.
- Optional steps may be skipped unless the user explicitly asks for them. Mention skipped optional steps in the final summary.
- If the user does not specify software versions, downstream specialists should install the latest available versions.
- Never use document sample values for IP addresses, hostnames, local paths, network interfaces, tokens, or other machine-specific values.

## Orchestration workflow

### Stage 1: Linux initialization

Send the machine list to the `linux` specialist first.

Requirements for the dispatch message:

- State that the target task is machine initialization for K8s preparation.
- State that the linux specialist must use its machine initialization skill.
- State that it must not add any extra operations, extra commands, or extra scripts outside that skill.
- State that if any required machine-specific value is missing and cannot be discovered safely, it must stop and ask the user.
- State that if initialization fails, it must stop immediately and return the failure instead of attempting repairs.

Do not continue until the linux specialist clearly reports one of these outcomes:

- **Success**: initialization completed for the intended machines
- **Blocked**: missing required information; ask the user
- **Failed**: initialization failed; stop the overall workflow

### Stage 2: Container runtime installation

Only after Stage 1 succeeds, send the machine list to the `container` specialist.

Requirements for the dispatch message:

- State that Linux initialization is complete.
- State that the target task is container runtime installation for the same machines.
- State that the container specialist must use its Docker/containerd installation skill.
- State that it must not add any extra operations, extra commands, or extra scripts outside that skill.
- State that if any required machine-specific value is missing and cannot be discovered safely, it must stop and ask the user.
- State that if installation fails, it must stop immediately and return the failure instead of attempting repairs.

Do not continue until the container specialist clearly reports one of these outcomes:

- **Success**: container runtime installation completed for the intended machines
- **Blocked**: missing required information; ask the user
- **Failed**: installation failed; stop the overall workflow

### Stage 3: Kubernetes installation and initialization

Only after Stage 2 succeeds, send the machine list to the `k8s` specialist.

Requirements for the dispatch message:

- State that Linux initialization is complete.
- State that Docker installation is already complete.
- State that containerd installation is already complete.
- State that the target task is Kubernetes cluster installation and initialization for the same machines.
- Forward the user-provided control-plane / worker role mapping if present.
- Forward the user-provided version if present.
- State that the k8s specialist must use its Kubernetes installation skill.
- State that it must not add any extra operations, extra commands, or extra scripts outside that skill.
- State that if any required machine-specific value is missing and cannot be discovered safely, it must stop and ask the user.
- State that if installation fails, it must stop immediately and return the failure instead of attempting repairs.

Do not continue after this stage except to summarize the outcome for the user.

## Dispatch composition rules

When sending a task to a specialist, include only the information that matters:

- the current stage objective
- the raw machine list from the user
- any role mapping from the user
- any version requirement from the user
- the hard rule that the specialist must use its own relevant skill only
- the hard rule that the specialist must not add extra operations or scripts
- the hard rule that missing machine-specific values must trigger a pause and question, not guessing
- the hard rule that failure ends the stage immediately without repair attempts

Do not add your own implementation ideas.

## Stop conditions

Stop the orchestration immediately when any of the following happens:

1. A specialist reports failure.
2. A specialist reports missing required information.
3. The user input is too ambiguous to know which machines are in scope.
4. The user did not provide necessary node-role information by the time the k8s stage needs it.
5. A previous stage has not explicitly completed but a later stage is about to start.

## Final reporting

When the workflow ends, report in a compact stage-based summary:

- Stage 1 Linux initialization: success / blocked / failed
- Stage 2 container runtime installation: success / blocked / failed / not started
- Stage 3 Kubernetes installation and initialization: success / blocked / failed / not started

Also report:

- which optional steps were skipped
- whether latest versions were used by default because the user did not specify versions
- any missing machine-specific values that still require user input

## Example dispatch shape

Use this as a style guide, not as a fixed template.

### To linux specialist

- Task: initialize the following Linux machines for K8s preparation
- Machine list: <raw user input>
- Constraint: must use the machine initialization skill only
- Constraint: must not add extra operations or scripts
- Constraint: if any required variable is missing and cannot be discovered safely, stop and ask
- Constraint: if initialization fails, stop and report failure

### To container specialist

- Task: install Docker and containerd on the following machines
- Precondition: Linux initialization already completed
- Machine list: <raw user input>
- Constraint: must use the container runtime installation skill only
- Constraint: must not add extra operations or scripts
- Constraint: if any required variable is missing and cannot be discovered safely, stop and ask
- Constraint: if installation fails, stop and report failure

### To k8s specialist

- Task: install and initialize a Kubernetes cluster on the following machines
- Precondition: Linux initialization already completed
- Precondition: Docker and containerd installation already completed
- Machine list: <raw user input>
- Role mapping: <user-provided role mapping>
- Version: <user-provided version or latest>
- Constraint: must use the Kubernetes installation skill only
- Constraint: must not add extra operations or scripts
- Constraint: if any required variable is missing and cannot be discovered safely, stop and ask
- Constraint: if installation fails, stop and report failure
