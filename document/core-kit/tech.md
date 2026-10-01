---
type: Reference
description: Languages, toolchain, build tooling and key dependency versions for bottlerocket-core-kit, taken from Twoliter.toml, Makefile, sources/Cargo.toml, go.mod and package manifests.
---

# Tech stack

## Toolchain & build tooling

| Component | Version | Where pinned |
|---|---|---|
| Twoliter (kit build orchestrator; wraps buildsys + cargo-make) | 0.23.0 (sha256-pinned per host arch) | `Makefile` `TWOLITER_VERSION` |
| Bottlerocket SDK container (cross toolchains, RPM macros) | v0.78.0, digest-pinned | `Twoliter.toml` `[sdk]`, `Twoliter.lock` |
| Twoliter schema | 2 | `Twoliter.toml` |
| Kit release version | 16.0.0 | `Twoliter.toml` `release-version` |
| cargo-make | latest via `cargo install cargo-make` | `BUILDING.md`, CI |
| Rust (host, to run cargo/twoliter) | stable via rustup; `BUILDING.md` states ≥1.51 as a floor | `BUILDING.md` |
| Rust (target) | provided by the SDK, not by this repo (no `rust-toolchain` file) | — |
| Go (target) | provided by SDK; modules declare `go 1.26.1` (host-ctr) and `go 1.24.9` (ecs-gpu-init) | `sources/*/go.mod` |
| Go (lint only, CI) | 1.21 with golangci-lint v2 config | `.github/workflows/golangci-lint.yaml`, `.golangci.yaml` |
| Docker | required on the build host | `BUILDING.md` |
| RPM | package format; specs use SDK `%cross_*` macros | `packages/*/*.spec` |

Package build artifacts live in `build/` (git-ignored). Cross-compilation host/target split is explained in `packages/README.md`.

## First-party Rust workspace (`sources/Cargo.toml`)

Resolver 1, edition 2021 crates, `[profile.release] debug = "line-tables-only"`. All third-party versions are centralised in `[workspace.dependencies]`; notable ones:

| Area | Crates (version req) |
|---|---|
| HTTP server / API | actix-web 4, actix 0.13, actix-web-actors 4, hyper 1, hyper-util 0.1, hyper-rustls 0.27, hyper-unix-connector 0.2, http 0.2, reqwest 0.12 |
| Async runtime | tokio ~1.51 (LTS pin), tokio-util 0.7, tokio-tungstenite 0.20, futures 0.3 |
| TLS / crypto | rustls 0.23, aws-lc-rs 1, hkdf 0.12, sha2 0.10, zeroize 1, x509-parser 0.18 |
| AWS | aws-config 1, aws-sdk-{ec2,eks,s3,ssm,cloudformation,secretsmanager} 1, aws-smithy-* (plus vendored `sources/aws-smithy-experimental`) |
| Updates | tough 0.24 (TUF), gptman 1, semver 1 |
| Serialization | serde 1, serde_json 1, toml 0.8, serde_yaml 0.9, olpc-cjson 0.1 |
| Templating / parsing | handlebars 4, pest 2.8 |
| CLI / errors / logging | argh 0.1, snafu 0.8, log 0.4.28, simplelog 0.12, env_logger 0.11 |
| D-Bus | zbus 5.11, zvariant 5.7 |
| Settings plugin ABI | abi_stable 0.11.3 |
| Testing | httptest 0.15, test-case 3, tokio-test 0.4, tempfile 3 |

**Git dependencies** (the only ones allowed by `sources/deny.toml`): `bottlerocket-settings-models` v0.25.0, `bottlerocket-modeled-types` v0.17.0, `settings-extension-oci-defaults` v0.1.0 (tag `bottlerocket-settings-models-v0.25.0`), and `bottlerocket-settings-plugin` v0.1.0, all from `github.com/bottlerocket-os/bottlerocket-settings-sdk`.

**Policy files**

| File | Enforces |
|---|---|
| `sources/deny.toml` | cargo-deny: license allowlist (Apache-2.0, MIT, BSD-3, ISC, MPL-2.0, Zlib, …), `multiple-versions = "deny"` with explicit `skip-tree` exceptions, bans `structopt`/`clap`, denies unknown registries/git |
| `sources/clippy.toml` | Disallows `BehaviorVersion::latest()` (aws-config / smithy) — pin an explicit version |
| `sources/clarify.toml` | License clarifications for the license-scan (`check-licenses`) |

## Go modules
`sources/host-ctr` (containerd client, urfave/cli app) and `sources/ecs-gpu-init` (`github.com/NVIDIA/go-nvml`). Both carry `go.sum`; vendoring for the containerized build is handled by buildsys.

## Notable third-party package versions (from `packages/*/Cargo.toml` `external-files`)
Versions change often; always read the manifest. At kit 16.0.0: glibc 2.43, systemd 257.13 (also a 252 line), containerd 2.3.4 (also 1.7, 2.2), runc 1.3.6, Kubernetes 1.36.2 from EKS Distro (also 1.31–1.35). Many manifests add `releases-url` so tooling can check for upstream releases.

## Repo-level tooling
commitlint (Node, `.commitlint.config.mjs`), Dependabot (GitHub Actions weekly; cargo/gomod security-only), rust-analyzer config in `.vscode/settings.json`.
