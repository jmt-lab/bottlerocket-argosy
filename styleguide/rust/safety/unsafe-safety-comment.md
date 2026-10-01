---
type: Styleguide Rule
description: "Avoid unsafe; where it is unavoidable, precede every unsafe block with a // SAFETY: comment justifying why the invariants hold."
language: rust
category: safety
---
# `unsafe` needs a SAFETY comment

## Good

```rust
// SAFETY: `fd` was just returned by `open` and is owned exclusively here.
let file = unsafe { File::from_raw_fd(fd) };
```

## Bad

```rust
let file = unsafe { File::from_raw_fd(fd) };
```
