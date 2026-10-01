---
type: Reference
description: Patterns bottlerocket-core-kit consistently follows — commit message format, CHANGELOG structure, package directory layout and manifest keys, first-party crate conventions, dependency policy and filename casing.
---

# Conventions

## Commit messages (enforced by `.commitlint.config.mjs` in CI)
Format is `scope: description`, **not** Conventional Commits types. Header regex `^[a-z][a-z0-9._-]*: .+$`, max 72 chars, no trailing period, body lines ≤72 with leading blank line. Scope is usually a package/crate name or area, e.g. `kubernetes-1.36: update to v1.36.2`, `changelog: prepare for 15.0.0`, `release: bump version to v16.0.0`. Description is lowercase imperative ("add", "fix", "update"). Merge commits and `Revert "…"` are exempt. `.amazonq/rules/03-bottlerocket-git-format.md` restates the same rule for AI assistants.

## CHANGELOG.md
Top section `# Unreleased`, then `# vX.Y.Z (YYYY-MM-DD)` in descending order. Subsections used: `## OS Changes`, `## Third Party Package Updates`, `## Build Changes`; bullets end with `([#NNN])` and reference-style links to PRs are collected below the section. Validated by `tools/validate-changelog.sh`.

## Package directories (`packages/<name>/`)
- Always `Cargo.toml` + `<name>.spec`; `Cargo.toml` has `publish = false`, `build = "../build.rs"`, `[lib] path = "../packages.rs"`, and a `[package.metadata.build-package]` table (present in all 130 packages, sometimes empty).
- Directory and spec use the upstream name with dots for versioned lines (`containerd-2.3`); the crate `name` replaces `.` with `_` and `package-name = "containerd-2.3"` restores it.
- `[[package.metadata.build-package.external-files]]` entries carry `url` + `sha512` (optionally `path`, `bundle-modules = ["go"]`, `bundle-root-path`, `bundle-output-path`). 110 of 130 packages also set `releases-url` for upstream release tracking.
- Signature files (`*.sig`, `*.asc`) are git-ignored except `gpgkey-*.asc` public keys checked into the package dir.
- Upstream/backport patches are numbered `0001-…patch`; Bottlerocket-specific patches use a `9001-…` series (47 across the tree). `packages/glibc` additionally has one `HACK-…` patch.
- First-party packages use `source-groups = [...]` (dirs under `sources/`) instead of external files. 124 of 130 packages list `glibc` in `[build-dependencies]`.
- Spec names are `%{_cross_os}<name>`; first-party specs set `%global _cross_first_party 1`. Macros containing `cross` are Bottlerocket-specific and defined in the SDK.
- Runtime config templates and systemd units for first-party daemons live beside the spec in `packages/os/` and `packages/release/`, with `Source` numbers grouped by range (e.g. `1xx` = systemd units in `os.spec`).

## First-party Rust crates (`sources/`)
- 51 of the 60 crates have a `README.tpl` and generate `README.md` from rustdoc via `cargo-readme` in `build.rs` (the `generate-readme` crate). For those, edit the doc comment in `src/main.rs`/`src/lib.rs`, not the README (each generated README ends with a "Colophon" saying so).
- Errors via `snafu` (49 crates; 22 keep a dedicated `error.rs`), CLI parsing via `argh` (16 crates, no `clap`), logging via `log` + `simplelog` (24 crates).
- Dependency versions live only in `sources/Cargo.toml` `[workspace.dependencies]`; crates reference them with `workspace = true`.
- `sources/deny.toml`: one version per crate (exceptions listed in `skip-tree` with a justification comment), allowlisted licenses only, git deps only from `bottlerocket-settings-sdk`.
- `sources/clippy.toml`: never call `BehaviorVersion::latest()`; pin an explicit AWS SDK behavior version.
- Boot-time coordination uses the `bottlerocket-launch` datastore transaction (`constants::LAUNCH_TRANSACTION`); services depending on earlier settings run `settings-committer` as a pre-exec.
- Crates that talk to the API use the `apiclient` library over the Unix socket (`constants::API_SOCKET` = `/run/api.sock`); settings-driven binaries read a TOML config rendered by thar-be-settings from a `*-toml` template in `packages/os/`.
- Component names follow the "dog"/animal theme (updog, sundog, corndog, netdog, ghostdog, logdog, metricdog, driverdog, dogtag, bloodhound, whippet, rottweiler, brush…); `GLOSSARY.md` decodes them.

## Filename casing (`CONTRIBUTING.md`)
Extensions lowercase; build config files Capitalized (`Infra.toml`, `Twoliter.toml`); documents/licenses ALL CAPS (`BUILDING.md`); everything else lowercase.

## Branching & versions
Development on `develop`; releases are tags `vX.Y.Z` mirroring `Twoliter.toml` `release-version`; patch branches (`X.Y.x`) only when a patch is needed. Advisories for a release go in `advisories/<X.Y.Z>/BRSA-<id>.toml`.
