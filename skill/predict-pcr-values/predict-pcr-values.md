---
type: Skill
description: Predict TPM PCR values for a Bottlerocket AMI or locally built disk image with Twoliter's pcrsys, without booting it — locate or build pcrsys, run the ami or disk mode (auto-finding efi-vars.json under build/sbkeys/<profile> and decompressing .img.lz4), and compare predictions to check whether an update changes the PCRs encrypted storage is sealed to, whether builds are reproducible, or whether a Secure Boot key change shows up in PCR 7.
---

# Predict PCR values

What pcrsys measures, the PCR table, the encrypted-storage bindings (7+11+14, or 4+7+9+11+14 with in-place updates disabled) and troubleshooting are in `document/twoliter/pcr-prediction`. Scripts are in `references/`.

## Input

- An AMI ID (plus optional region and AWS profile), **or** a disk image path (raw or `.img.lz4`), optional platform (`aws` default, `vmware`, `metal`) and the `bottlerocket` checkout root.
- Optionally a second AMI/image to compare against.

## Procedure

1. **Find pcrsys:** `references/find-pcrsys.sh` (honours `PCRSYS_BIN` and `TWOLITER_REPO`; searches sibling Twoliter builds, `build/tools/pcrsys` in sibling project checkouts, then `PATH`). If missing, build it: `cargo build --release -p pcrsys` in a Twoliter checkout.
2. **Predict:**
   - AMI: `references/predict-from-ami.sh AMI_ID [REGION] [PROFILE]`. Needs AWS credentials allowing `ec2:DescribeImages`, `ec2:DescribeImageAttribute`, `ebs:ListSnapshotBlocks`, `ebs:GetSnapshotBlock` (and KMS decrypt for encrypted snapshots). It downloads the root snapshot, which takes a while.
   - Local image: `references/predict-from-disk.sh build/images/<arch>-<variant>/latest/bottlerocket-<variant>-<arch>.img.lz4 [PLATFORM] [BOTTLEROCKET_ROOT]`. `efi-vars.json` is taken from `EFI_VARS_PATH`, else `<root>/build/sbkeys/${BUILDSYS_SBKEYS_PROFILE:-local}/efi-vars.json`, else a `build/` ancestor of the image, else next to the image. `.lz4` input is decompressed to a temp file.
3. **Compare** when there are two inputs:
   ```bash
   diff <(references/predict-from-ami.sh ami-OLD) <(references/predict-from-ami.sh ami-NEW)
   ```
4. **Report** the JSON (SHA-256 per PCR) and interpret differences using the document: changes in 7/11/14 (or 4/9 when updates are disabled) mean encrypted storage won't auto-unlock after the update; changes in 4/9 alone are expected when kernel, bootloader or command line changed; PCR 7 should change after a Secure Boot key rotation; identical sources should give identical predictions.
