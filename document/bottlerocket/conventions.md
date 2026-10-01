---
type: Reference
description: Patterns the bottlerocket top-level repo consistently follows — commit message format, filename casing, empty-lib build-driver crates, shared-defaults symlinks and numbering, migration naming, README generation, licensing.
---

# Conventions

## Commit messages (enforced by CI via `.commitlint.config.mjs`)
- Header is `scope: description` where scope matches `^[a-z][a-z0-9._-]*` — typically a component or area (`twoliter: Bump kernel-kit to 9.0.2`, `settings-plugins: add aws-k8s plugin`, `changelog: update changelog for v1.64.0`). Not Conventional-Commits types.
- Header ≤72 chars, trimmed, no trailing period; body lines ≤72 chars with a blank line after the header.
- Merge commits and `Revert "…"` are ignored by the linter.

## Filenames (`CONTRIBUTING.md`)
- Extensions lowercase. Build config files start with a capital (`Infra.toml`, `Release.toml`, `Test.toml`, `Twoliter.toml`, `Licenses.toml`). Documents/licenses ALL CAPS (`PUBLISHING.md`). Everything else lowercase.

## Cargo crates as build drivers
- Variant and package crates contain no code: `build = "../build.rs"` (execs `buildsys`) and `[lib] path = "../variants.rs"` / `"../packages.rs"` (empty files). Always `publish = false`.
- Crate names cannot contain `.`; variants use `_` (`aws-k8s-1_36`) with a comment noting the real name. Settings-defaults crates are `settings-defaults-<variant with _>`.
- Buildsys reads `[package.metadata.build-variant]` / `[package.metadata.build-package]`; Cargo ignores it.
- Most crates (44 of 49 variants, all `sources/` crates with generated READMEs) set `exclude = ["README.md"]` so doc edits don't trigger rebuilds.

## `sources/` crates
- README.md files are **generated** from rustdoc via `generate-readme` in `build.rs` + a sibling `README.tpl`; edit the crate-level `/*! … */` doc comment, not README.md. Set `SKIP_README` to skip.
- Errors use `snafu` with a private `mod error` and `pub type Result<T>`; migration `main()` wraps `run()` to print `Display` errors.
- Dependencies are declared once in `sources/Cargo.toml [workspace.dependencies]` and referenced with `.workspace = true`.
- License on every crate: `Apache-2.0 OR MIT`. Contributions are dual-licensed (PR template).
- Settings SDK crates are pulled from git by tag; all five must share the same tag.

## Settings defaults
- Canonical content lives in `sources/shared-defaults/<topic>.toml` (48 files). Per-variant `sources/settings-defaults/<variant>/defaults.d/NN-<topic>.toml` entries are **symlinks** (`../../../shared-defaults/<topic>.toml`); the only real files are the three `50-<variant>.toml` in the `*-dev` variants. Check `readlink` before editing "a variant's" default — you are editing every variant that links it.
- Files apply in lexical order; later override earlier. Observed bands: `10-defaults`, `11-updates`, `15-*-tuf`, `20/21` host/bootstrap containers, `25/26` cfsignal/autoscaling, `30/31` metrics, `40` creds, `50–58` orchestrator/containerd/image-verification, `60` lockdown, `70–77` oci hooks/defaults, `90-boot`.
- Alternatives are expressed as paired shared files a variant picks between: `lockdown-integrity` vs `lockdown-none`, `kubernetes-seccomp-default-true` vs `-false`, `kubernetes-device-ownership-default-true` vs `-false`, `public-*` vs `aws-*` (tuf, host containers, bootstrap containers).
- Setting-generator commands reference core-kit binaries (`schnauzer-v2 render --requires 'aws@v1' …`, `shibaken`, `bork`). `strength = "weak"` is used for values like host-container image URIs that should refresh on update.

## Settings migrations
- Path `sources/settings-migrations/v<X.Y.Z>/<kebab-name>/`; `X.Y.Z` is the *first version that ships the change*. Binary name becomes `migrate_v<X.Y.Z>_<kebab-name>`; the `Release.toml` entry is that name plus `.lz4`.
- Prefer `migration_helpers::common_migrations` (`AddPrefixesMigration`, etc.) over hand-written logic.
- Migrations older than the supported downgrade window move to `sources/settings-migrations/archived/` and are removed from `sources/Cargo.toml` (comment there marks the insertion point).

## Variants
- Every variant lists exactly the three local packages in `[build-dependencies]`; everything else comes from kits via `included-packages`.
- Dev variants (`*-dev`) include `release`, Docker, and debugging tools (`login`, `strace`, `iputils`), and set `in-place-updates = false`.
- `release-swap` (instead of `release`) is used only by the k8s 1.35 and 1.36 variants so far.
- Kubernetes variants support the named k8s minor plus the next three (documented in `variants/README.md`).
- Newer AWS variants (ecs-3+, k8s-1.33+, some FIPS siblings) carry an `amispec.toml` that is a copy of `variants/shared/amispec-split.toml` (IMDSv2 required, gp3 volumes); older AWS variants have none.

## Misc
- `.mailmap` maintained for author identities; `CHANGELOG.md` has an `# Unreleased` section at the top with PR-link footnotes.
- Git-ignored local state: `build/`, `.cargo/`, `.gomodcache/`, `Infra.toml`, `Test.toml`, `Licenses.toml`, `licenses/`, `keys/`, `roles/`, `sbkeys/**/`, `tests/`, `Twoliter.override`, `*.pem`.
