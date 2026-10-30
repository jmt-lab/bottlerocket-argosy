#!/bin/bash
set -euo pipefail

# Find the pcrsys binary.
# Priority: PCRSYS_BIN env > locally built twoliter > binary extracted by twoliter into build/tools > PATH

if [[ -n "${PCRSYS_BIN:-}" ]]; then
    if [[ -x "$PCRSYS_BIN" ]]; then
        echo "$PCRSYS_BIN"
        exit 0
    else
        echo "ERROR: PCRSYS_BIN is set to '$PCRSYS_BIN' but is not executable or does not exist." >&2
        exit 1
    fi
fi

# 1. Locally built twoliter (cargo build --release -p pcrsys)
TWOLITER_PATHS=()
if [[ -n "${TWOLITER_REPO:-}" ]]; then
    TWOLITER_PATHS+=("${TWOLITER_REPO}/target/release/pcrsys")
fi
TWOLITER_PATHS+=(
    "../twoliter/target/release/pcrsys"
    "../../twoliter/target/release/pcrsys"
    "../../../twoliter/target/release/pcrsys"
)

for path in "${TWOLITER_PATHS[@]}"; do
    if [[ -x "$path" ]]; then
        echo "$(cd "$(dirname "$path")" && pwd)/$(basename "$path")"
        exit 0
    fi
done

# 2. Binary extracted by twoliter into <project>/build/tools/ (or tools/twoliter/)
KIT_PATHS=(
    "./build/tools/pcrsys"
    "./tools/twoliter/pcrsys"
    "../build/tools/pcrsys"
    "../tools/twoliter/pcrsys"
    "../../build/tools/pcrsys"
    "../../tools/twoliter/pcrsys"
)

for repo in bottlerocket-kernel-kit bottlerocket-core-kit bottlerocket; do
    KIT_PATHS+=(
        "../${repo}/build/tools/pcrsys"
        "../../${repo}/build/tools/pcrsys"
        "../${repo}/tools/twoliter/pcrsys"
        "../../${repo}/tools/twoliter/pcrsys"
    )
done

for path in "${KIT_PATHS[@]}"; do
    if [[ -x "$path" ]]; then
        echo "$(cd "$(dirname "$path")" && pwd)/$(basename "$path")"
        exit 0
    fi
done

# 3. PATH
if command -v pcrsys &>/dev/null; then
    command -v pcrsys
    exit 0
fi

echo "ERROR: pcrsys binary not found." >&2
echo "Build from twoliter source: cd <twoliter-repo> && cargo build --release -p pcrsys" >&2
echo "Or set PCRSYS_BIN or TWOLITER_REPO to point to the right location." >&2
exit 1
