---
type: Reference
description: Patterns the Twoliter codebase enforces or consistently follows — lint rules, error handling split, env-var passthrough, embedding, typestate locking.
---

# Conventions

| Convention | Detail | Enforced by / seen in |
|---|---|---|
| **Never `canonicalize` paths** | `std::path::Path::canonicalize`, `std::fs::canonicalize`, `tokio::fs::canonicalize` are `disallowed_methods` ("Twoliter usually does not want to resolve symlinks. Use path_absolutize instead"). Use `path_absolutize::Absolutize` or `crate::common::fs` wrappers | `clippy.toml`; root `Cargo.toml` `[workspace.lints.clippy] disallowed_methods = "deny"`; `tests/integration-tests/src/twoliter_build.rs` (symlink test) |
| **Wrap AWS SDK errors** | `aws_sdk_{ec2,ssm,ebs,kms,sts}::error::SdkError` and `aws_smithy_runtime_api::…::SdkError` are `disallowed_types` in `clippy.toml`; use `error_utils::AwsSdkError` for consistent formatting | `clippy.toml` (warn-level lint, fatal under `make clippy`'s `-D warnings`), `tools/error-utils` |
| **Error style split** | The `twoliter` CLI crate uses `anyhow` (+ `.context()`). Most `tools/*` crates use `snafu` with a per-crate `error.rs`; exceptions using `anyhow`: `pipesys`, `unplug`, `krane` | `twoliter/Cargo.toml`, `tools/*/Cargo.toml` |
| **Logging** | `tracing` macros (with `log` feature) in the CLI, `env_logger` init; `--log-level` overrides `RUST_LOG` for the `twoliter` crate only; `-q` ⇒ warn and `TWOLITER_QUIET=1` → `PUBLISH_LOG_LEVEL=warn` in Makefile | `twoliter/src/cmd/mod.rs::init_logger`, `twoliter/embedded/Makefile.toml` |
| **Env passthrough is allowlisted** | Only `BUILDSYS_*`, `PUBLISH_*`, `REPO_*`, `BOOT_CONFIG*`, `AWS_*` prefixes plus the `ENV_VARS` list reach `cargo make`; `BUILDSYS_SDK_NAME/VERSION`, `BUILDSYS_REGISTRY`, `BUILDSYS_OUTPUT_GENERATION_ID` are rejected because their values now live in `Twoliter.toml`/code | `twoliter/src/cargo_make.rs` |
| **Typestate for lock level** | `Project<Unlocked | SDKLocked | Locked>`; `ProjectLock` is sealed with a private `SealToken`. Commands request the weakest lock they need | `twoliter/src/project/mod.rs` |
| **Fail closed on stale locks** | Every lock load re-resolves against registries and errors on mismatch rather than auto-updating; lockfile tag/version consistency is validated to catch hand edits | `twoliter/src/project/lock/mod.rs` |
| **Canonical JSON for on-disk metadata** | `olpc_cjson::CanonicalFormatter` for `external-kit-metadata.json` and verification manifests so byte-comparison is stable | `lock/mod.rs::synchronize_metadata`, `lock/verification.rs` |
| **Embed, don't install** | New helper binaries are added as `artifact = ["bin:…"]` workspace deps + a `twoliter/src/tool-crates/<name>` shim + an entry in `tools.rs::install_tools`; new scripts must be added to the allowlist in `tool-crates/embedded-bundle/build.rs` or they won't ship | see `document/twoliter/architecture` |
| **Uniform mtimes for extracted tools** | `install_tools` stamps every extracted file with `build.Dockerfile`'s mtime (docker cache stability) | `twoliter/src/tools.rs` |
| **Pinned, checksum-verified downloads** | Anything fetched at build time goes through `tools/build-cache-fetch` with a `SHA512 (file) = …` hash file; upstream fallback is opt-in | `tools/krane/hashes/*`, `tools/attribution/attribution.sh` |
| **Dependency hygiene** | `cargo deny` bans duplicate versions (explicit `skip` list with reasons), wildcard deps, unknown registries/git sources, and unused workspace deps | `deny.toml`, `make deny` |
| **Bash helper tests** | Embedded scripts get `twoliter/embedded/tests/test_*.sh` plus a one-line Rust wrapper in `tool-crates/embedded-bundle/tests/` so they run under `cargo test` | see `document/twoliter/development` |
| **Changelog + version bump in one PR** | Releases follow Keep-a-Changelog with PR links; rc versions (`X.Y.Z-rcN`) precede finals | `CHANGELOG.md`, README |
