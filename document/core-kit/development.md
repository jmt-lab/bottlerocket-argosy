---
type: Guide
description: How to build, test, lint, publish and contribute to bottlerocket-core-kit — the actual commands from Makefile, BUILDING.md and CI, plus prerequisites and CI workflow map.
---

# Development

## Prerequisites (from `BUILDING.md` and `.github/actions/setup-node/action.yml`)

| Need | Detail |
|---|---|
| Linux host, x86_64 or aarch64 | ≥80 GB disk; first full build ~20 min on a fast machine, hours on a small one; scales to 32+ cores |
| System packages | Ubuntu: `build-essential openssl libssl-dev pkg-config liblz4-tool cmake clang libclang-dev` — Fedora: `make automake gcc openssl openssl-devel pkg-config lz4 perl-FindBin perl-lib cmake clang clang-tools-extra` |
| Rust stable via rustup, plus `cargo install cargo-make` | Host-side only; target toolchains come from the SDK image |
| Docker running, user in `docker` group | Every package builds in a container |
| Twoliter | Installed automatically by `make prep` into `tools/twoliter/` (binary download, sha256-checked; falls back to source build) |

## Build

```shell
make                       # = make build: prep → fetch → twoliter build kit bottlerocket-core-kit --arch $(uname -m)
make ARCH=aarch64          # cross-build the other arch
make UPSTREAM_SOURCE_FALLBACK=true   # allow fetching external-files from upstream URLs, not just cache.bottlerocket.aws
make update                # twoliter update (refresh Twoliter.lock after changing SDK/kit deps)
make fetch                 # twoliter fetch --arch $ARCH (SDK + external kits)
```
Outputs: RPMs in `build/rpms/`, kit image staged under `build/` (git-ignored). Package builds are cached; only changed packages rebuild.

Finer-grained tasks (single-package builds, etc.) come from Twoliter's embedded cargo-make `Makefile.toml`, not this repo. `make twoliter <task> [args…]` forwards to `twoliter make --cargo-home .cargo --arch $ARCH <task> …`; run `./tools/twoliter/twoliter make --help` after `make prep` to list them. (`packages/README.md` shows the underlying `cargo make -e PACKAGE=<name> build-package` form.)

## Test / lint (exactly what CI runs, `.github/workflows/build.yml`)

```shell
rustup component add rustfmt
make twoliter check-licenses   # license checks over sources/ (uses sources/deny.toml + clarify.toml)
make twoliter unit-tests       # unit tests for the sources/ workspace
make twoliter check-fmt        # rustfmt check
make twoliter check-clippy     # clippy (honours sources/clippy.toml)
make twoliter check-shell      # shell script lint
make ARCH=x86_64               # full kit build (CI runs both arches)
```
Task bodies live in Twoliter, so the one-line descriptions above are inferred from the task names and the config files they consume. Go lint runs separately: golangci-lint on `sources/host-ctr` and `sources/ecs-gpu-init` (`.github/workflows/golangci-lint.yaml`, config `.golangci.yaml`).

For quick iteration on Rust code you can work directly in the `sources/` workspace with plain `cargo test -p <crate>` on the host (rust-analyzer is pointed at `sources/Cargo.toml` by `.vscode/settings.json`); this is not what CI runs and some crates need Linux-only system deps.

Test layout: unit tests inline (`#[cfg(test)]`, ~100 files) plus `tests/` dirs in `whippet`, `driverdog`, `ghostdog`, `netdog/systemd-derive`, `updater/update_metadata`, `updater/updog`, `api/certdog`, `api/prairiedog`, `api/schnauzer`, `api/storewolf`, `api/migration/migrator`. `host-ctr` has `cmd/host-ctr/main_test.go`.

## Publish a kit (for testing a variant against your changes)

1. Create `Infra.toml` (git-ignored) with `[vendor.<name>] registry = "<acct>.dkr.ecr.<region>.amazonaws.com"`.
2. `aws ecr get-login-password … | docker login …`
3. `make publish VENDOR=<name>` (= `twoliter publish kit bottlerocket-core-kit <vendor>`).
4. In the variant repo's `Twoliter.toml`, add the vendor and point `[[kit]] bottlerocket-core-kit` at your version, then `./tools/twoliter/twoliter update`.

Details: `BUILDING.md` §Publish / §Consuming.

## Adding or updating a package
Follow `packages/README.md`: create `packages/<name>/{Cargo.toml,<name>.spec}` pointing at `../build.rs` and `../packages.rs`, list `external-files` with sha512, declare `[build-dependencies]`/`[dependencies]`, add the member to root `Cargo.toml` and to `kits/bottlerocket-core-kit/Cargo.toml` `[build-dependencies]`. Go modules without vendored deps need `bundle-modules = ["go"]`. Conventions in `document/conventions`.

## CI workflows (`.github/workflows/`)

| Workflow | Trigger | Does |
|---|---|---|
| `build.yml` | PR to `develop` (ignores `*.md`, `*.yaml`, images, `.vscode`) | 32-core self-hosted runners, matrix x86_64/aarch64: restores `build-cache`, runs the check tasks above, full build |
| `cache.yml` | push to `develop` | Rebuilds both arches and saves `~/.cargo .cargo .gomodcache build/external-kits build/rpms build/state target` as `build-cache` |
| `commitlint.yml` | PR events | `npx commitlint -g .commitlint.config.mjs` over PR commits |
| `validate-changelog.yml` | PR touching `CHANGELOG.md` | `tools/validate-changelog.sh`: headers must be `# vX.Y.Z` (one optional leading `# Unreleased`), unique, descending |
| `golangci-lint.yaml` | PR touching Go files | lints both Go modules |
| `update-eni-max-pods.yaml` | weekly cron / manual | regenerates `packages/os/eni-max-pods` from aws/amazon-vpc-cni-k8s and opens a PR |

## Contributing (`CONTRIBUTING.md`, `.github/pull_request_template.md`)
Open an issue first for significant work; branch from `develop`; PR template asks for issue number, description, testing done; contributions are dual-licensed Apache-2.0/MIT. Releases are tagged `vX.Y.Z` with a matching `CHANGELOG.md` section and `Twoliter.toml` `release-version` bump; patch branches are cut only when needed.
