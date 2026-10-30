---
type: Reference
description: Test matrix for third-party package updates in Bottlerocket kits — maps every package to a test Type (0 none/library, 1 pod runs, 2 Kubernetes conformance, 4 SOCI snapshotter, 5 image-verifier pull, 6 targeted host one-liner over sheltie, plus GPU and EKS-join special cases), the runner skill that validates each Type, containerd/Kubernetes stream pairing, test-node instance types, and the per-package Type 6 commands with their execution gotchas.
---

# Third-party package test matrix

After a package bump (`document/core-kit/updating-third-party-packages`), build an image with the new RPM and validate it on a node. "Tested" means different things for different packages; this matrix fixes that per package. The authoritative package → Type mapping is the `classify-package.sh` script in `skill/test-third-party-package`; the tables below list the members.

ECS-tier packages (`amazon-ssm-agent`, `docker-cli-*`, `docker-engine-*`, `docker-init`, `ecs-agent`, `ecs-gpu-init`) are out of scope for this matrix.

## Baseline for every package

- **Node boots** — `launch-bottlerocket-ec2`.
- **Node joins** (Kubernetes variants) — `eks-smoke-test`. This is also the test for `aws-iam-authenticator` (the node-join auth path).

## Types

| Type | Packages | Test | Runner skill |
|---|---|---|---|
| 0 | libacl, libattr, libaudit, libbpf, libcap, libxcrypt, libz, libzstd, dbus-broker, binutils, libgcc, libstd-rust, libcrypto, libjansson, libjson-c, libnl, libpopt, libudev, libdrm, cni, cni-plugins | None beyond the baseline — libraries are exercised through their dependents | — |
| 1 | runc, pigz, libseccomp, containerd-1.7, containerd-2.1, containerd-2.2 | A pod schedules, pulls and runs | `simple-pod-runner` |
| 2 | kubernetes-1.30 … kubernetes-1.36 | Kubernetes conformance, once per updated Kubernetes minor / cluster type | `conformance-runner` |
| 4 | soci-snapshotter | A pod pulls through the SOCI snapshotter | `soci-snapshotter-tester` |
| 5 | ecr-credential-helper | Pull through the notation image verifier | `ssm-executor` |
| 6 | host-tier packages (table below) | Targeted host command over `sheltie` | `ssm-executor` |
| GPU | nvidia-k8s-device-plugin, nvidia-container-toolkit, libnvidia-container, other `nvidia-*` | A GPU pod runs on a GPU node | `nvidia-smoke-test-runner` |
| EKS | aws-iam-authenticator | Node registers with the cluster | `eks-smoke-test` |

Not covered by this matrix (boot/baseline only): ROCm tooling (`rocm-container-toolkit`, `rocm-k8s-device-plugin`); core OS/init/config components (`systemd-*`, `early-boot-config`, `static-pods`, `netdog`, `login`, `os`, `release`, `filesystem`, `selinux-policy`, `rottweiler`); and `amazon-ecs-cni-plugins`, `amazon-vpc-cni-plugins`, `cri-tools`, `host-ctr`, `erofs-utils`, `libaio`, `libtss2`, `tpm2-tools`, `nftables`, `notation`, `aws-signer-notation-plugin`, `aws-signing-helper`, `aws-otel-collector`, `perf`, `pciutils`, `rdma-core`, `ecr-credential-provider-*`. Anything else is unclassified — decide manually (default: baseline plus the most relevant smoke test).

**containerd ↔ Kubernetes streams.** Test `containerd-1.7` on a Kubernetes 1.30/1.31/1.32 variant, `containerd-2.1` on 1.33/1.34/1.35, `containerd-2.2` on 1.36.

**Type 2.** `kubernetes-1.NN` maps 1:1 to a Kubernetes minor; run conformance once per updated minor (and cluster type). `conformance-runner` picks its own instance types.

## Test nodes

For Type 1/4/6, use a general test node with NVMe instance store, which `apiclient ephemeral-storage init` (xfsprogs/e2fsprogs tests) requires:

| arch | instance type |
|---|---|
| x86_64 | `i7ie.12xlarge` |
| aarch64 | `i8g.12xlarge` |

Without instance store, the ephemeral-storage tests need extra attached volumes. Destructive tests (kdump, cryptsetup, SELinux policy load, storage reconfiguration) must run only on throwaway nodes.

## Type 5 — ecr-credential-helper

On the node, in a `sheltie` shell (via `ssm-executor`):
```bash
apiclient apply <<EOF
[settings.image-verifier-plugins]
enabled = true
EOF
cat /etc/containerd/image-verifiers/notation/trustpolicy.json
ctr i pull public.ecr.aws/docker/library/hello-world:latest
```
Pass = the trust policy is present and the pull succeeds with the verifier enabled.

## Type 6 — host one-liners

Run through `ssm-executor` (its sheltie-command helper) on the test node. `<arch>` is `x86_64` or `aarch64`.

### Execution model

1. **Enable the admin host container first.** `sheltie` and `apiclient exec admin` go through it; when `host-containers.admin.enabled=false` every command fails with `ctr: container "admin" ... not found`. From the control container: `apiclient set host-containers.admin.enabled=true`.
2. **`sheltie -- <cmd>` execs one host binary** (nsenter): no pipes, redirects or builtins, and the binary must be on the host root PATH. Pipe the *output* in the control-container shell, rewrite `cat x | grep` as `grep PATTERN x`, and run anything needing redirects from an interactive `sudo sheltie` shell.
3. **Some tools exist only in the admin container** — e.g. `bash` and `ping` on aws-k8s builds; run them as `apiclient exec admin <cmd>` (no `sheltie --`).
4. **Availability varies by variant.** `hwloc-ls`, `strace` and `cryptsetup` were absent from both the host and admin container on an aws-k8s build. Confirm the binary exists on the AMI under test before relying on its one-liner.
5. **Device paths depend on instance type.** Run `nvme list` before `nvme amzn stats <dev>`; an m5 has only EBS `nvme0n1`/`nvme1n1`.

### Commands

| Package(s) | Command(s) | Notes |
|---|---|---|
| glibc, kmod | — | Pass = an aws-dev instance boots |
| chrony | `systemctl status chronyd` (or `is-active`) | active |
| bash, readline, libncurses | `bash --version` | admin container on some builds |
| hwloc | `hwloc-ls` | topology prints |
| iptables, libnftnl | `iptables --version` | |
| iputils | `ping -c1 amazon.com` | DNS resolution is the signal; ICMP may be blocked by the security group |
| kexec-tools, makedumpfile, libelf | `echo c > /proc/sysrq-trigger` (needs a shell: run it in an interactive `sudo sheltie` session, not `sheltie --`) | **Destructive**: crashes the node to exercise kdump. After reboot, check `/var/log/kdump` |
| keyutils | `keyctl --version` | |
| nvme-cli, libnvme | `nvme version`; `nvme list`; `nvme amzn stats /dev/<dev>` | device varies |
| procps | `ps -ef` | |
| strace | `strace --version`; `strace ls` | |
| util-linux | `findmnt`; `findmnt -V` | |
| libdevmapper, libcryptsetup | `cryptsetup luksFormat --pbkdf argon2id --batch-mode --key-file /tmp/passphrase /dev/<dev>`; `cryptsetup open --key-file /tmp/passphrase /dev/<dev> crypt`; `ls -l /dev/mapper/crypt`; `cryptsetup --version` | needs an extra attached EBS volume (~100 GB); destroys its contents |
| coreutils | `sha256sum /<arch>-bottlerocket-linux-gnu/sys-root/usr/share/licenses/xfsprogs/GPL-2.0` | arch-specific path |
| xfsprogs, liburcu, mdadm, libinih | `apiclient ephemeral-storage init -t xfs`; `apiclient ephemeral-storage bind --dirs /var/lib/kubelet`; `cat /usr/share/xfsprogs/mkfs/default.conf`; `df -h /var/lib/kubelet`; `mkfs.xfs -V` | needs instance store; reconfigures storage |
| e2fsprogs | `apiclient ephemeral-storage init -t ext4`; `apiclient ephemeral-storage bind --dirs /var/lib/kubelet`; `df -h /var/lib/kubelet`; `mkfs.ext4 -V` | needs instance store |
| ethtool | `ethtool --version` | |
| findutils | `find /usr/bin -name whoami` | |
| grep, libpcre | `grep GNU /<arch>-bottlerocket-linux-gnu/sys-root/usr/share/licenses/xfsprogs/GPL-2.0` | arch-specific path |
| iproute | `ip maddress show` | |
| policycoreutils | `semodule -i /tmp/test.cil` | needs a staged test `.cil`; modifies SELinux policy |
| acpid, open-vm-tools, libffi, libglib, libisal, libtirpc | — | node boots / library loads; no dedicated command |
| libmnl, libnetfilter_conntrack, libnetfilter_cthelper, libnetfilter_cttimeout, libnetfilter_queue, conntrack-tools, libnfnetlink | exercise via iptables/conntrack | no single command |
| libselinux, libsemanage, libsepol | `getenforce`; `semodule -l` | node boots enforcing |
