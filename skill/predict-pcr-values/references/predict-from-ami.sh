#!/bin/bash
set -euo pipefail

# Predict PCR values from an AWS AMI.
# Usage: predict-from-ami.sh AMI_ID [REGION] [PROFILE]

AMI_ID="${1:?Usage: predict-from-ami.sh AMI_ID [REGION] [PROFILE]}"
REGION="${2:-}"
PROFILE="${3:-}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PCRSYS_BIN="${PCRSYS_BIN:-$("$SCRIPT_DIR/find-pcrsys.sh")}"

ARGS=("ami" "--ami-id" "$AMI_ID")

if [[ -n "$REGION" ]]; then
    ARGS+=("--region" "$REGION")
fi

if [[ -n "$PROFILE" ]]; then
    ARGS+=("--profile" "$PROFILE")
fi

echo "Predicting PCR values for AMI: $AMI_ID" >&2
echo "---" >&2

"$PCRSYS_BIN" "${ARGS[@]}"
