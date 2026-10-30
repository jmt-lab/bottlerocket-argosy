---
type: Skill
description: Node-join smoke test for a Bottlerocket EKS AMI — launch one node on the AMI into an existing EKS cluster and confirm it registers and reaches Ready; use after building an AMI or updating packages, as the fast gate before conformance or other heavier tests.
---

# EKS smoke test (node join)

Checks only whether a node on the AMI joins and goes `Ready`. For conformance, use `skill/conformance-runner`. Background and troubleshooting: `document/bottlerocket/testing-on-aws`.

## Inputs

AMI ID, cluster name, region, an instance type matching the arch (`m5.large` for x86_64, `m6g.large` for aarch64), plus `SUBNET_ID`, `SG_ID` (cluster SG and control-plane SG, space-separated) and `INSTANCE_PROFILE` (an EKS node profile whose role is mapped into the cluster). You need `kubectl` access to the cluster and `jq`.

## Procedure

1. Launch the node with `skill/launch-bottlerocket-ec2`, running from that skill's directory:
   ```bash
   references/scripts/get-eks-details.sh CLUSTER_NAME /tmp/userdata.toml
   INSTANCE_ID=$(references/scripts/launch-instance.sh AMI_ID /tmp/userdata.toml)
   references/scripts/wait-for-instance.sh "$INSTANCE_ID"
   ```
2. From this skill's directory, wait for the node to join:
   ```bash
   references/scripts/wait-for-node-join.sh "$INSTANCE_ID" 300
   ```
   The script matches the node on `.spec.providerID`, so it doesn't depend on the node's registered name. It prints `PASS` when the node is `Ready`. On a timeout it prints `FAIL` with `kubectl describe node` output.
3. Clean up: `aws ec2 terminate-instances --instance-ids "$INSTANCE_ID" --region "$REGION"`.

## If it fails

- The node never registers: bad user-data, a stale CA (regenerate it), security groups, or the node role isn't mapped into the cluster.
- The node registers but stays `NotReady`: inspect `journalctl -u kubelet` with `skill/ssm-executor` before you terminate the instance.
