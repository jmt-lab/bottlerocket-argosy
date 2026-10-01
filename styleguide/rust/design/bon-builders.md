---
type: Styleguide Rule
description: "In crates that use bon, structs with two or more fields derive Builder and are #[non_exhaustive]; put #[builder(into)] on individual String/PathBuf/newtype fields, never #[builder(on(_, into))], and do not add #[builder(default)] to Option fields."
language: rust
category: design
---
# `bon` builders

Applies where the crate already depends on `bon`.

- Any struct with 2+ fields uses `#[derive(Builder)]` **and** `#[non_exhaustive]`.
- `#[builder(into)]` on individual `String`, `PathBuf` and newtype fields.
- Never `#[builder(on(_, into))]`; it breaks numeric fields.
- `Option<T>` fields default to `None` already; do not add `#[builder(default)]`.
- Timestamps: `#[builder(default = Utc::now())]`.
- Only newtypes get a `new()` constructor.
- Callers pass `"value"`, not `"value".to_string()`, to `into` fields.

## Good

```rust
#[derive(Debug, Clone, PartialEq, Eq, Builder)]
#[non_exhaustive]
pub struct Job {
    #[builder(into)]
    name: String,
    retries: u32,
    timeout: Option<Duration>,
}
```

## Bad

```rust
#[derive(Builder)]
#[builder(on(_, into))]
pub struct Job {
    name: String,
    retries: u32,
    #[builder(default)]
    timeout: Option<Duration>,
}
```
