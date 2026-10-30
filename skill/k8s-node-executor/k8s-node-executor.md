---
type: Skill
description: Run commands on a Bottlerocket Kubernetes node through a short-lived privileged pod with host PID/IPC/network namespaces and the host root mounted at /host — use for node-level debugging (apiclient, systemd, containerd, filesystem, networking) when you have kubectl but not SSM access.
---

# Kubernetes node executor

Background, the `chroot /host` pattern, Pod Security admission and security implications: `document/bottlerocket/host-access-and-debugging`. Manifest: `references/executor-pod.yaml`.

This pod is root on the node. Use it on test clusters, get the user's agreement before using it anywhere else, and always delete it afterwards.

## Procedure

1. Pick the node with `kubectl get nodes -o wide`. Then deploy the pod pinned to that node, in a namespace that allows privileged pods:
   ```bash
   sed "s/NODE_NAME/<node-name>/" references/executor-pod.yaml | kubectl apply -f -
   kubectl wait --for=condition=Ready pod/br-executor --timeout=90s
   ```
   If admission rejects it, use a namespace labelled `pod-security.kubernetes.io/enforce=privileged` (add `-n <ns>` to every command).
2. Run commands:
   ```bash
   kubectl exec br-executor -- chroot /host apiclient get os
   kubectl exec br-executor -- chroot /host apiclient get settings.kubernetes
   kubectl exec br-executor -- chroot /host systemctl status kubelet --no-pager
   kubectl exec br-executor -- chroot /host journalctl -u kubelet --no-pager -n 100
   kubectl exec br-executor -- chroot /host ctr -n k8s.io containers list
   kubectl exec br-executor -- cat /host/etc/os-release
   kubectl exec br-executor -- ip addr        # host namespaces already apply to ip/ss/ps/iptables
   ```
   Host binaries must run under `chroot /host`. Otherwise `apiclient` can't find `/run/api.sock`. Debug tools can be added to the pod itself (`dnf install -y tcpdump strace`).
3. Clean up: `kubectl delete pod br-executor --wait=false`. Confirm it's gone with `kubectl get pod br-executor`.

## Troubleshooting

`kubectl describe pod br-executor` usually shows the cause: Pod Security admission, a wrong node name, taints (the manifest tolerates everything), or an image pull failure.
