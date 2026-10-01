---
type: Styleguide Rule
description: "Unit tests live at the bottom of the file they test in #[cfg(test)] mod test { use super::*; }, and integration tests live in the crate's tests/ directory."
language: rust
category: testing
---
# Test placement

- Unit tests: bottom of the same file, `#[cfg(test)] mod test { use super::*; … }`, co-located with the code they exercise. When splitting a file, move its tests with it.
- Integration tests: the crate's `tests/` directory. Tests that need Docker, network or full builds are `#[ignore]`d and run by the repo's integration target (e.g. Twoliter's `make integ`).
