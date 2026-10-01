---
type: Styleguide Rule
description: "Serde-deserialised configuration structs use #[serde(rename_all = \"kebab-case\", deny_unknown_fields)] and typed fields such as Url and Duration rather than strings."
language: rust
category: serialization
---
# Serde config structs

`deny_unknown_fields` turns typos in user config into errors instead of silently ignored keys. Kebab-case matches Bottlerocket's TOML files (`Twoliter.toml`, `Infra.toml`).

## Good

```rust
#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "kebab-case", deny_unknown_fields)]
pub struct Config {
    api_endpoint: Url,
    max_retries: u32,
}
```

## Bad

```rust
#[derive(Deserialize)]
pub struct Config {
    apiEndpoint: String,
    max_retries: u32,
}
```
