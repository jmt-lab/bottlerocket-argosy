---
type: Styleguide Rule
description: "In new modules, give each fallible operation its own snafu error enum declared with #[snafu(module)] directly below the function, and wrap low-level errors into higher-level variants hierarchically."
language: rust
category: error-handling
---
# Error type per operation

Each fallible function gets its own `#[derive(Debug, Snafu)] #[snafu(module)] pub enum XxxError`, placed **below** the function, so callers can match on exactly the failures that operation produces. Higher-level operations wrap lower-level errors as `source` variants.

Crates that already use a crate-level `error.rs` with `pub type Result<T>` (common in bottlerocket and core-kit `sources/`) keep that pattern.

## Good

```rust
pub fn load_config(path: &Path) -> Result<Config, LoadConfigError> { … }

#[derive(Debug, Snafu)]
#[snafu(module)]
pub enum LoadConfigError {
    #[snafu(display("failed to read config file {}", path.display()))]
    ReadFile { path: PathBuf, source: std::io::Error },
    #[snafu(display("failed to parse config"))]
    ParseToml { source: toml::de::Error },
}
```

## Bad

A single shared `Error` enum with dozens of variants returned by every function in a new module.
