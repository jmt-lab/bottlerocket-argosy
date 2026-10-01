---
type: Styleguide Rule
description: "APIs accept and return domain types (newtypes, Url, Duration, measurement types) rather than strings and bare numbers, put behaviour in methods on those types, and stream through impl Read rather than loading whole buffers."
language: rust
category: design
---
# Domain types over primitives

- Accept domain types (`&Chunk`, `&KitName`) instead of `&str`; prefer methods on the domain type over free functions on primitives.
- Use typed fields: `Url`, `Duration`, measurement types (`uom` where available) instead of `String`, `u64` seconds, or "megabytes as f64".
- Support streaming (`impl Read` / `impl Write`) instead of requiring the whole input in memory.

## Good

```rust
impl Manifest {
    pub fn from_reader(reader: impl Read) -> Result<Self, ParseManifestError> { … }
}
pub fn fetch(url: &Url, timeout: Duration) -> … 
```

## Bad

```rust
pub fn parse_manifest(contents: &str) -> … 
pub fn fetch(url: &str, timeout_secs: u64) -> … 
```
