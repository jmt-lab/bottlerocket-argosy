---
type: Reference
description: Toolchain, build-system versions and packaged component versions for the kernel kit, taken from Twoliter.toml, Makefile, Cargo manifests and RPM specs at v9.1.0.
---

# Tech Stack

## Build toolchain

| Item | Version / value | Defined in |
|---|---|---|
| Kit release | 9.1.0 | `Twoliter.toml` `release-version` |
| Twoliter | 0.24.0 (binary, sha256-pinned per host arch) | `Makefile` `TWOLITER_VERSION`, `TWOLITER_SHA256_*` |
| Bottlerocket SDK | `bottlerocket-sdk` 0.79.0 (`public.ecr.aws/bottlerocket/bottlerocket-sdk:v0.79.0`, digest pinned) | `Twoliter.toml` `[sdk]`, `Twoliter.lock` |
| Twoliter schema | 2 | `Twoliter.toml` |
| Cargo workspaces | root (`resolver = "2"`, packages + kit, `exclude = ["sources"]`); `sources/` (`resolver = "1"`) | `Cargo.toml`, `sources/Cargo.toml` |
| Rust edition | 2021 (all crates) | each `Cargo.toml` |
| Host requirements | Linux x86_64 or aarch64, Docker, cargo-make, ~80 GB disk; distro packages listed in `BUILDING.md` and `.github/actions/setup-node/action.yml` (`build-essential openssl libssl-dev pkg-config liblz4-tool clang`) | `BUILDING.md`, CI |
| Target arches | `x86_64`, `aarch64` (`--arch`, `BUILDSYS_ARCH`) | `Makefile`, CI matrix |

## First-party Rust (`sources/` workspace)

| Crate | Purpose | Key deps (workspace-pinned) |
|---|---|---|
| `nvidia-migmanager` 0.1.0 | Applies NVIDIA MIG partitioning from `/etc/nvidia-migmanager/nvidia-migmanager.toml`; subcommands `apply-mig`, `reboot-if-required` | argh 0.1, serde 1, toml 0.8, regex 1, snafu 0.8, simplelog 0.12, log 0.4.21, base64 0.22; dev: tempfile 3 |
| `generate-readme` 0.1.0 | build.rs helper that renders `README.md` from rustdoc via `README.tpl` | cargo-readme 3, snafu 0.8 |

License policy for these crates: `sources/deny.toml` (cargo-deny; allows Apache-2.0, BSD-3-Clause, MIT, Unicode-3.0; denies multiple versions, wildcards, unknown registries/git).

## Packaged component versions (v9.1.0)

| Package | Version | Source of truth |
|---|---|---|
| kernel-6.1 | 6.1.182 (AL2023 SRPM) | `packages/kernel-6.1/kernel-6.1.spec`, `Cargo.toml` |
| kernel-6.12 | 6.12.103 | `packages/kernel-6.12/kernel-6.12.spec` |
| kernel-6.18 | 6.18.44 | `packages/kernel-6.18/kernel-6.18.spec` |
| AWS Neuron driver (in kernels) | 2.29.0 latest, 2.24.13 inf1, plus pinned 2.x.7372/7693/8072 builds | kernel specs `%neuron_ver`, `%neuron_inf1_ver` |
| kmod-*-efa | EFA installer 1.49.0 (package Version 3.0.0) | `packages/kmod-6.12-efa/kmod-6.12-efa.spec` |
| kmod-*-nvidia-r580 | Tesla 580.178.04, GRID 19.6, gdrcopy 2.6 | `packages/kmod-6.12-nvidia-r580/Cargo.toml`, spec |
| kmod-*-nvidia-r595 | Tesla 595.91.07 | `packages/kmod-6.12-nvidia-r595/Cargo.toml` |
| grub | 2.06 (AL2023 `grub2-2.06-61.amzn2023.0.18` SRPM + 48 patches) | `packages/grub/grub.spec` |
| shim | 16.1 | `packages/shim/shim.spec` |
| linux-firmware | 20251111 | `packages/linux-firmware/linux-firmware.spec` |
| microcode | Intel 20240813, AMD (linux-firmware) 20240909 | `packages/microcode/microcode.spec` |
| libkcapi | 1.4.0 (AL2023 SRPM) | `packages/libkcapi/libkcapi.spec` |
| nvlsm | 2025.06.6 | `packages/nvlsm/Cargo.toml` |
| nvidia-migmanager (RPM) | 0.1, Epoch 1 | `packages/nvidia-migmanager/nvidia-migmanager.spec` |

Versions above change with nearly every release; always re-read the spec or `Cargo.toml` rather than trusting this table.

## Other languages / configs

- Bash for everything in `tools/` and `packages/*/latest-*.sh` (linted by `make twoliter check-shell` / shellcheck).
- RPM spec macros from the SDK (`%{_cross_os}`, `%{_cross_arch}`, `%cargo_build`, `variant-platform(...)`, `image-feature(...)` capabilities).
- `.golangci.yaml` exists for Go linting, but the repo currently contains no Go code.
- Node/commitlint (`.commitlint.config.mjs`) for commit-message CI only.

## Licensing

Dual `Apache-2.0 OR MIT` for first-party code (`COPYRIGHT`, `LICENSE-*`); packaged upstreams keep their own licenses (kernel GPL-2.0, NVIDIA EULAs fetched as `external-files`).
