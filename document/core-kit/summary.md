---
type: Reference
description: One-page orientation to bottlerocket-core-kit, the Twoliter "kit" of RPM packages and first-party Rust/Go daemons shared by all Bottlerocket OS variants.
---

# Bottlerocket Core Kit

**What it is.** The core kit for [Bottlerocket](https://github.com/bottlerocket-os/bottlerocket), a Linux-based container host OS from AWS. A *kit* is a versioned bundle of pre-built RPM packages published as a container image (`public.ecr.aws/bottlerocket/bottlerocket-core-kit`) that downstream *variant* builds consume. This repo defines every package in that kit and holds the source for Bottlerocket's first-party userspace.

**What it contains** (see `document/core-kit/architecture` for detail):

| Area | Path | Content |
|---|---|---|
| Package definitions | `packages/<name>/` | ~130 RPM specs + `Cargo.toml` manifests: shared libraries (glibc, libz…), daemons (systemd, dbus-broker, chrony), container runtimes (containerd, docker, runc), orchestrator agents (kubernetes 1.31–1.36, ecs-agent), GPU tooling, SELinux policy, and the first-party `os` / `release` packages |
| First-party source | `sources/` | Rust workspace (~60 crates) for the settings API system, update client, network config, storage encryption, logging, etc., plus two Go modules (`host-ctr`, `ecs-gpu-init`) |
| Kit manifest | `kits/bottlerocket-core-kit/Cargo.toml` | Lists every package the kit image bundles |
| Advisories | `advisories/<version>/BRSA-*.toml` | Security/end-of-life advisories per kit release |

**Who it is for.** Bottlerocket maintainers and anyone building a custom Bottlerocket variant or out-of-tree kit. It is not a standalone product: nothing here boots on its own, and the repo is not self-hosting (every package is cross-compiled inside the Bottlerocket SDK container).

**Key facts**

| Fact | Value | Source |
|---|---|---|
| Current kit version | 16.0.0 | `Twoliter.toml` `release-version`; git tags `vX.Y.Z` |
| Build tool | Twoliter 0.23.0 (downloaded by `make prep`) | `Makefile` |
| SDK image | `bottlerocket-sdk` v0.78.0 | `Twoliter.toml`, `Twoliter.lock` |
| Target arches | x86_64, aarch64 | `Makefile` `ARCH`, CI matrix |
| Main branch | `develop` | `CONTRIBUTING.md` |
| License | Apache-2.0 OR MIT (dual) | `COPYRIGHT`, PR template |

**Canonical long-form docs in the repo**

- `README.md`, `BUILDING.md` — build & publish overview (distilled in `document/core-kit/development`)
- `packages/README.md` — why RPM + containers + cross-compilation, and how to add a package
- `sources/api/README.md` — the settings API system, in boot order
- `sources/updater/README.md` — TUF-based update system (updog, signpost, waves)
- `docs/ENCRYPTED_STORAGE.md` — LUKS2/fscrypt/TPM2 encrypted storage design (implemented by `sources/rottweiler`)
- `GLOSSARY.md` — Bottlerocket component names (bork, corndog, sundog, thar-be-settings…)
- `CHANGELOG.md` — per-release notes, validated by CI
