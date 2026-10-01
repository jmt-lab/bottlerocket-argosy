---
type: Reference
description: Languages, toolchain, pinned kit/SDK/tool versions, and key Rust dependencies of the bottlerocket top-level repo, taken from the manifests.
---

# Tech stack

## Languages and runtime
| Layer | Technology | Notes |
|---|---|---|
| First-party code in this repo | Rust, edition 2021 | Only `sources/` compiles into the image. No `rust-toolchain` file or `rust-version` pin; `BUILDING.md` says Rust ≥ 1.51 for the host. |
| Build orchestration | cargo-make (`Makefile.toml`) → Twoliter | Twoliter builds inside Docker/BuildKit using the Bottlerocket SDK image. |
| Packaging | RPM spec files (`packages/*.spec`) | RPM is a build-time format only; not present in images. |
| Image contents | Linux kernel, systemd, containerd, kubelet/ECS agent, GRUB (patched), wicked or systemd-networkd, SELinux, dm-verity | All come from kits, not this repo. |
| Helper scripts | Bash (`tools/*`, `sbkeys/*`) | Linted via `cargo make check-shell` (runs in Twoliter). |
| Commit lint | Node / commitlint (`.commitlint.config.mjs`) | CI only. |
| Go | no `go.mod` anywhere in this repo | `.golangci.yaml` and the `GO_MOD_CACHE`/`GOPROXY` knobs still exist for the `check-golangci-lint` task and kit-era Go builds. |

## Pinned versions (source of truth in parentheses)
| Item | Version |
|---|---|
| Bottlerocket release (`Release.toml`, `Twoliter.toml release-version`) | 1.64.0 |
| Twoliter (`Makefile.toml TWOLITER_VERSION`) | v0.24.0 |
| bottlerocket-sdk (`Twoliter.toml`) | 0.78.0 |
| bottlerocket-core-kit (`Twoliter.toml`) | 15.1.0 |
| bottlerocket-kernel-kit (`Twoliter.toml`) | 9.0.2 |
| tuftool for publishing (`Makefile.toml PUBLISH_TUFTOOL_VERSION`) | 0.10.0 |
| bottlerocket-settings-sdk crates (`sources/Cargo.toml`, git tag) | `bottlerocket-settings-models-v0.25.0` → settings-models 0.25.0, modeled-types 0.17.0, defaults-helper 0.1.1, settings-plugin 0.1.0, settings-extension-oci-defaults 0.1.0 |
| Kit registry (`Twoliter.toml`) | `public.ecr.aws/bottlerocket` |
| Twoliter schema (`Twoliter.toml`) | 2 |

Kits and Twoliter are bumped frequently (see recent commits like `twoliter: Bump kernel-kit to 9.0.2`); re-read `Twoliter.toml` and `Makefile.toml` rather than trusting this table.

## Kit packages referenced by current variants (from `variants/*/Cargo.toml`)
Kernels `kernel-6.1` (metal-dev) and `kernel-6.18` (others); `containerd-2.2`; `systemd-257`; `kubelet-1.31`…`kubelet-1.36`; Docker in dev variants (`docker-cli-29`/`docker-engine-29` in aws-dev and vmware-dev, unversioned `docker-cli`/`docker-engine` in metal-dev, plus `docker-init`); `release` in 37 variants vs `release-swap` in the 12 k8s-1.35/1.36 variants (aws and vmware); `nftables`, `whippet`, `cni`, `cni-plugins`, `aws-iam-authenticator`, `soci-snapshotter`, `aws-signer-notation-plugin`, `digestion-image-verifier`, `notation-image-verifier`, `thar-be-image-verifiers`, `open-vm-tools`, `linux-firmware`.

## Rust workspaces
| Workspace | Members | Purpose |
|---|---|---|
| root `Cargo.toml` (resolver 1, `profile.dev opt-level='z'`, `debug=false`) | 49 `variants/*` + `packages/settings-defaults`, `packages/settings-plugins` | Build-driver crates only; no real code. |
| `sources/Cargo.toml` (resolver 1, `profile.release debug=true`) | datastore, migration-helpers, bottlerocket-release, constants, generate-readme, models, retry-read, 27 settings-defaults, 25 settings-migrations, 10 settings-plugins | Real code compiled into RPMs. |

### Key `sources/` workspace dependencies (from `[workspace.dependencies]`)
| Crate | Version | Used for |
|---|---|---|
| serde / serde_json / serde_plain / toml | 1 / 1 / 1 / 0.8 | Models, datastore, defaults |
| snafu | 0.8 | Error handling everywhere |
| abi_stable | 0.11.3 | Plugin ABI for settings plugins |
| handlebars | 4 | Migration helpers (template-aware) |
| tokio | ~1.43 | migration-helpers runtime |
| semver | 1 | `bottlerocket-release` version parsing |
| envy | 0.4 | os-release parsing |
| cargo-readme | 3 | `generate-readme` build.rs READMEs |
| hyper 0.14, reqwest 0.12, rustls 0.23, aws-lc-rs 1, tokio-tungstenite 0.20, argh, pest, nix, … | — | Declared at workspace level as shared version pins; not all are used by the crates that remain in this repo |

`sources/deny.toml`: allowed licenses Apache-2.0, BSD-3-Clause, ISC, MIT, Unlicense, Zlib, MPL-2.0, Unicode-3.0; `multiple-versions = "deny"` (skips for `syn 1`, `thiserror 1`, `windows-sys` tree); bans `structopt` and `clap` (except via cargo-readme); only git source allowed is bottlerocket-settings-sdk.

## Host build prerequisites
See `document/development`.

## CI runners
GitHub Actions on the `bottlerocket` runner group (`bottlerocket_ubuntu-latest_32-core` for builds, 8-core for cache); Docker with BuildKit; see `document/development`.
