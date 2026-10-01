---
type: Styleguide Rule
description: "Tool configuration is a TOML file whose path is passed as a CLI argument, deserialised into a typed struct; do not configure behaviour through ad-hoc environment variables."
language: rust
category: configuration
---
# Configuration via TOML and CLI args

Prefer TOML over JSON/YAML for configuration. Pass the config path (and overrides) as CLI arguments so invocations are explicit and reproducible. Environment variables are reserved for established passthrough contracts (for example Twoliter's allowlisted `BUILDSYS_*`/`PUBLISH_*` prefixes).

## Good

```
mytool --config /etc/mytool/config.toml
```

## Bad

```rust
let retries = std::env::var("MYTOOL_RETRIES").unwrap_or("3".into());
```
