#!/bin/bash
set -euo pipefail

# Predict PCR values from a local Bottlerocket disk image.
# Usage: predict-from-disk.sh IMAGE_PATH [PLATFORM] [BOTTLEROCKET_ROOT]
#
# Accepts a raw image or the .img.lz4 from build/images/<arch>-<variant>/latest/.
# Automatically locates efi-vars.json from the build tree.
# Override with EFI_VARS_PATH env var.

IMAGE_PATH="${1:?Usage: predict-from-disk.sh IMAGE_PATH [PLATFORM] [BOTTLEROCKET_ROOT]}"
PLATFORM="${2:-aws}"
BOTTLEROCKET_ROOT="${3:-}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PCRSYS_BIN="${PCRSYS_BIN:-$("$SCRIPT_DIR/find-pcrsys.sh")}"

if [[ ! -f "$IMAGE_PATH" ]]; then
    echo "ERROR: Disk image not found: $IMAGE_PATH" >&2
    exit 1
fi

find_efi_vars() {
    # 1. Explicit override
    if [[ -n "${EFI_VARS_PATH:-}" ]]; then
        if [[ -f "$EFI_VARS_PATH" ]]; then
            echo "$EFI_VARS_PATH"
            return 0
        else
            echo "ERROR: EFI_VARS_PATH is set to '$EFI_VARS_PATH' but file does not exist." >&2
            return 1
        fi
    fi

    # 2. sbkeys profile in build tree (profile defaults to "local")
    local profile="${BUILDSYS_SBKEYS_PROFILE:-local}"
    if [[ -n "$BOTTLEROCKET_ROOT" ]]; then
        local candidate="$BOTTLEROCKET_ROOT/build/sbkeys/$profile/efi-vars.json"
        if [[ -f "$candidate" ]]; then
            echo "$candidate"
            return 0
        fi
    fi

    # 3. Try to infer repo root from image path (look for build/ ancestor)
    local dir="$IMAGE_PATH"
    while [[ "$dir" != "/" ]]; do
        dir="$(dirname "$dir")"
        if [[ "$(basename "$dir")" == "build" ]] && [[ -d "$dir/sbkeys" ]]; then
            local candidate="$dir/sbkeys/$profile/efi-vars.json"
            if [[ -f "$candidate" ]]; then
                echo "$candidate"
                return 0
            fi
        fi
    done

    # 4. Sibling of the image file
    local image_dir="$(dirname "$IMAGE_PATH")"
    if [[ -f "$image_dir/efi-vars.json" ]]; then
        echo "$image_dir/efi-vars.json"
        return 0
    fi

    return 1
}

EFI_VARS="$(find_efi_vars)" || {
    echo "ERROR: Could not locate efi-vars.json." >&2
    echo "Searched:" >&2
    echo "  - EFI_VARS_PATH env var (not set or file missing)" >&2
    echo "  - build/sbkeys/${BUILDSYS_SBKEYS_PROFILE:-local}/efi-vars.json" >&2
    echo "  - $(dirname "$IMAGE_PATH")/efi-vars.json" >&2
    echo "" >&2
    echo "Set EFI_VARS_PATH or pass BOTTLEROCKET_ROOT as third argument." >&2
    exit 1
}

# pcrsys reads a raw disk image; decompress build output (.img.lz4) to a temp file first.
RAW_IMAGE="$IMAGE_PATH"
if [[ "$IMAGE_PATH" == *.lz4 ]]; then
    command -v lz4 &>/dev/null || { echo "ERROR: lz4 is required to decompress $IMAGE_PATH" >&2; exit 1; }
    TMP_DIR="$(mktemp -d)"
    trap 'rm -rf "$TMP_DIR"' EXIT
    RAW_IMAGE="$TMP_DIR/$(basename "${IMAGE_PATH%.lz4}")"
    echo "Decompressing $IMAGE_PATH -> $RAW_IMAGE" >&2
    lz4 -dq "$IMAGE_PATH" "$RAW_IMAGE"
fi

echo "Predicting PCR values for disk image: $IMAGE_PATH" >&2
echo "Platform: $PLATFORM" >&2
echo "EFI vars: $EFI_VARS" >&2
echo "---" >&2

"$PCRSYS_BIN" disk \
    --image "$RAW_IMAGE" \
    --efi-vars "$EFI_VARS" \
    --platform "$PLATFORM"
