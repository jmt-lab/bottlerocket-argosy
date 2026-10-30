---
type: Skill
description: Run upstream Kubernetes [Conformance] tests against a Bottlerocket aws-k8s AMI using kubetest2 eksapi — create a throwaway EKS cluster with unmanaged nodes on the AMI, run the ginkgo suite, and tear everything down; use to validate a new K8s AMI or Kubernetes package update, once per Kubernetes minor version.
---

# Conformance runner

Background (tooling, flags, cost): the conformance section of `document/bottlerocket/testing-on-aws`. Script: `references/scripts/run-conformance.sh`, run from this skill's directory.

## Inputs

| Flag | Default | Notes |
|---|---|---|
| `--ami` | required | AMI under test |
| `--arch` | required | `x86_64` uses `m5.xlarge`, `aarch64` uses `m6g.xlarge` |
| `--kubernetes-version` | `1.35` | Must match the AMI's variant. It also selects the `latest-<ver>.txt` test-package marker. |
| `--region` | `us-west-2` | |
| `--nodes` | `15` | Number of unmanaged nodes; also sets ginkgo parallelism |
| `--install` | off | `go install`s kubetest2 (+ ginkgo tester) and the aws-k8s-tester `kubetest2-eksapi` deployer |

## Procedure

1. Confirm the account with `aws sts get-caller-identity`. The run creates an EKS cluster, IAM roles, CloudFormation stacks and 15 xlarge instances, so it costs real money. Make sure the user expects that.
2. Run it:
   ```bash
   references/scripts/run-conformance.sh --ami ami-0123456789abcdef0 --arch x86_64 --kubernetes-version 1.35 --install
   ```
   Output is tee'd to `$RESULTS_DIR` (default `/tmp/pkg-test-results`). Expect the run to take tens of minutes, so run it in the background and monitor the log.
3. Pass means ginkgo prints `SUCCESS!` and the script exits `0`. Also check the log for kubetest2's down phase, which confirms teardown.

## If it fails

- `kubetest2: command not found` or `unknown deployer eksapi`: run with `--install`, and check that `$(go env GOPATH)/bin` is on `PATH`.
- Nodes never join: bad AMI or user-data. Inspect a node with `skill/ssm-executor` before the down phase cleans it up.
- Capacity errors: retry, or try another region.
- The run was interrupted: look for leaked EKS clusters and CloudFormation stacks and clean them up (see the cleanup section of the doc).
