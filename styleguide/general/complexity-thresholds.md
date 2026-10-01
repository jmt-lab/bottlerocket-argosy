---
type: Styleguide Rule
description: "Keep nesting depth at most 4, functions at most about 60 lines, and non-test source files at most 550 lines; exceeding these is a signal to restructure."
language: general
category: complexity
---
# Complexity thresholds

Readability means a reader can answer "what does this do and why" without holding the whole thing in their head. Treat these as review triggers:

- Nesting deeper than **4** levels.
- Functions longer than **60** lines.
- Non-test source files longer than **550** lines. For Rust, convert a module to a directory module (`foo/mod.rs` + submodules) once it passes about 500 lines.

When a threshold is crossed, restructure as described in `styleguide/general/fix-design-lints-structurally`. Do not shrink a file by deleting doc comments, comments, or test structure.
