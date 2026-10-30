---
type: Reference
description: Languages, toolchain, runtime requirements, and key dependency versions (from the manifests) for Twoliter.
---

# Tech stack

## Language & toolchain

| Item | Value | Source |
|---|---|---|
| Language | Rust, edition 2021; Bash for embedded build scripts | `twoliter/Cargo.toml`, `twoliter/embedded/` |
| Toolchain | **nightly `nightly-2026-08-09`**, profile `default` — pinned for reproducibility; nightly is *required* for cargo `bindeps` | `rust-toolchain.toml`, `.cargo/config.toml` |
| Unstable cargo features | `bindeps = true`, `profile-hint-mostly-unused = true`; `rustflags = ["-Z", "threads=8"]` | `.cargo/config.toml` |
| Workspace | `resolver = "2"`, 34 explicit members (21 under `tools/`, `twoliter` + 11 `twoliter/src/tool-crates/*`, `tests/integration-tests`) plus `tools/krane` pulled in as a path dep | root `Cargo.toml` |
| Release profile | `strip = "debuginfo"`, `lto = "thin"`; `profile.dist` inherits release with `lto = "fat"`, `codegen-units = 1`; AWS SDK crates marked `hint-mostly-unused` | root `Cargo.toml` |
| Lints | `[workspace.lints.clippy] disallowed_methods = "deny"` + `clippy.toml` disallowed list (see `document/twoliter/conventions`) | root `Cargo.toml`, `clippy.toml` |
| Release targets | `x86_64-unknown-linux-musl`, `aarch64-unknown-linux-musl` (static) | root `Cargo.toml` `[workspace.metadata.dist]`, `.github/workflows/*.yml` |

## Runtime requirements (host running `twoliter`)

| Requirement | Why | Source |
|---|---|---|
| Linux | `pipesys`/`unplug` are Linux-only (UDS SCM_RIGHTS, seccomp) | `tools/pipesys/src/non_linux_server.rs`, `tools/unplug/src/main.rs` |
| Docker ≥ 23.0.0 with BuildKit | `build.Dockerfile` needs Dockerfile syntax 1.4.3; `DOCKER_BUILDKIT=1` set by `Makefile.toml` | `tools/buildsys/src/builder.rs`, `twoliter/embedded/Makefile.toml` |
| `cargo` + `cargo-make` | Twoliter execs `cargo make` on the host; `Makefile.toml` tasks run `cargo build` in the project's workspaces | `twoliter/src/cargo_make.rs`, README |
| `gzip`, `lz4` | preflight check + `setup-build` task | `twoliter/src/preflight.rs`, `Makefile.toml` |
| Bottlerocket SDK image | Pulled with embedded krane; default in fixtures/Makefile is `public.ecr.aws/bottlerocket/bottlerocket-sdk:v0.66.0` | root `Makefile`, `tests/projects/*/Twoliter.toml` |
| AWS credentials | Only for `pubsys`/`pcrsys`/`eif-builder` KMS paths (default SDK credential chain; `AWS_*` env passed through) | `tools/pubsys`, `twoliter/src/cargo_make.rs` |

## Key dependencies (workspace-pinned in root `Cargo.toml`)

| Area | Crates (version req) |
|---|---|
| CLI / async | `clap 4` (derive, env), `tokio 1`, `futures 0.3`, `async-trait 0.1`, `async-recursion 1`, `async-walkdir 1` |
| Errors / logging | `anyhow 1` (twoliter CLI), `snafu 0.8` (tools), `tracing 0.1` + `log 0.4` + `env_logger 0.11`, `simplelog 0.12` |
| Serialization | `serde 1`, `serde_json 1`, `toml 0.9`, `serde_yaml 0.9`, `olpc-cjson 0.1` (canonical JSON for lock/metadata), `serde_plain 1` |
| Versions / ids | `semver 1`, `uuid 1`, `jiff 0.2` (time), `strum 0.27` |
| Process / fs | `duct 1.1`, `which 8`, `path-absolutize 3.1`, `tempfile 3`, `walkdir 2`, `filetime 0.2` |
| Archives / compression | `tar 0.4`, `flate2 1`, `zstd 0.13`, `lzma-rs 0.3` |
| Containers | embedded `krane` = go-containerregistry **0.21.8** (`tools/krane/build.rs`); `oci-cli-wrapper` (local) |
| AWS | `aws-config 1`, `aws-sdk-{ec2,ebs,kms,ssm,sts} 1`, `aws-smithy-*`, `aws-lc-rs 1.17`, `coldsnap 0.11` (EBS snapshot up/download) |
| TUF | `tough 0.24`, `tough-kms 0.16`, `tough-ssm 0.19`, `tuftool 0.17` (embedded as a binary) |
| HTTP | `reqwest 0.13` (default-features off) |
| Cargo metadata | `guppy 0.17` (buildsys manifest graph) |
| RPM / images / boot | `rpm 0.18`, `gptman 3`, `fatfs 0.3`, `ext4-view 0.9`, `authenticode 0.5`, `object 0.37`, `pest 2.8` (grub/bootconfig parsers) |
| EIF / crypto | `coset 0.3`, `minicbor-serde 0.7`, `x509-cert 0.2`, `pem 3`, `sha2 0.10`, `crc32fast 1` |
| Sandboxing / IPC | `seccompiler 0.5`, `uds 0.4`, `inotify 0.11`, `nix 0.31`, `daemonize 0.5`, `libc 0.2` |
| Templating | `handlebars 6` (amispec), `tinytemplate 1` |
| Macros | `syn 2`, `quote 1`, `proc-macro2 1`, `darling 0.23`, `bon 3`, `nutype 0.5` |
| Testing | `test-case 3`, `mockall 0.13` |

Exact resolved versions: `Cargo.lock`. Dependency policy (allowed licenses, `multiple-versions = "deny"` with a skip list, `unknown-registry/git = "deny"`, `workspace-dependencies.unused = "deny"`): `deny.toml`. License-scan clarifications for attribution: `clarify.toml` (not a cargo-deny file).

## CI / release tooling

| Tool | Pin | Where |
|---|---|---|
| `cargo-deny`, `cargo-make` | `cargo install --locked` (latest) | `.github/workflows/rust.yml` |
| `cross` | git `cross-rs/cross` rev `7b79041`; `CROSS_NO_WARNINGS=0` | `rust.yml`, `release.yml` |
| `cargo-dist` fork | `webern/cargo-dist` rev `3dcbe823db0c4068f38db790d996a4af54e68b3e` (fork enables cross-compilation via `cross`) | `release.yml`, README |
| Go | `^1.18` via `actions/setup-go` in release jobs | `release.yml` |
| musl | `musl-tools musl-dev` apt packages + `rustup target add x86_64-unknown-linux-musl` | `rust.yml` |
| Dependabot | GitHub Actions weekly; cargo daily but `open-pull-requests-limit: 0` (security-only) | `.github/dependabot.yaml` |
