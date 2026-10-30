---
type: Skill
description: Validate the soci-snapshotter package on a Bottlerocket Kubernetes node — switch the node's container-runtime snapshotter to soci with parallel pull/unpack (via user-data or apiclient apply over SSM), then confirm a pod pulls through soci and runs; use after updating soci-snapshotter.
---

# SOCI snapshotter tester

Background and the full settings block: the SOCI section of `document/bottlerocket/testing-on-aws`. Scripts are in `references/scripts/` and should be run from this skill's directory.

## Procedure

1. **Enable soci on the target node.** Either put the settings in user-data when you launch with `skill/launch-bottlerocket-ec2`, or apply them to a running node over SSM:
   ```bash
   references/scripts/configure-node.sh INSTANCE_ID REGION
   ```
   This base64-encodes the TOML, pipes it into `apiclient apply` in the control container, and prints `settings.container-runtime.snapshotter`, which should be `soci`. It changes the node's settings persistently and restarts containerd, so only run it on a test node.
2. **Run a pod on that node:**
   ```bash
   references/scripts/run-soci-pod.sh --node <node-name>   # default image public.ecr.aws/docker/library/rabbitmq:4.1.0; also --image/--name/--timeout
   ```
   Pass `--node` so the pod lands on the configured node.
3. **Verify:** the pod is `Running` and its logs show RabbitMQ starting. On the node (`skill/ssm-executor` sheltie command), `journalctl -u soci-snapshotter-grpc` shows pull/unpack activity and no errors.

## If it fails

- The pod ran but soci wasn't used: the image was pulled before the switch. Confirm the setting, then delete and re-run the pod so the image is pulled fresh (or use an image the node hasn't pulled yet).
- `apiclient apply` rejected a key: the schema differs on this AMI. Check it with `apiclient get settings.container-runtime-plugins`.
