---
type: Styleguide Rule
description: "Derive Debug, Clone, PartialEq and Eq on data types by default (plus Copy for simple enums), and always derive PartialEq/Eq on types that tests compare."
language: rust
category: design
---
# Standard derives

## Good

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Arch { X86_64, Aarch64 }
```

## Bad

```rust
pub enum Arch { X86_64, Aarch64 } // tests fall back to field-by-field or matches! checks
```
