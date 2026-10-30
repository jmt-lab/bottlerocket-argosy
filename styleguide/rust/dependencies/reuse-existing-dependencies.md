---
type: Styleguide Rule
description: "Before adding a crate, check the workspace Cargo.toml for one that already serves the purpose and use it; add a new dependency only when nothing existing fits, and declare it once in [workspace.dependencies]."
language: rust
category: dependencies
---
# Reuse existing dependencies

Every new crate is more code to vendor, license-scan and keep patched. Bottlerocket workspaces already carry standard choices (for example `snafu` for errors, `argh` or `clap` for CLIs, `log` or `tracing` for logging); pick the one the workspace uses (`styleguide/general/match-existing-conventions`).

## Good

```toml
[dependencies]
snafu.workspace = true
```

## Bad

```toml
[dependencies]
thiserror = "2"     # workspace already uses snafu
structopt = "0.3"   # crate already parses args with argh
```
