---
type: Guide
description: How to build, test, lint, publish and maintain the kernel kit — the actual make/twoliter commands from the Makefile, CI workflows and BUILDING.md.
---

# Development

Long-form: `BUILDING.md` (host setup, publishing, consuming), `CONTRIBUTING.md` (PR process). Versions referenced here are owned by `document/kernel-kit/tech`.

## Prerequisites

- Linux host, x86_64 or aarch64, Docker running, ~80 GB free disk (first build takes 20 min on a fast machine to hours on a small one; later builds are cached).
- Distro packages: Ubuntu `apt install build-essential openssl libssl-dev pkg-config liblz4-tool` (CI adds `clang`); Fedora equivalents in `BUILDING.md`.
- Rust via rustup plus `cargo install cargo-make`. Twoliter itself is installed by `make prep`, not by you.
- For `tools/collect-kernel-config`, `tools/diff-kernel-config`: `rpm2cpio`, `cpio`, `rpm`.

## Everyday commands

| Task | Command | Notes |
|---|---|---|
| Install pinned Twoliter | `make prep` | Into `tools/twoliter/` (gitignored). Falls back to `cargo +nightly install` from source if no matching binary |
| Fetch SDK / external kits | `make fetch` (`ARCH=`) | Runs `twoliter fetch --arch` |
| Build the kit for host arch | `make` or `make build` | = `twoliter build kit bottlerocket-kernel-kit --arch $(uname -m)` |
| Build for another arch | `make ARCH=aarch64` / `make ARCH=x86_64` | Cross-builds inside the SDK |
| Build a single package | `PACKAGE=kernel-6_12 BUILDSYS_ARCH=x86_64 make twoliter build-package` | Crate names use `_` (see `tools/diff-kernel-config`) |
| Refresh `Twoliter.lock` | `make update` | Required after changing `[sdk]` or kit deps in `Twoliter.toml` |
| Run an SDK `Makefile.toml` task | `make twoliter <task> [args]` | Forwards to `twoliter make --cargo-home .cargo --arch $ARCH` |
| Publish to a registry | `make publish VENDOR=<vendor>` | Needs `Infra.toml` with `[vendor.<vendor>] registry = ...` and `docker login`; see `BUILDING.md` |
| Regenerate full kernel configs | `make full-config` (optional `SDK=<image>`) | Runs `tools/latest-kernel-full-config.sh` in the SDK container via `tools/docker-run.sh`; honours `Twoliter.override`. Commit resulting `config-full-bottlerocket-*` changes |
| Compare kernel configs across commits | `tools/diff-kernel-config -b <rev> -a <rev> -k 6.12 -o <dir>` | Full kernel builds for each arch/version; needs clean tree |
| Extract built kernel configs | `tools/collect-kernel-config -o <dir>` | Reads `build/rpms/kernel-*`; script currently loops over 6.1 and 6.12 only |
| Validate CHANGELOG format | `./tools/validate-changelog.sh` | Same check CI runs |

To test kernel-kit changes in a variant without cloud credentials (local registry + `Twoliter.override`), see `document/bottlerocket/local-kit-workflow`. Bumping the pinned Twoliter or testing a local Twoliter build: `document/twoliter/version-bump-and-local-testing`.

## Tests and lints (what CI runs on PRs to `develop`)

From `.github/workflows/build.yml`, per arch in `{x86_64, aarch64}` on 32-core runners:

```
rustup component add rustfmt
make twoliter check-licenses
make twoliter unit-tests
make twoliter check-fmt
make twoliter check-clippy
make twoliter check-shell
make ARCH=<arch>
```

These task names come from the SDK's embedded `Makefile.toml` (via Twoliter), not from this repo; their exact scope is defined there. The only Rust with unit tests here is `sources/nvidia-migmanager` (`#[test]` fns in `src/main.rs`). `check-lints` (Go) is intentionally skipped; there is no Go code. Kernel/driver correctness is otherwise validated by the full build and the `make full-config` config check.

Other workflows:

| Workflow | Trigger | Does |
|---|---|---|
| `commitlint.yml` | PR opened/edited/sync | `npx commitlint -g .commitlint.config.mjs --from base --to head` (rules in `document/kernel-kit/conventions`) |
| `validate-changelog.yml` | PR touching `CHANGELOG.md` | `./tools/validate-changelog.sh` |
| `cache.yml` | push to `develop` | Builds both arches and saves `~/.cargo .cargo .gomodcache build/external-kits build/rpms build/state target` under cache key `build-cache` for PR runs |

`build.yml` ignores doc-only changes (`**.md`, `**.png`, `**.yaml`, `.github/CODEOWNERS`, …).

## Typical maintenance workflows

**Bump a kernel.** Run `packages/kernel-<v>/latest-kernel-srpm-url.sh` (uses an `amazonlinux:2023` container) to get the new SRPM URL; update `url`/`sha512` in `Cargo.toml` and `Source0`/`Version` in the spec; run `make full-config` and commit config diffs; build both arches; add a CHANGELOG line "Update kernel from A to B ([#PR])".

**Bump Neuron / NVIDIA / EFA.** Same pattern with `latest-neuron-srpm-url.sh`, `latest-2.24-neuron-srpm-url.sh`, or the `releases-url` in the kmod `Cargo.toml`; NVIDIA and EFA changes normally land in the r580/r595 or efa dirs for all three kernels at once.

**Bump the SDK or Twoliter.** SDK: edit `Twoliter.toml` `[sdk] version`, run `make update`, commit `Twoliter.lock` (CODEOWNERS-gated). Twoliter: edit `TWOLITER_VERSION` and both `TWOLITER_SHA256_*` in `Makefile`.

**Release.** Bump `release-version` in `Twoliter.toml`, add a `# vX.Y.Z (YYYY-MM-DD)` section at the top of `CHANGELOG.md`, tag `vX.Y.Z`. Advisories for that release go under `advisories/X.Y.Z/`.

## Gitignored local state

`build/`, `target/`, `.cargo/`, `.gomodcache/`, `tools/twoliter/`, `Infra.toml`, `Twoliter.override`, downloaded `*.tar.*`, `*.run`, and signature files under `packages/*/` (except `gpgkey-*.asc`).
