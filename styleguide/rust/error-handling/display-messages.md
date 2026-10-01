---
type: Styleguide Rule
description: "Snafu display messages state what failed and never interpolate {source}; remediation advice belongs in diagnostics or help text, not the message."
language: rust
category: error-handling
---
# Error display messages

- Never put `{source}` in `display`; error reporters print the source chain, so interpolating it duplicates text.
- Say *what* failed (with the identifying data: path, key, URL), not how to fix it.

## Good

```rust
#[snafu(display("failed to read {}", path.display()))]
ReadFile { path: PathBuf, source: std::io::Error },
```

## Bad

```rust
#[snafu(display("failed to read {}: {source}. Check the file exists.", path.display()))]
ReadFile { path: PathBuf, source: std::io::Error },
```
