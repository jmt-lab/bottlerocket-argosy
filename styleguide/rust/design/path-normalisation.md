---
type: Styleguide Rule
description: "Never hand-roll path normalisation or canonicalisation; use the crate's established helper (path_absolutize in Twoliter, where canonicalize is disallowed because it resolves symlinks; path-clean elsewhere)."
language: rust
category: design
---
# Path normalisation

Hand-written `..`/`.` handling is a recurring source of bugs. `std::fs::canonicalize` also resolves symlinks and needs the path to exist, which build tooling usually does not want; Twoliter's `clippy.toml` forbids it.

## Good

```rust
use path_absolutize::Absolutize;
let dir = input.absolutize()?;
```

## Bad

```rust
let dir = std::fs::canonicalize(input)?;
let cleaned = input.to_string_lossy().replace("/./", "/");
```
