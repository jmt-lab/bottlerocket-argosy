---
type: Styleguide Rule
description: "When tests differ only in inputs and expected outputs, write one #[test_case(...; \"name\")] test instead of copy-pasted tests."
language: rust
category: testing
---
# Parameterise with `test_case`

Use it for multiple invalid inputs, multiple inputs to one behaviour, or input/expected pairs.

## Good

```rust
#[test_case("./foo", "foo" ; "strips leading dot-slash")]
#[test_case("foo/../bar", "bar" ; "resolves parent directory")]
fn normalises_path(input: &str, expected: &str) {
    // Given / When
    let actual = normalise(input);
    // Then
    assert_eq!(actual, Path::new(expected));
}
```

## Bad

```rust
#[test] fn normalises_dot_slash() { assert_eq!(normalise("./foo"), Path::new("foo")); }
#[test] fn normalises_parent()    { assert_eq!(normalise("foo/../bar"), Path::new("bar")); }
```
