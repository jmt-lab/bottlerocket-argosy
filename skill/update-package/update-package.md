---
type: Skill
description: Update one or more third-party packages to a new upstream version in bottlerocket-core-kit or bottlerocket-kernel-kit and build them — bump Cargo.toml external-files URLs and sha512 hashes (including signatures), update the spec Version/Release or versioning macro and GO_MAJOR, drop upstreamed or rebase failing patches, rotate GPG keys, build the single package with upstream source fallback, and commit one signed-off commit per package. Also use it just to rebuild a single package after a spec or patch change.
---

# Update (and build) a third-party package

Background and all the per-pattern details are in `document/core-kit/updating-third-party-packages`; spec rules are in `document/core-kit/packaging-style-guide` and `styleguide/rpm-spec/*`. This is the procedure.

## Input

- Package(s) and target version, e.g. `libselinux=3.7 libsepol=3.7`.
- Kit repo: a local checkout of `bottlerocket-core-kit` or `bottlerocket-kernel-kit`.

Run everything from the kit repo root. Docker must be running; `make prep` installs Twoliter.

## Procedure (per package)

1. **Locate** `packages/<name>/` (versioned dirs such as `kubernetes-1.35` exist). Read `Cargo.toml`, the spec and every patch before editing. Kernels and kernel modules follow the kernel-kit section of the document instead.
2. **Cargo.toml:** check the new version via `releases-url`; update the version in each `external-files` `url` and `path` (archive and signature); recompute every `sha512` from the real download. Add new incremental-patch entries if upstream published them (and cover them in the package `.gitignore`).
3. **Spec:** identify the versioning pattern (direct `Version:`, `gover`, `releasever`+`gover`, `unversion`, `ncurses_rev`, `majorminor`/`version`) and edit only what it requires. Reset `Release:` to `1%{?dist}` unless the spec uses a special form. Never touch `Epoch:`. Update `SourceN:` filenames that changed. For Go packages, set, bump or remove `GO_MAJOR` per upstream's `go.mod`.
4. **Patches:** for each, decide upstreamed (remove file + spec lines), still needed (keep), or failing (rebase via `git cherry-pick -x` + `git format-patch` from upstream). When unsure, keep it and let the build decide.
5. **Build just this package:**
   ```bash
   PACKAGE=<name> BUILDSYS_UPSTREAM_SOURCE_FALLBACK=true make twoliter build-package   # after a version bump
   PACKAGE=<name> make twoliter build-package                                         # same-version spec/patch change
   ```
   Use `_` for dots in the name (`kubernetes-1_35`). Add `BUILDSYS_ARCH=aarch64` for the other arch. On failure, use the troubleshooting tables in the document (GPG key rotation, missing `BuildRequires`, patch fuzz, cache fetch errors) and loop back to step 2–4.
6. **Validate** against the checklist in the document.
7. **Commit** one package per commit, message in a file: `<name>: update to <version>`, body listing removed/rebased patches and cite-style links for any new Bottlerocket patch; `git commit -s -F <file>` (add `-S` if you sign commits).

Repeat for each package, building them one by one.

## Next

Test the change on a node: `skill/test-third-party-package`. For Go packages, consider `skill/govulncheck-source`.
