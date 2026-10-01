---
type: Styleguide Rule
description: "In Cargo.toml, pin pre-1.0 crates as major.minor and post-1.0 crates as major only, keep dependencies alphabetised, and use workspace = true when the workspace declares the dependency."
language: rust
category: dependencies
---
# Cargo dependency specs

- Pre-1.0: `crate = "0.8"`. Post-1.0: `crate = "1"`.
- Alphabetise dependency tables.
- Declare versions once in `[workspace.dependencies]` (e.g. `sources/Cargo.toml`) and reference them with `workspace = true`, adding features locally.

## Good

```toml
[dependencies]
log.workspace = true
serde = { workspace = true, features = ["derive"] }
snafu.workspace = true
```

## Bad

```toml
[dependencies]
snafu = "0.8.5"
serde = { version = "1.0.210", features = ["derive"] }
log = "*"
```
