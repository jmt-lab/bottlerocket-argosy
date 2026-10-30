---
type: Skill
description: Smoke-test GPU support on a Bottlerocket aws-k8s-*-nvidia node by scheduling a pod that requests nvidia.com/gpu and confirming it schedules and runs — use after updating NVIDIA-stack packages (driver, libnvidia-container, nvidia-container-toolkit, nvidia-k8s-device-plugin) or validating a new NVIDIA variant AMI.
---

# NVIDIA smoke test runner

Background and GPU troubleshooting: the smoke-pod section of `document/bottlerocket/testing-on-aws`. Script: `references/scripts/run-nvidia-pod.sh`, run from this skill's directory.

## Procedure

1. Make sure there is at least one GPU node (a `g*` or `p*` instance) on the NVIDIA AMI under test, and that it advertises GPUs:
   ```bash
   kubectl get nodes -o json | jq '.items[] | {name: .metadata.name, gpu: .status.allocatable["nvidia.com/gpu"]}'
   ```
   GPU instances are expensive. Launch them just for this test and terminate them straight after.
2. Run it:
   ```bash
   references/scripts/run-nvidia-pod.sh            # flags: --image, --command (default nvidia-smi), --name, --timeout (default 180s)
   ```
   The pod requests `nvidia.com/gpu: 1` and tolerates `nvidia.com/gpu:NoSchedule`. The default image is NVIDIA's `nvcr.io/nvidia/cuda:12.4.1-base-ubuntu22.04` running `nvidia-smi`; its log should list the GPU. Any CUDA image that runs `nvidia-smi` or a small kernel works, as long as its CUDA version is supported by the AMI's driver.
3. Pass means the pod reaches `Succeeded` or `Running`, and its logs show the GPU. The script prints the logs and deletes the pod on exit.

## If it fails

- `Insufficient nvidia.com/gpu`: the device plugin isn't advertising GPUs. Check the plugin and driver on the node (`skill/ssm-executor`, e.g. `systemctl status nvidia-k8s-device-plugin`, `journalctl -u nvidia-k8s-device-plugin`).
- `failed to create shim` or an OCI hook error: suspect the container toolkit or `libnvidia-container`. Check containerd logs on the node.
- CUDA/driver mismatch in the logs: pick an image built for the AMI's driver.
