---
type: Skill
description: Run commands on a Bottlerocket EC2 instance through AWS SSM — in the control container (apiclient) or on the host via admin container + sheltie — use for debugging any Bottlerocket instance (EKS, ECS, standalone, or a node that never joined its cluster) when kubectl access is unavailable or insufficient.
---

# SSM executor

Background on the control container → admin container → sheltie chain, apiclient, interactive sessions and security: `document/bottlerocket/host-access-and-debugging`. Scripts are in `references/scripts/` and should be run from this skill's directory. They need the AWS CLI and `jq`.

## Procedure

1. **Check connectivity:** `references/scripts/verify-connectivity.sh INSTANCE_ID REGION` should show `Online` and `Bottlerocket`. If the instance isn't listed, check the instance profile (`AmazonSSMManagedInstanceCore`) and the network path to the SSM endpoints.
2. **Control-container commands** (apiclient and basic tools):
   ```bash
   references/scripts/control-container-command.sh INSTANCE_ID REGION "apiclient get os"
   references/scripts/control-container-command.sh INSTANCE_ID REGION "apiclient get settings.kubernetes"
   ```
3. **Host commands** (root, host namespaces). These need the admin container. If it's disabled and the user agrees, enable it with `control-container-command.sh ... "apiclient set host-containers.admin.enabled=true"`, then:
   ```bash
   references/scripts/sheltie-command.sh INSTANCE_ID REGION "systemctl status kubelet"
   references/scripts/sheltie-command.sh INSTANCE_ID REGION "journalctl -u containerd --no-pager -n 100"
   ```
   The command is split into words and passed to sheltie, so wrap pipes and `&&` in `bash -c '...'`, or they will run in the control container instead.
4. The scripts wait for completion, print stdout and stderr, and exit non-zero if the SSM status isn't `Success`.

## Rules

- Prefer read-only commands. `apiclient set`/`apply` changes persist and restart services, so record the old value and get the user's agreement first on any node that might be shared or production.
- If you enabled the admin container just for this, disable it again when you're done (`apiclient set host-containers.admin.enabled=false`).
- On Kubernetes nodes where SSM isn't available, use `skill/k8s-node-executor` instead.
