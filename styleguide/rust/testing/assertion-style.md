---
type: Styleguide Rule
description: "Assert error variants with assert!(matches!(...)), compare whole structs with assert_eq! rather than field by field, and build JSON fixtures with fully qualified serde_json::from_value(json!({...}))."
language: rust
category: testing
---
# Assertion style

## Good

```rust
assert!(matches!(result, Err(LookupError::NotFound { .. })));
assert_eq!(actual, expected);
let input: Settings = serde_json::from_value(json!({ "motd": "hi" })).unwrap();
```

## Bad

```rust
match result {
    Err(LookupError::NotFound { .. }) => {}
    _ => panic!("wrong error"),
}
assert_eq!(actual.name, expected.name);
assert_eq!(actual.version, expected.version);
```
