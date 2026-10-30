---
type: Skill
description: Bump the pinned Twoliter version and SHA256 checksums across bottlerocket-core-kit, bottlerocket-kernel-kit and bottlerocket with one chore commit per repo; use when adopting a new Twoliter release or release candidate everywhere.
---

# Update Twoliter everywhere

Full procedure, formats and notes: `document/twoliter/version-bump-and-local-testing` (section A). Assumes sibling checkouts of `bottlerocket-core-kit`, `bottlerocket-kernel-kit` and `bottlerocket` on clean branches. Ask for the target version `X.Y.Z` (e.g. `0.13.0`, `0.13.0-rc1`) if not given.

1. Fetch both checksums:
   ```bash
   for a in x86_64 aarch64; do
     curl -fsSL "https://github.com/bottlerocket-os/twoliter/releases/download/vX.Y.Z/twoliter-$a-unknown-linux-musl.tar.xz.sha256"
   done
   ```
   If either fails, stop and check the release page exists with the musl tarballs attached.
2. In each kit `Makefile`, set `TWOLITER_VERSION ?= "X.Y.Z"` (no `v`), `TWOLITER_SHA256_AARCH64`, `TWOLITER_SHA256_X86_64`; then `git add Makefile && git commit -m "chore: bump to twoliter X.Y.Z"`.
3. In `bottlerocket/Makefile.toml`, set `TWOLITER_VERSION = "vX.Y.Z"` (with `v`) and the two SHA256 values; then `git add Makefile.toml && git commit -m "chore: bump to twoliter X.Y.Z"`.
4. Validate each repo: `git show HEAD --stat` → 1 file changed, 3 insertions, 3 deletions.
5. RC → stable on an existing bump commit: edit the same lines and `git commit --amend -m "chore: bump to twoliter X.Y.Z"`.
6. Touch `schema-version` only if the Twoliter release notes require it.

Do not push. Report the three commits; the user opens one PR per repo, which runs CI against the new Twoliter.
