---
type: Guide
description: How to get onto a running Bottlerocket host to inspect or change it — the control and admin host containers, sheltie, apiclient (get/set/apply/exec), non-interactive AWS SSM send-command, interactive SSM sessions, and the Kubernetes alternative of a privileged host-namespace pod — with the security implications and teardown steps for each.
---

# Host access and debugging

Bottlerocket ships no shell or SSH on the host. You reach the host through *host containers*, which run under a separate `host-containerd` outside the orchestrator (see `document/bottlerocket/glossary`). On Kubernetes nodes there is also the option of a privileged pod. Matching skills: `skill/ssm-executor` and `skill/k8s-node-executor`. To launch a node in the first place, see `document/bottlerocket/testing-on-aws`.

## The access chain

```
SSM ──▶ control container ──apiclient exec admin──▶ admin container ──sheltie──▶ host (root, all namespaces)
```

| Context | Enabled by default (AWS) | What you get |
|---|---|---|
| **control** | yes | Runs the SSM agent. You get `apiclient` (talks to the API server over `/run/api.sock`) and a basic userland, but not the host filesystem or host processes. |
| **admin** | no | A "superpowered" container with SSH and the `sheltie` helper. Enable it with `apiclient set host-containers.admin.enabled=true` (or `enable-admin-container` in the control container), or `[settings.host-containers.admin] enabled = true` in user-data. |
| **sheltie** | n/a | Run from the admin container, it enters the host's namespaces as root. From there you can use host binaries (`systemctl`, `journalctl`, `containerd`, `kubelet`, `ctr`) and the real `/`. |

## apiclient essentials

```bash
apiclient get settings                      # all settings (JSON)
apiclient get settings.kubernetes           # one subtree
apiclient get os                            # variant, version, arch
apiclient set motd="debug session"          # set one or more keys, then commit + apply
apiclient apply < settings.toml             # apply a TOML/JSON document (reads stdin by default)
apiclient exec admin <cmd...>               # run a command inside a host container
apiclient exec admin sheltie -- <cmd...>    # ...or on the host itself via sheltie
```

Changes made with `set`/`apply` persist and restart the affected services (for example, changing `settings.container-runtime.snapshotter` restarts containerd).

## Over AWS SSM

Prerequisites: the instance profile includes `AmazonSSMManagedInstanceCore`, the instance can reach the SSM endpoints (internet or VPC endpoints), and `aws ssm describe-instance-information` shows the instance as `Online` with platform `Bottlerocket`. If you attached the role after launch, the instance may need a reboot before it shows up.

**Interactive:** `aws ssm start-session --target <instance-id>` puts you in the control container. From there, `enter-admin-container` (with the admin container enabled) and then `sudo sheltie` gives a root shell on the host.

**Non-interactive:** `aws ssm send-command --document-name AWS-RunShellScript` runs `commands` in the control container. Prefix a command with `apiclient exec admin sheltie --` to run it on the host. Fetch the output with `aws ssm get-command-invocation` once the command finishes (`aws ssm wait command-executed`). Build the `--parameters` JSON with a JSON encoder rather than string interpolation, because quotes in the command will break it. For multi-line input such as TOML, base64 it, then decode and pipe it on the node.

Useful host commands: `systemctl status kubelet containerd`, `journalctl -u kubelet`, `journalctl -u early-boot-config` (user-data processing), `cat /etc/os-release`, `df -h`, `ip addr`, `ip route`, `ss -tlnp`. Commands that fail with "not found" or "permission denied" in the control container usually need sheltie.

SSM works for any EC2 instance: EKS, ECS, standalone, or a node that never joined its cluster. That makes it the default when kubelet is broken.

## Privileged host-namespace pod (Kubernetes)

If you have `kubectl` but no SSM, you can schedule a pod on the node with `hostNetwork`, `hostPID` and `hostIPC` set, `privileged: true`, and the host root mounted at `/host` (pin it to a node with `spec.nodeName`). Inside that pod:

- Run host binaries with `chroot /host <cmd>`, e.g. `chroot /host apiclient get os` or `chroot /host systemctl status kubelet`. Without the chroot, `/host/usr/bin/apiclient` looks for `/run/api.sock` inside the pod and fails.
- Read host files at `/host/...` (`/host/etc/os-release`).
- Process and network tools (`ps`, `ip`, `ss`, `iptables`) already see the host because of the host namespaces.
- Container runtime: `chroot /host ctr -n k8s.io containers list`.
- Extra tools can be installed in the pod image (e.g. `dnf install tcpdump strace bind-utils` on an Amazon Linux base). They are not added to the host.

Namespaces that enforce Pod Security Standards `baseline` or `restricted` reject this pod. Use a namespace labelled `pod-security.kubernetes.io/enforce=privileged`, or a policy exception. Use public base images (e.g. `public.ecr.aws/amazonlinux/amazonlinux:2023`) so the pull doesn't need registry credentials.

## Security implications

- The admin container, sheltie, and a privileged host pod each amount to **root on the node**. They can read and modify any host file, see every container's processes and secrets, and change settings in ways that destabilise the node.
- `apiclient set`/`apply` changes persist and restart services. On a shared or production node, record the original value and restore it.
- Use these paths on test nodes. Tear them down as soon as you are finished: `kubectl delete pod <executor>`, and `apiclient set host-containers.admin.enabled=false` if you enabled the admin container just for this. Never leave a privileged debug pod running.
- Prefer read-only commands (`get`, `status`, `journalctl`) over mutating ones unless the test requires a change.
