---
type: Reference
description: One-page orientation — what Twoliter is, who uses it, and the shape of the repo.
---

# Twoliter — project summary

**Twoliter** is the command-line build tool for creating custom [Bottlerocket](https://github.com/bottlerocket-os/bottlerocket) OS variants *out of tree*: a maintainer keeps their own repository (a "Twoliter project" with `Twoliter.toml`), pulls prebuilt package collections ("kits") and the Bottlerocket SDK as OCI images, builds their own packages/kits/variants, and publishes the results (TUF repos, AMIs, SSM params, OVAs, kit images). The Bottlerocket monorepo itself is built through Twoliter (`twoliter make`).

| Fact | Value | Source |
|---|---|---|
| Repo | `bottlerocket-os/twoliter` (this checkout tracks branch `develop`; PRs come from the `jmt-lab` fork) | `twoliter/Cargo.toml`, git log |
| Current version | `0.24.1-rc2` (released 2026-09-03) | `twoliter/Cargo.toml`, `CHANGELOG.md` |
| Language | Rust (nightly, pinned) + Bash helper scripts embedded in the binary | see `document/twoliter/tech` |
| Distribution | Static musl binaries for `x86_64`/`aarch64` on GitHub Releases via a `cargo-dist` fork; **not** on crates.io | `README.md` "Releasing", `.github/workflows/release.yml` |
| License | MIT OR Apache-2.0 | `twoliter/Cargo.toml`, `LICENSE-*` |
| Design doc | `docs/design/README.md` (long-form rationale; some sections describe plans that were never built — `twoliter new`, docker-socket-in-container — and are marked as such) | |
| Changelog | `CHANGELOG.md` (Keep-a-Changelog format; a PR that bumps the version also updates it) | |

## What the binary does

`twoliter` is a single static binary that **embeds** everything a build needs except Docker and a Rust toolchain: the helper binaries (`buildsys`, `pubsys`, `pubsys-setup`, `pipesys`, `pcrsys`, `ukisys`, `unplug`, `eif-builder`, `advisory-checker`, `tuftool`, `krane`) and the build scripts (`Makefile.toml`, `build.Dockerfile`, `rpm2img`, `img2img`, …). On every run it extracts them into `<project>/build/tools/` and drives the build with `cargo make` against that `Makefile.toml`. See `document/twoliter/architecture` for the flow.

User-facing command surface (`twoliter/src/cmd/mod.rs`):

| Command | Purpose |
|---|---|
| `twoliter update` | Resolve `Twoliter.toml` deps against registries and write `Twoliter.lock` |
| `twoliter fetch --arch A` | Verify lock and extract external kits into `build/external-kits/` |
| `twoliter build kit <name>` / `build variant <name>` / `build clean` | Build a local kit / a variant image / clean |
| `twoliter make --cargo-home P --arch A <task> [args…]` | Thin passthrough to any `Makefile.toml` task (`repo`, `ami`, `ssm`, `repack-variant`, …); passes `BUILDSYS_*`/`PUBLISH_*`/`REPO_*`/`AWS_*` env through |
| `twoliter publish kit <kit> <vendor> [repo]` | Push a built kit image to a vendor registry |
| `twoliter debug check-tools [--install-dir D]` | Extract the embedded tools and leave them for inspection |

Global flags: `--log-level`, `-q/--quiet`; `RUST_LOG` is honored.

## Repo map

| Path | What |
|---|---|
| `twoliter/` | The CLI crate (`src/cmd`, `src/project`, `src/tools.rs`, `src/cargo_make.rs`) |
| `twoliter/embedded/` | Bash scripts, `Makefile.toml`, `build.Dockerfile`, wave policies — tarred into the binary |
| `twoliter/src/tool-crates/*` | Shim crates that embed each helper binary (via cargo `bindeps`) |
| `tools/*` | The helper binaries and shared libraries (21 crates + scripts) — see `document/twoliter/architecture` |
| `tests/integration-tests/`, `tests/projects/*` | Integration test crate and fixture Twoliter projects — see `document/twoliter/development` |
| `docs/design/` | Design doc, custom-variant notes, PlantUML build-sequence diagram |

## Who works on it

Bottlerocket maintainers and out-of-tree variant maintainers. The README's "For Maintainers" section covers testing a local Twoliter build against the Bottlerocket repo (`TWOLITER_REPO`, `TWOLITER_VERSION`, `TWOLITER_ALLOW_SOURCE_INSTALL`, `TWOLITER_ALLOW_BINARY_INSTALL`, `TWOLITER_SKIP_VERSION_CHECK` env vars for Bottlerocket's `cargo make`) and the rc → final release dance.
