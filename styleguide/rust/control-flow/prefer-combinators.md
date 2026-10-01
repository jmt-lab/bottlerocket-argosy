---
type: Styleguide Rule
description: "Prefer Option/Result combinators (map, and_then, ok_or_else) and the ? operator with .context(...) over nested match; use if let for early returns that have side effects."
language: rust
category: control-flow
---
# Prefer combinators

## Good

```rust
let port = settings.port.map(Port::from).unwrap_or_default();
let cfg = read(path).context(ReadSnafu { path })?;
```

## Bad

```rust
let cfg = match read(path) {
    Ok(c) => c,
    Err(e) => return Err(Error::Read { path: path.into(), source: e }),
};
```
