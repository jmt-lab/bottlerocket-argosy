---
type: Styleguide Rule
description: "Validate preconditions with snafu::ensure! rather than if-conditions that return Err manually."
language: rust
category: error-handling
---
# Use `ensure!` for validation

## Good

```rust
ensure!(!name.is_empty(), EmptyNameSnafu);
```

## Bad

```rust
if name.is_empty() {
    return Err(Error::EmptyName);
}
```
