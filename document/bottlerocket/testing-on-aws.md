---
type: Guide
description: How to validate a Bottlerocket image on AWS by hand — find or build an AMI, write TOML user-data for standalone and EKS nodes, launch with the AWS CLI, verify the node joins and reaches Ready, run Kubernetes conformance with kubetest2 eksapi + ginkgo, run container-runtime, GPU and SOCI snapshotter smoke pods, and clean up so nothing keeps billing.
---

# Testing Bottlerocket images on AWS

This guide covers ad-hoc, CLI-driven validation of an AMI: launching a node, checking it works, running targeted smoke tests. The repo's automated TestSys flow (`cargo make test`, `TESTSYS_*` env) is described in `document/bottlerocket/development`; AMI registration (`cargo make ami`) is there too. To get onto a node to debug, see `document/bottlerocket/host-access-and-debugging`.

Matching skills: `skill/launch-bottlerocket-ec2`, `skill/eks-smoke-test`, `skill/conformance-runner`, `skill/simple-pod-runner`, `skill/nvidia-smoke-test-runner`, `skill/soci-snapshotter-tester`.

## Prerequisites

- AWS CLI with credentials for the target account, plus `jq` and `kubectl`. Check who you are with `aws sts get-caller-identity` before creating anything.
- A VPC subnet and security group(s). EKS nodes usually need both the cluster security group and the control-plane security group.
- An IAM instance profile. Every Bottlerocket node needs `AmazonSSMManagedInstanceCore` (the control container runs the SSM agent). EKS nodes also need `AmazonEKSWorkerNodePolicy`, `AmazonEKS_CNI_Policy` and `AmazonEC2ContainerRegistryReadOnly`, and the role must be allowed into the cluster (an EKS access entry for the node role, or an `aws-auth` mapping). See [EKS node IAM role](https://docs.aws.amazon.com/eks/latest/userguide/create-node-role.html).
- An AMI: one you built and registered, or a public one. Public Bottlerocket AMI IDs are published as SSM parameters:

```bash
aws ssm get-parameter --region us-west-2 \
  --name /aws/service/bottlerocket/aws-k8s-1.33/x86_64/latest/image_id \
  --query Parameter.Value --output text
```

Match the instance type to the AMI architecture (`m5.*` for x86_64, `m6g.*` for aarch64), and the cluster Kubernetes version to the variant (`aws-k8s-1.33` goes in a 1.33 cluster).

## User-data (TOML settings)

Bottlerocket reads EC2 user-data as TOML and applies it through the settings API on first boot; it does not use cloud-init. Keys are the same `settings.*` paths that `apiclient get`/`set` use. Upstream reference: [Using user data](https://github.com/bottlerocket-os/bottlerocket#using-user-data) and the settings reference on [bottlerocket.dev](https://bottlerocket.dev/).

**EKS node (`aws-k8s-*`)**: these three settings are the minimum.

```toml
[settings.kubernetes]
api-server = "https://<endpoint>"
cluster-name = "<cluster>"
cluster-certificate = "<base64 CA data>"
```

Generate it from `aws eks describe-cluster` right before launch (the `get-eks-details.sh` script in `skill/launch-bottlerocket-ec2` does this). Never copy the CA by hand or cache it between steps: one bad character in the base64 shows up as `x509: certificate signed by unknown authority`.

**Standalone / `aws-dev` / debugging**: user-data can be empty, or carry only what you need, for example:

```toml
[settings]
motd = "test node"

[settings.host-containers.admin]
enabled = true          # only if you need sheltie; see host-access-and-debugging
```

ECS variants need `settings.ecs.cluster`. Other features are just more tables in the same file, e.g. the SOCI snapshotter settings below. Invalid TOML or unknown keys mean the settings are not applied, so check `apiclient get settings` on the node if the node isn't behaving as configured.

## Launching

```bash
aws ec2 run-instances --region "$REGION" --image-id "$AMI" --instance-type m5.large \
  --subnet-id "$SUBNET_ID" --security-group-ids $SG_IDS \
  --iam-instance-profile "Name=$PROFILE" --user-data file://userdata.toml \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=bottlerocket-test}]'
aws ec2 wait instance-running --instance-ids "$ID" --region "$REGION"
```

Always tag test instances so they are easy to find during cleanup.

## Verifying the node

1. **EC2 status**: `aws ec2 describe-instance-status --instance-ids "$ID"`.
2. **SSM registration**: `aws ssm describe-instance-information --filters Key=InstanceIds,Values=$ID` should show `PingStatus` `Online` and platform `Bottlerocket`. This is what host access depends on.
3. **Node join (EKS)**: find the node whose `.spec.providerID` contains the instance ID. That works whatever name the node registered under. Then wait for its `Ready` condition to be `True` (about 1–3 minutes after boot is typical; allow 5).
   - It never registers: usually bad user-data, a stale CA, security groups that block the control plane, or a node role that isn't mapped into the cluster.
   - It registers but stays `NotReady`: usually the CNI or kubelet. Check `journalctl -u kubelet` on the host.

## Kubernetes conformance (kubetest2 eksapi)

To run conformance on an AMI, create a throwaway EKS cluster with unmanaged nodes booted from that AMI, run the upstream ginkgo `[Conformance]` suite, and delete the cluster. Tooling:

```bash
go install sigs.k8s.io/kubetest2/...@latest              # kubetest2 + kubetest2-tester-ginkgo
go install github.com/aws/aws-k8s-tester/...@HEAD        # kubetest2-eksapi deployer
export PATH="$PATH:$(go env GOPATH)/bin"
```

The core invocation:

```bash
kubetest2 eksapi --region "$REGION" --kubernetes-version 1.33 \
  --user-data-format bottlerocket --unmanaged-nodes --ami "$AMI" \
  --instance-types m5.xlarge --nodes 15 --up --down \
  --test ginkgo -- \
  --test-package-marker latest-1.33.txt --parallel 15 \
  --ginkgo-args --flake-attempts=3 \
  --focus-regex='\[Conformance\]' \
  --skip-regex='\[Serial\]|\[Disruptive\]|\[Slow\]|Garbage.collector'
```

- `--user-data-format bottlerocket` makes the deployer write TOML user-data instead of a bootstrap script.
- `--test-package-marker` selects the e2e test binaries and must match the cluster version (`latest-<minor>.txt`).
- `--up --down` tears the cluster down even when tests fail. To debug failing nodes, get onto them over SSM before the down phase runs.
- Credentials need to be able to create and delete EKS clusters, EC2 instances, IAM roles and CloudFormation stacks.
- A pass looks like ginkgo printing `SUCCESS!` and a zero exit code. Run once per Kubernetes minor version under test.

## Targeted smoke pods

Each of these is one pod that is applied, waited on, logged, and deleted. Pick the one that exercises what you changed.

| Change under test | Pod | Pass criterion |
|---|---|---|
| Container runtime path (`runc`, `containerd`, image decompression such as `pigz`) | Any public image, e.g. `public.ecr.aws/docker/library/busybox` running `echo`, or `nginx` | Phase `Running`/`Succeeded`; no `ImagePullBackOff`, `CreateContainerError`, `CrashLoopBackOff` |
| NVIDIA stack (driver, `libnvidia-container`, `nvidia-container-toolkit`, `nvidia-k8s-device-plugin`) on an `aws-k8s-*-nvidia` AMI on a GPU instance (`g*`/`p*`) | Requests `resources.limits."nvidia.com/gpu": 1` with a toleration for `nvidia.com/gpu:NoSchedule` | Pod schedules (node advertises `nvidia.com/gpu` in `.status.allocatable`), runs, and its logs show the GPU |
| `soci-snapshotter` | Node switched to `snapshotter = "soci"`, then a large public image (e.g. `public.ecr.aws/docker/library/rabbitmq`) | Pod `Running`, and `journalctl -u soci-snapshotter-grpc` on the host shows pull/unpack activity without errors |

GPU troubleshooting: `Insufficient nvidia.com/gpu` means the device plugin isn't advertising GPUs. `failed to create shim` or an OCI hook error points at the container toolkit or `libnvidia-container`. A CUDA/driver mismatch in the logs means the image needs a newer driver than the AMI ships.

### SOCI snapshotter settings

```toml
[settings.container-runtime]
snapshotter = "soci"
[settings.container-runtime-plugins.soci-snapshotter]
pull-mode = "parallel-pull-unpack"
[settings.container-runtime-plugins.soci-snapshotter.parallel-pull-unpack]
concurrent-download-chunk-size = "8mb"
discard-unpacked-layers = true
max-concurrent-downloads = 12
max-concurrent-downloads-per-image = 5
max-concurrent-unpacks = 8
max-concurrent-unpacks-per-image = 4
```

Put these in user-data at launch, or apply them to a running node with `apiclient apply` (which reads TOML from stdin). Confirm with `apiclient get settings.container-runtime.snapshotter`. Images pulled before the switch are not re-pulled, so delete and re-create the test pod afterwards. If `apply` rejects a key, run `apiclient get settings.container-runtime-plugins` on that AMI to see the schema it actually supports.

## Cleanup and cost hygiene

- Terminate every instance you launched: `aws ec2 terminate-instances --instance-ids ...`. Delete test pods (the smoke scripts do this on exit through a trap).
- Before you finish, look for leftovers by tag: `aws ec2 describe-instances --filters Name=tag:Name,Values=bottlerocket-test Name=instance-state-name,Values=pending,running,stopped`.
- Conformance clusters are large (15 × xlarge by default). Check that kubetest2 logged its down phase. If a run was killed, `kubetest2-eksapi-janitor` (from aws-k8s-tester) or a manual CloudFormation and EKS sweep finds the leaked stacks.
- GPU instances are expensive: launch them only for the GPU test and terminate them straight after.
- Remove the admin container and any privileged debug pods once you're done (see `document/bottlerocket/host-access-and-debugging`).
- Custom AMIs and their EBS snapshots keep costing money until deregistered or deleted. Clean them up deliberately, and only for images you own.
