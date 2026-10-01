---
type: Styleguide Rule
description: "Every public Rust item has a doc comment with a summary line under 120 characters; skip # Errors and parameter/return sections, and avoid vague words like robust, efficient, handles, manages."
language: rust
category: documentation
---
# Doc comments on public items

- Every public item gets `///` docs; the first line is a concrete summary under 120 characters.
- Do not write `# Errors` sections or per-parameter/return docs; the types say that.
- Avoid vague words: "robust", "efficient", "handles", "manages". Say what actually happens.
- In crates whose `README.md` is generated from rustdoc (`README.tpl` + `generate-readme`), edit the crate-level doc comment, not the README.

## Good

```rust
/// Resolves every kit in the project to an image digest and writes `Twoliter.lock`.
pub fn lock(&self) -> Result<Lock, LockError> { … }
```

## Bad

```rust
/// Handles locking robustly.
///
/// # Errors
/// Returns an error if locking fails.
pub fn lock(&self) -> Result<Lock, LockError> { … }
```
