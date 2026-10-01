---
type: Styleguide Rule
description: "When wrapping errors from trait objects or associated error types, store them as `source: Box<dyn std::error::Error + Send + Sync + 'static>` and convert with .map_err(|e| Box::new(e) as _).context(...)."
language: rust
category: error-handling
---
# Boxed sources for trait-object errors

## Good

```rust
#[derive(Debug, Snafu)]
#[snafu(module)]
pub enum FetchError {
    #[snafu(display("store lookup failed"))]
    Lookup { source: Box<dyn std::error::Error + Send + Sync + 'static> },
}

store.get(&key).map_err(|e| Box::new(e) as _).context(LookupSnafu)?;
```

## Bad

```rust
store.get(&key).map_err(|e| FetchError::Lookup { message: e.to_string() })?;
```
