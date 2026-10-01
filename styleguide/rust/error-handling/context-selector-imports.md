---
type: Styleguide Rule
description: "Import a per-operation error's snafu context selectors inside the function body (use xxx_error::*), and make that the only function-level import; propagate with .context(...)?."
language: rust
category: error-handling
---
# Context selector imports

With `#[snafu(module)]`, the selectors live in a module named after the error. Import them at the top of the function that uses them; this is the only import allowed inside a function. Everything else is imported at module level.

## Good

```rust
fn load_config(path: &Path) -> Result<Config, LoadConfigError> {
    use load_config_error::*;
    let content = std::fs::read_to_string(path).context(ReadFileSnafu { path })?;
    toml::from_str(&content).context(ParseTomlSnafu)
}
```

## Bad

```rust
use crate::config::load_config_error::*; // module-level glob of one function's selectors

fn load_config(path: &Path) -> Result<Config, LoadConfigError> {
    use std::fs::read_to_string; // non-selector import inside a function
    …
}
```
