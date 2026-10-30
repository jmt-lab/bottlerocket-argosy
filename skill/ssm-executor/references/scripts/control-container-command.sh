#!/bin/bash
# Run COMMAND in the control container of a Bottlerocket instance via SSM Run Command
# and print its stdout (and stderr, if any). Exits non-zero if the command failed.
set -euo pipefail
INSTANCE_ID="${1:?Usage: control-container-command.sh INSTANCE_ID REGION COMMAND}"
REGION="${2:?Usage: control-container-command.sh INSTANCE_ID REGION COMMAND}"
COMMAND="${3:?Usage: control-container-command.sh INSTANCE_ID REGION COMMAND}"

# Build the parameters with jq so quotes in COMMAND survive.
PARAMS=$(jq -cn --arg c "$COMMAND" '{commands: [$c]}')

CMD_ID=$(aws ssm send-command \
  --instance-ids "$INSTANCE_ID" \
  --document-name "AWS-RunShellScript" \
  --parameters "$PARAMS" \
  --region "$REGION" \
  --query 'Command.CommandId' \
  --output text)

# The waiter errors if the command itself failed; still fetch the output in that case.
aws ssm wait command-executed --command-id "$CMD_ID" --instance-id "$INSTANCE_ID" --region "$REGION" 2>/dev/null || true

STATUS=$(aws ssm get-command-invocation --command-id "$CMD_ID" --instance-id "$INSTANCE_ID" \
  --region "$REGION" --query 'Status' --output text)
aws ssm get-command-invocation --command-id "$CMD_ID" --instance-id "$INSTANCE_ID" \
  --region "$REGION" --query 'StandardOutputContent' --output text
ERR=$(aws ssm get-command-invocation --command-id "$CMD_ID" --instance-id "$INSTANCE_ID" \
  --region "$REGION" --query 'StandardErrorContent' --output text)
[[ -n "$ERR" && "$ERR" != "None" ]] && echo "$ERR" >&2
[[ "$STATUS" == "Success" ]] || { echo "SSM command $CMD_ID status: $STATUS" >&2; exit 1; }
