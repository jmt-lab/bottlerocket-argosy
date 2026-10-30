#!/bin/bash
# Switch a running Bottlerocket node to the soci snapshotter (parallel pull/unpack)
# by piping TOML into `apiclient apply` in the control container over SSM.
set -euo pipefail
INSTANCE_ID="${1:?Usage: configure-node.sh INSTANCE_ID REGION}"
REGION="${2:?Usage: configure-node.sh INSTANCE_ID REGION}"

RESULTS_DIR="${RESULTS_DIR:-/tmp/pkg-test-results}"; mkdir -p "$RESULTS_DIR"
LOG_FILE="$RESULTS_DIR/soci-configure-${INSTANCE_ID}-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee -a "$LOG_FILE") 2>&1
echo "# logging to $LOG_FILE"

read -r -d '' TOML <<'TOML' || true
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
TOML

# base64 the TOML so it survives SSM/JSON quoting; decode, apply, and read back on the node.
B64=$(printf '%s\n' "$TOML" | base64 | tr -d '\n')
NODE_CMD="echo ${B64} | base64 -d | apiclient apply && apiclient get settings.container-runtime.snapshotter"
PARAMS=$(jq -cn --arg c "$NODE_CMD" '{commands: [$c]}')

CMD_ID=$(aws ssm send-command \
  --instance-ids "$INSTANCE_ID" \
  --document-name "AWS-RunShellScript" \
  --parameters "$PARAMS" \
  --region "$REGION" \
  --query 'Command.CommandId' --output text)
aws ssm wait command-executed --command-id "$CMD_ID" --instance-id "$INSTANCE_ID" --region "$REGION" 2>/dev/null || true
aws ssm get-command-invocation \
  --command-id "$CMD_ID" --instance-id "$INSTANCE_ID" --region "$REGION" \
  --query '[Status,StandardOutputContent,StandardErrorContent]' --output text
echo "Expect status Success and snapshotter \"soci\" above."
