---
type: Reference
description: One-page orientation to bottlerocket-kernel-kit, the Twoliter "kit" that packages Linux kernels, bootloaders, firmware and GPU/EFA drivers for Bottlerocket OS.
---

# Bottlerocket Kernel Kit — Summary

**What it is.** A [Twoliter](https://github.com/bottlerocket-os/twoliter) *kit*: a versioned OCI image of prebuilt RPMs that downstream [Bottlerocket](https://github.com/bottlerocket-os/bottlerocket) variant builds consume. It is not a runnable application; the deliverable is the `bottlerocket-kernel-kit` image published to the `bottlerocket` vendor registry `public.ecr.aws/bottlerocket` (`Twoliter.toml`; public listing at gallery.ecr.aws/bottlerocket/bottlerocket-kernel-kit per `README.md`).

**What it contains** (one RPM package per directory under `packages/`):

| Group | Packages | Upstream source |
|---|---|---|
| Linux kernels | `kernel-6.1`, `kernel-6.12`, `kernel-6.18` | Amazon Linux 2023 kernel SRPMs + Bottlerocket patches/configs; AWS Neuron drivers bundled in |
| Out-of-tree modules | `kmod-<ver>-efa`, `kmod-<ver>-nvidia-r580`, `kmod-<ver>-nvidia-r595` (one per kernel) | AWS EFA installer; NVIDIA Tesla/GRID/open-gpu `.run` installers, fabricmanager, IMEX, gdrcopy |
| Boot chain | `grub`, `shim` | AL2023 grub2 SRPM (+ Bottlerocket GPT/gptprio patches); rhboot shim tarball |
| Firmware | `linux-firmware`, `microcode` | kernel.org linux-firmware; Intel microcode GitHub |
| Libraries / tools | `libkcapi`, `nvlsm`, `nvidia-migmanager` | AL2023 SRPM; NVIDIA subnet manager RPM; first-party Rust in `sources/` |

**Who it is for.** Bottlerocket maintainers and anyone building a custom Bottlerocket variant who needs to patch, reconfigure or update a kernel, bootloader or driver. Consumers pin the kit in their own `Twoliter.toml` (see `BUILDING.md`, section "Consuming the published kit image").

**Current state** (from `Twoliter.toml`, `CHANGELOG.md`, git tags): release `v9.1.0` (2026-09-03), SDK `bottlerocket-sdk` 0.79.0, Twoliter 0.24.0. Development happens on the `develop` branch; releases are tags `vX.Y.Z`.

**Also in the repo.** `advisories/` holds Bottlerocket Security Advisory (BRSA) TOML files grouped by kit release version. `tools/` holds shell helpers for installing Twoliter, regenerating kernel configs and validating the changelog.

**Where to go next**

- How the build works and how packages fit together: `document/kernel-kit/architecture`
- Versions and toolchain: `document/kernel-kit/tech`
- Build / test / lint / publish commands: `document/kernel-kit/development`
- Commit, changelog and package-layout rules: `document/kernel-kit/conventions`
- Jargon (kit, buildsys, gptprio, BRSA, …): `document/kernel-kit/glossary`
- Canonical long-form docs in the repo: `README.md`, `BUILDING.md`, `CONTRIBUTING.md`, `packages/kernel-6.12/README.md`
