---
type: Styleguide Rule
description: "Organise Rust code into domain-specific modules with each operation's error type next to it; no types.rs or utils.rs grab-bags, and switch to a directory module once a file nears 500 lines."
language: rust
category: organization
---
# Domain modules

- Name modules after domain concepts (`lock`, `vendor`, `manifest`), not artifact kinds (`types`, `errors`, `utils`).
- Error types live next to the operations that produce them.
- Every submodule should be explainable in one line of the parent's module doc.
- Convert `foo.rs` to `foo/mod.rs` + submodules once it passes about 500 lines (`styleguide/general/complexity-thresholds`).

## Good

```
project/
  mod.rs
  lock/
    mod.rs
    verification.rs
  vendor.rs
```

## Bad

```
src/
  types.rs
  errors.rs
  utils.rs
```
