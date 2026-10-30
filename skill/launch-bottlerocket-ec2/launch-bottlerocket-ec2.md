---
type: Skill
description: Launch a Bottlerocket EC2 instance from a given AMI with correct TOML user-data (EKS node or standalone), wait for it to run, and confirm SSM and cluster registration — use when you need a live node to test a custom or public Bottlerocket AMI, settings change, or debugging scenario.
---

# Launch a Bottlerocket EC2 instance

Background (IAM, user-data format, AMI lookup, verification, cleanup): `document/bottlerocket/testing-on-aws`. Scripts are in `references/scripts/` and should be run from this skill's directory. They need the AWS CLI and `jq`.

## Inputs

AMI ID (or look up a public one through the SSM parameter shown in the doc), region, an instance type that matches the AMI arch, and for `aws-k8s-*` variants the EKS cluster name.

## Procedure

1. Run `aws sts get-caller-identity` to confirm you're in the intended account. Treat any account you can't positively identify as production and don't launch there without asking.
2. Choose the network: `aws ec2 describe-subnets` / `describe-security-groups --filters Name=vpc-id,Values=<vpc>`. EKS nodes usually need both the cluster SG and the control-plane SG.
3. Write the user-data:
   - EKS: `references/scripts/get-eks-details.sh CLUSTER_NAME /tmp/userdata.toml` builds `[settings.kubernetes]` from a live `describe-cluster`. Run it right before launch and never hand-copy the CA.
   - Standalone: write a small TOML (e.g. `motd`, or `[settings.host-containers.admin] enabled = true` if you will need sheltie). Empty user-data is valid too.
4. Launch:
   ```bash
   export REGION=us-west-2 SUBNET_ID=subnet-... SG_ID="sg-a sg-b" INSTANCE_PROFILE=<profile> \
          INSTANCE_TYPE=m5.large INSTANCE_NAME=bottlerocket-test
   INSTANCE_ID=$(references/scripts/launch-instance.sh AMI_ID /tmp/userdata.toml)
   references/scripts/wait-for-instance.sh "$INSTANCE_ID"
   ```
   `SG_ID` is deliberately expanded unquoted, so a space-separated list passes several groups.
5. Verify: SSM `PingStatus` is `Online` (`skill/ssm-executor`'s `verify-connectivity.sh`), and for EKS the node reaches `Ready` (`skill/eks-smoke-test`'s `wait-for-node-join.sh`).

## Cleanup

`aws ec2 terminate-instances --instance-ids "$INSTANCE_ID" --region "$REGION"` once you're done. Report the instance ID to the user so nothing gets left running.

## Common issues

- `x509: certificate signed by unknown authority` means the CA is stale or corrupted. Re-run `get-eks-details.sh`.
- The node doesn't join: check security groups and the node role's access entry or `aws-auth` mapping.
- SSM is offline: check the instance profile has `AmazonSSMManagedInstanceCore` and there's a network path to the SSM endpoints.
- Settings weren't applied: the TOML is invalid or has unknown keys. Inspect with `apiclient get settings` and `journalctl -u early-boot-config` (see `document/bottlerocket/host-access-and-debugging`).
