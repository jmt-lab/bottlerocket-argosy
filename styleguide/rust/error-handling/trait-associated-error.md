---
type: Styleguide Rule
description: "Fallible traits declare an associated `type Error: std::error::Error + Send + Sync + 'static` so each implementation has its own error type, never a shared concrete one."
language: rust
category: error-handling
---
# Associated error types on fallible traits

## Good

```rust
pub trait Store {
    type Error: std::error::Error + Send + Sync + 'static;
    fn get(&self, key: &Key) -> Result<Value, Self::Error>;
}
```

## Bad

```rust
pub trait Store {
    fn get(&self, key: &Key) -> Result<Value, crate::Error>;
}
```
