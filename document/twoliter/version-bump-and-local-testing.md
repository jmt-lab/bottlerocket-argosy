---
type: Guide
description: Two cross-repo Twoliter workflows — bumping the pinned Twoliter version and SHA256s in core-kit/kernel-kit Makefiles (X.Y.Z) and bottlerocket/Makefile.toml (vX.Y.Z) with chore-bump commits, and testing a locally built Twoliter against a kit via make build TWOLITER_DIR=…
---

# Twoliter: version bumps and local testing

Complements `document/twoliter/development` (building/releasing Twoliter itself) and `document/bottlerocket/decisions/kits-and-twoliter`. Paths below assume sibling checkouts of `twoliter`, `bottlerocket-core-kit`, `bottlerocket-kernel-kit` and `bottlerocket`.

## A. Bump Twoliter across kits and bottlerocket

1. Fetch checksums for the target release (`X.Y.Z`, e.g. `0.13.0` or `0.13.0-rc1`):
   ```bash
   curl -sSL "https://github.com/bottlerocket-os/twoliter/releases/download/vX.Y.Z/twoliter-x86_64-unknown-linux-musl.tar.xz.sha256"
   curl -sSL "https://github.com/bottlerocket-os/twoliter/releases/download/vX.Y.Z/twoliter-aarch64-unknown-linux-musl.tar.xz.sha256"
   ```
2. Each kit (`bottlerocket-core-kit`, `bottlerocket-kernel-kit`) — edit `Makefile` (**no** `v` prefix):
   ```makefile
   TWOLITER_VERSION ?= "X.Y.Z"
   TWOLITER_SHA256_AARCH64 ?= "<aarch64 sha>"
   TWOLITER_SHA256_X86_64 ?= "<x86_64 sha>"
   ```
   `git add Makefile && git commit -m "chore: bump to twoliter X.Y.Z"`
3. `bottlerocket/Makefile.toml` (**with** `v` prefix):
   ```toml
   TWOLITER_VERSION = "vX.Y.Z"
   TWOLITER_SHA256_AARCH64 = "<aarch64 sha>"
   TWOLITER_SHA256_X86_64 = "<x86_64 sha>"
   ```
   `git add Makefile.toml && git commit -m "chore: bump to twoliter X.Y.Z"`
4. Validate: each repo's `git show HEAD --stat` shows 1 file, 3 insertions, 3 deletions:
   ```bash
   for r in bottlerocket-core-kit bottlerocket-kernel-kit bottlerocket; do (cd "$r" && git show HEAD --stat); done
   ```

If the `.sha256` download fails, check that `https://github.com/bottlerocket-os/twoliter/releases/tag/vX.Y.Z` exists and has the musl tarballs attached.

Notes: the bump only creates local commits — push and open one PR per repo yourself; PRs trigger CI against the new Twoliter. Moving RC → stable: edit the same three lines, then `git add <file> && git commit --amend -m "chore: bump to twoliter X.Y.Z"`. Twoliter `schema-version` changes are rare — only touch them when release notes say so (kits and Twoliter must be bumped together when the schema changes). The kit repos' commitlint requires `scope: description` (`document/core-kit/conventions`); `chore: bump to twoliter X.Y.Z` matches that header regex.

## B. Test a locally built Twoliter

Twoliter CLI sources are under `twoliter/twoliter/src/`; the cargo-make tasks and scripts it embeds are under `twoliter/twoliter/embedded/`.
```bash
cd twoliter && cargo build --release            # binary at target/release/twoliter
cd ../bottlerocket-core-kit
make build TWOLITER_DIR=../twoliter/target/release  # directory containing the locally built binary
```
Iterate: rebuild Twoliter, rerun `make build …`. Omit `TWOLITER_DIR` to return to the pinned release in `tools/twoliter/twoliter`.

Troubleshooting: confirm `ls -lh twoliter/target/release/twoliter` exists after each change; `cargo check` / `cargo clippy` / `cargo test` inside `twoliter/` for compile issues; for kit failures, run the twoliter binary directly with `--log-level debug`.
