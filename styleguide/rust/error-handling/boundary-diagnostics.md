---
type: Styleguide Rule
description: "In crates that use miette, the application boundary (main and CLI entry points) returns miette::Result and its error types derive both Snafu and miette::Diagnostic with a unique code(...) and an actionable help(...); inner errors stay plain snafu."
language: rust
category: error-handling
---
# Diagnostics at the application boundary

Applies where the crate already depends on `miette`; other crates keep their existing reporting (`styleguide/general/match-existing-conventions`).

snafu builds the error; miette presents it. Only the errors a user actually sees at the boundary carry diagnostics:

- `main` returns `miette::Result<()>`; enable miette's `fancy` feature in the binary crate for coloured output.
- Boundary error types derive `Snafu` and `Diagnostic`. Each variant has a unique `code(crate::area::what)` and a `help(...)` that tells the user what *they* can do, not how the code works.
- The `display` message still states only what failed (`styleguide/rust/error-handling/display-messages`); remediation lives in `help`.

## Good

```rust
#[derive(Debug, Snafu, Diagnostic)]
#[snafu(module)]
pub enum MainError {
    #[snafu(display("failed to load configuration"))]
    #[diagnostic(
        code(mytool::config::load),
        help("check that config.toml exists and is valid TOML")
    )]
    LoadConfig { source: LoadConfigError },
}

fn main() -> miette::Result<()> {
    run()?;
    Ok(())
}
```

## Bad

```rust
fn main() {
    if let Err(e) = run() {
        eprintln!("error: {e:?} (try checking your config, it's parsed in config.rs line 40)");
        std::process::exit(1);
    }
}
```
