---
type: Styleguide Rule
description: "In crates that use tracing, annotate functions with #[instrument] (#[instrument(err)] when fallible) and log with structured fields rather than formatted strings."
language: rust
category: logging
---
# Structured logging with `tracing`

Applies where the crate uses `tracing`; crates on `log` + `simplelog` stay on them (`styleguide/general/match-existing-conventions`).

## Good

```rust
use tracing::{info, instrument};

#[instrument(err)]
fn process(input: &[u8]) -> Result<(), ProcessError> {
    info!(length = input.len(), "Processing input");
    …
}
```

## Bad

```rust
fn process(input: &[u8]) -> Result<(), ProcessError> {
    println!("processing {} bytes", input.len());
    …
}
```
