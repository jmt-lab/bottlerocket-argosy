---
type: Styleguide Rule
description: "Do not write tests that only exercise libraries or the compiler (serde round-trips, builders building, derives, trivial getters, field existence); test domain rules, business logic, transformations and your own error conditions."
language: rust
category: testing
---
# No useless tests

Rule of thumb: a good test still passes against a different implementation that satisfies the same domain rules; a useless test passes only because a particular library was used.

Do test: domain validation (a `KitName` rejecting `""`), business logic and transformations, error conditions specific to your code.

## Good

```rust
#[test]
fn migration_moves_motd_to_new_key() { … }
```

## Bad

```rust
#[test]
fn config_serde_round_trip() { … }
#[test]
fn builder_builds() { … }
#[test]
fn debug_impl_works() { … }
```
