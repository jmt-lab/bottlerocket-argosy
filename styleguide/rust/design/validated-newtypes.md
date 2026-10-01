---
type: Styleguide Rule
description: "Represent validated values as newtypes (nutype where available) that cannot be constructed invalid, instead of passing raw primitives and re-checking them."
language: rust
category: design
---
# Validated newtypes

- Single-predicate validation: `#[nutype(validate(not_empty), derive(…))]`.
- Custom rules: `validate(with = fn, error = E)`; use `new_unchecked` only where the invariant is already proven.
- Hand-write the newtype and its snafu error only when nutype cannot express the rule (or the crate does not use nutype).

## Good

```rust
#[nutype(validate(not_empty), derive(Debug, Clone, PartialEq, Eq, AsRef))]
pub struct KitName(String);
```

## Bad

```rust
pub fn publish(kit_name: &str) -> Result<()> {
    ensure!(!kit_name.is_empty(), EmptyNameSnafu); // repeated in every caller
    …
}
```
