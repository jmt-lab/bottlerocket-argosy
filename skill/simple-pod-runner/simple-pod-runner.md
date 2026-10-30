---
type: Skill
description: Smoke-test the container runtime path on a Bottlerocket Kubernetes node by scheduling one pod from a public image and confirming it pulls, starts, and runs — use after updating runtime-path packages such as runc, containerd, or pigz, or as a quick "can this node run a container at all?" check.
---

# Simple pod runner

This runs one pod, which exercises scheduling → image pull → layer decompression → containerd/runc start. Background: the smoke-pod table in `document/bottlerocket/testing-on-aws`. Script: `references/scripts/run-pod.sh`, run from this skill's directory.

## Procedure

1. Make sure `kubectl` points at a cluster whose nodes run the AMI under test (`kubectl get nodes -o wide`).
2. Run it:
   ```bash
   references/scripts/run-pod.sh                                    # nginx from public ECR
   references/scripts/run-pod.sh --image public.ecr.aws/docker/library/busybox:latest --name busybox-test
   ```
   Flags: `--image` (default `public.ecr.aws/docker/library/nginx:latest`), `--name` (default `simple-pod`), `--timeout` in seconds (default `120`). Output is tee'd to `$RESULTS_DIR` (default `/tmp/pkg-test-results`).
3. The pod passes when its phase is `Running` (server images) or `Succeeded` (batch images such as busybox, which exits immediately). The script fails fast on `Failed`, `ErrImagePull`/`ImagePullBackOff`, `CreateContainerError` or `CrashLoopBackOff`, and prints `kubectl describe pod`. It always deletes the pod on exit.

## If it fails

- `ImagePullBackOff`: the node has no network path to `public.ecr.aws`, or the image name is wrong.
- `CreateContainerError` or runc errors (most likely right after a runc update): check `kubectl describe pod`, then `journalctl -u containerd` on the node through `skill/ssm-executor` or `skill/k8s-node-executor`.
- Stuck `Pending`: there's no schedulable node on the AMI. Check node readiness and taints.
