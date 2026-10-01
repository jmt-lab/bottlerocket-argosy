---
type: Styleguide Rule
description: "Mock trait dependencies with mockall (#[automock] on the trait, expectations with predicates) instead of hand-written fakes; use tempfile for filesystem fixtures."
language: rust
category: testing
---
# Mocks and fixtures

| Need | Crate |
|---|---|
| trait mocks | `mockall` |
| temp files / dirs | `tempfile` |
| collection literals | `maplit` |
| tests sharing a global resource (port, Docker) | `serial_test` |

## Good

```rust
#[cfg_attr(test, mockall::automock)]
pub trait Repository { fn get(&self, id: &str) -> Option<Item>; }

let mut repo = MockRepository::new();
repo.expect_get().with(predicate::eq("123")).returning(|_| Some(item()));
```
