---
type: Skill
description: Decide how to test a Bottlerocket third-party package after updating it and drive the right test — classify each package into a test Type (0 none, 1 pod runs, 2 conformance, 4 SOCI, 5 image verifier, 6 host one-liner, plus GPU/EKS cases) with classify-package.sh, confirm the node boots and joins, run the matching runner skill, and log all output to one results directory. Use right after update-package has built an image with the new RPM.
---

# Test a third-party package

The matrix (package → Type → test → runner skill), test-node instance types, the Type 5 procedure and the full Type 6 command table with execution gotchas are in `document/core-kit/package-test-matrix`. Read it first.

## Input

- Updated package name(s), as given to `skill/update-package` (e.g. `runc`, `kubernetes-1.35`, `keyutils`).
- AMI(s) built with the updated package, the arch (`x86_64`/`aarch64`), and the region.

## Procedure

1. **Classify:**
   ```bash
   references/classify-package.sh runc kubernetes-1.35 keyutils
   ```
   Each line gives the Type and the runner/command. `UNKNOWN` means classify manually (default: baseline plus the most relevant smoke test). `Out of scope` (ECS-tier packages) is not covered here; report it as untested.
2. **Set up logging** so the whole run is reviewable in one place:
   ```bash
   export RESULTS_DIR=/tmp/pkg-test-results/<pkg>-$(date +%Y%m%d)   # default /tmp/pkg-test-results
   ```
   Runner skills write `$RESULTS_DIR/<test>-<timestamp>.log`. Wrap ad-hoc commands with `references/log-cmd.sh TAG CMD [ARGS...]`, which tees output to the same directory.
3. **Baseline:** boot the AMI (`launch-bottlerocket-ec2`); for Kubernetes variants confirm nodes join (`eks-smoke-test`). Use the test-node instance types from the document for Type 1/4/6.
4. **Run the Type-specific test** with its runner skill:
   - Type 1 → `simple-pod-runner` (containerd on the matching Kubernetes stream).
   - Type 2 → `conformance-runner`, once per updated Kubernetes minor.
   - Type 4 → `soci-snapshotter-tester`.
   - GPU → `nvidia-smoke-test-runner` on a GPU node.
   - Type 5/6 → `ssm-executor`. Enable the admin host container first. Then run the commands from the document through its sheltie-command helper, wrapped in `log-cmd.sh`, e.g.
     `references/log-cmd.sh keyutils ../ssm-executor/references/scripts/sheltie-command.sh INSTANCE_ID REGION "keyctl --version"`.
     Run destructive commands (kdump crash, cryptsetup, ephemeral-storage, `semodule -i`) only on a throwaway node, and only after asking the user.
5. **Review** `ls -t "$RESULTS_DIR"` and summarise per package: Type, test, pass/fail, log path.
6. **Clean up** instances and clusters you launched (the runner skills document their teardown).

## Validation

- [ ] Every updated package was classified (none left `UNKNOWN` without a manual decision).
- [ ] Node boots and, for Kubernetes variants, joins.
- [ ] The Type-specific test passed for each package, with a log in `$RESULTS_DIR`.
