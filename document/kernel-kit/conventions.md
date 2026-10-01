---
type: Reference
description: Enforced and observed conventions in the kernel kit — commit message format, CHANGELOG structure, package directory layout, naming, versioning and advisories.
---

# Conventions

## Commit messages (enforced by `.commitlint.config.mjs` in CI)

- Header is `scope: description`, regex `^[a-z][a-z0-9._-]*: .+$`. Scope is usually a package dir (`kernel-6.12: update to 6.12.103`) or an area (`changelog: update for v9.1.0`, `twoliter: bump kit version to v9.1.0`).
- Header ≤ 72 chars, trimmed, no trailing period; body lines ≤ 72 chars with a blank line before the body.
- Standard Conventional Commit types (`feat:`, `fix:`) are *not* used.
- Ignored: `Merge pull request #…` and `Revert "…"` messages.

## CHANGELOG.md (enforced by `tools/validate-changelog.sh`)

- Top-level headers must be `# vX.Y.Z (YYYY-MM-DD)`, unique, in descending version order; a single leading `# Unreleased` is allowed.
- Sections seen: `## OS Changes`, `### Third Party Package Updates`, `## Build Changes`. Bullets end with `([#NNN])` and each PR gets a reference-style link line `[#NNN]: https://github.com/bottlerocket-os/bottlerocket-kernel-kit/pull/NNN` at the end of the section.

## Package layout (`packages/<name>/`)

- Directory name uses dots (`kernel-6.12`); Cargo crate name uses underscores (`kernel-6_12`). When the two differ, `[package.metadata.build-package] package-name` records the RPM/dir name.
- Every package `Cargo.toml` sets `build = "../build.rs"`, `[lib] path = "../packages.rs"`, `publish = false`, `edition = "2021"`, `version = "0.1.0"` (verified across all 19 packages).
- Upstream inputs are `[[package.metadata.build-package.external-files]]` entries with `url` and `sha512`; `force-upstream = true` marks files that must be fetched from the original URL rather than the Bottlerocket cache. Kernel manifests carry a comment naming the helper script that produced each URL (`latest-kernel-srpm-url.sh`, `latest-neuron-srpm-url.sh`); other packages rely on `releases-url` or a `latest-*.sh` script in the directory.
- Spec file is `<name>.spec`; RPM name is `%{_cross_os}<name>`. Where upstream signs its artifacts, the dir ships a `gpgkey-<fingerprint>.asc` and the spec verifies before extracting: `rpmkeys --checksig` for AL2023 SRPMs (kernels, grub, libkcapi) and `%{gpgverify}` for tarballs (shim, microcode, linux-firmware). NVIDIA/EFA/nvlsm inputs are hash-checked only.
- Patch numbering: kernel dirs use `1001-…` for Bottlerocket patches and `2001-…` for Neuron; `grub` uses `0001-…0048-…`. Patch filenames are `git format-patch` style.
- Per-kernel module packages exist in parallel (`kmod-6.1-*`, `kmod-6.12-*`, `kmod-6.18-*`) and are updated together, but are not byte-identical (e.g. `kmod-6.1-nvidia-r580` has no IMEX inputs). Diff the sibling dirs before assuming a change applies to all three.
- Variant coupling is expressed with SDK capabilities in specs: `variant-platform(aws|vmware|metal)`, `variant-flavor(nvidia|nvidia-fips)`, `image-feature(fips|uki-image|no-erofs-root-partition|external-kmod-development|…)`.

## First-party Rust (`sources/`)

- Crates use workspace-pinned dependencies (`foo.workspace = true`), `snafu` for errors, `argh` for CLI, `simplelog`.
- `README.md` is generated from the crate's rustdoc by `generate-readme` in `build.rs` with `README.tpl`; edit the doc comment in `src/main.rs`, not the README.
- Licenses/duplicates policed by `sources/deny.toml`.

## Filenames (from `CONTRIBUTING.md`)

Lowercase extensions; build configuration files start with a capital (`Twoliter.toml`, `Infra.toml`); documents/licenses all caps (`BUILDING.md`); everything else lowercase.

## Versioning and branches

- Kit version lives only in `Twoliter.toml` `release-version`; git tags are `vX.Y.Z`; work lands on `develop`.
- Crate versions (`0.1.0`) are placeholders and never bumped.
- `advisories/<kit-version>/BRSA-<id>.toml` records advisories shipped in that kit version; `advisories/staging/` holds unreleased ones (empty at v9.1.0). Advisory `package-name` values may reference kernels no longer in the kit (e.g. `kernel-5.10`) because the directory is historical.

## Ownership

`Twoliter.*` changes require review from the owners listed in `.github/CODEOWNERS`.
