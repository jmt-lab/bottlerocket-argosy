---
type: Guide
description: How to build, lint, test, and release Twoliter — the real commands from Makefile, CI, and README, plus the test layout and fixtures.
---

# Development

Prerequisites (toolchain, Docker, cargo-make, gzip/lz4) are listed in `document/twoliter/tech`. `rustup` picks the pinned nightly from `rust-toolchain.toml` automatically.

## Everyday commands (root `Makefile`)

| Command | What it runs | Notes |
|---|---|---|
| `make fmt` | `cargo fmt --check` | |
| `make clippy` | `cargo clippy --locked -- -D warnings --no-deps` | `disallowed_methods` is deny-level (see `document/twoliter/conventions`) |
| `make deny` | `cargo deny --no-default-features check licenses bans sources` | needs `cargo install cargo-deny --locked` |
| `make test` | `cargo test --release --locked` | whole workspace; includes `integ-tests` feature tests that are **not** `#[ignore]`d — slow |
| `make integ` | `cargo test --manifest-path tests/integration-tests/Cargo.toml -- --include-ignored` | runs the Docker/network/full-build tests |
| `make attributions` | builds `tools/attribution/Dockerfile.attribution` on `BOTTLEROCKET_SDK_IMAGE` (default `public.ecr.aws/bottlerocket/bottlerocket-sdk:v0.66.0`) and runs `attribution.sh` → `twoliter-attributions.tar.gz` | needs Docker |
| `make check` | `fmt clippy deny attributions test integ` | |
| `make build` | `check` then `cargo build --release --locked` | what PR CI runs (`CARGO_BUILD_TARGET=x86_64-unknown-linux-musl make build`) |
| `make design` | `docs/design/bin/render-plantuml.sh` → `docs/design/diagrams/build-sequence.svg` | installs `planturl`, runs `plantuml/plantuml-server` in Docker |

Fast local loops:

```sh
cargo build --release --package twoliter --bin twoliter      # just the CLI
cargo test --no-default-features                              # skip integ-tests feature (README)
cargo test -p twoliter                                        # CLI unit tests only
cross build --release --bin twoliter --target aarch64-unknown-linux-musl   # as CI cross-build does
```

To exercise a local build against a real kit (`make build TWOLITER_DIR=…` in a kit checkout) or to roll a new release out to the kits and `bottlerocket`, see `document/twoliter/version-bump-and-local-testing`.

First builds download the pinned `krane` tarball from `https://cache.bottlerocket.aws` (`tools/krane/build.rs`); set `UPSTREAM_SOURCE_FALLBACK=true` to allow GitHub as a fallback.

## Test layout

| Location | What | Gate |
|---|---|---|
| `twoliter/src/**` `#[cfg(test)]` | Unit tests: project parsing/migration (`project/mod.rs`, `project/migrate/`), lock verification tags, `cargo_make` env filtering, `tools::test_install_tools`, `Make` arg parsing | always |
| `twoliter/src/test/` | Helpers `data_dir()` (→ `twoliter/src/test/data/`: `Twoliter-1.toml`, `Twoliter-invalid-version.toml`, `Release-{1,2}.toml`, `override/`, a mini `Makefile.toml`), `projects_dir()`, `copy_project_to_temp_dir()` | `#[cfg(test)]` |
| `twoliter/src/test/cargo_make.rs` | Runs real `cargo make` against the test `Makefile.toml` | feature `integ-tests` (default on); needs `cargo-make` |
| `twoliter/src/cmd/mod.rs` tests | `build_core_kit`, `build_extra_{1,2,3}_kit` — full in-process kit builds of `local-kit` | feature `integ-tests` **and** `#[ignore]` |
| `twoliter/src/cmd/make.rs` tests | `test_fetch_sdk_*`, `test_validate_kits_*` (real cargo make) | `#[ignore]` |
| `twoliter/src/tool-crates/embedded-bundle/tests/*.rs` | Wrappers that `bash twoliter/embedded/tests/test_<x>.sh` for `eif_sign_helper`, `guest_images_helper`, `partyplanner`, `provide_loader_config`, `uki_bootconfig` | always. `test_esp_loader_config.sh`, `test_fat_usage.sh`, `test_rpm2eif_args.sh` have **no** wrapper and are not run by `cargo test` |
| `tests/integration-tests/src/` | Separate crate; uses the built binaries via `env!("CARGO_BIN_FILE_TWOLITER")` / `CARGO_BIN_FILE_ADVISORY_CHECKER` (bindeps). Modules: `twoliter_build` (symlink handling), `twoliter_update` (spins up a local TLS `registry:2.8.3` in Docker, builds+publishes a kit, tests `Twoliter.override` redirect), `variant_build` (clones Bottlerocket, builds/repacks `aws-ecs-2`), `advisory_checker`, `appinventory` (compares application inventory between released and HEAD twoliter — **not** `#[ignore]`d, needs network + two full builds), `guest_images_helper`, `imghelper` (bash function tests) | most `#[ignore]` → `make integ` |
| `tools/*/src/**` | Per-crate unit tests (e.g. `tools/buildsys/src/manifest.rs` runs `cargo metadata --offline` on fixtures) | always |

### Fixture projects — `tests/projects/`

| Fixture | Shape | Used by |
|---|---|---|
| `local-kit` | SDK v0.66.0 with a deliberately bad registry fixed by `Twoliter.override`; kits `core-kit`, `extra-1/2/3-kit`; packages `pkg-a-1.27`…`pkg-g`; variants `hello-ootb`, `hello-eif`; Rust + Go sources | most twoliter and integration tests |
| `external-kit` | No `[sdk]`; depends on external `core-kit` from `custom-vendor` | `twoliter_update` |
| `project1` | Single variant, Go module `hello-go` | `Project::find_go_modules` test |
| `guest-images-kit` | `wrapper-variant` embedding `inner-variant` via `[package.metadata.build-variant.guest-images]` | buildsys manifest tests |
| `guest-images-graph` | No `Twoliter.toml`; cargo-metadata-only graph fixture | buildsys manifest tests |

## Trying a local Twoliter in the Bottlerocket repo

README "Testing the Binary in a Project": either point Bottlerocket's `cargo make` at a commit (`-e TWOLITER_REPO=… -e TWOLITER_VERSION=<sha> -e TWOLITER_ALLOW_SOURCE_INSTALL=true -e TWOLITER_ALLOW_BINARY_INSTALL=false -e TWOLITER_SKIP_VERSION_CHECK=true`, after `rm -rf tools/twoliter`), or copy `target/release/twoliter` into `$BOTTLEROCKET_REPO/tools/twoliter/` and set both `*_ALLOW_*_INSTALL=false` + `TWOLITER_SKIP_VERSION_CHECK=true`.

Debugging the embedded tools: `twoliter debug check-tools [--install-dir D]` extracts them and prints the directory.

## Release process (README "Releasing", `.github/workflows/release.yml`)

1. PR bumping `twoliter/Cargo.toml` version (+ `Cargo.lock`, `CHANGELOG.md`) to `X.Y.Z-rcN`; merge.
2. Push tag `vX.Y.Z-rcN`. The `Release` workflow (tag glob `*-?v[0-9]+*`, only on `bottlerocket-os/twoliter`, environment `release` — needs a second approver) runs `cargo dist plan` → draft GitHub release → `cargo dist build` per musl target via `cross` → uploads artifacts + `twoliter-attributions.tar.gz` → un-drafts.
3. Test the rc in a Bottlerocket PR; then PR dropping `-rc`, merge, tag `vX.Y.Z`, approve again, update the Bottlerocket PR to the final tag.

CI for PRs (`.github/workflows/rust.yml`): `build` job = `make build` on musl; `cross-build` matrix for both musl targets. Markdown/PlantUML/SVG-only changes skip CI.

## Contributing

`CONTRIBUTING.md`: open an issue for significant work, fork + PR, keep changes focused; security issues go to AWS vulnerability reporting, not GitHub issues. `.github/pull_request_template.md` exists.
