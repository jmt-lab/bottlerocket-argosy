---
type: Reference
description: Components of the kernel kit build (Makefile → Twoliter → Cargo → buildsys → rpmbuild → kit image), where each lives, package dependency graph, and how a `make` run flows.
---

# Architecture

The repo is a build description, not a program. Cargo is used only as a dependency-ordered task runner: every "crate" is an empty library whose `build.rs` shells out to `buildsys` (a tool shipped inside the Bottlerocket SDK container via Twoliter).

## Components

| Component | Location | Responsibility | Talks to |
|---|---|---|---|
| Make front-end | `Makefile` | Installs a pinned Twoliter and wraps `twoliter fetch/build/publish/make`; also `make full-config` | `tools/install-twoliter.sh`, `tools/twoliter/twoliter` (gitignored install dir) |
| Twoliter project | `Twoliter.toml`, `Twoliter.lock` | Declares kit `release-version`, project vendor/registry, and the SDK image (name, version, digest) | Pulls `public.ecr.aws/bottlerocket/bottlerocket-sdk` |
| Package workspace | `Cargo.toml` (root), `packages/*/Cargo.toml`, `packages/build.rs`, `packages/packages.rs` | One crate per RPM. `build.rs` runs `buildsys build-package`; `packages.rs` is the shared empty `lib.rs`. Metadata under `[package.metadata.build-package]` lists `external-files` (url + sha512, optional `force-upstream`), `package-name`, `releases-url`, or `source-groups` for first-party code | `buildsys` inside the SDK |
| RPM specs + payload | `packages/<name>/<name>.spec` plus patches, configs, systemd units, GPG keys | Define the RPM(s) each package produces and their `Requires`/`Provides`/`Conflicts` against variant features | rpmbuild inside the SDK |
| Kit crate | `kits/bottlerocket-kernel-kit/Cargo.toml`, `kits/build.rs`, `kits/kit.rs` | `build-dependencies` on every package; `build.rs` runs `buildsys build-kit` to assemble the kit OCI image | All packages |
| First-party sources | `sources/Cargo.toml` (separate workspace, excluded from root), `sources/nvidia-migmanager`, `sources/generate-readme`, `sources/deny.toml` | Rust code compiled by `packages/nvidia-migmanager/nvidia-migmanager.spec` via `%cargo_build`. `sources/README.md` notes the dir also exists because Twoliter expects it for buildkit mounts | `nvidia-migmanager` package |
| Helper tools | `tools/*.sh`, `tools/collect-*`, `tools/diff-kernel-config` | Twoliter install, SDK docker wrapper, kernel config regeneration/diffing, changelog validation | Makefile, CI, maintainers |
| Advisories | `advisories/<kit-version>/BRSA-*.toml`, `advisories/staging/` | Security advisory metadata per kit release (id, CVE, severity, per-package patched version) | Bottlerocket update/advisory tooling (out of repo) |
| CI | `.github/workflows/*.yml`, `.github/actions/setup-node/action.yml` | PR build matrix, cache warming, commit lint, changelog validation | GitHub Actions self-hosted 32-core runners |

## Package dependency graph

From `Cargo.lock` / `[build-dependencies]`:

```
bottlerocket-kernel-kit
├── kernel-6.1   ─┐
├── kernel-6.12  ─┼── microcode
├── kernel-6.18  ─┘
├── kmod-6.<v>-efa          → kernel-6.<v>
├── kmod-6.<v>-nvidia-r580  → kernel-6.<v>
├── kmod-6.<v>-nvidia-r595  → kernel-6.<v>
├── grub, shim, linux-firmware, libkcapi, nvlsm, nvidia-migmanager (leaf)
```

Runtime RPM relationships live in the specs, not Cargo. Examples: `kernel-6.12.spec` `Requires: %{_cross_os}kmod-6.12-efa`; NVIDIA kmod specs `Requires: %{_cross_os}nvidia-migmanager`; `shim.spec` provides `shim(shim-efi)` via mutually exclusive `grub` and `systemd-boot` subpackages selected by `image-feature(uki-image)`; `grub.spec` `Provides: bootloader(efi)`.

## Kernel package anatomy (`packages/kernel-6.12/` is representative)

| File(s) | Role |
|---|---|
| `Cargo.toml` `external-files` | AL2023 `kernel6.12-*.src.rpm` (`force-upstream = true`) plus Neuron `aws-neuronx-dkms-*.noarch.rpm` files |
| `kernel-6.12.spec` | Verifies SRPM signature with `gpgkey-*.asc`, extracts tarball + upstream patches, applies `1001-*.patch`…, merges configs, builds; subpackages `devel`, `modules`, `headers`, `fips`, `bootconfig-aws`, `bootconfig-vmware`, `mkfs-xfs-conf`, `modules-neuron` (x86_64) |
| `config-bottlerocket`, `config-bottlerocket-<arch>` | Bottlerocket kconfig fragments merged onto the AL2023 base (order documented in `packages/kernel-6.12/README.md`) |
| `config-full-bottlerocket-<arch>` | Generated full config used for validation; regenerate with `make full-config`. `kernel-6.18` uses `-on-<hostarch>` variants |
| `fipsmodules-<arch>`, `check-fips-modules.drop-in.conf.in` | FIPS module list and check |
| `latest-*-url.sh` | Print newest upstream SRPM / Neuron RPM URLs for bumps |

Differences: `kernel-6.1` still supports bare metal (`bootconfig-metal`, `modules-metal`, `devel-squashed`, `archive` subpackages); `kernel-6.12` and `kernel-6.18` `Conflicts: variant-platform(metal)` and require erofs root. Patch numbering: `1001+` Bottlerocket kernel patches, `2001+` Neuron driver patches (see `kernel-6.18`).

## Flow of `make ARCH=<arch>`

1. `prep` — `tools/install-twoliter.sh` downloads the Twoliter release pinned by `TWOLITER_VERSION`/`TWOLITER_SHA256_*` in `Makefile` into `tools/twoliter/` (or builds from source with nightly cargo if no binary matches).
2. `fetch` — `twoliter fetch --arch` pulls the SDK image and any external kits recorded in `Twoliter.lock` (this kit has none: `kit = []`).
3. `build` — `twoliter build kit bottlerocket-kernel-kit --arch` runs `cargo build` on the kit crate inside the SDK container. Cargo orders crates by `build-dependencies`; each `build.rs` calls `buildsys build-package`, which downloads `external-files`, checks sha512, and runs `rpmbuild` with the package spec. RPMs land in `build/rpms/<package>/`.
4. The kit crate's `build.rs` calls `buildsys build-kit`, producing the kit image under `build/`.
5. `make publish VENDOR=<vendor>` — `twoliter publish kit` pushes it to the registry defined for that vendor in `Infra.toml` (gitignored, user-created).

`make twoliter <task>` forwards to `twoliter make --cargo-home .cargo --arch <arch> <task>`, exposing the SDK's embedded `Makefile.toml` tasks (`check-licenses`, `unit-tests`, `check-fmt`, `check-clippy`, `check-shell`, `fetch`, `build-package`, …) used by CI and `tools/diff-kernel-config`.

## Kernel-config regeneration path

`make full-config` → `tools/docker-run.sh` (resolves the SDK image from `Twoliter.lock`, or from `Twoliter.override` via `twoliter update`) → runs `tools/latest-kernel-full-config.sh` inside the SDK with the repo mounted at `/bottlerocket-kernel-kit`. That script fetches the SRPMs named in each kernel `Cargo.toml`, applies upstream + Bottlerocket patches, runs `scripts/kconfig/merge_config.sh` per arch, writes `config-full-bottlerocket-*`, and fails if any `CONFIG_` line from the fragments is missing from the result.
