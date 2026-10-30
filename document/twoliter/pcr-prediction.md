---
type: Guide
description: How to predict TPM PCR values for a Bottlerocket image without booting it using Twoliter's pcrsys — locating or building the binary, the ami and disk subcommands, the efi-vars.json Secure Boot variables from build/sbkeys/<profile>, what each PCR measures, which PCRs Bottlerocket seals encrypted-storage keys to (7+11+14 or 4+7+9+11+14), and how to use predictions to check updates, reproducibility and key rotation.
---

# Predicting PCR values with pcrsys

`pcrsys` (Twoliter `tools/pcrsys`) computes the TPM PCR values a Bottlerocket image will produce at boot, from a disk image or an AMI. Use it to pre-register attestation policies, to check whether an update will change PCRs that encrypted storage is sealed to, and to compare builds. `skill/predict-pcr-values` wraps it in scripts.

## Getting the binary

- Twoliter embeds `pcrsys` and extracts it into `<project>/build/tools/pcrsys` on every run, so any `bottlerocket` or kit checkout that has built has one.
- Or build from a Twoliter checkout: `cargo build --release -p pcrsys` → `target/release/pcrsys`.

## Usage

```bash
pcrsys disk --image <disk.img> --efi-vars <efi-vars.json> [--platform aws|vmware|metal]   # default aws
pcrsys ami  --ami-id ami-0123456789abcdef0 [--region us-west-2] [--profile <aws-profile>]
```

- **disk** reads a raw GPT image (EFI system partition with shim/grub, boot partition with `vmlinuz`, `grub.cfg`, `bootconfig.data`). It opens the file directly, so decompress build output first: `lz4 -d bottlerocket-<variant>-<arch>.img.lz4 <out>.img`.
- **ami** reads the AMI's UEFI data (`ec2:DescribeImageAttribute`) and root snapshot (`ec2:DescribeImages`), then downloads the snapshot with coldsnap via the EBS direct APIs (`ebs:ListSnapshotBlocks`, `ebs:GetSnapshotBlock`, plus KMS decrypt for encrypted snapshots). Platform is always `aws`.
- Output is JSON keyed by PCR index with SHA-256 digests: `{"pcrs": {"7": {"sha256": ["<hex>"]}, ...}}`.

**Local build artifacts.** After `cargo make` in `bottlerocket`, the image is `build/images/<arch>-<variant>/latest/bottlerocket-<variant>-<arch>.img.lz4`. The matching `efi-vars.json` (PK, KEK, db, dbx as JSON, produced by `virt-fw-vars` from the Secure Boot certificates) is in the sbkeys profile directory; for local dev builds that is `build/sbkeys/local/efi-vars.json`, generated on the first build. Use the `efi-vars.json` of the profile that signed the image — a different profile yields a different PCR 7.

**Platform.** Firmware behaviour differs per platform and changes PCRs 0, 1, 4, 5 and 7; pass the platform you will deploy on (`aws` for EC2 Nitro, `vmware`, `metal`).

## What the PCRs measure

| PCR | Measures (pcrsys model) |
|---|---|
| 0, 1 | Platform firmware code / configuration (static per platform) |
| 2, 3, 6 | Option ROM code / config, resume events (separator only) |
| 4 | Boot manager code: shim, grub, vmlinuz authenticode hashes |
| 5 | GPT partition table |
| 7 | Secure Boot policy: PK, KEK, db, dbx, SbatLevel, MokListRT |
| 9 | Kernel command line (grub.cfg + bootconfig; includes the dm-verity root hash) |
| 11 | systemd boot phases |
| 14 | Shim MOK lists (MokList, MokListX, MokListTrusted) |
| 10, 12, 13, 15 | Zero (unused) |

PCRs 4 and 9 are skipped for images with A/B boot partitions, since the active kernel and root hash change across updates.

Bottlerocket also extends, from userspace at boot: **PCR 8** with canonicalized OS settings (`measure-settings.service`, after settings are applied and before bootstrap commands), **PCR 9** with `/proc/cmdline` (`measure-cmdline.service`, to capture the final command line after bootconfig), and **PCR 11** with boot-phase strings `sysinit → preconfigured → configured → ready → shutdown → final`. pcrsys predicts the value before runtime phase extensions; PCR 8 depends on the node's settings and is not predicted.

## Encrypted storage binding

Bottlerocket seals LUKS and fscrypt keys with `systemd-creds` to TPM2 PCRs:

- **In-place updates enabled** (default): PCRs **7 + 11 + 14** — kernel and userspace may change.
- **In-place updates disabled**: PCRs **4 + 7 + 9 + 11 + 14** — locked to a specific kernel and root filesystem.

If a bound PCR differs between the old and new image, data sealed on the old image will not unlock on the new one without re-encryption. Sealing to PCR 11 also time-limits access: local-storage and datastore keys are sealed before `sysinit` completes, so they cannot be unsealed after that phase on any boot. Full design: `docs/ENCRYPTED_STORAGE.md` in `bottlerocket-core-kit`.

## Using predictions

```bash
diff <(pcrsys ami --ami-id ami-OLD) <(pcrsys ami --ami-id ami-NEW)
```

- **Pre-update check:** if 7, 11 or 14 differ (or 4/9 when updates are disabled), encrypted storage won't auto-unlock after the update.
- **Reproducibility:** two builds of the same source should predict identical PCRs.
- **Secure Boot key rotation:** after changing the sbkeys profile, PCR 7 should change and reflect the new certificates.
- Differences in 4 or 9 are expected when the kernel, shim, grub or command line changed.

## Troubleshooting

| Problem | Fix |
|---|---|
| `pcrsys` not found | Use `build/tools/pcrsys` from a built project or build it from Twoliter. |
| AWS permission errors (ami) | Grant `ec2:DescribeImages`, `ec2:DescribeImageAttribute`, `ebs:ListSnapshotBlocks`, `ebs:GetSnapshotBlock` (and KMS decrypt if the snapshot is encrypted). |
| Disk image parse errors | Decompress `.img.lz4` first; pass the OS image, not the `-data` image. |
| `efi-vars.json` missing | Build once so `build/sbkeys/<profile>/` is generated, or point at the profile used to sign the image. |

References: [Linux TPM PCR Registry](https://uapi-group.org/specifications/specs/linux_tpm_pcr_registry/), `tools/pcrsys/README.md` in Twoliter.
