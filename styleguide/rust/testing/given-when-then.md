---
type: Styleguide Rule
description: "Every Rust test body is structured with // Given, // When and // Then comments."
language: rust
category: testing
---
# Given / When / Then

Each marker may carry a short phrase describing that step (`// Given an empty string`). Never remove these markers to shorten a file.

## Good

```rust
#[test]
fn rejects_empty_kit_name() {
    // Given
    let input = "";
    // When
    let result = KitName::try_new(input);
    // Then
    assert!(result.is_err());
}
```

## Bad

```rust
#[test]
fn test1() {
    assert!(KitName::try_new("").is_err());
}
```
