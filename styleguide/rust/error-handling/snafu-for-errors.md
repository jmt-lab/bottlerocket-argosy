---
type: Styleguide Rule
description: "Define Rust error types with snafu, never thiserror; keep anyhow only in crates that already use it."
language: rust
category: error-handling
---
# Use snafu for errors

`snafu` is the error library across Bottlerocket's first-party Rust. Do not add `thiserror`. A few Twoliter crates (`twoliter` CLI, `pipesys`, `unplug`, `krane`) use `anyhow`; keep them consistent rather than mixing (`styleguide/general/match-existing-conventions`).

## Good

```rust
#[derive(Debug, Snafu)]
pub enum Error { … }
```

## Bad

```rust
#[derive(Debug, thiserror::Error)]
pub enum Error { … }
```
