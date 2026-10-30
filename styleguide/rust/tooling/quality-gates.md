---
type: Styleguide Rule
description: "Rust changes are not done until cargo fmt, cargo clippy (with no new warnings) and cargo test pass for the affected workspace, or the repository's equivalent check targets."
language: rust
category: tooling
---
# Quality gates before finishing

Formatting, lint and test failures are cheapest to fix before review. Run them for the workspace you changed (each repo's `sources/` or crate workspace), or the repo's wrapper targets if it has them. Fix clippy findings rather than silencing them (`styleguide/general/fix-design-lints-structurally`).

## Good

```
cargo fmt --all
cargo clippy --all-targets --locked -- -D warnings
cargo test --locked
```

## Bad

Opening a pull request after only `cargo build`, or adding `#[allow(clippy::…)]` to get a clean clippy run.
