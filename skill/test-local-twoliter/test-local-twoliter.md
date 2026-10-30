---
type: Skill
description: Build Twoliter from a local checkout and run a kit build with it via make build TWOLITER_DIR=…; use when validating Twoliter source changes against bottlerocket-core-kit or bottlerocket-kernel-kit before opening a PR or cutting a release.
---

# Test a locally built Twoliter

Background: `document/twoliter/version-bump-and-local-testing` (section B) and `document/twoliter/development`. Assumes sibling checkouts of `twoliter` and a kit repo.

1. Edit Twoliter: CLI code in `twoliter/twoliter/src/`, embedded cargo-make tasks/scripts in `twoliter/twoliter/embedded/`.
2. Build:
   ```bash
   cd twoliter && cargo build --release && ls -lh target/release/twoliter
   ```
   On compile errors use `cargo check`, `cargo clippy`, `cargo test -p twoliter`.
3. Run the kit build with the local binary (pass the directory that contains it):
   ```bash
   cd ../bottlerocket-core-kit
   make build TWOLITER_DIR=../twoliter/target/release
   ```
4. Iterate: rebuild Twoliter (step 2), rerun step 3.
5. If the kit build fails, read Twoliter's output; for more detail run the local binary directly with `--log-level debug`.
6. Return to the pinned release by omitting `TWOLITER_DIR` (uses `tools/twoliter/twoliter`).

Report whether the kit built with the local Twoliter, and any behaviour difference versus the pinned release.
