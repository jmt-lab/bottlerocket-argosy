---
type: Styleguide Rule
description: "Module docs (//!) open with an action-oriented sentence, follow with a capabilities paragraph, add an # Architecture list for modules with submodules and a # Quick Start example for entry-point modules, and bold key type names."
language: rust
category: documentation
---
# Module docs

Structure for `//!` docs:

1. An action-oriented opening sentence.
2. A paragraph on capabilities.
3. `# Architecture`: a bullet list of layers or submodules, for modules that have submodules.
4. `# Quick Start`: a runnable example, for facade or entry-point modules.

Bold the key type names (`**Lock**`).

## Good

```rust
//! Resolves and verifies the project's SDK and kit dependencies.
//!
//! Builds a **Lock** from `Twoliter.toml`, walks kit metadata transitively, and
//! rejects conflicting kit versions.
//!
//! # Architecture
//! - `resolve`: registry lookups and the dependency graph
//! - `verification`: on-disk verification markers
```

## Bad

```rust
//! Lock stuff.
```
