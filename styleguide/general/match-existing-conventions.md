---
type: Styleguide Rule
description: "Follow the established conventions of the repository and crate you are editing over generic style defaults; where a styleguide rule conflicts with a crate's existing pattern, match the crate."
language: general
category: organization
---
# Match existing conventions first

Bottlerocket spans several repositories with different, deliberate choices. The other `styleguide/` rules are defaults for new code; inside an existing crate, consistency with that crate wins.

Known divergences to respect:

| Area | Existing pattern | Where |
|---|---|---|
| CLI parsing | `argh` (no `clap`) | core-kit, kernel-kit `sources/` |
| Logging | `log` + `simplelog` | core-kit, kernel-kit `sources/` |
| Errors | crate-level `error.rs` with private `mod error` and `pub type Result<T>` | many bottlerocket / core-kit crates |
| Errors | `anyhow` + `.context()` | `twoliter` CLI crate, `pipesys`, `unplug`, `krane` |
| Paths | never `canonicalize`; use `path_absolutize` | Twoliter (`clippy.toml` `disallowed_methods`) |
| Commits | `scope: description`, enforced by commitlint | every repo (`styleguide/general/commits/header-format`) |

Check the repo's `document/<repo>/conventions` before introducing a new crate, pattern, or layout. When you want to move a crate toward a different pattern, propose it as its own change rather than mixing styles in one file.
