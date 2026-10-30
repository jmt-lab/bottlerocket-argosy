#!/bin/bash
# Run COMMAND on the Bottlerocket host (root, host namespaces) via SSM -> control
# container -> admin container -> sheltie. Requires the admin container to be enabled.
set -euo pipefail
INSTANCE_ID="${1:?Usage: sheltie-command.sh INSTANCE_ID REGION COMMAND}"
REGION="${2:?Usage: sheltie-command.sh INSTANCE_ID REGION COMMAND}"
COMMAND="${3:?Usage: sheltie-command.sh INSTANCE_ID REGION COMMAND}"

exec "$(dirname "$0")/control-container-command.sh" "$INSTANCE_ID" "$REGION" \
  "apiclient exec admin sheltie -- $COMMAND"
