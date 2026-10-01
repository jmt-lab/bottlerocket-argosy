---
type: Styleguide Rule
description: "Code comments explain why the code is the way it is, never restate what it does."
language: general
category: documentation
---
# Comments explain why

## Good

```rust
// Retry needed because S3 eventual consistency can cause brief 404s.
```

## Bad

```rust
// Loop over the items and retry.
```
