---
type: Styleguide Rule
description: "Production Rust code never calls unwrap() or expect(); return an error instead. Tests may use both."
language: rust
category: error-handling
---
# No `unwrap`/`expect` outside tests

Bottlerocket binaries run unattended on hosts; a panic is an outage. Return a contextual error. In `#[cfg(test)]` code and integration tests, `unwrap()`/`expect()` are fine.

## Good

```rust
let port = value.parse::<u16>().context(InvalidPortSnafu { value })?;
```

## Bad

```rust
let port = value.parse::<u16>().unwrap();
```
